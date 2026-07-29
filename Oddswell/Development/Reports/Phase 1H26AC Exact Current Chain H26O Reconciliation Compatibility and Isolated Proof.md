---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-29
---

# Phase 1H.26AC — Exact Current-Chain H26O Reconciliation Compatibility and Isolated Proof

## Outcome

Phase 1H.26AC extends the existing H26O read-only reconciliation surface to exactly one second approved canonical loss chain: the fixed H26W–H26AB evidence. It reuses the existing writer, `oddswell-match-winner-reconciliation-v1` projection, `/api/match-winner-reconciliation` endpoint, Brain Admin validator, and single Operations card.

The original H26O Harbor `97`–Mesa `101` loss remains valid. The new fixed variant is Harbor `79`–Mesa `113`, Mesa winner, with offer `c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d`, result `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`, and replay `35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db`.

The projection exposes only the existing approved fields: Harbor selected, probability `57586693`, decimal odds `17365`, stake `40`, potential gross return `69`, loss due/applied `0`, `settled_lost`, two ledger entries, balance `60`, and net `-40`.

## Boundary

Ponytail added one exact native predicate and one exact Admin variant. It did not add an endpoint, card, schema, framework, generalized history, automatic H26O chain, service, backend, simulator change, brain change, paid API, credit purchase, real-money path, retraining, payout, or refund.

H26P deliberately remains tied to the original `97`–`101` chain. The current H26AB clone produces no player receipt and the packaged proof log contains no H26P marker. A current-chain player receipt requires a separate Scope Director decision.

Partial, tampered, mixed old/current, malformed, and missing evidence fails closed. Rejection removes stale projection output and exposes no partial values. The existing archived win/loss/void consumers remain unchanged.

## Isolated packaged proof

A fresh Windows Development package cloned the accepted H26AB finalized SaveGame into a separate user directory and invoked only `-CanonicalMatchWinnerLossReconciliationQa`.

- Package: `50` files, `1,048,042,110` bytes, zero Python files.
- Packaged marker: `PASS`, exact current identities and `79-113` result, read-only, no controls, mutation, payout, or refund.
- Source SaveGame before and after: `10,082` bytes; SHA-256 `4cb4a0f70d45feef46da1dfb88f6086b05b85fbb82fcb90148c3e08dc66f9366`; UTC mtime `2026-07-28T22:20:03.1103768Z`.
- Projection: `4,137` bytes; SHA-256 `017e6ece1abb2dc4889f5af6484daf17345bd7a717d166b1d4d46534c38c20b5`.
- Brain Admin accepted the projection as `VALIDATED QA FINALIZED LOSS` with exact command and ledger linkage.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26AC-20260729`.

## Validation

- Editor compile: PASS.
- Focused native H26O automation: `1/1` PASS.
- Full native OddsWell automation: `34/34` PASS.
- Combined H26W/H26X/H26Y supervisor tests: `28/28` plus `13` subtests PASS.
- Brain Admin self-check and Python compilation: PASS.
- Full Python regression: final authorized quiet-load run `105/105` plus `119` subtests PASS in `285.95s`; canonical Python `3.12.13`, timing-sensitive test first, PID `35592` verified at High priority.
- Timing audit: the first full run was retained as a failed `104/105` attempt because the unchanged life-performance guard measured `140.481s` against `<120s`; the isolated diagnostic then passed in `119.76s`. No test, threshold, simulator, priority rule, or product behavior changed. Scope Decision A authorized exactly one quiet-load rerun, which passed.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- All eight canvases parse; diff hygiene and relevant-process cleanup passed; cost was `$0.00`.

## Next gate

Stop for Scope Director review. H26AC proves only exact current-chain H26O compatibility. Current-chain H26P, generalized history, multiple wagers, automatic H26O, correction, broader markets, online authority, and any brain or simulator change remain separate unapproved gates.
