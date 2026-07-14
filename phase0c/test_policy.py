import copy
import json
import random
import unittest

from phase0a.simulator import GameState, default_teams, simulate_game
from phase0c.fairness import run_paired_fairness
from phase0c.pilot import run_offline_pilot
from phase0c.policy import CONTEXT_KEYS, Completion, LLMPolicy, build_context, offline_fixture_completion
from phase0c.replay import replay_manifest, verify_replay_manifest
from phase0c.scenarios import SCENARIOS, canonical_request, run_recorded_scenarios


class PolicyTests(unittest.TestCase):
    def state(self) -> tuple[GameState, object, object]:
        home, away = default_teams()
        state = GameState(home, away, possession=home.name, possession_number=1, decision_number=1)
        state.score = {home.name: 0, away.name: 0}
        state.fatigue = {player.name: 0.0 for team in (home, away) for player in team.players}
        return state, home, away

    def test_context_is_exact_and_excludes_competitive_or_economy_data(self) -> None:
        state, home, away = self.state()
        context = build_context("offense", state, home, away, home.players[0].name)
        self.assertEqual(set(context), CONTEXT_KEYS)
        serialized = json.dumps(context).lower()
        for forbidden in ("seed", "probability", "credit", "wager", "wallet", "purchase", "payment"):
            self.assertNotIn(forbidden, serialized)

    def test_invalid_provider_outputs_fall_back_with_stable_categories(self) -> None:
        state, home, away = self.state()
        cases = (
            (lambda _: Completion("not json", "fake", "bad"), "malformed_json"),
            (lambda _: Completion(json.dumps({"role": "offense"}), "fake", "bad"), "invalid_action"),
            (lambda _: Completion(json.dumps({"role": "offense", "kind": "teleport", "actor": home.players[0].name, "target": None}), "fake", "bad"), "invalid_action"),
            (lambda _: (_ for _ in ()).throw(TimeoutError()), "timeout"),
            (lambda _: (_ for _ in ()).throw(RuntimeError("offline")), "provider_error"),
        )
        for complete, expected in cases:
            with self.subTest(expected):
                policy = LLMPolicy(complete)
                action = policy("offense", state, home, away, home.players[0].name, random.Random(7))
                self.assertTrue(policy.traces[-1]["fallback"])
                self.assertEqual(policy.traces[-1]["error_category"], expected)
                self.assertEqual(action.actor, home.players[0].name)

    def test_fixture_game_is_deterministic_and_replay_never_calls_provider(self) -> None:
        first_policy = LLMPolicy(offline_fixture_completion)
        second_policy = LLMPolicy(offline_fixture_completion)
        first = simulate_game(42, brain_version="llm-contract-fixture-v1", decision_policy=first_policy)
        second = simulate_game(42, brain_version="llm-contract-fixture-v1", decision_policy=second_policy)

        def bomb(_: str) -> Completion:
            raise AssertionError("replay called the provider")

        replayed = simulate_game(
            42,
            action_tape=first.action_tape,
            brain_version="llm-contract-fixture-v1",
            decision_policy=LLMPolicy(bomb),
        )
        self.assertEqual(first.records, second.records)
        self.assertEqual(first.records, replayed.records)
        self.assertTrue(first_policy.traces)
        self.assertFalse(any(trace["fallback"] for trace in first_policy.traces))

    def test_baseline_distributes_defensive_assignments(self) -> None:
        game = simulate_game(7)
        defenders = {
            event["action"]["actor"]
            for event in game.records
            if event["type"] == "brain_decision" and event["action"]["role"] == "defense"
        }
        self.assertGreater(len(defenders), 2)

    def test_replay_manifest_detects_event_log_mutation(self) -> None:
        matchup = default_teams()
        game = simulate_game(42, matchup=matchup)
        manifest = replay_manifest(game, matchup, "baseline-v2")
        self.assertTrue(verify_replay_manifest(manifest))

        tampered = copy.deepcopy(manifest)
        tampered["payload"]["event_log"][-1]["score"][game.home_team] += 1
        self.assertFalse(verify_replay_manifest(tampered))

    def test_offline_pilot_reports_zero_cost_and_exact_replay(self) -> None:
        result = run_offline_pilot(2, 10, 4)
        self.assertGreater(result.decisions, 0)
        self.assertEqual(result.invalid_outputs, 0)
        self.assertEqual(result.fallbacks, 0)
        self.assertEqual(result.estimated_cost_usd, 0.0)
        self.assertTrue(result.replayed_exactly)
        self.assertEqual(result.replay_manifests_verified, result.games)
        self.assertEqual(result.calibration_checks_passed, result.calibration_check_count)

    def test_paired_fairness_swaps_every_seed_and_passes_guardrails(self) -> None:
        result = run_paired_fairness(10)
        self.assertEqual(result.games, 20)
        self.assertEqual(result.invalid_outputs, 0)
        self.assertEqual(result.fallbacks, 0)
        self.assertEqual(result.exact_replays, result.games)
        self.assertTrue(all(passed for _, passed in result.checks))

    def test_recorded_llm_scenarios_are_legal_and_bound_to_exact_requests(self) -> None:
        result = run_recorded_scenarios()
        self.assertEqual(result.legal_count, result.scenario_count)
        self.assertEqual(result.hash_verified_count, result.scenario_count)
        self.assertEqual(result.fallback_count, 0)
        self.assertEqual(len({canonical_request(scenario) for scenario in SCENARIOS}), len(SCENARIOS))


if __name__ == "__main__":
    unittest.main()
