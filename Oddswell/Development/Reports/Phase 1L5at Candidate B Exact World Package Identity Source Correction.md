# Phase 1L.5at Candidate B Exact World-Package Identity Source Correction

## Status

`COMPLETE LOCALLY — SOURCE_CORRECTION_STATIC_FAIL; APPLY_PATCH_CONTEXT_MISMATCH; SOURCE UNCHANGED; BUILD/PACKAGE/LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 6/6; SIX-PHASE BATCH CLOSED`

Phase 1L.5at was the final Phase `6/6` source-only correction gate after Phase 1L.5as reliably observed loaded `SundaleGraybox` as `target=false`. The sole authorized patch failed atomically during context verification before any file write. No second patch, source repair, build, test, package, launch, transient access, cleanup, or product measurement followed.

## Authority and decision

This phase advances Beta Delivery Roadmap Phase 1L and the Beta Game Bible's Candidate B world-candidate activation diagnostic. UE 5.8 source authority distinguishes top-level non-package `GetOutermostObject` semantics from `GetPackage`, which returns the associated `UPackage`; the existing `CoreUObject` dependency requires no module change.

| Option | Identifier | Disposition | Recommendation | Reason |
|---|---|---|---|---|
| A | `GETPACKAGE_NAME_EXACT_PATH_BEFORE_CLAIM` | `SELECTED` | `RECOMMENDED` | uses the engine package API that preserves the exact loaded package identity before the one-shot claim |
| B | `ACCEPT_SHORT_SUNDALE_WORLD_NAME` | `NOT_SELECTED` | `REJECTED` | weakens exact identity and can collide with unrelated same-named worlds |
| C | `KEEP_GETOUTERMOSTOBJECT_OR_RERUN` | `NOT_SELECTED` | `REJECTED` | retains the proven non-package-name API and would repeat the measured failure |

A implementation disposition: `NOT_APPLIED_DUE_TO_ATOMIC_PATCH_FAILURE`.

Ponytail's minimal-change constraint limited the intended delta to one public header, one API replacement, and one assertion in the existing pure automation test. No helper, abstraction, dependency, or additional behavior was authorized.

## Atomic patch custody

- Baseline and post-attempt HEAD: `2736a503aad3a07ce883d8fb82c0cf2b2cbc48aa`; tracked worktree and index remain clean.
- Target source before and after: `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.cpp`, `32,586` bytes, SHA256 `9365824C3C75D65DA3D98D5C012EAB6A256F575C18B2358F1ACF5FBAE00AE4AD`, blob `340601c114e4674c6b776deddf24e8a715f8b662`.
- Patch attempt count: `1`; apply result: `false`; file writes: `0`; second patch count: `0`.
- Failure: the include hunk expected an adjacent include that did not match the file. Patch verification failed before any hunk was applied.
- Actual required-edit counts after the attempt: `UObject/Package.h` include `0`; `GetPackage()->GetName()` replacement `0`; old `GetOutermostObject()->GetName()` call `1`; short-Sundale rejection assertion `0`.
- Source diff paths: `0`; source diff lines: `0`; `git diff --check`: `0`.

## Exact static audit

| ordinal | subject | authority/evidence | status |
|---:|---|---|---|
| 1 | prior measured fact | committed Phase 1L.5as report proves short `SundaleGraybox`, `target=false`, and downstream markers `0` | `SOURCE_CONFIRMED` |
| 2 | GetOutermostObject semantics | frozen UE 5.8 UObjectBaseUtility source/header show top-level non-package object semantics | `AUTHORITY_CONFIRMED` |
| 3 | GetPackage semantics | frozen UE 5.8 source/header show directly associated `UPackage` and package-name API | `AUTHORITY_CONFIRMED` |
| 4 | Package header/dependency | frozen Package.h and existing CoreUObject Build.cs dependency require no new module | `AUTHORITY_CONFIRMED` |
| 5 | include | required Package.h include expected once; actual `0` | `EVIDENCE_ABSENT` |
| 6 | replacement | required `GetPackage()->GetName()` expected once; actual `0` | `EVIDENCE_ABSENT` |
| 7 | old API absence | old `GetOutermostObject()->GetName()` expected `0`; actual `1` | `EVIDENCE_ABSENT` |
| 8 | predicate/tests | exact predicate remains, but required short-name rejection assertion expected once; actual `0` | `EVIDENCE_ABSENT` |
| 9 | invariants | one-shot claim, weak BeginPlay/next-tick lifecycle, markers, constexpr registry/FNV `0x912A064DAD4DE242`, Replay separation, and compile guards remain byte-unchanged | `MATCH` |
| 10 | execution | build, package, and runtime execution were not performed in this phase | `EVIDENCE_ABSENT` |

The deterministic terminal outcome is `SOURCE_CORRECTION_STATIC_FAIL` with qualifier `APPLY_PATCH_CONTEXT_MISMATCH`. The phase does not claim source acceptance or retroactively alter Phase 1L.5as.

## Credits and boundaries

`exact_world_package_api_source_correction_credit=0`. Current build, focused automation, package, package-receipt, launch, activation, policy, route, gameplay, performance, minimum-PC, compatibility, accessibility, validation, readiness, and product credits are all `0`. Product remains `NOT_MEASURED`; Candidate B remains provisional/unvalidated. No product or security defect, Defender-clean state, retry, repair, cleanup, or successor authority is claimed.

Phase 1L.5as is truth-repaired to full commit `2736a503aad3a07ce883d8fb82c0cf2b2cbc48aa`, independently verified exactly two canonical Project upserts, count `5/6`, and report `Oddswell/Development/Reports/Phase 1L5as Candidate B Packaged World Candidate Activation and Policy Evidence.md`, `5,575` bytes/SHA `76DA668E36655034BB1418350C4B36186E8AB37ACA5EC98C9AC3030C779AB1EB`/blob `b894a1e41d88b97a315fc0983e70484ab6789f45`.

The six-phase ledger is:

1. `59f0d864a4332812dcf9077a229d8d2ea6f8b7fc`
2. `a85832eeeed18f745e7b6aad00cedb953c8086c3`
3. `8f9a1bd787ac0fda73c3e4594d4a684fa2d5866e`
4. `ff5d85485e1662e6bb22a05a416816169875a8b2`
5. `2736a503aad3a07ce883d8fb82c0cf2b2cbc48aa`
6. pending local documentation commit for this failure closure

NO SEVENTH PHASE — SIX-PHASE BATCH STOPPED.
