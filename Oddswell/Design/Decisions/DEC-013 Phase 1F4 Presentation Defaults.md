---
tags:
  - decision
  - beta
  - basketball
  - presentation
status: accepted
date: 2026-07-21
---

# DEC-013 Phase 1F.4 Presentation Defaults

## Decision

The owner approved the minimum current-beta basketball presentation defaults:

- symbolic 3D placeholder athletes;
- one fixed broadcast camera;
- text event callouts without voice commentary;
- an approximately three-minute game presentation; and
- no player skip control until Phase 1F.5 proves that watch, skip, late arrival, and reconnect cannot change the authoritative result.

The presentation must consume the existing verified event log. It may show illustrative positions, but it may not resimulate the game or change the recorded score, clock, actors, events, final result, or replay seal.

## Delivery split

Phase 1F.4 makes the accepted archived game readable at the approved defaults. Phase 1F.5 owns result-invariance proof and any minimum QA-only controls needed to test watch, skip, late arrival, and reconnect.

The accepted Season 1 Game 1 archive is a regulation game, so the current presentation truthfully shows `Overtime: NO`. A future replay must carry authoritative overtime evidence before the client may display a different overtime state.

## Boundary

This decision does not approve voice commentary, camera cuts, replay cuts, a crowd, condensed mode, final athlete or team art, wager interaction, odds, settlement, a backend, hosting, deployment, or a general skip feature. The final presentation treatment and whether important games run longer remain later content decisions.

## Phase 1F.5 follow-up

Phase 1F.5 proved that full watch, direct skip, mid-watch player skip, late arrival, and seal-validated cold reconnect all reach the identical recorded final frame. The player may now press `S` during the presentation to jump to that sealed result. This is a local replay-view control, not a network session or backend reconnect system.
