import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phase1h import execution
from phase1h.test_execution import OLD_ARCHIVE_REPLAY_SEAL, canonical, schedule


def evidence(root: str) -> tuple[Path, Path, Path]:
    handoff_dir = Path(root) / "handoff"
    receipt_dir = Path(root) / "receipts"
    seal_dir = Path(root) / "seals"
    handoff_dir.mkdir()
    handoff = execution.canonical_execution_handoff(
        schedule(),
        execution.EXPECTED_PREGAME_COMMITMENT_SHA256,
    )
    (handoff_dir / "handoff.json").write_text(handoff, encoding="utf-8")
    execution.consume_execution_handoff(handoff_dir, receipt_dir)
    return handoff_dir, receipt_dir, seal_dir


class PrivateExecutionDigestSealTests(unittest.TestCase):
    def test_reruns_once_then_cold_duplicate_never_reruns_or_rewrites(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir, receipt_dir, seal_dir = evidence(root)
            real_simulator = execution.simulate_scheduled_game
            with patch.object(
                execution,
                "simulate_scheduled_game",
                wraps=real_simulator,
            ) as simulator:
                status, seal_path = execution.seal_execution_receipt(
                    handoff_dir,
                    receipt_dir,
                    seal_dir,
                )
                self.assertEqual(status, "sealed")
                self.assertEqual(simulator.call_count, 1)
                before = (
                    seal_path.read_bytes(),
                    hashlib.sha256(seal_path.read_bytes()).hexdigest(),
                    seal_path.stat().st_mtime_ns,
                )
                duplicate, duplicate_path = execution.seal_execution_receipt(
                    handoff_dir,
                    receipt_dir,
                    seal_dir,
                )
                self.assertEqual(duplicate, "duplicate")
                self.assertEqual(duplicate_path, seal_path)
                self.assertEqual(simulator.call_count, 1)
                self.assertEqual(
                    before,
                    (
                        seal_path.read_bytes(),
                        hashlib.sha256(seal_path.read_bytes()).hexdigest(),
                        seal_path.stat().st_mtime_ns,
                    ),
                )
            seal = json.loads(seal_path.read_text(encoding="utf-8"))
            receipt = json.loads(next(receipt_dir.glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(
                seal["verified_output_digest_sha256"],
                receipt["output_digest_sha256"],
            )
            self.assertNotEqual(
                seal["verified_output_digest_sha256"],
                OLD_ARCHIVE_REPLAY_SEAL,
            )
            self.assertEqual(
                set(seal),
                {
                    "commitment_sha256",
                    "execution_input_sha256",
                    "executor_version",
                    "receipt_sha256",
                    "record_version",
                    "schema",
                    "seal_sha256",
                    "status",
                    "verified_output_digest_sha256",
                    "verifier_version",
                },
            )

    def test_digest_mismatch_missing_and_multiple_evidence_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir, receipt_dir, seal_dir = evidence(root)
            receipt_path = next(receipt_dir.glob("*.json"))
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["output_digest_sha256"] = "0" * 64
            body = dict(receipt)
            body.pop("receipt_sha256")
            receipt["receipt_sha256"] = hashlib.sha256(
                canonical(body).encode()
            ).hexdigest()
            receipt_path.write_text(canonical(receipt), encoding="utf-8")
            real_simulator = execution.simulate_scheduled_game
            with patch.object(
                execution,
                "simulate_scheduled_game",
                wraps=real_simulator,
            ) as simulator:
                with self.assertRaises(ValueError):
                    execution.seal_execution_receipt(
                        handoff_dir,
                        receipt_dir,
                        seal_dir,
                    )
                self.assertEqual(simulator.call_count, 1)
            self.assertFalse(list(seal_dir.glob("*.json")))

        for missing in ("handoff", "receipt"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as root:
                handoff_dir, receipt_dir, seal_dir = evidence(root)
                target = handoff_dir if missing == "handoff" else receipt_dir
                next(target.glob("*.json")).unlink()
                with patch.object(execution, "simulate_scheduled_game") as simulator:
                    with self.assertRaises(ValueError):
                        execution.seal_execution_receipt(
                            handoff_dir,
                            receipt_dir,
                            seal_dir,
                        )
                    simulator.assert_not_called()

        for multiple in ("handoff", "receipt"):
            with self.subTest(multiple=multiple), tempfile.TemporaryDirectory() as root:
                handoff_dir, receipt_dir, seal_dir = evidence(root)
                target = handoff_dir if multiple == "handoff" else receipt_dir
                source = next(target.glob("*.json"))
                (target / "extra.json").write_bytes(source.read_bytes())
                with patch.object(execution, "simulate_scheduled_game") as simulator:
                    with self.assertRaises(ValueError):
                        execution.seal_execution_receipt(
                            handoff_dir,
                            receipt_dir,
                            seal_dir,
                        )
                    simulator.assert_not_called()

    def test_seal_tamper_conflict_and_multiple_fail_without_repair(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir, receipt_dir, seal_dir = evidence(root)
            _, seal_path = execution.seal_execution_receipt(
                handoff_dir,
                receipt_dir,
                seal_dir,
            )
            original = json.loads(seal_path.read_text(encoding="utf-8"))
            mutations = {
                "schema": lambda value: value.update(schema="wrong"),
                "version": lambda value: value.update(record_version=2),
                "commitment": lambda value: value.update(commitment_sha256="0" * 64),
                "input": lambda value: value.update(execution_input_sha256="0" * 64),
                "receipt": lambda value: value.update(receipt_sha256="0" * 64),
                "executor": lambda value: value.update(executor_version="future"),
                "verifier": lambda value: value.update(verifier_version="future"),
                "digest": lambda value: value.update(
                    verified_output_digest_sha256="0" * 64
                ),
                "status": lambda value: value.update(status="resulted"),
                "seal_hash": lambda value: value.update(seal_sha256="0" * 64),
                "extra": lambda value: value.update(score=101),
                "missing": lambda value: value.pop("status"),
            }
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    value = copy.deepcopy(original)
                    mutate(value)
                    tampered = canonical(value)
                    seal_path.write_text(tampered, encoding="utf-8")
                    with patch.object(execution, "simulate_scheduled_game") as simulator:
                        with self.assertRaises(ValueError):
                            execution.seal_execution_receipt(
                                handoff_dir,
                                receipt_dir,
                                seal_dir,
                            )
                        simulator.assert_not_called()
                    self.assertEqual(seal_path.read_text(encoding="utf-8"), tampered)
            seal_path.write_text(canonical(original), encoding="utf-8")
            (seal_dir / "extra.json").write_text(canonical(original), encoding="utf-8")
            with patch.object(execution, "simulate_scheduled_game") as simulator:
                with self.assertRaises(ValueError):
                    execution.seal_execution_receipt(
                        handoff_dir,
                        receipt_dir,
                        seal_dir,
                    )
                simulator.assert_not_called()


if __name__ == "__main__":
    unittest.main()
