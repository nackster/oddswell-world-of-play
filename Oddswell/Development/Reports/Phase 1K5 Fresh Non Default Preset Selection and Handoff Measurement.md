---
tags:
  - development
  - beta
  - phase-1k
  - evidence
status: complete-failed-at-handoff
date: 2026-08-05
---

# Phase 1K.5 - Fresh Non-Default Preset Selection and Handoff Measurement

**Date:** 2026-08-05
**Status:** COMPLETE - PERSISTENCE PASSED; NORMAL WORLD HANDOFF FAILED
**Branch:** `agent/phase-0d`
**Package/source baseline:** `d3ed222`
**Evidence ID:** `phase1k5-20260805T173036Z`
**Cost:** `$0.00`

## Outcome

One fresh machine-local Windows Development attempt measured the existing normal character-confirmation path without repairing it. The accepted passive peer reached `SundaleGraybox` on gameplay UDP `127.0.0.1:17777` and received zero player input. The fresh owner launched through the package default, saw the approved chooser, pressed Right once to select non-default preset `masculine_tone_2`, and pressed Enter once.

Persistence passed. The owner log contains exactly one successful production appearance-save marker for `masculine_tone_2`, `starter_offwhite_top`, and `starter_offwhite_bottom`; the created SaveGame is `2,183` bytes with SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`.

The first canonical failure is the normal world handoff. Confirmation attempted `/Game/Maps/BlockCourtBenchmark?game=/Script/OddsWell.OddsWellLocomotionGameMode`, but that map is absent from the measured two-map package. Unreal emitted `ClientTravelFailure`, returned to Bootstrap, and presented the chooser again. The contract requires `SundaleGraybox`, so component 1 is not complete and components 2-8 remain **NOT REACHED**. No route input followed the failure.

## Measurement boundary

| Field | Recorded value |
| --- | --- |
| Unreal/package | unchanged Phase 1K.4 Windows Development package |
| Wrapper SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` |
| UFS manifest SHA-256 | `2ED40C30D77434F132ED81E6533EE75B6079564BFF89EE6C0A6D290E02F6DAD0` |
| Package files / bytes / Python | `50` / `1,049,384,364` / `0` |
| Owner launch | package default; fresh isolated `OwnerProfile`; no map URL, `?game=`, gameplay QA flag, input driver, SaveGame, or prestate |
| Peer launch | `/Game/Maps/SundaleGraybox?listen`, `-multihome=127.0.0.1`, `-port=17777`, fresh isolated `PeerProfile` |
| Machine-local security boundary | gameplay UDP `127.0.0.1:17777` on peer game PID `5160`; Unreal trace-control TCP `0.0.0.0:1985` remains accepted Development debt under DEC-022 |

The owner wrapper/game PIDs were `12216` / `43820`; peer wrapper/game PIDs were `22860` / `5160`. The owner and peer used separate profile and log paths under `C:\tmp\OddsWellPhase1K5-20260805T173036Z`.

## Ordered actions and result

| Order | Evidence time | Player action | Result |
| ---: | --- | --- | --- |
| 0 | `2026-08-05T17:32:34.1746261Z` | setup capture completed; no owner input yet | Bootstrap chooser visible with default `masculine_tone_1` selected; this is the technical run's setup boundary |
| 1 | capture completed `2026-08-05T17:32:45.4861423Z` | Right arrow once | visible selection moved to non-default `masculine_tone_2` |
| 2 | engine record `2026-08-05T17:33:02.251Z` | Enter once | one production appearance save passed; normal travel began |
| 3 | engine record `2026-08-05T17:33:02.279Z` | no further input | `ClientTravelFailure`: `/Game/Maps/BlockCourtBenchmark` did not exist; Bootstrap reloaded |

The Windows-control loop captured the post-action frame immediately after each action. It did not separately instrument the key-injection instant, so the Right-arrow row records the capture-completion upper bound rather than inventing a more precise time. There was no human participant, so first-time-player confusion or comprehension was not measured. The declared automated player inputs were exactly `[Right, Enter]`; peer inputs were `[]`; post-failure route inputs were `[]`.

## Persistence and handoff evidence

The owner log contains exactly one marker:

`ODDSWELL_APPEARANCE_SAVE|result=PASS|schema=1|preset=masculine_tone_2|top=starter_offwhite_top|bottom=starter_offwhite_bottom|slot=production|confirmed_once=true`

The same log then records:

- `WARNING: The map '/Game/Maps/BlockCourtBenchmark' does not exist.`
- `LoadMap: /Game/Maps/BlockCourtBenchmark?game=/Script/OddsWell.OddsWellLocomotionGameMode`
- `Travel failed, type: ETravelFailure::ClientTravelFailure`
- reload of `/Game/Maps/Bootstrap` with `OddsWellCharacterSelectionGameMode`.

The pre-input and post-failure chooser captures have the same SHA-256, while the selected-preset capture is different. This matches the logged failed travel and return to the initial chooser; it is not a persistence failure or a successful normal-play handoff.

## Retained evidence and cleanup

Artifacts remain outside the repository at `C:\tmp\OddsWellPhase1K5-20260805T173036Z\Evidence`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Owner.log` | `89,571` | `09E6AEE647953294C26069A4B3F6E95B1403DAB6FEC59FE51C1597685A174908` |
| `OwnerChooserBefore.jpg` | `120,674` | `33A83BA15E13F19124F77D63C743C45931A9FDC59B9DD0612EF14E169D8841D5` |
| `OwnerChooserSelected.jpg` | `119,086` | `95A71BDA9E2E2204D10E185D898ACBF138D5B387EE45062A5AB92A41A445E9AC` |
| `OwnerAfterConfirm.jpg` | `120,674` | `33A83BA15E13F19124F77D63C743C45931A9FDC59B9DD0612EF14E169D8841D5` |
| `Peer.log` | `96,207` | `0BD32F03121A455AB387EEF87B4F0C9571EEBDD1C94676077EC1B82763FAC5FF` |
| `Peer.jpg` | `194,900` | `11806487F6A8CF21F5D8D9AAD7DA3A0FB11646C6002480EB61740661BC98466B` |
| `PeerFinal.jpg` | `210,838` | `8E5155C222695C59AF5B3BC8FE3D2F64B3E1461FE8A02B0CD25CEBDB098EA980` |

The owner profile contained three files and has sorted manifest SHA-256 `78DD0FCB6303E1FFBE06567B36B5F17F755B267C2EDD6443436CB487B285C54C`. The peer profile contained six files and has sorted manifest SHA-256 `CA4E6C949DE1C2D4A1428B5266EF27EBF4EC3422B5A8EF08CAC736364F08E4BE`.

Both windows exited through normal viewport close with status `0`. Active owner/peer launch paths were removed from use and their hashed snapshots were retained under `Evidence\RetainedProfiles`. Zero OddsWell/Unreal/UAT processes remained, and UDP `17777` plus TCP `1985` returned to zero listeners.

## Verification

| Check | Result |
| --- | --- |
| Fresh owner save absence before selection | PASS |
| Non-default selection by one normal navigation input | PASS |
| One normal confirmation and exactly one save marker | PASS |
| Appearance SaveGame hash, size, and mtime | PASS |
| Required `SundaleGraybox` handoff | **FAIL - first canonical failure** |
| Passive peer and accepted gameplay-network prerequisite | PASS |
| No route continuation, hidden authority action, QA action, teleport, save edit, or evidence splice | PASS |
| Frozen Python suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` |
| Brain Admin `--check` | PASS |
| Process, port, and active-profile cleanup | PASS |

The unchanged Phase 1K.4 build, focused native `1/1`, full native `49/49`, BuildCookRun, and package audit are reused truthfully; Phase 1K.5 changes no runtime and therefore does not rebuild or rerun native automation.

## Boundary and next gate

Phase 1K.5 proves only fresh non-default selection, one production appearance save, and the first failed handoff. It does not prove normal play, shared-city entry, peer appearance agreement, any route component, first-time-player comprehension, beta readiness, or production readiness.

The smallest truthful next phase is Phase 1K.6: change only the chooser's normal confirmation target from absent `BlockCourtBenchmark` to the existing packaged `SundaleGraybox` with `OddsWellLocomotionGameMode`, then rebuild and repeat the fresh accepted-network component-1 proof. It must stop after a successful Sundale handoff and must not begin route movement or component 2 work in the same phase.
