---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-22
---

# Phase 1H.12 Immutable Authoritative Canceled-Game Evidence Link

## Outcome

Phase 1H.12 proves one canceled-game disposition without rewriting the sealed Season 1, Game 1 result. An explicitly noncanonical QA chain uses Season 99, Game 1 and persists one separate versioned `oddswell-match-winner-canceled-game-v1` record. The record binds the exact accepted request and game-start lock, season and game, one server cancellation command ID, one cancellation evidence ID, one authoritative cancellation time, the neutral reason `game_canceled`, and closed status `closed_canceled`.

The canonical Harbor City Waves `101` to Mesa Vista Sol `104` archive remains immutable and cannot be relabeled as canceled. Exact retry returns the existing cancellation record. Unknown or mismatched request, lock, game, time, schema, version, status, or reason; conflicting command reuse; a second disposition; malformed persistence; and any chain that already has a sealed result, settlement decision, or finalization fail closed.

Ponytail extended the existing SaveGame record and native economy automation. Schema v8 migrates to v9 with an empty canceled-game collection; migration invents no cancellation. The old exact loss remains `2` ledger entries and balance `60`, and the old exact win remains `3` entries and balance `160`.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed twice: `13.05s` before test expansion and `9.34s` for the final build |
| Focused native economy automation | `1/1` passed with exit code `0` |
| Full native OddsWell automation | `11/11` passed with exit code `0` |
| Focused odds-contract tests | `3/3` passed in `0.055s` |
| Canceled-game record | One noncanonical Season 99, Game 1 record binds the exact request, lock, command, evidence, time, reason, and status |
| Idempotency and rejection | Exact retry is duplicate-safe; wrong or conflicting identity, state, timing, version, reason, second disposition, and malformed persistence reject without mutation |
| Migration and cold load | Schema v8 cold-loads as v9 with zero invented cancellations; the exact record survives cold load; old loss and win profiles remain exact |
| Frozen timing guard | `1/1` passed in `59.431s` under the accepted Codex Python 3.12 runtime, process verified at High priority |
| Frozen Python regression | `65/65` passed in `145.685s` with the unchanged timing-sensitive test first, process verified at High priority |
| Wrong-interpreter rejection | Two Unreal Python 3.11 runs were rejected as noncanonical evidence after identical hash mismatches; no frozen code, threshold, or `PYTHONHASHSEED` setting changed |
| Brain Admin self-check | Passed |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, `29,160` bytes, SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This phase records canceled-game evidence only. It adds no ledger credit, refund, void amount due, settlement decision, application, finalization, reconciliation projection, Admin surface, player UI, generalized cancellation service, timeout policy, correction taxonomy, alternate market, backend, deployment, real-money connection, or basketball/Athlete Life brain behavior.

The cancellation QA chain is deliberately separate from the immutable Season 1, Game 1 loss and win evidence. A canceled-game record is not a refund and makes no claim that player funds have been restored.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement. Any void/refund due decision, application/finalization, correction, or player-facing history/UI remains a separate unproved gate.
