from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
import json
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
from phase0d.league import LEAGUE_VERSION, new_league, simulate_next_season  # noqa: E402
from phase0d.prediction import PREDICTION_VERSION, run_prediction_study  # noqa: E402


LEAGUE_VIEW_GAMES = 20
LEAGUE_VIEW_START_SEED = 15_000
CAREER_SEASONS = 3


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
        "prediction_version": PREDICTION_VERSION,
        "admin_modules": [
            {"id": "overview", "name": "Overview", "state": "AVAILABLE", "detail": "Verified local system summary."},
            {"id": "brains", "name": "Brains", "state": "ACTIVE", "detail": "Cinematic Observatory and truthful training preview."},
            {"id": "athletes", "name": "Athletes", "state": "READ ONLY", "detail": "Stable multi-season careers, cumulative totals, specialties, availability, and verified replay history."},
            {"id": "simulation", "name": "Simulation", "state": "ACTIVE", "detail": "Runs the seeded authoritative simulator and opens its recorded Game Theater replay."},
            {"id": "content", "name": "Content", "state": "LOCKED", "detail": "Clothing and item systems are not implemented."},
            {"id": "world", "name": "World / League", "state": "READ ONLY", "detail": "League and public prediction evidence are visible; admin mutations are not implemented."},
            {"id": "operations", "name": "Operations", "state": "LOCKED", "detail": "Economy, moderation, releases, and support are not implemented."},
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
                "status": "PLANNED",
                "version": "Not implemented",
                "detail": "Future career development, training, rest, recovery, habits, relationships, social choices, legal consequences, and long-term memory.",
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
                "detail": "Chooses legal intents from each athlete's distinct ratings and game context. The active version is deterministic; a trained model is not active yet.",
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
    state = new_league(LEAGUE_VIEW_START_SEED)
    for _ in range(CAREER_SEASONS):
        state = simulate_next_season(state, LEAGUE_VIEW_GAMES)
    return state


@lru_cache(maxsize=1)
def league_season():
    return career_league().seasons[0]


@lru_cache(maxsize=1)
def league_prediction_study():
    return run_prediction_study(0, 1, LEAGUE_VIEW_GAMES, LEAGUE_VIEW_START_SEED)


@lru_cache(maxsize=1)
def league_payload() -> dict[str, object]:
    """Build one public-only archived season for the local League Viewer."""
    teams = default_teams()
    season = league_season()
    study = league_prediction_study()
    predictions = {record.game_number: record for record in study.records}
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
    return recorded_game_payload(simulate_game(seed, matchup=matchup), matchup, seed)


@lru_cache(maxsize=LEAGUE_VIEW_GAMES * CAREER_SEASONS)
def archived_game_result(game_number: int, season_number: int = 1) -> GameResult:
    if not 1 <= season_number <= CAREER_SEASONS:
        raise ValueError(f"season number must be between 1 and {CAREER_SEASONS}")
    if not 1 <= game_number <= LEAGUE_VIEW_GAMES:
        raise ValueError(f"game number must be between 1 and {LEAGUE_VIEW_GAMES}")
    archived = career_league().seasons[season_number - 1].games[game_number - 1]
    teams = {team.name: team for team in default_teams()}
    matchup = (teams[archived.home_team], teams[archived.away_team])
    game = simulate_game(
        archived.seed,
        matchup=matchup,
        initial_fatigue=dict(archived.pregame_fatigue),
        initial_availability=dict(archived.pregame_availability),
    )
    if (
        game.home_score != archived.home_score
        or game.away_score != archived.away_score
        or dict(game.minutes_played) != dict(archived.minutes_played)
    ):
        raise RuntimeError(f"archived replay mismatch for season {season_number}, game {game_number}")
    return game


@lru_cache(maxsize=LEAGUE_VIEW_GAMES * CAREER_SEASONS)
def archived_replay_payload(season_number: int, game_number: int) -> dict[str, object]:
    game = archived_game_result(game_number, season_number)
    season = career_league().seasons[season_number - 1]
    archived = season.games[game_number - 1]
    teams = {team.name: team for team in default_teams()}
    matchup = (teams[archived.home_team], teams[archived.away_team])
    payload = recorded_game_payload(game, matchup, frame_limit=None)
    payload["archive"] = {
        "season": season.season_number,
        "game": game_number,
        "replay_sha256": archived.replay_sha256,
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
    players = tuple(player for team in teams for player in team.players)
    player_team = {player.name: team.name for team in teams for player in team.players}
    final_availability = dict(state.availability)
    league_average = sum(overall_rating(player) for player in players) / len(players)
    career_totals: dict[str, Counter[str]] = defaultdict(Counter)
    season_splits: dict[str, list[dict[str, object]]] = defaultdict(list)

    for season in state.seasons:
        standings = {standing.team: standing for standing in season.standings}
        totals: dict[str, Counter[str]] = defaultdict(Counter)
        histories: dict[str, list[dict[str, object]]] = defaultdict(list)
        for archived in season.games:
            game = archived_game_result(archived.number, season.season_number)
            game_stats = player_game_stats(game)
            minutes = dict(game.minutes_played)
            availability = dict(archived.pregame_availability)
            for player in players:
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

        for player in players:
            name = player.name
            standing = standings[player_team[name]]
            line = athlete_stat_line(totals[name], f"{standing.wins}-{standing.losses}")
            season_splits[name].append(
                {
                    "number": season.season_number,
                    **line,
                    "form": athlete_form(histories[name], float(line["points_per_game"])),
                    "history": list(reversed(histories[name])),
                }
            )
            career_totals[name].update(totals[name])
            career_totals[name]["team_wins"] += standing.wins
            career_totals[name]["team_losses"] += standing.losses

    profiles: list[dict[str, object]] = []
    for team in teams:
        for roster_index, player in enumerate(team.players):
            name = player.name
            overall = overall_rating(player)
            rating_band = (
                "Above roster average"
                if overall > league_average + 1
                else "Below roster average"
                if overall < league_average - 1
                else "Near roster average"
            )
            splits = season_splits[name]
            current = splits[-1]
            total = career_totals[name]
            career_line = athlete_stat_line(
                total, f"{int(total['team_wins'])}-{int(total['team_losses'])}"
            )
            profiles.append(
                {
                    "id": name.lower().replace(" ", "-"),
                    "name": name,
                    "team": team.name,
                    "overall": overall,
                    "ratings": {
                        "shooting": player.shooting,
                        "passing": player.passing,
                        "defense": player.defense,
                        "rebounding": player.rebounding,
                        "stamina": player.stamina,
                    },
                    "career": {
                        "status": "ACTIVE",
                        "retired_after_season": None,
                        "current_season": current["number"],
                        "seasons": len(splits),
                        "experience": f"{len(splits)} VERIFIED SEASONS",
                        "stage": "ESTABLISHED",
                        "role": "Starter" if roster_index < 5 else "Sixth player",
                        "tier": player_tier(overall),
                        "rating_band": rating_band,
                        "specialty": player_specialty(player),
                        "durable_ratings": True,
                        "life_brain": "PLANNED / NOT ACTIVE",
                        "totals": career_line,
                    },
                    "availability": {
                        "available": final_availability[name] == 0,
                        "label": "AVAILABLE" if final_availability[name] == 0 else "OUT",
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
            "active_athletes": len(profiles),
            "retired_athletes": 0,
        },
        "boundary": (
            "Three verified seasons and cumulative career totals are active. All 12 athletes remain "
            "ACTIVE; retired history has a stable boundary, but retirement, aging, rating development, "
            "contracts, and Athlete Life Brain consequences are not simulated yet."
        ),
        "profiles": profiles,
    }


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
    assert [module["id"] for module in status["admin_modules"]] == [
        "overview", "brains", "athletes", "simulation", "content", "world", "operations", "audit"
    ]
    assert game["summary"]["home_score"] != game["summary"]["away_score"]
    assert game["timeline"][-1]["kind"] == "final"
    assert game["theater_timeline"][-1]["kind"] == "final"
    assert len(game["theater_timeline"]) <= 97
    assert all(len(event["score"]) == 2 for event in game["theater_timeline"])
    assert league["season"]["games"] == LEAGUE_VIEW_GAMES
    assert sum(standing["wins"] for standing in league["standings"]) == LEAGUE_VIEW_GAMES
    assert len(league["games"]) == LEAGUE_VIEW_GAMES
    assert all(len(game["replay_sha256"]) == 64 for game in league["games"])
    assert all(len(game["prediction_commitment_sha256"]) == 64 for game in league["games"])
    public_json = json.dumps(league, sort_keys=True)
    assert not any(
        forbidden in public_json
        for forbidden in ('"seed"', '"fatigue"', '"recovery_days"', '"injury_risk"')
    )
    assert archived["archive"]["replay_sha256"] == league["games"][19]["replay_sha256"]
    assert archived["summary"]["home_score"] == league["games"][19]["home_score"]
    assert archived["summary"]["away_score"] == league["games"][19]["away_score"]
    assert "seed" not in archived["summary"]
    assert len(archived["theater_timeline"]) > 97
    assert archived["theater_timeline"][-1]["kind"] == "final"
    archived_json = json.dumps(archived, sort_keys=True)
    assert not any(
        forbidden in archived_json
        for forbidden in ('"seed"', '"fatigue"', '"recovery_days"', '"injury_risk"')
    )
    assert career_archived["archive"]["season"] == CAREER_SEASONS
    assert career_archived["archive"]["game"] == 20
    assert len(athletes["profiles"]) == 12
    assert athletes["archive"] == {
        "seasons": CAREER_SEASONS,
        "games": CAREER_SEASONS * LEAGUE_VIEW_GAMES,
        "active_athletes": 12,
        "retired_athletes": 0,
    }
    assert all(len(profile["seasons"]) == CAREER_SEASONS for profile in athletes["profiles"])
    assert all(
        len(season["history"]) == LEAGUE_VIEW_GAMES
        for profile in athletes["profiles"]
        for season in profile["seasons"]
    )
    assert all(
        profile["career"]["totals"]["scheduled_games"]
        == CAREER_SEASONS * LEAGUE_VIEW_GAMES
        for profile in athletes["profiles"]
    )
    assert len({profile["id"] for profile in athletes["profiles"]}) == 12
    assert all(profile["career"]["status"] == "ACTIVE" for profile in athletes["profiles"])
    assert sum(profile["career"]["totals"]["total_points"] for profile in athletes["profiles"]) == sum(
        standing.points_for
        for season in career_league().seasons
        for standing in season.standings
    )
    assert len({profile["career"]["specialty"] for profile in athletes["profiles"]}) >= 4
    athlete_json = json.dumps(athletes, sort_keys=True)
    assert not any(
        forbidden in athlete_json
        for forbidden in ('"seed"', '"fatigue"', '"recovery_days"', '"injury_risk"')
    )
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "audit.log"
        record_audit("self-check", "admin-console", {"seed": 42}, path)
        entries = audit_payload(path=path)["entries"]
        assert len(entries) == 1 and entries[0]["details"] == {"seed": 42}
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
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
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
