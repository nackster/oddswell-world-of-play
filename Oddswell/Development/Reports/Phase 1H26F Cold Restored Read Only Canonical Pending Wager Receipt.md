# Phase 1H.26F — Cold-Restored Read-Only Canonical Pending Wager Receipt

## Outcome

**COMPLETE** for one exact active local-beta H26E request only.

Before authoritative tipoff, the existing stadium ticket-booth browser can cold-restore the accepted canonical request and show a concise, read-only receipt:

- `BET ACCEPTED`
- `PENDING TIPOFF`
- Harbor City Waves
- stake `40` Odds Bucks
- potential gross return `69`
- balance `60`
- authoritative tipoff and lock time

Technical request, offer, command, and ledger IDs remain off-screen. Match Winner cards remain noninteractive.

## Smallest implementation

Ponytail reused the existing H18 cold validation approach and H24/H26D HUD. It added one phase-specific reader instead of a generalized receipt service, dependency, schema, widget tree, or history framework.

The reader loads the current SaveGame directly and exposes a receipt only after independently verifying:

- exact H26A schedule, H26B public commitment, and H26C canonical offer;
- Odds Bucks schema `12` with no migration required;
- exactly one sequence-`1` `+100` job credit and one sequence-`2` `-40` `match_winner_stake` debit;
- balance `60`;
- one H26E evidence-version-`1` request for Harbor City Waves;
- probability `57586693`, decimal odds integer `17365`, stake `40`, and potential gross `69`;
- `accepted_pending_lock`, server-owned accepted time, and canonical tipoff/lock;
- no lock, result, decision, cancellation, finalization, settlement, refund, correction, or other downstream evidence.

The output object is cleared before validation and assigned only after the complete record passes.

## Player behavior and failure boundary

- A valid pretipoff request replaces the H26D read-only offer slip with the pending receipt.
- No request preserves the H26D read-only offer.
- Missing, multiple, orphaned, stale-schema, mismatched, tampered, or downstream evidence fails closed.
- At or after tipoff without an authoritative canonical lock, the booth makes no pending, locked, or settled claim. If the no-request H26D offer is already open as tipoff arrives, its teams and prices clear immediately into the unavailable/locked panel without close/reopen.
- Opening, switching tabs, closing, leaving the frontage, returning, reopening, and cold restarting never call acceptance and never debit.
- The receipt reader performs zero migration, reconciliation, save, or deletion work.

This phase adds no normal selection/editor/confirmation route, game-start lock, result, settlement, history, multiple-request model, later market, backend/account, payment, real-money path, deployment, retraining, simulator, or brain behavior.

## Validation evidence

### Native and frozen regressions

- Focused automation: the exact receipt plus held-open no-request tipoff regressions passed `2/2`.
- Full Unreal automation: `23/23` passed.
- Phase 1H odds contracts: `3/3` passed in `0.08s`.
- Frozen Python suite: `68` tests and `16` subtests passed in `125.24s`.
- Brain Admin self-check passed.
- Python `compileall` passed.
- Final correction-source editor and game builds passed.
- Fresh correction-source Windows BuildCookRun passed in `51.66s`.
- Final correction package: `50` files, `1,046,411,022` bytes.

### Packaged cold-process proof

A fresh package process created the exact H26E state. A separate cold H26F process then opened, switched tabs, closed, left the frontage, returned, and reopened the receipt. All four persisted files retained identical bytes, SHA-256, and UTC modification times:

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| H26A schedule | `2,771` | `73808dcf0668e7e383febafc18e72458386965765d7152caeab76842b42d895c` |
| H26B commitment | `5,153` | `ae9ec48201771f176011ad2a48c76e07865957fe2a4c0c821c6abf201e98a7bc` |
| H26C offer | `2,960` | `ccf17fa66e3964da1063ef0027945ee2c36147f557e08ac6ffff00481d66cf25` |
| QA ledger/request | `4,791` | `036bf29c0d96cbe89cb5a49404c303a7e0cd186f959c86766f1cadde08a75556` |

Separate packaged proofs also showed:

- a valid no-request state preserves H26D with ledger count `0`, balance `0`, and zero mutation;
- the older H17 QA request is rejected with no partial receipt and byte-stable persisted state;
- accepted, cold-view, missing, and rejected runs exit without fatal errors or ensures.

The retained rendered frame `Phase1H26F_CanonicalPendingReceipt.png` was inspected at `1280×800`: the receipt is legible, unclipped, IDs are hidden, and the cards are visibly read-only.

### Held-open tipoff correction

Coordinator review found that H26F receipt polling had accidentally narrowed the older H26D tipoff expiry to states that already contained a receipt. The same phase was corrected by restoring unconditional visible-offer expiry while retaining independent receipt revalidation.

The final native test `OddsWell.League.CanonicalPendingReceiptHeldOpenMissingTipoff` holds a no-request offer open, advances the observed server time to the exact lock, and proves that the menu stays open while the offer and receipt evidence clear. The resulting HUD path is therefore `MATCH WINNER UNAVAILABLE / LOCKED`, with no teams or prices. QA ledger existence and bytes remain unchanged.

A fresh correction package repeated the proof across two processes. The first created exact H26A/H26B/H26C with no request, ledger entries `0`, and balance `0`. The second held the menu open at exact tipoff and logged:

- `offer_cleared=true`;
- `receipt=false`;
- `locked_panel=true`;
- `teams=false`;
- `prices=false`;
- entries and balance `0/0` before and after;
- `request_api=false`, `debit=false`, `write=false`, and `close_reopen=false`.

All three canonical files retained their exact lengths, hashes, and UTC modification times:

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| H26A schedule | `2,771` | `09c3d52ce9a279c35463512632ff4f03bafe85b13a95e033f0fe79b7efe4cf56` |
| H26B commitment | `5,153` | `ea59e03178bd9b911af0e1c3c91ffe9d87716e0ed33e0174b9451f5843bffee4` |
| H26C offer | `2,960` | `406e692b6c6c2d3a823db3d46c3bd0e55ae38b24e0c3134a4b93ab537f52af10` |

The retained `1280×800` frame `Phase1H26F_HeldOpenMissingTipoffLocked.png` was visually inspected: it cleanly shows the locked panel and explicitly states that no teams, prices, selections, or wager controls are shown.

### Unchanged deterministic evidence

- League export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Cost: `$0.00`.

## Next candidate gate

Scope Director review of the smallest server-owned canonical game-start lock for this exact request. Phase 1H.26G has not begun.
