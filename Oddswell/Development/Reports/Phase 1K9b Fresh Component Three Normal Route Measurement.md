---
tags:
  - development
  - phase-1k
  - unreal
  - multiplayer
  - evidence
status: complete-failed-measurement
date: 2026-08-06
---

# Phase 1K.9b — Fresh Component-Three Normal-Route Measurement

## Outcome

**COMPLETE FAILED MEASUREMENT: COMPONENTS 1-2 PASSED; STUDIO ENTRY AND EMPTY `6/0/0/0` PASSED; REQUIRED PRIVATE-INTERIOR MOVEMENT WAS NOT AUDITABLE; EXIT, EXACT RETURN, CITY ROUTE, JOB, AND LATER STEPS WERE NOT REACHED.**

This phase changed no production code or package. It reused the exact accepted Phase 1K.9a package with fresh isolated owner and peer profiles. The owner selected `masculine_tone_2`, joined the loopback peer, produced a retained shared-city movement difference using only supported Computer Use atomic inputs, returned to the exact visible Studio prompt, and entered the private empty Studio.

Inside the Studio, all `24` supported atomic `Shift+D` calls resolved, but the retained before/after frames showed identical character bounds and no auditable displacement. Current Computer Use guidance permits its JS APIs only and exposes atomic `press_key`; it forbids the prior mixed direct-Windows timed-hold fallback. The attempt stopped immediately rather than borrow Phase 1K.9a movement or force an unproved route.

This is an input/evidence-boundary failure, not a measured production gameplay defect. It does not reopen the accepted Phase 1K.9a Studio correction. It establishes no Job-frontage or Stadium runtime finding.

## Scope and package identity

Evidence root: `C:\tmp\OddsWellPhase1K9bFreshRoute-20260807T004325Z`.

- Repository start: clean `agent/phase-0d` at `aee25f486694c2141a6874d8f49aaa7b9114353a`.
- Package: `C:\tmp\OddsWellPhase1K9aSnapPackage-20260806T233000Z\Windows`.
- Inventory: `50` files, `1,049,518,508` bytes, `0` Python files.
- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `924BE91CFE643B6131F154DE7B4C0D4A3CECAB4C725DD91A39C83946FF73E6C3`.
- UFS manifest SHA-256: `0A6C630D63D8B072EC158743AB6D36818993A0B46537A1B94D5F765648CD4446`.
- Peer wrapper/game PIDs: `35112` / `21632`; HWND `99945444`; gameplay UDP `127.0.0.1:17777`.
- Owner wrapper/game PIDs: `9736` / `20552`; HWND `7540066`; normal default launch.
- QA flag, teleport, direct transform, save edit, shell input, paid service, and deployment: `false`.

Because source and package were hash-identical, the passing Phase 1K.9a automated evidence remains proportional: focused native `1/1 + 1/1 + 1/1`, full native `50/50`, Python `105/105`, Brain Admin self-check, editor/game builds, BuildCookRun, and package audit. No no-op rebuild or duplicate regression run was performed.

## Exact operator action ledger

Every focus operation used Computer Use `activate_window` only. The only inputs were supported Computer Use atomic key calls. Repeated calls are grouped below with exact key/chord, count, transaction interval, and resolution count; the machine ledger retains the complete `24` interior-call intervals that determine the stop.

| # | Actor | Action | UTC evidence | Result |
| --- | --- | --- | --- | --- |
| 1 | Owner | Right | `00:47:12.199`–`00:47:12.568` | `1/1` resolved |
| 2 | Owner | Enter | `00:47:38.967`–`00:47:39.333` | `1/1` resolved |
| 3 | Peer | `F9` before owner movement | `00:48:20.940`–`00:48:21.320` | diagnostic only |
| 4 | Owner | `12` atomic `W` taps | focus `00:51:16.898`–`00:51:17.223`; calls `00:51:17.223`–`00:51:17.808` | `12/12` resolved |
| 5 | Peer | `F9` after first batch | `00:51:43.339`–`00:51:43.718` | diagnostic only |
| 6 | Owner | `24` additional atomic `W` taps | focus `00:56:23.859`–`00:56:24.197`; calls `00:56:24.197`–`00:56:25.397` | `24/24` resolved |
| 7 | Peer | `F9` after cumulative `36 W` | `00:56:53.645`–`00:56:54.000` | diagnostic only |
| 8 | Owner | `36` atomic `Shift+D` chords | focus `00:59:18.655`–`00:59:18.982`; calls `00:59:18.982`–`00:59:20.786` | `36/36` resolved |
| 9 | Peer | `F9` after clear shared movement | `01:00:06.401`–`01:00:06.783` | diagnostic only |
| 10 | Owner | `36` atomic `Shift+A` reverse chords | focus `01:01:46.158`–`01:01:46.504`; calls `01:01:46.504`–`01:01:48.283` | `36/36` resolved |
| 11 | Owner | `36` atomic `S` reverse taps | focus `01:02:58.486`–`01:02:58.774`; calls `01:02:58.774`–`01:03:00.590` | `36/36` resolved |
| 12 | Owner | `F9` at exact Studio prompt | `01:03:30.424`–`01:03:30.775` | exact prompt retained |
| 13 | Owner | one atomic `E` to enter | `01:04:19.206`–`01:04:19.542` | one entry marker |
| 14 | Owner | `F9` private interior before | `01:05:05.245`–`01:05:05.561` | retained |
| 15 | Owner | `24` atomic `Shift+D` chords inside | focus `01:06:14.846`–`01:06:15.135`; calls `01:06:15.135`–`01:06:16.389` | `24/24` resolved; no auditable displacement |
| 16 | Owner | `F9` private interior after | `01:06:48.381`–`01:06:48.715` | retained; stop |

The exact per-call intervals for action 15 are:

`15.135–15.200`, `15.200–15.252`, `15.252–15.302`, `15.302–15.363`, `15.363–15.412`, `15.412–15.460`, `15.460–15.510`, `15.510–15.560`, `15.560–15.609`, `15.609–15.659`, `15.659–15.706`, `15.706–15.755`, `15.755–15.803`, `15.803–15.868`, `15.868–15.918`, `15.918–15.966`, `15.966–16.016`, `16.016–16.064`, `16.064–16.112`, `16.112–16.160`, `16.160–16.208`, `16.208–16.266`, `16.266–16.323`, `16.323–16.389`, all UTC during `2026-08-07T01:06`.

Totals were `168` owner movement calls, `6` owner non-movement calls, `4` peer diagnostic `F9` calls, and `0` peer gameplay inputs. No exit input, Job-route input, mouse input, shell input, or unlisted action occurred.

## Retained evidence

### Shared-city reproduction

The owner created exactly one production appearance save for `masculine_tone_2`, `2,183` bytes, SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`. The peer reached `clients=2` and accepted the matching preset plus `starter_offwhite_top` and `starter_offwhite_bottom`.

The fixed peer's initial and final shared-city captures retain Player 1 and the world background while tan Player 2 visibly changes position/scale after the bounded atomic input batches. This is sufficient to show replicated movement occurred; no world distance is claimed.

### Studio entry

Owner `ScreenShot00000.png` visibly retains the exact `Press E to enter your empty Studio` prompt. One atomic `E` emitted exactly one entry marker and exactly one READY marker:

`ODDSWELL_STUDIO_TRANSITION|direction=to_studio|private=true|visits=false|shared_return=false`

`ODDSWELL_STUDIO_READY|result=PASS|private=true|visits=false|active_tier=studio|structure=6|upgrade_surfaces=0|furniture=0|furniture_parts=0|decorations=0|snap_points=0`

The Studio save remained unchanged through the stop: `2,141` bytes, mtime `2026-08-07T01:04:19.5508359Z`, SHA-256 `A7C0F98C2D5BC0E279FAC719B45075017CFF165EE7B71887258041A6A72D18FE`.

### First failure

The private-interior capture pair is independently auditable:

| Capture | Bytes | UTC mtime | SHA-256 | Tan-character diagnostic |
| --- | ---: | --- | --- | --- |
| Before | 1,253,916 | `01:05:05.7245852` | `5771664FA730796CF7FF20197D80C73504BEBB55AD5C65A168E9ABCAC8864F66` | bounds `590..689 x 310..617`; centroid `(639.49, 364.94)` |
| After | 1,259,845 | `01:06:48.8813542` | `1B371A7DB2C827829A3C23221E8667B33AEE8578FE6BDDAE946000111D6DDBA4` | bounds `590..689 x 310..617`; centroid `(639.49, 364.49)` |

The diagnostic uses a disclosed RGB threshold only to reject a success claim; it is not authoritative world telemetry. Bounds and centroid X are identical, the `0.45 px` centroid-Y difference is render noise, and the character, mat, walls, and ceiling retain the same alignment. Therefore the `24` resolved atomic calls do not prove interior displacement.

Exit and same-peer return were not attempted. No evidence from Phase 1K.9a is borrowed into this fresh run.

### Files and hashes

- Owner log: `97,284` bytes; SHA-256 `186F628F5BD265FCF9AF098D4E101BB53F81E7F10A9BBE8B94CB7953F1435771`.
- Peer log: `98,567` bytes; SHA-256 `A61721CF81EF04E1F1E33FAFE25F6222698B0841A814B205E61AC36C998A9992`.
- `Evidence/setup.json`: `2,221` bytes; SHA-256 `3D54675B9772230A7FD2BB2FAB087843E9B809ADB64E92B9F40D1B48CF37F9AA`.
- `Evidence/actions.json`: `7,433` bytes; SHA-256 `3D138B57AC4A014C4E738CA5613B860A5A63B2BED5A5E75651D1454F548C6B62`.
- `Evidence/captures.json`: `4,103` bytes; SHA-256 `B2D0AFC78B2FBB7A3B7896995E1D626690E07F1F05308F91E5AAA7801479F1DA`.
- `Evidence/session.json`: `2,971` bytes; SHA-256 `91114FC81C4B5D16A95108F59FE013032232054E475BE75217E9F4C73DE0DADF`.

The owner log contains `0` exits, `0` Job markers, `0` ledger/economy markers, and `0` fatal/assert/ensure/travel/network-failure markers. No owner ledger exists. The peer contains `0` return markers and `0` fatal/assert/ensure/travel/network-failure markers.

Cleanup closed only PIDs `35112`, `21632`, `9736`, and `20552`. Relevant remaining processes and UDP `17777` endpoints are `0`.

## Verdict and next gate

- Component 1: **PASS**.
- Component 2: **PASS** with supported atomic input and fixed-peer capture.
- Component 3 Studio prompt/entry/empty truth: **PASS**.
- Component 3 private-interior movement: **FAIL / NOT AUDITABLE IN THIS FRESH ATTEMPT**.
- Studio exit/exact return, city route, Job, Stadium, ticket booth, clothing store, furniture store, and components 4-8: **NOT REACHED**.

Do not change production gameplay from this result. The next gate is an input-evidence decision: use a supported hold-capable normal-input path or an observed physical player session, then repeat a wholly fresh measurement from component 1. Preserve the same stop-before-Job-`E` boundary. Do not infer or repair Job frontage or the disclosed Stadium guard until a fresh accepted run reaches them.

Cost was `$0.00`. No push was performed.
