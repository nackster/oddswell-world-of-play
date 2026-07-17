from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from phase0a.simulator import (
    BRAIN_VERSION,
    ENGINE_VERSION,
    MAX_READINESS_MODIFIER,
    MAX_RECOVERY_DAYS,
    Team,
    default_teams,
    simulate_game,
)
from phase0c.replay import replay_manifest, verify_replay_manifest
from phase0d.life import (
    DEFAULT_LIFE_BRAIN_VERSION,
    LIFE_BRAIN_V1_VERSION,
    LIFE_BRAIN_V2_VERSION,
    LIFE_BRAIN_V3_VERSION,
    LIFE_BRAIN_V4_VERSION,
    LifeDecision,
    between_game_choices,
    next_routine_streak,
    recent_scoring_form,
)


LEAGUE_VERSION = "phase05w-v1"
STATE_SCHEMA = "oddswell-league-state-v4"
FATIGUE_MODEL_VERSION = "minutes-workload-v1"
INJURY_MODEL_VERSION = "minor-availability-v1"
INJURY_SEED_SALT = 0x1A11AB1E
MAX_INJURY_RISK = 0.04
INJURY_RECOVERY_DAYS = (2, 3, 5, 7)
INJURY_RECOVERY_WEIGHTS = (50, 30, 15, 5)
MAX_CARRYOVER_FATIGUE = 0.35
RECOVERY_PER_DAY = 0.04
BETWEEN_GAME_REST_DAYS = 1
OFFSEASON_REST_DAYS = 7

FatigueSnapshot = tuple[tuple[str, float], ...]
MinutesSnapshot = tuple[tuple[str, float], ...]
AvailabilitySnapshot = tuple[tuple[str, int], ...]
ReadinessSnapshot = tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class ScheduledGame:
    number: int
    seed: int
    home: Team
    away: Team


@dataclass(frozen=True)
class SeasonGame:
    number: int
    seed: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    winner: str
    replay_sha256: str
    pregame_fatigue: FatigueSnapshot
    postgame_fatigue: FatigueSnapshot
    minutes_played: MinutesSnapshot
    pregame_availability: AvailabilitySnapshot
    postgame_availability: AvailabilitySnapshot
    pregame_readiness: ReadinessSnapshot
    life_decisions: tuple[LifeDecision, ...]


@dataclass(frozen=True)
class Standing:
    team: str
    games: int
    wins: int
    losses: int
    points_for: int
    points_against: int

    @property
    def win_rate(self) -> float:
        return self.wins / self.games

    @property
    def point_difference(self) -> int:
        return self.points_for - self.points_against


@dataclass(frozen=True)
class SeasonResult:
    season_number: int
    start_seed: int
    games: tuple[SeasonGame, ...]
    standings: tuple[Standing, ...]
    initial_fatigue: FatigueSnapshot
    final_fatigue: FatigueSnapshot
    initial_availability: AvailabilitySnapshot
    final_availability: AvailabilitySnapshot


@dataclass(frozen=True)
class LeagueState:
    schema: str
    next_season: int
    next_seed: int
    fatigue: FatigueSnapshot
    availability: AvailabilitySnapshot
    seasons: tuple[SeasonResult, ...]


def build_schedule(
    game_count: int = 20,
    start_seed: int = 10_000,
    teams: tuple[Team, Team] | None = None,
) -> tuple[ScheduledGame, ...]:
    if game_count < 2 or game_count % 2:
        raise ValueError("game_count must be a positive even number")
    first, second = teams or default_teams()
    return tuple(
        ScheduledGame(
            number=index + 1,
            seed=start_seed + index,
            home=first if index % 2 == 0 else second,
            away=second if index % 2 == 0 else first,
        )
        for index in range(game_count)
    )


def fatigue_snapshot(values: Mapping[str, float], teams: tuple[Team, Team] | None = None) -> FatigueSnapshot:
    return tuple(
        (player.name, round(float(values[player.name]), 4))
        for team in (teams or default_teams())
        for player in team.players
    )


def empty_fatigue(teams: tuple[Team, Team] | None = None) -> FatigueSnapshot:
    return tuple((player.name, 0.0) for team in (teams or default_teams()) for player in team.players)


def minutes_snapshot(values: Mapping[str, float], teams: tuple[Team, Team] | None = None) -> MinutesSnapshot:
    return tuple(
        (player.name, round(float(values[player.name]), 4))
        for team in (teams or default_teams())
        for player in team.players
    )


def availability_snapshot(
    values: Mapping[str, int],
    teams: tuple[Team, Team] | None = None,
) -> AvailabilitySnapshot:
    roster = teams or default_teams()
    expected = {player.name for team in roster for player in team.players}
    if set(values) != expected or any(
        not isinstance(values[name], int)
        or isinstance(values[name], bool)
        or not 0 <= values[name] <= MAX_RECOVERY_DAYS
        for name in expected
    ):
        raise ValueError("invalid availability roster or recovery days")
    if any(sum(values[player.name] == 0 for player in team.players) < 5 for team in roster):
        raise ValueError("each team needs at least five available players")
    return tuple(
        (player.name, values[player.name])
        for team in roster
        for player in team.players
    )


def empty_availability(teams: tuple[Team, Team] | None = None) -> AvailabilitySnapshot:
    return tuple((player.name, 0) for team in (teams or default_teams()) for player in team.players)


def readiness_snapshot(
    values: Mapping[str, float],
    teams: tuple[Team, Team] | None = None,
) -> ReadinessSnapshot:
    roster = teams or default_teams()
    expected = {player.name for team in roster for player in team.players}
    if set(values) != expected or any(
        not isinstance(values[name], (int, float))
        or isinstance(values[name], bool)
        or not -MAX_READINESS_MODIFIER <= values[name] <= MAX_READINESS_MODIFIER
        for name in expected
    ):
        raise ValueError("invalid readiness roster or value")
    return tuple(
        (player.name, round(float(values[player.name]), 4))
        for team in roster
        for player in team.players
    )


def empty_readiness(teams: tuple[Team, Team] | None = None) -> ReadinessSnapshot:
    return tuple((player.name, 0.0) for team in (teams or default_teams()) for player in team.players)


def apply_life_day(
    game_number: int,
    fatigue: FatigueSnapshot,
    availability: AvailabilitySnapshot,
    teams: tuple[Team, Team],
    *,
    policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
    routine_streaks: Mapping[str, int] | None = None,
    recent_scoring_forms: Mapping[str, str] | None = None,
) -> tuple[FatigueSnapshot, AvailabilitySnapshot, ReadinessSnapshot, tuple[LifeDecision, ...]]:
    decisions = between_game_choices(
        game_number, dict(fatigue), dict(availability), teams,
        policy_version=policy_version,
        routine_streaks=routine_streaks,
        recent_scoring_forms=recent_scoring_forms,
    )
    return (
        fatigue_snapshot(
            {decision.athlete: decision.fatigue_after for decision in decisions}, teams
        ),
        availability_snapshot(
            {decision.athlete: decision.recovery_after for decision in decisions}, teams
        ),
        readiness_snapshot(
            {decision.athlete: decision.readiness for decision in decisions}, teams
        ),
        decisions,
    )


def recover_fatigue(
    fatigue: FatigueSnapshot,
    rest_days: int,
    teams: tuple[Team, Team] | None = None,
) -> FatigueSnapshot:
    if rest_days < 0:
        raise ValueError("rest_days cannot be negative")
    values = dict(fatigue)
    return fatigue_snapshot(
        {name: max(0.0, amount - RECOVERY_PER_DAY * rest_days) for name, amount in values.items()},
        teams,
    )


def recover_availability(
    availability: AvailabilitySnapshot,
    rest_days: int,
    teams: tuple[Team, Team] | None = None,
) -> AvailabilitySnapshot:
    if rest_days < 0:
        raise ValueError("rest_days cannot be negative")
    return availability_snapshot(
        {name: max(0, recovery_days - rest_days) for name, recovery_days in availability},
        teams,
    )


def injury_risk(minutes: float, pregame_fatigue: float) -> float:
    if minutes <= 0:
        return 0.0
    return min(
        MAX_INJURY_RISK,
        max(
            0.0,
            0.002
            + 0.006 * minutes / 48
            + 0.04 * pregame_fatigue
            + 0.012 * max(0.0, minutes - 36) / 12,
        ),
    )


def add_minor_injuries(
    availability: AvailabilitySnapshot,
    fatigue: FatigueSnapshot,
    minutes_played: MinutesSnapshot,
    teams: tuple[Team, Team],
    seed: int,
) -> AvailabilitySnapshot:
    values = dict(availability)
    fatigue_values = dict(fatigue)
    minutes = dict(minutes_played)
    rng = random.Random(seed ^ INJURY_SEED_SALT)
    for team in teams:
        available_count = sum(values[player.name] == 0 for player in team.players)
        for player in team.players:
            if available_count <= 5:
                break
            if values[player.name] or minutes[player.name] <= 0:
                continue
            if rng.random() < injury_risk(minutes[player.name], fatigue_values[player.name]):
                values[player.name] = rng.choices(
                    INJURY_RECOVERY_DAYS,
                    weights=INJURY_RECOVERY_WEIGHTS,
                    k=1,
                )[0]
                available_count -= 1
    return availability_snapshot(values, teams)


def add_game_load(
    fatigue: FatigueSnapshot,
    teams: tuple[Team, Team],
    minutes_played: MinutesSnapshot,
) -> FatigueSnapshot:
    values = dict(fatigue)
    minutes = dict(minutes_played)
    return fatigue_snapshot(
        {
            player.name: min(
                MAX_CARRYOVER_FATIGUE,
                values[player.name]
                + (0.05 + (100 - player.stamina) / 1_000) * (minutes[player.name] / 48),
            )
            for team in teams
            for player in team.players
        },
        teams,
    )


def simulate_scheduled_game(
    fixture: ScheduledGame,
    fatigue: FatigueSnapshot,
    availability: AvailabilitySnapshot,
    teams: tuple[Team, Team],
    readiness: ReadinessSnapshot | None = None,
    life_decisions: tuple[LifeDecision, ...] = (),
    *,
    life_policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
    _player_points: dict[str, int] | None = None,
) -> SeasonGame:
    """Resolve one scheduled game through the authoritative league transition."""
    if life_policy_version not in {
        LIFE_BRAIN_V1_VERSION, LIFE_BRAIN_V2_VERSION, LIFE_BRAIN_V3_VERSION,
        LIFE_BRAIN_V4_VERSION,
    }:
        raise ValueError(f"unsupported Athlete Life Brain policy: {life_policy_version!r}")
    matchup = (fixture.home, fixture.away)
    if any(decision.policy_version != life_policy_version for decision in life_decisions):
        raise ValueError("life decision policy does not match replay metadata")
    readiness = readiness or empty_readiness(teams)
    result = simulate_game(
        fixture.seed,
        matchup=matchup,
        initial_fatigue=dict(fatigue),
        initial_availability=dict(availability),
        initial_readiness=dict(readiness),
    )
    if _player_points is not None:
        _player_points.update({player.name: 0 for team in teams for player in team.players})
        for record in result.records:
            if record["type"] == "shot_made":
                _player_points[str(record["player"])] += int(record["points"])
    played = minutes_snapshot(dict(result.minutes_played), teams)
    postgame_fatigue = add_game_load(fatigue, teams, played)
    postgame_availability = add_minor_injuries(
        availability, fatigue, played, teams, fixture.seed
    )
    manifest = replay_manifest(
        result,
        matchup,
        BRAIN_VERSION,
        {
            "injury_model_version": INJURY_MODEL_VERSION,
            "minutes_played": dict(played),
            "pregame_availability": dict(availability),
            "postgame_availability": dict(postgame_availability),
            "life_brain_version": life_policy_version,
            "life_decisions": [asdict(decision) for decision in life_decisions],
            "pregame_readiness": dict(readiness),
        },
    )
    if not verify_replay_manifest(manifest):
        raise RuntimeError(f"replay manifest failed for game {fixture.number}")
    return SeasonGame(
        fixture.number,
        fixture.seed,
        result.home_team,
        result.away_team,
        result.home_score,
        result.away_score,
        result.home_team if result.home_score > result.away_score else result.away_team,
        manifest["sha256"],
        fatigue,
        postgame_fatigue,
        played,
        availability,
        postgame_availability,
        readiness,
        life_decisions,
    )


def simulate_season(
    game_count: int = 20,
    start_seed: int = 10_000,
    initial_fatigue: FatigueSnapshot | None = None,
    initial_availability: AvailabilitySnapshot | None = None,
    season_number: int = 1,
    teams: tuple[Team, Team] | None = None,
    *,
    life_policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
) -> SeasonResult:
    teams = teams or default_teams()
    schedule = build_schedule(game_count, start_seed, teams)
    fatigue = initial_fatigue or empty_fatigue(teams)
    fatigue = fatigue_snapshot(dict(fatigue), teams)
    availability = initial_availability or empty_availability(teams)
    availability = availability_snapshot(dict(availability), teams)
    season_start = fatigue
    season_start_availability = availability
    totals: dict[str, Counter[str]] = {team.name: Counter() for team in teams}
    games = []
    routine_streaks = (
        {player.name: 0 for team in teams for player in team.players}
        if life_policy_version in {LIFE_BRAIN_V3_VERSION, LIFE_BRAIN_V4_VERSION}
        else None
    )
    scoring_history: dict[str, tuple[tuple[int, float], ...]] = {
        player.name: () for team in teams for player in team.players
    }

    for index, fixture in enumerate(schedule):
        readiness = empty_readiness(teams)
        life_decisions: tuple[LifeDecision, ...] = ()
        if index:
            fatigue = recover_fatigue(fatigue, BETWEEN_GAME_REST_DAYS, teams)
            availability = recover_availability(availability, BETWEEN_GAME_REST_DAYS, teams)
            scoring_forms = None
            if life_policy_version == LIFE_BRAIN_V4_VERSION:
                scoring_forms = {
                    athlete: recent_scoring_form(history)
                    for athlete, history in scoring_history.items()
                }
            fatigue, availability, readiness, life_decisions = apply_life_day(
                fixture.number, fatigue, availability, teams,
                policy_version=life_policy_version,
                routine_streaks=routine_streaks,
                recent_scoring_forms=scoring_forms,
            )
            if routine_streaks is not None:
                routine_streaks = {
                    decision.athlete: next_routine_streak(
                        routine_streaks[decision.athlete], decision.selected
                    )
                    for decision in life_decisions
                }
        player_points: dict[str, int] | None = (
            {} if life_policy_version == LIFE_BRAIN_V4_VERSION else None
        )
        game = simulate_scheduled_game(
            fixture, fatigue, availability, teams, readiness, life_decisions,
            life_policy_version=life_policy_version,
            _player_points=player_points,
        )
        if life_policy_version == LIFE_BRAIN_V4_VERSION:
            assert player_points is not None
            minutes = dict(game.minutes_played)
            scoring_history = {
                athlete: history + ((player_points[athlete], minutes[athlete]),)
                for athlete, history in scoring_history.items()
            }
        winner = game.winner
        loser = game.away_team if winner == game.home_team else game.home_team

        totals[winner]["wins"] += 1
        totals[loser]["losses"] += 1
        totals[game.home_team]["points_for"] += game.home_score
        totals[game.home_team]["points_against"] += game.away_score
        totals[game.away_team]["points_for"] += game.away_score
        totals[game.away_team]["points_against"] += game.home_score
        games.append(game)
        fatigue = game.postgame_fatigue
        availability = game.postgame_availability

    standings = tuple(
        sorted(
            (
                Standing(
                    team,
                    totals[team]["wins"] + totals[team]["losses"],
                    totals[team]["wins"],
                    totals[team]["losses"],
                    totals[team]["points_for"],
                    totals[team]["points_against"],
                )
                for team in totals
            ),
            key=lambda row: (-row.wins, -row.point_difference, -row.points_for, row.team),
        )
    )
    return SeasonResult(
        season_number,
        start_seed,
        tuple(games),
        standings,
        season_start,
        fatigue,
        season_start_availability,
        availability,
    )


def new_league(start_seed: int = 10_000) -> LeagueState:
    return LeagueState(STATE_SCHEMA, 1, start_seed, empty_fatigue(), empty_availability(), ())


def simulate_next_season(
    state: LeagueState,
    game_count: int = 20,
    teams: tuple[Team, Team] | None = None,
    *,
    life_policy_version: str = DEFAULT_LIFE_BRAIN_VERSION,
) -> LeagueState:
    if state.schema != STATE_SCHEMA:
        raise ValueError(f"unsupported league state schema: {state.schema}")
    season_teams = teams or default_teams()
    fatigue_values = dict(state.fatigue)
    availability_values = dict(state.availability)
    aligned_fatigue = fatigue_snapshot(
        {
            player.name: fatigue_values.get(player.name, 0.0)
            for team in season_teams
            for player in team.players
        },
        season_teams,
    )
    aligned_availability = availability_snapshot(
        {
            player.name: availability_values.get(player.name, 0)
            for team in season_teams
            for player in team.players
        },
        season_teams,
    )
    initial_fatigue = (
        recover_fatigue(aligned_fatigue, OFFSEASON_REST_DAYS, season_teams)
        if state.seasons
        else aligned_fatigue
    )
    initial_availability = (
        recover_availability(aligned_availability, OFFSEASON_REST_DAYS, season_teams)
        if state.seasons
        else aligned_availability
    )
    season = simulate_season(
        game_count,
        state.next_seed,
        initial_fatigue,
        initial_availability,
        state.next_season,
        season_teams,
        life_policy_version=life_policy_version,
    )
    return LeagueState(
        STATE_SCHEMA,
        state.next_season + 1,
        state.next_seed + game_count,
        season.final_fatigue,
        season.final_availability,
        state.seasons + (season,),
    )


def save_league(state: LeagueState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _snapshot_from_json(value: object) -> FatigueSnapshot:
    if not isinstance(value, list) or any(
        not isinstance(item, list)
        or len(item) != 2
        or not isinstance(item[0], str)
        or not isinstance(item[1], (int, float))
        for item in value
    ):
        raise ValueError("invalid fatigue snapshot")
    snapshot = tuple((item[0], float(item[1])) for item in value)
    expected = {player.name for team in default_teams() for player in team.players}
    if len(snapshot) != len(expected) or {name for name, _ in snapshot} != expected or any(
        not 0 <= amount <= MAX_CARRYOVER_FATIGUE for _, amount in snapshot
    ):
        raise ValueError("invalid fatigue roster or value")
    return snapshot


def _minutes_from_json(value: object) -> MinutesSnapshot:
    if not isinstance(value, list) or any(
        not isinstance(item, list)
        or len(item) != 2
        or not isinstance(item[0], str)
        or not isinstance(item[1], (int, float))
        or isinstance(item[1], bool)
        for item in value
    ):
        raise ValueError("invalid minutes snapshot")
    snapshot = tuple((item[0], float(item[1])) for item in value)
    expected = {player.name for team in default_teams() for player in team.players}
    if len(snapshot) != len(expected) or {name for name, _ in snapshot} != expected or any(
        not 0 <= minutes <= 100 for _, minutes in snapshot
    ):
        raise ValueError("invalid minutes roster or value")
    return snapshot


def _availability_from_json(value: object) -> AvailabilitySnapshot:
    expected_count = sum(len(team.players) for team in default_teams())
    if not isinstance(value, list) or len(value) != expected_count or any(
        not isinstance(item, list)
        or len(item) != 2
        or not isinstance(item[0], str)
        or not isinstance(item[1], int)
        or isinstance(item[1], bool)
        for item in value
    ):
        raise ValueError("invalid availability snapshot")
    return availability_snapshot({name: recovery_days for name, recovery_days in value})


def _readiness_from_json(value: object) -> ReadinessSnapshot:
    if not isinstance(value, list) or any(
        not isinstance(item, list)
        or len(item) != 2
        or not isinstance(item[0], str)
        or not isinstance(item[1], (int, float))
        or isinstance(item[1], bool)
        for item in value
    ):
        raise ValueError("invalid readiness snapshot")
    return readiness_snapshot({name: amount for name, amount in value})


def _life_decisions_from_json(value: object) -> tuple[LifeDecision, ...]:
    if not isinstance(value, list):
        raise ValueError("invalid life decisions")
    decisions = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("invalid life decision")
        decision = dict(item)
        legal_choices = decision.get("legal_choices")
        if not isinstance(legal_choices, list):
            raise ValueError("invalid life decision choices")
        decision["legal_choices"] = tuple(legal_choices)
        decisions.append(LifeDecision(**decision))
    return tuple(decisions)


def load_league(path: Path) -> LeagueState:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or set(value) != {
            "schema",
            "next_season",
            "next_seed",
            "fatigue",
            "availability",
            "seasons",
        }:
            raise ValueError("invalid league state fields")
        if value["schema"] != STATE_SCHEMA:
            raise ValueError(f"unsupported league state schema {value['schema']!r}; expected {STATE_SCHEMA!r}")
        if not isinstance(value["seasons"], list):
            raise ValueError("invalid seasons")
        seasons = []
        for season_value in value["seasons"]:
            season_data = dict(season_value)
            games = []
            for game_value in season_data.pop("games"):
                game_data = dict(game_value)
                game_data["pregame_fatigue"] = _snapshot_from_json(game_data["pregame_fatigue"])
                game_data["postgame_fatigue"] = _snapshot_from_json(game_data["postgame_fatigue"])
                game_data["minutes_played"] = _minutes_from_json(game_data["minutes_played"])
                game_data["pregame_availability"] = _availability_from_json(
                    game_data["pregame_availability"]
                )
                game_data["postgame_availability"] = _availability_from_json(
                    game_data["postgame_availability"]
                )
                game_data["pregame_readiness"] = _readiness_from_json(
                    game_data["pregame_readiness"]
                )
                game_data["life_decisions"] = _life_decisions_from_json(
                    game_data["life_decisions"]
                )
                games.append(SeasonGame(**game_data))
            standings = tuple(Standing(**row) for row in season_data.pop("standings"))
            season_data["initial_fatigue"] = _snapshot_from_json(season_data["initial_fatigue"])
            season_data["final_fatigue"] = _snapshot_from_json(season_data["final_fatigue"])
            season_data["initial_availability"] = _availability_from_json(
                season_data["initial_availability"]
            )
            season_data["final_availability"] = _availability_from_json(
                season_data["final_availability"]
            )
            seasons.append(SeasonResult(games=tuple(games), standings=standings, **season_data))
        return LeagueState(
            value["schema"],
            int(value["next_season"]),
            int(value["next_seed"]),
            _snapshot_from_json(value["fatigue"]),
            _availability_from_json(value["availability"]),
            tuple(seasons),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid league state {path}: {error}") from error


def average_fatigue(fatigue: FatigueSnapshot) -> float:
    return sum(value for _, value in fatigue) / len(fatigue)


def availability_metrics(state: LeagueState) -> dict[str, float | int]:
    active_player_games = 0
    missed_player_games = 0
    new_injuries = 0
    high_workload_games = 0
    high_workload_injuries = 0
    lower_workload_games = 0
    lower_workload_injuries = 0
    zero_minute_absences = 0
    minimum_available = len(default_teams()[0].players)
    max_recovery_days = 0
    teams = default_teams()

    for season in state.seasons:
        for game in season.games:
            before = dict(game.pregame_availability)
            after = dict(game.postgame_availability)
            minutes = dict(game.minutes_played)
            max_recovery_days = max(max_recovery_days, *after.values())
            for team in teams:
                minimum_available = min(
                    minimum_available,
                    sum(before[player.name] == 0 for player in team.players),
                )
            for player, recovery_days in before.items():
                if recovery_days:
                    missed_player_games += 1
                    zero_minute_absences += minutes[player] == 0
                    continue
                active_player_games += 1
                injured = after[player] > 0
                new_injuries += injured
                if minutes[player] > 36:
                    high_workload_games += 1
                    high_workload_injuries += injured
                else:
                    lower_workload_games += 1
                    lower_workload_injuries += injured

    return {
        "active_player_games": active_player_games,
        "missed_player_games": missed_player_games,
        "new_injuries": new_injuries,
        "injury_rate": new_injuries / active_player_games if active_player_games else 0.0,
        "high_workload_games": high_workload_games,
        "high_workload_injuries": high_workload_injuries,
        "high_workload_rate": high_workload_injuries / high_workload_games if high_workload_games else 0.0,
        "lower_workload_games": lower_workload_games,
        "lower_workload_injuries": lower_workload_injuries,
        "lower_workload_rate": lower_workload_injuries / lower_workload_games if lower_workload_games else 0.0,
        "zero_minute_absences": zero_minute_absences,
        "minimum_available": minimum_available,
        "max_recovery_days": max_recovery_days,
    }


def render_markdown(season: SeasonResult) -> str:
    lines = [
        "---",
        "tags:",
        "  - development",
        "  - simulation",
        "  - season",
        "status: active",
        "---",
        "",
        "# Phase 0D Schedule and Standings",
        "",
        (
            f"Deterministic **{len(season.games)}-game** league run using seeds "
            f"`{season.start_seed}`-`{season.start_seed + len(season.games) - 1}`, "
            f"league `{LEAGUE_VERSION}`, and brain `{BRAIN_VERSION}`."
        ),
        "",
        "## Standings",
        "",
        "| Rank | Team | W | L | Win% | PF | PA | Diff |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, standing in enumerate(season.standings, 1):
        lines.append(
            f"| {rank} | {standing.team} | {standing.wins} | {standing.losses} | "
            f"{standing.win_rate:.1%} | {standing.points_for} | {standing.points_against} | "
            f"{standing.point_difference:+d} |"
        )
    lines.extend(
        [
            "",
            "## Schedule and results",
            "",
            "| Game | Seed | Away | Score | Home | Winner | Replay hash | Avg pregame fatigue |",
            "| ---: | ---: | --- | ---: | --- | --- | --- | ---: |",
        ]
    )
    for game in season.games:
        lines.append(
            f"| {game.number} | {game.seed} | {game.away_team} | "
            f"{game.away_score}-{game.home_score} | {game.home_team} | {game.winner} | "
            f"`{game.replay_sha256[:12]}` | {average_fatigue(game.pregame_fatigue):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            (
                "This slice proves balanced scheduling, deterministic standings, replay integrity, and "
                "bounded fatigue carried between games."
            ),
            "",
            (
                "Tactical substitutions, public information, prediction scoring, and live LLM control "
                "remain separate measured steps."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def render_league_markdown(state: LeagueState) -> str:
    metrics = availability_metrics(state)
    lines = [
        "---",
        "tags:",
        "  - development",
        "  - simulation",
        "  - season",
        "  - fatigue",
        "  - availability",
        "  - injuries",
        "status: complete",
        "---",
        "",
        "# Phase 0D.3 Availability and Recovery",
        "",
        (
            f"Deterministic **{len(state.seasons)}-season** run using state schema `{STATE_SCHEMA}`, "
            f"league `{LEAGUE_VERSION}`, engine `{ENGINE_VERSION}`, fatigue model `{FATIGUE_MODEL_VERSION}`, "
            f"injury model `{INJURY_MODEL_VERSION}`, and brain `{BRAIN_VERSION}`."
        ),
        "",
        "## Season summary",
        "",
        "| Season | Seeds | Leader | Record | New injuries | Missed player-games | Replay hashes |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for season in state.seasons:
        leader = season.standings[0]
        season_state = LeagueState(
            STATE_SCHEMA,
            0,
            0,
            season.final_fatigue,
            season.final_availability,
            (season,),
        )
        season_metrics = availability_metrics(season_state)
        lines.append(
            f"| {season.season_number} | {season.start_seed}-{season.start_seed + len(season.games) - 1} | "
            f"{leader.team} | {leader.wins}-{leader.losses} | {season_metrics['new_injuries']} | "
            f"{season_metrics['missed_player_games']} | {len(season.games)}/{len(season.games)} |"
        )
    lines.extend(
        [
            "",
            "## Fixed-seed realism guardrails",
            "",
            f"- **{metrics['new_injuries']}** new minor injuries across **{metrics['active_player_games']}** active player-games "
            f"(**{metrics['injury_rate']:.2%}**). The per-player ceiling is **{MAX_INJURY_RISK:.0%}**.",
            f"- High-workload player-games above 36 minutes: **{metrics['high_workload_injuries']}/{metrics['high_workload_games']}** "
            f"(**{metrics['high_workload_rate']:.2%}**); lower workload: "
            f"**{metrics['lower_workload_injuries']}/{metrics['lower_workload_games']}** "
            f"(**{metrics['lower_workload_rate']:.2%}**).",
            f"- Unavailable players missed **{metrics['missed_player_games']}** player-games; "
            f"**{metrics['zero_minute_absences']}/{metrics['missed_player_games']}** recorded zero minutes.",
            f"- Every team retained at least **{metrics['minimum_available']}** available players. "
            f"The longest assigned recovery was **{metrics['max_recovery_days']} days**.",
            "",
            "## Persistence gate",
            "",
            "- JSON stores pregame and postgame availability, recovery days, minutes, fatigue, seeds, and replay hashes.",
            "- Save, load, and resume use the same deterministic simulation path.",
            "- Replay evidence binds the injury-model version, minutes, and pregame/postgame availability.",
            "",
            "## Availability model",
            "",
            "- Only players who logged minutes can receive a new postgame injury.",
            "- Injury risk rises with authoritative minutes and pregame fatigue, then clamps at 4%.",
            "- Recovery durations are 2, 3, 5, or 7 days and decrease by scheduled rest days.",
            "- Unavailable players are excluded from lineups. The six-player prototype suppresses another injury at five available players.",
            "",
            "## Scope",
            "",
            "In-game injuries, diagnoses, limited/questionable status, permanent injuries, treatment choices, "
            "off-court injuries, credits, wagers, paid model calls, and retraining are outside this gate.",
            "The probabilities are provisional engineering calibration values, not medical claims.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic OddsWell Phase 0D seasons.")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--seasons", type=int, default=1)
    parser.add_argument("--start-seed", type=int, default=10_000)
    parser.add_argument("--state", type=Path, help="Optional JSON state to load and save.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.seasons < 1:
        parser.error("--seasons must be positive")

    state = load_league(args.state) if args.state and args.state.exists() else new_league(args.start_seed)
    for _ in range(args.seasons):
        state = simulate_next_season(state, args.games)
    if args.state:
        save_league(state, args.state)
        print(f"wrote {args.state}")

    report = render_league_markdown(state)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    champion = state.seasons[-1].standings[0]
    print(
        f"seasons={len(state.seasons)} games={sum(len(season.games) for season in state.seasons)} "
        f"latest_leader={champion.team} record={champion.wins}-{champion.losses}"
    )


if __name__ == "__main__":
    main()
