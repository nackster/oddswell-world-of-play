---
tags:
  - decision
  - beta
  - unreal-engine
  - client
status: approved
date: 2026-07-19
---

# DEC-006: Unreal Engine 5.8 Beta Adoption

## Decision

Unreal Engine 5.8 is the approved 3D client engine for OddsWell beta development.

The owner accepted the completed Phase 1A benchmark evidence on July 19, 2026 and authorized continued Unreal work needed to deliver the beta roadmap.

## Evidence accepted

- A portable project reopens in UE 5.8.
- Local Windows Development packages build and launch reproducibly.
- The noncanonical street-block and basketball-court graybox passes Map Check and collision checks.
- The packaged client directly renders the verified 421-frame public replay without resimulating basketball.
- Two final replay runs produced the same final score, replay seal, and canonical trace hash.
- Generated files remain ignored and the frozen simulation and Brain Admin checks remain green.

See [[Development/Reports/Phase 1A2b Authoritative 421-Frame Replay Renderer]] for the final benchmark evidence.

## Boundary

This decision approves UE 5.8 for beta client development. It does not approve a city identity, camera style, character-art direction, paid service, deployment, monetization, or any later roadmap feature by itself.

