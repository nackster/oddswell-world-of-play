---
title: Phase 1L.5ac Candidate B Dummy-World Claim Lifecycle Reconciliation
type: report
status: Complete locally - static mechanism confirmed, runtime identity unproven
date: 2026-08-21
---

# Phase 1L.5ac — Candidate B Dummy-World Claim Lifecycle Reconciliation

## Result

`COMPLETE LOCALLY — STATIC DUMMY-WORLD CLAIM MECHANISM CONFIRMED; RUNTIME INSTANCE IDENTITY UNPROVEN; FUTURE EXACT-SUNDALE-WORLD-BEFORE-CLAIM CORRECTION SELECTED; NO SOURCE/BUILD/PACKAGE/LAUNCH; PRODUCT NOT MEASURED; FRESH BATCH PHASE 1/6`

Top verdict: `STATIC_DUMMY_WORLD_CLAIM_MECHANISM_CONFIRMED_RUNTIME_INSTANCE_IDENTITY_UNPROVEN`.

Static source custody confirms a mechanism by which Unreal initializes a dummy `EWorldType::Game` world and broadcasts post-world initialization before the real loaded world, while the project accepts any first game-world match and makes its one-shot claim before binding. Phase 1L.5ab runtime evidence does not retain the claimed-world package, type, or begun-play identity, so it cannot prove which runtime world instance was claimed. This is reconciliation only, not a causal defect finding or implementation credit.

## Prior closure truth

Phase 1L.5ab closed at commit `fc70109bca5740f67866ca52cdc0d2fb18ee1673` with independently verified exactly two canonical Project upserts. Its limited evidence and zero credits remain unchanged. Prior scoped task facts remain shared `33`, external PermitWatchdog `28`, OddsWell relation `1`, OddsWell new `0`, and Cursor `0`; this docs-only phase performed no task mutation.

## Exact 11-row audit

| ordinal | contract | expected | observed | status | canonical_source |
| ---: | --- | --- | --- | --- | --- |
| 1 | `FLAG_REGISTRATION` | Candidate flag registers post-world-init | `OddsWell.cpp:19–29` | `SOURCE_PRESENT` | `OddsWell.cpp` |
| 2 | `STANDALONE_INITIALIZATION` | GameEngine constructs GameInstance and calls InitializeStandalone | `GameEngine.cpp:1262–1264` | `ENGINE_PRESENT` | `GameEngine.cpp` |
| 3 | `DUMMY_GAME_WORLD_CREATION` | InitializeStandalone creates DummyWorld as EWorldType::Game before real LoadMap | `GameInstance.cpp:190–200` | `ENGINE_PRESENT` | `GameInstance.cpp` |
| 4 | `DUMMY_WORLD_INITIALIZATION` | CreateWorld→InitializeNewWorld→InitWorld | `World.cpp:2817–2850 and 2752–2765` | `ENGINE_PRESENT` | `World.cpp` |
| 5 | `POST_INIT_BROADCAST` | InitWorld broadcasts OnPostWorldInitialization | `World.cpp:2596–2601` | `ENGINE_PRESENT` | `World.cpp` |
| 6 | `GAME_WORLD_PREDICATE` | IsGameWorld accepts EWorldType::Game | `World.cpp:9313–9315` | `ENGINE_PRESENT` | `World.cpp` |
| 7 | `PROJECT_WORLD_FILTER` | exact Sundale identity before claim | project accepts any World&&IsGameWorld without target package, `OddsWell.cpp:39–50` | `BROAD_MATCH_PRESENT` | `OddsWell.cpp` |
| 8 | `PROJECT_ONE_SHOT_CLAIM` | target world only claimed before binding | first accepted world sets global claim before weak BeginPlay bind/WORLD_BOUND, `CandidateBPolicySmoke.cpp:622–646` | `EARLY_ONE_SHOT_PRESENT` | `CandidateBPolicySmoke.cpp` |
| 9 | `REAL_WORLD_INITIALIZATION` | later loaded real world receives InitWorld | `UnrealEngine.cpp:16527–16531` | `ENGINE_PRESENT` | `UnrealEngine.cpp` |
| 10 | `REAL_WORLD_BEGINPLAY` | real world later calls BeginPlay and broadcasts OnWorldBeginPlay | `UnrealEngine.cpp:16656–16665` plus `World.cpp:6153–6181` / World.h declarations | `ENGINE_PRESENT` | `UnrealEngine.cpp/World.cpp/World.h` |
| 11 | `RUNTIME_MARKER_AND_IDENTITY` | FLAG_ACCEPTED/WORLD_BOUND/BEGIN_PLAY/NEXT_TICK_DISPATCHED counts 1/1/1/1 and exact claimed-world package/type/begun-play identity retained | committed Phase1L.5ab report records counts 1/1/0/0, WORLD_BOUND first_line 892, Sundale map-load completion count 1, and no claimed-world package/type/begun-play identity; no line number or relative ordering for map-load completion is claimed | `EVIDENCE_ABSENT` | `Oddswell/Development/Reports/Phase 1L5ab Packaged Candidate B Activation Diagnostic Marker Evidence.md` |

Row 11 is one atomic evidence result. It does not split map-load completion from claimed-world identity, and it does not assert a line number or relative ordering that the committed Phase 1L.5ab report does not contain.

## Source custody

| Canonical source | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| `client/OddsWell/Source/OddsWell/OddsWell.cpp` | `1,605` | `D7F7EE196395CA9500B5EA50B8ADAC2BEB010972A08FAEACE6DE1536FE5FE778` | `090e0d6c18c2584d17eae67825fba1867f2cf2db` |
| `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.cpp` | `31,560` | `DE732410F08B3ADA7D7E373EEF894B38252B0C07F8D6050D7FC7E676B75DFC32` | `a448a4cf29db60cfd5c4f5527c1dbefa079802d4` |
| `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.h` | `231` | `69DF7B6E9805B272A83B5C979FDC56FB09EE6403C12DA76067D63837958884FB` | `4b4bd2b87edac67ce2ccb26adc4ede0e0528da77` |
| `Engine/Source/Runtime/Engine/Private/GameEngine.cpp` | `75,242` | `344FABB69CB7BE62A21A24E990D6C477D5CE38319474A6FB2993DFC8DB1834C7` | `NOT_APPLICABLE_INSTALLED_ENGINE_SOURCE` |
| `Engine/Source/Runtime/Engine/Private/GameInstance.cpp` | `52,315` | `158EF8564BE91F84DE8155E88D4051CD614917DF9D5B1730CF9500B0C0FB75B1` | `NOT_APPLICABLE_INSTALLED_ENGINE_SOURCE` |
| `Engine/Source/Runtime/Engine/Private/World.cpp` | `363,113` | `15DBEB16CD7E11060231EB9CA4F3017EE0FAF507D625198012D089979CB74748` | `NOT_APPLICABLE_INSTALLED_ENGINE_SOURCE` |
| `Engine/Source/Runtime/Engine/Classes/Engine/World.h` | `215,920` | `BB193A298086BBF10ACFC9793071180DAB3055DD4E5C66FBDD7F45AD8E01DFF6` | `NOT_APPLICABLE_INSTALLED_ENGINE_SOURCE` |
| `Engine/Source/Runtime/Engine/Private/UnrealEngine.cpp` | `719,903` | `A856525BD245039126444FF9978C1BF68FFADD76AEAF340B01DA30D608AF84BF` | `NOT_APPLICABLE_INSTALLED_ENGINE_SOURCE` |
| `Oddswell/Development/Reports/Phase 1L5ab Packaged Candidate B Activation Diagnostic Marker Evidence.md` | `5,406` | `A4E46904675DCE569223D8F4614EE94438E9F6502CC58E656D71EF15689A89B6` | `9cf8a38f7207056b99411bc3acc118589da8ddab` |

## Selection

- A `EXACT_SUNDALE_WORLD_BEFORE_CLAIM` — `SELECTED/RECOMMENDED`.
- B `DEFER_GLOBAL_CLAIM_UNTIL_BEGINPLAY` — `NOT_SELECTED`/rejected.
- C `UNCHANGED_RERUN` — `NOT_SELECTED`/rejected.

The selected future correction requires exact Sundale-world identity before the one-shot claim. No source implementation is authored here; any source change, build, package, or launch requires its own later gate.

## Credits and nonclaims

- `activation_lifecycle_reconciliation_credit=1`.
- Implementation, source-correction, build, automation, package, launch, runtime activation, policy application, renderer, visible-window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain maturity, and readiness credits are `0`.
- Product remains `NOT_MEASURED`; Candidate B remains owner-selected, provisional, and unvalidated; Phase 1L exit remains incomplete.
- This static mechanism reconciliation does not establish actual Phase 1L.5ab runtime instance identity and does not demonstrate a product defect.
- No transient evidence root was accessed; no source, config, package, profile, test, build, launch, Defender, task, or external operational state was changed.

## Boundary and stop

FRESH BATCH PHASE 1/6 CLOSED — NO AUTOMATIC PHASE 2
