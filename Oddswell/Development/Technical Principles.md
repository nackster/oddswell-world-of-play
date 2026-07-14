---
tags:
  - development
  - architecture
---

# Technical Principles

1. The server is authoritative for credits, predictions, league state, and match outcomes.
2. A match result never depends on whether a player watches it.
3. Each match produces a deterministic, versioned event log that clients can render at different fidelity levels.
4. Every credit mutation is represented by an auditable ledger entry.
5. Real-money purchase processing is idempotent and verified server-side.
6. Competitive information is released equally to all players.
7. Prototype the simulation before committing to expensive 3D production.
8. Apply Ponytail: reuse existing capabilities and build only the smallest correct system required by the current phase.
