from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from phase0d.league import (
    MAX_CARRYOVER_FATIGUE,
    average_fatigue,
    build_schedule,
    load_league,
    new_league,
    render_league_markdown,
    render_markdown,
    save_league,
    simulate_next_season,
    simulate_season,
)


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

    def test_fatigue_is_bounded_and_recovers_between_games(self) -> None:
        season = simulate_season(6, 800)
        first, second = season.games[:2]
        self.assertEqual(average_fatigue(first.pregame_fatigue), 0.0)
        self.assertGreater(average_fatigue(first.postgame_fatigue), 0.0)
        self.assertLess(average_fatigue(second.pregame_fatigue), average_fatigue(first.postgame_fatigue))
        self.assertGreater(average_fatigue(second.pregame_fatigue), 0.0)
        self.assertTrue(
            all(0 <= value <= MAX_CARRYOVER_FATIGUE for game in season.games for _, value in game.postgame_fatigue)
        )

    def test_saved_league_resumes_identically(self) -> None:
        first = simulate_next_season(new_league(900), 6)
        uninterrupted = simulate_next_season(first, 6)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "league.json"
            save_league(first, path)
            loaded = load_league(path)
        self.assertEqual(first, loaded)
        self.assertEqual(uninterrupted, simulate_next_season(loaded, 6))
        self.assertIn("Multi-Season Persistence and Fatigue", render_league_markdown(uninterrupted))


if __name__ == "__main__":
    unittest.main()
