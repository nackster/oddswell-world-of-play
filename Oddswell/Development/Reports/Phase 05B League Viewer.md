---
tags:
  - development
  - admin
  - league
  - visualization
status: complete
---

# Phase 0.5B League Viewer

Phase 0.5B adds a read-only League Viewer to the local OddsWell Admin Console. It presents one deterministic 20-game development season through the same public-information boundary used by Phase 0D.4 prediction evaluation. Cost: **$0.00**.

## Implemented

- Final standings with records, points for, points against, and point differential.
- All twelve fictional athletes with public ratings, overall rating, and final published availability.
- A complete 20-game schedule with home/away assignment, final score, and winner.
- Per-game inspection with pregame public availability and authoritative minutes played.
- Three pregame home-win probabilities: fixed 50%, public-history Elo, and Elo plus public availability.
- The SHA-256 prediction commitment created before each game and the verified replay hash linked after the result.
- A cached local read model, so the archived season is generated once per server session without adding a database or dependency.

## Truth and privacy boundary

The interface does not expose simulator seeds, hidden fatigue, recovery timers, injury-risk calculations, RNG state, future results, economy data, or user data. It has no controls for changing schedules, teams, results, credits, or predictions.

The prediction percentages are evidence from a fictional simulator. They are not a wagering product or a claim about real-world sports performance.

## Validation

- Admin Console self-check passed, including 20-game totals, replay and commitment hashes, and forbidden-key checks.
- All 29 simulator, policy, league, availability, persistence, and prediction regression tests passed.
- Browser QA loaded the World / League page, selected Game 20, verified Harbor City Waves won 86-77, and found no browser console errors.

## Known limits

- This is one archived development season with two teams, not a live league service.
- The Viewer is local and read-only; authentication and role-based access are still required before network exposure.
- Archived schedule entries do not yet open their exact recorded Game Theater replay.

## Next gate

Phase 0.5C should link each archived league result to its exact recorded Game Theater playback while keeping hidden league state server-side. Credits, settlement, and wagering remain separate later gates.
