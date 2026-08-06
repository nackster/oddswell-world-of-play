# Phase 1H.26G — Server-Owned Exact Canonical Game-Start Lock

## Result

**COMPLETE for the exact Phase 1H.26E canonical request only.**

Phase 1H.26G adds one parameterless authoritative transition that can append one separate immutable game-start lock at the exact H26A tipoff. It does not start a game, simulate play, create a result, decide or settle a wager, or expand the request model.

## Proven chain

The transition independently reloads and validates:

1. H26A schema-v1 Season `1`, Game `1`, Harbor City Waves home versus Mesa Vista Sol away, `scheduled_unplayed`, exact server tipoff.
2. H26B schema-v1 equal-public prediction commitment.
3. H26C exact canonical Match Winner offer.
4. Current Odds Bucks schema `12` with exactly:
   - sequence `1`: `+100` job credit;
   - sequence `2`: `-40` `match_winner_stake`;
   - balance `60`;
   - one Harbor request at probability `57586693`, odds `17365`, gross return `69`;
   - status `accepted_pending_lock`;
   - no prior lock, result, decision, settlement, or finalization.

Only server-observed time equal to the H26A tipoff may cross the boundary. The public production transition accepts no timestamp, offer, team, stake, command, or lock ID from a caller. It owns a stable H26G command and persists one separate lock linked to Season `1`, Game `1`, the exact request, and the exact offer.

## Invariants

- The request remains `accepted_pending_lock`; its accepted time, offer evidence, selection, stake, odds, payout convention, and gross return are unchanged.
- Ledger sequences `1` and `2`, balance `60`, and job cooldown remain unchanged.
- H26A, H26B, and H26C bytes, SHA-256 hashes, and UTC mtimes remain unchanged.
- The lock record is separate, immutable, idempotent, and exact-retry safe.
- Early, late, missing, malformed, migrated, multiple, conflicting, downstream, tampered-upstream, or persistence-failure evidence rejects without mutation.
- No player-controlled timestamp or lock command exists.

## Player-facing proof

After lock, the existing Sundale ticket booth renders one `MATCH WINNER UNAVAILABLE / LOCKED` panel. It displays no pending receipt, teams, prices, selections, result, or wager controls. The visual route is read-only and preserved all four SaveGame files byte-for-byte.

Rendered evidence:

- `client/OddsWell/Saved/Screenshots/Windows/Phase1H26G_CanonicalPostLockBooth.png`
- `1280 × 800`, visually inspected for legibility and partial-state absence.

## Validation evidence

- Focused native automation: `OddsWell.League.CanonicalMatchWinnerLock`, `1/1`.
- Full native automation: `24/24`.
- Frozen Python regressions: `68/68` across groups `9 + 2 + 8 + 46 + 3`.
- Phase 1H odds contracts: `3/3`.
- Brain Admin self-check: PASS.
- Python compilation: PASS.
- Unreal editor build: PASS.
- Unreal game build: PASS.
- Final explicit-Sundale Windows BuildCookRun: PASS in `51.11s`.
- Final package: `50` files, `1,046,598,926` bytes.
- Packaged H26E seed → exact H26G lock → post-lock visual → cold duplicate → conflict rejection → cleanup: PASS.
- League export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Replay seal: `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.
- Canvas JSON parsing, diff hygiene, cleanup, and zero lingering OddsWell/Unreal processes: PASS.
- Cost: `$0.00`.

Retained logs:

- `client/OddsWell/Saved/Logs/Phase1H26G_Focused.log`
- `client/OddsWell/Saved/Logs/Phase1H26G_Full.log`
- `client/OddsWell/Saved/Logs/Phase1H26G_PackagedH26ESeed.log`
- `client/OddsWell/Saved/Logs/Phase1H26G_PackagedLock.log`
- `client/OddsWell/Saved/Logs/Phase1H26G_PackagedPostLockVisual.log`
- `client/OddsWell/Saved/Logs/Phase1H26G_PackagedColdVerify.log`

## Boundary and next gate

This phase adds no normal selection/editor/confirmation route, simulation, game result, wager decision, settlement, history projection, correction, multiple-request behavior, later market, backend/account, payment, real money, deployment, retraining, simulator change, or brain behavior.

The next candidate is Scope Director review of the smallest authoritative post-lock canonical game prerequisite. No Phase 1H.26H work has begun.
