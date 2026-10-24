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

from phase1h import execution, result_supervisor, supervisor
from phase1h.test_result import rehash, sealed_evidence
from phase1h.test_supervisor import FakeKernel, FakeProcess


class LocalResultSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.upstream = Path(self.temporary.name) / "Upstream"
        self.private = Path(self.temporary.name) / "ResultProof"
        self.upstream.mkdir()
        handoff, receipt, seal, _ = sealed_evidence(str(self.upstream))
        self.patches = [
            patch.object(result_supervisor, "HANDOFF_DIRECTORY", handoff),
            patch.object(result_supervisor, "RECEIPT_DIRECTORY", receipt),
            patch.object(result_supervisor, "SEAL_DIRECTORY", seal),
            patch.object(result_supervisor, "PRIVATE_ROOT", self.private),
            patch.object(result_supervisor, "RESULT_DIRECTORY", self.private / "Results"),
            patch.object(
                result_supervisor,
                "ATTEMPT_DIRECTORY",
                self.private / "ResultAttempts",
            ),
            patch.object(result_supervisor, "LOG_DIRECTORY", self.private / "ResultLogs"),
        ]
        for active in self.patches:
            active.start()
        self.commitment, _, self.seal = execution._sealed_execution_evidence(
            result_supervisor.HANDOFF_DIRECTORY,
            result_supervisor.RECEIPT_DIRECTORY,
            result_supervisor.SEAL_DIRECTORY,
        )
        expected = execution._result_record(
            self.commitment,
            self.seal,
            execution._simulate_result(self.commitment),
        )["record_sha256"]
        self.approved = patch.object(result_supervisor, "APPROVED_RESULT_SHA256", expected)
        self.approved.start()

    def tearDown(self) -> None:
        self.approved.stop()
        for active in reversed(self.patches):
            active.stop()
        self.temporary.cleanup()

    def reset_evidence(self) -> None:
        shutil.rmtree(self.upstream, ignore_errors=True)
        shutil.rmtree(self.private, ignore_errors=True)
        self.upstream.mkdir()
        sealed_evidence(str(self.upstream))

    def test_01_allowlist_manual_entry_and_fixed_four_directory_child(self) -> None:
        result_supervisor._validate_allowlist()
        with patch.object(result_supervisor, "APPROVED_SEAL_SUPERVISOR_SHA256", "0" * 64):
            with self.assertRaisesRegex(supervisor.SupervisorError, "control_not_allowlisted"):
                result_supervisor._validate_allowlist()
        with patch.object(result_supervisor, "run_result_supervisor") as run, contextlib.redirect_stderr(
            io.StringIO()
        ):
            self.assertEqual(result_supervisor._main(["--score", "100-90"]), 2)
        run.assert_not_called()

        name = f"{self.commitment.commitment_sha256}.json"
        fake = FakeProcess(f"recorded: {name}\n")
        kernel = FakeKernel()
        with patch.object(supervisor.subprocess, "Popen", return_value=fake) as popen, patch.object(
            supervisor, "_job_for", return_value=(kernel, 1)
        ):
            self.assertEqual(result_supervisor._run_child(name), ("recorded", 0))
        self.assertEqual(
            popen.call_args.args[0],
            [
                str(supervisor.APPROVED_PYTHON),
                "-B",
                "-m",
                "phase1h.execution",
                str(result_supervisor.HANDOFF_DIRECTORY),
                str(result_supervisor.RECEIPT_DIRECTORY),
                str(result_supervisor.SEAL_DIRECTORY),
                str(result_supervisor.RESULT_DIRECTORY),
            ],
        )

    def test_02_fresh_evidence_claims_once_and_writes_exact_result(self) -> None:
        with patch.object(
            result_supervisor,
            "_run_child",
            wraps=result_supervisor._run_child,
        ) as child:
            status, path = result_supervisor.run_result_supervisor()
        self.assertEqual(status, "recorded")
        self.assertEqual(child.call_count, 1)
        record = execution._validate_result_record(
            path.read_text(encoding="utf-8"),
            self.commitment,
            self.seal,
        )
        self.assertEqual(record["status"], "recorded_pending_decision")
        self.assertEqual(record["record_sha256"], result_supervisor.APPROVED_RESULT_SHA256)
        self.assertEqual(record["replay_sha256"], self.seal["verified_output_digest_sha256"])
        self.assertEqual(
            record["winner"],
            record["home_team"]
            if record["home_score"] > record["away_score"]
            else record["away_team"],
        )

    def test_03_concurrent_supervisors_launch_exactly_one_child(self) -> None:
        entered = threading.Event()
        release = threading.Event()

        def record_once(result_name: str) -> tuple[str, int]:
            entered.set()
            self.assertTrue(release.wait(5))
            status, result = execution.record_game_result(
                result_supervisor.HANDOFF_DIRECTORY,
                result_supervisor.RECEIPT_DIRECTORY,
                result_supervisor.SEAL_DIRECTORY,
                result_supervisor.RESULT_DIRECTORY,
            )
            self.assertEqual(result.name, result_name)
            return status, 0

        with patch.object(
            result_supervisor,
            "_run_child",
            side_effect=record_once,
        ) as child, ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(result_supervisor.run_result_supervisor)
            self.assertTrue(entered.wait(5))
            second = pool.submit(result_supervisor.run_result_supervisor)
            with self.assertRaisesRegex(supervisor.SupervisorError, "uncertain_prior_attempt"):
                second.result(timeout=5)
            release.set()
            self.assertEqual(first.result(timeout=5)[0], "recorded")
        self.assertEqual(child.call_count, 1)

    def test_04_exact_result_is_duplicate_without_child_simulation_or_rewrite(self) -> None:
        _, result = execution.record_game_result(
            result_supervisor.HANDOFF_DIRECTORY,
            result_supervisor.RECEIPT_DIRECTORY,
            result_supervisor.SEAL_DIRECTORY,
            result_supervisor.RESULT_DIRECTORY,
        )
        paths = [
            *result_supervisor.HANDOFF_DIRECTORY.glob("*.json"),
            *result_supervisor.RECEIPT_DIRECTORY.glob("*.json"),
            *result_supervisor.SEAL_DIRECTORY.glob("*.json"),
            result,
        ]
        before = {
            path: (path.read_bytes(), hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
            for path in paths
        }
        with patch.object(result_supervisor, "_run_child") as child, patch.object(
            execution,
            "_simulate_result",
        ) as simulator:
            status, duplicate = result_supervisor.run_result_supervisor()
        self.assertEqual((status, duplicate), ("duplicate", result))
        child.assert_not_called()
        simulator.assert_not_called()
        self.assertEqual(
            before,
            {
                path: (
                    path.read_bytes(),
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    path.stat().st_mtime_ns,
                )
                for path in paths
            },
        )

    def test_05_missing_multiple_or_tampered_upstream_stops_without_child(self) -> None:
        directories = (
            result_supervisor.HANDOFF_DIRECTORY,
            result_supervisor.RECEIPT_DIRECTORY,
            result_supervisor.SEAL_DIRECTORY,
        )
        for directory in directories:
            with self.subTest(missing=directory.name):
                target = next(directory.glob("*.json"))
                raw = target.read_bytes()
                target.unlink()
                with patch.object(result_supervisor, "_run_child") as child:
                    with self.assertRaisesRegex(supervisor.SupervisorError, "rejected"):
                        result_supervisor.run_result_supervisor()
                child.assert_not_called()
                target.write_bytes(raw)
        for directory in directories:
            with self.subTest(multiple=directory.name):
                source = next(directory.glob("*.json"))
                extra = directory / "extra.json"
                extra.write_bytes(source.read_bytes())
                with patch.object(result_supervisor, "_run_child") as child:
                    with self.assertRaisesRegex(supervisor.SupervisorError, "rejected"):
                        result_supervisor.run_result_supervisor()
                child.assert_not_called()
                extra.unlink()

        seal = next(result_supervisor.SEAL_DIRECTORY.glob("*.json"))
        tampered = seal.read_text(encoding="utf-8").replace(
            '"status":"sealed_pending_result"',
            '"status":"wrong"',
        )
        seal.write_text(tampered, encoding="utf-8")
        with patch.object(result_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "rejected"):
                result_supervisor.run_result_supervisor()
        child.assert_not_called()
        self.assertEqual(seal.read_text(encoding="utf-8"), tampered)

    def test_06_validly_rehashed_score_tamper_and_multiple_result_are_not_repaired(self) -> None:
        _, result = execution.record_game_result(
            result_supervisor.HANDOFF_DIRECTORY,
            result_supervisor.RECEIPT_DIRECTORY,
            result_supervisor.SEAL_DIRECTORY,
            result_supervisor.RESULT_DIRECTORY,
        )
        original = json.loads(result.read_text(encoding="utf-8"))
        changed = dict(original)
        score = "home_score" if changed["winner"] == changed["home_team"] else "away_score"
        changed[score] += 1
        rehash(changed)
        tampered = execution._canonical_json(changed)
        result.write_text(tampered, encoding="utf-8")
        with patch.object(result_supervisor, "_run_child") as child, patch.object(
            execution,
            "_simulate_result",
        ) as simulator:
            with self.assertRaisesRegex(supervisor.SupervisorError, "result_rejected"):
                result_supervisor.run_result_supervisor()
        child.assert_not_called()
        simulator.assert_not_called()
        self.assertEqual(result.read_text(encoding="utf-8"), tampered)

        result.write_text(execution._canonical_json(original), encoding="utf-8")
        (result_supervisor.RESULT_DIRECTORY / "extra.json").write_text("{}", encoding="utf-8")
        with patch.object(result_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "result_set_conflicts"):
                result_supervisor.run_result_supervisor()
        child.assert_not_called()

    def test_07_timeout_retains_claim_and_blocks_retry(self) -> None:
        with patch.object(
            result_supervisor,
            "_run_child",
            side_effect=supervisor.SupervisorError("child_timeout", 124),
        ):
            with self.assertRaisesRegex(supervisor.SupervisorError, "child_timeout"):
                result_supervisor.run_result_supervisor()
        claim = result_supervisor.ATTEMPT_DIRECTORY / f"{self.commitment.commitment_sha256}.json"
        self.assertTrue(claim.is_file())
        with patch.object(result_supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "uncertain_prior_attempt"):
                result_supervisor.run_result_supervisor()
        child.assert_not_called()

    def test_08_exact_result_bounded_log_and_no_h26l_exist(self) -> None:
        with patch.object(result_supervisor, "_run_child", return_value=("recorded", 0)):
            with self.assertRaisesRegex(supervisor.SupervisorError, "exact_result_required"):
                result_supervisor.run_result_supervisor()

        self.reset_evidence()
        result_supervisor.run_result_supervisor()
        log = result_supervisor.LOG_DIRECTORY / f"{self.commitment.commitment_sha256}.jsonl"
        raw = log.read_text(encoding="utf-8").strip()
        record = json.loads(raw)
        self.assertLessEqual(len(raw.encode("utf-8")), 1024)
        self.assertEqual(record["status"], "recorded")
        self.assertEqual(record["supervisor_version"], result_supervisor.RESULT_SUPERVISOR_VERSION)
        self.assertFalse(
            any(
                key in raw
                for key in (
                    "home_score",
                    "away_score",
                    "winner",
                    "team",
                    "seed",
                    "digest",
                    "replay",
                )
            )
        )
        for later in ("Links", "Decisions", "Settlement", "History"):
            self.assertFalse((self.private / later).exists())


if __name__ == "__main__":
    unittest.main()
