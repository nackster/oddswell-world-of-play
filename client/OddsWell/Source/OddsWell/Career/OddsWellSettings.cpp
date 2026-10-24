#include "Career/OddsWellSettings.h"

#include "Engine/Engine.h"
#include "Kismet/KismetSystemLibrary.h"

namespace
{
	enum ESettingsRow : int32
	{
		DisplayMode,
		Resolution,
		Quality,
		VSync,
		FrameLimit,
		Sensitivity,
		InvertY,
		ControlHints,
		RowCount
	};

	const float FrameLimits[] = {30.0f, 60.0f, 120.0f, 0.0f};
	const TCHAR* QualityNames[] = {TEXT("Low"), TEXT("Medium"), TEXT("High"), TEXT("Epic")};

	FString WindowModeName(const EWindowMode::Type Mode)
	{
		switch (Mode)
		{
		case EWindowMode::Fullscreen: return TEXT("Fullscreen");
		case EWindowMode::WindowedFullscreen: return TEXT("Borderless");
		default: return TEXT("Windowed");
		}
	}

	int32 FrameLimitIndex(const float Limit)
	{
		for (int32 Index = 0; Index < UE_ARRAY_COUNT(FrameLimits); ++Index)
		{
			if (FMath::IsNearlyEqual(FrameLimits[Index], Limit))
			{
				return Index;
			}
		}
		return 3;
	}
}

UOddsWellGameUserSettings* UOddsWellGameUserSettings::Get()
{
	return GEngine ? Cast<UOddsWellGameUserSettings>(GEngine->GetGameUserSettings()) : nullptr;
}

void FOddsWellSettingsMenu::Open()
{
	SelectedRow = 0;
	bPendingChanges = false;
	Resolutions.Reset();
	TArray<FIntPoint> Supported;
	if (UKismetSystemLibrary::GetSupportedFullscreenResolutions(Supported))
	{
		for (const FIntPoint& Size : Supported)
		{
			if (Size.X >= 1280 && Size.Y >= 720)
			{
				Resolutions.AddUnique(Size);
			}
		}
	}
	if (Resolutions.IsEmpty())
	{
		Resolutions = {{1280, 720}, {1600, 900}, {1920, 1080}, {2560, 1440}};
	}
	if (const UOddsWellGameUserSettings* Settings = UOddsWellGameUserSettings::Get())
	{
		Resolutions.AddUnique(Settings->GetScreenResolution());
	}
	Resolutions.Sort([](const FIntPoint& A, const FIntPoint& B) { return A.X * A.Y < B.X * B.Y; });
}

int32 FOddsWellSettingsMenu::GetRowCount() const
{
	return RowCount;
}

void FOddsWellSettingsMenu::MoveSelection(const int32 Delta)
{
	SelectedRow = (SelectedRow + Delta + RowCount) % RowCount;
}

TArray<FOddsWellSettingsRow> FOddsWellSettingsMenu::BuildRows() const
{
	TArray<FOddsWellSettingsRow> Rows;
	const UOddsWellGameUserSettings* Settings = UOddsWellGameUserSettings::Get();
	if (!Settings)
	{
		return Rows;
	}
	const FIntPoint Size = Settings->GetScreenResolution();
	const int32 QualityLevel = FMath::Clamp(Settings->GetOverallScalabilityLevel(), 0, 3);
	const float Limit = Settings->GetFrameRateLimit();
	Rows.Add({TEXT("Display mode"), WindowModeName(Settings->GetFullscreenMode())});
	Rows.Add({TEXT("Resolution"), FString::Printf(TEXT("%d x %d"), Size.X, Size.Y)});
	Rows.Add({TEXT("Graphics quality"), Settings->GetOverallScalabilityLevel() < 0 ? FString(TEXT("Custom")) : FString(QualityNames[QualityLevel])});
	Rows.Add({TEXT("VSync"), Settings->IsVSyncEnabled() ? TEXT("On") : TEXT("Off")});
	Rows.Add({TEXT("Frame limit"), Limit <= 0.0f ? FString(TEXT("Unlimited")) : FString::Printf(TEXT("%.0f fps"), Limit)});
	Rows.Add({TEXT("Mouse sensitivity"), FString::Printf(TEXT("%.2fx"), Settings->MouseSensitivity)});
	Rows.Add({TEXT("Invert look up/down"), Settings->bInvertLookY ? TEXT("On") : TEXT("Off")});
	Rows.Add({TEXT("Control hints"), Settings->bShowControlHints ? TEXT("On") : TEXT("Off")});
	return Rows;
}

void FOddsWellSettingsMenu::ChangeValue(const int32 Delta)
{
	UOddsWellGameUserSettings* Settings = UOddsWellGameUserSettings::Get();
	if (!Settings)
	{
		return;
	}
	bPendingChanges = true;
	switch (SelectedRow)
	{
	case DisplayMode:
	{
		const EWindowMode::Type Modes[] = {EWindowMode::Windowed, EWindowMode::WindowedFullscreen, EWindowMode::Fullscreen};
		int32 Index = 0;
		for (int32 Candidate = 0; Candidate < 3; ++Candidate)
		{
			Index = Modes[Candidate] == Settings->GetFullscreenMode() ? Candidate : Index;
		}
		Settings->SetFullscreenMode(Modes[(Index + Delta + 3) % 3]);
		break;
	}
	case Resolution:
	{
		int32 Index = Resolutions.IndexOfByKey(Settings->GetScreenResolution());
		Index = Index == INDEX_NONE ? 0 : (Index + Delta + Resolutions.Num()) % Resolutions.Num();
		Settings->SetScreenResolution(Resolutions[Index]);
		break;
	}
	case Quality:
		Settings->SetOverallScalabilityLevel(FMath::Clamp(FMath::Max(0, Settings->GetOverallScalabilityLevel()) + Delta, 0, 3));
		break;
	case VSync:
		Settings->SetVSyncEnabled(!Settings->IsVSyncEnabled());
		break;
	case FrameLimit:
		Settings->SetFrameRateLimit(FrameLimits[(FrameLimitIndex(Settings->GetFrameRateLimit()) + Delta + 4) % 4]);
		break;
	case Sensitivity:
		Settings->MouseSensitivity = FMath::Clamp(Settings->MouseSensitivity + 0.25f * Delta, 0.25f, 3.0f);
		break;
	case InvertY:
		Settings->bInvertLookY = !Settings->bInvertLookY;
		break;
	case ControlHints:
		Settings->bShowControlHints = !Settings->bShowControlHints;
		break;
	default:
		break;
	}
}

void FOddsWellSettingsMenu::Apply()
{
	if (UOddsWellGameUserSettings* Settings = UOddsWellGameUserSettings::Get())
	{
		Settings->ApplySettings(false);
		Settings->SaveSettings();
	}
	bPendingChanges = false;
}
