# Phase 1H.26R - Exact Harbor/40 Canonical Wager Placement

## Result

**COMPLETE for one Harbor City Waves, `40` Odds Bucks request against the exact active H26A/H26B/H26C local-beta offer only.**

The existing ticket-booth slip now supports a real two-confirm player action with mouse, keyboard, or controller. Harbor at `40` is the sole eligible combination. The first confirmation visibly changes the slip to `ARMED - CONFIRM AGAIN TO PLACE` while the request count stays `0`, the ledger stays at the existing job-credit entry, and balance stays `100`. The second confirmation creates the durable pending request and receipt.

## Minimal implementation

- Reused the H26Q selection/stake slip and native HUD.
- Reused the H17 two-confirm interaction shape.
- Added one parameterless player-to-server RPC and one parameterless canonical Harbor/`40` wrapper.
- Reused H26A/H26B/H26C authority, H26E atomic request/debit persistence, and H26F receipt loading.
- Added no schema, writer, service, dependency, generalized submit form, or new ledger operation.

## Authority and atomic result

The client sends no offer ID, team, stake, odds, time, or command identity. On the second confirmation, the server independently reloads exact H26A/H26B/H26C evidence, derives the current offer ID, Harbor selection, stake `40`, immutable probability/odds, UTC acceptance time, and stable H26E command, then invokes the existing atomic primitive.

The accepted state is exactly:

- one request with status `accepted_pending_lock`;
- Harbor City Waves, probability `57586693`, decimal odds `1.7365`;
- stake `40`, potential gross return `69`;
- ledger sequence `1` job credit `+100`;
- ledger sequence `2` linked stake debit `-40`;
- one request, two ledger entries, balance `60`; and
- the existing H26F `BET ACCEPTED / PENDING TIPOFF` receipt only after durable success.

## Interaction safety

- Mesa, every stake other than `40`, no selection, insufficient balance, invalid evidence, or a later market cannot arm and displays placement unavailable.
- Team/stake changes, tab changes, close, leave, Escape, reopen, and tipoff clear the transient arm.
- A repeated confirmation after the receipt creates no second request or debit.
- Pending and settled receipts retain precedence over selection and placement.
- The retained H26E automation again proves exact duplicate, conflicting team/stake, invalid offer, insufficient funds, tipoff, H26A/H26B/H26C tamper, and native persistence-failure rejection with zero persisted mutation.

## Validation

- Unreal Editor build: PASS.
- Focused native H26R automation: `1/1`.
- Full native OddsWell automation: `33/33`.
- Frozen simulator/brain/league/odds contracts: `77` tests and `106` subtests.
- Brain Admin Python compilation and self-check: PASS and unchanged.
- Unreal Win64 Development game build: PASS.
- Final explicit `Bootstrap+SundaleGraybox` BuildCookRun: PASS in `65.45s`.
- Package: `50` files, `1,047,902,846` bytes, zero Python files.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Packaged normal route: PASS for job `100` -> ticket booth -> Harbor `40` -> first confirmation -> second confirmation -> pending receipt.
- Retained `1280x800` armed and accepted screenshots: visually inspected, legible, and unclipped.
- Separate packaged cold restore: PASS; H26A, H26B, H26C, and ledger files retained exact byte lengths, SHA-256 hashes, and mtimes.
- Cost: `$0.00`.

## Boundary and next gate

H26R does not auto-run H26G through H26P. It adds no automatic lock, simulation, result, decision, settlement, payout, refund, history publication, correction, Mesa placement, other stake, multiple request, later market, live odds, backend, deployment, retraining, simulator change, or brain behavior.

Scope Director review must choose the next smallest truthful dependency.
