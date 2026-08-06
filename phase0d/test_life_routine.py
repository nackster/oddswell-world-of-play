import time
import unittest

from phase0d.life import (
    DEFAULT_LIFE_BRAIN_VERSION,
    LIFE_BRAIN_V2_VERSION,
    LIFE_BRAIN_V3_VERSION,
    LIFE_BRAIN_V4_VERSION,
)
from phase0d.league import LEGACY_STATE_SCHEMA
from phase0d.life_routine import (
    LIFE_ROUTINE_VERSION,
    SEED_BLOCKS,
    run_life_routine_evaluation,
)


class LifeRoutineEvaluationTests(unittest.TestCase):
    def test_routine_evaluation_is_reproducible_bounded_and_non_promoting(self) -> None:
        started = time.perf_counter()
        result = run_life_routine_evaluation()
        self.assertLess(time.perf_counter() - started, 60)
        self.assertIs(result, run_life_routine_evaluation())
        self.assertEqual(DEFAULT_LIFE_BRAIN_VERSION, LIFE_BRAIN_V4_VERSION)
        self.assertEqual(result.version, LIFE_ROUTINE_VERSION)
        self.assertEqual(result.state_schema, LEGACY_STATE_SCHEMA)
        self.assertEqual(result.seed_blocks, SEED_BLOCKS)
        self.assertEqual(result.games_per_policy, 800)
        self.assertEqual(result.v2.policy_version, LIFE_BRAIN_V2_VERSION)
        self.assertEqual(result.v3.policy_version, LIFE_BRAIN_V3_VERSION)
        self.assertEqual(result.v2.decisions, 9_120)
        self.assertEqual(result.v3.decisions, 9_120)
        self.assertEqual(result.routine.decisions, 9_120)
        self.assertEqual(result.routine.violations, 0)
        self.assertLessEqual(result.routine.max_abs_streak, 2)
        self.assertLessEqual(result.routine.max_elective_run, 2)
        groups = {group.preference: group for group in result.routine.groups}
        self.assertLessEqual(
            abs(groups["practice"].variation_rate - groups["social"].variation_rate),
            0.05,
        )
        self.assertEqual(result.failures, ())
        self.assertEqual(result.promotion_status, "ELIGIBLE FOR LATER REVIEW")
        self.assertNotEqual(result.promotion_status, "PROMOTED")
        self.assertEqual(
            result.sha256,
            "eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618",
        )


if __name__ == "__main__":
    unittest.main()
