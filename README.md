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
