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

# Phase 1L.1t - Studio Entry/Exit Prompt Presentation Pass

**Status:** COMPLETE - BOUNDED NATIVE STUDIO-INTERACTION-PROMPT PRESENTATION PASS
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap#Phase 1L â€” Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#3. Discover the starter home|First-hour player journey]], and [[Design/Beta Game Bible#Apartment progression|Housing and furniture]].

## Outcome

The five existing Studio interaction prompts now use one small native Canvas dark field with a teal state rail. Ponytail kept the production change to one message selector, one existing HUD draw path, and reuse of that HUD inside the private Studio. The treatment uses exactly two native shapes and the already established standard/compact breakpoint. No widget framework, generalized prompt framework, texture, animation, external asset, dependency, later housing tier, visit system, decoration, or final UI was added.

The prompt remains transient local process state. It is present only for the existing valid Studio doorway or private interior condition, is not saved or replicated, and remains unavailable to a listen host or dedicated server. The first packaged diagnostic correctly showed the entry panel but exposed that the private Studio still used Unreal's empty default HUD; that capture was rejected. The final source reuses the existing native HUD in the private Studio, and all final build, package, runtime, and visual evidence below comes from that corrected source.

## Frozen Studio, housing, and authority contract

Exact existing wording remains:

- `Press E to enter your empty Studio`
- `Press E to enter your Studio`
- `Press E to enter your One-bedroom`
- `Press E to leave your Studio`
- `Press E to leave your One-bedroom`

The existing `350 cm` Studio doorway radius, E input, one-shot latch, private entry/exit transition, saved return vector, same-city return, Studio ownership, save schema/slot/index, and network authority remain unchanged. The existing housing goal text remains on its original path. The Modular Chair remains exactly three gray/teal parts at `studio_primary` after ownership; a fresh Studio remains exact `structure=6,furniture=0,decorations=0,snap_points=0`. The One-bedroom remains the existing `500`-Odds-Bucks upgrade with its Studio prerequisite, two-confirm immutable debit, exact three-surface partition/open doorway, retained chair, duplicate protection, and cold persistence.

No ledger, save, housing catalog, map, doorway transform, interaction radius, purchase, partition, route, unrelated prompt, shared-session rule, brain, simulator, wager, settlement, inventory, store, city, or Phase 1L.1a-s behavior changed. The authored Sundale map, Studio-home save, housing catalog, and Odds Bucks ledger sources remain byte-identical to their baselines.

## Verification

| Check | Result |
| --- | --- |
| UE 5.8 editor Development build | PASS; `4` actions / `11.90s` |
| Focused `OddsWell.Character.StudioInteractionPromptPresentation` | PASS `1/1` |
| Full native OddsWell automation | PASS `70/70`; zero failed tests |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions / `19.55s` |
| BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `27.59s` |
| Package audit | `50` files / `1,050,352,044` bytes / `0` Python files |
| Fresh standard `1280x720` enter/leave/move/return | PASS |
| Fresh compact `888x500` enter/leave/move/return | PASS |
| Owned-chair fresh/cold prompt and Studio display | PASS |
| One-bedroom fresh/cold enter/leave and interior invariants | PASS |
| Existing two-client shared-city authority/movement/appearance | PASS |

Package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `E555EFA01BB6B4D645D9318E079F24FFE81ADEFFF0CDEE1A623A79668791F7F1`
- UFS container: `2B64050791D1421856833B92E3180B8613C2BD361BF4681C3E1DD80BFE743B78`

## Packaged prompt, housing, and shared-authority evidence

Eight accepted final-package Development logs exited without fatal, assertion, ensure, unhandled-exception, or OddsWell QA failure markers:

1. Fresh standard and compact processes each showed the exact empty-Studio enter prompt, entered the private Studio, showed the exact Studio leave prompt, retained `structure=6,furniture=0,decorations=0,snap_points=0`, walked `200.5/200.4 cm`, exited, and returned to Sundale.
2. The fresh Modular Chair process used the existing physical two-confirm purchase, retained exactly two ledger entries/balance `0`, showed `Press E to enter your Studio`, entered, and retained the exact three-part chair at `studio_primary`. Its cold process restored the same state and cleaned the QA saves.
3. The fresh One-bedroom process used the existing chair and Apartment Management purchase path, retained exactly three ledger entries/balance `0`, showed exact One-bedroom enter and leave states, and retained the exact partition/open doorway and three-part chair. Its cold process restored the same state and cleaned the QA saves.
4. The existing two-client listen automation retained `clients=2`, mutual visible-player and starter-appearance agreement, client-RPC appearance acceptance, `301.9 cm` authoritative replicated movement, and normal automated exit. The focused contract separately locks local standalone/client eligibility, remote/listen/dedicated exclusion, and prompt absence outside the existing valid condition.

Accepted logs:

- fresh standard: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\FreshStandardFinal\PackagedFreshStudioStandardFinal.log`, `108,222` bytes, SHA-256 `BBFF8C909CE0D868446A73CA980F58A79150652D67BDA1EB7198A549DBEB345E`
- fresh compact: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\FreshCompactFinal\PackagedFreshStudioCompactFinal.log`, `108,877` bytes, SHA-256 `EF40665F6F2FFEC6BFABDF1163CA5363D3CE659DFF9A64AA7374043D36B5E5BC`
- chair fresh: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\ChairFinal\PackagedChairFreshFinal.log`, `100,701` bytes, SHA-256 `A9C26C4B6F067379F86CCB07B265FC8873113F340D24BE9FCDF16FFC27E5D359`
- chair cold: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\ChairFinal\PackagedChairColdFinal.log`, `89,815` bytes, SHA-256 `E89209777AF6D53CB7634DF29EFE7EB5CC2468855E74B21E7211A38650BACB5E`
- One-bedroom fresh: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\OneBedroomFinal\PackagedOneBedroomFreshFinal.log`, `102,213` bytes, SHA-256 `11783A85428D0D1F461D09E52CE4319AA660DC4AF608B0DCBDE032C72F6922AA`
- One-bedroom cold: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\OneBedroomFinal\PackagedOneBedroomColdFinal.log`, `90,041` bytes, SHA-256 `A6637905B74163484BBB568F83858A6A9B09C2223B1AD3B94C4A64BA5E4B4C66`
- shared-city listen peer: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\SharedCityFinal\PackagedSharedCityServerFinal.log`, `82,614` bytes, SHA-256 `4B8B4A3508E0A4229F2DE5AAE075E5B6832600EA57954A9769A7DB272514DB61`
- shared-city client: `C:\tmp\OddsWellPhase1L1tFinal\Evidence\Runtime\SharedCityFinal\PackagedSharedCityClientFinal.log`, `95,731` bytes, SHA-256 `6D61D9B96517391FE6127C9F70E0F0EF7CB77AED5FC17BD23645ABE9F91610B3`

## Visual and performance evidence

Original-resolution inspection found the complete exact prompt text inside the panel in all four accepted fixed views, without observed panel/text clipping or overlap:

| Image | Bytes | SHA-256 |
| --- | ---: | --- |
| Standard empty-Studio enter `1280x720` | `971,610` | `E9280378B387D6B31226909B6CA69BC319BE479AF3F149EB7B3C528881128203` |
| Standard Studio leave `1280x720` | `1,044,248` | `43263AD6242D3DD93CE266A206B2BB72B0EA0B07EC52FEEAD3C21FF0152E9E53` |
| Compact empty-Studio enter `888x500` | `466,021` | `C324DF4D44A2FAF3DEAA06FF71343C4C41205BF964A0228B74E96DEC402A954D` |
| Compact Studio leave `888x500` | `497,174` | `1275EA74DD45F774100DF8DD6242563EAF566B2587539F6DD1DB28FF4774DE42` |

The entry frames are fixed close views of the existing Studio frontage with a bright graybox horizon and partial player body. The leave frames are fixed centered views of the existing empty private Studio. These are disclosed frame contents, not presentation-quality or usability claims.

Largest active OddsWell-process sampling at roughly `500ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| Standard, all | `18` | `1239.3 / 1511.8` | `2815.0 / 3721.2` |
| Standard, warm after first five | `13` | `1427.6 / 1490.2` | `3442.8 / 3721.2` |
| Compact, all | `17` | `1256.9 / 1504.2` | `2688.6 / 3317.7` |
| Compact, warm after first five | `12` | `1393.6 / 1439.3` | `3106.9 / 3303.8` |

These are short descriptive Development-package samples across one level transition, not minimum-PC evidence.

## Rejected diagnostics

- The first package attempt ended after cooking when the local Unreal Zen service stopped before staging could read its oplog. It is not accepted evidence; the final corrected source passed a fresh BuildCookRun to the separate `PackageFinal` archive.
- The first Studio-leave image came from the pre-correction package and lacked the prompt because the private Studio still used Unreal's empty default HUD. It is rejected and not included in the visual table.
- The first focused HUD-class assertion used an unsupported `TestEqual` type combination and failed compilation locally. It was changed only to pointer equality with `TestTrue`; the accepted final editor/game builds and automation suites compile and pass.

## Protected boundaries

- Sundale map: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- Studio home save cpp: `2943D697E1E630BA8D76F71A9F0E0B2976F15013C633BF61511F5E8939371B3C`
- Studio home save header: `3E7B067C82D4B0C65EBC961ED2C55DB59C91FD6AAA22A0BC809715EAD23017B9`
- housing catalog cpp: `8629D23577E891555FB711F9E472CBF9E4D6A4F1171E055F950E0692D4FA90AF`
- housing catalog header: `BAF8775550414305F900AF2A4CA2F0F68A0B2935AC64A22FF926E0BCB4CD72EA`
- Odds Bucks ledger cpp: `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7`
- Odds Bucks ledger header: `A98DEC2027A403B7AC2A66F612A84A611E20710353E3A7E8399467B98B897FE9`

## Truth boundary and phase stop

The four images are automated fixed views with no same-view pre-phase baseline. They document panel presence, complete exact text, and bounded geometry only in those frames. Owned-chair and One-bedroom prompts have automated runtime-marker evidence but no accepted dedicated prompt screenshots. Contract and shared-city automation verify authority boundaries; there was no manual networked Studio prompt test. The evidence does not prove text/color readability, comprehension, physical keyboard/controller behavior, accessibility, subjective usability, every state/resolution/localization, final UI/apartment/art/materials/lighting, minimum-PC performance, beta readiness, or production readiness.

No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. This is new-nightly-batch phase `5/6`; after Coordinator and Notion closure, stop for one Scope Director gate before phase `6/6`.
