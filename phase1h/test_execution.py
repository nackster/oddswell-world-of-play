import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phase1h import execution


OLD_ARCHIVE_REPLAY_SEAL = (
    "00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75"
)


def schedule() -> dict[str, object]:
    return {
        "schema": "oddswell-canonical-scheduled-game-v1",
        "record_version": 1,
        "season_number": 1,
        "game_number": 1,
        "home_team": "Harbor City Waves",
        "away_team": "Mesa Vista Sol",
        "season_created_unix": 2_200_000_000,
        "tipoff_unix": 2_200_001_800,
        "offer_eligible_unix": 2_200_000_000,
        "status": "scheduled_unplayed",
        "environment": "local_beta",
        "timing_authority": "server",
        "production_timing": False,
        "offer_published": False,
    }


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


class PrivateExecutionReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.handoff = execution.canonical_execution_handoff(
            schedule(),
            execution.EXPECTED_PREGAME_COMMITMENT_SHA256,
        )

    def test_executes_once_then_cold_duplicate_never_reexecutes(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir = Path(root) / "handoff"
            receipt_dir = Path(root) / "receipts"
            handoff_dir.mkdir()
            (handoff_dir / "handoff.json").write_text(self.handoff, encoding="utf-8")
            real_simulator = execution.simulate_scheduled_game
            with patch.object(
                execution,
                "simulate_scheduled_game",
                wraps=real_simulator,
            ) as simulator:
                status, receipt_path = execution.consume_execution_handoff(
                    handoff_dir,
                    receipt_dir,
                )
                self.assertEqual(status, "executed")
                self.assertEqual(simulator.call_count, 1)
                before = (
                    receipt_path.read_bytes(),
                    hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
                    receipt_path.stat().st_mtime_ns,
                )
                duplicate, duplicate_path = execution.consume_execution_handoff(
                    handoff_dir,
                    receipt_dir,
                )
                self.assertEqual(duplicate, "duplicate")
                self.assertEqual(duplicate_path, receipt_path)
                self.assertEqual(simulator.call_count, 1)
                self.assertEqual(
                    before,
                    (
                        receipt_path.read_bytes(),
                        hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
                        receipt_path.stat().st_mtime_ns,
                    ),
                )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            commitment = execution.validate_execution_handoff(self.handoff)
            self.assertEqual(
                receipt["output_digest_sha256"],
                execution._simulate_once(commitment),
            )
            self.assertNotEqual(receipt["output_digest_sha256"], OLD_ARCHIVE_REPLAY_SEAL)
            self.assertEqual(
                set(receipt),
                {
                    "commitment_sha256",
                    "execution_input_sha256",
                    "executor_version",
                    "output_digest_sha256",
                    "receipt_sha256",
                    "record_version",
                    "schema",
                    "status",
                },
            )
            self.assertFalse(
                {
                    "score",
                    "winner",
                    "tape",
                    "event_log",
                    "replay",
                    "settlement",
                    "odds_bucks",
                }
                & set(receipt)
            )

    def test_handoff_tamper_extra_forbidden_and_exact_input_fail_closed(self) -> None:
        exact = json.loads(self.handoff)
        mutations = {
            "schema": lambda value: value.update(schema="wrong"),
            "status": lambda value: value.update(status="executed"),
            "record_version": lambda value: value.update(record_version=2),
            "commitment_hash": lambda value: value.update(commitment_sha256="0" * 64),
            "input_hash": lambda value: value.update(execution_input_sha256="0" * 64),
            "seed_hash": lambda value: value.update(seed_material_sha256="0" * 64),
            "seed": lambda value: value.update(execution_seed=1),
            "extra": lambda value: value.update(extra=True),
            "missing": lambda value: value.pop("environment"),
            "forbidden": lambda value: value["execution_input"].update(selection="home"),
            "engine_version": lambda value: value["execution_input"].update(
                engine_version="future"
            ),
            "roster": lambda value: value["execution_input"]["matchup"][0]["roster"][
                0
            ].update(shooting=99),
            "consistency": lambda value: value["execution_input"][
                "consistency_snapshot"
            ][0].update(cap=0.07),
            "involvement": lambda value: value["execution_input"][
                "offensive_involvement_snapshot"
            ][0].update(weight=1.2),
            "fatigue": lambda value: value["execution_input"]["opening_fatigue"][
                0
            ].update(value=0.1),
            "availability": lambda value: value["execution_input"][
                "opening_availability"
            ][0].update(recovery_days=1),
            "readiness": lambda value: value["execution_input"]["opening_readiness"][
                0
            ].update(value=0.1),
            "life": lambda value: value["execution_input"].update(
                life_decisions=[{"athlete": "Jalen Cross"}]
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                value = copy.deepcopy(exact)
                mutate(value)
                with self.assertRaises(ValueError):
                    execution.validate_execution_handoff(canonical(value))
        with self.assertRaises(ValueError):
            execution.validate_execution_handoff(self.handoff + "\n")
        duplicate_key = self.handoff.replace(
            '{"away_team":',
            '{"away_team":"Mesa Vista Sol","away_team":',
            1,
        )
        with self.assertRaises(ValueError):
            execution.validate_execution_handoff(duplicate_key)

    def test_missing_multiple_and_tampered_receipts_never_run_or_repair(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir = Path(root) / "handoff"
            receipt_dir = Path(root) / "receipts"
            handoff_dir.mkdir()
            with self.assertRaises(ValueError):
                execution.consume_execution_handoff(handoff_dir, receipt_dir)
            (handoff_dir / "one.json").write_text(self.handoff, encoding="utf-8")
            (handoff_dir / "two.json").write_text(self.handoff, encoding="utf-8")
            with self.assertRaises(ValueError):
                execution.consume_execution_handoff(handoff_dir, receipt_dir)
            (handoff_dir / "two.json").unlink()
            with patch.object(execution, "simulate_scheduled_game") as simulator:
                simulator.return_value.replay_sha256 = "invalid"
                with self.assertRaises(RuntimeError):
                    execution.consume_execution_handoff(handoff_dir, receipt_dir)
            self.assertFalse(list(receipt_dir.glob("*.json")))
            _, receipt_path = execution.consume_execution_handoff(
                handoff_dir,
                receipt_dir,
            )
            original = json.loads(receipt_path.read_text(encoding="utf-8"))
            mutations = {
                "schema": lambda value: value.update(schema="wrong"),
                "version": lambda value: value.update(record_version=2),
                "commitment": lambda value: value.update(commitment_sha256="0" * 64),
                "input": lambda value: value.update(execution_input_sha256="0" * 64),
                "executor": lambda value: value.update(executor_version="future"),
                "status": lambda value: value.update(status="sealed"),
                "output": lambda value: value.update(output_digest_sha256="0" * 64),
                "receipt_hash": lambda value: value.update(receipt_sha256="0" * 64),
                "extra": lambda value: value.update(score=101),
                "missing": lambda value: value.pop("status"),
            }
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    value = copy.deepcopy(original)
                    mutate(value)
                    tampered = canonical(value)
                    receipt_path.write_text(tampered, encoding="utf-8")
                    with patch.object(execution, "simulate_scheduled_game") as simulator:
                        with self.assertRaises(ValueError):
                            execution.consume_execution_handoff(
                                handoff_dir,
                                receipt_dir,
                            )
                        simulator.assert_not_called()
                    self.assertEqual(receipt_path.read_text(encoding="utf-8"), tampered)
            receipt_path.write_text(canonical(original), encoding="utf-8")
            (receipt_dir / "extra.json").write_text(canonical(original), encoding="utf-8")
            with patch.object(execution, "simulate_scheduled_game") as simulator:
                with self.assertRaises(ValueError):
                    execution.consume_execution_handoff(handoff_dir, receipt_dir)
                simulator.assert_not_called()


if __name__ == "__main__":
    unittest.main()
