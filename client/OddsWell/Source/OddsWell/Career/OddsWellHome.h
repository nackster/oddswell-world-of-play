#pragma once

#include "CoreMinimal.h"
#include "Career/OddsWellCatalog.h"

class UWorld;

// Spawns the career home for an apartment tier with the given furniture; returns the boxes spawned.
ODDSWELL_API int32 BuildOddsWellCareerHome(UWorld& World, int32 Tier, const TArray<FName>& Furniture, int32& OutFurniturePlaced);
