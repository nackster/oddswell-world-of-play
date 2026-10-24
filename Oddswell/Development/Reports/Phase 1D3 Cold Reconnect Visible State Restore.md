---
tags:
  - development
  - phase-1d
  - multiplayer
  - reconnect
  - unreal
status: complete
date: 2026-07-20
---

# Phase 1D.3 — Cold Reconnect Visible-State Restore

## Outcome

A local packaged client can leave Sundale, close, start as a new process, rejoin the same listen server, and restore the same server-visible preset, skin tone, starter top, and starter bottom from the existing validated local SaveGame record.

This is a local reconnect proof. It does not create a permanent player identity, account, profile backend, or production session service.

## Smallest implementation

- The production path remains the Phase 1B local appearance SaveGame plus the Phase 1D.2 server-validated appearance submission. No second persistence format was added.
- An opt-in reconnect QA path seeds the existing bounded QA SaveGame once, captures the first remote player's accepted preset/top/bottom tuple on the server, observes the remote leave, and compares it with a later joining pawn's submitted tuple.
- The comparison requires both records to be owner-submitted and exact across preset, top, and bottom. A fallback or changed preset cannot pass.
- The cold second client omits the preset override, loads the saved record with `source=loaded`, resubmits it through the normal server RPC, then deletes and verifies the QA save absent.
- The temporary proof label changes from `Player 2` to `Player 3`; permanent identity restoration remains outside this phase.

## Corrective evidence

The first packaged reconnect sequence restored the correct state, but it was rejected because the already-passed movement proof logged again every frame while the server waited for the reconnect. A single guard now prevents repeated movement-pass evidence, and reconnect completion prevents a second leave-capture line. The final package and all runtime evidence were rebuilt after that correction.

## Accepted packaged evidence

Windows Development BuildCookRun succeeded in `60.68s`. The fresh archive contains `54` files totaling `1,041,805,569` bytes. The listen server bound only to `127.0.0.1:7792`.

| Step | Accepted result |
| --- | --- |
| Host | `Player 1`, `masculine_tone_3` |
| First remote join | `Player 2`, `feminine_tone_4`, QA SaveGame seeded |
| First shared-city proof | one server movement pass at `305.7 cm` |
| Leave | server captured Player 2's accepted preset/top/bottom tuple |
| Cold rejoin | new process joined as temporary `Player 3` with `source=loaded` |
| Server restore | exact `feminine_tone_4` + `starter_offwhite_top` + `starter_offwhite_bottom` match |
| QA cleanup | save slot verified absent |
| Process exits | server `0`, first client `0`, reconnect client `0` |

The accepted server log contains exactly one movement pass, one reconnect leave capture, and one reconnect pass. The before/after clients both agreed with the host's visible state. The native, server, before-client, and after-client logs contain no fatal error, Unreal ensure, appearance error, rejected appearance, or failed QA result.

## Regression and integrity

- UE 5.8 editor and game builds: passed.
- Native `OddsWell.Character` automation: `5/5` passed.
- Frozen Python regressions: `65/65` passed in `137.551s`.
- Brain Admin self-check: passed.
- Python compilation and `git diff --check`: passed.
- Remaining OddsWell processes after validation: `0`.
- Cost: `$0.00`.

## Scope boundary

This does not add permanent identity, accounts, authentication, server-side profiles, external hosting, session discovery, matchmaking, invitations, friends, chat, voice, blocking/reporting, moderation, latency recovery, capacity conclusions, inventory ownership, trading, stores, Odds Bucks, wagering, final art, model training, or retraining. A reconnect receives a new temporary proof number and restores only the already-approved local appearance record.

## Next gate

Phase 1D.4 measures a small local client-count ladder before selecting any beta instance ceiling. Capacity remains evidence-driven, and external hosting still requires separate owner approval.
