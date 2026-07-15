from dataclasses import replace
import json
import unittest

from phase0a.simulator import default_teams
from phase0d.league import availability_snapshot, build_schedule, empty_availability
from phase0d.prediction import (
    MODEL_NAMES,
    prediction_probabilities,
    public_pregame_snapshot,
    run_prediction_study,
    verify_prediction_record,
)


class PredictionTests(unittest.TestCase):
    def test_public_snapshot_excludes_hidden_and_future_data(self) -> None:
        teams = default_teams()
        snapshot = public_pregame_snapshot(
            1,
            build_schedule(2, 500, teams)[0],
            {team.name: (0, 0) for team in teams},
            empty_availability(teams),
            7,
            teams,
        )
        self.assertEqual(
            set(snapshot),
            {
                "version",
                "season_number",
                "game_number",
                "home_team",
                "away_team",
                "standings",
                "rest_days",
                "rosters",
            },
        )
        encoded = json.dumps(snapshot).lower()
        for forbidden in ("seed", "rng", "fatigue", "score", "winner", "replay", "economy", "user"):
            with self.subTest(forbidden):
                self.assertNotIn(forbidden, encoded)
        for players in snapshot["rosters"].values():
            self.assertAlmostEqual(sum(player["projected_minutes"] for player in players), 240)

    def test_public_availability_changes_only_the_adjusted_model(self) -> None:
        teams = default_teams()
        fixture = build_schedule(2, 501, teams)[0]
        standings = {team.name: (0, 0) for team in teams}
        healthy = public_pregame_snapshot(
            1, fixture, standings, empty_availability(teams), 7, teams
        )
        recovery = dict(empty_availability(teams))
        recovery[fixture.home.players[0].name] = 2
        limited = public_pregame_snapshot(
            1,
            fixture,
            standings,
            availability_snapshot(recovery, teams),
            7,
            teams,
        )
        elo = {team.name: 1500.0 for team in teams}
        healthy_probabilities = dict(prediction_probabilities(healthy, elo))
        limited_probabilities = dict(prediction_probabilities(limited, elo))
        self.assertEqual(healthy_probabilities["coin"], limited_probabilities["coin"])
        self.assertEqual(healthy_probabilities["public_elo"], limited_probabilities["public_elo"])
        self.assertLess(
            limited_probabilities["public_elo_rotation"],
            healthy_probabilities["public_elo_rotation"],
        )

    def test_study_is_chronological_deterministic_and_tamper_evident(self) -> None:
        first = run_prediction_study(1, 1, 4, 700)
        second = run_prediction_study(1, 1, 4, 700)
        self.assertEqual(first, second)
        self.assertEqual(len(first.records), 8)
        self.assertTrue(all(verify_prediction_record(record) for record in first.records))
        self.assertEqual([metric.model for metric in first.metrics], list(MODEL_NAMES))
        self.assertTrue(all(metric.games == 4 for metric in first.metrics))
        self.assertEqual(first.metrics[0].brier, 0.25)
        self.assertEqual(first.metrics[0].brier_skill, 0.0)

        first_snapshot = json.loads(first.records[0].commitment_json)["snapshot"]
        second_snapshot = json.loads(first.records[1].commitment_json)["snapshot"]
        self.assertTrue(all(row["games"] == 0 for row in first_snapshot["standings"]))
        self.assertEqual(sum(row["games"] for row in second_snapshot["standings"]), 2)
        self.assertFalse(
            verify_prediction_record(
                replace(first.records[-1], commitment_json=first.records[-1].commitment_json + " ")
            )
        )

    def test_invalid_study_sizes_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_prediction_study(-1, 1, 4)
        with self.assertRaises(ValueError):
            run_prediction_study(1, 0, 4)
        with self.assertRaises(ValueError):
            run_prediction_study(1, 1, 3)


if __name__ == "__main__":
    unittest.main()
