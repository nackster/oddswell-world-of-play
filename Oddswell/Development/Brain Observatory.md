---
tags:
  - development
  - ai
  - admin
  - visualization
status: active
---

# Brain Observatory

The Brain Observatory is a local admin program for inspecting OddsWell's cooperating brains and authoritative systems.

## Open it

Double-click `Start Brain Observatory.cmd` in the project root. The launcher starts a local-only server and opens `http://127.0.0.1:8765`. Close the terminal window or press `Ctrl+C` there to stop it.

## Current capabilities

- Shows the Project, Athlete Life, World and League, Basketball, Rules and Outcome, and Learning components.
- Reads the current engine, league, basketball brain, and LLM policy versions directly from the executable project.
- Runs a real seeded basketball simulation and animates a cinematic sample of its recorded decisions and outcomes.
- Shows the final score, decision count, activity tape, training state, and approved $5 experiment ceiling.
- Includes a clearly marked training-visual preview so the intended presentation can be reviewed before actual model training exists.

## Truth rule

Animation must never imply that model weights are changing when no training job is active. The current Basketball Brain is deterministic `baseline-v2`; Phase 0C proved the guarded LLM contract, not a trained neural network.

When genuine training is approved, connect provider progress, dataset version, candidate version, validation metrics, estimated and actual cost, and promotion-gate results to the existing interface. Hosted LLM internals remain opaque, so the Observatory will display observable telemetry rather than fabricated neuron activations.

## Expansion direction

This program will become one module inside the general [[Design/Decisions/DEC-005 Game Admin Console|OddsWell Game Admin Console]]. New controls will be added only when their underlying game systems exist. Clothing and item activation, world operations, releases, support, economy administration, and protected AI-version controls are planned categories rather than implemented permissions.

## Source

- Server: `brain_admin/server.py`
- Interface: `brain_admin/index.html`
- Launcher: `Start Brain Observatory.cmd`
