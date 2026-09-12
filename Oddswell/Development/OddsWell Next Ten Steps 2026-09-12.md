# OddsWell next ten steps

Owner request: September 12, 2026. Goal: complete the next ten concrete steps after the accepted Phase 1L.5bt character asset handoff.

This is a new bounded batch. Earlier six-phase counters remain historical. It follows DEC-034/035, the Beta Game Bible, and the latest Current Plan. Work stays local and uses installed tools. Existing movement, camera, collision, replication, saves, item IDs, economy, and simulation remain authoritative.

| Step | Deliverable and acceptance | Status |
| --- | --- | --- |
| 1 | Skeletal body replaces primitive presentation; correct asset, stature, floor alignment, and unchanged capsule | Technical implementation and focused Unreal check PASS |
| 2 | Starter top/bottom and Signal Jacket use shared skeletal pose and existing equipment state | Technical implementation and focused Unreal check PASS |
| 3 | All eight presets retain their four exact skin tones, IDs, and saved appearance behavior | Eight preset applications PASS; persistence code unchanged; packaged verification follows |
| 4 | Walk/run playback responds to actual movement and stops at rest | Pending |
| 5 | Jump/landing playback follows the existing movement state with no animation-driven displacement | Pending |
| 6 | Two local players agree on skeletal appearance and observe replicated movement | Pending |
| 7 | Automated camera, collision, and Studio interaction checks pass with the new character | Pending |
| 8 | Fresh Windows Development package includes and exercises the character with appropriate regressions | Pending |
| 9 | One coherent OddsWell character-and-street visual candidate and an in-engine comparison are available for owner review | Pending |
| 10 | Evidence, local commits, roadmap/canvas, and verified Notion handoff close this batch | Pending |

Each result must distinguish automated technical evidence from physical playtest and subjective art approval. Step 9 delivers a review candidate; it cannot grant itself approval. Final art, first-hour usability, accessibility/performance exit, beta release, and Version 1 remain outside this completion claim.

## Steps 1–3 evidence

The native character now uses the accepted skeletal body and two skeletal clothing components. The top switches to the accepted Signal Jacket mesh when the existing replicated equipment flag is true; its second material slot carries the teal accent. Unreal leader pose keeps both clothing components on the body skeleton. The existing appearance resolver still supplies all eight preset IDs and four skin tones. Movement, capsule, camera, RPCs, save formats, inventory, and currency rules are unchanged.

A single shared color-parameter material explicitly supports skeletal meshes; its generated asset and editor-only builder are included. The character directory is explicitly cooked because material and mesh loads use fixed paths. No original imported mesh or animation was edited.

Editor build passed. `OddsWell.Character.SkeletalVisualBridge` passed in a fresh editor with zero warnings and process exit 0. It spawns a real native character, checks body asset/bones/stature/orientation/collision, applies every preset, verifies follower poses, switches jacket and starter top, and removes top independently. Raw evidence: `client/OddsWell/Saved/NextTen20260912/VisualTests2/index.json`, `visual-tests2.log`, and `build-visuals2.log`. The first test attempt failed because the test initialized an already initialized temporary world; that test setup was corrected, and the failed evidence is retained. Runtime motion and packaged visual evidence belong to the following steps.
