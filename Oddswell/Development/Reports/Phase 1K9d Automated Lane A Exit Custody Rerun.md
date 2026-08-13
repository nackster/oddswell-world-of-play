---
tags:
  - development
  - phase-1k
  - packaged
  - evidence
status: complete-blocked-before-valid-lane
date: 2026-08-12
---

# Phase 1K.9d — Automated Lane A Exit-Custody Rerun

**Status:** COMPLETE — BLOCKED BEFORE A VALID LANE A; CANARY PASS; LANES A/B/C NOT RUN
**Batch:** replacement Phase `4/6`
**Cost:** `$0.00`

## Outcome

The fresh exit-custody canary passed using one retained live `System.Diagnostics.Process` handle: bounded wait `true`, exact exit `0`, and parameterless wait drainage. The following Lane A runner then failed before a valid lane began because its PowerShell helper named a parameter `$args`, colliding with PowerShell's reserved automatic variable. The wrapper launched without the intended Lane A arguments, so it produced no Lane A `abslog`, no custody file, and no UDP `17777` bind.

That is a harness-only argument-forwarding failure, not a product defect. The two in-scope orphan processes were cleaned. No corrected retry occurred, and no Lane A command was accepted as evidence. Lanes A/B/C are **NOT RUN**, and lane/component credit is `0`.

## Frozen preflight

| Contract | Exact result |
| --- | --- |
| Repository | clean `a8878f78cad12a6e977610fcb52e7db54454e8a8` |
| Accepted package | `50` files / `1,051,962,028` bytes / `0` Python |
| Wrapper SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game SHA-256 | `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A` |
| UFS `.ucas` SHA-256 | `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356` |
| `SundaleGraybox.umap` SHA-256 | `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Initial target processes / ports | `0`; TCP/UDP `17777`, `1985`, and `7810` all `0` |

No source, configuration, test, package, map, art, save schema, gameplay, economy, brain, authority, or dependency changed.

## Canary

The canary used the existing `CharacterSelectAutoExit=2` flag with a fresh isolated profile. It added no flag, script, UI, or input path.

- retained PID `37824`;
- `WaitForExit(90000)=true`;
- exact `ExitCode=0`, read only after the completed wait;
- parameterless `WaitForExit()` completed drainage;
- elapsed `5.409s`;
- chooser presentation PASS: `cards=8`, `parts=16`, `roles=2`, `selected_index=0`;
- appearance saves `0`, handoffs `0`, SaveGames `0`;
- final process and port counts `0`.

## First blocker

The intended Lane A commands were not forwarded to the wrapper because the inline helper parameter used the reserved `$args` name. Wrapper PID `17220` and child PID `19500` therefore launched without the peer/listen or owner QA command line. They emitted no Lane A log or custody file and never established the required UDP `17777` peer boundary.

Both processes were force-cleaned after the invalid launch was identified. Final target process count is `0`; TCP/UDP `17777`, `1985`, and `7810` are all `0`. No product behavior was exercised, so no chooser, shared-city, Studio, route, Job, Store, Stadium, wager, ledger, or economy claim is made.

## Frozen evidence

Evidence root: `C:\tmp\OddsWellPhase1K9d-20260813T032333Z`

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Evidence/evidence_manifest.json` | `1,842` | `CF8A7A25FCEC1903E75F221FEE4453AA61C51B2DD55A1D8697E44EB2C0CDC1BC` |
| `Evidence/Canary/Canary.log` | `84,708` | `39284F2633EDC21532A67808F653436166478007286E45A4613355B44A0DD5DB` |
| `Evidence/Canary/custody.json` | `621` | `26E68A4B0D6D33935A722E0B7F60A33C6A37062A97B04442843FEBB672A13099` |
| `Evidence/LaneA/harness_failure.json` | `1,220` | `8357FFD5011370F27A36D23A7659DC16CA0636BCF9AD4F25F384FDCD997A8464` |
| Canary CrashReportClient config | `239` | `CE69D7E7BBD1A64729BD4D5724F3C1EFC47C6C3D555DA9D2C6AD741EDDC3D893` |
| Canary GameUserSettings | `1,376` | `B83359AE0EC63625F38B4B9918089C9BB69D9AA2846799EB16FB3E44EE6E8769` |

The evidence root is frozen. No rerun or mutation follows this closure.

## Evidence boundary

This attempt grants lane credit `0` and component credit `0`. It is not a Lane A mechanics result, smoke PASS, contiguous first-hour run, physical-input result, usability study, accessibility study, beta-readiness proof, or product-failure proof.

Hands-on held-control, discovery, comprehension, hesitation, usability, accessibility, same-peer Studio, and route evidence remains incomplete, owner-deferred until the beta-ready playtest boundary, and not waived. Phase 1K remains incomplete.

Execution creates no Notion or Cursor task; Cursor task count remains `0`. Replacement Phase `4/6` counts only after the exact local commit and the separate Notion role performs exactly two duplicate-checked upserts. Phase `5/6` requires a fresh Scope Director gate.
