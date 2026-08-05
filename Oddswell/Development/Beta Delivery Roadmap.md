---
tags:
  - development
  - beta
  - roadmap
  - scope
status: active
date: 2026-07-19
---

# OddsWell Beta Delivery Roadmap

## Purpose

This roadmap converts [[Design/Beta Game Bible|OddsWell Beta Game Bible]] into a dependency-ordered delivery path. The Bible defines **what** the beta is. This roadmap defines the current expected **order**. [[Development/Current Plan|Current Plan]] and phase reports prove **what is actually complete**.

The roadmap is intentionally made of measurable product gates, not hundreds of speculative tasks. The Scope Director may split a phase into the smallest truthful subphase, but it may not skip dependencies, invent an OPEN decision, or begin Version 1 early.

## Status labels

- **COMPLETE:** committed and validated evidence exists.
- **ACTIVE:** current delivery area.
- **OWNER GATE:** progress requires an explicit owner decision or approval.
- **PENDING:** dependency is not complete.
- **BETA EXIT:** release-wide evidence and owner acceptance are required.

## Current checkpoint

- Phase 0 simulation foundation: **COMPLETE and frozen** except for demonstrated defects or a measured beta requirement.
- Phase 1A.0 local 3D readiness audit: **COMPLETE** at commit `2634541`.
- Phase 1A.1a Unreal Engine 5.8 installation and first-editor-launch verification: **COMPLETE**; see [[Development/Reports/Phase 1A1a Unreal Engine Installation and Editor Launch Verification]].
- Phase 1A.1b official Microsoft Visual C++ x64 runtime alignment and post-reboot Unreal recheck: **COMPLETE**; see [[Development/Reports/Phase 1A1b Visual Cpp Runtime Prerequisite Alignment and Unreal Recheck]].
- Phase 1A.1c smallest empty local Windows project creation and reopen: **COMPLETE**; see [[Development/Reports/Phase 1A1c Minimal Blank OddsWell Project Bootstrap and Reopen]].
- Phase 1A.1d empty Windows package, launch, and baseline measurement: **COMPLETE**; see [[Development/Reports/Phase 1A1d Empty Windows Package Launch and Baseline Measurement]].
- Phase 1A.2a noncanonical primitive street block, basketball court, and representative asset iteration: **COMPLETE**; see [[Development/Reports/Phase 1A2a Noncanonical Street Block and Basketball Court Graybox]].
- Phase 1A.2b direct rendering of the existing verified 421-frame replay: **COMPLETE**; see [[Development/Reports/Phase 1A2b Authoritative 421-Frame Replay Renderer]].
- Phase 1A.3 Unreal Engine 5.8 beta adoption: **COMPLETE** by owner decision on July 19, 2026; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].
- Phase 1B camera/movement and minimum placeholder preset direction: **APPROVED**; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults]].
- Phase 1B.1 validated character preset and starter-outfit catalog: **COMPLETE**; see [[Development/Reports/Phase 1B1 Character Preset Catalog]].
- Phase 1B.2 fast local character-selection screen with a safe default: **COMPLETE**; see [[Development/Reports/Phase 1B2 Fast Local Character Selection Screen]].
- Phase 1B.3 controllable primitive placeholder and approved locomotion: **COMPLETE**; see [[Development/Reports/Phase 1B3 Controllable Placeholder Avatar and Approved Locomotion]].
- Phase 1B.4 separate replaceable starter outfit: **COMPLETE**; see [[Development/Reports/Phase 1B4 Replaceable Starter Outfit]].
- Phase 1B.5 local appearance persistence and first-playable handoff: **COMPLETE**; see [[Development/Reports/Phase 1B5 Local Character Appearance Persistence and First-Playable Handoff]].
- Phase 1B character onboarding exit review: **COMPLETE**; see [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].
- Phase 1C.0 noncanonical first-city concept packages: **COMPLETE**; see [[Development/Reports/Phase 1C0 Noncanonical First City Concept Packages]].
- Phase 1C owner selection: **COMPLETE**. The owner selected Concept B — Daymark / Sundale on July 20, 2026; see [[Design/Decisions/DEC-008 Beta First City Direction]].
- Phase 1C.1 minimal art-direction and loop freeze: **COMPLETE**; see [[Development/Reports/Phase 1C1 Sundale Art Direction and Core Loop Freeze]].
- Phase 1C.2 primitive Sundale graybox and packaged route measurement: **COMPLETE**; see [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].
- Phase 1C exit: **PASSED**. The primitive city route is measurable and traversable; final city art remains unbuilt.
- Phase 1D owner defaults: **RESOLVED**; see [[Design/Decisions/DEC-010 Phase 1D Shared City Defaults]].
- Phase 1D.1 local two-client shared-city presence: **COMPLETE**; see [[Development/Reports/Phase 1D1 Local Two-Client Shared City Presence]].
- Phase 1D.2 replicated appearance and starter clothing: **COMPLETE**; see [[Development/Reports/Phase 1D2 Replicated Appearance and Starter Clothing]].
- Phase 1D.3 cold reconnect and visible-state restore: **COMPLETE**; see [[Development/Reports/Phase 1D3 Cold Reconnect Visible State Restore]].
- Phase 1D.4 local concurrency ladder: **COMPLETE**; see [[Development/Reports/Phase 1D4 Local Concurrency Ladder]].
- Phase 1D exit: **PASSED FOR THE LOCAL PROTOTYPE**. No beta instance ceiling or external-host readiness is claimed.
- Phase 1E owner defaults: **RESOLVED FOR THE FIRST STUDIO**; see [[Design/Decisions/DEC-011 Empty Starter Studio]] and [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]].
- Phase 1E.1 private empty Studio enter/exit: **COMPLETE**; see [[Development/Reports/Phase 1E1 Private Empty Studio Enter and Exit]].
- Phase 1E.1a continuous mouse camera orbit correction: **COMPLETE**; see [[Development/Reports/Phase 1E1a Continuous Mouse Camera Orbit Correction]].
- Phase 1E.2 Studio ownership and return persistence: **COMPLETE**; see [[Development/Reports/Phase 1E2 Studio Ownership and Return Persistence]].
- Phase 1E.3 six-tier housing progression catalog: **COMPLETE**; see [[Development/Reports/Phase 1E3 Six-Tier Housing Progression Catalog]].
- Phase 1E.4 player-visible locked housing goals: **COMPLETE**; see [[Development/Reports/Phase 1E4 Player-Visible Locked Housing Goals]].
- Phase 1E standalone foundation: **COMPLETE THROUGH CURRENT DEPENDENCIES**. Phase 1I.4 now activates the first predefined Studio snap only after a legitimate furniture purchase and ownership record; larger interiors, prices, requirements, and additional snap points remain open.
- Phase 1F.1 player league view: **COMPLETE**; see [[Development/Reports/Phase 1F1 Player League View]].
- Phase 1F.2 stadium and public viewing-location graybox: **COMPLETE**; see [[Development/Reports/Phase 1F2 Stadium and Public Viewing Graybox]].
- Phase 1F.3 direct archived replay consumption in the stadium: **COMPLETE**; see [[Development/Reports/Phase 1F3 Direct Archived Replay Consumption in Stadium]].
- Phase 1F.4 readable three-minute fixed-camera presentation: **COMPLETE**; see [[Development/Reports/Phase 1F4 Readable Three Minute Stadium Presentation]] and [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]].
- Phase 1F.5 replay-view result invariance: **COMPLETE**; see [[Development/Reports/Phase 1F5 Replay View Result Invariance]].
- Phase 1F exit: **PASSED FOR THE CURRENT ARCHIVED-GAME SLICE**. The 82-game/two-team variety decision remains open and no backend reconnect is claimed.
- Phase 1G.1 empty server-authoritative Odds Bucks ledger: **COMPLETE**; see [[Development/Reports/Phase 1G1 Empty Server Authoritative Odds Bucks Ledger]].
- Phase 1G.2 server-validated placeholder Job interaction: **COMPLETE**; see [[Development/Reports/Phase 1G2 Server Validated Placeholder Job Interaction]].
- Phase 1G.3 persistent first job payout: **COMPLETE FOR ONE LOCAL SAVED PROFILE**; see [[Development/Reports/Phase 1G3 Persistent First Job Payout]] and [[Design/Decisions/DEC-014 Phase 1G3 Provisional First Job Payout]].
- Phase 1G.4 rolling job recovery: **COMPLETE FOR ONE LOCAL SAVED PROFILE**; start at `0`, earn `100` per successful shift on a rolling `24`-hour cooldown, accumulate balances, and provide no separate allowance or catch-up payout. See [[Development/Reports/Phase 1G4 Rolling 24 Hour Job Recovery]] and [[Design/Decisions/DEC-015 Phase 1G4 Rolling Job Recovery Defaults]].
- Phase 1G.5 read-only Admin reconciliation: **COMPLETE FOR ONE LOCAL SAVED PROFILE**; Unreal publishes a validated output-only ledger projection, and Brain Admin independently validates and displays the balance, entries, and next-job eligibility without economy commands. See [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]].
- Phase 1G exit: **PASSED FOR THE CURRENT LOCAL-PROFILE DEPENDENCY**. No online account, trusted backend clock, production authorization, price, purchase, wager, settlement, payment, or second currency is claimed.
- Phase 1H.0 basketball/odds/wager isolation: **ARCHITECTURE APPROVED** under [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]]. This adds no wager behavior.
- Phase 1H.1 Match Winner rules: **OWNER APPROVED** under [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]].
- Phase 1H.2 versioned Match Winner odds offer: **COMPLETE AS AN ISOLATED CALCULATION CONTRACT**; see [[Development/Reports/Phase 1H2 Versioned Match Winner Odds Offer]].
- Phase 1H.3 idempotent Match Winner request and stake debit: **COMPLETE AS A MACHINE-LOCAL PERSISTENCE PRIMITIVE**; see [[Development/Reports/Phase 1H3 Idempotent Match Winner Stake Debit]]. No player-facing route, lock transition, or settlement exists.
- Phase 1H.4 idempotent Match Winner game-start lock: **COMPLETE AS A MACHINE-LOCAL PERSISTENCE PRIMITIVE**; see [[Development/Reports/Phase 1H4 Idempotent Match Winner Game Start Lock]]. No result consumption or settlement exists.
- Phase 1H.5 immutable sealed Match Winner result linkage: **COMPLETE FOR THE EXACT SEASON 1, GAME 1 ARCHIVE ONLY**; see [[Development/Reports/Phase 1H5 Immutable Sealed Match Winner Result Linkage]]. No wager win/loss decision, settlement, return, payout, loss finalization, refund, void, correction, ledger mutation, UI, Admin wager view, props, backend, or brain change exists.
- Phase 1H.6 immutable deterministic Match Winner settlement decision: **COMPLETE FOR THE EXACT HARBOR-SELECTED LOSS ONLY**; see [[Development/Reports/Phase 1H6 Immutable Deterministic Match Winner Settlement Decision]]. The record is `lost`, gross return due `0`, and `decided_pending_apply`; no application, settled status, or ledger change exists.
- Phase 1H.7 idempotent exact-loss finalization: **COMPLETE FOR THE EXACT HARBOR-SELECTED LOSS ONLY**; see [[Development/Reports/Phase 1H7 Idempotent Exact Loss Finalization]]. One separate immutable record is `settled_lost` with gross return applied `0`; the prior decision, two-entry ledger, balance `60`, and cooldown remain unchanged.
- Phase 1H.8 read-only exact-loss reconciliation/history: **COMPLETE FOR ONE MACHINE-LOCAL OPERATIONS CARD**; see [[Development/Reports/Phase 1H8 Read Only Exact Loss Reconciliation History]]. Brain Admin independently validates the whole exact chain and exposes no mutation control or partial invalid evidence.
- Phase 1H.9 immutable exact-win return-due decision: **COMPLETE FOR ONE ISOLATED MESA-SELECTED QA CHAIN**; see [[Development/Reports/Phase 1H9 Immutable Exact Win Settlement Decision and Return Due Binding]]. The decision binds probability `40000000`, the approved formula, `won`, return due `100`, and `decided_pending_apply` without applying or finalizing the return or mutating the ledger.
- Phase 1H.10 idempotent exact-win application/finalization: **COMPLETE FOR THE SAME ISOLATED MESA-SELECTED QA CHAIN**; see [[Development/Reports/Phase 1H10 Idempotent Exact Win Return Application and Finalization]]. One atomic SaveGame write adds exactly one `+100` `match_winner_payout` entry and one separate immutable `settled_won` finalization, moving the ledger from `2/60` to `3/160` while leaving the cooldown and prior decision unchanged.
- Phase 1H.11 read-only exact-win reconciliation/history: **COMPLETE**; see [[Development/Reports/Phase 1H11 Read Only Exact Win Reconciliation History]]. The existing v1 projection/card validates exact stake and payout entries, settled win, count `3`, balance `160`, and net `+60`; invalid evidence reveals nothing and exposes no controls. Live browser/DOM inspection passed.
- Phase 1H.12 immutable authoritative canceled-game evidence link: **COMPLETE FOR ONE EXPLICITLY NONCANONICAL QA CHAIN ONLY**; see [[Development/Reports/Phase 1H12 Immutable Authoritative Canceled Game Evidence Link]]. One schema-v1 record links the exact request and lock to server cancellation command/evidence IDs, time, `game_canceled`, and `closed_canceled`; no refund, ledger credit, settlement, finalization, reconciliation, Admin/player UI, or canonical Game 1 relabeling occurs.
- Phase 1H.13 immutable exact canceled-wager void/refund-due decision: **COMPLETE FOR THE SAME NONCANONICAL QA CHAIN ONLY**; see [[Development/Reports/Phase 1H13 Immutable Exact Canceled Wager Void Refund Due Decision]]. One schema-v1 decision derives stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund` from exact H12 evidence. No refund is applied; the ledger remains `2/60` and no finalization, reconciliation, Admin/player UI, or canonical Game 1 change occurs.
- Phase 1H.14 idempotent exact canceled-wager refund application/finalization: **COMPLETE FOR THE SAME NONCANONICAL QA CHAIN ONLY**; see [[Development/Reports/Phase 1H14 Idempotent Exact Canceled Wager Refund Application and Finalization]]. One atomic schema-v11 SaveGame write appends sequence `3`, `+40`, `match_winner_refund`, balance `100`, plus one immutable `settled_void` finalization. H13 stays pending; exact retry is duplicate-safe; malformed, conflicting, second, normal-overlap, tampered, or anomalous evidence fails closed.
- Phase 1H.15 read-only exact canceled-wager reconciliation/history: **COMPLETE FOR THE SAME NONCANONICAL QA CHAIN ONLY**; see [[Development/Reports/Phase 1H15 Read Only Exact Canceled Wager Reconciliation History]]. The existing v1 writer, endpoint, independent validator, and Operations card bind exact cancellation evidence, stake `2/-40/60`, H13 pending decision, refund `3/+40/100`, `settled_void`, count `3`, balance `100`, and net `0`. Invalid or invented result evidence reveals nothing; the card has no controls. Live browser/API proof passed.
- Phase 1H.16 player-facing exact offer preview: **COMPLETE AT THE SEPARATE SUNDALE SPORTSBOOK FRONTAGE ONLY**; see [[Development/Reports/Phase 1H16 Player Facing Match Winner Offer Preview]]. The exact canonical Season 1, Game 1 offer remains visible read-only.
- Phase 1H.17 player-facing upcoming QA request: **COMPLETE FOR ONE EXPLICITLY NONCANONICAL MACHINE-LOCAL OFFER ONLY**; see [[Development/Reports/Phase 1H17 Player Facing Upcoming QA Match Winner Request]]. At the same frontage, QA mode proves team/stake selection, exact-return review, explicit confirm, one atomic pending request plus linked debit, cold duplicate safety, and zero-mutation rejection.
- Phase 1H.18 cold-restored pending receipt: **COMPLETE FOR THE EXACT H17 QA REQUEST ONLY**; see [[Development/Reports/Phase 1H18 Cold Restored Pending Match Winner Receipt]]. A separate read-only process exposes the exact request, offer, selection, stake, times, pending status, linked debit, and balance at the frontage; invalid or invented evidence exposes nothing, leaving closes it, and the persisted state remains byte-for-byte unchanged.
- Phase 1H.19 exact upcoming QA game-start lock: **COMPLETE FOR THE EXACT H17 QA REQUEST ONLY**; see [[Development/Reports/Phase 1H19 Exact Upcoming QA Game Start Lock]]. At fixed server-owned QA time `2100086400`, one parameterless transition appends fixed immutable lock `qa:h19:match_winner:lock:1`. The H17 request, offer, selection, debit, balance, and cooldown remain byte-for-value; exact cold retry is duplicate-safe and invalid or malformed evidence mutates nothing.
- Phase 1H.20 immutable authoritative upcoming QA cancellation evidence: **COMPLETE FOR THE EXACT H17/H19 QA CHAIN ONLY**; see [[Development/Reports/Phase 1H20 Immutable Authoritative Upcoming QA Cancellation Evidence]]. At fixed post-lock server time `2100086700`, one parameterless transition records fixed `game_canceled` / `closed_canceled` evidence. The H17 request/debit, H19 lock, ledger `2`, balance `60`, and cooldown remain unchanged; exact cold retry is duplicate-safe and every scoped invalid, malformed, fabricated-result, or completed-H16 case mutates nothing.
- Phase 1H.21 immutable exact upcoming QA void/refund-due decision: **COMPLETE FOR THE EXACT H17/H19/H20 QA CHAIN ONLY**; see [[Development/Reports/Phase 1H21 Immutable Exact Upcoming QA Void Refund Due Decision]]. One fixed parameterless transition derives Sparks, stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund`. Ledger `2`, balance `60`, and cooldown remain unchanged; no refund credit or finalization exists.
- Phase 1H.22 idempotent exact upcoming QA refund application/finalization: **COMPLETE FOR THE EXACT H17/H19/H20/H21 QA CHAIN ONLY**; see [[Development/Reports/Phase 1H22 Idempotent Exact Upcoming QA Refund Application and Finalization]]. One fixed parameterless transition atomically appends sequence `3`, `+40` `match_winner_refund`, balance `100`, plus a separate immutable `settled_void` finalization. H21 remains pending immutable; cold exact retry is duplicate-safe and the scoped rejection matrix mutates nothing.
- Phase 1H.23 player-facing ticket-booth odds presentation cleanup: **COMPLETE FOR THE CURRENT NORMAL-PLAY PLACEHOLDER ONLY**; see [[Development/Reports/Phase 1H23 Player Facing Ticket Booth Odds Presentation Cleanup]]. At the existing sportsbook route point, proximity shows exactly `Press E to open betting odds`; `E` shows a concise read-only matchup/odds/stake/lock panel with one close instruction. Technical offer identity and QA evidence remain off-screen, and the always-on league shortcut hint is removed.
- Phase 1H.24 graphical ticket-booth basketball market browser: **COMPLETE FOR THE CURRENT READ-ONLY PRESENTATION ONLY**; see [[Development/Reports/Phase 1H24 Graphical Ticket Booth Basketball Market Browser]]. The native Unreal HUD now presents a researched four-tab basketball layout, real Match Winner cards, a read-only bet slip, mouse/keyboard/controller navigation, explicit active/locked text, and modal control handling. Margin, Overtime, Points, Rebounds, and Personal Fouls are visible future categories with no published odds.
- Phase 1H.25 read-only exact upcoming QA reconciliation/history: **COMPLETE FOR THE EXACT H17-TO-H22 MACHINE-LOCAL QA CHAIN ONLY**; see [[Development/Reports/Phase 1H25 Read Only Exact Upcoming QA Wager Reconciliation History]]. The existing reconciliation-v1 writer, endpoint, validator, and single Operations card now show the exact Sparks cancellation/refund chain only after every fixed link, amount, timestamp, ledger entry, and status validates. Invalid or partial evidence shows nothing and no controls exist.
- Phase 1H.26A immutable canonical scheduled-unplayed game record: **COMPLETE FOR ONE ACTIVE LOCAL-BETA GAME ONLY**; see [[Development/Reports/Phase 1H26A Immutable Canonical Scheduled Unplayed Game Record]] and [[Design/Decisions/DEC-018 Canonical Local Beta Schedule Timing]]. A separate schema-v1 SaveGame fixes fresh Season `1`, Game `1`, Harbor home versus Mesa away, server-owned creation time, exact `+1,800`-second tipoff, offer eligibility at creation, no offer, and `scheduled_unplayed`. Exact retry/cold restore is identical; conflict or preexisting result-like state rejects without rewrite. The completed `PublicSeason1` archive and every Season `100` QA record remain untouched.
- Phase 1H.26B immutable equal-public pregame prediction commitment: **COMPLETE FOR THE SAME ACTIVE LOCAL-BETA GAME ONLY**; see [[Development/Reports/Phase 1H26B Immutable Equal Public Pregame Prediction Commitment]] and [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]]. A separate schema-v1 SaveGame binds the exact H26A opener to fresh `0-0` standings, equal `7`-day rest, existing public fictional rosters/ratings/availability/projected minutes, `oddswell-public-pregame-v1`, `phase0d4-v1`, `public_elo_rotation`, and deterministic SHA-256. Exact cold retry is immutable and duplicate-safe; malformed evidence rejects without rewrite. No completed archive input, offer, odds, UI, wager, simulation, or result was added.
- Phase 1H.26C immutable canonical Match Winner offer record: **COMPLETE FOR THE SAME ACTIVE LOCAL-BETA GAME ONLY**; see [[Development/Reports/Phase 1H26C Immutable Canonical Match Winner Offer Record]]. Before tipoff, one dedicated two-field SaveGame stores the canonical ID and JSON built by the existing exact odds contract from H26A and H26B. Exact cold retry is immutable; input, time, nested-field, or persisted conflict rejects without rewrite. H26A/H26B remain byte/hash/mtime identical. This adds no canonical player UI, slip, request, debit, lock transition, simulation, result, settlement, or later market.
- Phase 1H.26D player-facing read-only canonical Match Winner offer: **COMPLETE FOR THE SAME ACTIVE LOCAL-BETA GAME ONLY**; see [[Development/Reports/Phase 1H26D Player Facing Read Only Canonical Match Winner Offer]]. Before server tipoff, the existing ticket-booth HUD displays the exact H26C teams, integer-backed decimal odds, `10`–`100` step `10`, gross-return convention, tipoff, and local-beta scope. Missing, mismatched, tampered, or locked evidence shows one unavailable panel with no teams or prices. The older H16/PublicSeason1 offer is not a live fallback, and no selection, request, debit, or mutation exists.
- Phase 1H.26E server-authoritative canonical Match Winner request and atomic stake debit: **COMPLETE FOR ONE EXACT ACTIVE LOCAL-BETA REQUEST ONLY**; see [[Development/Reports/Phase 1H26E Server Authoritative Canonical Match Winner Request and Atomic Stake Debit]]. The server reloads exact H26A/H26B/H26C, owns UTC and the stable request command, accepts only exact offer/team/whole stake input, and atomically persists one versioned `accepted_pending_lock` request plus its linked debit. The accepted proof is sequence `2`, `-40`, balance `60`; exact cold retry is duplicate-safe and all rejection/atomic-failure fixtures leave zero mutation.
- Phase 1H.26F cold-restored read-only canonical pending wager receipt: **COMPLETE FOR THE EXACT H26E REQUEST ONLY**; see [[Development/Reports/Phase 1H26F Cold Restored Read Only Canonical Pending Wager Receipt]]. Before tipoff, the existing booth independently requires exact H26A/H26B/H26C, schema-`12` request/debit, Harbor selection, stake `40`, potential gross `69`, balance `60`, and no downstream evidence before showing `BET ACCEPTED / PENDING TIPOFF`. Missing request preserves the H26D offer; malformed, multiple, migrated, downstream, at-tipoff, or post-tipoff evidence fails closed with no partial values or writes.
- Phase 1H.26G server-owned exact canonical game-start lock: **COMPLETE FOR THE EXACT H26E REQUEST ONLY**; see [[Development/Reports/Phase 1H26G Server Owned Exact Canonical Game Start Lock]]. At exact H26A tipoff, one parameterless authoritative transition reloads exact H26A/H26B/H26C plus current schema-`12` H26E evidence and appends exactly one separate immutable lock linked to Season `1`, Game `1`. It preserves the request, ledger `2/-40/60`, balance, cooldown, upstream records, and all first-written times. Exact cold retry is duplicate-safe; early, late, malformed, migrated, multiple, conflicting, downstream, or failed-write evidence mutates nothing. The post-lock booth exposes only an unavailable/locked panel with no pending receipt, teams, prices, result, or controls.
- Phase 1H.26H immutable canonical active-game execution commitment: **COMPLETE FOR THE EXACT H26G-LOCKED GAME ONLY**; see [[Development/Reports/Phase 1H26H Immutable Canonical Active Game Execution Commitment]]. One parameterless transition persists a private schema-v1 `committed_for_execution` record. Its versioned seed material uses only immutable H26A schedule fields and the H26B SHA-256; its frozen input binds every current `simulate_scheduled_game` version, exact roster/rating, zero opening state, and full consistency/involvement snapshot. Wager/economy/post-lock caller data cannot affect it. Exact cold retry is immutable and duplicate-safe; missing, malformed, tampered, downstream, or failed-write evidence rejects. Nothing is exposed through the offer, booth, league, reconciliation, player UI, or Admin.
- Phase 1H.26I private canonical game execution receipt: **COMPLETE FOR THE EXACT H26H COMMITMENT ONLY**; see [[Development/Reports/Phase 1H26I Private Canonical Game Execution Receipt]]. One parameterless native handoff writes exact H26H canonical JSON under private Saved evidence. One external offline standard-library consumer revalidates it, executes the frozen simulator once, and atomically writes one commitment-keyed `executed_pending_seal` receipt containing hashes and one opaque private output digest only. Cold duplicate does not re-execute or rewrite. Python is not bundled or runtime-enabled; no score, winner, tape, event log, replay, result, settlement, Odds Bucks link, UI, Admin, service, or port was added.
- Phase 1H.26J immutable private canonical execution digest seal: **COMPLETE FOR THE EXACT H26H COMMITMENT AND H26I RECEIPT ONLY**; see [[Development/Reports/Phase 1H26J Immutable Private Canonical Execution Digest Seal]]. One offline standard-library verifier independently reruns the frozen simulator solely to recompute the opaque digest, requires exact H26I equality, and atomically writes one commitment-keyed `sealed_pending_result` record containing hashes and fixed version/status metadata only. Exact cold retry does not rerun or rewrite; missing, multiple, wrong-digest, tampered, conflicting, or extra evidence rejects without repair. Python remains absent from the package, and no score, winner, statistics, tape, replay, result record, settlement, Odds Bucks link, UI, Admin, service, or port was added.
- Phase 1H.26K immutable private canonical game result record: **COMPLETE FOR THE EXACT H26H/H26I/H26J CHAIN ONLY**; see [[Development/Reports/Phase 1H26K Immutable Private Canonical Game Result Record]]. One offline standard-library recorder revalidates the entire private chain, reruns the frozen simulator once, requires its replay SHA-256 to equal H26J, and atomically records only Season `1`, Game `1`, scheduled teams, integer `99`–`104` score, Mesa winner, hashes, and fixed version/status metadata. Cold duplicate recomputes once without rewrite; upstream, score, identity, winner, digest, hash, or validly rehashed conflicts reject without repair. No archive input, published replay, tape, presentation, standings, statistics, decision, settlement, Odds Bucks link, UI, Admin, service, or port was added.
- Phase 1H.26L server-owned immutable canonical Match Winner result link: **COMPLETE FOR THE EXACT ACTIVE H26E–H26K CHAIN ONLY**; see [[Development/Reports/Phase 1H26L Server Owned Immutable Canonical Match Winner Result Link]]. One parameterless native transition validates exact H26A/B/C, schema-`12` H26E request/debit, H26G lock, H26H commitment, H26J seal, and exactly one H26K result before deriving a command ID from the H26K record hash and appending one immutable request/lock/result link. Ledger `2/-40/60`, request, lock, and H26A–H26K evidence stay unchanged; decisions/finalizations/cancellations/refunds/payouts remain `0`. The archived `101`–`104` contract stays separately exact, with no fallback or relabel.
- Phase 1H.26M server-owned deterministic canonical Match Winner loss decision: **COMPLETE FOR THE EXACT HARBOR-SELECTED, MESA-WINNER H26E/H26G/H26L CHAIN ONLY**; see [[Development/Reports/Phase 1H26M Server Owned Deterministic Canonical Match Winner Loss Decision]]. One parameterless transition derives its command solely from H26L/H26K identity and reuses the existing deterministic decision primitive to append one immutable `lost`, gross-return-due `0`, `decided_pending_apply` record. Ledger `2/-40/60`, request, lock, result link, and H26A–H26K evidence stay unchanged; no finalization, application, credit, payout, refund, history, UI, Admin, replay, statistics, or brain/simulator change exists.
- Phase 1H.26N server-owned exact canonical Match Winner loss finalization: **COMPLETE FOR THE SAME EXACT H26M LOSS CHAIN ONLY**; see [[Development/Reports/Phase 1H26N Server Owned Exact Canonical Match Winner Loss Finalization]]. One parameterless transition derives its command solely from H26M/H26K identity and reuses the existing loss-finalization primitive to append one immutable `settled_lost` record with gross return applied `0`, ledger count `2`, and balance `60`. The H26M decision remains `decided_pending_apply`; no ledger entry, credit, payout, refund, correction, UI, Admin, replay, statistics, or brain/simulator change exists.
- Phase 1H.26O read-only exact canonical Match Winner loss reconciliation/history: **COMPLETE FOR THE SAME EXACT H26A–H26N LOSS CHAIN ONLY**; see [[Development/Reports/Phase 1H26O Read Only Exact Canonical Match Winner Loss Reconciliation History]]. The existing v1 atomic writer, API, independent validator, and single Operations card show the exact request price, `97–101` Mesa result, `0` return, `-40` net, count `2`, and balance `60`; invalid evidence fails closed with no partial values or controls.
- Phase 1H.26P read-only player-facing exact canonical settled-loss receipt: **COMPLETE FOR THE SAME EXACT H26A–H26N LOSS CHAIN ONLY**; see [[Development/Reports/Phase 1H26P Read Only Player Facing Exact Canonical Settled Loss Receipt]]. The existing physical ticket-booth HUD and one in-memory authoritative loader show the exact selection, stake, `97–101` result, returned `0`, net `-40`, and balance `60` without using Admin projection data or writing state. Invalid evidence shows only the existing unavailable panel.
- Phase 1H.26Q interactive canonical Match Winner selection and pre-commit review: **COMPLETE FOR THE EXACT ACTIVE H26A/H26B/H26C OFFER ONLY**; see [[Development/Reports/Phase 1H26Q Interactive Canonical Match Winner Selection and Pre Commit Bet Slip Review]]. Mouse, keyboard, and controller select either offered team and adjust a `10`-`100` by `10` in-memory stake while the slip shows immutable odds and exact gross return. It is explicitly review only, resets on close/leave/restart, and has no confirmation, request, debit, lock, receipt, persistence, or ledger mutation path.
- Phase 1H.26R exact Harbor/40 canonical wager placement: **COMPLETE FOR ONE EXACT ACTIVE LOCAL-BETA REQUEST ONLY**; see [[Development/Reports/Phase 1H26R Exact Harbor 40 Canonical Wager Placement]]. Harbor City Waves at stake `40` alone can arm, then submit through a parameterless server RPC. First confirmation is mutation-free; second confirmation independently reloads H26A/H26B/H26C and reuses H26E atomically to persist one `accepted_pending_lock` request plus sequence-`2` `-40`, leaving balance `60`, before the H26F receipt appears. Other teams/stakes remain unavailable.
- Phase 1H.26S automatic exact canonical tipoff lock: **COMPLETE FOR THE EXACT PENDING HARBOR/40 REQUEST ONLY**; see [[Development/Reports/Phase 1H26S Automatic Exact Canonical Tipoff Lock]]. Durable placement or authoritative pre-tipoff restore schedules at most one server timer; exact H26A tipoff invokes the existing parameterless H26G transition and refreshes the locked booth only after persisted reload.
- Phase 1H.26T automatic canonical active-game execution commitment: **COMPLETE FOR THAT EXACT H26S-LOCKED REQUEST ONLY**; see [[Development/Reports/Phase 1H26T Automatic Canonical Active Game Execution Commitment]]. Only after exact durable H26G reload, GameMode invokes existing parameterless H26H; H26H derives its private seed/input from pre-wager H26A/H26B evidence, persists or accepts one exact immutable commitment, and exposes nothing new to the locked booth.
- Phase 1H.26U automatic private canonical game-execution handoff: **COMPLETE FOR THAT EXACT H26T COMMITMENT ONLY**; see [[Development/Reports/Phase 1H26U Automatic Private Canonical Game Execution Handoff]]. Only after exact durable H26H reload, GameMode invokes the existing parameterless H26I handoff writer; it writes or accepts one exact canonical file at the fixed private path while the booth remains locked.
- Phase 1H.26V private execution-consumer authority review: **COMPLETE AS DESIGN EVIDENCE ONLY**; see [[Design/Decisions/DEC-019 Private Local Execution Supervisor Boundary]] and [[Development/Reports/Phase 1H26V Private Execution Consumer Authority Review]]. One external opt-in local one-shot development supervisor is the frozen recommendation; client-spawned/bundled Python is rejected and a trusted backend worker is deferred. No supervisor or receipt exists.
- Phase 1H.26W external one-shot local H26I supervisor proof: **COMPLETE FOR ONE FIXED H26U HANDOFF ONLY**; see [[Development/Reports/Phase 1H26W External One Shot Local H26I Supervisor Proof]]. The separate manual no-argument supervisor pins the interpreter, frozen revision, module, and private directories; reserves one atomic attempt; runs one bounded existing H26I child; validates one receipt; and exits. The game and package still stop at H26U.
- Phase 1H.26X external one-shot local H26J digest-seal proof: **COMPLETE FOR ONE FIXED H26W RECEIPT ONLY**; see [[Development/Reports/Phase 1H26X External One Shot Local H26J Digest Seal Proof]]. The separate manual no-argument supervisor reuses and pins the H26W controls, reserves one separate atomic seal attempt, invokes the unchanged H26J verifier once, independently validates one exact `sealed_pending_result` record, and exits. Exact duplicate launches no child and rewrites nothing; the game and package still stop at H26U.
- Phase 1H.26Y external one-shot local H26K canonical-result proof: **COMPLETE FOR ONE FIXED H26W/H26X CHAIN ONLY**; see [[Development/Reports/Phase 1H26Y External One Shot Local H26K Canonical Result Proof]]. The separate manual no-argument supervisor reuses and pins the shared controls and approved record hash, reserves one result attempt, invokes the unchanged H26K recorder once, independently validates one exact `recorded_pending_decision` result, and exits. Exact duplicate launches no child or simulation and rewrites nothing; the game and package still stop at H26U.
- Phase 1H.26Z explicit isolated packaged H26L result-link proof: **COMPLETE FOR ONE FIXED H26W/H26X/H26Y CHAIN ONLY**; see [[Development/Reports/Phase 1H26Z Explicit Isolated Packaged H26L Result Link Proof]]. The unchanged package linked the exact external result once, preserved the request/lock and ledger `2/-40/60`, rejected missing/tampered/archive-format evidence before save, and preserved an exact cold duplicate without simulation, settlement, or repair.
- Phase 1H.26AA explicit isolated packaged H26M loss-decision proof: **COMPLETE FOR ONE FIXED H26W–H26Z CHAIN ONLY**; see [[Development/Reports/Phase 1H26AA Explicit Isolated Packaged H26M Loss Decision Proof]]. The unchanged package derived one exact Harbor-loss decision from the H26Y record, preserved ledger `2/-40/60`, rejected missing/conflicting/downstream evidence before mutation, and preserved an exact cold duplicate without application or finalization.
- Phase 1H.26AB explicit isolated packaged H26N loss-finalization proof: **COMPLETE FOR ONE FIXED H26W–H26AA CHAIN ONLY UNDER DECISION A**; see [[Development/Reports/Phase 1H26AB Explicit Isolated Packaged H26N Loss Finalization Proof]]. The unchanged package appended one exact zero-return loss finalization, preserved ledger `2/-40/60` and H26M pending state, rejected invalid evidence before mutation, and preserved an exact cold duplicate. The pre-existing transient QA projection is disclosed and retained only as outside-userdir audit evidence; accepted QA artifacts were cleaned exactly.
- Phase 1H.26AC exact current-chain H26O reconciliation compatibility and isolated proof: **COMPLETE FOR EXACTLY THE RETAINED `97-101` LOSS AND FIXED CURRENT H26AB `79-113` LOSS**; see [[Development/Reports/Phase 1H26AC Exact Current Chain H26O Reconciliation Compatibility and Isolated Proof]]. The existing v1 writer, endpoint, validator, and single Operations card now accept the second fixed offer/result/replay identity without changing archived win/loss/void behavior. The isolated package preserved the H26AB source SaveGame bytes, SHA-256, and mtime; invalid, partial, tampered, or mixed evidence fails closed.
- Phase 1H.26AD read-only player-facing exact current-chain settled-loss receipt: **COMPLETE FOR THE SAME TWO EXACT APPROVED LOSSES ONLY**; see [[Development/Reports/Phase 1H26AD Read Only Player Facing Exact Current Chain Settled Loss Receipt]]. The existing H26P loader and ticket-booth HUD now show either approved score after the full authoritative chain validates. The current H26AB receipt shows Harbor `40`, final `79-113`, Mesa winner, return `0`, net `-40`, and balance `60`; view, close, leave, reopen, and cold restore preserve the source exactly.
- Phase 1H.26AE automatic exact current-chain H26L result link on local resume: **COMPLETE FOR THE FIXED H26W/H26X/H26Y CHAIN ONLY**; see [[Development/Reports/Phase 1H26AE Automatic Exact Current Chain H26L Result Link on Local Resume]]. Normal non-QA local startup reuses the strict parameterless H26L transition, reloads one exact durable link before updating memory, treats missing evidence as a locked no-op, and rejects invalid/conflicting evidence without repair. It creates no H26M-H26P state.
- Phase 1H.26AF automatic exact current-chain H26M loss decision on local resume: **COMPLETE FOR THE FIXED H26W–H26Y/H26L LOSS CHAIN ONLY**; see [[Development/Reports/Phase 1H26AF Automatic Exact Current Chain H26M Loss Decision on Local Resume]]. Exact durable H26L resume invokes the existing strict parameterless H26M transition once, reloads one exact Harbor-selected/Mesa-winner loss decision, and preserves ledger `2/60`. Cold restart requires exact `Duplicate`; missing/tampered lanes remain locked without mutation. It creates no H26N-H26P state.
- Phase 1H.26AG automatic exact current-chain H26N loss finalization on local resume: **COMPLETE FOR THE SAME FIXED H26W–H26Y/H26L/H26M LOSS CHAIN ONLY**; see [[Development/Reports/Phase 1H26AG Automatic Exact Current Chain H26N Loss Finalization on Local Resume]]. Exact durable H26M resume invokes the existing strict parameterless H26N transition, reloads one exact zero-return `settled_lost` finalization, and preserves ledger `2/-40/60`. Cold restart requires exact H26N `Duplicate`; missing/tampered lanes remain locked without mutation. The existing H26N loader regenerates the existing reconciliation projections, whose exact semantic identity is revalidated; no projection stability or new H26O/H26P work is claimed. `Fresh.log` and `Cold.log` unavoidably observed the existing H26P read-only receipt marker READY after finalization; the receipt code/UI was unmodified, the marker was not deliberately exercised, and it is not H26AG evidence or a new H26P completion claim.
- Phase 1H.26AH.1 settled-receipt ticket-booth direction cue: **COMPLETE FOR THE EXACT VALIDATED H26P LOSS RECEIPT ON `SundaleGraybox` ONLY**; see [[Development/Reports/Phase 1H26AH1 Settled Receipt Ticket Booth Direction Cue]]. Outside the fixed booth radius and with the menu closed, one top-center cue reports the booth as ahead, left, right, or behind plus current meters. It yields to the existing proximity prompt and hides without a valid receipt, on other maps, in Studio/stadium, or while the booth screen is open. No navigation system, minimap, saved state, timer, receipt/economy/simulation mutation, or brain change was added.
- Phase 1H.26AH normal-player settled-loss receipt lifecycle proof: **COMPLETE FOR THE SAME EXACT H26P LOSS RECEIPT AND COMMITTED H26AH.1 PACKAGE ONLY**; see [[Development/Reports/Phase 1H26AH Normal Player Settled Loss Receipt Lifecycle Proof]]. Normal play followed the city cue, opened the exact receipt, closed it, left, returned, reopened it, cold restarted, and reopened the identical receipt again. Two game-native `1280x800` captures are readable and unclipped; the authoritative save remained byte/hash/mtime stable. No QA receipt or teleport flags, production change, H26O write by H26P, or broader lifecycle claim was used.
- Phase 1H.26AI exact current-offer Mesa/`40` win-decision compatibility and isolated proof: **COMPLETE FOR ONE FIXED DECISION ONLY**; see [[Development/Reports/Phase 1H26AI Exact Current Offer Mesa 40 Win Decision Compatibility and Isolated Proof]]. The server-owned decision engine accepts the exact current `c929f90b...` offer and `79-113` Mesa result, derives `won` and return due `94`, and remains `decided_pending_apply`. The isolated ledger stays `2/-40/60`; invalid evidence rejects without mutation and the retained Harbor-loss route remains exact.
- Phase 1H.26AJ exact current Mesa `94` return application and win finalization: **COMPLETE FOR THE SAME FIXED H26AI CHAIN ONLY**; see [[Development/Reports/Phase 1H26AJ Exact Current Mesa 94 Return Application and Win Finalization]]. The existing atomic finalizer appends one sequence-`3` `+94` `match_winner_payout`, reaches balance `154`, and records one `settled_won` finalization. Exact duplicate is byte-stable; altered or conflicting evidence mutates nothing. The retained `+100` win and Harbor-loss paths remain exact.
- Phase 1H.26AK read-only exact current win reconciliation history: **COMPLETE FOR THE SAME FIXED H26AJ CHAIN ONLY**; see [[Development/Reports/Phase 1H26AK Read Only Exact Current Win Reconciliation History]]. The existing independent Brain Admin validator and Operations card now accept and display Mesa, probability `42413307`, score `79-113`, return `94`, net `+54`, three entries, balance `154`, `settled_won`, replay, and exact linkage. Altered, mixed, or partial evidence exposes no partial values; no control was added.
- Phase 1H.26AL read-only exact current win ticket-booth receipt: **COMPLETE FOR THE SAME FIXED H26AJ CHAIN ONLY**; see [[Development/Reports/Phase 1H26AL Read Only Player Facing Exact Current Win Receipt]]. The existing authoritative receipt surface now shows Mesa selected, final `79-113`, returned `94`, net `+54`, and balance `154`. Pending, partial, mixed, or altered evidence exposes no receipt; existing approved loss receipts remain exact.
- Phase 1H.26AM exact Mesa/`40` canonical wager placement: **COMPLETE FOR THE ONE CURRENT MATCH WINNER OFFER ONLY**; see [[Development/Reports/Phase 1H26AM Exact Mesa 40 Canonical Wager Placement]]. The normal two-confirm booth flow now accepts either exact offered team at stake `40`. Mesa persists probability `42413307`, odds `2.3577`, gross return `94`, one `-40` debit, one pending request, and balance `60`; first confirmation and repeated input mutate nothing.
- Phase 1H.26AP read-only exact automatic Mesa win reconciliation history: **COMPLETE FOR THE FIXED H26AM-H26AO CHAIN ONLY**; see [[Development/Reports/Phase 1H26AP Read Only Exact Automatic Mesa Win Reconciliation History]]. The existing reconciliation-v1 validator, API, and single Operations card independently accept the exact H26AN/H26AJ automatic chain and show Mesa, probability `42413307`, odds `2.3577`, potential/return `94`, final `79-113`, net `+54`, ledger `2/-40/60` then `3/+94/154`, balance `154`, `settled_won`, replay, and exact linkage. Invalid evidence exposes no partial values and the view mutates nothing.
- Phase 1H.26AQ read-only exact automatic Mesa win receipt compatibility: **COMPLETE FOR THE SAME FIXED H26AM-H26AO CHAIN ONLY**; see [[Development/Reports/Phase 1H26AQ Read Only Player Facing Exact Automatic Mesa Win Receipt Compatibility]]. The existing authoritative ticket-booth receipt now shows `WIN`, Mesa selected and winner, stake `40`, final `79-113`, returned `94`, net `+54`, ledger count `3`, balance `154`, and one close instruction only when the entire automatic chain is exact. Invalid evidence exposes no receipt or partial fields, the authoritative source remains stable, and the retained isolated win and approved losses remain exact.
- Phase 1H.26AR.1 Development-only held-input receipt lifecycle driver: **COMPLETE FOR ONE FIXED H26AQ DEVELOPMENT PROOF MODE ONLY**; see [[Development/Reports/Phase 1H26AR1 Development Only Held Input Receipt Lifecycle Driver]]. One explicit Development flag sends native held `W` / `A` / `D` and `E` press/release input through the existing movement and booth paths. The accepted package walked from `17,986 cm` away into the `350 cm` radius, opened, closed, left to `652 cm`, returned, and reopened the exact receipt while the authoritative SaveGame stayed byte/hash/mtime exact. Test and Shipping omit the driver; there is no transform, direct receipt/economy action, persistence write, fallback, or generalized navigation.
- Phase 1H.26AR.2 automated normal-path and cold-process exact automatic Mesa win receipt lifecycle proof: **COMPLETE FOR THE SAME FIXED H26AQ DEVELOPMENT PROOF ONLY**; see [[Development/Reports/Phase 1H26AR2 Automated Normal Path and Cold Process Exact Automatic Mesa Win Receipt Lifecycle Proof]]. Process A used the committed native held-input driver to open, close, leave, return, and reopen the exact receipt, then fully terminated. Process B cold-launched afterward against the same unchanged user directory and repeated it. Both readable game-native captures show the identical receipt and one close instruction; the authoritative SaveGame stayed exact before, between, and after. No QA/teleport/direct action or production change was used.
- Phase 1I.2 exact Sundale Signal Jacket purchase: **COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE**; see [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]] and [[Development/Reports/Phase 1I2 Exact Sundale Signal Jacket Purchase]]. At the physical Sundale clothing-store waypoint, the player reviews and confirms the one fixed `60`-Odds-Bucks purchase with two E presses. One immutable ledger debit is the durable ownership record; exact retry and cold restart debit nothing. No generalized inventory service, free grant, auto-equip, chair path, refund, trading, real-money path, or brain behavior was added.
- Phase 1I.3 owned Signal Jacket equip and shared-city visibility: **COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE AND ONE OTHER LOCAL SUNDALE CLIENT**; see [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]] and [[Development/Reports/Phase 1I3 Owned Signal Jacket Equip and Shared City Visibility]]. One E press at the physical clothing-store waypoint explicitly equips the restored owned item in the single `outfit` slot. No second ledger entry or debit occurs, purchase and restart do not auto-equip, and another packaged local client receives and renders the slate-and-teal graybox appearance.
- Phase 1I.4 exact Sundale Modular Chair purchase and Studio display: **COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE AND OWNED STUDIO**; see [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]], [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]], and [[Development/Reports/Phase 1I4 Exact Sundale Modular Chair Purchase and Studio Display]]. At the physical furniture-store waypoint, two E presses buy the exact `100`-Odds-Bucks chair once. Its immutable debit is durable ownership evidence, and the owned Studio shows the three-part gray-and-teal placeholder at `studio_primary` after fresh entry and cold restart.
- Phase 1I.5 exact One-bedroom upgrade purchase and in-place interior: **COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE AND OWNED STUDIO**; see [[Design/Decisions/DEC-020 First One Bedroom Apartment Upgrade]] and [[Development/Reports/Phase 1I5 Exact One Bedroom Upgrade Purchase and In Place Interior]]. At the physical apartment-management kiosk, two E presses buy the exact `500`-Odds-Bucks first upgrade once. Studio ownership is required, the existing interior gains a partition and doorway, and the owned chair remains at `studio_primary` after fresh entry and cold restart.
- Phase 1J.1 public athlete story pages: **COMPLETE FOR THE EXISTING PUBLIC SEASON 1 ARCHIVE**; see [[Development/Reports/Phase 1J1 Public Athlete Story Pages]]. The existing `L` league viewer now has one read-only page for each of twelve fictional athletes. It presents durable talent, ratings, specialty, consistency, role, form, scoring, public workload, availability, and the latest recorded Life Brain choice while explicitly withholding hidden fatigue, recovery, injury-risk, RNG, resolver, and private-effect values.
- Phase 1J.2 safe public athlete explanations: **COMPLETE FOR THE EXISTING PUBLIC SEASON 1 ARCHIVE**; see [[Development/Reports/Phase 1J2 Safe Public Athlete Explanations]]. Every athlete page now explains the durable baseline, public opportunity, recent scoring difference, form label, recorded life context, and availability boundary. It labels evidence as non-diagnostic, refuses to claim a life choice caused performance, and publishes no unavailable-athlete cause when the archive has none.
- Phase 1J.3a Development-only athlete-story comprehension instrument: **COMPLETE FOR ONE FIXED SIX-ITEM PUBLIC-FIXTURE CHECK**; see [[Development/Reports/Phase 1J3a Development Only Athlete Story Comprehension Instrument]]. One explicit Development QA flag presents an answer-keyed check for durable ability versus one recent game, specialty versus overall quality, opportunity versus guaranteed production, recent form versus season baseline, life context versus proven cause, and public `OUT` status versus diagnosis. It uses no hidden values and is absent from Shipping. Software validation of the instrument is not evidence of human comprehension.
- Phase 1J.3b.0 player-blind Development comprehension session mode: **COMPLETE FOR ONE FIXED SIX-ITEM MECHANISM**; see [[Development/Reports/Phase 1J3b0 Player Blind Development Comprehension Session Mode]]. The exact six 1J.3a prompts appear one at a time, accept one A/B response each, withhold expected answers and correctness until all six are complete, then show only the submitted sequence and score. The mode uses only the approved public fixture, persists and transmits nothing, and is absent from Shipping. Mechanism validation is not observed human comprehension.
- Phase 1J.3b.1a equivalent unseen Development form prerequisite: **COMPLETE FOR ONE SIX-ITEM PUBLIC-FIXTURE VARIANT**; see [[Development/Reports/Phase 1J3b1a Equivalent Blind Form Prerequisite]]. The existing player-blind path now supports a second form with changed public athletes, examples, wording, and independently arranged A/B sides. Its six internal concept mappings are retained for later miss reporting; no evaluation data appears before completion, nothing persists or transmits, and Shipping excludes the variant.
- Phase 1J.3b.1b one-owner observed comprehension session: **COMPLETE — INITIAL GATE NOT PASSED**; see [[Development/Reports/Phase 1J3b1b One Owner Observed Comprehension Session]]. One verified unseen and uncoached owner session completed all six items and scored `2/6`. The four measured presentation gaps were durable ability, recent form, life context versus causation, and public availability versus diagnosis. This is one-human evidence only, not population comprehension. The consumed form is retired, nothing persisted or transmitted, and no brain change is authorized.
- Phase 1J.3b.1c four-concept athlete reading guide: **COMPLETE FOR ALL TWELVE EXISTING PUBLIC ATHLETE PAGES**; see [[Development/Reports/Phase 1J3b1c Four Concept Athlete Reading Guide]]. One compact text-only guide distinguishes durable ability from one result, recent form from permanent ability, recorded life context from proven causation, and public `OUT` availability from diagnosis. Existing specialty and opportunity presentation is unchanged; no brain, simulator, athlete evidence, or comprehension form changed.
- Phase 1J.3b.1d fresh post-clarification blind Form C prerequisite: **COMPLETE FOR ONE DEVELOPMENT-ONLY SIX-ITEM PUBLIC-FIXTURE VARIANT**; see [[Development/Reports/Phase 1J3b1d Fresh Post Clarification Blind Form C Prerequisite]]. It covers each approved concept once with fresh public examples, wording, and independently arranged A/B sides while reusing the existing blind-session path. It starts unanswered, leaks no pre-completion evaluation data, persists and transmits nothing, leaves retired Forms A/B byte-unchanged, and is absent from Shipping. Its prompts and key remain undisclosed.
- Phase 1J.3b.1e one-owner post-clarification comprehension session: **COMPLETE — 5/6 IN ONE FRESH UNSEEN AND UNCOACHED SAMPLE**; see [[Development/Reports/Phase 1J3b1e One Owner Post Clarification Comprehension Session]]. The four concepts missed initially were answered correctly; specialty versus overall quality was the only measured miss. This is one-human evidence, not population comprehension or proof of causation. Form C is consumed and retired.
- Phase 1J.3b.1f public specialty clarification: **COMPLETE FOR ALL TWELVE EXISTING PUBLIC ATHLETE PAGES**; see [[Development/Reports/Phase 1J3b1f Public Specialty Clarification]]. One compact line explains that specialty is the athlete's strongest skill category, not overall quality or a guaranteed result. No athlete evidence, brain, simulator, form, or production authority changed.
- Phase 1J exit review: **COMPLETE FOR THE CURRENT BOUNDED BETA MILESTONE**; see [[Design/Decisions/DEC-021 Phase 1J Bounded Athlete Story Evidence Acceptance]] and [[Development/Reports/Phase 1J Exit Review]]. The owner accepts the one-person unseen and uncoached `5/6` result plus the completed specialty clarification. Forms A-C are consumed and retired; no fourth form or retest is authorized for this milestone. Population comprehension remains unproven.
- Phase 1K.0 first-hour integration baseline and evidence contract: **COMPLETE — DEFINITION ONLY**; see [[Development/Phase 1K First-Hour Integration Evidence Contract]] and [[Development/Reports/Phase 1K0 First-Hour Integration Baseline and Evidence Contract]]. All eight route components have bounded individual proof, but no fresh contiguous packaged session proves coexistence.
- Next gate: **PHASE 1K.1 — EXECUTE THE CANONICAL PACKAGED INTEGRATION CONTRACT AS A MEASUREMENT RUN**. No runtime correction is authorized until the attempt records a named failure.
- Current prerequisite note: UE 5.8, the aligned x64 runtime and .NET Framework 4.8 SDK, portable project, reproducible local Windows package, empty-map launch, LFS, generated-file ignores, primitive block/court iteration, collision, cold-process reopen, direct recorded-replay rendering, deterministic packaged traces, and local resource sampling are verified. UE 5.8 is now the approved beta client engine.

No later roadmap phase is authorized merely because it appears below.

## Critical path

| Order | Phase | Player-facing outcome | Status |
| --- | --- | --- | --- |
| 1 | 1A — Engine and packaged-build proof | A real 3D client can build and run | COMPLETE |
| 2 | 1B — Character selection and movement | Choose a default avatar and enter the world | COMPLETE |
| 3 | 1C — First-city identity and graybox | Walk between every required beta location | COMPLETE |
| 4 | 1D — Shared-city presence | Players see one another and equipped clothing | COMPLETE |
| 5 | 1E — Studio and apartment progression | Enter a persistent home and see the six-tier goal | FOUNDATION + FIRST ONE-BEDROOM UPGRADE COMPLETE |
| 6 | 1F — League, stadium, and match viewing | Research and watch authoritative basketball | COMPLETE FOR CURRENT ARCHIVED GAME |
| 7 | 1G — Odds Bucks and work recovery | Earn, persist, audit, and recover virtual currency | COMPLETE FOR CURRENT LOCAL PROFILE |
| 8 | 1H — Wager locking and settlement | Reach the physical booth, inspect approved odds, place approved wagers, and receive exact outcomes | COMPLETE FOR THE FIXED HARBOR/MESA `40` MATCH WINNER SLICE / GENERALIZATION UNPROVEN |
| 9 | 1I — Stores and lifestyle upgrades | Buy, equip, display, and place basic items | COMPLETE FOR ONE JACKET + ONE CHAIR + ONE-BEDROOM LOCAL PATH |
| 10 | 1J — Athlete life and league storytelling | Understand athletes, availability, and consequences | COMPLETE FOR CURRENT BOUNDED MILESTONE — OWNER ACCEPTED ONE-PERSON 5/6 + SPECIALTY CLARIFICATION; NO POPULATION CLAIM |
| 11 | 1K — First-hour integration | Complete the entire beta promise in one session | ACTIVE — 1K.0 CONTRACT COMPLETE; NEXT GATE 1K.1 MEASUREMENT RUN |
| 12 | 1L — Content, presentation, and accessibility | The slice feels coherent and readable | PENDING |
| 13 | 1M — Reliability, compliance, and beta exit | The owner can truthfully approve beta release | BETA EXIT |

## Phase 1A — Engine and packaged-build proof

### Bible sections advanced

- Current implementation boundary.
- World and city scope.
- Match presentation authority boundary.

### Ordered gates

1. **1A.0 COMPLETE:** local hardware, compiler, Git/LFS, and replay-interface readiness audit.
2. **1A.1a COMPLETE:** install the owner-approved free engine candidate and verify one no-project editor launch and normal exit.
3. **1A.1b COMPLETE:** align the official Microsoft x64 runtime, reboot manually, and verify the no-project editor without the earlier prerequisite warning.
4. **1A.1c COMPLETE:** create and reopen the smallest empty local Windows project with one empty default map.
5. **1A.1d COMPLETE:** package and run that unchanged empty Windows project; record disk, build time, launch time, frame time, memory, and explained runtime networking.
6. **1A.2a COMPLETE:** add one noncanonical primitive street block and basketball court to a separate benchmark map; record one representative asset iteration and preserve the empty-package baseline.
7. **1A.2b COMPLETE:** directly render the existing verified 421-frame replay without resimulating basketball.
8. **1A.3 COMPLETE:** owner accepted the benchmark evidence and approved Unreal Engine 5.8 for beta client development on July 19, 2026; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].

### Exit evidence

- Reproducible local packaged build.
- Measured representative performance and asset iteration.
- Generated/cache directories remain untracked.
- Frozen 65-test simulation and Admin checks remain green.
- Owner records the engine decision.

## Phase 1B — Character selection and movement

### Bible sections advanced

- First-hour player journey: choose a default character.
- Avatar and clothing.

### Smallest delivery path

1. **1B.1 COMPLETE:** placeholder preset data for varied masculine/feminine presentations and skin tones; see [[Development/Reports/Phase 1B1 Character Preset Catalog]].
2. **1B.2 COMPLETE:** fast local selection screen with a safe default; see [[Development/Reports/Phase 1B2 Fast Local Character Selection Screen]].
3. **1B.3 COMPLETE:** one controllable primitive placeholder with the approved camera and input direction; see [[Development/Reports/Phase 1B3 Controllable Placeholder Avatar and Approved Locomotion]].
4. **1B.4 COMPLETE:** worn off-white starter top and bottom are separate replaceable primitive equipment; see [[Development/Reports/Phase 1B4 Replaceable Starter Outfit]].
5. **1B.5 COMPLETE:** the selected preset and equipped starter outfit save locally, enter the packaged placeholder world, and recover exactly after a cold process restart; see [[Development/Reports/Phase 1B5 Local Character Appearance Persistence and First-Playable Handoff]].

### Owner gates

- **RESOLVED:** third-person camera and beta movement direction; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults]].
- **RESOLVED FOR PLACEHOLDERS:** eight-preset minimum and neutral placeholder direction; final character art remains deferred to the later art-direction gate.

### Exit evidence

A fresh player can choose a preset, enter a packaged placeholder world, move, close, reopen, and recover the same appearance without demographic attributes affecting gameplay.

**PASSED:** the committed Phase 1B.1–1B.5 evidence satisfies every clause; see [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].

## Phase 1C — First-city identity and graybox

### Bible sections advanced

- Enter the first city.
- Required beta locations.
- Art, music, and storytelling.

### Owner gate — complete

The owner selected Concept B — Daymark / Sundale on July 20, 2026. The theme, mostly flat commons-ring geography, visual language, and atmosphere are approved under [[Design/Decisions/DEC-008 Beta First City Direction]]. Sundale remains a working name.

**Phase 1C.0 planning evidence:** three grounded modern-day alternatives are complete in [[Design/First City Concept Packages]] and [[Visual Maps/First City Concepts]]. Concept B is selected. Phase 1C.1 subsequently froze the minimal Sundale art-direction sheet and measurable compact walking loop in [[Design/Sundale Art Direction and Core Loop]].

### Smallest delivery path

1. **1C.1 COMPLETE:** freeze the minimal Sundale art-direction sheet and `800 m` projected compact walking loop; see [[Design/Sundale Art Direction and Core Loop]].
2. **1C.2 COMPLETE:** graybox the apartment entrance, one job, stadium/sportsbook, clothing store, furniture store, public court, commons, and connecting streets in a separate map.
3. **COMPLETE IN 1C.2:** add blocking-floor collision, map-owned spawn/game mode, primitive landmarks, named thresholds, and simple route wayfinding. This does not claim NPC navigation or final assets.
4. **COMPLETE IN 1C.2:** benchmark the full required route in a packaged build before final city art.

### Exit evidence

**PASSED:** one packaged placeholder avatar walked and ran the entire `800 m` core loop, visited all eleven checkpoints, returned home, and retained blocking-floor collision without final assets. See [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].

## Phase 1D — Shared-city presence

### Bible sections advanced

- Shared player presence.
- Avatar and clothing visibility.

### Smallest delivery path

1. **1D.1 COMPLETE:** two local playable clients join the packaged Sundale instance, receive replicated temporary identities, pass through one another, and produce server-observed movement evidence; see [[Development/Reports/Phase 1D1 Local Two-Client Shared City Presence]].
2. **1D.2 COMPLETE:** the server validates and replicates each selected preset plus equipped starter top/bottom; both packaged clients agree on both distinct players' visible state; see [[Development/Reports/Phase 1D2 Replicated Appearance and Starter Clothing]].
3. **1D.3 COMPLETE:** a cold local client process rejoins the same server from the existing validated appearance SaveGame and restores the exact server-visible preset/top/bottom tuple; see [[Development/Reports/Phase 1D3 Cold Reconnect Visible State Restore]].
4. **1D.4 COMPLETE:** one packaged build passed local `2`, `3`, and `4` total-client rungs; every process saw all submitted visible states and the server measured every remote mover; see [[Development/Reports/Phase 1D4 Local Concurrency Ladder]].

### Owner gates

- **RESOLVED FOR LOCAL PROOF:** two clients first, `$0.00`, and no region/hosting choice before evidence.
- **RESOLVED:** players pass through one another and use temporary visible `Player 1` / `Player 2` proof labels.
- **STILL OPEN:** reconnect and local ladder evidence now exist, but they do not justify inventing a beta instance ceiling.
- **REQUIRED BEFORE EXTERNAL BETA:** minimum blocking/reporting surface and explicit external hosting/service approval.

### Exit evidence

**PASSED FOR THE LOCAL PROTOTYPE:** the packaged ladder measured `2`, `3`, and `4` total clients. Every client saw all approved owner-submitted appearances and the server measured every remote client moving at least `300 cm`. This does not prove an external beta capacity ceiling.

## Phase 1E — Studio and apartment progression

### Bible sections advanced

- Discover the starter home.
- Housing and furniture.

### Smallest delivery path

1. **1E.1 COMPLETE:** enter, walk and orbit the camera inside, then leave one private, completely empty placeholder Studio; see [[Development/Reports/Phase 1E1 Private Empty Studio Enter and Exit]] and [[Development/Reports/Phase 1E1a Continuous Mouse Camera Orbit Correction]].
2. **1E.2 COMPLETE:** persist Studio ownership and the player's exact Sundale return location across a cold process restart; see [[Development/Reports/Phase 1E2 Studio Ownership and Return Persistence]].
3. **1E.3 COMPLETE:** represent the six locked tiers in validated data—Studio, 1BR, 2BR, 3BR, 4BR, and Penthouse—while only Studio is available; see [[Development/Reports/Phase 1E3 Six-Tier Housing Progression Catalog]].
4. **1E.4 COMPLETE:** show one player-visible text status for all six tiers without building five unavailable interiors or inventing prices; see [[Development/Reports/Phase 1E4 Player-Visible Locked Housing Goals]].
5. **COMPLETE FOR ONE PURCHASED ITEM:** Phase 1I.4 activates only `studio_primary` after the exact Modular Chair purchase and durable ownership record; no free demonstration furniture or unrestricted placement exists.
6. **COMPLETE FOR THE FIRST PURCHASED TIER:** Phase 1I.5 buys the `500`-Odds-Bucks One-bedroom once, upgrades the existing Studio in place with a partition and doorway, and preserves the owned chair at `studio_primary` after cold restart.

### Owner gates

- **RESOLVED:** the starting Studio contains no free furniture or decoration; see [[Design/Decisions/DEC-011 Empty Starter Studio]].
- **RESOLVED FOR BETA:** interiors are private and other-player apartment visits are excluded; see [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]].
- **RESOLVED FOR FIRST PLACEMENT:** use `studio_primary` after the exact chair purchase; any additional point count or location remains later content work.
- **RESOLVED FOR ONE-BEDROOM ONLY:** use an in-place Studio upgrade; see [[Design/Decisions/DEC-020 First One Bedroom Apartment Upgrade]]. Every later tier's price, prerequisite, and layout remains open.

### Exit evidence

The player can return to the same owned Studio; all six tiers exist as truthful progression data while unbuilt interiors are clearly unavailable. A fresh Studio starts empty, and the first furniture appears only after a legitimate Phase 1I purchase, never as a free Phase 1E prop.

**FOUNDATION PASSED THROUGH CURRENT DEPENDENCIES:** ownership, return persistence, the initially empty Studio, all six tier records, visible locked/unbuilt statuses, one purchase-backed fixed furniture display, and one purchase-backed in-place One-bedroom graybox are proven. Later apartment layouts, prices, requirements, and additional placement points remain unimplemented owner gates.

## Phase 1F — League, stadium, and match viewing

### Bible sections advanced

- Basketball and wagering: league.
- Match presentation.
- Find the sports location.

### Smallest delivery path

1. **COMPLETE:** show the existing public teams, athletes, schedule, standings, availability, and history in the player client. See [[Development/Reports/Phase 1F1 Player League View]].
2. **COMPLETE:** graybox the stadium and public viewing location, with the future presentation area reserved and wagering kept inactive. See [[Development/Reports/Phase 1F2 Stadium and Public Viewing Graybox]].
3. **COMPLETE:** consume one verified archived replay directly inside the stadium without resimulation. See [[Development/Reports/Phase 1F3 Direct Archived Replay Consumption in Stadium]].
4. **COMPLETE:** owner-approved symbolic 3D placeholders, one fixed broadcast camera, text callouts without voice commentary, and a rendered three-minute presentation show score, clock, actors, key events, regulation/overtime status, and final seal. See [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F4 Readable Three Minute Stadium Presentation]].
5. **COMPLETE:** full watch, direct skip, mid-watch player skip, late arrival, and seal-validated cold reconnect all terminate at the identical frame `421`, score `101-104`, and authoritative seal without resimulation. Forged reconnect evidence renders zero frames. See [[Development/Reports/Phase 1F5 Replay View Result Invariance]].

### Owner gates

- **RESOLVED THROUGH PHASE 1F.5:** placeholder fidelity, one fixed camera, text-only callouts, three-minute full-watch duration, and result-invariant `S` skip; see [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]]. Final art, crowd, replay cuts, condensed mode, and special-game duration remain later decisions.
- How an 82-game season remains varied with the initial two-team scope.

### Exit evidence

The player can research a scheduled game, go to the venue, watch or skip the same authoritative result, and inspect the immutable history. The client never resimulates basketball.

**EXIT PASSED FOR THE CURRENT ARCHIVED-GAME SLICE:** the packaged player path can watch or press `S` to skip to the same sealed result; QA evidence proves late-arrival and seal-validated cold-reconnect reconstruction. Production backend/session reconnect and 82-game variety remain unbuilt or open.

## Phase 1G — Odds Bucks and work recovery

### Bible sections advanced

- Odds Bucks economy.
- Find work.
- Experience the consequence.

### Smallest delivery path

1. **COMPLETE:** add the server-authoritative virtual Odds Bucks ledger with append-only entries and idempotent commands. See [[Development/Reports/Phase 1G1 Empty Server Authoritative Odds Bucks Ledger]].
2. **COMPLETE:** create one server-validated placeholder action at Sundale's existing `Job` marker. See [[Development/Reports/Phase 1G2 Server Validated Placeholder Job Interaction]].
3. **COMPLETE FOR ONE LOCAL SAVED PROFILE:** credit one verified `100` Odds Bucks first-job payout, reject exact retries, and restore the one-entry ledger across a cold packaged-process restart. No online account or backend reconnect is claimed. See [[Development/Reports/Phase 1G3 Persistent First Job Payout]].
4. **COMPLETE FOR ONE LOCAL SAVED PROFILE:** start at `0`, credit `100` per successful shift on a rolling `24`-hour cooldown, count the first payout as period one, accumulate balances, and provide no separate allowance or missed-period catch-up. The next eligible timestamp and ledger survive a cold packaged-process restart. No online account, trusted backend clock, or backend reconnect is claimed. See [[Development/Reports/Phase 1G4 Rolling 24 Hour Job Recovery]].
5. **COMPLETE FOR ONE LOCAL SAVED PROFILE:** publish a validated output-only projection from Unreal and independently validate and display its balance, entries, and next-job eligibility in Brain Admin without mutation controls. See [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]].

### Owner gates

- **RESOLVED FOR LOCAL BETA RECOVERY:** placeholder interaction; starting balance `0`; `100` per successful shift; rolling `24`-hour eligibility; first payout as period one; accumulated balances; no separate allowance; no missed-period catch-up.
- Final job fiction, production account/time authority, recovery floor behavior after wagering, prices, and broader limits remain open.

### Exit evidence

**EXIT PASSED FOR THE CURRENT LOCAL-PROFILE DEPENDENCY:** the player can earn, retain, cold-restore, and locally audit virtual Odds Bucks through one non-paid path. No online account, trusted backend clock, production authorization, wager, real-money purchase, trade, or second currency is added in this phase.

## Phase 1H — Wager locking and settlement

### Bible sections advanced

- Place and watch the first wager.
- Beta wager markets.
- Wager integrity.

### Market order

1. Match winner.
2. Winning margin or spread-style outcome.
3. Overtime occurrence.
4. Player-points threshold.
5. Player-rebounds threshold.
6. Player-fouls threshold after authoritative foul statistics exist.

Each market is its own evidence gate. A later market does not begin until the previous active market proves exact lock, settlement, rollback, replay/history linkage, and Admin reconciliation.

### Architecture gate

- **1H.0 COMPLETE — DESIGN ONLY:** isolate the Basketball Brain, Basketball Rules and Outcome Engine, Basketball Odds Brain, Wager and Settlement Engine, and read-only Admin reconciliation. Evidence flows one way; wagers and balances cannot influence basketball. See [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]].
- **1H.1 COMPLETE — OWNER DECISION:** freeze the public prediction source, zero-house-edge integer payout formula, `10`–`100` stake range in increments of `10`, game-start lock, void/refund, correction, and equal-public-information rules. See [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]].
- **1H.2 COMPLETE — OFFER CONTRACT ONLY:** deterministically bind the approved rule/model versions, public prediction commitment, game, lock, probabilities, display odds, and stake rules into a SHA-256-identified offer. See [[Development/Reports/Phase 1H2 Versioned Match Winner Odds Offer]].
- **1H.3 COMPLETE — LOCAL REQUEST + STAKE DEBIT ONLY:** verify one exact pre-lock offer and persist one idempotent `accepted_pending_lock` request with one linked Odds Bucks debit. See [[Development/Reports/Phase 1H3 Idempotent Match Winner Stake Debit]].
- **1H.4 COMPLETE — LOCAL GAME-START LOCK ONLY:** persist one separate immutable lock decision linked to the exact accepted request without touching its evidence or the Odds Bucks ledger. See [[Development/Reports/Phase 1H4 Idempotent Match Winner Game Start Lock]].
- **1H.5 COMPLETE — EXACT SEALED RESULT LINK ONLY:** persist one separate immutable link from the accepted request and lock to the exact Season 1, Game 1 teams, `101`-`104` score, score-derived winner, and replay seal without touching the ledger. See [[Development/Reports/Phase 1H5 Immutable Sealed Match Winner Result Linkage]].
- **1H.6 COMPLETE — EXACT LOSS DECISION ONLY:** consume the exact request, lock, and result-link IDs and derive Harbor selected versus Mesa winner as `lost`, gross return due `0`, status `decided_pending_apply`, without changing the ledger. See [[Development/Reports/Phase 1H6 Immutable Deterministic Match Winner Settlement Decision]].
- **1H.7 COMPLETE — EXACT LOSS FINALIZATION ONLY:** derive one separate immutable finalization from the exact Phase 1H.6 decision and store `settled_lost`, gross return applied `0`, observed ledger entry count `2`, and observed balance `60`. The prior decision remains `decided_pending_apply`; no ledger entry, balance change, or cooldown change occurs. See [[Development/Reports/Phase 1H7 Idempotent Exact Loss Finalization]].
- **1H.8 COMPLETE — READ-ONLY EXACT-LOSS RECONCILIATION/HISTORY ONLY:** atomically publish one server-authored exact chain and independently validate it in Brain Admin before showing the immutable loss summary, replay seal, and command linkage. Missing or invalid projections reveal no partial evidence; no controls or money mutation exist. See [[Development/Reports/Phase 1H8 Read Only Exact Loss Reconciliation History]].
- **1H.9 COMPLETE — EXACT WIN RETURN-DUE DECISION ONLY:** in one isolated QA profile, recompute the exact Mesa selection probability and approved formula, derive `won` and gross return due `100`, and persist `decided_pending_apply` without payout, finalization, ledger mutation, or Admin/player display. See [[Development/Reports/Phase 1H9 Immutable Exact Win Settlement Decision and Return Due Binding]].
- **1H.10 COMPLETE — EXACT WIN APPLICATION/FINALIZATION ONLY:** use the exact Phase 1H.9 decision to atomically append one `+100` payout entry and one separate immutable `settled_won` finalization. The ledger moves from `2/60` to `3/160`; exact retry is idempotent and all mismatched or mutated evidence fails closed. No win reconciliation or UI is added. See [[Development/Reports/Phase 1H10 Idempotent Exact Win Return Application and Finalization]].
- **1H.11 COMPLETE — READ-ONLY EXACT-WIN RECONCILIATION/HISTORY:** reuse the existing v1 atomic projection, endpoint, independent validator, and Operations card for the exact H10 win. It shows the verified probability/formula, sealed result, stake/payout ledger entries, `settled_won`, count `3`, balance `160`, and net `+60`; invalid/partial evidence shows nothing and provides no controls. Automated and live browser/DOM validation passed. See [[Development/Reports/Phase 1H11 Read Only Exact Win Reconciliation History]].
- **1H.12 COMPLETE — NONCANONICAL CANCELED-GAME EVIDENCE ONLY:** persist one separate immutable Season 99, Game 1 QA disposition linked to its exact accepted request and lock, server cancellation command/evidence IDs, authoritative time, `game_canceled`, and `closed_canceled`. The exact retry is idempotent; invalid, conflicting, already-resolved, malformed, or second dispositions fail closed. No ledger restoration, settlement, finalization, reconciliation, UI, or sealed Season 1, Game 1 relabeling occurs. See [[Development/Reports/Phase 1H12 Immutable Authoritative Canceled Game Evidence Link]].
- **1H.13 COMPLETE — EXACT VOID/REFUND-DUE DECISION ONLY:** use one command plus exact H12 cancellation identity to derive the request, lock, offer, selected team, stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund`. Exact retry is idempotent; invalid, conflicting, normal-result/settlement, malformed, nonclosed, or second decisions fail closed. No refund credit, application, finalization, reconciliation, UI, or sealed Season 1, Game 1 change occurs. See [[Development/Reports/Phase 1H13 Immutable Exact Canceled Wager Void Refund Due Decision]].
- **1H.14 COMPLETE — EXACT CANCELED-WAGER REFUND APPLICATION/FINALIZATION ONLY:** use one command plus the exact H13 decision to atomically append sequence `3`, `+40`, `match_winner_refund`, balance `100`, and one separate immutable `settled_void` record binding the full H12-to-H13 chain. Exact retry is idempotent; conflicts, a second finalization, tamper, malformed persistence, normal overlap, and ledger anomalies fail closed. No reconciliation, Admin/player UI, generalized refund service, correction, prop market, backend, brain change, or canonical Game 1 change occurs. See [[Development/Reports/Phase 1H14 Idempotent Exact Canceled Wager Refund Application and Finalization]].
- **1H.15 COMPLETE — READ-ONLY EXACT CANCELED-WAGER RECONCILIATION/HISTORY:** reuse the existing v1 atomic projection, endpoint, independent validator, and Operations card for the exact H12-to-H14 chain. It shows cancellation evidence, stake `2/-40/60`, H13 pending decision, refund `3/+40/100`, `settled_void`, count `3`, balance `100`, net `0`, and full command linkage; missing, stale, invalid, partial, mixed, or invented result evidence reveals nothing and provides no controls. Automated and live browser/API validation passed. See [[Development/Reports/Phase 1H15 Read Only Exact Canceled Wager Reconciliation History]].
- **1H.16 COMPLETE — PLAYER-FACING EXACT OFFER PREVIEW ONLY:** at the separate Sundale Sportsbook frontage, `E` opens the exact canonical Season 1, Game 1 offer with teams, probabilities, odds, stake bounds, game-start lock, gross-return examples, offer ID, source versions, and commitment. It remains read-only. See [[Development/Reports/Phase 1H16 Player Facing Match Winner Offer Preview]].
- **1H.17 COMPLETE — ONE UPCOMING NONCANONICAL QA REQUEST ONLY:** at the same frontage under explicit machine-local QA mode, the player can choose either team and a `10`–`100`/`10` stake, review exact gross return, and explicitly confirm. Server authority writes one `accepted_pending_lock` request plus one linked debit atomically. Exact cold retry is duplicate-safe; all scoped rejection cases mutate nothing. See [[Development/Reports/Phase 1H17 Player Facing Upcoming QA Match Winner Request]].
- **1H.18 COMPLETE — COLD-RESTORED PENDING RECEIPT ONLY:** in a separate process, `E` at the frontage shows the exact H17 request ID, offer and version, team, stake, accepted/lock times, pending status, linked `2/-40` stake entry, and balance `60`. It closes on leave. Independent validation fails closed, and the receipt process performs no request, debit, lock, result, migration, reconciliation write, or state mutation. See [[Development/Reports/Phase 1H18 Cold Restored Pending Match Winner Receipt]].
- **1H.19 COMPLETE — EXACT UPCOMING QA GAME-START LOCK ONLY:** at fixed server-owned time `2100086400`, one fixed command creates exactly one immutable lock for the H17 request. H17 request, stake debit, ledger count `2`, balance `60`, and job cooldown remain unchanged. Exact cold retry is duplicate-safe; wrong, conflicting, second, malformed, completed-H16, or invented-time attempts mutate nothing. See [[Development/Reports/Phase 1H19 Exact Upcoming QA Game Start Lock]].
- **1H.20 COMPLETE — IMMUTABLE AUTHORITATIVE UPCOMING QA CANCELLATION ONLY:** at fixed post-lock server time `2100086700`, one fixed command/evidence pair records exactly one `game_canceled` / `closed_canceled` disposition for the H17/H19 chain. The ledger remains `2/60`, cooldown remains exact, and no normal result, settlement, refund decision, credit, or finalization exists. Exact cold retry and the full rejection matrix are byte-stable. See [[Development/Reports/Phase 1H20 Immutable Authoritative Upcoming QA Cancellation Evidence]].
- **1H.21 COMPLETE — EXACT UPCOMING QA VOID/REFUND-DUE DECISION ONLY:** one fixed parameterless transition binds the exact H17/H19/H20 chain and derives Sparks, stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund`. The ledger remains `2/60`, cooldown remains exact, and no refund credit or finalization exists. Exact cold retry and the full rejection/tamper matrix are byte-stable. See [[Development/Reports/Phase 1H21 Immutable Exact Upcoming QA Void Refund Due Decision]].
- **1H.22 COMPLETE — EXACT UPCOMING QA REFUND APPLICATION/FINALIZATION ONLY:** one fixed parameterless transition atomically appends sequence `3`, `+40` `match_winner_refund`, balance `100`, plus one separate immutable `settled_void` finalization for the exact H17/H19/H20/H21 chain. H21 stays `decided_void_pending_refund`. Exact cold retry and the full rejection/tamper matrix are byte-stable. See [[Development/Reports/Phase 1H22 Idempotent Exact Upcoming QA Refund Application and Finalization]].
- **1H.23 COMPLETE — PLAYER-FACING TICKET-BOOTH PRESENTATION CLEANUP ONLY:** at the existing sportsbook route point, proximity shows exactly `Press E to open betting odds`; `E` opens a concise read-only basketball-odds panel with one close instruction. Technical IDs, commitments, Unix time, QA wording, return tables, and the persistent league shortcut hint are absent from normal play. See [[Development/Reports/Phase 1H23 Player Facing Ticket Booth Odds Presentation Cleanup]].
- **1H.24 COMPLETE — GRAPHICAL READ-ONLY BASKETBALL MARKET BROWSER ONLY:** the ticket booth now opens an original native Unreal HUD with four market tabs, two real Match Winner selection cards, a persistent read-only slip, explicit stake/decimal-return/lock/currency disclosures, clickable tabs, keyboard/controller navigation, and modal movement/look handling. Margin, Overtime, Points, Rebounds, and Personal Fouls are discoverable but explicitly locked with no invented odds. See [[Design/Basketball Betting Interface Research]] and [[Development/Reports/Phase 1H24 Graphical Ticket Booth Basketball Market Browser]].
- **1H.25 COMPLETE — READ-ONLY EXACT UPCOMING QA RECONCILIATION/HISTORY ONLY:** the exact H17 request, H19 lock, H20 cancellation/evidence, H21 refund-due decision, H22 refund/finalization, and sequence-`2`/`3` ledger evidence reuse the existing reconciliation-v1 file, API, independent validator, and single Operations card. Missing, stale, partial, mixed, or tampered evidence reveals no partial values; the card exposes no controls. See [[Development/Reports/Phase 1H25 Read Only Exact Upcoming QA Wager Reconciliation History]].
- **1H.26O COMPLETE — READ-ONLY EXACT CANONICAL LOSS RECONCILIATION/HISTORY ONLY:** the retained H26A–H26N Harbor-selected/Mesa-winner chain reuses the existing reconciliation-v1 file, API, independent validator, and single Operations card. Exact odds/potential, result, return `0`, net `-40`, ledger count `2`, and balance `60` appear only after the entire fixed chain validates. See [[Development/Reports/Phase 1H26O Read Only Exact Canonical Match Winner Loss Reconciliation History]].
- **1H.26P COMPLETE — PLAYER-FACING EXACT SETTLED-LOSS RECEIPT ONLY:** at the physical ticket booth, the exact H26A–H26N chain produces one read-only `BET SETTLED — LOSS` receipt with Harbor, stake `40`, final `97–101`, Mesa winner, returned `0`, net `-40`, balance `60`, and one close instruction. Partial or foreign evidence shows only the existing unavailable panel. See [[Development/Reports/Phase 1H26P Read Only Player Facing Exact Canonical Settled Loss Receipt]].
- **1H.26Q COMPLETE - INTERACTIVE PRE-COMMIT REVIEW ONLY:** at the physical ticket booth, mouse, keyboard, and controller can select Harbor or Mesa and adjust a `10`-`100` by `10` in-memory stake. The persistent slip shows immutable H26C decimal odds, exact integer-formula gross return, balance, lock rule, and `REVIEW ONLY - WAGER NOT PLACED`. Close, leave, cold restart, and tipoff clear the review; pending/settled states retain precedence. No submit or mutation path exists. See [[Development/Reports/Phase 1H26Q Interactive Canonical Match Winner Selection and Pre Commit Bet Slip Review]].
- **1H.26R COMPLETE - EXACT HARBOR/40 NORMAL PLACEMENT ONLY:** the physical ticket booth now uses two confirmations for Harbor City Waves at exactly `40`. The first only arms; the second calls a parameterless server route that derives all H26A/H26B/H26C authority and atomically creates the existing H26E request/debit before the H26F pending receipt appears. Mesa, every other stake, and invalid evidence remain unavailable. See [[Development/Reports/Phase 1H26R Exact Harbor 40 Canonical Wager Placement]].
- **1H.26S COMPLETE - AUTOMATIC EXACT-TIPOFF LOCK FOR THAT REQUEST ONLY:** exact H26R success or valid pre-tipoff restore schedules one non-looping server timer. Only exact H26A tipoff calls the existing parameterless H26G lock; durable reload then clears the pending booth into its locked panel. There is no late catch-up or automatic H26H-H26P chain. See [[Development/Reports/Phase 1H26S Automatic Exact Canonical Tipoff Lock]].
- **1H.26T COMPLETE - AUTOMATIC H26H COMMITMENT FOR THAT EXACT LOCK ONLY:** only after H26S durably reloads H26G, GameMode calls the existing parameterless H26H creator. H26H derives its private seed/frozen input internally from H26A/H26B, accepts only `Created` or exact immutable `Duplicate`, and leaves the booth locked. H26I-H26P do not run. See [[Development/Reports/Phase 1H26T Automatic Canonical Active Game Execution Commitment]].
- **1H.26U COMPLETE - AUTOMATIC PRIVATE H26I HANDOFF FOR THAT EXACT COMMITMENT ONLY:** only after H26T durably reloads H26H, GameMode calls the existing parameterless writer. It emits or accepts one exact canonical JSON file at the fixed private path; conflicts are rejected without repair and the booth remains locked. No consumer, process, receipt, simulation, or H26J-H26P transition runs. See [[Development/Reports/Phase 1H26U Automatic Private Canonical Game Execution Handoff]].
- **1H.26V COMPLETE - PRIVATE EXECUTION-CONSUMER AUTHORITY REVIEW ONLY:** DEC-019 recommends one external opt-in local one-shot trusted development supervisor, rejects bundled/client-spawned Python, and defers a trusted backend worker. It freezes fixed directories, an allowlisted interpreter, existing `phase1h.execution`, one atomic attempt, a `120`-second timeout, bounded private logging, and fail-closed no-repair semantics. No runtime or receipt exists. See [[Design/Decisions/DEC-019 Private Local Execution Supervisor Boundary]] and [[Development/Reports/Phase 1H26V Private Execution Consumer Authority Review]].
- **1H.26W COMPLETE - EXTERNAL ONE-SHOT LOCAL H26I SUPERVISOR PROOF ONLY:** the separate manual no-argument command verifies the allowlisted interpreter and frozen revision, consumes one fixed exact H26U handoff, atomically reserves one attempt, invokes the unchanged H26I consumer once under a `120`-second Windows Job boundary, validates one exact receipt, writes bounded private metadata, and exits. Exact duplicate launches no child and rewrites nothing. The game/package still launches no Python. See [[Development/Reports/Phase 1H26W External One Shot Local H26I Supervisor Proof]].
- **1H.26X COMPLETE - EXTERNAL ONE-SHOT LOCAL H26J DIGEST-SEAL PROOF ONLY:** the separate manual no-argument command reuses and pins the H26W controls, validates one fixed exact H26W handoff/receipt, atomically reserves one seal attempt, invokes the unchanged H26J verifier once under the same bounded child controls, validates one exact `sealed_pending_result` record, writes bounded private metadata, and exits. Exact duplicate launches no child and rewrites nothing. See [[Development/Reports/Phase 1H26X External One Shot Local H26J Digest Seal Proof]].
- **1H.26Y COMPLETE - EXTERNAL ONE-SHOT LOCAL H26K CANONICAL-RESULT PROOF ONLY:** the separate manual no-argument command reuses and pins the shared controls plus one approved canonical result hash, validates the exact H26W/H26X chain, atomically reserves one result attempt, invokes the unchanged H26K recorder once, independently validates one exact `recorded_pending_decision` result, writes bounded result-free metadata, and exits. Exact duplicate launches no child or simulation and rewrites nothing. See [[Development/Reports/Phase 1H26Y External One Shot Local H26K Canonical Result Proof]].
- **1H.26Z COMPLETE - EXPLICIT ISOLATED PACKAGED H26L RESULT-LINK PROOF ONLY:** the unchanged package consumed the exact H26W request/lock plus byte-identical H26X seal and H26Y result in a disposable QA directory. It appended one immutable link, preserved ledger `2/-40/60`, rejected missing/tampered/archive-format evidence before save, and accepted an exact cold duplicate without simulation, settlement, or repair. See [[Development/Reports/Phase 1H26Z Explicit Isolated Packaged H26L Result Link Proof]].
- **1H.26AA COMPLETE - EXPLICIT ISOLATED PACKAGED H26M LOSS-DECISION PROOF ONLY:** the unchanged package consumed the exact H26Z linked state in a disposable QA directory, derived one immutable Harbor-loss decision from the H26Y record, preserved ledger `2/-40/60`, rejected missing/conflicting/downstream evidence before mutation, and accepted an exact cold duplicate without application, finalization, history, or UI. See [[Development/Reports/Phase 1H26AA Explicit Isolated Packaged H26M Loss Decision Proof]].
- **1H.26AB COMPLETE - EXPLICIT ISOLATED PACKAGED H26N LOSS-FINALIZATION PROOF ONLY:** under Decision A, the unchanged package consumed the exact H26AA decision, appended one zero-return `settled_lost` finalization, preserved ledger `2/-40/60` and H26M pending state, rejected invalid evidence before mutation, and accepted an exact cold duplicate. The pre-existing transient QA projection is disclosed, preserved only outside the accepted user directory for audit, and cleaned with the disposable ledger; no H26O/H26P consumer or UI/Admin feature ran. See [[Development/Reports/Phase 1H26AB Explicit Isolated Packaged H26N Loss Finalization Proof]].
- **1H.26AC COMPLETE - EXACT CURRENT-CHAIN H26O RECONCILIATION COMPATIBILITY AND ISOLATED PROOF ONLY:** the existing v1 writer, endpoint, independent validator, and single Operations card accept exactly the retained `97-101` canonical loss and fixed current H26AB `79-113` canonical loss. The isolated package preserved the H26AB source SaveGame bytes, SHA-256, and mtime; partial, tampered, mixed, or missing evidence fails closed. See [[Development/Reports/Phase 1H26AC Exact Current Chain H26O Reconciliation Compatibility and Isolated Proof]].
- **1H.26AD COMPLETE - READ-ONLY PLAYER-FACING EXACT CURRENT-CHAIN SETTLED-LOSS RECEIPT ONLY:** the existing H26P loader and ticket-booth HUD accept exactly the same retained and current loss predicates. The current chain shows Harbor selected, stake `40`, final `79-113`, Mesa winner, returned `0`, net `-40`, balance `60`, and one close instruction; invalid evidence exposes no partial values. See [[Development/Reports/Phase 1H26AD Read Only Player Facing Exact Current Chain Settled Loss Receipt]].
- **1H.26AE COMPLETE - AUTOMATIC EXACT CURRENT-CHAIN H26L RESULT LINK ON LOCAL RESUME ONLY:** normal non-QA local startup sees fixed private result evidence, calls the existing strict H26L transition, reloads one exact durable link, and then exposes only the locked/unavailable booth. Exact cold duplicate is byte-stable; missing or invalid evidence never creates a link, decision, finalization, history, or receipt. See [[Development/Reports/Phase 1H26AE Automatic Exact Current Chain H26L Result Link on Local Resume]].
- **1H.26AF COMPLETE - AUTOMATIC EXACT CURRENT-CHAIN H26M LOSS DECISION ON LOCAL RESUME ONLY:** after exact durable H26L resume, normal non-QA startup invokes the existing strict H26M transition once and reloads the one exact Harbor-selected, Mesa-winner, stake-`40`, zero-return pending loss decision. Cold restart requires exact `Duplicate`; missing or invalid evidence remains locked and unchanged. No H26N finalization, H26O history, or H26P receipt runs. See [[Development/Reports/Phase 1H26AF Automatic Exact Current Chain H26M Loss Decision on Local Resume]].
- **1H.26AG COMPLETE - AUTOMATIC EXACT CURRENT-CHAIN H26N LOSS FINALIZATION ON LOCAL RESUME ONLY:** after exact durable H26M resume, normal non-QA startup invokes the existing strict H26N transition and reloads one exact `settled_lost`, zero-return finalization with ledger `2/-40/60`. Cold restart requires exact H26N `Duplicate`; missing or invalid evidence remains locked and unchanged. The existing H26N reload regenerates existing H26O reconciliation projections, which are checked semantically without a byte/mtime claim. Both package logs then unavoidably observed the existing H26P read-only receipt marker READY; the marker was not deliberately exercised, receipt code/UI was unmodified, and the observation is not H26AG evidence or completion. No new H26O/H26P implementation or presentation was added. See [[Development/Reports/Phase 1H26AG Automatic Exact Current Chain H26N Loss Finalization on Local Resume]].
- **1H.26AH.1 COMPLETE - SETTLED-RECEIPT TICKET-BOOTH DIRECTION CUE ONLY:** the exact validated H26P receipt now produces one top-center relative direction and meter distance to the fixed Sundale booth while the player is outside its interaction radius. The cue hands off to the existing `Press E` prompt and hides on every invalid, wrong-map, interior, or open-menu condition. See [[Development/Reports/Phase 1H26AH1 Settled Receipt Ticket Booth Direction Cue]].
- **1H.26AH COMPLETE - NORMAL PLAYER SETTLED-LOSS RECEIPT LIFECYCLE PROOF:** in the exact committed H26AH.1 package, normal play follows the city cue and opens the authoritative Harbor/`40`/`79-113`/Mesa/returned-`0`/net-`40`/balance-`60` receipt, then closes, leaves, returns, reopens, cold restarts, and reopens the identical receipt. The exact save remains stable and rejected evidence leaks no partial receipt. This closes proof only; production code is unchanged. See [[Development/Reports/Phase 1H26AH Normal Player Settled Loss Receipt Lifecycle Proof]].
- **1H.26AI COMPLETE - EXACT CURRENT-OFFER MESA/40 WIN DECISION ONLY:** the existing server-owned decision engine now accepts the fixed current offer/result identity, derives Mesa `won`, return due `94`, and `decided_pending_apply`, and preserves ledger `2/-40/60`. Missing, tampered, mixed, foreign, and conflicting evidence fails closed; no payout or finalization occurs. See [[Development/Reports/Phase 1H26AI Exact Current Offer Mesa 40 Win Decision Compatibility and Isolated Proof]].
- **1H.26AJ COMPLETE - EXACT CURRENT MESA +94 RETURN AND SETTLED-WON FINALIZATION:** the existing atomic finalizer applies one sequence-`3` `+94` payout to the fixed H26AI chain, reaches balance `154`, and records one immutable `settled_won` finalization. Cold duplicate and conflict lanes are byte-stable; the retained `+100` win and Harbor loss remain exact. See [[Development/Reports/Phase 1H26AJ Exact Current Mesa 94 Return Application and Win Finalization]].
- **1H.26AK COMPLETE - READ-ONLY EXACT CURRENT WIN RECONCILIATION:** the existing Brain Admin validator and Operations card independently accept the fixed H26AJ projection and show Mesa, `79-113`, return `94`, net `+54`, balance `154`, `settled_won`, replay, and exact linkage. No endpoint, card, schema, dependency, or mutation control was added. See [[Development/Reports/Phase 1H26AK Read Only Exact Current Win Reconciliation History]].
- **1H.26AL COMPLETE - READ-ONLY EXACT CURRENT WIN TICKET-BOOTH RECEIPT:** the existing authoritative receipt loader and HUD accept the fixed H26AJ chain and show `WIN`, Mesa selected, `79-113`, return `94`, net `+54`, and balance `154`. It writes nothing and rejects pending, partial, mixed, or altered evidence without partial values. See [[Development/Reports/Phase 1H26AL Read Only Player Facing Exact Current Win Receipt]].
- **1H.26AM COMPLETE - EXACT MESA/40 CANONICAL WAGER PLACEMENT:** the existing normal two-confirm ticket-booth path now accepts either exact current Match Winner selection at stake `40`. Mesa persists its exact probability/odds, potential `94` gross return, one `-40` debit, one pending request, and balance `60`; first confirm and repeated input remain zero mutation. See [[Development/Reports/Phase 1H26AM Exact Mesa 40 Canonical Wager Placement]].
- **1H.26AN COMPLETE - AUTOMATIC EXACT CURRENT-CHAIN MESA WIN DECISION ON LOCAL RESUME ONLY:** after exact durable H26L resume, normal non-QA startup invokes the existing strict decision engine once and reloads the fixed Mesa-selected, Mesa-winner, stake-`40`, return-due-`94`, `decided_pending_apply` decision with ledger `2/-40/60`. Cold restart is exact and byte-stable; invalid evidence mutates nothing. No payout, finalization, reconciliation, or receipt runs. See [[Development/Reports/Phase 1H26AN Automatic Exact Current Chain Mesa Win Decision on Local Resume]].
- **1H.26AO COMPLETE - AUTOMATIC EXACT CURRENT-CHAIN MESA +94 RETURN AND WIN FINALIZATION ON LOCAL RESUME ONLY:** after exact durable H26AN resume, the existing H26AJ finalizer appends one sequence-`3` `+94` payout, reaches balance `154`, and records one exact `settled_won` finalization. Cold restart is an exact byte-stable duplicate; invalid evidence mutates nothing; Harbor loss remains `2/60` with no payout. Existing projection regeneration is retained behavior only, and no Admin history or player receipt claim is added. See [[Development/Reports/Phase 1H26AO Automatic Exact Current Chain Mesa 94 Return Application and Win Finalization on Local Resume]].
- **1H.26AP COMPLETE - READ-ONLY EXACT AUTOMATIC MESA WIN RECONCILIATION:** the existing reconciliation-v1 validator/API/Operations card independently accept the exact automatic H26AN/H26AJ chain and show Mesa, probability `42413307`, odds `2.3577`, potential/return `94`, `79-113`, net `+54`, ledger `2/-40/60` then `3/+94/154`, balance `154`, `settled_won`, replay, and exact linkage. Invalid evidence fails closed, the source remains stable, and no schema, endpoint, card, control, or player receipt was added. See [[Development/Reports/Phase 1H26AP Read Only Exact Automatic Mesa Win Reconciliation History]].
- **1H.26AQ COMPLETE - READ-ONLY EXACT AUTOMATIC MESA WIN RECEIPT COMPATIBILITY:** the existing H26AL ticket-booth receipt accepts the exact H26AN/H26AJ automatic chain and shows `WIN`, Mesa selected, stake `40`, Harbor `79-113` Mesa, winner Mesa, returned `94`, net `+54`, balance `154`, and one close instruction. It reads authoritative SaveGame only, writes nothing, and rejects pending, partial, mixed, or altered evidence without partial fields. The retained isolated win and approved losses remain exact. See [[Development/Reports/Phase 1H26AQ Read Only Player Facing Exact Automatic Mesa Win Receipt Compatibility]].
- **1H.26AR.1 COMPLETE - DEVELOPMENT-ONLY HELD-INPUT RECEIPT LIFECYCLE DRIVER:** one exact explicit Development command uses Unreal native `W` / `A` / `D` held input and `E` press/release to exercise existing movement, proximity, and booth interaction. Packaged proof reached, opened, closed, left, returned, and reopened H26AQ with no transform, direct action, or SaveGame write. Test and Shipping contain no driver. This does not claim the broader H26AR lifecycle. See [[Development/Reports/Phase 1H26AR1 Development Only Held Input Receipt Lifecycle Driver]].
- **1H.26AR.2 COMPLETE - AUTOMATED NORMAL-PATH AND COLD-PROCESS EXACT RECEIPT LIFECYCLE PROOF:** two entirely separate packaged Development processes used the committed native held-input driver. Process A opened, closed, left, returned, and reopened H26AQ; Process B cold-launched later against the exact unchanged SaveGame and repeated it. Both captures show the identical Mesa-win receipt and one close instruction. No QA/teleport/direct action or production change was used. See [[Development/Reports/Phase 1H26AR2 Automated Normal Path and Cold Process Exact Automatic Mesa Win Receipt Lifecycle Proof]].
- **NEXT GATE:** fresh Scope Director review before any further implementation. Manual-player usability, generalized history, variable stakes, multiple wagers, correction, later markets, online authority, backend, or brain/simulator work remains separate and unproved.

### Owner gates

- **RESOLVED FOR MATCH WINNER V1:** market order, public source model, fair payout formula, `10`–`100` stake range, game-start lock, void/refund, correction, and equal public information under [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]].
- Margin, overtime, points, rebounds, and fouls each retain separate formula, threshold, limit, lock, correction/cancellation, and public-evidence gates.
- Legal, platform, age-rating, and regional review before any external beta involving wagering mechanics.

### Exit evidence

Every accepted wager has one immutable request, balance entry, lock decision, authoritative result, settlement, and history record. No payment or real-money Odds Bucks path exists.

## Phase 1I — Stores and lifestyle upgrades

### Bible sections advanced

- Avatar and clothing.
- Furniture.
- Odds Bucks spending.

### Smallest delivery path

1. **COMPLETE:** freeze one tiny approved clothing set and one tiny furniture set. The exact Sundale-origin catalog is the `60`-Odds-Bucks Signal Jacket and `100`-Odds-Bucks Modular Chair under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]]. Later cities receive separate catalogs rather than sharing one universal store inventory.
2. **COMPLETE:** buy the exact Signal Jacket at the physical clothing store with one idempotent server-authoritative Odds Bucks command. The immutable `store:sundale:signal_jacket:purchase:v1` debit is the local durable ownership record; purchase does not equip the item.
3. **COMPLETE:** explicitly equip the owned Signal Jacket at the physical clothing store and show the replicated slate-and-teal graybox appearance to another packaged local Sundale client. Equip adds no debit and does not auto-equip on purchase or restart.
4. **COMPLETE:** buy the exact Modular Chair at the physical furniture store with one idempotent server-authoritative `-100` Odds Bucks command, then derive and show its three-part gray-and-teal placeholder at `studio_primary` in the owned Studio after fresh entry and cold restart.
5. **COMPLETE:** buy the exact One-bedroom at the physical apartment-management kiosk with one idempotent server-authoritative `-500` Odds Bucks command after Studio ownership. Upgrade the Studio in place, preserve the owned chair at `studio_primary`, and restore the exact state after a cold process restart.

### Owner gates

- **RESOLVED FOR THE TWO STARTER ITEMS ONLY:** exact counts, prices, visual direction, one `outfit` slot, one `studio_primary` snap point, and no refunds under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]]. Later items remain a new owner gate.
- **RESOLVED FOR 1I.5 ONLY:** One-bedroom, `500` Odds Bucks, Studio prerequisite, in-place Studio upgrade, physical kiosk, and two E presses; see [[Design/Decisions/DEC-020 First One Bedroom Apartment Upgrade]]. Later tiers remain owner gates.

### Exit evidence

Ownership, balance, appearance, and apartment state reconcile across reconnect and rollback. Trading, gifting, marketplace, and real-money purchasing remain absent.

## Phase 1J — Athlete life and league storytelling

### Bible sections advanced

- Athletes and brains.
- Environmental and emergent storytelling.

### Smallest delivery path

1. **COMPLETE — 1J.1:** present durable talent differences, specialties, form, public workload, availability, and current Life Brain choices using existing authoritative evidence. Hidden fatigue, recovery, injury-risk, RNG, resolver, and private-effect values remain unpublished; see [[Development/Reports/Phase 1J1 Public Athlete Story Pages]].
2. **COMPLETE — 1J.2:** explain the public baseline, recent scoring difference, opportunity, form label, recorded life context, and availability boundary without exposing hidden state or inventing a cause; see [[Development/Reports/Phase 1J2 Safe Public Athlete Explanations]].
3. **COMPLETE — 1J.3a:** validate one fixed Development-only six-item public-fixture comprehension instrument and its Shipping exclusion; see [[Development/Reports/Phase 1J3a Development Only Athlete Story Comprehension Instrument]]. This validates the instrument, not human comprehension.
4. **COMPLETE — 1J.3b.0:** present the unchanged instrument one item at a time, accept exactly one A/B response per item, withhold the key and correctness until completion, and show only the submitted sequence plus score; see [[Development/Reports/Phase 1J3b0 Player Blind Development Comprehension Session Mode]]. This validates the Development-only session mechanism, not human comprehension.
5. **COMPLETE — 1J.3b.1a:** provide one equivalent unseen six-item form with changed public examples and independently arranged response sides while preserving the internal concept mapping, blind pre-completion boundary, and Shipping exclusion; see [[Development/Reports/Phase 1J3b1a Equivalent Blind Form Prerequisite]].
6. **COMPLETE — 1J.3b.1b / INITIAL GATE NOT PASSED:** one verified unseen and uncoached owner session completed all six items and scored `2/6`; measured misses were durable ability, recent form, life context versus causation, and public availability versus diagnosis. The consumed form is retired; see [[Development/Reports/Phase 1J3b1b One Owner Observed Comprehension Session]].
7. **COMPLETE — 1J.3b.1c:** clarify only the existing public presentation of the four missed concepts across all twelve athlete pages; see [[Development/Reports/Phase 1J3b1c Four Concept Athlete Reading Guide]]. The initial comprehension gate remains not passed.
8. **COMPLETE — 1J.3b.1d:** provide one fresh post-clarification Development-only blind form with exactly one item per approved concept, materially changed public examples and wording, independently arranged A/B sides, unchanged retired forms, and Shipping exclusion; see [[Development/Reports/Phase 1J3b1d Fresh Post Clarification Blind Form C Prerequisite]].
9. **COMPLETE — 1J.3b.1e / ONE OWNER 5/6:** one fresh unseen and uncoached owner session answered the four previously missed concepts correctly and missed only specialty versus overall quality. Form C is consumed and retired; see [[Development/Reports/Phase 1J3b1e One Owner Post Clarification Comprehension Session]].
10. **COMPLETE — 1J.3b.1f:** add the smallest public specialty clarification to all twelve athlete pages without changing athlete evidence or brain behavior; see [[Development/Reports/Phase 1J3b1f Public Specialty Clarification]].
11. **COMPLETE — PHASE 1J EXIT REVIEW:** the owner accepts the one-human unseen and uncoached `5/6` result plus the completed specialty clarification for the current bounded milestone. Forms A-C are consumed and retired; no fourth form or retest is authorized. See [[Design/Decisions/DEC-021 Phase 1J Bounded Athlete Story Evidence Acceptance]] and [[Development/Reports/Phase 1J Exit Review]].
12. Reopen Phase 1J only if measured first-hour or player evidence shows that a required distinction cannot be represented by existing public fields and clearer presentation.

### Owner gates

- Any new nightlife, club, doubt, morale, relationship, legal-event, or permanent career behavior beyond the frozen implementation.

### Exit evidence

One bounded owner sample, the public presentation corrections it produced, and explicit owner acceptance close the current milestone without a population-comprehension, causality, realism, learning, neural, beta-readiness, or production-readiness claim.

## Current validation queue

1. **COMPLETE — Phase 1K.0:** the eight existing route components are inventoried and one canonical [[Development/Phase 1K First-Hour Integration Evidence Contract]] defines the required actions, authority, evidence, reset, attempt record, and fail-fast rules.
2. **NEXT — Phase 1K.1:** run the exact contract from a fresh isolated profile in a packaged Development build, recording every intervention and stopping at the first named failure. Do not repair runtime inside the measurement phase.
3. **PENDING — later Phase 1K gates:** select only from measured 1K.1 failures; do not invent a generalized tutorial, orchestration framework, or new authority.
4. **CONDITIONAL — reopen Phase 1J:** only if measured first-hour or player evidence shows that required athlete distinctions cannot be represented by existing public fields and clearer presentation.

## Phase 1K — First-hour integration

### Bible sections advanced

- Entire first-hour player journey.
- Beta win condition.

### End-to-end path

1. Choose character.
2. Enter the shared city and see other equipped avatars.
3. Find the Studio, job, stadium/sportsbook, and stores.
4. Earn Odds Bucks.
5. Research and place the first approved wager.
6. Watch or skip the authoritative game.
7. Receive exact settlement.
8. Save or buy one visible clothing, furniture, or apartment progression upgrade.

### Phase 1K.0 baseline

**COMPLETE — CONTRACT ONLY.** The canonical [[Development/Phase 1K First-Hour Integration Evidence Contract]] freezes the minimum route as fresh profile/preset -> Sundale/passive peer -> required locations and Studio -> `+100` job payout -> approved Mesa/`40` wager -> watch or player `S` skip -> exact win receipt/balance `154` -> Signal Jacket purchase/equip/peer visibility -> cold persistence.

Each of the eight numbered route components has bounded individual Phase 1B-1J evidence. No fresh contiguous packaged first-hour session currently proves their coexistence. The contract requires identity, time, actions, prompts, confusion, intervention, QA, hashes, ledger, peer, cold-boundary, and no-hidden-data fields; all developer intervention after setup must be disclosed and causes the observed-player gate to fail.

Known evidence boundary: the standalone Phase 1F replay ends `101-104`, while the exact Phase 1H Mesa receipt settles `79-113`. Those different games cannot be spliced. Phase 1K.1 must stop unless one watched game identity, result, and seal match the settlement link and receipt.

### Exit evidence

Observed first-time players complete the loop without developer intervention. Confusion and failure points become measured follow-up phases, not speculative systems.

## Phase 1L — Content, presentation, and accessibility

### Bible sections advanced

- Art, music, and storytelling.
- World, avatar, housing, match, and store presentation.

### Delivery path

1. Replace only the placeholders visible in the proven first-hour path.
2. Apply the approved city, character, team, clothing, furniture, UI, lighting, atmosphere, and audio rules.
3. Add owner-provided or properly licensed music through the approved asset pipeline.
4. Add scalable graphics, readable UI, input remapping, subtitles/captions where needed, contrast, and motion options.
5. Benchmark packaged performance after every representative asset family.

### Exit evidence

The complete loop is visually coherent, readable, accessible at the approved baseline, and within measured PC performance targets. Large catalogs and unseen districts remain out of scope.

## Phase 1M — Reliability, compliance, and beta exit

### Release-wide gates

1. Persistence, migration, backup, restore, rollback, and reconnect.
2. Shared-city capacity, latency, disconnect, and recovery.
3. Odds Bucks, wager, inventory, and apartment reconciliation.
4. Replay and settlement immutability.
5. Authentication, authorization, secrets, audit, privacy, blocking, reporting, and moderation for the approved surface.
6. Accessibility and minimum-PC performance.
7. Legal, platform, age-rating, regional, and wagering-mechanic review for the intended beta audience.
8. Observed first-hour usability and retention evidence.
9. Admin operational checks and incident recovery.
10. Owner review of every OPEN decision still affecting release.

### Exit evidence

A Beta Exit Report states **READY**, **BLOCKED WITH MEASURED CAUSE**, or **NOT READY**. Only the owner can approve beta release and later authorize a Version 1 scope freeze under [[Design/Version 1 Game Bible|Version 1 Game Bible]].

## Owner-decision queue in dependency order

1. **RESOLVED:** Unreal Engine 5.8 beta adoption; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].
2. **RESOLVED FOR PHASE 1B:** camera, movement, and minimum placeholder presets; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults]]. Final art remains later.
3. **RESOLVED FOR PHASE 1C:** Daymark / Sundale supplies the approved modern civic-commons direction; the primitive packaged `800 m` route passed Phase 1C exit. Sundale remains a working name and final art remains open; see [[Design/Decisions/DEC-008 Beta First City Direction]], [[Design/Sundale Art Direction and Core Loop]], and [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].
4. **CURRENT OWNER GATE:** shared-city instance capacity, regions, collision, names, and minimal safety surface.
5. **RESOLVED FOR THE FIRST UPGRADE ONLY:** One-bedroom costs `500`, requires Studio ownership, and upgrades the Studio in place. Later layouts, visits, and decorating controls remain open; see [[Design/Decisions/DEC-020 First One Bedroom Apartment Upgrade]].
6. **RESOLVED FOR THE CURRENT PHASE 1J MILESTONE:** accept one unseen and uncoached owner `5/6` result plus the completed specialty clarification; retire Forms A-C and create no fourth form or retest. See [[Design/Decisions/DEC-021 Phase 1J Bounded Athlete Story Evidence Acceptance]].
7. 82-game schedule variety, team count, calendar, and presentation cadence.
8. **PARTIALLY RESOLVED:** current placeholder fidelity, fixed camera, text-only callouts, three-minute full-watch duration, and result-invariant player skip; see [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]]. Final content treatment remains later.
9. **RESOLVED FOR LOCAL BETA RECOVERY:** start at `0`, earn `100` from the placeholder job on a rolling `24`-hour cooldown, accumulate balances, and use no separate allowance or catch-up payout. Production account/time authority, post-wager recovery-floor behavior, prices, and broader limits remain open.
10. Wager markets, odds, payouts, lock, limits, correction, and cancellation.
11. Clothing/furniture catalog, pricing, equipment, placement, and refunds. City-origin identity is resolved under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]].
12. Minimum PC, accessibility, beta audience, regions, and release channel.

## Scope Director operating rules

1. Read the entire Beta Game Bible, then this roadmap, Current Plan, latest report, and relevant decisions.
2. Follow the earliest incomplete dependency unless a measured defect requires a corrective gate.
3. Cite the roadmap phase and exact Bible section advanced.
4. Choose one smallest phase or subphase with explicit acceptance evidence.
5. Stop and ask the owner when the next dependency is an OWNER GATE or OPEN decision.
6. Never mark a roadmap phase complete from documentation alone when its outcome requires running software.
7. Update the roadmap status only after the Coordinator verifies a scoped commit and evidence.
8. Keep Version 1 and POST-V1 work inactive until owner-approved beta exit.
9. Preserve the frozen Phase 0 brains, authoritative event log, equal-information boundary, server-owned Odds Bucks/settlement, and immutable history.
10. Prefer one playable vertical path over generalized frameworks, large asset catalogs, or invisible infrastructure.

## Explicitly parked outside this roadmap

- Real-money Odds Bucks purchases.
- Player item trading, gifting, marketplace, or transfer.
- Other sports, including fights.
- Additional cities, travel, vehicles, houses, and mansions.
- Full 10-20-year career ecosystem.
- Open chat/voice or large social systems unless separately approved for beta safety needs.
- Version 1 implementation before beta exit approval.
