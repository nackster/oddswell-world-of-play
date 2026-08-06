from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

from phase0a.simulator import Action, GameState, Team, default_teams
from phase0c.policy import Completion, LLMPolicy, build_context


@dataclass(frozen=True)
class Scenario:
    name: str
    role: str
    clock_seconds: int
    home_score: int
    away_score: int
    ballhandler: str
    tired_player: str | None
    action: Action
    request_hash: str


SCENARIOS = (
    Scenario(
        "opening_star_attack",
        "offense",
        2_880,
        0,
        0,
        "Jalen Cross",
        None,
        Action("offense", "drive", "Jalen Cross", None),
        "c11fd9fbc9f71380abb1483454bd5ace944af3c6457e625397b0d949e7593fa1",
    ),
    Scenario(
        "elite_passer_creates",
        "offense",
        1_800,
        40,
        40,
        "Micah Vale",
        None,
        Action("offense", "pass", "Micah Vale", "Jalen Cross"),
        "c5fa40fc9f6d32c34bb5400b082c0aea967937d76fa1d8c825d23b03eb6031a4",
    ),
    Scenario(
        "late_trailing_three",
        "offense",
        45,
        92,
        97,
        "Jalen Cross",
        None,
        Action("offense", "shoot_3", "Jalen Cross", None),
        "dcd877a277e1e066d669b3dcf051013fd49e31bdfda71386ab2201fcf051e630",
    ),
    Scenario(
        "late_lead_low_risk",
        "offense",
        45,
        98,
        94,
        "Micah Vale",
        None,
        Action("offense", "drive", "Micah Vale", None),
        "8c37febd4f2a6b64cef4246f27659450542bb49d691b8d3806e9aa8eb04383ba",
    ),
    Scenario(
        "fatigued_scorer_moves_ball",
        "offense",
        600,
        80,
        80,
        "Jalen Cross",
        "Jalen Cross",
        Action("offense", "pass", "Jalen Cross", "Dorian Pike"),
        "18eaaf2598960762a71fb07680cc9e1f4aaaffd251702dce7898223bf4d53cb5",
    ),
    Scenario(
        "late_defensive_stop",
        "defense",
        20,
        99,
        98,
        "Jalen Cross",
        None,
        Action("defense", "defend", "Tariq Stone", "Jalen Cross"),
        "8915507d5bf3cf7abb8d0d10b46611fd216b47d0304d1879012c2a44ea3b07e5",
    ),
)


@dataclass(frozen=True)
class ScenarioResult:
    scenario_count: int
    legal_count: int
    hash_verified_count: int
    fallback_count: int
    choices: tuple[tuple[str, str], ...]


def scenario_inputs(scenario: Scenario) -> tuple[GameState, Team, Team]:
    full_home, full_away = default_teams()
    # Preserve the exact five-player requests that the recorded responses were authored against.
    home = Team(full_home.name, full_home.players[:5])
    away = Team(full_away.name, full_away.players[:5])
    state = GameState(
        home,
        away,
        clock_seconds=scenario.clock_seconds,
        possession_number=1,
        decision_number=1,
        possession=home.name,
    )
    state.score = {home.name: scenario.home_score, away.name: scenario.away_score}
    state.fatigue = {player.name: 0.0 for team in (home, away) for player in team.players}
    if scenario.tired_player:
        state.fatigue[scenario.tired_player] = 0.44
    controlled, opponent = (home, away) if scenario.role == "offense" else (away, home)
    return state, controlled, opponent


def canonical_request(scenario: Scenario) -> str:
    state, controlled, opponent = scenario_inputs(scenario)
    context = build_context(scenario.role, state, controlled, opponent, scenario.ballhandler)
    return json.dumps(context, separators=(",", ":"), sort_keys=True)


class RecordedScenarioCompletion:
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario

    def __call__(self, request: str) -> Completion:
        observed_hash = hashlib.sha256(request.encode()).hexdigest()
        if observed_hash != self.scenario.request_hash:
            raise ValueError("recorded LLM response does not match this request")
        return Completion(
            json.dumps(self.scenario.action.as_dict()),
            provider="codex-thread",
            model="gpt-5",
        )


def run_recorded_scenarios() -> ScenarioResult:
    legal_count = 0
    hash_verified_count = 0
    fallback_count = 0
    choices = []
    for scenario in SCENARIOS:
        state, controlled, opponent = scenario_inputs(scenario)
        policy = LLMPolicy(RecordedScenarioCompletion(scenario))
        action = policy(
            scenario.role,
            state,
            controlled,
            opponent,
            scenario.ballhandler,
            random.Random(0),
        )
        trace = policy.traces[-1]
        legal_count += action == scenario.action
        hash_verified_count += trace["request_hash"] == scenario.request_hash
        fallback_count += bool(trace["fallback"])
        choices.append((scenario.name, action.kind))
    return ScenarioResult(len(SCENARIOS), legal_count, hash_verified_count, fallback_count, tuple(choices))
