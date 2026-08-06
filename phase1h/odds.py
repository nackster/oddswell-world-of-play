"""Versioned Match Winner odds offers from frozen public prediction evidence."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json

from phase0d.prediction import PREDICTION_VERSION, PUBLIC_SNAPSHOT_VERSION


OFFER_VERSION = "basketball-match-winner-odds-v1"
SOURCE_MODEL = "public_elo_rotation"
PROBABILITY_SCALE = 100_000_000
MIN_STAKE = 10
MAX_STAKE = 100
STAKE_INCREMENT = 10


def _whole_number(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a whole number")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def match_winner_offer(
    prediction_commitment_json: str,
    prediction_commitment_sha256: str,
    lock_unix: int,
) -> dict[str, object]:
    """Create one immutable offer without accepting a stake or reading a result."""
    if hashlib.sha256(prediction_commitment_json.encode()).hexdigest() != prediction_commitment_sha256:
        raise ValueError("prediction commitment does not verify")
    try:
        commitment = json.loads(prediction_commitment_json)
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError("prediction commitment is not valid JSON") from error
    if not isinstance(commitment, dict) or set(commitment) != {"snapshot", "predictions"}:
        raise ValueError("prediction commitment has an invalid shape")
    snapshot = commitment["snapshot"]
    predictions = commitment["predictions"]
    if not isinstance(snapshot, dict) or snapshot.get("version") != PUBLIC_SNAPSHOT_VERSION:
        raise ValueError("prediction commitment has an unsupported public snapshot")
    if not isinstance(predictions, dict) or SOURCE_MODEL not in predictions:
        raise ValueError("prediction commitment is missing the approved source model")

    home = snapshot.get("home_team")
    away = snapshot.get("away_team")
    season = _whole_number(snapshot.get("season_number"), "season_number")
    game = _whole_number(snapshot.get("game_number"), "game_number")
    lock = _whole_number(lock_unix, "lock_unix")
    if not isinstance(home, str) or not home or not isinstance(away, str) or not away or home == away:
        raise ValueError("prediction commitment has invalid teams")
    if season <= 0 or game <= 0 or lock <= 0:
        raise ValueError("season, game, and lock time must be positive")

    value = predictions[SOURCE_MODEL]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("approved win probability must be numeric")
    probability = Decimal(str(value))
    scaled = probability * PROBABILITY_SCALE
    if not probability.is_finite() or scaled != scaled.to_integral_value():
        raise ValueError("approved win probability must have at most eight decimal places")
    home_probability = int(scaled)
    if not 0 < home_probability < PROBABILITY_SCALE:
        raise ValueError("approved win probability must be between zero and one")

    selections = []
    for team, probability_e8 in (
        (home, home_probability),
        (away, PROBABILITY_SCALE - home_probability),
    ):
        selections.append(
            {
                "team": team,
                "win_probability_e8": probability_e8,
                "decimal_odds_e4": PROBABILITY_SCALE * 10_000 // probability_e8,
            }
        )
    offer = {
        "schema": "oddswell-basketball-odds-offer-v1",
        "offer_version": OFFER_VERSION,
        "market": "match_winner",
        "currency": "odds_bucks",
        "source_prediction_version": PREDICTION_VERSION,
        "source_snapshot_version": PUBLIC_SNAPSHOT_VERSION,
        "source_model": SOURCE_MODEL,
        "source_commitment_sha256": prediction_commitment_sha256,
        "season_number": season,
        "game_number": game,
        "home_team": home,
        "away_team": away,
        "lock_unix": lock,
        "minimum_stake": MIN_STAKE,
        "maximum_stake": MAX_STAKE,
        "stake_increment": STAKE_INCREMENT,
        "house_edge_bps": 0,
        "payout_formula": "floor(stake*100000000/win_probability_e8)",
        "selections": selections,
    }
    return {"offer_id": hashlib.sha256(_canonical_json(offer).encode()).hexdigest(), **offer}


def match_winner_gross_return(offer: dict[str, object], team: str, stake: int) -> int:
    """Return the approved whole-Odds-Bucks gross payout; no ledger mutation occurs."""
    stake = _whole_number(stake, "stake")
    if stake < MIN_STAKE or stake > MAX_STAKE or stake % STAKE_INCREMENT:
        raise ValueError("stake must be 10-100 Odds Bucks in increments of 10")
    if offer.get("offer_version") != OFFER_VERSION or offer.get("market") != "match_winner":
        raise ValueError("unsupported odds offer")
    selections = offer.get("selections")
    if not isinstance(selections, list):
        raise ValueError("odds offer has no selections")
    selection = next(
        (candidate for candidate in selections if isinstance(candidate, dict) and candidate.get("team") == team),
        None,
    )
    if selection is None:
        raise ValueError("team is not offered")
    probability = _whole_number(selection.get("win_probability_e8"), "win_probability_e8")
    if not 0 < probability < PROBABILITY_SCALE:
        raise ValueError("offered probability is invalid")
    return stake * PROBABILITY_SCALE // probability
