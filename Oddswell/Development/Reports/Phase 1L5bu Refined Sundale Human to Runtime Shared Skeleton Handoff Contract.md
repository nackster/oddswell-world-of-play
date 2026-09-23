# Phase 1L.5bu — Refined Sundale Human-to-Runtime Shared-Skeleton Handoff Contract

Date: 2026-09-23
Status: **COMPLETE LOCALLY — INVENTORY AND FAIL-CLOSED HANDOFF CONTRACT ONLY**
Cost: **$0.00**

## Outcome

`Oddswell/Art/Production/SundaleStreetSlice/runtime_shared_skeleton_handoff_contract.json` records the exact bridge between the refined offline Sundale human study and the accepted DEC-034/DEC-035 runtime character contract. It hashes the retained `.blend`, delivery/cold-open evidence, five controlling rebuild inputs, the three accepted character contracts, and current motion-axis custody. It does not mutate the source or import anything into Unreal.

This phase closes an ambiguity, not an art milestone: the refined source is visually richer but is not presently a runtime-ready character. A Blender 4.5.5 LTS cold open measured `307` Character objects and `229` Character meshes, with `0` armatures, `0` Actions, `0` armature modifiers, `0` runtime-bone-weighted meshes, and `0` character LOD objects. Its only collision object is the hidden `Character | internal torso support` cloth aid; it is not a gameplay body.

## Exact source custody

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `OddsWell_Sundale_StreetSlice.blend` | `635,844,146` | `0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127` |
| `delivery.json` | `33,777` | `378189DD746EC8B93C06946B8C902773D3EE2FFC3D276F7DA7F7766EF1A6386C` |
| `cold-reopen.json` | `3,221` | `8639E91B367AAAD5E942BEB0C5587564682BBDDB30C486025E7EE67DDEDB1386` |
| DEC-034 contract | `1,717` | `BE283BD9EB10789682ACC71B14A293CFD8080ADBB4F75CDB808F80CA77222FBB` |
| DEC-035 import contract | `1,315` | `C44D4698CE7228EA257A0D1DDFE747C62AD2AE7BCF77165DD10FCC191D63822E` |
| FBX/Unreal contract | `7,577` | `3DAA1D94A19148F03D31682D15B2FA40D9D43133008A1DA099097FCC4AAD88C6` |
| Current motion-axis custody | `5,934` | `5591A6AFD5E8A41D601A9AE53ECDF914B9C1996008C5772A9B1F4043FB954BD4` |

The machine-readable artifact additionally fixes the exact hashes of `build_scene.py`, `develop_character_landscape.py`, `settle_cotton.py`, `settle_jacket.py`, and `verify_scene.py`. The source blend remained byte-identical before and after the read-only cold open.

## Measured gap inventory

| Area | Exact current source state | Required later proof |
| --- | --- | --- |
| Body mesh | Anatomical head `4,362/4,337` vertices/polygons; legs `736/694`; each hand `26,569/26,528`; body/detail objects are distributed rather than one export partition. Visible posed height is `1.720193 m`, not DEC-034 bind-pose stature proof. | One non-destructive derivative body partition at the exact `1.80 m` DEC-034 rest landmarks; preserve all eight preset IDs and four tones. |
| Starter top | No separate `starter_offwhite_top` exists. | Create one bounded derivative starter-top partition; do not relabel the refined slate jacket as the starter top. |
| Starter bottom | `Character | shorts leg continuous tailoring`, `7,159/7,040`, no UV, only a cloth `Waist attachment` group. | Separate runtime partition, UV, accepted-skeleton weights, and deformation proof. |
| Signal Jacket | Main shell `13,095/12,939`, no UV, only a cloth-pin group; collar, cuffs, yokes, zipper, seams, and details remain separate objects. | Select/consolidate intended visual surfaces into one alternative jacket partition, unwrap, bind, and validate against the accepted four clips. |
| Materials | `32` Character materials in a Cycles-oriented offline scene; `31` packed scene maps; body uses retained CC0 anatomical maps while garments include procedural/box-projected shading. | Explicit licensed bake/runtime mapping to the accepted Unreal material and four exact tone choices; no parity claim from offline renders. |
| UVs | `14/229` meshes have UVs: head, legs, hands, and ten nail-fold meshes. `215` meshes, including the bottom and jacket core, have none. | Deterministically retain/transfer body UVs and create bounded garment UVs. |
| Rig and weights | Armatures `0`; armature modifiers `0`; runtime-bone-weighted meshes `0`. Cloth pin groups are not skeletal weights. | Reuse the sole accepted twelve-bone skeleton and exact DEC-035 mapping; normalized weights for all four partitions. |
| Actions | Actions `0`; the static walking pose is not motion evidence. | Reuse accepted walk/run/jump/land assets without replacement or root translation, then measure derivative deformation. |
| LOD | Character LOD objects `0`; no approved budgets. | A separate performance gate must approve and measure LODs; this phase invents no budgets. |
| Collision | One hidden internal torso collision aid used for offline cloth fitting. | Exclude it from export and preserve the authoritative `ACharacter` capsule; any physics asset is separately gated. |

## Accepted runtime target retained

- One exact DEC-034 `1.80 m` neutral silhouette shared by all eight gameplay-identical preset IDs and four tones.
- Four separate mesh identities: body, starter top, starter bottom, and alternative Signal Jacket.
- One exact twelve-bone source skeleton and DEC-035 one-to-one Unreal name mapping; no new skeleton or hierarchy.
- Existing walk, run, jump, and land only, with exact-zero root translation and `ACharacter` retaining trajectory authority.
- Existing movement, capsule collision, camera, replication, saves, appearance IDs, inventory, economy, wagering, simulator, and brains remain authoritative.

## Verification

- Blender 4.5.5 LTS read-only cold open and focused inventory: **PASS**.
- Machine-readable contract JSON parse and fail-closed field checks: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`; log `328,902` bytes, SHA-256 `BB879513870341C2C06516459DFFF12A31EC322C0D80428CFF4157826CC3E32E`.
- Full frozen Python regression: **105/105 PASS**, exit `0`; stderr `212` bytes, SHA-256 `F390F244456465C6C74018A470503ACE821D0175AB2ADBAF9BB5CE15BD538D87`. An earlier generic discovery invocation found zero tests and exited `5`; it is rejected harness evidence, not a product/test failure, and was not counted.
- Brain Admin self-check: **PASS**, exit `0`; stdout `43` bytes, SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Unreal custody: **PASS** against the accepted `C:\tmp\OddsWellNextTen20260912\Package\Windows` inventory: exact `50` files / `1,038,710,362` bytes, all `50` hashes matched, with no missing or extra file. All ten accepted runtime character UAsset hashes also matched.
- Links, clean `22`-node / `0`-edge / `4`-group roadmap canvas, protected source/runtime hashes, zero client diff, and worktree/process/port hygiene are final pre-stage checks; no no-op cook or runtime launch was used.

## Boundaries

No mesh, UV, material, rig, weight, Action, LOD, collision, Blender source, FBX, UAsset, map, source/config/test, runtime, package input, gameplay authority, save, inventory, economy, wager, simulator, or brain was changed. This phase does not import the refined source, replace animation, approve final art, prove performance, approve beta readiness, or waive any Phase 1K/1L/1M exit evidence.

The next possible gate is one separately approved, non-destructive derivative body/clothing partition and accepted-shared-skeleton bind proof. It does not start automatically.
