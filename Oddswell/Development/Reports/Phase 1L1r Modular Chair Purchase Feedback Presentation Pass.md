---
tags:
  - development
  - beta
  - phase-1l
  - furniture
  - presentation
status: complete-bounded-pass
date: 2026-08-08
---

# Phase 1L.1r - Modular Chair Purchase Feedback Presentation Pass

**Status:** COMPLETE - BOUNDED NATIVE MODULAR-CHAIR FEEDBACK PRESENTATION PASS
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#Beta win condition|Earn-to-upgrade loop]], and [[Design/Beta Game Bible#Furniture|Housing and furniture]].

## Outcome

The three existing Sundale Modular Chair purchase-result states now reuse the small native Canvas feedback panel already used by the Job and Signal Jacket. Ponytail kept the implementation to one chair-specific message builder, the existing two-shape dark field/state rail, the existing five-second lifetime, and the existing standard/compact geometry. No widget framework, texture, animation, external asset, dependency, item, catalog entry, placement control, or final UI was added.

The owning client still receives only the existing purchase-success, already-owned, or rejection text. Feedback is transient local process memory: it is not saved or replicated. Chair ownership and the Studio display continue through their existing authoritative ledger and home paths.

## Frozen Store, furniture, Studio, and economy contract

- The Furniture Store remains at `(-9500, 5000)` with the exact `350 cm` interaction radius and existing E-driven review/two-confirm purchase path.
- The only furniture upgrade remains `sundale_modular_chair`, the Sundale Modular Chair, at exactly `100` Odds Bucks.
- Exact existing result wording remains:
  - `Sundale Modular Chair purchased | Balance: 0 Odds Bucks`
  - `Sundale Modular Chair already owned | Balance: 0 Odds Bucks`
  - `Modular Chair purchase rejected` when no server detail is supplied; authoritative server rejection detail still passes through unchanged.
- Purchase still follows the existing Job `+100` with one immutable `-100` debit, producing exactly two ledger entries and balance `0`. Ownership remains idempotent and cold-restorable.
- The owned chair remains exactly three native gray/teal parts at the single `studio_primary` point. No free placement, rotation, storage, refund, sale, trade, additional snap point, furniture item, or catalog behavior was added.
- A fresh Studio remains exactly `structure=6,furniture=0,furniture_parts=0,decorations=0,snap_points=0`.
- Ledger/save/schema/slot/index, server authority, shared session/network, wagers/settlement, inventory, apartment behavior, brains, simulator, stores, city, and every Phase 1L.1a-q layer remain unchanged.

The authored Sundale map, Studio-home save, housing catalog, and Odds Bucks ledger sources remain byte-identical to their baselines. This phase changes only `PlaceholderLocomotion.cpp`, bounded automated QA support in that file, documentation, and the affected roadmap canvas.

## Verification

| Check | Result |
| --- | --- |
| UE 5.8 editor Development build | PASS; `4` actions / `12.15s` |
| Focused `OddsWell.Character.ModularChairFeedbackPresentation` | PASS `1/1` |
| Full native OddsWell automation | PASS `68/68`; zero failed tests |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions / `19.04s` |
| BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `34.01s` |
| Package audit | `50` files / `1,050,278,828` bytes / `0` Python files |
| Fresh standard `1280x720` purchase/presentation/Studio process | PASS |
| Fresh compact `888x500` purchase/presentation/Studio process | PASS |
| Compact and standard cold restore/cleanup | PASS |
| Separate fresh empty-Studio route | PASS |

Package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `5345A117727B0B102E731C9A4D58ABFAAAEB3A8F27182383372E6188057CDCE5`
- UFS container: `2B64050791D1421856833B92E3180B8613C2BD361BF4681C3E1DD80BFE743B78`

## Packaged purchase, ownership, and Studio evidence

Five accepted current-package Development processes exited `0` without fatal, assertion, ensure, unhandled-exception, or OddsWell QA failure markers:

1. The fresh `1280x720` process used the unchanged physical Store/two-confirm path, retained exactly two ledger entries/balance `0`, ownership `true`, and duplicate debit `false`. Its presentation marker covered all three exact states with mask `7`, two native Canvas shapes, and no fixture mutation. It then entered the private Studio and found exactly one chair, three parts, and `studio_primary`.
2. The fresh `888x500` process independently repeated the same purchase, presentation, and exact Studio display.
3. The compact-profile cold process restored two entries/balance `0` and ownership, retained duplicate debit `false`, rebuilt the exact three-part chair at `studio_primary`, and removed both QA saves.
4. The standard-profile cold process independently reproduced the same restored state and cleanup.
5. A separate fresh user used the existing automated Studio route. It reported `structure=6,furniture=0,decorations=0,snap_points=0`, walked `201.2 cm`, exited, returned to Sundale, and exited normally.

The already-owned and fallback-rejection states are display-only automated fixtures after the real successful purchase. They do not call purchase authority and do not mutate the ledger, ownership, home save, or Studio contents.

Accepted logs:

- standard purchase/Studio: `C:\tmp\OddsWellPhase1L1rFinal\Evidence\Runtime\Standard\PackagedChairFeedback.log`, `100,723` bytes, SHA-256 `ED2921F1D552228415122DDB59292B03E071497E565DB8152C57BFC91720C002`
- compact purchase/Studio: `C:\tmp\OddsWellPhase1L1rFinal\Evidence\Runtime\Compact\PackagedChairFeedback.log`, `101,381` bytes, SHA-256 `DC2E645A1DD84CBEF741557349B5882A4CB82B63CB52ED3801B174908D71849C`
- compact-profile cold restore: `C:\tmp\OddsWellPhase1L1rFinal\Evidence\Runtime\Cold\PackagedChairColdCompact.log`, `89,615` bytes, SHA-256 `800D90DE442CBC235A41234E16D7EE3E3EA490E5F33998E25D1F38639C99736F`
- standard-profile cold restore: `C:\tmp\OddsWellPhase1L1rFinal\Evidence\Runtime\Cold\PackagedChairColdStandard.log`, `89,620` bytes, SHA-256 `C65132586E8C704AAB05E0D87D5362024E0F04F12FC3CA3DCC349FC73526B99F`
- fresh empty Studio: `C:\tmp\OddsWellPhase1L1rFinal\Evidence\Runtime\FreshStudio\PackagedFreshStudioFinal.log`, `107,753` bytes, SHA-256 `8A5E4BCD002FDB0EA6CB83AF915695EAD3B9A7B739C6623E2A3D7C0189F31681`

One earlier fresh-Studio diagnostic used the correct automated route but omitted the existing `-StudioAutoExit` QA flag. The route reached its PASS marker, then the wrapper stopped the otherwise-idle process at its bound. That diagnostic log is rejected. The accepted fresh-Studio process added only the existing auto-exit flag, repeated the same empty/walk/exit/return result, and exited `0`; no source correction was needed.

## Visual and performance evidence

Original-resolution inspection found the complete exact purchase-success line inside the panel at both accepted dimensions, without observed panel or text clipping:

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Standard purchase `1280x720` | `1,339,918` | `A729BDD36762680BF02BABC0DFAF2538B8F208C1FB6602E495E211D9825D882F` |
| Compact purchase `888x500` | `638,390` | `6D29F6FEDD2775C0B5E06A422E80D7F6E89A8296CF58DFB3EC8E761DB40D61E3` |

The existing automated Studio views document the same bounded three-part chair display:

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Fresh standard Studio `1280x720` | `1,238,807` | `DF229DE2FB47176392CAB32AE5CCF4E89A00BAA4DBCB059081BBE9F76A989744` |
| Fresh compact Studio `888x500` | `616,298` | `8B67F7EA7210198CA70F211527C80CD6B0C28585AFB72FBC4E0FCE4375BDAF64` |
| Cold compact-profile Studio `1280x720` | `1,255,415` | `F2D07C4928F6753FC37CA7776DA4E9C19126720578E2944E2B16B338F263726D` |

The purchase views include a centered placeholder avatar and strong late-afternoon ground shadow. The Studio views include existing home-progression and exit text. Those are disclosed frame contents, not presentation or usability claims.

Actual client-process sampling at roughly `250ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| Standard, all | `43` | `1264.5 / 1572.4` | `2835.1 / 3610.2` |
| Standard, warm after first five | `38` | `1396.6 / 1572.4` | `3186.2 / 3610.2` |
| Compact, all | `42` | `1274.0 / 1516.4` | `2768.4 / 3336.1` |
| Compact, warm after first five | `37` | `1404.9 / 1516.4` | `3104.2 / 3336.1` |

These are short descriptive Development-package samples with a level transition, not minimum-PC evidence.

## Protected boundaries

- Sundale map: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- Studio home save cpp: `2943D697E1E630BA8D76F71A9F0E0B2976F15013C633BF61511F5E8939371B3C`
- Studio home save header: `3E7B067C82D4B0C65EBC961ED2C55DB59C91FD6AAA22A0BC809715EAD23017B9`
- housing catalog cpp: `8629D23577E891555FB711F9E472CBF9E4D6A4F1171E055F950E0692D4FA90AF`
- housing catalog header: `BAF8775550414305F900AF2A4CA2F0F68A0B2935AC64A22FF926E0BCB4CD72EA`
- Odds Bucks ledger cpp: `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7`
- Odds Bucks ledger header: `A98DEC2027A403B7AC2A66F612A84A611E20710353E3A7E8399467B98B897FE9`

## Truth boundary and phase stop

The two feedback images are automated fixed views with no same-view pre-phase baseline. They document panel presence, exact success text, and bounded geometry in those frames only. Already-owned and rejection states have contract/runtime-marker evidence but no accepted screenshots. The chair images document the existing gray/teal placeholder at one fixed viewpoint; they do not prove every angle or visual equivalence across processes. The evidence does not prove text or color readability, comprehension, physical keyboard/controller behavior, accessibility, subjective usability, every state/error/value/resolution/localization, final UI/furniture/art/materials/lighting, minimum-PC performance, beta readiness, or production readiness.

No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. This is new-nightly-batch phase `3/6`; after Coordinator and Notion closure, stop for one Scope Director gate before phase `4/6`.
