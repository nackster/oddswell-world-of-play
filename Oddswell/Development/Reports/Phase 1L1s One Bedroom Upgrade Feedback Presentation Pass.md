---
tags:
  - development
  - beta
  - phase-1l
  - housing
  - presentation
status: complete-bounded-pass
date: 2026-08-08
---

# Phase 1L.1s - One-Bedroom Upgrade Feedback Presentation Pass

**Status:** COMPLETE - BOUNDED NATIVE ONE-BEDROOM-UPGRADE FEEDBACK PRESENTATION PASS
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap#Phase 1L â€” Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#Experience consequence|Experience consequence]], and [[Design/Beta Game Bible#Apartment progression|Housing and furniture]].

## Outcome

The three existing One-Bedroom upgrade-result states now reuse the small native Canvas feedback panel already used by the Job, Signal Jacket, and Modular Chair. Ponytail kept the implementation to one housing-specific message builder, the existing two-shape dark field/state rail, the existing five-second lifetime, and the existing standard/compact geometry. No widget framework, texture, animation, external asset, dependency, housing tier, layout, decoration, refund, trade, or final UI was added.

The owning client still receives only the existing purchase-success, already-owned, or rejection text. Feedback is transient local process memory: it is not saved or replicated. One-Bedroom ownership and Studio construction continue through their existing authoritative ledger and home paths.

## Frozen Apartment Management, housing, Studio, and economy contract

- Apartment Management remains at `(0, 800)` with the exact `350 cm` interaction radius and existing E-driven review/two-confirm purchase path.
- The only implemented housing upgrade remains `one_bedroom` at exactly `500` Odds Bucks, with existing Studio ownership required first.
- Exact existing result wording remains:
  - `One-bedroom upgrade purchased | Balance: 0 Odds Bucks`
  - `One-bedroom already owned | Balance: 0 Odds Bucks`
  - `One-bedroom upgrade rejected` when no server detail is supplied; authoritative server rejection detail still passes through unchanged.
- The automated purchase retains the existing QA funding path: one `600` funding entry, one immutable chair `-100` debit, and one immutable One-Bedroom `-500` debit, producing exactly three ledger entries and balance `0`.
- An opt-in authoritative duplicate check returns owned without purchase, retains three entries/balance `0`, and creates no second debit.
- The owned interior remains the original six Studio surfaces plus exactly three partition surfaces and an open doorway. The existing chair remains exactly three gray/teal parts at `studio_primary`.
- A fresh Studio remains exactly `structure=6,upgrade_surfaces=0,furniture=0,furniture_parts=0,decorations=0,snap_points=0`.
- Later housing tiers remain locked without prices or layouts. Entry, exit, exact city return, point light, ledger/save/schema/slot/index, server authority, shared session/network, wagers/settlement, inventory, store behavior, brains, simulator, city, and every Phase 1L.1a-r layer remain unchanged.

The authored Sundale map, Studio-home save, housing catalog, and Odds Bucks ledger sources remain byte-identical to their baselines. This phase changes only `PlaceholderLocomotion.cpp`, bounded automated QA support in that file, documentation, and the affected roadmap canvas.

## Verification

| Check | Result |
| --- | --- |
| UE 5.8 editor Development build | PASS; `4` actions / `11.56s` |
| Focused `OddsWell.Character.OneBedroomFeedbackPresentation` | PASS `1/1` |
| Full native OddsWell automation | PASS `69/69`; zero failed tests |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions / `18.99s` |
| BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `30.47s` |
| Package audit | `50` files / `1,050,310,060` bytes / `0` Python files |
| Fresh standard `1280x720` purchase/presentation/Studio process | PASS |
| Fresh compact `888x500` purchase/presentation/Studio process | PASS |
| Compact and standard cold restore/cleanup | PASS |
| Separate fresh empty-Studio route | PASS |

Package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `EE1B4ED56352FB1BB46B7696E5147C4F737AAB55BE6BCFFE997512040BBB3B2C`
- UFS container: `2B64050791D1421856833B92E3180B8613C2BD361BF4681C3E1DD80BFE743B78`

## Packaged purchase, ownership, and Studio evidence

Five accepted current-package Development processes exited `0` without fatal, assertion, ensure, unhandled-exception, or OddsWell QA failure markers:

1. The fresh `1280x720` process used the unchanged physical Furniture Store and Apartment Management two-confirm paths. It retained exactly three ledger entries/balance `0`, ownership `true`, and duplicate debit `false`. Its presentation marker covered all three exact feedback states with mask `7`, two native Canvas shapes, and no display-fixture mutation. It then entered the private Studio and found the exact three-surface partition/open doorway and one chair with three parts at `studio_primary`.
2. The fresh `888x500` process independently repeated the same purchase, duplicate, presentation, and exact Studio result.
3. The standard-profile cold process restored three entries/balance `0`, both ownership records, the same partition/open doorway and chair, then removed the QA ledger and Studio-home saves.
4. The compact-profile cold process independently reproduced the same restored state and cleanup.
5. A separate fresh user used the existing automated Studio route. It reported `structure=6,upgrade_surfaces=0,furniture=0,furniture_parts=0,decorations=0,snap_points=0`, walked `201.3 cm`, exited, returned to Sundale, and exited normally.

The already-owned and fallback-rejection messages are display-only automated fixtures after the real successful purchase and authoritative duplicate check. They do not call purchase authority or mutate the ledger, ownership, home save, or Studio contents.

Accepted logs:

- standard purchase/Studio: `C:\tmp\OddsWellPhase1L1sFinal\Evidence\Runtime\Standard\PackagedOneBedroomFeedbackFinal.log`, `102,071` bytes, SHA-256 `F01548DA80890AA92046D1A82652391A622FF90015EFA3BC3384E31BB9DF9F5A`
- compact purchase/Studio: `C:\tmp\OddsWellPhase1L1sFinal\Evidence\Runtime\Compact\PackagedOneBedroomFeedbackFinal.log`, `102,607` bytes, SHA-256 `BC1CAC4E033FE7F44D91E019745741F59D70D7759A1996F192859A3F99D53E01`
- standard-profile cold restore: `C:\tmp\OddsWellPhase1L1sFinal\Evidence\Runtime\Cold\PackagedOneBedroomColdStandardFinal.log`, `89,837` bytes, SHA-256 `249552B7F8EEA3D5A809BF97BF75D0FD8C964492947B270E1DF27E91E8C54A8F`
- compact-profile cold restore: `C:\tmp\OddsWellPhase1L1sFinal\Evidence\Runtime\Cold\PackagedOneBedroomColdCompactFinal.log`, `89,833` bytes, SHA-256 `EB5135570FCA58864C9CB1B84561CF44B0D45A14E18AC0103B3535ACFDB273E8`
- fresh empty Studio: `C:\tmp\OddsWellPhase1L1sFinal\Evidence\Runtime\FreshStudio\PackagedFreshStudioFinal.log`, `107,712` bytes, SHA-256 `C008236599B17AE9DDFE45589821361CC0731DA30098AA06C7E8249CA1C20B02`

## Visual and performance evidence

Original-resolution inspection found the complete exact purchase-success line inside the panel at both accepted dimensions, without observed panel or text clipping:

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Standard purchase `1280x720` | `885,699` | `1B7A8F6719C0713706A7312C0C3B42BE0FF16C78CC9F2BC4D526A454DC2C267A` |
| Compact purchase `888x500` | `412,125` | `B285A397380B1DD39698060E6A1FD16E7FDCECF514898F06D4ED91A09F83A891` |

The existing automated Studio views document the same bounded partition/open doorway and retained chair:

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Fresh standard Studio `1280x720` | `1,161,793` | `F84D5708694E6A3F2B675F4A0858CF00AB668A57F173E8CB9BE0A2FD4CC1104D` |
| Fresh compact Studio `888x500` | `580,050` | `C0B64E20A733A6663FFDD126AE62C57D9DEA5B58F5156F887AA8E687DAE8ED2A` |
| Cold standard-profile Studio `1280x720` | `1,160,080` | `46566FF269868272D30BBF6880D80B231E8F6E08B4BB296340026412740A5DCD` |
| Cold compact-profile Studio `1280x720` | `1,166,135` | `183BBBCA1DFFA5090E1DD629A207769021BBA637195340E01EBE89A0EED4FC45` |

The purchase views use an automated fixed position outside the kiosk radius and include dark overhead architecture plus a bright graybox horizon. The Studio views include the existing home-progression/exit text and partially foregrounded chair. Those are disclosed frame contents, not presentation or usability claims.

Actual client-process sampling at roughly `250ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| Standard, all | `45` | `1223.6 / 1591.2` | `2725.2 / 3653.8` |
| Standard, warm after first five | `40` | `1354.4 / 1591.2` | `3051.7 / 3653.8` |
| Compact, all | `43` | `1238.3 / 1544.8` | `2706.6 / 3383.1` |
| Compact, warm after first five | `38` | `1359.7 / 1544.8` | `3023.9 / 3383.1` |

These are short descriptive Development-package samples with one level transition, not minimum-PC evidence.

## Protected boundaries

- Sundale map: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- Studio home save cpp: `2943D697E1E630BA8D76F71A9F0E0B2976F15013C633BF61511F5E8939371B3C`
- Studio home save header: `3E7B067C82D4B0C65EBC961ED2C55DB59C91FD6AAA22A0BC809715EAD23017B9`
- housing catalog cpp: `8629D23577E891555FB711F9E472CBF9E4D6A4F1171E055F950E0692D4FA90AF`
- housing catalog header: `BAF8775550414305F900AF2A4CA2F0F68A0B2935AC64A22FF926E0BCB4CD72EA`
- Odds Bucks ledger cpp: `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7`
- Odds Bucks ledger header: `A98DEC2027A403B7AC2A66F612A84A611E20710353E3A7E8399467B98B897FE9`

## Truth boundary and phase stop

The two feedback images are automated fixed views with no same-view pre-phase baseline. They document panel presence, exact success text, and bounded geometry in those frames only. Already-owned and rejection states have contract/runtime-marker evidence but no accepted screenshots. The Studio images document the existing placeholder partition/open doorway and chair from one fixed viewpoint; they do not prove every angle or visual equivalence across processes. The evidence does not prove text or color readability, comprehension, physical keyboard/controller behavior, accessibility, subjective usability, every state/error/value/resolution/localization, final UI/apartment/furniture/art/materials/lighting, minimum-PC performance, beta readiness, or production readiness.

No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. This is new-nightly-batch phase `4/6`; after Coordinator and Notion closure, stop for one Scope Director gate before phase `5/6`.
