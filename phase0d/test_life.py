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
    simulate_next_season,
    simulate_season,
)
from phase0d.life import (
    LIFE_BRAIN_VERSION,
    apply_life_action,
    between_game_choices,
)


class AthleteLifeBrainTests(unittest.TestCase):
    def test_choices_are_deterministic_auditable_and_bounded(self) -> None:
        teams = default_teams()
        fatigue = dict(empty_fatigue(teams))
        availability = dict(empty_availability(teams))
        first = between_game_choices(2, fatigue, availability, teams)
        self.assertEqual(first, between_game_choices(2, fatigue, availability, teams))
        self.assertEqual(len(first), 12)
        self.assertEqual({decision.selected for decision in first}, {"train", "socialize"})
        self.assertTrue(all(decision.policy_version == LIFE_BRAIN_VERSION for decision in first))
        self.assertTrue(all(0 <= decision.readiness <= 0.02 for decision in first))
        self.assertTrue(all(decision.legal_choices for decision in first))

        fatigue[first[0].athlete] = 0.3
        availability[first[1].athlete] = 3
        special = between_game_choices(3, fatigue, availability, teams)
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
