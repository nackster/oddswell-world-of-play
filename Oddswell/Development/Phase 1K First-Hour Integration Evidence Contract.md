---
tags:
  - development
  - beta
  - phase-1k
  - evidence
status: accepted-baseline
date: 2026-08-04
---

# Phase 1K First-Hour Integration Evidence Contract

## Purpose

This is the canonical evidence contract for the minimum OddsWell first-hour route. It does not add or change gameplay. It defines what a future fresh packaged run must record before the existing bounded Phase 1B-1J evidence may be described as one integrated player journey.

The accepted minimum route is:

`fresh profile -> choose preset -> enter Sundale with one passive peer -> find and visit the Studio, job, stadium, ticket booth, clothing store, and furniture store -> earn +100 Odds Bucks -> place the approved Mesa/40 wager -> watch or use the approved S skip -> receive the exact settled-win receipt at balance 154 -> buy and explicitly equip the Sundale Signal Jacket -> prove peer visibility -> cold-restart and verify durable state`

The eight route components below each have bounded individual evidence. No fresh contiguous packaged first-hour session currently proves that all eight coexist.

## Session boundary

- Use one fresh isolated owner profile and a separate isolated passive-peer profile.
- Record the package commit, manifest hash, file count, byte count, executable hash, Unreal version, map, machine-local scope, and exact command lines before setup ends.
- Mark one explicit `setup_end_utc`. Every developer action after that point is an intervention and must be counted, timestamped, and described.
- An accepted human first-hour run permits zero developer interventions after setup. Assistance, coaching, state repair, teleporting, direct method calls, hidden answer disclosure, or restarting a failed step cannot be omitted from the record.
- A Development-only technical run may use diagnostic capture flags, but its record must identify every flag. A flag that drives player actions, teleports, mutates authority, supplies a result, or bypasses a prompt cannot satisfy observed-player exit evidence.
- The passive peer may observe and record replicated state but may not guide, move, pay, wager, buy, equip, or repair the owner's route after setup.

## Eight-component contract

### 1. Fresh profile and preset

- **Actions:** launch with no owner SaveGame, choose one non-default approved preset, confirm once, and enter normal play.
- **Location:** character selection -> `SundaleGraybox`.
- **Prerequisites:** validated eight-preset catalog; isolated owner user directory; no prior appearance, housing, ledger, wager, or ownership save.
- **Authority:** the existing validated local appearance record owns preset/top/bottom; demographic presentation changes no gameplay value.
- **Required evidence:** initial save absence; selected preset and starter item IDs; confirmation count; first normal-play map; appearance-save hash, size, and mtime; no fallback.
- **Reset:** delete only the isolated evidence profile after retained hashes and logs are copied; never alter a normal player profile.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]]; contiguous integration is **NOT RUN**.

### 2. Sundale and one passive peer

- **Actions:** the owner enters Sundale, sees the passive peer, moves by normal controls, and is seen by the peer in the starter appearance.
- **Location:** `SundaleGraybox`, local listen server bound to loopback only.
- **Prerequisites:** the owner and peer use separate isolated profiles; both submit server-validated appearances; the peer is already passive when timed player actions begin.
- **Authority:** Unreal server owns temporary identities, movement, and accepted replicated appearance; local saves remain the current source records.
- **Required evidence:** process identities; loopback endpoint; player labels; spawn and movement records; owner/peer appearance agreement; world collision retained; peer intervention count `0`.
- **Reset:** close both processes, preserve logs/captures, then remove only their isolated evidence profiles.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1D1 Local Two-Client Shared City Presence]], [[Development/Reports/Phase 1D2 Replicated Appearance and Starter Clothing]], and [[Development/Reports/Phase 1D3 Cold Reconnect Visible State Restore]]; contiguous integration is **NOT RUN**.

### 3. Discover the required locations and visit the Studio

- **Actions:** using normal movement, reach the Studio, job, stadium, ticket booth, clothing store, and furniture store; enter the empty Studio, move inside, exit, and return to its exact Sundale doorway.
- **Location:** the approved Sundale route and the private Studio interior.
- **Prerequisites:** no teleport or direct-location action after setup; blocking floor and interaction radii active.
- **Authority:** the packaged map owns route geometry and thresholds; the existing housing SaveGame owns Studio ownership and return position.
- **Required evidence:** ordered location arrivals with monotonic times; route distance; each exact prompt encountered; Studio structure `6`, furniture `0`, decorations `0`, snap points `0`; exact return error; housing-save hash/size/mtime.
- **Reset:** retain the owner profile for later route steps; cleanup occurs only after the final cold check.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]], [[Development/Reports/Phase 1E1 Private Empty Studio Enter and Exit]], and [[Development/Reports/Phase 1E2 Studio Ownership and Return Persistence]]; contiguous integration is **NOT RUN**.

### 4. Earn the first 100 Odds Bucks

- **Actions:** approach the physical job marker, observe its prompt, press `E`, and complete one accepted shift.
- **Location:** Sundale job interaction radius.
- **Prerequisites:** fresh authoritative ledger at balance `0`; Studio and peer state remain present; local clock source disclosed.
- **Authority:** the server validates map and proximity, then appends and persists the one existing job command before updating live state.
- **Required evidence:** exact prompt; one ledger entry with sequence, command ID, `+100`, reason, and balance `100`; next-eligible UTC; same-process retry blocked; read-only Admin projection agrees without mutation.
- **Reset:** do not reset between route steps; preserve the exact ledger chain for the wager and purchase.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1G3 Persistent First Job Payout]], [[Development/Reports/Phase 1G4 Rolling 24 Hour Job Recovery]], and [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]]; contiguous integration is **NOT RUN**.

### 5. Place the approved Mesa/40 wager

- **Actions:** walk to the physical stadium ticket booth, see `Press E to open betting odds`, open the existing browser, select Mesa Vista Sol and stake `40`, review once, then confirm once.
- **Location:** Sundale stadium ticket-booth interaction radius.
- **Prerequisites:** exact immutable current offer, equal public information, pre-lock state, one `+100` ledger entry, and balance `100`.
- **Authority:** the server owns offer identity, selection mapping, odds, lock time, stake, command identity, debit, and persistence. The client sends no raw team, price, probability, stake, balance, or command identity.
- **Required evidence:** prompt and menu capture; selected team; probability `42413307`; decimal odds `2.3577`; stake `40`; potential gross return `94`; first confirmation causes zero mutation; second confirmation creates one request and ledger sequence `2`, delta `-40`, balance `60`; repeated input adds nothing.
- **Reset:** do not replace or edit the profile; the exact request/lock/result chain must continue from these bytes.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1H26AM Exact Mesa 40 Canonical Wager Placement]]; contiguous integration is **NOT RUN**.

### 6. Watch or use the approved skip

- **Actions:** enter the stadium and either watch all `421` frames or press the approved player `S` control; do not invoke a direct QA skip.
- **Location:** Sundale stadium presentation.
- **Prerequisites:** exact public Season 1 Game 1 replay and seal; the wager chain from component 5 remains unchanged.
- **Authority:** the client consumes the sealed public replay and cannot change score, clock, events, actors, result, or seal.
- **Required evidence:** chosen view path; input; start/final frame; exact game/result identity, score, replay seal, and canonical trace; `resimulated=false`; no hidden simulator or athlete state displayed. The watched result must be the same result linked to component 7's settlement and receipt.
- **Reset:** preserve the same profile and immutable replay inputs for settlement evidence.
- **Status:** bounded watch/skip mechanics are proven in [[Development/Reports/Phase 1F3 Direct Archived Replay Consumption in Stadium]], [[Development/Reports/Phase 1F4 Readable Three Minute Stadium Presentation]], and [[Development/Reports/Phase 1F5 Replay View Result Invariance]], but that archived proof ends `101-104` while component 7's exact wager settlement is `79-113`. They are different game evidence and cannot be spliced; wager-linked watch/settlement coexistence is **NOT PROVEN**.

### 7. Receive exact Mesa win settlement

- **Actions:** allow the existing automatic authority path to produce its exact result link, win decision, `+94` payout, finalization, and ticket-booth receipt; open the receipt by normal proximity and `E` interaction.
- **Location:** authoritative local resume/settlement path and the Sundale ticket booth.
- **Prerequisites:** component 5's exact Mesa/40 request and debit; its matching immutable result, decision, and finalization identities; no manual save edit or direct settlement action.
- **Authority:** the existing event-linked settlement path owns the result, decision, payout command, ledger append, finalization, and receipt validation.
- **Required evidence:** exact request/lock/result/decision/finalization links; Mesa winner; sealed `79-113` settlement result; sequence `3`, `+94`, reason `match_winner_payout`, balance `154`; receipt shows stake `40`, returned `94`, net `+54`, ledger count `3`, and one close instruction; all read-only checks preserve bytes and mtime.
- **Reset:** retain the settled profile for the store step; no replay, projection, or ledger substitution is allowed.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1H26AN Automatic Exact Current Chain Mesa Win Decision on Local Resume]], [[Development/Reports/Phase 1H26AO Automatic Exact Current Chain Mesa 94 Return Application and Win Finalization on Local Resume]], [[Development/Reports/Phase 1H26AP Read Only Exact Automatic Mesa Win Reconciliation History]], [[Development/Reports/Phase 1H26AQ Read Only Player Facing Exact Automatic Mesa Win Receipt Compatibility]], and [[Development/Reports/Phase 1H26AR2 Automated Normal Path and Cold Process Exact Automatic Mesa Win Receipt Lifecycle Proof]]; one fresh route from component 1 is **NOT RUN**.

### 8. Buy, equip, show, and cold-restore the Signal Jacket

- **Actions:** walk to the clothing store, press `E` to review, press `E` to buy the `60`-Odds-Bucks Signal Jacket, explicitly equip it, and let the passive peer observe the slate-and-teal appearance. Then close the owner process and cold-launch from the same owner directory.
- **Location:** Sundale clothing-store radius, shared city, then a fresh owner process.
- **Prerequisites:** exact settled balance `154`, no prior jacket ownership, passive peer still present, and no developer action after setup.
- **Authority:** the server owns proximity, fixed item identity, fixed price, ownership command, debit, and replicated equip state. Equip is session state in the current slice.
- **Required evidence:** first `E` causes no debit; purchase appends sequence `4`, command `store:sundale:signal_jacket:purchase:v1`, delta `-60`, reason `clothing_purchase`, and expected integrated balance `94`; equip adds no entry; peer observes the exact jacket; cold owner launch restores preset, Studio ownership/return, all four ledger entries, balance `94`, settled wager, and jacket ownership. Because equip is not cold-persistent, the cold record must not claim automatic equip; any post-restart equip is an explicit new `E` action.
- **Reset:** after all retained hashes, logs, captures, and process exits are verified, remove only the isolated owner/peer evidence directories and confirm no process remains.
- **Status:** bounded individual proof exists in [[Development/Reports/Phase 1I2 Exact Sundale Signal Jacket Purchase]] and [[Development/Reports/Phase 1I3 Owned Signal Jacket Equip and Shared City Visibility]], with separate cold persistence proofs in Phases 1B, 1D, 1E, 1G, 1H, and 1I; the combined sequence-`4` balance-`94` route is **NOT RUN**.

## Required session record

Every future attempt must retain these fields even when it fails:

| Field group | Required fields |
| --- | --- |
| Identity | evidence ID, branch, commit SHA, build configuration, Unreal version, machine-local scope, owner process/profile ID, passive-peer process/profile ID, map, executable path |
| Time | setup start/end UTC, session start/end UTC, monotonic timestamp for every action/prompt/checkpoint, declared clock source, elapsed route time |
| Actions | ordered raw player inputs, resulting action, map/location, distance to interaction, accepted/rejected result |
| Prompts | exact visible text, first-seen time, response time, dismissal, capture path/hash |
| Confusion | observer timestamp, player question or hesitation, wrong turn/action, recovery, unresolved failure; `none observed` must be explicit rather than blank |
| Intervention | setup action count and description; after-setup developer action count, timestamp, actor, reason, and effect; omitted intervention invalidates the run |
| QA | every flag, driver, fixture, user directory, port, acceleration, and capture aid; whether it drives action, teleport, authority, result, or mutation |
| Hashes | executable, package manifest, replay fixture/seal, authoritative SaveGame before and after each mutation/read-only check, exported projections, retained captures/logs |
| Ledger | every sequence, command ID, delta, reason, running balance, request/finalization linkage, retry result, and expected final balance |
| Peer | join/leave time, temporary labels, movement and appearance agreement, starter/jacket observation, passive action count, process exit |
| Cold boundary | process A exit time/code, zero-process check, process B start time, same user-directory proof, before/between/after save size/hash/mtime, restored fields |
| No hidden data | public fixture/version inputs, hidden-field denylist result, `resimulated` value, answer/key exposure, private projection use, and any unavailable value shown to the player |

## Fail-fast rules

An attempt is failed and cannot be partially promoted when any of these occurs:

1. The owner profile is not fresh at component 1, or the owner/peer evidence directories are mixed.
2. The package, executable, fixture, save, projection, or replay identity does not match its recorded hash or accepted schema.
3. A required prompt, normal input, location/proximity check, authoritative mutation, ledger link, peer observation, or cold boundary is absent.
4. Any developer assists after setup, unless the run is explicitly retained as failed with that intervention recorded.
5. A QA flag drives actions, teleports, opens UI directly, alters time/authority, supplies a result, mutates persistence, or bypasses player prompts in a claimed observed-player run.
6. Logs, captures, hashes, or state from separate attempts are spliced together, except for the declared process A -> zero-process check -> process B cold boundary using the same unchanged owner directory.
7. A first confirmation, close, leave, retry, duplicate, or read-only view mutates money or authority.
8. The ledger is not exactly `+100 -> -40 -> +94 -> -60`, with balances `100 -> 60 -> 154 -> 94`, or any command/link is missing, duplicated, or foreign.
9. The watched game identity, final score, or seal differs from the result linked to settlement or shown on the receipt. The existing `101-104` archived replay and `79-113` settlement evidence may not be combined.
10. The passive peer acts, coaches, or fails to agree on the owner's visible starter and equipped-jacket states.
11. The cold run claims automatic jacket equip; current authority persists ownership, not equipped session state.
12. Hidden athlete/simulator values, answer keys, private settlement inputs, or invented explanations appear in the player surface.
13. A fatal, ensure, failed assertion, stale/partial acceptance, save-write failure, nonzero process exit, or leftover OddsWell/Unreal/test process remains.

Failure at any step stops the attempt. Preserve the failed evidence, name the measured cause, reset the isolated profiles, and schedule only the smallest corrective phase. Do not continue merely to produce a complete-looking record.

## Machine-local Development network distinction

Under [[Design/Decisions/DEC-022 Machine Local Development GameNetDriver Boundary]], the owner selected Option A for current machine-local Windows Development measurement only. A passive peer whose exact OddsWell game PID owns one gameplay `GameNetDriver` UDP endpoint at `127.0.0.1:17777` satisfies this contract's gameplay-network prerequisite for a new attempt.

This does not erase the failed Phase 1K.1 or Phase 1K.2 measurements, retroactively complete setup, or grant component credit. Unreal trace-control TCP `0.0.0.0:1985` remains recorded non-game Development diagnostic security debt. Whole-process loopback and network isolation are not proven. Trace control must be removed or contained and freshly verified before any external beta, release, deployment, shared or untrusted network, or production use.

## Baseline conclusion

The current repository contains bounded proof for each of the eight route components and separately accepted public athlete-story evidence under [[Development/Reports/Phase 1J Exit Review]]. It does not contain a fresh contiguous packaged first-hour run proving coexistence, zero post-setup developer intervention, first-time-player comprehension, beta readiness, or production readiness.

Phase 1K.4 corrected the first failure measured by Phase 1K.3 with one `GlobalDefaultGameMode` configuration entry. Fresh normal packaged Bootstrap startup now presents the existing approved chooser and remains unconfirmed after more than one minute of zero input. This does not complete component 1: no non-default preset was selected, confirmed, persisted, or handed into normal play.

## Attempt history

| Attempt | Date | Package / source identity | Outcome | First failure | Report |
| --- | --- | --- | --- | --- | --- |
| `phase1k1-20260805T004101Z` | 2026-08-04 local / 2026-08-05 UTC | existing Windows Development package; source baseline `fccfe73`; game executable SHA-256 `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` | **FAILED DURING SETUP; COMPONENTS 1-8 NOT REACHED** | passive peer listened on `0.0.0.0:7777` instead of loopback only; `setup_end_utc` was not reached | [[Development/Reports/Phase 1K1 Canonical Packaged First-Hour Contract Fail-Fast Technical Measurement]] |
| `phase1k2-20260805T010631Z` / `phase1k2b-20260805T010930Z` | 2026-08-04 local / 2026-08-05 UTC | unchanged Windows Development package; source baseline `32c3bb5`; game executable SHA-256 `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` | **TARGET GAMENETDRIVER LOOPBACK PASS; STRICT PID-WIDE PROOF FAILED; COMPONENTS 1-8 NOT REACHED** | `-multihome=127.0.0.1 -port=17777` produced exactly `127.0.0.1:17777` for gameplay, but the same OddsWell PID also owned Unreal trace-control TCP `0.0.0.0:1985`; `-notraceserver` did not remove it | [[Development/Reports/Phase 1K2 Loopback Only Passive Peer Launch Correction and Proof]] |
| `phase1k3-20260805T023402Z` | 2026-08-04 local / 2026-08-05 UTC | unchanged Windows Development package; source baseline `aaab386`; game executable SHA-256 `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` | **ACCEPTED PEER NETWORK PASSED; DEFAULT OWNER CHOOSER FAILED DURING SETUP; COMPONENTS 1-8 NOT REACHED** | fresh normal package startup loaded Bootstrap as plain `GameModeBase`, showed a black viewport, and produced no chooser, cards, preset/appearance state, prompt, modal, or owner SaveGame during `60.091` seconds of zero owner input | [[Development/Reports/Phase 1K3 Fresh Accepted Network Setup and Default Character Chooser Fail Fast Measurement]] |
| `phase1k4-20260805T142500Z` | 2026-08-05 | fresh Windows Development package; source baseline `49f982d`; game executable SHA-256 `13E0E660CF5A086F74F408631F80FC51DCF77488DC8A87CF79D761E59B9E019B` | **ACCEPTED PEER NETWORK PASSED; NORMAL DEFAULT CHOOSER PASSED; COMPONENTS 1-8 NOT REACHED** | no failure before the approved stop boundary: Bootstrap loaded `OddsWellCharacterSelectionGameMode`, showed all eight cards for `65.610` seconds with zero input, created no appearance SaveGame, and did not auto-confirm or enter the route | [[Development/Reports/Phase 1K4 Normal Bootstrap Character Chooser Correction and Fresh Proof]] |

The same failed setup also produced a secondary owner diagnostic: fresh Bootstrap loaded as plain `GameModeBase`, showed no chooser, emitted no appearance-save marker, and created no owner SaveGame during the bounded observation. It is not component-1 evidence because the earlier peer-bind failure had already invalidated setup.
