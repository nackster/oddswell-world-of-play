from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from phase0a.simulator import MAX_READINESS_MODIFIER, Team, clamp


LIFE_BRAIN_VERSION = "athlete-life-v1"
LIFE_CHOICES = ("train", "rest", "recover", "socialize")
HIGH_FATIGUE = 0.24


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
) -> str:
    if athlete == "" or game_number < 2 or roster_index < 0:
        raise ValueError("athlete, between-game number, and roster index are required")
    if recovery_days > 0:
        return "recover"
    if fatigue >= HIGH_FATIGUE:
        return "rest"
    return "train" if (game_number + roster_index) % 2 == 0 else "socialize"


def apply_life_action(
    athlete: str,
    game_number: int,
    action: str,
    fatigue: float,
    recovery_days: int,
) -> LifeDecision:
    if action not in LIFE_CHOICES:
        raise ValueError(f"illegal Athlete Life Brain choice: {action!r}")
    if not 0 <= fatigue <= 0.45 or not 0 <= recovery_days <= 7:
        raise ValueError("invalid temporary athlete state")

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
        reason = "Deterministic practice rotation"
        effect = "Practice +1.5%, fatigue +0.02; consumed next game"
    else:
        after_fatigue = min(0.35, fatigue + 0.01)
        readiness = 0.01
        reason = "Deterministic social rotation"
        effect = "Morale +1.0%, fatigue +0.01; consumed next game"

    return LifeDecision(
        athlete,
        game_number,
        LIFE_CHOICES,
        action,
        LIFE_BRAIN_VERSION,
        reason,
        round(fatigue, 4),
        round(after_fatigue, 4),
        recovery_days,
        after_recovery,
        round(clamp(readiness, -MAX_READINESS_MODIFIER, MAX_READINESS_MODIFIER), 4),
        effect,
    )


def between_game_choices(
    game_number: int,
    fatigue: Mapping[str, float],
    availability: Mapping[str, int],
    teams: tuple[Team, Team],
) -> tuple[LifeDecision, ...]:
    roster = tuple(player.name for team in teams for player in team.players)
    if set(fatigue) != set(roster) or set(availability) != set(roster):
        raise ValueError("life choices require the exact active roster")
    decisions = []
    for index, athlete in enumerate(roster):
        action = choose_life_action(
            athlete,
            game_number,
            index,
            float(fatigue[athlete]),
            int(availability[athlete]),
        )
        decisions.append(
            apply_life_action(
                athlete,
                game_number,
                action,
                float(fatigue[athlete]),
                int(availability[athlete]),
            )
        )
    return tuple(decisions)
