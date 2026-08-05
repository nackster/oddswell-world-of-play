# Phase 1K.3 - Fresh Accepted-Network Setup and Default Character-Chooser Fail-Fast Measurement

**Date:** 2026-08-04
**Status:** COMPLETE - ACCEPTED PEER NETWORK PASSED; DEFAULT OWNER CHOOSER FAILED DURING SETUP
**Branch:** `agent/phase-0d`
**Measurement baseline:** `aaab386fe7c91bd2aa2d1a31c593125b59ba5a22`
**Audited runtime/package baseline:** `fe5588e`
**Evidence ID:** `phase1k3-20260805T023402Z`
**Cost:** `$0.00`

## Outcome

Phase 1K.3 executed one fresh setup attempt under [[Design/Decisions/DEC-022 Machine Local Development GameNetDriver Boundary]]. The passive peer passed the accepted machine-local Development gameplay-network prerequisite: the exact OddsWell game PID owned one UDP `GameNetDriver` endpoint at `127.0.0.1:17777`. The same PID also owned Unreal trace-control TCP `0.0.0.0:1985`, retained as the already accepted non-game Development diagnostic security debt.

The fresh owner then launched through the package's normal default startup with no map URL, `?game=`, QA action flag, input driver, save, prestate, or hidden intervention. It loaded `/Game/Maps/Bootstrap` as plain `GameModeBase`, displayed a black viewport, created no character chooser, cards, preset state, appearance state, prompt, modal, or owner SaveGame, and emitted no project chooser/appearance/HUD marker. The owner received zero input for a measured `60.091` seconds after Bootstrap load. This missing default character chooser is the canonical first failure. Setup did not complete and route components 1-8 are **NOT REACHED**.

## Unchanged package and default path

| Field | Recorded value |
| --- | --- |
| Package configuration | Windows Development |
| Package files / bytes | `50` / `1,049,384,364` |
| UFS manifest SHA-256 | `8271D914393BA8BC4AAFC2FB0B101C796A9A980305D0D2CB698E3700E7B75CCD` |
| Wrapper executable SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` |
| Source default map | `GameDefaultMap=/Game/Maps/Bootstrap.Bootstrap` |
| `DefaultEngine.ini` | `2,684` bytes; SHA-256 `A3572A2B40D00436686E523150B8796F36C44EF40584F63B25A26BDBACC4BB8A` |
| Package/source mutation | none |

## Exact launches

### Passive peer

- Launch UTC: `2026-08-05T02:34:02.8516201Z`.
- Wrapper/game PIDs: `33148` / `28436`.
- Game start UTC: `2026-08-05T02:34:02.8891305Z`.
- Command:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\StagedBuilds\Windows\OddsWell.exe /Game/Maps/SundaleGraybox?listen -windowed -ResX=960 -ResY=540 -WinX=0 -WinY=0 -multihome=127.0.0.1 -port=17777 -userdir=C:\tmp\OddsWellPhase1K3-20260805T023402Z\PeerProfile -abslog=C:\tmp\OddsWellPhase1K3-20260805T023402Z\Evidence\Peer.log -NoSplash -NoSound -NoP4`

Unreal logged Sundale, `OddsWellLocomotionGameMode`, `Created socket for bind address: 127.0.0.1:17777`, `GameNetDriver ... listening on port 17777`, and `Control listening on port 1985`. Windows independently reported:

`pid=28436|udp=127.0.0.1:17777|udp_count=1|tcp=0.0.0.0:1985|tcp_count=1`

That canonical socket record has SHA-256 `C877DF5CDE8CCC165E075FE17AA2AF08456BC95C87EB0E6780729155E6C4E137`. Peer player-input list: `[]`.

### Fresh owner

- Launch UTC: `2026-08-05T02:36:40.9246716Z`.
- Wrapper/game PIDs: `4196` / `2964`.
- Game start UTC: `2026-08-05T02:36:40.9928361Z`.
- Command:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\StagedBuilds\Windows\OddsWell.exe -windowed -ResX=1280 -ResY=720 -WinX=980 -WinY=0 -userdir=C:\tmp\OddsWellPhase1K3-20260805T023402Z\OwnerProfile -abslog=C:\tmp\OddsWellPhase1K3-20260805T023402Z\Evidence\Owner.log -NoSplash -NoSound -NoP4`

The command contains no map URL, `?game=`, gameplay QA flag, input driver, save, or prestate. Bootstrap browse began at `2026-08-05T02:36:43.909Z`; `GameModeBase` loaded at `02:36:43.967Z`; the world came up at `02:36:43.968Z`; and `FindPlayerStart` reported no defined positively rated path at `02:36:43.969Z`.

## Sixty-second zero-input observation

| Field | Recorded value |
| --- | --- |
| Observation start | `2026-08-05T02:37:25.9149951Z` |
| Target end | `2026-08-05T02:38:25.9149951Z` |
| Recorded end | `2026-08-05T02:38:26.0061928Z` |
| Elapsed | `60.091` seconds |
| Raw owner player inputs | `[]` |
| Map | `/Game/Maps/Bootstrap` |
| GameMode | plain `GameModeBase` |
| HUD / project UI | no project HUD or chooser marker; accessibility exposed only the outer Windows window chrome |
| Viewport | fully black in the retained start capture; no project UI marker appeared during the full observation; an unrelated foreground app obscured the end capture, so it was not retained |
| Chooser/cards | absent |
| Preset/selection/appearance state | absent; zero matching project log markers |
| Prompts/modals | absent |
| Owner SaveGames | absent |

No character was selected. No input was sent until the post-failure cleanup `Alt+F4`, which is not route input or component evidence.

## Component verdicts

| Contract component | Verdict | Evidence boundary |
| --- | --- | --- |
| 1. Fresh profile and preset | NOT REACHED | fresh owner default startup produced no chooser or selectable preset |
| 2. Sundale and one passive peer | NOT REACHED | peer preparation passed, but no valid owner setup/session existed |
| 3. Required locations and Studio | NOT REACHED | no route session |
| 4. First `+100` job payout | NOT REACHED | no route session |
| 5. Mesa/`40` wager | NOT REACHED | no route session |
| 6. Watch or approved `S` skip | NOT REACHED | no route session |
| 7. Exact settlement and receipt | NOT REACHED | no route session |
| 8. Jacket purchase/equip/peer view/cold restore | NOT REACHED | no route session |

## Retained artifacts and profile manifests

Artifacts remain outside the repository at `C:\tmp\OddsWellPhase1K3-20260805T023402Z\Evidence`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Owner.log` | `84,981` | `8E51DAA3ABA81F6F9EBD7B7996C1041274A8DA780E992C274D4D72668C97AC2A` |
| `OwnerStart.png` | `49,504` | `42F22D38DBE34FD0AB2D647EC5D0E0E87E4961A76D904FFE6BCC9A911D98CF5B` |
| `Peer.log` | `95,696` | `1990CFCEF474F945A343F8080321F76152FF9FFF6341D77AAF8D55A600DAD771` |
| `Peer.png` | `315,864` | `57B7FE0B60FB41896819985AC1684EA2A2482758207ECC5D4CE9BFC1D083E5A5` |

The final owner profile contained only Crash Report Client configuration and `GameUserSettings.ini`; it contained no `Saved/SaveGames` directory. Its sorted profile-manifest SHA-256 is `F31A219CBF65EB4DA3B6704DEE7595E0B763B0CF52165F1F1F7358E0E1AC1`. The peer's six-file startup profile-manifest SHA-256 is `49C0460EAC27389B9CC310AEBC4EC337B3B77A07A041D3F82FF661025E636C3C`.

Owner and peer requested status-`0` exits at `2026-08-05T02:39:41.685Z` and `2026-08-05T02:40:06.812Z`. Both isolated profile directories were removed after hashing. Ports `17777` and `1985` are free and zero OddsWell, Unreal, commandlet, or Crash Report processes remain.

## Integrity and hidden-data boundary

- Setup actions were the disclosed peer and owner launches plus read-only observation. After-setup developer interventions are `0` because setup never completed.
- Cleanup occurred only after the first failure and full observation were declared.
- No QA action, teleport, direct UI open, save edit, fixture injection, result supply, ledger mutation, wager, replay, settlement, store action, hidden athlete/simulator field, answer key, or private projection was used or shown.
- The `101-104` replay and `79-113` settlement evidence were not used or combined.
- No firewall, runtime, configuration, package, source, content, schema, fixture, brain, simulator, economy, wager, inventory, housing, backend, telemetry, or deployment change occurred.

## Verification

| Check | Result |
| --- | --- |
| Accepted peer `GameNetDriver` boundary | PASS |
| Fresh default owner command and source/package default path | PASS |
| Sixty-second zero-input owner observation | PASS as measurement; chooser outcome **FAIL** |
| Frozen Python brain/simulator/execution suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` in `135.3s` |
| Brain Admin `--check` | PASS |
| Existing staged package re-audit | PASS: byte counts and hashes unchanged |
| Log, hidden-data, links, whitespace, canvas, docs-only scope | PASS: zero chooser/UI, fatal/assert/ensure, or hidden-data denylist markers; wiki links and whitespace clean; canvas `22` nodes / `0` edges; exactly five notes plus one affected canvas |
| Profile/process/port cleanup | PASS |

## Boundary and next gate

This phase measures and documents the first failure; it does not repair it. The smallest truthful next gate is a separately scoped Phase 1K.4 correction that makes the normal packaged Bootstrap startup present the already approved default character chooser without auto-selecting a preset or bypassing normal input. A fresh accepted-network setup measurement must prove that correction before any selection or route action. Phase 1K.3 does not begin that work.
