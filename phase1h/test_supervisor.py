import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from phase1h import execution, supervisor


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


class FakeProcess:
    def __init__(self, output: str = "", returncode: int = 0, timeout: bool = False) -> None:
        self.output = output
        self.returncode = returncode
        self.timeout = timeout
        self._handle = 1
        self.killed = False
        self.communications = 0

    def communicate(self, timeout: int | None = None) -> tuple[str, None]:
        self.communications += 1
        if self.timeout and self.communications == 1:
            raise subprocess.TimeoutExpired("child", timeout)
        return self.output, None

    def kill(self) -> None:
        self.killed = True

    def wait(self) -> int:
        return self.returncode


class FakeKernel:
    def __init__(self) -> None:
        self.terminated = False
        self.closed = False

    def TerminateJobObject(self, job: int, code: int) -> int:
        self.terminated = job == 1 and code == 124
        return 1

    def CloseHandle(self, job: int) -> int:
        self.closed = job == 1
        return 1


class LocalExecutionSupervisorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.private = Path(self.temporary.name) / "PrivateExecution"
        self.patches = [
            patch.object(supervisor, "PRIVATE_ROOT", self.private),
            patch.object(supervisor, "HANDOFF_DIRECTORY", self.private / "Handoff"),
            patch.object(supervisor, "RECEIPT_DIRECTORY", self.private / "Receipts"),
            patch.object(
                supervisor,
                "ATTEMPT_DIRECTORY",
                self.private / "SupervisorAttempts",
            ),
            patch.object(supervisor, "LOG_DIRECTORY", self.private / "SupervisorLogs"),
        ]
        for active in self.patches:
            active.start()
        self.handoff = execution.canonical_execution_handoff(
            schedule(), execution.EXPECTED_PREGAME_COMMITMENT_SHA256
        )
        self.commitment = execution.validate_execution_handoff(self.handoff)

    def tearDown(self) -> None:
        for active in reversed(self.patches):
            active.stop()
        self.temporary.cleanup()

    def write_handoff(self, name: str = "handoff.json", raw: str | None = None) -> Path:
        supervisor.HANDOFF_DIRECTORY.mkdir(parents=True, exist_ok=True)
        path = supervisor.HANDOFF_DIRECTORY / name
        path.write_text(self.handoff if raw is None else raw, encoding="utf-8")
        return path

    def reset_private(self) -> None:
        shutil.rmtree(self.private, ignore_errors=True)

    def test_01_game_package_boundary_has_no_client_python_launcher(self) -> None:
        client_source = supervisor.REPOSITORY_ROOT / "client" / "OddsWell" / "Source"
        forbidden = (
            "FPlatformProcess::CreateProc",
            "CreateProcessW(",
            "ShellExecuteW(",
            "python.exe",
            "phase1h.execution",
        )
        source = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in client_source.rglob("*")
            if path.suffix in {".cpp", ".h"}
        )
        self.assertFalse(any(value in source for value in forbidden))
        self.assertFalse(
            any(
                path.suffix == ".py"
                for path in (supervisor.REPOSITORY_ROOT / "client" / "OddsWell").rglob("*")
                if "Saved" not in path.parts and "Intermediate" not in path.parts
            )
        )

    def test_02_entry_is_manual_and_accepts_no_arguments(self) -> None:
        with patch.object(supervisor, "run_supervisor") as run, contextlib.redirect_stderr(
            io.StringIO()
        ):
            self.assertEqual(supervisor._main(["--path", "elsewhere"]), 2)
        run.assert_not_called()
        self.assertEqual(
            supervisor.HANDOFF_DIRECTORY,
            self.private / "Handoff",
        )
        self.assertEqual(supervisor.RECEIPT_DIRECTORY, self.private / "Receipts")

    def test_03_interpreter_revision_module_and_directories_are_allowlisted(self) -> None:
        supervisor._validate_allowlist()
        self.assertTrue(supervisor.APPROVED_PYTHON.is_absolute())
        self.assertEqual(supervisor.MODULE, "phase1h.execution")
        self.assertEqual(
            supervisor._frozen_manifest_sha256(),
            supervisor.APPROVED_FROZEN_MANIFEST_SHA256,
        )
        with patch.object(supervisor, "APPROVED_PYTHON", Path("python.exe")):
            with self.assertRaisesRegex(supervisor.SupervisorError, "allowlisted"):
                supervisor._validate_allowlist()

    def test_04_arguments_environment_ports_and_network_cannot_reach_child(self) -> None:
        malicious = ["--module", "evil", "--port", "80", "--path", "elsewhere"]
        with patch.object(supervisor.subprocess, "Popen") as popen, contextlib.redirect_stderr(
            io.StringIO()
        ):
            self.assertEqual(supervisor._main(malicious), 2)
        popen.assert_not_called()

        expected_name = f"{self.commitment.commitment_sha256}.json"
        fake = FakeProcess(f"executed: {expected_name}\n")
        kernel = FakeKernel()
        with patch.object(supervisor.subprocess, "Popen", return_value=fake) as popen, patch.object(
            supervisor, "_job_for", return_value=(kernel, 1)
        ):
            status, _ = supervisor._run_child(expected_name)
        self.assertEqual(status, "executed")
        command = popen.call_args.args[0]
        options = popen.call_args.kwargs
        self.assertEqual(command[0], str(supervisor.APPROVED_PYTHON))
        self.assertEqual(command[1:4], ["-B", "-m", "phase1h.execution"])
        self.assertEqual(command[4:], [str(supervisor.HANDOFF_DIRECTORY), str(supervisor.RECEIPT_DIRECTORY)])
        self.assertEqual(
            set(options["env"]),
            {"PYTHONDONTWRITEBYTECODE", "PYTHONNOUSERSITE", "PYTHONUTF8", "SYSTEMROOT", "WINDIR"},
        )
        self.assertNotIn("PATH", options["env"])

    def test_05_fresh_handoff_claims_once_runs_one_child_and_writes_receipt(self) -> None:
        self.write_handoff()
        with patch.object(supervisor, "_run_child", wraps=supervisor._run_child) as child:
            status, receipt = supervisor.run_supervisor()
        self.assertEqual(status, "executed")
        self.assertEqual(child.call_count, 1)
        self.assertEqual(receipt.name, f"{self.commitment.commitment_sha256}.json")
        execution._validate_receipt(receipt.read_text(encoding="utf-8"), self.commitment)
        claim = supervisor.ATTEMPT_DIRECTORY / receipt.name
        self.assertTrue(claim.is_file())
        self.assertEqual(
            json.loads(claim.read_text(encoding="utf-8"))["status"],
            "attempt_reserved",
        )

    def test_06_concurrent_supervisors_launch_exactly_one_child(self) -> None:
        self.write_handoff()
        entered = threading.Event()
        release = threading.Event()

        def consume_once(receipt_name: str) -> tuple[str, int]:
            entered.set()
            self.assertTrue(release.wait(5))
            status, receipt = execution.consume_execution_handoff(
                supervisor.HANDOFF_DIRECTORY,
                supervisor.RECEIPT_DIRECTORY,
            )
            self.assertEqual(receipt.name, receipt_name)
            return status, 0

        with patch.object(supervisor, "_run_child", side_effect=consume_once) as child, ThreadPoolExecutor(
            max_workers=2
        ) as pool:
            first = pool.submit(supervisor.run_supervisor)
            self.assertTrue(entered.wait(5))
            second = pool.submit(supervisor.run_supervisor)
            with self.assertRaisesRegex(supervisor.SupervisorError, "uncertain_prior_attempt"):
                second.result(timeout=5)
            release.set()
            self.assertEqual(first.result(timeout=5)[0], "executed")
        self.assertEqual(child.call_count, 1)

    def test_07_exact_receipt_is_duplicate_without_child_or_rewrite(self) -> None:
        self.write_handoff()
        _, receipt = execution.consume_execution_handoff(
            supervisor.HANDOFF_DIRECTORY,
            supervisor.RECEIPT_DIRECTORY,
        )
        before = (
            receipt.read_bytes(),
            hashlib.sha256(receipt.read_bytes()).hexdigest(),
            receipt.stat().st_mtime_ns,
        )
        with patch.object(supervisor, "_run_child") as child:
            status, duplicate = supervisor.run_supervisor()
        self.assertEqual((status, duplicate), ("duplicate", receipt))
        child.assert_not_called()
        self.assertEqual(
            before,
            (
                receipt.read_bytes(),
                hashlib.sha256(receipt.read_bytes()).hexdigest(),
                receipt.stat().st_mtime_ns,
            ),
        )

    def test_08_bad_handoff_or_receipt_stops_without_execution_or_repair(self) -> None:
        with patch.object(supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "one_handoff"):
                supervisor.run_supervisor()
        child.assert_not_called()

        self.write_handoff("one.json")
        self.write_handoff("two.json")
        with patch.object(supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "one_handoff"):
                supervisor.run_supervisor()
        child.assert_not_called()

        self.reset_private()
        tampered_handoff = self.write_handoff(raw=self.handoff.replace('"status":"committed_for_execution"', '"status":"wrong"'))
        before_handoff = tampered_handoff.read_bytes()
        with patch.object(supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "handoff_rejected"):
                supervisor.run_supervisor()
        child.assert_not_called()
        self.assertEqual(tampered_handoff.read_bytes(), before_handoff)

        self.reset_private()
        self.write_handoff()
        _, receipt = execution.consume_execution_handoff(
            supervisor.HANDOFF_DIRECTORY,
            supervisor.RECEIPT_DIRECTORY,
        )
        receipt.write_text(receipt.read_text(encoding="utf-8").replace('"status":"executed_pending_seal"', '"status":"wrong"'), encoding="utf-8")
        before_receipt = receipt.read_bytes()
        with patch.object(supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "receipt_rejected"):
                supervisor.run_supervisor()
        child.assert_not_called()
        self.assertEqual(receipt.read_bytes(), before_receipt)
        (supervisor.RECEIPT_DIRECTORY / "extra.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(supervisor.SupervisorError, "receipt_set_conflicts"):
            supervisor.run_supervisor()

    def test_09_timeout_and_crash_retain_claim_and_stop_future_attempt(self) -> None:
        self.write_handoff()
        with patch.object(
            supervisor,
            "_run_child",
            side_effect=supervisor.SupervisorError("child_timeout", 124),
        ):
            with self.assertRaisesRegex(supervisor.SupervisorError, "child_timeout"):
                supervisor.run_supervisor()
        claim = supervisor.ATTEMPT_DIRECTORY / f"{self.commitment.commitment_sha256}.json"
        self.assertTrue(claim.is_file())
        with patch.object(supervisor, "_run_child") as child:
            with self.assertRaisesRegex(supervisor.SupervisorError, "uncertain_prior_attempt"):
                supervisor.run_supervisor()
        child.assert_not_called()

        fake = FakeProcess(timeout=True)
        kernel = FakeKernel()
        with patch.object(supervisor.subprocess, "Popen", return_value=fake), patch.object(
            supervisor, "_job_for", return_value=(kernel, 1)
        ):
            with self.assertRaisesRegex(supervisor.SupervisorError, "child_timeout"):
                supervisor._run_child(f"{self.commitment.commitment_sha256}.json")
        self.assertTrue(kernel.terminated)
        self.assertTrue(kernel.closed)

    def test_10_clean_exit_exact_receipt_and_output_are_all_required(self) -> None:
        self.write_handoff()
        with patch.object(supervisor, "_run_child", return_value=("executed", 0)):
            with self.assertRaisesRegex(supervisor.SupervisorError, "exact_receipt_required"):
                supervisor.run_supervisor()

        expected_name = f"{self.commitment.commitment_sha256}.json"
        for output, returncode, reason in (
            (f"executed: {expected_name}\n", 7, "child_nonzero_exit"),
            ("unexpected\n", 0, "child_output_rejected"),
            ("x" * (supervisor.OUTPUT_LIMIT + 1), 0, "child_output_rejected"),
        ):
            with self.subTest(reason=reason):
                fake = FakeProcess(output, returncode)
                kernel = FakeKernel()
                with patch.object(supervisor.subprocess, "Popen", return_value=fake), patch.object(
                    supervisor, "_job_for", return_value=(kernel, 1)
                ):
                    with self.assertRaisesRegex(supervisor.SupervisorError, reason):
                        supervisor._run_child(expected_name)

    def test_11_private_audit_log_contains_only_approved_bounded_metadata(self) -> None:
        self.write_handoff()
        execution.consume_execution_handoff(
            supervisor.HANDOFF_DIRECTORY,
            supervisor.RECEIPT_DIRECTORY,
        )
        supervisor.run_supervisor()
        log = supervisor.LOG_DIRECTORY / f"{self.commitment.commitment_sha256}.jsonl"
        raw = log.read_text(encoding="utf-8").strip()
        self.assertLessEqual(len(raw.encode("utf-8")), 1024)
        record = json.loads(raw)
        self.assertEqual(
            set(record),
            {
                "commitment_sha256",
                "duration_ms",
                "ended_utc",
                "exit_code",
                "interpreter",
                "interpreter_version",
                "module",
                "started_utc",
                "status",
                "supervisor_version",
            },
        )
        forbidden = ("seed_material", "execution_input", "output_digest", "score", "stake", "token", "secret")
        self.assertFalse(any(value in raw for value in forbidden))

    def test_12_frozen_runtime_and_downstream_boundaries_remain_unchanged(self) -> None:
        before = supervisor._frozen_manifest_sha256()
        self.write_handoff()
        execution.consume_execution_handoff(
            supervisor.HANDOFF_DIRECTORY,
            supervisor.RECEIPT_DIRECTORY,
        )
        supervisor.run_supervisor()
        self.assertEqual(before, supervisor.APPROVED_FROZEN_MANIFEST_SHA256)
        self.assertEqual(supervisor._frozen_manifest_sha256(), before)
        self.assertFalse((self.private / "Seals").exists())
        self.assertFalse((self.private / "Results").exists())
        self.assertFalse((self.private / "Settlement").exists())


if __name__ == "__main__":
    unittest.main()
