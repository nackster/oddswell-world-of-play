---
tags:
  - development
  - ai
  - admin
  - visualization
status: active
---

# Admin Console and Brain Observatory

The local Admin Console is the first operational shell for OddsWell. The cinematic Brain Observatory remains its primary module for inspecting cooperating brains and authoritative systems.

## Open it

Double-click `Start Brain Observatory.cmd` in the project root. The launcher starts a local-only server and opens `http://127.0.0.1:8765`. Close the terminal window or press `Ctrl+C` there to stop it.

The server now requires exclusive ownership of its port. If an older console is still running, close it before starting the current build; duplicate local instances are rejected so stale and current interfaces cannot answer on the same address.

## Current capabilities

- Shows the Project, Athlete Life, World and League, Basketball, Rules and Outcome, and Learning components.
- Reads the current engine, league, basketball brain, and LLM policy versions directly from the executable project.
- Shows the Phase 0D.4 public prediction-evaluation version as read-only World / League evidence.
- Runs a real seeded basketball simulation and animates a cinematic sample of its recorded decisions and outcomes.
- Provides a dedicated Game Theater with a symbolic court, all twelve roster athletes, real recorded plays, lineup changes, clock and score progression, replay speed, and replay-last-game control.
- Provides a read-only League Viewer with standings, the complete archived schedule, public rosters and ratings, availability, per-game minutes, prediction probabilities, pregame commitments, and replay hashes.
- Opens every League Viewer result in the Game Theater as a full archived playback and verifies the reconstructed score and player minutes before display.
- Provides thirteen stable Athlete Career Profiles across four verified seasons, with explicit ages, bounded development and decline, preserved retired history, stable incoming roster identity, cumulative totals, selectable season splits, and direct cross-roster replay links.
- Shows the final score, decision count, activity tape, training state, and approved $5 experiment ceiling.
- Includes a clearly marked training-visual preview so the intended presentation can be reviewed before actual model training exists.
- Provides navigation for Overview, Brains, Athletes, Simulation, Content, World / League, Operations, and Audit.
- Exposes real seeded-simulation and status-refresh controls with strict server-side input validation.
- Persists successful admin actions as JSON lines in the ignored local file `brain_admin/admin-audit.log`.
- Shows clothing, items, economy, moderation, release controls, and other absent systems as locked or read-only boundaries rather than fake controls.

## Security boundary

The server is hard-bound to `127.0.0.1`. There is intentionally no login screen because no real authentication exists yet. Authentication, secure sessions, least-privilege role-based access control, and deployment hardening are mandatory before any network exposure. The local audit actor is labeled `local-admin`; that label is not an authenticated identity.

## Phase 0D integration validation

The 2026-07-15 integration pass confirmed the committed D.2 rotation/minutes, D.3 availability/recovery, and D.4 public-prediction gates through all 38 regression tests, the Admin Console self-check, and fresh deterministic runs. The D.2-D.4 reports remain historical evidence for their named engine/state versions; current reruns use engine `phase05h-v1` and league `phase05r-v1` and must not overwrite those earlier measurements.

Live localhost checks confirmed server-side seed guards, an audit entry surviving a server restart, read-only minutes/availability/prediction evidence, executable brain/engine/league/policy versions, and locked clothing/items/economy/moderation controls. Browser checks confirmed the Observatory animation at desktop and 390-pixel mobile widths with no console errors or horizontal page overflow. External cost remained `$0.00`; no paid API, credits, wagering, monetization, deployment, or retraining was used.

## Truth rule

Animation must never imply that model weights are changing when no training job is active. The current Basketball Brain is deterministic `baseline-v2`; Phase 0C proved the guarded LLM contract, not a trained neural network.

The Game Theater follows the same truth rule: event labels, lineups, clock, and scores are authoritative, while marker coordinates are illustrative because physical player locations are not yet simulated.

Phase 0.5I evaluates Athlete Life Brain v1 outside the interface. It reconstructs all 80 archived games and measures 912 choices, policy compliance, readiness exposure, and a fixed-seed zero-readiness comparison. These are simulator diagnostics, not neural-network training, learned behavior, or real-world performance claims; Admin Console behavior is intentionally unchanged.

Phase 0.5J defines a future fictional practice/social off-day preference and a version-safe history contract. It is not active in the Observatory or simulator. The displayed Athlete Life Brain remains v1 until a fresh v2 archive passes its own evaluation; archived v1 decisions must never be reinterpreted under later rules.

Phase 0.5K adds v2 only as an explicit local pilot path and produces a separate fixed-seed archive. The Admin Console deliberately remains on default v1; showing or promoting v2 waits for multi-seed evidence. Preference-group animation must not imply learning, personality inference, or neural-network training.

Phase 0.5L evaluates v1 and v2 across 800 paired games per policy. The stability guardrails pass, but v2 remains unpromoted and invisible in the Admin Console. Winner differences and animated comparisons are path-sensitive simulator telemetry, not accuracy, intelligence, or real-world realism.

Phase 0.5M approved v2 for a controlled promotion without changing runtime behavior at that gate. Approval was an engineering release decision, not evidence of learning or a neural-network training event.

Phase 0.5N makes v2 the default for newly generated Admin and league decisions. Frozen Phase 0.5I, Phase 0.5L, and Phase 0D.4 paths remain explicitly v1, while every saved decision and replay manifest retains its stored version. The interface derives each season label from those stored decisions and reports the current v2 default as `ACTIVE DEFAULT`. Changing the default requires an Admin process restart because payloads are cached.

Phase 0.5O defines one possible short-term routine streak for a future opt-in v3 but changes no runtime or Observatory behavior. The state is reconstructible from same-season decisions, expires at rest/recovery and season boundaries, and may only vary the existing train/socialize choice after two identical elective decisions. It is a mechanical pilot design—not learned memory, personality, discipline, partying, or model training. V2 remains displayed as the active default.

Phase 0.5P implements that rule only through an explicit v3 policy path and evaluates it outside the interface across 800 fresh paired games per policy. Its integrity and provisional stability alarms pass, making v3 eligible for a later review only. The Observatory remains on v2 and must not animate this result as neural-network training, learning, personality growth, or a promotion.

Phase 0.5Q approves v3 for a separate controlled rollout but changes nothing in the Observatory. Before v3 can become the displayed default, the Admin prediction study must carry the same season-local routine mapping as its league archive, all historical evidence must stay explicitly version-pinned, and rollback must remain a single default change plus process restart. Until that gate passes, v2 remains `ACTIVE DEFAULT`.

Phase 0.5R satisfies that gate. The Observatory now displays v3 as `ACTIVE DEFAULT`; Admin league and prediction paths share its season-local routine transitions and agree on winners and replay hashes. V1/v2 archives remain version-pinned, rollback remains one constant plus restart, and the animation still represents observable deterministic decisions—not learned memory or changing neural weights.

Phase 0.5S rechecks that rollout without changing runtime behavior. The four-season archive contains 119 bounded routine variations across 507 eligible decisions with zero rule violations; the first triggering archive, Season 1 Game 4, completes its exact 108-93 replay at frame 452/452 with `ARCHIVE VERIFIED`. Prediction, persistence, historical digest, full regression, and Admin self-check evidence remain clean. These visuals show auditable recorded transitions, not neurons, training, personality inference, or real-world learning.

Phase 0.5T defines one possible chronology-safe `recent_scoring_form` input for a future opt-in v4 but changes no runtime or Observatory behavior. It reads only the immediately previous game's points and the athlete's earlier same-season appearance average, expires after one decision, and keeps recovery, fatigue rest, and v3 routine variation above it. The current retrospective five-game form display is not a policy input because its completed-season baseline would leak future games during simulation. V3 remains `ACTIVE DEFAULT`; this proposal is deterministic scoring telemetry, not overall performance, confidence, personality, learning, or neural training.

The League Viewer follows the Phase 0D.4 public-information boundary. Hidden fatigue, recovery timers, injury-risk internals, seeds, RNG state, economy data, and admin mutations stay outside its payload.

Archived games reuse hidden authoritative league state only on the server. The browser receives the complete recorded play-frame stream and verified archive metadata, never the hidden reconstruction inputs.

Athlete profiles keep durable specialty identity separate from temporary form. Lifecycle v1 applies fictional age, bounded development/decline, and age-35 retirement; roster continuity v1 preserves Roman's retired record and introduces Soren Lake in Season 4. Athlete Life Brain v2 now drives new train, rest, recover, or socialize choices and shows each athlete's bounded next-game effect. Historical seasons continue to display their stored policy version. Hidden readiness, fatigue, recovery timers, and seeds remain private; contracts, draft/free agency, stories, legal events, and permanent life-driven rating changes remain inactive.

When genuine training is approved, connect provider progress, dataset version, candidate version, validation metrics, estimated and actual cost, and promotion-gate results to the existing interface. Hosted LLM internals remain opaque, so the Observatory will display observable telemetry rather than fabricated neuron activations.

## Expansion direction

The Observatory is now the primary module inside the first general [[Design/Decisions/DEC-005 Game Admin Console|OddsWell Game Admin Console]] shell. New controls will be added only when their underlying game systems exist. Clothing and item activation, world operations, releases, support, economy administration, and protected AI-version controls are planned categories rather than implemented permissions.

## Source

- Server: `brain_admin/server.py`
- Interface: `brain_admin/index.html`
- Launcher: `Start Brain Observatory.cmd`
