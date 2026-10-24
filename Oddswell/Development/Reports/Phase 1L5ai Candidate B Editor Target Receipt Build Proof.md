# Phase 1L.5ai — Candidate B Editor-Target Receipt Build Proof

Status: `COMPLETE LOCALLY — EDITOR_TARGET_RECEIPT_BUILD_PASS; PACKAGE AND LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 1/6`

## Scope and prior closure

Phase 1L.5ah closed the prior six-phase batch at commit `5faaf01c3f7116c5ab7a75f14f960bfa9d541668` with independently verified exactly two canonical Project upserts and counted Phase `6/6`. Phase 1L.5ai is a new-batch Phase `1/6` proof of the missing editor-target receipt remedy only. No package, automation, game launch, product measurement, cleanup, retry, source edit, or Defender action belonged to this gate.

## Attempt and transcript custody

| field | observed |
| --- | --- |
| Attempt | `1/1`, consumed; retry `false` |
| Target | `OddsWellEditor Win64 Development` |
| PID / exit | `61744`; natural exit `0`; `NATURAL_CHILD_PROPAGATED` |
| Elapsed / cap | `102.4270506 s` / `600 s` |
| Timeout / taskkill / cleanup | `false / false / false` |
| Build controls | `-NoUBA` `1`; maximum parallel actions `1`; `-DisableUnity` `1`; `-clean` `0` |
| Raw argument | `385` bytes; SHA-256 `A5A73DFC4E3C2FF01800A9982C6ABD7A9FCBA61ED537C323980D37C70D864D8B` |
| Transcript | `2565` bytes; SHA-256 `95D091A09BC7ADBCE447F0FDA465B930E26507B8B9B1E09A82FE7BF1C038E872`; strict UTF-8, no BOM, stable |
| Session | `6307` bytes; SHA-256 `73B7407EAC2119BF00939C0C8F4CEE67B018E75202BB172871F0B844C710F0C1`; exact `151` ordered unique nonblank rows |

Result Succeeded, Candidate compilation, editor-DLL link, and receipt metadata counts are `1/1/1/1`. All `22` action rows are `[NoUba]`, and maximum observed concurrency is `1`. Build-failed, engine-change refusal, compiler error, linker error, fatal, security, and low-memory counts are all `0`.

## Editor outputs and receipt identity

The three outputs were absent before the attempt and present afterward:

| output | bytes | mtime UTC | SHA-256 |
| --- | ---: | --- | --- |
| `CandidateBPolicySmoke.cpp.obj` for UnrealEditor | `1009052` | `2026-08-22T04:14:38.3729233Z` | `21F75186B40C326623860D8A8AC311F673E3D37EDCA844F03EB8267D405812C9` |
| `UnrealEditor-OddsWell.dll` | `2592768` | `2026-08-22T04:15:38.1306527Z` | `B768FEB7395F6225C7F4DF8EF221721FC879F7A3B370BFED775A553778E9E1E9` |
| `OddsWellEditor.target` | `946529` | `2026-08-22T04:15:38.7082715Z` | `6DE822DF7E35C9DF8B03B2ECBEDA04E2C76B34257378A6E2676C757669C074D5` |

The receipt is strict UTF-8 JSON and parses as target `OddsWellEditor`, platform `Win64`, configuration `Development`, target type `Editor`, architecture `x64`, and project `../../OddsWell.uproject`. Its build products contain exactly one `UnrealEditor-OddsWell.dll` `DynamicLibrary` entry. Receipt identity replay mismatch is `0`.

## Preserved boundaries

The existing game Candidate object, `OddsWell.exe`, and `OddsWell.target` remain byte/hash/mtime-identical at SHAs `3256AAFB…A733`, `FB214D41…E3C7`, and `17461517…D28A`. Repository HEAD remains `5faaf01c3f7116c5ab7a75f14f960bfa9d541668`; tracked source, config, and maps remain exact and clean. The sole pre-existing cmd PID `26944` remained excluded and untouched; watched process, unreadable, retained-PID TCP/UDP, and watched port counts are `0`.

`editor_target_receipt_build_credit=1`; `editor_source_compile_credit=1`; `current_product_measurement_credit=0`. Product is `NOT_MEASURED` and readiness is `NOT_CLAIMED`. Candidate B remains provisional/unvalidated. Package, launch, runtime activation, policy application, renderer, visible-window, route, gameplay, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, and beta-readiness evidence remain `0`; hands-on evidence is deferred, not waived. Phase 1M, roadmap Phase 2, and Version 1 remain unauthorized. Frozen brain, economy, wager, save, network, authority, and history boundaries are unchanged.

FRESH BATCH PHASE 1/6 CLOSED — NO AUTOMATIC PHASE 2
