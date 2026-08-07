---
tags:
  - development
  - phase-1k
  - unreal
  - multiplayer
  - housing
  - evidence
status: complete-failed-measurement
date: 2026-08-06
---

# Phase 1K.9a — Networked Studio Correction and Job-Frontage Fail-Fast Measurement

## Outcome

**COMPLETE CORRECTION; FRESH COMPONENTS 1-2 PASSED; THE STUDIO PORTION OF COMPONENT 3 PASSED; FULL COMPONENT 3 FAILED/REMAINS INCOMPLETE AT THE JOB FRONTAGE.**

Phase 1K.9a corrected only the measured shared-city client boundary around the existing private Studio. A fresh packaged owner selected `masculine_tone_2`, joined the unchanged loopback peer, retained peer-visible normal movement, entered the private empty Studio with one normal rapid `E`, moved inside with normal `W`, exited with one normal rapid `E`, and rejoined the same peer at the exact saved Sundale vector.

The same fresh attempt then continued component 3 with normal foreground-verified `Shift` + `W/A/S/D` holds. At the Job frontage the route became camera/wall/wayfinding-confused. The attempt never retained an auditable exact Job prompt or exact arrival distance. It stopped before Job `E`, so full component 3 did not pass and components 4-8 were not reached.

## Smallest production correction

- A locally controlled `NM_Client` may use the existing Studio prompt and private transition; remote pawns, listen hosts, and dedicated servers remain rejected.
- Entry opens the existing private Bootstrap Studio and carries one bounded return option. Exit client-travels only to the fixed loopback shared-city endpoint.
- The listen server validates the one-shot return vector inside the existing `350 cm` Studio doorway boundary, consumes it once for that controller, and spawns at that exact vector.
- One Studio-only `IE_Pressed` latch preserves rapid normal `E` taps until the next poll. Held input remains disarmed until release, and every non-Studio `E` path is unchanged.
- The production housing slot remains `OddsWellStudioHome`, user index `0`, schema `1`.
- Empty Studio presentation now reports `snap_points=0`. The existing purchased three-part Modular Chair still activates exactly one fixed `studio_primary` point; no inventory, placement, or economy rule changed.

No generalized housing networking, visits, replicated interiors, backend, new UI, dependency, or framework was added. This is the Ponytail minimum measured correction.

## Verification before runtime

Evidence root: `C:\tmp\OddsWellPhase1K9aSnap-20260806T233000Z\Evidence`.

- Unreal Engine 5.8 editor build: PASS.
- Focused native `OddsWell.Character.ModularChairPurchaseGate`: `1/1` PASS.
- Focused native `OddsWell.Character.NetworkClientStudioTransition`: `1/1` PASS.
- Focused native `OddsWell.Character.StudioHomePersistence`: `1/1` PASS.
- Full native `OddsWell`: `50/50` PASS; log SHA-256 `FA35D9C2F00EF42585011B47F02413A270E3D222EBF61F1BB40EDC3073A44212`.
- Repository-pinned Python `3.12.13`: `9 + 2 + 8 + 46 + 40 = 105/105` PASS.
- Brain Admin `python -B -m brain_admin.server --check`: PASS; output SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Win64 Development game build: PASS.
- Fresh BuildCookRun: PASS; output SHA-256 `A21A9D8B33731AEA6C125303026C48AAD98D60EB663CA2265ACBC2EDCE1BE45A`; zero fatal/assert/ensure/nonzero-exit markers.
- Package: `50` files, `1,049,518,508` bytes, `0` Python files.
- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game executable SHA-256: `924BE91CFE643B6131F154DE7B4C0D4A3CECAB4C725DD91A39C83946FF73E6C3`.
- UFS manifest SHA-256: `0A6C630D63D8B072EC158743AB6D36818993A0B46537A1B94D5F765648CD4446`.

The first package attempt failed only during archive because the local Zen endpoint at `[::1]:8558` became unavailable. It is retained as failed evidence and is not the package used below. The clean retry and the final snap-corrected package both passed.

## Retained earlier failed Studio run

An earlier fresh rapid-input run proved the network-client entry/exit and exact shared return but reported the fresh Studio as `structure=6`, `furniture=0`, `decorations=0`, `snap_points=1`. The canonical component-3 contract requires `6/0/0/0`, so that run failed immediately and its later evidence was not spliced into the accepted attempt.

- Evidence root: `C:\tmp\OddsWellPhase1K9aLatchFresh-20260806T231900Z`.
- Owner log SHA-256: `C29FFEB8B02FFBE2D1E9C5CB64DD6C3458DDDF0674F8B4A80D321B49A449AD56`.
- Peer log SHA-256: `CA76D543FE6C2A50F5652D942EF43DE113BA647B1F437455E9CFAD6E2F86EA6A`.
- Failed READY marker: `structure=6|upgrade_surfaces=0|furniture=0|furniture_parts=0|decorations=0|snap_points=1`.

The subsequent snap-count correction changed only active presentation count. It preserves the existing fixed snap definition and later purchased-chair behavior.

## Fresh packaged evidence identity

- Package root: `C:\tmp\OddsWellPhase1K9aSnapPackage-20260806T233000Z\Windows`.
- Runtime root: `C:\tmp\OddsWellPhase1K9aSnapFresh-20260806T233000Z`.
- Passive peer wrapper/game PIDs: `7988` / `34996`; exact gameplay endpoint `127.0.0.1:17777`.
- Owner wrapper/game PIDs: `29184` / `5068`; normal default launch with no QA flag.
- Owner log: `103,704` bytes; SHA-256 `3E845685DF0198787089C63B57159476C3EF31D15547FDD1C587E492FCBABAA7`.
- Peer log: `102,868` bytes; SHA-256 `C194F5248BC8653154C89A6652E47060FED5B74428C33B4B9B65BCE7A9E3245B`.
- Peer gameplay inputs: `0`.
- Teleport, direct transform, QA locomotion, hidden repair, and save edit: `false`.

The fresh owner produced one production appearance save for `masculine_tone_2`, `2,183` bytes, SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`. The peer logged `clients=2` and accepted Player 2 with the same preset plus `starter_offwhite_top` and `starter_offwhite_bottom`. Fixed-view peer captures before and after normal owner movement are retained; the peer remained passive.

## Studio portion of component 3

One normal rapid `E` produced exactly one owner entry marker:

`ODDSWELL_STUDIO_TRANSITION|direction=to_studio|private=true|visits=false|shared_return=false`

The fresh private interior then emitted exactly one canonical READY marker:

`ODDSWELL_STUDIO_READY|result=PASS|private=true|visits=false|active_tier=studio|structure=6|upgrade_surfaces=0|furniture=0|furniture_parts=0|decorations=0|snap_points=0`

The owner visibly moved inside with a normal `900 ms` `W` input. One normal rapid `E` then emitted exactly one exit marker with `shared_return=true`. The owner browsed back with the saved vector:

- `X=132.78807207751788`
- `Y=200`
- `Z=108.14999904879816`

The same peer process logged:

`ODDSWELL_NETWORK_STUDIO_RETURN_RESTORED|location=V(X=132.79, Y=200.00, Z=108.15)|exact=true|source=bounded_client_travel_option|external_authority=false`

The server assigns the parsed vector directly with `AlwaysSpawn`; assignment error is `0 cm`. The owner returned visibly to the same doorway and peer membership returned to `clients=2`.

The production Studio save remained unchanged through interior movement, exit, and rejoin:

- Path: `C:\tmp\OddsWellPhase1K9aSnapFresh-20260806T233000Z\OwnerProfile\Saved\SaveGames\OddsWellStudioHome.sav`
- Size: `2,141` bytes.
- Mtime: `2026-08-06T23:45:41.6358614Z`.
- SHA-256: `350ADA9F7AA52808DDCA14F1EC03260D8F1E7201C6037B50A9F6A06809AE562C`.

There was exactly one entry, one READY, one exit, and one peer exact-return marker. Owner logs contain `0` Job markers, `0` Odds-Bucks/ledger/economy markers, and `0` fatal/assert/ensure/travel/network-failure markers. No owner ledger file exists. The peer has only its launch-time empty ledger/reconciliation at `entries=0`, `balance=0`.

## First remaining component-3 failure

After the exact Studio return, the owner continued with ordinary foreground-verified `Shift` + `W/A/S/D` holds. No direct transform, teleport, QA route driver, or peer input was used. The player reached the Job building frontage and made normal lateral corrections, but the view became wall/wayfinding-confused. The exact `Press E to complete a shift (100 Odds Bucks once every 24 hours)` prompt was never retained, and production has no mere-arrival location or distance marker. Therefore an exact Job arrival cannot be audited.

The map/source audit confirms that the intended Job data agree: interaction center `(9500,0)`, radius `350 cm`, visible threshold center `(9500,0,300)`, and an exterior-reachable building face at `Y=0`. That static agreement does not replace missing fresh runtime evidence. The attempt stopped before any Job `E`, payout, ledger creation, or later location visit.

The same source audit also found that the stadium prompt/transition path currently returns unless `GetNetMode() == NM_Standalone`. A shared-city owner is `NM_Client`. Stadium was not reached in this failed attempt, so this is disclosed source risk, not runtime evidence and not a second measured failure.

## Verdict and next gate

- Components 1-2: PASS in this fresh attempt.
- Component 3 Studio entry/interior/exit/exact same-peer return: PASS.
- Full component 3: **FAIL / INCOMPLETE** at the first unauditable Job frontage arrival.
- Stadium, ticket booth, clothing store, and furniture store arrivals in this attempt: NOT REACHED.
- Components 4-8: NOT REACHED.
- Cleanup: exact four test PIDs closed; `0` relevant processes and `0` UDP `17777` endpoints remain.

Phase 1K.9b should address only the measured Job-frontage usability/evidence boundary. It must make the normal player route to the existing Job prompt clear and retain an auditable arrival/distance without awarding currency. Then rebuild and repeat fresh components 1-3, stopping at the next missing exact prompt. The disclosed network-client stadium guard must be measured only if the Job boundary passes. Do not begin Job `E`, economy, wager, purchase, deployment, or a generalized tutorial/navigation system in that phase.

Cost was `$0.00`. No push was performed.
