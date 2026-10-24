---
tags: [development, milestone, launch]
status: milestone-1-delivered
date: 2026-10-20
---

# Milestone 1: Living league

This delivers M1 of [[Development/Epic Store Launch Plan]] under [[Design/Decisions/DEC-037 Epic Store Launch Shape League Runtime Calendar and Size|DEC-037]]. The packaged Windows build now plays as a single-player career: a living eight-team league, in-game days, and betting on any game.

## What you can do in the build

1. Choose a character. You arrive in Sundale with a welcome note and 0 Odds Bucks.
2. **Job marker (E):** one paid shift per in-game day, +100.
3. **Ticket booth (E):** today's four games, each with fixed public Match Winner odds and no house edge.
   - Up/Down picks a game, Left/Right picks a team, and `-` / `=` set the stake (10–100).
   - Enter places the bet. You can place one bet per game.
4. **Arena (E):** tonight's games.
   - Enter, then Enter again to confirm, tips off. That closes betting for the day and plays the chosen game from its event log, with a scoreboard and play-by-play.
   - S skips to the final, Esc picks another game, and E leaves.
   - Your bet settles when you finish watching that game.
5. **Studio (Z):** sleep until tomorrow. Unplayed games resolve, remaining bets settle, and a morning report shows results, your bets and your balance.
6. **L:** standings, playoff series and today's games.

**Season structure:** each team plays 28 games, then best-of-three semifinals and a final. The next season then starts with offseason recovery.

## How it was built

- **League core:** `Source/OddsWell/League/OddsWellLeagueCore` is a dependency-free C++ port of the Python simulator, Athlete Life Brain v4, consistency, involvement, fatigue/injury, Elo prediction and the odds formula. It includes CPython's random number generator.
- **Career subsystem:** `Source/OddsWell/Career/` holds a GameInstance subsystem that owns the league, the one Odds Bucks ledger (reused unchanged), wagers and the `OddsWellCareer` save slot. It also holds the arena replay actor and the HUD screens.
- **Legacy lanes:** the older fixed-scenario QA lanes keep their behaviour behind their `-...Qa` flags. Normal play no longer creates the single canonical game.

## Evidence

| Check | Result |
|---|---|
| Python ↔ C++ parity (`client/tools/league_parity`) | PASS: 34 standalone games and a 20-game season, matching every event record, life choice, fatigue, injury, odds and standings value |
| Editor automation (`OddsWell` suite) | 76/76 pass, including the new full-season test |
| Packaged play-through (`-CareerSmoke -CharacterSelectAutoConfirm`) | PASS (see below) |
| Packaged season soak (`-CareerSeasonSoak`) | PASS: 33 nights, each saved; Sundale Signal champions; season 2 starts |
| Relaunch | Day 2, balance 129 and the wager restored from the save |

The play-through ran these steps:

1. A shift paid +100, and a second shift that day was refused.
2. A 40 bet was placed and a duplicate bet was refused.
3. At tipoff, a late bet was refused and the balance stayed 60 until the game was watched.
4. The replay played and the bet won: +69, for a balance of 129.
5. Sleeping moved the career to day 2.

Screenshots: `01_Welcome`, `02_Board`, `05_GameLive`, `08_MorningReport`.

## Bugs found and fixed on the way

- Confirming a character tried to join a development multiplayer server, which stranded single-player launches at the chooser.
- The packaged build did not contain the Sundale map unless it was named on the command line. It is now set in packaging settings.
- A champion was reset before the season-rollover report could name it.
- Bets settled at tipoff, so your balance spoiled games before you watched them.

## Known gaps

These are for M2 and later.

- **Prompts:** several existing prompts (arena enter/exit, Studio housing list) are engine debug messages. They overlap the status panel and **will not show in a Shipping build**; they move into the HUD in M2.
- **Placeholder art:** the player is still the primitive placeholder; the character system (plan D5) comes in M2. Arena players are labelled pillars.
- **Content:** only Match Winner bets; one job; Signal Jacket, Modular Chair and the One-bedroom are the only purchases.
- **Settings:** there is no main menu, pause, settings or "new career" screen yet. A career starts automatically, and `-NewCareer` / `-CareerSlot=` exist for testing.
- **Athlete pages:** the twelve athlete story pages still read the archived Season 1 file, not the live league.
- **Test runs:** the play-through drives the same functions the controls call, but it was not keyboard-played by a person. Owner hands-on play is the next check.
