from __future__ import annotations

import hashlib
import json
from typing import Mapping

from phase0a.simulator import ENGINE_VERSION, GameResult, Team


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def replay_manifest(game: GameResult, matchup: tuple[Team, Team], policy_version: str) -> dict[str, object]:
    payload = {
        "schema": "oddswell-replay-v1",
        "engine_version": ENGINE_VERSION,
        "policy_version": policy_version,
        "seed": game.seed,
        "matchup": [
            {
                "side": side,
                "team": team.name,
                "roster": [vars(player) for player in team.players],
            }
            for side, team in zip(("home", "away"), matchup)
        ],
        "action_tape": list(game.action_tape),
        "event_log": list(game.records),
    }
    return {"payload": payload, "sha256": hashlib.sha256(canonical_json(payload).encode()).hexdigest()}


def verify_replay_manifest(manifest: Mapping[str, object]) -> bool:
    payload = manifest.get("payload")
    digest = manifest.get("sha256")
    return isinstance(digest, str) and hashlib.sha256(canonical_json(payload).encode()).hexdigest() == digest
