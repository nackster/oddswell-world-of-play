import unittest

from phase0a.simulator import default_teams
from phase0d.career import (
    REPLACEMENTS,
    RATING_NAMES,
    RETIREMENT_AGE,
    age_for_season,
    career_status,
    player_for_season,
    retirement_season,
    teams_for_season,
)
from phase0d.league import new_league, simulate_next_season


class CareerLifecycleTests(unittest.TestCase):
    def test_lifecycle_is_bounded_and_deterministic(self) -> None:
        self.assertEqual(teams_for_season(1), default_teams())
        for team in default_teams():
            for player in team.players:
                season_three = player_for_season(player, 3)
                self.assertLessEqual(
                    max(
                        abs(getattr(season_three, name) - getattr(player, name))
                        for name in RATING_NAMES
                    ),
                    2,
                )
                self.assertTrue(
                    all(
                        40 <= getattr(season_three, name) <= 99
                        for name in RATING_NAMES
                    )
                )
        self.assertEqual(age_for_season("Roman Voss", 3), RETIREMENT_AGE)
        self.assertEqual(retirement_season("Roman Voss"), 3)
        self.assertEqual(career_status("Roman Voss", 3), "RETIRED")
        self.assertEqual(career_status("Jalen Cross", 3), "ACTIVE")
        season_four = teams_for_season(4)
        season_four_names = {player.name for team in season_four for player in team.players}
        self.assertNotIn("Roman Voss", season_four_names)
        self.assertIn(REPLACEMENTS["Roman Voss"].name, season_four_names)
        self.assertTrue(all(len(team.players) == 6 for team in season_four))

        state = new_league(1_600)
        for season_number in range(1, 5):
            state = simulate_next_season(state, 2, teams_for_season(season_number))
        current_names = {name for name, _ in state.fatigue}
        self.assertNotIn("Roman Voss", current_names)
        self.assertIn("Soren Lake", current_names)
        self.assertEqual(len(current_names), 12)


if __name__ == "__main__":
    unittest.main()
