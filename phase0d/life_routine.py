from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
import hashlib
import json

from phase0d.career import teams_for_season
from phase0d.league import LEGACY_STATE_SCHEMA, LeagueState
from phase0d.life import (
    HIGH_FATIGUE,
    LIFE_BRAIN_V2_VERSION,
    LIFE_BRAIN_V3_VERSION,
    OFF_DAY_PREFERENCES,
    apply_life_action,
    next_routine_streak,
)
from phase0d.life_multiseed import (
    GAMES_PER_SEASON,
    SEASONS_PER_BLOCK,
    PolicyMetrics,
    _compare,
    _league,
    _summarize,
)


LIFE_ROUTINE_VERSION = "life-routine-v1"
SEED_BLOCKS = tuple(40_000 + 80 * index for index in range(10))


@dataclass(frozen=True)
class RoutineGroupMetrics:
    preference: str
    eligible_decisions: int
    variations: int
    variation_rate: float


@dataclass(frozen=True)
class RoutineAudit:
    decisions: int
    eligible_decisions: int
    variations: int
    max_abs_streak: int
    max_elective_run: int
    violations: int
    groups: tuple[RoutineGroupMetrics, ...]


@dataclass(frozen=True)
class RoutineBlock:
    start_seed: int
    v2_decisions: int
    v3_decisions: int
    v3_variations: int
    action_divergence: int
    winner_disagreements: int
    mean_absolute_margin_difference: float


@dataclass(frozen=True)
class RoutineEvaluation:
    version: str
    state_schema: str
    seed_blocks: tuple[int, ...]
    seasons_per_block: int
    games_per_season: int
    games_per_policy: int
    v2: PolicyMetrics
    v3: PolicyMetrics
    routine: RoutineAudit
    blocks: tuple[RoutineBlock, ...]
    action_divergence: int
    winner_disagreements: int
    mean_absolute_margin_difference: float
    injury_rate_change_points: float
    missed_game_rate_change_points: float
    v3_preference_injury_gap_points: float
    v3_preference_missed_gap_points: float
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


def _audit(states: tuple[LeagueState, ...]) -> RoutineAudit:
    groups = {
        preference: Counter(eligible=0, variations=0)
        for preference in ("practice", "social")
    }
    decisions = eligible = variations = violations = 0
    max_abs_streak = max_elective_run = 0

    for state in states:
        for season in state.seasons:
            teams = teams_for_season(season.season_number)
            roster = tuple(player.name for team in teams for player in team.players)
            roster_index = {name: index for index, name in enumerate(roster)}
            streaks = {name: 0 for name in roster}
            last_elective = {name: "" for name in roster}
            elective_runs = {name: 0 for name in roster}
            for game_index, game in enumerate(season.games):
                expected_order = () if game_index == 0 else roster
                violations += tuple(
                    decision.athlete for decision in game.life_decisions
                ) != expected_order
                for decision in game.life_decisions:
                    decisions += 1
                    if decision.athlete not in roster_index:
                        violations += 1
                        continue
                    athlete = decision.athlete
                    before = streaks[athlete]
                    max_abs_streak = max(max_abs_streak, abs(before))
                    is_eligible = (
                        decision.recovery_before == 0
                        and decision.fatigue_before < HIGH_FATIGUE
                    )
                    is_variation = is_eligible and abs(before) == 2
                    preference = OFF_DAY_PREFERENCES[athlete]
                    groups[preference]["eligible"] += is_eligible
                    groups[preference]["variations"] += is_variation
                    eligible += is_eligible
                    variations += is_variation
                    try:
                        expected = apply_life_action(
                            athlete,
                            decision.game_number,
                            decision.selected,
                            decision.fatigue_before,
                            decision.recovery_before,
                            policy_version=LIFE_BRAIN_V3_VERSION,
                            routine_streak=before,
                        )
                    except ValueError:
                        violations += 1
                    else:
                        violations += decision != expected
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
                    streaks[athlete] = next_routine_streak(before, decision.selected)

    group_metrics = tuple(
        RoutineGroupMetrics(
            preference,
            group["eligible"],
            group["variations"],
            round(group["variations"] / group["eligible"], 6),
        )
        for preference, group in groups.items()
    )
    return RoutineAudit(
        decisions,
        eligible,
        variations,
        max_abs_streak,
        max_elective_run,
        violations,
        group_metrics,
    )


@lru_cache(maxsize=1)
def run_life_routine_evaluation() -> RoutineEvaluation:
    v2_states = tuple(_league(seed, LIFE_BRAIN_V2_VERSION) for seed in SEED_BLOCKS)
    v3_states = tuple(_league(seed, LIFE_BRAIN_V3_VERSION) for seed in SEED_BLOCKS)
    v2 = _summarize(v2_states, LIFE_BRAIN_V2_VERSION)
    v3 = _summarize(v3_states, LIFE_BRAIN_V3_VERSION)
    routine = _audit(v3_states)
    blocks = []
    total_actions = total_winners = 0
    weighted_margin = 0.0
    for seed, v2_state, v3_state in zip(SEED_BLOCKS, v2_states, v3_states, strict=True):
        actions, winners, margin = _compare(v2_state, v3_state)
        v2_block = _summarize((v2_state,), LIFE_BRAIN_V2_VERSION)
        v3_block = _summarize((v3_state,), LIFE_BRAIN_V3_VERSION)
        routine_block = _audit((v3_state,))
        total_actions += actions
        total_winners += winners
        weighted_margin += margin * SEASONS_PER_BLOCK * GAMES_PER_SEASON
        blocks.append(RoutineBlock(
            seed,
            v2_block.decisions,
            v3_block.decisions,
            routine_block.variations,
            actions,
            winners,
            margin,
        ))

    v2_groups = {group.preference: group for group in v2.preferences}
    v3_groups = {group.preference: group for group in v3.preferences}
    routine_groups = {group.preference: group for group in routine.groups}

    def difference_in_differences(name: str, scale: float = 1.0) -> float:
        return round((
            getattr(v3_groups["practice"], name) - getattr(v3_groups["social"], name)
            - getattr(v2_groups["practice"], name) + getattr(v2_groups["social"], name)
        ) * scale, 6)

    injury_change = round((v3.injury_rate - v2.injury_rate) * 100, 4)
    missed_change = round((v3.missed_game_rate - v2.missed_game_rate) * 100, 4)
    injury_gap = round(abs(
        v3_groups["practice"].injury_rate - v3_groups["social"].injury_rate
    ) * 100, 4)
    missed_gap = round(abs(
        v3_groups["practice"].missed_game_rate - v3_groups["social"].missed_game_rate
    ) * 100, 4)
    fatigue_did = difference_in_differences("mean_pregame_fatigue")
    minutes_did = difference_in_differences("minutes_per_active_game")
    high_workload_did = difference_in_differences("high_workload_rate", 100)
    injury_did = difference_in_differences("injury_rate", 100)
    missed_did = difference_in_differences("missed_game_rate", 100)
    readiness_did = difference_in_differences("mean_readiness")
    exposure_did = difference_in_differences("readiness_exposure_rate", 100)
    points_shift = round(v3.mean_team_points - v2.mean_team_points, 4)
    win_rate_shift = round((v3.harbor_win_rate - v2.harbor_win_rate) * 100, 4)
    game_count = len(SEED_BLOCKS) * SEASONS_PER_BLOCK * GAMES_PER_SEASON
    winner_rate = round(total_winners / game_count, 6)
    mean_margin = round(weighted_margin / game_count, 4)
    expected_decisions = len(SEED_BLOCKS) * SEASONS_PER_BLOCK * (GAMES_PER_SEASON - 1) * 12
    variation_gap = abs(
        routine_groups["practice"].variation_rate
        - routine_groups["social"].variation_rate
    ) * 100
    failures = []
    if v2.decisions != expected_decisions or v3.decisions != expected_decisions:
        failures.append("decision count")
    if any(metric.policy_violations or metric.tenure_violations or metric.version_violations for metric in (v2, v3)):
        failures.append("policy integrity")
    if routine.decisions != expected_decisions or routine.violations:
        failures.append("routine audit")
    if routine.max_abs_streak > 2 or routine.max_elective_run > 2:
        failures.append("routine bound")
    if variation_gap > 5.0:
        failures.append("routine trigger gap")
    if max(v2.max_readiness, v3.max_readiness) > 0.015:
        failures.append("readiness bound")
    if max(group.max_pregame_fatigue for metric in (v2, v3) for group in metric.preferences) > 0.35:
        failures.append("fatigue bound")
    if min(v2.minimum_available, v3.minimum_available) < 5:
        failures.append("availability floor")
    if v2.zero_minute_absences != v2.missed_player_games or v3.zero_minute_absences != v3.missed_player_games:
        failures.append("absence minutes")
    for failed, name in (
        (injury_change > 0.5, "overall injury rate"),
        (missed_change > 1.0, "overall missed-game rate"),
        (injury_gap > 0.75, "preference injury gap"),
        (missed_gap > 1.0, "preference missed-game gap"),
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
        (mean_margin > 8.0, "mean absolute margin difference"),
    ):
        if failed:
            failures.append(name)
    if any(block.v2_decisions != 912 or block.v3_decisions != 912 for block in blocks):
        failures.append("per-block decision count")

    result = RoutineEvaluation(
        LIFE_ROUTINE_VERSION,
        LEGACY_STATE_SCHEMA,
        SEED_BLOCKS,
        SEASONS_PER_BLOCK,
        GAMES_PER_SEASON,
        game_count,
        v2,
        v3,
        routine,
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
