# Phase 1L.5f Candidate Minimum-PC Specification Decision Packet

- Date: 2026-08-14
- Branch: `agent/phase-0d`
- Baseline commit: `388537de84eb2f9dceb7e82aa56bb89f15c6acb2`
- Status: **COMPLETE LOCALLY FOR THREE UNAPPROVED CANDIDATES; MINIMUM-PC REMAINS `OPEN_OWNER`**
- Batch position: fresh Phase `2/6`, pending local commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

This packet gives the owner exactly three equal-schema minimum-PC candidates for comparison. All three have status `CANDIDATE_NOT_APPROVED`. Candidate B alone carries the separate marker `RECOMMENDED_FOR_OWNER_REVIEW`; that marker is an editorial recommendation for discussion, not approval, selection, procurement authority, or a source claim. Approved candidates: `0`. Selected candidates: `0`.

The resolution, preset, FPS, frame-time, stutter, load, and SSD-headroom values are `NONBINDING_EDITORIAL_HYPOTHESIS_UNMEASURED_UNAPPROVED`. Official sources substantiate operating-system lifecycle, platform/API requirements, and named-product specifications only. No source substantiates OddsWell performance on these candidates, and no candidate machine was acquired, configured, or tested.

## Exact equal-schema candidate matrix

| # | Field | A | B | C |
|---:|---|---|---|---|
| 1 | Candidate ID | `MINPC-A_REACH_1080P30` | `MINPC-B_BALANCED_1080P60` | `MINPC-C_QUALITY_1440P60` |
| 2 | Name | Reach 1080p30 | Balanced 1080p60 | Quality 1440p60 |
| 3 | Status | `CANDIDATE_NOT_APPROVED` | `CANDIDATE_NOT_APPROVED` | `CANDIDATE_NOT_APPROVED` |
| 4 | Owner-review marker | `NONE` | `RECOMMENDED_FOR_OWNER_REVIEW` | `NONE` |
| 5 | Windows lifecycle | Currently supported Windows 11 Home/Pro 64-bit release; ordinary Windows 10 Home/Pro is excluded because support ended 2025-10-14; the complete system must satisfy CPU, UEFI, Secure Boot, and TPM 2.0 requirements. | Currently supported Windows 11 Home/Pro 64-bit release; ordinary Windows 10 Home/Pro is excluded because support ended 2025-10-14; the complete system must satisfy CPU, UEFI, Secure Boot, and TPM 2.0 requirements. | Currently supported Windows 11 Home/Pro 64-bit release; ordinary Windows 10 Home/Pro is excluded because support ended 2025-10-14; the complete system must satisfy CPU, UEFI, Secure Boot, and TPM 2.0 requirements. |
| 6 | API / DirectX / feature | DX12 and WDDM 2.0. `Direct3D feature level: OWNER_UNSET / UNVERIFIED`. Current packaged rendering path only; no Lumen, Nanite, Virtual Shadow Map, or hardware-ray-tracing dependency or enablement is assumed. Future validation gate: the owner approves the required feature level, then the representative system must query, log, and satisfy it before any candidate pass. | DX12 Ultimate-class GPU and WDDM 2.0. `Direct3D feature level: OWNER_UNSET / UNVERIFIED`. Current packaged rendering path only; Shader Model 6, Lumen, Nanite, and Virtual Shadow Map use remain `OWNER_UNSET`, with no enablement claim. Future validation gate: the owner approves the required feature level and feature set, then the representative system must query, log, and satisfy them before any candidate pass. | DX12 Ultimate-class GPU and WDDM 2.0. `Direct3D feature level: OWNER_UNSET / UNVERIFIED`. Current packaged rendering path only; Shader Model 6, Lumen, Nanite, and Virtual Shadow Map use remain `OWNER_UNSET`, with no enablement claim. Future validation gate: the owner approves the required feature level and feature set, then the representative system must query, log, and satisfy them before any candidate pass. |
| 7 | CPU rule and named example | At least 6 physical cores and 2.80 GHz base. Example: Intel Core i5-8400, 6 cores / 6 threads, 2.80 GHz base / 4.00 GHz maximum. | At least 6 cores / 12 threads and 3.50 GHz base. Example: AMD Ryzen 5 5600, 6 cores / 12 threads, 3.50 GHz base / up to 4.40 GHz boost. | At least 6 cores / 12 threads and 2.50 GHz base. Example: Intel Core i5-12400, 6 cores / 12 threads, 2.50 GHz base / 4.40 GHz maximum. |
| 8 | RAM | 16 GB | 16 GB | 32 GB |
| 9 | GPU rule, named example, and VRAM | Discrete DX12 GPU with at least 6 GB VRAM. Example: NVIDIA GeForce GTX 1060 6 GB. | Discrete DX12 Ultimate-class GPU with at least 8 GB VRAM. Example: AMD Radeon RX 6600 8 GB. | Discrete DX12 Ultimate-class GPU with at least 8 GB VRAM. Example: Intel Arc A750 8 GB. |
| 10 | SSD and free headroom | SSD with at least 20 GB free before install; editorial hypothesis, not measured installed-footprint proof. | SSD with at least 20 GB free before install; editorial hypothesis, not measured installed-footprint proof. | SSD with at least 20 GB free before install; editorial hypothesis, not measured installed-footprint proof. |
| 11 | Resolution | `1920x1080` | `1920x1080` | `2560x1440` |
| 12 | Preset | Low | Medium | High |
| 13 | Target average FPS | At least `30` | At least `60` | At least `60` |
| 14 | Target median FPS | At least `30` | At least `60` | At least `60` |
| 15 | Average frame-time target | At most `33.33 ms` | At most `16.67 ms` | At most `16.67 ms` |
| 16 | Median frame-time target | At most `33.33 ms` | At most `16.67 ms` | At most `16.67 ms` |
| 17 | P95 frame-time target | At most `50.00 ms` | At most `25.00 ms` | At most `25.00 ms` |
| 18 | Stutter target | After a `60 s` warm-up, at most `1.0%` of scored frames over `50.00 ms` and zero individual scored frames over `200 ms`. | After a `60 s` warm-up, at most `1.0%` of scored frames over `33.33 ms` and zero individual scored frames over `100 ms`. | After a `60 s` warm-up, at most `1.0%` of scored frames over `33.33 ms` and zero individual scored frames over `100 ms`. |
| 19 | Load target | Cold process launch to controllable Sundale at most `45 s`; city-to-stadium and stadium-to-city transitions at most `20 s` each. | Cold process launch to controllable Sundale at most `30 s`; city-to-stadium and stadium-to-city transitions at most `15 s` each. | Cold process launch to controllable Sundale at most `30 s`; city-to-stadium and stadium-to-city transitions at most `15 s` each. |
| 20 | Representative future scene envelope | Cold launch to controllable Sundale; current canonical 11-point / 80,000 cm city route; Commons, retail, and Studio traversal; Ticket Booth UI open and close; Stadium replay; city/stadium transitions; and a 10-minute steady Sundale loop, with no route or gameplay change. | Cold launch to controllable Sundale; current canonical 11-point / 80,000 cm city route; Commons, retail, and Studio traversal; Ticket Booth UI open and close; Stadium replay; city/stadium transitions; and a 10-minute steady Sundale loop, with no route or gameplay change. | Cold launch to controllable Sundale; current canonical 11-point / 80,000 cm city route; Commons, retail, and Studio traversal; Ticket Booth UI open and close; Stadium replay; city/stadium transitions; and a 10-minute steady Sundale loop, with no route or gameplay change. |
| 21 | Audience and tradeoff | Reach-oriented older or upgraded Windows 11 desktops: broadest access and lowest visual preset, with the highest driver-lifecycle risk and least headroom. | Mainstream 1080p desktops: proposed smoothness and quality balance with 8 GB VRAM, at higher entry cost than A and lower memory or quality headroom than C. | Quality-oriented 1440p desktops: higher image-quality and memory class, with the narrowest reach, highest complete-system cost, and Arc platform / ReBAR diligence. |
| 22 | Evidence status | `OFFICIAL_SPEC_RESEARCH_ONLY + PHASE1L5E_CURRENT_MACHINE_ONLY_NONCOMPARATIVE + CANDIDATE_UNMEASURED` | `OFFICIAL_SPEC_RESEARCH_ONLY + PHASE1L5E_CURRENT_MACHINE_ONLY_NONCOMPARATIVE + CANDIDATE_UNMEASURED` | `OFFICIAL_SPEC_RESEARCH_ONLY + PHASE1L5E_CURRENT_MACHINE_ONLY_NONCOMPARATIVE + CANDIDATE_UNMEASURED` |
| 23 | Known unknowns | Exact Direct3D feature level; packaged average and median FPS; frame-time distribution; VRAM, CPU, and RAM use; shader or streaming stutter; cold and warm loads; thermals and power; complete-system compatibility; installed footprint; player-device distribution; and Pascal lifecycle constraints. | Exact Direct3D feature level; packaged average and median FPS; frame-time distribution; VRAM, CPU, and RAM use; shader or streaming stutter; loads; thermals and power; complete-system compatibility; installed footprint; player-device distribution; and current or future driver support. | Exact Direct3D feature level; packaged 1440p High average and median FPS; frame-time distribution; VRAM, CPU, and RAM use; shader or streaming stutter; loads; thermals and power; complete-system, driver, and ReBAR compatibility; installed footprint; and player-device distribution. |
| 24 | Future proof | Owner approves the exact hardware, API, Direct3D feature level, and acceptance criteria. Then use a representative stock complete system, currently supported OS, and latest available vendor security-capable driver; hash-lock package and config; query and log feature level; run 3 cold and 3 warm repeats of the identical envelope; capture average and median FPS, average, median, and P95 frame time, stutter, loads, VRAM, RAM, CPU, thermals, power, and failures; grant no pass from partial evidence. | Owner approves the exact hardware, API, Direct3D feature level, and acceptance criteria. Then use a representative stock complete system, currently supported OS, and latest stable AMD driver; hash-lock package and config; query and log feature level; run 3 cold and 3 warm repeats of the identical envelope; capture the same complete metrics and failures; grant no pass from partial evidence. | Owner approves the exact hardware, API, Direct3D feature level, and acceptance criteria. Then use a representative stock complete system, currently supported OS, and latest stable Intel driver with ReBAR state recorded; hash-lock package and config; query and log feature level; run 3 cold and 3 warm repeats of the identical envelope; capture the same complete metrics and failures; grant no pass from partial evidence. |
| 25 | Authority and result | Approval `0`; selection `0`; minimum-PC and readiness credit `0`. | Approval `0`; selection `0`; minimum-PC and readiness credit `0`. | Approval `0`; selection `0`; minimum-PC and readiness credit `0`. |

Matrix audit: profiles `3`; equal 25-field schema rows `3`; `CANDIDATE_NOT_APPROVED` cells `3`; `RECOMMENDED_FOR_OWNER_REVIEW` cells `1` and only B; Direct3D feature-level values `OWNER_UNSET / UNVERIFIED` `3`; target average FPS values `30/60/60`; target median FPS values `30/60/60`; explicit P95, stutter, load, future-scene, evidence, unknown, and future-proof cells `3` each. Approved `0`; selected `0`; fresh tests or runs `0`; performance promises `0`; minimum-PC and readiness credit `0`.

## Why B alone is recommended for owner review

The separate B marker is a bounded editorial inference: it combines a currently supported Windows 11 CPU example, 6 cores / 12 threads, 16 GB RAM, and an 8 GB DX12 Ultimate-class GPU example while avoiding A's explicitly limited Pascal driver lifecycle and C's higher 1440p, memory, platform, and cost posture. This comparison does not establish equivalence across vendors, packaged-game performance, affordability in any market, or an approved minimum.

## Official primary-source ledger

Every source below was fetched successfully from its official publisher and accessed on 2026-08-14.

- [Epic Games: Unreal Engine 5.8 Hardware and Software Specifications](https://dev.epicgames.com/documentation/unreal-engine/hardware-and-software-specifications-for-unreal-engine?lang=en-US) lists Windows 11, a quad-core 2.5 GHz processor, 32 GB RAM, 8 GB graphics RAM, a DX12-compatible card, and current drivers as recommended development hardware. It separately identifies engine/editor software and feature-specific Lumen and Nanite requirements. Those values are context, not an OddsWell packaged-game minimum.
- [Microsoft: Windows 10 Home and Pro lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/windows-10-home-and-pro) records ordinary Windows 10 Home/Pro support ending on 2025-10-14.
- [Microsoft: Windows 11 Home and Pro lifecycle](https://learn.microsoft.com/en-gb/lifecycle/products/windows-11-home-and-pro) records the product as in support and gives release-specific retirement dates.
- [Microsoft: Windows 11 system requirements](https://support.microsoft.com/en-us/windows/windows-11-system-requirements-86c11283-ea52-4782-9efd-7674389a7ba3) identifies the approved-CPU, UEFI, Secure Boot, TPM 2.0, DX12, and WDDM 2.0 platform requirements.
- [Microsoft: DirectX installation and updates](https://support.microsoft.com/en-us/windows/hardware/display-graphics/how-to-install-the-latest-version-of-directx) explains that DirectX is a Windows component and that DirectX 12 updates arrive through Windows Update.
- [Microsoft: Windows 11 supported Intel processors](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-supported-intel-processors) lists 8th-generation and 12th-generation Core i5 families. [Microsoft: Windows 11 supported AMD processors](https://learn.microsoft.com/en-us/windows-hardware/design/minimum/supported/windows-11-supported-amd-processors) lists Ryzen 5 5600. These lists do not replace complete-system eligibility checks.
- [Intel: Core i5 Desktop Processor Comparison Chart](https://www.intel.com/content/dam/support/us/en/documents/processors/core/intel-core-i5-comparison-chart.pdf) gives the i5-8400 example as 6 cores / 6 threads at 2.80 GHz base and 4.00 GHz maximum.
- [NVIDIA: GeForce GTX 1060 specifications](https://www.nvidia.com/en-us/geforce/news/nvidia-geforce-gtx-1060/) gives the 6 GB GDDR5 example, and the [official NVIDIA GTX 1060 release PDF](https://nvidianews.nvidia.com/_gallery/download_pdf/5a0ee565ed6ae554781f77dc/) identifies DirectX 11/12 support. [NVIDIA's Pascal support plan](https://www.nvidia.com/en-my/geforce/news/mafia-the-old-country-geforce-game-ready-driver/) says the final Game Ready release was in October 2025 and quarterly security updates continue through October 2028.
- [AMD: Ryzen 5 5600 specifications and support](https://www.amd.com/en/support/downloads/drivers.html/processors/ryzen/ryzen-5000-series/amd-ryzen-5-5600.html) gives 6 cores / 12 threads, 3.50 GHz base, up to 4.40 GHz boost, and Windows 11 support.
- [AMD: Radeon RX 6600 specifications](https://www.amd.com/en/products/graphics/desktops/radeon/6000-series/amd-radeon-rx-6600.html) gives 8 GB GDDR6, and the [official AMD RX 6600 release](https://www.amd.com/en/newsroom/press-releases/2021-10-13-amd-radeon-rx-6600-graphics-card-delivers-incredib.html) identifies Windows 11 and DirectX 12 Ultimate support. Manufacturer benchmark marketing is not reused as OddsWell evidence.
- [Intel: Core i5-12400 specifications](https://www.intel.com/content/www/us/en/products/sku/134586/intel-core-i512400-processor-18m-cache-up-to-4-40-ghz/specifications.html) gives 6 cores / 12 threads, 2.50 GHz base, and 4.40 GHz maximum.
- [Intel: Arc A750 specifications](https://www.intel.com/content/www/us/en/products/sku/227954/intel-arc-a750-graphics/specifications.html) gives 8 GB GDDR6 and DirectX 12 Ultimate support. [Intel: Arc A-Series ReBAR guidance](https://www.intel.com/content/www/us/en/support/articles/000092416/graphics.html) says Arc works without ReBAR but requires it for optimal performance and expressly includes A750.

No cited source is used to claim an exact Direct3D feature level or OddsWell performance.

## Phase 1L.5e current-machine-only evidence

The retained Phase 1L.5e report has SHA-256 `EC84FD9FDAB8AF48D6062CE54C8D67E86D929128AE5F945A0FD3272F4CFAEE3C`. Its machine was Windows `10.0.26200.0`, Intel Core Ultra 9 185H, `22` logical processors, and `68,125,036,544` physical RAM bytes. Exactly `158` direct-PID one-second samples covered `157.019 s` with `0` errors. Working-set median/P95/maximum was `1,647.842/1,650.898/1,651.285 MiB`; private bytes was `3,876.734/3,878.793/3,879.168 MiB`; CPU advanced `620.125 s`, or `394.936%` of one logical-core equivalent.

The local evidence identities are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `machine.json` | 246 | `9831B4D62D2DFF730B73AAEBBFCA33246134C490781F78288E501B1E88604B14` |
| `result.json` | 1,860 | `BB543ADC0C144C0901260EB4BDE41C4992AB355400A2836C3C943EB58487227D` |
| `samples.stats.json` | 1,784 | `EC2CD8C9C3111DC420F19242B3BE5C4530DB9A645A0F7C4DDC3F66E294DC8821` |
| `manifest.tsv` | 2,179 | `9655738B19C35EB7635A20DD725869960D32CFCC9149F97E6846A845A933EC01` |
| `verdict.tsv` | 237 | `BFD2F3F208C87856AE94B392872292F5A01898BE07B4EA16E00DC30A0957810C` |

This evidence is `CURRENT_MACHINE_ONLY`. It contains no GPU model, GPU utilization, VRAM, FPS, frame-time, power, thermal, minimum-PC, or representative-population measurement and cannot select, approve, reject, rank by measured performance, or validate any candidate.

## Boundary and next gate

This phase changes documentation and canvas text only. It changes no product, client, map, package, runtime, config, test, route, gameplay, art, music, accessibility, input, brain, economy, or wagering behavior. No candidate is approved or selected, minimum-PC remains `OPEN_OWNER`, and no test, acquisition, procurement, optimization, compatibility, readiness, beta-exit, or release conclusion follows.

Phase 1K and the Phase 1L.5a input/accessibility evidence remain deferred, incomplete, and not waived. Music and Phase 1L exit remain incomplete. Phase 1M, roadmap Phase 2, Version 1, beta readiness, production readiness, and release work remain unauthorized. This is fresh Phase `2/6`; no Phase `3/6` or Notion work is authorized by this packet. See [[Development/Beta Delivery Roadmap]], [[Development/Current Plan]], and [[Design/Beta Game Bible]].
