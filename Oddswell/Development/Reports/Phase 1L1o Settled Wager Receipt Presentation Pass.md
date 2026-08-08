---
tags:
  - development
  - beta
  - phase-1l
  - wagering
  - presentation
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1o - Settled Wager Receipt Presentation Pass

**Status:** COMPLETE - BOUNDED NATIVE SETTLED-RECEIPT PRESENTATION PASS
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#5. Place and watch the first wager|First-hour wager]], [[Design/Beta Game Bible#6. Experience the consequence|First-hour consequence]], and [[Design/Beta Game Bible#Match presentation|Basketball presentation]].

## Outcome

The existing settled-wager receipt now has a small native Canvas hierarchy around its unchanged nine canonical lines: a header band and rail, a settlement-value band and rail, and a close footer. Those are exactly five new Canvas rectangles inside the existing receipt draw path. No widget framework, texture, animation, external asset, or dependency was added.

The existing standard `720x520` receipt panel remains unchanged at `1280x720`. At the already-supported compact Ticket Booth threshold, the receipt uses a bounded `720x468` panel with tighter vertical spacing, placing it exactly `16` pixels from the top and bottom of the measured `888x500` client area. This is a fixed compact correction, not a general responsive-system claim.

## Frozen receipt and wagering contract

- Exact canonical win: `Mesa Vista Sol` selected; Harbor `79-113` Mesa; winner Mesa; stake `40`; returned `94`; net `+54`; balance `154`; ledger count `3`.
- Exact nine text lines and the single `E or ESC: CLOSE` instruction are unchanged.
- The retained settled-loss path still exposes Harbor selected, Harbor `79-113` Mesa, returned `0`, net `-40`, balance `60`, and ledger count `2`.
- Close, leave the `350 cm` booth radius, reopen, later cold-process reopen, and read-only source behavior are unchanged.
- Existing result precedence remains fail-closed after tipoff. Each accepted packaged run emitted the expected blocked-offer diagnostic because a new canonical offer cannot be created after tipoff; the settled receipt then loaded from the authoritative receipt source and passed.
- Settlement, offers, odds, markets, stakes, returns, requests, schedule, replay, brains, simulator, authority, equal-information rules, SaveGame schema, immutable ledger/history, compact bet-slip behavior, and every previous Phase 1L layer remain unchanged.

The authored Sundale map and canonical schedule/offer/ledger sources remain byte-identical to their baselines. This phase changes only `PlaceholderLocomotion.cpp`, QA-only evidence, documentation, and the affected roadmap canvas.

## Verification

| Check | Result |
| --- | --- |
| UE 5.8 editor Development build | PASS; `4` actions, `11.03s` total |
| Focused `OddsWell.Character.SettledWagerReceiptPresentation` | PASS `1/1` |
| Full native OddsWell automation | PASS `65/65`; zero failed tests |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions, `17.81s` total |
| BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `27.28s` |
| Package audit | `50` files / `1,050,208,172` bytes / `0` Python files |
| Canonical Mesa win, standard + compact + cold | PASS |
| Retained canonical Harbor loss | PASS |

The first Python harness invocation completed all `105` assertions successfully but did not expose reliable child exit codes to PowerShell. It is rejected as evidence. The accepted unchanged rerun used the same pinned interpreter and tests at inherited High priority and returned explicit zero exits for all five modules; no test or threshold changed.

Package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `C5B2143C2DE0CF90F6B6CDAE5A04C7D79E8B5330AD468C83E1229BD50C4BE90B`
- UFS manifest: `EF52CE91FA60617CC5A9F12D8E4815D858BD910187DE98632D9FBFDD2F25FB04`

## Packaged receipt evidence

Four separate current-package Development processes exited `0` without fatal, assertion, ensure, unhandled-exception, or OddsWell QA failure markers:

1. The accepted `1280x720` win process reported `compact=false`, panel `720x520`, five native presentation pieces, nine canonical lines, and a fully bounded panel. The existing receipt QA then proved the exact Mesa win, one close instruction, close/leave/reopen, source-byte and source-mtime stability, three ledger entries, balance `154`, and `mutation=false`.
2. The accepted `888x500` win process reported `compact=true`, panel `720x468`, and the same exact receipt and invariance results.
3. A later cold process reused the first win profile unchanged and independently reproduced the exact receipt plus close/leave/reopen and source invariance.
4. A retained-loss process independently reproduced the exact Harbor loss, final `79-113`, returned `0`, net `-40`, balance `60`, two ledger entries, close/leave/reopen, and source invariance through the same presentation path.

The authoritative win SaveGame remained `10,658` bytes with SHA-256 `78C3E43DDC4C0E63E671187DC2B81A35E633EF6DE2BDDD5A6BF25871BBBFDC29`. The retained-loss source remained `10,082` bytes with SHA-256 `4CB4A0F70D45FEEF46DA1DFB88F6086B05B85FBB82FCB90148C3E08DC66F9366`.

Accepted logs:

- standard win: `C:\tmp\OddsWellPhase1L1o\Evidence\PackagedWin1280.log`, `95,690` bytes, SHA-256 `CDB9381C1066D1A15F298EA728511242EDE58FA1B2129EE581B06F1EFD365F11`
- compact win: `C:\tmp\OddsWellPhase1L1o\Evidence\PackagedWinCompact.log`, `96,372` bytes, SHA-256 `D1416B2AFFE3E38CEC7F5A011B2328239731B1A3E2A17D1E0357BBC42AF838CB`
- cold win: `C:\tmp\OddsWellPhase1L1o\Evidence\PackagedWinCold.log`, `95,638` bytes, SHA-256 `1544F862E824F42A0C07097B1061750B89E42719B5352C8998FF601059997B07`
- retained loss: `C:\tmp\OddsWellPhase1L1o\Evidence\PackagedRetainedLoss.log`, `96,207` bytes, SHA-256 `071779BBDBCCF45697B57BEFABD7CF8F89F330148D2AA8C4E0BA95E22B1124BE`

## Visual and performance evidence

The accepted standard image is `1280x720`, `719,763` bytes, SHA-256 `D0018CE68E880A61FE5C8C2EFCAC89B19273C97A8BBFDECD87D5136EE9F35FCF`. It shows the full bounded receipt, the five hierarchy shapes, all nine unchanged lines, and the exact Mesa win values. Its descriptive pixel measurements are mean RGB `0.2308, 0.2436, 0.2355`, luma `0.2398`, dark share `1.197%`, bright share `0.461%`, clipped share `0.003%`, and mean saturation `0.4158`.

The accepted compact image is `888x500`, `209,522` bytes, SHA-256 `BD9243C1FADF7317A533550E56AD1BBE7CF99D2B4E686F84B568BEFAD6D5A215`. It shows the same full receipt inside the measured client area, with the settlement band and close footer separated and no observed panel or line clipping in this one frame. Its descriptive measurements are mean RGB `0.2154, 0.2777, 0.2982`, luma `0.2653`, dark share `0.566%`, bright share `0.956%`, clipped share `0.006%`, and mean saturation `0.4298`.

Actual child-process sampling at roughly `250ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| Standard receipt, all | `24` | `1187.7 / 1730.3` | `2439.3 / 3757.0` |
| Standard receipt, warm after first five | `19` | `1429.0 / 1730.3` | `3035.4 / 3757.0` |
| Compact receipt, all | `23` | `1176.4 / 1650.4` | `2338.7 / 3478.1` |
| Compact receipt, warm after first five | `18` | `1416.7 / 1650.4` | `2908.1 / 3478.1` |

These are descriptive Development-package samples, not a minimum-PC benchmark.

## Protected boundaries

- Sundale map: `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`
- canonical Match Winner offer cpp: `5E8D97C6A5D43AE76FD3F7D632608A5F1CD488D27782614BF35EE956D4724F6C`
- canonical schedule cpp: `226CCF92A7F46251698B49BC6E4577632F63BB2DE85D178CA0416621F7818E86`
- Odds Bucks ledger cpp: `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7`
- Odds Bucks ledger header: `A98DEC2027A403B7AC2A66F612A84A611E20710353E3A7E8399467B98B897FE9`

## Truth boundary and batch stop

The two images are fixed automated views with no same-view pre-phase baseline. They document presence, hierarchy, exact canonical values, and bounded geometry in those two captures only. They do not prove text or color readability, comprehension, physical keyboard/controller behavior, accessibility, subjective usability, every result/state/resolution/localization, final UI/materials/lighting, minimum-PC performance, beta readiness, or production readiness.

No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. This is new-batch phase `6/6`. After Coordinator and Notion closure, perform the read-only six-phase audit and stop; do not begin a seventh implementation without fresh owner authorization.
