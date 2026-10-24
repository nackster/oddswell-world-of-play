# Phase 1L.5ar Candidate B WORLD_CANDIDATE Diagnostic Receipt-Backed Two-Layer Skip-Build Package Proof

Status: `COMPLETE LOCALLY — WORLD_CANDIDATE_TWO_LAYER_PACKAGE_PASS; PACKAGE LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 4/6`

## Scope and authority

This phase proves one receipt-backed Development package and its full/two-layer custody after the `WORLD_CANDIDATE` diagnostic compiled in Phase 1L.5aq. It uses the selected `-skipbuild` path and does not rebuild, clean, launch the package, run the game or editor, query Defender, measure product behavior or performance, or authorize broader roadmap work.

Option A `RECEIPT_BACKED_TWO_LAYER_SKIP_BUILD_PACKAGE` is `SELECTED`. Option B `REBUILD_OR_CLEAN_PACKAGE` is `NOT_SELECTED`. Option C `LAUNCH_OLD_PACKAGE_OR_COLLAPSE_PACKAGE_AND_RUNTIME` is `NOT_SELECTED`.

Phase 1L.5aq is truth-repaired to full commit `8f9a1bd787ac0fda73c3e4594d4a684fa2d5866e`, with independently verified exactly two canonical Project upserts, count `3/6`, and report identity `4,027` bytes/SHA `3E14CFABBD0FC4C0429B96DBBEAB4A5B369BE22C6E0BB2E26F2DB67F99E7AEE2`/blob `85f8efd06ca34af22036081f92a160ae9fa706cb`.

## Sole skip-build package attempt

The exact `577`-byte raw command has SHA `EF87B721B0B961562B0EFFD71975F8DDD2AEFECAAD387E49653147ACE440C343`. Retained cmd PID `62244` started at `2026-08-23T05:52:24.8946336Z`, exited naturally with code `0`, and drained at `2026-08-23T05:54:33.9468329Z` after `129.043968 s`. Timeout, taskkill, retry, cleanup, and launch are `false`.

AutomationTool exit-success and overall build-success counts are `1/1`; cook, stage, package, and archive completion counts are each `1`; both exact map-custody markers occur once. Build-command start/completion, Candidate compile, and game/editor link-or-metadata progress counts are `0/0/0/0`. Neutral ValidatePlatforms, bound `Trace.uba`, and disabled UBA/Horde configuration counts are `1/1/1`; unclassified UBT mode, low-memory, named-missing, fatal, and security counts are `0`.

## Exact-four evidence

| artifact | bytes | SHA-256 | custody |
|---|---:|---|---|
| `BuildCookRun.combined.txt` | 75,678 | `C34B8B94F822316443B464C3FCD70528127057C909C32F164582858DFA895E56` | process-created, immutable |
| `session_custody.tsv` | 13,337 | `219D53ADADDF88F8E5842201B24A111CCC44ABF0B909BCDA62F984F2B1093416` | exact 281 ordered rows |
| `package_manifest.tsv` | 6,266 | `00B348B2168F8C66B1B98CF25BB71A8DF7B7E0AF78AD04FEA4CC6B4AD422E4B7` | complete 50-row PackageFinal inventory |
| `saved_manifest.tsv` | 6,266 | `00B348B2168F8C66B1B98CF25BB71A8DF7B7E0AF78AD04FEA4CC6B4AD422E4B7` | complete 50-row current staged inventory |

The transcript is strict UTF-8 without BOM or NUL, contains `833` CRLF records and no bare LF/CR, ends CRLF, and remained byte/hash/mtime-identical across observations separated by `6.0044693 s`. The session is strict UTF-8 without BOM/NUL/CR, has `281` unique nonblank ordered rows and a final LF, preserves `receipt_backed_skip_build_package_credit` as key 197 and `package_custody_credit` as key 198, and has no row 282. Exact-four replay mismatch is `0`.

## Package and two-layer custody

PackageFinal and the current staged root each contain `50` files totaling `1,052,121,260` bytes. Their complete ordinal case-sensitive relative-path/byte/SHA manifests are byte-identical, with normalized mismatch `0`. The wrapper occurs once. The packaged game executable is `341,429,760` bytes/SHA `66FC9F8E407C670908CD8AB703E0850CB7E3DD8228A41A8B5CAE04F1602DA510`; the packaged game PDB is `380,547,072` bytes/SHA `73F34752028F3C1989970B699C2B7B2E4D1C26E8B7A18AE6D58CE48CE676690F`. Both equal their frozen prebuilt inputs. Required `OddsWell-Windows.pak`, `.utoc`, and `.ucas` each occur once with no case-variant duplicate.

The `PHASE1L5AR_V1` cross-run projection removes only `Manifest_DebugFiles_Win64.txt`, `Manifest_NonUFSFiles_Win64.txt`, `Manifest_UFSFiles_Win64.txt`, `OddsWell/Binaries/Win64/OddsWell.exe`, and `OddsWell/Binaries/Win64/OddsWell.pdb`. Its remaining `45` rows are `5,742` bytes with SHA `04F44B5EBEDC17110698BF8BBD9393F77F9007AB86FC7B11F29D63340923B782`.

The Debug manifest is `433` bytes/SHA `70BAC146180F1191A06A8AFB49F6ECCDA19B0968FE6749709C8700D5E7E765E5`, with `6` unique grammar-valid rows and path projection `277` bytes/SHA `16C8689A446390C8383BA65774CED8D6B1EE3ADBF8B14C8B0FA2A5090259C7C3`. The NonUFS manifest is `3,021` bytes/SHA `595FC4C5796422A1F68264C02B691C4FD5C8B96345E8043D234F6EB0FB710822`, with `36` unique rows and path projection `2,085` bytes/SHA `AC78DD0D01845B21A3184F9A10D3C680BFD4271E50E989A4909FF7F3DC60AED5`. The UFS manifest is `208,701` bytes/SHA `ECA2DA9FB02F920E36E0C2BCA6A97E22F78A2B260E5812AD7FD5F22A4D97FFAC`, with `2,366` unique rows and path projection `147,185` bytes/SHA `1772FD1893E0DA5194108875DB3F7637496089EAA6318AE164345665AA120745`. Missing, unexpected, duplicate, malformed, timestamp-parse, and unexpected stable-drift counts are all `0`. Timestamp values and source order are recorded, not cross-run predicates.

## Output, source, and process custody

All seven frozen game/editor object, executable, PDB, DLL, and receipt identities remained byte/mtime/SHA-identical. All ten tracked source/config/map inputs remained exact; repository HEAD stayed `8f9a1bd787ac0fda73c3e4594d4a684fa2d5866e` and clean. The exact PID `26944` command-process exclusion remained identity-exact and untouched; PID `58852` was absent as allowed. Watched process residue, unreadable process count, retained-PID TCP/UDP residue, and every TCP/UDP `17777/1985/7810` cell are `0`.

## Credits and nonclaims

`receipt_backed_skip_build_package_credit=1` and `package_custody_credit=1`. Current package launch, game/editor launch, runtime activation, policy application, renderer, visible window, route, gameplay, product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, and readiness credits are `0`. Product is `NOT_MEASURED`; Candidate B remains provisional/unvalidated. Zero security markers are an immutable-transcript observation, not a Defender-clean claim. No runtime, policy, product, defect, security, or readiness claim is made.

FRESH BATCH PHASE 4/6 CLOSED — NO AUTOMATIC PHASE 5
