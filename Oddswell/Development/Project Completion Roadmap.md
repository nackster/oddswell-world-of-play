---
tags: [development, roadmap, beta]
status: active-completion-plan
date: 2026-10-10
---

# OddsWell completion roadmap

OddsWell is a walkable 3D city built around a persistent fictional basketball league and Odds Bucks. A player chooses a character, arrives with little, works, inspects and watches a game, wagers, receives an authoritative result, and improves clothing and housing. The city and its people must have a recognizable OddsWell identity in an ordinary gameplay screenshot.

This is the short delivery view of [[Development/Beta Delivery Roadmap]] and [[Design/Beta Game Bible]], not a replacement for their product decisions. Completion first means an approved playable beta. Version 1 is a later, separately frozen release; its implementation remains inactive until owner-approved beta exit.

## Where we are

The engine, packaged client, movement, local shared-city presence, Studio, job recovery, wager/settlement components, small store catalog and athlete presentation have substantial bounded prototype evidence. They are not an external production service. Phase 1K still needs one observed, contiguous first-hour loop. Phase 1L still needs finished art, accessibility and measured target-PC performance. Phase 1M release reliability and operational gates remain open.

The owner accepted the scanned-human visual direction on October 10. Use that stronger base for future character work. Its original business clothes and experimental walk remain temporary. The older procedural character and rejected starter-outfit reviews are historical evidence, not the visual target to keep polishing. This does not silently promote either character into Unreal or pass existing runtime gates.

## Delivery milestones

| Order | Deliverable | Current position | Completion gate |
|---|---|---|---|
| 1 | Human character and OddsWell wardrobe | Scanned human imported and reviewed offline; source clothing and gait unfinished | Believable full figure, relaxed movement and hands; approved starter clothing and Signal Jacket; face, side, back and walking views pass visual review. Preserve editable licensed sources locally. |
| 2 | Character in the actual game | Existing shared skeletal runtime prototype; new scan has no engine integration | Compatible game derivative, correct scale and skinning, walk/run/jump/land and camera behavior; all eight preset IDs and four tones remain supported; equip, replication and cold saves still work. Decide how the scanned base satisfies the existing neutral-silhouette contract before promotion. |
| 3 | One distinctive Sundale block | Graybox route and presentation passes exist; offline street direction developed | Approved warm mineral/brick palette, varied storefront depth and awnings, mature canopy and layered planting, readable court/arena sightlines; character and city read together from the real gameplay camera. Replace only first-hour-visible content. |
| 4 | Finish first-hour presentation | Destination identities and bounded UI/replay work exist | Job, housing, sportsbook, arena, stores, athlete pages and receipts are understandable in play; consistent OddsWell graphics, sound and licensed audio; no obscured prompts or misleading result identity. |
| 5 | One complete first-hour session | Components have separate proof; automated route smoke exists; physical usability proof is owner-deferred | Fresh character, passive peer, Studio, job payout, exact game/wager/watch/settlement, upgrade and cold restore coexist in one retained session. Same game identity, score and seal throughout; record assistance and failures. Observed player proof is still required before beta exit. |
| 6 | Accessibility and target-PC performance | Provisional Balanced 1080p60/Medium policy selected; validation incomplete | Remapping, readable contrast/text, required captions and motion options; packaged measurements on the approved minimum PC after representative character/city assets. Policy selection alone is not a benchmark pass. |
| 7 | Durable multiplayer and authority | Local two-client and saved-profile evidence exists | Approved capacity/regions/safety surface; account and time authority, reconnect/disconnect, latency and recovery measurements; balances, wagers, equipment, furniture and housing reconcile through migration, backup, restore and rollback. |
| 8 | Closed beta readiness | Not ready for release | Security/privacy/moderation and intended-audience legal/platform review; remove or contain Development trace-listener debt before external use; admin incident recovery, critical defect ownership and observed first-hour usability. Produce Phase 1M Beta Exit Report and obtain owner release decision. |
| 9 | Beta feedback and Version 1 freeze | Future gate | Resolve measured beta defects; owner approves exact Version 1 scope, audience and release gates. Do not automatically expand into additional cities, sports, trading or real-money systems. |
| 10 | Version 1 delivery | Inactive until milestone 9 | Implement only the frozen Version 1 scope; repeat integration, reliability, performance and operational acceptance; owner reviews release evidence. Dates require a scope freeze and measured throughput. |

Milestones 1–4 form the current visual production path. A measured gameplay defect can take priority. Milestone 5's physical session remains deferred to the owner-approved playtest, while independent art work continues. Prototype evidence supports implementation reuse; it never substitutes for the later integration and release gates.

## Immediate work queue

1. Refine the accepted scan's exaggerated stride and outward arm posture; retain full, front and side images and a native walking preview. **First checkpoint delivered:** [[Art/Production/SundaleStreetSlice/ScannedHumanMotionCandidate/README]]. Planted-foot timing and relaxed hands still need review.
2. Build or obtain compatible casual clothing matching the existing off-white starter outfit and slate/teal Signal Jacket. A recolored vest does not meet this gate; source trousers cannot become shorts without appropriate leg geometry.
3. Review the whole character against the original street concept at close and gameplay distances, then establish the production export/rig/preset contract.
4. Integrate one character candidate into the existing Unreal path and verify movement, equipment, peer visibility and persistence before expanding the catalog.
5. Finish one city block around that accepted character, then benchmark the actual packaged combination.

Each completed step needs a visible or running result, a short report, editable source where applicable and a scoped local commit. Avoid another sequence of microscopic anatomy tweaks without a whole-character visual gain. A failed qualitative review stays failed even when numeric checks pass.

## Decisions needed before dependent release work

Shared-city capacity/regions and safety surface; production account/time authority; remaining league schedule and market choices; catalogs beyond the two approved starter items and first apartment upgrade; final audience, accessibility baseline and release channel. Resolve only when their dependency is reached, using the accepted decision records. No dates or percentage-complete estimate are invented here.

Sources: [[Development/Beta Delivery Roadmap]], [[Design/Beta Game Bible]], [[Design/Version 1 Game Bible]], [[Development/Phase 1K First-Hour Integration Evidence Contract]], [[Art/Production/SundaleStreetSlice/ScannedHumanCandidate/Review]]. The separate “Verify game plans” chat's latest nightly check reports its older Phase 1L.5ct review uncommitted/unsynced; this plan neither commits that work nor treats it as passed.
