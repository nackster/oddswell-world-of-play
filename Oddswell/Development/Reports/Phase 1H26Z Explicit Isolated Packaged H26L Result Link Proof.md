# Phase 1H.26Z — Explicit Isolated Packaged H26L Result-Link Proof

**COMPLETE for one fixed exact H26W/H26X/H26Y evidence chain only.**

## Result

H26Z proves that the existing packaged H26L native transition can consume the exact externally produced H26X seal and H26Y result without a production-code change. The proof used one disposable local QA directory cloned from the exact H26W pre-link state, staged the two immutable JSON records only after their file hashes matched, and invoked the existing packaged `-CanonicalMatchWinnerResultLinkQa` entrypoint once.

Ponytail reused the existing H26L transition, automation, QA entrypoints, H26U package, and fixed private paths. No launcher, supervisor, watcher, service, automatic chain, dependency, process bridge, simulator change, brain change, settlement path, UI, Admin feature, or public artifact was added.

## Exact input chain

- Commitment: `335d8b798898627d3a39ad092b303487241a52b5659c0b0b2b1fa21e8c9ea1e7`.
- H26W handoff: `7,102` bytes, SHA-256 `1f5996d1382932f80262b0f816ee7cffd06237983cc6039fccfb28a736984225`.
- H26W receipt: `515` bytes, SHA-256 `4e2a1f37a63658055ff78c80c6fd145d93df85db8aa075373590d65ee8aa75a5`.
- H26X seal file: `671` bytes, SHA-256 `bcf8fc469c90720af0acf31ff9c8c87209ae43674c1fd3b1336444357361416f`; canonical seal SHA-256 `580932546f3041bb3961cf14757b536c31c289d91f984fd0ae1418b98f0ff4ef`.
- H26Y result file: `660` bytes, SHA-256 `cbadfb9730c5de673b8c76b0a6cf88391a9968ae5c67a43dedae930b0ec8481b`; canonical record SHA-256 `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`.
- Replay SHA-256: `35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db`.

The restored H26W ledger was `5,502` bytes with SHA-256 `74acbe35ef6a374a9efaced5d85a60e62f49f33659553bc8dd7633f89ded2525`. Before H26L it contained exactly the job `+100` and Harbor stake `-40` entries, balance `60`, one Harbor/`40` request, one exact H26G lock, and zero result links, decisions, finalizations, cancellations, refunds, or payouts.

## Accepted packaged proof

The existing packaged transition returned `PASS` and `linked`. It appended exactly one immutable result link to the exact request, lock, H26Y record, and H26X seal:

- Harbor City Waves `79`, Mesa Vista Sol `113`;
- winner Mesa Vista Sol;
- exact H26Y replay digest and result command derived from record SHA-256 `05a4a2a1…`;
- ledger entries `2`, stake delta `-40`, balance `60`, result links `1`; and
- decisions, finalizations, cancellations, refunds, and payouts all `0`.

The resulting ledger is `6,745` bytes with SHA-256 `9050093af31f496ecbed53e58cd3ef4d04d5c6fac227f69fc71f71a67ae14258` and UTC mtime `2026-07-28T21:48:00.5071582Z`. The H26A schedule, H26B commitment, H26C offer, H26H execution commitment, H26W handoff/receipt/attempt/log, H26X seal, and H26Y result retained exact bytes and hashes. No simulation or settlement ran.

## Fail-closed and duplicate evidence

Three independent clones of the same pre-link state proved rejection before SaveGame mutation:

- missing H26Y result;
- changed `home_score` with the original record hash retained; and
- archived-result schema/recorder labels substituted at the private H26K path.

Each run returned `FAIL`. Every rejected ledger stayed exactly `5,502` bytes, SHA-256 `74acbe35ef6a374a9efaced5d85a60e62f49f33659553bc8dd7633f89ded2525`, and UTC mtime `2026-07-28T20:44:14.8220464Z`.

An exact clone of the linked state then ran the existing packaged cold-duplicate verifier. It returned `PASS`, `duplicate`, `cold_process_restore=true`, and `duplicate_byte_stable=true`, with one result link and the same score, winner, replay, request, lock, ledger, and balance. The canonical accepted ledger retained its exact `6,745` bytes, SHA-256, and mtime. The verifier removed only its disposable QA clone during its existing cleanup step.

## Validation

- Packaged accepted, missing, tampered, archive-format, and cold-duplicate lanes: PASS for their expected outcomes.
- Focused H26L native automation: PASS `1/1`.
- Full native Unreal automation: PASS `34/34`.
- Combined H26W/H26X/H26Y supervisor tests: PASS `28/28` in `2.736s`.
- Full Python simulator/brain/league/odds/execution suite: PASS `105/105` in `140.394s`.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Unchanged H26U package: `50` files, `1,047,999,614` bytes, zero Python files.
- All eight canvases parse; relevant lingering processes: `0`; cost: `$0.00`.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26Z-20260728`.

## Boundary and next gate

H26Z proves one explicit isolated H26L link only. It does not make H26L automatic and creates no H26M decision, H26N finalization, H26O history, H26P receipt, correction, generalized wager, service, backend, player/Admin feature, simulator change, or brain change.

The next Scope Director review may consider only whether one separate explicit H26M decision invocation against this exact linked evidence is the smallest truthful next proof. No automatic H26L–H26P chain is authorized.
