---
tags:
  - development
  - tooling
  - process
  - index
status: active
---

# Project Tool Register

This register is the searchable source of truth for which tools OddsWell uses, why they are used, their status, and what would cause the decision to change. The visual overview is [[Visual Maps/Project Tool Map]].

## Status definitions

- **Primary:** The project's current source-of-truth tool for that responsibility.
- **Active:** Available and approved for its stated use.
- **Pilot:** Being tested on a limited representative asset or workflow.
- **Pending:** Needed, but the product or implementation choice is not yet approved.
- **Deferred:** Not needed yet; keep a defined reason and revisit trigger.

## Current register

| Area | Tool or system | Status | Responsibility |
| --- | --- | --- | --- |
| Project knowledge | Obsidian | Primary | Local project brain for decisions, plans, art direction, research, and visual maps. |
| Development collaboration | Codex | Active | Research, design support, implementation, documentation, testing, and maintaining the project brain during active work. |
| Development method | Ponytail | Active | Adopted full-mode development workflow. |
| Sports decision AI | Baseline policy → LLM decision policy | Phase 0A active; provider pending | Choose athlete and coach action intents through a strict structured-action contract. |
| Simulation authority | Deterministic sport rules engines | Phase 0B calibrated baseline | Validate legal actions, resolve consequences, and produce replayable event logs. |
| Simulation analytics | Phase 0B batch analyzer | Active | Aggregate team/player box scores, evaluate calibration guardrails, and generate reproducible reports from versioned event logs. |
| Shared athlete simulation | Athlete Life Brain | Planned after stable basketball loop | Model persistent personalities, memory, relationships, habits, training, rest, social choices, and career consequences across sports. |
| AI learning | Memory + versioned evaluation loop | Planned | Learn from structured history immediately and promote tested policy, prompt, fine-tune, or model versions deliberately. |
| Source control | [GitHub](https://github.com/nackster/oddswell-world-of-play) | Active; private | Version control, branches, reviews, CI, and release history for the project. |
| Local source control | Git 2.49.0 | Active | Local versioning client verified during Phase 1A.0. |
| Repository administration | GitHub CLI 2.96.0 | Active | Create and administer the project repository from the local workstation. |
| Large asset versioning | Git LFS 3.6.1 | Active | Version large binary assets through Git using the project tracking policy in `.gitattributes`; no large 3D/engine assets are tracked yet. |
| Work tracking | GitHub Issues/Projects | Active | Track executable tasks, bugs, pull requests, milestones, and roadmap views without adding another planning service. |
| Build automation | GitHub Actions | Pending tests | Run automated tests and builds; consider a private self-hosted runner on project servers after the repository is secured. |
| Agent orchestration | Ruflo | Deferred | Revisit after the Phase 0 simulator exists and parallel automation would provide measurable value. |
| Visual references | Higgsfield | Active subscription | Controlled character and item references, turnarounds, storyboards, and cinematic exploration. |
| 3D production | Blender 4.5.5 LTS | Primary; installed and verified | Final geometry, topology, UVs, materials, optimization, LODs, collision, rigs, and exports. |
| Image to 3D | Meshy | Pilot | First-pass props and environment objects before Blender cleanup. |
| Character rigging | Rigify | Primary | Controllable production rigs for main characters. |
| Fast rigging | AccuRIG | Active alternative | Rapid humanoid rigs for prototypes or imported meshes. |
| Human/NPC generation | Character Creator + Headshot | Deferred | Revisit if the approved style and NPC volume justify it. |
| Local image to 3D | TRELLIS.2 / Hunyuan3D | Deferred | Benchmark on project servers when volume, privacy, or per-generation cost justifies setup. |
| Engine distribution | Epic Games Launcher 1.3.150.0 | Installed; pilot delivered | Installed the owner-approved UE 5.8 default bundle and preserved its manifests and Build Patch success evidence. |
| Native build toolchain | Visual Studio 2022 + MSVC 14.44 + Windows SDK 10.0.22000.0 + VC++ x64 runtime 14.51.36247.00 | Present; prerequisite aligned, package compatibility pending | The official Microsoft x64 runtime update and required owner reboot passed; UE 5.8 no longer shows the earlier prerequisite warning. |
| Runtime | Unreal Engine 5.8.0 CL 55116800 | Pilot installed; blank project verified | `client/OddsWell` reopens with one empty default map, ray tracing off, no code/plugins/Starter Content, LFS coverage, and ignored generated outputs. Package, performance, replay, and permanent-adoption evidence remain pending. |
| Runtime candidate | Unreal Engine 5.8 | Active pilot; adoption pending | Benchmark the smallest packaged Windows project, one representative street block, and the authoritative recorded replay before adoption. |
| Game backend | Nakama | Pilot after Phase 0 | Self-hosted accounts, social systems, matchmaking, leaderboards, tournaments, chat, and server runtime. Keep purchased-credit accounting in a dedicated auditable ledger design. |
| Procedural environment | Blender Geometry Nodes | Active; included | First choice for repeated city assets and rule-based placement before considering Houdini. |
| Texture production | Substance 3D Painter | Phase 1 pilot | Benchmark one hero character and one city prop before purchasing or standardizing. |
| Motion capture | Rokoko Vision | Phase 1 pilot | Test short basketball motions before evaluating paid mocap tools or hardware. |
| Payments | Payment provider | Pending compliance gate | No implementation until legal, platform, age-rating, fraud, refund, and regional requirements are understood. |

## Capability coverage to track

| Capability | Needed by | Current state |
| --- | --- | --- |
| Game and economy design | Phase 0 | Active design work; formal balance rules still required. |
| Deterministic simulation engineering | Phase 0 | Next implementation focus. |
| Backend, identity, ledger, and security | Phase 0.5 | Architecture pending. |
| UI/UX and accessibility | Phase 0.5 | Direction pending. |
| 3D modeling and technical art | Phase 1 | Pipeline selected; production benchmark pending. |
| Rigging and animation | Phase 1 | Tool roles selected; deformation benchmark pending. |
| Environment art and lighting | Phase 1 | Depends on first-city identity and engine selection. |
| QA, balancing, telemetry, and live operations | Before public testing | Process and tools pending. |
| Legal, payments, gambling, platform, privacy, and age-rating review | Before monetized wagering or credit sales | Mandatory external compliance gate. |

## Operating rules

1. Every adopted tool must have one defined responsibility; overlapping tools require a benchmark or clear fallback purpose.
2. Paid Higgsfield or other metered generations require notice to the project owner before credits are consumed.
3. Store approved prompts, settings, reference images, licenses, source URLs, and generation dates with the resulting asset.
4. Generated content remains exploratory until it passes the appropriate visual, technical, performance, and licensing gates.
5. Record important tool changes as decisions, including the reason and revisit trigger.
6. Review this register at the end of each major phase and whenever a tool creates recurring cost, lock-in, security, or licensing risk.

See [[Development/Tool Efficiency Review]] for the ordered shortlist and evaluation gates.

## Required asset record

Every production asset should eventually record:

- Asset ID, name, class, owner, and current status.
- Original source or generation tool.
- Prompt, seed, model/version, settings, and generation date when applicable.
- License and commercial-use evidence.
- Approved reference family and style version.
- Blender source file and exported engine files.
- Polygon, texture, LOD, collision, rig, and animation information.
- Review history and final approver.
