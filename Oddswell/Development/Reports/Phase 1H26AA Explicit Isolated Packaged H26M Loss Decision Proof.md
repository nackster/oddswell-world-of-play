# Phase 1H.26AA — Explicit Isolated Packaged H26M Loss-Decision Proof

**COMPLETE for one fixed exact H26W–H26Z evidence chain only.**

## Result

H26AA proves that the existing packaged H26M native transition can consume the exact H26Z-linked state without a production-code or runtime change. The proof cloned the accepted isolated H26Z user directory and invoked the existing packaged `-CanonicalMatchWinnerLossDecisionQa` entrypoint once.

Ponytail reused the existing H26M transition, automation, QA entrypoints, H26U package, and exact H26Z evidence. No decision input, launcher, supervisor, trigger, watcher, service, dependency, process bridge, simulator change, brain change, automatic chain, settlement application, UI, Admin feature, history, or public artifact was added.

## Exact before state

The starting schema-`12` ledger was `6,745` bytes, SHA-256 `9050093af31f496ecbed53e58cd3ef4d04d5c6fac227f69fc71f71a67ae14258`, and UTC mtime `2026-07-28T21:48:00.5071582Z`. It contained:

- exactly two ledger entries, deltas `+100/-40`, and balance `60`;
- one exact Harbor City Waves request for stake `40`;
- one exact H26G lock;
- one exact H26L link to H26Y record `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- Harbor City Waves `79`, Mesa Vista Sol `113`, and Mesa winner; and
- zero decisions, loss/win finalizations, cancellations, voids, refunds, payouts, credits, applications, or history.

## Accepted packaged proof

The unchanged package returned `PASS` and `decided`. H26M derived one immutable decision entirely from existing authoritative evidence:

- decision command `canonical:h26m:match_winner:decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`;
- exact H26E request, H26G lock, and H26L result-command links;
- schema/version `oddswell-match-winner-settlement-decision-v1` / `match-winner-settlement-decision-v1`;
- Harbor City Waves selected, Mesa Vista Sol authoritative winner;
- stake `40`, outcome `lost`, gross return due `0`; and
- status `decided_pending_apply`.

The resulting SaveGame is `8,332` bytes, SHA-256 `48749e724bb21b0d0fa0e668389fa378c16f9534f9f12c43c2c18dc63697fa9c`, and UTC mtime `2026-07-28T22:05:22.4282342Z`. It still has exactly two ledger entries and balance `60`, one request, one lock, one result link, and now one decision. No third ledger entry, credit, payout, refund, decision application, loss/win finalization, cancellation, void, history, UI, Admin projection, replay, statistics, or simulation was created.

The four canonical SaveGames and exact H26W handoff/receipt, H26X seal, and H26Y result all retained exact bytes, SHA-256, and mtimes.

## Rejection and duplicate evidence

A packaged clone with the H26C offer absent returned `FAIL` and `rejected` before mutation. Its H26Z ledger retained exact `6,745` bytes, SHA-256 `9050093af31f496ecbed53e58cd3ef4d04d5c6fac227f69fc71f71a67ae14258`, and UTC mtime `2026-07-28T21:48:00.5071582Z`, with decisions still `0`.

The focused H26M trust-boundary automation separately proved zero-mutation rejection for stale schema, changed request/debit/lock identity, archived-result substitution, a non-loss outcome, downstream cancellation/void state, a foreign decision identity, an already-finalized chain, and native persistence failure.

An exact clone of the decided state ran the existing packaged cold-duplicate verifier. It returned `PASS`, `duplicate`, `cold_process_restore=true`, and `duplicate_byte_stable=true`, retaining the same decision identity and exact ledger state. The canonical accepted SaveGame retained its exact `8,332` bytes, SHA-256, and mtime; the verifier removed only its disposable QA clone during existing cleanup.

## Validation

- Packaged accepted, missing-offer rejection, and cold-duplicate lanes: PASS for their expected outcomes.
- Focused H26M native trust-boundary automation: PASS `1/1`.
- Full native Unreal automation: PASS `34/34`.
- Combined H26W/H26X/H26Y supervisor tests: PASS `28/28` in `2.526s`.
- Full Python simulator/brain/league/odds/execution suite: PASS `105/105` in `136.766s`.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged H26U package: `50` files, `1,047,999,614` bytes, zero Python files.
- All eight canvases parse; relevant lingering processes: `0`; cost: `$0.00`.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26AA-20260728`.

## Boundary and next gate

H26AA proves one explicit isolated H26M loss decision only. It does not make H26M automatic and creates no H26N finalization, settlement application, reconciliation/history, player receipt, correction, generalized wager, service, backend, player/Admin feature, simulator change, or brain change.

The next Scope Director review may consider only whether one separate explicit H26N loss-finalization invocation against this exact decided evidence is the smallest truthful next proof. No automatic H26L–H26P chain is authorized.
