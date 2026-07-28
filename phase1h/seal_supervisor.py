"""Manual one-shot H26J seal supervisor for the fixed local engineering proof."""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

from phase1h import execution, supervisor


SEAL_SUPERVISOR_VERSION = "oddswell-local-seal-supervisor-v1"
APPROVED_CONTROL_SHA256 = (
    "5ab65177e9fba3149b014b95ff7cb93b04f07e25028c41abdbe0e73d631686ef"
)
UPSTREAM_PRIVATE_ROOT = (
    supervisor.REPOSITORY_ROOT
    / "client"
    / "OddsWell"
    / "Saved"
    / "Evidence"
    / "Phase1H26W-20260728"
    / "UserDirFinal"
    / "Saved"
    / "PrivateExecution"
)
PRIVATE_ROOT = (
    supervisor.REPOSITORY_ROOT
    / "client"
    / "OddsWell"
    / "Saved"
    / "Evidence"
    / "Phase1H26X-20260728"
    / "PrivateExecution"
)
HANDOFF_DIRECTORY = UPSTREAM_PRIVATE_ROOT / "Handoff"
RECEIPT_DIRECTORY = UPSTREAM_PRIVATE_ROOT / "Receipts"
SEAL_DIRECTORY = PRIVATE_ROOT / "Seals"
ATTEMPT_DIRECTORY = PRIVATE_ROOT / "SealAttempts"
LOG_DIRECTORY = PRIVATE_ROOT / "SealLogs"


def _validate_allowlist() -> None:
    supervisor._validate_allowlist()
    if (
        hashlib.sha256(Path(supervisor.__file__).read_bytes()).hexdigest()
        != APPROVED_CONTROL_SHA256
    ):
        raise supervisor.SupervisorError("supervisor_control_not_allowlisted")


def _load_evidence() -> tuple[
    execution.ExecutionCommitment,
    dict[str, object],
]:
    try:
        return execution._execution_evidence(HANDOFF_DIRECTORY, RECEIPT_DIRECTORY)
    except (OSError, UnicodeError, ValueError) as error:
        raise supervisor.SupervisorError("handoff_or_receipt_rejected") from error


def _validated_seal(
    commitment: execution.ExecutionCommitment,
    receipt: dict[str, object],
) -> Path | None:
    expected = SEAL_DIRECTORY / f"{commitment.commitment_sha256}.json"
    seals = sorted(SEAL_DIRECTORY.glob("*.json")) if SEAL_DIRECTORY.exists() else []
    if not seals:
        return None
    if seals != [expected]:
        raise supervisor.SupervisorError("seal_set_conflicts")
    try:
        execution._validate_seal(expected.read_text(encoding="utf-8"), commitment, receipt)
    except (OSError, UnicodeError, ValueError) as error:
        raise supervisor.SupervisorError("seal_rejected") from error
    return expected


def _reserve_attempt(commitment_sha256: str) -> tuple[Path, bool]:
    return supervisor._reserve_claim(
        ATTEMPT_DIRECTORY,
        commitment_sha256,
        "oddswell-local-seal-supervisor-attempt-v1",
        SEAL_SUPERVISOR_VERSION,
    )


def _run_child(seal_name: str) -> tuple[str, int]:
    return supervisor._run_execution_child(
        (HANDOFF_DIRECTORY, RECEIPT_DIRECTORY, SEAL_DIRECTORY),
        seal_name,
        "sealed",
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
        SEAL_SUPERVISOR_VERSION,
    )


def run_seal_supervisor() -> tuple[str, Path]:
    _validate_allowlist()
    commitment, receipt_record = _load_evidence()
    started = supervisor._timestamp()
    started_monotonic = time.monotonic()
    seal = _validated_seal(commitment, receipt_record)
    if seal is not None:
        _append_log(commitment.commitment_sha256, started, started_monotonic, "duplicate", 0)
        return "duplicate", seal

    _, created = _reserve_attempt(commitment.commitment_sha256)
    if not created:
        seal = _validated_seal(commitment, receipt_record)
        if seal is not None:
            _append_log(
                commitment.commitment_sha256,
                started,
                started_monotonic,
                "duplicate",
                0,
            )
            return "duplicate", seal
        _append_log(
            commitment.commitment_sha256,
            started,
            started_monotonic,
            "uncertain_prior_attempt",
            -1,
        )
        raise supervisor.SupervisorError("uncertain_prior_attempt")

    expected = SEAL_DIRECTORY / f"{commitment.commitment_sha256}.json"
    try:
        status, exit_code = _run_child(expected.name)
        seal = _validated_seal(commitment, receipt_record)
        if seal != expected:
            raise supervisor.SupervisorError("exact_seal_required", exit_code)
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
    return status, seal


def _main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments:
        print("rejected: arguments_not_allowed", file=sys.stderr)
        return 2
    try:
        status, seal = run_seal_supervisor()
    except supervisor.SupervisorError as error:
        print(f"rejected: {error.code}", file=sys.stderr)
        return 1
    print(f"{status}: {seal.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
