# Phase 1K.8a Shared Handoff Correction and Automated Membership Proof

## Outcome

**COMPLETE — THE PRODUCTION HANDOFF NOW JOINS THE ACCEPTED MACHINE-LOCAL SUNDALE SESSION; AUTOMATED MEMBERSHIP PASSED.**

Character confirmation now uses Unreal client travel to the accepted Development listen endpoint at `127.0.0.1:17777` instead of opening a second standalone `SundaleGraybox` world. A fresh packaged owner joined the already-running passive peer, and the peer reported `clients=2`.

This closes the Phase 1K.7 handoff defect. It does **not** complete component 2: a fresh no-QA physical-input repetition, mutual visibility, cross-client appearance agreement, and one normal movement remain unproven.

## Scope advanced

- Roadmap: Phase 1K — First-hour vertical slice, component 2 setup.
- Beta Game Bible: `First-hour player journey` — `1. Choose a default character` and `2. Enter the first city`.
- Player-facing risk reduced: a confirmed player no longer enters a private duplicate of Sundale while another client waits in the accepted shared session.

## Minimal implementation

- File: `client/OddsWell/Source/OddsWell/CharacterSelectionScreen.cpp`
- Replaced local `OpenLevel` with `APlayerController::ClientTravel` to the fixed machine-local Development endpoint `127.0.0.1:17777`.
- Added a fail-safe when no owning controller exists.
- Added one explicit handoff-start log marker and one focused assertion for the endpoint.
- Removed the now-unused gameplay-statics include.
- Added no discovery service, session browser, backend, dependency, or generalized networking layer.

The fixed endpoint is intentionally bounded by [[Design/Decisions/DEC-022 Machine Local Development GameNetDriver Boundary]]. It is not an external-beta or production-network design.

## Verification

- Unreal Editor Development compile: PASS.
- Unreal Game Development compile: PASS.
- Focused native `OddsWell.Character.SelectionState`: `1/1` PASS.
- Full native `OddsWell`: `49/49` PASS.
- Frozen Python suites: `105/105` PASS (`9 + 2 + 8 + 46 + 40`).
- Brain Admin `python -m brain_admin.server --check`: PASS.
- Windows Development BuildCookRun for Bootstrap and SundaleGraybox: PASS.
- Package audit: `50` files, `1,049,384,876` bytes, zero `.py` files.
- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `F4BA693DF3CD125689528B7298517096E1E8E053FF439136FDBD9A485EC03E54`.

## Fresh packaged membership evidence

Evidence root: `C:\tmp\OddsWellPhase1K8-20260806T035734Z`

1. The passive peer launched `/Game/Maps/SundaleGraybox?listen` on gameplay UDP `127.0.0.1:17777`.
2. The packaged owner followed the existing Development chooser driver through the normal production selection, save, and handoff code.
3. The owner saved non-default `masculine_tone_2` with the starter top and bottom.
4. The owner logged `mode=client_travel` and browsed `127.0.0.1:17777`.
5. The peer logged `ODDSWELL_SHARED_CITY_JOIN|clients=2|boundary=local_listen_server`.
6. The peer accepted the owner-submitted `masculine_tone_2` appearance through the client RPC.
7. The attempt stopped at membership. No route or component-3 action was performed.

Retained evidence hashes:

- `AutomatedOwner.log`: `3B4CC171B3676157A4E88650B4E7FC5C04B1A88EEB202B1EFDD79E03C1A5CA3D`
- `Peer.log`: `83616C9C63E26C669BE08A428A32AE07274213CF86D19BCCB6089C9D699662E2`
- `FocusedNative.log`: `C4A2F7F0335D233E4347AE5056149E8E783326419814236BBAEC3474671C5F66`
- `FullNative.log`: `2B31EFD982978C24B124C5F6BD9866BEFB4E4CB86B2CC961383E97383B79B57A`
- `BuildCookRun.log`: `939B3A45EC1F1607BA9D64D939BD19A83B39E0E0CB96BAF80D7795AAF8D02A97`

All packaged OddsWell processes and UDP `17777` endpoints were removed after the run.

## Evidence boundary

Windows Computer Use identified the correct owner and peer windows, but its action bridge failed repeatedly with `node_repl exec context not found`. A separate fresh no-QA owner reached the normal chooser and received no synthetic input; it made no selection and produced no handoff marker. The accepted packaged proof therefore uses the existing Development chooser driver to exercise the same production save and travel code.

This phase does not claim a successful physical keypress proof, player usability, mutual visibility, cross-client appearance agreement, replicated movement, beta readiness, external-network safety, or production readiness.

## Next gate

Phase 1K.8b should use one fresh no-QA owner with exactly `[Right, Enter]`. It must first reproduce peer `clients=2`. Only if membership holds may it measure mutual visibility, starter-appearance agreement, and one normal movement, then stop before component 3.
