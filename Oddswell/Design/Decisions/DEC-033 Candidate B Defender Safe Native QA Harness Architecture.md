---
tags:
  - decision
  - minimum-pc
  - qa-architecture
  - phase-1l
status: accepted-architecture-only
date: 2026-08-16
---

# DEC-033 Candidate B Defender-Safe Native QA Harness Architecture

## Decision status

`COMPLETE LOCALLY — NATIVE HARNESS ARCHITECTURE SELECTED; IMPLEMENTATION NOT STARTED`

This decision selects only a future architecture for applying and reading back the provisional Candidate B policies. It creates no implementation, build, package, launch, test, product result, performance result, or readiness credit.

## Options compared

| Option | Disposition | Architecture and tradeoff |
| --- | --- | --- |
| A | `SELECTED` | **Native in-game QA harness — SELECTED/RECOMMENDED:** one opt-in C++ flag and deterministic log/readback seam inside existing OddsWell module/route architecture; normal launch unchanged. This is the smallest surface and avoids a new executable, dependency, or process controller. |
| B | `NOT_SELECTED` | **External compiled helper — not selected:** new binary/build/signing/security custody. |
| C | `NOT_SELECTED` | **Unreal Gauntlet/AutomationTool harness — not selected now:** broader framework/process/script surface. |

Exactly one option is selected: A. Options B and C remain not selected; this decision does not reject them forever or authorize their implementation.

## Selected seven-part contract

1. The exact future opt-in flag is `-CandidateBPolicySmokeQa`. When it is absent, the Candidate B policy-smoke code-path count, callback-registration count, and log-marker count must each be `0`, and normal behavior must remain unchanged.
2. The harness must use the existing primary game module/world-initialization seam plus the existing Sundale route and `LocomotionAutoExit` seam. It may add no service, executable, plugin, dependency, process controller, network behavior, save behavior, or admin behavior.
3. Only when the flag is present may the native harness apply DEC-027 through DEC-032 policy custody; read all `11` scalability selectors, all `154` installed Medium child controls, all `8` selected controls, runtime renderer evidence, native-TSR evidence, and a visible `1920x1080` client rectangle; emit exactly one start marker, the exact named evidence fields, and one fail-closed verdict. The existing Sundale route and `LocomotionAutoExit` own route execution and natural exit.
4. The exact four Phase 1L.5k product verdicts and truth-table semantics remain unchanged, and all credits begin at `0`.
5. Any later external custody uses only individually invoked, short, transparent native `git`, `Get-Process`, `netstat`, or `certutil` commands. It may not use a reusable PowerShell controller or script, a long inline command, Defender command, encoded or hidden invocation, WMI, CIM, elevation, exclusion, or scheduled task.
6. Native code must never query or control Defender. The newer inactive/remediated alert may be cited only from the committed Phase 1L.5l report, without a harmlessness inference. The frozen transient files must not be opened, read, hashed, edited, executed, copied, imported, or operationally referenced by path.
7. The next gate is a separate minimal native implementation plus focused native automation proving flag-absent counts `0` and flag-present deterministic behavior. A later build/package gate and a still-later launch gate remain separate. No source, build, package, or launch authority follows from this decision.

## Frozen product verdict truth table

| Verdict | attempt_consumed | valid_attempt_started | product_measured | product_result | credit_application | credit_route | cleanup_performed | retry_allowed |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| `PRELAUNCH_BLOCKED` | `false` | `false` | `false` | `NOT_MEASURED` | `0` | `0` | `false` | `false` |
| `PRODUCT_FAIL` | `true` | `true` | `true` | `FAIL` | `0` | `0` | exact observed cleanup state | `false` |
| `EVIDENCE_LIMITED` | `true` | exact retained-PID plus exact-absolute-log predicate | `false` | `INDETERMINATE` | `0` | `0` | exact observed timeout-cleanup state | `false` |
| `CURRENT_MACHINE_POLICY_APPLICATION_PASS` | `true` | `true` | `true` | `PASS` | `1` | `1` | `false` | `false` |

No field defaults true. Reliable mismatches remain product failures; incomplete or ambiguous evidence without a reliable mismatch remains evidence-limited. This architecture selection itself is not a product attempt and leaves every product field unmeasured with every credit `0`.

## Committed-source basis

At commit `41af22819f681d65d69c738646136d094dd4c0cd`, `client/OddsWell/Source/OddsWell/OddsWell.cpp` lines `8–29` contain the primary game module, startup command-line parsing, post-world-initialization callback, and game-world actor spawn seam; its Git blob is `44355f5892cbb45cb75cbc1af6e0892051981d1b`. `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` lines `2083–2113`, `3285–3287`, and `8617–8751` contain `BeginPlay`, `LocomotionAutoExit`, `SundaleRouteQa`, `SundaleRouteRun`, route execution, the deterministic route result, and natural auto-exit scheduling; its Git blob is `3d0d6ed39378f2ae8a3aa74ca0189a9457f399af`.

The exact string `CandidateBPolicySmokeQa` is absent from current committed `client/OddsWell` source. This absence is architecture evidence only: no harness exists and implementation has not started.

## Preserved policy and proof boundaries

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. DEC-027 through DEC-032 remain provisional policy custody only. Brains remain frozen. Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived.

The product result is `NOT_MEASURED`. Source implementation, automated tests, build, package, launch, representative validation, measured performance, minimum-PC validation, compatibility, accessibility, and readiness credits remain `0`. No product, runtime, source, config, package, process, or Defender operational state changed. The exact six local documentation files and the later exact two canonical Project upserts are the only documentation-state changes.

## Next gates

1. Separately authorize the minimum native implementation and focused native automation described in contract item 7.
2. After source tests pass, separately authorize build and package custody.
3. After package custody passes, separately authorize any product launch.

These are future gates, not work authorized by this decision.
