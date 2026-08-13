---
tags:
  - development
  - phase-1k
  - packaged
  - evidence
status: complete-evidence-limited-fail
date: 2026-08-12
---

# Phase 1K.9c — Automated Packaged Components One Through Three Smoke Suite

**Status:** COMPLETE — EVIDENCE-LIMITED FAIL AT LANE A; LANES B/C NOT RUN
**Batch:** replacement Phase `3/6`
**Cost:** `$0.00`

## Outcome

The approved three-lane automated packaged smoke measurement stopped at its first evidence-custody failure. Lane A produced diagnostic mechanics markers for the existing chooser and shared-city path, but its owner process did not complete within the harness's `40`-second `WaitForExit` bound. The custody record therefore truthfully contains `owner_completed=false` and `owner_exit=null`.

The owner log later closed normally `0.223s` after custody ended. A log close is not an operating-system exit code, so no exit result is inferred. Lane A receives zero lane or component credit. The fail-fast contract left lanes B and C **NOT RUN**. This is an evidence-harness custody failure, not a measured product defect or a smoke-suite pass.

## Frozen package and preflight

The suite reused the accepted Phase 1L.4b Windows Development package without changing it:

| Contract | Exact result |
| --- | --- |
| Package excluding runtime `Saved` | `50` files / `1,051,962,028` bytes / `0` Python |
| Wrapper SHA-256 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| Game executable SHA-256 | `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A` |
| UFS `.ucas` SHA-256 | `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356` |
| `SundaleGraybox.umap` SHA-256 | `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Repository baseline | `c4cd32c55924159ab140f21faf7762a8d8c2fd82`, clean |
| Preflight processes / gameplay ports | `0`; TCP/UDP `17777`, `1985`, and `7810` all `0` |

No source, configuration, map, test, package, art, gameplay, economy, brain, save schema, authority, or dependency changed. No new QA flag, script, input driver, or framework was added.

## Exact lane plan and result

| Lane | Existing QA path | Result |
| --- | --- | --- |
| A | Fresh chooser owner plus machine-local shared-city peer/owner | **EVIDENCE-LIMITED FAIL**; owner OS exit custody incomplete |
| B | `StudioQa` plus `StudioAutoExit` | **NOT RUN** because Lane A failed first |
| C | `SundaleRouteQa` plus `SundaleRouteRun` and existing auto-exit | **NOT RUN** because Lane A failed first |

Lane A used fresh isolated peer and owner profiles. The peer launched the existing listen path on `127.0.0.1:17777`; the owner used the existing one-step non-default chooser automation and existing shared-city auto-exit path. There was no manual input, Computer Use gameplay, Job QA, Job `E`, store action, Stadium/Arena action, wager action, or economy mutation.

## Lane A custody failure

- Peer PID `32512` bound gameplay UDP `17777` and returned exact process exit `0`.
- Owner PID `17016` did not complete within the harness's `40`-second wait.
- `custody.json` records `owner_completed=false` and `owner_exit=null`.
- The owner log closed at `2026-08-13T02:22:18.208Z`, `0.223s` after the custody interval ended.
- The owner process no longer existed when read-only recovery was attempted, so its exit code was unrecoverable.
- No rerun was performed. Lanes B and C were not started.

The following markers are retained as diagnostic-only observations and grant no component credit:

- one non-default `masculine_tone_2` appearance save with the unchanged off-white starter items;
- existing client-travel handoff to `127.0.0.1:17777`;
- peer `clients=2`;
- owner `actors=2`, visible names, and pawn collision ignore;
- shared appearance `agreement=true`;
- peer locomotion QA `result=PASS`.

The peer's normal startup created canonical scheduled-game, pregame-commitment, and match-winner-offer saves plus a read-only reconciliation JSON. These are baseline startup artifacts, not player actions. The reconciliation and ledger markers report `entries=0`, `balance=0`, `next_job_payout_unix=0`, and `wagering=false`. There is no Job ledger save, Job marker, Store marker, Stadium/Arena marker, wager marker, or forbidden interaction evidence.

## Frozen evidence ledger

Evidence root: `C:\tmp\OddsWellPhase1K9c-20260813T022041Z`

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Evidence/evidence_manifest.json` | `2,967` | `9313764DF15438981F7BA0747EA5518E25C26F6A66689CE14A64C883F51348C8` |
| `Evidence/LaneA/custody.json` | `1,169` | `D0DAEF0AFA23AD833BBDF85961BB717CDEB6AD7C6A36A07860D182D2D77DE02C` |
| `Evidence/LaneA/failure.json` | `1,593` | `20E7155259434B9BA4C41A03ED2F673F163AF9329913227FD96FBD5F5402F136` |
| `Evidence/LaneA/Owner.log` | `100,115` | `0D964C18AB87D6F00A3577842B1335A1215F858A6C55BF786D9A1F9628393E25` |
| `Evidence/LaneA/Peer.log` | `104,956` | `F6AC97C8137E6ECF42F848E1EFFB8CEC6FB618CF27D10F2CDE01B8D285ADFE30` |
| Owner appearance save | `2,183` | `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98` |
| Peer reconciliation JSON | `503` | `CCAA35514A2836661AFF31E2D47502EF982B08E98660AE3465E3CBA6B4099F1C` |
| Peer match-winner offer | `2,960` | `4FC941AF87E210A1720A7BBBF6C64C40C039DFDF0DC273BABB5DB328725C18AF` |
| Peer pregame commitment | `5,153` | `D00134E4084048295A0E2CFF122D8F18A5ED9269F72712883CCED2D5AB8A0292` |
| Peer scheduled game | `2,771` | `43A27F915DFD1ECE29C4724ACB4F1382FB6582272800B882E103BDEDF7476C78` |

The isolated profiles remain frozen for evidence custody and are not reused. Final target-process count is `0`; TCP/UDP `17777`, `1985`, and `7810` listeners/endpoints are all `0`.

## Evidence boundary

This attempt earns component credit `0` and lane credit `0`. It is not contiguous first-hour evidence and is not equivalent to normal physical play. It proves no physical held control, discovery, comprehension, hesitation, usability, accessibility, same-peer Studio flow, full route, beta readiness, or production readiness.

Hands-on evidence remains incomplete, owner-deferred until the beta-ready playtest boundary, and not waived. Phase 1K remains incomplete. No production correction is authorized from this evidence-limited failure.

Execution creates no Notion or Cursor task; Cursor task count remains `0`. After Coordinator post-commit verification, the separate Notion role must perform exactly two duplicate-checked upserts for the canonical milestone status and evidence result.
