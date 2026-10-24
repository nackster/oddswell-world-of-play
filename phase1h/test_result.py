import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from phase1h import execution
from phase1h.test_execution import OLD_ARCHIVE_REPLAY_SEAL, canonical
from phase1h.test_seal import evidence


def sealed_evidence(root: str) -> tuple[Path, Path, Path, Path]:
    handoff_dir, receipt_dir, seal_dir = evidence(root)
    execution.seal_execution_receipt(handoff_dir, receipt_dir, seal_dir)
    return handoff_dir, receipt_dir, seal_dir, Path(root) / "results"


def rehash(record: dict[str, object]) -> None:
    body = dict(record)
    body.pop("record_sha256", None)
    record["record_sha256"] = hashlib.sha256(canonical(body).encode()).hexdigest()


class PrivateCanonicalGameResultTests(unittest.TestCase):
    def test_records_once_then_cold_duplicate_recomputes_without_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir, receipt_dir, seal_dir, result_dir = sealed_evidence(root)
            real_simulator = execution.simulate_scheduled_game
            with patch.object(
                execution,
                "simulate_scheduled_game",
                wraps=real_simulator,
            ) as simulator:
                status, result_path = execution.record_game_result(
                    handoff_dir,
                    receipt_dir,
                    seal_dir,
                    result_dir,
                )
                self.assertEqual(status, "recorded")
                self.assertEqual(simulator.call_count, 1)
                before = (
                    result_path.read_bytes(),
                    hashlib.sha256(result_path.read_bytes()).hexdigest(),
                    result_path.stat().st_mtime_ns,
                )
                duplicate, duplicate_path = execution.record_game_result(
                    handoff_dir,
                    receipt_dir,
                    seal_dir,
                    result_dir,
                )
                self.assertEqual(duplicate, "duplicate")
                self.assertEqual(duplicate_path, result_path)
                self.assertEqual(simulator.call_count, 2)
                self.assertEqual(
                    before,
                    (
                        result_path.read_bytes(),
                        hashlib.sha256(result_path.read_bytes()).hexdigest(),
                        result_path.stat().st_mtime_ns,
                    ),
                )
            record = json.loads(result_path.read_text(encoding="utf-8"))
            seal = json.loads(next(seal_dir.glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(record["season_number"], 1)
            self.assertEqual(record["game_number"], 1)
            self.assertEqual(record["home_team"], "Harbor City Waves")
            self.assertEqual(record["away_team"], "Mesa Vista Sol")
            self.assertEqual(
                record["winner"],
                record["home_team"]
                if record["home_score"] > record["away_score"]
                else record["away_team"],
            )
            self.assertEqual(
                record["replay_sha256"],
                seal["verified_output_digest_sha256"],
            )
            self.assertNotEqual(record["replay_sha256"], OLD_ARCHIVE_REPLAY_SEAL)
            self.assertEqual(
                set(record),
                {
                    "away_score",
                    "away_team",
                    "commitment_sha256",
                    "game_number",
                    "home_score",
                    "home_team",
                    "record_sha256",
                    "record_version",
                    "recorder_version",
                    "replay_sha256",
                    "schema",
                    "seal_sha256",
                    "season_number",
                    "status",
                    "winner",
                },
            )

    def test_invalid_upstream_and_impossible_simulator_results_fail_closed(self) -> None:
        for missing in ("handoff", "receipt", "seal"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as root:
                handoff_dir, receipt_dir, seal_dir, result_dir = sealed_evidence(root)
                target = {
                    "handoff": handoff_dir,
                    "receipt": receipt_dir,
                    "seal": seal_dir,
                }[missing]
                next(target.glob("*.json")).unlink()
                with patch.object(execution, "simulate_scheduled_game") as simulator:
                    with self.assertRaises(ValueError):
                        execution.record_game_result(
                            handoff_dir,
                            receipt_dir,
                            seal_dir,
                            result_dir,
                        )
                    simulator.assert_not_called()

        for multiple in ("handoff", "receipt", "seal"):
            with self.subTest(multiple=multiple), tempfile.TemporaryDirectory() as root:
                handoff_dir, receipt_dir, seal_dir, result_dir = sealed_evidence(root)
                target = {
                    "handoff": handoff_dir,
                    "receipt": receipt_dir,
                    "seal": seal_dir,
                }[multiple]
                source = next(target.glob("*.json"))
                (target / "extra.json").write_bytes(source.read_bytes())
                with patch.object(execution, "simulate_scheduled_game") as simulator:
                    with self.assertRaises(ValueError):
                        execution.record_game_result(
                            handoff_dir,
                            receipt_dir,
                            seal_dir,
                            result_dir,
                        )
                    simulator.assert_not_called()

        for malformed in ("handoff", "receipt", "seal"):
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as root:
                handoff_dir, receipt_dir, seal_dir, result_dir = sealed_evidence(root)
                target = {
                    "handoff": handoff_dir,
                    "receipt": receipt_dir,
                    "seal": seal_dir,
                }[malformed]
                path = next(target.glob("*.json"))
                path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
                with patch.object(execution, "simulate_scheduled_game") as simulator:
                    with self.assertRaises(ValueError):
                        execution.record_game_result(
                            handoff_dir,
                            receipt_dir,
                            seal_dir,
                            result_dir,
                        )
                    simulator.assert_not_called()

        with tempfile.TemporaryDirectory() as root:
            handoff_dir, receipt_dir, seal_dir, result_dir = sealed_evidence(root)
            commitment = execution.validate_execution_handoff(
                next(handoff_dir.glob("*.json")).read_text(encoding="utf-8")
            )
            exact = execution._simulate_result(commitment)
            invalid = {
                "digest": replace(exact, replay_sha256="0" * 64),
                "home_team": replace(exact, home_team="Wrong Team"),
                "away_team": replace(exact, away_team="Wrong Team"),
                "tie": replace(
                    exact,
                    away_score=exact.home_score,
                    winner=exact.home_team,
                ),
                "negative": replace(exact, home_score=-1),
                "winner": replace(
                    exact,
                    winner=(
                        exact.away_team
                        if exact.winner == exact.home_team
                        else exact.home_team
                    ),
                ),
            }
            for label, result in invalid.items():
                with self.subTest(simulator=label), patch.object(
                    execution,
                    "_simulate_result",
                    return_value=result,
                ) as simulator:
                    with self.assertRaises(ValueError):
                        execution.record_game_result(
                            handoff_dir,
                            receipt_dir,
                            seal_dir,
                            result_dir,
                        )
                    simulator.assert_called_once()
                    self.assertFalse(list(result_dir.glob("*.json")))

    def test_result_tamper_valid_rehash_and_multiple_never_repair(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            handoff_dir, receipt_dir, seal_dir, result_dir = sealed_evidence(root)
            _, result_path = execution.record_game_result(
                handoff_dir,
                receipt_dir,
                seal_dir,
                result_dir,
            )
            original = json.loads(result_path.read_text(encoding="utf-8"))
            mutations = {
                "schema": lambda value: value.update(schema="wrong"),
                "version": lambda value: value.update(record_version=2),
                "status": lambda value: value.update(status="decided"),
                "recorder": lambda value: value.update(recorder_version="future"),
                "commitment": lambda value: value.update(commitment_sha256="0" * 64),
                "seal": lambda value: value.update(seal_sha256="0" * 64),
                "season": lambda value: value.update(season_number=2),
                "game": lambda value: value.update(game_number=2),
                "home_team": lambda value: value.update(home_team="Wrong Team"),
                "away_team": lambda value: value.update(away_team="Wrong Team"),
                "home_score": lambda value: value.update(
                    home_score=value["home_score"] + 1
                ),
                "away_score": lambda value: value.update(
                    away_score=value["away_score"] + 1
                ),
                "tie": lambda value: value.update(away_score=value["home_score"]),
                "negative": lambda value: value.update(home_score=-1),
                "winner": lambda value: value.update(
                    winner=(
                        value["away_team"]
                        if value["winner"] == value["home_team"]
                        else value["home_team"]
                    )
                ),
                "replay": lambda value: value.update(replay_sha256="0" * 64),
                "extra": lambda value: value.update(statistics={}),
                "missing": lambda value: value.pop("status"),
                "record_hash": lambda value: value.update(record_sha256="0" * 64),
            }
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    value = copy.deepcopy(original)
                    mutate(value)
                    if label != "record_hash":
                        rehash(value)
                    tampered = canonical(value)
                    result_path.write_text(tampered, encoding="utf-8")
                    with patch.object(
                        execution,
                        "_simulate_result",
                        wraps=execution._simulate_result,
                    ):
                        with self.assertRaises(ValueError):
                            execution.record_game_result(
                                handoff_dir,
                                receipt_dir,
                                seal_dir,
                                result_dir,
                            )
                    self.assertEqual(result_path.read_text(encoding="utf-8"), tampered)
            result_path.write_text(canonical(original), encoding="utf-8")
            (result_dir / "extra.json").write_text(canonical(original), encoding="utf-8")
            with patch.object(execution, "_simulate_result") as simulator:
                with self.assertRaises(ValueError):
                    execution.record_game_result(
                        handoff_dir,
                        receipt_dir,
                        seal_dir,
                        result_dir,
                    )
                simulator.assert_not_called()


if __name__ == "__main__":
    unittest.main()
