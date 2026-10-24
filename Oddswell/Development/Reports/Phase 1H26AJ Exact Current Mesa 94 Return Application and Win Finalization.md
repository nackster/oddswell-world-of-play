# Phase 1H.26AJ - Exact Current Mesa 94 Return Application and Win Finalization

## Outcome

The owner-approved H26AI Mesa/`40` winning decision now advances through the existing server-owned atomic win finalizer exactly once.

The final state is:

- stake ledger: sequence `2`, `-40`, balance `60`;
- payout ledger: sequence `3`, `+94`, reason `match_winner_payout`, balance `154`;
- win finalization: one `settled_won` record with gross return applied `94`;
- ledger entry count: `3`; and
- H26AI decision: still immutable as `decided_pending_apply`.

The applied return remains the exact H26AI integer result:

`floor(40 * 100000000 / 42413307) = 94`

## Minimal implementation

Ponytail reused the existing v1 win-finalization record, append-only Odds Bucks ledger, atomic SaveGame write, duplicate/conflict rules, and validated-load projection contract. One shared exact-terms helper now recognizes either:

1. the retained approved probability-`40000000`, return-`100`, balance-`160` win; or
2. the fixed current probability-`42413307`, return-`94`, balance-`154` win.

No schema, API, dependency, service, UI, market, or parallel payout system was added.

## Integrity evidence

The dedicated isolated QA test reconstructs the exact current `c929f90b...` offer, Mesa request, H26G lock, `79-113` result link, and H26AI decision before finalization.

- Altering return due from `94` to `95` rejects without changing the tampered bytes.
- The exact finalization appends only one `+94` entry and one finalization.
- A cold validated load restores balance `154`, three entries, and one win finalization.
- Exact retry returns `Duplicate` without changing bytes.
- A conflicting second finalization rejects without changing bytes.
- The retained H26AI decision-only test, H26M Harbor-loss test, and legacy win test all pass unchanged.

The existing validated-load contract also regenerates the existing v1 reconciliation projection with probability `42413307`, return `94`, payout `94`, final balance `154`, and net `+54`. H26AJ does not claim independent Brain Admin validation or a player-facing receipt for that projection.

## Verification

- Focused H26AJ native automation: `1/1` PASS.
- Retained H26AI native automation: `1/1` PASS.
- Retained H26M Harbor-loss automation: `1/1` PASS.
- Retained legacy `+100` win automation: `1/1` PASS.
- Full native OddsWell automation: `40/40` PASS.
- Frozen Python regression: `77/77` PASS in `164.055s`.
- Supervisor regression: `28/28` PASS in `2.819s`.
- Combined Python evidence: `105/105` PASS.
- Brain Admin `--check`: PASS.
- Python compilation: PASS.
- Deterministic public league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic archived replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.
- Unreal editor build: PASS.
- Unreal Windows Development game build: PASS in `20.45s`.
- Explicit `Bootstrap+SundaleGraybox` Windows BuildCookRun: PASS in `32.15s`.
- Package audit: `50` files, `1,048,388,223` bytes, zero Python files.
- Cost: `$0.00`.

## Scope boundary and next gate

H26AJ applies and finalizes only the exact current Mesa/`40` return. It does not add a player Mesa wager route, expose a win receipt, independently validate the current win in Brain Admin, generalize offers or history, add multiple wagers or markets, change basketball simulation, change any brain, add a backend, or connect real money.

The next implementation requires fresh Scope Director review. The smallest candidate is Phase 1H.26AK: independently validate and display the current exact win reconciliation through the existing read-only Brain Admin Operations card.
