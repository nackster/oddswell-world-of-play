# Phase 1K.2 - Loopback-Only Passive-Peer Launch Correction and Proof

**Date:** 2026-08-04
**Status:** COMPLETE - GAMENETDRIVER LOOPBACK PROOF PASSED; STRICT PID-WIDE PROOF FAILED
**Branch:** `agent/phase-0d`
**Measurement baseline:** `32c3bb5d311acfa809463a84dad91a9304cffeab`
**Audited runtime/package baseline:** `fe5588e`
**Evidence IDs:** `phase1k2-20260805T010631Z`, `phase1k2b-20260805T010930Z`
**Cost:** `$0.00`

## Outcome

Phase 1K.2 corrected the packaged passive peer's gameplay endpoint without changing runtime: Unreal's native `-multihome=127.0.0.1 -port=17777` flags made the one `GameNetDriver` endpoint bind exactly to `127.0.0.1:17777`. The retained Unreal log and an elevated Windows socket-owner audit agree on the exact OddsWell game PID and endpoint. Sundale loaded with `OddsWellLocomotionGameMode`, the peer received zero player input, and the process exited normally.

The broader requested assertion still failed. The same OddsWell PID also owned Unreal's in-process trace-control TCP listener at `0.0.0.0:1985`. Adding the documented engine flag `-notraceserver` in a second isolated attempt did not remove that listener. Therefore Phase 1K.2 proves a loopback-only **gameplay socket**, but does not prove that every socket owned by the process is loopback-only. Setup remains invalid under the strict PID-wide condition; `setup_end_utc`, route start, and components 1-8 are **NOT REACHED**.

## Unchanged package identity

| Field | Recorded value |
| --- | --- |
| Package configuration | Windows Development |
| Unreal | `5.8.0-55116800+++UE5+Release-5.8` |
| Machine-local scope | one Windows machine; no remote service |
| Package root | `client/OddsWell/Saved/StagedBuilds/Windows` |
| Package files / bytes | `50` / `1,049,384,364` |
| UFS manifest SHA-256 | `8271D914393BA8BC4AAFC2FB0B101C796A9A980305D0D2CB698E3700E7B75CCD` |
| Wrapper executable SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` |
| Package mutation | none; the retained staged package was reused |

## Isolated attempts

| Attempt | Exact launch delta | Game PID | Gameplay endpoint | Other endpoint owned by same PID | Verdict |
| --- | --- | ---: | --- | --- | --- |
| `phase1k2-20260805T010631Z` | `SundaleGraybox?listen -multihome=127.0.0.1 -port=17777` with fresh `-userdir` and retained `-abslog` | `16772` | exactly `127.0.0.1:17777` UDP | `0.0.0.0:1985` TCP LISTEN | target game socket PASS; strict PID-wide proof FAIL |
| `phase1k2b-20260805T010930Z` | same, plus `-notraceserver`, with a second fresh profile and log | `30520` | exactly `127.0.0.1:17777` UDP | `0.0.0.0:1985` TCP LISTEN | target game socket PASS; strict PID-wide proof FAIL |

The full second command was:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\StagedBuilds\Windows\OddsWell.exe /Game/Maps/SundaleGraybox?listen -windowed -ResX=960 -ResY=540 -WinX=0 -WinY=0 -multihome=127.0.0.1 -port=17777 -notraceserver -userdir=C:\tmp\OddsWellPhase1K2B-20260805T010930Z\PeerProfile -abslog=C:\tmp\OddsWellPhase1K2B-20260805T010930Z\Evidence\Peer.log -NoSplash -NoSound -NoP4`

The first launch began at `2026-08-05T01:06:49.3198271Z`; its wrapper/game PIDs were `17468`/`16772`. The second began at `2026-08-05T01:09:53.4862003Z`; its wrapper/game PIDs were `38244`/`30520`.

## Exact second-attempt socket proof

At `2026-08-05T01:11:28.6887254Z`, Windows reported this canonical record for game PID `30520`:

`pid=30520|udp=127.0.0.1:17777|udp_count=1|tcp=0.0.0.0:1985|tcp_count=1|target_exact=true|all_pid_exact=false`

Its SHA-256 is `0E3CBF8749E16E153837A0EAACFF4A600CB779690FC1173124D16C9448AF4976`. The corresponding Unreal log reports:

- browse `/Game/Maps/SundaleGraybox?listen`;
- game class `OddsWellLocomotionGameMode`;
- `Created socket for bind address: 127.0.0.1:17777`;
- `GameNetDriver ... listening on port 17777`;
- `Control listening on port 1985`.

The first attempt produced the same endpoint split. Neither attempt exposed an alternate gameplay UDP port. Both peer viewports visibly reached Sundale with fallback player `1`; neither peer received a player action.

## Why `-notraceserver` did not close the listener

The installed UE 5.8 source was inspected read-only. `TraceAuxiliary.cpp` uses `-notraceserver` to suppress automatic launch of Unreal Trace Server. The separate in-process trace-control implementation in `TraceLog/Private/Trace/Control.cpp` listens on TCP port `1985`, so the second launch still recorded `Control listening on port 1985`.

| Installed engine source | Bytes | SHA-256 |
| --- | ---: | --- |
| `Runtime/TraceLog/Private/Trace/Control.cpp` | `9,043` | `238E6AC9FB9320F3A1050ABD91438FF663C43AE7CCFD98EDBEA264BA98DE77FD` |
| `Runtime/Core/Private/ProfilingDebugging/TraceAuxiliary.cpp` | `98,700` | `2B22138854CE293B9ADA5065DA500F17B814CBFC1A5B9ECE09701A5DE337501A` |

This source audit explains the observation; it does not authorize an engine, build, or runtime correction.

## Retained evidence and cleanup

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `C:\tmp\OddsWellPhase1K2-20260805T010631Z\Evidence\Peer.log` | `95,822` | `BB0BBE4F8599114DDADEE9D0D490A62B83974C830ED7EFD9D12E66B8F6D62636` |
| `C:\tmp\OddsWellPhase1K2B-20260805T010930Z\Evidence\Peer.log` | `95,729` | `535308144F9B8BC74E5EB278418BD7FADECDB7A4CE0EAABD4D4942CA36D028F7` |

The first isolated profile manifest was retained by individual file hashes. The second profile manifest SHA-256 over sorted `relative/path|bytes|filehash` records is `306DB6A002E917393DA8180CDF83F220F64D40E5D5C8A428A61E4C40BFA1B253`. Both isolated profile directories were removed after hashing; both evidence directories remain. Attempt A exited normally at `2026-08-05T01:08:47.023Z`; attempt B exited normally at `2026-08-05T01:11:46.602Z`. No OddsWell, Unreal, commandlet, or Crash Report process remains, and ports `17777` and `1985` are free.

## Contract boundary

- Raw peer player-input list: `[]` for both attempts.
- Developer interventions after setup: not applicable; setup never completed.
- No owner process, Bootstrap, chooser, route action, prompt, ledger mutation, save edit, wager, replay, settlement, store action, hidden-data exposure, or component credit occurred.
- No firewall rule, network service, engine source, executable, package, configuration, content, code, schema, fixture, brain, economy, wager, inventory, housing, UI, backend, telemetry, or deployment behavior changed.
- The `101-104` replay and `79-113` settlement evidence were not used or combined.

## Verification

| Check | Result |
| --- | --- |
| Target `GameNetDriver` endpoint | PASS: one exact `127.0.0.1:17777` UDP endpoint owned by the matching OddsWell PID |
| Strict all-sockets endpoint assertion | **FAIL:** the same PID also owned `0.0.0.0:1985` TCP LISTEN |
| Map / GameMode | PASS: Sundale / `OddsWellLocomotionGameMode` |
| Peer actions | PASS: zero |
| Frozen Python brain/simulator/execution suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` under repository-pinned Python `3.12.13` in `137.1s` |
| Brain Admin `--check` | PASS |
| Existing staged package re-audit | PASS: byte counts and package hashes unchanged |
| Profile/process cleanup | PASS |
| Wiki links / whitespace / canvas JSON | PASS: canvas remains `22` nodes and `0` edges; only the affected Beta Delivery Roadmap canvas changed |
| Documentation-only scope | PASS: exactly the five required notes plus one affected canvas |

## Next gate

Do not start the player route. Scope Director and owner must decide whether the beta's security boundary requires every socket owned by the process to be loopback-only, or whether it specifically governs the gameplay `GameNetDriver`. If the strict PID-wide condition remains, a separately scoped and approved package/build/runtime correction must remove or contain Unreal's in-process trace-control listener before another setup attempt. This phase does not make that decision and does not authorize a third launch variant.
