---
tags:
  - development
  - phase-06l
  - athlete-performance
  - offensive-involvement
  - controlled-rollout
status: complete
date: 2026-07-17
---

# Phase 0.6L: Controlled Offensive Involvement Rollout

## Decision

Promote `offensive-involvement-v1` for new baseline-policy games. Every frozen Phase 0.6K integration, history, labeling, and rollback condition passes. The truthful scope remains **OPPORTUNITY ONLY**.

The resolver only weights initial-ballhandler and pass-target selection. It does not change ratings, post-possession action weights, shot probability, minutes, Consistency v2, Athlete Life behavior, career development, or custom decision policies.

## Frozen production snapshot

The production table was frozen before rollout evidence and keeps the pilot weights unchanged:

- `featured = 1.15`: Jalen Cross, Micah Vale, Nico Reyes, Eli Mercer
- `standard = 1.00`: Dorian Pike, Malik Frost, Tariq Stone, Mateo Cruz
- `low = 0.85`: Kellan Shore, Andre North, Roman Voss, Cal Brooks
- Season 4 replacement: Soren Lake inherits Roman Voss's `low = 0.85` tier.

Every active matchup snapshot contains exactly 12 unique athletes. The static table covers all 13 durable career identities without placing retired Roman and incoming Soren in the same active roster.

## Authoritative integration

- One named default constant selects v1 or disabled for new games.
- League version `phase06l-v1` stores the exact version and full snapshot in `oddswell-league-state-v6`.
- V4 history loads with Consistency and Offensive Involvement disabled. V5 history keeps its stored Consistency evidence and loads Offensive Involvement as disabled.
- New replay manifests bind the exact involvement version and snapshot. Disabled manifests omit involvement fields, preserving prior replay identity.
- Current league, prediction study, Admin live Game Theater, Athlete Profiles, and archived Game Theater all use v1.
- Stored archive reconstruction uses the stored snapshot, not the current production table.
- Historical Phase 0D.4 predictions and frozen Athlete Life studies explicitly pass the disabled version.
- Custom decision policies remain rejected when involvement settings are supplied.

## Fresh evidence

- 80/80 games in the four-season Admin archive use `offensive-involvement-v1`.
- 80/80 games store complete 12-athlete snapshots.
- All 20 Season 4 games store Soren Lake and exclude retired Roman Voss.
- Current Season 1 league and prediction evidence agree on winner and replay hash for 20/20 games.
- Archived Season 1 Game 1 reconstructs 421 recorded frames with a verified replay seal.
- The existing shot-formula isolation and frozen `0.85`/`1.00`/`1.15` weights remain unchanged.

## Historical locks

All frozen Athlete Life digests remain exact:

- V1/V2 multi-seed: `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`
- V2/V3 routine: `eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618`
- V3/V4 performance: `a7b61128668fce26c392a52fac4425324ec41fdfead3b261e57535ff83fc4f60`

No historical study is reinterpreted as having Offensive Involvement.

## One-switch rollback

Change `DEFAULT_OFFENSIVE_INVOLVEMENT_VERSION` from `offensive-involvement-v1` to `offensive-involvement-disabled` and restart. Only new games change. Stored v1 games retain their exact version and snapshot and continue to replay through the explicit stored-history path. V5 and earlier history remains disabled.

## Validation

- 29/29 focused involvement, league persistence/replay, migration, rollback, prediction, and historical-isolation tests pass.
- All 65 simulator, league, prediction, career, life-policy, consistency, and involvement regressions pass.
- All three frozen historical digest locks pass unchanged.
- Admin Console self-check passes, including current league/prediction agreement and live/archive reconstruction.
- Python compilation, both affected canvas structure checks, and repository whitespace validation pass.
- External cost: **$0.00**. No dependency, paid API, retraining, deployment, credit, purchase, wagering, or monetization work was added.

## Truth boundary

This is deterministic opportunity weighting in a fictional simulator. It is not learning, intelligence, coaching, confidence, personality, neural-network training, a player-quality improvement, or evidence of correct real-world usage.

## Next gate

Phase 0.6M: a **read-only post-rollout integration review**. Recheck fresh v1 history, prediction agreement, archive reconstruction, v5 migration, historical locks, and rollback before selecting another athlete-performance input.
