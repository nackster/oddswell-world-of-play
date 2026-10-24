# Phase 1L.5af — Candidate B Exact Sundale Claim Development Package Build and Custody

## Status

`COMPLETE LOCALLY — PACKAGE_EVIDENCE_LIMITED; TIMEOUT IN UBA LOW-MEMORY LOOP; PRODUCT NOT MEASURED; FRESH BATCH PHASE 4/6`

- Outcome: `PACKAGE_EVIDENCE_LIMITED`.
- Qualifier: `TIMEOUT_IN_UBA_LOW_MEMORY_LOOP`.
- Attempt consumed: `1`; attempt number: `1`; retry allowed: `false`.
- Product measured: `false`.

## Prior phase custody

Phase 1L.5ae closed at commit `e7b51f488a13f01bd587e636f4d9d3e387b9017c` with independently verified exactly two canonical Project upserts and counted Phase `3/6`.

The Phase 1L.5ae native build, exact Sundale guard source compilation, and focused predicate automation credits remain prior evidence only. This phase did not consume or extend them.

## Attempt custody

The sole attempt invoked signed `C:\Windows\System32\cmd.exe` with one pre-serialized `576`-character, `576`-byte argument string, SHA-256 `DC5927AEDC130EB71A1BA16D626C35FBE03016CC8736BA996B3A8D72F545162A`. Its direct dotnet child retained the exact `20`-argument BuildCookRun vector and file-backed combined stdout/stderr redirection.

| field | observed |
|---|---|
| cmd PID | `66364` |
| start UTC | `2026-08-21T13:42:09.2030675Z` |
| cap | `1200 s` |
| elapsed | `1200.6164663 s` |
| natural exit | `false` |
| timed out | `true` |
| exact PID/path/start revalidation | `true` |
| exact retained-tree taskkill | `true`; exit `0` |
| process drain observed | `true` |
| wrapper exit | `1`, observed after forced stop |
| dotnet exit propagated | `false` |

The exact taskkill tree action was the bounded timeout cleanup. No retry, repair, exclusion, package/game launch, or post-attempt artifact cleanup followed.

## Immutable evidence

| artifact | bytes | SHA-256 | role |
|---|---:|---|---|
| `C:\tmp\OddsWellPhase1L5af\Evidence\BuildCookRun.combined.txt` | `198128` | `A9678517A52B589AF83DC7F8996CA86042C4DE6B05C7E840925C6C76A0214F75` | process-created combined transcript |
| `C:\tmp\OddsWellPhase1L5af\Evidence\session_custody.tsv` | `5733` | `8ADD075BDF1E0314ADD17E2382120AE99AB24C23D08E100A057B25DB51BB8D3E` | exact `127`-row LIMITED session |
| `C:\tmp\OddsWellPhase1L5af\Evidence\package_manifest.tsv` | `27` | `C6988B2A3D3C63F106C96F3DEB0019C7F0D2A086AEAE684CA8655BE2B88F9D05` | header-only absent-package manifest |
| `C:\tmp\OddsWellPhase1L5af\Evidence\saved_manifest.tsv` | `6266` | `BE0DFA48AC51AB9FB94D2C2CD411108FA274D1D9EB5EAF6711E30AE39D4C7871` | separately labeled pre-attempt staged-mirror inventory |

The transcript last-write time is `2026-08-21T14:02:09.0731069Z`. Stable observations at `2026-08-21T14:02:23.2368362Z` and `2026-08-21T14:02:31.7179576Z` were separated by `8.4811214 s` and returned the same size and SHA. It is strict UTF-8 without BOM, contains `0` NUL bytes, has `1181` CRLF records, `0` bare LF, `0` bare CR, `1182` split elements, and ends with CRLF. The transcript was never rewritten.

All four artifacts replayed to their frozen identities. The session has exactly `127` ordered unique keys with no blank values. The evidence directory contains exactly four files.

## Observed build boundary

BuildCookRun reached native build startup after its two clean commands. The transcript then recorded exactly `1140` `Low on memory` rows, from lines `42` through `1181`, as UBA repeatedly killed shared-PCH compile processes. The attempt did not reach a reliable terminal build result before the cap.

| predicate | count |
|---|---:|
| `AutomationTool exiting with ExitCode=0 (Success)` | `0` |
| `BUILD SUCCESSFUL` | `0` |
| BUILD/COOK/STAGE/PACKAGE/ARCHIVE completed | `0/0/0/0/0` |
| exact HasMapsToCook / Params.HasMapsToCook | `0/0` |
| real `CandidateBPolicySmoke.cpp` compile progress | `0` |
| real `OddsWell.exe` link progress | `0` |
| named missing-package / fatal / security marker | `0/0/0` |

The absence of a reliable completion or failure result makes this evidence limited. The repeated low-memory rows are retained host/build-process evidence, not proof of a product or source defect.

## Generated and package custody

The BuildCookRun `-clean` step removed both pre-attempt generated identities before the timeout:

- Candidate object pre-identity: `889117` bytes, SHA-256 `FCDF0BCFFF6BD3F9761574D506550027853FBCD8315B1D26C778269C31F92147`; post-attempt identity `NOT_AVAILABLE` because the file is absent.
- Project game executable pre-identity: `341428224` bytes, SHA-256 `A668E6334794A60B18D895276BB1B8B23DD034022CDFD9AB77AC15B9D5321226`; post-attempt identity `NOT_AVAILABLE` because the file is absent.

`C:\tmp\OddsWellPhase1L5af\PackageFinal` and its Windows package root are absent. Package file, wrapper, direct executable, PAK, UTOC, and UCAS counts are all `0`; the package manifest is therefore header-only.

The existing project staged mirror remains `50` files and `1052111532` bytes. Its manifest has `50` rows, `6239` data bytes, data SHA-256 `1E9D2A9199F11856B70F65F44E4E58CA341358E764B5BA228ED1CDFC7F1F7D57`, and live missing/mismatch/unexpected counts `0/0/0`. Its inner game executable remains the old `341428224`-byte SHA `A668E6334794A60B18D895276BB1B8B23DD034022CDFD9AB77AC15B9D5321226`. It is explicitly `existing_pre_attempt_staged_mirror_supplemental_only`; it does not substitute for a Phase 1L.5af package or prove package equality.

## Repository and process custody

Repository HEAD remained `e7b51f488a13f01bd587e636f4d9d3e387b9017c`; tracked worktree and index were clean and `git diff --check` returned `0` before these exact-five documentation edits. Candidate source, header, module, Build.cs, and project descriptor hashes remained unchanged. Watched process count and unreadable-path ambiguity were `0/0`; strict TCP and UDP cells for ports `17777`, `1985`, and `7810` were all `0` with no malformed rows.

No Defender query was performed, and no Defender-clean claim is made.

## Credits and nonclaims

- `exact_sundale_claim_package_build_credit=0`
- `exact_sundale_claim_package_custody_credit=0`
- package launch, runtime activation, policy application/readback, renderer, visible window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain maturity, and readiness credits: `0`
- product result: `NOT_MEASURED`

This phase does not demonstrate a reliable build failure, a product defect, or a source defect. It does not validate a new package, packaged execution, Candidate policy application, native renderer, visible client window, route, gameplay, performance, minimum-PC compatibility, accessibility, or beta readiness. Evidence, generated-state absence, and the stale staged mirror remain preserved; no retry or cleanup is authorized by this report.

## Boundary and stop

Phase 1L remains incomplete. Any Phase 5/6 activity requires a fresh owner-approved gate.

FRESH BATCH PHASE 4/6 CLOSED — NO AUTOMATIC PHASE 5
