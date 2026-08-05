# Phase 1K.1 - Canonical Packaged First-Hour Contract Fail-Fast Technical Measurement

**Date:** 2026-08-04
**Status:** COMPLETE - FAILED DURING SETUP; ROUTE NOT STARTED
**Branch:** `agent/phase-0d`
**Measurement baseline:** `fccfe734bc8db9dc308534ef548341dbe511ceef`
**Audited runtime/package baseline:** `fe5588e`
**Evidence ID:** `phase1k1-20260805T004101Z`
**Cost:** `$0.00`

## Outcome

Phase 1K.1 executed one bounded technical attempt against the existing Windows Development package and stopped without repairing runtime. The attempt failed before `setup_end_utc`: the prepared passive-peer listen process bound `0.0.0.0:7777`, while [[Development/Phase 1K First-Hour Integration Evidence Contract]] requires a loopback-only endpoint. Because this is the earliest measured contract failure, no route component is accepted and components 1-8 are all **NOT REACHED**.

A separately launched fresh owner process later loaded `/Game/Maps/Bootstrap` as plain `GameModeBase`, presented a black viewport for the bounded observation, emitted no character-selection or appearance-save marker, and created no owner SaveGame. That is retained as a secondary diagnostic observation only. It is not promoted as component-1 evidence because the session setup had already failed.

## Package identity

| Field | Recorded value |
| --- | --- |
| Package configuration | Windows Development |
| Unreal | `5.8.0-55116800+++UE5+Release-5.8` |
| Machine-local scope | one Windows machine; no remote service |
| Package root | `client/OddsWell/Saved/StagedBuilds/Windows` |
| Package files / bytes | `50` / `1,049,384,364` |
| UFS manifest SHA-256 | `8271D914393BA8BC4AAFC2FB0B101C796A9A980305D0D2CB698E3700E7B75CCD` |
| Wrapper executable | `OddsWell.exe`; `171,520` bytes; SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable | `OddsWell/Binaries/Win64/OddsWell.exe`; `341,185,536` bytes; SHA-256 `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` |
| Package mutation | none; existing staged package was audited and reused |

## Fail-fast chronology

Clock source: UTC timestamps from the host clock and Unreal logs. No route timer started because setup did not complete.

| UTC | Actor | Action / observation | Classification |
| --- | --- | --- | --- |
| `2026-08-05T00:41:01Z` | operator | launched the passive peer from a fresh isolated profile with `SundaleGraybox?listen` | setup action |
| `2026-08-05T00:41:04.147Z` | peer | `IpNetDriver` reported `Created socket for bind address: 0.0.0.0:7777` and `listening on port 7777` | **first contract failure** |
| `2026-08-05T00:41:04.214Z` | peer | completed `SundaleGraybox`; one fallback starter appearance was visible; peer received no input | retained setup observation |
| `2026-08-05T00:42:17Z` | operator | launched the owner from a separate fresh isolated profile | setup action after the missed first-failure marker |
| `2026-08-05T00:42:20.458Z` | owner | completed `/Game/Maps/Bootstrap` as `GameModeBase` | secondary diagnostic observation |
| `2026-08-05T00:42:20Z` to `2026-08-05T00:46:44.3378160Z` | operator | observed a black owner viewport; no player input, prompt, selection marker, or owner save appeared | secondary diagnostic observation |
| `2026-08-05T00:46:48.794Z` | operator / owner | closed the owner viewport; log requested status-`0` exit | cleanup |
| after failure | operator | stopped the passive peer, hashed files, removed only the two isolated profiles, retained both logs, and confirmed zero OddsWell/Unreal processes | cleanup |

`setup_end_utc`: **NOT REACHED**. `session_start_utc`: **NOT REACHED**. `session_end_utc`: **NOT REACHED**. There were zero player inputs and zero developer interventions after setup because setup never ended.

## Component verdicts

| Contract component | Verdict | Evidence boundary |
| --- | --- | --- |
| 1. Fresh profile and preset | NOT REACHED | owner launch was diagnostic after the setup failure; no chooser or appearance save appeared |
| 2. Sundale and one passive peer | NOT REACHED | prepared peer was not loopback-only, so no valid owner/peer session existed |
| 3. Required locations and Studio | NOT REACHED | no route session |
| 4. First `+100` job payout | NOT REACHED | no route session |
| 5. Mesa/`40` wager | NOT REACHED | no route session |
| 6. Watch or approved `S` skip | NOT REACHED | no route session |
| 7. Exact settlement and receipt | NOT REACHED | no route session |
| 8. Jacket purchase/equip/peer view/cold restore | NOT REACHED | no route session |

## Required attempt record

| Field group | Retained record |
| --- | --- |
| Identity | evidence ID, branch, source baseline, runtime baseline, package hashes, configuration, Unreal version, executable path, owner wrapper/child PIDs `1216`/`3660`, peer wrapper/child PIDs `20776`/`47632`, separate profile paths, requested maps, and machine-local scope are recorded above. |
| Time | setup start and every available engine event are listed above. Setup end, route start/end, player-action monotonic time, and elapsed route time are explicitly **NOT REACHED**. |
| Actions | setup launches and cleanup only. Raw player-input list: `[]`. No action was accepted or rejected by a route interaction. |
| Prompts | exact visible route prompt: none. The expected character chooser and its instructions never appeared. No prompt capture file/hash was retained, so this field cannot satisfy route evidence. |
| Confusion | not applicable to this Codex-operated technical attempt; no first-time human participated and no player question, hesitation, wrong turn, or recovery is claimed. |
| Intervention | setup actions: two process launches plus observation. After-setup developer actions: `0`, because setup never ended. Cleanup after the declared failure is recorded above and changed no retained authority. |
| QA | owner flags: `-windowed -ResX=1280 -ResY=720 -WinX=100 -WinY=100 -userdir=<OwnerProfile> -abslog=<Owner.log> -NoSplash -NoSound -NoP4`. Peer used the corresponding `960x540` window/profile/log flags plus `/Game/Maps/SundaleGraybox?listen`. No QA action, teleport, save edit, time/authority change, result supply, direct UI open, or prompt bypass was used. The peer map/listen setup and its incorrect wildcard bind are disclosed. |
| Hashes | package and executable hashes are above. Retained owner and peer log hashes are below. Replay, authority-save mutation, projection, and prompt-capture hashes are **NOT REACHED**. |
| Ledger | owner ledger absent; no owner mutation. Expected `+100 -> -40 -> +94 -> -60` chain was **NOT REACHED**. Peer setup created only its normal local fixture/save state; none was used as owner evidence. |
| Peer | peer entered Sundale and logged fallback `player=1`; bind was `0.0.0.0:7777`, not loopback-only. Join, owner/peer movement agreement, owner appearance, jacket view, and valid loopback session are **NOT REACHED**. Passive-peer player-action count: `0`. |
| Cold boundary | **NOT REACHED**. No process-A route state exists. Both isolated profiles were removed only after their files were hashed; zero OddsWell/Unreal processes remained. |
| No hidden data | no private simulator/athlete field, answer key, settlement input, result, or projection was displayed or used. Replay fixture/version, denylist, `resimulated`, and player-facing result checks are **NOT REACHED**. |

## Retained evidence and cleanup

Retained logs remain outside the repository at `C:\tmp\OddsWellPhase1K1-20260805T004101Z\Evidence`:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Owner.log` | `84,715` | `FF905CE9757676F01F5B3C12E768BCFA7999FB0164B3F0B1E3433E6BCD66DDF6` |
| `Peer.log` | `92,769` | `DDFBF030B48CBF5B1E5B8FAEB1E782D31F7B9D9E9A0DE1F56A740019FBEE65C3` |

Before deletion, the owner profile contained no SaveGame. Its only material runtime file was `GameUserSettings.ini`, `1,378` bytes, SHA-256 `25034567F71ECEC90A640FA803A6BB0292EC483021905251EC22F55C8B4AA91B`. The peer profile's three normal startup SaveGames were hashed before cleanup: schedule `D92A569683CA908F73ADEBB46BCA1A26559691DF43A87100D3534CBFD3C32DC2`, pregame commitment `CBF1E176B26015BFF3A727DBE9F84DB49C784A537D4CE8BF2BEAC72E068A8EF0`, and match-winner offer `E1ED2654130A2FD4223A3B50019EC3B2F450CFA9366286DEE89473E6B90D535D`.

No result from the `101-104` replay or `79-113` settlement lane was used. The no-splice rule held because no route evidence was promoted.

## Verification

| Check | Result |
| --- | --- |
| Frozen Python brain/simulator/execution suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` |
| Brain Admin `--check` | PASS |
| Existing staged package re-audit | PASS: `50` files, `1,049,384,364` bytes; wrapper, game executable, and UFS manifest hashes unchanged |
| Retained log re-hash | PASS: both byte counts and SHA-256 values match this report |
| Isolated profile cleanup | PASS: owner and peer profile directories absent; retained evidence directory present |
| Wiki links | PASS |
| Canvas JSON | PASS: `22` nodes, `0` edges; only the existing clean Beta Delivery Roadmap canvas changed |
| Documentation-only scope and whitespace | PASS |
| Process cleanup | PASS: zero OddsWell, Unreal Editor, Unreal commandlet, or Crash Report Client processes |

## Boundary and next gate

This phase changes documentation only. It does not change C++, Python, Unreal content, package bytes, fixture data, schemas, brains, simulator behavior, ledger, economy, wager authority, UI, network behavior, inventory, housing, telemetry, backend, or deployment.

The smallest truthful next gate must be selected from this measured setup failure: establish and verify one loopback-only passive-peer launch before attempting any player route. The secondary Bootstrap/chooser observation may be investigated only after a valid setup reaches that boundary. Phase 1K.1 does not authorize either correction and does not begin Phase 1K.2.
