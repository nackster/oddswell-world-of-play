---
tags:
  - development
  - beta
  - phase-1k
  - evidence
  - multiplayer
status: complete-failed-shared-session
date: 2026-08-05
---

# Phase 1K.7 - Normal Shared-Session Membership Fail-Fast Measurement

**Date:** 2026-08-05
**Status:** COMPLETE - SHARED-SESSION MEMBERSHIP FAILED; COMPONENT 2 INCOMPLETE
**Branch:** `agent/phase-0d`
**Package/source identity:** `b060027`
**Evidence ID:** `phase1k7-20260806T022019Z`
**Cost:** `$0.00`

## Outcome

Phase 1K.7 measured the normal post-chooser path against an already-running passive Sundale listen server without changing runtime code or launching the owner through a direct-connect shortcut.

The fresh owner repeated component 1 successfully: one Right-arrow input selected non-default `masculine_tone_2`, one Enter input confirmed it, exactly one production appearance-save marker was written, and normal play entered `SundaleGraybox` under `OddsWellLocomotionGameMode`.

The first component-2 failure is shared-session membership. The owner's normal handoff browsed the local `/Game/Maps/SundaleGraybox` asset and created a separate standalone world. It never connected to `127.0.0.1:17777`. The passive peer remained at `ODDSWELL_SHARED_CITY_JOIN|clients=1`; neither process logged another visible player or a cross-client appearance agreement.

The attempt stopped at that failure. Owner movement inputs were `[]`; peer inputs were `[]`. Starter-appearance agreement and movement were not attempted, and component 3 did not begin.

## Measurement boundary

| Field | Recorded value |
| --- | --- |
| Package | unchanged Phase 1K.6 Windows Development package |
| Source / package commit | `b060027a686a57857d5a4fe7a1f5a5ac841fdd25` |
| Package files / bytes / Python | `50` / `1,049,392,044` / `0` |
| Wrapper SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `E9C6DE41A8A4391D7CE0C108FA12836E4B16DA19F1D420FDD84B617812CEF8F8` |
| UFS manifest SHA-256 | `CB2BEFE5FFDB071CA9CEB5ED267A49B75CCC2EBC4D69AE02827B94886AEA6E74` |
| Peer launch | `/Game/Maps/SundaleGraybox?listen`, `-multihome=127.0.0.1`, `-port=17777`, fresh isolated `PeerProfile` |
| Owner launch | package default, fresh isolated `OwnerProfile`; no map URL, server address, `?game=`, gameplay QA flag, input driver, SaveGame, or prestate |
| Accepted gameplay boundary | peer game PID `44720` owned exact UDP `127.0.0.1:17777`; trace-control TCP `0.0.0.0:1985` remained the machine-local Development debt accepted by DEC-022 |

## Ordered actions and first failure

| Order | Action | Result |
| ---: | --- | --- |
| 0 | launch passive peer and fresh normal owner | peer listens at exact loopback endpoint; owner shows default chooser; both profiles begin with zero files |
| 1 | owner Right once | visible selection changes to `masculine_tone_2` |
| 2 | owner Enter once | one production appearance save passes; owner loads normal Sundale play |
| 3 | no further player input | peer stays at `clients=1`; owner records no shared-city join, visibility, or appearance-agreement marker |

The declared owner player inputs are exactly `[Right, Enter]`. Owner route/movement inputs are `[]`; peer inputs are `[]`. No direct-connect command, QA action, teleport, save edit, hidden authority action, or evidence splice occurred.

## Membership evidence

The peer log records exactly one listen-server host join:

`ODDSWELL_SHARED_CITY_JOIN|clients=1|boundary=local_listen_server`

It records no `clients=2`, no `ODDSWELL_SHARED_CITY_VISIBLE`, and no `ODDSWELL_SHARED_CITY_APPEARANCE` agreement. The owner log records no `ODDSWELL_SHARED_CITY_JOIN`, visibility, or cross-client appearance-agreement marker. Its browse record is the local map path:

`LoadMap: /Game/Maps/SundaleGraybox?game=/Script/OddsWell.OddsWellLocomotionGameMode`

The owner did create one local authoritative appearance record in its separate world, but that cannot satisfy server-owned cross-process agreement. The peer still had exactly one player and never observed the owner.

## Retained evidence and cleanup

Evidence remains outside the repository at `C:\tmp\OddsWellPhase1k7-20260806T022019Z\Evidence`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Owner.log` | `94,896` | `4FC5893BFB9AB31BB70BA0645D7614097307F8EA0F2E307D54328464799D47D9` |
| `OwnerChooserDefault.jpg` | `119,777` | `A75A0F8AADD83F2D89AFD6F46B733B5F34F9E232251BE61A228BB67F25CEF30A` |
| `OwnerChooserSelected.jpg` | `118,236` | `385D27EC5FB66132D76140475B207B5A9FE713663B528B745651102FDCFE52B1` |
| `OwnerSundaleEntry.jpg` | `347,811` | `565835F30B7204D49B2245E4790E86D9265787E0AA670AECBB4B278DB8F887FF` |
| `Peer.log` | `96,179` | `AD8C4321462BE403825E9FE326935A39F905BAFF14D121227A25FA30F17C9C49` |
| `PeerStart.jpg` | `122,003` | `21311B6592971183F07AADD1505DB4F5E766BBB70AFBB1ECEF40F0331037924D` |
| `PeerAfterOwnerHandoff.jpg` | `121,389` | `08F1C5B1C7B01384FB0ECE3D1371FF8B6431E5BA9C34D9C7B9AA25294649312D` |

The retained owner profile has seven files and sorted manifest SHA-256 `FE6C1CD3C1493EAF0031E571FDF7CEE28A2DE00128EE3996A00F10793BFB0127`; the retained peer profile has six files and sorted manifest SHA-256 `8597068F98443FDF28C768BFF9042BE20543630CD5740E12B3C25555E1EFD7F7`.

Both clients closed normally. Active profile launch paths no longer exist; retained snapshots remain under `Evidence\RetainedProfiles`. OddsWell process count, UDP `17777`, and TCP `1985` returned to zero.

## Verification

| Check | Result |
| --- | --- |
| Fresh owner and peer profile boundary | PASS |
| Component-1 selection, save, and Sundale entry | PASS |
| Exact passive-peer loopback endpoint | PASS |
| Normal owner membership in the listen session | **FAIL - first component-2 failure** |
| Peer sees owner / owner sees peer | NOT REACHED |
| Cross-client starter-appearance agreement | NOT REACHED |
| First normal owner movement and server displacement | NOT REACHED |
| Frozen Python suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` |
| Brain Admin `--check` | PASS |
| Process, port, and active-profile cleanup | PASS |

Runtime was unchanged, so the Phase 1K.6 editor build, focused native `1/1`, full native `49/49`, BuildCookRun, and package audit are reused without a no-op rebuild.

## Boundary and next gate

This automated technical measurement does not prove shared presence, appearance synchronization, replicated movement, first-time-player usability, beta readiness, or production readiness. Component 1 remains complete; component 2 is incomplete at its first shared-session prerequisite; components 3-8 remain **NOT REACHED**.

The smallest truthful next phase is Phase 1K.8: correct only the normal post-confirmation handoff so it joins the accepted machine-local Sundale listen endpoint instead of opening a standalone local map. Rebuild, repeat the fresh component-1 path, and stop first at membership. Only if membership passes may the phase measure mutual visibility, starter-appearance agreement, and one normal movement; it must not begin component 3.
