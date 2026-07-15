---
tags:
  - development
  - plan
status: active
---

# Current Plan

## Phase 0: Simulation foundation

1. Define two teams and a minimal athlete attribute model.
2. Build a deterministic possession-based rules and outcome engine.
3. Define one strict structured-action contract for the Basketball AI Brain.
4. Validate the loop with a simple baseline policy, then pilot one LLM policy through the same contract.
5. Record the AI model/version, decision inputs and outputs, simulation seed, and auditable match event log.
6. Run automated games and seasons.
7. Validate team strength, athlete statistics, upsets, fatigue, injuries, AI decision quality, cost, and latency.
8. Test whether public information supports meaningful predictions.

### Phase 0A implementation status

- **Status:** Complete and merged into `main` at commit `df65467`.
- **Implemented:** two fictional teams, ten athletes, strict offense/defense action validation, baseline decision policy, seeded authoritative resolution, fatigue, passing, turnovers, shooting, rebounding, overtime, JSONL audit logs, and decision-tape replay.
- **Validated:** identical seed replay, recorded-tape replay, illegal-action rejection, and a 100-game plausibility smoke test.

### Phase 0B implementation status

- **Active branch:** `agent/phase-0b`
- **Implemented:** deterministic batch analysis, team and player box-score aggregation, nine calibration guardrails, and reproducible Markdown reporting.
- **Baseline:** 1,000 games using seeds `0`–`999` with alternating home assignment; 92.12 average team points, 206.62 total possessions, 38.3% field-goal percentage, 26.9% three-point attempt share, 9.19 turnovers per team, 50.0% home wins, and 2.8% overtime.
- **Calibration fix:** weighted rebound assignment replaced the maximum-rating shortcut, reducing the worst player rebound concentration from roughly 68 to 16.79 per game.
- **Result:** 9/9 baseline checks pass. See [[Development/Reports/Phase 0B Baseline]].
- **Next:** connect one LLM policy through the existing action contract and compare it with this exact baseline.

### Phase 0C implementation status

- **Active branch:** `agent/phase-0c`
- **Implemented:** a provider-neutral LLM completion boundary, exact sports-only context, enumerated legal actions, strict JSON/action validation, deterministic baseline fallback, categorized failure telemetry, request hashing, model/policy provenance, and replay that never calls the provider.
- **Realism correction:** initial ballhandlers are weighted by passing and shooting; defenders are distributed by defense rating instead of assigning one defender to every ballhandler.
- **Offline pilot:** 10 games, 8,140 structured decisions, zero invalid outputs, zero fallbacks, exact action-tape replay, and $0.00 paid API cost using a deterministic local fixture.
- **Recorded LLM sample:** six Codex-authored basketball situations produced 6/6 legal actions, verified against 6/6 exact request hashes with zero fallbacks. This closes the no-cost LLM evidence gap while remaining smaller than a live provider test.
- **One-hour fairness audit:** 100 paired seeds were each run with home assignments swapped. All 200 games replayed exactly; 5/5 checks passed, with a 53.0% aggregate home win rate, a 6.0-point maximum team home-away gap, zero invalid provider outputs, and zero fallbacks.
- **Two-hour integrity audit:** all 10 pilot games now produce verified canonical SHA-256 replay manifests binding the engine, seed, matchup, full roster, policy, action tape, and event log. A mutation test confirms that changing a recorded score invalidates the manifest.
- **Important limit:** the fixture proves the integration and safety path, not LLM intelligence. See [[Development/Reports/Phase 0C Offline LLM Policy Pilot]].
- **Next gate:** choose a provider/model and approve a small cost/latency budget, then test one team's offense for 5-10 games with paired seeds and swapped home assignments.
- **Next documented phase:** Phase 0D, beginning with deterministic schedules and standings. Prediction validation remains later in that phase; no wagering or credit work is authorized here.

### Phase 0D implementation status

- **Active branch:** `agent/phase-0d`
- **Implemented:** balanced alternating home/away schedules, deterministic game seeds, season history, standings, stable ranking tie-breakers, and a verified replay-integrity hash for every result.
- **First league run:** 20 games using seeds `10000`-`10019`; Harbor City Waves finished 12-8 and Mesa Vista Sol finished 8-12. All 20 replay manifests verified. See [[Development/Reports/Phase 0D Schedule and Standings]].
- **Season-length limit:** 20 games is an engineering sample, not the final product season length.
- **Retraining budget:** the first retraining experiment has a hard $5 total ceiling under [[Design/Decisions/DEC-004 AI Retraining Budget]]. No paid job starts until a provider/model is selected and the cap can be enforced.
- **Next Phase 0D gate:** Phase 0D.1 multi-season persistence and between-game fatigue.

### Phase 0D.1 implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** versioned JSON league state, full season history, seeds, standings, replay hashes, player fatigue snapshots, deterministic save/load/resume, one-day recovery between games, and seven-day recovery between seasons.
- **Authoritative integration:** pregame fatigue now enters the existing game simulator, affects outcomes through the existing fatigue calculations, and is bound into replay evidence.
- **Measured run:** three 20-game seasons using seeds `11000`-`11059`; 60/60 replay manifests verified. Season-one average pregame fatigue progressed from `0.000` in game 1 to `0.238` in game 10 and `0.310` in game 20. Offseason recovery reduced the next season start to `0.070`.
- **Persistence gate:** uninterrupted simulation and save/load/resume produce identical state and results.
- **Known limit:** the ten-player prototype has no bench or substitutions, so every player currently receives full-game workload.
- **Result:** 18/18 Phase 0A-0D tests pass. See [[Development/Reports/Phase 0D1 Multi-Season Fatigue]].
- **Next Phase 0D gate:** add minutes and a minimal rotation model before injuries or prediction scoring.

### Phase 0D.2 implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** six-player fictional rosters, deterministic five-player lineups, one reserve sharing five regulation shifts, lineup-change events, exact player minutes, minutes-driven in-game and carryover fatigue, and versioned persistence under `oddswell-league-state-v2`.
- **Replay and persistence:** action-tape replay reproduces lineups, minutes, fatigue, and outcomes exactly; minutes are stored in season history and bound into the hashed event log. Save/load/resume remains identical to uninterrupted simulation.
- **Fixed-seed comparison:** seed `12000` produced exactly `240.0` team-minutes per team. Starters averaged `43.16` minutes and reserves `24.20`; reserve carryover load was `0.0343`/`0.0338` versus starter averages `0.0601`/`0.0596`.
- **Measured season:** 20 games using seeds `12000`-`12019`; Harbor City Waves finished 11-9, all 20 replay hashes verified, and final average fatigue was `0.2962`.
- **Result:** all 18 prior tests plus 2 focused rotation/workload tests pass (20/20). See [[Development/Reports/Phase 0D2 Rotation Minutes and Workload]].
- **Known limit:** the six-player rotation is deliberately small and fixed; tactical substitutions, foul trouble, injuries, and coach-controlled rotations remain separate gates.
- **Next Phase 0D gate:** deterministic availability, minor injuries, and recovery using D.2 minutes as workload evidence.

### Phase 0D.3 implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** exact roster availability snapshots, 2/3/5/7-day minor injury recovery, actual-minutes and pregame-fatigue risk, a 4% per-player risk ceiling, a separate deterministic injury RNG, five-player availability floor, zero minutes for inactive athletes, and offseason recovery.
- **Replay and persistence:** state schema `oddswell-league-state-v3` persists pregame/postgame availability and recovery days. Replay evidence binds the injury model, authoritative minutes, and both availability snapshots. Save/load/resume remains identical to uninterrupted simulation.
- **Fixed-seed run:** three 20-game seasons using seeds `13100`-`13159` produced 10 injuries across 700 active player-games (1.43%), 20 missed player-games, 20/20 zero-minute absences, and 60/60 verified replay hashes.
- **Guardrails:** all teams retained at least five available athletes; high-workload incidence was 1.50% versus 1.00% at lower workload. Probabilities are provisional engineering calibration values, not medical claims.
- **Result:** 25 focused and regression tests pass. See [[Development/Reports/Phase 0D3 Availability and Recovery]].
- **Known limit:** injuries occur after games and create binary availability only. In-game injuries, diagnoses, limited status, permanent injuries, treatment choices, and off-court injuries remain later work.
- **Next Phase 0D gate:** expose public schedules, standings, fatigue, and availability for prediction-quality validation before any credit or wagering implementation.

### Phase 0D.4 implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** versioned public-only pregame snapshots, deterministic projected minutes, fixed 50%/public Elo/Elo-plus-availability models, chronological warm-up, a locked holdout, five-bin calibration error, and SHA-256 prediction commitments created before each authoritative game transition.
- **Leakage boundary:** commitments exclude seeds, RNG state, hidden fatigue and injury-risk internals, results, replay/action tapes, future games, economy data, and user data. Verified outcomes and replay hashes are linked only after games finish.
- **Locked evaluation:** 15 warm-up seasons followed by a fixed 5-season/100-game holdout using seeds `14000`-`14399`. All 100 holdout commitments verify.
- **Measured result:** fixed 50% Brier `0.2500`; public-history Elo `0.2417`; Elo plus public availability/rotation `0.2416`. The adjusted model achieved `+3.3%` Brier skill despite lower threshold accuracy, so calibration—not raw winner count—drives this gate.
- **Absence subset:** 34 holdout games had at least one published absence. Public Elo Brier was `0.2363`; adding the provisional availability adjustment changed it to `0.2367`, so no extra benefit is claimed on that subset.
- **Result:** 29 focused and regression tests pass; Admin Console self-check passes. Cost was `$0.00`. See [[Development/Reports/Phase 0D4 Public Prediction Evaluation]].
- **Known limit:** this measures fictional simulator data, not real-world predictive power. No model was trained, tuned on the holdout, or connected to wagering.
- **Next gate:** completed as Phase 0.5B; the read-only League Viewer now exposes teams, athletes, schedule, standings, availability, and committed prediction history before any credits or settlement work.

## Phase 0.5: Functional sports loop

1. Display teams, athletes, schedules, standings, and public information.
2. Place and lock match-winner predictions.
3. Simulate and settle matches server-side.
4. Replay event logs through a simple interface.
5. Record credit transactions and prediction history.

### Phase 0.5A Game Theater implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** a local Admin Console Game Theater that runs the real seeded simulator and animates a replay-safe 96-frame sample of recorded passes, shots, rebounds, turnovers, lineup changes, clock, score, and final replay seal.
- **Visual language:** all twelve roster athletes appear as team-colored markers; active ballhandlers, pass targets, ball travel, benches, court markings, play callouts, progress, replay speed, and replay-last-game controls are visible.
- **Truth boundary:** scores, clock, lineups, and play labels come from the authoritative event log. Court coordinates are explicitly illustrative because Phase 0 does not simulate physical player positions or 3D movement.
- **Validation:** Admin Console self-check, simulator/league/prediction regression tests, localhost API check, and a browser-driven seed `42` replay passed. The browser displayed a sealed Harbor City Waves `111`–`114` Mesa Vista Sol result with no console errors.
- **Next gate:** Phase 0.5B read-only League Viewer for teams, athlete ratings, schedules, standings, availability, prediction commitments, and per-game inspection.

### Phase 0.5B League Viewer implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** a cached public-only 20-game season payload and an Admin Console League Viewer with standings, both teams, all twelve athlete ratings, final availability, the complete schedule, scores, winners, per-game availability and minutes, three pregame prediction probabilities, prediction commitments, and authoritative replay hashes.
- **Leakage boundary:** seeds, hidden fatigue, recovery timers, injury-risk internals, RNG state, future information, economy data, and user data are excluded. Schedule, team, result, prediction, credit, and settlement mutations remain unavailable.
- **Validation:** Admin Console self-check and all 29 regression tests pass. Browser QA selected Game 20, displayed the correct 86-77 Harbor City result, and reported no console errors. See [[Development/Reports/Phase 05B League Viewer]].
- **Cost:** `$0.00`; no new dependency, database, or model job was added.
- **Next gate:** Phase 0.5C should connect archived league games to their exact recorded Game Theater playback while keeping hidden league state server-side.

### Phase 0.5C Archived Game Playback implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** every completed schedule entry opens its exact deterministic Game Theater playback. The server reconstructs the original matchup from authoritative pregame league state, verifies the score and minutes, and sends every recorded play frame plus the linked replay hash to the browser.
- **Leakage boundary:** reconstruction seeds, fatigue, recovery timers, injury-risk internals, and RNG state remain server-side. The browser receives public teams, verified results, recorded play frames, and archive evidence only.
- **Shared path:** live simulations and archived games use one replay-payload builder. No new dependency or persistence schema was required.
- **Validation:** Admin Console self-check and all 29 regression tests pass. Browser QA played all 433 Game 20 play frames, finished Mesa Vista Sol 77-86 Harbor City Waves with `ARCHIVE VERIFIED`, and reported no console errors. See [[Development/Reports/Phase 05C Archived Game Playback]].
- **Cost:** `$0.00`.
- **Next gate:** Phase 0.5D Athlete Career Profiles for durable ratings, specialties, career state, availability, recent performance, and history.

### Phase 0.5D Athlete Career Profiles implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** a new read-only Athletes module with twelve stable profiles, durable ratings, baseline roles, transparent specialties, prototype tiers/rating bands, current availability, verified season statistics, five-game form graphics, complete 20-game histories, and direct archived-replay actions.
- **Evidence source:** every statistic is aggregated from the authoritative 20-game season and its reconstructed verified event records. The payload is cached and adds no dependency or database.
- **Identity rule:** temporary rising/steady/cooling form never changes the displayed durable ratings. Athlete Life Brain, aging, contracts, development, and personal-life consequences remain explicitly inactive.
- **Measured examples:** Nico Reyes led scoring at `21.63` PPG; Roman Voss led rebounding at `14.55` RPG; Cal Brooks finished `OUT` after playing 15 games and missing 5.
- **Validation:** Admin Console self-check and all 29 regression tests pass. Browser QA verified profile switching, an unavailable athlete, form/history rendering, and athlete-to-Game-Theater navigation with no console errors. See [[Development/Reports/Phase 05D Athlete Career Profiles]].
- **Cost:** `$0.00`.
- **Next gate:** Phase 0.5E Athlete Career Persistence for multi-season cumulative totals, experience/career stage, and active/retired history.

## Phase 1: 3D vertical slice

Build the one-city scope defined in [[Design/Decisions/DEC-002 First Playable Scope]].

## Future shared simulation layer

After the basketball loop is stable, pilot the shared Athlete Life Brain with a few daily choices: train, rest, recover, and socialize. Expand into relationships, nightlife, media, discipline, career decisions, and other sports only after the smaller loop produces believable, auditable consequences.

Athletes keep distinct career identities: stars, specialists, average players, and below-average players are allowed and should not be automatically equalized. Durable ability changes gradually, while temporary form, fatigue, availability, practice, discipline, partying, fictional legal trouble, and other life consequences can alter performance and career outcomes through visible causal chains. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

The shared life, world, memory, and learning layers will support every sport. Each new sport receives its own AI decision brain and authoritative rules engine. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

## Next unresolved decisions

- Engine selection.
- First city identity.
- First two team identities.
- Minimal athlete attributes.
- Initial live LLM provider/model and separate inference budget.
- First retraining dataset and method that fit the $5 ceiling.
- Minimal Athlete Life Brain traits and daily choices.
- AI evaluation criteria and model-update cadence.
- Ranked competition scoring.
- Match schedule and season length.
