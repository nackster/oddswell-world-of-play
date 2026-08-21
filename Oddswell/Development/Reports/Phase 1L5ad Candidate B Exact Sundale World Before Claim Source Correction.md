---
title: Phase 1L.5ad Candidate B Exact Sundale World-Before-Claim Source Correction
type: report
status: Complete locally - exact Sundale claim correction authored, static pass
date: 2026-08-21
---

# Phase 1L.5ad — Candidate B Exact Sundale World-Before-Claim Source Correction

## Result

`COMPLETE LOCALLY — EXACT SUNDALE WORLD-BEFORE-CLAIM SOURCE CORRECTION AUTHORED; STATIC SOURCE AUDIT PASS; BUILD/AUTOMATION/PACKAGE/LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 2/6`

The selected `EXACT_SUNDALE_WORLD_BEFORE_CLAIM` correction is authored in the existing Candidate B source. A case-sensitive helper accepts only the exact Sundale package name, and the existing early-return guard invokes it before the sole one-shot claim. Three assertions are authored in the existing automation test. Static source review passes; compilation, test execution, build, package, and launch were not run.

## Prior phase truth

Phase 1L.5ac closed at commit `745f646627e5fbc48115a424a5b25a1176f29f80` with independently verified exactly two canonical Project upserts and counted Phase `1/6`. Its `activation_lifecycle_reconciliation_credit=1` remains prior only. Prior scoped task facts remain shared `33`, external PermitWatchdog `28`, OddsWell relation `1`, OddsWell new `0`, and Cursor `0`; this phase performed no task mutation.

## Source custody

| Field | Baseline | Authored source |
| --- | --- | --- |
| path | `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.cpp` | same |
| bytes | `31,560` | `32,165` |
| lines | `745` | `754` |
| SHA-256 | `DE732410F08B3ADA7D7E373EEF894B38252B0C07F8D6050D7FC7E676B75DFC32` | `45C98916986422AB7AD55A83CA882D344AE2C4076E171AB698024C58FC0960F0` |
| Git blob | `a448a4cf29db60cfd5c4f5527c1dbefa079802d4` | `749ca81bdc76f07767bd54dbd4043f2eeabb5fb8` |
| diff | — | `9` insertions / `1` deletion |

No header, `OddsWell.cpp`, Build.cs, include, state, helper file, module dependency, callback, marker, registry, setter, readback, or lifecycle expansion was added.

## Authored correction

The anonymous-namespace helper is exactly:

```cpp
bool IsCandidateBTargetWorldPackage(const FString& WorldPackageName)
{
	return WorldPackageName.Equals(TEXT("/Game/Maps/SundaleGraybox"), ESearchCase::CaseSensitive);
}
```

`BindToWorld` retains the existing null and `IsGameWorld` checks, then requires:

```cpp
!IsCandidateBTargetWorldPackage(World->GetOutermostObject()->GetName())
```

The helper definition is at line `25`, the authoritative guard is at line `629`, and the sole `bCandidateWorldClaimed = true;` assignment remains at line `634`. The guard therefore precedes the claim. The weak-world BeginPlay and next-tick flow plus all FLAG_ACCEPTED/WORLD_BOUND/BEGIN_PLAY/NEXT_TICK_DISPATCHED/START/FIELD/RESULT markers remain unchanged.

## Authored assertions

The existing `FCandidateBPolicySmokeCommandLineTest` now also authors:

- empty `FString()` package → `false`;
- `/Game/Maps/Bootstrap` → `false`;
- exact `/Game/Maps/SundaleGraybox` → `true`.

The three assertions are at lines `668–670`. Each assertion, the helper definition, the case-sensitive comparison, and the authoritative guard occurs exactly once. The helper name occurs five times total: definition, guard, and three assertions. These are authored assertions only; automation was not run.

## Static audit

- Exactly one source file is dirty; staged files are `0`; diff-check errors are `0`.
- The authoritative target-package guard occurs once and precedes the sole claim assignment.
- The exact Sundale literal occurs twice: helper and acceptance assertion. Bootstrap occurs once in the rejection assertion.
- Candidate source WORLD_BOUND, BEGIN_PLAY, NEXT_TICK_DISPATCHED, START, and RESULT markers remain once each; FLAG_ACCEPTED remains once in unchanged `OddsWell.cpp`.
- Source is valid UTF-8 without BOM and retains a final LF.
- No compilation, automation, build, package, launch, product measurement, transient-root access, or Defender action occurred.

## Credits and nonclaims

- `exact_sundale_world_claim_source_correction_credit=1`.
- Prior `activation_lifecycle_reconciliation_credit=1` remains prior only.
- Compile, automation execution, build, package, launch, runtime activation, policy application, renderer, visible window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain maturity, and readiness credits are `0`.
- Product remains `NOT_MEASURED`; Candidate B remains owner-selected, provisional, and unvalidated; Phase 1L exit remains incomplete.
- Static source audit does not substitute for compilation, test execution, packaged runtime activation, or product evidence.

## Boundary and stop

FRESH BATCH PHASE 2/6 CLOSED — NO AUTOMATIC PHASE 3
