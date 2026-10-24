from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from phase0a.simulator import ENGINE_VERSION, default_teams, simulate_game


@dataclass(frozen=True)
class Analysis:
    game_count: int
    start_seed: int
    overall: dict[str, float]
    teams: dict[str, dict[str, float]]
    players: tuple[dict[str, object], ...]
    checks: tuple[dict[str, object], ...]


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def analyze_games(game_count: int = 1_000, start_seed: int = 0) -> Analysis:
    if game_count < 1:
        raise ValueError("game_count must be positive")

    home, away = default_teams()
    teams = (home, away)
    player_team = {player.name: team.name for team in teams for player in team.players}
    team_totals: dict[str, Counter[str]] = {team.name: Counter() for team in teams}
    player_totals: dict[str, Counter[str]] = defaultdict(Counter)
    home_wins = 0
    overtime_games = 0

    for game_number, seed in enumerate(range(start_seed, start_seed + game_count)):
        matchup = (home, away) if game_number % 2 == 0 else (away, home)
        game = simulate_game(seed, matchup=matchup)
        for team in teams:
            team_totals[team.name]["games"] += 1
            for player in team.players:
                player_totals[player.name]["games"] += 1

        team_totals[game.home_team]["points"] += game.home_score
        team_totals[game.away_team]["points"] += game.away_score
        winner = game.home_team if game.home_score > game.away_score else game.away_team
        team_totals[winner]["wins"] += 1
        home_wins += winner == game.home_team

        for event in game.records:
            event_type = event["type"]
            if event_type == "possession_started":
                team_totals[event["offense"]]["possessions"] += 1
            elif event_type in {"shot_made", "shot_missed"}:
                player = event["player"]
                team = player_team[player]
                made = event_type == "shot_made"
                team_totals[team]["field_goal_attempts"] += 1
                player_totals[player]["field_goal_attempts"] += 1
                if event["action"] == "shoot_3":
                    team_totals[team]["three_attempts"] += 1
                    player_totals[player]["three_attempts"] += 1
                if made:
                    team_totals[team]["field_goals_made"] += 1
                    player_totals[player]["field_goals_made"] += 1
                    player_totals[player]["points"] += event["points"]
                    if event["action"] == "shoot_3":
                        team_totals[team]["threes_made"] += 1
                        player_totals[player]["threes_made"] += 1
            elif event_type == "turnover":
                player = event["player"]
                team_totals[player_team[player]]["turnovers"] += 1
                player_totals[player]["turnovers"] += 1
            elif event_type == "pass_completed":
                player_totals[event["passer"]]["passes"] += 1
            elif event_type in {"offensive_rebound", "defensive_rebound"}:
                player = event["player"]
                key = "offensive_rebounds" if event_type == "offensive_rebound" else "defensive_rebounds"
                team_totals[player_team[player]][key] += 1
                player_totals[player][key] += 1
            elif event_type == "game_ended":
                overtime_games += event["overtime"] > 0

    team_results: dict[str, dict[str, float]] = {}
    for team in teams:
        totals = team_totals[team.name]
        games = totals["games"]
        team_results[team.name] = {
            "wins": totals["wins"],
            "win_rate": ratio(totals["wins"], games),
            "points_per_game": ratio(totals["points"], games),
            "possessions_per_game": ratio(totals["possessions"], games),
            "field_goal_percentage": ratio(totals["field_goals_made"], totals["field_goal_attempts"]),
            "three_attempt_rate": ratio(totals["three_attempts"], totals["field_goal_attempts"]),
            "turnovers_per_game": ratio(totals["turnovers"], games),
            "offensive_rebounds_per_game": ratio(totals["offensive_rebounds"], games),
            "defensive_rebounds_per_game": ratio(totals["defensive_rebounds"], games),
        }

    player_results = []
    for team in teams:
        for player in team.players:
            totals = player_totals[player.name]
            games = totals["games"]
            player_results.append(
                {
                    "player": player.name,
                    "team": team.name,
                    "points_per_game": ratio(totals["points"], games),
                    "attempts_per_game": ratio(totals["field_goal_attempts"], games),
                    "field_goal_percentage": ratio(totals["field_goals_made"], totals["field_goal_attempts"]),
                    "three_percentage": ratio(totals["threes_made"], totals["three_attempts"]),
                    "passes_per_game": ratio(totals["passes"], games),
                    "turnovers_per_game": ratio(totals["turnovers"], games),
                    "rebounds_per_game": ratio(
                        totals["offensive_rebounds"] + totals["defensive_rebounds"], games
                    ),
                }
            )

    all_teams = tuple(team_results.values())
    total_attempts = sum(team_totals[team.name]["field_goal_attempts"] for team in teams)
    total_makes = sum(team_totals[team.name]["field_goals_made"] for team in teams)
    total_threes = sum(team_totals[team.name]["three_attempts"] for team in teams)
    overall = {
        "average_team_score": sum(team["points_per_game"] for team in all_teams) / 2,
        "possessions_per_game": sum(team["possessions_per_game"] for team in all_teams),
        "field_goal_percentage": ratio(total_makes, total_attempts),
        "three_attempt_rate": ratio(total_threes, total_attempts),
        "turnovers_per_team_game": sum(team["turnovers_per_game"] for team in all_teams) / 2,
        "home_win_rate": ratio(home_wins, game_count),
        "overtime_rate": ratio(overtime_games, game_count),
        "max_player_attempts_per_game": max(player["attempts_per_game"] for player in player_results),
        "max_player_rebounds_per_game": max(player["rebounds_per_game"] for player in player_results),
    }

    targets = (
        ("Average team score", "average_team_score", 85, 120, "85–120 points"),
        ("Total possessions", "possessions_per_game", 190, 230, "190–230 per game"),
        ("Field-goal percentage", "field_goal_percentage", 0.38, 0.55, "38–55%"),
        ("Three-point attempt share", "three_attempt_rate", 0.10, 0.45, "10–45%"),
        ("Turnovers", "turnovers_per_team_game", 5, 25, "5–25 per team"),
        ("Home win rate", "home_win_rate", 0.43, 0.57, "43–57%"),
        ("Overtime rate", "overtime_rate", 0, 0.15, "0–15%"),
        ("Maximum player shot attempts", "max_player_attempts_per_game", 0, 30, "0–30 per game"),
        ("Maximum player rebounds", "max_player_rebounds_per_game", 0, 20, "0–20 per game"),
    )
    checks = tuple(
        {
            "metric": label,
            "value": overall[key],
            "target": target,
            "passed": minimum <= overall[key] <= maximum,
        }
        for label, key, minimum, maximum, target in targets
    )
    return Analysis(
        game_count=game_count,
        start_seed=start_seed,
        overall=overall,
        teams=team_results,
        players=tuple(sorted(player_results, key=lambda row: row["points_per_game"], reverse=True)),
        checks=checks,
    )


def percent(value: float) -> str:
    return f"{value:.1%}"


def render_markdown(analysis: Analysis) -> str:
    def display(metric: str, value: float) -> str:
        return percent(value) if "percentage" in metric.lower() or "rate" in metric.lower() or "share" in metric.lower() else f"{value:.2f}"

    passed = sum(check["passed"] for check in analysis.checks)
    lines = [
        "---",
        "tags:",
        "  - development",
        "  - simulation",
        "  - validation",
        "status: active",
        "---",
        "",
        "# Phase 0B Baseline Report",
        "",
        f"Reproducible analysis of **{analysis.game_count:,} games** using seeds "
        f"`{analysis.start_seed}`–`{analysis.start_seed + analysis.game_count - 1}`, alternating home assignment, "
        f"and engine `{ENGINE_VERSION}`.",
        "",
        f"**Calibration result: {passed}/{len(analysis.checks)} checks passed.**",
        "",
        "## Calibration checks",
        "",
        "| Metric | Result | Target | Status |",
        "| --- | ---: | --- | --- |",
    ]
    lines.extend(
        f"| {check['metric']} | {display(check['metric'], check['value'])} | {check['target']} | "
        f"{'✅ Pass' if check['passed'] else '⚠️ Review'} |"
        for check in analysis.checks
    )
    lines.extend(
        [
            "",
            "## Team results",
            "",
            "| Team | Wins | Win rate | PPG | Possessions | FG% | 3PA share | Turnovers | OREB | DREB |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, team in analysis.teams.items():
        lines.append(
            f"| {name} | {int(team['wins'])} | {percent(team['win_rate'])} | {team['points_per_game']:.2f} | "
            f"{team['possessions_per_game']:.2f} | {percent(team['field_goal_percentage'])} | "
            f"{percent(team['three_attempt_rate'])} | {team['turnovers_per_game']:.2f} | "
            f"{team['offensive_rebounds_per_game']:.2f} | {team['defensive_rebounds_per_game']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Player results",
            "",
            "| Player | Team | PPG | FGA | FG% | 3P% | Passes | Turnovers | Rebounds |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for player in analysis.players:
        lines.append(
            f"| {player['player']} | {player['team']} | {player['points_per_game']:.2f} | "
            f"{player['attempts_per_game']:.2f} | {percent(player['field_goal_percentage'])} | "
            f"{percent(player['three_percentage'])} | {player['passes_per_game']:.2f} | "
            f"{player['turnovers_per_game']:.2f} | {player['rebounds_per_game']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "These are engineering guardrails, not final league-balance promises. Passing every broad check means the "
            "baseline is stable enough for deeper analysis; it does not prove realism or entertainment quality.",
            "",
            "The next comparison should run the first LLM policy through the same action contract and measure it "
            "against this exact baseline.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze deterministic Phase 0 basketball games.")
    parser.add_argument("--games", type=int, default=1_000)
    parser.add_argument("--start-seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    analysis = analyze_games(args.games, args.start_seed)
    report = render_markdown(analysis)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    print(f"games={analysis.game_count} checks={sum(check['passed'] for check in analysis.checks)}/{len(analysis.checks)}")


if __name__ == "__main__":
    main()
