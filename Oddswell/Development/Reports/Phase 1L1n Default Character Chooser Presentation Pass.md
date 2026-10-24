---
tags:
  - development
  - beta
  - phase-1l
  - character
  - presentation
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1n - Default Character Chooser Presentation Pass

**Status:** COMPLETE - BOUNDED NATIVE CHOOSER PRESENTATION PASS
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`
**Authority:** [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, accessibility, performance|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#1. Choose a default character|First-hour journey: choose a default character]], [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]], and [[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]].

## Outcome

The existing eight-card native chooser now gives every placeholder the same simple portrait stage: one dark backdrop and one thin warm rail. This is the smallest presentation-only correction that makes the block silhouettes feel intentionally framed without changing what any preset means or does.

The treatment is exactly two native Canvas rectangles per card, `16` across the unchanged four-by-two grid. It adds no asset, dependency, widget framework, new option, new character identity, final body, face, hair, name, pronoun, accessibility option, later editor, or final art.

## Frozen character and flow contract

- Exact catalog order: `masculine_tone_1` through `masculine_tone_4`, then `feminine_tone_1` through `feminine_tone_4`.
- Exact eight gameplay-identical presets and the same four skin tones across both approved presentations.
- Exact `starter_offwhite_top` and `starter_offwhite_bottom` on every card.
- Deterministic selection index `0`, wrapping keyboard/controller navigation, explicit confirmation, one confirmation per session, and no automatic confirmation.
- Exact local appearance-save schema and machine-local handoff target `127.0.0.1:17777`.
- Exact selected appearance and starter outfit continue into the existing Sundale shared-city path.
- Presentation and skin tone remain cosmetic only. No ability, wealth, intelligence, behavior, athlete, economy, wager, inventory, brain, simulator, authority, session, or network rule changed.

`CharacterPresetCatalog.cpp` and `CharacterAppearanceSave.cpp/.h` are byte-identical to the baseline. The implementation touches only the existing native chooser draw path and one focused automation contract.

## Verification

| Check | Result |
| --- | --- |
| UE 5.8 editor Development build | PASS; `4` actions, `5.25s` total |
| Focused `OddsWell.Character.DefaultChooserPresentation` | PASS `1/1` |
| Full native OddsWell automation | PASS `64/64`; zero failure markers |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| UE 5.8 game Development build | PASS; `3` actions, `12.78s` total |
| BuildCookRun `Bootstrap+SundaleGraybox` | PASS; `27.06s` |
| Package audit | `50` files / `1,050,177,964` bytes / `0` Python files |
| Automated fresh no-input chooser hold | PASS |
| Automated non-default save / handoff / shared appearance | PASS |

Package hashes:

- wrapper: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`
- game executable: `743ACC6645400D4BCAE29E9B97F360C2F936292C57E8D77454A1212CF51CB090`
- UFS manifest: `576F02A744AE691DEA66EA7AF290554103654BDED7C11AB643AA5A14F1B2B56F`

## Fresh no-input chooser hold

An isolated fresh profile launched the normal packaged default at `1280x720` with zero navigation or confirmation input. The existing `CharacterSelectAutoExit=8` test timer and native `shot` console command supplied bounded capture and exit only.

- Bootstrap loaded `OddsWellCharacterSelectionGameMode`.
- Runtime reported exact `cards=8`, `parts=16`, `roles=2`, `selected_index=0`, shared treatment, unchanged catalog, gameplay-identical presets, and unchanged starter outfit.
- The chooser remained active from its presentation marker to normal exit for `9.183s`.
- `ODDSWELL_APPEARANCE_SAVE` count: `0`.
- `ODDSWELL_CHARACTER_HANDOFF` count: `0`.
- Appearance SaveGame files: `0`.
- Accepted failure/fatal/assert/ensure/unhandled/travel-failure markers: `0`.

Accepted log: `C:\tmp\OddsWellPhase1L1n\Evidence\PackagedChooserNoInput.log`, `84,802` bytes, SHA-256 `6AFE03D035018CEA39D91199D2EB874DFBFE74197EE35FEDD1ED1134FB2F0278`.

## Fresh non-default confirmation and handoff

A second isolated run used the existing automated chooser controls to navigate one step and confirm once. A packaged Sundale listen peer was already bound to exact loopback gameplay UDP `127.0.0.1:17777`.

- The chooser marker reported `selected_index=1` before confirmation.
- Exactly one save marker recorded `masculine_tone_2`, `starter_offwhite_top`, `starter_offwhite_bottom`, production slot, and `confirmed_once=true`.
- The `2,183`-byte isolated appearance SaveGame has SHA-256 `1EBEFEE97CD3DEB7EA19833353747A7121AC361B5476450345EB53A42FD1AF98`.
- The owner started the existing client-travel handoff, loaded `127.0.0.1:17777/Game/Maps/SundaleGraybox`, and joined as the second visible player.
- The owner then loaded and replicated exact `masculine_tone_2` plus both starter items. The shared-city agreement reported that exact local appearance while the peer retained its independent safe default.
- The owner and automated peer both exited normally; gameplay UDP `17777` and OddsWell process counts returned to zero.
- Accepted failure/fatal/assert/ensure/unhandled/travel-failure markers: `0` in both logs.

Accepted logs:

- owner: `C:\tmp\OddsWellPhase1L1n\Evidence\PackagedChooserHandoffOwnerFinal.log`, `99,382` bytes, SHA-256 `956AFEFF3D6AC04C7D63F42B11C2222C5341A1D3672EAE3FE44F0E3C012EA919`
- peer: `C:\tmp\OddsWellPhase1L1n\Evidence\PackagedChooserHandoffPeerFinal.log`, `104,609` bytes, SHA-256 `0A0DD5DAADE5D00A562EA3923F19A4E6ECF20C29FF56D2892795EA8678375787`

An earlier diagnostic owner/peer pair is rejected because the harness stopped the still-running peer immediately after the owner completed. The accepted `Final` pair above repeated the same proof and allowed both processes to exit normally.

## Visual and performance evidence

The accepted `1280x720` PNG shows all eight existing cards, the two shared portrait-stage shapes on every card, the existing first-card focus, the unchanged skin tones, and the worn off-white top/bottom silhouettes.

- PNG: `C:\tmp\OddsWellPhase1L1n\NoInputUser\Saved\Screenshots\Windows\ScreenShot00000.png`
- bytes / SHA-256: `57,269` / `171545CC16AC3EE2FBFE13218042C5AB51455EE5F5CC5A824F7943C894844407`
- mean RGB / luma: `0.2813, 0.3323, 0.3909` / `0.3256`
- dark / bright / clipped share: `0.000%` / `2.348%` / `0.418%`
- mean saturation: `0.3156`

Actual child-process sampling at roughly `250ms` intervals:

| Process | Samples | Working set avg / peak MiB | Private avg / peak MiB |
| --- | ---: | ---: | ---: |
| No-input chooser, all | `18` | `1159.5 / 1343.9` | `2011.0 / 2479.6` |
| No-input chooser, warm after first five | `13` | `1283.2 / 1343.9` | `2294.6 / 2475.3` |
| Final handoff owner, all | `9` | `1109.6 / 1388.1` | `2384.9 / 3446.4` |
| Final handoff owner, warm after first five | `4` | `1255.8 / 1388.1` | `2833.6 / 3446.4` |

These are descriptive Development-package samples, not a minimum-PC benchmark.

## Truth boundary

The screenshot is one fixed view and has no same-view pre-phase baseline. It documents presence and complete-card framing; it does not prove text or color readability, comprehension, controller hardware behavior, accessibility, subjective usability, every resolution or localization, later appearance editing, final proportions/body/face/hair/outfit/UI art, minimum-PC performance, beta readiness, or production readiness.

No manual player input or owner testing was used. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. This is new-batch phase `5/6`; stop for the Scope Director after Coordinator and Notion closure.
