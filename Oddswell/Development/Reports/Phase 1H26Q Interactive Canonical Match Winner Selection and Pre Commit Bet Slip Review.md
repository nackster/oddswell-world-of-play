# Phase 1H.26Q - Interactive Canonical Match Winner Selection and Pre-Commit Bet-Slip Review

## Result

**COMPLETE for review of the exact active H26A/H26B/H26C local-beta offer only.**

At the existing physical stadium ticket booth, a player can now:

- select Harbor City Waves or Mesa Vista Sol with mouse, keyboard, or controller;
- adjust an in-memory stake from `10` to `100` Odds Bucks in increments of `10`; and
- review the selected team, immutable decimal odds, exact integer-formula potential gross return, current balance, and game-start lock rule.

The slip always states `REVIEW ONLY - WAGER NOT PLACED` (with an em dash in the rendered HUD). There is no confirm or submit action.

## Minimal implementation

The phase reuses the existing H24 native HUD and hitboxes, the H26C immutable offer preview, the existing keyboard/controller bindings, and the established integer payout formula. Review state consists of only one selection index and one stake value on the existing character. No dependency, service, framework, schema, persistence type, writer, API, or generalized betting form was added.

## State and trust boundary

- Review exists only while an exact validated H26A/H26B/H26C offer is available before tipoff.
- Pending and settled receipts retain precedence over review.
- Close, leave, reopen, and cold restart reset selection and stake.
- Exact tipoff clears the offer and review and exposes the existing locked panel.
- Invalid or malformed upstream evidence exposes only `BET SLIP UNAVAILABLE`, with no partial team, odds, stake, or return values.
- Margin, Overtime, and Player Props remain visibly locked and publish no odds.
- No confirmation, request, debit, lock transition, receipt, SaveGame write, or ledger mutation is reachable from this UI.

## Exact return evidence

For stakes `10,20,...,100`, the integer formula `floor(stake * 100000000 / win_probability_e8)` produced:

- Harbor (`57586693`, decimal `1.7365`): `17, 34, 52, 69, 86, 104, 121, 138, 156, 173`;
- Mesa (`42413307`, decimal `2.3577`): `23, 47, 70, 94, 117, 141, 165, 188, 212, 235`.

## Validation

- Unreal Editor build: PASS.
- Focused native H26Q automation: `1/1`.
- Full native OddsWell automation: `32/32`.
- Frozen simulator/brain/league/odds contracts: `77` tests and `106` subtests.
- Brain Admin Python compilation and self-check: PASS and unchanged.
- Unreal Win64 Development game build: PASS.
- Explicit `Bootstrap+SundaleGraybox` BuildCookRun: PASS in `58.22s`.
- Package: `50` files, `1,047,827,422` bytes, zero Python files.
- Deterministic league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Packaged interactive QA: PASS for both teams, all ten stake increments, exact returns, mouse/keyboard/controller routes, close/reopen/leave reset, later-tab safety, no request/debit/ledger mutation, and exact-tipoff clearing.
- Separate cold packaged process: all three H26A/H26B/H26C SaveGames retained identical byte lengths, SHA-256 values, and mtimes; screenshot count remained unchanged; no ledger SaveGame was created.
- Rendered `1280x800` inspection: selected Mesa at `2.3577`, stake `40`, gross `94`, current balance, game-start lock, review-only label, and all controls were legible and unclipped.
- Diff hygiene, canvas JSON, package log audit, and zero lingering OddsWell/Admin processes: PASS.
- Cost: `$0.00`.

## Future boundary

The owner's live/in-game odds and optional roughly 20-minute presentation ideas are recorded as **OPEN POST-BETA targets** in the Version 1 Game Bible. Beta remains immutable pregame odds with an inherited roughly two-to-five-minute presentation target. No live repricing, duration expansion, simulator/brain change, backend, dependency, or deployment work was added.

## Next gate

Scope Director review must select the smallest truthful dependency after the interactive review slip. Normal confirmation/placement, correction, generalized player history, multiple requests, later markets, live odds, backend, deployment, retraining, simulator changes, and brain behavior remain separate unproved gates.
