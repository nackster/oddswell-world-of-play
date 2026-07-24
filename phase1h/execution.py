"""Offline parity proof for the private canonical active-game commitment."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

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
        or len(pregame_sha256) != 64
        or any(character not in "0123456789abcdef" for character in pregame_sha256)
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
    first = simulate_scheduled_game(*arguments, **options).replay_sha256
    second = simulate_scheduled_game(*arguments, **options).replay_sha256
    if first != second:
        raise RuntimeError("identical execution commitments produced different manifests")
    return first
