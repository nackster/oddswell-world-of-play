#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CanonicalActiveGameExecutionCommitment.generated.h"

struct FOddsWellMatchWinnerResultLinkRecord;
enum class EOddsWellMatchWinnerResultLinkResult : uint8;

UCLASS()
class ODDSWELL_API UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame final
	: public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	FString Schema;

	UPROPERTY(SaveGame)
	int32 RecordVersion = 0;

	UPROPERTY(SaveGame)
	FString ScheduleSchema;

	UPROPERTY(SaveGame)
	int32 ScheduleRecordVersion = 0;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	FString HomeTeam;

	UPROPERTY(SaveGame)
	FString AwayTeam;

	UPROPERTY(SaveGame)
	int64 ScheduleCreatedUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 ScheduleTipoffUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 OfferEligibleUnixSeconds = 0;

	UPROPERTY(SaveGame)
	FString PregameCommitmentSha256;

	UPROPERTY(SaveGame)
	FString SeedDerivationVersion;

	UPROPERTY(SaveGame)
	FString SeedMaterialJson;

	UPROPERTY(SaveGame)
	FString SeedMaterialSha256;

	UPROPERTY(SaveGame)
	int64 ExecutionSeed = 0;

	UPROPERTY(SaveGame)
	FString ExecutionInputJson;

	UPROPERTY(SaveGame)
	FString ExecutionInputSha256;

	UPROPERTY(SaveGame)
	FString CommitmentJson;

	UPROPERTY(SaveGame)
	FString CommitmentSha256;

	UPROPERTY(SaveGame)
	FString Status;

	UPROPERTY(SaveGame)
	FString Environment;
};

struct FOddsWellCanonicalActiveGameExecutionCommitmentRecord
{
	FString Schema;
	int32 RecordVersion = 0;
	FString ScheduleSchema;
	int32 ScheduleRecordVersion = 0;
	int32 SeasonNumber = 0;
	int32 GameNumber = 0;
	FString HomeTeam;
	FString AwayTeam;
	int64 ScheduleCreatedUnixSeconds = 0;
	int64 ScheduleTipoffUnixSeconds = 0;
	int64 OfferEligibleUnixSeconds = 0;
	FString PregameCommitmentSha256;
	FString SeedDerivationVersion;
	FString SeedMaterialJson;
	FString SeedMaterialSha256;
	int64 ExecutionSeed = 0;
	FString ExecutionInputJson;
	FString ExecutionInputSha256;
	FString CommitmentJson;
	FString CommitmentSha256;
	FString Status;
	FString Environment;
};

enum class EOddsWellCanonicalActiveGameExecutionCommitmentResult : uint8
{
	Created,
	Duplicate,
	Rejected
};

enum class EOddsWellCanonicalGameExecutionHandoffResult : uint8
{
	Created,
	Duplicate,
	Rejected
};

ODDSWELL_API EOddsWellCanonicalActiveGameExecutionCommitmentResult
	CreateOddsWellCanonicalActiveGameExecutionCommitment(
		FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
		FString& OutError);
ODDSWELL_API bool LoadOddsWellCanonicalActiveGameExecutionCommitment(
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
	FString& OutError);
ODDSWELL_API EOddsWellCanonicalGameExecutionHandoffResult
	WriteOddsWellCanonicalGameExecutionHandoff(
		FString& OutPath,
		FString& OutSha256,
		FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerResultLinkResult
	LinkOddsWellCanonicalMatchWinnerResult(
		FOddsWellMatchWinnerResultLinkRecord& OutRecord,
		FString& OutError);
