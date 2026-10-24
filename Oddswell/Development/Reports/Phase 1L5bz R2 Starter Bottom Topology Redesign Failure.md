# Phase 1L.5bz-R2 starter-bottom topology redesign failure

**Status:** BLOCKED / UNCOUNTED — fail closed at neutral topology
**Date:** 2026-09-26

## Outcome

The bottom-only topology-and-weight redesign did not produce an acceptable derivative. The initial diagnostic cleared the automated 21-frame intersection proof but failed mandatory visual review because it read as an oversized flared shell with a low hanging saddle. Those outputs were rejected and removed.

One coordinator-authorized bounded repair narrowed only the bottom profile and raised the saddle: upper X/Y 0.48/0.40 m, leg X/Y 0.30/0.36 m, and saddle height `0.58 + 0.04 * abs(2*t-1)^2` m. The exact repaired mesh remained one connected component with no non-manifold edges, but collapsed to one boundary loop instead of the required waist plus two leg openings. It failed before animation sampling.

The deterministic failure receipt preserves exact accepted custody, trial constants, and the measured neutral-topology result. No accepted body, top, bottom source, skeleton, action, runtime, client, or package input changed. No derived Blend or review image is retained.

## Boundary

This evidence is a repair-only blocker, not a successful Phase 6 proof. Frozen native/Python regressions, Brain Admin, package verification, and Unreal checks were intentionally not run because the focused topology gate failed. It earns zero phase credit, performs no Notion completion sync, and authorizes no next phase.
