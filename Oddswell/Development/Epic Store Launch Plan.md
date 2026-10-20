---
tags: [development, roadmap, launch]
status: proposed-awaiting-owner-decisions
date: 2026-10-20
---

# OddsWell Epic Games Store launch plan

**Goal (owner, 2026-10-20):** sell OddsWell on the Epic Games Store for **$9.99** on Windows PC.

This plan turns that goal into decisions and milestones. It does not override [[Design/Beta Game Bible]] by itself. Where it recommends changing a locked item, that change needs your explicit approval, which would then be recorded as a decision.

## 1. Where the game actually is

I read the Beta and Version 1 Bibles, the completion roadmap and the handoff, then checked the Unreal source and game data directly.

**Real and reusable**

- A packaged Windows build with a character chooser, third-person movement and a graybox Sundale city.
- Two-player shared-city presence, on one machine only.
- The Studio apartment, with the first upgrade and chair placement.
- A job that pays 100 Odds Bucks.
- A careful append-only Odds Bucks ledger with idempotent purchases and wager settlement.
- Two shop items: the Signal Jacket and the Modular Chair.
- Twelve athlete story pages and a 3-minute symbolic game replay with skip.
- About 37,000 lines of C++, plus a small, well-tested Python basketball simulator of about 3,000 lines.

**Narrower than it sounds**

- **Wagering works for exactly one game.** The client has a single hard-wired fixture, Harbor City Waves vs Mesa Vista Sol, and a fixed stake path. There is no general "pick any upcoming game and bet" system yet.
- **The league does not run inside the game.** The simulator is Python outside Unreal. The game ships one season archive of 20 completed games and one replay file.
- **Time is real-world time.** The job pays once per real 24 hours and the scheduled game tips off 30 real minutes after creation. For a paid single-player game, that would feel like a mobile energy timer.
- **Content runs to about 20–40 minutes.** That's one job, two shop items, one apartment upgrade and two teams.
- **Art and characters aren't in the game.** The Unreal player is still a primitive placeholder. The scanned human and new outfits exist only in Blender.
- **One scanned man can't cover the cast.** The Bible requires eight presets: masculine and feminine across four skin tones.
- **No one has played the whole loop end to end.**

**A process problem worth naming.** Since September, most effort went into evidence rituals rather than the game: graphics-policy harnesses, process-custody reruns, six-phase batches with Notion upserts, and dozens of character sub-phases (1L.5a through 1L.5ct). The rigor kept results honest, but at that pace the game never ships.

## 2. Decisions you need to make

My recommendation is listed first in each.

**D1 — Launch shape.** *Recommended: single-player at launch; the shared online city comes later as a free update.*

- A one-time $9.99 sale can't safely fund servers, accounts, cheat protection, moderation and support indefinitely.
- Epic also requires multiplayer games sold on other PC stores to support crossplay between them.
- The Bible currently LOCKS "multiplayer city", so choosing this changes a locked item.
- Alternatives: online at launch (largest cost and risk), or a single-player city plus an online league. The second still needs a server.

**D2 — League engine.** *Recommended: port the simulator into the game as C++, seeded per save, so each player has their own living league.*

- It's small enough to port, and the existing Python tests become the reference to check the port against.
- Alternative: bake pre-simulated seasons as data. That's faster, but the same results ship to everyone and can be read from the files.

**D3 — Time.** *Recommended: an in-game calendar with days, shifts and a game schedule, advanced by playing or sleeping in the apartment.*

- This replaces the real-time 24-hour job cooldown and the real-time tipoff.

**D4 — League size and season.** *Recommended: 8 fictional teams, a shorter season of about 28 games plus playoffs, and repeatable seasons.*

- With only two teams, every game is the same matchup.
- 82 games stays possible later as a "full season" option.

**D5 — Characters.** *Recommended: evaluate MetaHuman, Epic's free realistic-human system built into Unreal, for the eight presets with faces, hair, body types and skin tones.*

- The scanned Eric becomes the quality bar and look reference.
- Alternative: buy and fit a separate Renderpeople rigged scan per preset. Each needs its own outfit fitting.
- Keeping only Eric fails the eight-preset requirement.

**D6 — Wager markets at launch.** *Recommended: Match Winner, Winning Margin, Overtime and Player Points.*

- Rebounds and fouls come after launch.

**D7 — Content for $9.99.** *Recommended target: 3–6 hours to "complete".*

- About 4 jobs, about 20 clothing items, about 15 furniture items and all 6 apartment tiers.
- A season goal: for example, own the Penthouse, or finish a season with a target bankroll.
- 15–25 achievements.

**D8 — Rating and wording.** *Recommended: aim for ESRB Teen / PEGI 12–16 with a "simulated gambling" descriptor.*

- Odds Bucks are never buyable with real money and never cash out. Your design already says this.
- The store page should present it as a sports-life sim, not as gambling.

**D9 — Process.** *Recommended:* each milestone ends in a **packaged build you can play**, with a short report, ordinary automated tests and scoped commits. Retire the six-phase batches, Notion upserts, custody rituals and the Candidate B policy harness.

**D10 — Name check.** Run a trademark search on "OddsWell" and the final city name before buying store art or paying the $100 fee.

## 3. Milestones

Each milestone ends with a build you play.

**M1 — Living league (foundation).**

- In-game calendar.
- C++ simulator port checked against the Python tests.
- 8 teams with fictional rosters.
- Season schedule.
- A general wager flow for *any* upcoming game, reusing the existing ledger and settlement rules.
- Watch or skip any game's replay.
- One save file that holds everything.
- QA-only fixed-scenario code removed from the player path.

*Done when:* you can play several in-game days, bet on different games, and see wins and losses settle correctly after restarting.

**M2 — Complete loop with real characters.**

- The chosen character system (D5) in the game with walk, run and jump, plus the starter outfit and Signal Jacket swap.
- Main menu, pause, settings, save and load.
- A first-time-player tutorial path through Studio, job, stadium and shop.

*Done when:* someone who has never seen the game finishes the first-hour loop without help.

**M3 — Content.**

- Jobs, clothing and furniture catalogs, apartment tier interiors, the extra wager markets and the season goal.
- Achievements through Epic Online Services, which is free.
- Balancing the economy against the new calendar.

**M4 — Sundale and presentation.**

- One finished, distinctive city block and the arena.
- Better game presentation: athletes, crowd and score bug.
- UI art, sound effects and your music.

**M5 — Polish.**

- Accessibility: remapping, subtitles and contrast.
- Performance measured on a real minimum-spec PC, with a Low/Medium/High settings menu.
- Crash reporting and bug fixing.

**M6 — Store readiness.**

- Epic developer account and the $100 fee.
- Free IARC age rating.
- Store page: capsule art, 5+ screenshots and a trailer.
- EULA and privacy policy.
- An asset licence ledger for every shipped file.
- Encrypted pak files to satisfy Renderpeople §4.3(b).
- Final price and regional pricing.

**M7 — Closed playtest.** 5–10 outside players on Epic keys, a fix pass, then a release candidate.

**M8 — Launch.** Then the free online shared-city update, if D1 goes that way.

I won't invent dates: throughput depends on your decisions and how quickly you review builds. After M1 we'll have a measured pace to estimate the rest from.

## 4. Not in the launch

- Shared online city, accounts, chat and friends.
- Trading and marketplace.
- Real-money purchases.
- More cities and other sports.
- Live or in-game odds.
- The 20-minute presentation mode.
- Brain retraining.
- The Admin Console as a player feature.

All of these stay in [[Design/Version 1 Game Bible]] as later options.

## 5. Kept, reworked or retired

**Kept:**

- The ledger and settlement rules: append-only, idempotent, and wagers can't affect outcomes.
- The equal-information rule for odds.
- The athlete reading guide.
- The replay invariance rule: skipping never changes a result.
- The Studio and housing tiers.
- The Sundale direction and palette.

**Reworked:**

- The single canonical game becomes a schedule.
- Real-time cooldowns become in-game days.
- The primitive player becomes the chosen character system.

**Retired:**

- The Candidate B rendering-policy smoke harness and its evidence chain.
- Machine-local two-client QA lanes, if D1 is single-player.
- Batch and Notion closure rituals.

## 6. Main risks

- **Scope:** the content target (D7) is the biggest effort, so cut items rather than slip.
- **Perception:** simulated gambling in a game that may attract teenagers. Mitigate with the rating, wording and no real money.
- **Characters:** MetaHuman cost on mid-range PCs. Check it in M2 on the minimum-spec machine.
- **Licences:** each shipped asset needs a recorded licence. Renderpeople allows games (§4.1(b), §4.2(c)) but forbids easily extractable files (§4.3(b)).
- **Epic terms change:** recheck the current Epic Developer Portal terms before M6. Epic's store page currently states a $100 recoupable fee per game, 100% revenue on the first $1M net per product per year then 88/12, and a required IARC rating.

**Sources:**

- [Epic store publishing information](https://store.epicgames.com/about)
- [Epic self-publishing requirements](https://store.epicgames.com/news/epic-games-store-launches-self-publishing-tools-for-game-developers-and-publishers)
- [Renderpeople terms](https://renderpeople.com/general-terms-and-conditions/)
