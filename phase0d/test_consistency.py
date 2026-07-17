import unittest

from phase0a.simulator import default_teams
from phase0d.consistency import (
    ATHLETE_CONSISTENCY,
    CONSISTENCY_SPREAD,
    CONSISTENCY_VERSION,
    calibrate_consistency,
    consistency_tier,
    evaluate_consistency,
    game_form,
)


class AthleteConsistencyTests(unittest.TestCase):
    def test_consistency_pilot_is_rare_bounded_and_replayable(self) -> None:
        players = [player.name for team in default_teams() for player in team.players]
        self.assertTrue(all(player in ATHLETE_CONSISTENCY for player in players))
        self.assertEqual(sum(consistency_tier(player) == "elite" for player in players), 1)

        first = game_form(60_000)
        self.assertEqual(first, game_form(60_000))
        self.assertTrue(
            all(
                abs(first[player]) <= CONSISTENCY_SPREAD[consistency_tier(player)]
                for player in players
            )
        )

        result = evaluate_consistency(80)
        self.assertEqual(result, evaluate_consistency(80))
        self.assertEqual(result["version"], CONSISTENCY_VERSION)
        self.assertEqual(result["games"], 80)
        self.assertEqual(result["tier_counts"], {
            "steady": 4,
            "normal": 5,
            "volatile": 2,
            "elite": 1,
        })
        self.assertEqual(result["replay_violations"], 0)
        self.assertEqual(result["score_differences"], 47)
        self.assertEqual(result["winner_differences"], 12)
        self.assertEqual(result["mean_absolute_team_score_difference"], 4.2062)
        form = result["mean_absolute_form"]
        self.assertLess(form["elite"], form["steady"])
        self.assertLess(form["steady"], form["normal"])
        self.assertLess(form["normal"], form["volatile"])
        self.assertTrue(
            all(
                result["max_absolute_form"][tier] <= spread
                for tier, spread in CONSISTENCY_SPREAD.items()
            )
        )

    def test_unknown_player_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing game consistency"):
            consistency_tier("Unknown Athlete")

    def test_same_athlete_calibration_blocks_promotion(self) -> None:
        result = calibrate_consistency(100)
        self.assertEqual(result, calibrate_consistency(100))
        self.assertFalse(result["eligible_for_rollout"])
        self.assertEqual(result["replay_violations"], 0)
        self.assertEqual(result["failures"], [
            "elite point-deviation reduction",
            "elite bad-night reduction",
            "elite performance floor",
        ])


if __name__ == "__main__":
    unittest.main()
