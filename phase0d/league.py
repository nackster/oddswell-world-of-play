from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from phase0a.simulator import BRAIN_VERSION, ENGINE_VERSION, GameResult, Team, default_teams, simulate_game
from phase0c.replay import replay_manifest, verify_replay_manifest


LEAGUE_VERSION = "phase0d1-v1"
STATE_SCHEMA = "oddswell-league-state-v1"
FATIGUE_MODEL_VERSION = "between-games-v1"
MAX_CARRYOVER_FATIGUE = 0.35
RECOVERY_PER_DAY = 0.04
BETWEEN_GAME_REST_DAYS = 1
OFFSEASON_REST_DAYS = 7

FatigueSnapshot = tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class ScheduledGame:
    number: int
    seed: int
    home: Team
    away: Team


@dataclass(frozen=True)
class SeasonGame:
    number: int
    seed: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    winner: str
    replay_sha256: str
    pregame_fatigue: FatigueSnapshot
    postgame_fatigue: FatigueSnapshot


@dataclass(frozen=True)
class Standing:
    team: str
    games: int
    wins: int
    losses: int
    points_for: int
    points_against: int

    @property
    def win_rate(self) -> float:
        return self.wins / self.games

    @property
    def point_difference(self) -> int:
        return self.points_for - self.points_against


@dataclass(frozen=True)
class SeasonResult:
    season_number: int
    start_seed: int
    games: tuple[SeasonGame, ...]
    standings: tuple[Standing, ...]
    initial_fatigue: FatigueSnapshot
    final_fatigue: FatigueSnapshot


@dataclass(frozen=True)
class LeagueState:
    schema: str
    next_season: int
    next_seed: int
    fatigue: FatigueSnapshot
    seasons: tuple[SeasonResult, ...]


def build_schedule(
    game_count: int = 20,
    start_seed: int = 10_000,
    teams: tuple[Team, Team] | None = None,
) -> tuple[ScheduledGame, ...]:
    if game_count < 2 or game_count % 2:
        raise ValueError("game_count must be a positive even number")
    first, second = teams or default_teams()
    return tuple(
        ScheduledGame(
            number=index + 1,
            seed=start_seed + index,
            home=first if index % 2 == 0 else second,
            away=second if index % 2 == 0 else first,
        )
        for index in range(game_count)
    )


def fatigue_snapshot(values: Mapping[str, float], teams: tuple[Team, Team] | None = None) -> FatigueSnapshot:
    return tuple(
        (player.name, round(float(values[player.name]), 4))
        for team in (teams or default_teams())
        for player in team.players
    )


def empty_fatigue(teams: tuple[Team, Team] | None = None) -> FatigueSnapshot:
    return tuple((player.name, 0.0) for team in (teams or default_teams()) for player in team.players)


def recover_fatigue(
    fatigue: FatigueSnapshot,
    rest_days: int,
    teams: tuple[Team, Team] | None = None,
) -> FatigueSnapshot:
    if rest_days < 0:
        raise ValueError("rest_days cannot be negative")
    values = dict(fatigue)
    return fatigue_snapshot(
        {name: max(0.0, amount - RECOVERY_PER_DAY * rest_days) for name, amount in values.items()},
        teams,
    )


def add_game_load(
    fatigue: FatigueSnapshot,
    teams: tuple[Team, Team],
    game_minutes: int,
) -> FatigueSnapshot:
    values = dict(fatigue)
    # ponytail: all five players carry the same game duration until substitutions and minute tracking exist.
    return fatigue_snapshot(
        {
            player.name: min(
                MAX_CARRYOVER_FATIGUE,
                values[player.name] + 0.05 * (game_minutes / 48) + (100 - player.stamina) / 1_000,
            )
            for team in teams
            for player in team.players
        },
        teams,
    )


def game_minutes(result: GameResult) -> int:
    ended = result.records[-1]
    if ended.get("type") != "game_ended":
        raise ValueError("game result is missing its final event")
    return 48 + 5 * int(ended["overtime"])


def simulate_season(
    game_count: int = 20,
    start_seed: int = 10_000,
    initial_fatigue: FatigueSnapshot | None = None,
    season_number: int = 1,
) -> SeasonResult:
    teams = default_teams()
    schedule = build_schedule(game_count, start_seed, teams)
    fatigue = initial_fatigue or empty_fatigue(teams)
    fatigue = fatigue_snapshot(dict(fatigue), teams)
    season_start = fatigue
    totals: dict[str, Counter[str]] = {team.name: Counter() for team in teams}
    games = []

    for index, fixture in enumerate(schedule):
        if index:
            fatigue = recover_fatigue(fatigue, BETWEEN_GAME_REST_DAYS, teams)
        matchup = (fixture.home, fixture.away)
        result = simulate_game(fixture.seed, matchup=matchup, initial_fatigue=dict(fatigue))
        manifest = replay_manifest(result, matchup, BRAIN_VERSION)
        if not verify_replay_manifest(manifest):
            raise RuntimeError(f"replay manifest failed for game {fixture.number}")
        winner = result.home_team if result.home_score > result.away_score else result.away_team
        loser = result.away_team if winner == result.home_team else result.home_team
        postgame_fatigue = add_game_load(fatigue, teams, game_minutes(result))

        totals[winner]["wins"] += 1
        totals[loser]["losses"] += 1
        totals[result.home_team]["points_for"] += result.home_score
        totals[result.home_team]["points_against"] += result.away_score
        totals[result.away_team]["points_for"] += result.away_score
        totals[result.away_team]["points_against"] += result.home_score
        games.append(
            SeasonGame(
                fixture.number,
                fixture.seed,
                result.home_team,
                result.away_team,
                result.home_score,
                result.away_score,
                winner,
                manifest["sha256"],
                fatigue,
                postgame_fatigue,
            )
        )
        fatigue = postgame_fatigue

    standings = tuple(
        sorted(
            (
                Standing(
                    team,
                    totals[team]["wins"] + totals[team]["losses"],
                    totals[team]["wins"],
                    totals[team]["losses"],
                    totals[team]["points_for"],
                    totals[team]["points_against"],
                )
                for team in totals
            ),
            key=lambda row: (-row.wins, -row.point_difference, -row.points_for, row.team),
        )
    )
    return SeasonResult(season_number, start_seed, tuple(games), standings, season_start, fatigue)


def new_league(start_seed: int = 10_000) -> LeagueState:
    return LeagueState(STATE_SCHEMA, 1, start_seed, empty_fatigue(), ())


def simulate_next_season(state: LeagueState, game_count: int = 20) -> LeagueState:
    if state.schema != STATE_SCHEMA:
        raise ValueError(f"unsupported league state schema: {state.schema}")
    initial_fatigue = (
        recover_fatigue(state.fatigue, OFFSEASON_REST_DAYS) if state.seasons else state.fatigue
    )
    season = simulate_season(game_count, state.next_seed, initial_fatigue, state.next_season)
    return LeagueState(
        STATE_SCHEMA,
        state.next_season + 1,
        state.next_seed + game_count,
        season.final_fatigue,
        state.seasons + (season,),
    )


def save_league(state: LeagueState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _snapshot_from_json(value: object) -> FatigueSnapshot:
    if not isinstance(value, list) or any(
        not isinstance(item, list)
        or len(item) != 2
        or not isinstance(item[0], str)
        or not isinstance(item[1], (int, float))
        for item in value
    ):
        raise ValueError("invalid fatigue snapshot")
    snapshot = tuple((item[0], float(item[1])) for item in value)
    expected = {player.name for team in default_teams() for player in team.players}
    if len(snapshot) != len(expected) or {name for name, _ in snapshot} != expected or any(
        not 0 <= amount <= MAX_CARRYOVER_FATIGUE for _, amount in snapshot
    ):
        raise ValueError("invalid fatigue roster or value")
    return snapshot


def load_league(path: Path) -> LeagueState:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or set(value) != {
            "schema",
            "next_season",
            "next_seed",
            "fatigue",
            "seasons",
        }:
            raise ValueError("invalid league state fields")
        if value["schema"] != STATE_SCHEMA or not isinstance(value["seasons"], list):
            raise ValueError("unsupported league state")
        seasons = []
        for season_value in value["seasons"]:
            season_data = dict(season_value)
            games = []
            for game_value in season_data.pop("games"):
                game_data = dict(game_value)
                game_data["pregame_fatigue"] = _snapshot_from_json(game_data["pregame_fatigue"])
                game_data["postgame_fatigue"] = _snapshot_from_json(game_data["postgame_fatigue"])
                games.append(SeasonGame(**game_data))
            standings = tuple(Standing(**row) for row in season_data.pop("standings"))
            season_data["initial_fatigue"] = _snapshot_from_json(season_data["initial_fatigue"])
            season_data["final_fatigue"] = _snapshot_from_json(season_data["final_fatigue"])
            seasons.append(SeasonResult(games=tuple(games), standings=standings, **season_data))
        return LeagueState(
            value["schema"],
            int(value["next_season"]),
            int(value["next_seed"]),
            _snapshot_from_json(value["fatigue"]),
            tuple(seasons),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid league state: {path}") from error


def average_fatigue(fatigue: FatigueSnapshot) -> float:
    return sum(value for _, value in fatigue) / len(fatigue)


def render_markdown(season: SeasonResult) -> str:
    lines = [
        "---",
        "tags:",
        "  - development",
        "  - simulation",
        "  - season",
        "status: active",
        "---",
        "",
        "# Phase 0D Schedule and Standings",
        "",
        (
            f"Deterministic **{len(season.games)}-game** league run using seeds "
            f"`{season.start_seed}`-`{season.start_seed + len(season.games) - 1}`, "
            f"league `{LEAGUE_VERSION}`, and brain `{BRAIN_VERSION}`."
        ),
        "",
        "## Standings",
        "",
        "| Rank | Team | W | L | Win% | PF | PA | Diff |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, standing in enumerate(season.standings, 1):
        lines.append(
            f"| {rank} | {standing.team} | {standing.wins} | {standing.losses} | "
            f"{standing.win_rate:.1%} | {standing.points_for} | {standing.points_against} | "
            f"{standing.point_difference:+d} |"
        )
    lines.extend(
        [
            "",
            "## Schedule and results",
            "",
            "| Game | Seed | Away | Score | Home | Winner | Replay hash | Avg pregame fatigue |",
            "| ---: | ---: | --- | ---: | --- | --- | --- | ---: |",
        ]
    )
    for game in season.games:
        lines.append(
            f"| {game.number} | {game.seed} | {game.away_team} | "
            f"{game.away_score}-{game.home_score} | {game.home_team} | {game.winner} | "
            f"`{game.replay_sha256[:12]}` | {average_fatigue(game.pregame_fatigue):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This slice proves balanced scheduling, deterministic standings, replay integrity, and "
                "bounded fatigue carried between games."
            ),
            "",
            (
                "Injuries, substitutions, public information, prediction scoring, and live LLM control "
                "remain separate measured steps."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def render_league_markdown(state: LeagueState) -> str:
    lines = [
        "---",
        "tags:",
        "  - development",
        "  - simulation",
        "  - season",
        "  - fatigue",
        "status: complete",
        "---",
        "",
        "# Phase 0D.1 Multi-Season Persistence and Fatigue",
        "",
        (
            f"Deterministic **{len(state.seasons)}-season** run using state schema `{STATE_SCHEMA}`, "
            f"league `{LEAGUE_VERSION}`, engine `{ENGINE_VERSION}`, fatigue model `{FATIGUE_MODEL_VERSION}`, "
            f"and brain `{BRAIN_VERSION}`."
        ),
        "",
        "## Season summary",
        "",
        "| Season | Seeds | Leader | Record | Start fatigue | Final fatigue | Replay hashes |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for season in state.seasons:
        leader = season.standings[0]
        lines.append(
            f"| {season.season_number} | {season.start_seed}-{season.start_seed + len(season.games) - 1} | "
            f"{leader.team} | {leader.wins}-{leader.losses} | {average_fatigue(season.initial_fatigue):.3f} | "
            f"{average_fatigue(season.final_fatigue):.3f} | {len(season.games)}/{len(season.games)} |"
        )
    first_season = state.seasons[0]
    middle_game = first_season.games[len(first_season.games) // 2 - 1]
    last_game = first_season.games[-1]
    lines.extend(
        [
            "",
            "## Measured progression",
            "",
            (
                f"- Season 1 average pregame fatigue: **{average_fatigue(first_season.games[0].pregame_fatigue):.3f}** "
                f"in game 1, **{average_fatigue(middle_game.pregame_fatigue):.3f}** in game {middle_game.number}, "
                f"and **{average_fatigue(last_game.pregame_fatigue):.3f}** in game {last_game.number}."
            ),
            (
                f"- Seven offseason rest days reduced the next season's starting average to "
                f"**{average_fatigue(state.seasons[1].initial_fatigue):.3f}**."
                if len(state.seasons) > 1
                else "- Offseason recovery will be measured when a second season is run."
            ),
            "",
            "## Persistence gate",
            "",
            "- JSON stores every season result, standing, replay hash, seed, and player fatigue snapshot.",
            "- Save, load, and resume use the same deterministic simulation path.",
            "- Automated equality tests compare uninterrupted play with save-and-resume play.",
            "",
            "## Fatigue model",
            "",
            f"- Carryover fatigue is bounded at **{MAX_CARRYOVER_FATIGUE:.2f}**.",
            f"- Players recover **{RECOVERY_PER_DAY:.2f} per rest day**, with one day between games and seven between seasons.",
            "- Game load uses duration and stamina. Pregame fatigue is passed into the authoritative simulator and replay record.",
            "- The current ten-player prototype has no bench, so every player receives full-game workload.",
            "",
            "## Scope",
            "",
            "No injuries, credits, wagers, purchases, paid model calls, or retraining jobs are part of this gate.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic OddsWell Phase 0D seasons.")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--seasons", type=int, default=1)
    parser.add_argument("--start-seed", type=int, default=10_000)
    parser.add_argument("--state", type=Path, help="Optional JSON state to load and save.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.seasons < 1:
        parser.error("--seasons must be positive")

    state = load_league(args.state) if args.state and args.state.exists() else new_league(args.start_seed)
    for _ in range(args.seasons):
        state = simulate_next_season(state, args.games)
    if args.state:
        save_league(state, args.state)
        print(f"wrote {args.state}")

    report = render_markdown(state.seasons[-1]) if len(state.seasons) == 1 else render_league_markdown(state)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    champion = state.seasons[-1].standings[0]
    print(
        f"seasons={len(state.seasons)} games={sum(len(season.games) for season in state.seasons)} "
        f"latest_leader={champion.team} record={champion.wins}-{champion.losses}"
    )


if __name__ == "__main__":
    main()
