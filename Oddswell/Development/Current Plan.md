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

### Phase 1D.2 Replicated Appearance and Starter Clothing status

- **Status:** Complete on `agent/phase-0d`; smallest server-validated visible-state synchronization proof only.
- **Implementation:** one replicated character tuple carries the selected preset, starter top, starter bottom, and an owner-submitted proof bit. Owners resolve the approved local appearance; the server validates the tuple against the same catalog rules and republishes it. Every viewer renders that authoritative tuple instead of reading its own local save for remote players.
- **Packaged proof:** Player 1 selected `masculine_tone_3`; Player 2 selected `feminine_tone_4`. Both packaged processes independently reported the same two presets and the same off-white starter top/bottom, while the server measured `305.0 cm` of replicated movement. Both exited `0` without forced termination.
- **Corrective evidence:** two preliminary comparisons were rejected—first because a deterministic fallback could be logged before owner submission, then because listen-host possession preceded material initialization. The final gate requires both accepted owner records, and host submission now occurs after initialization.
- **Validation:** fresh BuildCookRun passed in `53.91s`; native character automation passed `5/5`; all `65/65` frozen regressions passed in `150.162s`; Brain Admin self-check, Python compilation, diff hygiene, accepted-log checks, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1D2 Replicated Appearance and Starter Clothing]].
- **Boundary:** no reconnect, capacity, account, external hosting, matchmaking, chat, moderation, item ownership, trading, store, Odds Bucks, wagering, final art, model, training, or retraining behavior was added.
- **Next gate:** Phase 1D.3 proves leave/reconnect restores the same server-visible preset and starter clothing before any capacity ladder.

### Phase 1D.3 Cold Reconnect Visible-State Restore status

- **Status:** Complete on `agent/phase-0d`; smallest local cold-process reconnect proof only.
- **Implementation:** an opt-in QA harness reuses the existing local appearance SaveGame and Phase 1D.2 server validation. The server captures the first remote player's accepted preset/top/bottom tuple, observes the leave, and passes only when a later joining pawn submits the identical owner-approved tuple. No new persistence format or service exists.
- **Packaged proof:** Player 2 joined with `feminine_tone_4`, seeded the bounded QA save, moved `305.7 cm`, and left. A new packaged process joined the same server as temporary Player 3, loaded `feminine_tone_4` plus the exact starter top/bottom with `source=loaded`, matched the server baseline, verified both clients' visible agreement, cleaned the QA save, and closed. Server and both clients exited `0`.
- **Corrective evidence:** the first successful reconnect sequence was rejected because the prior movement-pass line repeated while the server waited. The final guard produces exactly one movement pass, one reconnect leave capture, and one reconnect pass.
- **Validation:** fresh BuildCookRun passed in `60.68s`; native character automation passed `5/5`; all `65/65` frozen regressions passed in `137.551s`; Brain Admin self-check, Python compilation, accepted-log checks, diff hygiene, QA-save cleanup, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1D3 Cold Reconnect Visible State Restore]].
- **Boundary:** no permanent identity, account, server profile, external hosting, matchmaking, chat, moderation, capacity conclusion, item ownership, trading, store, Odds Bucks, wagering, final art, model, training, or retraining behavior was added.
- **Next gate:** Phase 1D.4 measures a small local concurrency ladder before any beta instance ceiling is selected.

### Phase 1D.4 Local Concurrency Ladder status

- **Status:** Complete on `agent/phase-0d`; Phase 1D local-prototype exit evidence is closed.
- **Implementation:** the existing shared-city QA accepts an opt-in, clamped `2–4` target. Every packaged client reports the complete named, valid, owner-submitted visible set; the listen server passes only after every remote player moves at least `300 cm` from the full-rung start. No load-test framework or service was added.
- **Packaged proof:** the same fresh package passed `2`, `3`, and `4` total-client rungs. Remote movers were `1/1`, `2/2`, and `3/3`; minimum server distances were `302.7`, `301.3`, and `300.5 cm`. All processes exited `0`. Peak combined launcher/game working set was `685.6`, `1,030.1`, and `1,373.9 MB`; these are NullRHI localhost samples, not a beta ceiling.
- **Validation:** editor/game builds and BuildCookRun passed; native character automation passed `5/5`; all `65/65` frozen regressions passed in `138.007s`; Brain Admin self-check, Python compilation, accepted-log audit, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1D4 Local Concurrency Ladder]].
- **Boundary:** no capacity ceiling, external hosting, account, matchmaking, communication, moderation, apartment, item ownership, economy, wagering, final art, deployment, model, training, or retraining system was added or claimed.
- **Owner direction:** [[Design/Decisions/DEC-011 Empty Starter Studio]] locks a completely unfurnished, undecorated starting Studio. Only the structural shell, entry/exit, necessary lighting, and collision may be present before the player buys furnishings in later authorized phases.
- **Owner direction:** [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]] locks private interiors, no other-player apartment visits in beta, and predefined snap points only after a legitimate furniture purchase and ownership record.
- **Next gate:** completed as Phase 1E.1; the private empty Studio now has a packaged enter/walk/exit proof.

### Phase 1E.1 Private Empty Studio Enter and Exit status

- **Status:** Complete on `agent/phase-0d`; smallest reversible empty-interior proof only.
- **Implementation:** an explicit native Studio game mode reuses the existing Bootstrap map and creates only six built-in structural surfaces plus necessary light. A standalone player near the Sundale Studio threshold can press `E` to enter; inside, `E` returns to Sundale after a release-to-arm guard.
- **Packaged proof:** the avatar entered the private Studio, verified `structure=6`, `furniture=0`, `decorations=0`, and `snap_points=0`, walked `200.0 cm`, exited, returned to Sundale, and closed with exit code `0` in `5.50s`.
- **Validation:** editor and game builds passed; native character automation passed `5/5`; two-map BuildCookRun passed in `64.89s`; all `65/65` frozen regressions passed in `133.495s`; Brain Admin self-check, Python compilation, accepted-log audit, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1E1 Private Empty Studio Enter and Exit]].
- **Boundary:** no ownership/return persistence, multiplayer-session handoff, larger interior, furniture, decoration, active snap point, inventory, catalog, Odds Bucks, purchase, price, visit, trading, final art, hosting, or deployment was added.
- **Post-completion correction:** the owner's packaged walkthrough exposed a zero-width yaw clamp caused by explicit `-180°`/`180°` limits. Those overrides are removed; editor and packaged Studio runs each proved a continuous `370.0°` orbit with `0.0 cm` player drift. Native tests passed `5/5`, frozen regressions passed `65/65`, and Admin/Python/log/hygiene checks passed. See [[Development/Reports/Phase 1E1a Continuous Mouse Camera Orbit Correction]].
- **Next gate:** Phase 1E.2 adds the smallest durable Studio ownership and return-location record without adding furniture or economy behavior.

### Phase 1E.2 Studio Ownership and Return Persistence status

- **Outcome:** complete and committed locally after final validation. The first valid Studio entry grants the default Studio, saves the exact Sundale doorway position, and restores that position after Studio exit and a cold process restart.
- **Implementation:** one native schema-v1 Unreal `SaveGame` record contains only an owned-Studio flag and Sundale return vector. Invalid type, schema, ownership, or coordinates are rejected. Save/load failure blocks the transition rather than risking an unowned or lost return.
- **Packaged proof:** a fresh two-map package entered the still-empty Studio and returned with `0.0 cm` error. A separate cold packaged process restored the same record and position with `0.0 cm` error, then deleted the isolated QA save.
- **Validation:** editor/game builds and clean BuildCookRun passed in `111.07s`; native character automation passed `6/6`; all `65/65` frozen regressions passed in `132.3s`; Brain Admin self-check, Python compilation, accepted-log audit, QA cleanup, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1E2 Studio Ownership and Return Persistence]].
- **Boundary:** no account, backend, multiplayer interior handoff, visit, larger interior, furniture, decoration, active snap point, inventory, catalog, Odds Bucks, purchase, trade, final art, hosting, or deployment was added.
- **Next gate:** Phase 1E.3 represents the six locked housing tiers as truthful data while keeping only the Studio available.

### Phase 1E.3 Six-Tier Housing Progression Catalog status

- **Outcome:** complete and committed locally after final validation. One ordered catalog now contains exactly Studio, One-bedroom, Two-bedroom, Three-bedroom, Four-bedroom, and Penthouse.
- **Truth boundary:** only Studio is marked available. Every larger tier is explicitly locked and unbuilt; no price, dimensions, layout, requirement, or upgrade action was invented.
- **Packaged proof:** the runtime reported `tiers=6`, `available=studio`, all five approved larger IDs as locked, `larger_interiors=false`, and `upgrade_ui=false`; the existing room remained six structural surfaces with zero furniture, decorations, or snap points.
- **Validation:** editor/game builds and clean BuildCookRun passed in `138.80s`; native character automation passed `7/7`; the final reordered full regression run passed `65/65` in `296.515s`; Brain Admin self-check, Python compilation, accepted-log audit, diff hygiene, and zero-process cleanup passed. The unchanged time-sensitive regression was evaluated first after normal-order machine load caused two timing-only misses; no frozen code or threshold changed. Cost was `$0.00`. See [[Development/Reports/Phase 1E3 Six-Tier Housing Progression Catalog]].
- **Boundary:** no upgrade screen, price, Odds Bucks, purchase, larger interior, furniture, inventory, account, visit, trade, final art, hosting, or deployment was added.
- **Next gate:** Phase 1E.4 shows the six tiers as clear locked upgrade goals while keeping only Studio available.

### Phase 1E.4 Player-Visible Locked Housing Goals status

- **Outcome:** complete and committed locally after final validation. The owned Studio now shows one text-based Home Progression overlay: Studio is `OWNED / AVAILABLE`; the five larger approved tiers are `LOCKED / INTERIOR NOT BUILT`; prices and requirements are explicitly not set.
- **Implementation:** the validated catalog builds the text and the existing Unreal keyed-message path displays it only after local Studio ownership loads. Status is written in text rather than conveyed by color alone. No widget framework or speculative upgrade logic was added.
- **Packaged proof:** the runtime reported `player_visible=true`, `studio=owned_available`, `locked=5`, `unbuilt=5`, `prices=false`, `requirements=false`, and `text_statuses=true`. The same run preserved the empty room and exact return; a second cold process restored ownership/location and removed the QA save.
- **Validation:** editor/game builds and clean BuildCookRun passed in `101.79s`; native character automation passed `7/7`; all `65/65` frozen regressions passed in `132.470s`; Brain Admin self-check, Python compilation, accepted-log audit, QA cleanup, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1E4 Player-Visible Locked Housing Goals]].
- **Boundary:** no final housing menu, price, requirement, upgrade action, Odds Bucks, purchase, larger interior, furniture, placement point, inventory, visit, account, trade, modern art, hosting, or deployment was added.
- **Dependency handoff:** Phase 1E's standalone foundation is complete. Furniture activation waits for Phase 1I's legitimate purchase and ownership path.
- **Closed by Phase 1F.1:** existing public teams, athletes, schedule, standings, availability, and history now appear in the player client.

### Phase 1F.1 Player League View status

- **Status:** Complete on `agent/phase-0d`; smallest read-only player-client league slice only.
- **Implementation:** one deterministic exporter reuses the existing Brain Admin public-only league payload and stages it as `oddswell-public-league-v1`. Unreal validates that frozen snapshot and exposes seven pages: standings, both six-athlete rosters with final availability, and four five-game schedule/history pages covering all 20 completed games. `L` toggles the view; `,` and `.` change pages.
- **Truth boundary:** the player client reads a build-time public snapshot. It does not run or resimulate basketball, mutate league state, expose seeds/hidden fatigue/recovery/RNG data, or claim live backend synchronization.
- **Packaged evidence:** the accepted Windows package reported `2` teams, `12` athletes, `2` standings rows, `20` completed games, `1` unavailable athlete, and `7` readable pages. Rendered Page 7 showed Games 16-20, scores, winners, and replay-seal prefixes over Sundale. The first archive attempt omitted the required cooked containers and was rejected; only the corrected `-pak -iostore` archive is accepted.
- **Validation:** editor/game builds passed; native character automation passed `8/8`; BuildCookRun passed in `50.25s`; all `65/65` frozen regressions passed in `135.279s`; Brain Admin self-check, exporter determinism, Python compilation, log audit, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1F1 Player League View]].
- **Next gate:** Phase 1F.2 grayboxes the stadium and its physical public viewing location. Wager interaction, odds, settlement, match-presentation choices, and the 82-game/two-team owner gate remain inactive.

### Phase 1F.2 Stadium and Public Viewing Graybox status

- **Status:** Complete on `agent/phase-0d`; smallest reversible stadium and public-viewing shell only.
- **Implementation:** a URL-selected native stadium game mode reuses `Bootstrap` and creates eight built-in primitive structural surfaces plus five labeled zones: entry/concourse, court floor, public viewing, future match presentation, and exit. At Sundale's existing Arena threshold, `E` enters the venue; inside, `E` returns to the exact safe city position recorded on entry.
- **Packaged proof:** the final 55-file Windows package entered from the Arena, traversed all five zones, reached the reserved presentation marker, exited, and restored Sundale with `0.0 cm` horizontal error. The visual run captured the future match-presentation wall from inside the venue. The public league overlay remains available.
- **Corrective evidence:** rejected runs exposed a `42.1 cm` collision adjustment where the city marker lies on a blocking line. The accepted implementation records the player's actual walkable entry position instead of pretending the marker center is a safe spawn.
- **Validation:** final editor/game builds and BuildCookRun passed; native character automation passed `9/9`; all `65/65` frozen regressions passed in `129.803s`; Brain Admin self-check, deterministic league export, Python compilation, packaged log audit, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1F2 Stadium and Public Viewing Graybox]].
- **Boundary:** no replay is shown in the stadium yet. No wager interaction, odds, settlement, simulator, resimulation, crowd, commentary, team branding, final art, backend, service, purchase, or deployment behavior was added.
- **Next gate:** Phase 1F.3 directly consumes one already verified archived replay inside the stadium without resimulating basketball. Presentation duration, cameras, commentary, skip rules, and the 82-game/two-team variety decision remain later owner gates.

### Phase 1F.3 Direct Archived Replay Consumption in Stadium status

- **Status:** Complete on `agent/phase-0d`; smallest direct stadium-consumption slice only.
- **Implementation:** the stadium game mode spawns one compact instance of the already validated `AReplayBenchmarkActor` on the primitive court. The renderer, fixture parser, hash locks, 421-frame event sequence, symbolic markers, and final-seal behavior are reused unchanged. No second replay system was created.
- **Packaged proof:** a fresh Windows package entered the stadium from Sundale, consumed all `421` archived frames, finished Harbor City `101` to Mesa Vista `104`, reproduced canonical trace SHA-256 `12fb61d032a93e667451c364f77907e68e53b934c46f765b6f32eefe9316dbbe`, exited, and restored the city position with `0.0 cm` error. The packaged replay fixture remained byte-identical to the tracked `256,442`-byte source.
- **Visual proof:** midpoint and final `1280x720` captures show the symbolic replay on the stadium court with public score/clock/event text; the final capture displays the exact authoritative replay seal. This is consumption evidence, not the final presentation.
- **Validation:** final editor/game builds and BuildCookRun passed; native character automation passed `9/9`; all `65/65` frozen regressions passed in `153.004s`; Brain Admin self-check, replay and league exporters, Python compilation, hash checks, packaged log audit, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1F3 Direct Archived Replay Consumption in Stadium]].
- **Boundary:** no resimulation, new replay data, presentation-duration decision, camera system, commentary, skip/condensed mode, crowd, team branding, final art, wager interaction, odds, settlement, backend, service, purchase, or deployment behavior was added.
- **Follow-up:** the owner accepted those defaults in [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]], and Phase 1F.4 is complete below.

### Phase 1F.4 Readable Three-Minute Stadium Presentation status

- **Status:** Complete on `agent/phase-0d`; the owner-approved current-beta presentation defaults are implemented and verified.
- **Implementation:** the existing archived-replay actor now uses a closer fixed broadcast camera, larger symbolic athletes and labels, a default `180 / 421`-second cadence, and explicit text evidence for score, clock, event, actor, target, regulation/overtime status, voice-off state, and final seal. The existing fixture parser and renderer remain the only replay path.
- **Rendered packaged proof:** the accepted Windows package displayed all `421` frames over `180.016s` wall time, ended Harbor City `101` to Mesa Vista `104`, reproduced canonical trace SHA-256 `12fb61d032a93e667451c364f77907e68e53b934c46f765b6f32eefe9316dbbe`, and showed the exact replay seal with zero replay errors.
- **Validation:** final UE editor/game build and BuildCookRun passed; native automation passed `10/10`; all `65/65` frozen regressions passed in `166.190s`; Brain Admin self-check, deterministic exporters, Python compilation, visual inspection, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1F4 Readable Three Minute Stadium Presentation]] and [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]].
- **Boundary:** no skip, late-arrival/reconnect reconstruction, voice commentary, camera cuts, crowd, final art, wager interaction, odds, settlement, backend, hosting, purchase, deployment, model, training, or retraining behavior was added.
- **Follow-up:** Phase 1F.5 completed that result-invariance proof below and enabled the player `S` skip control.

### Phase 1F.5 Replay-View Result Invariance status

- **Status:** Complete on `agent/phase-0d`; Phase 1F exits for the current archived-game slice.
- **Implementation:** the existing replay actor resolves `watch`, QA `skip`, `late`, and seal-validated `reconnect` to bounded public frame cursors. The player can press `S` during a full watch to invoke the same skip-to-final function. Forged seals, invalid cursors, unknown modes, and invalid QA skip requests fail closed.
- **Packaged proof:** full watch rendered `421` frames, direct skip `1`, late arrival `211`, cold reconnect `211`, and mid-watch player skip `212`. Every accepted path ended at frame `421`, Harbor City `101` to Mesa Vista `104`, the exact replay seal, and `resimulated=false`; a forged reconnect rendered `0` frames.
- **Validation:** final UE editor/game build and BuildCookRun passed; native automation passed `10/10`; all `65/65` frozen regressions passed in `163.106s`; Brain Admin self-check, deterministic exporters, Python compilation, offscreen visual inspection, fail-closed boundary checks, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1F5 Replay View Result Invariance]].
- **Boundary:** no backend/session reconnect, account, cursor-delivery service, wager, odds, settlement, Odds Bucks, job, purchase, hosting, final art, model, training, or retraining behavior was added.
- **Closed by Phase 1G.1:** the empty append-only, idempotent virtual Odds Bucks ledger is complete below. Job fantasy and all balance/payout/cadence/price/limit amounts remain owner gates.

### Phase 1G.1 Empty Server-Authoritative Odds Bucks Ledger status

- **Status:** Complete on `agent/phase-0d`; smallest empty authority only.
- **Implementation:** one append-only in-memory ledger is owned by Sundale's existing server-only Unreal `GameMode`. Exact command retries are idempotent; conflicting command reuse, invalid inputs, overflow, and overspend fail without appending.
- **Packaged proof:** the final 53-file Windows package started the Sundale authority at exactly `0` entries and `0` balance with client commands, real money, and wagering disabled.
- **Validation:** editor/game builds and BuildCookRun passed; focused automation passed `1/1`; full native automation passed `11/11`; all `65/65` frozen regressions passed in `121.038s`; Brain Admin self-check, deterministic exporters, Python compilation, runtime-log audit, diff hygiene, and process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1G1 Empty Server Authoritative Odds Bucks Ledger]].
- **Boundary:** no player/account identity, persistence, restart/reconnect restore, job, earning, starting balance, payout, allowance, recovery floor, price, purchase, wager, settlement, Admin ledger, deployment, real-money connection, or second currency was added.
- **Closed by Phase 1G.2:** the owner-approved server-validated placeholder shift is complete below; payout and recovery rules remain owner gates.

### Phase 1G.2 Server-Validated Placeholder Job Interaction status

- **Status:** Complete on `agent/phase-0d`; interaction-only slice with no payout.
- **Implementation:** the existing Sundale `Job` route marker shows an `E` prompt. The owning server accepts completion only when its authoritative player position is within the marker radius, then sends visible success or rejection feedback to that player.
- **Packaged proof:** an outside-location request was rejected; an at-location request completed; both paths left the ledger at `0` entries and `0` balance with no command and no payout rules.
- **Validation:** editor/game builds and final BuildCookRun passed in `58.11s`; focused automation passed `1/1`; full native automation passed `11/11`; all `65/65` frozen regressions passed in `119.209s`; Brain Admin self-check, deterministic exporters, Python compilation, runtime-log audit, diff hygiene, and process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1G2 Server Validated Placeholder Job Interaction]].
- **Boundary:** no durable job history, payout, command ID, account, persistence, restart/reconnect restore, eligibility, cooldown, cadence, allowance, recovery floor, starting balance, price, purchase, wager, settlement, final job fiction, animation, final art, deployment, real-money connection, or second currency was added.
- **Next owner gate:** Phase 1G.3 needs a provisional payout and limit. Smallest recommendation: `100` Odds Bucks once per local saved profile for one idempotent credit-and-cold-restore proof; repeat and daily recovery remain disabled until Phase 1G.4.

### Phase 1G.3 Persistent First Job Payout status

- **Status:** Complete on `agent/phase-0d`; owner-approved provisional local-profile slice only.
- **Implementation:** the server issues one stable `+100` Odds Bucks command after the existing validated shift. Unreal SaveGame persists the validated append-only entries, and the candidate is saved before the authoritative in-memory ledger changes. Exact retries remain duplicates.
- **Packaged proof:** process one rejected an outside request, applied one `+100` credit, and kept a same-process retry at `1` entry and balance `100`. Process two restored exactly `1` entry and balance `100`, kept the post-restart retry unchanged, and removed the isolated QA save.
- **Validation:** editor/game builds and the final `48.65s` BuildCookRun passed; focused persistence automation passed `1/1`; full native automation passed `11/11`; all `65/65` frozen regressions passed in `141.263s`; Brain Admin self-check, deterministic exporters, Python compilation, runtime-log audit, and QA-save cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1G3 Persistent First Job Payout]] and [[Design/Decisions/DEC-014 Phase 1G3 Provisional First Job Payout]].
- **Boundary:** local saved profile only. No online account/backend reconnect, repeat income, daily allowance, recovery floor, starting balance, price, purchase, wager, settlement, Admin reconciliation, deployment, real-money connection, or second currency was added.
- **Closed by Phase 1G.4:** the owner-approved rolling local recovery defaults are complete below.

### Phase 1G.4 Rolling 24-Hour Job Recovery status

- **Status:** Complete on `agent/phase-0d`; owner-approved local-profile beta slice.
- **Defaults:** start at `0` Odds Bucks; earn `100` from a validated shift; become eligible again after a rolling `24` hours; count the first payout as period one; accumulate balances; provide no separate allowance or missed-period catch-up.
- **Implementation:** the authoritative GameMode saves one next-eligible UTC timestamp beside the validated append-only ledger. An eligible shift creates one idempotent scheduled command, saves the candidate ledger and new timestamp before changing live state, and schedules the next opportunity from the accepted time. Existing schema-v1 saves migrate without fabricating a second payout.
- **Packaged proof:** process one rejected an outside request, credited the first `100`, blocked an immediate retry, advanced the isolated QA clock by `86,400` seconds, credited the second `100`, and remained at `2` entries/balance `200` on another immediate retry. Process two restored those exact values from disk, proved the cooldown still blocked one second before eligibility, then credited a third `100` at eligibility for `3` entries/balance `300` and removed the isolated QA save.
- **Validation:** editor compilation passed in `11.30s`, game compilation in `18.37s`, and clean BuildCookRun in `102.16s`; focused ledger automation passed `1/1`; full native automation passed `11/11`; all `65/65` frozen regressions passed in `157.595s`; Brain Admin self-check, deterministic exporters, Python compilation, package/runtime evidence, diff hygiene, and QA-save cleanup passed. The Windows package contains `54` files totaling `1,042,817,855` bytes. Cost was `$0.00`. See [[Development/Reports/Phase 1G4 Rolling 24 Hour Job Recovery]] and [[Design/Decisions/DEC-015 Phase 1G4 Rolling Job Recovery Defaults]].
- **Boundary:** one machine-local saved profile using the machine UTC clock. No trusted backend clock, online account, backend reconnect, multi-device recovery, allowance, missed-period catch-up, price, purchase, wager, settlement, Admin reconciliation, deployment, real-money connection, or second currency was added.
- **Closed by Phase 1G.5:** truthful read-only ledger and next-job-eligibility reconciliation is complete below without granting commands or claiming backend/account authority.

### Phase 1G.5 Read-Only Odds Bucks Admin Reconciliation status

- **Status:** Complete on `agent/phase-0d`; current machine-local profile only. Phase 1G exits for this bounded local dependency.
- **Implementation:** Unreal validates the authoritative SaveGame ledger and atomically publishes an output-only JSON projection at startup and after each accepted job credit. Brain Admin independently rejects malformed or internally inconsistent projections, then shows the validated balance, entry count, eligibility, next eligible UTC time, and append-only entries on the Operations page. It exposes no economy mutation route or control.
- **Packaged proof:** the first QA process projected `2` entries, balance `200`, and an exact `86,400`-second cooldown. The cold second process restored those values, projected `3` entries and balance `300` at eligibility, and removed the isolated QA save and QA projection. A normal packaged launch published a valid empty-profile projection with balance `0` and the first shift available.
- **Validation:** editor compilation passed in `12.71s`, game compilation in `20.61s`, and clean BuildCookRun in `100.75s`; focused automation passed `1/1`; full native automation passed `11/11`; all `65/65` frozen regressions passed in `140.036s`; Brain Admin self-check, browser inspection, deterministic exporters, Python compilation, runtime-log audit, diff hygiene, and QA cleanup passed. The Windows package contains `56` files totaling `1,042,923,557` bytes. Cost was `$0.00`. See [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]].
- **Boundary:** this is a read-only local projection, not a source of truth, authenticated console, or anti-cheat control. No online account, trusted backend clock, cloud/multi-device recovery, economy command, price, purchase, wager, settlement, payment, deployment, real-money connection, or second currency was added.
- **Closed by Phase 1H.1:** the owner approved the Match Winner v1 rules recorded below.

### Phase 1H.0 Basketball Odds and Wager Isolation status

- **Status:** Architecture approved by the owner on 2026-07-21; design-only gate complete.
- **Decision:** keep the Basketball Brain, Basketball Rules and Outcome Engine, Basketball Odds Brain, deterministic Wager and Settlement Engine, and read-only Admin reconciliation as separate roles with one-way evidence flow. See [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]].
- **Integrity boundary:** the Odds Brain may use only one frozen public pregame snapshot. Wagers, stakes, balances, purchases, and displayed odds cannot influence athlete decisions or the sealed result. Settlement consumes that result exactly once and never resimulates basketball.
- **Implementation boundary:** no odds offer, payout formula, stake debit, wager request, lock, settlement, cancellation, correction, or wager Admin view was added. The existing public prediction evidence is not automatically promoted into betting odds.
- **Closed by Phase 1H.1:** the approved Match Winner rules are recorded below.

### Phase 1H.1 Match Winner Rules status

- **Status:** Owner approved on 2026-07-21 under [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]].
- **Rules:** `phase0d4-v1` public Elo-plus-availability/rotation source; zero house edge; `10`–`100` Odds Bucks in increments of `10`; gross whole-credit return `floor(stake/probability)` including the returned stake; lock at authoritative game start; void/refund an unsealed or canceled game; use a separate auditable correction rather than rewriting history.
- **Public boundary:** only the exact equal `oddswell-public-pregame-v1` snapshot may drive the offer. Private Athlete Life Brain choices, hidden fatigue, seeds, RNG, future results, economy data, and user data are excluded.
- **Later owner direction:** introduce points, rebounds, and fouls as separate rarity-priced player-prop gates. Public consequences may affect later odds; private choices cannot. Rebounds need durable aggregation, and fouls need an authoritative foul model.
- **Closed by Phase 1H.2:** the first versioned offer-calculation contract is complete below.

### Phase 1H.2 Versioned Match Winner Odds Offer status

- **Status:** Complete on `agent/phase-0d`; calculation contract only.
- **Implementation:** `phase1h.odds` verifies an existing public pregame commitment and emits one deterministic `basketball-match-winner-odds-v1` offer with exact integer probabilities/display odds, approved stake rules, lock time, public source versions, and SHA-256 offer identity. A separate pure calculation returns the approved whole-Odds-Bucks gross payout without touching the ledger.
- **Validation:** focused odds tests passed `3/3` in `0.054s`; all `65/65` frozen regressions passed in `139.785s`; Brain Admin self-check, unchanged replay/league exporters, Python compilation, leakage checks, tamper rejection, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H2 Versioned Match Winner Odds Offer]].
- **Boundary:** no runtime offer publication, account, trusted clock, wager request, stake reservation/debit, lock transition, cancellation/refund, settlement, payout credit, prop market, wager history, Admin wager view, Unreal UI, payment, real-money connection, or second currency was added.
- **Closed by Phase 1H.3:** the first local request and stake-debit persistence primitive is complete below.

### Phase 1H.3 Idempotent Match Winner Stake Debit status

- **Status:** Complete on `agent/phase-0d`; machine-local server-owned persistence primitive only.
- **Implementation:** one exact Phase 1H.2 offer, request command ID, offered team, whole Odds Bucks stake, accepted time, and lock time are validated before one `accepted_pending_lock` request and one linked `match_winner_stake` debit are saved together. Exact retries are idempotent; conflicting reuse and all invalid, late, tampered, or underfunded requests fail without mutation. Existing schema v1/v2 saves migrate to v3 without inventing wager history.
- **Validation:** native automation passed `11/11`, including the focused Odds Bucks path; focused odds tests passed `3/3`; all `65/65` frozen regressions passed in `144.957s`; Brain Admin self-check, unchanged exporters, Python compilation, offer-ID parity, disk reload, rejection invariants, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H3 Idempotent Match Winner Stake Debit]].
- **Boundary:** no player-facing request route, runtime offer publication, trusted backend clock, online account, lock transition, cancellation/refund, settlement, payout, correction, prop market, wager history screen, Admin wager view, Unreal UI, payment, real-money connection, or second currency was added.
- **Closed by Phase 1H.4:** the separate immutable game-start lock decision is complete below.

### Phase 1H.4 Idempotent Match Winner Game-Start Lock status

- **Status:** Complete on `agent/phase-0d`; machine-local server-owned lock primitive only.
- **Implementation:** one lock command links an existing accepted request to its exact season, game, and approved game-start timestamp in a separate immutable record. Exact retries return the same record; wrong identities/times, conflicting command reuse, a second lock, unknown requests, and malformed saved links fail without mutation. Schema v1-v3 saves migrate to v4 with zero fabricated locks.
- **Invariance:** locking adds no ledger entry and preserves the accepted offer, team, stake, accepted time, lock time, balance, and job cooldown exactly.
- **Validation:** native automation passed `11/11`, including focused economy automation `1/1`; focused odds tests passed `3/3`; all `65/65` frozen regressions passed in `143.229s`; Brain Admin self-check, unchanged exporters, Python compilation, disk reload, migration, rejection invariants, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H4 Idempotent Match Winner Game Start Lock]].
- **Boundary:** no result consumption, win/loss decision, settlement, payout, lost-stake finalization, void/refund, cancellation, correction, ledger mutation, player route/UI, Admin wager view, props, trusted clock, online account, payment, real-money connection, or second currency was added.
- **Closed by Phase 1H.5:** the exact immutable sealed-result link is complete below.

### Phase 1H.5 Immutable Sealed Match Winner Result Linkage status

- **Status:** Complete on `agent/phase-0d`; one machine-local archive-evidence link only.
- **Implementation:** one result command links the exact accepted request and game-start lock to the verified Season 1, Game 1 archive: Harbor City Waves `101`, Mesa Vista Sol `104`, winner Mesa Vista Sol, and replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`. Exact retries return the same record; unknown or unlocked requests, wrong locks, ties, tampered fields, conflicting reuse, a second link, and malformed saved evidence fail without mutation. Schema v1-v4 saves migrate to v5 with zero fabricated result links.
- **Invariance:** linking adds no ledger entry and preserves the two-entry ledger, balance `60`, job cooldown, `accepted_pending_lock` request, `locked` decision, Basketball Brain, replay, public prediction, and league outputs exactly.
- **Validation:** native automation passed `11/11`, including focused economy automation `1/1`; focused odds tests passed `3/3` in `0.052s`; all `65/65` frozen regressions passed in `143.403s`; Brain Admin self-check, unchanged `421`-frame replay with exact seal, unchanged `2`-team/`12`-athlete/`20`-game league export, Python compilation, migration, rejection invariants, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H5 Immutable Sealed Match Winner Result Linkage]].
- **Boundary:** no wager win/loss decision, settlement status, gross return, payout, lost-stake finalization, refund, void, correction, new ledger entry, player route/UI, Admin wager view, props, backend, brain change, payment, real-money connection, or second currency was added.
- **Closed by Phase 1H.6:** the exact deterministic losing decision is complete below without application or settlement.

### Phase 1H.6 Immutable Deterministic Match Winner Settlement Decision status

- **Status:** Complete on `agent/phase-0d`; one machine-local decision record for the exact archived losing selection only.
- **Implementation:** one decision command consumes the exact accepted request, game-start lock, and sealed-result link IDs, then derives Harbor City Waves selected versus Mesa Vista Sol winner as `lost`, `GrossReturnDue = 0`, status `decided_pending_apply`. Exact retries return the same record; missing or mismatched chains, conflicting command reuse, a second decision, and malformed saved decisions fail without mutation. Schema v1-v5 saves migrate to v6 with zero fabricated decisions.
- **Invariance:** deciding adds no ledger entry and preserves the two-entry ledger, balance `60`, job cooldown, accepted request, lock, result link, exact replay seal, Basketball Brain, public prediction, and league outputs.
- **Validation:** native automation passed `11/11`, including focused economy automation `1/1`; focused odds tests passed `3/3` in `0.051s`; all `65/65` frozen regressions passed in `143.773s`; Brain Admin self-check, unchanged `421`-frame replay and exact seal, unchanged `2`-team/`12`-athlete/`20`-game league export, Python compilation, migration, rejection invariants, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H6 Immutable Deterministic Match Winner Settlement Decision]].
- **Boundary:** `decided_pending_apply` is not applied, finalized, or settled. No settled status, payout, refund, void, correction, new ledger entry, balance change, player route/UI, Admin wager view, props, backend, brain change, payment, real-money connection, or second currency was added.
- **Closed by Phase 1H.7:** the exact loss now has one separate immutable finalization record below.

### Phase 1H.7 Idempotent Exact-Loss Finalization status

- **Status:** Complete on `agent/phase-0d`; one machine-local finalization record for the exact archived loss only.
- **Implementation:** one finalization command names the exact Phase 1H.6 decision, then derives its request, lock, sealed result, offer, Harbor selection, Mesa winner, stake `40`, `lost` outcome, and zero return from saved evidence. The separate record stores status `settled_lost`, gross return applied `0`, observed ledger entry count `2`, and observed balance `60`. Exact retry returns the same record; conflicting reuse, a second finalization, missing or mismatched evidence, tamper, malformed data, a nonloss decision, and a nonzero return fail without mutation. Schema v1-v6 saves migrate to v7 with zero fabricated finalizations.
- **Invariance:** finalizing adds no ledger entry, including no zero-value entry, and preserves balance `60`, job cooldown, prior request/lock/result/decision evidence, replay, public prediction, league outputs, and basketball behavior. The prior decision remains immutable as `decided_pending_apply`; finalization is a separate `settled_lost` record.
- **Validation:** native automation passed `11/11`, including focused economy automation `1/1`; focused odds tests passed `3/3` in `0.049s`; all `65/65` frozen regressions passed in `143.619s`; Brain Admin self-check, unchanged `421`-frame replay and exact seal, unchanged `2`-team/`12`-athlete/`20`-game league export, compilation, migration, rejection invariants, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H7 Idempotent Exact Loss Finalization]].
- **Boundary:** this is exact-loss finalization only, not winning-return or payout proof. No alternate wager, payout, refund, void, correction, player route/UI, wager history, Admin wager view, props, backend, brain change, payment, real-money connection, or second currency was added.
- **Closed by Phase 1H.8:** the exact finalized loss now has one independently validated read-only Operations reconciliation/history card below.

### Phase 1H.8 Read-Only Exact-Loss Reconciliation History status

- **Status:** Complete on `agent/phase-0d`; output-only machine-local Operations evidence for the exact finalized loss.
- **Implementation:** Unreal atomically publishes one separate `oddswell-match-winner-reconciliation-v1` JSON projection only from the fully validated request/debit, lock, sealed result, decision, finalization, and ledger chain. Brain Admin independently validates every exact identity and value before showing Harbor selected, Mesa won, stake `40`, return `0`, net `-40`, balance `60`, `settled_lost`, replay seal, and command linkage. Missing, malformed, tampered, or partial projections show unavailable with no partial fields.
- **Invariance:** the projection is read-only and has no controls. It adds no ledger entry, changes no balance or cooldown, does not rewrite the `decided_pending_apply` decision or separate `settled_lost` finalization, and leaves the generic Odds Bucks reconciliation v1 unchanged. No SaveGame schema bump was required.
- **Validation:** editor build, focused economy automation `1/1`, full native automation `11/11`, focused odds tests `3/3` in `0.048s`, all `68/68` Python tests in `143.296s`, Brain Admin self-check, live browser/DOM inspection, unchanged `421`-frame replay/exact seal/`256,442`-byte fixture, unchanged `2`-team/`12`-athlete/`20`-game league export, compilation, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H8 Read Only Exact Loss Reconciliation History]].
- **Boundary:** this is not player wager history and proves no winning payout, alternate wager, refund, void, correction, player route/UI, prop market, account, trusted clock, backend, deployment, payment, real-money connection, or brain change.
- **Closed by Phase 1H.9:** the existing Mesa-selected exact win now binds one immutable return-due decision below without applying it.

### Phase 1H.9 Immutable Exact-Win Settlement Decision and Return-Due Binding status

- **Status:** Complete on `agent/phase-0d`; one isolated machine-local winning decision for the exact archived offer and result.
- **Implementation:** the QA profile selects Mesa Vista Sol for stake `40`, recomputes and validates the existing offer with probability `40000000` and `floor(stake*100000000/win_probability_e8)`, consumes the exact request, game-start lock, and sealed Harbor `101`-`104` Mesa result, then persists `won`, `GrossReturnDue = 100`, and `decided_pending_apply`. The probability and payout formula are bound into the immutable decision. Exact retry is idempotent; missing/tampered offer data, mismatched chains, conflicting reuse, a second decision, and malformed saved evidence fail closed.
- **Invariance:** deciding adds no ledger entry, finalization, payout, projection, or Admin card. The isolated profile retains two ledger entries, balance `60`, and the job cooldown. The exact loss decision, finalization, reconciliation/history, replay, league, and basketball behavior remain unchanged.
- **Validation:** editor build, focused economy automation `1/1`, full native automation `11/11`, focused odds tests `3/3` in `0.073s`, all `65/65` frozen tests in `311.250s` with the unchanged time-sensitive test first and the test process verified at High priority, Brain Admin self-check, unchanged replay/league exporters, Python compilation, cold reload, migration-without-invention, tamper rejection, loss-chain restoration, and diff hygiene passed. The timing guard also passed in an isolated idle run at `117.386s`. Cost was `$0.00`. See [[Development/Reports/Phase 1H9 Immutable Exact Win Settlement Decision and Return Due Binding]].
- **Boundary:** return due `100` is not applied, credited, paid, finalized, reconciled, or exposed in player/Admin UI. No refund, void, correction, alternate wager, prop, account, trusted clock, backend, deployment, payment, real-money connection, or brain change was added.
- **Closed by Phase 1H.10:** the exact return is now applied once with a separate immutable win finalization below.

### Phase 1H.10 Idempotent Exact-Win Return Application and Finalization status

- **Status:** Complete on `agent/phase-0d`; one isolated machine-local exact-win application/finalization for the existing Mesa-selected QA chain.
- **Implementation:** a caller supplies only one finalization/application command ID and the exact Phase 1H.9 decision ID. Validated saved evidence derives the request, lock, sealed result, offer, selected probability, approved formula, stake, winner, and return. One atomic SaveGame write appends exactly one `+100` `match_winner_payout` entry and one separate immutable `settled_won` finalization. The ledger changes from `2` entries / balance `60` to `3` entries / balance `160`; the job cooldown and prior `decided_pending_apply` decision remain unchanged, with no separate stake-return entry.
- **Safety:** exact retry returns the same record without another credit. Conflicting command reuse, a second finalization, wrong or missing chain evidence, a loss, wrong probability/formula/return, malformed persistence, tamper, and an extra ledger mutation fail without rewriting state. Schema v7 loss history migrates intact, and migrations invent no win finalization.
- **Validation:** editor build, focused economy automation `1/1`, full native automation `11/11`, focused odds tests `3/3` in `0.048s`, all `65/65` frozen tests in `152.531s` with the timing-sensitive test first and the accepted Python process verified at High priority, isolated timing guard `1/1` in `59.125s`, Brain Admin self-check, exact unchanged replay/league exporters, Python compilation, cold reload, migration/loss preservation, rejection invariants, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H10 Idempotent Exact Win Return Application and Finalization]].
- **Boundary:** this is not winning reconciliation/history and exposes no player/Admin UI. No refund, void, correction, alternate wager, prop, account, trusted clock, backend, deployment, payment, real-money connection, or brain change was added.
- **Closed by Phase 1H.11:** the exact win now uses the existing read-only reconciliation/history path below, including completed live browser/DOM evidence.

### Phase 1H.11 Read-Only Exact-Win Reconciliation History status

- **Status:** COMPLETE on `agent/phase-0d`.
- **Implementation:** the existing `oddswell-match-winner-reconciliation-v1` atomic writer, endpoint, validator, and Operations card now accept either the exact loss or exact win. The win projection binds Mesa selected, stake `40`, probability `40000000`, approved formula, sealed Harbor `101`-`104` Mesa result, `won`, due/applied `100`, exact stake `2/-40/60`, exact payout `3/+100/160`, `settled_won`, count `3`, balance `160`, net `+60`, replay seal, and all command links. Finalization and validated cold load publish; stale, malformed, tampered, partial, or extra-mutated state publishes nothing.
- **Invariance:** the exact-loss projection/card remains count `2`, balance `60`, net `-40`, and `settled_lost`. No SaveGame schema, saved state, ledger command, cooldown, replay, league, or basketball behavior changed. The card remains output-only with no controls.
- **Validation:** editor build, focused economy automation `1/1`, full native automation `11/11`, focused odds tests `3/3` in `0.043s`, all `65/65` frozen tests in `148.904s` with the timing-sensitive test first and the process verified at High priority, Brain Admin exact loss/win/tamper/no-partial self-check, unchanged replay/league exporters, Python compilation, cold regeneration, stale suppression, loss invariance, and diff hygiene passed. Live browser/DOM inspection showed `VALIDATED QA FINALIZED WIN`, the exact Mesa probability/formula/result, stake and payout sequence, `3/160`, net `+60`, `settled_won`, the exact replay seal, zero controls, and no horizontal overflow. Cost was `$0.00`. See [[Development/Reports/Phase 1H11 Read Only Exact Win Reconciliation History]].
- **Boundary:** no player wager route/history UI, refund, void, correction, alternate wager, prop, account, trusted clock, backend, deployment, payment, real-money connection, or brain change was added.
- **Next candidate gate:** Scope Director review of the smallest remaining Phase 1H Match Winner evidence requirement. Void/refund, correction, and player-facing history/UI remain separate unproved gates.

### Phase 1H.12 Immutable Authoritative Canceled-Game Evidence Link status

- **Status:** COMPLETE on `agent/phase-0d`; one explicitly noncanonical machine-local QA disposition only.
- **Implementation:** a separate schema-v1 canceled-game record binds the exact accepted request and game-start lock for QA Season 99, Game 1 to one server cancellation command ID, one evidence ID, authoritative cancellation time, neutral reason `game_canceled`, and status `closed_canceled`. Exact retry is idempotent; unknown, mismatched, conflicting, malformed, already-resolved, or second dispositions fail closed. SaveGame schema v8 migrates to v9 with zero invented cancellations.
- **Invariance:** the sealed Season 1, Game 1 Harbor `101` to Mesa `104` result cannot be relabeled. Cancellation adds no ledger entry or credit, creates no settlement or finalization, publishes no Admin projection, and preserves the exact loss at `2/60` and exact win at `3/160`.
- **Validation:** editor build, focused economy automation `1/1`, full native automation `11/11`, focused odds tests `3/3` in `0.055s`, canonical Python 3.12 timing guard `1/1` in `59.431s`, all `65/65` frozen tests in `145.685s` with the timing-sensitive test first and both processes verified at High priority, Brain Admin self-check, unchanged replay/league exporters, Python compilation, cold load, migration-without-invention, tamper rejection, old loss/win preservation, and diff hygiene passed. Two Unreal Python 3.11 timing runs were rejected as wrong-interpreter evidence; no frozen code or setting changed. Cost was `$0.00`. See [[Development/Reports/Phase 1H12 Immutable Authoritative Canceled Game Evidence Link]].
- **Boundary:** this is canceled-game evidence, not a refund. No void/refund amount due, ledger restoration, application, finalization, reconciliation, Admin/player UI, generalized cancellation service, correction, later market, backend, deployment, real-money connection, or brain change was added.
- **Next candidate gate:** Scope Director review. Void/refund due, application/finalization, correction, and player-facing history/UI remain separate unproved gates.

### Phase 1H.13 Immutable Exact Canceled-Wager Void/Refund-Due Decision status

- **Status:** COMPLETE on `agent/phase-0d`; one machine-local decision for the exact noncanonical Phase 1H.12 QA cancellation only.
- **Implementation:** a caller supplies one void-decision command ID plus the exact cancellation command/evidence IDs. Validated schema-v10 state derives the request, lock, offer identity/schema/version, selected team, stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund` into one separate immutable schema-v1 record. Exact retry is idempotent; identity mismatch, conflicting reuse, a second decision, nonclosed or malformed evidence, wrong values, and any result/normal decision/finalization conflict fail closed.
- **Invariance:** the pending refund decision adds no ledger entry or credit and leaves the isolated ledger at `2/60`. It creates no finalization or projection. The canceled chain cannot enter normal result/settlement; canonical Season 1, Game 1, exact loss, and exact win evidence remain unchanged. Schema v9 migration invents no decision and preserves H12.
- **Validation:** final editor build passed in `9.92s`; focused economy automation `1/1`, full native automation `11/11`, focused odds tests `3/3` in `0.048s`, canonical Python 3.12 timing guard `1/1` in `62.332s`, and all `65/65` frozen tests in `148.282s` with the timing-sensitive test first and both processes verified at High priority. Brain Admin self-check, unchanged replay/league exporters, Python compilation, cold load, migration, tamper/nonclosed rejection, old-chain preservation, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H13 Immutable Exact Canceled Wager Void Refund Due Decision]].
- **Boundary:** refund due `40` is not applied or finalized. No ledger restoration, reconciliation, Admin/player UI, generalized void service, correction, later market, backend, deployment, payment, real-money connection, or brain change was added.
- **Next candidate gate:** Scope Director review. Exact refund application/finalization, read-only reconciliation, correction, and player-facing history/UI remain separate unproved gates.

### Phase 1H.14 Idempotent Exact Canceled-Wager Refund Application and Finalization status

- **Status:** COMPLETE on `agent/phase-0d`; one machine-local application/finalization for the exact noncanonical H12-to-H13 QA chain only.
- **Implementation:** a caller supplies one finalization/refund command ID plus the exact H13 void-decision ID. Validated schema-v11 state derives the cancellation, request, lock, offer, selection, stake `40`, `game_canceled`, `voided`, and refund due `40`. One atomic SaveGame write appends sequence `3`, `+40`, reason `match_winner_refund`, balance `100`, plus one separate immutable `settled_void` finalization that binds the full chain, ledger command, count `3`, and balance `100`.
- **Safety and invariance:** exact retry is duplicate-safe. Conflict, second finalization, tamper, malformed status, normal-outcome overlap, ledger anomaly, unexpected extra mutation, and malformed persistence fail closed without rewrite. H13 remains `decided_void_pending_refund`; canonical Game 1, old loss `2/60`, old win `3/160`, cooldown, brains, replay, prediction, and league outputs remain unchanged. Schema v10 migration invents no finalization.
- **Validation:** editor build, focused economy automation `1/1`, full native automation `11/11`, focused odds `3/3` in `0.046s`, canonical Python 3.12 timing guard `1/1` in `54.531s`, and the frozen `65/65` set inside an ordered `68/68` run in `131.613s` passed with timing first and both processes verified at High priority. Brain Admin self-check, unchanged exact replay/league exporters, Python compilation, cold load, migration, fail-closed evidence, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H14 Idempotent Exact Canceled Wager Refund Application and Finalization]].
- **Boundary:** no void reconciliation, Admin/player UI, generalized cancellation/refund service, correction/timeout policy, alternate market, props, backend, deployment, retraining, payment, real-money connection, or brain behavior was added.
- **Closed by Phase 1H.15:** the exact canceled wager now uses the existing independently validated read-only reconciliation/history path below.

### Phase 1H.15 Read-Only Exact Canceled-Wager Reconciliation History status

- **Status:** COMPLETE on `agent/phase-0d`; one QA-only machine-local Operations history for the exact noncanonical H12-to-H14 chain.
- **Implementation:** the existing reconciliation-v1 atomic writer, endpoint, validator, and single Operations card now accept one exact `voided` branch. It binds request, sequence-`2` `-40` stake to balance `60`, lock, cancellation command/evidence/time/schema/version, H13 refund-due decision, sequence-`3` `+40` refund to balance `100`, and H14 `settled_void` finalization. Brain Admin independently requires every exact value and link before showing `VALIDATED QA FINALIZED VOID`.
- **Safety and invariance:** missing, malformed, stale, partial, tampered, mixed normal-result, or invented winner/score/replay evidence fails closed without partial display. The card has no controls. No SaveGame schema, ledger command, gameplay, brain, replay, prediction, league, loss, or win behavior changed; exact loss remains `2/60/-40`, exact win `3/160/+60`, and exact void `3/100/0`.
- **Validation:** editor build, focused economy `1/1`, full native `11/11`, odds contracts `3/3`, canonical Python 3.12 timing-first frozen regression `65/65` in `145.197s`, Brain Admin self-check, live browser/API/DOM proof, unchanged replay/league exporters, Python compilation, canvas parsing, and diff hygiene passed. The browser showed zero controls and no overflow. Cost was `$0.00`. See [[Development/Reports/Phase 1H15 Read Only Exact Canceled Wager Reconciliation History]].
- **Boundary:** no player wager route/history UI, correction/timeout policy, generalized void service, alternate market, prop, backend, deployment, retraining, payment, real-money connection, or brain behavior was added.
- **Closed by Phase 1H.16:** the exact canonical offer is now visible read-only at the separate Sundale Sportsbook frontage below.

### Phase 1H.16 Player-Facing Match Winner Offer Preview status

- **Status:** COMPLETE on `agent/phase-0d`; one location-gated, read-only player preview for the exact canonical Season 1, Game 1 public offer.
- **Implementation:** the existing league exporter publishes the immutable `basketball-match-winner-odds-v1` offer beside unchanged league evidence. At the labeled Sportsbook frontage only, `E` shows both teams, probabilities `57586693`/`42413307`, display odds `1.7365x`/`2.3577x`, `10`–`100` Odds Bucks in increments of `10`, game-start lock, exact gross-return examples, offer ID, source versions, commitment, and an explicit read-only warning. Leaving the frontage closes the view.
- **Safety and invariance:** Unreal independently accepts only the exact offer/public-evidence link; stale, malformed, tampered, hidden-field, or mismatched evidence exposes no values. Packaged QA proves the action is unavailable elsewhere and ledger entries/balance remain `0/0` before and after. The prior league object is byte-equivalent after removing the one new offer field; all results, replay seals, brains, predictions, and authoritative behavior are unchanged.
- **Validation:** focused native offer automation `1/1`, full native `11/11`, odds contracts `3/3`, bundled Python 3.12 timing-first frozen regressions `65/65` in `134.983s`, Brain Admin self-check, final editor/game builds, `86.52s` BuildCookRun, deterministic exporters, packaged rendered/log proof, compilation, canvases, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H16 Player Facing Match Winner Offer Preview]].
- **Boundary:** no wager submission, request, debit, ledger/history mutation, correction, live service, new market, prop, account, backend, real money, payment, deployment, retraining, brain/model, or Admin mutation path was added.
- **Closed by Phase 1H.17:** one explicitly noncanonical upcoming QA offer now has the isolated player review-and-confirm request path below.

### Phase 1H.17 Player-Facing Upcoming QA Match Winner Request status

- **Status:** COMPLETE on `agent/phase-0d`; one machine-local upcoming QA request at the existing Sundale Sportsbook frontage only.
- **Implementation:** under the explicit QA mode, the player selects either Sundale Sparks or Red Mesa Rivals, chooses `10`–`100` Odds Bucks in increments of `10`, reviews the exact integer gross return, and confirms a second time. The server rebuilds the exact Season `100`, Game `1` QA offer and fixed pre-lock time, then reuses `AcceptOddsWellMatchWinnerRequest` to atomically persist exactly one `accepted_pending_lock` request and one linked `match_winner_stake` debit. The accepted view shows request ID, selected team, stake, and resulting balance.
- **Safety and invariance:** the existing job path funds the isolated QA profile; exact cold retry is duplicate-safe. Stale, tampered, invalid-team, invalid-stake, late, conflicting, completed-H16, and insufficient-balance requests all reject with zero mutation. No score, winner, replay, result link, hidden result, lock, simulation, settlement, refund, correction, history, generalized market, canonical calendar change, account, backend, real-money path, deployment, Admin control, retraining, or brain change was added.
- **Validation:** focused native H17 automation `1/1`, full native `12/12`, odds contracts `3/3` in `0.048s`, bundled Python 3.12 timing-first frozen regressions `65/65` in `132.613s`, Brain Admin self-check, final editor/game builds, `50.87s` BuildCookRun, packaged accepted/cold-retry/rejection proof, deterministic unchanged league/replay exporters, visual inspection, canvas parsing, compilation, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H17 Player Facing Upcoming QA Match Winner Request]].
- **Closed by Phase 1H.18:** the exact pending H17 request now has the independently validated cold-restored receipt below.

### Phase 1H.18 Cold-Restored Pending Match Winner Receipt status

- **Status:** COMPLETE on `agent/phase-0d`; one read-only receipt for the exact noncanonical machine-local H17 pending request only.
- **Implementation:** in a separate cold process, `E` at the existing Sundale Sportsbook frontage shows the exact request ID, offer ID/version, selected team, stake `40`, accepted and lock times, `accepted_pending_lock`, linked sequence-`2` `-40` `match_winner_stake` entry, and balance `60`. Leaving the frontage closes it. Ponytail reused the SaveGame, frontage, input path, and native on-screen reader without a history framework, widget system, service, schema, or dependency.
- **Safety and invariance:** the loader directly validates the current SaveGame schema, initial job credit, stake debit, request, exact offer, times, status, balance, and absence of every lock/result/decision/finalization/cancellation/void record before exposing any value. Missing, multiple, mismatched, stale, malformed, duplicate, or invented evidence fails closed with no partial display. The receipt process calls no request API and bypasses migration and reconciliation writes. Packaged state stayed exactly `3,737` bytes with unchanged SHA-256 and timestamp across the cold viewer. H17 duplicate/rejection behavior and cleanup remain intact; H16 and every canonical artifact are unchanged.
- **Validation:** focused H18 native automation `1/1`, full native `13/13`, odds contracts `3/3` in `0.056s`, bundled Python 3.12 timing-first frozen regressions `65/65` in `133.602s`, Brain Admin self-check, editor/game builds, clean `151.50s` and final incremental `50.38s` BuildCookRun passes, packaged two-process read-only proof, H17 cold audit, unchanged deterministic league/replay exporters, visual inspection, Python compilation, canvas parsing, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H18 Cold Restored Pending Match Winner Receipt]].
- **Boundary:** no submit, debit, lock, result, settlement, refund, correction, migration, generalized history, account, backend, payment, real-money connection, deployment, retraining, brain/model, or Admin mutation path was added.
- **Next candidate gate:** Scope Director review of the smallest remaining Match Winner requirement. Canonical future-game request, game-start and settlement integration, correction, and broader player history remain separate unproved gates; no later phase has begun.

### Phase 1H.19 Exact Upcoming QA Game-Start Lock status

- **Status:** COMPLETE on `agent/phase-0d`; one server-owned lock for the exact noncanonical machine-local H17 request only.
- **Implementation:** GameMode owns the fixed command `qa:h19:match_winner:lock:1`, exact H17 request ID, Season `100`, Game `1`, and authoritative QA time `2100086400`. A parameterless transition reuses `LockOddsWellMatchWinnerRequest` only when the server clock reaches that exact time, then persists one immutable `locked` record. No player key, command ID, game identity, or time enters the production path.
- **Safety and invariance:** the transition independently requires the exact H17 request, offer, teams, Sparks selection, stake `40`, accepted time, sequence-`2` `-40` debit, balance `60`, and job cooldown before lock. All H17 values remain byte-for-value; only one lock record is added. Exact cold retry is `DUPLICATE`. Wrong request/game/time, early/late/invented time, conflict reuse, a second lock, completed-H16 identity, and malformed request/debit/offer evidence reject with zero mutation. No result, replay, simulation, settlement, refund, correction, UI, account, backend, real-money path, deployment, retraining, or brain change was added.
- **Validation:** focused native H19 automation `1/1`, final full native `14/14`, odds contracts `3/3` in `0.047s`, bundled Python `3.12.13` timing-first frozen regressions `65/65` in `146.516s`, Brain Admin self-check, editor/game builds, final `38.57s` BuildCookRun, deterministic league/replay exporters, packaged H17 seed → H19 lock → cold duplicate/rejection/cleanup proof, Python compilation, canvas parsing, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H19 Exact Upcoming QA Game Start Lock]].
- **Next candidate gate:** Scope Director review. Authoritative result integration, settlement integration, correction, and broader player history remain separate unproved gates; no Phase 1H.20 work has begun.

### Phase 1H.20 Immutable Authoritative Upcoming QA Cancellation Evidence status

- **Status:** COMPLETE on `agent/phase-0d`; one server-owned canceled-game disposition for the exact noncanonical H17/H19 QA chain only.
- **Implementation:** GameMode owns fixed command `qa:h20:match_winner:cancellation:1`, fixed evidence ID `qa:h20:match_winner:cancellation:evidence:1`, exact request/lock links, Season `100`, Game `1`, and post-lock QA time `2100086700`. A parameterless transition reuses `RecordOddsWellMatchWinnerCanceledGame` to persist one immutable `game_canceled` / `closed_canceled` record. No player identity, time, reason, or status enters the production path.
- **Safety and invariance:** the transition independently requires the exact H17 request/debit, exact H19 lock, ledger `2`, balance `60`, cooldown `2100086400`, and zero downstream evidence. Exact cold retry is `DUPLICATE`. Wrong link/game/time/evidence, conflict, second cancellation, malformed state/input, fabricated normal result, and completed-H16 identity reject with byte-stable zero mutation. Canonical outputs and prior exact loss/win/void histories remain unchanged.
- **Validation:** focused native H20 automation `1/1`, full native `15/15`, odds contracts `3/3` in `0.045s`, bundled Python `3.12.13` timing-first frozen regressions `65/65` in `140.932s`, Brain Admin self-check, editor/game builds, `52.26s` BuildCookRun, packaged H17 seed → H19 lock → H20 cancellation → cold duplicate/rejection/cleanup proof, deterministic league/replay exporters, Python compilation, canvas parsing, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H20 Immutable Authoritative Upcoming QA Cancellation Evidence]].
- **Boundary:** no refund decision or credit, application/finalization, settlement, normal result, UI, generalized cancellation policy, canonical mutation, account, backend, payment, deployment, retraining, simulator, or brain change was added.
- **Closed by Phase 1H.21:** the exact H20 cancellation now has the independently validated void/refund-due decision below.

### Phase 1H.21 Immutable Exact Upcoming QA Void Refund Due Decision status

- **Status:** COMPLETE on `agent/phase-0d`; one server-owned void/refund-due decision for the exact noncanonical H17/H19/H20 QA chain only.
- **Implementation:** GameMode owns fixed command `qa:h21:match_winner:void-decision:1`. A parameterless transition reuses `DecideOddsWellMatchWinnerVoidRefundDue` and derives the exact H17 request, H19 lock, H20 cancellation command/evidence, Season `100`, Game `1`, Sparks selection, stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund`. No player identity, command, link, game, team, stake, outcome, amount, or status enters the production path.
- **Safety and invariance:** ledger count remains `2`, balance remains `60`, and cooldown remains `2100086400`; no refund is applied and no credit or finalization exists. Exact cold retry is `DUPLICATE`. Wrong links/evidence, conflict, second decision, malformed input, fabricated normal result, and persisted cancellation/decision tamper reject with byte-stable zero mutation. Canonical outputs and prior exact histories remain unchanged.
- **Validation:** focused native H21 automation `1/1`, full native `16/16`, odds contracts `3/3` in `0.045s`, bundled Python `3.12.13` timing-first frozen regressions `65/65` in `141.229s`, Brain Admin self-check, editor/game builds, `52.50s` BuildCookRun, packaged H17 seed → H19 lock → H20 cancellation → H21 decision → cold duplicate/rejection/cleanup proof, deterministic league/replay exporters, Python compilation, canvas parsing, and diff hygiene passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H21 Immutable Exact Upcoming QA Void Refund Due Decision]].
- **Boundary:** no refund application or finalization, ledger credit, settlement, normal result, read-only history, UI, generalized refund policy, canonical mutation, account, backend, payment, deployment, retraining, simulator, or brain change was added.
- **Closed by Phase 1H.22:** the exact H21 refund is now atomically applied and separately finalized below.

### Phase 1H.22 Idempotent Exact Upcoming QA Refund Application and Finalization status

- **Status:** COMPLETE on `agent/phase-0d`; one server-owned refund application/finalization for the exact noncanonical H17/H19/H20/H21 QA chain only.
- **Implementation:** GameMode owns fixed command `qa:h22:match_winner:void-finalization:1`. A parameterless transition reuses `FinalizeOddsWellMatchWinnerVoidRefund` to atomically append ledger sequence `3`, `+40`, reason `match_winner_refund`, balance `100`, plus one separate immutable `settled_void` finalization binding the exact request, lock, cancellation/evidence, H21 decision, refund due/applied `40`, ledger count `3`, and balance `100`. H21 remains `decided_void_pending_refund`.
- **Safety and invariance:** exact cold retry is `DUPLICATE`. Wrong decision/link, conflict, second finalization, persisted tamper, malformed identity, fabricated normal-result overlap, and unexpected ledger evidence reject with byte-stable zero mutation. The H17 request, H19 lock, H20 cancellation, H21 decision, cooldown, canonical outputs, prior exact histories, simulator, and brains remain unchanged.
- **Validation:** focused native H22 automation `1/1`, full native `17/17`, odds contracts `3/3` in `0.045s`, bundled Python `3.12.13` timing-first frozen regressions `65/65` in `144.229s`, Brain Admin self-check, editor build `11.18s`, game build `17.46s`, `66.75s` BuildCookRun, deterministic league/replay exporters, Python compilation, canvas parsing, and diff hygiene passed. A clean final-source rerun with the packaged executable modified `2026-07-23 02:41:35.976 -06:00` ran H17 seed → H19 lock → H20 cancellation → H21 decision → H22 finalization → cold verifier as six separate processes. `Phase1H22_FinalSource_H22_Finalization.log` proves `detail=none`, sequence `3`, `+40`, entries `3`, and balance `100`; `Phase1H22_FinalSource_H22_ColdVerify.log` proves cold restore, exact duplicate, the full rejection audit, byte-stable zero mutation, exact links, cleanup, and `detail=none`. The finalized state was `8,849` bytes with SHA-256 `8c3d75d80c2da06797338727eb3481d7ba5c424cbfc3cd6eba28aea4703ca2f1` before cleanup and absent afterward. Cost was `$0.00`. See [[Development/Reports/Phase 1H22 Idempotent Exact Upcoming QA Refund Application and Finalization]].
- **Boundary:** no player/Admin UI, read-only history feature, correction, canonical result or settlement, generalized service, account, backend, payment, deployment, retraining, simulator, or brain change was added.
- **Closed by Phase 1H.23:** the normal player-facing offer presentation now uses the concise stadium ticket-booth interaction below.

### Phase 1H.23 Player-Facing Ticket Booth Odds Presentation Cleanup status

- **Status:** COMPLETE on `agent/phase-0d`; one concise normal-play presentation at the existing Sundale sportsbook route point, now labeled as the stadium ticket booth.
- **Implementation:** proximity shows exactly `Press E to open betting odds`. `E` opens the validated Match Winner matchup, both teams' decimal odds, the approved `10`–`100` Odds Bucks stake range, game-start lock rule, and one `[E] CLOSE` instruction. The persistent `Press L` league hint and normal-view offer IDs, source versions, commitments, probabilities, Unix timestamps, return tables, and QA wording were removed.
- **Safety and invariance:** the underlying technical offer builder and QA log remain available off-screen. The interaction stays read-only; no request, debit, balance, settlement, market, result, simulator, brain, map topology, or persistence behavior changed.
- **Validation:** editor build passed in `11.65s`; Windows Development BuildCookRun passed in `119.32s`; focused stadium automation passed `1/1`; full native automation passed `17/17`; the bundled Python 3.12 timing guard passed `1/1` in `102.513s`; all `68/68` Python checks passed in `242.746s`; Brain Admin self-check, Python compilation, rendered QA, visual inspection, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H23 Player Facing Ticket Booth Odds Presentation Cleanup]].
- **Boundary:** this is still a native development text panel at a placeholder route point. No UMG production menu, Escape/controls menu, final ticket-booth art, canonical player wager submission, new-chain history, correction, backend, deployment, payment, or real-money path was added.
- **Closed by Phase 1H.24:** the native development text panel is replaced by the graphical read-only basketball market browser below.

### Phase 1H.24 Graphical Ticket-Booth Basketball Market Browser status

- **Status:** COMPLETE on `agent/phase-0d`; one researched native Unreal HUD for the current read-only ticket-booth path.
- **Implementation:** `E` at the booth opens a modal four-tab basketball browser with Game Lines, Margin, Overtime, and Player Props. Game Lines renders the exact validated Match Winner teams and decimal odds. The persistent read-only slip names the Odds Bucks stake range, decimal-return convention, game-start lock, and no-real-money boundary. Mouse-clickable tabs plus Left/Right, controller shoulders, `E`, Escape, and controller Back navigation work while movement/look input is suspended and restored on close.
- **Safety and invariance:** Margin, Overtime, Points, Rebounds, and Personal Fouls appear only as explicitly locked categories with `ODDS NOT PUBLISHED`. Active/locked states use text as well as color. Technical identifiers remain off-screen. The phase adds no price, formula, offer, probability, request, debit, canonical wager submission, result, settlement, balance mutation, simulator behavior, brain behavior, persistence schema, dependency, payment, or real-money path.
- **Validation:** editor build, focused stadium automation `1/1`, full native automation `17/17`, rendered 1280x800 ticket-booth QA, visual inspection, packaged Windows proof, frozen Python regressions, Brain Admin self-check, Python compilation, canvas parsing, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Design/Basketball Betting Interface Research]] and [[Development/Reports/Phase 1H24 Graphical Ticket Booth Basketball Market Browser]].
- **Closed by Phase 1H.25:** the exact H17-to-H22 finalized QA chain now publishes through the existing read-only reconciliation path below.

### Phase 1H.25 Read-Only Exact Upcoming QA Wager Reconciliation/History status

- **Status:** COMPLETE on `agent/phase-0d`; the existing reconciliation-v1 writer, API, independent validator, and single Operations card now accept the exact finalized H17/H19/H20/H21/H22 Season `100`, Game `1` chain.
- **Implementation:** the writer publishes only when every fixed offer, request, lock, cancellation/evidence, void-decision, finalization, ledger, time, amount, and status value matches. The existing card shows Sparks, stake/refund `40`, sequence `2/-40/60`, sequence `3/+40/100`, `settled_void`, count `3`, balance `100`, net `0`, and the exact command chain. No new endpoint, card, control, schema, dependency, or abstraction was added.
- **Safety and invariance:** missing, stale, partial, mixed, or tampered Season `100` evidence fails closed and shows no partial wager values. Cold load regenerates the exact projection; exact retry stays duplicate-safe; rejection cleanup removes stale projection data. The older exact loss, win, and Season `99` void paths remain accepted, and deterministic league/replay exports remain unchanged.
- **Validation:** focused native `1/1`, full native `17/17`, frozen Python groups `68/68` in `163.162s`, Brain Admin self-check, final editor/game builds, fresh `44.03s` Windows BuildCookRun, five-process packaged H17-to-H22 proof, separate cold duplicate/rejection/zero-mutation cleanup proof, live Admin API/page proof, Python compilation, canvas parsing, and diff hygiene passed. The fresh package contained `50` files totaling `1,045,635,342` bytes. Cost was `$0.00`. See [[Development/Reports/Phase 1H25 Read Only Exact Upcoming QA Wager Reconciliation History]].
- **Boundary:** this is one noncanonical machine-local QA history only. It adds no canonical future-game submission, correction workflow, generalized player history, later market, backend/account, payment, deployment, retraining, simulator, or brain behavior.
- **Closed by Phase 1H.26A:** the active local-beta schedule now has the separate immutable scheduled-game prerequisite below.

### Phase 1H.26A Immutable Canonical Scheduled-Unplayed Game Record status

- **Status:** COMPLETE on `agent/phase-0d`; one active canonical local-beta schedule record only.
- **Implementation:** one authoritative GameMode no-input transition creates or cold-restores schema `oddswell-canonical-scheduled-game-v1`, version `1`, fresh Season `1`, Game `1`, Harbor City Waves home, Mesa Vista Sol away, server-owned creation time, tipoff exactly `+1,800` seconds, eligibility at creation, no published offer, and `scheduled_unplayed`. The record explicitly says `local_beta`, timing authority `server`, and non-production timing.
- **Safety and invariance:** exact retry restores every first-written field. Conflicting identity, timing, schema/version, production/offer flags, or result-like status rejects without rewrite. The dedicated SaveGame contains no result, score, winner, replay/action tape, seed/RNG, private athlete, economy, or user data. It does not mutate `PublicSeason1`, Season `100` QA, any ledger/history, UI, simulator, or brain behavior.
- **Validation:** focused native `1/1`, full native `18/18`, frozen Python groups `68/68`, Brain Admin self-check, editor/game builds, fresh `93.41s` Windows BuildCookRun, exact deterministic league/replay hashes, Python compilation, canvas parsing, and diff hygiene passed. A clean first package process retained `transition=created` in `C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Logs\Phase1H26A_Retained_Created.log`; a separate cold process retained `transition=duplicate` with every original field identical in `C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Logs\Phase1H26A_Retained_Duplicate.log`. The isolated record stayed `2,771` bytes with SHA-256 `40fa5d048857e870575418f704548261c71418b00a1f77d0cee05be4a5104f84` and UTC mtime `2026-07-24T16:05:17.7663150Z`, then was deleted and verified absent with zero OddsWell test or Zen processes. Cost was `$0.00`. See [[Development/Reports/Phase 1H26A Immutable Canonical Scheduled Unplayed Game Record]] and [[Design/Decisions/DEC-018 Canonical Local Beta Schedule Timing]].
- **Boundary:** no offer, request, debit, lock, simulation, result, settlement, correction, broader history, backend/account, deployment, payment, real money, retraining, or brain change was added.
- **Closed by Phase 1H.26B:** the active schedule now has the separate immutable equal-public pregame prediction commitment below.

### Phase 1H.26B Immutable Equal-Public Pregame Prediction Commitment status

- **Status:** COMPLETE on `agent/phase-0d`; one immutable public prediction commitment for the active local-beta opener only.
- **Implementation:** after independently validating H26A, one no-input GameMode transition creates or cold-restores schema `oddswell-canonical-pregame-commitment-v1`, version `1`. It binds fresh Season `1`, Game `1`, Harbor home versus Mesa away to `oddswell-public-pregame-v1`, `phase0d4-v1`, input class `public_elo_rotation`, and SHA-256 `898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f`. The `2,072`-byte canonical JSON uses fresh `0-0` standings, equal `7`-day rest, and existing public fictional rosters, ratings, availability, and projected minutes.
- **Safety and invariance:** the commitment is reconstructed from existing simulation source without reading the completed `PublicSeason1` archive. Exact retry/cold restore is identical; malformed or conflicting schedule link, versions, JSON, hash, status, or environment rejects without rewrite. H26A remains byte-for-byte unchanged. No offer, odds, UI, wager, simulation, result, private input, backend, model, or brain behavior was added.
- **Validation:** focused native `1/1`, full native `19/19`, frozen Python groups `68/68`, Brain Admin self-check, editor/game builds, fresh `50.39s` Windows BuildCookRun, exact deterministic league/replay hashes, Python compilation, canvas parsing, diff hygiene, and zero-process cleanup passed. Clean create and separate cold duplicate package logs were retained; both isolated H26A and H26B SaveGames preserved exact byte hashes and UTC mtimes, then were deleted and verified absent. Cost was `$0.00`. See [[Development/Reports/Phase 1H26B Immutable Equal Public Pregame Prediction Commitment]], [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]], and [[Design/Decisions/DEC-018 Canonical Local Beta Schedule Timing]].
- **Boundary:** this is only an immutable prediction commitment. It adds no offer, price, request, debit, lock, simulation, result, settlement, correction, broader history, backend/account, deployment, payment, real money, retraining, or new model.
- **Closed by Phase 1H.26C:** the active schedule and public commitment now have the separate immutable canonical Match Winner offer record below.

### Phase 1H.26C Immutable Canonical Match Winner Offer Record status

- **Status:** COMPLETE on `agent/phase-0d`; one immutable canonical Match Winner offer record for the active local-beta opener only.
- **Implementation:** before H26A tipoff, one no-input GameMode transition consumes exact validated H26A and H26B records, reuses the existing Phase 1H canonical serializer/SHA/validator, and persists only the offer ID plus exact canonical JSON. The record is `oddswell-basketball-odds-offer-v1` / `basketball-match-winner-odds-v1`, `match_winner`, `odds_bucks`, H26B public source, tipoff lock, stakes `10`–`100` by `10`, edge `0`, exact floor payout, Harbor `57586693` / `17365`, and Mesa `42413307` / `23577`.
- **Safety and invariance:** before-creation or at/after-tipoff time rejects; wrong upstream identity/version/hash/state and persisted conflicts reject without rewrite. A recursive nested-field audit excludes private, seed/RNG, fatigue/life, result, wager-action, economy, and user fields. Exact cold retry is duplicate-safe. H26A and H26B bytes/hashes/mtimes remain unchanged, including H26A `offer_published=false`. No `PublicSeason1` input, UI/slip, request, debit, lock transition, simulation, result, settlement, backend, or later market was added.
- **Validation:** focused native `1/1`, full native `20/20`, frozen Python groups `68/68`, Phase 1H odds contracts `3/3`, Brain Admin self-check, Python compilation, editor/game builds, fresh final `47.14s` Windows BuildCookRun, exact deterministic league/replay hashes, clean packaged create plus separate cold duplicate proof, canvas parsing, diff hygiene, and zero-process cleanup passed. The isolated H26A/H26B/H26C files preserved exact byte lengths, hashes, and UTC mtimes before deletion. Cost was `$0.00`. See [[Development/Reports/Phase 1H26C Immutable Canonical Match Winner Offer Record]] and [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]].
- **Boundary:** this is not a player-facing canonical offer path and creates no wager action. Presentation, selection, slip, request, debit, accepted wager, lock transition, simulation, result, settlement, correction, broader history, backend/account, deployment, payment, real money, retraining, and later markets remain unproved.
- **Closed by Phase 1H.26D:** the exact H26C record now has the fail-closed read-only player consumer below.

### Phase 1H.26D Player-Facing Read-Only Canonical Match Winner Offer status

- **Status:** COMPLETE on `agent/phase-0d`; one normal-play read-only consumer of the exact active H26A/H26B/H26C local-beta offer only.
- **Implementation:** before server tipoff, the existing Phase 1H.24 stadium ticket-booth HUD now loads exact H26A, H26B, and H26C evidence and displays Mesa at Harbor, Match Winner, integer-backed decimal displays `1.7365` / `2.3577`, Odds Bucks `10`–`100` step `10`, exact gross-return examples/convention, server tipoff, and `LOCAL BETA`. The cards and slip remain read-only. Existing mouse, keyboard, and controller modal controls are reused.
- **Safety and invariance:** missing, mismatched, tampered, before-creation, or at/after-tipoff evidence clears the preview and shows one unavailable/locked panel with no partial teams or prices. Normal play has no H16/PublicSeason1 offer fallback and accepts no caller-provided time. No selection, editor, confirmation, request, debit, receipt, persistence write, lock transition, simulation, result, settlement, history, repricing, backend, or later market was added. Cold packaged restore preserved exact H26A/H26B/H26C bytes, hashes, and mtimes; ledger entries/balance stayed `0/0`; deterministic league and replay exports remain exact.
- **Validation:** focused native `1/1`, full native `20/20`, frozen Python `68` tests plus `16` subtests, Phase 1H contracts `3/3`, Brain Admin self-check, Python compilation, editor/game builds, final `65.3s` explicit-Sundale Windows BuildCookRun, fresh packaged canonical QA, cold duplicate/invariance proof, `1280x800` rendered inspection, canvas parsing, diff hygiene, and zero-process cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H26D Player Facing Read Only Canonical Match Winner Offer]].
- **Boundary:** this proves only read-only presentation of the exact canonical pre-tipoff offer. It does not prove or authorize a canonical player action.
- **Closed by Phase 1H.26E:** the exact canonical offer now has the server-authoritative request and atomic stake debit below.

### Phase 1H.26E Server-Authoritative Canonical Match Winner Request and Atomic Stake Debit status

- **Status:** COMPLETE on `agent/phase-0d`; one exact accepted request for the active local-beta opener only.
- **Implementation:** the caller supplies only exact H26C offer ID, one offered team, and one whole approved stake. The server reloads exact H26A/H26B/H26C, uses server UTC and a stable server-owned request command, then reuses the existing atomic request/debit primitive. The accepted proof reused the local `+100` job credit and persisted sequence `2`, `-40`, one `accepted_pending_lock` request, and balance `60`.
- **Immutable evidence:** Odds Bucks schema `12` adds versioned offer/source/game/selection/probability/odds/stake/payout/gross-return/server-time/lock evidence. Existing records retain legacy evidence version `0`; new requests require internally exact evidence version `1`. Cold exact retry is duplicate-safe and preserves the first server time.
- **Safety and invariance:** bad offer, team, stake, changed valid stake, early/late time, tampered H26A/B/C, underfunding, command conflict, and native persistence failure reject with zero mutation. A forced read-only SaveGame failure remained byte-stable with balance `100` and zero requests. H26D stays read-only; only an explicit isolated command-line QA route invokes the packaged proof.
- **Validation:** focused native `1/1`, full native `21/21`, odds contracts `3/3`, frozen Python `68/68`, Brain Admin self-check, Python compilation, editor/game builds, and final `68.62s` Windows BuildCookRun passed. Separate packaged processes proved accepted sequence `2/-40/60`, cold duplicate, bad-input zero mutation, exact upstream preservation, and QA cleanup. The package contains `50` files totaling `1,046,248,718` bytes. Deterministic league/replay hashes remain exact. Cost was `$0.00`. See [[Development/Reports/Phase 1H26E Server Authoritative Canonical Match Winner Request and Atomic Stake Debit]].
- **Boundary:** no normal selection/editor/confirmation route, receipt, canonical game-start lock, result, settlement, history, multiple request model, later market, backend/account, payment, real money, deployment, retraining, simulator, or brain behavior was added.
- **Closed by Phase 1H.26F:** the exact H26E request now has the independently validated, cold-restored pending receipt below.

### Phase 1H.26F Cold-Restored Read-Only Canonical Pending Wager Receipt status

- **Status:** COMPLETE on `agent/phase-0d`; one read-only receipt for the exact active local-beta H26E request only.
- **Implementation:** before server tipoff, the existing ticket-booth browser independently restores exact H26A/H26B/H26C plus Odds Bucks schema `12`, one sequence-`1` `+100` job credit, one sequence-`2` `-40` `match_winner_stake` debit, one Harbor City Waves request at probability `57586693` and odds `17365`, gross return `69`, `accepted_pending_lock`, and balance `60`. The slip shows only `BET ACCEPTED / PENDING TIPOFF`, team, stake, potential gross, balance, tipoff, and lock; technical IDs remain hidden and all cards remain noninteractive.
- **Safety and invariance:** the viewer directly reads and validates current evidence without migration, reconciliation, acceptance, or any write path. Missing request evidence preserves the H26D offer before tipoff. A coordinator-found held-open regression was corrected: at exact tipoff the already-open no-request offer now clears its teams/prices and immediately renders the locked panel without requiring close/reopen. Multiple, orphaned, stale-schema, tampered, downstream, at-tipoff, or post-tipoff evidence fails closed with no partial receipt. Opening, tabbing, closing, leaving, reopening, and cold restarting cannot submit or debit.
- **Validation:** final correction-focused native receipt and held-open tests passed `2/2`; full native passed `23/23`. Odds contracts `3/3`, frozen Python `68/68` plus `16` subtests, Brain Admin self-check, Python compilation, and unchanged deterministic league/replay hashes retain their final H26F passes. Final correction-source editor/game builds and a fresh `51.66s` Windows BuildCookRun passed; the correction package contains `50` files totaling `1,046,411,022` bytes. Separate packaged processes proved exact acceptance, byte/hash/mtime-stable cold receipt viewing, no-request H26D preservation, fail-closed rejection of the older QA request, and the held-open exact-tipoff transition to a no-teams/no-prices locked panel with ledger `0/0`, no write/debit, and unchanged H26A/H26B/H26C bytes, hashes, and mtimes. Cost was `$0.00`. See [[Development/Reports/Phase 1H26F Cold Restored Read Only Canonical Pending Wager Receipt]].
- **Boundary:** no normal player selection/editor/confirmation route, canonical game-start lock, result, settlement, history, multiple-request model, later market, backend/account, payment, real money, deployment, retraining, simulator, or brain behavior was added.
- **Closed by Phase 1H.26G:** the exact H26E request now has the separate immutable server-owned game-start lock below.

### Phase 1H.26G Server-Owned Exact Canonical Game-Start Lock status

- **Status:** COMPLETE on `agent/phase-0d`; one exact game-start lock for the active local-beta H26E request only.
- **Implementation:** one parameterless authoritative transition reloads and independently validates exact H26A/H26B/H26C plus current schema-`12` H26E evidence. It runs only when server-observed time equals the H26A tipoff, owns the stable H26G command and lock ID, and appends exactly one separate immutable `locked` record linked to Season `1`, Game `1`, Harbor selection, stake `40`, odds `17365`, and gross return `69`.
- **Safety and invariance:** the original `accepted_pending_lock` request, sequence-`1` `+100` credit, sequence-`2` `-40` stake debit, balance `60`, cooldown, H26A/H26B/H26C records, and all first-written times remain unchanged. Early, late, malformed, migrated, missing, multiple, conflicting, downstream, or write-failure evidence rejects with zero mutation. Exact cold retry is duplicate-safe.
- **Player-facing state:** after lock, the existing booth shows one `MATCH WINNER UNAVAILABLE / LOCKED` panel. It exposes no pending receipt, teams, prices, selections, result, or controls and performs no write.
- **Validation:** focused native `1/1`, full native `24/24`, frozen Python `68/68`, Phase 1H odds contracts `3/3`, Brain Admin self-check, Python compilation, editor/game builds, exact deterministic league/replay hashes, final explicit-Sundale Windows package, packaged seed/lock/visual/cold-retry/rejection/cleanup chain, upstream hash/mtime invariance, canvas parsing, diff hygiene, and zero-process cleanup passed. The package contains `50` files totaling `1,046,598,926` bytes. Cost was `$0.00`. See [[Development/Reports/Phase 1H26G Server Owned Exact Canonical Game Start Lock]].
- **Boundary:** no normal selection/editor/confirmation route, simulation, result, decision, settlement, history, correction, multiple-request model, later market, backend/account, payment, real money, deployment, retraining, simulator change, or brain behavior was added.
- **Closed by Phase 1H.26H:** the exact locked game now has the separate private execution commitment below.

### Phase 1H.26H Immutable Canonical Active-Game Execution Commitment status

- **Status:** COMPLETE on `agent/phase-0d`; one private server-only execution commitment for the exact H26G-locked canonical opener.
- **Implementation:** one parameterless transition reloads exact H26A/H26B/H26C/H26G evidence, derives a seed from versioned canonical JSON containing only immutable H26A schedule fields plus the H26B SHA-256, and persists a separate schema-v1 `committed_for_execution` record. Its frozen input binds `simulate_scheduled_game`, league `phase06l-v1`, engine `phase05h-v1`, brain `baseline-v2`, Athlete Life v4, consistency v2, involvement v1, fatigue/injury versions, exact rosters/ratings, full consistency/involvement snapshots, zero opening fatigue/recovery/readiness, no life decisions, and disabled player-points capture.
- **Safety and privacy:** request, selection, stake, balance, price, ledger, lock-command, accepted-time, and other post-offer fields cannot enter seed material. Seed, seed material, and full input remain absent from the public offer, booth, league export, reconciliation, player UI, and Brain Admin. Exact cold retry is duplicate-safe. Missing, multiple, malformed, migrated, conflicting, downstream, tampered, or write-failure evidence rejects without create or repair.
- **Validation:** editor/game builds, focused native `1/1`, full native `25/25`, frozen Python plus odds contracts `68/68`, Brain Admin self-check, Python compilation, independent Python/native canonical JSON and SHA parity, two identical in-memory dry-simulation manifests with no saved result, deterministic unchanged league/replay exporters, final `48.41s` explicit-Sundale Windows BuildCookRun, packaged create/cold-duplicate/missing-lock rejection/immutable-record/QA-ledger-cleanup proof, canvas parsing, diff hygiene, and zero-process cleanup passed. The package contains `50` files totaling `1,046,898,142` bytes. Cost was `$0.00`. See [[Development/Reports/Phase 1H26H Immutable Canonical Active Game Execution Commitment]].
- **Boundary:** no simulation result, score, winner, action tape, wager decision, settlement, history, player/Admin control, normal selection/confirmation, multiple-request model, later market, backend/account, payment, real money, deployment, retraining, simulator change, or brain behavior was added.
- **Closed by Phase 1H.26I:** the exact H26H commitment now has the private offline execution receipt below.

### Phase 1H.26I Private Canonical Game Execution Receipt status

- **Status:** COMPLETE on `agent/phase-0d`; one private local-authority handoff and one offline digest-only execution receipt for the exact H26H commitment.
- **Implementation:** a parameterless native function validates H26H and writes one fixed canonical JSON handoff under `Saved/PrivateExecution/Handoff`. A standalone standard-library Python command requires that exact handoff, revalidates every schema/status/hash/version/roster/snapshot/opening-state/seed field and forbidden-field absence, calls frozen `simulate_scheduled_game` exactly once, and atomically writes one receipt named by H26H commitment hash. The receipt contains only commitment/input hashes, executor version, opaque output digest, receipt hash, schema/version, and `executed_pending_seal`.
- **Safety and privacy:** no caller seed, input, version, team, wager, time, output, or path enters the native authority. Python is absent from the package and no runtime bridge, plugin, service, or port exists. Exact cold retry validates the receipt and returns duplicate without execution or rewrite. Handoff or receipt missing/extra/multiple/tampered/conflicting evidence rejects without repair. No score, winner, tape, event log, replay, result, settlement, or Odds Bucks link is persisted or exposed.
- **Validation:** focused Python `3/3`, focused native `1/1`, full native `26/26`, frozen Python plus odds `68/68`, odds `3/3`, Brain Admin, compilation, editor/game builds, deterministic exporters, final `56.18s` explicit-Sundale package, real packaged H26E→H26G→H26H→H26I handoff, external first execution, cold duplicate byte/hash/mtime invariance, invalid evidence/no-repair tests, QA-ledger cleanup, canvas parsing, and zero-process cleanup passed. The package contains `50` files totaling `1,046,948,318` bytes and zero Python files. Cost was `$0.00`. See [[Development/Reports/Phase 1H26I Private Canonical Game Execution Receipt]].
- **Boundary:** no authoritative seal, result record, score, winner, event/action tape, replay publication, presentation, wager decision, settlement, history, player/Admin surface, backend, deployment, retraining, simulator change, or brain behavior was added.
- **Closed by Phase 1H.26J:** the exact H26I receipt now has the immutable digest-only seal below.

### Phase 1H.26J Immutable Private Canonical Execution Digest Seal status

- **Status:** COMPLETE on `agent/phase-0d`; one immutable private digest seal for the exact H26H commitment and H26I receipt only.
- **Implementation:** the existing offline standard-library command accepts the exact handoff, receipt, and seal directories. It independently revalidates H26H/H26I, reruns the frozen deterministic simulator solely to recompute the opaque output digest, requires exact equality with H26I, and atomically writes one commitment-keyed schema-v1 `sealed_pending_result` record. The record contains only H26H commitment/input hashes, the H26I receipt hash, executor/verifier versions, the verified opaque digest, schema/version/status, and its canonical SHA-256.
- **Safety and privacy:** exact cold retry validates the existing seal and returns duplicate without simulation or rewrite. Missing, multiple, malformed, tampered, conflicting, wrong-digest, wrong-version, extra-field, or hash-invalid evidence fails closed without repair. No native runtime bridge, bundled Python, service, plugin, or port was added. No score, winner, statistics, action/event tape, replay, presentation, result record, wager decision, settlement, refund, Odds Bucks, reconciliation, player UI, or Admin surface was added.
- **Validation:** focused H26J Python `3/3`, retained H26I Python `3/3`, focused native boundary `1/1`, full native `26/26`, frozen Python plus odds `68/68`, Brain Admin, compilation, editor/game builds, exact deterministic exporters, and a fresh explicit-Sundale Windows package passed. The package contains `50` files totaling `1,046,948,318` bytes and zero Python files. A real packaged H26E→H26G→H26H→H26I chain produced a `515`-byte receipt and `671`-byte seal; the seal digest exactly matched the receipt, differed from the archived replay seal, and stayed byte/hash/mtime identical on cold duplicate. Separate canonical tamper rejected without repair, upstream evidence stayed exact, and QA-ledger cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H26J Immutable Private Canonical Execution Digest Seal]].
- **Boundary:** this is not an authoritative game result. Score/winner/result persistence, decision, settlement, replay publication, game presentation, history, player/Admin surfaces, backend, deployment, retraining, simulator changes, and brain changes remain unproved.
- **Closed by Phase 1H.26K:** the exact H26J seal now has the immutable private result record below.

### Phase 1H.26K Immutable Private Canonical Game Result Record status

- **Status:** COMPLETE on `agent/phase-0d`; one immutable private canonical result for the exact H26H/H26I/H26J chain only.
- **Implementation:** the existing offline standard-library command accepts only the exact handoff, receipt, seal, and result directories. It revalidates H26H/H26I/H26J, reruns the frozen simulator exactly once, requires its replay SHA-256 to equal the H26J verified digest, and atomically writes one commitment-keyed schema-v1 `recorded_pending_decision` record. The record contains only recorder/schema/version/status, commitment/seal/record/replay hashes, Season `1`, Game `1`, scheduled teams, integer scores, and the higher-scoring scheduled team as winner.
- **Safety and privacy:** no caller result field exists. A valid cold duplicate recomputes once, then preserves the first result bytes, file hash, and mtime. Missing, multiple, malformed, invalid-hash, wrong-digest, wrong-team, wrong-identity, negative, tied, wrong-winner, changed-score, extra-field, or validly rehashed conflicting evidence rejects without create or repair. No `PublicSeason1` or archive input, native bridge, bundled Python, service, plugin, framework, or port was added.
- **Validation:** focused H26K Python `3/3`, retained H26I/H26J/odds `9/9`, focused native boundary `1/1`, full native `26/26`, frozen Python plus odds `68/68`, Brain Admin, compilation, editor/game builds, deterministic exporters, and a fresh `89.88s` explicit-Sundale package passed. The package contains `50` files totaling `1,046,948,318` bytes and zero Python files. A real packaged H26E→H26K chain produced Harbor `99`, Mesa `104`, Mesa winner, replay SHA exactly equal to H26J, and one `660`-byte result. Cold duplicate and all upstream evidence stayed byte/hash/mtime exact; separate validly rehashed score tamper rejected without repair. The ledger remained `2/-40/60` until QA cleanup, and the booth, archive, exporters, and H26A–H26J evidence stayed invariant. Cost was `$0.00`. See [[Development/Reports/Phase 1H26K Immutable Private Canonical Game Result Record]].
- **Boundary:** this private record is not published replay or game presentation and creates no standings, statistics, UI/Admin surface, Odds Bucks link, wager decision, settlement, payout, history, or correction. Simulator and brain behavior remain unchanged.
- **Closed by Phase 1H.26L:** the exact private H26K result now has the immutable request/lock linkage below.

### Phase 1H.26L Server-Owned Immutable Canonical Match Winner Result Link status

- **Status:** COMPLETE on `agent/phase-0d`; one server-owned immutable Match Winner result link for the exact active Season `1`, Game `1` H26E–H26K chain only.
- **Implementation:** one parameterless native transition reloads exact H26A/B/C, current schema-`12` H26E request/debit, H26G lock, H26H commitment, one fixed-path H26J seal, and exactly one fixed-path H26K result. It enforces exact JSON keys/types/canonical bytes, fixed schema/version/status values, recomputed seal/record hashes, and transitive commitment/input/seal/replay/season/game/team/score/winner links. It derives the command ID solely from the H26K record hash and reuses the immutable result-link primitive to append one link with the exact request, lock, H26K schema/recorder, teams, scores, winner, and replay SHA-256.
- **Safety:** the archived `101`–`104` result remains under its separate exact predicate; H26L provides no archive fallback or relabel. Exact cold duplicate never rewrites. Missing/multiple/malformed/noncanonical/wrong-schema/version/status/hash/commitment/seal/replay/team/game/score/winner evidence rejects before mutation. The accepted transition leaves the ledger at `2/-40/60`, request/lock unchanged, result links `1`, and decisions/finalizations/cancellations/refunds/payouts `0`. It does not rerun the simulator.
- **Validation:** focused H26L native `1/1`, full native `27/27`, retained H26I/J/K `9/9`, frozen Python plus odds `68/68`, Brain Admin, compilation, editor/game builds, deterministic exporters, and a fresh `92.51s` explicit-Sundale package passed. The package contains `50` files totaling `1,047,229,918` bytes and zero Python files. A real packaged H26E→H26L chain produced Harbor `97`, Mesa `101`, Mesa winner, replay `efe75759…`, and command identity derived from H26K record `e4b8b4e2…`. Missing-result rejection preserved ledger bytes/hash/mtime; restored cold duplicate was byte-stable; eight H26A–H26K files stayed byte/hash/mtime exact; QA cleanup passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H26L Server Owned Immutable Canonical Match Winner Result Link]].
- **Boundary:** no wager decision, settlement, outcome/return due, payout, refund, correction, history, replay publication, tape, presentation, standings, statistics, UI/Admin surface, backend, deployment, retraining, simulator change, or brain behavior was added.
- **Closed by Phase 1H.26M:** the exact H26L loss result now has the immutable deterministic decision below.

### Phase 1H.26M Server-Owned Deterministic Canonical Match Winner Loss Decision status

- **Status:** COMPLETE on `agent/phase-0d`; one parameterless decision transition for the exact Harbor-selected, Mesa-winner active chain only.
- **Implementation:** the authority reloads exact H26A/B/C, schema-`12` H26E request/debit, H26G lock, and one exact private H26L result link. It derives `canonical:h26m:match_winner:decision:<H26K record_sha256>` solely from H26L/H26K identity and reuses the existing deterministic decision primitive. The one immutable record binds the approved schema/version/offer plus Harbor, Mesa, stake `40`, `lost`, gross return due `0`, and `decided_pending_apply`.
- **Safety:** ledger `2/-40/60`, request, lock, result link, and eight H26A–H26K files remain unchanged. Exact cold retry is byte-stable. Stale/mutated/archived/non-loss/downstream/foreign/finalized/write-failure evidence rejects without mutation. Finalizations, cancellations, voids, refunds, payouts, credits, history, UI, Admin, replay, statistics, and simulation changes remain `0`.
- **Validation:** focused native `1/1`, final full native `28/28`, frozen plus retained Python `77` tests and `106` subtests, Brain Admin, compilation, editor/game builds, deterministic league/replay exports, final `50.42s` explicit-Sundale package, authorized byte-exact retained H26L restore, decisions `0→1`, cold duplicate/cleanup, missing-H26C rejection, and upstream hash/mtime invariance passed. The package contains `50` files totaling `1,047,353,310` bytes and zero Python. A separately generated Harbor `115`–`101` Mesa chain was correctly stopped as a non-loss gate. Cost was `$0.00`. See [[Development/Reports/Phase 1H26M Server Owned Deterministic Canonical Match Winner Loss Decision]].
- **Boundary:** decision evidence only; no finalization, return application, ledger credit, settlement history, player/Admin surface, correction, backend, deployment, retraining, simulator change, or brain behavior was added.
- **Closed by Phase 1H.26N:** the exact H26M loss decision now has the immutable zero-return finalization below.

### Phase 1H.26N Server-Owned Exact Canonical Match Winner Loss Finalization status

- **Status:** COMPLETE on `agent/phase-0d`; one parameterless finalization transition for the exact retained Harbor-selected, Mesa-winner H26M loss chain only.
- **Implementation:** the authority reloads exact H26A/B/C, schema-`12` H26E request/debit, H26G lock, H26L result, and H26M decision. It derives `canonical:h26n:match_winner:finalization:<H26K record_sha256>` solely from the H26M/H26K identity and reuses the existing immutable loss-finalization primitive. The appended approved schema/version record binds Harbor, Mesa, stake `40`, `lost`, gross return applied `0`, `settled_lost`, ledger count `2`, and balance `60`.
- **Safety:** the H26M decision remains `decided_pending_apply` with gross return due `0`; ledger sequence `1/+100`, sequence `2/-40`, count `2`, and balance `60` remain exact, with no third entry. Request, lock, result, and eight separate H26A–H26K files remain unchanged. Stale/mutated/nonzero-return/winning/foreign/downstream/third-ledger/write-failure evidence rejects without mutation, and exact cold retry is byte-stable. This phase adds no ledger operation, credit, payout, refund, application, correction, history, UI/Admin surface, replay, statistics, simulator, or brain behavior. The reused primitive's pre-existing read-only projection behavior was not expanded; QA cleanup removed its transient file.
- **Validation:** focused native `1/1`, full native `29/29`, frozen plus retained Python `77` tests and `106` subtests, Brain Admin, Python compilation, editor/game builds, deterministic league/replay exports, and final `51.63s` explicit-Sundale package passed. The package contains `50` files totaling `1,047,528,414` bytes and zero Python. The authorized retained H26M ledger changed only by one finalization from SHA-256 `09f2bc8a…`, `8,332` bytes to `4731637e…`, `10,082` bytes; the eight separate upstream files stayed byte/hash/mtime exact. Packaged finalization, cold duplicate byte stability, QA cleanup, and missing-H26C rejection with exact source-ledger hash/length/mtime preservation passed. Cost was `$0.00`. See [[Development/Reports/Phase 1H26N Server Owned Exact Canonical Match Winner Loss Finalization]].
- **Closed by Phase 1H.26O:** the exact H26N finalization now has the output-only reconciliation/history surface below. Correction, broader player-visible history, multiple requests, and later markets remain unproved.

### Phase 1H.26O Read-Only Exact Canonical Match Winner Loss Reconciliation/History status

- **Status:** COMPLETE on `agent/phase-0d`; one output-only reconciliation for the exact retained H26A–H26N Harbor-selected, Mesa-winner loss chain.
- **Implementation:** the existing `oddswell-match-winner-reconciliation-v1` atomic writer, `/api/match-winner-reconciliation` endpoint, independent Brain Admin validator, and single Operations card now recognize this exact canonical chain. The card shows Harbor probability `57586693`, decimal odds `1.7365`, potential gross return `69`, final `97–101` Mesa, stake `40`, return `0`, net `-40`, ledger count `2`, balance `60`, and `decided_pending_apply → settled_lost`.
- **Safety:** publication loads schema `12` directly without migration, validates the full retained identities and evidence, and writes only the read-only projection. Missing, stale, partial, mixed, or tampered evidence removes any stale projection and exposes no partial values or controls. The source SaveGame stays byte/hash/mtime exact; no ledger entry, payout, refund, player receipt, new market, simulator/brain change, backend, deployment, or real-money path was added. Existing archived loss, win, and void reconciliation paths remain valid.
- **Validation:** focused native `1/1`; full native `30/30`; Python `77` tests and `106` subtests; Brain Admin self-check and Python compilation; editor/game builds; deterministic league/replay exporters; and final Windows package all passed. The real packaged run retained source SHA-256 `4731637ed326b5d139e328b8fab0cc8265c7efcf16e734f7d7dc35099e574997`, emitted exact H26O evidence, passed the live API and served-card structure checks, then passed cold verify/cleanup with source bytes and mtime stable. Browser inventory was unavailable, so no browser screenshot is claimed. The deliverable contains `50` files, `1,047,642,892` bytes, and zero Python files. Cost was `$0.00`. See [[Development/Reports/Phase 1H26O Read Only Exact Canonical Match Winner Loss Reconciliation History]].
- **Closed by Phase 1H.26P:** the exact H26N settled loss now has the player-facing read-only ticket-booth receipt below. Correction, generalized history, multiple requests, and later markets remain unproved.

### Phase 1H.26P Read-Only Player-Facing Exact Canonical Settled-Loss Receipt status

- **Status:** COMPLETE on `agent/phase-0d`; one read-only player receipt for the exact retained H26A–H26N Harbor-selected, Mesa-winner loss chain only.
- **Implementation:** the existing physical ticket-booth HUD now checks one in-memory native receipt before the existing offer/pending/unavailable states. The loader reuses exact H26A/H26B/H26C offer validation and H26O's exact authoritative schema-`12` H26E–H26N chain validator; it does not read the transient Admin projection. The settled screen shows only `BET SETTLED — LOSS`, Harbor selected, stake `40`, final Harbor `97–101` Mesa, Mesa winner, returned `0`, net `-40`, balance `60`, and one close instruction.
- **Safety:** state order remains offer → pending receipt → locked/unavailable → settled receipt. Missing, stale, partial, mixed, tampered, Season `99`, Season `100`, or archived evidence cannot substitute and exposes only the existing unavailable state with no partial values. View, close, leave, reopen, and cold restart do not mutate source bytes, hash, mtime, ledger count `2`, or balance `60`. No command ID, hash, seed, private athlete data, persistence, schema, writer, API, projection, Admin card, dependency, ledger operation, payout, refund, correction, simulator/brain change, backend, or deployment was added.
- **Validation:** focused native `2/2`; final full native `31/31`; frozen Python `77` tests and `106` subtests; Brain Admin self-check and Python compilation; deterministic league/replay exporters; editor/game builds; and final `55.94s` Windows package all passed. Two separate packaged cold processes showed the identical receipt while source SHA-256 `4731637ed326b5d139e328b8fab0cc8265c7efcf16e734f7d7dc35099e574997`, `10,082` bytes, and mtime remained exact. A packaged H26M source missing finalization and exact H26N source missing H26C both rendered only the existing unavailable panel without mutation. The inspected `1280×800` receipt was legible and unclipped. The clean deliverable contains `50` files, `1,047,731,678` bytes, and zero Python files. Cost was `$0.00`. See [[Development/Reports/Phase 1H26P Read Only Player Facing Exact Canonical Settled Loss Receipt]].
- **Closed by Phase 1H.26Q:** the exact active H26A/H26B/H26C offer now has the separate interactive review-only slip below. Normal confirmation/placement, correction, generalized player history, multiple requests, and later markets remain unproved.

### Phase 1H.26Q Interactive Canonical Match Winner Selection and Pre-Commit Bet-Slip Review status

- **Status:** COMPLETE on `agent/phase-0d`; one in-memory review-only player interaction for the exact active H26A/H26B/H26C pregame offer.
- **Implementation:** the existing native ticket-booth HUD now lets a player select Harbor City Waves or Mesa Vista Sol with mouse, keyboard, or controller and adjust an in-memory stake from `10` through `100` in increments of `10`. The persistent slip shows the selected team, immutable decimal odds, exact integer-formula potential gross return, current balance, game-start lock rule, and the exact label `REVIEW ONLY - WAGER NOT PLACED` (rendered with an em dash in game).
- **Safety:** there is no confirm or submit control and no request, debit, lock, receipt, SaveGame, or ledger mutation path. Close, leave, reopen, and cold restart reset the review. Exact pending and settled receipts retain precedence; game start clears the review to the existing locked panel; malformed H26A-H26C evidence reveals no partial values. Margin, Overtime, and Player Props remain visibly locked with no published odds.
- **Validation:** focused native `1/1`; full native `32/32`; frozen Python `77` tests and `106` subtests; Brain Admin self-check and Python compilation; deterministic league/replay exporters; editor/game builds; and final explicit-map Windows BuildCookRun passed. The package contains `50` files totaling `1,047,827,422` bytes and zero Python files. Packaged QA proved both teams and all ten stake increments with exact gross returns, visible mouse/keyboard/controller routes, reset and tipoff behavior, and no ledger/request mutation. A second cold process preserved all three H26A/H26B/H26C SaveGames by byte length, SHA-256, and mtime and created no new screenshot. The inspected `1280x800` slip was legible and unclipped. Cost was `$0.00`. See [[Development/Reports/Phase 1H26Q Interactive Canonical Match Winner Selection and Pre Commit Bet Slip Review]].
- **Closed by Phase 1H.26R:** this phase itself remains review only; H26R adds the separate exact Harbor/`40` two-confirm placement path. Correction, generalized player history, multiple requests, later markets, live odds, backend, deployment, retraining, simulator changes, and brain behavior remain separate unproved gates.

### Phase 1H.26R Exact Harbor/40 Canonical Wager Placement status

- **Status:** COMPLETE on `agent/phase-0d`; one normal player placement path for Harbor City Waves at exactly `40` Odds Bucks against the active H26A/H26B/H26C offer only.
- **Interaction:** the H26Q slip now exposes mouse, keyboard, and controller confirmation only for Harbor/`40`. The first confirmation visibly arms the slip without mutation; the second invokes a parameterless server RPC. Team, stake, tab, close, leave, Escape, reopen, or invalid evidence disarms or fails closed. Mesa, every other stake, and no selection explicitly show placement unavailable.
- **Authority:** the server independently reloads H26A/H26B/H26C, derives the offer identity, Harbor selection, stake `40`, immutable odds, UTC acceptance time, and stable H26E command, then reuses the existing atomic H26E request/debit primitive. Durable success creates exactly one `accepted_pending_lock` request and linked sequence-`2` `-40` debit after the existing `+100` job credit, leaving balance `60`; only then does the existing H26F pending receipt appear.
- **Validation:** focused native H26R `1/1`; full native `33/33`; frozen Python `77` tests and `106` subtests; Brain Admin; editor/game builds; deterministic exporters; and final explicit-map Windows package all passed. The package contains `50` files totaling `1,047,902,846` bytes and zero Python. Packaged normal-route QA and inspected `1280x800` armed/accepted screenshots proved job `100` -> booth -> Harbor `40` -> first confirm -> second confirm -> pending receipt. Cold packaged restore kept H26A/H26B/H26C and ledger bytes, hashes, and mtimes exact. The retained H26E regression again proved duplicate, conflict, insufficient-funds, tipoff, tamper, and persistence-failure zero-mutation behavior. Cost was `$0.00`. See [[Development/Reports/Phase 1H26R Exact Harbor 40 Canonical Wager Placement]].
- **Closed by Phase 1H.26S:** the exact pending Harbor/`40` request now schedules the existing H26G lock automatically at H26A tipoff. H26T adds the separate automatic H26H commitment below; H26I-H26P remain manual and separate.

### Phase 1H.26S Automatic Exact Canonical Tipoff Lock status

- **Status:** COMPLETE on `agent/phase-0d`; one automatic server-owned lock for the exact pending Harbor/`40` H26R request only.
- **Implementation:** after exact H26R durable success, or authoritative pre-tipoff restore, GameMode reloads the existing H26F pending receipt and schedules at most one non-looping timer for H26A tipoff. The callback accepts no caller time, command, offer, team, or stake and invokes the existing parameterless H26G transition. Only a persisted and reloaded H26G lock refreshes an open booth into the existing locked/unavailable panel.
- **Timing safety:** production uses the precise UTC duration to H26A tipoff. An early or late callback cannot invoke H26G; at or after tipoff no catch-up timer is scheduled and no timestamp is backdated. Restart before tipoff may schedule one replacement process-local timer. Package QA shortens only the wait to four seconds and reuses H26G's existing exact-H26A QA observation; it is not production wall-clock evidence.
- **Validation:** focused H26S and retained H26G native tests passed `1/1` each; full native passed `34/34`; frozen Python passed `77` tests and `106` subtests; Brain Admin compilation/self-check, deterministic exporters, editor/game builds, and final explicit-map Windows BuildCookRun passed. The package contains `50` files totaling `1,047,983,742` bytes and zero Python. Fresh packaged QA proved job `100` -> Harbor `40` -> pending -> one timer -> one H26G lock -> locked panel with ledger `+100,-40`, balance `60`, and the request unchanged. A separate pending-process restart rescheduled exactly one lock. H26A/H26B/H26C remained byte/hash/mtime exact, repeated ticks and reloads added no lock, and the inspected `1280x800` panel was legible and unclipped. Cost was `$0.00`. See [[Development/Reports/Phase 1H26S Automatic Exact Canonical Tipoff Lock]].
- **Closed by Phase 1H.26T:** H26S itself still stops after durable H26G and locked-booth refresh. H26T now invokes the existing parameterless H26H commitment only after that exact durable reload. H26I-H26P remain manual.

### Phase 1H.26T Automatic Canonical Active-Game Execution Commitment status

- **Status:** COMPLETE on `agent/phase-0d`; one automatic H26H commitment for the exact H26S-locked Harbor/`40` request only.
- **Implementation:** after H26S durably reloads H26G and refreshes the booth into its existing locked panel, GameMode calls the existing parameterless H26H creator. H26H independently reloads exact H26A/H26B/H26C/H26G, derives the private seed and frozen simulator input internally, and persists its existing immutable commitment. Only `Created` or exact `Duplicate` plus a validated durable reload is accepted.
- **Safety:** no caller seed, input, time, path, version, team, wager, stake, balance, or lock command enters H26H. The seed remains derived from H26A/H26B pre-wager evidence only; raw seed/input remain private and the player sees only the locked booth. Invalid, conflicting, tampered, downstream, or failed persistence creates or repairs nothing. H26I-H26P do not run.
- **Validation:** focused H26S/H26H passed `1/1` each; full native passed `34/34`; frozen Python passed `77` tests and `106` subtests; Brain Admin, deterministic exporters, and final editor/game BuildCookRun passed. The final package contains `50` files totaling `1,047,995,518` bytes and zero Python. Fresh packaged QA proved zero commitment before lock and exactly one automatic commitment after durable H26G. Cold H26H verification returned `Duplicate` while the single `9,744`-byte commitment retained SHA-256 `599de148a43e68165911006c0724c9d0adc17208972ccce7c3454493eccf4403` and exact mtime; no H26I handoff or result file existed. The inspected `1280x800` locked panel was legible and exposed no private commitment data. Cost was `$0.00`. See [[Development/Reports/Phase 1H26T Automatic Canonical Active Game Execution Commitment]].
- **Closed by Phase 1H.26U:** H26T still stops after the durable H26H commitment. H26U now invokes the existing parameterless H26I writer after that exact reload; the consumer, digest receipt, and H26J-H26P remain manual.

### Phase 1H.26U Automatic Private Canonical Game-Execution Handoff status

- **Status:** COMPLETE on `agent/phase-0d`; one automatic private H26I handoff for the exact H26T commitment only.
- **Implementation:** only after H26T accepts `Created` or exact `Duplicate` and reloads the durable H26H commitment, GameMode calls the existing parameterless handoff writer. That writer independently reloads exact H26H, emits its existing canonical UTF-8 JSON to the fixed private path, computes the file SHA-256, and uses the existing atomic write. Only `Created` or an exact immutable `Duplicate` is accepted.
- **Safety:** no caller seed, simulator input, time, path, version, team, wager, or stake enters the handoff. The locked booth does not expose private data. Conflict, bad/missing/tampered/multiple H26H, or failed persistence creates, overwrites, or repairs nothing. No Python consumer or process starts; no execution receipt, H26J seal, H26K result, H26L link, decision, finalization, settlement, or history is produced.
- **Validation:** focused H26S and H26I native tests passed `1/1` each; full native passed `34/34`; frozen Python passed `77` tests and `106` subtests; Brain Admin compilation/self-check, deterministic exporters, editor/game builds, and final Windows BuildCookRun passed. The package contains `50` files totaling `1,047,999,614` bytes and zero Python. Fresh packaged QA proved zero handoffs before H26H and exactly one afterward. The canonical `7,102`-byte private handoff retained SHA-256 `d97daf12b288f6254851d6145e9841c6ca628f243afd27edf0becaaab1cc08f4`; every embedded H26H commitment/input/seed-material digest matched. Cold duplicate preserved handoff and all H26A-H26H bytes, hashes, and mtimes; isolated conflict remained byte/hash/mtime exact and was not repaired. No receipt, seal, or result file existed. The inspected `1280x800` locked panel remained legible and exposed no private handoff data. Cost was `$0.00`. See [[Development/Reports/Phase 1H26U Automatic Private Canonical Game Execution Handoff]].
- **Closed by Phase 1H.26V:** H26U still stops after the private handoff. H26V now freezes the design-only external one-shot local supervisor boundary below; no supervisor, process, or receipt has been implemented.

### Phase 1H.26V Private Execution-Consumer Authority Review status

- **Status:** COMPLETE on `agent/phase-0d` as a design-only authority and threat-model gate; runtime remains exactly H26U.
- **Decision:** [[Design/Decisions/DEC-019 Private Local Execution Supervisor Boundary]] recommends one separate, explicitly invoked, one-shot trusted development supervisor for local-beta engineering. Bundled or client-spawned Python is rejected. A trusted backend worker is deferred until backend identity, authentication, queue, deployment, recovery, secrets, and operations receive separate authorization.
- **Frozen local boundary:** the future supervisor must use fixed private directories, one normalized absolute allowlisted interpreter, the approved repository revision, and existing `phase1h.execution` only. It accepts no arbitrary executable/module/path/argument/port or network input, reserves one atomic commitment-keyed attempt, runs one child for at most `120` seconds, requires clean exit `0`, preserves exact duplicate without re-execution, and stops on conflict, malformed evidence, race, crash, or timeout without retry or repair. Private logs contain bounded metadata only.
- **Threats and acceptance:** client spawn, executable/path injection, duplicate workers, races, crash ambiguity, tamper, forged receipts, sensitive logging, and service creep have explicit fail-closed controls and twelve pre-registered tests. Any implementation requires a separate Scope Director approval.
- **Read-only proof:** the final H26U package remains `50` files, `1,047,999,614` bytes, and zero Python; game source has no process-launch API path and there is no sanctioned launcher, watcher, service, or backend. The `28` frozen `phase0a`/`phase0d`/`phase1h` Python files retain aggregate manifest SHA-256 `6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c`; league/replay hashes remain unchanged. All canvases parse. Cost was `$0.00`. See [[Development/Reports/Phase 1H26V Private Execution Consumer Authority Review]].
- **Closed by Phase 1H.26W:** the separately approved external local proof below now implements DEC-019 without changing the client, package, simulator, or existing H26I consumer. H26J-H26P remain gated.

### Phase 1H.26W External One-Shot Local H26I Supervisor Proof status

- **Status:** COMPLETE on `agent/phase-0d`; one manual, external, nonresident local engineering supervisor for the exact fixed H26U handoff only.
- **Implementation:** the no-argument command uses the absolute allowlisted Python `3.12.13` interpreter and `phase1h.supervisor`. It verifies the unchanged `28`-file frozen manifest, fixed private H26W directories, and exact handoff; atomically reserves one commitment-keyed attempt; launches at most one allowlisted `-B -m phase1h.execution` child; enforces a `120`-second Windows Job timeout; requires exit `0`, exact bounded output, and the existing validated atomic receipt; writes approved private metadata; then exits. `phase1h.execution` is unchanged.
- **Safety:** no executable, module, path, argument, port, network input, seed, simulation input, output, or receipt field is caller-controlled. Exact existing receipt returns `duplicate` without a child or rewrite. Race, crash, timeout, malformed/tampered/multiple evidence, conflict, forged receipt, unexpected output, or nonzero exit stops without retry or repair. The game cannot launch the supervisor; Python remains outside the package. No watcher, service, backend, H26J seal, result, wager link, settlement, UI, or brain change exists.
- **Validation:** all twelve DEC-019 focused tests passed in `0.731s`; the full suite passed `89` tests in `147.067s`; full native Unreal automation passed `34/34`; Brain Admin self-check, Python compilation, and deterministic league/replay exports passed. A fresh unchanged package produced exactly one H26U handoff while reporting `python_consumer=false` and `receipt=false`. The external supervisor produced one `515`-byte `executed_pending_seal` receipt, one `255`-byte attempt claim, and one bounded two-record audit log; cold duplicate preserved handoff and receipt bytes/hash/mtime exactly. The package remains `50` files, `1,047,999,614` bytes, and zero Python, client launch references remain `0`, downstream H26J/result/settlement files remain `0`, and cost was `$0.00`. See [[Development/Reports/Phase 1H26W External One Shot Local H26I Supervisor Proof]].
- **Boundary and next gate:** H26W stops after the private H26I receipt. The next Scope Director review may consider only whether a separate explicit external H26J seal invocation is the smallest truthful next gate; no automatic seal, result, settlement, service, backend, or client process path is authorized.

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
