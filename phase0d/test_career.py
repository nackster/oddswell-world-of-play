import unittest

from phase0a.simulator import default_teams
from phase0d.career import (
    RATING_NAMES,
    RETIREMENT_AGE,
    age_for_season,
    career_status,
    player_for_season,
    retirement_season,
    teams_for_season,
)


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
        with self.assertRaisesRegex(ValueError, "retired after season 3"):
            teams_for_season(4)


if __name__ == "__main__":
    unittest.main()
