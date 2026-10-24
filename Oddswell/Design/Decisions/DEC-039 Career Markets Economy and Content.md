---
tags:
  - decision
  - economy
  - wagering
  - launch
status: working-assumption
date: 2026-10-24
---

# DEC-039 Career Markets, Economy and Content

## Context and authority

The [[Development/Epic Store Launch Plan]] lists recommended defaults for D6 (wager markets) and D7 (content for $9.99). The owner asked to start M3 without choosing them separately, so Claude adopted the recommendations as **working assumptions**. Everything here is data in one place (`OddsWellCatalog.cpp`, `OddsWellLeagueCore.h`) and can be changed without new systems.

## Decision

**Markets (D6).** Every game offers five markets: Match Winner, Winning Margin (home or away by 1-5, 6-10, 11+), Overtime (yes or no), and each team's star scorer over or under a points line. Rebounds and fouls come after launch. A player may hold one bet per market per game.

**Pricing.**
- Every market is priced from 240 simulations of the matchup. They use the same pregame inputs as the real game but different seeds, never the real game's seed.
- Quotes add a **4% house margin**, and no outcome is priced below 5%. A single bet therefore pays at most 20 times its stake.
- The public Elo probability is kept on each game as a reference number.

**Why the change from the M1 Elo price.** A 12-season run of the real league core showed two edges a player could exploit blindly:
- The Elo model assumes a home-court advantage that the simulator does not have. Always backing away teams returned **+22%**.
- Pricing that left out fatigue made "under" on star points return **+11–18%**.

With simulated pricing, every market returns about 93–108% (sampling noise included), averaging about 96%. Betting is exciting but slightly losing on average, and jobs drive progression. This fits D8's "sports-life sim, not gambling" framing. Re-run with `client/tools/economy/run_economy.bat`.

**Jobs (D7: about 4).** One shift per in-game day. Shifts worked unlock the next job:

| Job | Pay per shift | Shifts needed |
| --- | --- | --- |
| Corner store clerk | 100 | 0 |
| Arena usher | 130 | 6 |
| Stats desk assistant | 170 | 14 |
| Team scout | 220 | 26 |

**Homes (all 6 tiers).** Each home needs the one before it:

| Home | Price |
| --- | --- |
| Studio | free |
| One-bedroom | 500 (unchanged) |
| Two-bedroom | 900 |
| Three-bedroom | 1,400 |
| Four-bedroom | 2,000 |
| Penthouse | 2,800 |

**Season goal:** own the Penthouse. The status panel always shows the next home and its price.

**Catalogs.**
- 20 clothing items, each a colour of the MetaHuman garment's top or shorts. The Signal Jacket is one of them.
- 16 furniture items, some needing a bigger home.
- Furniture appears in the home at fixed spots that an automated test checks for overlaps at every tier.

**Achievements:** 22, stored in the career save. Mirroring them to Epic Online Services is M6 work, because it needs the product's EOS registration.

**Pacing target:** a casual player owns the Penthouse in about 50–60 in-game days, roughly 4–6 hours. `-CareerSmoke -CareerProgressSoak` measures this in the packaged game.

## Boundaries

- Odds Bucks are never bought with or cashed out for real money (D8).
- Graybox homes and flat-colour clothing are placeholders. Interiors, separate bedroom walls and textured clothing are M4 presentation work.
- Saves from before M3 load: old bets read as Match Winner, and old purchases of the jacket, chair and One-bedroom count as owned.
