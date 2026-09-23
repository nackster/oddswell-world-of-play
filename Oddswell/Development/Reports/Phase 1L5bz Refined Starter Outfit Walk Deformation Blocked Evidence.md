# Phase 1L.5bz refined starter-outfit walk deformation blocked evidence

**Status:** BLOCKED / UNCOUNTED — fail-closed at frame 2
**Date:** 2026-09-23
**Cost:** $0

## Outcome

The exact accepted Phase 1L.5bv body, 1L.5bw starter top, and 1L.5bx starter bottom were composed on the sole accepted twelve-bone skeleton with the current unchanged `walk_candidate_v1` from `CharacterMotionAxisCorrection`. Exact source, mesh, bone, twelve-entry DEC-035 mapping, Action, topology, and normalized-weight custody passed before evaluation: body `58,324/0/0`, top `8/0/0`, and bottom `7,159/0/0` vertices/unweighted/invalid-or-non-normalized.

The every-integer-frame gate passed frame `1`, then failed closed at frame `2` (`0.035714286 s`) with `587` evaluated body/bottom BVH triangle overlaps. Body/top and top/bottom overlaps remained `0`. Per the approved gate, no accepted mesh, weights, Action, thresholds, or runtime input was repaired; later frames were not evaluated and no derivative Blend was written.

## Deterministic evidence

| Evidence | Result |
| --- | --- |
| Failure receipt | `11,290` bytes; SHA-256 `57D8193B8F50117B0B574FE3D7337FEA53AC4BA202057BCBB9A261FC72EFBD9C` |
| Diagnostic builder | `15,856` bytes; SHA-256 `B77B2539EE91AA4AD18B28E546469F570CE8AC4766E3795B9E3FDC0479AAC7AF` |
| Transient fail log | `1,299` bytes; SHA-256 `4234F0CC9F916A6AD807912A10ECAF312D6D126D934D9EC2C7474B94D34CEA3C`; exact process exit `1` |
| Body / top / bottom mesh identities | `F340C34B...BF03CD` / `9996AF8A...D30C3` / `ED49AEDD...8BDF96` |
| Current corrected walk semantic | `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`; action name/timing/values unchanged |

Frame `1` had intersection counts `0/0/0`. Bidirectional vertex-sampled minimum clearance was `0.042323530 m` for body/top and `0.004069991 m` for body/bottom. At frame `2`, body/top and top/bottom remained `0`, while body/bottom became `587`; the receipt retains exact frame-indexed bounds and the passed frame-1 record. Root-bone and armature translation are exact `[0,0,0] m` at both frames.

The method evaluates Blender meshes at every integer frame, checks triangle overlap with BVH, and samples both garment vertices to the body surface and body vertices to each garment surface. Clearance is vertex-sampled, not continuous triangle-distance proof.

## Boundaries

This is a measurement failure, not phase credit and not a repaired asset. No jacket, run, jump, land, hidden repair, FBX, UAsset, Unreal import, runtime/client/config/test/map/package input, gameplay authority, final art, performance, or readiness work occurred. Frozen regression suites were not rerun because the fail-first deformation gate stopped before product integration. Phase 1L.5bz remains blocked and uncounted; no Phase 7 exists.

See [[Development/Reports/Phase 1L5bv Refined Sundale Human Body Derivative Neutral Bind Proof]], [[Development/Reports/Phase 1L5bw Refined Sundale Starter Off White Top Neutral Bind Proof]], and [[Development/Reports/Phase 1L5bx Refined Sundale Starter Off White Bottom Neutral Bind Proof]].
