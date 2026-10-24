from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping


ENGINE_VERSION = "phase05h-v1"
BRAIN_VERSION = "baseline-v2"
REGULATION_SECONDS = 48 * 60
ROTATION_SEGMENT_SECONDS = REGULATION_SECONDS // 10
POSSESSION_SECONDS = 14
MAX_GAME_FATIGUE = 0.45
MAX_RECOVERY_DAYS = 7
MAX_READINESS_MODIFIER = 0.02
MAX_GAME_FORM_MODIFIER = 0.015
MIN_OFFENSIVE_INVOLVEMENT = 0.85
MAX_OFFENSIVE_INVOLVEMENT = 1.15
ACTION_KEYS = {"role", "kind", "actor", "target"}
OFFENSE_ACTIONS = {"pass", "drive", "shoot_2", "shoot_3"}


@dataclass(frozen=True)
class Player:
    name: str
    shooting: int
    passing: int
    defense: int
    rebounding: int
    stamina: int


@dataclass(frozen=True)
class Team:
    name: str
    players: tuple[Player, ...]

    def player(self, name: str) -> Player:
        try:
            return next(player for player in self.players if player.name == name)
        except StopIteration as error:
            raise ValueError(f"{name!r} is not on {self.name}") from error


@dataclass(frozen=True)
class Action:
    role: str
    kind: str
    actor: str
    target: str | None

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> Action:
        if set(value) != ACTION_KEYS:
            raise ValueError(f"action must contain exactly {sorted(ACTION_KEYS)}")
        if not all(isinstance(value[key], str) for key in ("role", "kind", "actor")):
            raise ValueError("role, kind, and actor must be strings")
        if value["target"] is not None and not isinstance(value["target"], str):
            raise ValueError("target must be a string or null")
        return cls(value["role"], value["kind"], value["actor"], value["target"])

    def as_dict(self) -> dict[str, object]:
        return {
            "role": self.role,
            "kind": self.kind,
            "actor": self.actor,
            "target": self.target,
        }


@dataclass
class GameState:
    home: Team
    away: Team
    clock_seconds: int = REGULATION_SECONDS
    possession_number: int = 0
    decision_number: int = 0
    possession: str = ""
    score: dict[str, int] = field(default_factory=dict)
    fatigue: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class GameResult:
    seed: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    action_tape: tuple[dict[str, object], ...]
    records: tuple[dict[str, object], ...]
    minutes_played: tuple[tuple[str, float], ...]
    final_fatigue: tuple[tuple[str, float], ...]

    def jsonl(self) -> str:
        return "\n".join(json.dumps(record, sort_keys=True) for record in self.records) + "\n"


def default_teams() -> tuple[Team, Team]:
    return (
        Team(
            "Harbor City Waves",
            (
                Player("Jalen Cross", 84, 78, 72, 58, 86),
                Player("Micah Vale", 76, 86, 75, 55, 88),
                Player("Dorian Pike", 79, 71, 82, 70, 84),
                Player("Kellan Shore", 72, 69, 78, 84, 80),
                Player("Andre North", 68, 65, 80, 88, 78),
                Player("Malik Frost", 74, 72, 74, 63, 82),
            ),
        ),
        Team(
            "Mesa Vista Sol",
            (
                Player("Nico Reyes", 82, 80, 70, 56, 87),
                Player("Tariq Stone", 78, 75, 83, 68, 85),
                Player("Eli Mercer", 75, 84, 74, 60, 89),
                Player("Roman Voss", 73, 67, 79, 86, 81),
                Player("Cal Brooks", 70, 64, 81, 89, 77),
                Player("Mateo Cruz", 74, 73, 73, 65, 83),
            ),
        ),
    )


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def other_team(state: GameState, team: Team) -> Team:
    return state.away if team.name == state.home.name else state.home


def rotation_lineup(
    team: Team,
    clock_seconds: int,
    overtime: int = 0,
    unavailable: frozenset[str] = frozenset(),
) -> Team:
    available = tuple(player for player in team.players if player.name not in unavailable)
    if len(available) < 5:
        raise ValueError(f"{team.name} needs at least five players")
    starters = available[:5]
    if len(available) == 5 or overtime:
        return Team(team.name, starters)
    # ponytail: one reserve is the D.2 ceiling; add coach-selected depth only when rotations expand.
    segment = min(9, (REGULATION_SECONDS - clock_seconds) // ROTATION_SEGMENT_SECONDS)
    if segment % 2 == 0:
        return Team(team.name, starters)
    resting_starter = segment // 2
    return Team(
        team.name,
        tuple(player for index, player in enumerate(starters) if index != resting_starter)
        + (available[5],),
    )


def validate_action(action: Action, team: Team, opponent: Team, ballhandler: str) -> None:
    team.player(action.actor)
    if action.role == "offense":
        if action.kind not in OFFENSE_ACTIONS:
            raise ValueError(f"illegal offense action: {action.kind}")
        if action.actor != ballhandler:
            raise ValueError("only the ballhandler can take an offense action")
        if action.kind == "pass":
            if action.target is None or action.target == action.actor:
                raise ValueError("a pass needs a different teammate target")
            team.player(action.target)
        elif action.target is not None:
            raise ValueError(f"{action.kind} cannot have a target")
        return

    if action.role != "defense" or action.kind != "defend":
        raise ValueError("defense actions must use role=defense and kind=defend")
    opponent.player(action.target or "")
    if action.target != ballhandler:
        raise ValueError("a defender must target the current ballhandler")


def legal_actions(role: str, team: Team, ballhandler: str) -> tuple[Action, ...]:
    if role == "defense":
        return tuple(Action("defense", "defend", player.name, ballhandler) for player in team.players)
    return (
        *(Action("offense", "pass", ballhandler, player.name) for player in team.players if player.name != ballhandler),
        Action("offense", "drive", ballhandler, None),
        Action("offense", "shoot_2", ballhandler, None),
        Action("offense", "shoot_3", ballhandler, None),
    )


def baseline_action(
    role: str,
    state: GameState,
    team: Team,
    ballhandler: str,
    rng: random.Random,
    offensive_involvement: Mapping[str, float] | None = None,
) -> Action:
    if role == "defense":
        defender = rng.choices(team.players, weights=[player.defense for player in team.players], k=1)[0]
        return Action("defense", "defend", defender.name, ballhandler)

    player = team.player(ballhandler)
    trailing = state.score[team.name] < state.score[other_team(state, team).name]
    kinds = ("pass", "drive", "shoot_2", "shoot_3")
    weights = (
        max(10, player.passing - 45),
        24,
        max(10, player.shooting - 45),
        max(8, player.shooting - (52 if trailing else 58)),
    )
    kind = rng.choices(kinds, weights=weights, k=1)[0]
    if kind == "pass":
        targets = tuple(teammate for teammate in team.players if teammate != player)
        weights = [teammate.shooting for teammate in targets]
        if offensive_involvement is not None:
            weights = [
                teammate.shooting * offensive_involvement[teammate.name]
                for teammate in targets
            ]
        target = rng.choices(targets, weights=weights, k=1)[0]
        return Action("offense", kind, player.name, target.name)
    return Action("offense", kind, player.name, None)


def simulate_game(
    seed: int,
    action_tape: Iterable[Mapping[str, object]] | None = None,
    brain_version: str = BRAIN_VERSION,
    matchup: tuple[Team, Team] | None = None,
    decision_policy: Callable[[str, GameState, Team, Team, str, random.Random], Action] | None = None,
    initial_fatigue: Mapping[str, float] | None = None,
    initial_availability: Mapping[str, int] | None = None,
    initial_readiness: Mapping[str, float] | None = None,
    initial_game_form: Mapping[str, float] | None = None,
    initial_shooting_consistency: Mapping[str, tuple[float, float]] | None = None,
    initial_offensive_involvement: Mapping[str, float] | None = None,
) -> GameResult:
    home, away = matchup or default_teams()
    state = GameState(home=home, away=away, possession=home.name)
    state.score = {home.name: 0, away.name: 0}
    player_names = tuple(player.name for team in (home, away) for player in team.players)
    if initial_fatigue is None:
        state.fatigue = {name: 0.0 for name in player_names}
    else:
        if set(initial_fatigue) != set(player_names):
            raise ValueError("initial_fatigue must contain every matchup player exactly once")
        if any(
            not isinstance(initial_fatigue[name], (int, float))
            or isinstance(initial_fatigue[name], bool)
            or not 0 <= initial_fatigue[name] <= MAX_GAME_FATIGUE
            for name in player_names
        ):
            raise ValueError(f"initial fatigue must be between 0 and {MAX_GAME_FATIGUE}")
        state.fatigue = {name: float(initial_fatigue[name]) for name in player_names}

    if initial_availability is None:
        availability = {name: 0 for name in player_names}
    else:
        if set(initial_availability) != set(player_names):
            raise ValueError("initial_availability must contain every matchup player exactly once")
        if any(
            not isinstance(initial_availability[name], int)
            or isinstance(initial_availability[name], bool)
            or not 0 <= initial_availability[name] <= MAX_RECOVERY_DAYS
            for name in player_names
        ):
            raise ValueError(f"recovery days must be integers between 0 and {MAX_RECOVERY_DAYS}")
        availability = dict(initial_availability)
    unavailable = frozenset(name for name, recovery_days in availability.items() if recovery_days)
    for team in (home, away):
        if sum(player.name not in unavailable for player in team.players) < 5:
            raise ValueError(f"{team.name} needs at least five available players")

    if initial_readiness is None:
        readiness = {name: 0.0 for name in player_names}
    else:
        if set(initial_readiness) != set(player_names):
            raise ValueError("initial_readiness must contain every matchup player exactly once")
        if any(
            not isinstance(initial_readiness[name], (int, float))
            or isinstance(initial_readiness[name], bool)
            or not -MAX_READINESS_MODIFIER <= initial_readiness[name] <= MAX_READINESS_MODIFIER
            for name in player_names
        ):
            raise ValueError(
                f"readiness must be between {-MAX_READINESS_MODIFIER} and {MAX_READINESS_MODIFIER}"
            )
        readiness = {name: float(initial_readiness[name]) for name in player_names}

    if initial_game_form is None:
        game_form = {name: 0.0 for name in player_names}
    else:
        if set(initial_game_form) != set(player_names):
            raise ValueError("initial_game_form must contain every matchup player exactly once")
        if any(
            not isinstance(initial_game_form[name], (int, float))
            or isinstance(initial_game_form[name], bool)
            or not -MAX_GAME_FORM_MODIFIER
            <= initial_game_form[name]
            <= MAX_GAME_FORM_MODIFIER
            for name in player_names
        ):
            raise ValueError(
                f"game form must be between {-MAX_GAME_FORM_MODIFIER} and "
                f"{MAX_GAME_FORM_MODIFIER}"
            )
        game_form = {name: float(initial_game_form[name]) for name in player_names}

    if initial_game_form is not None and initial_shooting_consistency is not None:
        raise ValueError("game form and shooting consistency cannot run together")
    if initial_shooting_consistency is None:
        shooting_consistency = {name: (0.0, 0.0) for name in player_names}
    else:
        if set(initial_shooting_consistency) != set(player_names):
            raise ValueError(
                "initial_shooting_consistency must contain every matchup player exactly once"
            )
        if any(
            not isinstance(initial_shooting_consistency[name], tuple)
            or len(initial_shooting_consistency[name]) != 2
            or any(
                not isinstance(value, (int, float)) or isinstance(value, bool)
                for value in initial_shooting_consistency[name]
            )
            or not 0 <= initial_shooting_consistency[name][0] <= 0.5
            or not 0 <= initial_shooting_consistency[name][1] <= 0.1
            for name in player_names
        ):
            raise ValueError(
                "shooting consistency must be (strength, cap) within 0..0.5 and 0..0.1"
            )
        shooting_consistency = {
            name: tuple(float(value) for value in initial_shooting_consistency[name])
            for name in player_names
        }

    if initial_offensive_involvement is None:
        offensive_involvement = {name: 1.0 for name in player_names}
    else:
        if decision_policy is not None:
            raise ValueError("offensive involvement pilot requires the baseline decision policy")
        if set(initial_offensive_involvement) != set(player_names):
            raise ValueError(
                "initial_offensive_involvement must contain every matchup player exactly once"
            )
        if any(
            not isinstance(initial_offensive_involvement[name], (int, float))
            or isinstance(initial_offensive_involvement[name], bool)
            or not MIN_OFFENSIVE_INVOLVEMENT
            <= initial_offensive_involvement[name]
            <= MAX_OFFENSIVE_INVOLVEMENT
            for name in player_names
        ):
            raise ValueError(
                "offensive involvement must be between "
                f"{MIN_OFFENSIVE_INVOLVEMENT} and {MAX_OFFENSIVE_INVOLVEMENT}"
            )
        offensive_involvement = {
            name: float(initial_offensive_involvement[name]) for name in player_names
        }

    decision_rng = random.Random(seed ^ 0xA11CE)
    outcome_rng = random.Random(seed ^ 0xDDF00D)
    replay = iter(action_tape) if action_tape is not None else None
    emitted_actions: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    seconds_played = {name: 0 for name in player_names}
    expected_shot_points = {name: 0.0 for name in player_names}
    actual_shot_points = {name: 0 for name in player_names}
    previous_lineups: dict[str, tuple[str, ...]] = {}

    def record(event_type: str, **details: object) -> None:
        records.append({"sequence": len(records) + 1, "type": event_type, **details})

    def decide(role: str, team: Team, opponent: Team, ballhandler: str) -> Action:
        if replay is None:
            action = (
                decision_policy(role, state, team, opponent, ballhandler, decision_rng)
                if decision_policy is not None
                else baseline_action(
                    role,
                    state,
                    team,
                    ballhandler,
                    decision_rng,
                    offensive_involvement if initial_offensive_involvement is not None else None,
                )
            )
        else:
            try:
                action = Action.from_mapping(next(replay))
            except StopIteration as error:
                raise ValueError("action tape ended before the game") from error
        validate_action(action, team, opponent, ballhandler)
        emitted_actions.append(action.as_dict())
        record(
            "brain_decision",
            brain_version=brain_version,
            possession=state.possession_number,
            clock_seconds=state.clock_seconds,
            score=dict(state.score),
            action=action.as_dict(),
        )
        return action

    start_details: dict[str, object] = {
        "engine_version": ENGINE_VERSION,
        "brain_version": brain_version,
        "seed": seed,
    }
    if initial_fatigue is not None:
        start_details["pregame_fatigue"] = {name: round(state.fatigue[name], 4) for name in player_names}
    if initial_availability is not None:
        start_details["pregame_availability"] = dict(availability)
    if initial_readiness is not None:
        start_details["pregame_readiness"] = {
            name: round(readiness[name], 4) for name in player_names
        }
    if initial_game_form is not None:
        start_details["pregame_game_form"] = {
            name: round(game_form[name], 4) for name in player_names
        }
    if initial_shooting_consistency is not None:
        start_details["pregame_shooting_consistency"] = {
            name: {"strength": strength, "cap": cap}
            for name, (strength, cap) in shooting_consistency.items()
        }
    if initial_offensive_involvement is not None:
        start_details["pregame_offensive_involvement"] = dict(offensive_involvement)
    record("game_started", **start_details)
    overtime = 0

    while state.clock_seconds > 0 or state.score[home.name] == state.score[away.name]:
        if state.clock_seconds == 0:
            overtime += 1
            state.clock_seconds = 5 * 60
            record("overtime_started", overtime=overtime)

        home_lineup = rotation_lineup(home, state.clock_seconds, overtime, unavailable)
        away_lineup = rotation_lineup(away, state.clock_seconds, overtime, unavailable)
        for lineup in (home_lineup, away_lineup):
            names = tuple(player.name for player in lineup.players)
            if previous_lineups.get(lineup.name) != names:
                record("lineup_changed", team=lineup.name, players=names, clock_seconds=state.clock_seconds)
                previous_lineups[lineup.name] = names

        offense = home_lineup if state.possession == home.name else away_lineup
        defense = away_lineup if offense.name == home.name else home_lineup
        state.possession_number += 1
        ballhandler_weights = [player.passing + player.shooting for player in offense.players]
        if initial_offensive_involvement is not None:
            ballhandler_weights = [
                weight * offensive_involvement[player.name]
                for player, weight in zip(offense.players, ballhandler_weights)
            ]
        ballhandler = outcome_rng.choices(
            offense.players,
            weights=ballhandler_weights,
            k=1,
        )[0].name
        record(
            "possession_started",
            possession=state.possession_number,
            offense=offense.name,
            ballhandler=ballhandler,
            clock_seconds=state.clock_seconds,
        )

        # ponytail: four decisions stand in for a shot clock until timing needs finer simulation.
        for decision_number in range(1, 5):
            state.decision_number = decision_number
            defense_action = decide("defense", defense, offense, ballhandler)
            offense_action = decide("offense", offense, defense, ballhandler)
            defender = defense.player(defense_action.actor)
            attacker = offense.player(offense_action.actor)
            attacker_fatigue = state.fatigue[attacker.name]

            if offense_action.kind == "pass":
                turnover_chance = clamp(
                    0.17
                    + (defender.defense - attacker.passing) / 250
                    + attacker_fatigue * 0.12
                    - readiness[attacker.name]
                    + game_form[defender.name]
                    - game_form[attacker.name],
                    0.05,
                    0.32,
                )
                if outcome_rng.random() < turnover_chance:
                    record(
                        "turnover",
                        possession=state.possession_number,
                        player=attacker.name,
                        defense=defender.name,
                    )
                    break
                record(
                    "pass_completed",
                    possession=state.possession_number,
                    passer=attacker.name,
                    receiver=offense_action.target,
                )
                ballhandler = offense_action.target or ballhandler
                continue

            points = 3 if offense_action.kind == "shoot_3" else 2
            base_chance = {"drive": 0.52, "shoot_2": 0.45, "shoot_3": 0.34}[offense_action.kind]
            base_make_chance = clamp(
                base_chance
                + (attacker.shooting - defender.defense) / 220
                - attacker_fatigue * 0.15
                + readiness[attacker.name]
                + game_form[attacker.name]
                - game_form[defender.name],
                0.08,
                0.78,
            )
            residual = expected_shot_points[attacker.name] - actual_shot_points[attacker.name]
            strength, cap = shooting_consistency[attacker.name]
            consistency_correction = clamp((residual / 2) * strength, -cap, cap)
            make_chance = clamp(base_make_chance + consistency_correction, 0.08, 0.78)
            made = outcome_rng.random() < make_chance
            shot_details: dict[str, object] = {
                "possession": state.possession_number,
                "player": attacker.name,
                "defense": defender.name,
                "action": offense_action.kind,
                "points": points,
                "probability": round(make_chance, 4),
            }
            if initial_shooting_consistency is not None:
                shot_details.update(
                    base_probability=round(base_make_chance, 4),
                    consistency_correction=round(consistency_correction, 4),
                    performance_residual=round(residual, 4),
                )
            record("shot_made" if made else "shot_missed", **shot_details)
            expected_shot_points[attacker.name] += base_make_chance * points
            if made:
                actual_shot_points[attacker.name] += points
            if made:
                state.score[offense.name] += points
                break

            offense_rebounding = sum(player.rebounding for player in offense.players) / len(offense.players)
            defense_rebounding = sum(player.rebounding for player in defense.players) / len(defense.players)
            rebound_chance = clamp(0.24 + (offense_rebounding - defense_rebounding) / 400, 0.12, 0.42)
            if decision_number < 4 and outcome_rng.random() < rebound_chance:
                rebounder = outcome_rng.choices(
                    offense.players,
                    weights=[player.rebounding for player in offense.players],
                    k=1,
                )[0]
                ballhandler = rebounder.name
                record("offensive_rebound", possession=state.possession_number, player=rebounder.name)
                continue
            rebounder = outcome_rng.choices(
                defense.players,
                weights=[player.rebounding for player in defense.players],
                k=1,
            )[0]
            record("defensive_rebound", possession=state.possession_number, player=rebounder.name)
            break
        else:
            record("shot_clock_violation", possession=state.possession_number, team=offense.name)

        elapsed_seconds = min(POSSESSION_SECONDS, state.clock_seconds)
        for team in (home_lineup, away_lineup):
            for player in team.players:
                seconds_played[player.name] += elapsed_seconds
                state.fatigue[player.name] = min(
                    MAX_GAME_FATIGUE,
                    state.fatigue[player.name]
                    + (0.0015 + (100 - player.stamina) / 50_000)
                    * (elapsed_seconds / POSSESSION_SECONDS),
                )
        state.clock_seconds -= elapsed_seconds
        state.possession = defense.name

    if replay is not None:
        sentinel = object()
        if next(replay, sentinel) is not sentinel:
            raise ValueError("action tape contains decisions after the game ended")

    minutes_played = tuple((name, round(seconds_played[name] / 60, 4)) for name in player_names)
    record(
        "game_ended",
        score=dict(state.score),
        possessions=state.possession_number,
        overtime=overtime,
        minutes_played=dict(minutes_played),
    )
    return GameResult(
        seed=seed,
        home_team=home.name,
        away_team=away.name,
        home_score=state.score[home.name],
        away_score=state.score[away.name],
        action_tape=tuple(emitted_actions),
        records=tuple(records),
        minutes_played=minutes_played,
        final_fatigue=tuple((name, round(state.fatigue[name], 4)) for name in player_names),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OddsWell Phase 0A basketball simulator.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log", type=Path, help="Optional JSONL event-log destination.")
    args = parser.parse_args()

    result = simulate_game(args.seed)
    print(f"{result.home_team} {result.home_score} - {result.away_score} {result.away_team}")
    print(f"seed={result.seed} decisions={len(result.action_tape)} events={len(result.records)}")
    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        args.log.write_text(result.jsonl(), encoding="utf-8")
        print(f"wrote {args.log}")


if __name__ == "__main__":
    main()
