# Phase 1L.5bv refined Sundale human body derivative neutral-bind proof

Date: 2026-09-23
Status: **COMPLETE LOCALLY — BODY-ONLY DERIVATIVE AND NEUTRAL-BIND TECHNICAL PROOF; NO RUNTIME IMPORT OR FINAL-ART CLAIM**

## Outcome

One non-destructive body-only derivative now proves that selected refined Sundale anatomy can be normalized to the accepted DEC-034 `1.80 m` stature and bound at rest to the accepted twelve-bone shared skeleton with the exact DEC-035 name mapping. The original `OddsWell_Sundale_StreetSlice.blend` remains byte-identical.

The retained derivative copies only `Character | anatomical head`, left hand, legs, and right hand from the refined source. A deliberately simple native low-poly torso/arm bridge fills the source regions hidden beneath clothing only so every accepted bone can participate in the neutral-bind proof. The bridge is marked `neutral_bind_proxy_only`; it is not production anatomy or final art. Clothing, footwear, the hidden `internal torso support`, and every other offline fitting/collision aid are excluded.

## Deterministic custody

| Item | Result |
|---|---|
| Original refined source | `635,844,146` bytes; SHA-256 `0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127` |
| Accepted prior handoff | SHA-256 `9DFE96E72883BBC3BB9AFB7FAD799644C54DE817142CE625862F9BA06764926A` |
| Accepted shared-bind source | SHA-256 `9CBD196FDB42FA76788673467D16954733796AE6820073075005444B0942A443` |
| Derivative semantic identity | SHA-256 `91AAB962825784679391C85FD06239A2F8EB118FEABA906EF9C5FB373FB8CF08` across repeated builds |
| Derivative mesh identity | `58,324` vertices / `58,143` polygons; canonical SHA-256 `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD` |
| Retained Blend custody | `17,486,411` bytes; SHA-256 `83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB` |

The canonical semantic and mesh hashes are the deterministic identities. Blender container bytes are separately recorded as custody for the retained output; a repeated rebuild reproduced the semantic and mesh identities while Blender rewrote container bytes.

## Fail-closed proof

- Body bounds are exactly `[-0.337676, -0.294926, 0.0]` to `[0.337676, 0.294926, 1.8]` metres.
- The armature contains exactly the accepted `12` source bones, hierarchy, neutral landmarks, and DEC-035 source-to-Unreal mapping.
- Every one of `58,324` vertices has one normalized influence; unweighted and non-normalized vertices are both `0`, and every accepted bone owns at least one vertex.
- Maximum evaluated neutral/rest-bind drift is `0.000000241 m`.
- Actions, animation data, root translation, additional meshes, clothing, fitting/collision aids, FBX, UAsset, and Unreal import are all `0`.
- The builder and saved-source validator stop on source/hash drift, bone-set drift, stature drift, unweighted or non-normalized vertices, neutral-bind drift, additional meshes, Actions, or non-zero armature transform.

## Verification

- Blender 4.5.5 LTS build, repeated semantic rebuild, and saved-source reopen/focused validation: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`; log `334,975` bytes, SHA-256 `76591FD33C631FF7E0A352AB4015887F62FB3DA6CF707E1D79AAD4B9E23C9945`.
- Full frozen Python regression: **105/105 PASS**, exit `0`; stderr `212` bytes, SHA-256 `AE2182DB39CE3D094E9FBDBFCD4CD5E4750868DB6205BD104A1C92FAC232326A`.
- Brain Admin self-check: **PASS**, exit `0`; stdout `43` bytes, SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Unreal custody: **PASS** at exact `50` files / `1,038,710,362` bytes, `50/50` hashes, missing/extra `0/0`; all ten accepted runtime character UAssets remain exact.
- New links, strict UTF-8, clean `22`-node / `0`-edge / `4`-group roadmap canvas, protected hashes, zero client diff, and process/port hygiene are final pre-stage checks; no no-op build, cook, package, or runtime launch was used.

## Boundaries

No source Blend, identity preset, tone, accepted animation, FBX, UAsset, client/runtime/config/test/map/package input, movement, capsule collision, camera, replication, persistence, economy, wagering, simulator, brain, or authority changed. This proof does not bind clothing, import into Unreal, replace the runtime pawn, approve final art, establish performance, or approve beta/production readiness. Any clothing bind or runtime import requires a separate Scope Director gate.

See [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate|DEC-034]], [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping|DEC-035]], and [[Development/Reports/Phase 1L5bu Refined Sundale Human to Runtime Shared Skeleton Handoff Contract]].
