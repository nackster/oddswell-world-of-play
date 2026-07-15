from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

from phase0a.simulator import Player, Team, default_teams
from phase0d.league import (
    BETWEEN_GAME_REST_DAYS,
    OFFSEASON_REST_DAYS,
    AvailabilitySnapshot,
    ScheduledGame,
    availability_snapshot,
    build_schedule,
    empty_availability,
    empty_fatigue,
    recover_availability,
    recover_fatigue,
    simulate_scheduled_game,
)


PREDICTION_VERSION = "phase0d4-v1"
PUBLIC_SNAPSHOT_VERSION = "oddswell-public-pregame-v1"
MODEL_NAMES = ("coin", "public_elo", "public_elo_rotation")
MODEL_LABELS = {
    "coin": "Fixed 50%",
    "public_elo": "Public-history Elo",
    "public_elo_rotation": "Elo + public availability/rotation",
}
ELO_K = 20.0
HOME_ADVANTAGE_ELO = 55.0
RATING_DIFFERENCE_ELO = 6.0


@dataclass(frozen=True)
class PredictionRecord:
    season_number: int
    game_number: int
    holdout: bool
    injury_subset: bool
    commitment_json: str
    commitment_sha256: str
    predictions: tuple[tuple[str, float], ...]
    home_win: int
    winner: str
    replay_sha256: str


@dataclass(frozen=True)
class ModelMetrics:
    model: str
    games: int
    accuracy: float
    brier: float
    log_loss: float
    ece: float
    brier_skill: float


@dataclass(frozen=True)
class PredictionStudy:
    warmup_seasons: int
    holdout_seasons: int
    games_per_season: int
    records: tuple[PredictionRecord, ...]
    metrics: tuple[ModelMetrics, ...]
    injury_metrics: tuple[ModelMetrics, ...]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def projected_minutes(team: Team, availability: Mapping[str, int]) -> dict[str, float]:
    available = [player for player in team.players if availability[player.name] == 0]
    if len(available) < 5:
        raise ValueError(f"{team.name} needs at least five available players")
    minutes = {player.name: 0.0 for player in team.players}
    if len(available) == 5:
        for player in available:
            minutes[player.name] = 48.0
    else:
        for player in available[:5]:
            minutes[player.name] = 43.2
        minutes[available[5].name] = 24.0
    return minutes


def public_pregame_snapshot(
    season_number: int,
    fixture: ScheduledGame,
    standings: Mapping[str, tuple[int, int]],
    availability: AvailabilitySnapshot,
    rest_days: int,
    teams: tuple[Team, Team] | None = None,
) -> dict[str, object]:
    roster = teams or default_teams()
    available = dict(availability_snapshot(dict(availability), roster))
    if set(standings) != {team.name for team in roster}:
        raise ValueError("standings must contain every team exactly once")

    def player_public(player: Player, minutes: Mapping[str, float]) -> dict[str, object]:
        return {
            "name": player.name,
            "shooting": player.shooting,
            "passing": player.passing,
            "defense": player.defense,
            "rebounding": player.rebounding,
            "stamina": player.stamina,
            "available": available[player.name] == 0,
            "projected_minutes": minutes[player.name],
        }

    minutes = {team.name: projected_minutes(team, available) for team in roster}
    return {
        "version": PUBLIC_SNAPSHOT_VERSION,
        "season_number": season_number,
        "game_number": fixture.number,
        "home_team": fixture.home.name,
        "away_team": fixture.away.name,
        "standings": [
            {
                "team": team.name,
                "games": sum(standings[team.name]),
                "wins": standings[team.name][0],
                "losses": standings[team.name][1],
            }
            for team in roster
        ],
        "rest_days": {fixture.home.name: rest_days, fixture.away.name: rest_days},
        "rosters": {
            team.name: [player_public(player, minutes[team.name]) for player in team.players]
            for team in roster
        },
    }


def _team_strength(players: list[dict[str, object]]) -> float:
    return sum(
        sum(float(player[key]) for key in ("shooting", "passing", "defense", "rebounding", "stamina"))
        / 5
        * float(player["projected_minutes"])
        / 240
        for player in players
    )


def _elo_probability(difference: float) -> float:
    return 1 / (1 + 10 ** (-difference / 400))


def prediction_probabilities(
    snapshot: Mapping[str, object], elo: Mapping[str, float]
) -> tuple[tuple[str, float], ...]:
    home = str(snapshot["home_team"])
    away = str(snapshot["away_team"])
    rosters = snapshot["rosters"]
    if not isinstance(rosters, dict) or home not in rosters or away not in rosters:
        raise ValueError("snapshot rosters do not match the fixture")
    base_difference = float(elo[home]) - float(elo[away]) + HOME_ADVANTAGE_ELO
    home_strength = _team_strength(rosters[home])
    away_strength = _team_strength(rosters[away])
    values = {
        "coin": 0.5,
        "public_elo": _elo_probability(base_difference),
        "public_elo_rotation": _elo_probability(
            base_difference + RATING_DIFFERENCE_ELO * (home_strength - away_strength)
        ),
    }
    return tuple((name, round(values[name], 8)) for name in MODEL_NAMES)


def verify_prediction_record(record: PredictionRecord) -> bool:
    if hashlib.sha256(record.commitment_json.encode()).hexdigest() != record.commitment_sha256:
        return False
    try:
        payload = json.loads(record.commitment_json)
    except json.JSONDecodeError:
        return False
    if not isinstance(payload, dict) or set(payload) != {"snapshot", "predictions"}:
        return False
    snapshot = payload["snapshot"]
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "version",
        "season_number",
        "game_number",
        "home_team",
        "away_team",
        "standings",
        "rest_days",
        "rosters",
    }:
        return False
    if payload["predictions"] != dict(record.predictions):
        return False
    if record.winner not in {snapshot["home_team"], snapshot["away_team"]}:
        return False
    if record.home_win != int(record.winner == snapshot["home_team"]):
        return False
    try:
        return len(record.replay_sha256) == 64 and int(record.replay_sha256, 16) >= 0
    except ValueError:
        return False


def _metrics(
    records: tuple[PredictionRecord, ...], model: str, reference_brier: float | None = None
) -> ModelMetrics:
    if not records:
        return ModelMetrics(model, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    pairs = [(dict(record.predictions)[model], record.home_win) for record in records]
    count = len(pairs)
    accuracy = sum((probability >= 0.5) == bool(outcome) for probability, outcome in pairs) / count
    brier = sum((probability - outcome) ** 2 for probability, outcome in pairs) / count
    log_loss = -sum(
        outcome * math.log(min(0.999, max(0.001, probability)))
        + (1 - outcome) * math.log(min(0.999, max(0.001, 1 - probability)))
        for probability, outcome in pairs
    ) / count
    bins: list[list[tuple[float, int]]] = [[] for _ in range(5)]
    for probability, outcome in pairs:
        bins[min(4, int(probability * 5))].append((probability, outcome))
    ece = sum(
        len(bucket)
        / count
        * abs(
            sum(probability for probability, _ in bucket) / len(bucket)
            - sum(outcome for _, outcome in bucket) / len(bucket)
        )
        for bucket in bins
        if bucket
    )
    skill = 0.0 if reference_brier in (None, 0) else 1 - brier / reference_brier
    return ModelMetrics(model, count, accuracy, brier, log_loss, ece, skill)


def run_prediction_study(
    warmup_seasons: int = 15,
    holdout_seasons: int = 5,
    games_per_season: int = 20,
    start_seed: int = 14_000,
) -> PredictionStudy:
    if warmup_seasons < 0 or holdout_seasons < 1:
        raise ValueError("warmup must be nonnegative and holdout must be positive")
    teams = default_teams()
    fatigue = empty_fatigue(teams)
    availability = empty_availability(teams)
    elo = {team.name: 1500.0 for team in teams}
    records: list[PredictionRecord] = []

    for season_number in range(1, warmup_seasons + holdout_seasons + 1):
        if season_number > 1:
            fatigue = recover_fatigue(fatigue, OFFSEASON_REST_DAYS, teams)
            availability = recover_availability(availability, OFFSEASON_REST_DAYS, teams)
        standings = {team.name: [0, 0] for team in teams}
        schedule = build_schedule(
            games_per_season,
            start_seed + (season_number - 1) * games_per_season,
            teams,
        )
        for index, fixture in enumerate(schedule):
            rest_days = OFFSEASON_REST_DAYS if index == 0 else BETWEEN_GAME_REST_DAYS
            if index:
                fatigue = recover_fatigue(fatigue, rest_days, teams)
                availability = recover_availability(availability, rest_days, teams)
            snapshot = public_pregame_snapshot(
                season_number,
                fixture,
                {name: tuple(record) for name, record in standings.items()},
                availability,
                rest_days,
                teams,
            )
            predictions = prediction_probabilities(snapshot, elo)
            commitment_json = canonical_json(
                {"snapshot": snapshot, "predictions": dict(predictions)}
            )
            commitment_sha256 = hashlib.sha256(commitment_json.encode()).hexdigest()

            game = simulate_scheduled_game(fixture, fatigue, availability, teams)
            home_win = int(game.winner == game.home_team)
            injury_subset = any(
                not bool(player["available"])
                for players in snapshot["rosters"].values()
                for player in players
            )
            record = PredictionRecord(
                season_number,
                fixture.number,
                season_number > warmup_seasons,
                injury_subset,
                commitment_json,
                commitment_sha256,
                predictions,
                home_win,
                game.winner,
                game.replay_sha256,
            )
            if not verify_prediction_record(record):
                raise RuntimeError(f"prediction commitment failed for season {season_number} game {fixture.number}")
            records.append(record)

            public_elo_probability = dict(predictions)["public_elo"]
            change = ELO_K * (home_win - public_elo_probability)
            elo[game.home_team] += change
            elo[game.away_team] -= change
            standings[game.winner][0] += 1
            standings[game.away_team if game.winner == game.home_team else game.home_team][1] += 1
            fatigue = game.postgame_fatigue
            availability = game.postgame_availability

    all_records = tuple(records)
    holdout = tuple(record for record in all_records if record.holdout)
    coin = _metrics(holdout, "coin")
    metrics = tuple(
        coin if model == "coin" else _metrics(holdout, model, coin.brier)
        for model in MODEL_NAMES
    )
    injury_records = tuple(record for record in holdout if record.injury_subset)
    injury_coin = _metrics(injury_records, "coin")
    injury_metrics = tuple(
        injury_coin if model == "coin" else _metrics(injury_records, model, injury_coin.brier)
        for model in MODEL_NAMES
    )
    return PredictionStudy(
        warmup_seasons,
        holdout_seasons,
        games_per_season,
        all_records,
        metrics,
        injury_metrics,
    )


def render_markdown(study: PredictionStudy) -> str:
    holdout_games = study.holdout_seasons * study.games_per_season
    commitments = sum(record.holdout and verify_prediction_record(record) for record in study.records)
    best = min(study.metrics, key=lambda value: value.brier)
    coin = study.metrics[0]
    conclusion = (
        f"{MODEL_LABELS[best.model]} beat the fixed 50% baseline on locked-holdout Brier score."
        if best.model != "coin" and best.brier < coin.brier
        else "Neither public model beat the fixed 50% baseline on locked-holdout Brier score."
    )
    lines = [
        "---",
        "tags:",
        "  - development",
        "  - simulation",
        "  - prediction",
        "  - evaluation",
        "status: complete",
        "---",
        "",
        "# Phase 0D.4 Public Prediction Evaluation",
        "",
        f"Version `{PREDICTION_VERSION}` evaluates public-only pregame predictions after "
        f"**{study.warmup_seasons} warm-up seasons** on a locked **{study.holdout_seasons}-season / "
        f"{holdout_games}-game holdout**. Cost: **$0.00**.",
        "",
        "## Locked holdout",
        "",
        "| Model | Games | Accuracy | Brier | Log loss | 5-bin ECE | Brier skill vs 50% |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for metric in study.metrics:
        lines.append(
            f"| {MODEL_LABELS[metric.model]} | {metric.games} | {metric.accuracy:.1%} | "
            f"{metric.brier:.4f} | {metric.log_loss:.4f} | {metric.ece:.4f} | "
            f"{metric.brier_skill:+.1%} |"
        )
    lines.extend(
        [
            "",
            f"**Result:** {conclusion}",
            "",
            "## Games with a published absence",
            "",
            "| Model | Games | Accuracy | Brier | Log loss | 5-bin ECE |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for metric in study.injury_metrics:
        lines.append(
            f"| {MODEL_LABELS[metric.model]} | {metric.games} | {metric.accuracy:.1%} | "
            f"{metric.brier:.4f} | {metric.log_loss:.4f} | {metric.ece:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Leakage and timing boundary",
            "",
            "- Each prediction is hashed before the authoritative game transition runs.",
            "- The commitment contains only version, season/game number, team names, public pregame standings, rest days, public roster ratings, published availability, projected minutes, and fixed-model probabilities.",
            "- Seeds, RNG state, scores, winners, replay/action tapes, hidden fatigue, injury risk internals, future games, economy data, and user data are excluded.",
            f"- **{commitments}/{holdout_games}** holdout commitments verify and link afterward to a winner and replay SHA-256.",
            "",
            "## Interpretation",
            "",
            "This is an engineering evaluation of fictional simulator data, not a wagering product or evidence of real-world predictive power. The holdout is not used for tuning. A failed baseline is retained as valid evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OddsWell Phase 0D.4 prediction evaluation.")
    parser.add_argument("--warmup-seasons", type=int, default=15)
    parser.add_argument("--holdout-seasons", type=int, default=5)
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--start-seed", type=int, default=14_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    study = run_prediction_study(
        args.warmup_seasons,
        args.holdout_seasons,
        args.games,
        args.start_seed,
    )
    report = render_markdown(study)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    for metric in study.metrics:
        print(
            f"{metric.model}: games={metric.games} accuracy={metric.accuracy:.3f} "
            f"brier={metric.brier:.4f} log_loss={metric.log_loss:.4f} ece={metric.ece:.4f}"
        )


if __name__ == "__main__":
    main()
