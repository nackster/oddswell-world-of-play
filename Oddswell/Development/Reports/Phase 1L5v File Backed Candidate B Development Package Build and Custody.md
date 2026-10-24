---
title: Phase 1L.5v File-Backed Candidate B Development Package Build and Custody
type: report
status: Complete locally - package build pass
date: 2026-08-18
---

# Phase 1L.5v File-Backed Candidate B Development Package Build and Custody

## Result

`COMPLETE LOCALLY — PACKAGE_BUILD_PASS; PRODUCT NOT MEASURED; FRESH BATCH PHASE 4/6 CLOSED`

Phase 1L.5v consumed one approved direct package-build attempt and applied the Phase 1L.5u file-backed transcript contract. The attempt completed build, cook, stage, package, and archive custody with an immutable combined process transcript and two independently replayed manifests. It did not launch the package or game and did not measure the product.

## Prior contract closure

Phase 1L.5u closed at commit `6bf826d4f4e13ae9c05030a85c8cee65535226d6` with independently verified exactly two canonical Project upserts and counted Phase `3/6`. Its `package_transcript_contract_credit=1` remains intact. Phase 1L.5t remains `PACKAGE_EVIDENCE_LIMITED`; its credits remain `0` and are not repaired retroactively.

## Attempt custody

| Field | Evidence |
| --- | --- |
| outcome | `PACKAGE_BUILD_PASS` |
| attempt | `1` consumed; attempt number `1`; retry allowed `false` |
| outer executable | `C:\Windows\System32\cmd.exe` |
| retained PID | `48632` |
| start UTC | `2026-08-18T20:00:45.4257183Z` |
| natural exit | `true` |
| exit | `0`, propagated from dotnet |
| elapsed | `115.511776 s` |
| timeout / forced cleanup | `false / false` |
| raw argument identity | `574` characters / `574` UTF-8 bytes / SHA-256 `49860862F5ED1D0FE97BCEAF3DE56A7424522F794199B95EC3B60EACEAD4868C` |
| logical vectors | cmd arguments `6`; dotnet child arguments `20`; AutomationTool.dll occurrence `1` |

The one `cmd.exe` attempt received the audited `/d /q /v:off /s /c` transport and direct dotnet child. No intermediary, reusable controller, retry, package launch, game launch, broad kill, cleanup, or Defender action occurred.

## Immutable combined transcript

`C:\tmp\OddsWellPhase1L5v\Evidence\BuildCookRun.combined.txt` was created by cmd OS redirection before the dotnet child. It was never reconstructed from the tool return, substituted with internal logs, or rewritten.

| Field | Value |
| --- | --- |
| bytes | `82,329` |
| SHA-256 | `5C8F262CB873750FC0652DCD937C9387FE3B95ABEBB37F7EE96278B5AF7028AC` |
| last write UTC | `2026-08-18T20:02:40.8744400Z` |
| encoding | strict UTF-8 pass; BOM `false`; NUL count `0` |
| records | CRLF records `923`; split elements `924`; final CRLF `true` |
| observation 1 | `2026-08-18T20:02:49.8785046Z`; same bytes/SHA |
| observation 2 | `2026-08-18T20:02:58.0565815Z`; same bytes/SHA |
| separation | `8.1780769 s` |

Tool return was not evidence. Supplemental AutomationTool logs did not substitute for the combined transcript.

## Terminal marker proof

The direct raw transcript recorded AutomationTool exit success `1`, `BUILD SUCCESSFUL` `1`, and cook, stage, package, and archive completion markers `1` each. `HasMapsToCook` and `Params.HasMapsToCook` were independently counted as `1` each. Named missing-package failure, fatal, and security markers were `0`. Security-marker count `0` is limited transcript custody and is not a Defender-clean claim.

## Exact-four evidence custody

| Evidence | Bytes | SHA-256 | Replay |
| --- | ---: | --- | --- |
| `BuildCookRun.combined.txt` | 82,329 | `5C8F262CB873750FC0652DCD937C9387FE3B95ABEBB37F7EE96278B5AF7028AC` | immutable transcript identity matched |
| `session_custody.tsv` | 3,638 | `7AB26CFEDB60499CA8D3A5FC7FBCA78DAD7BC4EA7945BACE52D8B04BC9B7B5CA` | 96 ordered data rows / 96 unique keys / placeholders 0 |
| `package_manifest.tsv` | 6,666 | `C5CB77DEF21E8294E250A969BCF1400309961212BD6E67FDA817F407985B2EA2` | exact ordinal reconstruction matched |
| `saved_manifest.tsv` | 6,266 | `A25B99B5A3D6A96BB805A050325870CBFC688355143BF3ECB7DAC2309285B3A5` | exact ordinal reconstruction matched |

All four files passed strict UTF-8, no-BOM, no-NUL custody. The three TSV files use LF and final LF. Exactly one authorized non-executable evidence patch created only the TSV files; it did not touch the transcript, package, or project files.

## Package and staged-mirror manifests

The archived package and project staged mirror each contain exactly `50` files totaling `1,052,102,828` bytes. Fresh case-sensitive ordinal replay produced missing `0`, mismatch `0`, and unexpected `0` for both manifests; staged-mirror mismatch count is `0`.

Package custody records wrapper executable count `1`, direct game executable count `1`, required pak/utoc/ucas counts `1/1/1`, case-variant container duplicate count `0`, Python-family file count `0`, and package paths containing a Saved segment `0`. These are package-build and file-custody facts, not package-launch or gameplay proof.

The post-build editor module DLL is `2,591,232` bytes, last-write UTC `2026-08-18T20:01:57.0957020Z`, SHA-256 `9AE6914DEE022AA67DC5CFCDC76EA97E173F366CF1D5FCBA706C799351B69BC6`. Project config, maps, source, target, build rules, and uproject identities remained unchanged; repository product/source mutation count is `0`.

## Credits and non-inference

- `development_package_build_credit=1`
- `package_custody_credit=1`
- `package_transcript_contract_credit=1` remains prior Phase 1L.5u credit
- Phase 1L.5t credits remain `0`

All Phase 1L.5v product measurement, policy application, renderer validation, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, hands-on, beta-exit, and readiness credits remain `0`. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. A successful development package build does not establish a shipping build, product runtime result, playability, performance, compatibility, or readiness.

## Boundary and next gate

Product remains `NOT_MEASURED`. The package and evidence root remain preserved; cleanup is not authorized. Phase 1L exit remains incomplete. Phase 1M, roadmap Phase 2, Version 1 scope freeze, package/game launch, and release or beta-exit approval remain unauthorized.

Phase `4/6` closes only through the local commit containing this report and later exactly two canonical Project upserts. Tasks remain unchanged and Cursor is `0`. No automatic Phase 5 is authorized.
