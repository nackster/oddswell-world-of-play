# Next ten steps: runtime character and visual review

September 12, 2026. The user-authorized ten-step batch advances the accepted character asset handoff into the playable client and delivers a concrete visual proposal. See [[Development/OddsWell Next Ten Steps 2026-09-12]] for the original sequence and per-step evidence.

The runtime uses one shared skeletal body with two pose-following clothing components. The existing equipment flag selects the Signal Jacket. All eight preset IDs and four exact skin tones pass native checks. Actual character velocity and movement mode select idle, walk, run, jump, and landing presentation. Existing movement, camera, collision, multiplayer, saves, inventory, OddsBucks, and deterministic simulation retain their authority.

Runtime evaluation exposed two defects missed by import-only checks: the animation root lost its 100x unit scale, and local-Y bone curves twisted limbs instead of producing strides. The source-preserving derivative corrects local axes and the explicit animation-only import restores scale. Native verification now measures actual head height and knee travel. Original sources, exports, failed attempts, and exact before/after hashes are preserved.

## Accepted validation

- Editor and Windows Development game builds pass. All 75 native tests pass with zero warning-successes, failures, or not-run tests.
- Python 3.12.14 passes 105 tests: Phase 0A 9, 0B 2, 0C 8, 0D 46, and 1H 40. Brain Admin self-check passes.
- Fresh package: `C:/tmp/OddsWellNextTen20260912/Package/Windows`, 50 files, 1,038,710,362 bytes. All file hashes and current ten character/material asset hashes are retained in [evidence JSON](NextTen20260912-evidence.json).
- Five packaged processes exit 0: locomotion, Studio, camera, listen server, and client. The tests verify all five visual states, normal speeds and blocking-floor landing, empty Studio entry/walk/exit, orbit without player drift, exact preset colors/shared poses, and remote animated movement. The server owns UDP `127.0.0.1:17777`; its accepted remote knee travel is 8.49 cm and replicated displacement is 304.0 cm.
- The durable driver is `client/tools/verify_packaged_character.py`. Its initial PowerShell query failed when a free port returned no endpoint; the corrected full rerun is retained under `client/OddsWell/Saved/NextTen20260912/PackagedChecks2`. Earlier diagnostic failures are excluded from completion credit.

## Visual delivery and limits

[[Art/Reviews/OddsWellStreetIdentityCandidate/README]] contains the editable Blender street study, generated visual proposal, generation brief, and copied packaged screenshots. The generated image proposes warm stone/terracotta, blue courts, green canopies, and a narrow teal band joining jacket and city details. It is more realistic than the requested sculpted/painterly style and remains a candidate for review. It does not show implemented geometry, materials, lighting, or a proven performance target.

The actual runtime character is a technical mannequin. Clip transitions, anatomy, materials, overexposure, camera obstruction, and mirrored shared-player labels still need visual polish. The next concrete art milestone is a small production street slice and refined character/jacket, judged in ordinary street, arena-adjacent, and home screenshots. Final art and screenshot recognition cannot be self-approved by this batch.

Phase 1K physical first-hour proof remains owner-deferred and incomplete. Phase 1L art/accessibility/performance exit and Phase 1M beta exit remain incomplete; Version 1 is inactive. This ten-step completion does not reopen historical six-phase counters or claim those gates.

## Handoff

Implementation checkpoints are local commits `c1826b7` (body/outfit), `ae9fed2` (animation and measured corrections), and `afe5032` (shared/Studio verification). This report and review packet receive a separate local closeout commit; canonical Notion receives and verifies that exact commit. Nothing is pushed or deployed. Current Plan, Beta Delivery Roadmap, Beta Game Bible, visual consistency notes, vault entry point, and the roadmap canvas carry the new checkpoint.
