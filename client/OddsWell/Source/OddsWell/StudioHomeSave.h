#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "StudioHomeSave.generated.h"

UCLASS()
class ODDSWELL_API UOddsWellStudioHomeSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	int32 SchemaVersion = 1;

	UPROPERTY(SaveGame)
	bool bOwnsStudio = false;

	UPROPERTY(SaveGame)
	FVector SundaleReturnLocation = FVector::ZeroVector;
};

struct FOddsWellStudioHomeState
{
	bool bOwnsStudio = false;
	FVector SundaleReturnLocation = FVector::ZeroVector;
};

ODDSWELL_API bool UseOddsWellStudioHomeQaSlot();
ODDSWELL_API bool SaveOwnedOddsWellStudio(const FVector& SundaleReturnLocation, bool bQaSlot, FString& OutError);
ODDSWELL_API bool LoadOwnedOddsWellStudio(bool bQaSlot, FOddsWellStudioHomeState& OutState, FString& OutError);
ODDSWELL_API bool DeleteOddsWellQaStudioHomeAndVerify(FString& OutError);
