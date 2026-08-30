# Phase 1L.5bh — Runtime Placeholder-to-Eight-Preset Silhouette Compatibility Review and Owner Decision Packet

Date: 2026-08-30
Status: **COMPLETE LOCALLY — COMPATIBILITY REVIEW PACKET READY; OWNER PROMOTION/MODELING/RIGGING DECISION REQUIRED**
Cost: **$0.00**

## Outcome

The articulated Unreal placeholder and the existing Phase 1L.3g eight-preset review sheet agree on the beta-facing identity contract: the same eight gameplay-identical preset IDs, four skin tones, two presentation labels, starter item IDs, Signal Jacket identity/colors, third-person visibility, and one shared geometry path. They do **not** form a production-ready character contract.

The runtime pawn is one neutral primitive body for all eight presets, measures approximately `1.885 m` from capsule floor to visible crown, rotates limb cubes around their centers, and uses runtime clothing transforms that differ from the `1.80 m`, two-base, eight-landmark, shared-fit review contract. The review sheet contains no skeleton, skin weights, deformation, animation, or Unreal import proof. Promotion therefore stops at an explicit owner gate.

This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#1. Choose a default character|First-hour character onboarding]], [[Design/Beta Game Bible#2. Enter the first city|city entry]], and [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]]. It reduces the player-facing risk of starting character production from two incompatible placeholder specifications.

## Evidence compared

| Evidence | Bytes | SHA-256 | Authority used |
| --- | ---: | --- | --- |
| `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` | `628,410` | `C61077774F97F15A91D3F7A92F079075B52760FA0390919021D075EB202D7A43` | current runtime geometry, materials, gait, outfit visibility |
| `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.h` | `23,293` | `EBA4EFF49C99D1A8031E7A56CCB053D639C404AA6AE9AD1DB99C63E0409940E4` | component inventory and gait state |
| `client/OddsWell/Source/OddsWell/CharacterPresetCatalog.cpp` | `4,628` | `C78132F21C303838BA7F0C0ED75E5A8B81260747F688760DF7E0A7C1E281AB1F` | exact eight preset IDs/order, tones, starter items |
| `Oddswell/Art/Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json` | `12,060` | `CCA6E44FC213D9F23547C2BE0964CAB9D85E4EE472E696183A864E44B95B811A` | `1.80 m`, two-base, eight-landmark, shared-fit review contract |
| `Oddswell/Art/Reviews/PlayerCharacterSilhouetteReviewSheet/PROVENANCE.md` | `1,117` | `D0D194EA54BBD91585D49DF0DE4BBCF7C725916FAC5A4C6A6EC0C49127645616` | noncanonical/no-external-input boundary |
| [[Development/Reports/Phase 1L3g Player Character Silhouette Proportion and Outfit Fit Review Sheet]] | `14,060` | `1B3C9EE0A0295E55FBBC9EBFAFA53FA499AF573E26BB41562F31675BC67EC710` | accepted review evidence and limitations |

The runtime measurements below use Unreal's native `100 cm` basic-shape dimensions and the current component transforms. They describe the placeholder only; they are not body-design approval.

## Compatibility matrix

| Contract surface | Current runtime placeholder | Phase 1L.3g review | Result |
| --- | --- | --- | --- |
| Presets | exact eight catalog IDs/order | exact same eight IDs/order | **MATCH** |
| Skin tones | exact four production `FColor` values | exact same four RGBA8 values | **MATCH** |
| Gameplay | one movement/collision path for every preset | gameplay-identical displays | **MATCH** |
| Presentation bases | masculine/feminine labels select no geometry difference | two bounded torso/hip silhouettes | **GAP** — runtime has one neutral silhouette |
| Visible stature | capsule floor `-96 cm` to head crown `+92.5 cm` = approximately `1.885 m`; visible mesh bottom-to-crown approximately `1.845 m` | exact floor-to-crown `1.80 m` | **GAP** — scale origin and target differ |
| Joint landmarks | no skeleton; limb cubes pivot at component centers | ankle `.10`, knee `.53`, hip `.94`, wrist `.78`, elbow `1.12`, shoulder `1.45`, head center `1.66`, crown `1.80 m` | **GAP** — no exact landmark binding or joint pivots |
| Articulation | four separate limb cubes; opposing center-pivot pitch from velocity; walk `1.4 Hz/18°`, run `2.2 Hz/30°` | no armature, rig, skin weights, or animation | **PARTIAL** — motion intent exists; promotion compatibility is unproved |
| Starter outfit identity/colors | `starter_offwhite_top`, `starter_offwhite_bottom`, exact off-white | same item IDs and color | **MATCH** |
| Starter fit | top `0.62 × 0.50 × 0.50 m`; bottom one `0.56 × 0.46 × 0.48 m` cube | top `0.54 × 0.285 × 0.48 m`; bottom shell plus two leg pieces, shared between bases | **GAP** — different dimensions, topology proxy, and seams |
| Signal Jacket identity/colors | starter-top cube recolored slate plus teal accent `0.70 × 0.58 × 0.14 m` | jacket shell `0.58 × 0.315 × 0.50 m` plus accent `0.59 × 0.018 × 0.075 m`, fitted once per base | **PARTIAL/GAP** — semantic identity matches; fit transform does not |
| Shared fit | all eight reuse one runtime geometry/outfit transform | one fit signature shared across two bases | **PARTIAL** — reuse matches; the signatures do not |
| Production readiness | primitive static meshes, no skeleton/rig/authored clips | faceless primitive review mannequins, no skeleton/rig/deformation/import | **NOT PROVEN** |

## Owner decision packet

Choose exactly one bounded direction before any character modeling, skeleton, rigging, animation-asset, or import phase:

### Option A — Keep the articulated primitive through beta

- Keep the current runtime placeholder and treat Phase 1L.3g as noncanonical visual exploration only.
- Spend no character-production scope now.
- Accept that the beta character remains visibly primitive and that final silhouette/fit work stays open.

### Option B — Authorize one shared-skeleton production-candidate bridge

- Authorize one faceless shared-landmark mannequin contract at the owner-selected controlling stature, with the owner-selected one-neutral-or-two-silhouette treatment using the same skeleton and the existing eight cosmetic presets.
- Refit only `starter_offwhite_top`, `starter_offwhite_bottom`, and `sundale_signal_jacket` to that contract, then prove a minimal Unreal walk/run/jump import on the existing movement authority.
- Treat the result as a bounded production candidate, not final art. Faces, hair, deep customization, extra clothing, marketplace features, and final animation polish remain out of scope.

### Option C — Reconcile the review target before production authorization

- Authorize a new noncanonical review revision only, choosing whether `1.80 m` or the current runtime/capsule scale controls and whether the two presentation labels require distinct silhouettes.
- Do not model, rig, import, or replace the runtime pawn yet.

No option is selected by this report. If Option B or C is chosen, the owner must also state the controlling stature (`1.80 m` review target or current runtime/capsule target) and whether the two presentation labels retain distinct torso/hip silhouettes.

## Verification

This phase changes documentation and one roadmap canvas only. It changes no Unreal source, content, map, config, test, package input, character catalog, save, replication, authority, economy, wager, simulator, or brain behavior.

| Gate | Result |
| --- | --- |
| Source/manifest hash and line-reference comparison | PASS |
| Focused Obsidian link, phase-ID, decision-option, and canvas JSON checks | PASS; `22` unique nodes, `0` dangling edges, wiki targets present, client diff `0` |
| Full native Unreal automation | PASS `74/74`, warnings/errors `0/0` |
| Frozen Python regression | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| Proportionate packaged Unreal verification | PASS by integrity reuse of accepted Phase 1L.5bg package; `50` files, `1,052,124,588` bytes, Python `0`, client diff `0`; no recook or launch |

Native evidence is `C:\tmp\OddsWellPhase1L5bh\FullNative\AutomationReport\index.json`, `30,130` bytes, SHA-256 `5DC035380B3EBCECBB56D598A27AFFA867EA233EFEA338F260170C6BD4231039`.

The first frozen-Python attempt used bundled Python `3.12.13` for every suite. Phase 0A, 0B, and 0C passed, but Phase 0D's deterministic LifePerformance evaluation took `165.278 s` against its `<120 s` wall-clock ceiling; its isolated retry took `144.713 s`. No result mismatch occurred and no test or threshold changed. The installed project interpreter Python `3.13.5` passed the identical isolated test in `92.186 s`, then the complete Phase 0D suite passed `46/46` in `134.220 s`; Phase 0A, 0B, and 0C also passed there. Phase 1H intentionally rejected Python `3.13.5` as `interpreter_or_revision_not_allowlisted`; the required bundled/allowlisted Python `3.12.13` then passed `40/40` in `6.035 s`. These rejected environment attempts are retained as diagnostics, not counted as passing gates.

The accepted Phase 1L.5bg package remained exact: wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`, game executable SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`, and accepted runtime log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D`. A recook or relaunch would add no evidence because this phase changes no package input.

Final process audit found no OddsWell game, OddsWell editor, `UnrealEditor-Cmd`, Python-test, or Brain Admin process. The still-open `UnrealEditor.exe` PID `33648` targets the unrelated user project `C:/Users/reali/Documents/Youtube Auto/Dock 9/World3D/Unreal/Dock9World.uproject`; its sponsored Unreal Trace Server PID `34936` is also unrelated and was not terminated or counted as OddsWell residue.

## Boundary and next gate

No modeling, mesh promotion, skeleton, rig, skin weights, animation assets, import, runtime/config change, or final-art claim is authorized or performed. The frozen Phase 0 simulation, authoritative event-log architecture, server-owned settlement, equal-information boundary, Odds Bucks authority, immutable inventory/history boundaries, and current brain maturity remain untouched.

**OPEN / OWNER GATE:** choose Option A, B, or C and answer the stature/two-silhouette questions above. Until then, the current primitive remains the only implemented character, and Phase 1L exit, Phase 1M, beta readiness, Roadmap Phase 2, Version 1, and production readiness remain unauthorized or incomplete. Cursor delegation is not suitable for this authority-bearing character decision.
