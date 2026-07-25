# Phase 1H.26N — Server-Owned Exact Canonical Match Winner Loss Finalization

## Result

**COMPLETE for the exact retained Harbor-selected, Mesa-winner H26M loss chain only.**

Phase 1H.26N adds one parameterless native authority transition. It reloads the exact canonical schedule, pregame commitment, offer, schema-`12` request/debit, game-start lock, private result link, and deterministic loss decision before appending one immutable loss-finalization record.

## Authority transition

The transition accepts no caller command, request, lock, result, decision, offer, team, score, winner, stake, outcome, return, schema, version, time, or path.

It requires:

1. exact H26A schema-v1 Season `1`, Game `1` schedule;
2. exact H26B equal-public pregame commitment;
3. exact H26C canonical Match Winner offer;
4. schema `12`, ledger sequence `1` `+100`, sequence `2` `-40`, balance `60`, and one exact H26E Harbor request for stake `40`;
5. exactly one exact H26G game-start lock;
6. exactly one private H26L result link whose command suffix is a lower-case H26K record SHA-256 and whose authoritative winner is Mesa Vista Sol;
7. exactly one H26M decision linked to that identity, with Harbor selected, Mesa authoritative winner, stake `40`, `lost`, gross return due `0`, and `decided_pending_apply`;
8. no win finalization, cancellation, void, refund, payout, third ledger entry, or other later state.

The finalization command is derived solely from H26M and H26K identity:

`canonical:h26n:match_winner:finalization:<H26K record_sha256>`

The transition reuses the existing loss-finalization primitive. The immutable record binds the approved finalization schema/version and exact offer, request, lock, result, and decision identities, Harbor City Waves selected, Mesa Vista Sol authoritative winner, stake `40`, outcome `lost`, gross return applied `0`, status `settled_lost`, observed ledger count `2`, and observed balance `60`.

## Mutation boundary

The accepted transition appends exactly one loss finalization. It preserves:

- the H26M decision as `decided_pending_apply` with gross return due `0`;
- ledger entries `2`, deltas `+100/-40`, and balance `60`, with no third entry;
- the H26E request, H26G lock, and H26L result link;
- all eight separate H26A–H26K canonical/private evidence files byte-, SHA-256-, and mtime-identically;
- zero win/void finalizations, cancellation, refund, payout, balance credit, or decision application.

An exact cold retry returns duplicate without rewriting the SaveGame. Stale schema, changed request/debit/lock/result/decision, nonzero return, a Harbor-winning chain, foreign finalization identity, downstream state, a third ledger entry, and native write failure reject with zero mutation. Existing archived loss/win/void chains remain valid through the full regression suite.

No reconciliation/history feature or consumer was added. The reused primitive's existing read-only projection behavior remains unchanged; packaged duplicate cleanup removed the transient QA projection and ledger.

## Packaged proof

A fresh explicit-Sundale Windows package passed in `51.63s`. It contains `50` files totaling `1,047,528,414` bytes and zero Python files.

The current H26N binary restored the authorized retained H26M loss state as test evidence. The source chain was Harbor `97`–`101` Mesa, H26K record `e4b8b4e26126612e1173b4509c67666df44cfcf7082b51051e9de0097f45d0c6`, replay `efe7575962c88e9b8b4fcfcb6357c5307c6eeedd828b4b8f532c6e5eae985f62`, and H26M decision command with the same H26K suffix.

The source H26M ledger matched SHA-256 `09f2bc8a989b97f9213b836f0356ebd60075d9039401690b3f883add59b567e1`, length `8,332`, and retained mtime tick `639205979176541606`. H26N appended one finalization and produced SHA-256 `4731637ed326b5d139e328b8fab0cc8265c7efcf16e734f7d7dc35099e574997`, length `10,082`, while the ledger remained `2/+100,-40/60`. The eight separate upstream files remained byte/hash/mtime exact.

A cold packaged retry returned duplicate, verified byte stability, and removed the QA ledger and transient QA projection. The accepted finalization ledger remains in the isolated audit backup.

A separate missing-H26C packaged rejection exposed no finalization and preserved the source H26M ledger SHA-256, length, and mtime exactly. The retained fresh Harbor `115`–`101` Mesa packaged chain from H26M remains the real non-loss stop; H26N also directly exercises a structurally valid Harbor-winning rejection at its focused trust boundary without changing the authorized packaged loss evidence.

## Validation

- Focused native H26N trust-boundary automation: `1/1`.
- Full native OddsWell automation: `29/29`.
- Frozen simulator/brain/league plus odds and retained H26I/H26J/H26K contracts: `77` tests and `106` subtests passed in `124.78s`.
- Brain Admin self-check: PASS unchanged.
- Python compilation: PASS.
- Unreal editor and game builds: PASS.
- Deterministic public league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic archived replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Canvas JSON parsing and repository diff hygiene: PASS.
- Cost: `$0.00`.

Retained logs:

- `client/OddsWell/Saved/Logs/Phase1H26N_FocusedNative.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_FullNative.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_FrozenPytest.out.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_BuildCookRun.out.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_PackagedFinalization.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_PackagedMissingOfferRejection.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_PackagedDuplicateCleanup.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_LeagueExport.log`
- `client/OddsWell/Saved/Logs/Phase1H26N_ReplayExport.log`

The final package is `C:\Users\reali\AppData\Local\Temp\OddsWell_Phase1H26N_Final_20260725_121610`. The live `MesaLossProof` QA ledger is absent after duplicate cleanup; `AuditAcceptedFinalization` retains the accepted evidence.

## Boundary and next gate

This phase records exact loss-finalization evidence only. It adds no return application, ledger credit, payout, refund, new reconciliation/history surface, player UI, Admin surface, replay publication, statistics, standings, correction, multiple-request support, backend, deployment, retraining, simulator change, or brain behavior.

The next candidate requires Scope Director review of the smallest truthful dependency after exact loss finalization. No Phase 1H.26O work has begun.
