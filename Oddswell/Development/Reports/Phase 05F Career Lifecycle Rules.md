---
tags:
  - development
  - athletes
  - careers
  - simulation
status: complete
---

# Phase 0.5F Career Lifecycle Rules

Phase 0.5F makes career age, gradual development, gradual decline, and retirement part of the authoritative three-season career archive. The same season-specific ratings that appear in the Admin Console now drive game decisions and are bound into replay evidence. Cost: **$0.00**.

## Rules implemented

- Every fictional athlete has an explicit Season 1 age between 20 and 33.
- At age 24 or younger, the athlete's two highest baseline ratings gain at most one point per season, capped at three points above the debut rating.
- Beginning at age 31, stamina loses at most one point per season. Beginning at age 33, the weakest non-signature rating can also lose one point per season.
- Ratings have a floor of 40 and a ceiling of 99. No rating can move more than one point between adjacent seasons.
- Specialty classifications are checked after every season and remain preserved across the archive.
- An athlete completes the age-35 season and then retires. Trying to create a later-season roster with that athlete is rejected until a replacement system exists.

## Authoritative integration

The existing league transition accepts an optional season roster. The career archive supplies the lifecycle-adjusted roster for each season; the standard league and locked prediction study retain their original default roster behavior. Season 1 remains identical to the existing League Viewer archive.

Cross-season replay reconstruction uses the same lifecycle roster as the original game. Replay manifests already bind the complete player ratings, so any rating mismatch breaks verification.

## Measured examples

- Micah Vale ages from 22 to 24 and moves from 76 to 77 overall. Passing rises from 86 to 88 and stamina from 88 to 90 while his Floor General specialty remains intact.
- Kellan Shore ages from 31 to 33, moves from 77 to 76 overall, and keeps 84 rebounding and the Rebounding Anchor specialty.
- Roman Voss completes his age-35 final season at 76 overall with 86 rebounding unchanged. His career closes as `RETIRED` after 51 games, 819 points, and 734 rebounds.
- The archive now contains **11 active** and **1 retired** career.

## Truth boundary

These are transparent fictional design rules, not a trained model and not a claim about real human aging. There is no hidden potential rating, random development, coaching effect, contract logic, draft, free agency, replacement player, personal-life choice, or Athlete Life Brain consequence yet.

Lifecycle rosters are currently rebuilt from versioned deterministic code for the read-only archive; they are not serialized inside `LeagueState`. Mutable season administration must persist exact roster snapshots before it is enabled.

Retirement is real at the archive boundary: Roman cannot be placed into Season 4. A roster-continuity system must fill that opening before the league advances.

## Validation

- The new lifecycle test verifies unchanged Season 1 ratings, bounded values and deltas, deterministic ages, retirement timing, and rejection after retirement.
- Admin Console self-check verifies 11 active/1 retired records, one-point adjacent-season bounds, specialty preservation, exact cumulative scoring, hidden-state exclusion, and cross-season replay reconstruction.
- All 30 simulator, policy, league, persistence, availability, prediction, and lifecycle tests pass.
- Browser QA displayed Micah's 76-to-77 growth, Roman's retired age-35 record, and a lifecycle-adjusted Season 3 Game 20 replay ending 111-108 with `ARCHIVE VERIFIED` and no console errors.

## Next gate

Phase 0.5G should add Roster Continuity: one deterministic replacement path for retirement, stable incoming athlete IDs and ratings, a five-player availability floor, and preservation of retired career history. The first Athlete Life Brain choices can follow once the league can safely advance beyond a retirement.
