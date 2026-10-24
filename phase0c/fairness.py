from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from phase0a.simulator import default_teams, simulate_game
from phase0c.policy import LLMPolicy, offline_fixture_completion


@dataclass(frozen=True)
class FairnessResult:
    seed_pairs: int
    games: int
    home_win_rate: float
    max_team_home_away_gap: float
    invalid_outputs: int
    fallbacks: int
    exact_replays: int
    checks: tuple[tuple[str, bool], ...]


def run_paired_fairness(seed_pairs: int = 100) -> FairnessResult:
    if seed_pairs < 1:
        raise ValueError("seed_pairs must be positive")

    first, second = default_teams()
    home_wins = 0
    invalid_outputs = 0
    fallbacks = 0
    exact_replays = 0
    side_results: dict[str, Counter[str]] = defaultdict(Counter)

    for seed in range(seed_pairs):
        for matchup in ((first, second), (second, first)):
            policy = LLMPolicy(offline_fixture_completion)
            game = simulate_game(
                seed,
                matchup=matchup,
                brain_version="llm-contract-fixture-v1",
                decision_policy=policy,
            )
            replay = simulate_game(
                seed,
                matchup=matchup,
                brain_version="llm-contract-fixture-v1",
                action_tape=game.action_tape,
            )
            exact_replays += game.records == replay.records
            invalid_outputs += sum(trace["error_category"] is not None for trace in policy.traces)
            fallbacks += sum(bool(trace["fallback"]) for trace in policy.traces)

            winner = game.home_team if game.home_score > game.away_score else game.away_team
            home_wins += winner == game.home_team
            for team, side in ((game.home_team, "home"), (game.away_team, "away")):
                side_results[team][f"{side}_games"] += 1
                side_results[team][f"{side}_wins"] += winner == team

    games = seed_pairs * 2
    gaps = []
    for totals in side_results.values():
        home_rate = totals["home_wins"] / totals["home_games"]
        away_rate = totals["away_wins"] / totals["away_games"]
        gaps.append(abs(home_rate - away_rate))
    home_win_rate = home_wins / games
    max_gap = max(gaps)
    checks = (
        ("No invalid provider outputs", invalid_outputs == 0),
        ("No deterministic fallbacks", fallbacks == 0),
        ("Every game replays exactly", exact_replays == games),
        ("Aggregate home win rate is 40-60%", 0.40 <= home_win_rate <= 0.60),
        ("Maximum team home-away gap is at most 15 points", max_gap <= 0.15),
    )
    return FairnessResult(
        seed_pairs,
        games,
        home_win_rate,
        max_gap,
        invalid_outputs,
        fallbacks,
        exact_replays,
        checks,
    )
