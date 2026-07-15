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

## Current capabilities

- Shows the Project, Athlete Life, World and League, Basketball, Rules and Outcome, and Learning components.
- Reads the current engine, league, basketball brain, and LLM policy versions directly from the executable project.
- Shows the Phase 0D.4 public prediction-evaluation version as read-only World / League evidence.
- Runs a real seeded basketball simulation and animates a cinematic sample of its recorded decisions and outcomes.
- Provides a dedicated Game Theater with a symbolic court, all twelve roster athletes, real recorded plays, lineup changes, clock and score progression, replay speed, and replay-last-game control.
- Provides a read-only League Viewer with standings, the complete archived schedule, public rosters and ratings, availability, per-game minutes, prediction probabilities, pregame commitments, and replay hashes.
- Opens every League Viewer result in the Game Theater as a full archived playback and verifies the reconstructed score and player minutes before display.
- Provides twelve stable Athlete Career Profiles spanning three verified seasons, with explicit ages, bounded development and decline, preserved specialties, retirement status, cumulative totals, selectable season splits, and direct cross-season replay links.
- Shows the final score, decision count, activity tape, training state, and approved $5 experiment ceiling.
- Includes a clearly marked training-visual preview so the intended presentation can be reviewed before actual model training exists.
- Provides navigation for Overview, Brains, Athletes, Simulation, Content, World / League, Operations, and Audit.
- Exposes real seeded-simulation and status-refresh controls with strict server-side input validation.
- Persists successful admin actions as JSON lines in the ignored local file `brain_admin/admin-audit.log`.
- Shows clothing, items, economy, moderation, release controls, and other absent systems as locked or read-only boundaries rather than fake controls.

## Security boundary

The server is hard-bound to `127.0.0.1`. There is intentionally no login screen because no real authentication exists yet. Authentication, secure sessions, least-privilege role-based access control, and deployment hardening are mandatory before any network exposure. The local audit actor is labeled `local-admin`; that label is not an authenticated identity.

## Truth rule

Animation must never imply that model weights are changing when no training job is active. The current Basketball Brain is deterministic `baseline-v2`; Phase 0C proved the guarded LLM contract, not a trained neural network.

The Game Theater follows the same truth rule: event labels, lineups, clock, and scores are authoritative, while marker coordinates are illustrative because physical player locations are not yet simulated.

The League Viewer follows the Phase 0D.4 public-information boundary. Hidden fatigue, recovery timers, injury-risk internals, seeds, RNG state, economy data, and admin mutations stay outside its payload.

Archived games reuse hidden authoritative league state only on the server. The browser receives the complete recorded play-frame stream and verified archive metadata, never the hidden reconstruction inputs.

Athlete profiles keep durable specialty identity separate from temporary form. Lifecycle v1 now applies transparent fictional age, bounded development/decline, and age-35 retirement rules to the same ratings used by the games. Contracts, replacement players, personal-life decisions, and Athlete Life Brain consequences remain inactive.

When genuine training is approved, connect provider progress, dataset version, candidate version, validation metrics, estimated and actual cost, and promotion-gate results to the existing interface. Hosted LLM internals remain opaque, so the Observatory will display observable telemetry rather than fabricated neuron activations.

## Expansion direction

The Observatory is now the primary module inside the first general [[Design/Decisions/DEC-005 Game Admin Console|OddsWell Game Admin Console]] shell. New controls will be added only when their underlying game systems exist. Clothing and item activation, world operations, releases, support, economy administration, and protected AI-version controls are planned categories rather than implemented permissions.

## Source

- Server: `brain_admin/server.py`
- Interface: `brain_admin/index.html`
- Launcher: `Start Brain Observatory.cmd`
