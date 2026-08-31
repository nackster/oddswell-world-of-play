---
tags:
  - decision
  - character
  - phase-1l
status: accepted
date: 2026-08-31
---

# DEC-034 Shared-Skeleton Player-Character Production Candidate

## Owner response

The owner approved the recommended character-production direction:

> Option B — build a bounded shared-skeleton character candidate at `1.80 m` with one neutral beta silhouette.

## Decision

Authorize one faceless `1.80 m` production-candidate mannequin, one shared skeleton, and one neutral body silhouette for all eight existing gameplay-identical presets. The exact machine-readable contract is `Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json`.

The bridge may refit only `starter_offwhite_top`, `starter_offwhite_bottom`, and `sundale_signal_jacket`, then prove only walk, run, jump, and landing in Unreal on the existing character movement authority.

## Preserved boundaries

- The existing `ACharacter` movement, capsule collision, camera, replication, saves, appearance IDs, economy, inventory, wagering, simulator, and brain behavior remain authoritative and unchanged.
- The eight preset IDs and four approved skin tones remain exact; presentation labels do not select different geometry in this beta bridge.
- The Phase 1L.3g joint heights control the candidate: ankle `.10`, knee `.53`, hip `.94`, wrist `.78`, elbow `1.12`, shoulder `1.45`, head center `1.66`, and crown `1.80 m`.
- Cost remains `$0`; no external asset, paid service, marketplace download, plugin, or dependency is authorized.

## Not authorized

This decision does not approve final art, a second silhouette, faces, hair, body sliders, a deep creator, additional clothing, extra animation, retargeting frameworks, marketplace features, deployment, beta readiness, production readiness, Version 1, or post-Version-1 work.

## Next gate

Create and verify one deterministic Blender production-candidate source with the shared armature and neutral mannequin. Export/import, clothing refit, animation, and runtime replacement remain later separately verified subphases.

## Evidence

This decision closes the owner gate in [[Development/Reports/Phase 1L5bh Runtime Placeholder to Eight Preset Silhouette Compatibility Review and Owner Decision Packet]]. The bounded closure and contract freeze are recorded in [[Development/Reports/Phase 1L5bi Shared Skeleton Player Character Production Contract]].
