# Phase 1H.26AH — Normal Player Settled-Loss Receipt Lifecycle Proof

## Outcome

The committed H26AH.1 Windows package now has normal-player proof for the complete bounded receipt lifecycle:

1. follow the existing settled-receipt direction cue to the Sundale ticket booth;
2. open the exact settled-loss receipt;
3. close it, leave the booth, return, and reopen it; and
4. cold restart the package, follow the cue again, and reopen the identical receipt.

No QA receipt flag or teleport flag was used. This phase changes no production code.

## Visible receipt

Both accepted game-native `1280x800` screenshots are readable and unclipped. Each contains exactly one close instruction and the same player-facing values:

- `BET SETTLED — LOSS`
- `Harbor City Waves selected`
- `Stake 40 Odds Bucks`
- `Final Harbor 79–113 Mesa`
- `Winner Mesa Vista Sol`
- `Returned 0`
- `Net -40`
- `Balance 60`
- `E or ESC: CLOSE`

The first capture followed open, close, leave, and reopen in one normal process. The second capture followed a full process close and cold restart, then normal cue-following and receipt open.

## Authority and persistence

H26P loads the exact validated SaveGame directly. Its runtime marker reports `projection=false|write=false`, and the H26P interaction invokes no H26O writer, projection, or mutation. The existing H26N startup loader may regenerate its existing H26O projection before H26P runs, so this proof makes no global H26O byte or mtime stability claim.

The authoritative save stayed exact through every open, close, movement, reopen, process close, and cold reopen:

- size: `10,082` bytes;
- SHA-256: `4cb4a0f70d45feef46da1dfb88f6086b05b85fbb82fcb90148c3e08dc66f9366`; and
- UTC mtime: `2026-07-29T08:59:10.0144689Z`.

The first and cold-start logs both loaded `/Game/Maps/SundaleGraybox`, returned H26AG `Duplicate`, exposed H26P `READY` for final score `79-113`, and retained ledger count `2` with balance `60`.

## Evidence

Evidence lane: `client/OddsWell/Saved/Evidence/Phase1H26AH-20260730/OwnerNormalLifecycle-f5eef2d-20260730-101716`

- normal lifecycle log: `Owner-Normal-Lifecycle.log`;
- cold-restart log: `Owner-Normal-Cold-Restart.log`;
- normal reopen capture: `UserDir/Saved/Screenshots/Windows/ScreenShot00000.png`, `963,453` bytes, SHA-256 `b77f30889dfcb8f119d84e17e20dbc7c5ba0c05d9c501a04b9255be78ccdaf26`;
- cold-restart reopen capture: `UserDir/Saved/Screenshots/Windows/ScreenShot00001.png`, `851,890` bytes, SHA-256 `9fda81b8ee32b5638d24aac4d2057816a1f356a7e7bfa3e9c4132c553a122a59`; and
- both captures: `1280x800`, readable and unclipped.

## Verification

- Focused H26AG automatic-finalization regression: `1/1` PASS.
- Combined H26AD/H26P authority and negative-state regression: `1/1` PASS. It proves direct authoritative receipt state, rejects missing, tampered, partial, H26M-only, mixed, and archived substitutes, exposes no partial fields on rejection, and does not mutate source bytes.
- Focused H26P presentation regression: `1/1` PASS. It verifies all nine visible lines, exactly one close instruction, and no internal IDs, hashes, seeds, private athlete values, offers, or requests.
- Full native OddsWell automation: `38/38` PASS.
- Canonical Python 3.12 regression: `105/105` PASS in `142.230s`.
- Separate supervisor regression: `28/28` PASS in `2.615s`.
- Brain Admin supported `--check`: PASS.
- Python compilation: PASS.
- Deterministic public league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic archived replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.
- Relevant game processes after proof: `0`.
- Cost: `$0.00`.

Because H26AH adds no production change beyond committed H26AH.1, its already-valid editor/game builds, BuildCookRun, and exact package are reused truthfully. That exact package produced the lifecycle evidence and contains `50` files totaling `1,048,234,622` bytes with zero Python files.

## Scope boundary

H26AH is proof-only for one exact validated settled-loss receipt in the committed local Windows package. It adds no navigation system, minimap, generalized receipt history, multiple wagers, correction, later markets, online authority, backend, deployment, retraining, simulation change, or brain change. The next implementation requires a fresh Scope Director decision.
