# Phase 1L.5ax UBT Progress and Log-Sidecar Evidence Contract Reconciliation

## Status

`COMPLETE LOCALLY — UBT_EVIDENCE_CONTRACT_RECONCILED; SUFFIX PROGRESS GRAMMAR AND EXACT-THREE LOG TOPOLOGY SELECTED; BUILD NOT RERUN; PRODUCT NOT MEASURED; NEW NIGHTLY BATCH PHASE 4/6`

Phase 1L.5ax is one docs-only, read-only-auditable reconciliation under Phase 1L and the Beta Bible's Candidate B world-candidate activation diagnostic. It corrects the prospective UBT evidence contract without rerunning, deleting, rewriting, cleaning, rescoring, or granting retroactive build credit.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `SOURCE_BACKED_SUFFIX_AND_LOG_JSON_TOPOLOGY` | `SELECTED` | `RECOMMENDED` | Installed UE5.8 source owns both the suffix progress grammar and native log/JSON topology. |
| B | `RETROACTIVE_BUILD_CREDIT` | `NOT_SELECTED` | `REJECTED` | Reconciliation cannot change the frozen Phase 1L.5aw verdict or credits. |
| C | `RERUN_OR_DELETE_JSON` | `NOT_SELECTED` | `REJECTED` | A rerun or deletion would mutate preserved evidence and is unnecessary to reconcile the contract. |

## Frozen inputs

Baseline HEAD is `bf5c64c011e14ac6f864312fe95fa4705d76a2d6`, clean with index `0`. Phase 1L.5aw remains `EDITOR_BUILD_EVIDENCE_LIMITED` / `PROGRESS_GRAMMAR_AND_EVIDENCE_FILE_COUNT_MISMATCH`, with `candidate_editor_build_credit=0` and `candidate_source_compile_credit=0`. Its report is `Oddswell/Development/Reports/Phase 1L5aw Candidate B Exact World Package Source Editor Build Proof.md`, `4,737` bytes, SHA `C409AE9CD4B57EBB655B444B863A4E999E1661B45D4409BAFB0C23A0AEDC47AD`, blob `93710dd01f28b6a5a8fc1e443c11b6af590c961c`.

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| `Executors/ActionLogger.cs` | 14,570 | `D62F2A4D424BA7A62072998E939ECC4AEB4FA19404B01E311F4CD10169357F4F` |
| `Executors/UnrealBuildAccelerator/UBAExecutor.cs` | 52,038 | `CFC02E8DA06174BA9CE67922B2D52493E704D67B2D47A9501A7BBAE8B2C9A3EB` |
| `Shared/EpicGames.Core/Logging/Log.cs` | 49,521 | `D8AD2C9316814796E57AD5505099032AABCB6628F8AB3E7D52453612E460E4B4` |
| `UnrealBuildTool/UnrealBuildTool.cs` | 22,825 | `BCECEF684328BEB5DF5C20A719A98DF5ED349C3CD420696CF816A8786EA2BE72` |

## Exact reconciliation table

| row | subject | authority/evidence | status |
| ---: | --- | --- | --- |
| 1 | Phase 1L.5aw custody | The committed report records natural exit `0`, `Result: Succeeded` count `1`, suffix compile/link counts `1/1`, frozen prefix counts `0/0`, native log plus JSON count `2`, session count `0`, and build/compile credits `0`. | `SOURCE_CONFIRMED` |
| 2 | NoUBA ownership | `UBAExecutor.cs` line 1038 sets `additionalDescription = "[NoUba]"`. | `SOURCE_CONFIRMED` |
| 3 | action-description order | `ActionLogger.cs` lines 25–35 build command and status text before appending nonempty `AdditionalDescription`. | `SOURCE_CONFIRMED` |
| 4 | compile grammar | The observed `[2/21] Compile [x64] CandidateBPolicySmoke.cpp [NoUba]` line matches the source-backed suffix grammar. | `SOURCE_CONFIRMED` |
| 5 | link grammar | The observed `[19/21] Link [x64] UnrealEditor-OddsWell.dll [NoUba]` line matches the suffix grammar; `Action:` graph rows are echoes, not proof. | `SOURCE_CONFIRMED` |
| 6 | explicit log writer | `UnrealBuildTool.cs` lines 354–359 route non-null `Options.LogFileName` through `Log.AddFileWriter("LogTraceListener", Options.LogFileName)`. | `SOURCE_CONFIRMED` |
| 7 | JSON backup ownership | `Log.cs` lines 1197–1202 back up both the output file and `outputFile.ChangeExtension(".json")`. | `SOURCE_CONFIRMED` |
| 8 | JSON writer ownership | `Log.cs` lines 1212–1217 call `AddJsonWriter(outputFile.ChangeExtension(".json"))`; the sidecar is expected native output. | `SOURCE_CONFIRMED` |
| 9 | future contract | The suffix parser and exact-three topology below follow installed source while retaining exact Candidate target identity. | `SOURCE_CONFIRMED` |
| 10 | no retroactive credit | Phase 1L.5aw remains LIMITED with build/compile credits `0`; no rerun, cleanup, or retroactive credit occurs. | `SOURCE_CONFIRMED` |

All ten rows are `SOURCE_CONFIRMED`; the outcome is `UBT_EVIDENCE_CONTRACT_RECONCILED` with qualifier `NONE`.

## Prospective evidence contract

Future Candidate compile proof is unique physical-line count `1` for exact regex `^\[[0-9]+/[0-9]+\] Compile \[x64\] CandidateBPolicySmoke\.cpp \[NoUba\]$`. Future editor-link proof is count `1` for exact regex `^\[[0-9]+/[0-9]+\] Link \[x64\] UnrealEditor-OddsWell\.dll \[NoUba\]$`. Lines containing exact `Action:` are excluded. Natural exit `0`, trimmed exact `Result: Succeeded` count `1`, zero failure/refusal/fatal/security markers, object and DLL advance, and receipt replay remain mandatory.

An explicit `-Log=<Evidence>\UnrealBuildTool.log` requires native nonzero `UnrealBuildTool.log` and `UnrealBuildTool.json`, each observed with identical path, bytes, mtime, and SHA twice at least one second apart. The log remains strict UTF-8 input for the line parser. The JSON is strict UTF-8, and every nonempty physical line must independently parse as one JSON value/event with malformed count `0`; this makes no semantic-equivalence claim.

One later, separately gated evidence patch may add `session_custody.tsv`. The final relative file set must be exactly `{UnrealBuildTool.log, UnrealBuildTool.json, session_custody.tsv}`, count `3`, with no extras, deletion, rename, rewrite, or substitution. The session records both native-file identities and parser facts, `evidence_patch_count=1`, and `evidence_file_count=3`. These rules are prospective only and do not rescore Phase 1L.5aw.

## Credits and boundary

`editor_build_evidence_contract_reconciliation_credit=1`. `candidate_editor_build_credit=0` and `candidate_source_compile_credit=0`; every current automation, game-build, package, launch, runtime, policy, renderer, visible-client, route, gameplay, product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, validation, and readiness credit is `0`. Product is `NOT_MEASURED`; Candidate B remains provisional/unvalidated. There is no source, product, or security defect and no Defender-clean claim.

Phase 1L.5aw is truth-repaired to full commit `bf5c64c011e14ac6f864312fe95fa4705d76a2d6`, independently verified exactly two canonical Project upserts and count `3/6`. No Tasks or Cursor artifact is created.

NEW NIGHTLY BATCH PHASE 4/6 CLOSED — NO AUTOMATIC PHASE 5
