# Phase 1L.5by refined Sundale Signal Jacket neutral-bind proof

**Status:** COMPLETE — consolidated jacket-only technical proof; not runtime or final art
**Date:** 2026-09-23
**Cost:** $0

## Outcome

The approved visible jacket surfaces now form exactly one separately replaceable `sundale_signal_jacket` around the accepted Phase 1L.5bv body. The partition replaces `starter_offwhite_top`; it is not layered over that starter garment. The accepted body, starter top, and starter bottom remain byte-identical inputs or references.

The inclusion ledger contains `194` source objects: main shell, standing collar, paired cuffs, rear and sleeve signal yokes, zipper tape/teeth/slider/pull, and exactly three yoke topstitch objects. The source has no separately named jacket-panel, rear-jacket, or sleeve-seam objects. Cloth pin groups, hidden anatomy, offline collision/fitting/support aids, and Actions/clips are excluded. The deterministic fit removes `1,835` penetrating source faces and records per-source pre/removed/retained polygon counts rather than presenting the result as untouched tailoring. Every approved contributor survives; the main shell retains `12,032/12,939` faces and collar retains `8,626/9,216`.

## Deterministic custody

| Artifact | Identity |
| --- | --- |
| Immutable source Blend | SHA-256 `0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127` |
| Accepted body Blend / custody | `83D9AFED...D3BCAB` / `2299550A...958A0` |
| Accepted body semantic / mesh | `91AAB962...B8CF08` / `F340C34B...BF03CD` |
| Unchanged starter top / bottom | `B06360F3...F9C935` / `18103E29...5798CA` |
| Jacket semantic identity | SHA-256 `7C1AE452E77C5DBBA92443620603DFFA809E630E94D3AA14DAB2F799BEFB9740` |
| Jacket mesh | `45,232` vertices / `38,174` polygons; SHA-256 `C7E297D7F9B62531E34DBD2115CACCD0D9CC36BC61A0A6BB1DCCD477D4C95089` |
| Proof Blend | `40,359,987` bytes; SHA-256 `28A0C089874528E408E58670FDE64D633F8ACB46E6431F58CD84B6F219E38FDD` |

## Neutral-bind proof

- Exactly two mesh partitions and one armature exist: accepted body plus jacket; starter top is absent and Actions are `0`.
- The exact accepted twelve bones and DEC-035 mapping remain unchanged; root translation is zero.
- All `45,232` jacket vertices have one normalized accepted influence. Unweighted and non-normalized counts are `0`.
- Post-fit topology has `13,298` boundary/non-manifold edges, inherited open garment/detail topology plus deterministic face removal; cleanup leaves wire edges `0` and isolated vertices `0`. This is not a watertight-manifold claim.
- Coverage bounds are X `-0.368366–0.382267 m` and Z `0.813445–1.507401 m`, spanning torso, shoulders, and arms.
- Body/jacket triangle intersection pairs are `0`.
- Bidirectional vertex-to-opposite-surface BVH sampling measures jacket→body `0.000085141 m`, body→jacket `0.000441466 m`, and takes the truthful minimum `0.000085141 m`. This is vertex-sampled evidence, not continuous triangle-distance proof; fail-closed bounds are `[0.00005, 0.20] m`.
- Maximum neutral/rest bind drift is `0.000000241 m`.

## Verification

- Blender 4.5.5 deterministic rebuild and saved-source cold-open validator: **PASS**. Build log SHA-256 `938F3F421E03E3C6F6A083726EE1630653B6A9F8C47EABC83B334A29640FF3AA`; validation log SHA-256 `3F3D44CA03BBE94AE30E6C04BA09E2D8F627CA6E06CD8121A662357E49F5823D`.
- Full frozen native automation: **75/75 PASS**, exit `0`; log SHA-256 `695D9036F4EBA1EFA36D8E59C3A8C247282EEF49BC3A474A952AE820C09EF077`.
- Full frozen Python regression: **105/105 PASS**, exit `0`; log SHA-256 `9FAA195EF6CE5AD0118477AD08A50AD476575053FF58403082B83A9C1F5525B2`.
- Brain Admin self-check: **PASS**, exit `0`; SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained package: exact `50` files / `1,038,710,362` bytes and `50/50` hashes. Protected map remains SHA-256 `180B31BA...8C015`.

## Boundaries

No source, body, top, bottom, identity preset, tone, clip, animation, UV/runtime material bake, FBX, UAsset, client/runtime/config/test/map/package input, gameplay authority, persistence, economy, wagering, simulator, or brain changed. This proof does not establish animated deformation, finished materials, final art, runtime fit, performance, or beta/production readiness.

See [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate|DEC-034]], [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping|DEC-035]], and [[Development/Reports/Phase 1L5bv Refined Sundale Human Body Derivative Neutral Bind Proof]].
