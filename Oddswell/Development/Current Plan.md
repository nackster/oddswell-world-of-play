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

### Phase 0.5E Athlete Career Persistence implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** twelve stable athlete IDs across three deterministic 20-game seasons, cumulative career totals, experience and career-stage labels, selectable season splits, current availability, and exact archived replay links for every season.
- **Record boundary:** all twelve athletes are explicitly `ACTIVE`; zero are `RETIRED`. The retired-history field is stable, but no retirement rule is claimed.
- **Measured archive:** 60 games and 720 scheduled player-games. Jalen Cross recorded 57 games, 1,188 points, 582 rebounds, 2,481.2 minutes, and 20.84 career PPG.
- **Validation:** cumulative player scoring reconciles exactly with league scoring; Admin Console self-check and all 29 regression tests pass. Browser QA switched season splits and completed a Season 3 archived replay with no console errors. See [[Development/Reports/Phase 05E Athlete Career Persistence]].
- **Cost:** `$0.00`; the existing league state and standard-library cache were reused without a database or new dependency.
- **Next gate:** Phase 0.5F Career Lifecycle Rules for bounded development and decline, specialty preservation, and real retirement criteria before Athlete Life Brain consequences.

### Phase 0.5F Career Lifecycle Rules implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** explicit fictional debut ages, age bands, at-most-one-point adjacent-season changes, growth in young signature ratings, veteran decline, rating floors/ceilings, specialty-preservation checks, an age-35 final season, and rejection of post-retirement roster generation.
- **Authoritative integration:** lifecycle-adjusted ratings drive Seasons 2-3 and are bound into replay evidence. The standard league and locked prediction-study behavior remain unchanged; Season 1 stays compatible with the League Viewer.
- **Measured examples:** Micah Vale grows from 76 to 77 overall while passing/stamina rise from 86/88 to 88/90. Roman Voss retires after Season 3 at age 35, remains a Rebounding Anchor with 86 rebounding, and closes with 51 games, 819 points, and 734 rebounds.
- **Archive boundary:** 11 active careers and 1 retired career. Roman cannot enter Season 4 until the league has a replacement-player path.
- **Validation:** all 30 regression tests and the Admin Console self-check pass. Browser QA confirmed rating progression, retirement, and a lifecycle-adjusted 111-108 archived replay with no console errors. See [[Development/Reports/Phase 05F Career Lifecycle Rules]].
- **Cost:** `$0.00`; no model, database, or dependency was added.
- **Next gate:** Phase 0.5G Roster Continuity, followed by the first small Athlete Life Brain choice loop.

### Phase 0.5G Roster Continuity implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Implemented:** stable incoming athlete Soren Lake, a deterministic Roman-to-Soren roster transition, newcomer fatigue/availability initialization, removal of the retired athlete from active snapshots, six-player roster preservation, and exact Season 4 replay reconstruction.
- **Historical boundary:** Roman retains all three career seasons and remains visible as `RETIRED`; Soren begins a separate stable career in Season 4.
- **Measured archive:** 4 seasons, 80 games, 13 profiles, 12 active athletes, and 1 retired athlete. Soren played 20 games with 358 points, 276 rebounds, 17.90 PPG, and 13.80 RPG as Mesa Vista finished 13-7.
- **Validation:** all 30 regression tests and the Admin Console self-check pass. Browser QA verifies the incoming and retired profiles plus an exact Season 4 replay. See [[Development/Reports/Phase 05G Roster Continuity]].
- **Cost:** `$0.00`; no model, database, or dependency was added.
- **Next gate:** an agent audit will confirm Phase 0.5H Athlete Life Brain v1 before implementation.

### Phase 0.5H Athlete Life Brain v1 implementation status

- **Status:** Complete on `agent/phase-0d` after the basketball-realism agent gate.
- **Implemented:** every active athlete makes one deterministic between-game choice from `train`, `rest`, `recover`, or `socialize`. Unavailable athletes recover, high-fatigue athletes rest, and the remaining roster alternates training and social choices by stable schedule context.
- **Temporary effects:** train and socialize add at most `+1.5%` next-game readiness with bounded workload; rest reduces carryover fatigue; recover shortens recovery by one day. Readiness is consumed by the next game. Durable ratings, specialties, age, development, and retired history never change through this system.
- **Audit and replay:** each internal decision records the exact legal choices, selected action, policy version, reason, before/after temporary state, and next-game effect. Decisions are bound into the replay manifest and survive league save/load/resume. Public athlete profiles show only choice, reason, and effect; hidden readiness, fatigue, recovery timers, seeds, and RNG state remain server-side.
- **Measured archive:** 912 choices across four 20-game seasons: 386 rest, 252 socialize, 251 train, and 23 recover. Roman has 57 choices only in Seasons 1-3; Soren has 19 choices only in Season 4.
- **Cost:** `$0.00`; the standard library and existing deterministic simulator were reused.
- **Next gate:** Phase 0.5I should evaluate the choice distribution and measured game impact before adding traits, long-term memory, narratives, or an LLM.

### Phase 0.5I Athlete Life Brain Evaluation implementation status

- **Status:** Complete on `agent/phase-0d` after a basketball-realism audit.
- **Implemented:** a read-only, fixed-archive evaluator covering choice distribution, per-season and per-athlete tenure, exact v1 policy compliance, readiness exposure, fatigue/recovery effects, archived replay reconstruction, and a zero-readiness fixed-seed sensitivity comparison.
- **Measured archive:** 912/912 expected choices across four seasons: 386 rest (42.32%), 252 socialize (27.63%), 251 train (27.52%), and 23 recover (2.52%). All 80 games reconstruct; policy and roster-tenure violations are both zero.
- **Measured influence:** readiness appeared in 503 choices (55.15%), averaged 0.6891% overall and 1.2495% when active, and never exceeded 1.5%. Against identical zero-readiness replays, it changed results by +1.4125 points per team-game, +0.6654 field-goal percentage points, -0.275 turnovers per team-game, 22/80 winners, and 6.275 mean absolute margin points.
- **Truth boundary:** these are path-sensitive effects in fictional fixed-seed games, not real-world estimates or evidence of learning. Training/socializing parity comes from deterministic alternation; rest dominance comes from the explicit fatigue threshold.
- **Cost:** `$0.00`; no gameplay, policy, schema, Admin Console, LLM, training, retraining, economy, credits, or wagering behavior changed. See [[Development/Reports/Phase 05I Athlete Life Brain Evaluation]].
- **Next gate:** Phase 0.5J should review the v1 policy and define the smallest explicit fictional trait input before any long-term memory, narrative event, or LLM control.

### Phase 0.5J Life Preference Policy Review implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded agent audits.
- **Decision:** define exactly one future input, `off_day_preference = practice | social`, from a version-owned fictional mapping of stable athlete identities. Every active team has three athletes in each group in every current season.
- **Proposed v2 precedence:** unavailable athletes recover; fatigue at or above `0.24` forces rest; otherwise practice-preferring athletes train and social-preferring athletes socialize. Existing temporary consequences and bounds remain unchanged.
- **Frozen-state review:** the 912 stored v1 before-states split evenly across preference groups. A one-step counterfactual changes 240 stored choices, but it does not resimulate sequential fatigue, injuries, RNG, or results and is not a realism claim.
- **History contract:** v1 remains immutable. Future v2 decisions start in a new archive, reuse the existing stored policy version and reason fields, and must be validated by their own version without rewriting Phase 0.5I evidence.
- **Cost:** `$0.00`; runtime code, tests, schemas, archives, Admin Console behavior, LLMs, training, economy, credits, and wagering remain unchanged. See [[Development/Reports/Phase 05J Life Preference Policy Review]].
- **Next gate:** Phase 0.5K may implement and evaluate the preference pilot beside immutable v1.

### Phase 0.5K Versioned Life Preference Pilot implementation status

- **Status:** Complete on `agent/phase-0d` after a bounded versioning audit.
- **Implemented:** explicit opt-in `athlete-life-v2` preference decisions beside default v1, keyword-only policy propagation, exact preference reasons, decision/replay version agreement, policy-version-aware evaluation, and unchanged save/load/resume under the existing state schema.
- **Fresh archive:** 912 v2 decisions across four seasons and 80 games: 379 rest, 271 socialize, 239 train, and 23 recover. All 80 games reconstruct; policy and tenure violations are zero.
- **Preference evidence:** 456 practice-group choices contain no socialize action; 456 social-group choices contain no train action. Recovery and high-fatigue rest retain priority.
- **Same-seed sensitivity:** v1 and v2 differ on 381/912 sequential choices, 15/80 winners, and 5.725 mean absolute margin points. Both samples record 20 new injuries and 14 missed player-games; this single fixed archive is not a promotion decision.
- **Compatibility:** every omitted policy argument remains v1, Phase 0.5I evidence stays exact, the Admin Console stays v1, and durable athlete identity is unchanged.
- **Cost:** `$0.00`; no new dependency, schema, UI, LLM, learning, retraining, memory, narrative, economy, credits, or wagering was added. See [[Development/Reports/Phase 05K Versioned Life Preference Pilot]].
- **Next gate:** Phase 0.5L read-only multi-seed evaluation before any v2 promotion or added trait.

### Phase 0.5L Multi-Seed Life Preference Evaluation implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded evaluation audits.
- **Implemented:** one read-only standard-library evaluator over ten untouched paired seed blocks, with 800 games and 9,120 decisions per policy, per-block evidence, a canonical SHA-256 digest, and no simulator mutation.
- **Integrity:** decision counts reconcile; policy, tenure, and version violations are zero; readiness stays at or below 1.5%; fatigue stays bounded; every team retains five available athletes; every absence records zero minutes.
- **Preference evidence:** v2 practice and social groups contain 4,560 decisions each with exact elective adherence. V1-adjusted workload, fatigue, injury, missed-game, and readiness differences all remain inside the provisional engineering alarms.
- **Outcome sensitivity:** v1/v2 actions differ 3,707/9,120 times, winners differ 147/800 times, and margin MAE is 6.4212. Scoring changes by -0.0069 point per team-game and Harbor City's win rate changes by -2.875 percentage points.
- **Decision:** v2 is `ELIGIBLE FOR LATER REVIEW`, not promoted. Results describe fictional deterministic stability, not intelligence, policy quality, or real-world realism.
- **Cost:** `$0.00`; no schema, gameplay, default policy, UI, historical archive, LLM, learning, retraining, memory, narrative, economy, credits, or wagering changed. See [[Development/Reports/Phase 05L Multi-Seed Life Preference Evaluation]].
- **Next gate:** Phase 0.5M deliberate v2 promotion review.

### Phase 0.5M Athlete Life Brain v2 Promotion Review implementation status

- **Status:** Complete on `agent/phase-0d`.
- **Decision:** v2 is approved for a controlled promotion, but this review does not change the default. Phase 0.5L's ten untouched seed blocks passed every frozen integrity and provisional stability gate.
- **History boundary:** the current default also feeds frozen Phase 0.5I, Phase 0.5L, Phase 0D.4, league, test, and Admin Console paths. The rollout must first pin historical evidence explicitly to v1 so a default change cannot reinterpret it.
- **Rollout contract:** use immutable v1/v2 constants, move only new league and Admin Console state to v2, keep old decisions and replay manifests unchanged, display the active version truthfully, and retain a one-constant rollback.
- **Cost and scope:** `$0.00`; no runtime, schema, archive, interface, LLM, learning, retraining, narrative, economy, credits, or wagering behavior changed. See [[Development/Reports/Phase 05M V2 Promotion Review]].
- **Next gate:** Phase 0.5N controlled v2 default rollout with explicit historical v1 pins and full replay/regression validation.

## Phase 1: 3D vertical slice

Build the one-city scope defined in [[Design/Decisions/DEC-002 First Playable Scope]].

## Future shared simulation layer

Athlete Life Brain v1 now pilots train, rest, recover, and socialize as deterministic between-game choices with bounded, auditable temporary consequences. Expand into traits, relationships, nightlife, media, discipline, career decisions, and other sports only after the smaller loop passes measured realism evaluation.

Athletes keep distinct career identities: stars, specialists, average players, and below-average players are allowed and should not be automatically equalized. Durable ability changes gradually, while temporary form, fatigue, availability, practice, discipline, partying, fictional legal trouble, and other life consequences can alter performance and career outcomes through visible causal chains. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

The shared life, world, memory, and learning layers will support every sport. Each new sport receives its own AI decision brain and authoritative rules engine. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

## Next unresolved decisions

- Engine selection.
- First city identity.
- First two team identities.
- Minimal athlete attributes.
- Initial live LLM provider/model and separate inference budget.
- First retraining dataset and method that fit the $5 ceiling.
- Athlete Life Brain v2 controlled default rollout with explicit historical v1 pins.
- AI evaluation criteria and model-update cadence.
- Ranked competition scoring.
- Match schedule and season length.
