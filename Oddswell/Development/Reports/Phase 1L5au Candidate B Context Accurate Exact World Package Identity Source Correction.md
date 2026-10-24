# Phase 1L.5au Candidate B Context-Accurate Exact World-Package Identity Source Correction

## Status

`COMPLETE LOCALLY — SOURCE_CORRECTION_STATIC_FAIL; STATIC_ACCEPTANCE_MISMATCH; BUILD/PACKAGE/LAUNCH NOT RUN; PRODUCT NOT MEASURED; NEW NIGHTLY BATCH PHASE 1/6`

Phase 1L.5au opened a new nightly batch with one context-accurate atomic source patch. The patch applied, but the frozen assertion-label acceptance predicate did not match. One patch was consumed; no second patch, repair, rollback, build, focused automation, package, launch, runtime, or product measurement followed.

## Decision

| Option | Identifier | Disposition | Recommendation |
|---|---|---|---|
| A | `GETPACKAGE_NAME_EXACT_PATH_BEFORE_CLAIM` | `SELECTED` | `RECOMMENDED` |
| B | `ACCEPT_SHORT_SUNDALE_WORLD_NAME` | `NOT_SELECTED` | `REJECTED` |
| C | `KEEP_GETOUTERMOSTOBJECT_OR_RERUN` | `NOT_SELECTED` | `REJECTED` |

A remains selected, but terminal outcome `SOURCE_CORRECTION_STATIC_FAIL` / `STATIC_ACCEPTANCE_MISMATCH` controls and `exact_world_package_api_source_correction_credit=0`.

## Controlling result

- Terminal enum: `SOURCE_CORRECTION_STATIC_FAIL`.
- Qualifier: `STATIC_ACCEPTANCE_MISMATCH`.
- Required assertion-label literal: `Short Sundale world package is rejected`; expected count `1`, actual count `0`.
- Unexpected actual assertion-label literal: `Short Sundale world name is rejected`; actual count `1`.
- Patch count: `1`; second patch count: `0`; repair count: `0`; rollback count: `0`.

The label mismatch controls despite the semantic source changes being present. This phase makes no source-acceptance or execution claim.

## Source custody

- Path: `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.cpp`.
- Pre-source: `32,586` bytes/SHA `9365824C3C75D65DA3D98D5C012EAB6A256F575C18B2358F1ACF5FBAE00AE4AD`/blob `340601c114e4674c6b776deddf24e8a715f8b662`.
- Post-source: `32,730` bytes/SHA `C0ED652B94980B174358201346B3A3A8999AA6B3B4AA9EFE7E831EE0E2EC2E39`/prospective blob `25c7b80d3dd548d45f5155464ebe533c34d4c49a`.
- Exact target-only diff: add `#include "UObject/Package.h"` immediately after `#include "UnrealClient.h"`; replace the sole `World->GetOutermostObject()->GetName()` with `World->GetPackage()->GetName()`; add the sole short-name assertion using exact input `SundaleGraybox` and actual label `Short Sundale world name is rejected`.
- Diff scope: one path, `3+ / 1-`; `git diff --check=0`; index remains empty.
- `OddsWell.Build.cs`: `357` bytes/SHA `AD9081D5745E5CE16D41E282A31D74C5FE5E451E6073A4A4A78D7A71E942B692`/blob `89d3e63662e9e74c54fb9b883fccfa7c926f0604`, unchanged with existing CoreUObject dependency.

## Exact static audit

| ordinal | subject | authority/evidence | status |
|---:|---|---|---|
| 1 | `baseline_source_identity` | pre-source `32586` bytes/SHA `9365824C3C75D65DA3D98D5C012EAB6A256F575C18B2358F1ACF5FBAE00AE4AD`/blob `340601c114e4674c6b776deddf24e8a715f8b662` matched before the sole patch | `MATCH` |
| 2 | `package_header` | expected `UObject/Package.h` include count `1`; actual `1` | `MATCH` |
| 3 | `package_api` | expected `GetPackage()->GetName()` count `1`; actual `1` | `MATCH` |
| 4 | `old_api_absence` | expected `GetOutermostObject()->GetName()` count `0`; actual `0` | `MATCH` |
| 5 | `short_name_assertion_label` | required exact label expected/actual `1/0`; unexpected `Short Sundale world name is rejected` actual `1` | `EVIDENCE_MISMATCH` |
| 6 | `predicate_assertions` | empty-package rejection, Bootstrap rejection, exact `/Game/Maps/SundaleGraybox` acceptance, case-sensitive predicate, and short-name input are source-present; execution not run | `SOURCE_PRESENT` |
| 7 | `invariants` | package/target computation precedes WORLD_CANDIDATE, target-or-claimed guard, and claim; lifecycle, markers, RequestExit, registry/FNV `0x912A064DAD4DE242`, Replay separation, and compile boundaries remain unchanged | `MATCH` |
| 8 | `build_dependency` | Build.cs identity unchanged and CoreUObject already present | `MATCH` |
| 9 | `diff_custody` | Candidate source is the sole source-diff path; only three intended semantic edits exist; diff-check `0` | `MATCH` |
| 10 | `execution` | build, automation, package, launch, and runtime were not performed | `EVIDENCE_ABSENT` |

## Credits and nonclaims

`exact_world_package_api_source_correction_credit=0`. Build, focused automation, package, receipt/custody, launch, activation, policy application/full validation, renderer, visible-client, route, gameplay, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, product, validation, and readiness credits are all `0`.

Product remains `NOT_MEASURED`; Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. There is no source acceptance, compile or build success, runtime behavior, product or security defect, Defender-clean state, retry, repair, rollback, cleanup, or successor authority.

## Prior truth and stop

Phase 1L.5at remains closed at full commit `ec190fcb11b62ebcfce163ec32cb7e13681fcaa9`, with independently established exactly two canonical Project upserts and prior batch count `6/6`. Its report `Oddswell/Development/Reports/Phase 1L5at Candidate B Exact World Package Identity Source Correction.md` remains `5,728` bytes/SHA `40E931F6D3FF130B1993B493852144AED4CAC52C870EECD542F77E256E37C4A4`/blob `b5bd2d714535588840549c47aa5c21ebf89a9377`; its hard stop and correction credit `0` remain unchanged.

NEW NIGHTLY BATCH PHASE 1/6 CLOSED — NO AUTOMATIC PHASE 2
