# Phase 1H.26AN — Automatic Exact Current-Chain Mesa Win Decision on Local Resume

**Date:** 2026-07-30
**Status:** COMPLETE
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

Normal non-QA local startup now advances one exact current Mesa Vista Sol/`40` wager from its durable H26L result link to one immutable H26AN win decision. The decision is Mesa selected, Mesa winner, `won`, gross return due `94`, and `decided_pending_apply`.

This phase stops before money moves. The authoritative ledger remains two entries, `+100/-40`, with balance `60`. There is no payout, sequence-`3` ledger entry, win finalization, reconciliation publication, or player receipt.

## Minimal implementation

Ponytail full mode reused the existing strict settlement decision engine:

- one parameterless current-Mesa wrapper owns the exact command and fixed current identities;
- the existing startup resume route reads the persisted request and selects either the retained Harbor-loss wrapper or the new current-Mesa-win wrapper;
- after `Decided` or exact `Duplicate`, startup reloads the whole SaveGame and validates the complete pending decision before updating memory;
- no new schema, service, process, timer, watcher, dependency, input surface, or generalized decision abstraction was added.

The exact accepted decision is:

- offer `c929f90b...`;
- result `05a4a2a...`, Harbor `79`, Mesa `113`, winner Mesa;
- request/lock/result/decision counts `1/1/1/1`;
- Mesa selected, stake `40`, probability `42413307`;
- outcome `won`, gross return due `94`, status `decided_pending_apply`;
- ledger count `2`, balance `60`;
- win/loss finalization counts `0/0`.

## Failure and idempotency evidence

Focused automation rejects missing, partial, tampered, mixed, foreign, conflicting, wrong-result, and failed-write evidence without mutation. The retained Harbor automatic loss route remains exact.

A normal packaged fresh launch produced H26L `Linked` followed by H26AN `Decided`. A second cold launch produced exact H26AN `Duplicate`. The resulting SaveGame remained:

- size `8,372` bytes;
- SHA-256 `23515c3a9cad21c775c30b14eb135b73a65de012d8d0dca7b7f129f7c0dc440c`;
- identical mtime across the cold duplicate.

Separate missing-result and tampered-result packaged lanes did not reach H26AN and preserved the `5,519`-byte pre-result SaveGame byte-for-byte.

## Validation

- focused native H26AN: `1/1`;
- focused retained H26AI: `1/1`;
- focused retained H26AF: `1/1`;
- full native OddsWell suite: `41/41`;
- frozen Python modules: `77/77`;
- supervisor modules: `28/28`;
- Brain Admin `--check`: passed;
- Python compilation: passed;
- Unreal editor and game builds: passed;
- fresh `Bootstrap+SundaleGraybox` BuildCookRun: passed;
- package: `50` files, `1,048,503,407` bytes, zero `.py`, `.pyc`, or `.pyd` files;
- accepted packaged proof used no QA flags.

For setup only, an existing H26AI native test temporarily exported the exact pre-result Mesa request/lock fixture needed after the fixed offer tipoff had passed. That temporary export line was removed before the final editor rebuild and is not present in committed source or the accepted package. Earlier rejected setup attempts used a wrong map, a post-tipoff placement, or mixed chain state; none is accepted as phase evidence.

## Boundary

Phase 1H.26AN proves only the pending win decision. Applying the `94` return and recording `settled_won` would be a separate economy mutation requiring a fresh Scope Director gate. Reconciliation, receipt, generalized history, multiple wagers, variable stakes, correction, later markets, online authority, backend, and brain/simulator changes remain out of scope.
