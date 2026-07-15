# OddsWell: World of Play

> Build a life. Back a team. A world in play.

OddsWell is a persistent 3D basketball and lifestyle game beginning with one city, a deterministic sports simulation, and a unified credit economy.

Private repository: [nackster/oddswell-world-of-play](https://github.com/nackster/oddswell-world-of-play)

## Current stage

The project is in early concept and pre-production. The immediate development focus is a deterministic, auditable basketball simulation before the 3D vertical slice.

## Project brain

The canonical local Obsidian vault is [`Oddswell/`](Oddswell/). Start with [`Oddswell/00 Home.md`](Oddswell/00%20Home.md).

## Production defaults

- Initial platform: PC / Steam
- 3D source of truth: Blender 4.5.5 LTS
- Source control: private GitHub repository with Git LFS 3.7.1 for large binary production assets
- Project knowledge: local Obsidian vault
- Development approach: Ponytail full mode

Confirmed decisions and detailed plans belong in the Obsidian vault. Executable work belongs in source control, issues, tests, and builds.

## Phase 0A simulator

The first headless basketball simulator lives in [`phase0a/`](phase0a/). It uses only Python's standard library.

```powershell
python phase0a/simulator.py --seed 42 --log phase0a/game-42.jsonl
python -m unittest discover -s phase0a -p "test_*.py" -v
```

Phase 0B analyzes reproducible batches and writes the tracked Obsidian baseline report:

```powershell
python -m phase0b.analyze --games 1000 --output "Oddswell/Development/Reports/Phase 0B Baseline.md"
python -m unittest phase0b.test_analyze -v
```

Phase 0C adds the guarded, provider-neutral LLM action boundary and runs a no-cost offline integration pilot:

```powershell
python -m phase0c.pilot --games 10 --calibration-games 1000 --fairness-seed-pairs 100 --output "Oddswell/Development/Reports/Phase 0C Offline LLM Policy Pilot.md"
python -m unittest phase0c.test_policy -v
```

The offline fixture proves validation, deterministic fallback, telemetry, and replay. It is not a live LLM; a live pilot requires an approved provider and cost/latency budget.

Phase 0D begins the deterministic league layer with a balanced schedule and standings:

```powershell
python -m phase0d.league --games 20 --start-seed 10000 --output "Oddswell/Development/Reports/Phase 0D Schedule and Standings.md"
python -m unittest phase0d.test_league -v
```

Phase 0D.1 established versioned multi-season persistence and bounded fatigue. Its historical evidence remains in [`Phase 0D1 Multi-Season Fatigue.md`](Oddswell/Development/Reports/Phase%200D1%20Multi-Season%20Fatigue.md).

Phase 0D.2 adds one reserve per team, deterministic lineups, authoritative minutes, and minutes-driven workload:

```powershell
python -m phase0d.league --games 20 --seasons 1 --start-seed 12000 --output "Oddswell/Development/Reports/Phase 0D2 Rotation Minutes and Workload.md"
python -m unittest phase0a.test_simulator phase0b.test_analyze phase0c.test_policy phase0d.test_league -v
```

## Local Admin Console

Double-click [`Start Brain Observatory.cmd`](Start%20Brain%20Observatory.cmd) to open the local-only Admin Console. Its primary Brain Observatory module visualizes the six brain/authority components, runs a real seeded game through the current simulator, and animates its recorded decision and outcome flow. General navigation now covers Overview, Brains, Simulation, Content, World / League, Operations, and Audit.

Only seeded simulation and status refresh are operational controls today, and successful actions are written to `brain_admin/admin-audit.log`. Clothing, items, economy, moderation, releases, and other unbuilt systems are clearly locked rather than represented by fake switches. The training preview is explicitly a visual demonstration; it does not claim model weights are changing.

The server binds only to `127.0.0.1`. It intentionally has no pretend login: authentication, role-based access control, and secure deployment are required before any network exposure.
