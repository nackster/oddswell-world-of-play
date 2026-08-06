---
tags:
  - development
  - admin
  - league
  - replay
status: complete
---

# Phase 0.5C Archived Game Playback

Phase 0.5C connects every completed League Viewer result to the Game Theater. A selected game is deterministically reconstructed from its authoritative pregame league state and checked against the archived score, minutes, and replay evidence. Cost: **$0.00**.

## Implemented

- Every League Viewer game has a **Watch exact replay** action.
- The server reconstructs the selected matchup with its original home/away assignment, hidden pregame fatigue, published availability, and deterministic engine seed.
- The browser receives no seed, fatigue values, recovery timers, injury-risk internals, or RNG state.
- Archived playback includes every recorded pass, shot, rebound, turnover, and shot-clock violation frame, plus lineup state and the final replay seal.
- The Game Theater identifies the season and game, displays the complete frame count, and ends in an **ARCHIVE VERIFIED** state.
- Live seeded simulations and archived games share one replay-payload builder; no duplicate replay system, database, or dependency was added.

## Verification boundary

Before an archived replay reaches the browser, its reconstructed home score, away score, and exact player minutes must match the stored league result. The public replay metadata links back to the archived SHA-256 replay evidence.

The symbolic court remains a presentation layer. Team assignments, lineups, clock, score, actors, targets, and play events are authoritative; physical marker coordinates are illustrative because Phase 0 does not simulate 3D positions.

## Validation

- Admin Console self-check passed for a full archived Game 20 reconstruction.
- All 29 simulator, policy, league, persistence, availability, and prediction regression tests passed.
- The local API returned Game 20 with 434 total frames, a 77-86 result, a verified replay link, and no public seed.
- Browser QA selected Game 20 from the League Viewer, played all 433 recorded play frames, ended 77-86 with **ARCHIVE VERIFIED**, enabled replay-last-game, and reported no console errors.

## Athlete design rule recorded alongside this phase

[[Design/Decisions/DEC-003 Multi-Brain AI Architecture|DEC-003]] now explicitly separates durable athlete talent and specialties from temporary form and Athlete Life Brain consequences. Players may be stars, specialists, average, or below average across their careers. Practice, discipline, partying, fictional legal trouble, health, and other life choices can affect development, trust, consistency, availability, contracts, and career length through visible causal chains.

## Next gate

Phase 0.5D should add Athlete Career Profiles that make durable ratings, specialties, career state, recent performance, availability, and history easy to inspect. The Athlete Life Brain remains a later implementation after this sports foundation is visible and auditable.
