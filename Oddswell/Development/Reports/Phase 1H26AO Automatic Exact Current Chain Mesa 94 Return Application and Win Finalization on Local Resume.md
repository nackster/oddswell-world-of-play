# Phase 1H.26AO — Automatic Exact Current-Chain Mesa +94 Return Application and Win Finalization on Local Resume

**Date:** 2026-07-30
**Status:** COMPLETE
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

Normal non-QA local startup now advances the exact durable H26AN Mesa win decision through the existing H26AJ finalizer. It appends exactly one payout entry and persists exactly one immutable win finalization:

- ledger sequence `3`;
- command `canonical:h26aj:match_winner:win-finalization:05a4a2a...`;
- delta `+94`;
- reason `match_winner_payout`;
- balance `154`;
- outcome `won`;
- status `settled_won`;
- gross return applied `94`;
- observed ledger count `3`.

The linked H26AN decision remains immutable as `decided_pending_apply`.

## Minimal implementation

Ponytail full mode reused `FinalizeOddsWellMatchWinnerWin` directly. One private startup method owns the fixed H26AJ finalization command and H26AN decision command, accepts only `Finalized` or exact `Duplicate`, reloads the complete state, and verifies the exact request, lock, result, decision, ledger, and finalization before updating memory.

No new finalizer, schema, service, process, timer, watcher, dependency, market, input surface, reconciliation writer, Admin card, or player receipt was added.

## Safety and retained behavior

Focused native coverage combines the H26AO exact predicate with the existing H26AJ/H26AN engine tests and full ledger regression. Missing, partial, altered-return, mixed, foreign, conflicting-finalization, wrong-result, anomalous-ledger, and failed-write evidence changes nothing. The H26AJ test now also proves that a read-only SaveGame rejects the payout without a partial balance or finalization.

The retained Harbor-loss route passes unchanged with two ledger entries, balance `60`, and no payout.

Validated finalization reload regenerates the existing read-only H26AK projection as retained behavior. Its bytes and mtime are not claimed stable. H26AO adds no independent history validation, and the H26AL player receipt deliberately remains unavailable for the H26AN/H26AO command chain.

## Validation

- focused native H26AO: `1/1`;
- focused retained H26AJ: `1/1`;
- focused retained H26AN: `1/1`;
- focused retained H26AG: `1/1`;
- full native OddsWell suite: `42/42`;
- frozen Python modules: `77/77` in `144.155s`;
- supervisor modules: `28/28` in `2.545s`;
- Brain Admin `--check`: passed;
- Python compilation: passed;
- final Unreal editor and game builds: passed;
- final explicit `Bootstrap+SundaleGraybox` BuildCookRun: passed in `88.90s`;
- final package: `50` files, `1,048,557,679` bytes, zero `.py`, `.pyc`, or `.pyd` files.

The accepted final package used no QA flags:

- fresh resume produced H26AO `Finalized`;
- cold resume produced H26AO `Duplicate`;
- the final SaveGame is `10,658` bytes with SHA-256 `78c3e43ddc4c0e63e671187dc2b81a35e633ef6de2bddd5a6bf25871bbbfdc29`;
- its bytes, hash, and mtime remained exact on cold resume;
- no H26AL receipt READY marker appeared;
- missing-result and tampered-result lanes exited cleanly, never reached H26AO, and preserved SaveGame bytes, hash, and mtime.

During validation, a preliminary compatibility allowlist made the retained receipt accept the automatic chain. The runtime audit caught that scope expansion. The allowlist was removed, all final native builds/tests and the package were regenerated, and only the corrected final package and runtime lanes above are accepted evidence.

## Boundary

Phase 1H.26AO proves only automatic return application and finalization for one exact current Mesa/`40` chain. Independent read-only Admin validation or a player receipt for this automatic command chain requires a separate gate. Generalized history, multiple wagers, variable stakes, correction, later markets, online authority, backend, deployment, retraining, and brain/simulator changes remain out of scope.
