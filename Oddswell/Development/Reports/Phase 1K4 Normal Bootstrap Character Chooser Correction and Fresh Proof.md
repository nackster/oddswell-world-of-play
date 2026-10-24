# Phase 1K.4 - Normal Bootstrap Character-Chooser Correction and Fresh Proof

**Date:** 2026-08-05
**Status:** COMPLETE - NORMAL DEFAULT STARTUP PRESENTS THE APPROVED CHOOSER
**Branch:** `agent/phase-0d`
**Implementation baseline:** `49f982d`
**Evidence ID:** `phase1k4-20260805T142500Z`
**Cost:** `$0.00`

## Outcome

Phase 1K.4 fixes only the failure measured in Phase 1K.3. The existing Bootstrap map was already the normal packaged default, and the approved chooser already existed as `AOddsWellCharacterSelectionGameMode` plus `AOddsWellCharacterSelectionHUD`. The missing link was the project default game mode.

Ponytail added one native Unreal configuration entry:

`GlobalDefaultGameMode=/Script/OddsWell.OddsWellCharacterSelectionGameMode`

A fresh Windows Development package then passed the accepted machine-local network setup. A completely fresh owner launched through the normal package default with no map URL, `?game=`, gameplay QA flag, input driver, SaveGame, prestate, or hidden intervention. Bootstrap loaded as `OddsWellCharacterSelectionGameMode` and visibly presented the existing eight-card chooser. The chooser remained present for `65.610` seconds with zero owner input. No preset was confirmed, no appearance SaveGame was created, and no route action occurred.

This proves the Phase 1K.4 correction only. Contract components 1-8 remain **NOT REACHED** because component 1 requires an explicit non-default selection, one confirmation, persistence, and a normal world handoff.

## Minimal implementation

| File | Change |
| --- | --- |
| `client/OddsWell/Config/DefaultEngine.ini` | one `GlobalDefaultGameMode` entry for the existing chooser GameMode |

No new C++, map, widget, input handler, dependency, framework, SaveGame, server authority, brain, simulator, economy, wager, inventory, housing, network implementation, backend, telemetry, or deployment behavior was added. The chooser still requires normal player input and does not auto-select or auto-confirm a preset.

## Fresh package

| Field | Recorded value |
| --- | --- |
| Unreal | `5.8`, Windows Development |
| BuildCookRun | `Bootstrap` + `SundaleGraybox`; PASS in `79.09s` |
| Package files / bytes / Python | `50` / `1,049,384,364` / `0` |
| UFS manifest SHA-256 | `2ED40C30D77434F132ED81E6533EE75B6079564BFF89EE6C0A6D290E02F6DAD0` |
| Wrapper SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` |
| `DefaultEngine.ini` SHA-256 | `1442E7ADF71B4028993465D95A92C12C9FB8E39D0DA4AC77229C6B920E38F6D1` |

The wrapper and game executable hashes remain unchanged because Phase 1K.4 is configuration-only. The staged UFS manifest and packaged containers were regenerated from the corrected source.

## Accepted passive-peer setup

- Launch UTC: `2026-08-05T14:25:03.4276878Z`.
- Wrapper/game PIDs: `13840` / `5400`.
- Command:

`C:\tmp\OddsWellPhase1K4Package-20260805\Windows\OddsWell.exe /Game/Maps/SundaleGraybox?listen -windowed -ResX=960 -ResY=540 -WinX=0 -WinY=0 -multihome=127.0.0.1 -port=17777 -userdir=C:\tmp\OddsWellPhase1K4-20260805T142500Z\PeerProfile -abslog=C:\tmp\OddsWellPhase1K4-20260805T142500Z\Evidence\Peer.log -NoSplash -NoSound -NoP4`

Unreal loaded Sundale with `OddsWellLocomotionGameMode`. Unreal and Windows agreed that game PID `5400` owned gameplay UDP `127.0.0.1:17777`. The same PID owned the already accepted Development trace-control debt at TCP `0.0.0.0:1985`. Peer player input was `[]`.

## Fresh owner proof

- Launch UTC: `2026-08-05T14:26:03.2691068Z`.
- Wrapper/game PIDs: `20300` / `26324`.
- Command:

`C:\tmp\OddsWellPhase1K4Package-20260805\Windows\OddsWell.exe -windowed -ResX=1280 -ResY=720 -WinX=980 -WinY=0 -userdir=C:\tmp\OddsWellPhase1K4-20260805T142500Z\OwnerProfile -abslog=C:\tmp\OddsWellPhase1K4-20260805T142500Z\Evidence\Owner.log -NoSplash -NoSound -NoP4`

The owner log records `/Game/Maps/Bootstrap` and `Game class is 'OddsWellCharacterSelectionGameMode'`. Read-only Windows capture visibly showed:

- the `CHOOSE YOUR PLACEHOLDER` heading;
- the existing eight gameplay-identical approved cards;
- deterministic safe focus on the first card;
- normal keyboard/controller navigation and confirmation instructions; and
- no automatic confirmation or world handoff.

The zero-input observation ran from `2026-08-05T14:26:55.3614467Z` through `2026-08-05T14:28:00.9718649Z`, or `65.610` seconds. Owner input was `[]`; `ODDSWELL_APPEARANCE_SAVE` marker count was `0`; the owner launch path contained no `Saved/SaveGames` directory.

## Evidence and cleanup

Artifacts remain outside the repository at `C:\tmp\OddsWellPhase1K4-20260805T142500Z\Evidence`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Owner.log` | `84,815` | `D3B4702FA1998D0655C54AA6A3751D4A64615CEF900E3451514779EFEBD6463D` |
| `OwnerChooserStart.png` | `120,252` | `39CCF4E15C1045CE273AD436440286F8F8BB060BC633CEF871A00D8C9C511F10` |
| `OwnerChooserEnd.png` | `120,286` | `5B5DDD333AC54A4452399CEA2E386F83A92D9CFFA1094E0CABC83A4156A3A29D` |
| `Peer.log` | `95,787` | `C139CB1B686EF1F69AE4340F7A77D16FB1D229ED4F07A4AD3B4DBF7AD9E746E4` |
| `Peer.png` | `324,478` | `AFFC97457B08838251BA1B44A79CA7EA7779C88DC021049C25EB8909F7E7F567` |

The owner profile contained two configuration files and no SaveGame; its sorted profile manifest is `AD2E1774E28DFEB2F77C7D817CF954874EA040B3E9BA321657800FA590CD1DE1`. The peer profile manifest is `E53F140257C747CA39AD8040E3551C3CDF0AC1A374DA9E67EFF03B5D617294D5`. After normal status-`0` exits, both launch paths were removed from active use and their hashed snapshots were retained under the evidence root's `RetainedProfiles` directory. Ports `17777` and `1985` returned to zero listeners, and zero OddsWell or Unreal processes remained.

## Verification

| Check | Result |
| --- | --- |
| One-line source/config scope | PASS |
| Focused `OddsWell.Character.SelectionState` automation | PASS `1/1` |
| Full native OddsWell automation | PASS `49/49` |
| Frozen Python brain/simulator/execution suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` |
| Brain Admin `--check` | PASS |
| Windows Development BuildCookRun | PASS |
| Accepted peer gameplay-network boundary | PASS |
| Normal fresh owner chooser, zero input | PASS |
| No auto-selection, appearance save, route action, or hidden data | PASS |
| Process and port cleanup | PASS |

## Boundary and next gate

Phase 1K.4 does not prove selection, persistence, world handoff, first-time-player comprehension, any later route component, beta readiness, or production readiness. The next smallest Phase 1K gate should measure one fresh non-default preset selection and one normal confirmation, then stop at the first resulting persistence or handoff failure. It must not preemptively repair the current world target or begin the city route.
