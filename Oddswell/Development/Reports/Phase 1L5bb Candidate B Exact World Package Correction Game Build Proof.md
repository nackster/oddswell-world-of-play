# Phase 1L.5bb Candidate B Exact World-Package Correction Game Build Proof

## Status

`COMPLETE LOCALLY — GAME_BUILD_PASS; EXACT WORLD-PACKAGE CORRECTION COMPILED AND LINKED; PACKAGE/GAME LAUNCH NOT RUN; PRODUCT NOT MEASURED; AUGUST 26 NIGHTLY BATCH PHASE 2/6`

Phase 1L.5bb performed one direct non-unity NoUBA OddsWell Win64 Development game build. It proves that the corrected Candidate B source compiled into the game target and that the OddsWell game executable linked and advanced. It does not prove package custody, game launch, runtime activation, broad product behavior, or readiness.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `ONE_DIRECT_NONUNITY_NOUBA_GAME_BUILD` | `SELECTED` | `RECOMMENDED` | It is the smallest proof that the corrected Candidate source reaches the game binary. |
| B | `REUSE_EDITOR_BUILD_AS_GAME_BUILD` | `NOT_SELECTED` | `REJECTED` | The editor DLL cannot prove the separately linked OddsWell game executable. |
| C | `CLEAN_PACKAGE_OR_GAME_LAUNCH_NOW` | `NOT_SELECTED` | `REJECTED` | Clean, package, and launch expand authority before the corrected game binary is proven. |

## Baseline and lifecycle

Baseline and post HEAD are `fb041232b9e8a8cd09a9dd76b9831c4e7e415004`, clean with index `0`. Candidate source, uproject, game Target.cs, and Build.cs identities remained exact. The sole attempt retained PID `33472`, started `2026-08-26T12:26:46.2147844Z`, ended `2026-08-26T12:28:40.3951597Z`, and elapsed `114.1510406` seconds. It exited naturally `0`, with timeout `false`, taskkill count `0`, process drain observed, and retry count `0`.

The exact ten-argument raw value was `250` UTF-8 bytes, SHA `0C3E0CE0797F1DED6FDC22B06232B64B9100E01E6478051D37CB94CEA867D059`. The attempt used one direct UBT invocation with `-NoUBA`, `-MaxParallelActions=1`, `-DisableUnity`, and no Clean action.

## Build result and outputs

| observation | count |
| --- | ---: |
| Result Succeeded | 1 |
| Candidate compile progress | 1 |
| OddsWell game link progress | 1 |
| reliable failure | 0 |
| engine-change protective refusal | 0 |
| fatal | 0 |
| security | 0 |

The Candidate game object advanced from `898,125` bytes/SHA `18D85E7752B9188A9F31CF5F63CB704B8FD7C63BDA0E0E28917B4985FD842BEF` to `898,924` bytes/SHA `A009B7A7D178C5C5010990A41C212DC43F4ED35E92A07322B533F25FF0CA5ACE`. The OddsWell game executable advanced from SHA `66FC9F8E407C670908CD8AB703E0850CB7E3DD8228A41A8B5CAE04F1602DA510` to `8D90D8D5A02C05FB2967C305D8EAAC1A16C10726714FBA52A42B6CD8259A0FBC`, with post size `341,429,760` bytes.

The receipt remained `113,066` bytes/SHA `174615176804EDEF83A956F2A8DD3FD3A6C683E31241D040579B5965AFFDD28A` and parsed `OddsWell` / `Win64` / `Development` / `../../OddsWell.uproject`, Launch `$(ProjectDir)/Binaries/Win64/OddsWell.exe`, with exactly one matching BuildProduct of type `Executable`. Receipt content stability is observational; object/executable advance supplies build proof.

## Evidence custody

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Evidence/UnrealBuildTool.log` | 8,019 | `1F5E79A9760526B65B95D101F76FE6DD6BF0AED62EC719C2CF9D347BA809AC5A` |
| `Evidence/UnrealBuildTool.json` | 25,148 | `5BDFB516AE48908F372543275CA0741CFF26C3F66427E788EDE74E796CB0E0BD` |
| `Evidence/session_custody.tsv` | 3,713 | `C72DDE84145EF195C84AD6A8FC91E6C21AC4C4736B2718BBD029C507976C507E` |

The log was strict UTF-8, BOM absent, NUL `0`, CRLF `120`, no bare LF/CR, final CRLF, and stable twice over `2.0236831` seconds. The JSON was strict UTF-8, BOM absent, NUL `0`, with `108` nonempty physical lines and parse-failure count `0`, stable twice over `2.0192754` seconds. The exact103 session is UTF-8 without BOM, LF/final LF, `103` unique rows. Evidence topology is exactly log, JSON, and session. Watched process residue, unreadable custody, retained PID TCP/UDP, and TCP/UDP ports `17777/1985/7810` all replayed `0`.

## Credits and boundary

`candidate_game_build_credit=1`; `candidate_source_compile_credit=1`; `exact_world_package_game_build_credit=1`. Phase 1L.5ba's focused credits remain prior-only. Current package, package receipt/custody, game launch, runtime activation, policy, renderer, visible-client, route, gameplay, product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, validation, and readiness credits are `0`. Product is `NOT_MEASURED`; Candidate B remains provisional/unvalidated. Zero security markers do not establish a Defender-clean state.

Phase 1L.5ba is truth-repaired to full commit `fb041232b9e8a8cd09a9dd76b9831c4e7e415004`, independently verified exactly two canonical Project upserts and August 26 nightly count `1/6`. Its report is `Oddswell/Development/Reports/Phase 1L5ba Candidate B Reconciled Parser Focused Native Automation.md`, `5,053` bytes, SHA `A34A1DA060E8AEF289D5983C3FEF078D5979C7E5FCE6D580CBE0630226A639CF`, blob `eefd4ccaf743f0a3914ea6f64e4486e4c09aa18f`. No Tasks or Cursor artifact is created.

AUGUST 26 NIGHTLY BATCH PHASE 2/6 CLOSED — NO AUTOMATIC PHASE 3
