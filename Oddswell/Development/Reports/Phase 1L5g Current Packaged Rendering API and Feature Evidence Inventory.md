# Phase 1L.5g Current Packaged Rendering API and Feature Evidence Inventory

- Date: 2026-08-14
- Branch: `agent/phase-0d`
- Baseline commit: `c9cba81dfcd6f315c9e436e14698fd13c0bf0651`
- Status: **COMPLETE LOCALLY — EVIDENCE INVENTORY ONLY; B VALIDATION INCOMPLETE**
- Batch position: fresh Phase `4/6`, pending local commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

This read-only inventory records exactly `16` rendering API and feature surfaces from current project configuration and retained Phase 1L.5e packaged-process evidence. It launches no process, performs no test, changes no source or configuration, and makes no performance or compatibility claim.

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. Its historical candidate evidence status remains `CANDIDATE_NOT_APPROVED`; its Direct3D feature level remains `OWNER_UNSET / UNVERIFIED`; overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. This inventory grants final approval, validation, representative testing, measured performance, minimum-PC validation, compatibility, and readiness credits of `0`.

## Evidence custody

| Input | Bytes | SHA-256 / retained identity |
|---|---:|---|
| `client/OddsWell/OddsWell.uproject` | `190` | `020234D58303E8D98C9E1D83B683F4F8F7889383932F069640E3284EBD2FEE18`; line 3 binds `EngineAssociation` to `5.8` |
| `client/OddsWell/Config/DefaultEngine.ini` | `2,755` | `1442E7ADF71B4028993465D95A92C12C9FB8E39D0DA4AC77229C6B920E38F6D1` |
| `client/OddsWell/Config/DefaultGame.ini` | `675` | `CE966B4DEF240A9F99712BBF79BD1F9832125D4251FCEFB60498458523F86048`; no graphics-policy keys |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/machine.json` | `246` | `9831B4D62D2DFF730B73AAEBBFCA33246134C490781F78288E501B1E88604B14` |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/result.json` | `1,860` | `BB543ADC0C144C0901260EB4BDE41C4992AB355400A2836C3C943EB58487227D` |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/route.log` | `96,908` | `4576B02AAD4D51A6E0F8F416ACB4181CF61AED38412FCE0BD1A4F4E851647347` |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/manifest.tsv` | `2,179` | `9655738B19C35EB7635A20DD725869960D32CFCC9149F97E6846A845A933EC01` |
| [[Development/Reports/Phase 1L5e Direct Packaged Game Process Fixed Machine Resource Baseline]] | `4,768` | `EC84FD9FDAB8AF48D6062CE54C8D67E86D929128AE5F945A0FD3272F4CFAEE3C` |

The retained Phase 1L.5e result is `BASELINE_RETAINED` and product `PASS` for one current machine only: direct game PID custody, operating-system exit `0`, route `11/11`, and `158` samples with `0` errors. The retained canonical ledger is package `50` files / `1,051,962,028` bytes / Python `0`; game SHA-256 `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A`; UFS SHA-256 `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356`; protected map SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`; and manifest `20` rows with missing `0` / mismatch `0`. No package or UFS rebuild occurred.

## Exact 16-row inventory

| # | Surface | Status | Exact raw value | Precise evidence and bounded meaning | Candidate-B relevance | Remaining proof or owner decision |
|---:|---|---|---|---|---|---|
| 1 | Default graphics RHI | `CONFIG_EXPLICIT_VALUE` | `DefaultGraphicsRHI=DefaultGraphicsRHI_DX12` twice identically | `DefaultEngine.ini:35-36`; same-value duplicate, not a conflict; config default is DX12. | Aligns with B's DX12-class posture but proves neither DX12 Ultimate nor representative compatibility. | Owner defines B API/feature policy; representative run logs it. |
| 2 | D3D12 targeted shader format | `CONFIG_EXPLICIT_VALUE` | `-D3D12TargetedShaderFormats=PCD3D_SM5`; `+D3D12TargetedShaderFormats=PCD3D_SM6` | `DefaultEngine.ini:37-38`; PCD3D_SM6 cook/build target, not runtime Direct3D feature-level or DX12-Ultimate proof. | Relevant only as current build configuration. | Representative B system loads the hash-locked package and logs actual RHI, feature, and shader support. |
| 3 | D3D11 fallback target | `CONFIG_EXPLICIT_VALUE` | `-D3D11TargetedShaderFormats=PCD3D_SM5`; `+D3D11TargetedShaderFormats=PCD3D_SM5` | `DefaultEngine.ini:39-40`; D3D11 SM5 build/fallback target only; no evidence that D3D11 ran. | Does not validate B's DX12 target or fallback performance. | Owner decides whether D3D11 remains supported; any fallback claim needs a separately authorized run. |
| 4 | Runtime-observed RHI | `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | `Using Default RHI: D3D12`; `Loading RHI module D3D12RHI`; metadata `rhiname="D3D12"` | `route.log:623-646,683-689,750-753`; the retained current machine ran D3D12. | Confirms only the current RTX 4070 Laptop path, not B or RX 6600. | Repeat the exact envelope on representative B hardware with retained runtime log. |
| 5 | Runtime adapter / vendor / device | `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | Adapter 0 `NVIDIA GeForce RTX 4070 Laptop GPU`; VendorId `10de`; DeviceId `2820`; dedicated video memory `7948MB`; `Chosen D3D12 Adapter Id = 0` | `route.log:628-645,697-703`; exact selected current-machine adapter identity. | It is not B's RX 6600 example and cannot substitute for it. | Owner selects a representative complete B system; proof logs adapter, VRAM, and driver. |
| 6 | Runtime Direct3D feature level | `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | Chosen adapter capability `Max supported Feature Level 12_2`; chosen adapter 0; D3D12 RHI accepted | `route.log:628-646`; current adapter maximum only. | B remains `OWNER_UNSET / UNVERIFIED`; this machine cannot choose B's feature level. | Owner sets the exact B feature level; representative system queries, logs, and satisfies it. |
| 7 | Runtime shader model | `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | Chosen adapter `shader model 6.7`; metadata `rhifeaturelevel="SM6"`; `shaderplatform="PCD3D_SM6"` | `route.log:629,646,752-753`; current adapter/runtime facts only. | Does not prove B's named hardware supports the required runtime path. | Owner sets the requirement; representative B proof logs the same markers. |
| 8 | Dynamic GI method / Lumen | `CONFIG_EXPLICIT_VALUE` | `r.DynamicGlobalIlluminationMethod=1`; retained log also applies `r.Lumen.DiffuseIndirect.Allow:1` | `DefaultEngine.ini:14`; `route.log:478,482`; raw value `1` remains undecoded because no authoritative enum mapping was fetched; no active rendered-output claim. | GI choice materially affects B cost, but supplies no B validation. | Owner decides the required GI method; authoritative mapping and representative visible measurement remain required. |
| 9 | Reflection method / Lumen | `CONFIG_EXPLICIT_VALUE` | `r.ReflectionMethod=1`; retained log also applies `r.Lumen.Reflections.Allow:1` | `DefaultEngine.ini:16`; `route.log:523,526`; raw value `1` remains undecoded; no visible-reflection claim. | Reflection choice materially affects B cost. | Owner decides the method; authoritative mapping and representative visible proof remain required. |
| 10 | Virtual Shadow Maps | `CONFIG_EXPLICIT_ENABLED` | `r.Shadow.Virtual.Enable=1`; same CVar applied as `1` in retained log | `DefaultEngine.ini:10`; `route.log:380`; exact named enable CVar, not image-quality or performance proof. | Must be included in B's envelope if retained. | Owner confirms policy; representative B run proves compatibility and performance with the exact setting. |
| 11 | Hardware ray tracing | `CONFIG_EXPLICIT_DISABLED` | `r.RayTracing=False`; `r.RayTracing.RayTracingProxies.ProjectEnabled=False` | `DefaultEngine.ini:20,22`; `route.log:728` only reports current-adapter RT tier 1.1 support; support is not use and does not conflict with project disablement. | B has no proved hardware-RT runtime requirement; no broader feature promise follows. | Owner confirms disabled policy; representative proof preserves exact config. |
| 12 | Nanite | `UNPROVEN` | No explicit Nanite enable/use key; retained log only has `r.Nanite.Streaming.ReservedResources:1` | Allowlisted config absence; `route.log:354`; reserved resources do not prove Nanite enabled, used by content, or rendered; absence is not disabled. | B cost and compatibility cannot assume Nanite on or off. | Owner decides Nanite policy; inventory relevant content and log/render the representative scene before a claim. |
| 13 | Anti-aliasing / upscaler | `UNSET_DEFAULT_DEPENDENT` | No explicit project selector; runtime profile applies `AntiAliasingQuality@3`, `r.TemporalAA.Quality=2`, TSR quality CVars, and `r.Upscale.Quality=3` | Allowlisted config absence; `route.log:431-438,549`; quality CVars do not prove selected visible method or screen-percentage policy. | B image quality and performance depend on the method. | Owner sets exact method, upscaler, and screen-percentage contract; representative visible run logs effective values. |
| 14 | VSync / frame cap | `UNSET_DEFAULT_DEPENDENT` | No `r.VSync`, `t.MaxFPS`, fixed-frame-rate, smooth-frame-rate, or frame-limit marker | Allowlisted config/log absence; absence is not disabled and effective behavior may depend on engine or user defaults. | B FPS/frame-time interpretation is unavailable without this custody. | Owner sets VSync/cap policy; proof logs effective values before measurement. |
| 15 | Resolution / screen percentage | `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | `-ResX=1280 -ResY=720 -RenderOffScreen`; metadata `resx="1280"`, `resy="720"`; no screen-percentage marker | `route.log:28,45-46,292`; retained off-screen process requested 1280x720; screen percentage remains unproven. | Not B's visible 1920x1080 Medium envelope; proves no FPS, GPU, VRAM, quality, compatibility, or B validation. | Representative visible B run sets and logs 1920x1080 and exact screen percentage. |
| 16 | Scalability / preset | `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | `DefaultGraphicsPerformance=Maximum`; `AppliedDefaultGraphicsPerformance=Maximum`; runtime applies ViewDistance, AA, Shadow, GI, Reflection, Post, Texture, Effects, Foliage, Shading, and Landscape `Quality@3` groups | `DefaultEngine.ini:75-76`; `route.log:428-623`; raw project/runtime tier facts only; no authoritative `@3` label decode or visible preset proof. | Cannot claim B Medium; off-screen 1280x720 is not B validation. | Owner fixes exact B preset and CVars; representative visible proof logs all effective groups and metrics. |

## Classification totals and truth rules

| Status | Count |
|---|---:|
| `CONFIG_EXPLICIT_VALUE` | `5` |
| `CONFIG_EXPLICIT_ENABLED` | `1` |
| `CONFIG_EXPLICIT_DISABLED` | `1` |
| `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY` | `6` |
| `UNSET_DEFAULT_DEPENDENT` | `2` |
| `UNPROVEN` | `1` |
| **Total** | **`16`** |

- The identical duplicate `DefaultGraphicsRHI_DX12` values are not a conflict.
- D3D11 SM5 is a fallback/build target, not runtime evidence.
- PCD3D_SM6 targeting is not runtime feature-level or DX12-Ultimate proof.
- Raw GI and reflection values `1` remain raw without authoritative enum mapping.
- Absence is never converted to disabled.
- `-RenderOffScreen -ResX=1280 -ResY=720` proves no visible preset, FPS, GPU, VRAM, quality, compatibility, or B validation.
- Current-machine runtime evidence cannot choose candidate B's Direct3D feature level.

## Boundary and next gate

No runtime, test, source, config, package, map, route, gameplay, art, accessibility, input, brain, procurement, machine acquisition, performance promise, minimum-PC validation, readiness, release, DEC, or Notion work occurred. Phase 1K remains incomplete and not waived. Music and Phase 1L exit remain incomplete. Phase 1M, roadmap Phase 2, Version 1, Phase `5/6`, beta readiness, production readiness, and release remain unauthorized.

Any later validation requires this phase's local documentation commit and a fresh Scope Director gate. The owner must then set the exact feature level, rendering policy, visible 1920x1080 Medium envelope, screen percentage, VSync/frame cap, and acceptance custody before representative candidate-B evidence can begin.
