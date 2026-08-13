# Phase 1K.9e Corrected Lane A Argument and Exit Custody Rerun

- Date: 2026-08-12/13 conversation boundary
- Branch: `agent/phase-0d`
- Baseline commit: `324fd7cc2f28496c8ea0012ac18f0501e3c712c7`
- Status: **COMPLETE - LANE-A AUTOMATED PACKAGED MECHANICS / ARGUMENT / EXIT-CUSTODY PASS**
- Batch position: Phase 5/6, counting only after the scoped docs commit and canonical Notion closure
- Credit: Lane A `1`; Components 1-3 `0`; Lanes B/C `NOT_RUN`
- Cost: `$0`
- Cursor: unsuitable; task count `0`

## Outcome

The corrected in-memory launch helper used the non-reserved parameter `$launchArguments`. Exact JSON round-trip validation preserved every argument token, order, value, and reconstructed command before launch. A fresh command-observed canary then proved that the child process received all 11 intended tokens and the exact `UserDir` and `abslog` paths. The canary retained its live process handle, completed inside the 90-second bound, returned exact OS exit code `0`, drained with parameterless `WaitForExit()`, emitted no save, and cleaned up.

The first and only authorized Lane A attempt then passed the same custody contract for both packaged processes. The peer child command contained all 15 intended tokens and bound UDP `17777`; the owner child command contained all 14 intended tokens. Both retained handles completed inside the 120-second bounds, returned exact OS exit code `0`, and drained. The automated mechanics evidence proves non-default chooser index `1`, the `masculine_tone_2` off-white appearance save and handoff, two shared-city clients, two visible named actors, appearance agreement, server acceptance of player 2, and the peer's existing locomotion QA `PASS`.

The server ledger remained empty: `entries=0`, `balance=0`, and `wagering=false`. Forbidden Job, store, Stadium, wager-action, settlement, and Odds Bucks append markers were `0`; fatal/assert/ensure/unhandled/`result=FAIL` markers were `0`. No Job or Odds Bucks ledger save exists. The normal fresh-profile schedule, commitment, offer, and read-only reconciliation artifacts are retained and classified below; they do not represent a wager or economy action.

This is one automated packaged Lane A smoke credit only. It gives **zero Components 1-3 credit**, is noncontiguous, and is not equivalent to physical controller/keyboard hands-on evidence. Lanes B and C were not run. Hands-on discovery, holds, comprehension, hesitation, usability, accessibility, and representative physical-input proof remain incomplete, owner-deferred until beta-ready, and not waived. This result is not a beta-readiness claim and found no product defect.

## Frozen evidence

Evidence root: `C:\tmp\OddsWellPhase1K9e-20260813T033735Z`

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `Evidence\manifest.tsv` | 1,623 | `29126D4BF65BE768F4CCF1C7BED1B6707771BAA0E8DAB2C79D719FC46B802548` |
| `Evidence\Preflight\arguments.json` | 1,997 | `9212F79F37AE309B0D7DC17853D617ECF18E8C787C49616349473E42C0D23E34` |
| `Evidence\Preflight\argument_validation.json` | 3,633 | `3918C4791122E2A9754A7ECB61422A0553650BD4EF6A2BD4D223DDBBDAB2D956` |
| `Evidence\Canary\Canary.log` | 84,709 | `D5CAA91F57262F65A24004FF2E4B08368758C51EA8452E817D756C9A60AD1E37` |
| `Evidence\Canary\custody.json` | 3,534 | `E7E0E7FBA4D418F3F922B932818E9B5BF0FE411D55ACCBF5E453BCA32435F457` |
| `Evidence\LaneA\custody.json` | 9,769 | `E7C316069DB354983F54EC0E8F75E4F02826D3EDAE05722EAF9D5F33B9075C67` |
| `Evidence\LaneA\Peer.log` | 104,892 | `BABBF8FDA1FB3B0F702A01A6DC75F6985EC31042B9D02AA1EEE8A20480377820` |
| `Evidence\LaneA\Owner.log` | 99,641 | `2C5AA5A3D983242A13ECF362B7F0B0B11D8EC67E69993981D64C27AE5F5AD4F8` |
| `Evidence\LaneA\result.json` | 1,913 | `AF7191779D7A12037BB0D010102EFEB45ACBCB91444DAD7891EAF7EB3C18FF89` |
| Owner `OddsWellCharacterAppearance.sav` | 2,183 | `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98` |
| Peer `OddsBucksReconciliation.json` | 503 | `685F490412DA5EF7FE6D93FD9642D8B0C8E5D59ABDDED0E9BE6F16A32DEA1F88` |
| Peer `OddsWellCanonicalScheduledGame.sav` | 2,771 | `85571F30660D06CE1D79C789A5F04921AD7030B0FA443C346D384E837CFDB42E` |
| Peer `OddsWellCanonicalPregameCommitment.sav` | 5,153 | `217310D14895588854D1E5E251586B058E85339C098D6C9CA8B2F361A8D899B0` |
| Peer `OddsWellCanonicalMatchWinnerOffer.sav` | 2,960 | `21DC0D9AA0F6FD9EBE77390B6841CB937C3A1FE7155747552E5482784FBCFD05` |

The manifest lists 13 subordinate evidence files with `0` missing or mismatched entries. Existing QA emitted `0` screenshots for Lane A; this closure claims automated mechanics evidence only.

## Exact custody and mechanics

- Preflight was no-launch and preserved token counts exactly: canary `11`, peer `15`, owner `14`.
- Canary: child command observed with all `11` tokens; requested log exists; completed `true`; exit `0`; drained `true`; chooser `8` cards / `16` parts / `2` roles at index `0`; SaveGames `0`.
- Peer: child PID `38528`; all `15` tokens observed; UDP `17777` bound; completed `true`; exit `0`; drained `true`.
- Owner: child PID `37668`; all `14` tokens observed; completed `true`; exit `0`; drained `true`.
- Chooser: exact non-default `selected_index=1`; catalog/gameplay/starter outfit remained unchanged.
- Shared city: `clients=2`, `actors=2`, `names=true`, `agreement=true`; player 2 appearance accepted through the server RPC.
- Movement: peer server log contains `ODDSWELL_LOCOMOTION_QA|result=PASS` with walking, running, landing, blocking-floor, and yaw markers.
- Economy boundary: reconciliation is `read_only=true`, ledger is `entries=0|balance=0|wagering=false`, and Job/ledger save count is `0`.
- Action boundary: forbidden action markers `0`; fatal/failure markers `0`; product defect `false`.

## Startup-artifact classification

The listen peer's normal fresh-profile startup created the canonical scheduled-game, pregame-commitment, and match-winner-offer saves. Their markers explicitly report no UI wager request, debit, lock transition, simulation, result, or settlement. The retained reconciliation JSON is read-only with zero entries and zero balance. These files are baseline startup artifacts, not Lane A actions and not economy credit.

## Production invariance

The accepted packaged build remained exact at `50` files, `1,051,962,028` bytes, and `0` Python files, excluding runtime `Saved` content.

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- Game executable SHA-256: `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A`
- UFS SHA-256: `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356`
- Protected map SHA-256: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- Repository production/client diff: `0`
- Final target processes: `0`
- Final TCP/UDP endpoints on `17777`, `1985`, and `7810`: `0`

No source, configuration, map, test, package, art, economy, brain, or simulator file changed. The evidence root is transient and frozen.

## Scope boundary and next gate

Phase 1K remains incomplete. This measurement does not waive the physical Components 1-3 evidence contract and does not establish controller parity, natural input discovery, prompt comprehension, sustained holds, hesitation, usability, accessibility, same-peer Studio traversal, or beta readiness. A fresh Scope Director gate is required for Phase 6/6. No Lane B, Lane C, product change, rerun, Notion action, or Phase 6 implementation is authorized here.

After Coordinator post-commit verification, the separate Notion role must perform exactly two duplicate-checked canonical upserts: milestone closure and Phase 1K.9e status. Execution creates no Notion or Cursor task.

## Related records

- [[Development/Phase 1K First-Hour Integration Evidence Contract]]
- [[Development/Beta Delivery Roadmap]]
- [[Design/Beta Game Bible]]
- [[Development/Current Plan]]
- [[Development/Reports/Phase 1K9d Automated Lane A Exit Custody Rerun]]
