from __future__ import annotations

from copy import deepcopy
from statistics import fmean

from phase0a.simulator import BRAIN_VERSION, Team, clamp, default_teams, simulate_game
from phase0c.replay import replay_manifest, verify_replay_manifest
from phase0d.consistency import (
    DEFAULT_CONSISTENCY_VERSION,
    shooting_consistency_settings,
)


OFFENSIVE_INVOLVEMENT_VERSION = "offensive-involvement-v1"
OFFENSIVE_INVOLVEMENT_WEIGHTS = {"low": 0.85, "standard": 1.0, "featured": 1.15}
OffensiveInvolvementSnapshot = tuple[tuple[str, str, float], ...]


def involvement_snapshot(
    athlete: str,
    tier: str,
    teams: tuple[Team, Team] | None = None,
) -> OffensiveInvolvementSnapshot:
    if tier not in OFFENSIVE_INVOLVEMENT_WEIGHTS:
        raise ValueError(f"unknown offensive involvement tier: {tier!r}")
    names = tuple(player.name for team in (teams or default_teams()) for player in team.players)
    if athlete not in names:
        raise ValueError(f"unknown pilot athlete: {athlete!r}")
    return tuple(
        (name, tier if name == athlete else "standard", OFFENSIVE_INVOLVEMENT_WEIGHTS[tier if name == athlete else "standard"])
        for name in names
    )


def involvement_settings(snapshot: OffensiveInvolvementSnapshot) -> dict[str, float]:
    if not snapshot or len({name for name, _, _ in snapshot}) != len(snapshot):
        raise ValueError("offensive involvement snapshot needs unique athletes")
    for _, tier, weight in snapshot:
        if tier not in OFFENSIVE_INVOLVEMENT_WEIGHTS or weight != OFFENSIVE_INVOLVEMENT_WEIGHTS[tier]:
            raise ValueError("offensive involvement tier and weight do not match")
    return {name: weight for name, _, weight in snapshot}


def _metrics(game: object, athlete: str) -> tuple[int, int, int, int, float, int]:
    records = game.records
    starts = sum(
        record["type"] == "possession_started" and record["ballhandler"] == athlete
        for record in records
    )
    pass_targets = sum(
        record["type"] == "brain_decision"
        and record["action"]["role"] == "offense"
        and record["action"]["kind"] == "pass"
        and record["action"]["target"] == athlete
        for record in records
    )
    shots = [
        record
        for record in records
        if record["type"] in {"shot_made", "shot_missed"} and record["player"] == athlete
    ]
    made = sum(record["type"] == "shot_made" for record in shots)
    points = sum(int(record["points"]) for record in shots if record["type"] == "shot_made")
    possessions = int(records[-1]["possessions"])
    return starts, pass_targets, len(shots), made, points, possessions


def evaluate_offensive_involvement(
    game_count: int = 200,
    start_seed: int = 76_000,
    athlete: str = "Jalen Cross",
) -> dict[str, object]:
    if game_count <= 0:
        raise ValueError("game_count must be positive")
    teams = default_teams()
    consistency = shooting_consistency_settings(DEFAULT_CONSISTENCY_VERSION, teams=teams)
    values = {
        tier: {key: [] for key in ("starts", "targets", "shots", "made", "points", "possessions")}
        for tier in OFFENSIVE_INVOLVEMENT_WEIGHTS
    }
    score_differences = {tier: 0 for tier in OFFENSIVE_INVOLVEMENT_WEIGHTS}
    winner_differences = {tier: 0 for tier in OFFENSIVE_INVOLVEMENT_WEIGHTS}
    omission_replay_violations = replay_violations = manifest_violations = 0
    shot_formula_violations = 0

    for seed in range(start_seed, start_seed + game_count):
        omitted = simulate_game(
            seed, matchup=teams, initial_shooting_consistency=consistency
        )
        omitted_replay = simulate_game(
            seed,
            omitted.action_tape,
            matchup=teams,
            initial_shooting_consistency=consistency,
        )
        omission_replay_violations += omitted != omitted_replay
        pilot_games = {}

        for tier in OFFENSIVE_INVOLVEMENT_WEIGHTS:
            snapshot = involvement_snapshot(athlete, tier, teams)
            settings = involvement_settings(snapshot)
            game = simulate_game(
                seed,
                matchup=teams,
                initial_shooting_consistency=consistency,
                initial_offensive_involvement=settings,
            )
            replay = simulate_game(
                seed,
                game.action_tape,
                matchup=teams,
                initial_shooting_consistency=consistency,
                initial_offensive_involvement=settings,
            )
            replay_violations += game != replay
            manifest = replay_manifest(
                game,
                teams,
                BRAIN_VERSION,
                {
                    "offensive_involvement_version": OFFENSIVE_INVOLVEMENT_VERSION,
                    "offensive_involvement_snapshot": snapshot,
                },
            )
            manifest_violations += not verify_replay_manifest(manifest)
            if seed == start_seed and tier == "featured":
                tampered = deepcopy(manifest)
                changed_snapshot = list(
                    tampered["payload"]["audit"]["offensive_involvement_snapshot"]
                )
                changed_snapshot[0] = (
                    athlete,
                    "low",
                    0.85,
                )
                tampered["payload"]["audit"]["offensive_involvement_snapshot"] = tuple(
                    changed_snapshot
                )
                manifest_violations += verify_replay_manifest(tampered)

            starts, targets, shots, made, points, possessions = _metrics(game, athlete)
            for key, value in zip(values[tier], (starts, targets, shots, made, points, possessions)):
                values[tier][key].append(value)
            shot_formula_violations += sum(
                abs(
                    float(record["probability"])
                    - round(
                        clamp(
                            float(record["base_probability"])
                            + float(record["consistency_correction"]),
                            0.08,
                            0.78,
                        ),
                        4,
                    )
                )
                > 0.00011
                or any("involvement" in key for key in record)
                for record in game.records
                if record["type"] in {"shot_made", "shot_missed"}
            )
            pilot_games[tier] = game

        standard = pilot_games["standard"]
        if omitted.action_tape != standard.action_tape or (
            omitted.home_score,
            omitted.away_score,
        ) != (standard.home_score, standard.away_score):
            omission_replay_violations += 1
        for tier in OFFENSIVE_INVOLVEMENT_WEIGHTS:
            if tier == "standard":
                continue
            game = pilot_games[tier]
            score_differences[tier] += (game.home_score, game.away_score) != (
                standard.home_score,
                standard.away_score,
            )
            winner_differences[tier] += (
                game.home_score > game.away_score
            ) != (standard.home_score > standard.away_score)

    tiers: dict[str, object] = {}
    for tier, samples in values.items():
        attempts = sum(samples["shots"])
        tiers[tier] = {
            "weight": OFFENSIVE_INVOLVEMENT_WEIGHTS[tier],
            "mean_initial_possessions": round(fmean(samples["starts"]), 4),
            "mean_pass_targets": round(fmean(samples["targets"]), 4),
            "mean_selection_opportunities": round(
                fmean(a + b for a, b in zip(samples["starts"], samples["targets"])), 4
            ),
            "mean_shot_attempts": round(fmean(samples["shots"]), 4),
            "field_goal_percentage": round(sum(samples["made"]) / attempts, 4)
            if attempts
            else 0.0,
            "mean_points": round(fmean(samples["points"]), 4),
            "mean_team_possessions": round(fmean(samples["possessions"]) / 2, 4),
            "score_differences_from_standard": score_differences[tier],
            "winner_differences_from_standard": winner_differences[tier],
        }

    opportunities = [
        tiers[tier]["mean_selection_opportunities"]
        for tier in ("low", "standard", "featured")
    ]
    failures = []
    if not opportunities[0] < opportunities[1] < opportunities[2]:
        failures.append("ordered opportunity")
    if omission_replay_violations:
        failures.append("omitted behavior")
    if replay_violations:
        failures.append("exact replay")
    if manifest_violations:
        failures.append("manifest binding")
    if shot_formula_violations:
        failures.append("rating-driven shot formula")
    return {
        "version": OFFENSIVE_INVOLVEMENT_VERSION,
        "athlete": athlete,
        "games_per_tier": game_count,
        "scope": "OPPORTUNITY ONLY",
        "consistency_version": DEFAULT_CONSISTENCY_VERSION,
        "tiers": tiers,
        "omission_replay_violations": omission_replay_violations,
        "replay_violations": replay_violations,
        "manifest_violations": manifest_violations,
        "shot_formula_violations": shot_formula_violations,
        "failures": failures,
        "eligible_for_review": not failures,
    }
