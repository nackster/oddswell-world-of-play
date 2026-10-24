# Phase 1L.5bg — Articulated Runtime Placeholder and QA Save Warning Repair

Date: 2026-08-29
Status: **COMPLETE LOCALLY — QA SAVE WARNING ROOT FIXED; ARTICULATED PLACEHOLDER PACKAGED AND RUNNING; FINAL CHARACTER ART/RIG/ANIMATION NOT STARTED**
Cost: **$0.00**

## Outcome

OddsWell's packaged Sundale pawn now has separate primitive arms and legs with a velocity-driven walk/run gait. The existing third-person movement, capsule collision, eight gameplay-identical appearances, worn starter outfit, Signal Jacket path, save behavior, and replication authority remain in place.

This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L presentation delivery]], [[Design/Beta Game Bible#1. Choose a default character|First-hour character onboarding]], [[Design/Beta Game Bible#2. Enter the first city|city entry]], and [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]]. It reduces the player-facing risk that the city prototype feels like a sliding capsule while preserving the replaceable Phase 1B placeholder boundary.

It does **not** create or claim final proportions, a skeletal mesh, skeleton, rig, authored animation clips, face, hair, deep creator, production character art, beta readiness, or Version 1 scope.

## Corrective prerequisite

Phase 1L.5bf's 25 warnings came from one shared first-save path: `SaveOddsWellOddsBucksState` attempted to load `OddsWellOddsBucksQA.sav` before the QA slot existed while trying to preserve optional prior void-finalization data. The minimal correction checks `DoesSaveGameExist` before that preservation load. No warning allowlist, relaxed regression contract, new save schema, migration, ledger rule, settlement behavior, or authority change was added.

Verification against only that correction produced native automation `74/74` succeeded, `0` succeeded-with-warnings, `0` failed, and `0` warnings. This closes the current warning blocker without rescoring the historical Phase 1L.5bf run.

## Character presentation slice

- Four native cube components form left/right arms and legs; the existing cylinder torso, cube head, outfit top/bottom, and Signal Jacket components remain.
- Arms use the selected preset's existing dynamic skin material. Legs reuse the existing off-white starter-bottom material.
- A small per-pawn phase value derives opposing arm/leg pitch from replicated horizontal velocity. Walk is `1.4` cycles/second at `18°`; run approaches `2.2` cycles/second at `30°`.
- The native `ACharacter` movement component remains the sole movement authority. Walk `260`, held run `520`, jump `520`, collision, camera, controls, saves, economy, wagering, simulator, brain, and networking contracts are unchanged.
- No asset, plugin, dependency, download, character framework, or generalized animation system was introduced.

## Verification

| Gate | Result |
| --- | --- |
| Editor Development build after save correction | PASS |
| Save-correction full native suite | PASS `74/74`, warnings `0` |
| Editor Development build after character slice | PASS |
| Focused `OddsWell.Character.LocomotionDefaults` | PASS `1/1`, warnings/errors `0/0` |
| Final full native suite | PASS `74/74`, warnings/errors `0/0` |
| Frozen Python suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| Fresh Win64 Development BuildCookRun | PASS in `242.60s`; final source-only rebuild/stage/archive refresh PASS in `37.16s` against the unchanged cook |
| Package custody excluding runtime `Saved` | `50` files, `1,052,124,588` bytes, `0` Python files |
| Warm packaged Sundale locomotion run | PASS |

The first combined Python run had one environmental timing failure: `LifePerformanceTests.test_paired_evaluation_is_reproducible_bounded_and_non_promoting` took `125.528s` against its `<120s` ceiling while Unreal work was adjacent. The frozen test was not changed. Its isolated retry passed in `63.659s`; the complete `phase0d` rerun then passed `46/46` in `132.742s`, and `phase1h` passed `40/40` in `5.423s`.

The final fresh-package city run performed walk/run/jump/landing correctly but failed the legacy camera predicate at `7.5° < 10°` during first-launch shader work. No threshold or code changed. One warmed-package retry passed with `walk_peak=260.0`, `run_peak=520.0`, `max_jump=128.0`, `landed=true`, `floor_blocking=true`, and `yaw_delta=35.1`; both retained package processes then exited naturally.

## Evidence custody

- Corrective native index: `C:\tmp\OddsWellCharacterPhase\QaSaveRepair2\AutomationReport\index.json`, `30,127` bytes, SHA-256 `131B0859E5C0B2C662C4015E5E77BA1C5D9BA339A0AA17C4416491F9F6A410E0`.
- Focused character index: `C:\tmp\OddsWellCharacterPhase\CharacterFocusedFinal\AutomationReport\index.json`, `1,098` bytes, SHA-256 `79E52726C2181A03F542C4A1A621F495CCE7AB80FFD73DF91431CC871B3ECED5`.
- Final native index: `C:\tmp\OddsWellCharacterPhase\FullNativeFinal\AutomationReport\index.json`, `30,133` bytes, SHA-256 `4EE40FCE431621D5842C10DC7544EC5B18E809BC1712151177CE7B06D0A46811`.
- Package game executable: `341,432,832` bytes, SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`.
- Accepted packaged log: `101,922` bytes, SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D`.

## Boundary and next gate

The next character step should remain a separately approved, bounded placeholder-production bridge: evaluate the already-authored eight-preset silhouette sheet against this runtime articulation, then decide whether to promote one shared-skeleton mannequin into Unreal. Modeling/rigging, final animation, body compatibility, and final art remain owner-review gates. Phase 1L exit, hands-on accessibility/usability, Candidate B full policy validation, beta exit, Phase 1M, Roadmap Phase 2, and Version 1 remain incomplete or unauthorized.
