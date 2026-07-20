---
tags:
  - development
  - beta
  - unreal-engine
  - character
  - clothing
status: complete
date: 2026-07-20
---

# Phase 1B.4: Replaceable Starter Outfit

## Outcome

The packaged placeholder avatar now visibly wears the catalog-approved `starter_offwhite_top` and `starter_offwhite_bottom` as two separate, replaceable equipment components. The underlying primitive body and head remain separate, and the approved locomotion is unchanged.

## Implementation

- The existing validated Phase 1B.1 catalog remains the only runtime source for both equipment IDs. All eight presets still use exactly the same top and bottom with no gameplay modifiers.
- A minimal local two-slot state accepts only the catalog top in `Top` and the catalog bottom in `Bottom`. Unknown IDs, wrong-slot assignments, duplicate assignments, empty removal, and incomplete outfits fail locally with a clear error.
- `StarterOutfitTop` and `StarterOutfitBottom` are separately named, noncolliding native cube components. Each can be removed and restored independently while the neutral cylinder body and cube head remain present.
- Both components use one native dynamic material set to a visibly off-white placeholder color. This is noncanonical primitive proof, not fabric, final clothing, a skeletal asset, a rig, or animation.
- The safe preset is applied directly only after catalog validation. Phase 1B.2 selection is not transferred, saved, or persisted in this phase.
- Opt-in packaged QA removes the top while leaving the bottom and base body, restores the exact catalog top, validates the complete outfit, and logs both distinct component identities plus the unchanged `260` walk, `520` run, and `520` jump settings.

## Validation

- UE 5.8 `OddsWellEditor` Development build: **passed**, 5 actions; UnrealBuildTool completed in `19.29s`.
- Native `OddsWell.Character` automation: **4/4 passed** for locomotion defaults, preset catalog, selection state, and starter outfit state.
- UE 5.8 `OddsWell` Development game build: **passed**, 4 actions; UnrealBuildTool completed in `18.52s`.
- Fresh Windows Development BuildCookRun: **passed** in `93.87s`; both tracked maps were cooked. The isolated archive contains 49 files totaling `1,041,115,331` bytes.
- Fresh combined packaged QA produced exactly one outfit READY record with both IDs, slots, and `replaceable=true`; one top UNEQUIP record while the bottom and base remained; one outfit PASS with distinct restored `StarterOutfitTop` and `StarterOutfitBottom`; and one locomotion PASS with walk/run peaks `260/520`, a `118`-unit jump, blocking-floor landing, and `180`-degree camera-yaw change.
- Computer Use confirmed exactly one unobstructed noncanonical avatar with distinct off-white upper and lower primitive pieces over the separate base body/head in the existing BlockCourtBenchmark.
- The first fresh executable launch displayed Windows Firewall. Automation did not interact or change security settings; the owner clicked **Cancel**. The accepted rerun was unobstructed and showed no security overlay or modal.
- The accepted run exited cleanly with zero fatal, assert, unhandled, or outfit-error matches and left zero related processes. A separate bounded sample found only the explained local TCP listener `0.0.0.0:1985`, with no established remote TCP connection or UDP endpoint; it also closed with zero remaining related processes.
- Frozen Python regressions: **65/65 passed** in `138.963s`. Brain Admin self-check passed in `3.30s`, and Python compilation passed in `0.08s`.
- Obsidian links, Beta Delivery Roadmap canvas JSON, frozen map/replay hashes, Git LFS and ignored-output rules, Android network/token boundary, related-process cleanup, whitespace, and scoped-diff checks: **passed**.
- Cost: **$0.00**.

## Preserved evidence and boundary

- `Bootstrap.umap` remains SHA-256 `44fc5e531591672e10e3740a780eafb34326c2eadc7d85a37cfa352541932c16`.
- `BlockCourtBenchmark.umap` remains SHA-256 `f970a2f4609f2d6ec24475ae48c98e12db53bde2cd95a238f2015c3ff0840018`.
- The tracked replay fixture remains SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`; its authoritative seal, 421 frames, and no-resimulation path remain unchanged.
- No inventory, ownership, pricing, store, economy, wagering, account, backend, service, multiplayer, city, NPC, apartment, deployment, model, retraining, final character art, fabric, skeletal asset, rig, animation, hair, or face behavior was added.

The next smallest planned gate is **Phase 1B.5: locally save and reload the chosen preset and equipped starter outfit**, scoped separately before multiplayer persistence.
