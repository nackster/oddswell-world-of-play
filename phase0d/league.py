from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from phase0a.simulator import BRAIN_VERSION, Team, default_teams, simulate_game
from phase0c.replay import replay_manifest, verify_replay_manifest


LEAGUE_VERSION = "phase0d-v1"


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
    start_seed: int
    games: tuple[SeasonGame, ...]
    standings: tuple[Standing, ...]


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


def simulate_season(game_count: int = 20, start_seed: int = 10_000) -> SeasonResult:
    schedule = build_schedule(game_count, start_seed)
    totals: dict[str, Counter[str]] = {team.name: Counter() for team in default_teams()}
    games = []

    for fixture in schedule:
        matchup = (fixture.home, fixture.away)
        result = simulate_game(fixture.seed, matchup=matchup)
        manifest = replay_manifest(result, matchup, BRAIN_VERSION)
        if not verify_replay_manifest(manifest):
            raise RuntimeError(f"replay manifest failed for game {fixture.number}")
        winner = result.home_team if result.home_score > result.away_score else result.away_team
        loser = result.away_team if winner == result.home_team else result.home_team

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
            )
        )

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
    return SeasonResult(start_seed, tuple(games), standings)


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
            f"Deterministic **{len(season.games)}-game** first league run using seeds "
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
            "| Game | Seed | Away | Score | Home | Winner | Replay hash |",
            "| ---: | ---: | --- | ---: | --- | --- | --- |",
        ]
    )
    for game in season.games:
        lines.append(
            f"| {game.number} | {game.seed} | {game.away_team} | "
            f"{game.away_score}-{game.home_score} | {game.home_team} | {game.winner} | "
            f"`{game.replay_sha256[:12]}` |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This first Phase 0D slice proves balanced home/away scheduling, deterministic season history, "
                "standings with stable tie-breakers, and a verified replay-integrity hash for every game."
            ),
            "",
            (
                "Injuries, between-game fatigue, public information, prediction scoring, and live LLM control "
                "remain separate measured steps. No credits, wagers, purchases, or paid model calls are part "
                "of this run."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic OddsWell Phase 0D season.")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--start-seed", type=int, default=10_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    season = simulate_season(args.games, args.start_seed)
    report = render_markdown(season)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    champion = season.standings[0]
    print(
        f"games={len(season.games)} leader={champion.team} record={champion.wins}-{champion.losses} "
        f"manifests={len(season.games)}/{len(season.games)}"
    )


if __name__ == "__main__":
    main()
