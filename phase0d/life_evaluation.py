from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from phase0a.simulator import GameResult, simulate_game
from phase0d.career import teams_for_season
from phase0d.consistency import CONSISTENCY_DISABLED_VERSION
from phase0d.involvement import OFFENSIVE_INVOLVEMENT_DISABLED_VERSION
from phase0d.league import new_league, simulate_next_season
from phase0d.life import (
    LIFE_BRAIN_V1_VERSION,
    LIFE_BRAIN_V2_VERSION,
    OFF_DAY_PREFERENCES,
    choose_life_action,
)


LIFE_EVALUATION_VERSION = "life-evaluation-v1"


@dataclass(frozen=True)
class LifeEvaluation:
    version: str
    policy_version: str
    seasons: int
    games: int
    decisions: int
    expected_decisions: int
    choice_counts: tuple[tuple[str, int], ...]
    choice_shares: tuple[tuple[str, float], ...]
    choices_by_season: tuple[tuple[int, tuple[tuple[str, int], ...]], ...]
    choices_by_athlete: tuple[tuple[str, int], ...]
    choices_by_preference: tuple[tuple[str, tuple[tuple[str, int], ...]], ...]
    policy_violations: int
    tenure_violations: int
    reconstructed_games: int
    readiness_exposures: int
    readiness_exposure_rate: float
    mean_readiness: float
    mean_active_readiness: float
    max_readiness: float
    net_fatigue_change: float
    recovery_days_saved: int
    point_change_per_team: float
    field_goal_percentage_point_change: float
    turnover_change_per_team_game: float
    winner_flips: int
    mean_absolute_margin_change: float


def _box_totals(game: GameResult) -> tuple[int, int, int]:
    made = attempts = turnovers = 0
    for record in game.records:
        if record["type"] in {"shot_made", "shot_missed"}:
            attempts += 1
            made += record["type"] == "shot_made"
        elif record["type"] == "turnover":
            turnovers += 1
    return made, attempts, turnovers


@lru_cache(maxsize=2)
def _run_life_evaluation(policy_version: str) -> LifeEvaluation:
    state = new_league(15_000)
    for season_number in range(1, 5):
        state = simulate_next_season(
            state, 20, teams_for_season(season_number),
            life_policy_version=policy_version,
            consistency_version=CONSISTENCY_DISABLED_VERSION,
            offensive_involvement_version=OFFENSIVE_INVOLVEMENT_DISABLED_VERSION,
        )

    choices = Counter()
    choices_by_season: list[tuple[int, tuple[tuple[str, int], ...]]] = []
    choices_by_athlete = Counter()
    choices_by_preference = {"practice": Counter(), "social": Counter()}
    policy_violations = tenure_violations = reconstructed_games = 0
    readiness_values = []
    net_fatigue_change = 0.0
    recovery_days_saved = 0
    actual_points = control_points = 0
    actual_made = actual_attempts = actual_turnovers = 0
    control_made = control_attempts = control_turnovers = 0
    winner_flips = 0
    margin_changes = []

    for season in state.seasons:
        teams = teams_for_season(season.season_number)
        team_by_name = {team.name: team for team in teams}
        roster = tuple(player.name for team in teams for player in team.players)
        roster_index = {name: index for index, name in enumerate(roster)}
        season_choices = Counter()
        for archived in season.games:
            matchup = (team_by_name[archived.home_team], team_by_name[archived.away_team])
            readiness = dict(archived.pregame_readiness)
            actual = simulate_game(
                archived.seed,
                matchup=matchup,
                initial_fatigue=dict(archived.pregame_fatigue),
                initial_availability=dict(archived.pregame_availability),
                initial_readiness=readiness,
            )
            control = simulate_game(
                archived.seed,
                matchup=matchup,
                initial_fatigue=dict(archived.pregame_fatigue),
                initial_availability=dict(archived.pregame_availability),
                initial_readiness={name: 0.0 for name in roster},
            )
            reconstructed_games += (
                actual.home_score == archived.home_score
                and actual.away_score == archived.away_score
                and dict(actual.minutes_played) == dict(archived.minutes_played)
            )
            actual_points += actual.home_score + actual.away_score
            control_points += control.home_score + control.away_score
            made, attempts, turnovers = _box_totals(actual)
            actual_made += made
            actual_attempts += attempts
            actual_turnovers += turnovers
            made, attempts, turnovers = _box_totals(control)
            control_made += made
            control_attempts += attempts
            control_turnovers += turnovers
            actual_winner = actual.home_team if actual.home_score > actual.away_score else actual.away_team
            control_winner = control.home_team if control.home_score > control.away_score else control.away_team
            winner_flips += actual_winner != control_winner
            margin_changes.append(
                abs(
                    (actual.home_score - actual.away_score)
                    - (control.home_score - control.away_score)
                )
            )

            for decision in archived.life_decisions:
                choices[decision.selected] += 1
                season_choices[decision.selected] += 1
                choices_by_athlete[decision.athlete] += 1
                choices_by_preference[OFF_DAY_PREFERENCES[decision.athlete]][decision.selected] += 1
                tenure_violations += decision.athlete not in roster_index
                if decision.athlete in roster_index:
                    expected = choose_life_action(
                        decision.athlete,
                        decision.game_number,
                        roster_index[decision.athlete],
                        decision.fatigue_before,
                        decision.recovery_before,
                        policy_version=decision.policy_version,
                    )
                    policy_violations += expected != decision.selected
                readiness_values.append(decision.readiness)
                net_fatigue_change += decision.fatigue_after - decision.fatigue_before
                recovery_days_saved += decision.recovery_before - decision.recovery_after
        choices_by_season.append((season.season_number, tuple(sorted(season_choices.items()))))

    decisions = sum(choices.values())
    expected_decisions = sum((len(season.games) - 1) * 12 for season in state.seasons)
    active_readiness = [value for value in readiness_values if value]
    team_games = len(margin_changes) * 2
    return LifeEvaluation(
        LIFE_EVALUATION_VERSION,
        policy_version,
        len(state.seasons),
        len(margin_changes),
        decisions,
        expected_decisions,
        tuple(sorted(choices.items())),
        tuple((choice, round(count / decisions, 4)) for choice, count in sorted(choices.items())),
        tuple(choices_by_season),
        tuple(sorted(choices_by_athlete.items())),
        tuple(
            (preference, tuple(sorted(counts.items())))
            for preference, counts in choices_by_preference.items()
        ),
        policy_violations,
        tenure_violations,
        reconstructed_games,
        len(active_readiness),
        round(len(active_readiness) / decisions, 4),
        round(sum(readiness_values) / decisions, 6),
        round(sum(active_readiness) / len(active_readiness), 6),
        max(readiness_values),
        round(net_fatigue_change, 2),
        recovery_days_saved,
        round((actual_points - control_points) / team_games, 4),
        round((actual_made / actual_attempts - control_made / control_attempts) * 100, 4),
        round((actual_turnovers - control_turnovers) / team_games, 4),
        winner_flips,
        round(sum(margin_changes) / len(margin_changes), 3),
    )


def run_life_evaluation() -> LifeEvaluation:
    return _run_life_evaluation(LIFE_BRAIN_V1_VERSION)


def run_life_v2_pilot() -> LifeEvaluation:
    return _run_life_evaluation(LIFE_BRAIN_V2_VERSION)
