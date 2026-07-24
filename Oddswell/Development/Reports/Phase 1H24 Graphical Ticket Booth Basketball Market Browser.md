---
tags:
  - development
  - beta
  - basketball
  - wagering
  - unreal
  - interface
  - phase-1h
status: complete
date: 2026-07-23
---

# Phase 1H.24 Graphical Ticket-Booth Basketball Market Browser

## Outcome

The Sundale stadium ticket booth now opens an original full-screen native Unreal basketball interface instead of the temporary debug-text panel.

The browser has four concise market tabs:

1. **Game Lines** — active and populated by the exact validated Match Winner offer.
2. **Margin** — visible and locked.
3. **Overtime** — visible and locked.
4. **Player Props** — Points, Rebounds, and Personal Fouls are visible and locked.

Every unavailable card says `LOCKED - ODDS NOT PUBLISHED`. No placeholder price, probability, return, or settlement capability was fabricated.

## Researched interaction direction

[[Design/Basketball Betting Interface Research]] records the official source review. The implementation adopts the useful structural patterns—short market navigation, comparable selection cards, a persistent slip, explicit pre-commit information, and accessible navigation—without copying operator branding or art.

The right-side slip is deliberately read-only. It shows:

- no wager selected;
- `10`–`100` Odds Bucks stake range;
- decimal return as stake multiplied by displayed odds;
- game-start lock;
- Odds Bucks only and no real money.

## Controls and accessibility

- Mouse: click any market tab or Close.
- Keyboard: Left/Right changes markets; `E` or Escape closes.
- Controller: shoulder buttons change markets; face-right closes.
- Opening the menu suspends movement and camera input; closing restores both.
- Active and locked state is written in text as well as represented by color.
- The normal proximity prompt remains exactly `Press E to open betting odds`.

## Ponytail boundary

This phase uses one native `AHUD` class in the existing locomotion module. It adds no UMG/Slate dependency, plugin, widget framework, backend, data model, or market abstraction.

It reuses the existing booth radius, validated offer loader, Match Winner selections, `E` interaction, and QA path. It does not change the Basketball Brain, Basketball Odds Brain calculation, Rules and Outcome Engine, Wager and Settlement Engine, ledger, SaveGame schema, canonical game, replay, or public league evidence.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Unreal editor build | Passed |
| Focused stadium/ticket-booth automation | `1/1` passed |
| Full native OddsWell automation | `17/17` passed |
| Frozen simulation and odds contracts | `68/68` passed in `133.316s` across the five frozen test groups |
| Brain Admin self-check | Passed unchanged |
| Python compilation | Passed |
| Windows Development BuildCookRun | Passed in `82.82s`; 50 files / `1,045,592,846` bytes |
| Packaged ticket-booth QA | Passed; exact offer visible only at booth, read-only, ledger entries/balance unchanged at `0/0` |
| Packaged 1280x800 visual inspection | Passed; no overlap or clipping on the Game Lines page |
| Obsidian canvas JSON | Parsed successfully |
| Cost | `$0.00` |

## Truth boundary and next gate

This is a usable graphical browser for the current read-only offer, not canonical player wager submission and not evidence that later markets exist.

The next Scope Director review should choose the smallest remaining Match Winner evidence requirement. New-chain read-only history, correction, canonical future-game integration, and broader player history remain separate. Margin, Overtime, Points, Rebounds, and Personal Fouls each require owner-approved rules plus their own offer, lock, event, result, settlement, replay, reconciliation, and rejection evidence before any odds may be published.
