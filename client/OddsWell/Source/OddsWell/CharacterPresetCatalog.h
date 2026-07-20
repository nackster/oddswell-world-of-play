#pragma once

#include "CoreMinimal.h"

enum class EOddsWellCharacterPresentation : uint8
{
	Masculine,
	Feminine
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
