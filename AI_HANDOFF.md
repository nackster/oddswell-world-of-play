# OddsWell — project status and AI handoff

Snapshot checked **October 20, 2026 (Asia/Bangkok)**. Latest implementation checkpoint: **October 11, 2026**, commit `82ecfda` on local branch `agent/phase-0d`. No newer commits were present when this handoff was written. Recheck Git before starting; this is a dated snapshot, not a live status dashboard.

## Read this first

OddsWell has a substantial **machine-local playable Unreal prototype** and a stronger **offline Blender character/street art direction**. They are separate deliverables. The realistic scanned character and its new Signal Jacket are **not integrated into Unreal**. The project is **not beta-ready**.

The owner wants a realistic human and a distinctive city/graphics style that communicates “this is OddsWell” in an ordinary gameplay screenshot. They accepted the imported scanned-human direction after extensive procedural-body work failed to reach the desired quality. **Continue from the scan; do not restart the long loop of tiny edits to the old mannequin.** Favor visible, reviewable gains and a working player experience.

## What we are building

A walkable 3D fantasy city centered on a persistent fictional basketball league and one virtual currency, **Odds Bucks**. The beta player loop is:

`choose character → enter city → visit Studio → find job → earn Odds Bucks → inspect game → place wager → watch result → settle wager → buy/save toward clothing or housing`

The approved first-city direction is **Daymark / Sundale**, a modern civic commons. Its visual direction combines warm mineral/terracotta and brick surfaces, varied storefronts and deep awnings, mature trees and layered planting, blue basketball courts, an open/glass arena, warm daylight, and restrained slate/teal accents. Sundale is a working name.

Initial delivery is PC; the repository lists PC/Steam as the platform direction. Unreal Engine **5.8** is adopted. Blender **4.5.5 LTS** is the native art source of truth. The Obsidian vault in `Oddswell/` holds product decisions and implementation evidence.

Real-money purchases, player trading, extra cities/sports and a broad life-simulation expansion are not current beta work. Version 1 implementation waits for owner-approved beta exit and an explicit scope freeze.

## Authority and essential reading

The owner's newest explicit direction and accepted decision records control scope. The Beta Game Bible is product authority; reports demonstrate implementation, not permission to expand it. This handoff summarizes those sources and does not replace them.

| Read | Why |
|---|---|
| [Project Completion Roadmap](Oddswell/Development/Project%20Completion%20Roadmap.md) | Short milestone sequence and immediate work queue. |
| [Beta Game Bible](Oddswell/Design/Beta%20Game%20Bible.md) | Canonical beta promise, required loop and scope boundaries. |
| [Beta Delivery Roadmap](Oddswell/Development/Beta%20Delivery%20Roadmap.md) | Detailed dependencies, accepted evidence and unresolved gates. |
| [Current Plan](Oddswell/Development/Current%20Plan.md) | Implementation history; latest character notes are near the end. Large historical document. |
| [Runtime character review](Oddswell/Development/Reports/Next%20Ten%20Steps%20Runtime%20Character%20and%20Visual%20Review.md) | What the existing Unreal skeletal character actually proved. |
| [Signal Jacket checkpoint](Oddswell/Art/Production/SundaleStreetSlice/ScannedSignalJacketCandidate/README.md) | Latest offline character asset, recipes and limitations. |
| [First-hour evidence contract](Oddswell/Development/Phase%201K%20First-Hour%20Integration%20Evidence%20Contract.md) | Required contiguous player-session proof. |
| [Version 1 Game Bible](Oddswell/Design/Version%201%20Game%20Bible.md) | Future boundary only; not authorization to implement Version 1. |

For visual comparison, use the original [street concept](Oddswell/Art/Reviews/OddsWellStreetIdentityCandidate/OddsWell_Visual_Direction_Concept.png) and the latest [native street render](Oddswell/Art/Production/SundaleStreetSlice/ScannedSignalJacketCandidate/Gameplay.png). The concept is a generated proposal. The latter is actual Blender geometry, **not an Unreal screenshot**.

## What already exists

| Area | Evidence-backed position | Important limit |
|---|---|---|
| Basketball/league | Deterministic Python simulation, authoritative event logs, replay/result evidence, league and public athlete presentation. | Do not claim live learning, retraining, physical 3D athlete simulation, or a production backend. |
| Unreal client | Packaged Windows prototype, character chooser, movement/camera and Sundale graybox route. | Final city and character artwork are unfinished. |
| Existing runtime character | Shared skeletal body, pose-following clothing, eight preset IDs/four tones, equipment flag, velocity/movement-driven idle/walk/run/jump/land presentation. | Technical mannequin; this is not the new 88-bone scanned character. |
| Shared city | Packaged machine-local two-client presence, appearance and animated movement evidence. | No external-service readiness or approved production capacity follows. |
| Housing | Empty Studio enter/exit and persistence; bounded chair placement and first one-bedroom upgrade. | Broad decorating, visits and later apartment tiers remain outside current implemented slice. |
| Job/economy | Local saved-profile ledger and recovery: start at 0, earn 100 from a successful job on a rolling 24-hour cooldown. | Production account/time authority and broader recovery policy remain open. |
| Wagering | Bounded authoritative offer/request/debit/lock/result/settlement/history paths, idempotency and reconciliation evidence. | Separate component/QA proofs do not establish a complete production wagering service. Read exact Phase 1H reports before changing it. |
| Shops | Approved Signal Jacket purchase/equip/peer visibility, Modular Chair purchase/Studio snap and first housing upgrade. | Tiny approved catalog, not a generalized marketplace. |
| Athlete storytelling | Public athlete pages and a bounded owner comprehension milestone accepted under DEC-021. | No population-wide comprehension or new athlete-brain behavior is implied. |
| New offline artwork | Scanned human, restrained walk study, separate fitted Signal Jacket, Sundale street scene and native render previews. | No scan/jacket engine integration, final visual acceptance, complete cloth contacts or target-PC performance proof. |

The September 12 runtime report records **75 native tests**, **105 Python tests**, Brain Admin self-check, Editor/game builds and five packaged process checks passing. Those are **historical recorded results**, not fresh October 20 runs. The latest art work used source-integrity, cold-reopen and native geometry/render checks; it did not rerun the full Unreal suite.

## Latest character checkpoints

| Commit | Delivered |
|---|---|
| `b4eac4d` | Downloaded/imported Renderpeople **Eric Rigged 001**; reviewed realistic face/body, source textures and rig; local editable asset. |
| `1f9a25d` | Completion roadmap and restrained scanned-human walking study. Maximum foot-bone separation reduced from approximately 0.858 m to 0.715 m. |
| `82ecfda` | Separate fitted Signal Jacket shell, zip tape/teeth, pocket welts, tapered rib collar, teal chest tab, four garment/figure views, walking preview and street-camera composition. |
| Oct 20 | **Direction change:** Epic Games Store target at $9.99, single-player first (DEC-037). See `Oddswell/Development/Epic Store Launch Plan.md`. **M1 delivered:** C++ league core with Python parity, career subsystem, in-game days, betting on any game, arena replays, and packaged play-through/soak checks. See `Oddswell/Development/Reports/M1 Living League/README.md`. |
| Oct 24 | **M2 delivered:** eight MetaHuman presets (DEC-038), plus a title screen, pause menu, settings and first-day guide. One known gap: hair does not render yet. See `Oddswell/Development/Reports/M2 Complete Loop/README.md`. **M3 delivered:** five bet markets priced by simulation with a 4% margin, a 4-job ladder, 6 homes, 20 clothing and 16 furniture items, 22 achievements, and the Penthouse season goal (DEC-039). See `Oddswell/Development/Reports/M3 Content/README.md`. |
| Oct 20 | Off-white starter outfit (mock-neck long-sleeve top, cuffed joggers, slate sneakers) as separate skinned shells; long garments chosen by the owner in DEC-036. See `Oddswell/Art/Production/SundaleStreetSlice/ScannedStarterOutfitCandidate/README.md`. Local editable file: `downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy/OddsWellStarterOutfit.blend`. |

The scan has **10,353 vertices, 10,558 polygons, an 88-bone rig and three packed source maps**. Original geometry, UVs, weights, bind matrices and packed-map bytes pass the retained comparisons. The walk has 49 authored keys; whole-mesh grounding is not foot locking. The motion report records up to approximately **1.55 mm** interpolated ground penetration at sampled half-frames.

The jacket has **1,826 base vertices**, deriving fit from **1,816 clothed upper-body faces**. It shares the scan's rig. All jacket/trim meshes evaluate to finite geometry at the 49 authored walk keys. This does **not** certify collision-free cloth, complete contacts or Unreal compatibility.

The main Signal Jacket palette is slate `[0.12, 0.18, 0.22, 1]` and teal `[0.08, 0.72, 0.68, 1]`. The scan's formal trousers, belt, shoes, white shirt cuffs and small neck edge remain temporary. Hands and planted-foot timing need work.

The older production contract in `Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json` describes a faceless, neutral, 1.80 m shared-skeleton candidate and eight preset IDs. Later owner direction asks for a realistic human with a face. Reconcile the new asset with the still-required preset/rig/runtime behavior before promotion; do not silently treat the old contract as either fully satisfied or wholly obsolete.

## Local editable assets — important for another AI

Workspace on this machine: `C:/Users/reali/Documents/SaaS/Oddswell`.

The following files were present and their hashes were verified when this handoff was written. Paths below are relative to the repository root.

| Asset | Local path | SHA-256 |
|---|---|---|
| Original compact scan | `downloads/licensed-characters/RenderpeopleEric/OddsWellHuman.blend` | `3ed84ad823f809e19ff6c7bafc591109e90e20d96455b28bcd15431f82ae4485` |
| Restrained motion | `downloads/licensed-characters/RenderpeopleEric/MotionRefinement/OddsWellHumanMotion.blend` | `1c75042928c5df6eaa198c1fe032a5b3985224c33b766bd322b7dc10b126aca4` |
| Latest jacket/character | `downloads/licensed-characters/RenderpeopleEric/SignalJacketStudy/OddsWellSignalJacket.blend` | `fa455707fe273b6230fd19fa7f2a934ae560d81b551fb05850d732740f3c0099` |
| Full native street source | `client/OddsWell/Saved/NextTen20260912/ScannedHumanStudy/ScannedHumanWalk.blend` | `118a64a22401e78a25c6d76ab0e38b6a03e013ff7ad31ae0830ad4ecfe07bb92` |

The jacket file is approximately 22 MB; the full street source is approximately 754 MB. The compact files are the efficient starting points for character work.

These vendor-derived models and original textures are **ignored local assets**, not committed model files. A fresh clone will not contain them. The repository retains permitted renders, manifests, source hashes and rebuild recipes in:

- `Oddswell/Art/Production/SundaleStreetSlice/ScannedHumanCandidate/`
- `Oddswell/Art/Production/SundaleStreetSlice/ScannedHumanMotionCandidate/`
- `Oddswell/Art/Production/SundaleStreetSlice/ScannedSignalJacketCandidate/`

The publisher is [Renderpeople](https://renderpeople.com/free-3d-people/); the retained acquisition review links its [terms](https://renderpeople.com/general-terms-and-conditions/). Existing custody keeps vendor FBX/textures, raw archives and derived Blender models local because model-file redistribution is restricted. Do not add them to Git or upload them to another service as part of this handoff. On another machine, inspect the acquisition recipes and applicable license/access rather than assuming a clone includes the asset. Additional body/clothing sources have not been selected or acquired; MakeHuman/Blender Studio were only researched as possibilities.

## What is left, in delivery order

1. **Finish a believable modular human and wardrobe.** Obtain/build compatible underlying body and leg geometry; make the approved off-white starter garments and casual footwear. Refine relaxed hands, gait and foot planting. The clothed scan contains no bare-leg replacement for cutting its trousers into shorts. Keep the accepted face/body quality; do not disguise missing anatomy with a texture recolor.
2. **Review the complete character.** Close, full, side/back, walking and street-distance evidence must show a coherent human and OddsWell outfit. Address collar/zip details, clothing fit and visible contacts. A numeric pass does not override a poor silhouette.
3. **Freeze the production handoff and integrate one candidate.** Resolve rig, scale, presets/tones, texture/material budget, animation retargeting and export. Verify actual Unreal movement, camera/collision, walk/run/jump/land, equip state, peer appearance and cold saves. Preserve existing gameplay authority.
4. **Finish one distinctive Sundale block.** Improve storefront variety/depth and awnings, arena sightlines, mature canopy and layered ground planting. Prioritize the first-hour route and normal gameplay camera; avoid expanding to unseen districts.
5. **Complete first-hour presentation and the contiguous player session.** Character → Studio → job → exact game/offer/wager/watch/settlement → upgrade → cold restore. Game identity, score and replay seal must agree throughout. Record assistance/failures; do not splice independent QA results into one claimed playthrough. Physical player proof is owner-deferred to the playtest, still required before beta exit.
6. **Accessibility and measured PC performance.** Finish remapping/readability/contrast, required captions and motion options. Validate the provisional Balanced 1080p60/Medium policy on the approved minimum PC using the representative packaged character/city. A chosen policy is not a benchmark pass.
7. **Production reliability and multiplayer.** Resolve capacity/regions/safety surface and account/time authority. Prove disconnect/reconnect, persistence/migration, backup/restore/rollback and economy/inventory/housing reconciliation. Preserve immutable replay and settlement history.
8. **Beta exit.** Finish authentication/authorization, privacy/moderation, intended-audience/platform/legal review, admin incident recovery and observed usability. Development trace-listener exposure remains external-use debt. Phase 1M needs an evidence-backed Beta Exit Report and owner approval.
9. **Only then freeze and deliver Version 1.** Use measured beta feedback and an owner-approved scope; do not automatically start extra cities, sports, trading or monetization.

No reliable completion percentage or calendar ETA is currently established.

## Recommended first assignment for an additional AI

**Update, October 20:** The starter-outfit half of this assignment is delivered as long garments over the scan (DEC-036; see the checkpoint table above). The body/leg source is still open and now belongs with the production rig/preset/export contract. It is needed for shorts and for preset/tone variety. The original assignment text follows for reference.

**Deliver one compatible body/leg and starter-outfit candidate around the accepted human direction.** Keep the Signal Jacket checkpoint and original scan intact. Work in a new candidate folder and retain editable sources under the relevant license.

Acceptance for this bounded assignment:

- Identify the body/clothing source and license, and explain how it fits the accepted face, scale and rig.
- Show actual appropriate body geometry beneath the off-white starter top/bottom and casual footwear; do not merely recolor the business suit.
- Retain front, side, back, full-figure and short walking renders; review at street distance as well as close up.
- Preserve or explicitly report skin weights, UVs, source texture custody and motion changes. State contact/foot-sliding limitations honestly.
- Deliver a short report, source paths/hashes and reproducible steps. Review the whole figure before choosing another small corrective pass.
- Do not alter the simulator, ledger, wagering, save formats, runtime capsule/camera or canonical scope as part of this art task. Engine promotion follows a separate compatible handoff and running verification.

If two AIs work concurrently, separate source ownership. One can own the new body/wardrobe candidate while another handles a bounded city-art candidate or read-only runtime integration inventory. Use separate branches/worktrees and candidate outputs where practical. This document does not assign ownership or ask either AI to message another chat. Check overlap before editing shared files.

## Repository map and tools

| Location | Contents |
|---|---|
| `Oddswell/` | Canonical Obsidian vault: design, decisions, roadmap, art and reports. |
| `client/OddsWell/` | Unreal project, C++ source, Content and ignored Saved evidence. Project: `OddsWell.uproject`; engine association is 5.8. |
| `client/tools/verify_packaged_character.py` | Existing packaged character verification driver. Read its arguments and evidence requirements before using it. |
| `phase0a/` through `phase0d/` | Python simulation, analysis, policy boundary, league and athlete work. |
| `phase1h/` | Odds/wager execution, result/seal and supervisory work. |
| `brain_admin/` | Local-only Admin Console and self-check. |
| `downloads/` | Ignored licensed assets and local working files; not a distributable asset repository. |

Installed local tools previously used successfully:

- Blender: `C:/Users/reali/AppData/Local/Programs/Blender Foundation/blender-4.5.5-windows-x64/blender.exe`
- Python: `C:/Users/reali/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`
- `ffmpeg` / `ffprobe` on PATH.

Use CPU Cycles as the known working baseline; prior GPU/CUDA attempts failed. Render one OddsWell Blender job at a time and preserve unrelated projects' processes. For unattended source work use `--background --factory-startup --disable-autoexec --python-exit-code 1 --python <recipe>`. Many recipes write to ignored local folders and pin source hashes; read them before execution. Rebuilding the original scene may require older retained source files beyond the compact character.

Useful existing checks, from the repository root (replace `python` with the installed executable if needed):

```powershell
git status --short
git log -6 --oneline
python -m unittest discover -s phase0a -p 'test_*.py'
python -m unittest discover -s phase0b -p 'test_*.py'
python -m unittest discover -s phase0c -p 'test_*.py'
python -m unittest discover -s phase0d -p 'test_*.py'
python -m unittest discover -s phase1h -p 'test_*.py'
python -m brain_admin.server --check
```

Run checks proportionate to the change. Runtime changes also need current native/build/package verification; historical passing counts do not pass new code. Unreal exit code 0 alone does not establish that a Python import/verification succeeded—require the documented report and success markers. Do not blindly reimport over accepted assets. No tests, builds or game processes were run to create this documentation-only handoff; local file existence and hashes were checked.

## Existing uncommitted work — preserve it

The worktree was already dirty before this handoff. These changes belong to the separate older starter-outfit/nightly workflow and must not be discarded or swept into a new commit:

```text
 M Oddswell/Design/Beta Game Bible.md
 M Oddswell/Development/Beta Delivery Roadmap.md
 M Oddswell/Development/Current Plan.md
 M Oddswell/Visual Maps/Beta Delivery Roadmap.canvas
?? Oddswell/Art/Production/SundaleStreetSlice/SideUnderarmCorrectedCombinedStarterOutfitVisualAcceptanceReview/
?? Oddswell/Development/Reports/Phase 1L5ct Side Underarm Corrected Combined Starter Outfit Offline Visual Acceptance Review.md
```

That older Phase 1L.5ct review is **REJECTED_VISUAL_CORRECTION_REQUIRED**, not an accepted outfit or authorization to export/import it. Do not convert it to a pass because the newer scan looks better. The two evidence streams are separate.

Never use a blanket `git add .`, reset, cleanup or overwrite to make this worktree appear clean. For shared documents, stage only your own change; do not commit the entire already-modified file. Recent character work used a HEAD-to-HEAD-plus-owned-note patch applied to the index, while preserving the existing worktree bytes. Prefer adding a separate concise report when that avoids overlapping edits. Check current branch/index/diff before every commit. Existing character checkpoints are local commits; this handoff does not establish remote push/sync status.

## Boundaries to carry forward

Preserve the frozen simulation and authoritative event-log architecture; equal public information; server-owned Odds Bucks/wager settlement; immutable inventory/result/history boundaries. Do not claim learning, intelligence, realism, production readiness or beta completion from a render or isolated test. Keep the local Admin Console private; its existing local-only setup is not a deployed authenticated service.

Keep progress concrete: one useful candidate or measured correction, a visible/running result, a short honest report and scoped source control. Avoid another unbounded anatomy-tweak loop, unneeded frameworks or broad catalog expansion. When an OPEN owner decision actually blocks a dependent step, surface that exact decision and continue independent work where possible.
