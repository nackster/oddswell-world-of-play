---
tags:
  - development
  - plan
status: active
---

# Current Plan

## Planning authority

- The Scope Director must read [[Design/Beta Game Bible|OddsWell Beta Game Bible]] before selecting a phase.
- It must then follow [[Development/Beta Delivery Roadmap|Beta Delivery Roadmap]] and the earliest incomplete dependency unless measured evidence requires a corrective gate.
- [[Design/Version 1 Game Bible|OddsWell Version 1 Game Bible]] is a future boundary only until the owner approves beta exit and a Version 1 scope freeze.
- **LOCKED** and **BETA TARGET** describe product intent, not proof that a feature exists.
- Work depending on an **OPEN** decision stops for the owner; **LATER** items are not scheduled beta work.
- This plan and phase reports remain the implementation truth.

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

### Phase 0.5N Controlled Athlete Life Brain v2 Default Rollout implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded read-only audits.
- **Implemented:** immutable v1/v2 constants, an explicit v2 default for newly generated life and league decisions, explicit historical-v1 evaluation paths, matching v2 Admin league/prediction generation, and stored-version display in athlete profiles.
- **Fresh default evidence:** the four-season Admin archive contains 80 games and 912/912 v2 decisions: 379 rest, 23 recover, 239 train, and 271 socialize. Admin league winners and replay hashes agree with its same-version prediction commitments.
- **History boundary:** Phase 0.5I retains its exact v1 metrics; Phase 0.5L retains its canonical digest; the no-argument Phase 0D.4 study remains v1. A saved v1 season round-trips unchanged and remains untouched when a new default-v2 season is appended.
- **Validation:** 16 focused tests and all 44 regression tests pass; the Admin Console self-check passes. Cost was `$0.00`. No schema migration, dependency, LLM, learning, retraining, narrative, economy, credits, or wagering was added. See [[Development/Reports/Phase 05N Controlled V2 Default Rollout]].
- **Next gate:** Phase 0.5O review of one bounded short-term Athlete Life Brain memory input before implementation.

### Phase 0.5O Short-Term Routine Memory Review implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded read-only audits.
- **Decision:** define one future signed `routine_streak` from `-2` to `+2`. Two consecutive train choices trigger one socialize choice; two consecutive socialize choices trigger one train choice. Rest, recovery, offseason, and debut reset the state.
- **History contract:** future behavior must be opt-in `athlete-life-v3`; v2 remains default and v1/v2 stay immutable. Reconstruct the same-season streak from ordered archived decisions, so the completed-season save model needs no new schema or duplicated persistent state.
- **Frozen diagnostic:** 120/912 stored v2 choices reach the proposed variation gate. Practice/social trigger rates are 21.76%/25.09%, a 3.33-point gap; one-step choice totals become 255 train, 255 socialize, 379 rest, and 23 recover. This is not a sequential outcome forecast.
- **Validation:** 5 focused tests and all 44 regression tests pass; the Admin Console self-check and both clean canvas checks pass.
- **Cost and scope:** `$0.00`; no runtime, schema, archive, interface, LLM, learning, narrative, ratings, economy, credits, or wagering behavior changed. See [[Development/Reports/Phase 05O Short-Term Routine Memory Review]].
- **Next gate:** Phase 0.5P opt-in v3 routine-memory pilot and fresh paired evaluation; no automatic promotion.

### Phase 0.5P Opt-In Routine Memory Pilot implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded read-only audits.
- **Implemented:** explicit opt-in `athlete-life-v3` with one signed same-season `routine_streak`, a two-choice elective-action ceiling, exact transition reconstruction, unchanged recovery/rest precedence, and no persistence-schema change. V2 remains the default.
- **Fresh paired evidence:** ten untouched seed blocks produced 800 games and 9,120 decisions per policy. V3 recorded 1,208 routine variations across 5,091 eligible decisions; the practice/social trigger-rate gap was 1.8220 percentage points. Policy, version, tenure, transition, ordering, and streak violations were zero.
- **Stability evidence:** actions differed 2,899 times and winners differed in 130/800 games; aggregate margin MAE was 5.8438. Injury, missed-game, fatigue, workload, readiness, scoring, and outcome-sensitivity alarms all pass.
- **Decision:** v3 is `ELIGIBLE FOR LATER REVIEW`, not promoted and not shown in the Admin Console. This is deterministic recent-choice reconstruction, not learning, personality, intelligence, or real-world evidence.
- **Validation:** 7 focused tests and all 46 regression tests pass; the Admin Console self-check and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05P Opt-In Routine Memory Pilot]].
- **Next gate:** Phase 0.5Q deliberate v3 review; the review must not change the default.

### Phase 0.5Q Athlete Life Brain v3 Promotion Review implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded read-only audits.
- **Decision:** approve v3 for a later controlled rollout, but do not promote it during this review. Phase 0.5P passed every frozen aggregate integrity and stability gate; v2 remains the default.
- **Risk boundary:** v2/v3 differ on 2,899 decisions and 130/800 winners. One seed block reached 8.3875 margin MAE even though the frozen aggregate result is 5.8438. These are path-sensitivity signals, not evidence of intelligence, learning, realism, or better outcomes.
- **Required blocker:** the explicit v3 prediction-study path must maintain and reset the same season-local routine mapping before the Admin default can change. Historical Phase 0D.4 remains pinned to v1.
- **Rollout contract:** pin Phase 0.5I to v1, Phase 0.5L to v1/v2, and Phase 0.5P to v2/v3; align new Admin league and prediction state under v3; preserve old history; prove replay, persistence, locked digests, and one-constant rollback; keep state schema v4.
- **Validation:** the focused Phase 0.5P evidence lock, all 46 regression tests, Admin Console self-check, and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05Q V3 Promotion Review]].
- **Next gate:** Phase 0.5R controlled v3 rollout; stop without changing the default if the prediction/history/replay contract cannot be satisfied.

### Phase 0.5R Controlled Athlete Life Brain v3 Default Rollout implementation status

- **Status:** Complete on `agent/phase-0d` after two bounded read-only audits.
- **Implemented:** season-local v3 routine state in the prediction path, one default-constant switch to v3, league implementation `phase05r-v1`, truthful Admin descriptions, and unchanged state schema v4. Historical Phase 0D.4 remains v1.
- **Fresh default evidence:** the four-season Admin archive contains 80 games and 912/912 v3 decisions: 23 recover, 382 rest, 252 socialize, and 255 train. Its first season finished Harbor City 13-7, with 20/20 prediction winners and replay hashes matching the league archive.
- **History boundary:** saved v1/v2 seasons remain byte-for-byte equivalent as objects when a default-v3 season is appended. Phase 0.5L and 0.5P digests remain exact; explicit v2/v3 save, resume, and replay paths pass.
- **Admin/browser evidence:** the Observatory displays `athlete-life-v3` as `ACTIVE DEFAULT`; the League Viewer displays `phase05r-v1`; archived Game 1 completed 422/422 frames at 78-117 with `ARCHIVE VERIFIED` and no console warnings or errors.
- **Validation:** 20 focused tests and all 47 regression tests pass; Admin Console self-check and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05R Controlled V3 Default Rollout]].
- **Rollback:** change one default constant back to v2 and restart; preserve all stored v3 history.
- **Next gate:** Phase 0.5S read-only post-rollout integration review before another Athlete Life Brain input.

### Phase 0.5S Athlete Life Brain v3 Post-Rollout Integration Review status

- **Status:** Complete on `agent/phase-0d`; read-only review with no runtime or data change.
- **Archive evidence:** 912 v3 decisions include 507 elective routine-eligible decisions, 119 bounded variations, a maximum absolute streak and elective run of 2, and 0 routine violations. Practice-group variation was 57/250 (22.8%); social-group variation was 62/257 (24.1245%).
- **Prediction/history evidence:** all 20 first-season Admin predictions agree with league winners and replay hashes. Frozen Phase 0.5L and 0.5P digests remain exact; v1/v2 append-history and explicit v2/v3 replay/resume tests pass.
- **Admin/browser evidence:** the first routine-trigger archive, Season 1 Game 4, completed 452/452 frames at 108-93 with `ARCHIVE VERIFIED`, the expected replay SHA, and no console warnings or errors.
- **Validation:** 2 focused evidence locks and all 47 regression tests pass; Admin Console self-check and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05S Post-Rollout Integration Review]].
- **Decision:** keep v3 as the default. This remains deterministic routine telemetry, not learning, intelligence, personality, or real-world validation.
- **Next gate:** Phase 0.5T design-only Recent Performance Response Review; define and evaluate the information boundary before any new policy version or gameplay change.

### Phase 0.5T Recent Performance Response Review status

- **Status:** Complete on `agent/phase-0d`; design-only review with no runtime or data change.
- **Decision:** define one future three-value `recent_scoring_form` from the immediately previous game's points versus that athlete's earlier same-season appearance average. It defaults to `typical` without three prior appearances or when the athlete did not play.
- **Boundary:** only completed chronological points/minutes enter the signal; it expires after one decision and at every season boundary. Recovery, fatigue rest, and v3 routine variation keep priority. The retrospective Admin form label is not reused because its full-season comparison would leak future games during simulation.
- **Frozen diagnostic:** 912 stored v3 decisions classify as 342 below, 343 typical, and 227 above; 755 have enough prior evidence. The response gate is reached in 211 states and changes 93 choices in a one-step counterfactual without resimulation.
- **Version contract:** any implementation must be opt-in `athlete-life-v4`; v1-v3 history and digests remain immutable, v3 remains the default, and no persistence schema is added.
- **Validation:** 7 focused tests and all 47 regression tests pass; the Admin Console self-check and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05T Recent Performance Response Review]].
- **Truth boundary:** this is a deterministic scoring-response proposal, not overall performance, personality, confidence, learning, intelligence, or real-world evidence.
- **Next gate:** Phase 0.5U opt-in v4 recent-scoring-response pilot and fresh paired evaluation on ten untouched seed blocks; no automatic promotion.

### Phase 0.5U Opt-In Recent Scoring Response Pilot status

- **Status:** Complete on `agent/phase-0d`; v4 remains opt-in and v3 remains the default.
- **Implemented:** one chronology-safe `recent_scoring_form` derived from the immediately previous game versus earlier same-season appearances, with the Phase 0.5T minimum-history and neutral-band rules. Recovery, fatigue rest, and routine variation retain priority.
- **Fresh paired evidence:** ten seed blocks beginning at 50,000 contain 800 games and 9,120 decisions per policy. V4 has 7,564 covered decisions and applies 2,089/2,089 reached responses. All integrity and provisional stability gates pass.
- **Measured impact:** 2,529 action differences, 130/800 winner differences, 5.4813-point margin MAE, +0.1906 mean team points, +1.0-point Harbor win-rate shift, +0.0113-point injury-rate change, and +0.0417-point missed-game-rate change.
- **History boundary:** v1-v3 history remains immutable, Phase 0.5L/0.5P digests remain pinned, the state schema stays v4, explicit v4 save/resume and replay pass, and omission of the v4 argument returns to default v3.
- **Validation:** 12 focused tests pass; final full-suite, Admin self-check, canvas, and whitespace results are recorded in [[Development/Reports/Phase 05U Opt-In Recent Scoring Response Pilot]]. Cost was `$0.00`.
- **Truth boundary:** this is deterministic fictional scoring-response telemetry, not learning, confidence, personality, intelligence, or real-world evidence.
- **Next gate:** Phase 0.5V deliberate v4 promotion review; the review must not change the default.

### Phase 0.5V Athlete Life Brain v4 Promotion Review status

- **Status:** Complete on `agent/phase-0d`; read-only decision phase with no runtime or data change.
- **Decision:** approve v4 for a separate controlled rollout. V3 remains the active default during this review.
- **Evidence:** Phase 0.5U's 800 games and 9,120 decisions per policy retain zero integrity failures, 2,089/2,089 reached responses, and canonical digest `a7b61128668fce26c392a52fac4425324ec41fdfead3b261e57535ff83fc4f60`.
- **Path sensitivity:** v3/v4 differ on 2,529 actions and 130/800 winners. Passing provisional alarms does not prove better outcomes, learning, intelligence, or realism.
- **Required blocker:** the explicit prediction path must reconstruct the same season-local routine and chronological scoring history as the league before any default switch. Historical v1-v4 evidence, replay, persistence, truthful Admin labels, and one-constant rollback are frozen rollout requirements.
- **Validation:** the expected prediction-path blocker is reproduced, 2 focused evaluator/digest tests and all 49 regressions pass, and the Admin Console self-check passes. Cost was `$0.00`. See [[Development/Reports/Phase 05V V4 Promotion Review]].
- **Next gate:** Phase 0.5W controlled v4 rollout; stop without changing the default if any frozen rollout requirement fails.

### Phase 0.5W Controlled Athlete Life Brain v4 Default Rollout status

- **Status:** Complete on `agent/phase-0d`; controlled rollout passed every frozen stop condition.
- **Implemented:** the explicit v4 prediction path now reconstructs the authoritative league's season-local routine map and chronology-safe scoring history. The default changed to v4 only after an 8/8 winner/replay compatibility gate passed; league implementation is `phase05w-v1` and state schema remains v4.
- **Fresh default evidence:** the four-season Admin archive contains 80 games and 912/912 v4 decisions: 24 recover, 386 rest, 234 socialize, and 268 train. It records 204 reached recent-scoring responses; first-season prediction winners and replay hashes agree with the league on 20/20 games.
- **History boundary:** saved v1/v2/v3 seasons remain unchanged when a default-v4 season is appended. Phase 0.5L, 0.5P, and 0.5U retain their exact canonical digests; explicit v4 replay and save/load/resume pass.
- **Admin/browser evidence:** the Observatory displays `athlete-life-v4` as `ACTIVE DEFAULT`; the League Viewer displays `phase05w-v1`; archived Game 1 completed 422/422 frames at 78-117 with `ARCHIVE VERIFIED` and no console warnings or errors.
- **Validation:** 17 focused tests and all 50 regressions pass; Admin Console self-check and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05W Controlled V4 Default Rollout]].
- **Rollback:** change the one default constant back to v3 and restart; preserve all stored v4 history.
- **Next gate:** Phase 0.5X read-only v4 post-rollout integration review before another Athlete Life Brain input.

### Phase 0.5X Athlete Life Brain v4 Post-Rollout Integration Review status

- **Status:** Complete on `agent/phase-0d`; read-only review with no runtime or data change.
- **Archive evidence:** 912/912 v4 decisions classify as 235 above, 327 below, and 350 typical. There are 754 covered classifications, 14 no-appearance defaults, 144 insufficient-history defaults, and 204/204 reached scoring responses.
- **Integrity evidence:** maximum routine streak and elective run remain 2; policy, version, tenure, chronology, classification, precedence, transition, ordering, and replay violations are all zero.
- **Prediction/history evidence:** first-season prediction winners and replay hashes agree 20/20. V1-v3 saved history remains unchanged when v4 is appended, and Phase 0.5L/0.5P/0.5U digests remain exact.
- **Replay evidence:** the first response, Jalen Cross before Season 1 Game 5, follows a chronology-safe `above` classification. The 104-101 archive reconstructs all 423 frames with replay SHA `94afac0a7d08cbea7518acf036363ea25bceada15c1ea71b13351aeeec81c90c` and a verified seal.
- **Validation:** 5 focused locks and all 50 regressions pass; Admin Console self-check and both affected clean canvas checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 05X V4 Post-Rollout Integration Review]].
- **Decision:** keep v4 as the default. This remains deterministic scoring-response telemetry, not learning, confidence, personality, intelligence, or real-world evidence.
- **Next gate:** Phase 0.5Y design-only Next Athlete Life Input Selection Review; choose at most one justified bounded input, or none, before implementation.

### Phase 0.5Y Next Athlete Input Selection decision

- **Decision:** select no new Athlete Life Brain input. The requested star-versus-average behavior is competitive performance variance, so it belongs in the Athlete Profile and Basketball Brain rather than personal-life policy.
- **Selected core input:** one durable `game_consistency` tier that changes variance around existing ratings without adding talent.
- **Next gate:** Phase 0.6A opt-in Athlete Game Consistency pilot; default league behavior must remain unchanged.

### Phase 0.6A Opt-In Athlete Game Consistency Pilot status

- **Status:** Complete on `agent/phase-0d`; explicit pilot only, not authoritative league behavior.
- **Implemented:** versioned volatile/normal/steady/elite tiers produce one deterministic zero-centered game-form modifier per athlete and seed. The bounded modifier reaches passing/turnover and shooting/defense resolution only when explicitly supplied.
- **Rarity:** the active twelve-athlete prototype has 1 elite, 4 steady, 5 normal, and 2 volatile athletes. Elite consistency alone does not create a superstar; rare high ratings must also be present.
- **80-game evidence:** tier form width is strictly ordered; 47 scores and 12 winners differ, mean absolute team-score difference is 4.2062 points, and replay violations are zero.
- **History/Admin boundary:** omission returns the exact legacy resolver; frozen v1-v4 studies remain clean. Athlete profiles show the value as an `OPT-IN PILOT`, not active training or learned behavior.
- **Validation:** 10 focused tests, all 53 regressions, and the Admin Console self-check pass. Cost was `$0.00`. See [[Development/Reports/Phase 06A Opt-In Athlete Consistency Pilot]].
- **Next gate:** Phase 0.6B read-only multi-season same-athlete calibration before any rollout decision.

### Phase 0.6B Athlete Game Consistency Calibration status

- **Status:** Complete on `agent/phase-0d`; read-only outcome calibration with no rollout or authoritative-league change.
- **Controlled evidence:** Tariq Stone keeps identical ratings, role, team, matchup, and healthy/rested state across 1,000 games per tier. All other athlete form is zero.
- **Passed:** tier means stay within 0.057 points, team win-rate spread is 0.8 percentage points, and all 4,000 pilot games replay exactly.
- **Failed:** elite point deviation is 6.3128 versus volatile 6.3590; bad-night rates are 19.2% versus 19.3%; both 20th-percentile floors are 14 points. The frozen reliability gates therefore fail.
- **Decision:** keep `athlete-consistency-v1` opt-in and do not promote it. Its label is mechanically real but does not yet create the intended superstar reliability.
- **Validation:** all 54 regressions pass and the Admin self-check remains green. Cost was `$0.00`. See [[Development/Reports/Phase 06B Athlete Consistency Calibration]].
- **Next gate:** Completed as Phase 0.6C; the first replacement contract is frozen before implementation.

### Phase 0.6C Consistency Resolver Redesign Review status

- **Status:** Complete on `agent/phase-0d`; design-only, with no simulator, league, Admin, schema, or historical-evidence change.
- **Decision:** approve one explicit opt-in `athlete-consistency-v2` candidate for testing. A game-local shooting ledger compares cumulative unmodified expected shot points with actual shot points and applies a bounded next-shot correction.
- **Talent boundary:** ratings, matchup, fatigue, and readiness continue to define the base probability. Consistency narrows variance around that expectation; it does not add ratings, usage, opportunity, or career value.
- **Frozen tiers:** volatile has no correction; normal, steady, and elite use increasing strengths with 3-, 6-, and 10-percentage-point caps. V1 and v2 may not run together.
- **Scope:** shooting only. Passing, defense, rebounding, opportunity smoothing, confidence, personality, cross-game memory, and generic specialist consistency remain later work.
- **Promotion gates:** at least 10% lower elite point deviation, 20% fewer elite bad nights, a one-point higher 20th-percentile floor, preserved nonzero bad nights and 90th-percentile highs, means within 0.5 points, attempts within 0.5, team win spread within five points, exact replay, and unchanged legacy/history paths.
- **Frozen scoring floors:** Tariq retains the Phase 0.6B fewer-than-14-point threshold. Jalen's untouched 1,000-game control averaged 20.565 points, freezing his bad night as fewer than 16 points before v2 implementation.
- **Rarity:** elite consistency is not a superstar by itself. The future production target is no more than about 1% of established athletes combining top-tier ability with elite consistency; the current one-of-twelve fixture is calibration only.
- **Cost and truth:** `$0.00`; deterministic variance control, not learning, confidence, mentality, personality, neural-network training, or real-world evidence. See [[Development/Reports/Phase 06C Consistency Resolver Redesign Review]].
- **Next gate:** Completed as Phase 0.6D; the opt-in v2 candidate passed the frozen evaluation without automatic promotion.

### Phase 0.6D Opt-In Consistency Resolver v2 Pilot status

- **Status:** Complete on `agent/phase-0d`; v2 is eligible for a separate review but remains inactive in the authoritative league.
- **Implemented:** a per-game expected-versus-actual shot-points ledger, frozen tier strengths and caps, bounded next-shot correction, per-shot audit fields, exact replay reconstruction, full input validation, and rejection of simultaneous v1/v2 inputs.
- **Controlled evidence:** Tariq Stone and Jalen Cross each ran 1,000 games per tier with identical ratings and circumstances: 8,000 games plus 8,000 exact replays.
- **Tariq result:** elite deviation falls 26.14%, bad nights fall 40.93%, and the P20 floor rises from 14 to 15. Tier means span 0.076 points, attempts span 0.083, P90 remains within two points, and team wins span 2.0 percentage points.
- **Jalen result:** elite deviation falls 21.42%, bad nights fall 28.50%, and the P20 floor rises from 15 to 16. Tier means span 0.246 points, attempts span 0.122, P90 remains within two points, and team wins span 2.2 percentage points.
- **Integrity:** every frozen gate passes, replay violations are 0/8,000, omission preserves legacy behavior, and all historical paths remain green.
- **Admin boundary:** profiles display v2 as `OPT-IN CANDIDATE` with `SHOOTING ONLY` scope. Passing, defense, rebounding, confidence, personality, learning, and real-world evidence are not claimed.
- **Validation:** 13 focused tests and all 56 regressions pass; Admin Console self-check passes. Cost was `$0.00`. See [[Development/Reports/Phase 06D Opt-In Consistency Resolver v2 Pilot]].
- **Next gate:** Completed as Phase 0.6E; v2 is approved for a separate controlled rollout while the default remains unchanged.

### Phase 0.6E Consistency v2 Promotion Review status

- **Status:** Complete on `agent/phase-0d`; read-only review with no runtime, default, schema, league, prediction, or Admin behavior change.
- **Decision:** approve the shooting-only v2 candidate for a separate controlled rollout. It remains opt-in during this review.
- **Path sensitivity:** elite versus volatile changes 815/1,000 Tariq scores and 231/1,000 winners; Jalen changes 816/1,000 scores and 238/1,000 winners. Mean absolute team-score differences are 5.7725 and 5.5495 points.
- **Audit evidence:** 20,312 Tariq and 20,912 Jalen shots have complete audit fields and zero violations. Roughly 95% receive a nonzero correction and about 80% hit the 0.10 cap; this saturation remains visible and parameters may not be tuned during rollout.
- **Required blocker:** the authoritative league, replay manifest, persisted season history, prediction study, and Admin archive reconstruction do not yet share or store a consistency version and tier snapshot.
- **Rollout contract:** add one v2/disabled default switch, bind exact settings into replay evidence, store versioned history with safe v4 compatibility, align new predictions with the league, preserve historical disabled paths, keep the shooting-only label, and prove rollback without reinterpreting stored v2 games.
- **Validation:** four focused consistency tests, Admin self-check, both clean canvas checks, and whitespace validation pass; the unchanged runtime retains Phase 0.6D's 56/56 full regression evidence.
- **Cost and truth:** `$0.00`; deterministic fictional scoring-variance control, not learning, intelligence, confidence, mentality, or real-world validation. See [[Development/Reports/Phase 06E Consistency v2 Promotion Review]].
- **Next gate:** Phase 0.6F controlled v2 rollout; stop without promotion if any frozen integration or rollback requirement fails.

### Phase 0.6F Controlled Consistency v2 Rollout status

- **Status:** Complete on `agent/phase-0d`; every frozen Phase 0.6E rollout condition passed.
- **Implemented:** `athlete-consistency-v2` is the default for new games through one explicit switch. League `phase06f-v1` passes a full frozen roster snapshot through the shooting resolver, stores it in v5 season history, and binds it into v2 replay evidence.
- **Compatibility:** existing v4 state loads as v5 with consistency disabled; disabled manifests preserve old replay hashes. V5 save/load also supports the Roman Voss to Soren Lake roster transition.
- **Prediction/Admin:** historical Phase 0D.4 studies stay disabled. The current Admin league and prediction study explicitly share v2, archived Game Theater uses each stored snapshot, and profiles show `ACTIVE DEFAULT` with `SHOOTING ONLY` scope.
- **History and rollback:** frozen life-policy digests remain exact. Changing one default constant to `athlete-consistency-disabled` plus restart affects new games only; stored v2 games remain replayable.
- **Validation:** 23/23 league/prediction rollout tests, 4/4 frozen multi-seed checks, all 59 regressions, and the Admin Console self-check pass. Cost was `$0.00`. See [[Development/Reports/Phase 06F Controlled Consistency v2 Rollout]].
- **Truth boundary:** deterministic fictional shooting-variance control, not learning, confidence, personality, intelligence, or real-world evidence.
- **Next gate:** Phase 0.6G read-only post-rollout integration review before another athlete-performance input.

### Phase 0.6G Consistency v2 Post-Rollout Integration Review status

- **Status:** Complete on `agent/phase-0d`; read-only review with no runtime, default, parameter, schema, API, or Admin behavior change.
- **Fresh archive:** all 80/80 games use v2 with complete 12-athlete stored snapshots. First-season prediction winners and replay hashes agree 20/20; archived Season 1 Game 1 reconstructs all 428 frames with a verified replay seal.
- **Compatibility:** v4-to-v5 disabled migration, historical Phase 0D.4 prediction isolation, frozen life-policy digests, and stored-v2 replay remain exact.
- **Rollback:** one default-constant change to disabled plus restart still affects only new games; stored v2 history retains its version and snapshot.
- **Validation:** 7/7 focused locks, all 59 regressions, Admin Console self-check, fresh archive reconstruction, and the affected clean canvas pass. Cost was `$0.00`. See [[Development/Reports/Phase 06G Consistency v2 Post-Rollout Integration Review]].
- **Decision:** keep shooting-only v2 as the active default. No realism, learning, confidence, personality, or real-world claim is added.
- **Next gate:** Phase 0.6H design-only Next Athlete Performance Input Selection Review; choose at most one justified bounded input or none before implementation.

### Phase 0.6H Next Athlete Performance Input Selection decision

- **Status:** Complete on `agent/phase-0d`; design-only review with no runtime, schema, replay, prediction, Admin, or default behavior change.
- **Decision:** select one durable `offensive_involvement` tier (`low`, `standard`, or `featured`) for an opt-in pilot. It may only redistribute initial ballhandler and pass-target selection, so its truthful scope is `OPPORTUNITY ONLY`.
- **Evidence:** the four-season archive shows a compact opportunity range across visibly different roles. Cal Brooks records 22.18 field-goal attempts per 48 minutes with 70 shooting, only 4.8% below Nico Reyes at 23.29; high-passing Micah Vale and Eli Mercer record 19.80 and 19.93.
- **Boundaries:** ratings and circumstances still define ability and shot probability; Consistency v2 still controls shooting variance. The future pilot is bounded to 0.85-1.15 selection weights, one frozen pregame snapshot, exact replay evidence, explicit opt-in, and immutable history.
- **Not selected:** shot-location profiles, clutch/confidence/mentality, defensive consistency, and another Life Brain input. None has a smaller measured need than opportunity.
- **Validation:** authoritative 80-game archive evidence was reconstructed from event records; 4/4 focused Consistency v2 boundary tests, the Admin self-check, documentation, affected canvas structure, and whitespace checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 06H Next Athlete Performance Input Selection Review]].
- **Next gate:** Phase 0.6I opt-in Offensive Involvement pilot; keep the authoritative league default unchanged and stop without promotion if the frozen opportunity, talent, replay, history, Admin-label, or rollback boundary fails.

### Phase 0.6I Opt-In Offensive Involvement Pilot status

- **Status:** Complete on `agent/phase-0d`; explicit pilot only, not authoritative league behavior.
- **Implemented:** frozen low/standard/featured weights of 0.85/1.00/1.15 multiply only initial-ballhandler and pass-target selection. Ratings, action weights after possession starts, shot probability, minutes, Consistency v2, Life Brain decisions, and career progression are unchanged.
- **Paired evidence:** 200 Jalen seeds per tier produce strictly ordered mean selection opportunities of 25.375, 28.085, and 31.085. Mean shot attempts are 19.180, 20.990, and 23.290 while field-goal percentage stays at 45.26%, 45.21%, and 45.38%.
- **Sensitivity:** low/featured change 157/146 scores and 54/43 winners versus standard. These are visible path differences, not claimed improvements.
- **Integrity:** 600/600 pilot games and 200/200 omitted controls replay exactly; manifests bind the exact version and snapshot, tampering fails, and shot-formula violations are zero.
- **Admin/history:** profiles say `OPT-IN PILOT` and `OPPORTUNITY ONLY`; no production roster tiers, default, prediction, schema, or stored-history behavior changed.
- **Validation:** 3 focused tests, all 62 regressions, Admin Console self-check, canvas structure, and whitespace checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 06I Opt-In Offensive Involvement Pilot]].
- **Next gate:** Phase 0.6J read-only multi-athlete Offensive Involvement calibration across a high-passing creator, a lower-rated scorer, and Jalen's control before any promotion review.

### Phase 0.6J Multi-Athlete Offensive Involvement Calibration status

- **Status:** Complete on `agent/phase-0d`; read-only calibration with the athlete set, seeds, and numeric gates frozen before measurement.
- **Role coverage:** 200 paired seeds per tier cover high-passing Micah Vale, lower-rated scorer Cal Brooks, and the original Jalen Cross control. The existing 0.85/1.00/1.15 weights and all player ratings remain unchanged.
- **Opportunity result:** low is 9.95%-12.17% below standard and featured is 8.89%-11.71% above standard for all three athletes. Field-goal percentage spreads stay within 0.54-0.98 percentage points and team-possession spreads within 0.220-0.495.
- **Talent boundary:** Cal's featured 39.54% field-goal rate remains below Jalen's standard 44.02%; added opportunity does not erase their frozen shooting-rating difference.
- **Integrity:** 1,800/1,800 pilot replays, 600/600 omitted-control checks, and 1,800/1,800 manifests pass. Three snapshot-tamper checks fail verification as required; shot-formula violations are zero.
- **Decision:** eligible only for a separate promotion review. The pilot remains `OPT-IN PILOT` and `OPPORTUNITY ONLY`; the authoritative league still supplies no snapshot.
- **Validation:** 3 focused tests, all 62 regressions, Admin Console self-check, canvas structure, and whitespace checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 06J Multi-Athlete Offensive Involvement Calibration]].
- **Next gate:** Phase 0.6K read-only Offensive Involvement Promotion Review; decide controlled-rollout eligibility without implementing rollout.

### Phase 0.6K Offensive Involvement Promotion Review status

- **Status:** Complete on `agent/phase-0d`; read-only review with no runtime, default, schema, parameter, rating, prediction, replay, or Admin behavior change.
- **Decision:** approve `offensive-involvement-v1` for a separate controlled rollout. It remains `OPT-IN PILOT` and `OPPORTUNITY ONLY` during this review.
- **Evidence:** 2,400 pilot games and 800 omitted controls across Phases 0.6I-0.6J retain ordered opportunity, stable shooting efficiency and team possessions, exact replay/manifests, an unchanged shot formula, and a preserved Cal/Jalen shooting-talent boundary.
- **Sensitivity and limits:** 19.0%-25.5% of paired winners change across the six multi-role comparisons. The reviewed creator, lower-rated scorer, and higher-rated control support an engineering rollout only; no real-world usage distribution, intelligence, confidence, personality, or learning claim is authorized.
- **Required integration:** add one v1/disabled default switch, freeze a complete roster snapshot, persist version/snapshot with safe v5-disabled migration, bind replay evidence, align current league/prediction/Admin/archive paths, preserve all historical evidence, and keep custom decision policies disabled for involvement.
- **Rollback:** one default-constant change to disabled plus restart affects new games only; stored v1 seasons must replay from their stored snapshots.
- **Validation:** 3/3 focused tests, all 62 regressions, Admin Console self-check, canvas structure, and whitespace checks pass. Cost was `$0.00`. See [[Development/Reports/Phase 06K Offensive Involvement Promotion Review]].
- **Next gate:** Phase 0.6L controlled Offensive Involvement rollout; stop without promotion if any frozen integration, history, labeling, or rollback condition fails.

### Phase 0.6L Controlled Offensive Involvement Rollout status

- **Status:** Complete on `agent/phase-0d`; every frozen Phase 0.6K rollout condition passed.
- **Implemented:** `offensive-involvement-v1` is the default for new baseline-policy games through one explicit switch. The frozen full-career table produces exact 12-athlete matchup snapshots and covers the Roman Voss to Soren Lake transition without changing the `0.85`/`1.00`/`1.15` weights.
- **Persistence and replay:** league `phase06l-v1` stores version and snapshot in v6 history and replay evidence. V4/V5 history migrates with involvement disabled; stored v1 archives reconstruct from their own snapshot after rollback.
- **Current surfaces:** league, prediction, Admin live simulation, Athlete Profiles, and archived playback agree on v1. Labels say `ACTIVE DEFAULT`, `OPPORTUNITY ONLY`, and baseline policy only.
- **Historical boundary:** Phase 0D.4 and frozen Life Brain studies remain explicitly disabled. All three historical digests stay exact.
- **Validation:** 29/29 focused checks, all 65 regressions, Admin self-check, archive reconstruction, compilation, canvas structure, and whitespace pass. Cost was `$0.00`.
- **Truth boundary:** deterministic fictional opportunity weighting, not learning, coaching intelligence, confidence, personality, player quality, or real-world usage evidence.
- **Next gate:** Phase 0.6M read-only post-rollout integration review before another athlete-performance input.

### Phase 0.6M Offensive Involvement Post-Rollout Integration Review status

- **Status:** Complete on `agent/phase-0d`; read-only review with no runtime, default, tier, weight, schema, rating, prediction, replay, API, or Admin behavior change.
- **Fresh archive:** all 80 games store v1 and complete 12-athlete snapshots; all 20 Season 4 snapshots contain Soren Lake, first-season prediction winners and replay hashes agree 20/20, and Season 1 Game 1 reconstructs 421 verified frames.
- **Integration:** Admin status and all 13 durable profiles retain `ACTIVE DEFAULT`, `OPPORTUNITY ONLY`, and baseline-policy-only labels. Stored archive reconstruction uses each game's snapshot.
- **Migration/history/rollback:** v5 loads as v6 with involvement disabled, historical prediction and Life Brain studies remain disabled, all three frozen digests stay exact, and one-switch rollback changes only new games.
- **Decision:** keep `offensive-involvement-v1` as the default without tuning. No real-world usage, learning, intelligence, coaching, confidence, personality, or player-quality claim is authorized.
- **Validation:** 11/11 focused locks, all 65 regressions, Admin self-check, compilation, canvas structure, and whitespace pass. Cost was `$0.00`. See [[Development/Reports/Phase 06M Offensive Involvement Post-Rollout Integration Review]].
- **Next gate:** Phase 0.6N design-only Next Athlete Performance Input Selection Review; select at most one bounded input or explicitly select none.

### Phase 0.6N Athlete Performance Scope Freeze and Phase 1 Handoff status

- **Status:** Complete on `agent/phase-0d`; documentation-only decision with no runtime, source, schema, roster, prediction, replay, API, or Admin behavior change.
- **Decision:** select no additional Athlete Performance input. Phase 0 is frozen except for demonstrated defects in an existing contract.
- **Frozen stack:** Athlete Life Brain v4, shooting-only Consistency v2, opportunity-only Offensive Involvement v1, v6 stored history, authoritative event-log outcomes, archived replay, Admin truth labels, historical pins, migration, and rollback boundaries remain unchanged.
- **Reopen rule:** a deferred input requires a named first-playable experience failure, a preregistered controlled miss of at least 10% across at least 1,000 paired seeds, or a verified replay/persistence/migration/Admin defect. Backlog ideas are not scheduled work without one of these triggers.
- **Validation:** all 65 frozen regressions, Admin self-check, compilation, Obsidian links, affected canvas structure, and whitespace pass. Cost was `$0.00`. See [[Development/Reports/Phase 06N Athlete Performance Scope Freeze and Phase 1 Handoff]].
- **Next gate:** Phase 1A One-Block 3D Vertical-Slice Engine Benchmark. Use placeholders, measure frame time, memory, build time, and asset iteration, and keep the engine/version choice open until evidence exists.

## Phase 1: 3D vertical slice

Build the one-city scope defined in [[Design/Decisions/DEC-002 First Playable Scope]].

### Phase 1A next gate

- Benchmark one compact street block, one court, one controllable rigged avatar, basic lighting/collision/navigation, placeholder NPCs, and one recorded-game adapter.
- Preserve the authority boundary: the 3D client renders stored event-log outcomes and never resimulates basketball.
- Record packaged-build frame time, memory use, build time, and one representative asset-iteration time before selecting an engine and version.
- Begin with the owner-gated local readiness audit; do not install an engine, create final art, add economy/credits/wagering, deploy, use paid APIs, or train a model without a later explicit phase.

### Phase 1A.0 Local 3D Toolchain and Replay Interface Readiness Audit status

- **Status:** Complete on `agent/phase-0d`; read-only audit with no download, install, project scaffold, adapter, schema, API, simulator, Admin, art, backend, deployment, or model change.
- **Measured workstation:** Windows 11 Pro; Core Ultra 9 185H; 63.4 GiB RAM; RTX 4070 Laptop GPU with 8,188 MiB; 3,053.6 GiB free on `C:`.
- **Toolchain:** Epic Launcher, Blender 4.5.5 LTS, Visual Studio 2022 C++/MSVC 14.44, Windows SDK 10.0.22000.0, Git 2.49.0, and Git LFS 3.6.1 are present. No Unreal installation was found beyond PATH in Epic manifests, Unreal registries, or common fixed-drive install roots.
- **Repository:** existing generated-directory ignores and LFS rules cover the first expected engine/3D paths; no speculative rule changed.
- **Replay interface:** Season 1 Game 1 independently reproduces Harbor City `101`–`104` Mesa Vista across 421 public frames with the exact verified replay seal. Hidden seed, fatigue/readiness, recovery, injury-risk, RNG, and resolver snapshots remain server-side; a 3D client renders recorded outcomes and never resimulates.
- **Validation:** all 65 frozen regressions, Admin self-check, compilation, Obsidian links, affected canvas structure, whitespace, and scoped diff pass. Cost was `$0.00`. See [[Development/Reports/Phase 1A0 Local 3D Toolchain and Replay Interface Readiness Audit]].
- **Outcome:** **READY FOR OWNER INSTALL APPROVAL**. Engine/version selection and compatibility remain unverified until the owner approves one installer; Phase 1A.0 starts no later phase.

### Phase 1A.1a Unreal Engine Installation and Editor Launch Verification status

- **Status:** Complete on `agent/phase-0d`; owner-approved Unreal Engine 5.8 pilot installation and one first-launch verification only.
- **Installed candidate:** UE `5.8.0`, changelist `55116800`, at `C:\Program Files\Epic Games\UE_5.8`; the approved default bundle also installed Quixel Bridge `2025.0.1` and Fab UE Plugin `0.0.13`.
- **Install evidence:** all three manifests are present. Main and companion Build Patch jobs report success, `ErrorCode: OK`, and final progress `1.000000`; the main job downloaded 12.381 GB, wrote 30.676 GB, and completed in 58:17.
- **Launch evidence:** the editor reached the no-project Project Browser, reported the exact 5.8 build, logged startup completion with zero fatal/critical/unhandled/assert matches, and created no repository `.uproject` file.
- **Safety and prerequisite:** the owner manually handled two Windows Firewall prompts. UE reports installed Visual C++ Redistributable `14.44.35211.0` below recommended `14.50.35719.0`; no prerequisite installer ran.
- **Exit:** normal editor shutdown completed and no Unreal Editor, trace, Zen, crash, or CEF process remained.
- **Validation:** final frozen regressions, Brain Admin self-check, documentation, canvas, and hygiene evidence are recorded in [[Development/Reports/Phase 1A1a Unreal Engine Installation and Editor Launch Verification]]. Cost was `$0.00`.
- **Next gate:** Phase 1A.1b aligns the official Microsoft x64 runtime and repeats the no-project editor check in a separate phase. Project creation, packaging, permanent engine adoption, final art, and the one-block replay benchmark remain inactive.

### Phase 1A.1b Visual C++ Runtime Prerequisite Alignment and Unreal Recheck status

- **Status:** Complete on `agent/phase-0d`; official Microsoft Visual C++ 2015–2022 x64 runtime alignment and post-reboot Unreal recheck only.
- **Package evidence:** official Microsoft x64 package version `14.51.36247.0`, size `18,731,856` bytes, SHA-256 `843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C`, with valid Microsoft Corporation Authenticode signature.
- **Install evidence:** registered x64 runtime advanced from `v14.44.35211.00` to `v14.51.36247.00`; Setup and both MSI packages succeeded, returned reboot-required code `3010`, and did not restart automatically.
- **Safety:** the owner approved the exact installer at action time, manually handled UAC, and rebooted manually. No x86 package, Visual Studio workload, compiler, SDK, security control, or privacy control was changed.
- **Recheck:** the UE 5.8 no-project Project Browser returned without the earlier runtime warning. The exact build logged startup completion with zero fatal/critical/unhandled/assert matches.
- **Exit and scope:** normal close completed, no UE 5.8 process remained, and no repository `.uproject` exists.
- **Validation:** final frozen regressions, Brain Admin self-check, documentation, canvas, and hygiene evidence are recorded in [[Development/Reports/Phase 1A1b Visual Cpp Runtime Prerequisite Alignment and Unreal Recheck]]. Cost was `$0.00`.
- **Next gate:** Phase 1A.1c creates and reopens the smallest empty local Windows project in a separate phase. Packaging, permanent adoption, final art, and the one-block replay benchmark remain inactive.

### Phase 1A.1c Minimal Blank OddsWell Project Bootstrap and Reopen status

- **Status:** Complete on `agent/phase-0d`; smallest portable UE 5.8 Blueprint-only desktop project and reopen proof only.
- **Portable project:** `client/OddsWell/OddsWell.uproject` associates with Engine `5.8`, declares no modules or plugins, and has four generated portable config files plus exactly one map.
- **Map and settings:** `Content/Maps/Bootstrap.umap` is an 8,422-byte empty level with zero actors. Editor and game defaults point to `/Game/Maps/Bootstrap.Bootstrap`; ray tracing and its project proxies are disabled. Unreal's default Android file-server path is explicitly disabled, network access is off, and no portable token remains.
- **Scope:** no Starter Content, `.uasset`, C++ source/build target, gameplay Blueprint, package, replay adapter, art, backend, economy, wagering, API, Admin runtime, or model work was added.
- **Reopen evidence:** UE Project Browser identified the exact disk path and Engine 5.8; the reopened editor loaded `Bootstrap`, logged startup completion with zero fatal/critical/unhandled/assert matches, and closed normally with no editor or shader worker left.
- **Repository:** the map uses Git LFS; `DerivedDataCache`, `Intermediate`, and `Saved` remain ignored and unstaged. See [[Development/Reports/Phase 1A1c Minimal Blank OddsWell Project Bootstrap and Reopen]]. Cost was `$0.00`.
- **Next gate:** Phase 1A.1d packages and runs this unchanged empty Windows project and records disk, build, launch, frame-time, and memory evidence. No gameplay or permanent engine adoption begins automatically.

### Phase 1A.1d Empty Windows Package, Launch, and Baseline Measurement status

- **Status:** Complete on `agent/phase-0d`; the unchanged empty UE 5.8 project packaged twice and launched as a local Windows Development executable.
- **Packaging:** clean package passed in `191.420s`; unchanged incremental package passed in `69.497s`. The pre-launch archive contained 48 files and 968,411,765 bytes (`0.902 GiB`). Generated package, cook, cache, log, and local settings output remains ignored and unstaged.
- **Runtime:** the visible 1280x720 window appeared in `0.656s`, engine initialization completed approximately `3.613s` after process start, and `/Game/Maps/Bootstrap` loaded in `0.086006s` with zero fatal/prerequisite match.
- **Empty-map baseline:** three warm readings averaged `4.35 ms` frame, `3.61 ms` GPU, and `1.31 GB` displayed memory. Process samples averaged `1.307 GiB` working set and `2.364 GiB` private bytes. This is preliminary empty Development-build evidence only.
- **Security/network:** no established TCP connection or UDP endpoint existed. Unreal Trace's explained Development listener used TCP `1985`; the owner manually selected **Cancel** on Windows Firewall, and automation changed no security setting.
- **Integrity:** normal close left no related process, all six portable input hashes remained exact, 65/65 frozen regressions and the Brain Admin self-check passed, and cost was `$0.00`. See [[Development/Reports/Phase 1A1d Empty Windows Package Launch and Baseline Measurement]].
- **Next gate:** Phase 1A.2a adds one noncanonical primitive street block and court in a separate benchmark map and measures one representative asset iteration. City identity, camera, avatar, multiplayer, final art, replay rendering, and permanent Unreal adoption remain inactive.

### Phase 1A.2a Noncanonical Street Block and Basketball Court Graybox status

- **Status:** Complete on `agent/phase-0d`; one separate UE 5.8 benchmark map only. The empty `Bootstrap` default and all five portable configuration inputs remain byte-identical.
- **Map:** `Content/Maps/BlockCourtBenchmark.umap` contains 25 labeled benchmark actors: 21 built-in cube/cylinder mesh actors with `BlockAll` collision plus four native lighting/environment actors. The geometry is explicitly noncanonical and does not select the city, art direction, camera, avatar, navigation, multiplayer, gameplay, or final assets.
- **Representative iteration:** `Benchmark_Building_04` moved from `(3000, -2700, 450)` to `(3000, -2500, 450)` and resized from `(8, 5, 9)` to `(10, 5, 9)` in `0.486s`, including map save. A fresh editor-command process reopened and verified the result.
- **Evidence:** final map size is `48,831` bytes with SHA-256 `F970A2F4609F2D6EC24475AE48C98E12DB53BDE2CD95A238F2015C3FF0840018`; Map Check reports 0 errors and 0 warnings. A local ignored `1920x1080` proof image frames the block, court, two hoop assemblies, road, sidewalks, and four building masses.
- **Integrity:** all 65 frozen regressions passed in `160.509s`; Brain Admin self-check and Python compilation passed; the empty package remains 51 files and 968,413,407 bytes; no Unreal, crash, trace, or shader-worker process remained. Cost was `$0.00`. See [[Development/Reports/Phase 1A2a Noncanonical Street Block and Basketball Court Graybox]].
- **Next gate:** Phase 1A.2b directly renders the existing verified 421-frame replay in the benchmark client without resimulating basketball. It remains a separate phase; permanent Unreal adoption still waits for replay evidence and owner review.

### Phase 1A.2b Authoritative 421-Frame Replay Renderer status

- **Status:** Complete on `agent/phase-0d`; the benchmark-only UE 5.8 runtime directly displays the frozen public Season 1 Game 1 replay. The default Bootstrap map and noncanonical block/court map remain unchanged.
- **Input:** tracked 256,442-byte public fixture with 421 frames, exact Harbor City 101-104 Mesa Vista final, fixture SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, and authoritative replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`. Forbidden hidden-state keys are absent.
- **Client boundary:** 12 symbolic built-in markers, fixed illustrative positions, public clock/score/event text, actor/target emphasis, and final seal. The module activates only for `-ReplayBenchmark`; it has no simulator, random source, Python runtime, network call, external service, or plugin dependency.
- **Build evidence:** owner-approved Visual Studio Installer added only the required .NET Framework 4.8 SDK. Final editor/game compilation and Windows BuildCookRun passed; the final incremental package completed in `58.14s`.
- **Runtime evidence:** two final packaged runs each rendered all 421 frames, exited `0`, produced zero replay errors, ended 101-104 with the exact seal, and shared canonical trace SHA-256 `12fb61d032a93e667451c364f77907e68e53b934c46f765b6f32eefe9316dbbe`. A final measured run completed in `8.861s` with `1.213 GiB` average and `1.763 GiB` peak working set across startup, accelerated replay, and shutdown.
- **Integrity:** all 65 frozen regressions passed in `131.138s`; Brain Admin self-check, fixture export, Python compilation, packaged-copy hashes, and repository hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1A2b Authoritative 421-Frame Replay Renderer]].
- **Next gate:** Phase 1A.3 is an owner review: accept Unreal Engine 5.8 for continued beta work, reject it, or request one specific measured comparison. Character selection and every later roadmap phase remain inactive until that decision is recorded.

### Phase 1A.3 Unreal Engine 5.8 Beta Adoption status

- **Status:** Complete by explicit owner decision on July 19, 2026.
- **Decision:** Unreal Engine 5.8 is approved for OddsWell beta client development; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].
- **Accepted evidence:** portable project reopen, reproducible Windows packaging and launch, representative block/court iteration, packaged 421-frame authoritative replay rendering, deterministic replay traces, clean generated-file boundaries, frozen regressions, and Brain Admin checks.
- **Boundary:** the decision approves the engine, not a city identity, camera, character-art direction, paid service, deployment, or later feature.
- **Next gate:** Phase 1B needs the owner to approve camera/movement style and the minimum placeholder preset/character-art direction before implementation chooses those product details.

### Phase 1B.1 Character Preset Catalog status

- **Status:** Complete on `agent/phase-0d`; smallest executable Phase 1B data slice only.
- **Owner direction:** third-person trailing camera; keyboard/mouse and controller walk, run, and jump; eight gameplay-identical placeholders covering two presentations and four shared skin tones; neutral placeholder proportions; replaceable worn off-white top and bottom. See [[Design/Decisions/DEC-007 Phase 1B Character Defaults]].
- **Implementation:** a native UE 5.8 catalog stores only cosmetic preset identity, presentation, skin tone, and equipped item IDs. It contains no gameplay modifiers and adds no plugin or dependency.
- **Validation:** final `OddsWellEditor` Development build passed; the native `OddsWell.Character.PresetCatalog` test passed 1/1; all 65 frozen regressions passed in `132.517s`; Brain Admin self-check and Python compilation passed. Cost was `$0.00`.
- **Boundary:** no selection screen, mesh, animation, controllable pawn, save file, final character art, city, economy, wagering, service, or deployment was added. See [[Development/Reports/Phase 1B1 Character Preset Catalog]].
- **Next gate:** Phase 1B.2 builds the fast local selection screen with a safe default from this catalog.

### Phase 1B.2 Fast Local Character Selection Screen status

- **Status:** Complete on `agent/phase-0d`; one local selection screen only.
- **Implementation:** a native UE 5.8 HUD consumes the validated eight-entry catalog directly, shows the same neutral placeholder silhouette and replaceable off-white top and bottom for every option, starts on a deterministic safe default, wraps keyboard/controller navigation, and allows exactly one session-local confirmation. A transient URL-selected game mode leaves the Bootstrap default unchanged.
- **Safety boundary:** catalog failure remains local and unconfirmed. The selected ID is not persisted or sent anywhere, and no pawn, movement, camera, mesh, animation, account, backend, multiplayer, economy, wagering, service, model, or retraining behavior was added.
- **Validation:** final editor and Development game builds passed; native character automation passed 2/2; a 55-file Windows package visibly confirmed the default and one non-default option exactly once each with clean exits; all 65 frozen regressions, Brain Admin self-check, and Python compilation passed. After the owner manually canceled the initial Windows Firewall prompt, a bounded safe-default rerun showed no security prompt or modal and left no related process. Controller routes are automation-tested; physical controller hardware was not tested. Cost was `$0.00`. See [[Development/Reports/Phase 1B2 Fast Local Character Selection Screen]].
- **Next gate:** Phase 1B.3 adds one controllable placeholder avatar with the approved third-person camera and keyboard/mouse/controller walk, run, and jump direction.

### Phase 1B.3 Controllable Placeholder Avatar and Approved Locomotion status

- **Status:** Complete on `agent/phase-0d`; one separate local locomotion proof only.
- **Implementation:** a neutral cylinder-and-cube `ACharacter` uses the native capsule, `CharacterMovement`, spring-arm camera collision, and direct keyboard/mouse/controller routes in the unchanged noncanonical BlockCourtBenchmark. Placeholder calibration is walk `260`, held run `520`, jump velocity `520`, camera distance `420`, pitch `-65°` to `65°`, and yaw `-180°` to `180°`.
- **Measured proof:** the packaged QA moved from `Z=118.15` to a blocking-floor landing at `Z=98.15`, reached walk/run peaks of `260/520`, rose `118` units, landed with floor collision, changed camera yaw by `180°`, and returned to walk speed. One unobstructed window showed exactly one primitive avatar from the trailing camera against the existing benchmark.
- **Safety boundary:** Phase 1B.2 remains session-local and unchanged. No preset transfer, save/reload, clothing component, skeletal asset, rig, animation, combat, crouch, parkour, vehicle, flight, swimming, ability, final art, city, NPC, multiplayer, economy, wagering, backend, deployment, model, or retraining behavior was added.
- **Validation:** final editor/game builds, 3/3 native character tests, and a 49-file Windows package passed. After sleep/resume, the owner reported no popup was visible and a bounded visual check confirmed the game window was unobstructed; no security setting was changed, no remote connection or UDP endpoint and no remaining related process were observed. All 65 frozen regressions, Brain Admin self-check, and Python compilation passed. Controller routes are automation-tested; physical controller hardware was not tested. Cost was `$0.00`. See [[Development/Reports/Phase 1B3 Controllable Placeholder Avatar and Approved Locomotion]].
- **Next gate:** Phase 1B.4 renders the worn off-white starter top and bottom as separate replaceable equipment on the placeholder, without final art or persistence.

### Phase 1B.4 Replaceable Starter Outfit status

- **Status:** Complete on `agent/phase-0d`; smallest local two-slot clothing proof only.
- **Implementation:** the validated preset catalog supplies the exact `starter_offwhite_top` and `starter_offwhite_bottom` IDs. A minimal local state enforces `Top` and `Bottom`, rejects unknown, wrong-slot, duplicate, empty-removal, and incomplete states, and independently removes/restores either slot. Two separately named, noncolliding native cube components render the visibly off-white placeholders over the unchanged primitive body/head.
- **Measured proof:** packaged QA removed the top while the bottom and base remained, restored the exact top, and passed with distinct `StarterOutfitTop`/`StarterOutfitBottom` identities. One unobstructed window showed exactly one noncanonical avatar with separate off-white upper/lower pieces in BlockCourtBenchmark. Locomotion remained walk/run `260/520`, jump `520`, with the measured run reaching a `118`-unit jump, blocking-floor landing, and `180°` yaw change.
- **Safety boundary:** Phase 1B.2 remains session-local and unconnected. No save/reload, inventory, ownership, pricing, store, economy, wagering, account, backend, multiplayer, city, NPC, apartment, final art, fabric, skeletal asset, rig, animation, model, retraining, service, or deployment behavior was added.
- **Validation:** final editor/game builds, 4/4 native character tests, and a fresh 49-file Windows package passed. The owner canceled the initial Windows Firewall prompt; automation changed no security setting, and the accepted rerun was unobstructed with clean exit, no remote/UDP endpoint, and zero remaining related process. All 65 frozen regressions, Brain Admin self-check, Python compilation, documentation, canvas, and hygiene checks passed. Cost was `$0.00`. See [[Development/Reports/Phase 1B4 Replaceable Starter Outfit]].
- **Next gate:** Phase 1B.5 locally saves and reloads the chosen preset plus equipped starter outfit before any multiplayer persistence.

### Phase 1B.5 Local Character Appearance Persistence and First-Playable Handoff status

- **Status:** Complete on `agent/phase-0d`; smallest native local appearance record and first-playable handoff only.
- **Implementation:** one `USaveGame` schema v1 stores only preset, top, and bottom IDs. Valid selection saves before confirmation and travels into the existing BlockCourtBenchmark locomotion proof. The pawn loads the record all-or-nothing, applies the catalog skin tone to the separate neutral body/head, and equips the exact stored starter top/bottom. Missing or rejected data uses the first validated complete preset without rewriting the record.
- **Packaged proof:** Process A selected and saved non-default `feminine_tone_2`, entered the benchmark, visibly applied skin `D2A078FF` plus both off-white components, passed outfit/locomotion QA, and closed with the QA save present. A second cold process produced no selection or save-write record, loaded the exact same appearance with `source=loaded`, passed both QA paths, deleted the QA slot, verified absence, and exited cleanly. Bounded samples returned no TCP or UDP endpoint rows.
- **Corrective evidence:** the first handoff exposed a UE 5.8 ensure from binding digital W/A/S/D through `BindAxisKey`. That run was rejected. Keyboard movement now uses native key polling; only verified `Axis1D` mouse/controller keys use axis binding. All corrected build, automation, package, and runtime evidence was regenerated with zero ensure matches.
- **Validation:** corrected editor/game builds, 5/5 native character tests, and a fresh 58-file Windows package passed. All 65 frozen regressions passed in `132.457s`; Brain Admin self-check, Python compilation, documentation, canvas, hashes, and hygiene checks passed. The owner canceled the initial Windows Firewall prompt; automation changed no security setting. Cost was `$0.00`. See [[Development/Reports/Phase 1B5 Local Character Appearance Persistence and First-Playable Handoff]].
- **Boundary:** no persistence framework, JSON/database/registry/cloud/account/backend/network/multiplayer/profile UI, other saved state, schema migration machinery, new clothing, final art, rig, animation, city canon, economy, wagering, Phase 0, replay, model, retraining, paid service, or deployment was added.
- **Next gate:** the Phase 1B exit review, now complete in [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].

### Phase 1B Exit Review status

- **Status:** Complete on `agent/phase-0d`; Phase 1B character onboarding evidence is closed.
- **Decision:** the committed Phase 1B.1–1B.5 path proves eight gameplay-identical presets, safe-default selection, direct packaged-world handoff, approved third-person movement, separate replaceable starter clothing, schema-v1 local appearance persistence, all-or-nothing fallback, exact non-default cold-process recovery, and no demographic gameplay effect.
- **Accepted evidence:** contiguous commits `8fe374e` through `bada971`; corrected editor/game builds; 5/5 native character tests; fresh 58-file package; exact Process A/Process B recovery and QA cleanup; 65/65 frozen regressions; Brain Admin self-check; Python compilation; frozen hashes; Obsidian/Canvas/hygiene checks; and `$0.00` cost. This documentation-only review did not rebuild or relaunch Unreal.
- **Boundary:** no runtime, source, map, config, save, gameplay, art, city, backend, multiplayer, economy, wagering, paid service, deployment, model, training, retraining, Phase 0, or replay behavior changed. See [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].
- **Closed by later evidence:** the owner selected Concept B — Daymark / Sundale, and Phase 1C.1 froze its minimal art-direction sheet and compact commons-ring walking loop. Sundale remains a working name.

### Phase 1C.0 Noncanonical First City Concept Packages status

- **Status:** Complete on `agent/phase-0d`; planning and owner-comparison artifacts only.
- **Owner direction captured:** the beta first city should feel modern-day and distinctive without being plain, futuristic, luxurious, or highly fantastical. More elaborate later-city ideas, including water-focused and Tartaria-inspired directions, remain parked after the beta first city.
- **Packages:** Mainline/Rookwell uses a flat brick-and-steel renewal loop; Daymark/Sundale uses a flat sunlit commons ring; Northreach/Alderpoint uses two green accessible terraces. Each package covers a proposed name, theme, required-location loop, skyline/architecture, palette, lighting, materials, wayfinding, music handoff, strengths, and risks.
- **Visual evidence:** three project-local concept images plus [[Visual Maps/First City Concepts|a clean comparison canvas]] and [[Design/First City Concept Packages|the complete package document]]. The images are concepts only, not production-ready or license-approved assets.
- **Owner selection:** Concept B — Daymark / Sundale is the canonical beta first-city direction under [[Design/Decisions/DEC-008 Beta First City Direction]]. The working name may still change without reopening the selected theme, geography, atmosphere, or visual language.
- **Boundary:** the selection changes planning authority only. No Unreal map, source, configuration, runtime, graybox, production art, 3D asset, multiplayer, apartment, Odds Bucks, wagering, brain, deployment, or retraining behavior changed. See [[Development/Reports/Phase 1C0 Noncanonical First City Concept Packages]].
- **Closed by Phase 1C.1:** the minimal Sundale art-direction sheet and measurable compact commons-ring walking loop are frozen in [[Design/Sundale Art Direction and Core Loop]].

### Phase 1C.1 Sundale Art Direction and Core Loop Freeze status

- **Status:** Complete on `agent/phase-0d`; canonical planning freeze only.
- **Art direction:** [[Design/Sundale Art Direction and Core Loop]] freezes the selected warm civic-commons identity, three-to-six-story human-scale massing, north arena landmark, limestone/terracotta/sage/cobalt palette, late-afternoon light, material family, wayfinding hierarchy, and explicit visual exclusions.
- **Layout:** the graybox ceiling is `340 m × 280 m` with a `140 m × 90 m` central commons. One continuous step-free clockwise route covers the Studio, job, clothing store, arena, attached public sportsbook frontage, court, furniture store, and return streets in exactly `800 m` of planned centerline.
- **Projection:** at the approved placeholder speeds, arithmetic estimates are approximately `5:08` walking at `260 cm/s` and `2:34` running at `520 cm/s`. These are unmeasured planning projections, not packaged runtime evidence.
- **Visual evidence:** [[Visual Maps/Sundale Core Loop]] presents the approved image, art constraints, ordered location loop, segment distances, footprint, and next gate without overlapping information panels.
- **Boundary:** no Unreal level, map geometry, collision, navigation, source, config, material, mesh, final art, interior, multiplayer, account, store system, inventory, Odds Bucks, wagering, deployment, model, training, or retraining behavior changed. See [[Development/Reports/Phase 1C1 Sundale Art Direction and Core Loop Freeze]].
- **Next gate:** Phase 1C.2 creates a separate primitive Sundale graybox, adds named thresholds and collision-safe continuous streets, packages it, and replaces projected traversal with measured route, visibility, collision, and performance evidence.

### Phase 1C.2 Primitive Sundale Graybox and Packaged Route Measurement status

- **Status:** Complete on `agent/phase-0d`; Phase 1C city-graybox exit evidence is closed.
- **Implementation:** a separate `SundaleGraybox` map contains `45` labeled built-in/native primitive actors: bounded ground, central commons, the exact `800 m` route, two shortcuts, required location masses, six named thresholds, a public court, simple trees, and native environment lights. The map owns the existing locomotion game mode.
- **Measured package:** walk passed in `307.074s` over `79,987.6 cm`; run passed in `155.201s` over `79,936.5 cm`. Both visited `11/11` checkpoints, returned home, stayed grounded, and retained blocking-floor collision. The first run caught a wall that touched the route; the wall was moved clear and all final evidence was rebuilt.
- **Performance:** a `600`-frame rendered Development capture averaged `8.062 ms` frame time (`9.422 ms` p95) and `7.082 ms` GPU time (`7.513 ms` p95) after warm-up. This is primitive local evidence, not a final-art target.
- **Integrity:** Map Check `0/0`; native character tests `5/5`; frozen regressions `65/65`; Brain Admin self-check; Python compilation; hashes; Obsidian/Canvas; and repository hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].
- **Boundary:** no final asset, interior, multiplayer, backend, account, store catalog, item ownership, apartment system, Odds Bucks, wager, deployment, model, training, or retraining behavior was added.
- **Next gate:** Phase 1D shared-city presence. Before implementation, freeze the smallest local two-client proof defaults for provisional capacity direction, player collision, visible names, and the no-external-hosting boundary.

### Phase 1D.1 Local Two-Client Shared City Presence status

- **Status:** Complete on `agent/phase-0d`; smallest local listen-server presence proof only.
- **Owner direction:** [[Design/Decisions/DEC-010 Phase 1D Shared City Defaults]] freezes two local clients first, `$0.00`, no external service, players passing through one another, temporary visible proof labels, reconnect before capacity measurement, and blocking/reporting before external beta access.
- **Implementation:** the existing native placeholder character explicitly replicates movement and one server-assigned temporary player number. A built-in text component displays `Player 1` / `Player 2`; player capsules ignore only the Pawn channel; and two networked spawns begin `200 cm` apart. The existing Unreal character movement, camera, city map, and local appearance record remain otherwise unchanged.
- **Packaged proof:** one hidden local listen server bound only to `127.0.0.1:7787`; one joining local client was welcomed into `SundaleGraybox`. Both processes observed two labeled players. The joining client moved through normal character input, and the server measured `300.2 cm` of authoritative movement. Both processes exited `0` without manual termination.
- **Validation:** final editor/game builds passed; native character automation passed `5/5`; Windows BuildCookRun passed in `53.07s`; the archive contains `53` files totaling `1,041,716,034` bytes; all `65/65` frozen regressions passed in `159.452s`; Brain Admin self-check and Python compilation passed; server/client/native logs contain zero fatal or ensure matches. Cost was `$0.00`. See [[Development/Reports/Phase 1D1 Local Two-Client Shared City Presence]].
- **Boundary:** this does not prove synchronized appearance/clothing, reconnect, capacity, accounts, matchmaking, invitations, friends, chat, voice, moderation, blocking/reporting, external hosting, deployment, ownership transfer, economy, wagering, final art, or production multiplayer readiness.
- **Next gate:** Phase 1D.2 synchronizes the selected placeholder appearance and equipped starter top/bottom between the same two local clients. Reconnect remains Phase 1D.3.

## Future shared simulation layer

Athlete Life Brain v4 is the default for newly generated train, rest, recover, and socialize decisions. It adds only one bounded, one-decision, same-season recent-scoring response above v3's routine behavior. V1-v4 history remains immutable. Expand into longer memory, traits, relationships, nightlife, media, discipline, career decisions, and other sports only after each smaller input passes its own engineering evaluation.

Athletes keep distinct career identities: stars, specialists, average players, and below-average players are allowed and should not be automatically equalized. Durable ability changes gradually, while temporary form, fatigue, availability, practice, discipline, partying, fictional legal trouble, and other life consequences can alter performance and career outcomes through visible causal chains. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

The shared life, world, memory, and learning layers will support every sport. Each new sport receives its own AI decision brain and authoritative rules engine. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

## Next unresolved decisions

- Final character art and post-start customization after the approved Phase 1B placeholder direction.
- Final lock or replacement of the working city name “Sundale”; the selected Concept B direction is already canonical.
- First two team identities.
- Minimal athlete attributes.
- Initial live LLM provider/model and separate inference budget.
- First retraining dataset and method that fit the $5 ceiling.
- AI evaluation criteria and model-update cadence.
- Ranked competition scoring.
- 82-game schedule variety, team count, calendar, and presentation cadence.
