#if UE_BUILD_DEVELOPMENT

#include "CandidateBPolicySmoke.h"

#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformMisc.h"
#include "Misc/App.h"
#include "Misc/Parse.h"
#include "RHI.h"
#include "RHIStrings.h"
#include "TimerManager.h"
#include "UnrealClient.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogCandidateBPolicySmoke, Log, All);

namespace
{
bool IsCandidateBTargetWorldPackage(const FString& WorldPackageName)
{
	return WorldPackageName.Equals(TEXT("/Game/Maps/SundaleGraybox"), ESearchCase::CaseSensitive);
}

enum class EPolicyRegistryKind : uint8
{
	Selector,
	Child,
	Control,
};

enum class EPolicyValueType : uint8
{
	Integer,
	Float,
};

struct FPolicyRegistryRow
{
	EPolicyRegistryKind Kind;
	EPolicyValueType Type;
	const TCHAR* Name;
	const TCHAR* SourceSection;
	int64 IntegerValue;
	double FloatValue;
};

static constexpr TCHAR CandidateBBaseScalabilitySha256[] =
	TEXT("579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6");

#define POLICY_SELECTOR(Name, Value) \
	{EPolicyRegistryKind::Selector, EPolicyValueType::Integer, TEXT(Name), nullptr, Value, 0.0}
#define POLICY_CHILD_INT(Section, Name, Value) \
	{EPolicyRegistryKind::Child, EPolicyValueType::Integer, TEXT(Name), TEXT(Section), Value, 0.0}
#define POLICY_CHILD_FLOAT(Section, Name, Value) \
	{EPolicyRegistryKind::Child, EPolicyValueType::Float, TEXT(Name), TEXT(Section), 0, Value}
#define POLICY_CONTROL_INT(Name, Value) \
	{EPolicyRegistryKind::Control, EPolicyValueType::Integer, TEXT(Name), nullptr, Value, 0.0}

static constexpr FPolicyRegistryRow CandidateBPolicyRegistry[] = {
	POLICY_SELECTOR("sg.ViewDistanceQuality", 1),
	POLICY_SELECTOR("sg.AntiAliasingQuality", 1),
	POLICY_SELECTOR("sg.ShadowQuality", 1),
	POLICY_SELECTOR("sg.GlobalIlluminationQuality", 1),
	POLICY_SELECTOR("sg.ReflectionQuality", 1),
	POLICY_SELECTOR("sg.PostProcessQuality", 1),
	POLICY_SELECTOR("sg.TextureQuality", 1),
	POLICY_SELECTOR("sg.EffectsQuality", 1),
	POLICY_SELECTOR("sg.FoliageQuality", 1),
	POLICY_SELECTOR("sg.ShadingQuality", 1),
	POLICY_SELECTOR("sg.LandscapeQuality", 1),

	POLICY_CHILD_INT("ViewDistanceQuality@1", "r.SkeletalMeshLODBias", 1),
	POLICY_CHILD_FLOAT("ViewDistanceQuality@1", "r.ViewDistanceScale", 0.6),

	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.FXAA.Quality", 1),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TemporalAA.Quality", 1),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.History.R11G11B10", 1),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.History.ScreenPercentage", 100),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.History.UpdateQuality", 1),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.ShadingRejection.Flickering", 0),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.RejectionAntiAliasingQuality", 1),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.ReprojectionField", 0),
	POLICY_CHILD_INT("AntiAliasingQuality@1", "r.TSR.Resurrection", 1),

	POLICY_CHILD_INT("ShadowQuality@1", "r.LightFunctionQuality", 1),
	POLICY_CHILD_INT("ShadowQuality@1", "r.ShadowQuality", 3),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.CSM.MaxCascades", 1),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.MaxResolution", 1024),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.MaxCSMResolution", 1024),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.RadiusThreshold", 0.05),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.DistanceScale", 0.7),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.CSM.TransitionScale", 0.25),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.PreShadowResolutionFactor", 0.5),
	POLICY_CHILD_INT("ShadowQuality@1", "r.DistanceFieldShadowing", 0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.VolumetricFog", 0),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.LightMaxDrawDistanceScale", 0.5),
	POLICY_CHILD_INT("ShadowQuality@1", "r.CapsuleShadows", 1),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.Virtual.MaxPhysicalPages", 512),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.Virtual.ResolutionLodBiasDirectional", 0.0),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.Virtual.ResolutionLodBiasDirectionalMoving", 0.0),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.Virtual.ResolutionLodBiasLocal", 1.0),
	POLICY_CHILD_FLOAT("ShadowQuality@1", "r.Shadow.Virtual.ResolutionLodBiasLocalMoving", 2.0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.Virtual.SMRT.RayCountDirectional", 4),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.Virtual.SMRT.SamplesPerRayDirectional", 2),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.Virtual.SMRT.RayCountLocal", 4),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.Virtual.SMRT.SamplesPerRayLocal", 2),
	POLICY_CHILD_INT("ShadowQuality@1", "r.Shadow.Virtual.MarkCoarsePagesLocal", 2),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.NumSamplesPerPixel", 2),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.DownsampleMode", 2),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.ScreenTraces.Quality", 0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.FrontLayerTranslucency.Allow", 0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.FrontLayerTranslucency.SpecularOnly", 1),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.FrontLayerTranslucency.SoftShadows", 0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.FrontLayerTranslucency.TexturedRectLights", 0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.Spatial.UseHistorySpatialVariance", 0),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.Volume.GridPixelSize", 16),
	POLICY_CHILD_INT("ShadowQuality@1", "r.MegaLights.Volume.GridSizeZ", 64),

	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.DistanceFieldAO", 1),
	POLICY_CHILD_FLOAT("GlobalIlluminationQuality@1", "r.SkylightIntensityMultiplier", 1.0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.AOQuality", 1),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.DiffuseIndirect.Allow", 1),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.FinalGatherMethod", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.SurfaceCache.AtlasSize", 2048),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.SurfaceCache.CardTexelDensityScale", 50),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.SurfaceCache.CardMinResolution", 2),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.SurfaceCache.CardMaxResolution", 256),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.DirectLighting.MaxLightsPerTile", 4),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.DirectLighting.UpdateFactor", 128),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.Radiosity.UpdateFactor", 128),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.Radiosity.ProbeSpacing", 4),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.LumenScene.Radiosity.HemisphereProbeResolution", 3),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TraceMeshSDFs.Allow", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.ScreenProbeGather.ShortRangeAO.DownsampleFactor", 1),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.ScreenProbeGather.ShortRangeAO.HorizonSearch.SliceCount", 1),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.ScreenProbeGather.ShortRangeAO.BentNormal", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.ScreenProbeGather.ShortRangeAO.HorizonSearch.HZB", 1),
	POLICY_CHILD_FLOAT("GlobalIlluminationQuality@1", "r.Lumen.ScreenProbeGather.ShortRangeAO.HorizonSearch.ForegroundSampleRejectPower", 1.5),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.ScreenProbeGather.ShortRangeAO.FoliageOcclusionStrength", 1),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.GridPixelSize", 128),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.TraceFromVolume", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.ShareRadianceCacheWithOpaque", 1),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.SpatialFilter", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.RadianceCache.ProbeResolution", 8),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.RadianceCache.GridResolution", 12),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.TranslucencyVolume.RadianceCache.NumProbesToTraceBudget", 30),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.Lumen.HardwareRayTracing.HitLighting.Allowed", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.RayTracing.Scene.BuildMode", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.RayTracing.Geometry.SkeletalMeshes", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.MeshCardRepresentation.SkeletalMesh", 0),
	POLICY_CHILD_INT("GlobalIlluminationQuality@1", "r.RayTracing.DynamicGeometry.MaxUpdatePrimitivesPerFrame", 1000),

	POLICY_CHILD_INT("ReflectionQuality@1", "r.SSR.Quality", 2),
	POLICY_CHILD_INT("ReflectionQuality@1", "r.SSR.HalfResSceneColor", 1),
	POLICY_CHILD_INT("ReflectionQuality@1", "r.Lumen.Reflections.Allow", 0),

	POLICY_CHILD_INT("PostProcessQuality@1", "r.MotionBlurQuality", 3),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.MotionBlur.HalfResGather", 1),
	POLICY_CHILD_FLOAT("PostProcessQuality@1", "r.AmbientOcclusionMipLevelFactor", 1.0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.AmbientOcclusionMaxQuality", 60),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.AmbientOcclusionLevels", -1),
	POLICY_CHILD_FLOAT("PostProcessQuality@1", "r.AmbientOcclusionRadiusScale", 1.5),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DepthOfFieldQuality", 1),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.RenderTargetPoolMin", 350),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.LensFlareQuality", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.SceneColorFringeQuality", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.EyeAdaptationQuality", 2),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.BloomQuality", 4),
	POLICY_CHILD_FLOAT("PostProcessQuality@1", "r.Bloom.ScreenPercentage", 35.355),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.FastBlurThreshold", 2),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.Upscale.Quality", 2),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.LightShaftQuality", 0),
	POLICY_CHILD_FLOAT("PostProcessQuality@1", "r.Filter.SizeScale", 0.7),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.LUT.Shaper", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.LUT.Size", 32),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.Tonemapper.Quality", 2),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Gather.ResolutionDivisor", 2),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Gather.AccumulatorQuality", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Gather.PostfilterMethod", 2),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Gather.EnableBokehSettings", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Gather.RingCount", 3),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Scatter.ForegroundCompositing", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Scatter.BackgroundCompositing", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.Recombine.Quality", 0),
	POLICY_CHILD_INT("PostProcessQuality@1", "r.DOF.TemporalAAQuality", 0),
	POLICY_CHILD_FLOAT("PostProcessQuality@1", "r.DOF.Kernel.MaxForegroundRadius", 0.006),
	POLICY_CHILD_FLOAT("PostProcessQuality@1", "r.DOF.Kernel.MaxBackgroundRadius", 0.006),

	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.MipBias", 1),
	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.AmortizeCPUToGPUCopy", 0),
	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.MaxNumTexturesToStreamPerFrame", 0),
	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.Boost", 1),
	POLICY_CHILD_INT("TextureQuality@1", "r.MaxAnisotropy", 2),
	POLICY_CHILD_INT("TextureQuality@1", "r.VT.MaxAnisotropy", 4),
	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.LimitPoolSizeToVRAM", 1),
	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.PoolSize", 600),
	POLICY_CHILD_INT("TextureQuality@1", "r.Streaming.MaxEffectiveScreenSize", 0),

	POLICY_CHILD_INT("EffectsQuality@1", "r.TranslucencyLightingVolume.Dim", 32),
	POLICY_CHILD_INT("EffectsQuality@1", "r.RefractionQuality", 0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SceneColorFormat", 3),
	POLICY_CHILD_INT("EffectsQuality@1", "r.DetailMode", 1),
	POLICY_CHILD_INT("EffectsQuality@1", "r.TranslucencyLightingVolume.Blur", 0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.MaterialQualityLevel", 2),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SSS.Scale", 0.75),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SSS.SampleSet", 0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SSS.Quality", 0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SSS.HalfRes", 1),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SSGI.Quality", 1),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.EmitterSpawnRateScale", 0.25),
	POLICY_CHILD_INT("EffectsQuality@1", "r.ParticleLightQuality", 0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SkyAtmosphere.AerialPerspectiveLUT.FastApplyOnOpaque", 1),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SkyAtmosphere.AerialPerspectiveLUT.SampleCountMaxPerSlice", 1),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.AerialPerspectiveLUT.DepthResolution", 16.0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SkyAtmosphere.FastSkyLUT", 1),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.FastSkyLUT.SampleCountMin", 4.0),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.FastSkyLUT.SampleCountMax", 32.0),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.SampleCountMin", 4.0),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.SampleCountMax", 32.0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.SkyAtmosphere.TransmittanceLUT.UseSmallFormat", 0),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.TransmittanceLUT.SampleCount", 10.0),
	POLICY_CHILD_FLOAT("EffectsQuality@1", "r.SkyAtmosphere.MultiScatteringLUT.SampleCount", 15.0),
	POLICY_CHILD_INT("EffectsQuality@1", "r.Fog.SeparateComposition", 0),
	POLICY_CHILD_INT("EffectsQuality@1", "fx.Niagara.QualityLevel", 1),
	POLICY_CHILD_INT("EffectsQuality@1", "r.HeterogeneousVolumes.Allowed", 0),

	POLICY_CHILD_FLOAT("FoliageQuality@1", "foliage.DensityScale", 0.4),
	POLICY_CHILD_FLOAT("FoliageQuality@1", "grass.DensityScale", 0.4),
	POLICY_CHILD_INT("FoliageQuality@1", "pcg.Quality", 1),

	POLICY_CHILD_INT("ShadingQuality@1", "r.HairStrands.SkyLighting.IntegrationType", 2),
	POLICY_CHILD_INT("ShadingQuality@1", "r.HairStrands.SkyAO.SampleCount", 4),
	POLICY_CHILD_INT("ShadingQuality@1", "r.HairStrands.Visibility.MSAA.SamplePerPixel", 1),
	POLICY_CHILD_INT("ShadingQuality@1", "r.AnisotropicMaterials", 0),

	POLICY_CONTROL_INT("r.DynamicGlobalIlluminationMethod", 1),
	POLICY_CONTROL_INT("r.ReflectionMethod", 2),
	POLICY_CONTROL_INT("r.AntiAliasingMethod", 4),
	POLICY_CONTROL_INT("r.TemporalAA.Upscaler", 1),
	POLICY_CONTROL_INT("r.ScreenPercentage", 100),
	POLICY_CONTROL_INT("r.DynamicRes.OperationMode", 0),
	POLICY_CONTROL_INT("r.VSync", 0),
	POLICY_CONTROL_INT("t.MaxFPS", 0),
};

#undef POLICY_SELECTOR
#undef POLICY_CHILD_INT
#undef POLICY_CHILD_FLOAT
#undef POLICY_CONTROL_INT

static_assert(UE_ARRAY_COUNT(CandidateBPolicyRegistry) == 173, "Candidate B policy registry must remain exact");

struct FPolicyRegistryView
{
	const FPolicyRegistryRow* Rows;
	int32 Count;
};

FPolicyRegistryView PolicyApplyOrder()
{
	return {CandidateBPolicyRegistry, UE_ARRAY_COUNT(CandidateBPolicyRegistry)};
}

FPolicyRegistryView PolicyEvidenceOrder()
{
	return {CandidateBPolicyRegistry, UE_ARRAY_COUNT(CandidateBPolicyRegistry)};
}

enum class EFieldStatus : uint8
{
	Match,
	Mismatch,
	Missing,
	Ambiguous,
	Unavailable,
};

struct FFieldCounts
{
	int32 Emitted = 0;
	int32 Matches = 0;
	int32 Mismatches = 0;
	int32 Gaps = 0;
};

bool bCandidateWorldClaimed = false;

const TCHAR* KindText(const EPolicyRegistryKind Kind)
{
	switch (Kind)
	{
	case EPolicyRegistryKind::Selector: return TEXT("SELECTOR");
	case EPolicyRegistryKind::Child: return TEXT("CHILD");
	default: return TEXT("CONTROL");
	}
}

const TCHAR* StatusText(const EFieldStatus Status)
{
	switch (Status)
	{
	case EFieldStatus::Match: return TEXT("MATCH");
	case EFieldStatus::Mismatch: return TEXT("MISMATCH");
	case EFieldStatus::Missing: return TEXT("MISSING");
	case EFieldStatus::Ambiguous: return TEXT("AMBIGUOUS");
	default: return TEXT("UNAVAILABLE");
	}
}

FString EscapeMarkerValue(FString Value)
{
	Value.ReplaceInline(TEXT("\\"), TEXT("\\\\"));
	Value.ReplaceInline(TEXT("|"), TEXT("\\|"));
	Value.ReplaceInline(TEXT("="), TEXT("\\="));
	Value.ReplaceInline(TEXT("\r"), TEXT("\\r"));
	Value.ReplaceInline(TEXT("\n"), TEXT("\\n"));
	return Value;
}

void EmitField(
	const TCHAR* Kind,
	const TCHAR* Name,
	const TCHAR* Expected,
	const FString& Actual,
	const EFieldStatus Status,
	FFieldCounts& Counts)
{
	++Counts.Emitted;
	if (Status == EFieldStatus::Match)
	{
		++Counts.Matches;
	}
	else if (Status == EFieldStatus::Mismatch)
	{
		++Counts.Mismatches;
	}
	else
	{
		++Counts.Gaps;
	}

	UE_LOG(
		LogCandidateBPolicySmoke,
		Display,
		TEXT("ODDSWELL_CANDIDATE_B_POLICY_FIELD|schema=1|kind=%s|name=%s|expected=%s|actual=%s|status=%s"),
		Kind,
		*EscapeMarkerValue(Name),
		*EscapeMarkerValue(Expected),
		*EscapeMarkerValue(Actual),
		StatusText(Status));
}

int32 CountRegistryName(const TCHAR* Name)
{
	int32 Count = 0;
	for (const FPolicyRegistryRow& Row : CandidateBPolicyRegistry)
	{
		Count += FCString::Strcmp(Row.Name, Name) == 0 ? 1 : 0;
	}
	return Count;
}

FString ExpectedText(const FPolicyRegistryRow& Row)
{
	return Row.Type == EPolicyValueType::Integer
		? FString::Printf(TEXT("%lld"), static_cast<long long>(Row.IntegerValue))
		: FString::SanitizeFloat(Row.FloatValue);
}

EFieldStatus EvaluateRegistryActual(const FPolicyRegistryRow& Row, const FString& Actual)
{
	double ActualValue = 0.0;
	if (!LexTryParseString(ActualValue, *Actual) || !FMath::IsFinite(ActualValue))
	{
		return EFieldStatus::Unavailable;
	}

	if (Row.Type == EPolicyValueType::Integer)
	{
		if (FMath::TruncToDouble(ActualValue) != ActualValue)
		{
			return EFieldStatus::Unavailable;
		}
		return ActualValue == static_cast<double>(Row.IntegerValue)
			? EFieldStatus::Match
			: EFieldStatus::Mismatch;
	}

	const double Tolerance = FMath::Max(0.000001, FMath::Abs(Row.FloatValue) * 0.000001);
	return FMath::Abs(ActualValue - Row.FloatValue) <= Tolerance
		? EFieldStatus::Match
		: EFieldStatus::Mismatch;
}

#if WITH_DEV_AUTOMATION_TESTS
const TCHAR* TypeText(const EPolicyValueType Type)
{
	return Type == EPolicyValueType::Integer ? TEXT("INTEGER") : TEXT("FLOAT");
}

FString ProjectRegistryForTest(const FPolicyRegistryView View)
{
	FString Projection;
	for (int32 Index = 0; Index < View.Count; ++Index)
	{
		const FPolicyRegistryRow& Row = View.Rows[Index];
		Projection += FString::Printf(
			TEXT("%d|%s|%s|%s|%s|%s\n"),
			Index,
			KindText(Row.Kind),
			TypeText(Row.Type),
			Row.SourceSection ? Row.SourceSection : TEXT(""),
			Row.Name,
			*ExpectedText(Row));
	}
	return Projection;
}

uint64 HashAsciiProjectionForTest(const FString& Projection)
{
	uint64 Hash = 0xCBF29CE484222325ull;
	for (int32 Index = 0; Index < Projection.Len(); ++Index)
	{
		const TCHAR Character = Projection[Index];
		if (Character > 0x7f)
		{
			return 0;
		}
		Hash ^= static_cast<uint8>(Character);
		Hash *= 0x100000001B3ull;
	}
	return Hash;
}
#endif

void ApplyRegistry()
{
	const FPolicyRegistryView View = PolicyApplyOrder();
	for (int32 Index = 0; Index < View.Count; ++Index)
	{
		const FPolicyRegistryRow& Row = View.Rows[Index];
		const FString Expected = ExpectedText(Row);
		if (CountRegistryName(Row.Name) != 1)
		{
			continue;
		}

		IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(Row.Name);
		if (Variable)
		{
			Variable->Set(*Expected, ECVF_SetByCommandline);
		}
	}
}

void EmitRegistryReadbacks(FFieldCounts& Counts)
{
	const FPolicyRegistryView View = PolicyEvidenceOrder();
	for (int32 Index = 0; Index < View.Count; ++Index)
	{
		const FPolicyRegistryRow& Row = View.Rows[Index];
		const FString Expected = ExpectedText(Row);
		if (CountRegistryName(Row.Name) != 1)
		{
			EmitField(KindText(Row.Kind), Row.Name, *Expected, TEXT("DUPLICATE_REGISTRY_NAME"), EFieldStatus::Ambiguous, Counts);
			continue;
		}

		IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(Row.Name);
		if (!Variable)
		{
			EmitField(KindText(Row.Kind), Row.Name, *Expected, TEXT("MISSING"), EFieldStatus::Missing, Counts);
			continue;
		}

		const FString Actual = Variable->GetString();
		EmitField(
			KindText(Row.Kind),
			Row.Name,
			*Expected,
			Actual,
			EvaluateRegistryActual(Row, Actual),
			Counts);
	}
}

void EmitRuntimeFields(FFieldCounts& Counts)
{
	if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport)
	{
		const FIntPoint Size = GEngine->GameViewport->Viewport->GetSizeXY();
		if (Size.X > 0 && Size.Y > 0)
		{
			const FString Actual = FString::Printf(TEXT("%dx%d"), Size.X, Size.Y);
			EmitField(TEXT("RUNTIME"), TEXT("viewport_size"), TEXT("1920x1080"), Actual,
				Actual == TEXT("1920x1080") ? EFieldStatus::Match : EFieldStatus::Mismatch, Counts);
		}
		else
		{
			EmitField(TEXT("RUNTIME"), TEXT("viewport_size"), TEXT("1920x1080"), TEXT("UNAVAILABLE"), EFieldStatus::Unavailable, Counts);
		}
	}
	else
	{
		EmitField(TEXT("RUNTIME"), TEXT("viewport_size"), TEXT("1920x1080"), TEXT("UNAVAILABLE"), EFieldStatus::Unavailable, Counts);
	}

	FString RhiName = FApp::GetGraphicsRHI();
	RhiName.TrimStartAndEndInline();
	EmitField(TEXT("RUNTIME"), TEXT("rhi_name"), TEXT("D3D12"), RhiName.IsEmpty() ? TEXT("UNAVAILABLE") : RhiName,
		RhiName.IsEmpty() ? EFieldStatus::Unavailable
			: (RhiName.Equals(TEXT("D3D12"), ESearchCase::IgnoreCase) ? EFieldStatus::Match : EFieldStatus::Mismatch), Counts);

	FString AdapterName = GRHIAdapterName;
	AdapterName.TrimStartAndEndInline();
	EmitField(TEXT("RUNTIME"), TEXT("adapter_name"), TEXT("NONEMPTY"), AdapterName.IsEmpty() ? TEXT("UNAVAILABLE") : AdapterName,
		AdapterName.IsEmpty() ? EFieldStatus::Unavailable : EFieldStatus::Match, Counts);

	FString FeatureLevel;
	GetFeatureLevelName(GMaxRHIFeatureLevel, FeatureLevel);
	EmitField(TEXT("RUNTIME"), TEXT("rhi_feature_level"), TEXT("SM6"), FeatureLevel.IsEmpty() ? TEXT("UNAVAILABLE") : FeatureLevel,
		FeatureLevel.IsEmpty() ? EFieldStatus::Unavailable
			: (FeatureLevel == TEXT("SM6") ? EFieldStatus::Match : EFieldStatus::Mismatch), Counts);

	const FString ShaderPlatform = LexToString(GMaxRHIShaderPlatform);
	EmitField(TEXT("RUNTIME"), TEXT("shader_platform"), TEXT("PCD3D_SM6"), ShaderPlatform.IsEmpty() ? TEXT("UNAVAILABLE") : ShaderPlatform,
		ShaderPlatform.IsEmpty() ? EFieldStatus::Unavailable
			: (ShaderPlatform == TEXT("PCD3D_SM6") ? EFieldStatus::Match : EFieldStatus::Mismatch), Counts);

	EmitField(TEXT("RUNTIME"), TEXT("d3d_feature_level_12_0"), TEXT("true"), TEXT("UNAVAILABLE_PUBLIC_GAME_THREAD_API"), EFieldStatus::Unavailable, Counts);
	EmitField(TEXT("RUNTIME"), TEXT("shader_model_6_6"), TEXT("true"), TEXT("UNAVAILABLE_PUBLIC_GAME_THREAD_API"), EFieldStatus::Unavailable, Counts);

	IConsoleVariable* Vsm = IConsoleManager::Get().FindConsoleVariable(TEXT("r.Shadow.Virtual.Enable"));
	if (Vsm)
	{
		int32 Value = 0;
		const FString Raw = Vsm->GetString();
		if (LexTryParseString(Value, *Raw))
		{
			const bool bEnabled = Value == 1;
			EmitField(TEXT("RUNTIME"), TEXT("vsm_enabled"), TEXT("true"), bEnabled ? TEXT("true") : TEXT("false"),
				bEnabled ? EFieldStatus::Match : EFieldStatus::Mismatch, Counts);
		}
		else
		{
			EmitField(TEXT("RUNTIME"), TEXT("vsm_enabled"), TEXT("true"), TEXT("UNAVAILABLE"), EFieldStatus::Unavailable, Counts);
		}
	}
	else
	{
		EmitField(TEXT("RUNTIME"), TEXT("vsm_enabled"), TEXT("true"), TEXT("UNAVAILABLE"), EFieldStatus::Unavailable, Counts);
	}

	IConsoleVariable* RayTracing = IConsoleManager::Get().FindConsoleVariable(TEXT("r.RayTracing"));
	if (RayTracing)
	{
		int32 Value = 0;
		const FString Raw = RayTracing->GetString();
		if (LexTryParseString(Value, *Raw))
		{
			const bool bDisabled = Value == 0;
			EmitField(TEXT("RUNTIME"), TEXT("hwrt_disabled"), TEXT("true"), bDisabled ? TEXT("true") : TEXT("false"),
				bDisabled ? EFieldStatus::Match : EFieldStatus::Mismatch, Counts);
		}
		else
		{
			EmitField(TEXT("RUNTIME"), TEXT("hwrt_disabled"), TEXT("true"), TEXT("UNAVAILABLE"), EFieldStatus::Unavailable, Counts);
		}
	}
	else
	{
		EmitField(TEXT("RUNTIME"), TEXT("hwrt_disabled"), TEXT("true"), TEXT("UNAVAILABLE"), EFieldStatus::Unavailable, Counts);
	}

	EmitField(TEXT("RUNTIME"), TEXT("native_tsr_identity"), TEXT("BUILT_IN_UNREAL_TSR"), TEXT("UNAVAILABLE_PUBLIC_GAME_THREAD_API"), EFieldStatus::Unavailable, Counts);
	EmitField(TEXT("POLICY"), TEXT("nanite_required"), TEXT("false"), TEXT("false"), EFieldStatus::Match, Counts);
}

void RunPolicySmoke(UWorld* World)
{
	if (!World || !World->IsGameWorld())
	{
		return;
	}

	UE_LOG(LogCandidateBPolicySmoke, Display, TEXT("ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=START|schema=1|selectors=11|children=154|controls=8"));

	FFieldCounts Counts;
	ApplyRegistry();
	EmitRegistryReadbacks(Counts);
	EmitRuntimeFields(Counts);

	const TCHAR* Result = Counts.Mismatches > 0
		? TEXT("POLICY_FAIL")
		: (Counts.Gaps > 0 || Counts.Emitted != 184 ? TEXT("EVIDENCE_LIMITED") : TEXT("POLICY_PASS"));

	UE_LOG(
		LogCandidateBPolicySmoke,
		Display,
		TEXT("ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=RESULT|schema=1|result=%s|fields_expected=184|fields_emitted=%d|matches=%d|mismatches=%d|gaps=%d"),
		Result,
		Counts.Emitted,
		Counts.Matches,
		Counts.Mismatches,
		Counts.Gaps);

	if (FCString::Strcmp(Result, TEXT("POLICY_PASS")) != 0)
	{
		FPlatformMisc::RequestExit(false);
	}
}
}

namespace OddsWellCandidateBPolicySmoke
{
bool IsCandidateBPolicySmokeRequested(const TCHAR* CommandLine)
{
	return CommandLine && FParse::Param(CommandLine, TEXT("CandidateBPolicySmokeQa"));
}

void BindToWorld(UWorld* World)
{
	if (!World || !World->IsGameWorld() || !IsCandidateBTargetWorldPackage(World->GetOutermostObject()->GetName()) || bCandidateWorldClaimed)
	{
		return;
	}

	bCandidateWorldClaimed = true;
	const TWeakObjectPtr<UWorld> WeakWorld(World);
	World->OnWorldBeginPlay.AddWeakLambda(World, [WeakWorld]()
	{
		if (UWorld* LiveWorld = WeakWorld.Get(); LiveWorld && LiveWorld->IsGameWorld())
		{
			UE_LOG(LogCandidateBPolicySmoke, Display, TEXT("ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=BEGIN_PLAY|schema=1"));
			LiveWorld->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateLambda([WeakWorld]()
			{
				if (UWorld* NextTickWorld = WeakWorld.Get(); NextTickWorld && NextTickWorld->IsGameWorld())
				{
					UE_LOG(LogCandidateBPolicySmoke, Display, TEXT("ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=NEXT_TICK_DISPATCHED|schema=1"));
					RunPolicySmoke(NextTickWorld);
				}
			}));
		}
	});
	UE_LOG(LogCandidateBPolicySmoke, Display, TEXT("ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=WORLD_BOUND|schema=1"));
}
}

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FCandidateBPolicySmokeCommandLineTest,
	"OddsWell.CandidateBPolicySmoke.CommandLinePredicate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FCandidateBPolicySmokeCommandLineTest::RunTest(const FString& Parameters)
{
	(void)Parameters;
	TestFalse(TEXT("Empty command line remains off"), OddsWellCandidateBPolicySmoke::IsCandidateBPolicySmokeRequested(TEXT("")));
	TestFalse(TEXT("Existing route flags do not opt in"), OddsWellCandidateBPolicySmoke::IsCandidateBPolicySmokeRequested(TEXT("-SundaleRouteQa -SundaleRouteRun -LocomotionAutoExit")));
	TestTrue(TEXT("Exact Candidate B flag opts in"), OddsWellCandidateBPolicySmoke::IsCandidateBPolicySmokeRequested(TEXT("-CandidateBPolicySmokeQa")));
	TestFalse(TEXT("Empty world package is rejected"), IsCandidateBTargetWorldPackage(FString()));
	TestFalse(TEXT("Bootstrap world package is rejected"), IsCandidateBTargetWorldPackage(FString(TEXT("/Game/Maps/Bootstrap"))));
	TestTrue(TEXT("Exact Sundale world package is accepted"), IsCandidateBTargetWorldPackage(FString(TEXT("/Game/Maps/SundaleGraybox"))));

	int32 SelectorCount = 0;
	int32 ChildCount = 0;
	int32 ControlCount = 0;
	int32 IntegerCount = 0;
	int32 FloatCount = 0;
	int32 SourceSectionCount = 0;
	int32 LandscapeSelectorCount = 0;
	int32 LandscapeChildCount = 0;
	bool bUniqueNames = true;
	bool bOrderedKinds = true;
	bool bCanonicalScalars = true;
	const TCHAR* PreviousSection = nullptr;

	for (int32 Index = 0; Index < UE_ARRAY_COUNT(CandidateBPolicyRegistry); ++Index)
	{
		const FPolicyRegistryRow& Row = CandidateBPolicyRegistry[Index];
		SelectorCount += Row.Kind == EPolicyRegistryKind::Selector ? 1 : 0;
		ChildCount += Row.Kind == EPolicyRegistryKind::Child ? 1 : 0;
		ControlCount += Row.Kind == EPolicyRegistryKind::Control ? 1 : 0;
		IntegerCount += Row.Type == EPolicyValueType::Integer ? 1 : 0;
		FloatCount += Row.Type == EPolicyValueType::Float ? 1 : 0;
		bOrderedKinds &= Index < 11
			? Row.Kind == EPolicyRegistryKind::Selector
			: (Index < 165 ? Row.Kind == EPolicyRegistryKind::Child : Row.Kind == EPolicyRegistryKind::Control);
		bCanonicalScalars &= Row.Name && Row.Name[0] != TEXT('\0');
		bCanonicalScalars &= Row.Type == EPolicyValueType::Integer
			? Row.FloatValue == 0.0
			: Row.IntegerValue == 0 && FMath::IsFinite(Row.FloatValue);

		if (Row.Kind == EPolicyRegistryKind::Child)
		{
			bCanonicalScalars &= Row.SourceSection && Row.SourceSection[0] != TEXT('\0');
			if (Row.SourceSection && (!PreviousSection || FCString::Strcmp(PreviousSection, Row.SourceSection) != 0))
			{
				++SourceSectionCount;
				PreviousSection = Row.SourceSection;
			}
			LandscapeChildCount += Row.SourceSection
				&& FCString::Strcmp(Row.SourceSection, TEXT("LandscapeQuality@1")) == 0 ? 1 : 0;
		}
		else
		{
			bCanonicalScalars &= Row.SourceSection == nullptr;
		}

		LandscapeSelectorCount += Row.Kind == EPolicyRegistryKind::Selector
			&& FCString::Strcmp(Row.Name, TEXT("sg.LandscapeQuality")) == 0
			&& Row.Type == EPolicyValueType::Integer
			&& Row.IntegerValue == 1 ? 1 : 0;

		for (int32 OtherIndex = Index + 1; OtherIndex < UE_ARRAY_COUNT(CandidateBPolicyRegistry); ++OtherIndex)
		{
			bUniqueNames &= FCString::Strcmp(Row.Name, CandidateBPolicyRegistry[OtherIndex].Name) != 0;
		}
	}

	TestEqual(TEXT("Registry row count"), static_cast<int32>(UE_ARRAY_COUNT(CandidateBPolicyRegistry)), 173);
	TestEqual(TEXT("Selector count"), SelectorCount, 11);
	TestEqual(TEXT("Child count"), ChildCount, 154);
	TestEqual(TEXT("Control count"), ControlCount, 8);
	TestEqual(TEXT("Integer policy type count"), IntegerCount, 144);
	TestEqual(TEXT("Float policy type count"), FloatCount, 29);
	TestEqual(TEXT("Present source section count"), SourceSectionCount, 10);
	TestEqual(TEXT("Landscape selector count"), LandscapeSelectorCount, 1);
	TestEqual(TEXT("Landscape child count"), LandscapeChildCount, 0);
	TestTrue(TEXT("Registry names are unique"), bUniqueNames);
	TestTrue(TEXT("Registry kind order is selector, child, control"), bOrderedKinds);
	TestTrue(TEXT("Registry values, types, and source-section nullability are canonical"), bCanonicalScalars);
	TestEqual(
		TEXT("BaseScalability source SHA remains exact"),
		FString(CandidateBBaseScalabilitySha256),
		FString(TEXT("579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6")));
	const FString ApplyProjection = ProjectRegistryForTest(PolicyApplyOrder());
	const FString EvidenceProjection = ProjectRegistryForTest(PolicyEvidenceOrder());
	TestFalse(TEXT("Apply-order registry projection is nonempty"), ApplyProjection.IsEmpty());
	TestEqual(TEXT("Apply and evidence order projections are byte-identical"), ApplyProjection, EvidenceProjection);
	TestEqual(TEXT("Apply-order full registry FNV-1a identity"), HashAsciiProjectionForTest(ApplyProjection), 0x912A064DAD4DE242ull);
	TestEqual(TEXT("Evidence-order full registry FNV-1a identity"), HashAsciiProjectionForTest(EvidenceProjection), 0x912A064DAD4DE242ull);
	return true;
}

#endif
#endif
