"""Offline parity proof for the private canonical active-game commitment."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from phase0a.simulator import BRAIN_VERSION, ENGINE_VERSION, default_teams
from phase0d.consistency import (
    DEFAULT_CONSISTENCY_VERSION,
    consistency_snapshot,
)
from phase0d.involvement import (
    DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
    production_involvement_snapshot,
)
from phase0d.league import (
    FATIGUE_MODEL_VERSION,
    INJURY_MODEL_VERSION,
    LEAGUE_VERSION,
    ScheduledGame,
    empty_availability,
    empty_fatigue,
    empty_readiness,
    simulate_scheduled_game,
)
from phase0d.life import DEFAULT_LIFE_BRAIN_VERSION


SCHEMA = "oddswell-canonical-active-game-execution-commitment-v1"
RECORD_VERSION = 1
SEED_DERIVATION_VERSION = "oddswell-canonical-active-game-seed-v1"
STATUS = "committed_for_execution"
ENVIRONMENT = "local_beta"
EXPECTED_PREGAME_COMMITMENT_SHA256 = (
    "898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f"
)
EXECUTOR_VERSION = "oddswell-private-game-executor-v1"
RECEIPT_SCHEMA = "oddswell-private-game-execution-receipt-v1"
RECEIPT_STATUS = "executed_pending_seal"
VERIFIER_VERSION = "oddswell-private-game-digest-verifier-v1"
SEAL_SCHEMA = "oddswell-private-game-execution-digest-seal-v1"
SEAL_STATUS = "sealed_pending_result"
_FORBIDDEN_HANDOFF_KEY_PARTS = (
    "offer_id",
    "request",
    "selection",
    "stake",
    "balance",
    "ledger",
    "lock_command",
    "accepted_unix",
    "output",
)


@dataclass(frozen=True)
class ExecutionCommitment:
    seed_material_json: str
    seed_material_sha256: str
    execution_seed: int
    execution_input_json: str
    execution_input_sha256: str
    commitment_json: str
    commitment_sha256: str


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _require_upstream(schedule: dict[str, object], pregame_sha256: str) -> None:
    required = {
        "schema",
        "record_version",
        "season_number",
        "game_number",
        "home_team",
        "away_team",
        "season_created_unix",
        "tipoff_unix",
        "offer_eligible_unix",
        "status",
        "environment",
        "timing_authority",
        "production_timing",
        "offer_published",
    }
    if (
        set(schedule) != required
        or schedule["schema"] != "oddswell-canonical-scheduled-game-v1"
        or schedule["record_version"] != 1
        or schedule["season_number"] != 1
        or schedule["game_number"] != 1
        or schedule["home_team"] != "Harbor City Waves"
        or schedule["away_team"] != "Mesa Vista Sol"
        or not isinstance(schedule["season_created_unix"], int)
        or isinstance(schedule["season_created_unix"], bool)
        or schedule["season_created_unix"] <= 0
        or schedule["tipoff_unix"] != schedule["season_created_unix"] + 1800
        or schedule["offer_eligible_unix"] != schedule["season_created_unix"]
        or schedule["status"] != "scheduled_unplayed"
        or schedule["environment"] != ENVIRONMENT
        or schedule["timing_authority"] != "server"
        or schedule["production_timing"] is not False
        or schedule["offer_published"] is not False
        or pregame_sha256 != EXPECTED_PREGAME_COMMITMENT_SHA256
    ):
        raise ValueError("exact immutable H26A/H26B evidence is required")


def active_game_execution_commitment(
    schedule: dict[str, object],
    pregame_sha256: str,
) -> ExecutionCommitment:
    _require_upstream(schedule, pregame_sha256)
    seed_material = {
        "away_team": schedule["away_team"],
        "domain": SEED_DERIVATION_VERSION,
        "environment": schedule["environment"],
        "game_number": schedule["game_number"],
        "home_team": schedule["home_team"],
        "offer_eligible_unix": schedule["offer_eligible_unix"],
        "offer_published": schedule["offer_published"],
        "pregame_commitment_sha256": pregame_sha256,
        "production_timing": schedule["production_timing"],
        "schedule_created_unix": schedule["season_created_unix"],
        "schedule_record_version": schedule["record_version"],
        "schedule_schema": schedule["schema"],
        "schedule_status": schedule["status"],
        "schedule_tipoff_unix": schedule["tipoff_unix"],
        "season_number": schedule["season_number"],
        "timing_authority": schedule["timing_authority"],
    }
    seed_material_json = _canonical_json(seed_material)
    seed_material_sha256 = hashlib.sha256(seed_material_json.encode()).hexdigest()
    execution_seed = int.from_bytes(bytes.fromhex(seed_material_sha256)[:4], "big") & 0x7FFFFFFF

    teams = default_teams()
    execution_input = {
        "brain_version": BRAIN_VERSION,
        "consistency_snapshot": [
            {"athlete": athlete, "cap": cap, "strength": strength, "tier": tier}
            for athlete, tier, strength, cap in consistency_snapshot(
                DEFAULT_CONSISTENCY_VERSION, teams
            )
        ],
        "consistency_version": DEFAULT_CONSISTENCY_VERSION,
        "engine_version": ENGINE_VERSION,
        "fatigue_model_version": FATIGUE_MODEL_VERSION,
        "injury_model_version": INJURY_MODEL_VERSION,
        "league_version": LEAGUE_VERSION,
        "life_decisions": [],
        "life_policy_version": DEFAULT_LIFE_BRAIN_VERSION,
        "matchup": [
            {
                "roster": [
                    {
                        "defense": athlete.defense,
                        "name": athlete.name,
                        "passing": athlete.passing,
                        "rebounding": athlete.rebounding,
                        "shooting": athlete.shooting,
                        "stamina": athlete.stamina,
                    }
                    for athlete in team.players
                ],
                "side": side,
                "team": team.name,
            }
            for side, team in zip(("home", "away"), teams)
        ],
        "offensive_involvement_snapshot": [
            {"athlete": athlete, "tier": tier, "weight": weight}
            for athlete, tier, weight in production_involvement_snapshot(
                DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION, teams
            )
        ],
        "offensive_involvement_version": DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
        "opening_availability": [
            {"athlete": athlete, "recovery_days": recovery_days}
            for athlete, recovery_days in empty_availability(teams)
        ],
        "opening_fatigue": [
            {"athlete": athlete, "value": value}
            for athlete, value in empty_fatigue(teams)
        ],
        "opening_readiness": [
            {"athlete": athlete, "value": value}
            for athlete, value in empty_readiness(teams)
        ],
        "player_points_capture": False,
        "schedule": {
            "away_team": schedule["away_team"],
            "game_number": schedule["game_number"],
            "home_team": schedule["home_team"],
            "seed": execution_seed,
        },
        "simulation_function": "simulate_scheduled_game",
    }
    execution_input_json = _canonical_json(execution_input)
    execution_input_sha256 = hashlib.sha256(execution_input_json.encode()).hexdigest()
    commitment = {
        "away_team": schedule["away_team"],
        "environment": ENVIRONMENT,
        "execution_input_sha256": execution_input_sha256,
        "execution_seed": execution_seed,
        "game_number": schedule["game_number"],
        "home_team": schedule["home_team"],
        "offer_eligible_unix": schedule["offer_eligible_unix"],
        "pregame_commitment_sha256": pregame_sha256,
        "record_version": RECORD_VERSION,
        "schedule_created_unix": schedule["season_created_unix"],
        "schedule_record_version": schedule["record_version"],
        "schedule_schema": schedule["schema"],
        "schedule_tipoff_unix": schedule["tipoff_unix"],
        "schema": SCHEMA,
        "seed_derivation_version": SEED_DERIVATION_VERSION,
        "seed_material_sha256": seed_material_sha256,
        "season_number": schedule["season_number"],
        "status": STATUS,
    }
    commitment_json = _canonical_json(commitment)
    return ExecutionCommitment(
        seed_material_json,
        seed_material_sha256,
        execution_seed,
        execution_input_json,
        execution_input_sha256,
        commitment_json,
        hashlib.sha256(commitment_json.encode()).hexdigest(),
    )


def dry_simulation_manifest_hash(commitment: ExecutionCommitment) -> str:
    """Resolve twice in memory and return only the identical private manifest hash."""
    if (
        hashlib.sha256(commitment.seed_material_json.encode()).hexdigest()
        != commitment.seed_material_sha256
        or hashlib.sha256(commitment.execution_input_json.encode()).hexdigest()
        != commitment.execution_input_sha256
        or hashlib.sha256(commitment.commitment_json.encode()).hexdigest()
        != commitment.commitment_sha256
    ):
        raise ValueError("execution commitment hashes do not verify")
    first = _simulate_once(commitment)
    second = _simulate_once(commitment)
    if first != second:
        raise RuntimeError("identical execution commitments produced different manifests")
    return first


def _simulate_once(commitment: ExecutionCommitment) -> str:
    values = json.loads(commitment.execution_input_json)
    teams = default_teams()
    fixture = ScheduledGame(1, commitment.execution_seed, teams[0], teams[1])
    consistency = tuple(
        (row["athlete"], row["tier"], row["strength"], row["cap"])
        for row in values["consistency_snapshot"]
    )
    involvement = tuple(
        (row["athlete"], row["tier"], row["weight"])
        for row in values["offensive_involvement_snapshot"]
    )
    arguments = (
        fixture,
        empty_fatigue(teams),
        empty_availability(teams),
        teams,
        empty_readiness(teams),
        (),
    )
    options = {
        "life_policy_version": values["life_policy_version"],
        "consistency_version": values["consistency_version"],
        "stored_consistency_snapshot": consistency,
        "offensive_involvement_version": values["offensive_involvement_version"],
        "stored_offensive_involvement_snapshot": involvement,
    }
    return simulate_scheduled_game(*arguments, **options).replay_sha256


def canonical_execution_handoff(
    schedule: dict[str, object],
    pregame_sha256: str,
) -> str:
    commitment = active_game_execution_commitment(schedule, pregame_sha256)
    return _canonical_json(
        {
            "away_team": schedule["away_team"],
            "commitment": json.loads(commitment.commitment_json),
            "commitment_sha256": commitment.commitment_sha256,
            "environment": ENVIRONMENT,
            "execution_input": json.loads(commitment.execution_input_json),
            "execution_input_sha256": commitment.execution_input_sha256,
            "execution_seed": commitment.execution_seed,
            "game_number": schedule["game_number"],
            "home_team": schedule["home_team"],
            "offer_eligible_unix": schedule["offer_eligible_unix"],
            "pregame_commitment_sha256": pregame_sha256,
            "record_version": RECORD_VERSION,
            "schedule_created_unix": schedule["season_created_unix"],
            "schedule_record_version": schedule["record_version"],
            "schedule_schema": schedule["schema"],
            "schedule_tipoff_unix": schedule["tipoff_unix"],
            "schema": SCHEMA,
            "season_number": schedule["season_number"],
            "seed_derivation_version": SEED_DERIVATION_VERSION,
            "seed_material": json.loads(commitment.seed_material_json),
            "seed_material_sha256": commitment.seed_material_sha256,
            "status": STATUS,
        }
    )


def _loads_exact_json(raw: str) -> dict[str, object]:
    def no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    try:
        value = json.loads(raw, object_pairs_hook=no_duplicates)
    except (json.JSONDecodeError, ValueError) as error:
        raise ValueError("private execution JSON is malformed") from error
    if not isinstance(value, dict) or _canonical_json(value) != raw:
        raise ValueError("private execution JSON is not exact canonical JSON")
    return value


def _reject_forbidden_handoff_keys(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if any(part in key for part in _FORBIDDEN_HANDOFF_KEY_PARTS):
                raise ValueError("private execution handoff contains a forbidden field")
            _reject_forbidden_handoff_keys(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_handoff_keys(item)


def validate_execution_handoff(raw: str) -> ExecutionCommitment:
    handoff = _loads_exact_json(raw)
    _reject_forbidden_handoff_keys(handoff)
    expected_keys = {
        "away_team",
        "commitment",
        "commitment_sha256",
        "environment",
        "execution_input",
        "execution_input_sha256",
        "execution_seed",
        "game_number",
        "home_team",
        "offer_eligible_unix",
        "pregame_commitment_sha256",
        "record_version",
        "schedule_created_unix",
        "schedule_record_version",
        "schedule_schema",
        "schedule_tipoff_unix",
        "schema",
        "season_number",
        "seed_derivation_version",
        "seed_material",
        "seed_material_sha256",
        "status",
    }
    if set(handoff) != expected_keys or not isinstance(handoff["seed_material"], dict):
        raise ValueError("private execution handoff fields are not exact")
    seed_material = handoff["seed_material"]
    try:
        schedule = {
            "schema": handoff["schedule_schema"],
            "record_version": handoff["schedule_record_version"],
            "season_number": handoff["season_number"],
            "game_number": handoff["game_number"],
            "home_team": handoff["home_team"],
            "away_team": handoff["away_team"],
            "season_created_unix": handoff["schedule_created_unix"],
            "tipoff_unix": handoff["schedule_tipoff_unix"],
            "offer_eligible_unix": handoff["offer_eligible_unix"],
            "status": seed_material["schedule_status"],
            "environment": handoff["environment"],
            "timing_authority": seed_material["timing_authority"],
            "production_timing": seed_material["production_timing"],
            "offer_published": seed_material["offer_published"],
        }
        pregame_sha256 = handoff["pregame_commitment_sha256"]
        expected_raw = canonical_execution_handoff(schedule, pregame_sha256)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("private execution handoff is not exact H26H evidence") from error
    if raw != expected_raw:
        raise ValueError("private execution handoff conflicts with exact H26H evidence")
    return active_game_execution_commitment(schedule, pregame_sha256)


def _valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _validate_receipt(
    raw: str,
    commitment: ExecutionCommitment,
) -> dict[str, object]:
    receipt = _loads_exact_json(raw)
    expected_keys = {
        "commitment_sha256",
        "execution_input_sha256",
        "executor_version",
        "output_digest_sha256",
        "receipt_sha256",
        "record_version",
        "schema",
        "status",
    }
    if (
        set(receipt) != expected_keys
        or receipt["schema"] != RECEIPT_SCHEMA
        or receipt["record_version"] != 1
        or receipt["commitment_sha256"] != commitment.commitment_sha256
        or receipt["execution_input_sha256"] != commitment.execution_input_sha256
        or receipt["executor_version"] != EXECUTOR_VERSION
        or receipt["status"] != RECEIPT_STATUS
        or not _valid_sha256(receipt["output_digest_sha256"])
    ):
        raise ValueError("private execution receipt conflicts with the handoff")
    body = dict(receipt)
    receipt_sha256 = body.pop("receipt_sha256")
    if (
        not _valid_sha256(receipt_sha256)
        or hashlib.sha256(_canonical_json(body).encode()).hexdigest() != receipt_sha256
    ):
        raise ValueError("private execution receipt hash does not verify")
    return receipt


def _write_atomically(path: Path, raw: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.stem}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(raw)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def consume_execution_handoff(
    handoff_directory: str | Path,
    receipt_directory: str | Path,
) -> tuple[str, Path]:
    handoffs = sorted(Path(handoff_directory).glob("*.json"))
    if len(handoffs) != 1:
        raise ValueError("exactly one private execution handoff is required")
    raw_handoff = handoffs[0].read_text(encoding="utf-8")
    commitment = validate_execution_handoff(raw_handoff)
    receipt_directory = Path(receipt_directory)
    receipt_path = receipt_directory / f"{commitment.commitment_sha256}.json"
    receipts = sorted(receipt_directory.glob("*.json")) if receipt_directory.exists() else []
    if receipts:
        if receipts != [receipt_path]:
            raise ValueError("private execution receipt set conflicts with the handoff")
        _validate_receipt(receipt_path.read_text(encoding="utf-8"), commitment)
        return "duplicate", receipt_path

    output_digest = _simulate_once(commitment)
    if not _valid_sha256(output_digest):
        raise RuntimeError("private execution produced an invalid output digest")
    body = {
        "commitment_sha256": commitment.commitment_sha256,
        "execution_input_sha256": commitment.execution_input_sha256,
        "executor_version": EXECUTOR_VERSION,
        "output_digest_sha256": output_digest,
        "record_version": 1,
        "schema": RECEIPT_SCHEMA,
        "status": RECEIPT_STATUS,
    }
    receipt = dict(body)
    receipt["receipt_sha256"] = hashlib.sha256(_canonical_json(body).encode()).hexdigest()
    raw_receipt = _canonical_json(receipt)
    _write_atomically(receipt_path, raw_receipt)
    _validate_receipt(receipt_path.read_text(encoding="utf-8"), commitment)
    return "executed", receipt_path


def _execution_evidence(
    handoff_directory: str | Path,
    receipt_directory: str | Path,
) -> tuple[ExecutionCommitment, dict[str, object]]:
    handoffs = sorted(Path(handoff_directory).glob("*.json"))
    if len(handoffs) != 1:
        raise ValueError("exactly one private execution handoff is required")
    commitment = validate_execution_handoff(handoffs[0].read_text(encoding="utf-8"))
    receipt_path = Path(receipt_directory) / f"{commitment.commitment_sha256}.json"
    receipts = sorted(Path(receipt_directory).glob("*.json"))
    if receipts != [receipt_path]:
        raise ValueError("exactly one matching private execution receipt is required")
    receipt = _validate_receipt(receipt_path.read_text(encoding="utf-8"), commitment)
    return commitment, receipt


def _validate_seal(
    raw: str,
    commitment: ExecutionCommitment,
    receipt: dict[str, object],
) -> dict[str, object]:
    seal = _loads_exact_json(raw)
    expected_keys = {
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
    }
    if (
        set(seal) != expected_keys
        or seal["schema"] != SEAL_SCHEMA
        or seal["record_version"] != 1
        or seal["commitment_sha256"] != commitment.commitment_sha256
        or seal["execution_input_sha256"] != commitment.execution_input_sha256
        or seal["receipt_sha256"] != receipt["receipt_sha256"]
        or seal["executor_version"] != EXECUTOR_VERSION
        or seal["verifier_version"] != VERIFIER_VERSION
        or seal["verified_output_digest_sha256"]
        != receipt["output_digest_sha256"]
        or seal["status"] != SEAL_STATUS
    ):
        raise ValueError("private execution digest seal conflicts with exact evidence")
    body = dict(seal)
    seal_sha256 = body.pop("seal_sha256")
    if (
        not _valid_sha256(seal_sha256)
        or hashlib.sha256(_canonical_json(body).encode()).hexdigest() != seal_sha256
    ):
        raise ValueError("private execution digest seal hash does not verify")
    return seal


def seal_execution_receipt(
    handoff_directory: str | Path,
    receipt_directory: str | Path,
    seal_directory: str | Path,
) -> tuple[str, Path]:
    commitment, receipt = _execution_evidence(
        handoff_directory,
        receipt_directory,
    )
    seal_path = Path(seal_directory) / f"{commitment.commitment_sha256}.json"
    seals = sorted(Path(seal_directory).glob("*.json")) if Path(seal_directory).exists() else []
    if seals:
        if seals != [seal_path]:
            raise ValueError("private execution digest seal set conflicts with evidence")
        _validate_seal(
            seal_path.read_text(encoding="utf-8"),
            commitment,
            receipt,
        )
        return "duplicate", seal_path

    verified_output_digest = _simulate_once(commitment)
    if (
        not _valid_sha256(verified_output_digest)
        or verified_output_digest != receipt["output_digest_sha256"]
    ):
        raise ValueError("private execution digest does not match the receipt")
    body = {
        "commitment_sha256": commitment.commitment_sha256,
        "execution_input_sha256": commitment.execution_input_sha256,
        "executor_version": EXECUTOR_VERSION,
        "receipt_sha256": receipt["receipt_sha256"],
        "record_version": 1,
        "schema": SEAL_SCHEMA,
        "status": SEAL_STATUS,
        "verified_output_digest_sha256": verified_output_digest,
        "verifier_version": VERIFIER_VERSION,
    }
    seal = dict(body)
    seal["seal_sha256"] = hashlib.sha256(_canonical_json(body).encode()).hexdigest()
    _write_atomically(seal_path, _canonical_json(seal))
    _validate_seal(
        seal_path.read_text(encoding="utf-8"),
        commitment,
        receipt,
    )
    return "sealed", seal_path


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Consume one private OddsWell H26H handoff.")
    parser.add_argument("handoff_directory")
    parser.add_argument("receipt_directory")
    parser.add_argument("seal_directory", nargs="?")
    args = parser.parse_args()
    if args.seal_directory:
        status, output_path = seal_execution_receipt(
            args.handoff_directory,
            args.receipt_directory,
            args.seal_directory,
        )
    else:
        status, output_path = consume_execution_handoff(
            args.handoff_directory,
            args.receipt_directory,
        )
    print(f"{status}: {output_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
