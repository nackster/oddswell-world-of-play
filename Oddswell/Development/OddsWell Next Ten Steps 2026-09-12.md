# OddsWell next ten steps

Owner request: September 12, 2026. Goal: complete the next ten concrete steps after the accepted Phase 1L.5bt character asset handoff.

This is a new bounded batch. Earlier six-phase counters remain historical. It follows DEC-034/035, the Beta Game Bible, and the latest Current Plan. Work stays local and uses installed tools. Existing movement, camera, collision, replication, saves, item IDs, economy, and simulation remain authoritative.

| Step | Deliverable and acceptance | Status |
| --- | --- | --- |
| 1 | Skeletal body replaces primitive presentation; correct asset, stature, floor alignment, and unchanged capsule | Technical implementation and focused Unreal check PASS |
| 2 | Starter top/bottom and Signal Jacket use shared skeletal pose and existing equipment state | Technical implementation and focused Unreal check PASS |
| 3 | All eight presets retain their four exact skin tones, IDs, and saved appearance behavior | Eight preset applications PASS; persistence code unchanged; two different packaged peer presets PASS |
| 4 | Walk/run playback responds to actual movement and stops at rest | Native transition/pose checks and rendered gameplay PASS |
| 5 | Jump/landing playback follows the existing movement state with no animation-driven displacement | Native transition/pose checks and rendered gameplay PASS |
| 6 | Two local players agree on skeletal appearance and observe replicated movement | Two-player rendered editor and packaged sessions PASS |
| 7 | Automated camera, collision, and Studio interaction checks pass with the new character | Camera orbit, locomotion collision, Studio entry/walk/exit PASS |
| 8 | Fresh Windows Development package includes and exercises the character with appropriate regressions | PASS: fresh package; five packaged process exits 0; 75 native/105 Python tests and Brain self-check |
| 9 | One coherent OddsWell character-and-street visual candidate and an in-engine comparison are available for owner review | Delivered: generated proposal, editable Blender study, actual packaged street/shared/Studio captures; art approval open |
| 10 | Evidence, local commits, roadmap/canvas, and verified Notion handoff close this batch | Closeout packet complete; exact local closeout commit and sync verification recorded in canonical Notion |

Each result must distinguish automated technical evidence from physical playtest and subjective art approval. Step 9 delivers a review candidate; it cannot grant itself approval. Final art, first-hour usability, accessibility/performance exit, beta release, and Version 1 remain outside this completion claim.

## Steps 1–3 evidence

The native character now uses the accepted skeletal body and two skeletal clothing components. The top switches to the accepted Signal Jacket mesh when the existing replicated equipment flag is true; its second material slot carries the teal accent. Unreal leader pose keeps both clothing components on the body skeleton. The existing appearance resolver still supplies all eight preset IDs and four skin tones. Movement, capsule, camera, RPCs, save formats, inventory, and currency rules are unchanged.

A single shared color-parameter material explicitly supports skeletal meshes; its generated asset and editor-only builder are included. The character directory is explicitly cooked because material and mesh loads use fixed paths. No original imported mesh or animation was edited.

Editor build passed. `OddsWell.Character.SkeletalVisualBridge` passed in a fresh editor with zero warnings and process exit 0. It spawns a real native character, checks body asset/bones/stature/orientation/collision, applies every preset, verifies follower poses, switches jacket and starter top, and removes top independently. Raw evidence: `client/OddsWell/Saved/NextTen20260912/VisualTests2/index.json`, `visual-tests2.log`, and `build-visuals2.log`. The first test attempt failed because the test initialized an already initialized temporary world; that test setup was corrected, and the failed evidence is retained. Runtime motion and packaged visual evidence belong to the following steps.

## Steps 4-5 evidence

Actual velocity selects walk/run and controls playback rate. Switching preserves normalized cycle phase. Stationary presentation holds the neutral frame; the existing movement mode selects jump and a bounded landing clip. The character movement component remains the sole movement authority.

Rendered validation exposed two defects that the earlier import-only checks had missed. First, animation-only FBX reimport lost the skeleton root's meter-to-centimeter scale, giving a 1.66 cm evaluated head height. Explicit animation import scale 100 restores the bind scale and 166 cm head height; mesh import stays scale 1. Second, the original local-Y rotation curves twisted limbs without moving knees. A derivative source changes those curves to local X pitch while preserving every angle value and key time. Measured left-knee travel changes from zero to 12.85 cm for walk, 21.26 cm for run, 15.68 cm for jump, and 30.77 cm for land. Original sources and historical exports are preserved. Four animation assets are corrected; body/skeleton/clothing assets remain unchanged.

The new derivative in `Art/Production/PlayerCharacter/CharacterMotionAxisCorrection` includes Blender source, deterministic eight-file FBX handoff, sidecars, and measured axis evidence. Two scene-reopen exports match. The hash-bound correction script preserves before/after animation hashes and uses existing-asset import settings, which Unreal's legacy reimport requires. The fresh import contract and validator now require the correct animation root scale.

Accepted checks: editor build `build-axes.log`; 75/75 native tests with zero warning-successes in `FullNative/index.json`; rendered `motion-final.log` at 260 cm/s walk and 520 cm/s run, 126.5 cm jump, landed on blocking floor, all five visual states observed, zero root translation, and process exit 0. Full-size run/jump frames are retained under `MotionFinalUser/Saved/Screenshots/WindowsEditor`. Earlier invisible and twisting-motion captures remain diagnostic failures, not completion evidence. The native test now evaluates head height and knee travel, rather than only checking asset assignment or nonzero rotations.

## Steps 6-7 evidence

`Network2/shared-processes.json` retains exact arguments, PIDs, and exit 0 for both local players; the server owns gameplay UDP 127.0.0.1:17777. Both clients verify the exact preset skin colors and shared-pose clothing. The server observes 5.72 cm of actual remote knee travel at 260 cm/s and 302.7 cm of replicated character travel. No networking or appearance authority was replaced. The initial network attempt timed out while Unreal startup waited for the concurrent game build; it is excluded from completion credit.

`camera.log` proves a 370-degree orbit, zero player drift, and exit 0. `studio-final.log` proves the empty 6/0/0/0 Studio, valid entry/leave prompts, 201.7 cm of interior walking, exit/return to Sundale, and exit 0. The earlier Studio launch omitted its auto-exit flag and was stopped after technical completion; only the corrected run has completion credit. Rendered locomotion also proves blocking-floor landing and unchanged speed limits. These are automated technical checks, not physical usability or a contiguous first-hour session.

## Steps 8-10 evidence

The new Windows Development package at `C:/tmp/OddsWellNextTen20260912/Package/Windows` contains 50 files totaling 1,038,710,362 bytes. `PackagedChecks2/processes.json` records exact commands/PIDs and exit 0 for locomotion, Studio, camera, server, and client. Both peers agree on skin colors and skeletal clothing. The server measures 8.49 cm of remote knee travel and 304.0 cm of replicated movement. Its gameplay socket binds to 127.0.0.1:17777. The initial packaged script failed its free-port query after passing three local checks; the corrected full rerun passes. Package and log hashes are in [[Development/Reports/NextTen20260912-evidence.json]]. All 75 native tests, 105 Python tests, and Brain Admin self-check pass.

[[Art/Reviews/OddsWellStreetIdentityCandidate/README]] delivers a native Blender study and generated concept beside actual packaged street, shared-city, and Studio images. The generated concept proposes warm stone/terracotta, blue courts, green canopies, and scarce repeated teal bands; it is more realistic than the requested sculpted/painterly style. Current graybox captures document the implementation gap. This is a delivered review candidate, not final art or recognition approval.

[[Development/Reports/Next Ten Steps Runtime Character and Visual Review]] is the durable handoff. Current Plan, roadmap, canvas, Bible, visual consistency, and vault entry notes reflect this checkpoint. Canonical Notion receives the exact local closeout commit and is fetched after insertion to verify it alongside earlier history. No push or deployment belongs to this batch. The next milestone is a small production street slice and refined character/jacket, with physical first-hour, art approval, accessibility/performance, and beta exit still open.
