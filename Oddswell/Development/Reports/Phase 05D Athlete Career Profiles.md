---
tags:
  - development
  - admin
  - athletes
  - careers
status: complete
---

# Phase 0.5D Athlete Career Profiles

Phase 0.5D adds a read-only Athlete Career Profiles module to the local Admin Console. It separates durable basketball identity from temporary season evidence and future Athlete Life Brain consequences. Cost: **$0.00**.

## Implemented

- Twelve selectable fictional athlete profiles with stable IDs, team, baseline role, prototype tier, and current availability.
- Durable shooting, passing, defense, rebounding, stamina, and overall ratings.
- Transparent specialties derived from rating combinations: scoring creator, floor general, defensive specialist, interior stopper, rebounding anchor, and rotation utility.
- Above/near/below prototype-roster rating context without forcing athletes toward equal ability.
- Verified season PPG, rebounds, minutes, field-goal percentage, passes, games played, and missed games.
- Five-game scoring-form graphics labeled rising, steady, or cooling without changing durable ratings.
- Complete 20-game athlete histories with opponent, result, score, points, rebounds, minutes, availability, and direct archived Game Theater replay links.
- One cached standard-library read model derived from the existing authoritative season and replay records.

## Measured prototype examples

- Nico Reyes led the prototype at **21.63 points per game**.
- Roman Voss led at **14.55 rebounds per game**.
- Jalen Cross is a **Scoring creator** with 84 shooting, 78 passing, and a currently cooling five-game scoring window; his durable ratings do not change with that temporary label.
- Cal Brooks remains an **Interior stopper** while currently `OUT`, with 15 games played and 5 missed.

## Truth boundary

The current profiles do not claim that aging, contracts, development, potential, personal-life choices, legal stories, or Athlete Life Brain decisions are active. The page displays verified sports evidence only. Hidden fatigue, recovery timers, injury-risk internals, RNG state, and seeds remain excluded.

The 12-player prototype was previously calibrated in a narrow rating range and currently has no athlete at the 80+ `Star` tier. Star, average, specialist, and below-average careers are supported by the profile categories, but widening the roster distribution must be a measured simulator change because it will alter existing balance and replay evidence.

## Validation

- Admin Console self-check verified 12 profiles, 20 history entries per player, multiple specialties, exact league point totals, and the no-leakage boundary.
- All 29 simulator, policy, league, persistence, availability, and prediction regression tests passed.
- Browser QA displayed Jalen Cross's full profile and form visualization, selected Cal Brooks as `OUT` with 15 games played and 5 missed, opened Cal's Game 20 archived replay, and reported no console errors.

## Next gate

Phase 0.5E should add Athlete Career Persistence: stable athlete records across multiple seasons, cumulative career totals, experience/career stage, and an explicit active/retired history boundary. Rating development and Athlete Life Brain consequences should remain separate measured gates.
