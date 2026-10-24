import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from phase1h import execution, seal_supervisor, supervisor
from phase1h.test_execution import schedule
from phase1h.test_supervisor import FakeKernel, FakeProcess


class LocalSealSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.upstream = Path(self.temporary.name) / "Upstream"
        self.private = Path(self.temporary.name) / "SealProof"
        self.patches = [
            patch.object(seal_supervisor, "UPSTREAM_PRIVATE_ROOT", self.upstream),
            patch.object(seal_supervisor, "PRIVATE_ROOT", self.private),
            patch.object(seal_supervisor, "HANDOFF_DIRECTORY", self.upstream / "Handoff"),
            patch.object(seal_supervisor, "RECEIPT_DIRECTORY", self.upstream / "Receipts"),
            patch.object(seal_supervisor, "SEAL_DIRECTORY", self.private / "Seals"),
            patch.object(seal_supervisor, "ATTEMPT_DIRECTORY", self.private / "SealAttempts"),
            patch.object(seal_supervisor, "LOG_DIRECTORY", self.private / "SealLogs"),
        ]
        for active in self.patches:
            active.start()
        self.make_evidence()

    def tearDown(self) -> None:
        for active in reversed(self.patches):
            active.stop()
        self.temporary.cleanup()

    def make_evidence(self) -> None:
        seal_supervisor.HANDOFF_DIRECTORY.mkdir(parents=True, exist_ok=True)
        handoff = execution.canonical_execution_handoff(
            schedule(), execution.EXPECTED_PREGAME_COMMITMENT_SHA256
        )
        (seal_supervisor.HANDOFF_DIRECTORY / "handoff.json").write_text(
            handoff, encoding="utf-8"
        )
        self.commitment = execution.validate_execution_handoff(handoff)
        execution.consume_execution_handoff(
            seal_supervisor.HANDOFF_DIRECTORY,
            seal_supervisor.RECEIPT_DIRECTORY,
        )

    def reset_evidence(self) -> None:
        shutil.rmtree(self.upstream, ignore_errors=True)
        shutil.rmtree(self.private, ignore_errors=True)
        self.make_evidence()

    def test_01_allowlist_manual_entry_and_fixed_three_directory_child(self) -> None:
        seal_supervisor._validate_allowlist()
        with patch.object(
            seal_supervisor,
            "APPROVED_CONTROL_SHA256",
            "0" * 64,
        ):
            with self.assertRaisesRegex(supervisor.SupervisorError, "control_not_allowlisted"):
                seal_supervisor._validate_allowlist()
        with patch.object(seal_supervisor, "run_seal_supervisor") as run, contextlib.redirect_stderr(
            io.StringIO()
        ):
            self.assertEqual(seal_supervisor._main(["--seal-dir", "elsewhere"]), 2)
        run.assert_not_called()

        name = f"{self.commitment.commitment_sha256}.json"
        fake = FakeProcess(f"sealed: {name}\n")
        kernel = FakeKernel()
        with patch.object(supervisor.subprocess, "Popen", return_value=fake) as popen, patch.object(
            supervisor, "_job_for", return_value=(kernel, 1)
        ):
            self.assertEqual(seal_supervisor._run_child(name), ("sealed", 0))
        command = popen.call_args.args[0]
        self.assertEqual(
            command,
            [
                str(supervisor.APPROVED_PYTHON),
                "-B",
                "-m",
                "phase1h.execution",
                str(seal_supervisor.HANDOFF_DIRECTORY),
                str(seal_supervisor.RECEIPT_DIRECTORY),
                str(seal_supervisor.SEAL_DIRECTORY),
            ],
        )

    def test_02_fresh_evidence_claims_once_runs_one_child_and_writes_exact_seal(self) -> None:
        with patch.object(
            seal_supervisor,
            "_run_child",
            wraps=seal_supervisor._run_child,
        ) as child:
            status, seal = seal_supervisor.run_seal_supervisor()
        self.assertEqual(status, "sealed")
        self.assertEqual(child.call_count, 1)
        _, receipt = execution._execution_evidence(
            seal_supervisor.HANDOFF_DIRECTORY,
            seal_supervisor.RECEIPT_DIRECTORY,
        )
        record = execution._validate_seal(
            seal.read_text(encoding="utf-8"),
            self.commitment,
            receipt,
        )
        self.assertEqual(record["status"], "sealed_pending_result")
        self.assertEqual(
            record["verified_output_digest_sha256"],
            receipt["output_digest_sha256"],
        )
        self.assertEqual(
            set(record),
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

    def test_03_concurrent_supervisors_launch_exactly_one_child(self) -> None:
        entered = threading.Event()
        release = threading.Event()

        def seal_once(seal_name: str) -> tuple[str, int]:
            entered.set()
            self.assertTrue(release.wait(5))
            status, seal = execution.seal_execution_receipt(
                seal_supervisor.HANDOFF_DIRECTORY,
                seal_supervisor.RECEIPT_DIRECTORY,
                seal_supervisor.SEAL_DIRECTORY,
            )
            self.assertEqual(seal.name, seal_name)
            return status, 0

        with patch.object(seal_supervisor, "_run_child", side_effect=seal_once) as child, ThreadPoolExecutor(
            max_workers=2
        ) as pool:
            first = pool.submit(seal_supervisor.run_seal_supervisor)
            self.assertTrue(entered.wait(5))
            second = pool.submit(seal_supervisor.run_seal_supervisor)
            with self.assertRaisesRegex(supervisor.SupervisorError, "uncertain_prior_attempt"):
                second.result(timeout=5)
            release.set()
            self.assertEqual(first.result(timeout=5)[0], "sealed")
        self.assertEqual(child.call_count, 1)

    def test_04_exact_seal_is_duplicate_without_child_or_rewrite(self) -> None:
        _, seal = execution.seal_execution_receipt(
            seal_supervisor.HANDOFF_DIRECTORY,
            seal_supervisor.RECEIPT_DIRECTORY,
            seal_supervisor.SEAL_DIRECTORY,
        )
        before = (
            seal.read_bytes(),
            hashlib.sha256(seal.read_bytes()).hexdigest(),
            seal.stat().st_mtime_ns,
        )
        with patch.object(seal_supervisor, "_run_child") as child:
            status, duplicate = seal_supervisor.run_seal_supervisor()
        self.assertEqual((status, duplicate), ("duplicate", seal))
        child.assert_not_called()
        self.assertEqual(
            before,
            (
                seal.read_bytes(),
                hashlib.sha256(seal.read_bytes()).hexdigest(),
                seal.stat().st_mtime_ns,
            ),
        )

    def test_05_missing_multiple_or_tampered_upstream_stops_without_child(self) -> None:
        for directory in (
            seal_supervisor.HANDOFF_DIRECTORY,
            seal_supervisor.RECEIPT_DIRECTORY,
        ):
            with self.subTest(missing=directory.name):
                target = next(directory.glob("*.json"))
                before = target.read_bytes()
                target.unlink()
                with patch.object(seal_supervisor, "_run_child") as child:
                    with self.assertRaisesRegex(supervisor.SupervisorError, "rejected"):
                        seal_supervisor.run_seal_supervisor()
                child.assert_not_called()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(before)

        for directory in (
            seal_supervisor.HANDOFF_DIRECTORY,
            seal_supervisor.RECEIPT_DIRECTORY,
        ):
            with self.subTest(multiple=directory.name):
                source = next(directory.glob("*.json"))
                extra = directory / "extra.json"
                extra.write_bytes(source.read_bytes())
                with patch.object(seal_supervisor, "_run_child") as child:
                    with self.assertRaisesRegex(supervisor.SupervisorError, "rejected"):
                        seal_supervisor.run_seal_supervisor()
                child.assert_not_called()
                extra.unlink()

        receipt = next(seal_supervisor.RECEIPT_DIRECTORY.glob("*.json"))
        tampered = receipt.read_text(encoding="utf-8").replace(
            '"status":"executed_pending_seal"', '"status":"wrong"'
        )
        receipt.write_text(tampered, encoding="utf-8")
        with patch.object(seal_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "rejected"):
                seal_supervisor.run_seal_supervisor()
        child.assert_not_called()
        self.assertEqual(receipt.read_text(encoding="utf-8"), tampered)

    def test_06_tampered_or_multiple_seal_stops_without_child_or_repair(self) -> None:
        _, seal = execution.seal_execution_receipt(
            seal_supervisor.HANDOFF_DIRECTORY,
            seal_supervisor.RECEIPT_DIRECTORY,
            seal_supervisor.SEAL_DIRECTORY,
        )
        tampered = seal.read_text(encoding="utf-8").replace(
            '"status":"sealed_pending_result"', '"status":"wrong"'
        )
        seal.write_text(tampered, encoding="utf-8")
        with patch.object(seal_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "seal_rejected"):
                seal_supervisor.run_seal_supervisor()
        child.assert_not_called()
        self.assertEqual(seal.read_text(encoding="utf-8"), tampered)

        seal.write_text(execution._canonical_json(json.loads(tampered) | {"status": "sealed_pending_result"}), encoding="utf-8")
        (seal_supervisor.SEAL_DIRECTORY / "extra.json").write_text("{}", encoding="utf-8")
        with patch.object(seal_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "seal_set_conflicts"):
                seal_supervisor.run_seal_supervisor()
        child.assert_not_called()

    def test_07_timeout_or_crash_retains_claim_and_blocks_retry(self) -> None:
        with patch.object(
            seal_supervisor,
            "_run_child",
            side_effect=supervisor.SupervisorError("child_timeout", 124),
        ):
            with self.assertRaisesRegex(supervisor.SupervisorError, "child_timeout"):
                seal_supervisor.run_seal_supervisor()
        claim = seal_supervisor.ATTEMPT_DIRECTORY / f"{self.commitment.commitment_sha256}.json"
        self.assertTrue(claim.is_file())
        with patch.object(seal_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "uncertain_prior_attempt"):
                seal_supervisor.run_seal_supervisor()
        child.assert_not_called()

    def test_08_exact_seal_and_bounded_log_are_required_and_no_h26k_exists(self) -> None:
        with patch.object(seal_supervisor, "_run_child", return_value=("sealed", 0)):
            with self.assertRaisesRegex(supervisor.SupervisorError, "exact_seal_required"):
                seal_supervisor.run_seal_supervisor()

        self.reset_evidence()
        seal_supervisor.run_seal_supervisor()
        log = seal_supervisor.LOG_DIRECTORY / f"{self.commitment.commitment_sha256}.jsonl"
        raw = log.read_text(encoding="utf-8").strip()
        record = json.loads(raw)
        self.assertLessEqual(len(raw.encode("utf-8")), 1024)
        self.assertEqual(record["status"], "sealed")
        self.assertEqual(record["supervisor_version"], seal_supervisor.SEAL_SUPERVISOR_VERSION)
        self.assertFalse(
            any(
                key in raw
                for key in (
                    "seed_material",
                    "execution_input",
                    "output_digest",
                    "score",
                    "winner",
                    "stake",
                    "secret",
                )
            )
        )
        self.assertFalse((self.private / "Results").exists())
        self.assertFalse((self.private / "Settlement").exists())


if __name__ == "__main__":
    unittest.main()
