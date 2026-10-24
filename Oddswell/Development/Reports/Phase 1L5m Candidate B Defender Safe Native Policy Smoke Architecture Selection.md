---
tags:
  - development-report
  - minimum-pc
  - qa-architecture
  - phase-1l
status: complete-architecture-only
date: 2026-08-16
---

# Phase 1L.5m Candidate B Defender-Safe Native Policy-Smoke Architecture Selection

## Result

`COMPLETE LOCALLY — NATIVE HARNESS ARCHITECTURE SELECTED; IMPLEMENTATION NOT STARTED`

Phase 1L.5m selected Option A, a native in-game QA harness, for a possible future Candidate B policy smoke. It made documentation changes only. The product remains `NOT_MEASURED`; implementation, tests, build, package, launch, validation, compatibility, accessibility, performance, and readiness credits are all `0`.

## Options and selection

| Option | Exact disposition | Summary |
| --- | --- | --- |
| A | `SELECTED` | **Native in-game QA harness — SELECTED/RECOMMENDED:** one opt-in C++ flag and deterministic log/readback seam inside existing OddsWell module/route architecture; normal launch unchanged. |
| B | `NOT_SELECTED` | **External compiled helper — not selected:** new binary/build/signing/security custody. |
| C | `NOT_SELECTED` | **Unreal Gauntlet/AutomationTool harness — not selected now:** broader framework/process/script surface. |

Selection counts are A `1`, B `0`, and C `0`. The decision is recorded in [[Design/Decisions/DEC-033 Candidate B Defender Safe Native QA Harness Architecture]].

## Current committed-source evidence

The audit used only short transparent reads of committed source at `41af22819f681d65d69c738646136d094dd4c0cd`:

| Source | Evidence | Git blob |
| --- | --- | --- |
| `client/OddsWell/Source/OddsWell/OddsWell.cpp` lines `8–29` | primary game module, `StartupModule`, command-line parsing, post-world-initialization callback, and game-world actor spawn seam | `44355f5892cbb45cb75cbc1af6e0892051981d1b` |
| `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` lines `2083–2113` | character `BeginPlay` and existing `LocomotionAutoExit`, `SundaleRouteQa`, and `SundaleRouteRun` parsing | `3d0d6ed39378f2ae8a3aa74ca0189a9457f399af` |
| same file lines `3285–3287` and `8617–8751` | existing route dispatch, deterministic result marker, and natural auto-exit scheduling | same blob |

`CandidateBPolicySmokeQa` is absent from current committed `client/OddsWell` source. No source implementation exists.

## Frozen seven-part implementation contract

1. Exact flag: `-CandidateBPolicySmokeQa`. With the flag absent, Candidate B policy-smoke code-path executions, callback registrations, and log markers are exactly `0`; normal behavior is unchanged.
2. Reuse only the primary game module/world-init and Sundale route/`LocomotionAutoExit` seams. Add no service, executable, plugin, dependency, process controller, network, save, or admin surface.
3. Flagged-only behavior applies DEC-027 through DEC-032; reads `11` selectors, `154` installed Medium child controls, `8` selected controls, renderer/native-TSR evidence, and visible `1920x1080`; emits one start marker, every exact evidence field, and one fail-closed verdict. Existing route and auto-exit behavior retain route and natural-exit ownership.
4. Retain the four Phase 1L.5k verdicts and truth table exactly: `PRELAUNCH_BLOCKED`, `PRODUCT_FAIL`, `EVIDENCE_LIMITED`, and `CURRENT_MACHINE_POLICY_APPLICATION_PASS`. Credits default to `0`; no evidence field defaults true.
5. Future external custody is limited to individually invoked short transparent native `git`, `Get-Process`, `netstat`, and `certutil` commands. Reusable PowerShell controllers/scripts, long inline commands, Defender commands, encoded/hidden invocation, WMI, CIM, elevation, exclusions, and scheduled tasks are forbidden.
6. Native code never touches Defender. Only the committed Phase 1L.5l report may be cited for the observed newer inactive/remediated alert, without a harmlessness inference. Frozen transient files are not opened, read, hashed, edited, executed, copied, imported, or operationally referenced by path.
7. A later minimal implementation and focused native automation must prove absent-flag counts `0` and deterministic present-flag behavior. Build/package and product launch are separate later gates.

## Frozen verdict table

| Verdict | attempt_consumed | valid_attempt_started | product_measured | product_result | application credit | route credit | cleanup_performed | retry_allowed |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `PRELAUNCH_BLOCKED` | `false` | `false` | `false` | `NOT_MEASURED` | `0` | `0` | `false` | `false` |
| `PRODUCT_FAIL` | `true` | `true` | `true` | `FAIL` | `0` | `0` | exact observed state | `false` |
| `EVIDENCE_LIMITED` | `true` | exact retained-PID and absolute-log predicate | `false` | `INDETERMINATE` | `0` | `0` | exact observed timeout-cleanup state | `false` |
| `CURRENT_MACHINE_POLICY_APPLICATION_PASS` | `true` | `true` | `true` | `PASS` | `1` | `1` | `false` | `false` |

This report records no attempt. Therefore `attempt_consumed=false`, `valid_attempt_started=false`, `product_measured=false`, `product_result=NOT_MEASURED`, application credit `0`, route credit `0`, cleanup performed `false`, and retry allowed `false`.

## Security and historical custody boundary

Phase 1L.5l remains a committed `CONTROLLER_STATIC_FAIL` with one consumed preflight invocation, no game launch, product `NOT_MEASURED`, and no retry. Its committed report records one newer remediated alert with inactive status. This report makes no harmlessness, causation, or safety inference. It did not access or operate on the frozen transient files and does not import their controller architecture.

Future observation must remain short, transparent, native, and individually invoked. No PowerShell controller or script, Defender action, source/build/test command, game process, or helper process was run for Phase 1L.5m.

## Custody and limits

Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; DEC-027 through DEC-032 are unchanged. The selected architecture is not a policy application, current-state proof, performance measurement, minimum-PC validation, compatibility finding, security finding, or readiness decision.

Brains remain frozen with no training, learning, retraining, or readiness claim. Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. No product, runtime, source, config, package, process, or Defender operational state changed. The exact six local documentation files and the later exact two canonical Project upserts are the only documentation-state changes.

## Future gate sequence

1. Separate minimal native implementation plus focused native automation for absent-flag zero counts and deterministic flagged behavior.
2. Separate build/package gate after source proof.
3. Separate launch gate after package custody.

None of these gates is authorized by this report.
