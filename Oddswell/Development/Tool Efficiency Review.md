---
tags:
  - development
  - tooling
  - efficiency
  - evaluation
status: active
reviewed: 2026-07-13
---

# Tool Efficiency Review

## Objective

Add a tool only when it removes a demonstrated bottleneck, integrates cleanly with the chosen source-of-truth tools, and saves more time than it adds in setup, maintenance, licensing, training, and migration risk.

## Local readiness snapshot

Checked on 2026-07-13:

- Git is available.
- Git LFS 3.7.1 is installed and configured for the project tracking policy.
- Docker Desktop CLI 28.1.1 is installed; its Linux engine was not running during this check.
- Blender 4.5.5 LTS is installed in the user's local programs directory, exposed on the user `PATH`, and pinned as the approved production version.
- Unreal Editor, Unity, and Godot were not detected on `PATH`. This does not rule out an installation that is not exposed on `PATH`.
- The OddsWell workspace is a local Git repository on `main`, connected to the private [nackster/oddswell-world-of-play](https://github.com/nackster/oddswell-world-of-play) repository.

## Recommended order

### 1. Establish source control — complete

**Stack:** Private GitHub repository + current Git LFS + GitHub Issues/Projects.

Use GitHub for executable work: code, issues, pull requests, CI results, and release history. Keep Obsidian as the local design brain and decision record; do not duplicate long-form design notes into a second planning product.

The initial Git LFS policy covers Blender files, 3D exchange formats, source textures, audio, video, and Unreal binary assets in the root `.gitattributes` file.

Once automated tests exist, add GitHub Actions. The project owner's servers can later host build runners, but self-hosted runners should be attached only to a private, tightly controlled repository.

### 2. Install and pin Blender — complete

Blender 4.5.5 LTS is installed and recorded as the approved 3D source of truth. Do not let artists or automation silently migrate source files between unapproved versions.

Use Blender Geometry Nodes before adding Houdini for repeated city elements, street furniture, crowd placement, building variations, and rule-based environment assembly.

### 3. Run a narrow engine benchmark — before Phase 1

**Front-runner:** Unreal Engine 5.8.

This is an inference from the one-city 3D scope: Unreal's World Partition, HLOD, Data Layers, character tooling, and PC focus make it the strongest first candidate. The benchmark should still test a real OddsWell slice before adoption.

Benchmark one street block containing:

- One basketball court.
- One rigged player character with representative animation.
- Representative buildings, props, lighting, materials, collision, and navigation.
- Several placeholder NPCs.
- A headless/server-authoritative connection stub.
- A reproducible packaged PC build with frame-time, memory, build-time, and asset-iteration measurements.

Compare with Unity 6 only if the Unreal test exposes a serious productivity, hardware, deployment, or team-skill problem. Record licensing and revenue-model implications before the final decision.

### 4. Pilot Nakama after the deterministic simulator exists

**Purpose:** Self-hosted authentication, profiles, storage, matchmaking, leaderboards, tournaments, social features, chat, and server runtime integration.

Nakama is a good architectural candidate because it can run on project-controlled infrastructure and has official Unreal, Unity, and Godot clients. Use Docker for an isolated proof of concept after Phase 0.

Do not treat a generic game-wallet feature as the sole financial ledger for purchased or wagered credits. The unified-credit design requires a separate server-authoritative, append-only transaction model with idempotency, reconciliation, fraud controls, audit history, and compliance review.

### 5. Pilot art accelerators at the first production asset

#### Substance 3D Painter

Test on one approved hero character and one representative city prop. Adopt only if smart materials, masking, baking, and engine exports materially reduce texture-production and revision time compared with Blender alone.

#### Rokoko Vision

Test free single-camera capture on short basketball motions such as idle stance, dribble, pass, shot, rebound, and defensive shuffle. Evaluate foot sliding, hand/ball interaction, cleanup time, retargeting quality, and whether dual-camera or paid hardware would be justified.

## Deliberately deferred

- **Houdini:** Add only when Geometry Nodes cannot meet a measured procedural-city need.
- **Perforce:** Add only when Git LFS causes persistent binary-locking, repository-size, or team-concurrency problems.
- **FMOD or Wwise:** Evaluate when interactive audio implementation begins.
- **Sentry, analytics, and live-operations suites:** Evaluate when there is a playable client/server build to observe.
- **PlayFab or another managed backend:** Compare only if self-hosting Nakama becomes an operational burden.
- **DeepMotion and additional mocap services:** Compare only if Rokoko Vision fails the benchmark.
- **Ruflo:** Keep the existing Phase 0 revisit trigger.

## Tool intake gate

Before adopting or buying any new tool, record:

1. The exact bottleneck it addresses.
2. The existing tool or manual workflow used as the baseline.
3. One representative pilot task or asset.
4. Setup, subscription, usage, storage, compute, and exit costs.
5. Data location, privacy, security, commercial-use rights, and license constraints.
6. File formats, source-of-truth ownership, versioning, and migration path.
7. Measured production time, cleanup time, output quality, and revision difficulty.
8. Adopt, defer, or reject decision with a revisit trigger.

## Primary references

- [Git LFS](https://git-lfs.com/)
- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub self-hosted runners](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners)
- [Unreal Engine World Partition](https://dev.epicgames.com/documentation/unreal-engine/world-partition-in-unreal-engine)
- [Unreal Engine licensing](https://www.unrealengine.com/license)
- [Unity pricing changes](https://unity.com/products/pricing-updates)
- [Nakama](https://heroiclabs.com/nakama/)
- [Substance 3D Painter](https://www.adobe.com/products/substance3d/apps/painter.html)
- [Rokoko Vision](https://www.rokoko.com/products/vision)
- [Blender Geometry Nodes](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/)
