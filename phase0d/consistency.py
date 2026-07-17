from __future__ import annotations

import random
from collections import Counter, defaultdict
from statistics import fmean

from phase0a.simulator import Team, default_teams, simulate_game


CONSISTENCY_VERSION = "athlete-consistency-v1"
CONSISTENCY_SPREAD = {
    "volatile": 0.015,
    "normal": 0.01,
    "steady": 0.006,
    "elite": 0.0025,
}
ATHLETE_CONSISTENCY = {
    "Jalen Cross": "steady",
    "Micah Vale": "normal",
    "Dorian Pike": "steady",
    "Kellan Shore": "normal",
    "Andre North": "normal",
    "Malik Frost": "volatile",
    "Nico Reyes": "steady",
    "Tariq Stone": "elite",
    "Eli Mercer": "normal",
    "Roman Voss": "steady",
    "Cal Brooks": "normal",
    "Mateo Cruz": "volatile",
    "Soren Lake": "normal",
}


def consistency_tier(player_name: str) -> str:
    try:
        return ATHLETE_CONSISTENCY[player_name]
    except KeyError as error:
        raise ValueError(f"missing game consistency for {player_name!r}") from error


def game_form(
    seed: int,
    teams: tuple[Team, Team] | None = None,
) -> dict[str, float]:
    rng = random.Random(seed ^ 0xC015157)
    return {
        player.name: round(
            rng.triangular(
                -CONSISTENCY_SPREAD[consistency_tier(player.name)],
                CONSISTENCY_SPREAD[consistency_tier(player.name)],
                0.0,
            ),
            4,
        )
        for team in (teams or default_teams())
        for player in team.players
    }


def evaluate_consistency(
    game_count: int = 200,
    start_seed: int = 60_000,
) -> dict[str, object]:
    if game_count <= 0:
        raise ValueError("game_count must be positive")
    teams = default_teams()
    players = [player.name for team in teams for player in team.players]
    form_samples: dict[str, list[float]] = defaultdict(list)
    winner_differences = 0
    score_differences = 0
    team_score_difference = 0
    replay_violations = 0

    for seed in range(start_seed, start_seed + game_count):
        form = game_form(seed, teams)
        baseline = simulate_game(seed, matchup=teams)
        pilot = simulate_game(seed, matchup=teams, initial_game_form=form)
        replay = simulate_game(
            seed,
            pilot.action_tape,
            matchup=teams,
            initial_game_form=form,
        )
        replay_violations += pilot != replay
        baseline_winner = (
            baseline.home_team if baseline.home_score > baseline.away_score else baseline.away_team
        )
        pilot_winner = pilot.home_team if pilot.home_score > pilot.away_score else pilot.away_team
        winner_differences += baseline_winner != pilot_winner
        score_differences += (
            baseline.home_score != pilot.home_score or baseline.away_score != pilot.away_score
        )
        team_score_difference += abs(baseline.home_score - pilot.home_score)
        team_score_difference += abs(baseline.away_score - pilot.away_score)
        for player in players:
            form_samples[consistency_tier(player)].append(abs(form[player]))
    return {
        "version": CONSISTENCY_VERSION,
        "games": game_count,
        "tier_counts": dict(Counter(consistency_tier(player) for player in players)),
        "mean_absolute_form": {
            tier: round(fmean(form_samples[tier]), 6) for tier in CONSISTENCY_SPREAD
        },
        "max_absolute_form": {
            tier: max(form_samples[tier]) for tier in CONSISTENCY_SPREAD
        },
        "score_differences": score_differences,
        "mean_absolute_team_score_difference": round(
            team_score_difference / (2 * game_count), 4
        ),
        "winner_differences": winner_differences,
        "replay_violations": replay_violations,
    }
