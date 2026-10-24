---
tags: [development, milestone, launch]
status: milestone-3-delivered
date: 2026-10-24
---

# Milestone 3: Content

This delivers M3 of [[Development/Epic Store Launch Plan]] under [[Design/Decisions/DEC-039 Career Markets Economy and Content|DEC-039]]. D6 and D7 are adopted there as working assumptions, and you can change any of the numbers.

## What's new in the build

1. **Five bet markets on every game** at the ticket booth:
   - Match Winner
   - Winning Margin (home or away by 1-5, 6-10, 11+)
   - Overtime (yes or no)
   - Each team's star scorer over or under a points line

   Controls: Up/Down picks a game, **Tab** (or Y) changes market, Left/Right picks an outcome, and Enter places the bet. You can place one bet per market per game.
2. **Job ladder:**

   | Job | Pay per shift | Unlocks after |
   |---|---|---|
   | Corner store clerk | 100 | start |
   | Arena usher | 130 | 6 shifts |
   | Stats desk assistant | 170 | 14 shifts |
   | Team scout | 220 | 26 shifts |

   A promotion message appears when you move up.
3. **Shops:** the clothing store, furniture store and apartment listings each open a catalog with E.
   - **Clothing:** 20 items, a shirt colour and a shorts colour on your MetaHuman. They're worn as soon as you buy them, and Enter re-equips an item you own.
   - **Furniture:** 16 items. They appear in your home, and some need a bigger home first.
   - **Homes:** 5 upgrades, from the One-bedroom at 500 to the Penthouse at 2,800.
4. **Your home grows:** the Studio level builds the home you own. Bigger tiers add bedrooms behind a partition, the Penthouse gets a glass wall, and owned furniture sits at fixed spots.
5. **Season goal:** own the Penthouse. The status panel always shows the next home and its price.
6. **22 achievements:** a pop-up appears when you unlock one, and **K** lists them all.

## Economy check

`client/tools/economy` plays 12 full seasons of the real league core and flat-bets every outcome.

| | Before (M1 Elo price) | After (simulated price + 4% margin) |
|---|---|---|
| Match: always away team | 122.5% return | 100.7% |
| Match: always underdog | 123.2% | 104.0% |
| Star points: always under | 111–118% | 92–97% |
| All markets, average | — | about 96% |

The old prices had two free-money strategies. The new ones have none, so jobs drive progress and betting is the exciting extra.

## Evidence

| Check | Result |
|---|---|
| Python ↔ C++ parity (`client/tools/league_parity`) | PASS, unchanged. The market pricing never touches the real game. A new section checks every game's markets: published, margin book sums to 1, exactly one winning bucket, two-way markets settle one way, star-point props match the replay |
| Editor automation (`OddsWell` suite) | 77/77 pass. The new `OddsWell.Career.Catalog` test checks unique IDs, escalating prices, 4 jobs, 15–25 achievements, and that every tier fits its furniture without overlaps, walls, the partition or the spawn point |
| Packaged play-through (`-CareerSmoke`) | PASS: two markets on one game, a duplicate refused, a Match Winner win (+57) and a points-over loss, achievements unlocking, balance 117 on day 2 |
| Packaged progress soak (`-CareerSmoke -CareerProgressSoak`) | PASS: a casual player (a shift and two bets a day) owns the Penthouse on **day 61**, buying all 16 furniture items along the way. Homes came on days 8, 15, 25, 37 and 61. When only clothing was bought, the Penthouse came on day 51 |

Screenshots: `CareerSmoke_03_BetPlaced`, `CareerSmoke_09_ClothingStore`, `CareerSmoke_10_FinalHome`, `CareerSmoke_11_Achievements`.

Day 51–61 is about 4–6 hours at a few minutes per in-game day. That's inside the D7 target of 3–6 hours, but only owner play time can confirm it.

## Bugs found and fixed on the way

- **Blind betting edges:** the Elo price assumed a home advantage the simulator doesn't have. Pricing now uses simulations of the actual matchup.
- **Uncapped long shots:** they could pay 100× or more. Every outcome is now priced at 5% or higher, so a bet pays at most 20× its stake.
- **New keys repeating:** the Tab, Q, K and Y keys had no key-repeat guard and would have fired every frame.
- **HUD overlap:** the taller status panel overlapped the first-day guide and the centre panels.
- **Coffee table:** in the smallest homes it sat on the spawn point. The catalog test caught this.

## Known gaps

- **Placeholder art:** homes and furniture are graybox boxes, bedrooms share one wing, and clothing is flat colour. These are M4 presentation work.
- **Epic Online Services:** achievements are stored in the save, and mirroring them to EOS needs the product registered (M6).
- **Owner play time:** the hours-to-Penthouse estimate needs a real play session.
