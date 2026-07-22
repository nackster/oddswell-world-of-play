import json
import unittest

from phase0d.prediction import PREDICTION_VERSION, run_prediction_study
from phase1h.odds import (
    MAX_STAKE,
    MIN_STAKE,
    OFFER_VERSION,
    PROBABILITY_SCALE,
    match_winner_gross_return,
    match_winner_offer,
)


class MatchWinnerOddsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = run_prediction_study(0, 1, 4, 712).records[0]
        cls.offer = match_winner_offer(
            cls.record.commitment_json,
            cls.record.commitment_sha256,
            2_000_000_000,
        )

    def test_offer_is_deterministic_public_and_versioned(self) -> None:
        self.assertEqual(self.offer["offer_version"], OFFER_VERSION)
        self.assertEqual(self.offer["source_prediction_version"], PREDICTION_VERSION)
        self.assertEqual(self.offer["source_commitment_sha256"], self.record.commitment_sha256)
        self.assertEqual(len(self.offer["offer_id"]), 64)
        self.assertEqual(
            self.offer,
            match_winner_offer(self.record.commitment_json, self.record.commitment_sha256, 2_000_000_000),
        )
        self.assertEqual(
            sum(selection["win_probability_e8"] for selection in self.offer["selections"]),
            PROBABILITY_SCALE,
        )
        encoded = json.dumps(self.offer).lower()
        for forbidden in ("replay_sha256", '"score"', '"seed"', '"rng"', '"fatigue"', '"life"'):
            self.assertNotIn(forbidden, encoded)

    def test_approved_stakes_have_exact_fair_gross_returns(self) -> None:
        for stake in (MIN_STAKE, 50, MAX_STAKE):
            for selection in self.offer["selections"]:
                expected = stake * PROBABILITY_SCALE // selection["win_probability_e8"]
                self.assertEqual(match_winner_gross_return(self.offer, selection["team"], stake), expected)
                self.assertGreater(expected, stake)
        for invalid in (True, 0, 9, 11, 101):
            with self.assertRaises(ValueError):
                match_winner_gross_return(self.offer, self.offer["home_team"], invalid)
        with self.assertRaises(ValueError):
            match_winner_gross_return(self.offer, "Not A Team", MIN_STAKE)

    def test_tampered_or_invalid_commitments_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            match_winner_offer(self.record.commitment_json + " ", self.record.commitment_sha256, 2_000_000_000)
        with self.assertRaises(ValueError):
            match_winner_offer(self.record.commitment_json, self.record.commitment_sha256, 0)


if __name__ == "__main__":
    unittest.main()
