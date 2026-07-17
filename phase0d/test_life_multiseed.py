import time
import unittest

from phase0d.league import STATE_SCHEMA
from phase0d.life import LIFE_BRAIN_V1_VERSION, LIFE_BRAIN_V2_VERSION
from phase0d.life_multiseed import (
    LIFE_MULTISEED_VERSION,
    SEED_BLOCKS,
    run_life_multiseed_evaluation,
)


class LifeMultiSeedEvaluationTests(unittest.TestCase):
    def test_multiseed_evaluation_is_reproducible_bounded_and_non_promoting(self) -> None:
        started = time.perf_counter()
        result = run_life_multiseed_evaluation()
        self.assertLess(time.perf_counter() - started, 60)
        self.assertIs(result, run_life_multiseed_evaluation())
        self.assertEqual(result.version, LIFE_MULTISEED_VERSION)
        self.assertEqual(result.state_schema, STATE_SCHEMA)
        self.assertEqual(result.seed_blocks, SEED_BLOCKS)
        self.assertEqual(result.games_per_policy, 800)
        self.assertEqual((result.v1.decisions, result.v2.decisions), (9_120, 9_120))
        self.assertEqual(result.v1.policy_version, LIFE_BRAIN_V1_VERSION)
        self.assertEqual(result.v2.policy_version, LIFE_BRAIN_V2_VERSION)
        self.assertTrue(all(block.v1.decisions == block.v2.decisions == 912 for block in result.blocks))
        self.assertEqual(result.failures, ())
        self.assertEqual(result.promotion_status, "ELIGIBLE FOR LATER REVIEW")
        self.assertNotEqual(result.promotion_status, "PROMOTED")
        self.assertEqual(
            result.sha256,
            "0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588",
        )
        groups = {group.preference: group for group in result.v2.preferences}
        self.assertEqual((groups["practice"].decisions, groups["social"].decisions), (4_560, 4_560))
        self.assertNotIn("socialize", dict(groups["practice"].choice_counts))
        self.assertNotIn("train", dict(groups["social"].choice_counts))
        self.assertLessEqual(max(result.v1.max_readiness, result.v2.max_readiness), 0.015)
        self.assertEqual(result.v1.zero_minute_absences, result.v1.missed_player_games)
        self.assertEqual(result.v2.zero_minute_absences, result.v2.missed_player_games)


if __name__ == "__main__":
    unittest.main()
