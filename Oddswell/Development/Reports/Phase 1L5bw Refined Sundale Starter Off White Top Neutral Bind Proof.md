# Phase 1L.5bw refined Sundale starter off-white top neutral-bind proof

Date: 2026-09-23
Status: **COMPLETE LOCALLY — TOP-ONLY DERIVATIVE AND NEUTRAL-BIND TECHNICAL PROOF; NO RUNTIME IMPORT OR FINAL-ART CLAIM**

## Outcome

The exact `starter_offwhite_top` identity now exists as one additive native low-poly derivative around the accepted Phase 1L.5bv body. It retains the exact DEC-034 `1.80 m` body, accepted twelve-bone hierarchy, and DEC-035 mapping. It does not create a bottom, jacket, Action, FBX, UAsset, or runtime replacement.

The proof deliberately uses an open sleeveless torso envelope with one off-white proxy material. This is the smallest geometry that proves torso coverage, clearance, normalized shared-skeleton weights, and rest-bind stability without pretending to be a finished garment.

## Deterministic custody

| Item | Result |
|---|---|
| Accepted Phase 1L.5bv body Blend | SHA-256 `83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB` |
| Accepted body custody | SHA-256 `2299550AA590235BC2D71753BAFE3CE59A2573F8F5900EE817B91E2DB59958A0` |
| Retained body semantic / mesh identity | `91AAB962...B8CF08` / `F340C34B...BF03CD` |
| Starter-top semantic identity | SHA-256 `1AE3EDFC7C215A0508B2044D655FAFB2EF6D44996A0E26C3FB2CF572D248DD49`, reproduced after corrected build/reopen validation |
| Starter-top mesh identity | `8` vertices / `4` polygons; canonical SHA-256 `9996AF8A1271D6E236A45B8EDF93DF36A342FF0743D3276E1676AB3FE96D30C3` |
| Retained Blend custody | `16,768,158` bytes; SHA-256 `B06360F355AFFCA4E18802467186B3F8CFD4D5512C2BCE1B3A9AF66165F9C935` |

Canonical semantic and mesh hashes are the deterministic identities. The retained Blender container has its own custody hash because Blender rewrites container bytes on rebuild.

## Fail-closed proof

- Exactly two mesh partitions exist: the unchanged `BODY__refined_sundale_derivative_v1` and one `starter_offwhite_top`; bottom, jacket, and extra partition counts are `0`.
- The body remains exactly `1.80 m` with canonical mesh SHA `F340C34B...BF03CD`.
- The top covers `0.90–1.50 m`, spanning DEC-034 hip `0.94 m` through shoulder `1.45 m`.
- Body/top triangle intersection pairs are `0`. Bidirectional vertex-to-opposite-surface BVH sampling measures top→body `0.184177205 m`, body→top `0.042323500 m`, and takes the truthful minimum `0.042323500 m`; this is vertex-sampled evidence, not continuous triangle-distance proof. The builder fail-closes outside the accepted technical range `[0.009, 0.25] m`.
- All `8` top vertices have one normalized `spine` influence; unweighted and non-normalized counts are `0/0`.
- Maximum evaluated neutral/rest-bind drift is `0.0 m`; Actions, animation, and root translation are `0`.
- The builder and saved-source validator stop on body/source hash drift, body semantic or mesh drift, extra partitions, bone drift, unauthorized influence, unweighted/non-normalized vertices, intersection, clearance/coverage drift, neutral-bind drift, Actions, or root-transform drift.

## Verification

- Blender 4.5.5 LTS build, repeated semantic rebuild, and saved-source reopen/focused validation: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`; log `334,970` bytes, SHA-256 `6FA5C4E3E9DD771A70224C9AED6B43B86928F6EB86742C0EB4753EF2BA89236D`.
- Full frozen Python regression: **105/105 PASS**, exit `0`; stderr `212` bytes, SHA-256 `C3DB85430ECBE55C06F122EDDCD00746067B790AF5E46F95FB0E9A7999E21E13`.
- Brain Admin self-check: **PASS**, exit `0`; stdout `43` bytes, SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Unreal custody: **PASS** at exact `50` files / `1,038,710,362` bytes, `50/50` hashes; all ten accepted runtime character UAssets remain exact.
- New links, strict UTF-8, clean `22`-node / `0`-edge / `4`-group roadmap canvas, protected hashes, zero client diff, and process/port hygiene are final pre-stage checks; no no-op build, cook, package, or runtime launch was used.

## Boundaries

No body, source Blend, identity preset, tone, accepted animation, bottom, jacket, FBX, UAsset, client/runtime/config/test/map/package input, gameplay authority, persistence, economy, wagering, simulator, or brain changed. This proof does not establish sleeve design, finished materials, final art, runtime fit, deformation under animation, performance, or beta/production readiness. Those require separate gates.

See [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate|DEC-034]], [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping|DEC-035]], and [[Development/Reports/Phase 1L5bv Refined Sundale Human Body Derivative Neutral Bind Proof]].
