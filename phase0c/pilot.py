from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from phase0a.simulator import default_teams, simulate_game
from phase0b.analyze import analyze_games
from phase0c.policy import LLMPolicy, offline_fixture_completion


@dataclass(frozen=True)
class PilotResult:
    games: int
    calibration_games: int
    calibration_checks_passed: int
    calibration_check_count: int
    calibration: dict[str, float]
    decisions: int
    action_mix: dict[str, int]
    fallbacks: int
    invalid_outputs: int
    replayed_exactly: bool
    estimated_cost_usd: float


def run_offline_pilot(games: int = 10, calibration_games: int = 1_000) -> PilotResult:
    if games < 1 or calibration_games < 1:
        raise ValueError("game counts must be positive")

    first, second = default_teams()
    action_mix: Counter[str] = Counter()
    traces: list[dict[str, object]] = []
    replayed_exactly = True

    for seed in range(games):
        matchup = (first, second) if seed % 2 == 0 else (second, first)
        policy = LLMPolicy(offline_fixture_completion)
        game = simulate_game(seed, matchup=matchup, brain_version="llm-contract-fixture-v1", decision_policy=policy)
        replay = simulate_game(seed, matchup=matchup, brain_version="llm-contract-fixture-v1", action_tape=game.action_tape)
        replayed_exactly &= game.records == replay.records
        traces.extend(policy.traces)
        action_mix.update(trace["parsed_action"]["kind"] for trace in policy.traces)

    calibration = analyze_games(calibration_games)
    return PilotResult(
        games=games,
        calibration_games=calibration_games,
        calibration_checks_passed=sum(bool(check["passed"]) for check in calibration.checks),
        calibration_check_count=len(calibration.checks),
        calibration=calibration.overall,
        decisions=len(traces),
        action_mix=dict(sorted(action_mix.items())),
        fallbacks=sum(bool(trace["fallback"]) for trace in traces),
        invalid_outputs=sum(trace["error_category"] is not None for trace in traces),
        replayed_exactly=replayed_exactly,
        estimated_cost_usd=sum(float(trace["estimated_cost_usd"]) for trace in traces),
    )


def render_markdown(result: PilotResult) -> str:
    mix = "; ".join(f"{kind}: {count}" for kind, count in result.action_mix.items())
    return f"""---
tags:
  - development
  - simulation
  - ai
  - validation
status: active
---

# Phase 0C Offline LLM Policy Pilot

The provider-neutral LLM boundary is implemented and exercised across **{result.games} games** using a deterministic local fixture. The fixture proves integration, validation, fallback, telemetry, and replay without an API key or paid call. **It is not a live LLM and is not evidence that model decisions are intelligent.**

## Pilot result

| Measure | Result |
| --- | ---: |
| Structured decisions | {result.decisions:,} |
| Invalid provider outputs | {result.invalid_outputs} |
| Deterministic fallbacks | {result.fallbacks} |
| Exact action-tape replay | {"Yes" if result.replayed_exactly else "No"} |
| Estimated paid API cost | ${result.estimated_cost_usd:.2f} |

**Action mix:** {mix}

## Baseline-v2 realism calibration

The opportunity changes were rerun across **{result.calibration_games:,} seeded games**. **{result.calibration_checks_passed}/{result.calibration_check_count} engineering guardrails passed.**

| Measure | Result |
| --- | ---: |
| Average team score | {result.calibration['average_team_score']:.2f} |
| Total possessions | {result.calibration['possessions_per_game']:.2f} |
| Field-goal percentage | {result.calibration['field_goal_percentage']:.1%} |
| Three-point attempt share | {result.calibration['three_attempt_rate']:.1%} |
| Turnovers per team | {result.calibration['turnovers_per_team_game']:.2f} |
| Home win rate | {result.calibration['home_win_rate']:.1%} |
| Overtime rate | {result.calibration['overtime_rate']:.1%} |
| Maximum player attempts | {result.calibration['max_player_attempts_per_game']:.2f} |
| Maximum player rebounds | {result.calibration['max_player_rebounds_per_game']:.2f} |

## Guardrails now enforced

- The provider receives an exact-key sports snapshot: clock, score, possession, fatigue, ratings, ballhandler, and the complete legal-action list.
- The provider never receives the seed, outcome probabilities, credits, wagers, wallet, purchase, or payment data.
- Output must be one exact `Action` object already present in `legal_actions`.
- Timeout, provider, JSON, schema, actor, target, and legality failures use the seeded baseline fallback and are recorded by category.
- The rules engine remains authoritative; replay uses the recorded action tape and never asks the provider again.
- Policy traces capture provider/model, policy version, sanitized request, request hash, raw response, parsed action, fallback, latency, tokens, and cost. Chain-of-thought is never requested or stored.

## Realism correction included

Initial ballhandlers are now weighted by existing passing and shooting ratings, and defenders are distributed by defense rating instead of assigning the single best defender to every possession.

## Live pilot gate

Choose a provider/model and approve a small cost/latency budget before any live call. Start with fixed scenarios or one team's offense for 5-10 games, compare paired seeds and swapped home assignments, and promote a named policy version only if legality, replay, realism, cost, and latency pass.

Before persisted public matches or any wagering feature, bind the engine, seed, matchup, roster, policy, action tape, and event log into a canonical SHA-256 replay manifest so later mutation is detected.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the no-cost Phase 0C LLM policy plumbing pilot.")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--calibration-games", type=int, default=1_000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_offline_pilot(args.games, args.calibration_games)
    report = render_markdown(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {args.output}")
    print(
        f"games={result.games} decisions={result.decisions} calibration="
        f"{result.calibration_checks_passed}/{result.calibration_check_count} invalid={result.invalid_outputs} "
        f"fallbacks={result.fallbacks} replay={result.replayed_exactly} cost=${result.estimated_cost_usd:.2f}"
    )


if __name__ == "__main__":
    main()
