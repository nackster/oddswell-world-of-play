# Phase 1L.5an — Receipt-Backed Two-Layer Skip-Build Package Proof

## Status

`COMPLETE LOCALLY — RECEIPT_BACKED_TWO_LAYER_PACKAGE_PASS; PACKAGE LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 6/6; SIX-PHASE BATCH CLOSED`

Terminal verdict: `RECEIPT_BACKED_TWO_LAYER_PACKAGE_PASS`.

This final fresh-batch phase proves a receipt-backed Development package construction and exact custody under the source-backed action predicates and the selected two-layer package identity contract. It does not launch the package or measure the product.

## Authority and prior truth

Phase 1L.5am closed at full commit `c27744442270b752365525481441719b00131b40` with independently verified exactly two canonical Project upserts and counted Phase `5/6`. Its `package_identity_projection_reconciliation_credit=1` remains a prior contract credit only. Phase 1L.5aj remains permanently `PACKAGE_EVIDENCE_LIMITED` with credits `0`, and Phase 1L.5al remains permanently `PACKAGE_FAIL` / `PACKAGE_MANIFEST_IDENTITY_MISMATCH` with credits `0`.

The attempt is bounded to Beta Delivery Roadmap Phase 1L item 5 and the Beta Game Bible safe-operation and content boundaries. Candidate B remains provisional and unvalidated. Phase 1M, roadmap Phase 2, Version 1, beta exit, Brain expansion beyond `0.6N`, product launch, and product readiness remain unauthorized.

## Sole attempt custody

- Attempt: `1/1`; retry: `false`.
- Raw argument string: `573` characters / `573` UTF-8 bytes / SHA-256 `E2344F5362C9A508C04D88E3B456074D2BBDB5B529EF0F488D4AC24B02EDC9A1`.
- Retained cmd PID: `51972`.
- Start UTC: `2026-08-22T07:23:15.7662851Z`.
- End UTC: `2026-08-22T07:25:24.8629139Z`.
- Elapsed: `129.1003493 s`.
- Natural exit: `true`; observed child exit code: `0`; origin: `NATURAL_CHILD_DIRECTLY_OBSERVED`.
- Timeout, taskkill, stopped PID tree, retry, and cleanup: `false`.
- The one raw launch used signed `cmd.exe` with direct OS stdout/stderr redirection. No wrapper/controller exit typo or internal-log substitution exists in this phase.

## Direct transcript predicates

The process-created transcript is `C:\tmp\OddsWellPhase1L5an\Evidence\BuildCookRun.combined.txt`, `72,802` bytes, SHA-256 `D424891E0F6CF2A48735D05A593D39DF3652242692B914E76DFBD2C4867D3CDB`, last-write UTC `2026-08-22T07:25:24.8257172Z`. Two stable observations were `6.0372550 s` apart. It is strict UTF-8 without BOM, contains no NUL, has `808` CRLF records, no bare LF/CR, and ends CRLF.

| Predicate | Count |
| --- | ---: |
| AutomationTool ExitCode 0 Success | 1 |
| BUILD SUCCESSFUL | 1 |
| COOK / STAGE / PACKAGE / ARCHIVE completed | 1 / 1 / 1 / 1 |
| HasMapsToCook / Params.HasMapsToCook exact two-map payload | 1 / 1 |
| ValidatePlatforms / exact `Trace.uba` / disabled UBA-Horde configuration | 1 / 1 / 1 |
| Unclassified UBT mode | 0 |
| Build STARTED / COMPLETED | 0 / 0 |
| Candidate compiler / game-or-editor link-or-metadata progress | 0 / 0 |
| Low-memory / named-missing / fatal / security | 0 / 0 / 0 / 0 |

The neutral source-backed custody markers do not prove build activity. Action predicates remain zero and all six frozen game/editor outputs retain their exact pre-attempt bytes, hashes, and mtimes, so the skip-build contract is satisfied.

## Exact-four evidence

| File | Bytes | SHA-256 | Shape |
| --- | ---: | --- | --- |
| `BuildCookRun.combined.txt` | 72,802 | `D424891E0F6CF2A48735D05A593D39DF3652242692B914E76DFBD2C4867D3CDB` | immutable direct transcript |
| `session_custody.tsv` | 11,310 | `E581BC5CF133507EF0F3573EDDEDC5F1B7D62FE3121620F5A3756B71EBAF58B7` | exact `246` ordered unique rows |
| `package_manifest.tsv` | 6,266 | `510E795A170243B979D99317367B5EC040384B90C70167D134DD6F1ACC636180` | `50` ordinal rows |
| `saved_manifest.tsv` | 6,266 | `510E795A170243B979D99317367B5EC040384B90C70167D134DD6F1ACC636180` | `50` ordinal rows |

The transcript remained byte-identical during the one evidence patch. Exact-four postwrite replay mismatch is `0`. The session is UTF-8 without BOM/NUL, LF/final-LF, with exact key order, unique nonblank values, and the directly observed child-exit origin.

## Package structure and Layer 1

PackageFinal and the current project staged root each contain exactly `50` files / `1,052,104,364` bytes. Their complete normalized path/bytes/SHA manifests are byte-identical; missing, unexpected, byte/SHA mismatch, and replay mismatch counts are `0`.

The package contains exactly one wrapper (`171,520` bytes, SHA `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`) and one direct game executable (`341,429,248` bytes, SHA `FB214D41A75E86C99F8ACD68632A389D535FAFCF71ACFDED5D48E53F5A75E3C7`) equal to the prebuilt game executable. Required `OddsWell-Windows.pak`, `.utoc`, and `.ucas` counts are `1/1/1`; case-variant duplicates, Saved-segment files, and Python-family files are `0`. This is complete same-attempt Layer 1 custody.

## Layer 2 cross-attempt identity

- Two-layer contract: `PHASE1L5AM_V1`.
- Stable outer projection: `48` rows / `6,065` bytes / SHA `113EF909504D8C9DA8DC4889E559FB2A33037B294799B72214FD327B16FC54E6` / match `true`.
- `Manifest_NonUFSFiles_Win64.txt`: occurrence `1`, `3,021` bytes, current SHA `00334C42A59CF689578B84EF57FE4CEAF8E9040B73EA5D7CB804B29F54353648`, rows/unique `36/36`, path projection `2,085` bytes/SHA `AC78DD0D01845B21A3184F9A10D3C680BFD4271E50E989A4909FF7F3DC60AED5`.
- `Manifest_UFSFiles_Win64.txt`: occurrence `1`, `208,701` bytes, current SHA `E6D45B23324F0D0F2A3D02DE7EC9690336BAE76244175297FB437CD5CB7DB951`, rows/unique `2366/2366`, path projection `147,185` bytes/SHA `1772FD1893E0DA5194108875DB3F7637496089EAA6318AE164345665AA120745`.
- Generated case-variant duplicate, missing, unexpected, duplicate-path, malformed-row, and timestamp-parse-failure counts are all `0`.
- Generated timestamp values and source order are `RECORDED_NOT_CROSS_RUN_PREDICATE`.

Both full current manifests are equal and the two-layer contract matches. The generated files remain fully custodied in Layer 1; only their timestamp values and source order are excluded from cross-run byte predicates.

## Repository, process, and output custody

HEAD remains `c27744442270b752365525481441719b00131b40`, repository/index are clean, and all twelve tracked source/config/map inputs replay exactly. The game Candidate object, game executable, game receipt, editor Candidate object, editor DLL, and editor receipt are unchanged. Watched process residue and unreadable counts are `0`; the frozen pre-existing cmd PID `26944` remains excluded and untouched. Retained-PID TCP/UDP residue is `0`; TCP and UDP cells for ports `17777`, `1985`, and `7810` are all `0`.

## Credits and nonclaims

- `receipt_backed_skip_build_package_credit=1`
- `package_custody_credit=1`
- `current_product_measurement_credit=0`
- Prior-only: `package_identity_projection_reconciliation_credit=1`
- Product: `NOT_MEASURED`
- Readiness: `NOT_CLAIMED`

No package/game launch, runtime activation, policy application, renderer/window proof, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain expansion, or product-readiness credit is earned. Hands-on remains deferred, not waived. Candidate B remains provisional/unvalidated. No product, source, build, package, or security defect is demonstrated; no Defender-clean or revocation-clean claim is made; no cleanup or successor phase is authorized.

## Six-phase ledger

1. Phase `1/6`: `7197e748f15af441416039f1549d696fba0a38bd`
2. Phase `2/6`: `5ae11c645a213bfcde7402e3452aefa32e1ccefe`
3. Phase `3/6`: `f0afb8f72d8a6077fe8801060c7bbcccbaf1ebc1`
4. Phase `4/6`: `58b879a9238f087a0bf0a900f9c23f0c95292bc6`
5. Phase `5/6`: `c27744442270b752365525481441719b00131b40`
6. Phase `6/6`: the pending local commit containing this report and its four planning-surface updates

## Boundary and stop

NO SEVENTH PHASE — SIX-PHASE BATCH STOPPED.
