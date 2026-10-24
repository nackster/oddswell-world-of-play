"""Export the frozen public replay fixture consumed by the Unreal benchmark."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from brain_admin.server import archived_replay_payload


OUTPUT = Path("client/OddsWell/Content/Replay/Season1Game1.json")
EXPECTED_SEAL = "00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75"
FORBIDDEN_KEY_PARTS = ("seed", "rng", "fatigue", "readiness", "recovery", "injury_risk", "resolver")


def keys(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key.lower()
            yield from keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from keys(child)


def main() -> None:
    archived = archived_replay_payload(1, 1)
    fixture = {
        "schema": "oddswell-public-replay-v1",
        "summary": archived["summary"],
        "archive": archived["archive"],
        "frames": archived["theater_timeline"],
    }
    summary = fixture["summary"]
    archive = fixture["archive"]
    frames = fixture["frames"]
    assert summary["home"] == "Harbor City Waves" and summary["away"] == "Mesa Vista Sol"
    assert (summary["home_score"], summary["away_score"]) == (101, 104)
    assert summary["replay_frames"] == len(frames) == 421
    assert archive["verified"] is True and archive["replay_sha256"] == EXPECTED_SEAL
    assert frames[-1]["kind"] == "final" and frames[-1]["score"] == [101, 104]
    assert not [key for key in keys(fixture) if any(part in key for part in FORBIDDEN_KEY_PARTS)]

    encoded = (json.dumps(fixture, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(encoded)
    print(f"REPLAY_FIXTURE={OUTPUT}")
    print(f"REPLAY_FRAMES={len(frames)}")
    print(f"REPLAY_SEAL={archive['replay_sha256']}")
    print(f"FIXTURE_BYTES={len(encoded)}")
    print(f"FIXTURE_SHA1={hashlib.sha1(encoded).hexdigest()}")
    print(f"FIXTURE_SHA256={hashlib.sha256(encoded).hexdigest()}")


if __name__ == "__main__":
    main()
