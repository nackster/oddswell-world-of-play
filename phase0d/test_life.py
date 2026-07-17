from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from phase0a.simulator import default_teams, simulate_game
from phase0d.career import teams_for_season
from phase0d.league import (
    build_schedule,
    empty_availability,
    empty_fatigue,
    load_league,
    new_league,
    save_league,
    simulate_scheduled_game,
    simulate_next_season,
    simulate_season,
)
from phase0d.life import (
    DEFAULT_LIFE_BRAIN_VERSION,
    LIFE_BRAIN_V1_VERSION,
    LIFE_BRAIN_V2_VERSION,
    LIFE_BRAIN_V3_VERSION,
    LIFE_BRAIN_V4_VERSION,
    OFF_DAY_PREFERENCES,
    apply_life_action,
    between_game_choices,
    choose_life_action,
    next_routine_streak,
)


class AthleteLifeBrainTests(unittest.TestCase):
    def test_routine_memory_is_opt_in_bounded_and_season_local(self) -> None:
        self.assertEqual(DEFAULT_LIFE_BRAIN_VERSION, LIFE_BRAIN_V4_VERSION)
        self.assertEqual(
            next_routine_streak(next_routine_streak(0, "train"), "train"),
            2,
        )
        self.assertEqual(next_routine_streak(2, "socialize"), -1)
        self.assertEqual(next_routine_streak(-2, "train"), 1)
        self.assertEqual(next_routine_streak(2, "rest"), 0)
        for invalid in (True, 3):
            with self.assertRaisesRegex(ValueError, "routine streak"):
                next_routine_streak(invalid, "train")

        self.assertEqual(
            choose_life_action(
                "Jalen Cross", 4, 0, 0.1, 0,
                policy_version=LIFE_BRAIN_V3_VERSION,
                routine_streak=2,
            ),
            "socialize",
        )
        self.assertEqual(
            choose_life_action(
                "Micah Vale", 4, 1, 0.1, 0,
                policy_version=LIFE_BRAIN_V3_VERSION,
                routine_streak=-2,
            ),
            "train",
        )
        self.assertEqual(
            choose_life_action(
                "Jalen Cross", 4, 0, 0.3, 2,
                policy_version=LIFE_BRAIN_V3_VERSION,
                routine_streak=2,
            ),
            "recover",
        )
        teams = teams_for_season(1)
        roster = tuple(player.name for team in teams for player in team.players)
        with self.assertRaisesRegex(ValueError, "exact active roster"):
            between_game_choices(
                2,
                dict(empty_fatigue(teams)),
                dict(empty_availability(teams)),
                teams,
                policy_version=LIFE_BRAIN_V3_VERSION,
            )
        choices = between_game_choices(
            2,
            dict(empty_fatigue(teams)),
            dict(empty_availability(teams)),
            teams,
            policy_version=LIFE_BRAIN_V3_VERSION,
            routine_streaks={name: 0 for name in roster},
        )
        self.assertTrue(all(choice.policy_version == LIFE_BRAIN_V3_VERSION for choice in choices))

        state = simulate_next_season(
            new_league(1_960), 8, teams,
            life_policy_version=LIFE_BRAIN_V3_VERSION,
        )
        runs = {name: ("", 0) for name in roster}
        maximum = 0
        for game in state.seasons[0].games:
            for decision in game.life_decisions:
                previous, length = runs[decision.athlete]
                if decision.selected in {"train", "socialize"}:
                    length = length + 1 if previous == decision.selected else 1
                    previous = decision.selected
                else:
                    previous, length = "", 0
                runs[decision.athlete] = previous, length
                maximum = max(maximum, length)
        self.assertLessEqual(maximum, 2)
        self.assertTrue(any(
            decision.reason.startswith("Routine variation")
            for game in state.seasons[0].games
            for decision in game.life_decisions
        ))
        with TemporaryDirectory() as directory:
            path = Path(directory) / "routine.json"
            save_league(state, path)
            loaded = load_league(path)
        self.assertEqual(state, loaded)
        self.assertEqual(
            simulate_next_season(
                state, 4, teams_for_season(2),
                life_policy_version=LIFE_BRAIN_V3_VERSION,
            ),
            simulate_next_season(
                loaded, 4, teams_for_season(2),
                life_policy_version=LIFE_BRAIN_V3_VERSION,
            ),
        )

    def test_preference_pilot_is_explicit_complete_and_resumable(self) -> None:
        self.assertEqual(DEFAULT_LIFE_BRAIN_VERSION, LIFE_BRAIN_V4_VERSION)
        self.assertEqual(set(OFF_DAY_PREFERENCES), {
            player.name
            for season_number in range(1, 5)
            for team in teams_for_season(season_number)
            for player in team.players
        })
        for season_number in range(1, 5):
            for team in teams_for_season(season_number):
                self.assertEqual(
                    sorted(OFF_DAY_PREFERENCES[player.name] for player in team.players),
                    ["practice"] * 3 + ["social"] * 3,
                )
        self.assertEqual(
            choose_life_action("Jalen Cross", 2, 0, 0.2399, 0, policy_version=LIFE_BRAIN_V2_VERSION),
            "train",
        )
        self.assertEqual(
            choose_life_action("Micah Vale", 2, 1, 0.2399, 0, policy_version=LIFE_BRAIN_V2_VERSION),
            "socialize",
        )
        self.assertEqual(
            choose_life_action("Jalen Cross", 2, 0, 0.24, 0, policy_version=LIFE_BRAIN_V2_VERSION),
            "rest",
        )
        self.assertEqual(
            choose_life_action("Jalen Cross", 2, 0, 0.3, 2, policy_version=LIFE_BRAIN_V2_VERSION),
            "recover",
        )
        teams = teams_for_season(1)
        decisions = between_game_choices(
            2,
            dict(empty_fatigue(teams)),
            dict(empty_availability(teams)),
            teams,
            policy_version=LIFE_BRAIN_V2_VERSION,
        )
        legacy_decisions = between_game_choices(
            2,
            dict(empty_fatigue(teams)),
            dict(empty_availability(teams)),
            teams,
            policy_version=LIFE_BRAIN_V1_VERSION,
        )
        with self.assertRaisesRegex(ValueError, "policy does not match"):
            simulate_scheduled_game(
                build_schedule(2, 1_950, teams)[1],
                empty_fatigue(teams),
                empty_availability(teams),
                teams,
                life_decisions=legacy_decisions,
            )
        with self.assertRaisesRegex(ValueError, "missing off-day preference"):
            choose_life_action(
                "Unknown Athlete", 2, 0, 0.3, 2,
                policy_version=LIFE_BRAIN_V2_VERSION,
            )
        state = simulate_next_season(
            new_league(1_950), 4, teams_for_season(1),
            life_policy_version=LIFE_BRAIN_V2_VERSION,
        )
        self.assertEqual(
            simulate_next_season(new_league(1_950), 4, teams_for_season(1)),
            simulate_next_season(
                new_league(1_950), 4, teams_for_season(1),
                life_policy_version=LIFE_BRAIN_V4_VERSION,
            ),
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "pilot.json"
            save_league(state, path)
            loaded = load_league(path)
        self.assertEqual(state, loaded)
        self.assertEqual(
            simulate_next_season(
                state, 4, teams_for_season(2),
                life_policy_version=LIFE_BRAIN_V2_VERSION,
            ),
            simulate_next_season(
                loaded, 4, teams_for_season(2),
                life_policy_version=LIFE_BRAIN_V2_VERSION,
            ),
        )

    def test_choices_are_deterministic_auditable_and_bounded(self) -> None:
        teams = default_teams()
        fatigue = dict(empty_fatigue(teams))
        availability = dict(empty_availability(teams))
        routine_streaks = {
            player.name: 0 for team in teams for player in team.players
        }
        scoring_forms = {name: "typical" for name in routine_streaks}
        first = between_game_choices(
            2, fatigue, availability, teams,
            routine_streaks=routine_streaks,
            recent_scoring_forms=scoring_forms,
        )
        self.assertEqual(
            first,
            between_game_choices(
                2, fatigue, availability, teams,
                routine_streaks=routine_streaks,
                recent_scoring_forms=scoring_forms,
            ),
        )
        self.assertEqual(len(first), 12)
        self.assertEqual({decision.selected for decision in first}, {"train", "socialize"})
        self.assertTrue(
            all(decision.policy_version == DEFAULT_LIFE_BRAIN_VERSION for decision in first)
        )
        legacy = between_game_choices(
            2,
            dict(empty_fatigue(teams)),
            dict(empty_availability(teams)),
            teams,
            policy_version=LIFE_BRAIN_V1_VERSION,
        )
        self.assertTrue(all(decision.policy_version == LIFE_BRAIN_V1_VERSION for decision in legacy))
        self.assertNotEqual(first, legacy)
        self.assertTrue(all(0 <= decision.readiness <= 0.02 for decision in first))
        self.assertTrue(all(decision.legal_choices for decision in first))

        fatigue[first[0].athlete] = 0.3
        availability[first[1].athlete] = 3
        routine_streaks = {
            decision.athlete: next_routine_streak(0, decision.selected)
            for decision in first
        }
        special = between_game_choices(
            3, fatigue, availability, teams,
            routine_streaks=routine_streaks,
            recent_scoring_forms=scoring_forms,
        )
        self.assertEqual(special[0].selected, "rest")
        self.assertEqual(special[1].selected, "recover")
        self.assertEqual(special[1].recovery_after, 2)
        with self.assertRaisesRegex(ValueError, "illegal"):
            apply_life_action("Jalen Cross", 2, "party", 0.1, 0)

    def test_life_state_replays_and_resumes_without_rating_mutation(self) -> None:
        teams = default_teams()
        before = teams_for_season(1)
        season = simulate_season(4, 1_700, teams=teams)
        self.assertEqual(len(season.games[0].life_decisions), 0)
        self.assertTrue(all(len(game.life_decisions) == 12 for game in season.games[1:]))
        archived = season.games[1]
        fixture = build_schedule(4, 1_700, teams)[1]
        original = simulate_game(
            archived.seed,
            matchup=(fixture.home, fixture.away),
            initial_fatigue=dict(archived.pregame_fatigue),
            initial_availability=dict(archived.pregame_availability),
            initial_readiness=dict(archived.pregame_readiness),
        )
        replayed = simulate_game(
            archived.seed,
            original.action_tape,
            matchup=(fixture.home, fixture.away),
            initial_fatigue=dict(archived.pregame_fatigue),
            initial_availability=dict(archived.pregame_availability),
            initial_readiness=dict(archived.pregame_readiness),
        )
        self.assertEqual(original, replayed)
        self.assertEqual(
            (original.home_score, original.away_score),
            (archived.home_score, archived.away_score),
        )
        self.assertEqual(before, teams_for_season(1))

        state = simulate_next_season(new_league(1_800), 4)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "league.json"
            save_league(state, path)
            loaded = load_league(path)
        self.assertEqual(state, loaded)
        self.assertEqual(
            simulate_next_season(state, 4),
            simulate_next_season(loaded, 4),
        )

    def test_saved_v1_v2_v3_history_is_unchanged_when_default_v4_is_appended(self) -> None:
        legacy = simulate_next_season(
            new_league(1_850),
            4,
            teams_for_season(1),
            life_policy_version=LIFE_BRAIN_V1_VERSION,
        )
        legacy = simulate_next_season(
            legacy,
            4,
            teams_for_season(2),
            life_policy_version=LIFE_BRAIN_V2_VERSION,
        )
        legacy = simulate_next_season(
            legacy,
            4,
            teams_for_season(3),
            life_policy_version=LIFE_BRAIN_V3_VERSION,
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.json"
            save_league(legacy, path)
            loaded = load_league(path)
        self.assertEqual(legacy, loaded)
        mixed = simulate_next_season(loaded, 4, teams_for_season(4))
        self.assertEqual(mixed.seasons[:3], legacy.seasons)
        self.assertEqual(
            {
                decision.policy_version
                for game in mixed.seasons[0].games
                for decision in game.life_decisions
            },
            {LIFE_BRAIN_V1_VERSION},
        )
        self.assertEqual(
            {
                decision.policy_version
                for game in mixed.seasons[1].games
                for decision in game.life_decisions
            },
            {LIFE_BRAIN_V2_VERSION},
        )
        self.assertEqual(
            {
                decision.policy_version
                for game in mixed.seasons[2].games
                for decision in game.life_decisions
            },
            {LIFE_BRAIN_V3_VERSION},
        )
        self.assertEqual(
            {
                decision.policy_version
                for game in mixed.seasons[3].games
                for decision in game.life_decisions
            },
            {LIFE_BRAIN_V4_VERSION},
        )

    def test_retirement_and_debut_bound_the_choice_history(self) -> None:
        state = new_league(1_900)
        for season_number in range(1, 5):
            state = simulate_next_season(state, 2, teams_for_season(season_number))
        choices_by_season = {
            season.season_number: {
                decision.athlete
                for game in season.games
                for decision in game.life_decisions
            }
            for season in state.seasons
        }
        self.assertIn("Roman Voss", choices_by_season[3])
        self.assertNotIn("Roman Voss", choices_by_season[4])
        self.assertNotIn("Soren Lake", choices_by_season[3])
        self.assertIn("Soren Lake", choices_by_season[4])


if __name__ == "__main__":
    unittest.main()
