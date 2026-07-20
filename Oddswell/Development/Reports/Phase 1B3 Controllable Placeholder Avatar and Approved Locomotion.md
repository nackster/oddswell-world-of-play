---
tags:
  - development
  - beta
  - unreal-engine
  - character
  - locomotion
status: complete
date: 2026-07-20
---

# Phase 1B.3: Controllable Placeholder Avatar and Approved Locomotion

## Outcome

OddsWell now packages and visibly runs one neutral, noncanonical primitive avatar in the existing BlockCourtBenchmark. The local player can use the approved third-person trailing camera and native walk, held run, look, and jump routes.

## Implementation

- `AOddsWellPlaceholderCharacter` reuses UE 5.8's native `ACharacter`, capsule collision, `CharacterMovement`, spring arm, camera, and built-in cylinder/cube meshes. The inherited skeletal component has no mesh, rig, or animation and is hidden with collision disabled.
- The separate locomotion game mode spawns one transient pawn at `(0, 0, 220)` above the benchmark center and leaves both tracked maps unchanged.
- Placeholder calibration is walk speed `260`, held-run speed `520`, jump velocity `520`, camera distance `420`, pitch `-65 degrees` to `65 degrees`, and yaw `-180 degrees` to `180 degrees`. Spring-arm camera collision is enabled.
- Keyboard/mouse controls are W/S forward-back, A/D strafe, mouse look, held Left Shift run, and Space jump. Controller controls are left-stick move, right-stick look, held left-stick click run, and bottom face button jump.
- Crouch, flight, swimming, combat, attack, parkour, vehicle entry, and generalized abilities are absent. The native movement component is the only movement authority.
- Opt-in local QA drives and records one walk/look/run/jump/landing sequence. Normal play does not auto-drive or auto-exit.

## Measured packaged proof

The accepted R4 Development package produced exactly one READY record, one QA start, and one PASS record:

`start=V(Z=118.15) | end=V(X=-1644.51, Z=98.15) | walk_peak=260.0 | run_peak=520.0 | max_jump=118.0 | landed=true | floor_blocking=true | yaw_delta=180.0`

The 20-unit end-height difference is the avatar stepping from the raised center marking onto the adjacent blocking court floor, not falling through the map. The held-run peak was twice the walk peak, and the movement limit returned to `260` before the final evidence record.

Computer Use verified one unobstructed packaged window with exactly one vertical cylinder body and cube head, viewed from the trailing camera against the existing court/block geometry. No final body, face, hair, proportions, skeletal asset, rig, animation, or clothing art is claimed.

## Validation

- Final UE 5.8 `OddsWellEditor` Development build: **passed**, 4 actions in `5.98s`.
- Final UE 5.8 `OddsWell` Development game build: **passed**, 3 actions in `14.16s`.
- Native `OddsWell.Character` automation: **3/3 passed** for locomotion defaults, the Phase 1B.1 catalog, and the unchanged Phase 1B.2 selection state.
- Final R4 Windows BuildCookRun: **passed** with exit code `0` in `54.15s`; both tracked maps were cooked. The static archive contains 49 files totaling `1,041,050,707` bytes.
- Packaged QA: one PASS, zero fatal/assert/unhandled matches, and clean auto-exit. No related game, editor, Trace, or shader process remained after validation.
- The rebuilt executable surfaced a Windows Firewall prompt during visual capture. Automation did not interact with it or change any security setting. After sleep/resume, the owner reported no popup was visible; the bounded visual check confirmed the game window was unobstructed with no security overlay or other modal.
- While the visual run was alive, only the explained local TCP listener `0.0.0.0:1985` appeared. No established remote TCP connection or UDP endpoint was observed.
- Frozen Python regression suite: **65/65 passed** in `161.990s`.
- Brain Admin self-check and Python compilation: **passed**.
- Obsidian links, Beta Delivery Roadmap canvas JSON, frozen map/replay hashes, Git LFS and ignored-output rules, Android network/token boundary, related-process cleanup, whitespace, and scoped-diff checks: **passed**.
- Controller routes are covered by native automation; no physical controller hardware was tested.
- Cost: **$0.00**.

A pre-final QA run exposed the benchmark center marking's 20-unit height step and a yaw-bound measurement issue; the proof was corrected to measure a valid blocking-floor landing and reset the QA camera after GameMode restart. One fresh packaging attempt also hit a transient local Zen staging connection refusal; subsequent fresh R3 and accepted R4 packages succeeded without changing code or network/security settings.

## Preserved evidence and boundary

- `Bootstrap.umap` remains SHA-256 `44fc5e531591672e10e3740a780eafb34326c2eadc7d85a37cfa352541932c16`.
- `BlockCourtBenchmark.umap` remains SHA-256 `f970a2f4609f2d6ec24475ae48c98e12db53bde2cd95a238f2015c3ff0840018`.
- The tracked replay fixture remains SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, with the authoritative replay seal and 421-frame no-resimulation path unchanged.
- Phase 1B.2 remains session-local. This phase does not transfer a selected preset into the pawn or add onboarding travel, save/reload, clothing components, demographic effects, player attributes, accounts, multiplayer, city identity, NPCs, economy, wagering, backend, deployment, paid content, model work, retraining, or Phase 0 changes.

The next smallest gate is **Phase 1B.4: render the worn off-white starter top and bottom as separate replaceable equipment on the placeholder**, without final art or persistence.
