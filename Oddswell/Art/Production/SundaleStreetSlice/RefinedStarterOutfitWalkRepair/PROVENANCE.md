# Phase 1L.5bz-R1 failure provenance

- This directory records an uncounted, fail-closed bottom-only deformation repair attempt. It does not contain an accepted derived Blend.
- Exact accepted inputs remain the Phase 1L.5bv body, 1L.5bw starter top, 1L.5bx starter bottom, DEC-034/DEC-035 shared skeleton, and unchanged `walk_candidate_v1`.
- The deterministic builder first reproduces a normalized root/thigh weight-only trial, then applies the bounded diagnostic bottom position offset recorded in the receipt. It samples integer frames in order and stops at the first intersection.
- Weight-only fails at frame 2 with 219 body-bottom triangle pairs. The final diagnostic passes frames 1 and 2, then fails at frame 3 with 433 body-bottom triangle pairs.
- The final diagnostic offsets all 7,159 bottom vertices by 0.050 m away from the nearest neutral body surface and applies an additional -0.010 m X correction to eight recorded contact vertices. Maximum displacement is 0.050990195 m. Topology and the material slot remain unchanged.
- The accepted source bottom mesh identity and diagnostic derived mesh identity are separate receipt fields. Accepted inputs are never overwritten.
- No frozen regression, Brain Admin, package PASS, runtime integration, final-art, performance, readiness, phase credit, Notion sync, or phase advance is claimed.
