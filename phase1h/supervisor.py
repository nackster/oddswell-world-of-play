"""Manual one-shot H26I supervisor for the fixed local engineering workspace."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from phase1h import execution


SUPERVISOR_VERSION = "oddswell-local-execution-supervisor-v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = (
    REPOSITORY_ROOT
    / "client"
    / "OddsWell"
    / "Saved"
    / "Evidence"
    / "Phase1H26W-20260728"
    / "UserDirFinal"
    / "Saved"
    / "PrivateExecution"
)
HANDOFF_DIRECTORY = PRIVATE_ROOT / "Handoff"
RECEIPT_DIRECTORY = PRIVATE_ROOT / "Receipts"
ATTEMPT_DIRECTORY = PRIVATE_ROOT / "SupervisorAttempts"
LOG_DIRECTORY = PRIVATE_ROOT / "SupervisorLogs"
APPROVED_PYTHON = Path(
    r"C:\Users\reali\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)
APPROVED_PYTHON_VERSION = "3.12.13"
APPROVED_FROZEN_MANIFEST_SHA256 = (
    "6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c"
)
MODULE = "phase1h.execution"
TIMEOUT_SECONDS = 120
OUTPUT_LIMIT = 256
_SUPERVISOR_FILES = {
    Path("phase1h/supervisor.py"),
    Path("phase1h/test_supervisor.py"),
}


class SupervisorError(RuntimeError):
    def __init__(self, code: str, exit_code: int = -1) -> None:
        super().__init__(code)
        self.code = code
        self.exit_code = exit_code


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _frozen_manifest_sha256() -> str:
    files = sorted(
        path
        for directory in ("phase0a", "phase0d", "phase1h")
        for path in (REPOSITORY_ROOT / directory).rglob("*.py")
        if path.relative_to(REPOSITORY_ROOT) not in _SUPERVISOR_FILES
    )
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
        f"{path.relative_to(REPOSITORY_ROOT)}"
        for path in files
    ]
    if len(lines) != 28:
        raise SupervisorError("frozen_revision_not_allowlisted")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _validate_allowlist() -> None:
    try:
        approved = APPROVED_PYTHON.resolve(strict=True)
        running = Path(sys.executable).resolve(strict=True)
    except OSError as error:
        raise SupervisorError("interpreter_not_allowlisted") from error
    if (
        not APPROVED_PYTHON.is_absolute()
        or os.path.normcase(approved) != os.path.normcase(APPROVED_PYTHON)
        or os.path.normcase(running) != os.path.normcase(approved)
        or f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        != APPROVED_PYTHON_VERSION
        or _frozen_manifest_sha256() != APPROVED_FROZEN_MANIFEST_SHA256
    ):
        raise SupervisorError("interpreter_or_revision_not_allowlisted")


def _load_commitment() -> execution.ExecutionCommitment:
    handoffs = sorted(HANDOFF_DIRECTORY.glob("*.json")) if HANDOFF_DIRECTORY.exists() else []
    if len(handoffs) != 1:
        raise SupervisorError("exactly_one_handoff_required")
    try:
        return execution.validate_execution_handoff(handoffs[0].read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise SupervisorError("handoff_rejected") from error


def _validated_receipt(
    commitment: execution.ExecutionCommitment,
) -> Path | None:
    expected = RECEIPT_DIRECTORY / f"{commitment.commitment_sha256}.json"
    receipts = sorted(RECEIPT_DIRECTORY.glob("*.json")) if RECEIPT_DIRECTORY.exists() else []
    if not receipts:
        return None
    if receipts != [expected]:
        raise SupervisorError("receipt_set_conflicts")
    try:
        execution._validate_receipt(expected.read_text(encoding="utf-8"), commitment)
    except (OSError, UnicodeError, ValueError) as error:
        raise SupervisorError("receipt_rejected") from error
    return expected


def _reserve_attempt(commitment_sha256: str) -> tuple[Path, bool]:
    ATTEMPT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    claim = ATTEMPT_DIRECTORY / f"{commitment_sha256}.json"
    claims = sorted(ATTEMPT_DIRECTORY.glob("*.json"))
    if claims and claims != [claim]:
        raise SupervisorError("attempt_set_conflicts")
    raw = _canonical_json(
        {
            "commitment_sha256": commitment_sha256,
            "record_version": 1,
            "schema": "oddswell-local-execution-supervisor-attempt-v1",
            "status": "attempt_reserved",
            "supervisor_version": SUPERVISOR_VERSION,
        }
    )
    try:
        descriptor = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return claim, False
    except OSError as error:
        raise SupervisorError("attempt_claim_failed") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise SupervisorError("attempt_claim_failed") from error
    return claim, True


def _job_for(process: subprocess.Popen[str]) -> tuple[object, int]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = ctypes.c_void_p
    kernel32.AssignProcessToJobObject.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
    kernel32.AssignProcessToJobObject.restype = ctypes.c_int
    job = kernel32.CreateJobObjectW(None, None)
    if not job or not kernel32.AssignProcessToJobObject(job, int(process._handle)):
        if job:
            kernel32.CloseHandle(job)
        process.kill()
        process.wait()
        raise SupervisorError("child_job_failed")
    return kernel32, job


def _run_child(receipt_name: str) -> tuple[str, int]:
    command = [
        str(APPROVED_PYTHON),
        "-B",
        "-m",
        MODULE,
        str(HANDOFF_DIRECTORY),
        str(RECEIPT_DIRECTORY),
    ]
    environment = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
        "SYSTEMROOT": r"C:\Windows",
        "WINDIR": r"C:\Windows",
    }
    try:
        process = subprocess.Popen(
            command,
            cwd=REPOSITORY_ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NO_WINDOW,
        )
    except OSError as error:
        raise SupervisorError("child_start_failed") from error
    kernel32, job = _job_for(process)
    try:
        try:
            output, _ = process.communicate(timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as error:
            kernel32.TerminateJobObject(job, 124)
            process.communicate()
            raise SupervisorError("child_timeout", 124) from error
    finally:
        kernel32.CloseHandle(job)
    if process.returncode != 0:
        raise SupervisorError("child_nonzero_exit", process.returncode)
    if len(output.encode("utf-8")) > OUTPUT_LIMIT:
        raise SupervisorError("child_output_rejected", process.returncode)
    line = output.strip()
    allowed = {f"executed: {receipt_name}", f"duplicate: {receipt_name}"}
    if line not in allowed:
        raise SupervisorError("child_output_rejected", process.returncode)
    return line.split(":", 1)[0], process.returncode


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _append_log(
    commitment_sha256: str,
    started: str,
    started_monotonic: float,
    status: str,
    exit_code: int,
) -> None:
    record = {
        "commitment_sha256": commitment_sha256,
        "duration_ms": max(0, round((time.monotonic() - started_monotonic) * 1000)),
        "ended_utc": _timestamp(),
        "exit_code": exit_code,
        "interpreter": str(APPROVED_PYTHON),
        "interpreter_version": APPROVED_PYTHON_VERSION,
        "module": MODULE,
        "started_utc": started,
        "status": status,
        "supervisor_version": SUPERVISOR_VERSION,
    }
    raw = _canonical_json(record)
    if len(raw.encode("utf-8")) > 1024:
        raise SupervisorError("audit_log_rejected")
    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
    path = LOG_DIRECTORY / f"{commitment_sha256}.jsonl"
    try:
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(raw + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise SupervisorError("audit_log_failed") from error


def run_supervisor() -> tuple[str, Path]:
    _validate_allowlist()
    commitment = _load_commitment()
    started = _timestamp()
    started_monotonic = time.monotonic()
    receipt = _validated_receipt(commitment)
    if receipt is not None:
        _append_log(commitment.commitment_sha256, started, started_monotonic, "duplicate", 0)
        return "duplicate", receipt

    _, created = _reserve_attempt(commitment.commitment_sha256)
    if not created:
        receipt = _validated_receipt(commitment)
        if receipt is not None:
            _append_log(commitment.commitment_sha256, started, started_monotonic, "duplicate", 0)
            return "duplicate", receipt
        _append_log(
            commitment.commitment_sha256,
            started,
            started_monotonic,
            "uncertain_prior_attempt",
            -1,
        )
        raise SupervisorError("uncertain_prior_attempt")

    expected = RECEIPT_DIRECTORY / f"{commitment.commitment_sha256}.json"
    try:
        status, exit_code = _run_child(expected.name)
        receipt = _validated_receipt(commitment)
        if receipt != expected:
            raise SupervisorError("exact_receipt_required", exit_code)
    except SupervisorError as error:
        _append_log(
            commitment.commitment_sha256,
            started,
            started_monotonic,
            error.code,
            error.exit_code,
        )
        raise
    _append_log(commitment.commitment_sha256, started, started_monotonic, status, exit_code)
    return status, receipt


def _main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments:
        print("rejected: arguments_not_allowed", file=sys.stderr)
        return 2
    try:
        status, receipt = run_supervisor()
    except SupervisorError as error:
        print(f"rejected: {error.code}", file=sys.stderr)
        return 1
    print(f"{status}: {receipt.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
