#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CanonicalScheduledGame.generated.h"

UCLASS()
class ODDSWELL_API UOddsWellCanonicalScheduledGameSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	FString Schema;

	UPROPERTY(SaveGame)
	int32 RecordVersion = 0;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	FString HomeTeam;

	UPROPERTY(SaveGame)
	FString AwayTeam;

	UPROPERTY(SaveGame)
	int64 SeasonCreatedUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 TipoffUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 OfferEligibleUnixSeconds = 0;

	UPROPERTY(SaveGame)
	FString Status;

	UPROPERTY(SaveGame)
	FString Environment;

	UPROPERTY(SaveGame)
	FString TimingAuthority;

	UPROPERTY(SaveGame)
	bool bProductionTiming = true;

	UPROPERTY(SaveGame)
	bool bOfferPublished = true;
};

struct FOddsWellCanonicalScheduledGameRecord
{
	FString Schema;
	int32 RecordVersion = 0;
	int32 SeasonNumber = 0;
	int32 GameNumber = 0;
	FString HomeTeam;
	FString AwayTeam;
	int64 SeasonCreatedUnixSeconds = 0;
	int64 TipoffUnixSeconds = 0;
	int64 OfferEligibleUnixSeconds = 0;
	FString Status;
	FString Environment;
	FString TimingAuthority;
	bool bProductionTiming = true;
	bool bOfferPublished = true;
};

enum class EOddsWellCanonicalScheduledGameResult : uint8
{
	Created,
	Duplicate,
	Rejected
};

ODDSWELL_API EOddsWellCanonicalScheduledGameResult CreateOddsWellCanonicalLocalBetaScheduledGame(
	FOddsWellCanonicalScheduledGameRecord& OutRecord,
	FString& OutError);
ODDSWELL_API bool LoadOddsWellCanonicalLocalBetaScheduledGame(
	FOddsWellCanonicalScheduledGameRecord& OutRecord,
	FString& OutError);
