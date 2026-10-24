# Phase 1L.5bc Candidate B Exact World-Package Correction Receipt-Backed Two-Layer Skip-Build Package Proof

## Status

`COMPLETE LOCALLY — EXACT_WORLD_PACKAGE_CORRECTION_TWO_LAYER_PACKAGE_PASS; PACKAGE/GAME LAUNCH NOT RUN; PRODUCT NOT MEASURED; AUGUST 26 NIGHTLY BATCH PHASE 3/6`

Phase 1L.5bc performed one direct receipt-backed `-skipbuild` package and custody attempt for the corrected Candidate B game executable. It proves exact package/staged identity and two-layer custody. It does not prove package launch, runtime activation, policy behavior, broad product behavior, or readiness.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `ONE_RECEIPT_BACKED_TWO_LAYER_SKIP_BUILD_PACKAGE` | `SELECTED` | `RECOMMENDED` | It is the smallest custody proof for the corrected prebuilt game binary. |
| B | `REBUILD_OR_CLEAN_BEFORE_PACKAGE` | `NOT_SELECTED` | `REJECTED` | Rebuild or clean would mutate the frozen receipt-backed outputs. |
| C | `LAUNCH_PACKAGE_OR_COLLAPSE_PACKAGE_AND_RUNTIME` | `NOT_SELECTED` | `REJECTED` | Launch is a separate downstream dependency and would collapse package and runtime evidence. |

## Baseline and attempt

Baseline and post HEAD are `8cc71e1da84abd58281996bad52287196b224582`, clean with index `0`. Candidate source, module source, locomotion source, build and target files, project descriptor, engine configuration, and both maps retained their frozen identities. The seven game/editor output and receipt inputs also remained byte/hash/mtime-identical.

The exact one-string raw value was `573` UTF-8 bytes, SHA `C0C4981CCC96FC73E41039B289DB81D2F47421EEA661B9F8828914F62E2CEB85`. It contained one `-skipbuild` token and no build or clean token. The sole retained cmd child was PID `48628`, started `2026-08-26T13:13:51.2982044Z`, ended at the terminal observation `2026-08-26T13:15:25.8718317Z`, and elapsed `94.5255356` seconds. It exited naturally `0`; timeout, taskkill, retry, and cleanup were not used, and the process tree drained.

## Transcript result

The process-created immutable transcript is `72,869` bytes, SHA `57847D09C8943758427DC4CFA7747BB1CE97DCEB1AB128A9E0C9765BC65810A2`. It was stable twice over `13.1164845` seconds, strict UTF-8 without BOM or NUL, with `809` CRLF records, no bare LF/CR, and final CRLF.

| observation | count |
| --- | ---: |
| AutomationTool exit success | 1 |
| BUILD SUCCESSFUL | 1 |
| cook / stage / package / archive completed | 1 each |
| exact HasMapsToCook / Params.HasMapsToCook payload | 1 each |
| build command started / completed | 0 / 0 |
| Candidate compile / game-or-editor link-or-metadata | 0 / 0 |
| ValidatePlatforms / Trace.uba / disabled UbaHorde configuration | 1 / 1 / 1 |
| unclassified UBT / low-memory / named-missing / reliable failure / fatal / security | 0 each |

## Package and two-layer custody

PackageFinal and the current staged root each contain exactly `50` files totaling `1,052,121,260` bytes, with Saved-segment and Python counts `0`. The wrapper occurs once. The required `OddsWell-Windows` pak, utoc, and ucas each occur once with no case-variant duplicate.

Both layers contain the corrected prebuilt game executable at `341,429,760` bytes/SHA `8D90D8D5A02C05FB2967C305D8EAAC1A16C10726714FBA52A42B6CD8259A0FBC` and corrected PDB at `380,547,072` bytes/SHA `83304636D8BB271111CC27E8AE7651093B408983A47BC54BC543660CD9C20726`. The wrapper is `171,520` bytes/SHA `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.

The complete package and staged manifests are byte-identical, each `50` rows, `6,266` bytes, SHA `FA5A101D318118206BFC1A81C7EA73491D96515941D14665584D8D6A00D536E4`. Under `PHASE1L5BC_V1`, the exact `45` stable outer rows remain `5,742` bytes/SHA `04F44B5EBEDC17110698BF8BBD9393F77F9007AB86FC7B11F29D63340923B782`. The sorted path projections match for Debug (`6` rows, `277` bytes, SHA `16C8689A446390C8383BA65774CED8D6B1EE3ADBF8B14C8B0FA2A5090259C7C3`), NonUFS (`36` rows, `2,085` bytes, SHA `AC78DD0D01845B21A3184F9A10D3C680BFD4271E50E989A4909FF7F3DC60AED5`), and UFS (`2,366` rows, `147,185` bytes, SHA `1772FD1893E0DA5194108875DB3F7637496089EAA6318AE164345665AA120745`). All occurrence, uniqueness, grammar, duplicate, malformed, timestamp-parse, missing, and unexpected checks passed. Generated timestamp values and source order remain recorded, not cross-run predicates.

## Evidence custody

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Evidence/BuildCookRun.combined.txt` | 72,869 | `57847D09C8943758427DC4CFA7747BB1CE97DCEB1AB128A9E0C9765BC65810A2` |
| `Evidence/session_custody.tsv` | 13,705 | `E8858032ED12CDDEFE1DAB17D8E7C98EDDD0EB89072288894131DE118765BE24` |
| `Evidence/package_manifest.tsv` | 6,266 | `FA5A101D318118206BFC1A81C7EA73491D96515941D14665584D8D6A00D536E4` |
| `Evidence/saved_manifest.tsv` | 6,266 | `FA5A101D318118206BFC1A81C7EA73491D96515941D14665584D8D6A00D536E4` |

The session contains exactly `283` unique ordered rows with key 199 `receipt_backed_skip_build_package_credit` and key 200 `package_custody_credit`. All TSVs are UTF-8 without BOM, LF/final LF, and replayed byte-exactly. The three frozen pre-existing cmd identities remained ignored and untouched. Watched-process residue, unreadable custody, retained-PID TCP/UDP, and TCP/UDP ports `17777`, `1985`, and `7810` all replayed `0`.

## Credits and boundary

`receipt_backed_skip_build_package_credit=1`; `package_custody_credit=1`; `exact_world_package_correction_package_credit=1`. Phase 1L.5ba focused automation credits and Phase 1L.5bb game-build credits remain prior-only. Current package launch, runtime activation, policy application/full validation, renderer, visible client, route, gameplay, product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, validation, and readiness credits are `0`. Product is `NOT_MEASURED`; readiness is `NOT_CLAIMED`; Candidate B remains provisional/unvalidated. Zero security markers do not establish a security-clean or Defender-clean state.

Phase 1L.5bb is truth-repaired to full commit `8cc71e1da84abd58281996bad52287196b224582`, independently verified exactly two canonical Project upserts and August 26 nightly count `2/6`. Its report is `Oddswell/Development/Reports/Phase 1L5bb Candidate B Exact World Package Correction Game Build Proof.md`, `5,071` bytes, SHA `04B5431A901A171496B2CC0A1C1F8B0749676E1043BEC5A0EE760AF1D202454A`, blob `7b4a45857ec6eeaad2d90d18d608182aeb082878`. No Tasks or Cursor artifact is created.

AUGUST 26 NIGHTLY BATCH PHASE 3/6 CLOSED — NO AUTOMATIC PHASE 4
