import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from phase0a.simulator import BRAIN_VERSION, default_teams, simulate_game
from phase0c.replay import replay_manifest, verify_replay_manifest
from phase0d.league import (
    MAX_INJURY_RISK,
    add_minor_injuries,
    MAX_CARRYOVER_FATIGUE,
    availability_metrics,
    average_fatigue,
    build_schedule,
    empty_availability,
    empty_fatigue,
    injury_risk,
    load_league,
    minutes_snapshot,
    new_league,
    recover_availability,
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

    def test_actual_minutes_create_different_carryover_loads(self) -> None:
        season = simulate_season(2, 850)
        game = season.games[0]
        minutes = dict(game.minutes_played)
        fatigue = dict(game.postgame_fatigue)
        fixture = build_schedule(2, 850)[0]
        for team in (fixture.home, fixture.away):
            reserve = team.players[5].name
            self.assertAlmostEqual(sum(minutes[player.name] for player in team.players), 240, places=2)
            self.assertLess(minutes[reserve], min(minutes[player.name] for player in team.players[:5]))
            self.assertLess(fatigue[reserve], max(fatigue[player.name] for player in team.players[:5]))

    def test_saved_league_resumes_identically(self) -> None:
        first = simulate_next_season(new_league(900), 6)
        uninterrupted = simulate_next_season(first, 6)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "league.json"
            save_league(first, path)
            loaded = load_league(path)
        self.assertEqual(first, loaded)
        self.assertEqual(uninterrupted, simulate_next_season(loaded, 6))
        self.assertIn("Availability and Recovery", render_league_markdown(uninterrupted))

    def test_injury_risk_is_minutes_linked_monotonic_and_bounded(self) -> None:
        self.assertEqual(injury_risk(0, 0.35), 0)
        low = injury_risk(24, 0.1)
        self.assertGreater(injury_risk(42, 0.1), low)
        self.assertGreater(injury_risk(24, 0.3), low)
        self.assertEqual(injury_risk(100, 1), MAX_INJURY_RISK)

    def test_injury_roll_has_a_five_player_floor_and_recovery(self) -> None:
        teams = default_teams()
        availability = dict(empty_availability(teams))
        for team in teams:
            availability[team.players[0].name] = 7
        starting = tuple((player.name, availability[player.name]) for team in teams for player in team.players)
        minutes = minutes_snapshot(
            {player.name: 48 for team in teams for player in team.players},
            teams,
        )
        after = add_minor_injuries(starting, empty_fatigue(teams), minutes, teams, 1)
        self.assertEqual(after, starting)
        recovered = recover_availability(after, 7, teams)
        self.assertTrue(all(days == 0 for _, days in recovered))

    def test_fixed_seed_injury_rate_stays_inside_provisional_bound(self) -> None:
        teams = default_teams()
        availability = empty_availability(teams)
        fatigue = tuple((player.name, 0.25) for team in teams for player in team.players)
        minutes = minutes_snapshot(
            {
                player.name: (43.2 if index < 5 else 24)
                for team in teams
                for index, player in enumerate(team.players)
            },
            teams,
        )
        injuries = 0
        starter_injuries = 0
        for seed in range(1_000):
            after = dict(add_minor_injuries(availability, fatigue, minutes, teams, seed))
            injuries += sum(days > 0 for days in after.values())
            starter_injuries += sum(
                after[player.name] > 0 for team in teams for player in team.players[:5]
            )
        rate = injuries / (1_000 * 12)
        self.assertTrue(0.005 <= rate <= MAX_INJURY_RISK)
        self.assertGreater(starter_injuries / 10_000, (injuries - starter_injuries) / 2_000)

    def test_availability_audit_is_hashed_and_reported(self) -> None:
        teams = default_teams()
        availability = dict(empty_availability(teams))
        unavailable_player = teams[0].players[0].name
        availability[unavailable_player] = 2
        game = simulate_game(1_234, matchup=teams, initial_availability=availability)
        audit = {
            "minutes_played": dict(game.minutes_played),
            "pregame_availability": availability,
            "postgame_availability": availability,
        }
        manifest = replay_manifest(game, teams, BRAIN_VERSION, audit)
        self.assertTrue(verify_replay_manifest(manifest))
        tampered = copy.deepcopy(manifest)
        tampered["payload"]["audit"]["postgame_availability"][unavailable_player] = 0
        self.assertFalse(verify_replay_manifest(tampered))

        state = simulate_next_season(new_league(1_300), 6)
        metrics = availability_metrics(state)
        self.assertEqual(metrics["zero_minute_absences"], metrics["missed_player_games"])
        self.assertGreaterEqual(metrics["minimum_available"], 5)


if __name__ == "__main__":
    unittest.main()
