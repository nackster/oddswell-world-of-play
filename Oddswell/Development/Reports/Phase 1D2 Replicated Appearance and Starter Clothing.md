---
tags:
  - development
  - phase-1d
  - multiplayer
  - character
  - unreal
status: complete
date: 2026-07-20
---

# Phase 1D.2 — Replicated Appearance and Starter Clothing

## Outcome

Two playable local packaged clients now agree on each player's selected placeholder preset, skin tone, starter top, and starter bottom. The server validates and republishes one compact appearance record per character; remote pawns no longer render from the viewing process's local save.

This closes the visible-state synchronization slice of [[Development/Beta Delivery Roadmap|Phase 1D]]. It is local evidence only, not production multiplayer or an account/profile system.

## Smallest implementation

- The existing character record validator now accepts the same preset/top/bottom tuple from either a local save or a network submission. Unknown presets, wrong slots, duplicates, and non-starter combinations are rejected.
- One replicated character struct carries `PresetId`, `TopItemId`, `BottomItemId`, and an `owner submitted` proof bit.
- The owning player resolves the already-approved local appearance, submits it to the server, and the server validates and republishes it to every viewer.
- The server may render a deterministic fallback while a player joins, but that fallback cannot satisfy the Phase 1D.2 pass gate. Both owners must submit accepted records.
- The existing primitive skin material and separate replaceable starter top/bottom components render the replicated tuple. No inventory, ownership, account, profile service, database, multiplayer plugin, or new dependency was added.

## Corrective evidence

The first packaged comparison was rejected. The joining client synchronized correctly, but the listen server briefly treated its deterministic remote fallback as final evidence. A replicated `owner submitted` bit was added and the pass now waits for both accepted owner records.

The next packaged comparison exposed a listen-host lifecycle error: possession occurred before the placeholder materials and QA flags were initialized, so the host did not publish its selected preset. Host submission moved to initialized `BeginPlay`; the corrected evidence was rebuilt and rerun from a fresh package.

## Accepted packaged evidence

Windows Development BuildCookRun succeeded in `53.91s`. The fresh archive contains `53` files totaling `1,041,792,530` bytes. One packaged listen server bound only to `127.0.0.1:7790`; one packaged client joined it. Both wrapper and game processes exited `0` without forced termination.

| Evidence | Listen server view | Joining client view |
| --- | --- | --- |
| Local player | `Player 1` | `Player 2` |
| Local preset | `masculine_tone_3` | `feminine_tone_4` |
| Other preset | `feminine_tone_4` | `masculine_tone_3` |
| Local starter clothing | `starter_offwhite_top` + `starter_offwhite_bottom` | same |
| Other starter clothing | same | same |
| Record agreement | `true` | `true` |

The server accepted Player 1 from the host's `shared_city_qa` choice and Player 2 through the client RPC. It then measured `305.0 cm` of authoritative Player 2 movement and passed with `replicated_movement=true`, `appearance_synced=true`, and `starter_clothing_synced=true`.

No fatal error, Unreal ensure, appearance error, or rejected appearance record exists in the accepted native, server, or client logs. All accepted processes closed normally, and the two orphaned children from the earlier rejected run were identified by exact command line and closed before final hygiene checks.

## Regression and integrity

- UE 5.8 editor and game builds: passed.
- Native `OddsWell.Character` automation: `5/5` passed.
- Frozen Python regressions: `65/65` passed in `150.162s`.
- Brain Admin self-check: passed.
- Python compilation and `git diff --check`: passed.
- Remaining OddsWell processes after validation: `0`.
- Cost: `$0.00`.

## Scope boundary

This does not add reconnect restoration, capacity evidence, accounts, permanent names, authentication, external hosting, deployment, matchmaking, invitations, friends, chat, voice, blocking/reporting, moderation, inventory ownership, trading, stores, Odds Bucks, wagering, final character art, rigging, animation, model training, or retraining. The approved local appearance save remains the only local source record.

## Next gate

Phase 1D.3 proves that a local client can leave, rejoin the same Sundale session, and restore the same server-visible preset and starter clothing. Capacity measurement remains after reconnect evidence.
