# Phase 1L.5i Current AA, Upscaling, Medium-Profile, and Frame-Control Evidence Inventory

Date: 2026-08-14
Status: `EVIDENCE_INVENTORY_COMPLETE — EFFECTIVE VALUES AND OWNER POLICY UNPROVEN`

## Scope

This read-only inventory records the current project, retained Phase 1L.5e current-machine evidence, and installed Unreal Engine 5.8 default/reference evidence for six unresolved rendering controls. It does not select a value, change configuration, launch the product, measure performance, validate Candidate B, or grant compatibility or readiness credit.

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`. Policy-selection count remains `1`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Source custody

| Source | Bytes | SHA-256 | Use |
| --- | ---: | --- | --- |
| `client/OddsWell/Config/DefaultEngine.ini` | `2,755` | `1442E7ADF71B4028993465D95A92C12C9FB8E39D0DA4AC77229C6B920E38F6D1` | project settings and explicit-selector absence |
| `client/OddsWell/Config/DefaultGame.ini` | `675` | `CE966B4DEF240A9F99712BBF79BD1F9832125D4251FCEFB60498458523F86048` | project setting absence |
| `client/OddsWell/OddsWell.uproject` | `190` | `020234D58303E8D98C9E1D83B683F4F8F7889383932F069640E3284EBD2FEE18` | UE `5.8` association at line `3` |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Evidence/route.log` | `96,908` | `4576B02AAD4D51A6E0F8F416ACB4181CF61AED38412FCE0BD1A4F4E851647347` | retained current-machine runtime markers and absences |
| `client/OddsWell/Saved/Phase1L5e-20260814T030752Z/Profile/Saved/Config/Windows/GameUserSettings.ini` | `1,378` | `25034567F71ECEC90A640FA803A6BB0292EC483021905251EC22F55C8B4AA91B` | retained saved profile state, not effective runtime proof |
| `C:/Program Files/Epic Games/UE_5.8/Engine/Config/BaseScalability.ini` | `40,197` | `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6` | authoritative installed scalability reference |
| `C:/Program Files/Epic Games/UE_5.8/Engine/Config/BaseEngine.ini` | `265,467` | `DC5B359EE95CCFF0CCDFA4181B2875451B4A33474C0BB896FD8FEF23AED1BF8E` | exclusion custody: line `2481` is editor-only VSync state |
| `Engine/Source/Runtime/Engine/Private/SceneView.cpp` | local UE 5.8 | `8EE3DE0DED7B6454FC814E5F7357D48D989116B79AC2EF61972585A4BD1D9FD0` | AA default and override semantics, lines `235-246` |
| `Engine/Source/Runtime/Engine/Classes/Engine/RendererSettings.h` | local UE 5.8 | `A036AB5E245439BFED962FDF9A6EA510DE2E1DAA3704976593A150DCFC45F8DF` | AA project-setting binding, lines `862-866` |
| `Engine/Source/Runtime/Engine/Public/SceneUtils.h` | local UE 5.8 | `0922FE32369AAE3BA229FAA317523055DC29B64C33D7120E05CE5A54D116E57C` | AA enum names, lines `42-53` |
| `Engine/Source/Runtime/Renderer/Private/PostProcess/TemporalAA.cpp` | local UE 5.8 | `7A51D1D87094E07DA4FE87C5761A2967B33464C36BB9B04D4A30C4C3F5F9F756` | upscaler selector default and override, lines `61-67` |
| `Engine/Source/Runtime/Engine/Private/LegacyScreenPercentageDriver.cpp` | local UE 5.8 | `88AF2DE2E4182BF9134F73CF6B8310A36DFCDA3B49B927CAA5B49E081E4803EC` | screen-percentage default chain, lines `12-43` |
| `Engine/Source/Runtime/Core/Private/HAL/ConsoleManager.cpp` | local UE 5.8 | `BF8B60A73A3F4FE767B70444D4530B8DE0007A1D25EE99B615D8318F4B6022DD` | VSync CVar default, lines `4329-4334` |
| `Engine/Source/Runtime/Engine/Private/UnrealEngine.cpp` | local UE 5.8 | `A856525BD245039126444FF9978C1BF68FFADD76AEAF340B01DA30D608AF84BF` | frame-cap CVar default, lines `12136-12138` |
| `Engine/Source/Runtime/Engine/Private/GameUserSettings.cpp` | local UE 5.8 | `C9C677113E8DE4A93C7F3644E5914B3F5623D26555282C4B619EDA6445DACFC4` | user override paths, lines `287-303`, `413-429`, and `506-537` |
| [[Development/Reports/Phase 1L5e Direct Packaged Game Process Fixed Machine Resource Baseline]] | `4,768` | `EC84FD9FDAB8AF48D6062CE54C8D67E86D929128AE5F945A0FD3272F4CFAEE3C` | retained-run boundary |
| [[Development/Reports/Phase 1L5g Current Packaged Rendering API and Feature Evidence Inventory]] | `12,126` | `0362271E3CE7AD2F0C1F62A5C798F742A4A3C108959D952B4A8EAF13895B37A3` | prior rendering inventory |
| [[Development/Reports/Phase 1L5h Current GI and Reflection Raw Value Decode and Six Phase Batch Closeout Audit]] | `8,010` | `FCAB680AAF340247B05839A40A3D4F63B13C4D48643C866144289CB34649DE86` | current-config mapping and unresolved-policy boundary |

## Six-row evidence inventory

Allowed row statuses are `PROJECT_EXPLICIT_VALUE`, `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY`, `ENGINE_DEFAULT_REFERENCE_ONLY`, `SCALABILITY_PROFILE_REFERENCE_ONLY`, and `UNPROVEN_EFFECTIVE_VALUE`.

| # | Control | Status | Project explicit value or absence | Retained runtime marker or absence | Authoritative default/reference and override risk | Candidate B relevance and remaining proof |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `AA method` | `ENGINE_DEFAULT_REFERENCE_ONLY` | No `r.AntiAliasingMethod` or explicit method selector in the allowlisted project sources. | Exact effective marker absent. `route.log:431-440` applies `AntiAliasingQuality@3` and TAA/TSR quality CVars; these do not select a method. | `SceneView.cpp:235-246` defines raw default `4` as TSR and says post-process volume, camera, or game settings may override. `RendererSettings.h:862-866` binds the project setting; `SceneUtils.h:42-53` supplies enum names. Default is reference only; the effective visible method is unproven. | AA materially affects 1080p60 quality and performance. Owner must select the B method; a representative visible B run must retain the effective method/CVar and output. |
| 2 | `upscaler` | `ENGINE_DEFAULT_REFERENCE_ONLY` | No `r.TemporalAA.Upscaler` or explicit upscaler selector. | Exact marker absent. `route.log:434-440` TSR quality CVars and `route.log:549` `r.Upscale.Quality=3` do not identify the selected upscaler. | `TemporalAA.cpp:61-67` defines `r.TemporalAA.Upscaler=1` as `GTemporalUpscaler` and says a third-party plugin may override it. Selector default is reference only; effective algorithm/plugin is unproven. | Owner must select the B method/upscaler pairing; representative visible B proof must log the effective implementation and selector. |
| 3 | `screen percentage` | `ENGINE_DEFAULT_REFERENCE_ONLY` | No `r.ScreenPercentage` or explicit screen-percentage contract. | Exact marker absent. `route.log:28,292` off-screen `1280x720` is output/window custody only; `route.log:435` `r.TSR.History.ScreenPercentage=200` is history resolution, not primary screen percentage. Saved `sg.ResolutionQuality=0` at `GameUserSettings.ini:3` is not an effective runtime marker. | `LegacyScreenPercentageDriver.cpp:12-43` defines `r.ScreenPercentage.Default=100`, desktop mode `BasedOnDisplayResolution`, and `r.ScreenPercentage=0`, where non-positive delegates to default CVars. `BaseScalability.ini:10-11,36-42` maps ResolutionQuality directly to `r.ScreenPercentage` and makes preset `Default` use the project's default. References do not resolve one effective visible value; scalability, user, post-process, or dynamic-resolution state may override. | B needs explicit 1920x1080 Medium screen-percentage custody. Owner must select it; representative visible B proof must log both resolution and effective percentage. |
| 4 | `visible Medium scalability profile` | `SCALABILITY_PROFILE_REFERENCE_ONLY` | No explicit Medium selection. `DefaultEngine.ini:72-76` records `DefaultGraphicsPerformance=Maximum` and applied Maximum, not B Medium. | `route.log:428-623` applies eleven `Quality@3` groups; saved profile `GameUserSettings.ini:4-14` is also all `3`. Neither proves visible Medium/@1, and the run was off-screen 1280x720. | The installed @1 appendix below is reference only. Ten named @1 sections exist; `[LandscapeQuality@1]` is absent. Project, DeviceProfile, user, command-line, and runtime scalability may override. Effective B values are unproven. | Owner must freeze the complete B Medium CVar contract, including Landscape handling; representative visible B proof must retain all effective groups. |
| 5 | `VSync` | `ENGINE_DEFAULT_REFERENCE_ONLY` | No explicit packaged-game `r.VSync` policy. `BaseEngine.ini:2481 r.VSync=0` is under `[SystemSettingsEditor]` and is excluded from packaged-game proof. | Exact route marker absent. Saved profile `bUseVSync=False` at `GameUserSettings.ini:17` is not an effective runtime CVar marker. | `ConsoleManager.cpp:4329-4334` defines the engine CVar default `0`. `GameUserSettings.cpp:506-530` shows system or game settings can set it. Default/profile false is not effective packaged behavior proof. | VSync changes FPS/frame-time interpretation. Owner must select the policy; representative B proof must log effective `r.VSync` before measurement. |
| 6 | `frame cap` | `ENGINE_DEFAULT_REFERENCE_ONLY` | No explicit `t.MaxFPS`, fixed/smoothed-frame-rate, or frame-limit policy. | Exact route marker absent. Saved `FrameRateLimit=0.000000` at `GameUserSettings.ini:33` is not an effective runtime CVar marker. | `UnrealEngine.cpp:12136-12138` defines `t.MaxFPS=0`, with non-positive meaning uncapped. `GameUserSettings.cpp:287-303,413-429,506-537` shows saved/default state and the `SetMaxFPS` override path. Default is reference only; effective cap is unproven. | The cap affects the 60-FPS target and metrics. Owner must select it; representative B proof must log effective frame-limit state before measurement. |

Status totals: `ENGINE_DEFAULT_REFERENCE_ONLY=5`; `SCALABILITY_PROFILE_REFERENCE_ONLY=1`; `PROJECT_EXPLICIT_VALUE=0`; `RUNTIME_LOG_EVIDENCED_CURRENT_MACHINE_ONLY=0`; `UNPROVEN_EFFECTIVE_VALUE=0`. The selected status records the strongest available evidence class; the effective value remains explicitly unproven in every row.

## Exact installed Medium/@1 reference appendix

All values below are verbatim live assignments from installed `BaseScalability.ini`, SHA-256 `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6`. This is an engine reference, not a selected or effective project profile. There are `11` ordered groups, `10` present sections, `1` absent section, and `154` live assignments.

### 1. ViewDistance — lines 114-116 — 2 assignments

```ini
r.SkeletalMeshLODBias=1
r.ViewDistanceScale=0.6
```

### 2. AntiAliasing — lines 63-72 — 9 assignments

```ini
r.FXAA.Quality=1
r.TemporalAA.Quality=1
r.TSR.History.R11G11B10=1
r.TSR.History.ScreenPercentage=100
r.TSR.History.UpdateQuality=1
r.TSR.ShadingRejection.Flickering=0
r.TSR.RejectionAntiAliasingQuality=1
r.TSR.ReprojectionField=0
r.TSR.Resurrection=1
```

### 3. Shadow — lines 167-200 — 33 assignments

```ini
r.LightFunctionQuality=1
r.ShadowQuality=3
r.Shadow.CSM.MaxCascades=1
r.Shadow.MaxResolution=1024
r.Shadow.MaxCSMResolution=1024
r.Shadow.RadiusThreshold=0.05
r.Shadow.DistanceScale=0.7
r.Shadow.CSM.TransitionScale=0.25
r.Shadow.PreShadowResolutionFactor=0.5
r.DistanceFieldShadowing=0
r.VolumetricFog=0
r.LightMaxDrawDistanceScale=0.5
r.CapsuleShadows=1
r.Shadow.Virtual.MaxPhysicalPages=512
r.Shadow.Virtual.ResolutionLodBiasDirectional=0.0
r.Shadow.Virtual.ResolutionLodBiasDirectionalMoving=0.0
r.Shadow.Virtual.ResolutionLodBiasLocal=1.0
r.Shadow.Virtual.ResolutionLodBiasLocalMoving=2.0
r.Shadow.Virtual.SMRT.RayCountDirectional=4
r.Shadow.Virtual.SMRT.SamplesPerRayDirectional=2
r.Shadow.Virtual.SMRT.RayCountLocal=4
r.Shadow.Virtual.SMRT.SamplesPerRayLocal=2
r.Shadow.Virtual.MarkCoarsePagesLocal=2
r.MegaLights.NumSamplesPerPixel=2
r.MegaLights.DownsampleMode=2
r.MegaLights.ScreenTraces.Quality=0
r.MegaLights.FrontLayerTranslucency.Allow=0
r.MegaLights.FrontLayerTranslucency.SpecularOnly=1
r.MegaLights.FrontLayerTranslucency.SoftShadows=0
r.MegaLights.FrontLayerTranslucency.TexturedRectLights=0
r.MegaLights.Spatial.UseHistorySpatialVariance=0
r.MegaLights.Volume.GridPixelSize=16
r.MegaLights.Volume.GridSizeZ=64
```

### 4. GlobalIllumination — lines 326-367 — 33 assignments

```ini
r.DistanceFieldAO=1
r.SkylightIntensityMultiplier=1.0
r.AOQuality=1
r.Lumen.DiffuseIndirect.Allow=1
r.Lumen.FinalGatherMethod=0
r.LumenScene.SurfaceCache.AtlasSize=2048
r.LumenScene.SurfaceCache.CardTexelDensityScale=50
r.LumenScene.SurfaceCache.CardMinResolution=2
r.LumenScene.SurfaceCache.CardMaxResolution=256
r.LumenScene.DirectLighting.MaxLightsPerTile=4
r.LumenScene.DirectLighting.UpdateFactor=128
r.LumenScene.Radiosity.UpdateFactor=128
r.LumenScene.Radiosity.ProbeSpacing=4
r.LumenScene.Radiosity.HemisphereProbeResolution=3
r.Lumen.TraceMeshSDFs.Allow=0
r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor=1
r.Lumen.ScreenProbeGather.ShortRangeAO.HorizonSearch.SliceCount=1
r.Lumen.ScreenProbeGather.ShortRangeAO.BentNormal=0
r.Lumen.ScreenProbeGather.ShortRangeAO.HorizonSearch.HZB=1
r.Lumen.ScreenProbeGather.ShortRangeAO.HorizonSearch.ForegroundSampleRejectPower=1.5
r.Lumen.ScreenProbeGather.ShortRangeAO.FoliageOcclusionStrength=1
r.Lumen.TranslucencyVolume.GridPixelSize=128
r.Lumen.TranslucencyVolume.TraceFromVolume=0
r.Lumen.TranslucencyVolume.ShareRadianceCacheWithOpaque=1
r.Lumen.TranslucencyVolume.SpatialFilter=0
r.Lumen.TranslucencyVolume.RadianceCache.ProbeResolution=8
r.Lumen.TranslucencyVolume.RadianceCache.GridResolution=12
r.Lumen.TranslucencyVolume.RadianceCache.NumProbesToTraceBudget=30
r.Lumen.HardwareRayTracing.HitLighting.Allowed=0
r.RayTracing.Scene.BuildMode=0
r.RayTracing.Geometry.SkeletalMeshes=0
r.MeshCardRepresentation.SkeletalMesh=0
r.RayTracing.DynamicGeometry.MaxUpdatePrimitivesPerFrame=1000
```

### 5. Reflection — lines 519-522 — 3 assignments

```ini
r.SSR.Quality=2
r.SSR.HalfResSceneColor=1
r.Lumen.Reflections.Allow=0
```

### 6. PostProcess — lines 586-619 — 31 assignments

```ini
r.MotionBlurQuality=3
r.MotionBlur.HalfResGather=1
r.AmbientOcclusionMipLevelFactor=1.0
r.AmbientOcclusionMaxQuality=60
r.AmbientOcclusionLevels=-1
r.AmbientOcclusionRadiusScale=1.5
r.DepthOfFieldQuality=1
r.RenderTargetPoolMin=350
r.LensFlareQuality=0
r.SceneColorFringeQuality=0
r.EyeAdaptationQuality=2
r.BloomQuality=4
r.Bloom.ScreenPercentage=35.355
r.FastBlurThreshold=2
r.Upscale.Quality=2
r.LightShaftQuality=0
r.Filter.SizeScale=0.7
r.LUT.Shaper=0
r.LUT.Size=32
r.Tonemapper.Quality=2
r.DOF.Gather.ResolutionDivisor=2
r.DOF.Gather.AccumulatorQuality=0
r.DOF.Gather.PostfilterMethod=2
r.DOF.Gather.EnableBokehSettings=0
r.DOF.Gather.RingCount=3
r.DOF.Scatter.ForegroundCompositing=0
r.DOF.Scatter.BackgroundCompositing=0
r.DOF.Recombine.Quality=0
r.DOF.TemporalAAQuality=0
r.DOF.Kernel.MaxForegroundRadius=0.006
r.DOF.Kernel.MaxBackgroundRadius=0.006
```

### 7. Texture — lines 752-761 — 9 assignments

```ini
r.Streaming.MipBias=1
r.Streaming.AmortizeCPUToGPUCopy=0
r.Streaming.MaxNumTexturesToStreamPerFrame=0
r.Streaming.Boost=1
r.MaxAnisotropy=2
r.VT.MaxAnisotropy=4
r.Streaming.LimitPoolSizeToVRAM=1
r.Streaming.PoolSize=600
r.Streaming.MaxEffectiveScreenSize=0
```

### 8. Effects — lines 827-854 — 27 assignments

```ini
r.TranslucencyLightingVolume.Dim=32
r.RefractionQuality=0
r.SceneColorFormat=3
r.DetailMode=1
r.TranslucencyLightingVolume.Blur=0
r.MaterialQualityLevel=2
r.SSS.Scale=0.75
r.SSS.SampleSet=0
r.SSS.Quality=0
r.SSS.HalfRes=1
r.SSGI.Quality=1
r.EmitterSpawnRateScale=0.25
r.ParticleLightQuality=0
r.SkyAtmosphere.AerialPerspectiveLUT.FastApplyOnOpaque=1
r.SkyAtmosphere.AerialPerspectiveLUT.SampleCountMaxPerSlice=1
r.SkyAtmosphere.AerialPerspectiveLUT.DepthResolution=16.0
r.SkyAtmosphere.FastSkyLUT=1
r.SkyAtmosphere.FastSkyLUT.SampleCountMin=4.0
r.SkyAtmosphere.FastSkyLUT.SampleCountMax=32.0
r.SkyAtmosphere.SampleCountMin=4.0
r.SkyAtmosphere.SampleCountMax=32.0
r.SkyAtmosphere.TransmittanceLUT.UseSmallFormat=0
r.SkyAtmosphere.TransmittanceLUT.SampleCount=10.0
r.SkyAtmosphere.MultiScatteringLUT.SampleCount=15.0
r.Fog.SeparateComposition=0
fx.Niagara.QualityLevel=1
r.HeterogeneousVolumes.Allowed=0
```

### 9. Foliage — lines 972-975 — 3 assignments

```ini
foliage.DensityScale=0.4
grass.DensityScale=0.4
pcg.Quality=1
```

`BaseScalability.ini:976-978` contains commented examples only; they confer no values.

### 10. Shading — lines 1012-1016 — 4 assignments

```ini
r.HairStrands.SkyLighting.IntegrationType=2
r.HairStrands.SkyAO.SampleCount=4
r.HairStrands.Visibility.MSAA.SamplePerPixel=1
r.AnisotropicMaterials=0
```

### 11. Landscape — absent — 0 assignments

Exact full-file search finds no `[LandscapeQuality@1]` section in the installed authoritative file. No Landscape @1 value is inferred or invented. Retained `route.log:622` applies `[LandscapeQuality@3]` only; it is neither an @1 reference nor Candidate B proof.

## Non-inference and open-policy boundary

- Engine defaults and scalability sections are references, not project selection or effective state.
- TAA/TSR quality CVars do not prove the selected AA method or upscaler.
- Off-screen 1280x720 does not prove screen percentage, visible Medium, FPS, quality, compatibility, or readiness.
- Current-machine/runtime/profile `@3` does not prove Medium/@1.
- Engine VSync and frame-cap defaults, and retained saved-profile values, do not prove effective packaged behavior.
- The appendix does not select an owner policy, define final B settings, prove compatibility, measure performance, or support a readiness claim.

[[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]] remains unchanged. Its eight unresolved items remain exactly, and in order:

1. `GI method/raw mapping`
2. `reflection method/raw mapping`
3. `AA method`
4. `upscaler`
5. `screen percentage`
6. `exact visible Medium scalability CVars`
7. `VSync`
8. `frame cap`

Phase 1L.5h's authoritative current-config mappings do not close those owner-policy items. A future owner gate must select the six controls and the GI/reflection policy; only a later, separately authorized representative visible Candidate B run may provide effective-setting, performance, minimum-PC, compatibility, or readiness evidence.
