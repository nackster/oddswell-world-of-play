---
tags:
  - development-report
  - minimum-pc
  - native-qa
  - phase-1l
status: complete-source-only
date: 2026-08-16
---

# Phase 1L.5n Candidate B Native Policy-Smoke Source Authoring

## Result

`COMPLETE LOCALLY — NATIVE SOURCE AUTHORED; BUILD, AUTOMATION, PACKAGE, AND LAUNCH NOT RUN`

Phase 1L.5n authored the minimum native source selected by [[Design/Decisions/DEC-033 Candidate B Defender Safe Native QA Harness Architecture]]. Source-authored credit is `1`. It did not compile, run automation, build, package, launch, invoke the flag, apply policy to a product, or produce runtime evidence. Product remains `NOT_MEASURED`; compile, test-run, build, package, launch, policy-application, route, performance, minimum-PC, compatibility, accessibility, and readiness credits remain `0`.

## Exact source scope

| Path | Bounded change |
| --- | --- |
| `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.h` | development-only command-line predicate and world-bind declarations |
| `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.cpp` | one development-only native helper, one POD registry, marker/readback logic, one weak world lifecycle, and one pure authored automation test |
| `client/OddsWell/Source/OddsWell/OddsWell.cpp` | existing module/world-init hook; Replay and Candidate flags remain independent |
| `client/OddsWell/Source/OddsWell/OddsWell.Build.cs` | private built-in `RHI` dependency only |

`OddsWell.h`, `PlaceholderLocomotion.cpp`, and `PlaceholderLocomotion.h` are unchanged. No service, executable, plugin, external dependency, process controller, networking, save, admin, config, package, or map surface was added.

All Candidate includes, uses, and definitions are guarded by `#if UE_BUILD_DEVELOPMENT`. The authored automation test is additionally guarded by `WITH_DEV_AUTOMATION_TESTS`. Shipping has no Candidate include, hook, definition, test, or flag behavior.

## One source-backed registry

`CandidateBPolicySmoke.cpp` contains exactly one POD-only registry declaration:

`static constexpr FPolicyRegistryRow CandidateBPolicyRegistry[]`

Its compile-time row assertion is exactly `173`. It contains, in order:

- `11` selectors from `sg.ViewDistanceQuality` through `sg.LandscapeQuality`, each expected `1`;
- the exact `154` installed UE5.8 Medium/@1 child assignments recorded line by line in [[Phase 1L5i Current AA Upscaling Medium Profile and Frame Control Evidence Inventory]];
- the exact `8` controls: `r.DynamicGlobalIlluminationMethod=1`, `r.ReflectionMethod=2`, `r.AntiAliasingMethod=4`, `r.TemporalAA.Upscaler=1`, `r.ScreenPercentage=100`, `r.DynamicRes.OperationMode=0`, `r.VSync=0`, and `t.MaxFPS=0`.

The registry uses only POD fields: kind enum, policy-literal type enum, name pointer, nullable source-section pointer, `int64` scalar, and `double` scalar. The unused scalar is canonical zero. It contains no `FString`, `FName`, container, dynamic initializer, or second list. Its exact type ledger is `INTEGER=144` and `FLOAT=29`: the `11` selectors and `8` controls are integer policy rows; the committed `154` children retain their `125` integer-spelled and `29` decimal-spelled policy types. This describes policy literals, not engine CVar declaration types. The exact ten installed Medium source sections and BaseScalability SHA-256 `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6` are held in the same registry.

Apply, typed numeric readback, field markers, exact row counts, and the authored test projections all derive from this registry. Setters use canonical scalar text. An integer row accepts any finite numeric spelling only when it is mathematically integral and exactly equals the `int64` scalar; a fractional, nonfinite, or unparseable result is an evidence gap, while a finite unequal result is `MISMATCH`. A float row accepts a finite value within `max(1e-6, abs(expected) * 1e-6)`; nonfinite or unparseable is a gap, and a reliable value outside tolerance is `MISMATCH`. A missing CVar emits `MISSING`; a duplicate registry name emits `AMBIGUOUS`. Reliable mismatch takes verdict precedence over evidence gaps.

## Lifecycle and command-line behavior

The exact opt-in remains `-CandidateBPolicySmokeQa`. The pure predicate receives a supplied command-line string; it does not mutate or launch anything. The colocated authored automation test covers empty input, unrelated existing route flags, and the exact Candidate flag. The test was not run.

The primary module registers its existing global post-world-initialization delegate only when Replay or Candidate is requested. Replay actor creation still occurs only when Replay is requested. Candidate binding occurs only when Candidate is requested. The first eligible game world is claimed before binding a weak world-owned `OnWorldBeginPlay` callback. That callback schedules one next-tick lambda capturing only `TWeakObjectPtr<UWorld>`; both stages revalidate the weak game world. Shutdown removes only the existing global delegate.

The helper does not replace the existing Sundale route or `LocomotionAutoExit` ownership. It creates no second route driver or natural-success exit path.

## Exact marker schemas

The one start site emits:

`ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=START|schema=1|selectors=11|children=154|controls=8`

Every registry or runtime/policy field uses:

`ODDSWELL_CANDIDATE_B_POLICY_FIELD|schema=1|kind=<SELECTOR|CHILD|CONTROL|RUNTIME|POLICY>|name=<canonical>|expected=<escaped>|actual=<escaped>|status=<MATCH|MISMATCH|MISSING|AMBIGUOUS|UNAVAILABLE>`

The one result site emits:

`ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=RESULT|schema=1|result=<POLICY_PASS|POLICY_FAIL|EVIDENCE_LIMITED>|fields_expected=184|fields_emitted=<n>|matches=<n>|mismatches=<n>|gaps=<n>`

Expected field count is `184`: registry `173` plus runtime/policy `11`. A reliable mismatch produces `POLICY_FAIL`; otherwise any missing, ambiguous, unavailable, or count gap produces `EVIDENCE_LIMITED`; only complete matches could produce `POLICY_PASS`.

## Runtime and policy field contract

| # | Kind/name | Expected | Authored actual source and status |
| ---: | --- | --- | --- |
| 1 | `RUNTIME/viewport_size` | `1920x1080` | viewport `FIntPoint` formatted `XxY`; exact equality is `MATCH`, absent or nonpositive dimensions emit actual/status `UNAVAILABLE`, other observed size is `MISMATCH` |
| 2 | `RUNTIME/rhi_name` | `D3D12` | trimmed `FApp::GetGraphicsRHI()`; ASCII case-insensitive exact match, empty emits actual/status `UNAVAILABLE` |
| 3 | `RUNTIME/adapter_name` | `NONEMPTY` | trimmed `GRHIAdapterName`; nonempty is `MATCH`, empty emits actual/status `UNAVAILABLE` |
| 4 | `RUNTIME/rhi_feature_level` | `SM6` | public output-reference `GetFeatureLevelName(GMaxRHIFeatureLevel, FString&)`; canonical case-sensitive exact match, empty emits actual/status `UNAVAILABLE` |
| 5 | `RUNTIME/shader_platform` | `PCD3D_SM6` | public `LexToString(GMaxRHIShaderPlatform)`; canonical case-sensitive exact match, empty emits actual/status `UNAVAILABLE` |
| 6 | `RUNTIME/d3d_feature_level_12_0` | `true` | `UNAVAILABLE_PUBLIC_GAME_THREAD_API`; always `UNAVAILABLE` |
| 7 | `RUNTIME/shader_model_6_6` | `true` | `UNAVAILABLE_PUBLIC_GAME_THREAD_API`; always `UNAVAILABLE` |
| 8 | `RUNTIME/vsm_enabled` | `true` | read-only `r.Shadow.Virtual.Enable==1`; missing or unparseable emits actual/status `UNAVAILABLE`, reliable opposed value is `MISMATCH` |
| 9 | `RUNTIME/hwrt_disabled` | `true` | read-only `r.RayTracing==0`; missing or unparseable emits actual/status `UNAVAILABLE`, reliable opposed value is `MISMATCH` |
| 10 | `RUNTIME/native_tsr_identity` | `BUILT_IN_UNREAL_TSR` | `UNAVAILABLE_PUBLIC_GAME_THREAD_API`; always `UNAVAILABLE` |
| 11 | `POLICY/nanite_required` | `false` | metadata `false`; `MATCH`; no runtime Nanite claim |

VSM and hardware-ray-tracing gates are read only and are not added to the exact eight applied controls. Nanite is policy metadata only. The viewport field is viewport-size custody, not proof of an OS-visible client rectangle.

Fields `6`, `7`, and `10` deliberately remain `UNAVAILABLE`, so `POLICY_PASS` is unreachable in this source. This prevents the source-only phase from claiming complete evidence. A mismatch still takes precedence and produces `POLICY_FAIL`; absent or incomplete evidence produces `EVIDENCE_LIMITED`.

There is exactly one `FPlatformMisc::RequestExit(false)` call site, after the result marker and only when the result is `POLICY_FAIL` or `EVIDENCE_LIMITED`. There is no request-exit call on `POLICY_PASS`.

## Static checks performed

Only short source and Git checks were used. They confirmed registry rows `173 = 11 + 154 + 8`, policy types `INTEGER=144` and `FLOAT=29`, source sections `10`, Landscape selector `1` with child rows `0`, the exact BaseScalability hash, one static assertion, one START format site, one FIELD format site, one RESULT format site, one request-exit call site, Candidate references `0` in `OddsWell.h` and the two PlaceholderLocomotion files, private dependency addition `RHI` only, and no scoped diff-check error. The one authored test checks those identities and compares distinct apply-order and evidence-order projections derived from their actual runtime views. Both full ordered ASCII projections must match each other and the frozen FNV-1a 64-bit identity `0x912A064DAD4DE242`, covering every ordinal, kind, policy type, source section, name, and canonical expected value. These are authored-source checks, not compilation or test evidence.

## Security and proof boundaries

No reusable PowerShell controller or script, long inline command, Defender command, encoded/hidden invocation, WMI, CIM, elevation, exclusion, scheduled task, Python, Unreal process, build, test, package, or game launch was used; no helper process launched. Frozen Phase 1L.5l transient files were not accessed, read, hashed, copied, edited, or operationally referenced.

Phase 1L.5m closed at commit `d4f4e0100545f663acdaf5aff3de051a56c67cbc` with independently verified exactly two Notion upserts. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; all DEC-027 through DEC-032 policies remain provisional. Brains remain frozen. Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived.

## Future gates

1. Separately review and authorize compilation plus the focused native automation test.
2. Only after source proof, separately authorize build/package custody.
3. Only after package custody, separately authorize a product launch.

None of those gates is authorized or credited here.
