from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Callable

from phase0a.simulator import (
    Action,
    GameState,
    Team,
    baseline_action,
    legal_actions,
    validate_action,
)


POLICY_VERSION = "llm-contract-v1"
CONTEXT_KEYS = {
    "policy_version",
    "role",
    "clock_seconds",
    "possession_number",
    "decision_number",
    "score",
    "ballhandler",
    "controlled_team",
    "opponent_team",
    "legal_actions",
}


@dataclass(frozen=True)
class Completion:
    raw: str
    provider: str
    model: str
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0


def team_snapshot(team: Team, state: GameState) -> dict[str, object]:
    return {
        "name": team.name,
        "players": [
            {
                "name": player.name,
                "shooting": player.shooting,
                "passing": player.passing,
                "defense": player.defense,
                "rebounding": player.rebounding,
                "stamina": player.stamina,
                "fatigue": round(state.fatigue[player.name], 4),
            }
            for player in team.players
        ],
    }


def build_context(
    role: str,
    state: GameState,
    team: Team,
    opponent: Team,
    ballhandler: str,
) -> dict[str, object]:
    context = {
        "policy_version": POLICY_VERSION,
        "role": role,
        "clock_seconds": state.clock_seconds,
        "possession_number": state.possession_number,
        "decision_number": state.decision_number,
        "score": dict(state.score),
        "ballhandler": ballhandler,
        "controlled_team": team_snapshot(team, state),
        "opponent_team": team_snapshot(opponent, state),
        "legal_actions": [action.as_dict() for action in legal_actions(role, team, ballhandler)],
    }
    assert set(context) == CONTEXT_KEYS
    return context


class LLMPolicy:
    """Guarded provider-neutral LLM policy. The provider owns its network timeout."""

    def __init__(self, complete: Callable[[str], Completion]) -> None:
        self.complete = complete
        self.traces: list[dict[str, object]] = []

    def __call__(
        self,
        role: str,
        state: GameState,
        team: Team,
        opponent: Team,
        ballhandler: str,
        fallback_rng: random.Random,
    ) -> Action:
        context = build_context(role, state, team, opponent, ballhandler)
        request = json.dumps(context, separators=(",", ":"), sort_keys=True)
        request_hash = hashlib.sha256(request.encode()).hexdigest()
        completion: Completion | None = None
        action: Action | None = None
        error_category: str | None = None

        try:
            completion = self.complete(request)
            if not isinstance(completion, Completion):
                raise TypeError("provider must return Completion")
            value = json.loads(completion.raw)
            if not isinstance(value, dict):
                raise ValueError("provider output must be one action object")
            candidate = Action.from_mapping(value)
            validate_action(candidate, team, opponent, ballhandler)
            if candidate.as_dict() not in context["legal_actions"]:
                raise ValueError("provider selected an action outside legal_actions")
            action = candidate
        except TimeoutError:
            error_category = "timeout"
        except json.JSONDecodeError:
            error_category = "malformed_json"
        except (TypeError, ValueError):
            error_category = "invalid_action"
        except Exception:
            error_category = "provider_error"

        fallback = action is None
        if fallback:
            action = baseline_action(role, state, team, ballhandler, fallback_rng)

        self.traces.append(
            {
                "policy_version": POLICY_VERSION,
                "request": context,
                "request_hash": request_hash,
                "provider": completion.provider if completion else None,
                "model": completion.model if completion else None,
                "raw_response": completion.raw if completion else None,
                "parsed_action": action.as_dict(),
                "fallback": fallback,
                "error_category": error_category,
                "latency_ms": completion.latency_ms if completion else 0.0,
                "input_tokens": completion.input_tokens if completion else 0,
                "output_tokens": completion.output_tokens if completion else 0,
                "estimated_cost_usd": completion.estimated_cost_usd if completion else 0.0,
            }
        )
        return action


def offline_fixture_completion(request: str) -> Completion:
    """Deterministic plumbing fixture, not an LLM or a claim of intelligence."""

    context = json.loads(request)
    legal = context["legal_actions"]
    players = {player["name"]: player for player in context["controlled_team"]["players"]}
    digest = int(hashlib.sha256(request.encode()).hexdigest(), 16)

    if context["role"] == "defense":
        weights = [players[action["actor"]]["defense"] for action in legal]
    else:
        handler = players[context["ballhandler"]]
        trailing = context["score"][context["controlled_team"]["name"]] < context["score"][context["opponent_team"]["name"]]
        weights_by_kind = {
            "pass": max(10, handler["passing"] - 45),
            "drive": 24,
            "shoot_2": max(10, handler["shooting"] - 45),
            "shoot_3": max(8, handler["shooting"] - (48 if trailing and context["clock_seconds"] < 120 else 58)),
        }
        weights = [weights_by_kind[action["kind"]] for action in legal]

    roll = digest % sum(weights)
    selected = legal[-1]
    for action, weight in zip(legal, weights):
        if roll < weight:
            selected = action
            break
        roll -= weight
    return Completion(json.dumps(selected), "offline-fixture", "deterministic-rules-v1")
