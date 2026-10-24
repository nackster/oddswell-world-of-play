from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest

from phase0d.career import teams_for_season
from phase0d.league import load_league, new_league, save_league, simulate_next_season
from phase0d.life import (
    DEFAULT_LIFE_BRAIN_VERSION,
    LIFE_BRAIN_V3_VERSION,
    LIFE_BRAIN_V4_VERSION,
    apply_life_action,
    choose_life_action,
    recent_scoring_form,
)
from phase0d.life_performance import (
    LIFE_PERFORMANCE_VERSION,
    SEED_BLOCKS,
    run_life_performance_evaluation,
)


class LifePerformanceTests(unittest.TestCase):
    def test_v4_is_chronology_safe_and_resumable(self) -> None:
        self.assertEqual(DEFAULT_LIFE_BRAIN_VERSION, LIFE_BRAIN_V4_VERSION)
        self.assertEqual(recent_scoring_form(((8, 30.0), (10, 30.0), (12, 30.0))), "typical")
        self.assertEqual(
            recent_scoring_form(((8, 30.0), (10, 30.0), (12, 30.0), (13, 30.0))),
            "above",
        )
        self.assertEqual(
            recent_scoring_form(((8, 30.0), (10, 30.0), (12, 30.0), (12, 30.0))),
            "typical",
        )
        self.assertEqual(
            recent_scoring_form(((8, 30.0), (10, 30.0), (12, 30.0), (7, 30.0))),
            "below",
        )
        self.assertEqual(
            recent_scoring_form(((8, 30.0), (10, 30.0), (12, 30.0), (8, 30.0))),
            "typical",
        )
        self.assertEqual(
            recent_scoring_form(((8, 30.0), (10, 30.0), (12, 30.0), (14, 0.0))),
            "typical",
        )
        self.assertEqual(
            choose_life_action(
                "Micah Vale", 5, 1, 0.1, 0,
                policy_version=LIFE_BRAIN_V4_VERSION,
                recent_scoring_form="below",
            ),
            "train",
        )
        self.assertEqual(
            choose_life_action(
                "Jalen Cross", 5, 0, 0.1, 0,
                policy_version=LIFE_BRAIN_V4_VERSION,
                recent_scoring_form="above",
            ),
            "socialize",
        )
        self.assertEqual(
            choose_life_action(
                "Jalen Cross", 5, 0, 0.1, 0,
                policy_version=LIFE_BRAIN_V4_VERSION,
                routine_streak=2,
                recent_scoring_form="below",
            ),
            "socialize",
        )
        self.assertEqual(
            apply_life_action(
                "Micah Vale", 5, "train", 0.1, 0,
                policy_version=LIFE_BRAIN_V4_VERSION,
                recent_scoring_form="below",
            ).reason,
            "Recent scoring below earlier same-season average",
        )
        with self.assertRaisesRegex(ValueError, "v4-only"):
            choose_life_action(
                "Jalen Cross", 5, 0, 0.1, 0,
                policy_version=LIFE_BRAIN_V3_VERSION,
                recent_scoring_form="above",
            )

        state = simulate_next_season(
            new_league(2_000), 8, teams_for_season(1),
            life_policy_version=LIFE_BRAIN_V4_VERSION,
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "v4.json"
            save_league(state, path)
            loaded = load_league(path)
        self.assertEqual(state, loaded)
        self.assertEqual(
            simulate_next_season(
                state, 4, teams_for_season(2),
                life_policy_version=LIFE_BRAIN_V4_VERSION,
            ),
            simulate_next_season(
                loaded, 4, teams_for_season(2),
                life_policy_version=LIFE_BRAIN_V4_VERSION,
            ),
        )

    def test_paired_evaluation_is_reproducible_bounded_and_non_promoting(self) -> None:
        started = time.perf_counter()
        result = run_life_performance_evaluation()
        self.assertLess(time.perf_counter() - started, 120)
        self.assertIs(result, run_life_performance_evaluation())
        self.assertEqual(result.version, LIFE_PERFORMANCE_VERSION)
        self.assertEqual(result.seed_blocks, SEED_BLOCKS)
        self.assertEqual(result.games_per_policy, 800)
        self.assertEqual(result.v3.decisions, 9_120)
        self.assertEqual(result.v4.decisions, 9_120)
        self.assertEqual(result.performance.decisions, 9_120)
        self.assertEqual(result.performance.violations, 0)
        self.assertEqual(result.performance.covered_decisions, 7_564)
        self.assertEqual(result.performance.response_opportunities, 2_089)
        self.assertEqual(result.performance.responses, 2_089)
        self.assertLessEqual(result.performance.max_elective_run, 2)
        self.assertEqual(result.failures, ())
        self.assertEqual(result.promotion_status, "ELIGIBLE FOR LATER REVIEW")
        self.assertNotEqual(result.promotion_status, "PROMOTED")
        self.assertEqual(
            result.sha256,
            "a7b61128668fce26c392a52fac4425324ec41fdfead3b261e57535ff83fc4f60",
        )


if __name__ == "__main__":
    unittest.main()
