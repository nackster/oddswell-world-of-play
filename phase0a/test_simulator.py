import unittest

from phase0a.simulator import Action, default_teams, simulate_game, validate_action


class SimulatorTests(unittest.TestCase):
    def test_same_seed_and_tape_replay_identically(self) -> None:
        original = simulate_game(42)
        repeated = simulate_game(42)
        replayed = simulate_game(42, original.action_tape)
        self.assertEqual(original.records, repeated.records)
        self.assertEqual(original.records, replayed.records)

    def test_illegal_action_is_rejected(self) -> None:
        home, away = default_teams()
        bad_action = Action("offense", "teleport", home.players[0].name, None)
        with self.assertRaisesRegex(ValueError, "illegal offense action"):
            validate_action(bad_action, home, away, home.players[0].name)
        with self.assertRaisesRegex(ValueError, "exactly"):
            Action.from_mapping(
                {"role": "offense", "kind": "shoot_2", "actor": home.players[0].name, "target": None, "extra": True}
            )

    def test_pregame_fatigue_is_validated_and_replayable(self) -> None:
        teams = default_teams()
        fatigue = {player.name: 0.2 for team in teams for player in team.players}
        original = simulate_game(43, matchup=teams, initial_fatigue=fatigue)
        replayed = simulate_game(43, original.action_tape, matchup=teams, initial_fatigue=fatigue)
        self.assertEqual(original.records, replayed.records)
        with self.assertRaisesRegex(ValueError, "every matchup player"):
            simulate_game(43, initial_fatigue={})

    def test_temporary_readiness_is_bounded_and_replayable(self) -> None:
        teams = default_teams()
        readiness = {player.name: 0.015 for team in teams for player in team.players}
        original = simulate_game(46, matchup=teams, initial_readiness=readiness)
        replayed = simulate_game(
            46,
            original.action_tape,
            matchup=teams,
            initial_readiness=readiness,
        )
        self.assertEqual(original, replayed)
        readiness[teams[0].players[0].name] = 0.021
        with self.assertRaisesRegex(ValueError, "readiness"):
            simulate_game(46, matchup=teams, initial_readiness=readiness)

    def test_rotation_minutes_drive_workload_and_replay_exactly(self) -> None:
        teams = default_teams()
        original = simulate_game(44, matchup=teams)
        replayed = simulate_game(44, original.action_tape, matchup=teams)
        self.assertEqual(original, replayed)

        minutes = dict(original.minutes_played)
        fatigue = dict(original.final_fatigue)
        overtime = int(original.records[-1]["overtime"])
        for team in teams:
            team_minutes = sum(minutes[player.name] for player in team.players)
            self.assertAlmostEqual(team_minutes, 5 * (48 + 5 * overtime), places=2)
            reserve = team.players[5].name
            self.assertTrue(20 <= minutes[reserve] <= 28)
            self.assertTrue(all(minutes[player.name] > minutes[reserve] for player in team.players[:5]))
            self.assertLess(fatigue[reserve], max(fatigue[player.name] for player in team.players[:5]))

    def test_unavailable_player_is_excluded_and_replays_exactly(self) -> None:
        teams = default_teams()
        unavailable_player = teams[0].players[0].name
        availability = {player.name: 0 for team in teams for player in team.players}
        availability[unavailable_player] = 3
        original = simulate_game(45, matchup=teams, initial_availability=availability)
        replayed = simulate_game(
            45,
            original.action_tape,
            matchup=teams,
            initial_availability=availability,
        )
        self.assertEqual(original, replayed)
        self.assertEqual(dict(original.minutes_played)[unavailable_player], 0)
        self.assertFalse(
            any(
                unavailable_player in event.get("players", ())
                for event in original.records
                if event["type"] == "lineup_changed"
            )
        )
        with self.assertRaisesRegex(ValueError, "five available"):
            simulate_game(
                45,
                initial_availability={
                    name: (3 if index < 2 else 0)
                    for index, name in enumerate(availability)
                },
            )

    def test_one_hundred_games_finish_with_plausible_scores(self) -> None:
        scores = [simulate_game(seed) for seed in range(100)]
        points = [score for game in scores for score in (game.home_score, game.away_score)]
        self.assertTrue(all(game.home_score != game.away_score for game in scores))
        self.assertGreater(sum(points) / len(points), 65)
        self.assertLess(sum(points) / len(points), 145)


if __name__ == "__main__":
    unittest.main()
