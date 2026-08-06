# Phase 1H.26AQ — Read-Only Player-Facing Exact Automatic Mesa Win Receipt Compatibility

**Date:** 2026-07-31
**Status:** COMPLETE
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The existing ticket-booth receipt now accepts the one exact normal H26AM-H26AO automatic Mesa win chain:

- `BET SETTLED — WIN`;
- Mesa Vista Sol selected and won;
- stake `40`;
- final Harbor `79-113` Mesa;
- returned `94`;
- net `+54`;
- ledger count `3`;
- balance `154`; and
- one close instruction.

The retained isolated H26AL Mesa win and both approved loss receipts remain exact.

## Minimal implementation

Ponytail full mode reused the existing H26AL loader, receipt data, native HUD, close behavior, and ticket-booth direction cue. The current-win authority predicate now accepts either the exact isolated H26AI decision command or the exact automatic H26AN decision command, while requiring the finalization to link to the same accepted decision.

No new receipt system, screen, widget, schema, endpoint, projection, dependency, wager, payout, settlement action, simulator behavior, or brain behavior was added.

## Fail-closed evidence

The receipt reads the authoritative SaveGame directly. It does not read or create the H26AP projection and performs no reconciliation or authoritative write.

The complete automatic chain is required. The following tested variants return no receipt and expose no partial fields:

- pending H26AN without H26AO;
- partial automatic chain;
- mixed isolated H26AI and automatic H26AN identities;
- altered return;
- altered payout-command linkage;
- altered payout ledger;
- altered final balance;
- altered result;
- altered replay seal; and
- altered decision-to-result linkage.

Every accepted and rejected receipt read preserves the source bytes and mtime.

## Verification

- Focused automatic authority and negative automation: PASS `1/1`.
- Focused receipt presentation automation: PASS `1/1`.
- Final native automation: PASS `42/42`.
- Canonical Python `3.12.13`: PASS `105/105` in `142.154s`.
- Brain Admin `--check`: PASS.
- Python compilation: PASS.
- Editor and game builds: PASS.
- Fresh explicit `Bootstrap+SundaleGraybox` BuildCookRun: PASS.
- Final Windows package: `50` files, `1,048,614,511` bytes, zero Python artifacts.
- Exact packaged receipt source before and after the interaction: `10,658` bytes, SHA-256 `78c3e43ddc4c0e63e671187dc2b81a35e633ef6de2bddd5a6bf25871bbbfdc29`, unchanged mtime `2026-07-31T04:21:47.1328700Z`.
- Game-native `1280x800` receipt capture: `928,782` bytes, SHA-256 `981108f2eaf4185e19707151ca7c6c51c41e7cd84b0c627024fa160fe47a9239`; all exact values are readable and unclipped.
- Packaged QA interaction: receipt opened, closed, left, and reopened in one bounded process; source bytes and mtime remained stable, and the runtime marker reports `projection=false`, `writer=false`, and `mutation=false`.

The packaged evidence is a bounded exact-state UI proof. It does not claim generalized history, a complete normal-player lifecycle, cold-restart receipt behavior, multiple wagers, or variable values.

The packaged process also exercised the pre-existing validated-load startup behavior, which regenerated `MatchWinnerReconciliationQA.json` and `OddsBucksReconciliationQA.json` before the receipt interaction. Those files are disclosed startup output, not receipt input or receipt output. The focused authority test is the no-projection receipt proof: it deletes the Match Winner projection, reads the exact automatic receipt, verifies the projection remains absent, and verifies the authoritative SaveGame remains unchanged.

## Scope boundary and next gate

H26AQ proves compatibility for one fixed automatic command chain only. It does not add generalized receipt history, multiple wagers, variable stakes, correction, later markets, online authority, backend, deployment, retraining, simulator change, or brain change.

Stop for fresh Scope Director review before selecting another implementation phase.
