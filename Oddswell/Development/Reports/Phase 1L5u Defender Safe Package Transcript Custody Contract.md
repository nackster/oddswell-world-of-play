---
title: Phase 1L.5u Defender-Safe Package Transcript Custody Contract
type: report
status: Complete locally - direct file-backed transcript contract selected
date: 2026-08-18
---

# Phase 1L.5u Defender-Safe Package Transcript Custody Contract

## Result

`COMPLETE LOCALLY — DIRECT FILE-BACKED PACKAGE TRANSCRIPT CONTRACT SELECTED; NO PACKAGE RERUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 3/6 CLOSED`

Phase 1L.5u selects one future package-transcript custody contract and performs no package rerun. Option A, `CMD_NATIVE_COMBINED_REDIRECT`, is `SELECTED/RECOMMENDED`. It uses signed native `cmd.exe` only to open the raw transcript before launching the already approved direct dotnet child and to redirect that child's combined stdout/stderr into the transcript. The raw file is never reconstructed from a tool return or internal AutomationTool log.

## Prior truth preserved

Phase 1L.5t remains `PACKAGE_EVIDENCE_LIMITED / TOOL_OWNED_STDOUT_STDERR_TRUNCATED_AND_UNAVAILABLE`. Its required evidence files stayed `0`, all Phase 1L.5t credits stayed `0`, product stayed `NOT_MEASURED`, and supplemental package/internal-log custody did not substitute. Phase 1L.5t closed at commit `89bf7e1f3aa3758c43e158341f0977fd7331763a` with independently verified exactly two Notion upserts. It is Phase `2/6`; this contract is Phase `3/6`.

This report does not access any Phase 1L.5t transient root or package. No cmd, dotnet, UAT, AutomationTool, source, build, cook, package, evidence, Defender, or product action ran in Phase 1L.5u.

## Exactly four options

| Option | Enum | Disposition | Reason |
| --- | --- | --- | --- |
| A | `CMD_NATIVE_COMBINED_REDIRECT` | `SELECTED/RECOMMENDED` | creates one raw combined transcript before the child and does not depend on tool-return retention |
| B | `AUTOMATIONTOOL_INTERNAL_LOG_SUBSTITUTION` | `REJECTED` | internal `Log.txt` / `Log.json` remain supplemental and are not the direct combined process stream |
| C | `LARGER_TOOL_RETURN_CAP` | `REJECTED` | a larger UI/tool cap can still truncate or lose the returned payload and is not file custody |
| D | `POWERSHELL_OR_CONTROLLER_CAPTURE` | `REJECTED` | adds a reusable script/controller or broader process surface where native cmd redirection is sufficient |

Exactly one option is selected. The selection is a documentation contract for a separately gated future attempt, not launch authority.

## Frozen cmd identity and outer argument vector

Future preflight must require exact executable `C:\Windows\System32\cmd.exe`, Authenticode status `Valid`, and Microsoft signer subject `CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US`.

The future `cmd.exe` process receives exactly six OS arguments in this order:

1. `/d`
2. `/q`
3. `/v:off`
4. `/s`
5. `/c`
6. one whole-command value

The whole-command value must begin with a double quote immediately followed by the quoted dotnet path, and it must end exactly with `2>&1"`. The separately frozen future root is `C:\tmp\OddsWellPhase1L5v`, and the exact contract form is:

`""C:\Program Files\dotnet\dotnet.exe" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll" "BuildCookRun" "-project=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject" "-nop4" "-utf8output" "-unattended" "-platform=Win64" "-clientconfig=Development" "-build" "-cook" "-map=/Game/Maps/Bootstrap+/Game/Maps/SundaleGraybox" "-stage" "-pak" "-iostore" "-compressed" "-package" "-archive" "-archivedirectory=C:\tmp\OddsWellPhase1L5v\PackageFinal" "-clean" "-NoSign" 1>"C:\tmp\OddsWellPhase1L5v\Evidence\BuildCookRun.combined.txt" 2>&1"`

The one whole-command value is a single OS argument. `CALL`, intermediary executable/script/controller, pipe, chain, conditional, command substitution, environment expansion, delayed expansion, encoded or hidden invocation, and every metacharacter except the shown output/error redirections are forbidden.

## Exact dotnet child cardinality

After cmd parses only the two shown redirections, dotnet must receive exactly twenty child arguments:

1. `C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll`
2. `BuildCookRun`
3. `-project=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject`
4. `-nop4`
5. `-utf8output`
6. `-unattended`
7. `-platform=Win64`
8. `-clientconfig=Development`
9. `-build`
10. `-cook`
11. `-map=/Game/Maps/Bootstrap+/Game/Maps/SundaleGraybox`
12. `-stage`
13. `-pak`
14. `-iostore`
15. `-compressed`
16. `-package`
17. `-archive`
18. `-archivedirectory=C:\tmp\OddsWellPhase1L5v\PackageFinal`
19. `-clean`
20. `-NoSign`

Token 1 contains `AutomationTool.dll` exactly once. Token 2 is exactly `BuildCookRun`. Token 18 is the only child token changed from the accepted package vector and may substitute only the separately frozen fresh archive root. Token 20 is exactly `-NoSign`. The transcript redirections are cmd syntax and are not dotnet child arguments.

## Raw transcript custody

The separately authorized future root and its `Evidence` directory must be absent before their bounded creation, and `BuildCookRun.combined.txt` must be absent. Cmd redirection opens and creates the transcript before starting the dotnet child. The tool/UI return is progress only and is never evidence.

After the child drains, the raw transcript is immutable:

- never rewrite, normalize, append, patch, copy over, or replace it;
- take two read-only size and SHA-256 observations at least `1 s` apart;
- require identical nonzero size and SHA-256 from both reads;
- reopen with strict UTF-8 decoding and record BOM presence truthfully;
- require exact invocation/cardinality custody, AutomationTool start, build/cook/stage/package/archive terminal markers, terminal exit/result, and security/failure marker counts;
- treat a missing, unreadable, malformed, changing, truncated, ambiguous, or conflicting field as `PACKAGE_EVIDENCE_LIMITED` unless a reliable product/security failure has precedence.

Internal AutomationTool logs can corroborate but never replace the raw transcript. Package and project-staged inventories require complete path/bytes/SHA-256 manifests; one cannot substitute for the other.

## Future exact-four evidence sequence

The future gate must produce and validate exactly these four evidence files in order:

1. `Evidence/BuildCookRun.combined.txt` — created only by cmd redirection before dotnet starts, then sealed by stable read-only identity;
2. `Evidence/session_custody.tsv` — records cmd/dotnet identities, exact vectors, lifecycle, transcript identities, verdict inputs, and no-default-true result;
3. `Evidence/package_manifest.tsv` — complete archive-root relative path/bytes/SHA-256 rows;
4. `Evidence/saved_manifest.tsv` — complete project staged-root relative path/bytes/SHA-256 rows, separately labeled and compared.

The future operational sequence is preflight, one exact cmd attempt, transcript stability/strict parse plus read-only package inventories, then one bounded non-executable custody write for files 2–4. Missing or mismatched evidence is limited; no rerun or repair is implied.

## Credits and boundary

`package_transcript_contract_credit=1`

Phase 1L.5u build, cook, stage, pak, IoStore, package, archive, transcript-run, product, policy application, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, hands-on, beta-exit, and readiness credits are `0`. Product remains `NOT_MEASURED`; Candidate B remains provisional/unvalidated. Phase 1L.5t credits remain `0`; no product or source defect is inferred.

Phase `3/6` closes only through this exact-five documentation commit and later exactly two canonical Project upserts. Tasks are unchanged, Cursor is `0`, and no automatic Phase 4 is authorized. A future attempt requires a fresh gate and exact preflight.
