# Provenance

Deterministic standard-library/native-geometry review artifact.

- Direct source authority: `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`
- Source SHA-256: `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298`
- Weather ID: `SUNDALE_DRY_LATE_AFTERNOON`
- Scenario IDs: `COMMONS_OPEN_SUN`, `AWNING_PATTERNED_SHADE`, `ROUTE_LONG_VIEW_WARM_HAZE`
- Target IDs: `STARTER_OFFWHITE_READ`, `SIGNAL_JACKET_READ`, `COBALT_ROUTE_MARK_READ`, `BURNT_ORANGE_THRESHOLD_READ`, `LIMESTONE_TERRACOTTA_SURFACE_READ`

## Exact source bindings

- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:80` = `const FLinearColor StarterOffWhite(0.92f, 0.90f, 0.82f);`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:81` = `const FLinearColor SignalJacketSlate(0.12f, 0.18f, 0.22f);`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:82` = `const FLinearColor SignalJacketTeal(0.08f, 0.72f, 0.68f);`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1030` = `const FLinearColor SundaleWarmLimestone = FLinearColor::FromSRGBColor(FColor(0xD8, 0xC8, 0xA9));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1031` = `const FLinearColor SundaleMutedTerracotta = FLinearColor::FromSRGBColor(FColor(0xA6, 0x5F, 0x47));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1032` = `const FLinearColor SundaleSandConcrete = FLinearColor::FromSRGBColor(FColor(0xB9, 0xA7, 0x83));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1033` = `const FLinearColor SundaleSageGreen = FLinearColor::FromSRGBColor(FColor(0x6D, 0x7F, 0x62));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1034` = `const FLinearColor SundaleRestrainedCobalt = FLinearColor::FromSRGBColor(FColor(0x31, 0x5F, 0x79));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1035` = `const FLinearColor SundaleBurntOrange = FLinearColor::FromSRGBColor(FColor(0xC4, 0x6D, 0x3B));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1036` = `const FLinearColor SundaleCharcoalGray = FLinearColor::FromSRGBColor(FColor(0x4D, 0x50, 0x51));`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1224` = `struct FSundaleAtmosphereSpec`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1225` = `{`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1226` = `	float DirectionalIntensity;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1227` = `	float DirectionalTemperatureKelvin;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1228` = `	float SkyLightIntensity;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1229` = `	FLinearColor SkyLightColor;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1230` = `	float FogDensity;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1231` = `	FLinearColor FogInscatteringColor;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1232` = `	int32 ExpectedDirectionalLights;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1233` = `	int32 ExpectedSkyLights;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1234` = `	int32 ExpectedHeightFogs;`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1235` = `};`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1236` = ``
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1237` = `const FSundaleAtmosphereSpec& GetSundaleAtmosphereSpec()`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1238` = `{`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1239` = `	static const FSundaleAtmosphereSpec Spec = {`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1240` = `		5.0f,`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1241` = `		5000.0f,`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1242` = `		0.8f,`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1243` = `		FLinearColor::FromSRGBColor(FColor(0xD8, 0xE4, 0xF0)),`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1244` = `		0.003f,`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1245` = `		FLinearColor::FromSRGBColor(FColor(0xE8, 0xC9, 0xA5)),`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1246` = `		1,`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1247` = `		1,`
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp:1248` = `		1,`

## Scope flags

- `production_claim=false`
- `photometric_claim=false`
- `lighting_change=false`
- `weather_system=false`
- `weather_variants=0`
- `time_of_day_system=false`
- `accessibility_ready=false`
- `gameplay_change=false`
- `gameplay_additions=0`
