#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "OddsWellSettings.generated.h"

// Player settings, saved per user in GameUserSettings.ini alongside the engine's display and quality options.
UCLASS(config = GameUserSettings, configdonotcheckdefaults)
class ODDSWELL_API UOddsWellGameUserSettings final : public UGameUserSettings
{
	GENERATED_BODY()

public:
	static UOddsWellGameUserSettings* Get();

	UPROPERTY(config)
	float MouseSensitivity = 1.0f;

	UPROPERTY(config)
	bool bInvertLookY = false;

	UPROPERTY(config)
	bool bShowControlHints = true;
};

// One editable row of the settings screen shared by the title screen and the pause menu.
struct FOddsWellSettingsRow
{
	FString Label;
	FString Value;
};

class ODDSWELL_API FOddsWellSettingsMenu
{
public:
	void Open();
	TArray<FOddsWellSettingsRow> BuildRows() const;
	int32 GetSelectedRow() const { return SelectedRow; }
	int32 GetRowCount() const;
	void MoveSelection(int32 Delta);
	void ChangeValue(int32 Delta);
	// Applies display and quality changes, then saves everything.
	void Apply();
	bool HasPendingChanges() const { return bPendingChanges; }

private:
	TArray<FIntPoint> Resolutions;
	int32 SelectedRow = 0;
	bool bPendingChanges = false;
};
