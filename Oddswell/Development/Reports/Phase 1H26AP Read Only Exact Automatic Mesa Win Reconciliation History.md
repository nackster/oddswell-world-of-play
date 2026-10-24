# Phase 1H.26AP — Read-Only Exact Automatic Mesa Win Reconciliation History

**Date:** 2026-07-31
**Status:** COMPLETE
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The existing Brain Admin Operations reconciliation card now independently accepts and displays the exact normal non-QA H26AM-H26AO automatic Mesa win chain:

- Mesa Vista Sol selected and won;
- probability `42413307`, derived decimal odds `2.3577`, and potential return `94`;
- sealed score `79-113`;
- stake `40`, returned `94`, and net `+54`;
- ledger sequence `2`, `-40`, balance `60`, then sequence `3`, `+94`, balance `154`;
- three entries and one `settled_won` finalization; and
- exact H26E request, H26G lock, H26L result, H26AN decision, H26AJ finalization, and replay-seal linkage.

The card remains output-only and exposes no payout, correction, deletion, wager, or other mutation control.

## Minimal implementation

Ponytail full mode extends the one existing reconciliation-v1 validator branch instead of adding another projection, schema, endpoint, card, controller, writer, or dependency.

The validator accepts the fixed H26AN automatic decision command only when the projection is non-QA and every existing current-win field and link is exact. It retains the earlier isolated H26M current-win variant unchanged. Decimal odds and potential return are derived in memory from the already validated fixed probability and stake; the source projection is not rewritten.

The existing win renderer adds only the derived odds and potential return to its current sentence. No new screen, card, layout, or control exists.

## Fail-closed evidence

The Brain Admin self-check accepts the complete automatic chain and rejects each tested alteration without returning selected team, balance, or command linkage:

- QA substituted for the non-QA automatic record;
- isolated H26M and automatic H26AN identities mixed;
- altered decision command;
- wrong return due or payout delta;
- wrong entry count, payout balance, or final balance;
- stale/foreign result identity;
- tampered replay seal; and
- missing finalization command.

The retained isolated current win, retained legacy win, both approved loss variants, and approved void histories continue to validate. The validator and API read leave projection bytes and mtime unchanged.

## Verification

- Focused exact H26AO projection/API check: PASS.
- Brain Admin `--check`: PASS.
- Python compilation: PASS.
- Canonical Python `3.12.13`: `105/105` PASS in `145.919s`.
- Deterministic league export: unchanged SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: unchanged SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged native boundary audit: `42/42` PASS.
- Unchanged package boundary: `50` files, `1,048,557,679` bytes, zero `.py`, `.pyc`, or `.pyd` files.
- Authoritative SaveGame: unchanged `10,658` bytes, SHA-256 `78c3e43ddc4c0e63e671187dc2b81a35e633ef6de2bddd5a6bf25871bbbfdc29`.
- Source projection: unchanged `4,407` bytes, SHA-256 `95b7c7d5c35626aae7fcb13ab0c88b1cb20b92fb7037f2eb31abc19bf28116fc`.
- Static card audit: one existing reconciliation card, three output fields, zero mutation controls.
- Browser QA at `1280x800`: exact automatic status and values readable and unclipped; document client/scroll widths both `1265`; target card right edge `1244.79`; no overflowing elements; zero console errors.

Unreal source and packaged content are unchanged, so Ponytail correctly skipped a no-op rebuild and reused the accepted H26AO `42/42` native and package evidence. A preliminary full-Python command used non-allowlisted Python `3.13` and was rejected by the frozen supervisor allowlist; it is not accepted evidence. The canonical allowlisted `3.12.13` run above is the accepted result. An initial browser discovery had no available runtime and made no visual claim; the final browser evidence above is the accepted visual gate.

## Scope boundary and next gate

H26AP proves one read-only Admin history compatibility gate only. It does not create a player receipt for the automatic H26AN/H26AO command chain, another settlement action, generalized history, multiple wagers, variable stakes, correction, later markets, online authority, backend, deployment, retraining, simulator change, or brain change.

Stop for fresh Scope Director review. The smallest possible follow-up is Phase 1H.26AQ: allow the existing H26AL ticket-booth receipt to accept this one exact automatic command chain without creating another receipt system.
