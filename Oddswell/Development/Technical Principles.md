---
tags:
  - development
  - architecture
---

# Technical Principles

1. The server is authoritative for credits, predictions, league state, and match outcomes.
2. A match result never depends on whether a player watches it.
3. Each match stores a versioned AI decision tape plus a deterministic outcome log that clients can replay at different fidelity levels.
4. AI brains may choose strategies and action intents, but only schema-validated commands can enter an authoritative rules engine.
5. AI output never directly mutates credits, wagers, ledgers, rules, or final outcomes.
6. AI memory may update continuously, but model and policy changes are evaluated, versioned, and deliberately promoted.
7. Every credit mutation is represented by an auditable ledger entry.
8. Real-money purchase processing is idempotent and verified server-side.
9. Competitive information is released equally to all players.
10. Prototype the simulation before committing to expensive 3D production.
11. Apply Ponytail: reuse existing capabilities and build only the smallest correct system required by the current phase.
