"""Manual one-shot H26K result supervisor for the fixed local engineering proof."""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

from phase1h import execution, seal_supervisor, supervisor


RESULT_SUPERVISOR_VERSION = "oddswell-local-result-supervisor-v1"
APPROVED_SUPERVISOR_SHA256 = (
    "5ab65177e9fba3149b014b95ff7cb93b04f07e25028c41abdbe0e73d631686ef"
)
APPROVED_SEAL_SUPERVISOR_SHA256 = (
    "7a49cc3f912241d1b0e5140c403d83d4f67b4b139b47e006d2a67e80ded3d716"
)
APPROVED_RESULT_SHA256 = (
    "05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289"
)
PRIVATE_ROOT = (
    supervisor.REPOSITORY_ROOT
    / "client"
    / "OddsWell"
    / "Saved"
    / "Evidence"
    / "Phase1H26Y-20260728"
    / "PrivateExecution"
)
HANDOFF_DIRECTORY = seal_supervisor.HANDOFF_DIRECTORY
RECEIPT_DIRECTORY = seal_supervisor.RECEIPT_DIRECTORY
SEAL_DIRECTORY = seal_supervisor.SEAL_DIRECTORY
RESULT_DIRECTORY = PRIVATE_ROOT / "Results"
ATTEMPT_DIRECTORY = PRIVATE_ROOT / "ResultAttempts"
LOG_DIRECTORY = PRIVATE_ROOT / "ResultLogs"


def _validate_allowlist() -> None:
    supervisor._validate_allowlist()
    controls = (
        (supervisor.__file__, APPROVED_SUPERVISOR_SHA256),
        (seal_supervisor.__file__, APPROVED_SEAL_SUPERVISOR_SHA256),
    )
    if any(
        hashlib.sha256(Path(path).read_bytes()).hexdigest() != approved
        for path, approved in controls
    ):
        raise supervisor.SupervisorError("supervisor_control_not_allowlisted")


def _load_evidence() -> tuple[
    execution.ExecutionCommitment,
    dict[str, object],
    dict[str, object],
]:
    try:
        return execution._sealed_execution_evidence(
            HANDOFF_DIRECTORY,
            RECEIPT_DIRECTORY,
            SEAL_DIRECTORY,
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise supervisor.SupervisorError("sealed_evidence_rejected") from error


def _validated_result(
    commitment: execution.ExecutionCommitment,
    seal: dict[str, object],
) -> Path | None:
    expected = RESULT_DIRECTORY / f"{commitment.commitment_sha256}.json"
    results = sorted(RESULT_DIRECTORY.glob("*.json")) if RESULT_DIRECTORY.exists() else []
    if not results:
        return None
    if results != [expected]:
        raise supervisor.SupervisorError("result_set_conflicts")
    try:
        record = execution._validate_result_record(
            expected.read_text(encoding="utf-8"),
            commitment,
            seal,
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise supervisor.SupervisorError("result_rejected") from error
    if record["record_sha256"] != APPROVED_RESULT_SHA256:
        raise supervisor.SupervisorError("result_rejected")
    return expected


def _reserve_attempt(commitment_sha256: str) -> tuple[Path, bool]:
    return supervisor._reserve_claim(
        ATTEMPT_DIRECTORY,
        commitment_sha256,
        "oddswell-local-result-supervisor-attempt-v1",
        RESULT_SUPERVISOR_VERSION,
    )


def _run_child(result_name: str) -> tuple[str, int]:
    return supervisor._run_execution_child(
        (
            HANDOFF_DIRECTORY,
            RECEIPT_DIRECTORY,
            SEAL_DIRECTORY,
            RESULT_DIRECTORY,
        ),
        result_name,
        "recorded",
    )


def _append_log(
    commitment_sha256: str,
    started: str,
    started_monotonic: float,
    status: str,
    exit_code: int,
) -> None:
    supervisor._append_log(
        commitment_sha256,
        started,
        started_monotonic,
        status,
        exit_code,
        LOG_DIRECTORY,
        RESULT_SUPERVISOR_VERSION,
    )


def run_result_supervisor() -> tuple[str, Path]:
    _validate_allowlist()
    commitment, _, seal_record = _load_evidence()
    started = supervisor._timestamp()
    started_monotonic = time.monotonic()
    result = _validated_result(commitment, seal_record)
    if result is not None:
        _append_log(commitment.commitment_sha256, started, started_monotonic, "duplicate", 0)
        return "duplicate", result

    _, created = _reserve_attempt(commitment.commitment_sha256)
    if not created:
        result = _validated_result(commitment, seal_record)
        if result is not None:
            _append_log(
                commitment.commitment_sha256,
                started,
                started_monotonic,
                "duplicate",
                0,
            )
            return "duplicate", result
        _append_log(
            commitment.commitment_sha256,
            started,
            started_monotonic,
            "uncertain_prior_attempt",
            -1,
        )
        raise supervisor.SupervisorError("uncertain_prior_attempt")

    expected = RESULT_DIRECTORY / f"{commitment.commitment_sha256}.json"
    try:
        status, exit_code = _run_child(expected.name)
        result = _validated_result(commitment, seal_record)
        if result != expected:
            raise supervisor.SupervisorError("exact_result_required", exit_code)
    except supervisor.SupervisorError as error:
        _append_log(
            commitment.commitment_sha256,
            started,
            started_monotonic,
            error.code,
            error.exit_code,
        )
        raise
    _append_log(commitment.commitment_sha256, started, started_monotonic, status, exit_code)
    return status, result


def _main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments:
        print("rejected: arguments_not_allowed", file=sys.stderr)
        return 2
    try:
        status, result = run_result_supervisor()
    except supervisor.SupervisorError as error:
        print(f"rejected: {error.code}", file=sys.stderr)
        return 1
    print(f"{status}: {result.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
