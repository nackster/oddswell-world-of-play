#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CanonicalMatchWinnerOffer.generated.h"

UCLASS()
class ODDSWELL_API UOddsWellCanonicalMatchWinnerOfferSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString CanonicalOfferJson;
};

struct FOddsWellCanonicalMatchWinnerOfferRecord
{
	FString OfferId;
	FString CanonicalOfferJson;
	int64 LockUnixSeconds = 0;
};

enum class EOddsWellCanonicalMatchWinnerOfferResult : uint8
{
	Created,
	Duplicate,
	Rejected
};

ODDSWELL_API EOddsWellCanonicalMatchWinnerOfferResult CreateOddsWellCanonicalMatchWinnerOffer(
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError);
ODDSWELL_API bool LoadOddsWellCanonicalMatchWinnerOffer(
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError);
