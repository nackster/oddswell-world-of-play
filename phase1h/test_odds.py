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
from phase1h.execution import (
    active_game_execution_commitment,
    dry_simulation_manifest_hash,
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

        schedule = {
            "schema": "oddswell-canonical-scheduled-game-v1",
            "record_version": 1,
            "season_number": 1,
            "game_number": 1,
            "home_team": "Harbor City Waves",
            "away_team": "Mesa Vista Sol",
            "season_created_unix": 2_200_000_000,
            "tipoff_unix": 2_200_001_800,
            "offer_eligible_unix": 2_200_000_000,
            "status": "scheduled_unplayed",
            "environment": "local_beta",
            "timing_authority": "server",
            "production_timing": False,
            "offer_published": False,
        }
        execution = active_game_execution_commitment(
            schedule, self.record.commitment_sha256
        )
        self.assertEqual(
            execution,
            active_game_execution_commitment(
                dict(schedule), self.record.commitment_sha256
            ),
        )
        self.assertEqual(
            execution.seed_material_sha256,
            "0ee3e752bb9014911c7a535d08cf4fdb0c05f745a0d0ada28bb774a7fd19209b",
        )
        self.assertEqual(execution.execution_seed, 249_816_914)
        self.assertEqual(
            execution.execution_input_sha256,
            "b679a5269440bc53caed60d8c71b31e25ff076b14b0229d9a5739463f4ae9230",
        )
        self.assertEqual(
            execution.commitment_sha256,
            "c559694689831056b34c737e0dc2ac050635d3c424c8078032b6a47794a334f1",
        )
        self.assertEqual(
            dry_simulation_manifest_hash(execution),
            "251bf492d7bc167f0a6cc7ad554f9147765b327a2723740abe6ac5c31c9be185",
        )
        private_input = execution.execution_input_json.lower()
        for forbidden in (
            "offer_id",
            "request",
            "selection",
            "stake",
            "balance",
            "odds",
            "ledger",
            "lock_command",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, private_input)

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
        schedule = {
            "schema": "oddswell-canonical-scheduled-game-v1",
            "record_version": 1,
            "season_number": 1,
            "game_number": 1,
            "home_team": "Harbor City Waves",
            "away_team": "Mesa Vista Sol",
            "season_created_unix": 2_200_000_000,
            "tipoff_unix": 2_200_001_800,
            "offer_eligible_unix": 2_200_000_000,
            "status": "scheduled_unplayed",
            "environment": "local_beta",
            "timing_authority": "server",
            "production_timing": False,
            "offer_published": False,
        }
        for field, value in (
            ("tipoff_unix", 2_200_001_801),
            ("home_team", "Wrong Team"),
            ("record_version", 0),
            ("offer_published", True),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                active_game_execution_commitment(
                    {**schedule, field: value}, self.record.commitment_sha256
                )
        with self.assertRaises(ValueError):
            active_game_execution_commitment(schedule, "0" * 63)


if __name__ == "__main__":
    unittest.main()
