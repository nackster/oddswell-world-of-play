---
tags:
  - development
  - phase-06a
  - athlete-performance
  - consistency
status: complete
date: 2026-07-17
---

# Phase 0.6A: Opt-In Athlete Game Consistency Pilot

## Result

OddsWell now has one opt-in `athlete-consistency-v1` performance factor. Durable basketball ratings still determine how good an athlete is; the consistency tier controls only the width of one zero-centered game-form modifier.

This belongs to the Athlete Profile and Basketball Brain, not the Athlete Life Brain. Phase 0.5Y therefore selects **no new Life Brain input** and redirects the requested behavior to the core performance model.

The pilot is not active in the authoritative league. Existing v1-v4 history, default-v4 Life Brain behavior, predictions, replay hashes, and archives remain unchanged. Cost: **$0.00**.

## Smallest implementation

- Four durable tiers: `volatile`, `normal`, `steady`, and `elite`.
- One deterministic triangular game-form draw per athlete and seed, centered on zero so consistency does not add raw talent.
- Maximum absolute form by tier: 1.5%, 1.0%, 0.6%, and 0.25% respectively.
- The modifier affects pass/turnover execution and shot-versus-defense probability only when explicitly supplied to the simulator.
- Omitting the new input produces the exact legacy game and replay evidence.
- Every supplied form map must contain the full matchup roster and stay within ±1.5%.
- The Admin athlete profile displays the tier as `OPT-IN PILOT`; it does not label the factor active or trained.

## Prototype rarity

The current twelve-athlete active roster contains:

- 1 elite-consistency athlete: Tariq Stone.
- 4 steady athletes.
- 5 normal athletes.
- 2 volatile athletes.

Soren Lake also has a normal tier for career continuity. One elite tier in this tiny prototype is an evaluation fixture, not the final production-league rarity. A generational athlete still requires both rare high ratings and elite consistency; consistency alone cannot create a superstar.

## Frozen 80-game pilot

Across seeds 60,000-60,079:

- Mean absolute form: elite 0.0906%, steady 0.2162%, normal 0.3308%, volatile 0.5103%.
- Maximum absolute form: elite 0.24%, steady 0.60%, normal 0.94%, volatile 1.42%.
- 47/80 paired games changed at least one team score.
- 12/80 paired winners differed.
- Mean absolute team-score difference was 4.2062 points.
- Exact replay violations: **0**.

This proves the tier mechanics are ordered, bounded, consequential, and replayable. It does **not** yet prove that elite athletes achieve the intended healthy-game performance floor. Winner changes also show material path sensitivity, so promotion is not authorized.

## Validation

- Focused simulator and consistency suite: **10/10 passed** in 3.838 seconds.
- Full historical regression suite: **53/53 passed** in 119.323 seconds.
- Admin Console self-check: **passed**.
- All frozen v1-v4 studies, digests, prediction paths, and replay contracts remain green.
- Both affected clean canvases parse as valid JSON with unique identifiers and valid edge endpoints; repository whitespace checks pass.

## Truth boundary

This is deterministic fictional game-form variance, not confidence, mentality, personality, learning, intelligence, neural-network training, or real-world evidence. Fatigue, injuries, matchups, Life Brain choices, ratings, and random possession outcomes still produce good and bad nights.

## Next gate

Phase 0.6B read-only **Multi-Season Athlete Consistency Calibration**. Compare the same athlete ratings under every consistency tier so role, usage, and talent do not confound the result. Measure healthy-game bad-night frequency, performance floor, average-player distribution, specialist preservation, team balance, and replay integrity. Do not promote the pilot until that controlled evidence exists.
