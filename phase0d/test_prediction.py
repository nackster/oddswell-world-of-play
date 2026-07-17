from dataclasses import replace
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from phase0a.simulator import default_teams
from phase0d.league import (
    OFFSEASON_REST_DAYS,
    availability_snapshot,
    build_schedule,
    empty_availability,
    empty_fatigue,
    load_league,
    new_league,
    recover_availability,
    save_league,
    simulate_next_season,
    simulate_scheduled_game,
)
from phase0d.prediction import (
    MODEL_NAMES,
    _metrics,
    canonical_json,
    prediction_probabilities,
    public_pregame_snapshot,
    run_prediction_study,
    verify_prediction_record,
)
from phase0d.life import LIFE_BRAIN_V1_VERSION


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

    def test_historical_study_defaults_explicitly_to_v1(self) -> None:
        default = run_prediction_study(0, 1, 4, 701)
        explicit = run_prediction_study(
            0,
            1,
            4,
            701,
            life_policy_version=LIFE_BRAIN_V1_VERSION,
        )
        self.assertEqual(default, explicit)

    def test_commitment_is_created_before_each_authoritative_game(self) -> None:
        events = []

        def record_commitment(value):
            events.append("commitment")
            return canonical_json(value)

        def record_game(*args, **kwargs):
            events.append("game")
            return simulate_scheduled_game(*args, **kwargs)

        with patch("phase0d.prediction.canonical_json", side_effect=record_commitment), patch(
            "phase0d.prediction.simulate_scheduled_game", side_effect=record_game
        ):
            run_prediction_study(0, 1, 4, 702)

        self.assertEqual(events, ["commitment", "game"] * 4)

    def test_metrics_match_fixed_formulas(self) -> None:
        template = run_prediction_study(0, 1, 4, 703).records[0]
        snapshot = json.loads(template.commitment_json)["snapshot"]
        pairs = ((0.1, 0), (0.3, 0), (0.7, 1), (0.9, 1))
        records = tuple(
            replace(
                template,
                predictions=tuple((model, probability) for model in MODEL_NAMES),
                home_win=outcome,
                winner=snapshot["home_team"] if outcome else snapshot["away_team"],
            )
            for probability, outcome in pairs
        )

        metrics = _metrics(records, "public_elo", 0.25)
        self.assertEqual(metrics.accuracy, 1.0)
        self.assertAlmostEqual(metrics.brier, 0.05)
        self.assertAlmostEqual(
            metrics.log_loss,
            -(2 * math.log(0.9) + 2 * math.log(0.7)) / 4,
        )
        self.assertAlmostEqual(metrics.ece, 0.2)
        self.assertAlmostEqual(metrics.brier_skill, 0.8)

    def test_saved_public_state_resumes_with_identical_prediction(self) -> None:
        teams = default_teams()
        state = simulate_next_season(new_league(704), 4)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "league.json"
            save_league(state, path)
            loaded = load_league(path)

        fixture = build_schedule(4, state.next_seed, teams)[0]

        def next_prediction(source):
            availability = recover_availability(
                source.availability, OFFSEASON_REST_DAYS, teams
            )
            snapshot = public_pregame_snapshot(
                source.next_season,
                fixture,
                {team.name: (0, 0) for team in teams},
                availability,
                OFFSEASON_REST_DAYS,
                teams,
            )
            return canonical_json(snapshot), prediction_probabilities(
                snapshot, {team.name: 1500.0 for team in teams}
            )

        self.assertEqual(next_prediction(state), next_prediction(loaded))

    def test_outcomes_and_replay_hashes_link_to_authoritative_games(self) -> None:
        study = run_prediction_study(0, 1, 4, 705)
        first = study.records[0]
        teams = default_teams()
        game = simulate_scheduled_game(
            build_schedule(4, 705, teams)[0],
            empty_fatigue(teams),
            empty_availability(teams),
            teams,
            life_policy_version=LIFE_BRAIN_V1_VERSION,
        )
        self.assertEqual((first.winner, first.replay_sha256), (game.winner, game.replay_sha256))
        self.assertFalse(verify_prediction_record(replace(first, replay_sha256="tampered")))

    def test_invalid_study_sizes_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_prediction_study(-1, 1, 4)
        with self.assertRaises(ValueError):
            run_prediction_study(1, 0, 4)
        with self.assertRaises(ValueError):
            run_prediction_study(1, 1, 3)


if __name__ == "__main__":
    unittest.main()
