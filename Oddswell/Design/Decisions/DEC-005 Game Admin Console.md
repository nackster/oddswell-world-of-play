---
tags:
  - decision
  - admin
  - operations
  - security
status: approved-direction
date: 2026-07-14
---

# DEC-005: Game Admin Console

## Direction

The Brain Observatory will grow into a general OddsWell Admin Console for operating the game. The exact controls will be chosen as each game system becomes real instead of building speculative switches now.

Likely control areas include:

- Brain status, evaluation, candidate versions, and approved promotion.
- Teams, athletes, schedules, seasons, simulations, and world state.
- Clothing, items, content availability, release windows, and active/inactive flags.
- Economy configuration and auditable operational reports after the legal and payment gates are complete.
- Player support, moderation, announcements, maintenance, and release controls when those systems exist.

## Guardrails

- The game server remains authoritative; the dashboard requests validated changes rather than editing production data directly.
- Every consequential admin action records the operator, timestamp, previous value, new value, and reason.
- Use least-privilege roles and require authentication before the console is reachable beyond the local computer.
- Destructive, financial, economy, model-promotion, and live-release actions require confirmation and, where appropriate, a second approval.
- Secrets and payment data are never displayed in the interface or stored in the Obsidian vault.
- Visual brain activity must distinguish simulation, evaluation, memory updates, and actual model training.

## Current boundary

The present Observatory is local-only and read-oriented. It can run a real simulation and preview the future training presentation, but it does not control production data and it does not claim that model training is active.

See [[Development/Brain Observatory]] for the current implementation.
