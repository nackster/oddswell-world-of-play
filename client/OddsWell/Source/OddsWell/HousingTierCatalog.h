#pragma once

#include "CoreMinimal.h"

struct FOddsWellHousingTier
{
	FName Id;
	FString DisplayName;
	bool bInteriorAvailable = false;
};

ODDSWELL_API const TArray<FOddsWellHousingTier>& GetOddsWellHousingTiers();
ODDSWELL_API bool ValidateOddsWellHousingTiers(FString& OutError);
ODDSWELL_API const FOddsWellHousingTier* FindOddsWellHousingTier(FName TierId);
ODDSWELL_API FString BuildOddsWellHousingProgressionText(bool bOwnsStudio);
