# Phase 1L.5bz-R1 starter-outfit walk repair failure

**Status:** BLOCKED / UNCOUNTED — fail closed at frame 3
**Date:** 2026-09-24

## Outcome

The approved bottom-only repair did not satisfy the required zero-intersection walk proof. No corrected Blend was accepted or written, no accepted input was mutated, and Phase 1L.5bz remains blocked and uncounted.

The deterministic closure reproduces two bounded trials against the exact accepted Phase 1L.5bv body, 1L.5bw top, 1L.5bx bottom, DEC-034/DEC-035 skeleton, and unchanged `walk_candidate_v1`:

1. A normalized root-dominant waistband and anatomically side-selected thigh blend fails at frame 2 with 219 body-bottom triangle pairs.
2. The same weights plus the permitted diagnostic position offset passes frames 1 and 2, then fails at frame 3 with 433 body-bottom triangle pairs.

The offset affects all 7,159 bottom vertices by 0.050 m away from the nearest neutral body surface, with an additional -0.010 m X correction on eight recorded contact vertices. Maximum displacement is 0.050990195 m. The derived diagnostic retains 7,159 vertices, 7,040 polygons, and the exact accepted material slot, but it is not an accepted asset.

## Deterministic evidence

- Builder: `build_starter_outfit_walk_repair.py`, 19,814 bytes, SHA-256 `5177CD42CFCE923AB0A27410102F76B6FA6FA579B02CDFDA55A1726308E290D7`.
- Failure receipt: `starter_outfit_walk_repair_failure.json`, 54,327 bytes, SHA-256 `B9B63EA4DC393EDD07CACF1733F2294CD723022EF604073AD551574B1D820C56`.
- Two consecutive Blender 4.5.5 executions exited 1 and produced the byte-identical receipt above.
- Second retained log: `C:\tmp\OddsWellPhase1L5bzR1-final2.log`, 1,299 bytes, SHA-256 `BCA039B94842C1302D87FCBA994D54CB2FA946EEA80775667721E789464751AA`; terminal marker: `REFINED_STARTER_OUTFIT_WALK_FAIL frame=3 body_bottom=433`.
- Diagnostic derived bottom semantic SHA-256: `A9C2825F62819AA5E71533ECEB24071C687EEA3B3BDAAED5220C9CC097F87143`.

The receipt separately locks all accepted source hashes, DEC-035 mapping, normalized weight counts, unchanged action identity, root and armature translations, passed-frame records, attempted correction parameters, and the final failing-frame polygon pairs.

## Boundary

This is durable blocker evidence, not a successful proof. It makes no frozen-suite, Brain Admin, package verification, runtime, final-art, performance, readiness, or completion claim. It earns zero phase credit, triggers no Notion completion sync, and authorizes neither a seventh phase nor broader character redesign.
