import unittest

from phase0a.simulator import default_teams, simulate_game
from phase0d.involvement import (
    OFFENSIVE_INVOLVEMENT_VERSION,
    OFFENSIVE_INVOLVEMENT_WEIGHTS,
    evaluate_offensive_involvement,
    involvement_settings,
    involvement_snapshot,
)


class OffensiveInvolvementTests(unittest.TestCase):
    def test_snapshot_is_bounded_explicit_and_validated(self) -> None:
        snapshot = involvement_snapshot("Jalen Cross", "featured")
        self.assertEqual(dict((name, weight) for name, _, weight in snapshot)["Jalen Cross"], 1.15)
        self.assertEqual(set(OFFENSIVE_INVOLVEMENT_WEIGHTS), {"low", "standard", "featured"})
        self.assertTrue(all(0.85 <= weight <= 1.15 for _, _, weight in snapshot))
        with self.assertRaisesRegex(ValueError, "unknown offensive involvement tier"):
            involvement_snapshot("Jalen Cross", "star")
        with self.assertRaisesRegex(ValueError, "tier and weight"):
            involvement_settings((("Jalen Cross", "featured", 1.0),))

    def test_omission_preserves_current_game_and_opt_in_replays_exactly(self) -> None:
        teams = default_teams()
        current = simulate_game(76_000, matchup=teams)
        self.assertEqual(current, simulate_game(76_000, matchup=teams))
        settings = involvement_settings(involvement_snapshot("Jalen Cross", "featured", teams))
        pilot = simulate_game(76_000, matchup=teams, initial_offensive_involvement=settings)
        replay = simulate_game(
            76_000,
            pilot.action_tape,
            matchup=teams,
            initial_offensive_involvement=settings,
        )
        self.assertEqual(pilot, replay)
        self.assertNotIn("pregame_offensive_involvement", current.records[0])
        self.assertEqual(pilot.records[0]["pregame_offensive_involvement"], settings)
        with self.assertRaisesRegex(ValueError, "every matchup player"):
            simulate_game(76_000, initial_offensive_involvement={})
        with self.assertRaisesRegex(ValueError, "baseline decision policy"):
            simulate_game(
                76_000,
                initial_offensive_involvement=settings,
                decision_policy=lambda *args: None,
            )

    def test_paired_pilot_is_ordered_and_replayable(self) -> None:
        result = evaluate_offensive_involvement(40)
        self.assertEqual(result["version"], OFFENSIVE_INVOLVEMENT_VERSION)
        self.assertEqual(result["scope"], "OPPORTUNITY ONLY")
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["replay_violations"], 0)
        opportunities = [
            result["tiers"][tier]["mean_selection_opportunities"]
            for tier in ("low", "standard", "featured")
        ]
        self.assertLess(opportunities[0], opportunities[1])
        self.assertLess(opportunities[1], opportunities[2])


if __name__ == "__main__":
    unittest.main()
