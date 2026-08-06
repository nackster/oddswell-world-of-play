---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-23
---

# Phase 1H.18 Cold-Restored Pending Match Winner Receipt

## Outcome

Phase 1H.18 adds one read-only player receipt for the exact pending Phase 1H.17 QA request. In a new cold process, `E` at the existing Sundale Sportsbook frontage shows request ID, offer ID and version, selected team, stake, accepted time, lock time, `accepted_pending_lock`, the linked sequence-`2` `-40` `match_winner_stake` ledger entry, and current balance `60`. Leaving the frontage closes the receipt.

Ponytail reused the existing SaveGame, Sportsbook location and `E` interaction, native on-screen reader, and H17 isolated QA profile. It adds no history framework, widget system, service, generalized receipt, persistence schema, or dependency.

## Independent read-only boundary

The receipt loader reads the QA SaveGame directly and accepts only the exact current schema, two ledger entries, one request, one H17 offer, and zero lock, result, decision, finalization, cancellation, or void records. It independently revalidates the initial sequence-`1` `+100` job credit, sequence-`2` stake debit, request/debit identity, offer identity and version, teams, stake, times, status, and balance progression before returning any field.

Missing, multiple, mismatched, stale, malformed, duplicated, or invented evidence fails closed with one generic error and no partial values. The cold receipt process bypasses request APIs, ledger migration, reconciliation publication, debit, lock, result, and cleanup paths. The packaged QA save remained byte-for-byte unchanged at `3,737` bytes with SHA-256 `8d89d7ea1b1b3958a3b269b257972a2598412d2cc3a9905f2ad7a04d2eb1c99a` and the same modification time before and after the receipt process.

The separate H17 verification process still proved exact duplicate retry, all eight rejection classes, zero mutation, and cleanup. The normal H16 canonical preview, canonical Season 1, Game 1, existing loss/win/void histories, Basketball Brain, and simulator remain unchanged.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H18 receipt | `1/1` passed, including exact cold receipt and the complete fail-closed mutation matrix |
| Full native OddsWell automation | `13/13` passed, including the unchanged H17 request audit |
| Focused odds contracts | `3/3` passed in `0.056s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `133.602s` |
| Brain Admin self-check | Passed unchanged |
| Editor and game targets | Passed |
| Windows BuildCookRun | Clean two-map package passed in `151.50s`; final source-state incremental package passed in `50.38s`; pak, IoStore, compression, package, and archive succeeded |
| Packaged cold receipt | Separate H17 seed and H18 receipt processes passed; receipt log reports `request_api=false`, `debit=false`, `lock=false`, `result=false`, and `mutation=false` |
| Location behavior | Receipt is unavailable outside the Sportsbook frontage, opens through the `E` path, and closes on leave |
| H17 preservation | Cold exact retry remained `DUPLICATE`; stale, tampered, invalid-team, invalid-stake, late, conflicting, completed-H16, and insufficient-balance cases remained zero-mutation; cleanup passed |
| Visual proof | `Phase1H18_PendingMatchWinnerReceipt.png`, `783,491` bytes, visually shows every approved receipt field and the read-only warning |
| Canonical league | Deterministic re-export remained `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Canonical replay | Remained `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| Package | `50` files totaling `1,045,032,062` bytes |
| Cost | `$0.00` |

## Truth boundary

This is one cold-restored read-only receipt for one noncanonical machine-local QA request. It does not submit, debit, lock, simulate, resolve, settle, refund, correct, migrate, publish reconciliation, create generalized history, add an account or backend, connect real money, deploy, retrain, or change any brain.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement from current evidence. A canonical future-game request, game-start integration, settlement integration, correction policy, and broader player history remain separate unproved gates. No later phase begins from this report.
