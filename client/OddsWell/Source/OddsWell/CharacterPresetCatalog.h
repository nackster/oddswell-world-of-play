#pragma once

#include "CoreMinimal.h"

enum class EOddsWellCharacterPresentation : uint8
{
	Masculine,
	Feminine
};

enum class EOddsWellStarterEquipmentSlot : uint8
{
	Top,
	Bottom
};

struct FOddsWellCharacterPreset
{
	FName Id;
	EOddsWellCharacterPresentation Presentation;
	FColor SkinTone;
	TArray<FName> EquippedItemIds;
};

ODDSWELL_API const TArray<FOddsWellCharacterPreset>& GetOddsWellCharacterPresets();
ODDSWELL_API bool ValidateOddsWellCharacterPresets(FString& OutError);
ODDSWELL_API const FOddsWellCharacterPreset* FindOddsWellCharacterPreset(FName PresetId);
ODDSWELL_API bool GetOddsWellStarterEquipmentIds(FName& OutTop, FName& OutBottom, FString& OutError);
ODDSWELL_API bool ResolveOddsWellStarterEquipmentSlot(FName ItemId, EOddsWellStarterEquipmentSlot& OutSlot, FString& OutError);
