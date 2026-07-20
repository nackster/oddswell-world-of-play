#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CharacterAppearanceSave.generated.h"

struct FOddsWellCharacterPreset;

UCLASS()
class ODDSWELL_API UOddsWellCharacterAppearanceSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	int32 SchemaVersion = 1;

	UPROPERTY(SaveGame)
	FName PresetId;

	UPROPERTY(SaveGame)
	FName TopItemId;

	UPROPERTY(SaveGame)
	FName BottomItemId;
};

struct FOddsWellResolvedCharacterAppearance
{
	const FOddsWellCharacterPreset* Preset = nullptr;
	FName TopItemId;
	FName BottomItemId;
};

ODDSWELL_API bool UseOddsWellAppearanceQaSlot();
ODDSWELL_API bool ValidateOddsWellCharacterAppearanceSave(
	const UObject* SaveObject,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutError);
ODDSWELL_API bool ResolveOddsWellCharacterAppearance(
	const UObject* SaveObject,
	bool bSaveExists,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutSource,
	FString& OutError);
ODDSWELL_API bool SaveOddsWellCharacterAppearance(FName PresetId, bool bQaSlot, FString& OutError);
ODDSWELL_API bool LoadOddsWellCharacterAppearance(
	bool bQaSlot,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutSource,
	FString& OutError);
ODDSWELL_API bool DeleteOddsWellQaAppearanceAndVerify(FString& OutError);
