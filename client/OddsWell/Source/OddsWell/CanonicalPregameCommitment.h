#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "CanonicalPregameCommitment.generated.h"

UCLASS()
class ODDSWELL_API UOddsWellCanonicalPregameCommitmentSaveGame final : public USaveGame
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
	FString SnapshotVersion;

	UPROPERTY(SaveGame)
	FString PredictionVersion;

	UPROPERTY(SaveGame)
	FString InputClass;

	UPROPERTY(SaveGame)
	FString CommitmentJson;

	UPROPERTY(SaveGame)
	FString CommitmentSha256;

	UPROPERTY(SaveGame)
	FString Status;

	UPROPERTY(SaveGame)
	FString Environment;
};

struct FOddsWellCanonicalPregameCommitmentRecord
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
	FString SnapshotVersion;
	FString PredictionVersion;
	FString InputClass;
	FString CommitmentJson;
	FString CommitmentSha256;
	FString Status;
	FString Environment;
};

enum class EOddsWellCanonicalPregameCommitmentResult : uint8
{
	Created,
	Duplicate,
	Rejected
};

ODDSWELL_API EOddsWellCanonicalPregameCommitmentResult CreateOddsWellCanonicalPregameCommitment(
	FOddsWellCanonicalPregameCommitmentRecord& OutRecord,
	FString& OutError);
ODDSWELL_API bool LoadOddsWellCanonicalPregameCommitment(
	FOddsWellCanonicalPregameCommitmentRecord& OutRecord,
	FString& OutError);
