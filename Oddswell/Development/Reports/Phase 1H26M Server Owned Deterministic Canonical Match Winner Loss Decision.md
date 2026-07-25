# Phase 1H.26M — Server-Owned Deterministic Canonical Match Winner Loss Decision

## Result

**COMPLETE for the exact active Harbor-selected, Mesa-winner H26E/H26G/H26L chain only.**

Phase 1H.26M adds one parameterless native authority transition. It reloads the exact canonical schedule, pregame commitment, offer, schema-`12` request/debit, game-start lock, and immutable result link before appending one deterministic loss decision.

## Authority transition

The transition accepts no caller command, request, lock, result, offer, team, score, winner, stake, outcome, return, schema, version, time, or path.

It requires:

1. exact H26A schema-v1 Season `1`, Game `1` schedule;
2. exact H26B equal-public pregame commitment;
3. exact H26C canonical Match Winner offer;
4. schema `12`, ledger sequence `1` `+100`, sequence `2` `-40`, balance `60`, and one exact H26E Harbor request for stake `40`;
5. exactly one exact H26G game-start lock;
6. exactly one private H26L result link whose command suffix is a lower-case H26K record SHA-256 and whose authoritative winner is Mesa Vista Sol;
7. no cancellation, void, loss finalization, win finalization, refund, payout, or other later state.

The decision command is derived solely from the H26L result command and H26K record identity:

`canonical:h26m:match_winner:decision:<H26K record_sha256>`

The transition reuses the existing deterministic Match Winner decision primitive. The immutable record binds the approved decision schema/version and exact offer, request, lock, and result identities, Harbor City Waves selected, Mesa Vista Sol authoritative winner, stake `40`, outcome `lost`, gross return due `0`, and status `decided_pending_apply`.

## Mutation boundary

The accepted transition appends exactly one decision. It preserves:

- ledger entries `2`, deltas `+100/-40`, and balance `60`;
- the H26E request, H26G lock, and H26L result link;
- all eight H26A–H26K canonical/private evidence files byte-, SHA-256-, and mtime-identically;
- zero loss/win/void finalizations;
- zero cancellation, refund, payout, balance credit, or decision application.

An exact cold retry returns duplicate without rewriting the SaveGame. Stale schema, changed request/debit/lock, archived-result substitution, a Harbor-winning non-loss result, downstream cancellation or void state, foreign decision identity, already-finalized state, and native write failure reject with zero mutation. Existing archived loss/win/void chains remain valid and unchanged.

## Packaged proof

A fresh explicit-Sundale Windows package passed in `50.42s`. It contains `50` files totaling `1,047,353,310` bytes and zero Python files.

The fresh package's newly created server-owned game ended Harbor `115`–`101` Mesa. Work stopped before H26L/H26M on that chain because it was not the authorized loss outcome. No result field, seed, time, or score was changed; this remains retained fail-closed evidence.

With Coordinator authorization, the current H26M binary then restored the retained verified H26L loss state as test evidence. Nine source files matched the retained H26L source hashes, lengths, and mtimes exactly before execution: eight H26A–H26K canonical/private files plus the schema-`12` H26L ledger. The restored result was Harbor `97`–`101` Mesa, record `e4b8b4e26126612e1173b4509c67666df44cfcf7082b51051e9de0097f45d0c6`, replay `efe7575962c88e9b8b4fcfcb6357c5307c6eeedd828b4b8f532c6e5eae985f62`.

The restored H26L ledger started with SHA-256 `fba19eeecb6e2dc5ae09e1ce19bfade53d0634559876d4791cc0f0b2b64ca9a0`, length `6,745`, and its retained mtime. H26M appended one decision and produced SHA-256 `09f2bc8a989b97f9213b836f0356ebd60075d9039401690b3f883add59b567e1`, length `8,332`, while the ledger remained `2/-40/60`. The eight separate upstream files remained byte/hash/mtime exact. A cold packaged retry returned duplicate, verified byte stability, and removed the QA ledger. The accepted decision ledger remains in the isolated audit backup.

A separate missing-H26C packaged rejection returned `rejected`, exposed no partial decision, retained decisions `0`, and preserved the original H26L ledger hash, length, and mtime exactly.

## Validation

- Focused native H26M trust-boundary automation: `1/1`.
- Full native OddsWell automation after the final evidence-log correction: `28/28`.
- Frozen simulator/brain/league plus odds and retained H26I/H26J/H26K contracts: `77` tests and `106` subtests passed in `122.93s`; this includes the frozen `68/68` and retained private-chain `9/9`.
- Brain Admin self-check: PASS.
- Python compilation: PASS.
- Unreal editor and game builds: PASS.
- Deterministic public league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic archived replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Canvas JSON parsing and repository diff hygiene: PASS.
- Cost: `$0.00`.

Retained logs:

- `client/OddsWell/Saved/Logs/Phase1H26M_FocusedNative.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_FullNative.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_FrozenPytest.out.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_BuildCookRun.out.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_PackagedDecision.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_PackagedMissingOfferRejection.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_PackagedDuplicateCleanup.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_LeagueExport.log`
- `client/OddsWell/Saved/Logs/Phase1H26M_ReplayExport.log`

The final package is `C:\Users\reali\AppData\Local\Temp\OddsWell_Phase1H26M_Final_20260725_113639`. The `MesaLossProof` QA ledger is absent after duplicate cleanup; its `AuditAcceptedDecision` copy retains the accepted decision evidence.

## Boundary and next gate

This phase records decision evidence only. It adds no finalization, application, credit, payout, refund, reconciliation/history, player UI, Admin surface, replay publication, statistics, standings, correction, multiple-request support, backend, deployment, retraining, simulator change, or brain behavior.

The next candidate is Scope Director review of the smallest server-owned exact loss-finalization prerequisite after H26M. No Phase 1H.26N work has begun.
