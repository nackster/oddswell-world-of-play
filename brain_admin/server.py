from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import json
import os
import socket
import sys
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
INDEX = Path(__file__).with_name("index.html")
AUDIT_PATH = Path(__file__).with_name("admin-audit.log")
AUDIT_LOCK = threading.Lock()
sys.path.insert(0, str(ROOT))

from phase0a.simulator import (  # noqa: E402
    BRAIN_VERSION,
    ENGINE_VERSION,
    GameResult,
    Player,
    Team,
    default_teams,
    simulate_game,
)
from phase0c.policy import POLICY_VERSION  # noqa: E402
from phase0d.career import (  # noqa: E402
    CAREER_VERSION,
    DEBUT_AGES,
    REPLACEMENTS,
    RETIREMENT_AGE,
    RATING_NAMES,
    age_for_season,
    career_stage,
    career_status,
    debut_season,
    retirement_season,
    teams_for_season,
)
from phase0d.consistency import (  # noqa: E402
    DEFAULT_CONSISTENCY_VERSION,
    consistency_tier,
    shooting_consistency_settings,
)
from phase0d.league import (  # noqa: E402
    LEAGUE_VERSION,
    ScheduledGame,
    SeasonResult,
    new_league,
    simulate_next_season,
    simulate_scheduled_game,
)
from phase0d.involvement import (  # noqa: E402
    DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
    offensive_involvement_settings,
    production_involvement_tier,
)
from phase0d.life import DEFAULT_LIFE_BRAIN_VERSION  # noqa: E402
from phase0d.prediction import PREDICTION_VERSION, run_prediction_study  # noqa: E402


LEAGUE_VIEW_GAMES = 20
LEAGUE_VIEW_START_SEED = 15_000
CAREER_SEASONS = 4


def economy_projection_candidates() -> list[Path]:
    candidates = [ROOT / "client" / "OddsWell" / "Saved" / "Admin" / "OddsBucksReconciliation.json"]
    candidates.extend(ROOT.glob("client/OddsWell/Builds/*/Windows/OddsWell/Saved/Admin/OddsBucksReconciliation.json"))
    if local_app_data := os.environ.get("LOCALAPPDATA"):
        candidates.append(Path(local_app_data) / "OddsWell" / "Saved" / "Admin" / "OddsBucksReconciliation.json")
    return candidates


def match_winner_reconciliation_candidates() -> list[Path]:
    candidates = list((ROOT / "client" / "OddsWell" / "Saved" / "Admin").glob("MatchWinnerReconciliation*.json"))
    candidates.extend(ROOT.glob("client/OddsWell/Builds/*/Windows/OddsWell/Saved/Admin/MatchWinnerReconciliation*.json"))
    if local_app_data := os.environ.get("LOCALAPPDATA"):
        candidates.extend((Path(local_app_data) / "OddsWell" / "Saved" / "Admin").glob("MatchWinnerReconciliation*.json"))
    return candidates


def exact_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or int(value) != value:
        raise ValueError(f"{name} must be a whole number")
    return int(value)


def validated_economy_projection(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("projection must be a JSON object")
    expected = {
        "schema": "oddswell-odds-bucks-reconciliation-v1",
        "authority": "server",
        "currency": "odds_bucks",
        "profile_scope": "machine_local",
        "time_authority": "local_machine_utc",
        "read_only_projection": True,
        "job_payout": 100,
        "payout_interval_seconds": 86_400,
        "accumulation": True,
        "allowance": False,
    }
    for field, expected_value in expected.items():
        if data.get(field) != expected_value:
            raise ValueError(f"invalid {field}")
    if not isinstance(data.get("qa"), bool):
        raise ValueError("qa must be true or false")
    generated_at = data.get("generated_at_utc")
    if not isinstance(generated_at, str):
        raise ValueError("generated_at_utc must be text")
    datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    for field in ("observed_now_unix", "balance", "entry_count", "next_job_payout_unix"):
        data[field] = exact_integer(data.get(field), field)
    entries = data.get("entries")
    if not isinstance(entries, list) or len(entries) != data["entry_count"]:
        raise ValueError("entry_count does not match entries")
    balance = 0
    commands: set[str] = set()
    has_job_payout = False
    for sequence, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {sequence} must be an object")
        entry["sequence"] = exact_integer(entry.get("sequence"), f"entry {sequence} sequence")
        entry["delta"] = exact_integer(entry.get("delta"), f"entry {sequence} delta")
        entry["balance_after"] = exact_integer(entry.get("balance_after"), f"entry {sequence} balance_after")
        command = entry.get("command_id")
        reason = entry.get("reason")
        if entry["sequence"] != sequence or not isinstance(command, str) or not command.strip() or command in commands:
            raise ValueError(f"entry {sequence} has invalid identity")
        if not isinstance(reason, str) or not reason or entry["delta"] == 0:
            raise ValueError(f"entry {sequence} has invalid reason or delta")
        balance += entry["delta"]
        if balance < 0 or entry["balance_after"] != balance:
            raise ValueError(f"entry {sequence} has invalid running balance")
        commands.add(command)
        has_job_payout |= reason == "placeholder_job_payout"
    if balance != data["balance"]:
        raise ValueError("projection balance does not match its ledger")
    if (has_job_payout and data["next_job_payout_unix"] <= 0) or (not has_job_payout and data["next_job_payout_unix"] != 0):
        raise ValueError("job eligibility does not match its ledger")
    return data


def economy_payload(path: Path | None = None) -> dict[str, object]:
    if path is None:
        existing = [candidate for candidate in economy_projection_candidates() if candidate.is_file()]
        path = max(existing, key=lambda candidate: candidate.stat().st_mtime, default=None)
    if path is None:
        return {
            "available": False,
            "status": "NO LOCAL PROJECTION",
            "read_only": True,
            "entries": [],
            "boundary": "Launch the OddsWell client once to publish a local read-only ledger projection. No economy commands are available here.",
        }
    try:
        data = validated_economy_projection(path)
    except (OSError, ValueError, OverflowError, TypeError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return {
            "available": False,
            "status": "INVALID LOCAL PROJECTION",
            "read_only": True,
            "entries": [],
            "boundary": f"The local projection was rejected: {error}. No balance is shown and no command is available.",
        }
    now = data["observed_now_unix"] if data["qa"] else int(datetime.now(timezone.utc).timestamp())
    next_payout = data["next_job_payout_unix"]
    seconds_remaining = max(0, next_payout - now) if next_payout else 0
    return {
        "available": True,
        "status": "VALIDATED QA PROJECTION" if data["qa"] else "VALIDATED LOCAL PROJECTION",
        "read_only": True,
        "authority": data["authority"],
        "profile_scope": data["profile_scope"],
        "time_authority": data["time_authority"],
        "generated_at_utc": data["generated_at_utc"],
        "balance": data["balance"],
        "entry_count": data["entry_count"],
        "eligible_now": seconds_remaining == 0,
        "seconds_until_eligible": seconds_remaining,
        "next_job_payout_utc": datetime.fromtimestamp(next_payout, timezone.utc).isoformat().replace("+00:00", "Z") if next_payout else None,
        "job_payout": data["job_payout"],
        "payout_interval_seconds": data["payout_interval_seconds"],
        "accumulation": data["accumulation"],
        "allowance": data["allowance"],
        "entries": data["entries"],
        "boundary": "Read-only machine-local projection from the validated Unreal ledger. The local clock is not trusted production time; no account, backend, payment, wager, or mutation control is connected.",
    }


def validated_match_winner_reconciliation(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("projection must be a JSON object")
    expected = {
        "schema": "oddswell-match-winner-reconciliation-v1",
        "authority": "server",
        "profile_scope": "machine_local",
        "read_only_projection": True,
        "market": "match_winner",
        "offer_id": "9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459",
        "offer_version": "basketball-match-winner-odds-v1",
        "selected_team": "Harbor City Waves",
        "stake": 40,
        "request_status": "accepted_pending_lock",
        "stake_sequence": 2,
        "stake_delta": -40,
        "stake_reason": "match_winner_stake",
        "stake_balance_after": 60,
        "season_number": 1,
        "game_number": 1,
        "lock_decision": "locked",
        "result_schema": "oddswell-sealed-match-winner-result-v1",
        "result_version": "sealed-match-winner-result-v1",
        "home_team": "Harbor City Waves",
        "away_team": "Mesa Vista Sol",
        "home_score": 101,
        "away_score": 104,
        "winner": "Mesa Vista Sol",
        "replay_seal_sha256": "00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75",
        "decision_schema": "oddswell-match-winner-settlement-decision-v1",
        "decision_version": "match-winner-settlement-decision-v1",
        "decision_status": "decided_pending_apply",
        "outcome": "lost",
        "gross_return_due": 0,
        "finalization_schema": "oddswell-match-winner-loss-finalization-v1",
        "finalization_version": "match-winner-loss-finalization-v1",
        "finalization_status": "settled_lost",
        "gross_return_applied": 0,
        "ledger_entry_count": 2,
        "final_balance": 60,
        "net": -40,
    }
    for field, expected_value in expected.items():
        if data.get(field) != expected_value:
            raise ValueError(f"invalid {field}")
    if not isinstance(data.get("qa"), bool):
        raise ValueError("qa must be true or false")
    generated_at = data.get("generated_at_utc")
    if not isinstance(generated_at, str):
        raise ValueError("generated_at_utc must be text")
    datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    for field in (
        "stake", "stake_sequence", "stake_delta", "stake_balance_after", "season_number",
        "game_number", "game_start_unix", "lock_unix", "home_score", "away_score",
        "gross_return_due", "gross_return_applied", "ledger_entry_count", "final_balance", "net",
    ):
        data[field] = exact_integer(data.get(field), field)
    identity_fields = (
        "offer_id", "request_command_id", "stake_ledger_command_id", "lock_command_id",
        "result_command_id", "decision_command_id", "finalization_command_id",
    )
    if any(not isinstance(data.get(field), str) or not data[field].strip() for field in identity_fields):
        raise ValueError("command and offer identities must be non-empty text")
    if len(data["offer_id"]) != 64 or any(character not in "0123456789abcdef" for character in data["offer_id"]):
        raise ValueError("offer_id must be lower hexadecimal SHA-256")
    request = data["request_command_id"]
    lock = data["lock_command_id"]
    result = data["result_command_id"]
    decision = data["decision_command_id"]
    offer = data["offer_id"]
    if data["stake_ledger_command_id"] != request:
        raise ValueError("stake debit does not link to request")
    if data["lock_request_command_id"] != request or data["game_start_unix"] != data["lock_unix"] or data["lock_unix"] <= 0:
        raise ValueError("lock does not link to request and game start")
    if data["result_request_command_id"] != request or data["result_lock_command_id"] != lock:
        raise ValueError("sealed result does not link to request and lock")
    if (data["decision_request_command_id"], data["decision_lock_command_id"], data["decision_result_command_id"]) != (request, lock, result):
        raise ValueError("decision chain does not link")
    if data["decision_offer_id"] != offer or data["decision_offer_version"] != data["offer_version"]:
        raise ValueError("decision offer does not link")
    if (data["finalization_decision_command_id"], data["finalization_request_command_id"], data["finalization_lock_command_id"], data["finalization_result_command_id"]) != (decision, request, lock, result):
        raise ValueError("finalization chain does not link")
    if data["finalization_offer_id"] != offer or data["finalization_offer_version"] != data["offer_version"]:
        raise ValueError("finalization offer does not link")
    return data


def match_winner_reconciliation_payload(path: Path | None = None) -> dict[str, object]:
    if path is None:
        existing = [candidate for candidate in match_winner_reconciliation_candidates() if candidate.is_file()]
        path = max(existing, key=lambda candidate: candidate.stat().st_mtime, default=None)
    if path is None or not path.is_file():
        return {
            "available": False,
            "status": "NO FINALIZED LOSS PROJECTION",
            "read_only": True,
            "boundary": "No complete validated exact-loss reconciliation is available. No partial wager evidence is shown.",
        }
    try:
        data = validated_match_winner_reconciliation(path)
    except (OSError, ValueError, OverflowError, TypeError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return {
            "available": False,
            "status": "INVALID FINALIZED LOSS PROJECTION",
            "read_only": True,
            "boundary": f"The exact-loss projection was rejected: {error}. No partial wager evidence is shown.",
        }
    return {
        "available": True,
        "status": "VALIDATED QA FINALIZED LOSS" if data["qa"] else "VALIDATED FINALIZED LOSS",
        "read_only": True,
        "generated_at_utc": data["generated_at_utc"],
        "selected_team": data["selected_team"],
        "winner": data["winner"],
        "stake": data["stake"],
        "return": data["gross_return_applied"],
        "net": data["net"],
        "balance": data["final_balance"],
        "finalization_status": data["finalization_status"],
        "replay_seal_sha256": data["replay_seal_sha256"],
        "command_linkage": " -> ".join((data["request_command_id"], data["lock_command_id"], data["result_command_id"], data["decision_command_id"], data["finalization_command_id"])),
        "boundary": "Immutable read-only server evidence. The prior decision remains decided_pending_apply; this separate finalization adds no ledger entry and exposes no mutation control.",
    }


def overall_rating(player: Player) -> int:
    return round(
        (player.shooting + player.passing + player.defense + player.rebounding + player.stamina)
        / 5
    )


def player_specialty(player: Player) -> str:
    if player.shooting >= 80 and player.passing >= 78:
        return "Scoring creator"
    if player.passing >= 83:
        return "Floor general"
    if player.defense >= 80 and player.rebounding >= 84:
        return "Interior stopper"
    if player.rebounding >= 84:
        return "Rebounding anchor"
    if player.defense >= 80:
        return "Defensive specialist"
    if player.shooting >= 82:
        return "Scoring specialist"
    return "Rotation utility"


def player_tier(overall: int) -> str:
    if overall >= 80:
        return "Star"
    if overall >= 78:
        return "Featured starter"
    if overall >= 76:
        return "Core starter"
    if overall >= 73:
        return "Rotation contributor"
    return "Developmental"


def status_payload() -> dict[str, object]:
    return {
        "project": "OddsWell: World of Play",
        "console_mode": "LOCAL DEVELOPMENT / NO AUTHENTICATION",
        "engine_version": ENGINE_VERSION,
        "brain_version": BRAIN_VERSION,
        "league_version": LEAGUE_VERSION,
        "career_version": CAREER_VERSION,
        "prediction_version": PREDICTION_VERSION,
        "consistency_version": DEFAULT_CONSISTENCY_VERSION,
        "offensive_involvement": {
            "version": DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
            "status": "ACTIVE DEFAULT",
            "scope": "OPPORTUNITY ONLY",
        },
        "admin_modules": [
            {"id": "overview", "name": "Overview", "state": "AVAILABLE", "detail": "Verified local system summary."},
            {"id": "brains", "name": "Brains", "state": "ACTIVE", "detail": "Cinematic Observatory and truthful training preview."},
            {"id": "athletes", "name": "Athletes", "state": "READ ONLY", "detail": "Stable multi-season careers, age-driven development and decline, retirement, cumulative totals, and verified replay history."},
            {"id": "simulation", "name": "Simulation", "state": "ACTIVE", "detail": "Runs the seeded authoritative simulator and opens its recorded Game Theater replay."},
            {"id": "content", "name": "Content", "state": "LOCKED", "detail": "Clothing and item systems are not implemented."},
            {"id": "world", "name": "World / League", "state": "READ ONLY", "detail": "League and public prediction evidence are visible; admin mutations are not implemented."},
            {"id": "operations", "name": "Operations", "state": "READ ONLY", "detail": "Local Odds Bucks reconciliation is visible without economy commands; moderation, releases, and support remain locked."},
            {"id": "audit", "name": "Audit", "state": "ACTIVE", "detail": "Persistent local record of console actions."},
        ],
        "training": {
            "state": "IDLE",
            "label": "No model training is running",
            "spent_usd": 0.0,
            "budget_usd": 5.0,
        },
        "brains": [
            {
                "id": "project",
                "name": "Project Brain",
                "status": "ACTIVE",
                "version": "Obsidian local vault",
                "detail": "Plans, decisions, research, reports, and visual maps. Updated as knowledge, not trained as a model.",
            },
            {
                "id": "athlete",
                "name": "Athlete Life Brain",
                "status": "ACTIVE DEFAULT",
                "version": DEFAULT_LIFE_BRAIN_VERSION,
                "detail": "Deterministic between-game train, rest, recover, and socialize choices with bounded same-season routine variation, one-decision recent-scoring response, and auditable temporary effects. No learning, LLM, or permanent rating changes.",
            },
            {
                "id": "world",
                "name": "World + League Brain",
                "status": "PARTLY ACTIVE",
                "version": LEAGUE_VERSION,
                "detail": "Schedules, standings, minutes, fatigue, availability, recovery, persistence, league history, and public prediction evidence.",
            },
            {
                "id": "basketball",
                "name": "Basketball Brain",
                "status": "ACTIVE BASELINE",
                "version": BRAIN_VERSION,
                "detail": "Chooses legal intents from each athlete's distinct ratings and game context. Offensive involvement is the baseline-policy ACTIVE DEFAULT with OPPORTUNITY ONLY scope.",
            },
            {
                "id": "rules",
                "name": "Rules + Outcome Engine",
                "status": "AUTHORITATIVE",
                "version": ENGINE_VERSION,
                "detail": "Validates actions and resolves consequences with versioned rules and seeded randomness.",
            },
            {
                "id": "learning",
                "name": "Learning Loop",
                "status": "EVALUATING",
                "version": POLICY_VERSION,
                "detail": "Records decisions and evaluates replay, realism, fairness, latency, and cost before any promotion.",
            },
        ],
    }


def record_audit(
    action: str, target: str, details: dict[str, object], path: Path | None = None
) -> dict[str, object]:
    path = path or AUDIT_PATH
    entry: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "actor": "local-admin",
        "action": action,
        "target": target,
        "outcome": "SUCCESS",
        "details": details,
    }
    line = json.dumps(entry, separators=(",", ":"), sort_keys=True) + "\n"
    with AUDIT_LOCK, path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(line)
        audit_file.flush()
    return entry


def audit_payload(limit: int = 100, path: Path | None = None) -> dict[str, object]:
    path = path or AUDIT_PATH
    if not path.exists():
        return {"entries": []}
    entries: list[dict[str, object]] = []
    with AUDIT_LOCK, path.open(encoding="utf-8") as audit_file:
        for line in audit_file:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                entries.append(value)
    return {"entries": entries[-limit:][::-1]}


@lru_cache(maxsize=1)
def career_league():
    # ponytail: derived rosters fit this read-only archive; persist roster snapshots before mutable seasons.
    state = new_league(LEAGUE_VIEW_START_SEED)
    for _ in range(CAREER_SEASONS):
        state = simulate_next_season(
            state,
            LEAGUE_VIEW_GAMES,
            teams_for_season(state.next_season),
            life_policy_version=DEFAULT_LIFE_BRAIN_VERSION,
            consistency_version=DEFAULT_CONSISTENCY_VERSION,
            offensive_involvement_version=DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
        )
    return state


@lru_cache(maxsize=1)
def league_season():
    return career_league().seasons[0]


@lru_cache(maxsize=1)
def league_prediction_study():
    return run_prediction_study(
        0,
        1,
        LEAGUE_VIEW_GAMES,
        LEAGUE_VIEW_START_SEED,
        life_policy_version=DEFAULT_LIFE_BRAIN_VERSION,
        consistency_version=DEFAULT_CONSISTENCY_VERSION,
        offensive_involvement_version=DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
    )


def season_life_brain_version(season: SeasonResult) -> str:
    versions = {
        decision.policy_version
        for game in season.games
        for decision in game.life_decisions
    }
    if len(versions) != 1:
        raise RuntimeError("season must contain exactly one Athlete Life Brain version")
    return versions.pop()


@lru_cache(maxsize=1)
def league_payload() -> dict[str, object]:
    """Build one public-only archived season for the local League Viewer."""
    teams = default_teams()
    season = league_season()
    study = league_prediction_study()
    predictions = {record.game_number: record for record in study.records}
    if study.consistency_version != DEFAULT_CONSISTENCY_VERSION or any(
        game.consistency_version != study.consistency_version for game in season.games
    ):
        raise RuntimeError("league and prediction consistency versions do not match")
    if study.offensive_involvement_version != DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION or any(
        game.offensive_involvement_version != study.offensive_involvement_version
        for game in season.games
    ):
        raise RuntimeError("league and prediction offensive involvement versions do not match")
    final_availability = dict(season.final_availability)

    games: list[dict[str, object]] = []
    for game in season.games:
        prediction = predictions[game.number]
        if game.winner != prediction.winner or game.replay_sha256 != prediction.replay_sha256:
            raise RuntimeError(f"league evidence mismatch for game {game.number}")
        games.append(
            {
                "number": game.number,
                "home": game.home_team,
                "away": game.away_team,
                "home_score": game.home_score,
                "away_score": game.away_score,
                "winner": game.winner,
                "replay_sha256": game.replay_sha256,
                "prediction_commitment_sha256": prediction.commitment_sha256,
                "predictions": dict(prediction.predictions),
                "availability": {
                    name: recovery_days == 0
                    for name, recovery_days in game.pregame_availability
                },
                "minutes": dict(game.minutes_played),
            }
        )

    return {
        "season": {
            "number": season.season_number,
            "status": "COMPLETE",
            "games": len(season.games),
            "label": "Phase 0.5B archived development season",
        },
        "versions": {
            "league": LEAGUE_VERSION,
            "prediction": PREDICTION_VERSION,
            "brain": BRAIN_VERSION,
            "engine": ENGINE_VERSION,
            "life_brain": season_life_brain_version(season),
            "consistency": study.consistency_version,
            "offensive_involvement": study.offensive_involvement_version,
        },
        "boundary": (
            "Public-only read model. Hidden fatigue, recovery timers, injury-risk internals, "
            "random seeds, economy data, and admin mutations are excluded."
        ),
        "standings": [
            {
                "team": standing.team,
                "games": standing.games,
                "wins": standing.wins,
                "losses": standing.losses,
                "points_for": standing.points_for,
                "points_against": standing.points_against,
                "point_difference": standing.point_difference,
                "win_rate": round(standing.win_rate, 4),
            }
            for standing in season.standings
        ],
        "teams": [
            {
                "name": team.name,
                "players": [
                    {
                        "name": player.name,
                        "shooting": player.shooting,
                        "passing": player.passing,
                        "defense": player.defense,
                        "rebounding": player.rebounding,
                        "stamina": player.stamina,
                        "overall": overall_rating(player),
                        "available": final_availability[player.name] == 0,
                    }
                    for player in team.players
                ],
            }
            for team in teams
        ],
        "games": games,
    }


def evenly_sample(events: list[dict[str, object]], count: int) -> list[dict[str, object]]:
    if len(events) <= count:
        return events
    return [events[round(index * (len(events) - 1) / (count - 1))] for index in range(count)]


def recorded_game_payload(
    game: GameResult,
    matchup: tuple[Team, Team],
    seed: int | None = None,
    frame_limit: int | None = 96,
) -> dict[str, object]:
    candidates: list[dict[str, object]] = [
        {
            "source": "world",
            "target": "basketball",
            "kind": "context",
            "label": "Match context loaded" + (f" · seed {seed}" if seed is not None else ""),
            "score": [0, 0],
        }
    ]
    scores = {game.home_team: 0, game.away_team: 0}
    possession_team: dict[int, str] = {}
    possession_context: dict[int, dict[str, object]] = {}
    lineups: dict[str, list[str]] = {game.home_team: [], game.away_team: []}
    theater_events: list[dict[str, object]] = []

    for record in game.records:
        event_type = record["type"]
        if event_type == "lineup_changed":
            lineups[str(record["team"])] = [str(player) for player in record["players"]]
        elif event_type == "possession_started":
            possession = int(record["possession"])
            possession_team[possession] = str(record["offense"])
            possession_context[possession] = {
                "offense": str(record["offense"]),
                "clock_seconds": int(record["clock_seconds"]),
            }
        elif event_type == "brain_decision" and record["action"]["role"] == "offense":
            action = record["action"]
            score = record["score"]
            candidates.append(
                {
                    "source": "basketball",
                    "target": "rules",
                    "kind": "decision",
                    "label": f"{action['actor']} · {str(action['kind']).replace('_', ' ')}",
                    "score": [score[game.home_team], score[game.away_team]],
                }
            )
        elif event_type == "shot_made":
            team = possession_team[int(record["possession"])]
            scores[team] += int(record["points"])
            candidates.append(
                {
                    "source": "rules",
                    "target": "learning",
                    "kind": "outcome",
                    "label": f"{record['player']} scored {record['points']}",
                    "score": [scores[game.home_team], scores[game.away_team]],
                }
            )
        elif event_type == "turnover":
            candidates.append(
                {
                    "source": "rules",
                    "target": "learning",
                    "kind": "outcome",
                    "label": f"Turnover · {record['player']}",
                    "score": [scores[game.home_team], scores[game.away_team]],
                }
            )

        if event_type not in {
            "pass_completed",
            "turnover",
            "shot_made",
            "shot_missed",
            "offensive_rebound",
            "defensive_rebound",
            "shot_clock_violation",
        }:
            continue
        possession = int(record["possession"])
        context = possession_context[possession]
        offense = str(context["offense"])
        actor = str(
            record.get("passer")
            or record.get("player")
            or record.get("team")
            or ""
        )
        target = str(record.get("receiver") or "")
        labels = {
            "pass_completed": f"Pass · {record.get('passer')} → {record.get('receiver')}",
            "turnover": f"Turnover · {record.get('player')}",
            "shot_made": f"{record.get('points')} points · {record.get('player')}",
            "shot_missed": f"Missed {str(record.get('action')).replace('_', ' ')} · {record.get('player')}",
            "offensive_rebound": f"Offensive rebound · {record.get('player')}",
            "defensive_rebound": f"Defensive rebound · {record.get('player')}",
            "shot_clock_violation": f"Shot-clock violation · {record.get('team')}",
        }
        theater_events.append(
            {
                "kind": event_type,
                "label": labels[event_type],
                "clock_seconds": context["clock_seconds"],
                "score": [scores[game.home_team], scores[game.away_team]],
                "offense": offense,
                "actor": actor,
                "target": target,
                "lineups": {team: list(players) for team, players in lineups.items()},
            }
        )

    # ponytail: a cinematic sample keeps the browser smooth; expose full logs when an audit viewer needs them.
    selected = evenly_sample(candidates, 34)
    selected.append(
        {
            "source": "rules",
            "target": "learning",
            "kind": "final",
            "label": "Final result sealed into replay evidence",
            "score": [game.home_score, game.away_score],
        }
    )
    theater_timeline = (
        theater_events if frame_limit is None else evenly_sample(theater_events, frame_limit)
    )
    theater_timeline.append(
        {
            "kind": "final",
            "label": "Final result · replay evidence sealed",
            "clock_seconds": 0,
            "score": [game.home_score, game.away_score],
            "offense": "",
            "actor": "",
            "target": "",
            "lineups": {team: list(players) for team, players in lineups.items()},
        }
    )
    summary: dict[str, object] = {
        "home": game.home_team,
        "away": game.away_team,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "decisions": len(game.action_tape),
        "records": len(game.records),
        "brain_version": BRAIN_VERSION,
        "engine_version": ENGINE_VERSION,
        "home_players": [player.name for player in matchup[0].players],
        "away_players": [player.name for player in matchup[1].players],
        "replay_frames": len(theater_timeline),
    }
    if seed is not None:
        summary["seed"] = seed
    return {
        "summary": summary,
        "timeline": selected,
        "theater_timeline": theater_timeline,
    }


def simulation_payload(seed: int) -> dict[str, object]:
    if not 0 <= seed <= 2_147_483_647:
        raise ValueError("seed must be between 0 and 2147483647")
    matchup = default_teams()
    payload = recorded_game_payload(
        simulate_game(
            seed,
            matchup=matchup,
            initial_shooting_consistency=shooting_consistency_settings(
                DEFAULT_CONSISTENCY_VERSION, teams=matchup
            ),
            initial_offensive_involvement=offensive_involvement_settings(
                DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION, teams=matchup
            ),
        ),
        matchup,
        seed,
    )
    payload["summary"]["consistency_version"] = DEFAULT_CONSISTENCY_VERSION
    payload["summary"]["offensive_involvement_version"] = (
        DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION
    )
    return payload


@lru_cache(maxsize=LEAGUE_VIEW_GAMES * CAREER_SEASONS)
def archived_game_result(game_number: int, season_number: int = 1) -> GameResult:
    if not 1 <= season_number <= CAREER_SEASONS:
        raise ValueError(f"season number must be between 1 and {CAREER_SEASONS}")
    if not 1 <= game_number <= LEAGUE_VIEW_GAMES:
        raise ValueError(f"game number must be between 1 and {LEAGUE_VIEW_GAMES}")
    season = career_league().seasons[season_number - 1]
    archived = season.games[game_number - 1]
    season_teams = teams_for_season(season_number)
    teams = {team.name: team for team in season_teams}
    matchup = (teams[archived.home_team], teams[archived.away_team])
    reconstructed = simulate_scheduled_game(
        ScheduledGame(archived.number, archived.seed, *matchup),
        archived.pregame_fatigue,
        archived.pregame_availability,
        season_teams,
        archived.pregame_readiness,
        archived.life_decisions,
        life_policy_version=season_life_brain_version(season),
        consistency_version=archived.consistency_version,
        stored_consistency_snapshot=archived.consistency_snapshot,
        offensive_involvement_version=archived.offensive_involvement_version,
        stored_offensive_involvement_snapshot=archived.offensive_involvement_snapshot,
    )
    if reconstructed != archived:
        raise RuntimeError(f"archived evidence mismatch for season {season_number}, game {game_number}")
    game = simulate_game(
        archived.seed,
        matchup=matchup,
        initial_fatigue=dict(archived.pregame_fatigue),
        initial_availability=dict(archived.pregame_availability),
        initial_readiness=dict(archived.pregame_readiness),
        initial_shooting_consistency=shooting_consistency_settings(
            archived.consistency_version,
            archived.consistency_snapshot,
            matchup,
        ),
        initial_offensive_involvement=offensive_involvement_settings(
            archived.offensive_involvement_version,
            archived.offensive_involvement_snapshot,
            matchup,
        ),
    )
    if game.home_score != archived.home_score or game.away_score != archived.away_score:
        raise RuntimeError(f"archived replay mismatch for season {season_number}, game {game_number}")
    return game


@lru_cache(maxsize=LEAGUE_VIEW_GAMES * CAREER_SEASONS)
def archived_replay_payload(season_number: int, game_number: int) -> dict[str, object]:
    game = archived_game_result(game_number, season_number)
    season = career_league().seasons[season_number - 1]
    archived = season.games[game_number - 1]
    teams = {team.name: team for team in teams_for_season(season_number)}
    matchup = (teams[archived.home_team], teams[archived.away_team])
    payload = recorded_game_payload(game, matchup, frame_limit=None)
    payload["archive"] = {
        "season": season.season_number,
        "game": game_number,
        "replay_sha256": archived.replay_sha256,
        "offensive_involvement_version": archived.offensive_involvement_version,
        "verified": True,
    }
    return payload


def league_replay_payload(game_number: int) -> dict[str, object]:
    return archived_replay_payload(1, game_number)


def player_game_stats(game: GameResult) -> dict[str, Counter[str]]:
    stats: dict[str, Counter[str]] = defaultdict(Counter)
    for event in game.records:
        event_type = event["type"]
        if event_type in {"shot_made", "shot_missed"}:
            player_stats = stats[str(event["player"])]
            player_stats["field_goal_attempts"] += 1
            player_stats["three_attempts"] += int(event["action"] == "shoot_3")
            if event_type == "shot_made":
                player_stats["field_goals_made"] += 1
                player_stats["points"] += int(event["points"])
                player_stats["threes_made"] += int(event["action"] == "shoot_3")
        elif event_type == "turnover":
            stats[str(event["player"])]["turnovers"] += 1
        elif event_type == "pass_completed":
            stats[str(event["passer"])]["passes"] += 1
        elif event_type in {"offensive_rebound", "defensive_rebound"}:
            stats[str(event["player"])]["rebounds"] += 1
    return stats


def athlete_stat_line(total: Counter[str], team_record: str) -> dict[str, object]:
    games_played = int(total["games_played"])
    scheduled = int(total["scheduled"])
    return {
        "scheduled_games": scheduled,
        "games_played": games_played,
        "missed_games": scheduled - games_played,
        "team_record": team_record,
        "total_points": int(total["points"]),
        "total_rebounds": int(total["rebounds"]),
        "total_passes": int(total["passes"]),
        "total_turnovers": int(total["turnovers"]),
        "total_minutes": round(total["minutes"], 1),
        "points_per_game": round(total["points"] / games_played, 2) if games_played else 0.0,
        "rebounds_per_game": round(total["rebounds"] / games_played, 2) if games_played else 0.0,
        "passes_per_game": round(total["passes"] / games_played, 2) if games_played else 0.0,
        "turnovers_per_game": round(total["turnovers"] / games_played, 2) if games_played else 0.0,
        "minutes_per_game": round(total["minutes"] / games_played, 2) if games_played else 0.0,
        "field_goal_percentage": round(total["field_goals_made"] / total["field_goal_attempts"], 4)
        if total["field_goal_attempts"]
        else 0.0,
        "three_percentage": round(total["threes_made"] / total["three_attempts"], 4)
        if total["three_attempts"]
        else 0.0,
    }


def athlete_form(history: list[dict[str, object]], season_ppg: float) -> dict[str, object]:
    recent = history[-5:]
    played = [game for game in recent if float(game["minutes"]) > 0]
    recent_ppg = sum(int(game["points"]) for game in played) / len(played) if played else 0.0
    label = "RISING" if recent_ppg > season_ppg + 2 else "COOLING" if recent_ppg < season_ppg - 2 else "STEADY"
    return {"label": label, "points_per_game": round(recent_ppg, 2), "games": recent}


@lru_cache(maxsize=1)
def athlete_profiles_payload() -> dict[str, object]:
    teams = default_teams()
    state = career_league()
    base_players = tuple(player for team in teams for player in team.players) + tuple(
        REPLACEMENTS.values()
    )
    baseline_players = {player.name: player for player in base_players}
    player_team = {player.name: team.name for team in teams for player in team.players}
    roster_roles = {
        player.name: "Starter" if index < 5 else "Sixth player"
        for team in teams
        for index, player in enumerate(team.players)
    }
    for retired_name, replacement in REPLACEMENTS.items():
        player_team[replacement.name] = player_team[retired_name]
        roster_roles[replacement.name] = roster_roles[retired_name]
    season_players = {
        number: {
            player.name: player
            for team in teams_for_season(number)
            for player in team.players
        }
        for number in range(1, CAREER_SEASONS + 1)
    }
    current_players = season_players[CAREER_SEASONS]
    players = tuple(baseline_players[name] for name in current_players) + tuple(
        player for player in base_players if player.name not in current_players
    )
    final_availability = dict(state.availability)
    league_average = sum(overall_rating(player) for player in current_players.values()) / len(
        current_players
    )
    career_totals: dict[str, Counter[str]] = defaultdict(Counter)
    season_splits: dict[str, list[dict[str, object]]] = defaultdict(list)

    for season in state.seasons:
        life_brain_version = season_life_brain_version(season)
        standings = {standing.team: standing for standing in season.standings}
        totals: dict[str, Counter[str]] = defaultdict(Counter)
        histories: dict[str, list[dict[str, object]]] = defaultdict(list)
        life_histories: dict[str, list[dict[str, object]]] = defaultdict(list)
        for archived in season.games:
            game = archived_game_result(archived.number, season.season_number)
            game_stats = player_game_stats(game)
            minutes = dict(game.minutes_played)
            availability = dict(archived.pregame_availability)
            for decision in archived.life_decisions:
                life_histories[decision.athlete].append(
                    {
                        "game": archived.number,
                        "choice": decision.selected.upper(),
                        "reason": decision.reason,
                        "effect": decision.temporary_effect,
                    }
                )
            for player in season_players[season.season_number].values():
                name = player.name
                team = player_team[name]
                home = team == archived.home_team
                opponent = archived.away_team if home else archived.home_team
                team_score = archived.home_score if home else archived.away_score
                opponent_score = archived.away_score if home else archived.home_score
                totals[name].update(game_stats[name])
                totals[name]["scheduled"] += 1
                totals[name]["games_played"] += int(minutes[name] > 0)
                totals[name]["minutes"] += minutes[name]
                histories[name].append(
                    {
                        "season": season.season_number,
                        "game": archived.number,
                        "opponent": opponent,
                        "home": home,
                        "result": "W" if team_score > opponent_score else "L",
                        "score": f"{team_score}-{opponent_score}",
                        "available": availability[name] == 0,
                        "minutes": minutes[name],
                        "points": int(game_stats[name]["points"]),
                        "rebounds": int(game_stats[name]["rebounds"]),
                        "turnovers": int(game_stats[name]["turnovers"]),
                    }
                )

        for player in season_players[season.season_number].values():
            name = player.name
            standing = standings[player_team[name]]
            line = athlete_stat_line(totals[name], f"{standing.wins}-{standing.losses}")
            season_player = season_players[season.season_number][name]
            season_overall = overall_rating(season_player)
            season_splits[name].append(
                {
                    "number": season.season_number,
                    "age": age_for_season(name, season.season_number),
                    "stage": career_stage(age_for_season(name, season.season_number)),
                    "overall": season_overall,
                    "overall_change": season_overall - overall_rating(baseline_players[name]),
                    "ratings": {
                        rating: getattr(season_player, rating) for rating in RATING_NAMES
                    },
                    **line,
                    "form": athlete_form(histories[name], float(line["points_per_game"])),
                    "life": {
                        "version": life_brain_version,
                        "choices": len(life_histories[name]),
                        "breakdown": dict(
                            Counter(entry["choice"] for entry in life_histories[name])
                        ),
                        "recent": list(reversed(life_histories[name][-5:])),
                    },
                    "history": list(reversed(histories[name])),
                }
            )
            career_totals[name].update(totals[name])
            career_totals[name]["team_wins"] += standing.wins
            career_totals[name]["team_losses"] += standing.losses

    profiles: list[dict[str, object]] = []
    for player in players:
        name = player.name
        team_name = player_team[name]
        splits = season_splits[name]
        current = splits[-1]
        current_player = season_players[current["number"]][name]
        overall = overall_rating(current_player)
        rating_band = (
            "Above roster average"
            if overall > league_average + 1
            else "Below roster average"
            if overall < league_average - 1
            else "Near roster average"
        )
        total = career_totals[name]
        status = career_status(name, state.seasons[-1].season_number)
        final_season = retirement_season(name)
        career_line = athlete_stat_line(
            total, f"{int(total['team_wins'])}-{int(total['team_losses'])}"
        )
        profiles.append(
            {
                "id": name.lower().replace(" ", "-"),
                "name": name,
                "team": team_name,
                "overall": overall,
                "ratings": {
                    rating: getattr(current_player, rating) for rating in RATING_NAMES
                },
                "career": {
                    "status": status,
                    "retired_after_season": final_season if status == "RETIRED" else None,
                    "projected_retirement_season": final_season,
                    "debut_age": DEBUT_AGES[name],
                    "debut_season": debut_season(name),
                    "current_age": current["age"],
                    "retirement_age": RETIREMENT_AGE,
                    "current_season": current["number"],
                    "seasons": len(splits),
                    "experience": f"{len(splits)} VERIFIED SEASON{'S' if len(splits) != 1 else ''}",
                    "stage": "RETIRED" if status == "RETIRED" else current["stage"],
                    "role": roster_roles[name],
                    "tier": player_tier(overall),
                    "rating_band": rating_band,
                    "specialty": player_specialty(player),
                    "game_consistency": {
                        "tier": consistency_tier(name),
                        "version": DEFAULT_CONSISTENCY_VERSION,
                        "status": "ACTIVE DEFAULT",
                        "scope": "SHOOTING ONLY",
                    },
                    "offensive_involvement": {
                        "tier": production_involvement_tier(name),
                        "version": DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
                        "status": "ACTIVE DEFAULT",
                        "scope": "OPPORTUNITY ONLY",
                    },
                    "bounded_rating_changes": True,
                    "specialty_preserved": True,
                    "life_brain": current["life"]["version"],
                    "totals": career_line,
                },
                "availability": {
                    "available": status == "ACTIVE" and final_availability[name] == 0,
                    "label": "RETIRED"
                    if status == "RETIRED"
                    else "AVAILABLE"
                    if final_availability[name] == 0
                    else "OUT",
                },
                "season": current,
                "seasons": splits,
                "form": current["form"],
                "history": current["history"],
            }
        )

    return {
        "season": state.seasons[-1].season_number,
        "league_average_overall": round(league_average, 1),
        "archive": {
            "seasons": len(state.seasons),
            "games": sum(len(season.games) for season in state.seasons),
            "active_athletes": sum(
                profile["career"]["status"] == "ACTIVE" for profile in profiles
            ),
            "retired_athletes": sum(
                profile["career"]["status"] == "RETIRED" for profile in profiles
            ),
        },
        "boundary": (
            "Four verified seasons now preserve retired history and fill Roman Voss's roster slot with "
            f"stable incoming athlete Soren Lake. Athlete Life Brain {DEFAULT_LIFE_BRAIN_VERSION} "
            "records bounded between-game choices, same-season routine variation, one-decision recent-scoring "
            "response, and temporary next-game "
            "effects without learning or changing durable ratings or retired history."
        ),
        "profiles": profiles,
    }


class LocalHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self) -> None:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
        )
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, value: object, status: int = 200) -> None:
        self.send_bytes(json.dumps(value).encode("utf-8"), "application/json; charset=utf-8", status)

    def read_json(self, allowed_keys: set[str]) -> dict[str, object]:
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            raise ValueError("Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError as error:
            raise ValueError("Content-Length must be a whole number") from error
        if not 0 <= length <= 4096:
            raise ValueError("request is too large")
        data = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        unknown = set(data) - allowed_keys
        if unknown:
            raise ValueError(f"unknown field: {sorted(unknown)[0]}")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self.send_bytes(INDEX.read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/status":
            self.send_json(status_payload())
        elif path == "/api/audit":
            self.send_json(audit_payload())
        elif path == "/api/league":
            self.send_json(league_payload())
        elif path == "/api/athletes":
            self.send_json(athlete_profiles_payload())
        elif path == "/api/economy":
            self.send_json(economy_payload())
        elif path == "/api/match-winner-reconciliation":
            self.send_json(match_winner_reconciliation_payload())
        elif path.startswith("/api/career/replay/"):
            try:
                values = path.removeprefix("/api/career/replay/").split("/")
                if len(values) != 2 or any(not value.isdecimal() for value in values):
                    raise ValueError("season and game numbers must be whole numbers")
                self.send_json(archived_replay_payload(int(values[0]), int(values[1])))
            except ValueError as error:
                self.send_json({"error": str(error)}, 400)
        elif path.startswith("/api/league/replay/"):
            try:
                game_value = path.removeprefix("/api/league/replay/")
                if not game_value.isdecimal():
                    raise ValueError("game number must be a whole number")
                game_number = int(game_value)
                self.send_json(league_replay_payload(game_number))
            except ValueError as error:
                self.send_json({"error": str(error)}, 400)
        elif path == "/favicon.ico":
            self.send_bytes(b"", "image/x-icon", 204)
        else:
            self.send_json({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/api/simulate", "/api/refresh"}:
            self.send_json({"error": "not found"}, 404)
            return
        try:
            if path == "/api/refresh":
                self.read_json(set())
                record_audit("system.refresh", "admin-console", {})
                self.send_json(status_payload())
                return
            data = self.read_json({"seed"})
            if set(data) != {"seed"}:
                raise ValueError("seed is required")
            seed = data["seed"]
            if not isinstance(seed, int) or isinstance(seed, bool):
                raise ValueError("seed must be a whole number")
            result = simulation_payload(seed)
            summary = result["summary"]
            assert isinstance(summary, dict)
            record_audit(
                "simulation.run",
                f"seed:{seed}",
                {"home_score": summary["home_score"], "away_score": summary["away_score"]},
            )
            self.send_json(result)
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, 400)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[brain-admin] {format % args}")


def self_check() -> None:
    status = status_payload()
    game = simulation_payload(42)
    league = league_payload()
    archived = league_replay_payload(20)
    career_archived = archived_replay_payload(CAREER_SEASONS, 20)
    athletes = athlete_profiles_payload()
    assert len(status["brains"]) == 6
    assert status["prediction_version"] == PREDICTION_VERSION
    assert status["consistency_version"] == DEFAULT_CONSISTENCY_VERSION
    assert status["offensive_involvement"] == {
        "version": DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION,
        "status": "ACTIVE DEFAULT",
        "scope": "OPPORTUNITY ONLY",
    }
    assert status["career_version"] == CAREER_VERSION
    athlete_brain = next(brain for brain in status["brains"] if brain["id"] == "athlete")
    assert athlete_brain["status"] == "ACTIVE DEFAULT"
    assert athlete_brain["version"] == DEFAULT_LIFE_BRAIN_VERSION
    assert [module["id"] for module in status["admin_modules"]] == [
        "overview", "brains", "athletes", "simulation", "content", "world", "operations", "audit"
    ]
    assert next(module for module in status["admin_modules"] if module["id"] == "operations")["state"] == "READ ONLY"
    assert game["summary"]["home_score"] != game["summary"]["away_score"]
    assert game["summary"]["consistency_version"] == DEFAULT_CONSISTENCY_VERSION
    assert (
        game["summary"]["offensive_involvement_version"]
        == DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION
    )
    assert game["timeline"][-1]["kind"] == "final"
    assert game["theater_timeline"][-1]["kind"] == "final"
    assert len(game["theater_timeline"]) <= 97
    assert all(len(event["score"]) == 2 for event in game["theater_timeline"])
    assert league["season"]["games"] == LEAGUE_VIEW_GAMES
    assert sum(standing["wins"] for standing in league["standings"]) == LEAGUE_VIEW_GAMES
    assert len(league["games"]) == LEAGUE_VIEW_GAMES
    assert league["versions"]["life_brain"] == DEFAULT_LIFE_BRAIN_VERSION
    assert league["versions"]["consistency"] == DEFAULT_CONSISTENCY_VERSION
    assert (
        league["versions"]["offensive_involvement"]
        == DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION
    )
    assert all(len(game["replay_sha256"]) == 64 for game in league["games"])
    assert all(len(game["prediction_commitment_sha256"]) == 64 for game in league["games"])
    public_json = json.dumps(league, sort_keys=True)
    assert not any(
        forbidden in public_json
        for forbidden in ('"seed"', '"fatigue"', '"readiness"', '"recovery_days"', '"injury_risk"')
    )
    assert archived["archive"]["replay_sha256"] == league["games"][19]["replay_sha256"]
    assert (
        archived["archive"]["offensive_involvement_version"]
        == DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION
    )
    assert archived["summary"]["home_score"] == league["games"][19]["home_score"]
    assert archived["summary"]["away_score"] == league["games"][19]["away_score"]
    assert "seed" not in archived["summary"]
    assert len(archived["theater_timeline"]) > 97
    assert archived["theater_timeline"][-1]["kind"] == "final"
    archived_json = json.dumps(archived, sort_keys=True)
    assert not any(
        forbidden in archived_json
        for forbidden in ('"seed"', '"fatigue"', '"readiness"', '"recovery_days"', '"injury_risk"')
    )
    assert career_archived["archive"]["season"] == CAREER_SEASONS
    assert career_archived["archive"]["game"] == 20
    assert len(athletes["profiles"]) == 13
    assert athletes["archive"] == {
        "seasons": CAREER_SEASONS,
        "games": CAREER_SEASONS * LEAGUE_VIEW_GAMES,
        "active_athletes": 12,
        "retired_athletes": 1,
    }
    assert all(
        len(season["history"]) == LEAGUE_VIEW_GAMES
        for profile in athletes["profiles"]
        for season in profile["seasons"]
    )
    scheduled_games = {
        profile["name"]: profile["career"]["totals"]["scheduled_games"]
        for profile in athletes["profiles"]
    }
    assert scheduled_games["Roman Voss"] == 3 * LEAGUE_VIEW_GAMES
    assert scheduled_games["Soren Lake"] == LEAGUE_VIEW_GAMES
    assert all(
        games == CAREER_SEASONS * LEAGUE_VIEW_GAMES
        for name, games in scheduled_games.items()
        if name not in {"Roman Voss", "Soren Lake"}
    )
    assert len({profile["id"] for profile in athletes["profiles"]}) == 13
    retired = [
        profile
        for profile in athletes["profiles"]
        if profile["career"]["status"] == "RETIRED"
    ]
    assert len(retired) == 1 and retired[0]["name"] == "Roman Voss"
    assert retired[0]["career"]["retired_after_season"] == 3
    assert retired[0]["availability"] == {"available": False, "label": "RETIRED"}
    incoming = next(profile for profile in athletes["profiles"] if profile["name"] == "Soren Lake")
    assert incoming["career"]["debut_season"] == CAREER_SEASONS
    assert [season["number"] for season in incoming["seasons"]] == [CAREER_SEASONS]
    assert incoming["career"]["status"] == "ACTIVE"
    assert all(
        season["life"]["choices"] == LEAGUE_VIEW_GAMES - 1
        for profile in athletes["profiles"]
        for season in profile["seasons"]
    )
    assert sum(season["life"]["choices"] for season in retired[0]["seasons"]) == 57
    assert sum(season["life"]["choices"] for season in incoming["seasons"]) == 19
    assert all(
        profile["career"]["life_brain"] == DEFAULT_LIFE_BRAIN_VERSION
        for profile in athletes["profiles"]
    )
    assert sum(
        profile["career"]["game_consistency"]["tier"] == "elite"
        for profile in athletes["profiles"]
    ) == 1
    assert all(
        profile["career"]["game_consistency"] == {
            "tier": consistency_tier(profile["name"]),
            "version": DEFAULT_CONSISTENCY_VERSION,
            "status": "ACTIVE DEFAULT",
            "scope": "SHOOTING ONLY",
        }
        for profile in athletes["profiles"]
    )
    assert all(
        profile["career"]["offensive_involvement"] == {
            "tier": production_involvement_tier(profile["name"]),
            **status["offensive_involvement"],
        }
        for profile in athletes["profiles"]
    )
    assert all(
        season["life"]["version"] == DEFAULT_LIFE_BRAIN_VERSION
        for profile in athletes["profiles"]
        for season in profile["seasons"]
    )
    assert all(
        abs(current["ratings"][rating] - previous["ratings"][rating]) <= 1
        for profile in athletes["profiles"]
        for previous, current in zip(profile["seasons"], profile["seasons"][1:])
        for rating in RATING_NAMES
    )
    base_players = {player.name: player for team in default_teams() for player in team.players}
    base_players.update({player.name: player for player in REPLACEMENTS.values()})
    lifecycle_players = {
        number: {player.name: player for team in teams_for_season(number) for player in team.players}
        for number in range(1, CAREER_SEASONS + 1)
    }
    assert all(
        player_specialty(base_players[profile["name"]])
        == player_specialty(lifecycle_players[season["number"]][profile["name"]])
        for profile in athletes["profiles"]
        for season in profile["seasons"]
    )
    assert sum(profile["career"]["totals"]["total_points"] for profile in athletes["profiles"]) == sum(
        standing.points_for
        for season in career_league().seasons
        for standing in season.standings
    )
    assert len({profile["career"]["specialty"] for profile in athletes["profiles"]}) >= 4
    athlete_json = json.dumps(athletes, sort_keys=True)
    assert not any(
        forbidden in athlete_json
        for forbidden in ('"seed"', '"fatigue"', '"readiness"', '"recovery_days"', '"injury_risk"')
    )
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "audit.log"
        record_audit("self-check", "admin-console", {"seed": 42}, path)
        entries = audit_payload(path=path)["entries"]
        assert len(entries) == 1 and entries[0]["details"] == {"seed": 42}
        projection_path = Path(temporary_directory) / "economy.json"
        projection_path.write_text(json.dumps({
            "schema": "oddswell-odds-bucks-reconciliation-v1",
            "generated_at_utc": "2033-05-18T03:33:20Z",
            "authority": "server",
            "currency": "odds_bucks",
            "profile_scope": "machine_local",
            "time_authority": "local_machine_utc",
            "read_only_projection": True,
            "qa": True,
            "observed_now_unix": 2_000_086_400,
            "balance": 200,
            "entry_count": 2,
            "next_job_payout_unix": 2_000_172_800,
            "job_payout": 100,
            "payout_interval_seconds": 86_400,
            "accumulation": True,
            "allowance": False,
            "entries": [
                {"sequence": 1, "command_id": "job:placeholder_shift:first_payout:v1", "delta": 100, "reason": "placeholder_job_payout", "balance_after": 100},
                {"sequence": 2, "command_id": "job:placeholder_shift:scheduled_payout:2000086400", "delta": 100, "reason": "placeholder_job_payout", "balance_after": 200},
            ],
        }), encoding="utf-8")
        economy = economy_payload(projection_path)
        assert economy["available"] is True
        assert economy["status"] == "VALIDATED QA PROJECTION"
        assert economy["balance"] == 200 and economy["entry_count"] == 2
        assert economy["eligible_now"] is False and economy["seconds_until_eligible"] == 86_400
        projection_path.write_text("{}", encoding="utf-8")
        assert economy_payload(projection_path)["status"] == "INVALID LOCAL PROJECTION"
        wager_path = Path(temporary_directory) / "match-winner.json"
        assert match_winner_reconciliation_payload(wager_path)["status"] == "NO FINALIZED LOSS PROJECTION"
        wager_projection = {
            "schema": "oddswell-match-winner-reconciliation-v1",
            "generated_at_utc": "2033-05-18T03:33:20Z",
            "authority": "server",
            "profile_scope": "machine_local",
            "read_only_projection": True,
            "qa": True,
            "market": "match_winner",
            "offer_id": "9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459",
            "offer_version": "basketball-match-winner-odds-v1",
            "request_command_id": "wager:match_winner:request:test-1",
            "selected_team": "Harbor City Waves",
            "stake": 40,
            "request_status": "accepted_pending_lock",
            "stake_ledger_command_id": "wager:match_winner:request:test-1",
            "stake_sequence": 2,
            "stake_delta": -40,
            "stake_reason": "match_winner_stake",
            "stake_balance_after": 60,
            "lock_command_id": "wager:match_winner:lock:test-1",
            "lock_request_command_id": "wager:match_winner:request:test-1",
            "season_number": 1,
            "game_number": 1,
            "game_start_unix": 2_000_000_000,
            "lock_unix": 2_000_000_000,
            "lock_decision": "locked",
            "result_command_id": "wager:match_winner:result:test-1",
            "result_request_command_id": "wager:match_winner:request:test-1",
            "result_lock_command_id": "wager:match_winner:lock:test-1",
            "result_schema": "oddswell-sealed-match-winner-result-v1",
            "result_version": "sealed-match-winner-result-v1",
            "home_team": "Harbor City Waves",
            "away_team": "Mesa Vista Sol",
            "home_score": 101,
            "away_score": 104,
            "winner": "Mesa Vista Sol",
            "replay_seal_sha256": "00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75",
            "decision_command_id": "wager:match_winner:decision:test-1",
            "decision_request_command_id": "wager:match_winner:request:test-1",
            "decision_lock_command_id": "wager:match_winner:lock:test-1",
            "decision_result_command_id": "wager:match_winner:result:test-1",
            "decision_schema": "oddswell-match-winner-settlement-decision-v1",
            "decision_version": "match-winner-settlement-decision-v1",
            "decision_offer_id": "9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459",
            "decision_offer_version": "basketball-match-winner-odds-v1",
            "decision_status": "decided_pending_apply",
            "outcome": "lost",
            "gross_return_due": 0,
            "finalization_command_id": "wager:match_winner:finalization:test-1",
            "finalization_decision_command_id": "wager:match_winner:decision:test-1",
            "finalization_request_command_id": "wager:match_winner:request:test-1",
            "finalization_lock_command_id": "wager:match_winner:lock:test-1",
            "finalization_result_command_id": "wager:match_winner:result:test-1",
            "finalization_schema": "oddswell-match-winner-loss-finalization-v1",
            "finalization_version": "match-winner-loss-finalization-v1",
            "finalization_offer_id": "9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459",
            "finalization_offer_version": "basketball-match-winner-odds-v1",
            "finalization_status": "settled_lost",
            "gross_return_applied": 0,
            "ledger_entry_count": 2,
            "final_balance": 60,
            "net": -40,
        }
        wager_path.write_text(json.dumps(wager_projection), encoding="utf-8")
        wager = match_winner_reconciliation_payload(wager_path)
        assert wager == {
            "available": True,
            "status": "VALIDATED QA FINALIZED LOSS",
            "read_only": True,
            "generated_at_utc": "2033-05-18T03:33:20Z",
            "selected_team": "Harbor City Waves",
            "winner": "Mesa Vista Sol",
            "stake": 40,
            "return": 0,
            "net": -40,
            "balance": 60,
            "finalization_status": "settled_lost",
            "replay_seal_sha256": wager_projection["replay_seal_sha256"],
            "command_linkage": " -> ".join((wager_projection["request_command_id"], wager_projection["lock_command_id"], wager_projection["result_command_id"], wager_projection["decision_command_id"], wager_projection["finalization_command_id"])),
            "boundary": "Immutable read-only server evidence. The prior decision remains decided_pending_apply; this separate finalization adds no ledger entry and exposes no mutation control.",
        }
        wager_projection["final_balance"] = 61
        wager_path.write_text(json.dumps(wager_projection), encoding="utf-8")
        invalid_wager = match_winner_reconciliation_payload(wager_path)
        assert invalid_wager["available"] is False and "balance" not in invalid_wager
        wager_path.write_text("{}", encoding="utf-8")
        partial_wager = match_winner_reconciliation_payload(wager_path)
        assert partial_wager["available"] is False and "selected_team" not in partial_wager
    server = LocalHTTPServer(("127.0.0.1", 0), Handler)
    try:
        try:
            duplicate = LocalHTTPServer(server.server_address, Handler)
        except OSError:
            pass
        else:
            duplicate.server_close()
            raise AssertionError("duplicate local server binding was accepted")
    finally:
        server.server_close()
    print("OddsWell Admin Console self-check passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local OddsWell Admin Console.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        self_check()
        return
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")

    url = f"http://127.0.0.1:{args.port}"
    try:
        server = LocalHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.error(f"cannot bind {url}; close the existing Admin Console first ({error})")
    if not args.no_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    print(f"OddsWell Admin Console is running at {url}")
    print("Press Ctrl+C to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Admin Console.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
