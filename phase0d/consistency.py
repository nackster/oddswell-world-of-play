from __future__ import annotations

import random
from collections import Counter, defaultdict
from statistics import fmean, pstdev

from phase0a.simulator import Team, default_teams, simulate_game


CONSISTENCY_VERSION = "athlete-consistency-v1"
CONSISTENCY_V2_VERSION = "athlete-consistency-v2"
CONSISTENCY_DISABLED_VERSION = "athlete-consistency-disabled"
DEFAULT_CONSISTENCY_VERSION = CONSISTENCY_V2_VERSION
CONSISTENCY_SPREAD = {
    "volatile": 0.015,
    "normal": 0.01,
    "steady": 0.006,
    "elite": 0.0025,
}
CONSISTENCY_V2_PARAMETERS = {
    "volatile": (0.0, 0.0),
    "normal": (0.15, 0.03),
    "steady": (0.30, 0.06),
    "elite": (0.50, 0.10),
}
CONSISTENCY_V2_CALIBRATION = {
    "Tariq Stone": (70_000, 14),
    "Jalen Cross": (72_000, 16),
}
ConsistencySnapshot = tuple[tuple[str, str, float, float], ...]
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


def consistency_snapshot(
    version: str,
    teams: tuple[Team, Team] | None = None,
) -> ConsistencySnapshot:
    if version == CONSISTENCY_DISABLED_VERSION:
        return ()
    if version != CONSISTENCY_V2_VERSION:
        raise ValueError(f"unsupported consistency version: {version!r}")
    return tuple(
        (
            player.name,
            consistency_tier(player.name),
            *CONSISTENCY_V2_PARAMETERS[consistency_tier(player.name)],
        )
        for team in (teams or default_teams())
        for player in team.players
    )


def shooting_consistency_settings(
    version: str,
    snapshot: ConsistencySnapshot | None = None,
    teams: tuple[Team, Team] | None = None,
) -> dict[str, tuple[float, float]] | None:
    if version == CONSISTENCY_DISABLED_VERSION:
        if snapshot not in (None, ()):
            raise ValueError("disabled consistency must have an empty snapshot")
        return None
    if version != CONSISTENCY_V2_VERSION:
        raise ValueError(f"unsupported consistency version: {version!r}")
    values = snapshot if snapshot is not None else consistency_snapshot(version, teams)
    if not values:
        raise ValueError("v2 consistency requires a roster snapshot")
    expected = (
        {row[0] for row in values}
        if teams is None and snapshot is not None
        else {player.name for team in (teams or default_teams()) for player in team.players}
    )
    if len(values) != len(expected) or {row[0] for row in values} != expected:
        raise ValueError("consistency snapshot must contain every matchup player exactly once")
    for name, tier, strength, cap in values:
        if tier not in CONSISTENCY_V2_PARAMETERS:
            raise ValueError(f"unknown consistency tier: {tier!r}")
        if not 0 <= strength <= 1 or not 0 <= cap <= 1:
            raise ValueError("consistency parameters must be between zero and one")
        consistency_tier(name)
    return {name: (strength, cap) for name, _, strength, cap in values}


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


def calibrate_consistency(
    game_count: int = 1_000,
    start_seed: int = 70_000,
    athlete: str = "Tariq Stone",
) -> dict[str, object]:
    if game_count <= 0:
        raise ValueError("game_count must be positive")
    teams = default_teams()
    players = [player.name for team in teams for player in team.players]
    if athlete not in players:
        raise ValueError(f"unknown calibration athlete: {athlete!r}")
    athlete_team = next(
        team.name for team in teams if any(player.name == athlete for player in team.players)
    )

    tier_metrics: dict[str, dict[str, float | int]] = {}
    replay_violations = 0
    for tier, spread in CONSISTENCY_SPREAD.items():
        points: list[int] = []
        team_wins = 0
        for seed in range(start_seed, start_seed + game_count):
            form = {player: 0.0 for player in players}
            form[athlete] = round(
                random.Random(seed ^ 0xC015157).triangular(-spread, spread, 0.0),
                4,
            )
            game = simulate_game(seed, matchup=teams, initial_game_form=form)
            replay = simulate_game(
                seed,
                game.action_tape,
                matchup=teams,
                initial_game_form=form,
            )
            replay_violations += game != replay
            scored = sum(
                int(record["points"])
                for record in game.records
                if record["type"] == "shot_made" and record["player"] == athlete
            )
            points.append(scored)
            winner = game.home_team if game.home_score > game.away_score else game.away_team
            team_wins += winner == athlete_team

        ordered = sorted(points)
        tier_metrics[tier] = {
            "mean_points": round(fmean(points), 4),
            "point_deviation": round(pstdev(points), 4),
            "twentieth_percentile_points": ordered[max(0, game_count // 5 - 1)],
            "bad_night_rate": round(sum(value < 14 for value in points) / game_count, 4),
            "team_win_rate": round(team_wins / game_count, 4),
        }

    elite = tier_metrics["elite"]
    volatile = tier_metrics["volatile"]
    failures = []
    if float(elite["point_deviation"]) > float(volatile["point_deviation"]) * 0.9:
        failures.append("elite point-deviation reduction")
    if float(elite["bad_night_rate"]) > float(volatile["bad_night_rate"]) * 0.8:
        failures.append("elite bad-night reduction")
    if int(elite["twentieth_percentile_points"]) < int(
        volatile["twentieth_percentile_points"]
    ) + 1:
        failures.append("elite performance floor")
    if max(
        abs(float(metrics["mean_points"]) - float(elite["mean_points"]))
        for metrics in tier_metrics.values()
    ) > 0.5:
        failures.append("mean-talent preservation")
    if max(float(metrics["team_win_rate"]) for metrics in tier_metrics.values()) - min(
        float(metrics["team_win_rate"]) for metrics in tier_metrics.values()
    ) > 0.05:
        failures.append("team-balance shift")
    if replay_violations:
        failures.append("replay integrity")

    return {
        "version": CONSISTENCY_VERSION,
        "athlete": athlete,
        "games_per_tier": game_count,
        "bad_night_definition": "fewer than 14 points",
        "tiers": tier_metrics,
        "replay_violations": replay_violations,
        "failures": failures,
        "eligible_for_rollout": not failures,
    }


def calibrate_consistency_v2(game_count: int = 1_000) -> dict[str, object]:
    if game_count <= 0:
        raise ValueError("game_count must be positive")
    teams = default_teams()
    players = [player.name for team in teams for player in team.players]
    athlete_results: dict[str, object] = {}
    all_failures: list[str] = []
    replay_violations = 0

    for athlete, (start_seed, bad_night_threshold) in CONSISTENCY_V2_CALIBRATION.items():
        athlete_team = next(
            team.name for team in teams if any(player.name == athlete for player in team.players)
        )
        tier_metrics: dict[str, dict[str, float | int]] = {}
        for tier, parameters in CONSISTENCY_V2_PARAMETERS.items():
            points: list[int] = []
            attempts: list[int] = []
            team_wins = 0
            settings = {player: (0.0, 0.0) for player in players}
            settings[athlete] = parameters
            for seed in range(start_seed, start_seed + game_count):
                game = simulate_game(
                    seed,
                    matchup=teams,
                    initial_shooting_consistency=settings,
                )
                replay = simulate_game(
                    seed,
                    game.action_tape,
                    matchup=teams,
                    initial_shooting_consistency=settings,
                )
                replay_violations += game != replay
                athlete_shots = [
                    record
                    for record in game.records
                    if record["type"] in {"shot_made", "shot_missed"}
                    and record["player"] == athlete
                ]
                points.append(
                    sum(
                        int(record["points"])
                        for record in athlete_shots
                        if record["type"] == "shot_made"
                    )
                )
                attempts.append(len(athlete_shots))
                winner = game.home_team if game.home_score > game.away_score else game.away_team
                team_wins += winner == athlete_team

            ordered = sorted(points)
            tier_metrics[tier] = {
                "mean_points": round(fmean(points), 4),
                "point_deviation": round(pstdev(points), 4),
                "mean_attempts": round(fmean(attempts), 4),
                "bad_night_rate": round(
                    sum(value < bad_night_threshold for value in points) / game_count,
                    4,
                ),
                "twentieth_percentile_points": ordered[max(0, (game_count + 4) // 5 - 1)],
                "ninetieth_percentile_points": ordered[max(0, (9 * game_count + 9) // 10 - 1)],
                "team_win_rate": round(team_wins / game_count, 4),
            }

        elite = tier_metrics["elite"]
        volatile = tier_metrics["volatile"]
        failures: list[str] = []
        if float(elite["point_deviation"]) > float(volatile["point_deviation"]) * 0.9:
            failures.append("elite point-deviation reduction")
        if float(elite["bad_night_rate"]) > float(volatile["bad_night_rate"]) * 0.8:
            failures.append("elite bad-night reduction")
        if int(elite["twentieth_percentile_points"]) < int(
            volatile["twentieth_percentile_points"]
        ) + 1:
            failures.append("elite performance floor")
        if float(elite["bad_night_rate"]) == 0:
            failures.append("bad-night possibility")
        if max(float(value["mean_points"]) for value in tier_metrics.values()) - min(
            float(value["mean_points"]) for value in tier_metrics.values()
        ) > 0.5:
            failures.append("mean-talent preservation")
        if max(float(value["mean_attempts"]) for value in tier_metrics.values()) - min(
            float(value["mean_attempts"]) for value in tier_metrics.values()
        ) > 0.5:
            failures.append("usage preservation")
        if int(elite["ninetieth_percentile_points"]) < int(
            volatile["ninetieth_percentile_points"]
        ) - 2:
            failures.append("exceptional-game preservation")
        if max(float(value["team_win_rate"]) for value in tier_metrics.values()) - min(
            float(value["team_win_rate"]) for value in tier_metrics.values()
        ) > 0.05:
            failures.append("team-balance shift")

        athlete_results[athlete] = {
            "start_seed": start_seed,
            "bad_night_threshold": bad_night_threshold,
            "tiers": tier_metrics,
            "failures": failures,
        }
        all_failures.extend(f"{athlete}: {failure}" for failure in failures)

    if replay_violations:
        all_failures.append("replay integrity")
    return {
        "version": CONSISTENCY_V2_VERSION,
        "games_per_tier": game_count,
        "athletes": athlete_results,
        "replay_violations": replay_violations,
        "failures": all_failures,
        "eligible_for_review": not all_failures,
    }
