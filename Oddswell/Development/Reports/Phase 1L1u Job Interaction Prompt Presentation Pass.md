---
tags:
  - development
  - beta
  - phase-1l
  - job
  - presentation
status: complete-bounded-pass
date: 2026-08-08
---

# Phase 1L.1u - Job Interaction Prompt Presentation Pass

**Status:** COMPLETE - BOUNDED NATIVE JOB-INTERACTION-PROMPT PRESENTATION PASS
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap|Phase 1L delivery steps 1, 2, and 5]] and [[Design/Beta Game Bible|First-hour player journey, step 4]].

## Outcome

The exact existing Job interaction prompt now uses the established native Canvas dark field with a teal state rail. Ponytail kept the production change to one transient prompt string, one small validity selector, and reuse of the existing two-shape bottom interaction panel. No widget framework, generalized prompt system, texture, animation, external asset, dependency, tutorial, map marker, navigation system, Job fiction, or new Job was added.

The prompt is transient local process state. It is present only while the local player is within the unchanged approved Job radius in Sundale, is not saved or replicated, remains available to the local listen host, and is absent for a remote character or dedicated server.

## Frozen Job, economy, and authority contract

Exact existing wording remains:

`Press E to complete a shift (100 Odds Bucks once every 24 hours)`

The canonical Job anchor remains `(9500, 0)` with a `350 cm` radius. The existing E input, one-shot latch, server request, outside rejection, `100` Odds Bucks payout, rolling `86,400`-second cooldown, approximate retry-hour result wording, immutable ledger, local save/schema, and server authority remain unchanged. The Phase 1L.1p success/cooldown/rejection/unavailable result panels remain a separate five-second presentation path.

No map, coordinate, interaction radius, payout, cooldown, time boundary, ledger, save, authority, network, city, route, result panel, brain, simulator, wager, settlement, inventory, store, housing, or Phase 1L.1a-t behavior changed. The authored Sundale map, Studio-home save, housing catalog, and Odds Bucks ledger sources remain byte-identical to their protected baselines.

## Verification

| Check | Result |
| --- | --- |
| UE 5.8 editor Development build | PASS; `4` actions / `11.97s` |
| Focused `OddsWell.Character.JobInteractionPromptPresentation` | PASS `1/1` |
| Full native OddsWell automation | PASS `71/71`; zero failed tests |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions / `19.04s` |
| BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `30.48s` |
| Package audit | `50` files / `1,050,375,084` bytes / `0` Python files |
| Fresh standard `1280x720` prompt + E + result/retry | PASS |
| Fresh compact `888x500` prompt + E + result/retry | PASS |
| Standard and compact cold restore/cleanup | PASS |

Package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `9B7026C55EA287C08ED6BFDC340F7512B41EB60489454D728D880DFEAC1FE897`
- UFS container: `2B64050791D1421856833B92E3180B8613C2BD361BF4681C3E1DD80BFE743B78`

## Packaged prompt and economy evidence

Four accepted final-package Development logs exited `0` without fatal, assertion, ensure, unhandled-exception, or OddsWell QA failure markers:

1. Fresh standard and compact processes each proved prompt absence `1000 cm` outside the Job, then showed the exact prompt at `250 cm` inside the unchanged radius.
2. Each fresh process simulated the existing E input/latch path rather than calling a new reward path. Server validation credited exactly `+100`, producing one immutable ledger entry and balance `100`.
3. The immediate retry retained one entry/balance `100`, reported the unchanged `86,400`-second rolling cooldown, and produced no second credit.
4. Separate standard and compact cold processes restored one entry/balance `100`, retained the cooldown, and cleaned the QA save. The focused contract separately locks unrelated-location and dedicated/remote absence.

Accepted logs:

- fresh standard: `C:\tmp\OddsWellPhase1L1uFinal\Evidence\PackagedStandard.log`, `97,563` bytes, SHA-256 `F3C2515E855879A1765CC331DD7FC8073E05BD8EDEF6A66F9D307964132AAE33`
- standard cold: `C:\tmp\OddsWellPhase1L1uFinal\Evidence\PackagedStandardCold.log`, `95,112` bytes, SHA-256 `4F626839DBEEC977858AB76ADF898ED07DE177AACB6EB4D0DB286366419F37C2`
- fresh compact: `C:\tmp\OddsWellPhase1L1uFinal\Evidence\PackagedCompact.log`, `98,234` bytes, SHA-256 `095DFEB56D37EE325599794F67013E0EDE0E95E2A614E0B759802DB16C382612`
- compact cold: `C:\tmp\OddsWellPhase1L1uFinal\Evidence\PackagedCompactCold.log`, `95,776` bytes, SHA-256 `E74B8DBE33A025BA35B19B917E192AB9D6FCACC443EED34F6D4DCC76F75C47DA`

## Visual and performance evidence

Original-resolution inspection found the complete exact prompt inside the two-shape panel in both accepted prompt frames, without observed panel or text clipping. The fresh runs also captured the retained result panels; the exact success and cooldown lines are complete, and the simultaneous bottom prompt does not overlap those top panels in the accepted standard or compact frames.

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Standard prompt `1280x720` | `1,296,751` | `80AB383417CE59C29B62F4664A75CCF8B4DFF18270E589410A94F9A4CA6086F3` |
| Compact prompt `888x500` | `610,232` | `FF569BEBD32049F980E80054990262CEC079471F61089E001A4E8BAA2D16E154` |
| Standard success `1280x720` | `1,233,020` | `B98D12949390827A97F03CA42573D9FB6F376893ECF679C1111C8D38AE58BA6B` |
| Compact success `888x500` | `565,105` | `676AC3D1D35BC5E551035B4F9130D5C8B7409B38CE30EA09F9FA8DD97263486C` |
| Standard cooldown `1280x720` | `424,870` | `D0151175EC516A80533282698B22D4A3EEA3921D3300B15849527F731A53085D` |
| Compact cooldown `888x500` | `196,722` | `6764761A698F66DA1158D6E890897A63636590A35044241D545922B55C59E783` |

The prompt frames are fixed close views of the existing Job frontage with the placeholder player centered in front. The cooldown frames contain a bright graybox horizon and dark lower field. These are disclosed frame contents, not readability, lighting, art, or usability claims.

Largest active OddsWell-process sampling at roughly `500ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| Standard, all | `16` | `1141.3 / 1570.5` | `2425.3 / 3613.6` |
| Standard, warm after first five | `11` | `1456.8 / 1570.5` | `3314.9 / 3613.6` |
| Compact, all | `15` | `1206.1 / 1722.0` | `2423.6 / 3545.0` |
| Compact, warm after first five | `10` | `1498.1 / 1722.0` | `3147.9 / 3545.0` |

These are short descriptive Development-package samples, not minimum-PC evidence.

## Protected boundaries

- Sundale map: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- Studio home save cpp: `2943D697E1E630BA8D76F71A9F0E0B2976F15013C633BF61511F5E8939371B3C`
- Studio home save header: `3E7B067C82D4B0C65EBC961ED2C55DB59C91FD6AAA22A0BC809715EAD23017B9`
- housing catalog cpp: `8629D23577E891555FB711F9E472CBF9E4D6A4F1171E055F950E0692D4FA90AF`
- housing catalog header: `BAF8775550414305F900AF2A4CA2F0F68A0B2935AC64A22FF926E0BCB4CD72EA`
- Odds Bucks ledger cpp: `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7`
- Odds Bucks ledger header: `A98DEC2027A403B7AC2A66F612A84A611E20710353E3A7E8399467B98B897FE9`

## Truth boundary and phase stop

The six images are automated fixed views with no same-view pre-phase baseline. They document panel presence, complete exact text, bounded geometry, and lack of observed overlap/clipping only in those frames. The outside, unrelated, remote, and dedicated exclusions have automated contract/runtime-marker evidence rather than accepted screenshots. There was no manual Job interaction test.

The evidence does not prove text/color readability, comprehension, physical keyboard/controller behavior, accessibility, subjective usability, every state/resolution/localization, final UI/art/materials/lighting, minimum-PC performance, beta readiness, or production readiness.

No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. This is new-nightly-batch phase `6/6`; after Coordinator and Notion closure, perform the read-only final batch audit and do not begin a seventh implementation.
