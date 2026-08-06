# Phase 1H.26AB — Explicit Isolated Packaged H26N Loss-Finalization Proof

**COMPLETE for one fixed exact H26W–H26AA evidence chain under Scope Director Decision A.**

## Result

H26AB proves that the existing packaged parameterless H26N transition can consume the exact H26AA decided state without a production-code or runtime change. The proof cloned the accepted isolated H26AA user directory and invoked only the existing packaged `-CanonicalMatchWinnerLossFinalizationQa` entrypoint once.

Ponytail reused the existing H26N transition, automation, QA entrypoints, H26U package, and exact H26AA evidence. No H26O publisher, endpoint, validator, card, history consumer, H26P receipt, UI/Admin feature, launcher, trigger, watcher, service, dependency, process bridge, simulator change, brain change, or automatic chain was added or executed.

## Exact before state

The starting schema-`12` H26AA SaveGame was `8,332` bytes, SHA-256 `48749e724bb21b0d0fa0e668389fa378c16f9534f9f12c43c2c18dc63697fa9c`, and UTC mtime `2026-07-28T22:05:22.4282342Z`. It contained:

- exactly two ledger entries, deltas `+100/-40`, and balance `60`;
- one exact Harbor/`40` request, one H26G lock, and one H26L result link;
- one H26Y-derived H26M decision with Harbor selected, Mesa winner, `lost`, gross return due `0`, and `decided_pending_apply`; and
- zero loss/win finalizations, cancellations, voids, refunds, payouts, applications, or history.

## Accepted packaged proof

The unchanged package returned `PASS` and `finalized`. H26N appended exactly one immutable loss finalization derived from the H26Y record identity:

- command `canonical:h26n:match_winner:finalization:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- exact H26M decision, H26E request, H26G lock, and H26L result links;
- schema/version `oddswell-match-winner-loss-finalization-v1` / `match-winner-loss-finalization-v1`;
- Harbor City Waves selected, Mesa Vista Sol authoritative winner, stake `40`, outcome `lost`;
- gross return due/applied `0`, status `settled_lost`; and
- observed ledger count `2` and observed balance `60`.

The H26M decision remains `decided_pending_apply`. The finalized SaveGame is `10,082` bytes, SHA-256 `4cb4a0f70d45feef46da1dfb88f6086b05b85fbb82fcb90148c3e08dc66f9366`, and UTC mtime `2026-07-28T22:20:03.1103768Z`. There is no third ledger entry, credit, payout, refund, return application, win finalization, cancellation, void, correction, history, player receipt, UI, or simulation.

The four canonical SaveGames plus exact H26W handoff/receipt, H26X seal, and H26Y result all retained exact bytes, SHA-256, and mtimes through finalization and cleanup.

## Decision A: transient QA projection and cleanup

Whole-user-directory comparison found that the pre-existing H26N finalization loader writes `Saved/Admin/MatchWinnerReconciliationQA.json` while validating a finalized QA state. The `4,025`-byte file has SHA-256 `4494f6354cdc425ac18854e69131a2e784c523af9ec68692b9c35536e709059c` and UTC mtime `2026-07-28T22:20:03.1297218Z`.

This is existing H26N behavior, not an H26O invocation or a new Admin feature. The accepted command line contains only `-CanonicalMatchWinnerLossFinalizationQa`; its log contains zero H26O/H26P or reconciliation-QA command/evidence markers and explicitly reports `history=false`, `ui=false`, and `admin=false`.

Under Scope Director Decision A, a byte-identical projection copy is retained only as audit evidence under `TransientArtifacts`, outside the accepted user directory. The finalized SaveGame is likewise retained byte-identically under `AcceptedFinalizedEvidence`, outside the disposable user directory. The isolated accepted user directory was then cleaned of the Match Winner projection, its pre-existing unrelated Odds Bucks QA projection, and the disposable QA ledger. After cleanup it contains zero Admin files and zero QA ledger; the audit SaveGame retains exact bytes, SHA-256, and mtime, and every upstream authority file remains exact. No new or retained H26O/UI/Admin feature artifact remains in the accepted user directory.

## Rejection and duplicate evidence

A packaged clone with H26C absent returned `FAIL` and `rejected`. Its H26AA SaveGame retained exact `8,332` bytes, SHA-256 `48749e724bb21b0d0fa0e668389fa378c16f9534f9f12c43c2c18dc63697fa9c`, and UTC mtime `2026-07-28T22:05:22.4282342Z`.

Focused H26N trust-boundary automation separately proved pre-mutation rejection for stale schema, altered request/debit/lock/result identity, nonzero return, a winning result, a third ledger entry, downstream win/cancellation/void state, foreign finalization identity, and native persistence failure.

An exact clone of the finalized state ran the existing packaged cold-duplicate verifier. It returned `PASS`, `duplicate`, `cold_process_restore=true`, and `duplicate_byte_stable=true`, preserving the same finalization and ledger state. Its existing cleanup removed only that disposable clone's QA ledger and transient projection. The accepted audit SaveGame remained exact.

## Validation

- Packaged accepted, missing-H26C rejection, and cold-duplicate lanes: PASS for their expected outcomes.
- Focused H26N native trust-boundary automation: PASS `1/1`.
- Full native Unreal automation: PASS `34/34`.
- Combined H26W/H26X/H26Y supervisor tests: PASS `28/28` in `2.521s`.
- Full Python simulator/brain/league/odds/execution suite: PASS `105/105` in `142.563s`.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged H26U package: `50` files, `1,047,999,614` bytes, zero Python files.
- All eight canvases parse; relevant lingering processes: `0`; cost: `$0.00`.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26AB-20260728`.

## Boundary and next gate

H26AB proves one explicit isolated H26N loss finalization only. It does not make H26N automatic and adds or executes no H26O reconciliation/history consumer, H26P receipt, player/Admin surface, correction, generalized wager, service, backend, simulator change, or brain change.

The six-phase H26W–H26AB proof chain is complete. Any next phase requires a fresh Scope Director review; the smallest candidate is a separate explicit read-only H26O reconciliation/history proof. No automatic H26L–H26P chain is authorized.
