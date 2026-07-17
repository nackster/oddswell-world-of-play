import unittest

from phase0d.life_evaluation import (
    LIFE_EVALUATION_VERSION,
    run_life_evaluation,
    run_life_v2_pilot,
)
from phase0d.life import (
    DEFAULT_LIFE_BRAIN_VERSION,
    LIFE_BRAIN_V1_VERSION,
    LIFE_BRAIN_V2_VERSION,
)


class AthleteLifeEvaluationTests(unittest.TestCase):
    def test_fixed_archive_evaluation_is_exact_and_bounded(self) -> None:
        first = run_life_evaluation()
        self.assertIs(first, run_life_evaluation())
        self.assertEqual(first.version, LIFE_EVALUATION_VERSION)
        self.assertEqual(DEFAULT_LIFE_BRAIN_VERSION, LIFE_BRAIN_V2_VERSION)
        self.assertEqual(first.policy_version, LIFE_BRAIN_V1_VERSION)
        self.assertEqual((first.seasons, first.games), (4, 80))
        self.assertEqual(first.decisions, first.expected_decisions)
        self.assertEqual(dict(first.choice_counts), {
            "recover": 23,
            "rest": 386,
            "socialize": 252,
            "train": 251,
        })
        self.assertEqual(first.policy_violations, 0)
        self.assertEqual(first.tenure_violations, 0)
        self.assertEqual(first.reconstructed_games, 80)
        self.assertEqual(first.readiness_exposures, 503)
        self.assertEqual(first.readiness_exposure_rate, 0.5515)
        self.assertEqual(first.mean_readiness, 0.006891)
        self.assertEqual(first.mean_active_readiness, 0.012495)
        self.assertEqual(first.max_readiness, 0.015)
        self.assertEqual(first.net_fatigue_change, -4.04)
        self.assertEqual(first.recovery_days_saved, 23)
        self.assertEqual(first.point_change_per_team, 1.4125)
        self.assertEqual(first.field_goal_percentage_point_change, 0.6654)
        self.assertEqual(first.turnover_change_per_team_game, -0.275)
        self.assertEqual(first.winner_flips, 22)
        self.assertEqual(first.mean_absolute_margin_change, 6.275)
        self.assertEqual(dict(first.choices_by_athlete)["Roman Voss"], 57)
        self.assertEqual(dict(first.choices_by_athlete)["Soren Lake"], 19)

    def test_preference_pilot_is_fresh_versioned_and_directional(self) -> None:
        pilot = run_life_v2_pilot()
        self.assertIs(pilot, run_life_v2_pilot())
        self.assertEqual(pilot.policy_version, LIFE_BRAIN_V2_VERSION)
        self.assertEqual((pilot.seasons, pilot.games, pilot.decisions), (4, 80, 912))
        self.assertEqual(pilot.policy_violations, 0)
        self.assertEqual(pilot.tenure_violations, 0)
        self.assertEqual(pilot.reconstructed_games, 80)
        by_preference = {
            preference: dict(counts)
            for preference, counts in pilot.choices_by_preference
        }
        self.assertNotIn("socialize", by_preference["practice"])
        self.assertNotIn("train", by_preference["social"])
        self.assertEqual(sum(by_preference["practice"].values()), 456)
        self.assertEqual(sum(by_preference["social"].values()), 456)


if __name__ == "__main__":
    unittest.main()
