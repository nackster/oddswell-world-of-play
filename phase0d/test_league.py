import unittest

from phase0d.league import build_schedule, render_markdown, simulate_season


class LeagueTests(unittest.TestCase):
    def test_schedule_is_balanced_and_seeded(self) -> None:
        schedule = build_schedule(6, 500)
        self.assertEqual([game.seed for game in schedule], list(range(500, 506)))
        self.assertEqual(schedule[0].home, schedule[1].away)
        self.assertEqual(schedule[0].away, schedule[1].home)
        self.assertEqual(len({game.home.name for game in schedule}), 2)
        for game_count in (0, 1, 3):
            with self.subTest(game_count):
                with self.assertRaisesRegex(ValueError, "positive even"):
                    build_schedule(game_count)

    def test_season_and_standings_are_reproducible(self) -> None:
        first = simulate_season(6, 700)
        second = simulate_season(6, 700)
        self.assertEqual(first, second)
        self.assertEqual(sum(row.wins for row in first.standings), 6)
        self.assertEqual(sum(row.losses for row in first.standings), 6)
        self.assertTrue(all(row.games == 6 for row in first.standings))
        self.assertEqual(
            sum(row.points_for for row in first.standings),
            sum(row.points_against for row in first.standings),
        )
        self.assertTrue(all(len(game.replay_sha256) == 64 for game in first.games))
        self.assertIn("Phase 0D Schedule and Standings", render_markdown(first))


if __name__ == "__main__":
    unittest.main()
