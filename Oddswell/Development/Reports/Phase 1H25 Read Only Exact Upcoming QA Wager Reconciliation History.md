# Phase 1H.25 — Read-Only Exact Upcoming QA Wager Reconciliation/History

**Status:** COMPLETE
**Date:** July 23, 2026
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The exact noncanonical H17-to-H22 Match Winner QA chain now appears in the existing Brain Admin Operations reconciliation card after finalization. The phase reuses the established `oddswell-match-winner-reconciliation-v1` file, live API endpoint, independent validator, and one read-only card. It adds no new endpoint, card, schema, dependency, framework, or mutation control.

The accepted chain is fixed to offer `4a30feca21ab8dfb8a3f64ca642aadcdb33743b07a7cedf49b6b743f1c6f2f31`, request `qa:h17:match_winner:request:1`, lock `qa:h19:match_winner:lock:1`, cancellation/evidence `qa:h20:match_winner:cancellation:1` / `qa:h20:match_winner:cancellation:evidence:1`, decision `qa:h21:match_winner:void-decision:1`, and finalization `qa:h22:match_winner:void-finalization:1`.

## Exact visible evidence

- Season `100`, Game `1`, Sundale Sparks, stake `40`.
- Accepted at `2100000000`; locked at `2100086400`; canceled at `2100086700`.
- Cancellation `game_canceled` / `closed_canceled`.
- Decision `voided`, refund due `40`, status `decided_void_pending_refund`.
- Ledger sequence `2`, `-40`, `match_winner_stake`, balance `60`.
- Ledger sequence `3`, `+40`, `match_winner_refund`, balance `100`.
- Finalization `settled_void`, refund applied `40`, entry count `3`, final balance `100`, net `0`.

The packaged projection was `3,529` bytes. The live API returned `VALIDATED QA FINALIZED VOID` with the exact command and ledger linkages. The existing page and Operations card container returned HTTP `200`; the optional interactive browser backend was unavailable, so this report makes no visual-browser claim.

## Fail-closed boundary

Missing, stale, partial, mixed normal-result/void, wrong-offer, wrong-link, or otherwise tampered Season `100` evidence returns an unavailable payload with no partial team, balance, or linkage values. Cold load regenerates the exact projection. Rejected persisted mutations remove stale projection data. Exact retry remains duplicate-safe and the separate packaged cold verifier proves the rejection matrix and byte-stable zero mutation before cleanup.

The exact loss, win, and Season `99` void validators and card behavior remain unchanged. The deterministic league fixture remains `30,288` bytes with SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`. The deterministic replay remains `421` frames and `256,442` bytes with SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` and seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H22/H25 automation | `1/1` passed |
| Full native OddsWell automation | `17/17` passed |
| Frozen simulation and odds contracts | `68/68` passed in `163.162s` across five groups |
| Brain Admin self-check | Passed |
| Final editor / game builds | Passed in `12.00s` / `17.55s` |
| Fresh Windows Development BuildCookRun | Passed in `44.03s`; `50` files / `1,045,635,342` bytes |
| Packaged H17 → H22 chain | Five separate processes passed |
| Packaged cold verifier | Duplicate, rejection audit, zero mutation, history, and cleanup passed |
| Live Admin API / page | Exact payload passed; HTTP `200`; no controls |
| Deterministic league / replay exports | Exact prior hashes preserved |
| Canvas JSON / Python compilation / diff hygiene | Passed |

## Ponytail boundary

The phase removes one deliberate Season `100` publication suppression and extends the existing exact void validator with one fixed constant set. It does not generalize wagers, add an abstraction, or duplicate the Operations UI.

## Truth boundary and next gate

This is one machine-local noncanonical QA history proof, not canonical future-game submission, a correction workflow, generalized player history, a later market, account/backend authority, payment, deployment, retraining, simulator behavior, or brain behavior.

The next Scope Director review should choose the smallest remaining Match Winner requirement among correction, canonical future-game integration, or broader player history. Every later market remains separately gated.
