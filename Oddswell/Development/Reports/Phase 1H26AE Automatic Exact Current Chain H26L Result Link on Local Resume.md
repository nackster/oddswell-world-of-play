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

# Phase 1H.26AE — Automatic Exact Current-Chain H26L Result Link on Local Resume

## Outcome

Authoritative non-QA local GameMode startup now links the one fixed externally recorded canonical result when its private evidence is present. A normal packaged launch, with no QA flag, restored exact H26W state and H26X/H26Y evidence and appended the existing H26L link for Harbor City Waves `79`–`113` Mesa Vista Sol.

The link binds offer `c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d`, result `05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289`, and replay `35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db`. The ledger remains two entries, balance `60`, with one request, one lock, and one result link.

## Minimal implementation

Ponytail reused the existing parameterless `LinkOddsWellCanonicalMatchWinnerResult` transition and fixed private evidence directories. One startup method runs after authoritative Odds Bucks load, only outside isolated QA routes. It checks whether result evidence exists, delegates all validation and atomic persistence to H26L, accepts only `Linked` or exact `Duplicate`, then reloads the full wager state and verifies one identical durable link with no downstream decision or finalization before updating the in-memory ledger.

No polling, timer, watcher, process, Python launcher, path, command-line flag, SaveGame field, schema, dependency, simulator behavior, brain behavior, payout, refund, H26M decision, H26N finalization, H26O history, or H26P receipt was added.

## Fail-closed boundary

Missing private result evidence is a locked no-op. The strict H26L transition still rejects missing seals, malformed or noncanonical JSON, altered keys/types/bytes/hashes, commitment/input/receipt/digest/seal/replay mismatches, wrong season/game/team/score/winner, archived formats, multiple files, conflicting links, downstream state, and failed persistence without repair.

After any accepted transition, the GameMode independently reloads the durable state and requires ledger `2/-40/60`, one request, one lock, one byte-for-byte equivalent result record, and zero decisions or finalizations. A mismatch disables local Odds Bucks authority before any in-memory update or tipoff scheduling. Existing H26AD receipt code and coverage are unchanged.

## Packaged proof

- Fresh Windows package: `50` files, `1,048,110,718` bytes, zero Python files; BuildCookRun passed in `67.4s`.
- Normal no-QA launch: `Linked`, exact `79-113` Mesa result, ledger entries `2`, balance `60`, requests/locks/results `1/1/1`, H26M-H26P absent, booth locked.
- Cold normal no-QA launch: exact `Duplicate`; the linked SaveGame stayed `6,745` bytes with SHA-256 `9050093af31f496ecbed53e58cd3ef4d04d5c6fac227f69fc71f71a67ae14258` and unchanged UTC mtime `2026-07-29T07:23:52.9917430Z`.
- Missing-result lane: locked `NOOP`; the H26W SaveGame stayed `5,502` bytes with SHA-256 `74acbe35ef6a374a9efaced5d85a60e62f49f33659553bc8dd7633f89ded2525` and unchanged UTC mtime `2026-07-28T20:44:14.8220464Z`; no H26O projection appeared.
- Tampered-result lane: `REJECTED` before mutation with the same exact H26W bytes, hash, and mtime; no H26O projection appeared.
- The H26A/H26B/H26C/H26H SaveGames and H26W handoff/receipt, H26X seal, and H26Y result retained exact source hashes. The seal file remained SHA-256 `bcf8fc469c90720af0acf31ff9c8c87209ae43674c1fd3b1336444357361416f`; the result file remained SHA-256 `cbadfb9730c5de673b8c76b0a6cf88391a9968ae5c67a43dedae930b0ec8481b`.

## Validation

- Editor and game Win64 Development builds: PASS.
- Focused H26AE startup-gate automation: `1/1` PASS.
- Retained strict H26L automation: `1/1` PASS.
- Full native OddsWell automation: `35/35` PASS.
- H26W/H26X/H26Y supervisor tests: `28/28` plus `13` subtests PASS in `2.43s`.
- Canonical Python `3.12.13` timing-sensitive life-brain evaluation: PASS in `56.34s` at verified High priority.
- Full frozen Python regression: `105/105` plus `119` subtests PASS in `135.04s` at verified High priority.
- Brain Admin self-check and Python compilation: PASS.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Eight clean canvas JSON parses and diff hygiene: PASS.
- Cost: `$0.00`.

Evidence is retained under `client/OddsWell/Saved/Evidence/Phase1H26AE-20260729`.

## Next gate

Stop for Scope Director review. Automatic H26M-H26P, generalized history, multiple wagers, correction, later markets, online authority, backend authority, and simulator or brain changes remain separate unapproved gates.
