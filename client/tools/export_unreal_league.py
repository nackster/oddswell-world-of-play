"""Export the existing public league read model for the Unreal player client."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from brain_admin.server import athlete_profiles_payload, league_payload, player_tier
from phase0d.prediction import run_prediction_study
from phase1h.odds import match_winner_offer


OUTPUT = ROOT / "client/OddsWell/Content/League/PublicSeason1.json"
GAME_ONE_LOCK_UNIX = 2_000_000_000
FORBIDDEN_KEY_PARTS = (
    "seed",
    "rng",
    "fatigue",
    "readiness",
    "recovery",
    "injury_risk",
    "resolver",
)


def keys(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key.lower()
            yield from keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from keys(child)


def athlete_stories(public: dict[str, object]) -> list[dict[str, object]]:
    profiles = {
        profile["name"]: profile
        for profile in athlete_profiles_payload()["profiles"]
        if profile["career"]["debut_season"] == 1
    }
    available = {
        player["name"]: player["available"]
        for team in public["teams"]
        for player in team["players"]
    }
    stories = []
    for team in public["teams"]:
        for player in team["players"]:
            profile = profiles[player["name"]]
            season = profile["seasons"][0]
            recent_games = season["form"]["games"]
            latest_life = season["life"]["recent"][0]
            stories.append({
                "name": player["name"],
                "team": team["name"],
                "talent_tier": player_tier(season["overall"]),
                "specialty": profile["career"]["specialty"],
                "consistency": profile["career"]["game_consistency"]["tier"],
                "offensive_role": profile["career"]["offensive_involvement"]["tier"],
                "form": season["form"]["label"],
                "season_points_per_game": season["points_per_game"],
                "recent_points_per_game": season["form"]["points_per_game"],
                "recent_minutes_per_game": round(
                    sum(float(game["minutes"]) for game in recent_games) / len(recent_games),
                    2,
                ),
                "available": available[player["name"]],
                "life_choice": latest_life["choice"],
                "life_game": latest_life["game"],
                "life_brain_version": season["life"]["version"],
            })
    return stories


def main() -> None:
    public = league_payload()
    prediction = run_prediction_study(0, 1, 4, 712).records[0]
    assert prediction.season_number == 1 and prediction.game_number == 1
    assert public["games"][0]["prediction_commitment_sha256"] == prediction.commitment_sha256
    offer = match_winner_offer(
        prediction.commitment_json,
        prediction.commitment_sha256,
        GAME_ONE_LOCK_UNIX,
    )
    fixture = {
        "schema": "oddswell-public-league-v1",
        "public_only": True,
        "match_winner_offer": offer,
        "athlete_stories": athlete_stories(public),
        **public,
    }
    assert fixture["season"] == {
        "number": 1,
        "status": "COMPLETE",
        "games": 20,
        "label": "Phase 0.5B archived development season",
    }
    assert len(fixture["standings"]) == 2
    assert len(fixture["teams"]) == 2
    assert sum(len(team["players"]) for team in fixture["teams"]) == 12
    assert len(fixture["athlete_stories"]) == 12
    assert {story["name"] for story in fixture["athlete_stories"]} == {
        player["name"] for team in fixture["teams"] for player in team["players"]
    }
    assert all(story["life_brain_version"] == "athlete-life-v4" for story in fixture["athlete_stories"])
    assert all(story["life_choice"] in {"TRAIN", "REST", "RECOVER", "SOCIALIZE"} for story in fixture["athlete_stories"])
    assert len(fixture["games"]) == 20
    assert all(game["replay_sha256"] for game in fixture["games"])
    assert not [key for key in keys(fixture) if any(part in key for part in FORBIDDEN_KEY_PARTS)]

    encoded = (json.dumps(fixture, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(encoded)
    print(f"LEAGUE_FIXTURE={OUTPUT}")
    print("LEAGUE_TEAMS=2")
    print("LEAGUE_ATHLETES=12")
    print("LEAGUE_GAMES=20")
    print(f"FIXTURE_BYTES={len(encoded)}")
    print(f"FIXTURE_SHA256={hashlib.sha256(encoded).hexdigest()}")


if __name__ == "__main__":
    main()
