from __future__ import annotations

import argparse
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

from phase0a.simulator import BRAIN_VERSION, ENGINE_VERSION, default_teams, simulate_game  # noqa: E402
from phase0c.policy import POLICY_VERSION  # noqa: E402
from phase0d.league import LEAGUE_VERSION, simulate_season  # noqa: E402
from phase0d.prediction import PREDICTION_VERSION, run_prediction_study  # noqa: E402


LEAGUE_VIEW_GAMES = 20
LEAGUE_VIEW_START_SEED = 15_000


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
                "detail": "Future training, rest, recovery, relationships, social choices, and long-term consequences.",
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
                "detail": "Chooses legal athlete intents. The active version is deterministic; a trained model is not active yet.",
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
def league_payload() -> dict[str, object]:
    """Build one public-only archived season for the local League Viewer."""
    teams = default_teams()
    season = simulate_season(LEAGUE_VIEW_GAMES, LEAGUE_VIEW_START_SEED)
    study = run_prediction_study(0, 1, LEAGUE_VIEW_GAMES, LEAGUE_VIEW_START_SEED)
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
                        "overall": round(
                            (
                                player.shooting
                                + player.passing
                                + player.defense
                                + player.rebounding
                                + player.stamina
                            )
                            / 5
                        ),
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


def simulation_payload(seed: int) -> dict[str, object]:
    if not 0 <= seed <= 2_147_483_647:
        raise ValueError("seed must be between 0 and 2147483647")
    game = simulate_game(seed)
    candidates: list[dict[str, object]] = [
        {
            "source": "world",
            "target": "basketball",
            "kind": "context",
            "label": f"Match context loaded · seed {seed}",
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
    theater_timeline = evenly_sample(theater_events, 96)
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
    teams = default_teams()
    return {
        "summary": {
            "seed": seed,
            "home": game.home_team,
            "away": game.away_team,
            "home_score": game.home_score,
            "away_score": game.away_score,
            "decisions": len(game.action_tape),
            "records": len(game.records),
            "brain_version": BRAIN_VERSION,
            "engine_version": ENGINE_VERSION,
            "home_players": [player.name for player in teams[0].players],
            "away_players": [player.name for player in teams[1].players],
        },
        "timeline": selected,
        "theater_timeline": theater_timeline,
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
    assert len(status["brains"]) == 6
    assert status["prediction_version"] == PREDICTION_VERSION
    assert [module["id"] for module in status["admin_modules"]] == [
        "overview", "brains", "simulation", "content", "world", "operations", "audit"
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
