# Phase 1L.5aj — Candidate B Receipt-Backed Skip-Build Development Package and Custody

Status: `COMPLETE LOCALLY — PACKAGE_EVIDENCE_LIMITED; PACKAGE LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 2/6`

Qualifier: `UBT_UBA_ZERO_PREDICATE_NOT_MET`

## Scope and prior truth

Phase 1L.5ai closed at commit `7197e748f15af441416039f1549d696fba0a38bd` with independently verified exactly two canonical Project upserts and counted Phase `1/6`. Phase 1L.5aj consumed one receipt-backed `-skipbuild` package attempt. Package launch, product measurement, source editing, retry, cleanup, parser repair, and Defender action were outside this gate.

## Attempt and classification

The retained cmd PID `69576` ran from `2026-08-22T04:44:22.9373077Z` to `2026-08-22T04:46:35.1082125Z`, exited naturally `0` after `132.1892680 s`, and required no taskkill or cleanup. The exact raw argument is `573` UTF-8 bytes with SHA-256 `958DFCA23EC0A1AD00DFB2288BA4BCE04A857E62BBD97615A3D9114D66ABD8A0`.

AutomationTool success, overall success, exact map predicates, and cook/stage/package/archive completion counts are each `1`. Build start/completion, Candidate compile, game link, low-memory, named-missing, fatal, and security counts are `0`. The immutable transcript also contains UBT ValidatePlatforms custody `1` and `uba_marker_count=2` (`UnrealBuildTool\Trace.uba` and `LogUbaHorde ... UBA/Horde Configuration`). Frozen PASS required UBT/UBA `0`, so the terminal result is `PACKAGE_EVIDENCE_LIMITED`; no retroactive parser repair or rerun is authorized.

## Exact evidence

| evidence | bytes | SHA-256 |
| --- | ---: | --- |
| `BuildCookRun.combined.txt` | `73537` | `F27DBAB8229D14C13124AA550ABDB4B47BCAF9A87BE18B56434C09FC3D27B22C` |
| `session_custody.tsv` | `9324` | `0851A11A2C3C42BBEA9E45E089D3EE6CF636DF43A1F2905F9F7DF350B1DF2F72` |
| `package_manifest.tsv` | `6266` | `4E3FC3796AC374064504EE3FBC31879213073C134B29482C5AB8C1AD5C0E0DA4` |
| `saved_manifest.tsv` | `6266` | `4E3FC3796AC374064504EE3FBC31879213073C134B29482C5AB8C1AD5C0E0DA4` |

The session contains `199` ordered unique nonblank rows with UTF-8/no-BOM, LF/final-LF, and CR `0`. Package and staged manifests each replay `50` ordinal rows with mismatch `0`; each tree totals `1052104364` bytes. Wrapper/direct counts are `1/1`, required pak/utoc/ucas counts are `1/1/1`, case-variant duplicates and Python/Saved-segment files are `0`, and the packaged direct executable equals frozen prebuilt SHA `FB214D41…E3C7`.

All six game/editor output identities and the strict JSON editor receipt remain unchanged. Source, config, maps, and repository HEAD remain clean. The ignored cmd PID `26944` remained untouched; watched process, unreadable, retained-PID TCP/UDP, and watched-port counts are `0`.

The matching package and staged trees are `SUPPLEMENTAL_SUCCESSFUL_CONSTRUCTION_ARTIFACTS_NO_PHASE_CREDIT`. `receipt_backed_skip_build_package_credit=0`; `package_custody_credit=0`; `current_product_measurement_credit=0`. Product remains `NOT_MEASURED`, readiness `NOT_CLAIMED`, and Candidate B provisional/unvalidated. No build, source, product, or security defect is demonstrated; zero security markers are not a Defender-clean claim. Package launch, runtime policy, renderer, route, gameplay, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, and readiness evidence remain unmeasured or `0`. Phase 1M, roadmap Phase 2, and Version 1 remain unauthorized.

FRESH BATCH PHASE 2/6 CLOSED — NO AUTOMATIC PHASE 3
