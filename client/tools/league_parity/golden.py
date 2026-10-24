"""Reference outputs from the Python simulator for checking the C++ league port.

Writes:
  <out>/games/<name>.txt  one canonical line per event record (full detail, for diffing)
  <out>/golden.txt        compact expectations: per game score, record count and line hash,
                          plus league snapshots, life choices, standings and odds inputs.

The C++ parity harness formats its own records with the same rules and compares.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import phase0d.league as league  # noqa: E402
from phase0a.simulator import default_teams, simulate_game  # noqa: E402
from phase0d.prediction import (  # noqa: E402
    ELO_K,
    prediction_probabilities,
    public_pregame_snapshot,
)


def fmt(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.6f}"
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "{" + ";".join(f"{key}:{fmt(value[key])}" for key in sorted(value)) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(fmt(item) for item in value) + "]"
    raise TypeError(type(value))


def record_lines(records) -> list[str]:
    return [
        "|".join([record["type"]] + [f"{key}={fmt(record[key])}" for key in sorted(record) if key not in ("type", "sequence")])
        for record in records
    ]


def fnv1a(lines: list[str]) -> str:
    value = 0xCBF29CE484222325
    for byte in "\n".join(lines).encode("utf-8"):
        value ^= byte
        value = (value * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def snapshot_text(snapshot) -> str:
    return ",".join(f"{name}={fmt(value)}" for name, value in snapshot)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    games_dir = args.out / "games"
    games_dir.mkdir(parents=True, exist_ok=True)
    golden: list[str] = []

    # 1. Baseline single games: default teams, no league inputs.
    for seed in list(range(1, 31)) + [42, 10_000, 99_999, 2**31 + 7]:
        result = simulate_game(seed)
        lines = record_lines(result.records)
        (games_dir / f"baseline_{seed}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        golden.append(f"baseline|{seed}|{result.home_score}|{result.away_score}|{len(lines)}|{fnv1a(lines)}")

    # 2. One 20-game league season with the production brains, capturing every game's records.
    captured = []
    original = league.simulate_game

    def capture(*a, **k):
        result = original(*a, **k)
        captured.append(result)
        return result

    league.simulate_game = capture
    try:
        season = league.simulate_season(20, 10_000)
    finally:
        league.simulate_game = original

    teams = default_teams()
    elo = {team.name: 1500.0 for team in teams}
    standings = {team.name: [0, 0] for team in teams}
    for index, (game, result) in enumerate(zip(season.games, captured)):
        lines = record_lines(result.records)
        (games_dir / f"season_{game.number}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        fixture = league.ScheduledGame(game.number, game.seed, *(
            (teams[0], teams[1]) if game.home_team == teams[0].name else (teams[1], teams[0])
        ))
        snapshot = public_pregame_snapshot(
            1, fixture, {name: tuple(value) for name, value in standings.items()},
            game.pregame_availability, league.OFFSEASON_REST_DAYS if index == 0 else league.BETWEEN_GAME_REST_DAYS, teams,
        )
        probabilities = dict(prediction_probabilities(snapshot, elo))
        golden.append(
            "season_game|"
            + "|".join(str(x) for x in (game.number, game.seed, game.home_team, game.away_team, game.home_score, game.away_score, len(lines), fnv1a(lines)))
        )
        golden.append(f"season_pregame_fatigue|{game.number}|{snapshot_text(game.pregame_fatigue)}")
        golden.append(f"season_pregame_availability|{game.number}|{snapshot_text(game.pregame_availability)}")
        golden.append(f"season_pregame_readiness|{game.number}|{snapshot_text(game.pregame_readiness)}")
        golden.append(f"season_minutes|{game.number}|{snapshot_text(game.minutes_played)}")
        golden.append(f"season_postgame_fatigue|{game.number}|{snapshot_text(game.postgame_fatigue)}")
        golden.append(f"season_postgame_availability|{game.number}|{snapshot_text(game.postgame_availability)}")
        golden.append(
            f"season_life|{game.number}|"
            + ",".join(f"{d.athlete}={d.selected}" for d in game.life_decisions)
        )
        golden.append(
            f"season_odds|{game.number}|{probabilities['public_elo']:.8f}|{probabilities['public_elo_rotation']:.8f}"
        )
        home_win = int(game.winner == game.home_team)
        change = ELO_K * (home_win - probabilities["public_elo"])
        elo[game.home_team] += change
        elo[game.away_team] -= change
        standings[game.winner][0] += 1
        standings[game.away_team if game.winner == game.home_team else game.home_team][1] += 1
    for row in season.standings:
        golden.append(f"standing|{row.team}|{row.wins}|{row.losses}|{row.points_for}|{row.points_against}")

    (args.out / "golden.txt").write_text("\n".join(golden) + "\n", encoding="utf-8")
    print(f"GOLDEN_WRITTEN|lines={len(golden)}|out={args.out}")


if __name__ == "__main__":
    main()
