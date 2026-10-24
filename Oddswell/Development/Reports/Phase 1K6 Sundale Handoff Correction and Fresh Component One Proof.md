---
tags:
  - development
  - beta
  - phase-1k
  - evidence
status: complete-component-one
date: 2026-08-05
---

# Phase 1K.6 - Sundale Handoff Correction and Fresh Component-One Proof

**Date:** 2026-08-05
**Status:** COMPLETE - COMPONENT 1 PASSED; COMPONENTS 2-8 NOT REACHED
**Branch:** `agent/phase-0d`
**Source baseline:** `727f418`
**Evidence ID:** `phase1k6-20260805T235056Z`
**Cost:** `$0.00`

## Outcome

The measured Phase 1K.5 failure had one production caller: the existing character-selection HUD opened absent `/Game/Maps/BlockCourtBenchmark`. Phase 1K.6 changes only that `FName` to the already approved and packaged `/Game/Maps/SundaleGraybox`. The existing `OddsWellLocomotionGameMode`, chooser, persistence authority, input path, and every later first-hour system remain unchanged.

A fresh Windows Development package then passed the complete component-1 technical route. The owner began with an isolated empty profile, launched through the normal package default, selected non-default `masculine_tone_2` with one Right-arrow input, and confirmed once with Enter. Exactly one production appearance-save marker was emitted. The owner loaded `SundaleGraybox` under `OddsWellLocomotionGameMode` with no travel failure or fallback.

The proof stopped immediately at the first city-entry frame. The owner received no movement input; the passive peer received no input. The owner was not shown to join the peer's listen session, no peer appearance agreement was measured, and no component-2 credit is claimed.

## Implementation boundary

```cpp
UGameplayStatics::OpenLevel(
    this,
    FName(TEXT("/Game/Maps/SundaleGraybox")),
    true,
    TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode"));
```

This is a one-line root-cause correction. It adds no map, networking framework, tutorial, authority, save schema, dependency, QA shortcut, teleport, brain behavior, simulator behavior, economy behavior, wager behavior, or content system.

## Build and package evidence

| Check | Result |
| --- | --- |
| Editor build | PASS; `14.58s`, four actions; only `CharacterSelectionScreen.cpp` compiled and the editor module relinked |
| Focused native automation | PASS `1/1` - `OddsWell.Character.SelectionState` |
| Full native automation | PASS `49/49` |
| Windows Development BuildCookRun | PASS `93.80s`; maps `Bootstrap+SundaleGraybox` |
| Package files / bytes / Python | `50` / `1,049,392,044` / `0` |
| Wrapper SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `E9C6DE41A8A4391D7CE0C108FA12836E4B16DA19F1D420FDD84B617812CEF8F8` |
| UFS manifest SHA-256 | `CB2BEFE5FFDB071CA9CEB5ED267A49B75CCC2EBC4D69AE02827B94886AEA6E74` |

The package root is `C:\tmp\OddsWellPhase1K6Package-20260805T235056Z\Windows`. Focused and full native logs are retained under the evidence root with SHA-256 `9227A4136410FCF026F522CBB4AC7B1CB9748B407C31F9F8E47515E46018F910` and `73BB88EA57E9B83E229ADBF03574F88298E458C5170678D5FC05B81000B1A1D9`.

## Fresh packaged proof

| Field | Recorded value |
| --- | --- |
| Peer launch | `/Game/Maps/SundaleGraybox?listen`, `-multihome=127.0.0.1`, `-port=17777`, fresh isolated `PeerProfile` |
| Owner launch | package default, fresh isolated `OwnerProfile`; no map URL, `?game=`, gameplay QA flag, input driver, SaveGame, or prestate |
| Accepted gameplay boundary | exact peer gameplay UDP `127.0.0.1:17777`; trace-control TCP `0.0.0.0:1985` remains the machine-local Development debt accepted by DEC-022 |
| Owner player inputs | exactly `[Right, Enter]` |
| Owner route/movement inputs | `[]` |
| Peer inputs | `[]` |

The owner log contains exactly one marker:

`ODDSWELL_APPEARANCE_SAVE|result=PASS|schema=1|preset=masculine_tone_2|top=starter_offwhite_top|bottom=starter_offwhite_bottom|slot=production|confirmed_once=true`

It then records `LoadMap: /Game/Maps/SundaleGraybox?game=/Script/OddsWell.OddsWellLocomotionGameMode`, `Game class is 'OddsWellLocomotionGameMode'`, and successful map completion. `TravelFailure` count is `0`; `BlockCourtBenchmark` count is `0`. The appearance SaveGame is `2,183` bytes with SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`.

## Retained evidence and cleanup

Evidence remains outside the repository at `C:\tmp\OddsWellPhase1K6-20260805T235056Z\Evidence`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Owner.log` | `95,168` | `997D1BECCA4F742AB8C95FA8A778C4B04E244FDFE42EE9A71E5C3DD9C2A47CAC` |
| `OwnerChooserDefault.jpg` | `119,747` | `9CA5658C724B8C72A78C8DE6A92F9AB9D61D64121B0C755C49043349228A842A` |
| `OwnerChooserSelected.jpg` | `118,189` | `31CD974BF732FA8CE41E7902C4307B5B9159213213CC9B69DC88B8F70B012AE1` |
| `OwnerSundaleEntry.jpg` | `346,831` | `FDD6111A68A599D2F4B7921FD1427E41457DF93B86AEF5BFA38C26A3997DBB43` |
| `Peer.log` | `96,179` | `EC469D2A386CCB627263358D6F863AA8AF1B953BFA083B20A6B25DD7C8CAEBB3` |
| `PeerStart.jpg` | `315,706` | `1AD3AC6DE99289DABAA73A53AB019787121A8B7BB5422F579C5C3DF89E70F653` |
| `PeerFinal.jpg` | `316,238` | `1A87F7285DE5FAACE8BA8B1411B3B9EE6D7947E7D70FC221BED40F5751E434C0` |

The retained owner profile has seven files and sorted manifest SHA-256 `881CB58E6D499E7E54CE4CB29296CB05FA19368147A2D63BB347434044BA440F`; the retained peer profile has six files and sorted manifest SHA-256 `A314CAFEA4625B68D4748634EBE508573B3EC033A61F61212E2FE4D49FBC854F`.

Both clients closed normally. The active profile launch paths no longer exist; their snapshots remain under `Evidence\RetainedProfiles`. OddsWell process count, UDP `17777`, and TCP `1985` all returned to zero.

## Verification

| Check | Result |
| --- | --- |
| Fresh owner profile before selection | PASS |
| Non-default selection by one normal navigation input | PASS |
| One normal confirmation and exactly one production save marker | PASS |
| Appearance SaveGame hash, size, and mtime | PASS |
| Normal `SundaleGraybox` handoff under locomotion GameMode | PASS |
| No travel failure or fallback | PASS |
| No movement, route action, peer intervention, QA action, teleport, save edit, or evidence splice | PASS |
| Focused / full native automation | PASS `1/1` / `49/49` |
| Frozen Python suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` |
| Brain Admin `--check` | PASS |
| Process, port, and active-profile cleanup | PASS |

This is an automated technical proof, not an observed first-time-player usability session. It proves component 1 only. It does not prove that the owner joined the passive peer, that either client saw the other's starter appearance, that movement replicated, that component 2 passed, or that the beta is ready.

## Next gate

Phase 1K.7 should measure the current normal post-chooser owner path against the already-running passive peer. It must first prove or fail at shared listen-session membership and owner/peer starter-appearance agreement. Only if those pass may it exercise the first normal owner movement required by component 2, then stop. It must not begin location discovery or component 3.
