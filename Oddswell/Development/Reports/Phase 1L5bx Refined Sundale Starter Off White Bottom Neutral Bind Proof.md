# Phase 1L.5bx refined Sundale starter off-white bottom neutral-bind proof

**Status:** COMPLETE — technical bottom-only derivative proof; not runtime or final art
**Date:** 2026-09-23
**Cost:** $0

## Outcome

The retained `Character | shorts leg continuous tailoring` input now produces exactly one non-destructive `starter_offwhite_bottom` around the accepted Phase 1L.5bv body. The derivative retains all `7,159` vertices and `7,040` polygons, the DEC-034 `1.80 m` body, the accepted twelve-bone hierarchy, and DEC-035 mapping. Cloth-only `Waist attachment` authority is discarded; the proof uses only `root`, `thigh.L`, and `thigh.R`.

The deterministic fit projects the retained shorts vertices to the accepted body surface with a `0.03 m` technical offset. This is deliberately a neutral-bind proof, not authored final tailoring.

## Deterministic custody

| Artifact | Identity |
| --- | --- |
| Retained source Blend | `635,844,146` bytes; SHA-256 `0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127` |
| Accepted Phase 1L.5bv body Blend | SHA-256 `83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB` |
| Accepted body custody | SHA-256 `2299550AA590235BC2D71753BAFE3CE59A2573F8F5900EE817B91E2DB59958A0` |
| Retained body semantic / mesh identity | `91AAB962...B8CF08` / `F340C34B...BF03CD` |
| Starter-bottom semantic identity | SHA-256 `2F05F9A2FBC3492A9DDB7FC1ED0C7BA1896058A87E0D9C02D64D8575B6A30FE4`, reproduced across two builds |
| Starter-bottom mesh identity | `7,159` vertices / `7,040` polygons; canonical SHA-256 `ED49AEDD3C65D9E9F5B13E2C9B9B0CF6614ABE19BCD7E666D396D1234E8BDF96` |
| Retained proof Blend | `33,599,449` bytes; SHA-256 `18103E29F0D22B14A16457F3A61D49F9EFE48E388D8BF3AFD2AB67FE4F5798CA` |

## Neutral-bind proof

- Exactly two mesh partitions and one armature exist: accepted body plus `starter_offwhite_bottom`; Actions are `0`.
- The exact accepted twelve bones and DEC-035 mapping remain unchanged; root translation is zero.
- All `7,159` bottom vertices have exactly one normalized influence: root `972`, left thigh `3,229`, right thigh `2,958`; unweighted and non-normalized counts are `0`.
- Coverage is `0.567481–0.960000 m`, spanning the upper legs through the DEC-034 hip at `0.94 m`.
- Body/bottom triangle intersection pairs are `0`.
- Bidirectional vertex-to-opposite-surface BVH sampling measures bottom→body `0.004069997 m`, body→bottom `0.004072793 m`, and takes the truthful minimum `0.004069997 m`. This is vertex-sampled evidence, not continuous triangle-distance proof; the builder fail-closes outside `[0.001, 0.15] m`.
- Maximum neutral/rest bind drift is `0.000000030 m`.

## Verification

- Blender 4.5.5 deterministic rebuild and saved-source cold-open validator: **PASS**. Build log SHA-256 `722E1C191B93ECC88D0C0F3917B47F42B220A19C2CDE4840C9ECD3F3A7852A34`; validation log SHA-256 `5B79292722C09A1265B6FC948ED2051D883EC7D82EEE20AD3650ABF002D56245`.
- Full frozen native automation: **75/75 PASS**, exit `0`; log `335,165` bytes, SHA-256 `52367A5BA675DEB5EBD64FAE00C7A417DAE94E4E9CBBCCD898F90BED7CCCA4B4`.
- Full frozen Python regression: **105/105 PASS**, exit `0`; stderr `212` bytes, SHA-256 `5A25219E3AD83957E893E767C097C0F2C7D48350A52721AA7453131C1D2A5786`.
- Brain Admin self-check: **PASS**, exit `0`.
- Retained packaged Unreal custody: **PASS**, exact `50` files / `1,038,710,362` bytes and `50/50` hashes; protected map SHA-256 remains `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.

## Boundaries

No retained source, accepted body, top, jacket, identity preset, tone, Action, animation replacement, FBX, UAsset, client/runtime/config/test/map/package input, gameplay authority, persistence, economy, wagering, simulator, or brain changed. This proof does not establish animated deformation, finished UVs/materials, final art, runtime fit, performance, or beta/production readiness.

See [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate|DEC-034]], [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping|DEC-035]], [[Development/Reports/Phase 1L5bv Refined Sundale Human Body Derivative Neutral Bind Proof]], and [[Development/Reports/Phase 1L5bw Refined Sundale Starter Off White Top Neutral Bind Proof]].
