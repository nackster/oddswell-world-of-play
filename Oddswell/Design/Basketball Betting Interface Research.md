---
tags:
  - design
  - basketball
  - wagering
  - interface
  - research
status: accepted
date: 2026-07-23
---

# Basketball Betting Interface Research

## Purpose

This research informs OddsWell's fictional, virtual-currency stadium ticket-booth interface. It studies interaction patterns and disclosure requirements; it does not copy another operator's branding, artwork, wording, or trade dress.

## Useful patterns

- A short horizontal market row makes a broad basketball catalog understandable without placing every selection on one screen.
- Consistent selection cards make teams, lines, and decimal odds easy to compare.
- A persistent bet-slip area should keep the selection, stake, accepted odds, and potential return together before commitment.
- A bet receipt needs a durable identifier and the accepted selection/odds after commitment.
- Keyboard access, visible focus, strong text contrast, and labels in addition to color are required presentation constraints.

These patterns are supported by:

- [DraftKings betting glossary](https://sportsbook.draftkings.com/help/glossary/betting-terminology): defines the bet slip, receipt, and decimal-odds return convention.
- [DraftKings general rules](https://sportsbook.draftkings.com/help/general-betting-rules): emphasizes reviewing bet details and makes clear that accepted odds can differ if a market moves before acceptance.
- [UK Gambling Commission RTS 2](https://www.gamblingcommission.gov.uk/manual/remote-gambling-and-software-technical-standards/rts-2-displaying-transactions): requires stake, selections, bet type, accepted odds, and odds format to be clear before commitment.
- [NBA statistics glossary](https://www.nba.com/stats/help/glossary): supplies authoritative basketball meanings for points, rebounds, and personal fouls.
- [Microsoft accessibility checklist](https://learn.microsoft.com/en-us/windows/apps/design/accessibility/accessibility-checklist): requires keyboard navigation, visible focus, readable contrast, and information that does not depend on color alone.

## OddsWell translation

The ticket booth uses four concise categories:

1. **Game Lines** — active now for the already validated Match Winner offer.
2. **Margin** — visible but locked until exact scoring-band rules, probabilities, settlement, replay, and audit evidence pass.
3. **Overtime** — visible but locked until its Yes/No offer and regulation/overtime settlement evidence pass.
4. **Player Props** — visible subtypes for Points, Rebounds, and Personal Fouls, all locked until each statistic and threshold is authoritative from offer through settlement.

The right-side slip is read-only in this phase. It shows the Odds Bucks stake range, decimal-return convention, game-start lock, and no-real-money boundary. OddsWell does not publish placeholder numbers for unproven markets.

## Visual direction

- Original dark-navy, civic-ticket-booth presentation with teal and warm-gold accents.
- Market cards use identical geometry for rapid comparison.
- Active and locked states are written in text as well as color.
- Technical offer IDs, commitments, Unix timestamps, hidden probabilities, and QA wording stay out of the normal player view.
- The modal view pauses movement and camera input, supports keyboard/controller page navigation, provides clickable tabs, and restores normal control when closed.

## Truth boundary

This document is interface research, not authorization to activate every listed market. [[Design/Beta Game Bible]] remains authoritative: Match Winner is first, and every later basketball market requires its own approved rules and full evidence chain.
