import unittest

from phase0b.analyze import analyze_games, render_markdown


class AnalysisTests(unittest.TestCase):
    def test_analysis_is_reproducible_and_complete(self) -> None:
        first = analyze_games(25, 100)
        second = analyze_games(25, 100)
        self.assertEqual(first, second)
        self.assertEqual(len(first.teams), 2)
        self.assertEqual(len(first.players), 12)
        self.assertTrue(150 < first.overall["possessions_per_game"] < 260)
        self.assertEqual(sum(team["wins"] for team in first.teams.values()), 25)
        for team_name, team in first.teams.items():
            player_points = sum(
                player["points_per_game"] for player in first.players if player["team"] == team_name
            )
            self.assertAlmostEqual(player_points, team["points_per_game"])
        self.assertIn("Phase 0B Baseline Report", render_markdown(first))

    def test_game_count_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            analyze_games(0)


if __name__ == "__main__":
    unittest.main()
