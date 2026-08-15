---
tags:
  - decision
  - minimum-pc
  - phase-1l
status: accepted
date: 2026-08-14
---

# DEC-026 Provisional Balanced 1080p60 Minimum-PC Target

## Owner response

The owner's literal response was:

> Yes that's gret

## Decision

The owner provisionally selected candidate `MINPC-B_BALANCED_1080P60`. Its owner-selection status is `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. Candidate A `MINPC-A_REACH_1080P30` and candidate C `MINPC-C_QUALITY_1440P60` each have selection status `NOT_SELECTED`.

Overall minimum-PC decision status is `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Provisional owner-selection authority and count are `1` for B. This does not change the frozen candidate's historical `CANDIDATE_NOT_APPROVED` evidence status or supply final approval, validation, representative testing, measured performance, minimum-PC validation, compatibility, readiness, or release credit; each remains `0`.

## Frozen candidate B contract

The following 25 fields are copied unchanged from [[Development/Reports/Phase 1L5f Candidate Minimum PC Specification Decision Packet]].

| # | Field | Frozen candidate B value |
|---:|---|---|
| 1 | Candidate ID | `MINPC-B_BALANCED_1080P60` |
| 2 | Name | Balanced 1080p60 |
| 3 | Status | `CANDIDATE_NOT_APPROVED` |
| 4 | Owner-review marker | `RECOMMENDED_FOR_OWNER_REVIEW` |
| 5 | Windows lifecycle | Currently supported Windows 11 Home/Pro 64-bit release; ordinary Windows 10 Home/Pro is excluded because support ended 2025-10-14; the complete system must satisfy CPU, UEFI, Secure Boot, and TPM 2.0 requirements. |
| 6 | API / DirectX / feature | DX12 Ultimate-class GPU and WDDM 2.0. `Direct3D feature level: OWNER_UNSET / UNVERIFIED`. Current packaged rendering path only; Shader Model 6, Lumen, Nanite, and Virtual Shadow Map use remain `OWNER_UNSET`, with no enablement claim. Future validation gate: the owner approves the required feature level and feature set, then the representative system must query, log, and satisfy them before any candidate pass. |
| 7 | CPU rule and named example | At least 6 cores / 12 threads and 3.50 GHz base. Example: AMD Ryzen 5 5600, 6 cores / 12 threads, 3.50 GHz base / up to 4.40 GHz boost. |
| 8 | RAM | 16 GB |
| 9 | GPU rule, named example, and VRAM | Discrete DX12 Ultimate-class GPU with at least 8 GB VRAM. Example: AMD Radeon RX 6600 8 GB. |
| 10 | SSD and free headroom | SSD with at least 20 GB free before install; editorial hypothesis, not measured installed-footprint proof. |
| 11 | Resolution | `1920x1080` |
| 12 | Preset | Medium |
| 13 | Target average FPS | At least `60` |
| 14 | Target median FPS | At least `60` |
| 15 | Average frame-time target | At most `16.67 ms` |
| 16 | Median frame-time target | At most `16.67 ms` |
| 17 | P95 frame-time target | At most `25.00 ms` |
| 18 | Stutter target | After a `60 s` warm-up, at most `1.0%` of scored frames over `33.33 ms` and zero individual scored frames over `100 ms`. |
| 19 | Load target | Cold process launch to controllable Sundale at most `30 s`; city-to-stadium and stadium-to-city transitions at most `15 s` each. |
| 20 | Representative future scene envelope | Cold launch to controllable Sundale; current canonical 11-point / 80,000 cm city route; Commons, retail, and Studio traversal; Ticket Booth UI open and close; Stadium replay; city/stadium transitions; and a 10-minute steady Sundale loop, with no route or gameplay change. |
| 21 | Audience and tradeoff | Mainstream 1080p desktops: proposed smoothness and quality balance with 8 GB VRAM, at higher entry cost than A and lower memory or quality headroom than C. |
| 22 | Evidence status | `OFFICIAL_SPEC_RESEARCH_ONLY + PHASE1L5E_CURRENT_MACHINE_ONLY_NONCOMPARATIVE + CANDIDATE_UNMEASURED` |
| 23 | Known unknowns | Exact Direct3D feature level; packaged average and median FPS; frame-time distribution; VRAM, CPU, and RAM use; shader or streaming stutter; loads; thermals and power; complete-system compatibility; installed footprint; player-device distribution; and current or future driver support. |
| 24 | Future proof | Owner approves the exact hardware, API, Direct3D feature level, and acceptance criteria. Then use a representative stock complete system, currently supported OS, and latest stable AMD driver; hash-lock package and config; query and log feature level; run 3 cold and 3 warm repeats of the identical envelope; capture the same complete metrics and failures; grant no pass from partial evidence. |
| 25 | Authority and result | Approval `0`; selection `0`; minimum-PC and readiness credit `0`. |

The field-25 selection value remains the frozen candidate-packet snapshot. This decision records current provisional owner-selection authority and count `1` outside that historical evidence contract; it does not rewrite prior evidence into a measured or approved result.

## Required future validation

Before any minimum-PC approval, the owner must separately authorize the frozen field-24 proof on a representative complete system. The exact Direct3D feature level remains `OWNER_UNSET / UNVERIFIED` and must be approved, queried, logged, and satisfied. Average and median FPS, average and median frame time, P95 frame time, stutter, loads, VRAM, RAM, CPU, thermals, power, complete-system compatibility, and failure evidence remain unmeasured.

## Not authorized

This decision authorizes no machine acquisition, procurement, test, run, package or config change, performance promise, optimization, product change, accessibility completion, minimum-PC approval, beta readiness, production readiness, Phase `4/6`, roadmap Phase 2, Version 1, or release work. Phase 1K remains incomplete and not waived.

The bounded closure report is [[Development/Reports/Phase 1L5f1 Balanced 1080p60 Owner Selection Closure]].
