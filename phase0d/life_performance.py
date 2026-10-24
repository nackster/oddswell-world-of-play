from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
import hashlib
import json

from phase0d.career import teams_for_season
from phase0d.consistency import CONSISTENCY_DISABLED_VERSION
from phase0d.involvement import OFFENSIVE_INVOLVEMENT_DISABLED_VERSION
from phase0d.league import LEGACY_STATE_SCHEMA, LeagueState, ScheduledGame, simulate_scheduled_game
from phase0d.life import (
    HIGH_FATIGUE,
    LIFE_BRAIN_V3_VERSION,
    LIFE_BRAIN_V4_VERSION,
    OFF_DAY_PREFERENCES,
    apply_life_action,
    choose_life_action,
    next_routine_streak,
    recent_scoring_form,
)
from phase0d.life_multiseed import (
    GAMES_PER_SEASON,
    SEASONS_PER_BLOCK,
    PolicyMetrics,
    _compare,
    _league,
    _summarize,
)
from phase0d.life_routine import _audit as audit_routine


LIFE_PERFORMANCE_VERSION = "life-performance-v1"
SEED_BLOCKS = tuple(50_000 + 80 * index for index in range(10))
PERFORMANCE_REASONS = {
    "below": "Recent scoring below earlier same-season average",
    "above": "Recent scoring above earlier same-season average",
}


@dataclass(frozen=True)
class PerformanceGroupMetrics:
    preference: str
    decisions: int
    covered_decisions: int
    coverage_rate: float
    signal_counts: tuple[tuple[str, int], ...]
    response_opportunities: int
    responses: int
    response_rate: float


@dataclass(frozen=True)
class PerformanceAudit:
    decisions: int
    covered_decisions: int
    no_appearance_defaults: int
    insufficient_history_defaults: int
    signal_counts: tuple[tuple[str, int], ...]
    response_opportunities: int
    responses: int
    max_abs_streak: int
    max_elective_run: int
    policy_violations: int
    version_violations: int
    tenure_violations: int
    chronology_violations: int
    classification_violations: int
    precedence_violations: int
    transition_violations: int
    ordering_violations: int
    replay_violations: int
    groups: tuple[PerformanceGroupMetrics, ...]

    @property
    def violations(self) -> int:
        return sum((
            self.policy_violations,
            self.version_violations,
            self.tenure_violations,
            self.chronology_violations,
            self.classification_violations,
            self.precedence_violations,
            self.transition_violations,
            self.ordering_violations,
            self.replay_violations,
        ))


@dataclass(frozen=True)
class PerformanceBlock:
    start_seed: int
    v3_decisions: int
    v4_decisions: int
    covered_decisions: int
    responses: int
    action_divergence: int
    winner_disagreements: int
    mean_absolute_margin_difference: float


@dataclass(frozen=True)
class PerformanceEvaluation:
    version: str
    state_schema: str
    seed_blocks: tuple[int, ...]
    seasons_per_block: int
    games_per_season: int
    games_per_policy: int
    v3: PolicyMetrics
    v4: PolicyMetrics
    performance: PerformanceAudit
    blocks: tuple[PerformanceBlock, ...]
    action_divergence: int
    winner_disagreements: int
    mean_absolute_margin_difference: float
    injury_rate_change_points: float
    missed_game_rate_change_points: float
    v4_preference_injury_gap_points: float
    v4_preference_missed_gap_points: float
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


def _audit(states: tuple[LeagueState, ...]) -> PerformanceAudit:
    signals = Counter()
    groups = {
        preference: {
            "decisions": 0,
            "covered": 0,
            "signals": Counter(),
            "opportunities": 0,
            "responses": 0,
        }
        for preference in ("practice", "social")
    }
    decisions = covered = no_appearance = insufficient = opportunities = responses = 0
    policy = version = tenure = chronology = classification = precedence = transition = ordering = replay = 0
    max_abs_streak = max_elective_run = 0

    for state in states:
        for season in state.seasons:
            teams = teams_for_season(season.season_number)
            roster = tuple(player.name for team in teams for player in team.players)
            roster_set = set(roster)
            team_by_name = {team.name: team for team in teams}
            streaks = {name: 0 for name in roster}
            history: dict[str, tuple[tuple[int, float], ...]] = {name: () for name in roster}
            last_elective = {name: "" for name in roster}
            elective_runs = {name: 0 for name in roster}

            for game_index, game in enumerate(season.games):
                ordering += tuple(decision.athlete for decision in game.life_decisions) != (
                    () if game_index == 0 else roster
                )
                for decision in game.life_decisions:
                    decisions += 1
                    athlete = decision.athlete
                    if athlete not in roster_set:
                        tenure += 1
                        continue
                    form = recent_scoring_form(history[athlete])
                    earlier_appearances = sum(minutes > 0 for _, minutes in history[athlete][:-1])
                    is_covered = bool(history[athlete]) and history[athlete][-1][1] > 0 and earlier_appearances >= 3
                    covered += is_covered
                    no_appearance += bool(history[athlete]) and history[athlete][-1][1] <= 0
                    insufficient += not is_covered and not (
                        history[athlete] and history[athlete][-1][1] <= 0
                    )
                    signals[form] += 1
                    preference = OFF_DAY_PREFERENCES[athlete]
                    group = groups[preference]
                    group["decisions"] += 1
                    group["covered"] += is_covered
                    group["signals"][form] += 1
                    before = streaks[athlete]
                    max_abs_streak = max(max_abs_streak, abs(before))
                    chronology += decision.game_number != game.number or len(history[athlete]) != game_index
                    version += decision.policy_version != LIFE_BRAIN_V4_VERSION
                    expected_action = choose_life_action(
                        athlete,
                        decision.game_number,
                        roster.index(athlete),
                        decision.fatigue_before,
                        decision.recovery_before,
                        policy_version=LIFE_BRAIN_V4_VERSION,
                        routine_streak=before,
                        recent_scoring_form=form,
                    )
                    precedence += decision.selected != expected_action
                    expected = apply_life_action(
                        athlete,
                        decision.game_number,
                        expected_action,
                        decision.fatigue_before,
                        decision.recovery_before,
                        policy_version=LIFE_BRAIN_V4_VERSION,
                        routine_streak=before,
                        recent_scoring_form=form,
                    )
                    policy += decision != expected
                    for signal, reason in PERFORMANCE_REASONS.items():
                        classification += decision.reason == reason and form != signal
                    response_opportunity = (
                        decision.recovery_before == 0
                        and decision.fatigue_before < HIGH_FATIGUE
                        and abs(before) < 2
                        and form != "typical"
                    )
                    response = decision.reason == PERFORMANCE_REASONS.get(form)
                    opportunities += response_opportunity
                    responses += response
                    group["opportunities"] += response_opportunity
                    group["responses"] += response

                    if decision.selected in {"train", "socialize"}:
                        elective_runs[athlete] = (
                            elective_runs[athlete] + 1
                            if last_elective[athlete] == decision.selected
                            else 1
                        )
                        last_elective[athlete] = decision.selected
                    else:
                        elective_runs[athlete] = 0
                        last_elective[athlete] = ""
                    max_elective_run = max(max_elective_run, elective_runs[athlete])
                    next_streak = next_routine_streak(before, decision.selected)
                    transition += not -2 <= next_streak <= 2
                    streaks[athlete] = next_streak

                points: dict[str, int] = {}
                reconstructed = simulate_scheduled_game(
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
                    life_policy_version=LIFE_BRAIN_V4_VERSION,
                    consistency_version=CONSISTENCY_DISABLED_VERSION,
                    offensive_involvement_version=OFFENSIVE_INVOLVEMENT_DISABLED_VERSION,
                    _player_points=points,
                )
                replay += reconstructed != game
                minutes = dict(game.minutes_played)
                history = {
                    name: values + ((points[name], minutes[name]),)
                    for name, values in history.items()
                }

    group_metrics = tuple(
        PerformanceGroupMetrics(
            preference,
            group["decisions"],
            group["covered"],
            round(group["covered"] / group["decisions"], 6),
            tuple(sorted(group["signals"].items())),
            group["opportunities"],
            group["responses"],
            round(group["responses"] / group["opportunities"], 6)
            if group["opportunities"] else 0.0,
        )
        for preference, group in groups.items()
    )
    return PerformanceAudit(
        decisions,
        covered,
        no_appearance,
        insufficient,
        tuple(sorted(signals.items())),
        opportunities,
        responses,
        max_abs_streak,
        max_elective_run,
        policy,
        version,
        tenure,
        chronology,
        classification,
        precedence,
        transition,
        ordering,
        replay,
        group_metrics,
    )


@lru_cache(maxsize=1)
def run_life_performance_evaluation() -> PerformanceEvaluation:
    v3_states = tuple(_league(seed, LIFE_BRAIN_V3_VERSION) for seed in SEED_BLOCKS)
    v4_states = tuple(_league(seed, LIFE_BRAIN_V4_VERSION) for seed in SEED_BLOCKS)
    v3 = _summarize(v3_states, LIFE_BRAIN_V3_VERSION)
    v4 = _summarize(v4_states, LIFE_BRAIN_V4_VERSION)
    performance = _audit(v4_states)
    v3_routine = audit_routine(v3_states)
    blocks = []
    total_actions = total_winners = 0
    weighted_margin = 0.0
    for seed, v3_state, v4_state in zip(SEED_BLOCKS, v3_states, v4_states, strict=True):
        actions, winners, margin = _compare(v3_state, v4_state)
        v3_block = _summarize((v3_state,), LIFE_BRAIN_V3_VERSION)
        v4_block = _summarize((v4_state,), LIFE_BRAIN_V4_VERSION)
        audit = _audit((v4_state,))
        total_actions += actions
        total_winners += winners
        weighted_margin += margin * SEASONS_PER_BLOCK * GAMES_PER_SEASON
        blocks.append(PerformanceBlock(
            seed,
            v3_block.decisions,
            v4_block.decisions,
            audit.covered_decisions,
            audit.responses,
            actions,
            winners,
            margin,
        ))

    v3_groups = {group.preference: group for group in v3.preferences}
    v4_groups = {group.preference: group for group in v4.preferences}

    def difference_in_differences(name: str, scale: float = 1.0) -> float:
        return round((
            getattr(v4_groups["practice"], name) - getattr(v4_groups["social"], name)
            - getattr(v3_groups["practice"], name) + getattr(v3_groups["social"], name)
        ) * scale, 6)

    injury_change = round((v4.injury_rate - v3.injury_rate) * 100, 4)
    missed_change = round((v4.missed_game_rate - v3.missed_game_rate) * 100, 4)
    injury_gap = round(abs(v4_groups["practice"].injury_rate - v4_groups["social"].injury_rate) * 100, 4)
    missed_gap = round(abs(v4_groups["practice"].missed_game_rate - v4_groups["social"].missed_game_rate) * 100, 4)
    fatigue_did = difference_in_differences("mean_pregame_fatigue")
    minutes_did = difference_in_differences("minutes_per_active_game")
    workload_did = difference_in_differences("high_workload_rate", 100)
    injury_did = difference_in_differences("injury_rate", 100)
    missed_did = difference_in_differences("missed_game_rate", 100)
    readiness_did = difference_in_differences("mean_readiness")
    exposure_did = difference_in_differences("readiness_exposure_rate", 100)
    points_shift = round(v4.mean_team_points - v3.mean_team_points, 4)
    win_rate_shift = round((v4.harbor_win_rate - v3.harbor_win_rate) * 100, 4)
    game_count = len(SEED_BLOCKS) * SEASONS_PER_BLOCK * GAMES_PER_SEASON
    winner_rate = round(total_winners / game_count, 6)
    mean_margin = round(weighted_margin / game_count, 4)
    expected_decisions = len(SEED_BLOCKS) * SEASONS_PER_BLOCK * (GAMES_PER_SEASON - 1) * 12
    failures = []
    if v3.decisions != expected_decisions or v4.decisions != expected_decisions:
        failures.append("decision count")
    if any(metric.policy_violations or metric.tenure_violations or metric.version_violations for metric in (v3, v4)):
        failures.append("policy integrity")
    if performance.decisions != expected_decisions or performance.violations:
        failures.append("performance audit")
    if v3_routine.violations or max(performance.max_abs_streak, performance.max_elective_run) > 2:
        failures.append("routine integrity")
    if performance.responses != performance.response_opportunities:
        failures.append("performance response")
    if max(v3.max_readiness, v4.max_readiness) > 0.015:
        failures.append("readiness bound")
    if max(group.max_pregame_fatigue for metric in (v3, v4) for group in metric.preferences) > 0.35:
        failures.append("fatigue bound")
    if min(v3.minimum_available, v4.minimum_available) < 5:
        failures.append("availability floor")
    if v3.zero_minute_absences != v3.missed_player_games or v4.zero_minute_absences != v4.missed_player_games:
        failures.append("absence minutes")
    for failed, name in (
        (injury_change > 0.5, "overall injury rate"),
        (missed_change > 1.0, "overall missed-game rate"),
        (injury_gap > 0.75, "preference injury gap"),
        (missed_gap > 1.0, "preference missed-game gap"),
        (abs(fatigue_did) > 0.03, "fatigue difference-in-differences"),
        (abs(minutes_did) > 2.0, "minutes difference-in-differences"),
        (abs(workload_did) > 5.0, "workload difference-in-differences"),
        (abs(injury_did) > 0.5, "injury difference-in-differences"),
        (abs(missed_did) > 0.5, "missed-game difference-in-differences"),
        (abs(readiness_did) > 0.0025, "readiness difference-in-differences"),
        (abs(exposure_did) > 10.0, "readiness exposure difference-in-differences"),
        (abs(points_shift) > 2.0, "team scoring shift"),
        (abs(win_rate_shift) > 5.0, "team win-rate shift"),
        (winner_rate > 0.25, "winner disagreement rate"),
        (mean_margin > 8.0, "mean absolute margin difference"),
    ):
        if failed:
            failures.append(name)
    if any(block.v3_decisions != 912 or block.v4_decisions != 912 for block in blocks):
        failures.append("per-block decision count")

    result = PerformanceEvaluation(
        LIFE_PERFORMANCE_VERSION,
        LEGACY_STATE_SCHEMA,
        SEED_BLOCKS,
        SEASONS_PER_BLOCK,
        GAMES_PER_SEASON,
        game_count,
        v3,
        v4,
        performance,
        tuple(blocks),
        total_actions,
        total_winners,
        mean_margin,
        injury_change,
        missed_change,
        injury_gap,
        missed_gap,
        fatigue_did,
        minutes_did,
        workload_did,
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
