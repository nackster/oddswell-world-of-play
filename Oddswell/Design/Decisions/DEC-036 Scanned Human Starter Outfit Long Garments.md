---
tags:
  - decision
  - character
  - wardrobe
status: owner-decision
date: 2026-10-20
---

# DEC-036 Scanned Human Starter Outfit Long Garments

## Context and authority

[[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]] requires a worn off-white starter top and bottom as replaceable equipment. It does not specify shorts or short sleeves. The earlier procedural character used synthetic shorts, and the October 20 handoff assumed shorts for the accepted scanned human. The licensed scan has no bare-leg or bare-forearm geometry beneath its suit, so shorts or a t-shirt would require a separate compatible body source.

On 2026-10-20 the owner chose the recommended option: build the starter outfit as long garments over the accepted scan, and defer shorts until a body source is selected.

## Decision

For the scanned-human direction, the starter outfit is an off-white long-sleeve top, off-white long bottoms (cuffed joggers) and casual sneakers. Each is a separate skinned shell on the scan's shared 88-bone rig. The scan's face, body, UVs, weights, bind matrices and packed maps stay unchanged.

The Signal Jacket continues to replace the starter top, matching the existing runtime rule. The bottoms and sneakers remain visible with it.

## Boundaries

- Shorts, short sleeves and other exposed-limb garments wait for an approved underlying body source. That choice also bears on the eight preset IDs and four tones, so it belongs with the production rig/preset/export contract in milestone 2.
- This changes no catalog identity, price, slot, save format or runtime behavior.
- It is not visual acceptance; the candidate review records its own status.

Evidence: [[Art/Production/SundaleStreetSlice/ScannedStarterOutfitCandidate/README]].
