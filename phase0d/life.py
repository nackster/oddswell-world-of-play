from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from phase0a.simulator import MAX_READINESS_MODIFIER, Team, clamp


LIFE_BRAIN_V1_VERSION = "athlete-life-v1"
LIFE_BRAIN_V2_VERSION = "athlete-life-v2"
LIFE_BRAIN_V3_VERSION = "athlete-life-v3"
DEFAULT_LIFE_BRAIN_VERSION = LIFE_BRAIN_V2_VERSION
LIFE_CHOICES = ("train", "rest", "recover", "socialize")
HIGH_FATIGUE = 0.24
OFF_DAY_PREFERENCES = {
    "Jalen Cross": "practice",
    "Micah Vale": "social",
    "Dorian Pike": "practice",
    "Kellan Shore": "social",
    "Andre North": "social",
    "Malik Frost": "practice",
    "Nico Reyes": "practice",
    "Tariq Stone": "social",
    "Eli Mercer": "practice",
    "Roman Voss": "social",
    "Cal Brooks": "practice",
    "Mateo Cruz": "social",
    "Soren Lake": "social",
}


@dataclass(frozen=True)
class LifeDecision:
    athlete: str
    game_number: int
    legal_choices: tuple[str, ...]
    selected: str
    policy_version: str
    reason: str
    fatigue_before: float
    fatigue_after: float
    recovery_before: int
    recovery_after: int
    readiness: float
    temporary_effect: str


def choose_life_action(
    athlete: str,
    game_number: int,
    roster_index: int,
    fatigue: float,
    recovery_days: int,
    *,
    policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
    routine_streak: int = 0,
) -> str:
    if athlete == "" or game_number < 2 or roster_index < 0:
        raise ValueError("athlete, between-game number, and roster index are required")
    if policy_version not in {
        LIFE_BRAIN_V1_VERSION, LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION
    }:
        raise ValueError(f"unsupported Athlete Life Brain policy: {policy_version!r}")
    if (
        not isinstance(routine_streak, int)
        or isinstance(routine_streak, bool)
        or not -2 <= routine_streak <= 2
        or (policy_version != LIFE_BRAIN_V3_VERSION and routine_streak)
    ):
        raise ValueError("routine streak must be an integer from -2 to 2 and v3-only")
    if policy_version in {LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION} and athlete not in OFF_DAY_PREFERENCES:
        raise ValueError(f"missing off-day preference for {athlete!r}")
    if recovery_days > 0:
        return "recover"
    if fatigue >= HIGH_FATIGUE:
        return "rest"
    if policy_version == LIFE_BRAIN_V3_VERSION and routine_streak == 2:
        return "socialize"
    if policy_version == LIFE_BRAIN_V3_VERSION and routine_streak == -2:
        return "train"
    if policy_version in {LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION}:
        return "train" if OFF_DAY_PREFERENCES[athlete] == "practice" else "socialize"
    return "train" if (game_number + roster_index) % 2 == 0 else "socialize"


def apply_life_action(
    athlete: str,
    game_number: int,
    action: str,
    fatigue: float,
    recovery_days: int,
    *,
    policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
    routine_streak: int = 0,
) -> LifeDecision:
    if action not in LIFE_CHOICES:
        raise ValueError(f"illegal Athlete Life Brain choice: {action!r}")
    if not 0 <= fatigue <= 0.45 or not 0 <= recovery_days <= 7:
        raise ValueError("invalid temporary athlete state")
    if policy_version not in {
        LIFE_BRAIN_V1_VERSION, LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION
    }:
        raise ValueError(f"unsupported Athlete Life Brain policy: {policy_version!r}")
    if (
        not isinstance(routine_streak, int)
        or isinstance(routine_streak, bool)
        or not -2 <= routine_streak <= 2
        or (policy_version != LIFE_BRAIN_V3_VERSION and routine_streak)
    ):
        raise ValueError("routine streak must be an integer from -2 to 2 and v3-only")
    if policy_version in {LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION} and athlete not in OFF_DAY_PREFERENCES:
        raise ValueError(f"missing off-day preference for {athlete!r}")

    after_fatigue = fatigue
    after_recovery = recovery_days
    readiness = 0.0
    if action == "recover":
        if recovery_days == 0:
            raise ValueError("recover requires an unavailable athlete")
        after_recovery -= 1
        reason = "Unavailable: one focused recovery day"
        effect = "Recovery shortened by one day"
    elif action == "rest":
        after_fatigue = max(0.0, fatigue - 0.03)
        reason = "High carryover fatigue"
        effect = "Fatigue -0.03 for the next game"
    elif action == "train":
        after_fatigue = min(0.35, fatigue + 0.02)
        readiness = 0.015
        reason = (
            "Routine variation after two socialize choices"
            if policy_version == LIFE_BRAIN_V3_VERSION and routine_streak == -2
            else f"{OFF_DAY_PREFERENCES[athlete].title()} off-day preference"
            if policy_version in {LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION}
            else "Deterministic practice rotation"
        )
        effect = "Practice +1.5%, fatigue +0.02; consumed next game"
    else:
        after_fatigue = min(0.35, fatigue + 0.01)
        readiness = 0.01
        reason = (
            "Routine variation after two train choices"
            if policy_version == LIFE_BRAIN_V3_VERSION and routine_streak == 2
            else f"{OFF_DAY_PREFERENCES[athlete].title()} off-day preference"
            if policy_version in {LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION}
            else "Deterministic social rotation"
        )
        effect = "Morale +1.0%, fatigue +0.01; consumed next game"

    return LifeDecision(
        athlete,
        game_number,
        LIFE_CHOICES,
        action,
        policy_version,
        reason,
        round(fatigue, 4),
        round(after_fatigue, 4),
        recovery_days,
        after_recovery,
        round(clamp(readiness, -MAX_READINESS_MODIFIER, MAX_READINESS_MODIFIER), 4),
        effect,
    )


def next_routine_streak(streak: int, action: str) -> int:
    if (
        not isinstance(streak, int)
        or isinstance(streak, bool)
        or not -2 <= streak <= 2
    ):
        raise ValueError("routine streak must be an integer from -2 to 2")
    if action not in LIFE_CHOICES:
        raise ValueError(f"illegal Athlete Life Brain choice: {action!r}")
    if action == "train":
        return min(2, streak + 1) if streak > 0 else 1
    if action == "socialize":
        return max(-2, streak - 1) if streak < 0 else -1
    return 0


def between_game_choices(
    game_number: int,
    fatigue: Mapping[str, float],
    availability: Mapping[str, int],
    teams: tuple[Team, Team],
    *,
    policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
    routine_streaks: Mapping[str, int] | None = None,
) -> tuple[LifeDecision, ...]:
    roster = tuple(player.name for team in teams for player in team.players)
    if set(fatigue) != set(roster) or set(availability) != set(roster):
        raise ValueError("life choices require the exact active roster")
    if policy_version == LIFE_BRAIN_V3_VERSION:
        if routine_streaks is None or set(routine_streaks) != set(roster):
            raise ValueError("v3 routine streaks require the exact active roster")
    elif routine_streaks is not None:
        raise ValueError("routine streaks are v3-only")
    decisions = []
    for index, athlete in enumerate(roster):
        action = choose_life_action(
            athlete,
            game_number,
            index,
            float(fatigue[athlete]),
            int(availability[athlete]),
            policy_version=policy_version,
            routine_streak=0 if routine_streaks is None else routine_streaks[athlete],
        )
        decisions.append(
            apply_life_action(
                athlete,
                game_number,
                action,
                float(fatigue[athlete]),
                int(availability[athlete]),
                policy_version=policy_version,
                routine_streak=0 if routine_streaks is None else routine_streaks[athlete],
            )
        )
    return tuple(decisions)
