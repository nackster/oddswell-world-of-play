---
tags:
  - development
  - tooling
status: active
---

# Tooling Candidates

## Higgsfield AI

**Status:** Available subscription

Higgsfield may be used for character exploration, consistent reference characters, item and product-style concept sheets, storyboards, cinematic previsualization, and promotional imagery or video.

### Usage rule

- Tell the project owner before using paid Higgsfield generations or credits.
- Treat generated imagery as concept and reference material until explicitly approved.
- Preserve approved master references, prompts, colors, proportions, and style constraints in the local project brain.
- Do not treat generated images as final game-ready 3D assets.
- Final characters and items still require production modeling, topology, materials, rigging, animation, optimization, and engine integration.

### Reference

https://higgsfield.ai/

## Ruflo

**Status:** Deferred

Ruflo is an agent-orchestration framework offering multi-agent swarms, persistent vector memory, MCP tools, background workers, and development automation.

### Potential value

- Parallel simulation experiments.
- Automated test generation and review.
- Security and architecture audits.
- Repetitive development workflows.

### Why it is deferred

- The Codex adapter is currently an alpha release.
- Its generated Codex configuration includes unsafe defaults.
- Open Windows, MCP-transport, and memory-persistence fixes require validation.
- Its memory database would duplicate the Obsidian brain.
- The project does not yet have enough implementation complexity to justify the operational overhead.

### Revisit trigger

Evaluate Ruflo again after the Phase 0 basketball simulator exists in a Git repository. Test a pinned minimal version in an isolated folder before considering integration. Keep daemon, federation, cloud services, automatic updates, and unsafe Codex settings disabled during evaluation.

### Reference

https://github.com/ruvnet/ruflo

## 3D production stack

**Status:** Adopted for pilot use

- **Blender:** Primary source of truth for all production-ready 3D assets.
- **Rigify:** Primary controllable character-rig system.
- **Meshy:** Pilot image-to-3D service for props and environment first passes.
- **AccuRIG:** Fast alternative for automatic humanoid rigging.
- **Character Creator + Headshot:** Deferred unless the chosen style or NPC volume justifies it.
- **TRELLIS.2 / Hunyuan3D:** Later evaluation for private generation on project servers.

See [[Development/3D Asset Pipeline]] and [[Visual Maps/3D Asset Toolchain]].
