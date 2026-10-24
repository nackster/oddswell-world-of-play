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

# Phase 1H.26AF — Automatic Exact Current-Chain H26M Loss Decision on Local Resume

## Outcome

Authoritative non-QA local GameMode startup now advances the one fixed durable H26L result link through the existing parameterless H26M loss-decision transition. A normal packaged launch, with no QA flag, linked Harbor City Waves `79`–`113` Mesa Vista Sol and then persisted one exact Harbor-selected loss decision.

The decision binds offer `c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d`, result `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`, and decision `canonical:h26m:match_winner:decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`. It records Harbor selected, Mesa winner, stake `40`, outcome `lost`, gross return due `0`, and status `decided_pending_apply`. The ledger remains two entries and balance `60`, with one request, lock, result, and decision and zero win or loss finalizations.

## Minimal implementation

Ponytail reused `DecideOddsWellCanonicalMatchWinnerLossDecision`; no new settlement primitive exists. After H26AE proves the exact durable result link, one private GameMode method invokes H26M, accepts `Decided` or exact `Duplicate`, reloads the full wager state, and verifies ledger `2/60`, one request, one lock, one current result, one current decision, and zero finalizations before updating memory.

Cold H26M state causes the parameterless H26L wrapper to reject its no-downstream prerequisite before H26L can report a duplicate. H26AF recognizes only the two existing exact prerequisite errors, then requires H26M to return `Duplicate`, requires the exact current decision, and repeats the durable-chain verification. Missing private H26L evidence still exits before the wrapper. Tampered private result evidence still rejects before the fallback.

No timer, polling loop, watcher, service, process, Python launcher, caller input, new path, command-line flag, schema, dependency, simulator behavior, brain behavior, H26N finalization, H26O projection, or H26P receipt was added.

## Fail-closed boundary

The fresh path runs only after H26AE durably proves the fixed H26L result. The cold path cannot accept a new decision: it requires the existing H26M transition to return exact `Duplicate`. Both paths independently require the fixed current command IDs, Harbor/Mesa identity, `40` stake, `lost` outcome, return due `0`, `decided_pending_apply`, ledger count `2`, balance `60`, exactly one request/lock/result/decision, and no finalization.

Missing result evidence is a locked no-op. Tampered result evidence is rejected. Altered identity, conflicting decision, downstream state, third ledger entry, nonzero return, winning outcome, and failed persistence remain covered by the retained H26M transition tests and cannot update GameMode memory. H26N–H26P remain separate gates.

## Corrective evidence retained

Three preliminary rejected logs are retained for audit and are not the final accepted proof:

- `Accepted/H26AF-Accepted.log` records the first packaged attempt. H26AE linked the exact result and H26M persisted the exact decision, but H26AF reported `durable_reload_failed` because the new exact-result helper and fixture used `oddswell-private-result-recorder-v1` while the persisted record correctly used `oddswell-private-game-result-recorder-v1`. Local Odds Bucks authority failed closed; H26N–H26P did not run.
- `Accepted/H26AF-Accepted-Final2.log` records the same rejection after an editor-only rebuild accidentally left the packaged game executable on the preliminary binary. The persisted H26M SaveGame was still the exact expected `8,332`-byte artifact, H26AF rejected authority, H26P stayed unavailable, and no H26N or later mutation occurred.
- `Accepted/H26AF-ColdDuplicate.log` records the next cold-restart boundary discovery. The parameterless H26L wrapper returned its generic exact-prerequisite rejection before the narrower downstream-state error, so the preliminary fallback did not invoke H26M `Duplicate`. The SaveGame bytes, SHA-256, and mtime remained unchanged; no H26AF acceptance or H26N–H26P mutation occurred.

The first correction changed only the helper/fixture literal to the persisted `oddswell-private-game-result-recorder-v1`, rebuilt both editor and game targets, and repackaged. The second correction recognizes the wrapper's existing exact generic prerequisite error only as permission to attempt the already-strict H26M duplicate check; it still requires H26M to return `Duplicate`, the exact current decision fields, and a successful durable-chain reload. A missing result exits before the wrapper, and tampered private evidence returns a different error and never enters this fallback.

The final accepted evidence is `Accepted/H26AF-Accepted-SourceFinal.log` and `Accepted/H26AF-ColdDuplicate-SourceFinal.log`. Those source-final runs prove `Decided` and byte/hash/mtime-stable `Duplicate` respectively, with zero H26N finalizations and no H26P success.

## Packaged proof

- Final Windows package: `50` files, `1,048,153,214` bytes, zero Python files. The source-clean build/package passed in `146.01s`; the final scoped archive refresh passed in `45.42s`.
- Normal no-QA launch: H26AE `Linked`, then H26AF `Decided`; score `79-113`, Mesa winner, Harbor stake `40`, outcome `lost`, return due `0`, ledger entries `2`, balance `60`, requests/locks/results/decisions `1/1/1/1`, and finalizations `0/0`.
- The accepted SaveGame is `8,332` bytes with SHA-256 `48749e724bb21b0d0fa0e668389fa378c16f9534f9f12c43c2c18dc63697fa9c`.
- Cold normal no-QA launch: exact H26AF `Duplicate`; SaveGame bytes, SHA-256, and UTC mtime `2026-07-29T08:18:10.1420402Z` stayed unchanged.
- Missing-result lane: locked H26AE `NOOP`; no H26AF or H26N–H26P output. The H26W SaveGame stayed `5,502` bytes with SHA-256 `74acbe35ef6a374a9efaced5d85a60e62f49f33659553bc8dd7633f89ded2525` and unchanged UTC mtime `2026-07-28T20:44:14.8220464Z`.
- Tampered-result lane: H26AE `REJECTED` before H26AF; the same H26W bytes, hash, and mtime remained exact. No H26N–H26P state appeared.
- H26P remained unavailable after both accepted launches because H26N has not run.
- H26A/H26B/H26C/H26H stayed at their exact source hashes. The H26W handoff and receipt, H26X seal, and H26Y result also stayed exact: `1f5996d1...`, `4e2a1f37...`, `bcf8fc46...`, and `cbadfb97...` respectively.

## Validation

- Editor and game Win64 Development builds: PASS.
- Focused H26AF automation: `1/1` PASS.
- Retained H26AE and H26M focused automation: `1/1` each PASS.
- Full native OddsWell automation: `36/36` PASS.
- H26W/H26X/H26Y supervisor tests: `28/28` plus `13` subtests PASS in `2.43s`.
- Canonical Python `3.12.13` timing-sensitive life-brain evaluation: PASS in `56.38s` at verified High priority.
- Full frozen Python regression: `105/105` plus `119` subtests PASS in `135.71s` at verified High priority.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Eight clean canvas JSON parses and diff hygiene: PASS.
- Cost: `$0.00`.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26AF-20260729`.

## Next gate

Stop for Scope Director review. Automatic H26N finalization is the smallest possible next phase. H26O/H26P publication, generalized history, multiple wagers, correction, later markets, online authority, backend authority, and simulator or brain changes remain separate unapproved gates.
