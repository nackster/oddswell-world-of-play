from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
import hashlib
import json

from phase0d.career import teams_for_season
from phase0d.consistency import CONSISTENCY_DISABLED_VERSION
from phase0d.involvement import OFFENSIVE_INVOLVEMENT_DISABLED_VERSION
from phase0d.league import (
    LEGACY_STATE_SCHEMA,
    LeagueState,
    ScheduledGame,
    new_league,
    simulate_next_season,
    simulate_scheduled_game,
)
from phase0d.life import (
    LIFE_BRAIN_V3_VERSION,
    LIFE_BRAIN_V4_VERSION,
    LIFE_BRAIN_V1_VERSION,
    LIFE_BRAIN_V2_VERSION,
    OFF_DAY_PREFERENCES,
    choose_life_action,
    next_routine_streak,
    recent_scoring_form,
)


LIFE_MULTISEED_VERSION = "life-multiseed-v1"
SEED_BLOCKS = tuple(30_000 + 80 * index for index in range(10))
SEASONS_PER_BLOCK = 4
GAMES_PER_SEASON = 20


@dataclass(frozen=True)
class PreferenceMetrics:
    preference: str
    decisions: int
    choice_counts: tuple[tuple[str, int], ...]
    readiness_exposures: int
    readiness_exposure_rate: float
    mean_readiness: float
    max_readiness: float
    net_fatigue_change: float
    recovery_days_saved: int
    active_player_games: int
    minutes_per_active_game: float
    high_workload_rate: float
    mean_pregame_fatigue: float
    max_pregame_fatigue: float
    injuries: int
    injury_rate: float
    missed_player_games: int
    missed_game_rate: float


@dataclass(frozen=True)
class PolicyMetrics:
    policy_version: str
    games: int
    decisions: int
    choice_counts: tuple[tuple[str, int], ...]
    choice_shares: tuple[tuple[str, float], ...]
    readiness_exposures: int
    mean_readiness: float
    max_readiness: float
    net_fatigue_change: float
    recovery_days_saved: int
    active_player_games: int
    injuries: int
    injury_rate: float
    scheduled_player_games: int
    missed_player_games: int
    missed_game_rate: float
    zero_minute_absences: int
    minimum_available: int
    mean_team_points: float
    harbor_win_rate: float
    policy_violations: int
    tenure_violations: int
    version_violations: int
    preferences: tuple[PreferenceMetrics, ...]


@dataclass(frozen=True)
class BlockComparison:
    start_seed: int
    v1: PolicyMetrics
    v2: PolicyMetrics
    action_divergence: int
    winner_disagreements: int
    mean_absolute_margin_difference: float


@dataclass(frozen=True)
class MultiSeedEvaluation:
    version: str
    state_schema: str
    seed_blocks: tuple[int, ...]
    seasons_per_block: int
    games_per_season: int
    games_per_policy: int
    v1: PolicyMetrics
    v2: PolicyMetrics
    blocks: tuple[BlockComparison, ...]
    action_divergence: int
    winner_disagreements: int
    mean_absolute_margin_difference: float
    injury_rate_change_points: float
    missed_game_rate_change_points: float
    v2_preference_injury_gap_points: float
    v2_preference_missed_gap_points: float
    fatigue_difference_in_differences: float
    minutes_difference_in_differences: float
    high_workload_difference_in_differences_points: float
    injury_difference_in_differences_points: float
    missed_game_difference_in_differences_points: float
    readiness_difference_in_differences: float
    readiness_exposure_difference_in_differences_points: float
    mean_team_points_shift: float
    harbor_win_rate_shift_points: float
    winner_disagreement_rate: float
    failures: tuple[str, ...]
    promotion_status: str
    sha256: str


def _league(start_seed: int, policy_version: str) -> LeagueState:
    state = new_league(start_seed)
    for season_number in range(1, SEASONS_PER_BLOCK + 1):
        state = simulate_next_season(
            state,
            GAMES_PER_SEASON,
            teams_for_season(season_number),
            life_policy_version=policy_version,
            consistency_version=CONSISTENCY_DISABLED_VERSION,
            offensive_involvement_version=OFFENSIVE_INVOLVEMENT_DISABLED_VERSION,
        )
    return state


def _summarize(states: tuple[LeagueState, ...], policy_version: str) -> PolicyMetrics:
    choices = Counter()
    readiness = []
    fatigue_change = 0.0
    recovery_days = 0
    active = injuries = scheduled = missed = zero_minute_absences = 0
    minimum_available = 6
    total_points = harbor_wins = games = 0
    policy_violations = tenure_violations = version_violations = 0
    groups = {
        preference: {
            "choices": Counter(),
            "readiness": [],
            "fatigue_change": 0.0,
            "recovery_days": 0,
            "active": 0,
            "minutes": 0.0,
            "high_workload": 0,
            "fatigue": [],
            "injuries": 0,
            "scheduled": 0,
            "missed": 0,
        }
        for preference in ("practice", "social")
    }

    for state in states:
        for season in state.seasons:
            teams = teams_for_season(season.season_number)
            roster = tuple(player.name for team in teams for player in team.players)
            roster_index = {name: index for index, name in enumerate(roster)}
            routine_streaks = {name: 0 for name in roster}
            scoring_history: dict[str, tuple[tuple[int, float], ...]] = {
                name: () for name in roster
            }
            for game in season.games:
                games += 1
                total_points += game.home_score + game.away_score
                harbor_wins += game.winner == "Harbor City Waves"
                before = dict(game.pregame_availability)
                after = dict(game.postgame_availability)
                minutes = dict(game.minutes_played)
                fatigue = dict(game.pregame_fatigue)
                for team in teams:
                    minimum_available = min(
                        minimum_available,
                        sum(before[player.name] == 0 for player in team.players),
                    )
                for name in roster:
                    preference = OFF_DAY_PREFERENCES[name]
                    group = groups[preference]
                    scheduled += 1
                    group["scheduled"] += 1
                    if before[name] == 0:
                        active += 1
                        group["active"] += 1
                        group["minutes"] += minutes[name]
                        group["high_workload"] += minutes[name] > 36
                        group["fatigue"].append(fatigue[name])
                        new_injury = after[name] > 0
                        injuries += new_injury
                        group["injuries"] += new_injury
                    else:
                        missed += 1
                        group["missed"] += 1
                        zero_minute_absences += minutes[name] == 0

                for decision in game.life_decisions:
                    preference = OFF_DAY_PREFERENCES[decision.athlete]
                    group = groups[preference]
                    choices[decision.selected] += 1
                    group["choices"][decision.selected] += 1
                    readiness.append(decision.readiness)
                    group["readiness"].append(decision.readiness)
                    delta = decision.fatigue_after - decision.fatigue_before
                    fatigue_change += delta
                    group["fatigue_change"] += delta
                    days = decision.recovery_before - decision.recovery_after
                    recovery_days += days
                    group["recovery_days"] += days
                    tenure_violations += decision.athlete not in roster_index
                    version_violations += decision.policy_version != policy_version
                    if decision.athlete in roster_index:
                        scoring_form = (
                            recent_scoring_form(scoring_history[decision.athlete])
                            if decision.policy_version == LIFE_BRAIN_V4_VERSION
                            else "typical"
                        )
                        expected = choose_life_action(
                            decision.athlete,
                            decision.game_number,
                            roster_index[decision.athlete],
                            decision.fatigue_before,
                            decision.recovery_before,
                            policy_version=decision.policy_version,
                            routine_streak=(
                                routine_streaks[decision.athlete]
                                if decision.policy_version in {
                                    LIFE_BRAIN_V3_VERSION, LIFE_BRAIN_V4_VERSION
                                }
                                else 0
                            ),
                            recent_scoring_form=scoring_form,
                        )
                        policy_violations += expected != decision.selected
                        if decision.policy_version in {
                            LIFE_BRAIN_V3_VERSION, LIFE_BRAIN_V4_VERSION
                        }:
                            routine_streaks[decision.athlete] = next_routine_streak(
                                routine_streaks[decision.athlete], decision.selected
                            )
                if policy_version == LIFE_BRAIN_V4_VERSION:
                    team_by_name = {team.name: team for team in teams}
                    points: dict[str, int] = {}
                    simulate_scheduled_game(
                        ScheduledGame(
                            game.number,
                            game.seed,
                            team_by_name[game.home_team],
                            team_by_name[game.away_team],
                        ),
                        game.pregame_fatigue,
                        game.pregame_availability,
                        teams,
                        game.pregame_readiness,
                        game.life_decisions,
                        life_policy_version=policy_version,
                        consistency_version=CONSISTENCY_DISABLED_VERSION,
                        offensive_involvement_version=OFFENSIVE_INVOLVEMENT_DISABLED_VERSION,
                        _player_points=points,
                    )
                    minutes = dict(game.minutes_played)
                    scoring_history = {
                        name: history + ((points[name], minutes[name]),)
                        for name, history in scoring_history.items()
                    }

    preferences = []
    for preference, group in groups.items():
        values = group["readiness"]
        fatigue_values = group["fatigue"]
        preferences.append(PreferenceMetrics(
            preference,
            sum(group["choices"].values()),
            tuple(sorted(group["choices"].items())),
            sum(value > 0 for value in values),
            round(sum(value > 0 for value in values) / len(values), 6),
            round(sum(values) / len(values), 6),
            max(values),
            round(group["fatigue_change"], 2),
            group["recovery_days"],
            group["active"],
            round(group["minutes"] / group["active"], 4),
            round(group["high_workload"] / group["active"], 6),
            round(sum(fatigue_values) / len(fatigue_values), 6),
            max(fatigue_values),
            group["injuries"],
            round(group["injuries"] / group["active"], 6),
            group["missed"],
            round(group["missed"] / group["scheduled"], 6),
        ))

    decisions = sum(choices.values())
    return PolicyMetrics(
        policy_version,
        games,
        decisions,
        tuple(sorted(choices.items())),
        tuple((choice, round(count / decisions, 6)) for choice, count in sorted(choices.items())),
        sum(value > 0 for value in readiness),
        round(sum(readiness) / len(readiness), 6),
        max(readiness),
        round(fatigue_change, 2),
        recovery_days,
        active,
        injuries,
        round(injuries / active, 6),
        scheduled,
        missed,
        round(missed / scheduled, 6),
        zero_minute_absences,
        minimum_available,
        round(total_points / (games * 2), 4),
        round(harbor_wins / games, 6),
        policy_violations,
        tenure_violations,
        version_violations,
        tuple(preferences),
    )


def _compare(v1: LeagueState, v2: LeagueState) -> tuple[int, int, float]:
    actions = winners = 0
    margins = []
    for v1_season, v2_season in zip(v1.seasons, v2.seasons, strict=True):
        for v1_game, v2_game in zip(v1_season.games, v2_season.games, strict=True):
            actions += sum(
                first.selected != second.selected
                for first, second in zip(v1_game.life_decisions, v2_game.life_decisions, strict=True)
            )
            winners += v1_game.winner != v2_game.winner
            margins.append(abs(
                (v1_game.home_score - v1_game.away_score)
                - (v2_game.home_score - v2_game.away_score)
            ))
    return actions, winners, round(sum(margins) / len(margins), 4)


@lru_cache(maxsize=1)
def run_life_multiseed_evaluation() -> MultiSeedEvaluation:
    v1_states = tuple(_league(seed, LIFE_BRAIN_V1_VERSION) for seed in SEED_BLOCKS)
    v2_states = tuple(_league(seed, LIFE_BRAIN_V2_VERSION) for seed in SEED_BLOCKS)
    v1 = _summarize(v1_states, LIFE_BRAIN_V1_VERSION)
    v2 = _summarize(v2_states, LIFE_BRAIN_V2_VERSION)
    blocks = []
    total_actions = total_winners = 0
    weighted_margin = 0.0
    for seed, v1_state, v2_state in zip(SEED_BLOCKS, v1_states, v2_states, strict=True):
        actions, winners, margin = _compare(v1_state, v2_state)
        total_actions += actions
        total_winners += winners
        weighted_margin += margin * SEASONS_PER_BLOCK * GAMES_PER_SEASON
        blocks.append(BlockComparison(
            seed,
            _summarize((v1_state,), LIFE_BRAIN_V1_VERSION),
            _summarize((v2_state,), LIFE_BRAIN_V2_VERSION),
            actions,
            winners,
            margin,
        ))

    v2_groups = {group.preference: group for group in v2.preferences}
    v1_groups = {group.preference: group for group in v1.preferences}
    def difference_in_differences(name: str, scale: float = 1.0) -> float:
        return round((
            getattr(v2_groups["practice"], name) - getattr(v2_groups["social"], name)
            - getattr(v1_groups["practice"], name) + getattr(v1_groups["social"], name)
        ) * scale, 6)

    injury_change = round((v2.injury_rate - v1.injury_rate) * 100, 4)
    missed_change = round((v2.missed_game_rate - v1.missed_game_rate) * 100, 4)
    injury_gap = round(abs(
        v2_groups["practice"].injury_rate - v2_groups["social"].injury_rate
    ) * 100, 4)
    missed_gap = round(abs(
        v2_groups["practice"].missed_game_rate - v2_groups["social"].missed_game_rate
    ) * 100, 4)
    fatigue_did = difference_in_differences("mean_pregame_fatigue")
    minutes_did = difference_in_differences("minutes_per_active_game")
    high_workload_did = difference_in_differences("high_workload_rate", 100)
    injury_did = difference_in_differences("injury_rate", 100)
    missed_did = difference_in_differences("missed_game_rate", 100)
    readiness_did = difference_in_differences("mean_readiness")
    exposure_did = difference_in_differences("readiness_exposure_rate", 100)
    points_shift = round(v2.mean_team_points - v1.mean_team_points, 4)
    win_rate_shift = round((v2.harbor_win_rate - v1.harbor_win_rate) * 100, 4)
    winner_rate = round(total_winners / (len(SEED_BLOCKS) * SEASONS_PER_BLOCK * GAMES_PER_SEASON), 6)
    expected_decisions = len(SEED_BLOCKS) * SEASONS_PER_BLOCK * (GAMES_PER_SEASON - 1) * 12
    failures = []
    if v1.decisions != expected_decisions or v2.decisions != expected_decisions:
        failures.append("decision count")
    if any(metric.policy_violations or metric.tenure_violations or metric.version_violations for metric in (v1, v2)):
        failures.append("policy integrity")
    if dict(v2_groups["practice"].choice_counts).get("socialize", 0):
        failures.append("practice preference adherence")
    if dict(v2_groups["social"].choice_counts).get("train", 0):
        failures.append("social preference adherence")
    if max(v1.max_readiness, v2.max_readiness) > 0.015:
        failures.append("readiness bound")
    if max(group.max_pregame_fatigue for metric in (v1, v2) for group in metric.preferences) > 0.35:
        failures.append("fatigue bound")
    if min(v1.minimum_available, v2.minimum_available) < 5:
        failures.append("availability floor")
    if v1.zero_minute_absences != v1.missed_player_games or v2.zero_minute_absences != v2.missed_player_games:
        failures.append("absence minutes")
    if injury_change > 0.5:
        failures.append("overall injury rate")
    if missed_change > 1.0:
        failures.append("overall missed-game rate")
    if injury_gap > 0.75:
        failures.append("preference injury gap")
    if missed_gap > 1.0:
        failures.append("preference missed-game gap")
    for failed, name in (
        (abs(fatigue_did) > 0.03, "fatigue difference-in-differences"),
        (abs(minutes_did) > 2.0, "minutes difference-in-differences"),
        (abs(high_workload_did) > 5.0, "workload difference-in-differences"),
        (abs(injury_did) > 0.5, "injury difference-in-differences"),
        (abs(missed_did) > 0.5, "missed-game difference-in-differences"),
        (abs(readiness_did) > 0.0025, "readiness difference-in-differences"),
        (abs(exposure_did) > 10.0, "readiness exposure difference-in-differences"),
        (abs(points_shift) > 2.0, "team scoring shift"),
        (abs(win_rate_shift) > 5.0, "team win-rate shift"),
        (winner_rate > 0.25, "winner disagreement rate"),
    ):
        if failed:
            failures.append(name)
    if any(block.v1.decisions != 912 or block.v2.decisions != 912 for block in blocks):
        failures.append("per-block decision count")

    result = MultiSeedEvaluation(
        LIFE_MULTISEED_VERSION,
        LEGACY_STATE_SCHEMA,
        SEED_BLOCKS,
        SEASONS_PER_BLOCK,
        GAMES_PER_SEASON,
        len(SEED_BLOCKS) * SEASONS_PER_BLOCK * GAMES_PER_SEASON,
        v1,
        v2,
        tuple(blocks),
        total_actions,
        total_winners,
        round(
            weighted_margin / (len(SEED_BLOCKS) * SEASONS_PER_BLOCK * GAMES_PER_SEASON), 4
        ),
        injury_change,
        missed_change,
        injury_gap,
        missed_gap,
        fatigue_did,
        minutes_did,
        high_workload_did,
        injury_did,
        missed_did,
        readiness_did,
        exposure_did,
        points_shift,
        win_rate_shift,
        winner_rate,
        tuple(failures),
        "HOLD" if failures else "ELIGIBLE FOR LATER REVIEW",
        "",
    )
    payload = asdict(result)
    payload.pop("sha256")
    digest = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    return replace(result, sha256=digest)
