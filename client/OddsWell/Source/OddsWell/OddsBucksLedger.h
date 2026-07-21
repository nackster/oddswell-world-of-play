#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "OddsBucksLedger.generated.h"

enum class EOddsWellOddsBucksAppendResult : uint8
{
	Applied,
	Duplicate,
	Rejected
};

USTRUCT()
struct FOddsWellOddsBucksEntry
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	int64 Sequence = 0;

	UPROPERTY(SaveGame)
	FString CommandId;

	UPROPERTY(SaveGame)
	int64 Delta = 0;

	UPROPERTY(SaveGame)
	int64 BalanceAfter = 0;

	UPROPERTY(SaveGame)
	FName Reason;
};

UCLASS()
class ODDSWELL_API UOddsWellOddsBucksSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	int32 SchemaVersion = 1;

	UPROPERTY(SaveGame)
	TArray<FOddsWellOddsBucksEntry> Entries;
};

class FOddsWellOddsBucksLedger
{
public:
	EOddsWellOddsBucksAppendResult Append(const FString& CommandId, int64 Delta, FName Reason);
	bool Restore(const TArray<FOddsWellOddsBucksEntry>& SavedEntries, FString& OutError);
	int64 GetBalance() const { return Balance; }
	const TArray<FOddsWellOddsBucksEntry>& GetEntries() const { return Entries; }

private:
	int64 Balance = 0;
	TArray<FOddsWellOddsBucksEntry> Entries;
	TMap<FString, int32> CommandIndexes;
};

ODDSWELL_API int64 GetOddsWellFirstJobPayout();
ODDSWELL_API const FString& GetOddsWellFirstJobCommandId();
ODDSWELL_API FName GetOddsWellFirstJobReason();
ODDSWELL_API bool UseOddsWellOddsBucksQaSlot();
ODDSWELL_API bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, bool bQaSlot, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksLedger(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, bool& bOutFound, FString& OutError);
ODDSWELL_API bool ResetOddsWellQaOddsBucksAndVerify(FString& OutError);
