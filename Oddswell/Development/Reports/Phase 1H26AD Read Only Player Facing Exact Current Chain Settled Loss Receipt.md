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

# Phase 1H.26AD — Read-Only Player-Facing Exact Current-Chain Settled-Loss Receipt

## Outcome

The existing H26P ticket-booth receipt now accepts exactly two approved complete canonical loss chains: the retained Harbor `97`–Mesa `101` loss and the fixed current H26AB Harbor `79`–Mesa `113` loss. The current receipt shows Harbor selected, stake `40`, Mesa winner, returned `0`, net `-40`, balance `60`, and one close instruction.

## Minimal implementation

Ponytail reused the existing receipt struct, loader, ticket-booth HUD, text builder, QA lifecycle, and H26O exact-chain predicates. The loader gained only the second exact current-chain predicate. The HUD remains one screen and derives the approved final score from the validated receipt.

No persistence field, SaveGame schema, writer, projection, endpoint, Admin feature, dependency, gameplay command, ledger operation, payout, refund, correction, generalized history, simulator behavior, or brain behavior was added.

## Trust boundary

The current receipt is available only when the full fixed offer/result/replay identity and authoritative request, lock, decision, finalization, ledger, score, and balance all match. The original retained receipt remains valid.

Missing, partial, tampered, mixed retained/current, Season `99`, Season `100`, archived-result, win, void, cancellation, or otherwise foreign evidence exposes only the existing unavailable state and no partial receipt values. Viewing, closing, leaving, reopening, and restarting remain read-only.

## Validation

- Editor and game Win64 Development builds: PASS.
- Focused H26O/H26AD native automation: `1/1` PASS.
- Full native OddsWell automation: `34/34` PASS, including both H26O variants and retained H26P coverage.
- Combined H26W/H26X/H26Y supervisor tests: `28/28` plus `13` subtests PASS.
- Full frozen Python regression: `105/105` plus `119` subtests PASS in `135.81s` using bundled Python `3.12.13`, the timing-sensitive test first, and verified High priority; no retry was needed.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Fresh explicit-map Windows package: PASS in `50.48s`; `50` files, `1,048,068,734` bytes, zero Python files.
- Two separate packaged current-chain processes: exact receipt and lifecycle QA PASS with final `79-113`, `view_close_leave_reopen=true`, and cold restore.
- Authoritative H26AB SaveGame before, between, and after the packaged processes: `10,082` bytes; SHA-256 `4cb4a0f70d45feef46da1dfb88f6086b05b85fbb82fcb90148c3e08dc66f9366`; UTC mtime `2026-07-28T22:20:03.1103768Z`.
- Rendered `1280×800` receipt: legible and unclipped, with only the approved player-facing values and one close instruction.
- Cost: `$0.00`.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26AD-20260729`.

## Next gate

Stop for Scope Director review. Generalized history, multiple wagers, automatic H26O, correction, later markets, online authority, and any simulator or brain change remain separate unapproved gates.
