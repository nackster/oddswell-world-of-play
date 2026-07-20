#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "CharacterSelectionScreen.generated.h"

struct FOddsWellCharacterPreset;

class FOddsWellCharacterSelectionState
{
public:
	FOddsWellCharacterSelectionState();

	bool IsValid() const { return SelectedIndex != INDEX_NONE; }
	bool IsConfirmed() const { return !ConfirmedPresetId.IsNone(); }
	bool Navigate(int32 Delta);
	bool Confirm();
	int32 GetSelectedIndex() const { return SelectedIndex; }
	FName GetConfirmedPresetId() const { return ConfirmedPresetId; }
	const FOddsWellCharacterPreset* GetSelectedPreset() const;
	const FString& GetError() const { return Error; }

private:
	int32 SelectedIndex = INDEX_NONE;
	FName ConfirmedPresetId;
	FString Error;
};

UCLASS()
class ODDSWELL_API AOddsWellCharacterSelectionHUD final : public AHUD
{
	GENERATED_BODY()

public:
	AOddsWellCharacterSelectionHUD();
	virtual void BeginPlay() override;
	virtual void DrawHUD() override;
	virtual void Tick(float DeltaSeconds) override;

private:
	void MoveLeft();
	void MoveRight();
	void MoveUp();
	void MoveDown();
	void ConfirmSelection();
	void DrawCard(const FOddsWellCharacterPreset& Preset, int32 Index, float X, float Y, float Width, float Height);

	FOddsWellCharacterSelectionState State;
	double AutoExitAt = 0.0;
};

UCLASS()
class ODDSWELL_API AOddsWellCharacterSelectionGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellCharacterSelectionGameMode();
};
