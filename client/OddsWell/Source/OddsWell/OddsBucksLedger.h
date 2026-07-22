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

enum class EOddsWellMatchWinnerRequestResult : uint8
{
	Accepted,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerLockResult : uint8
{
	Locked,
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

USTRUCT()
struct FOddsWellMatchWinnerSelection
{
	GENERATED_BODY()

	FString Team;
	int64 WinProbabilityE8 = 0;
	int64 DecimalOddsE4 = 0;
};

USTRUCT()
struct FOddsWellMatchWinnerOffer
{
	GENERATED_BODY()

	FString OfferId;
	FString Schema;
	FString OfferVersion;
	FString Market;
	FString Currency;
	FString SourcePredictionVersion;
	FString SourceSnapshotVersion;
	FString SourceModel;
	FString SourceCommitmentSha256;
	int32 SeasonNumber = 0;
	int32 GameNumber = 0;
	FString HomeTeam;
	FString AwayTeam;
	int64 LockUnixSeconds = 0;
	int64 MinimumStake = 0;
	int64 MaximumStake = 0;
	int64 StakeIncrement = 0;
	int32 HouseEdgeBps = 0;
	FString PayoutFormula;
	TArray<FOddsWellMatchWinnerSelection> Selections;
};

USTRUCT()
struct FOddsWellMatchWinnerRequestRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString StakeLedgerCommandId;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	FString HomeTeam;

	UPROPERTY(SaveGame)
	FString AwayTeam;

	UPROPERTY(SaveGame)
	FString OfferedTeam;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	int64 AcceptedUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 LockUnixSeconds = 0;

	UPROPERTY(SaveGame)
	FName Status;
};

USTRUCT()
struct FOddsWellMatchWinnerLockRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	int64 AuthoritativeGameStartUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 LockUnixSeconds = 0;

	UPROPERTY(SaveGame)
	FName Decision;
};

UCLASS()
class ODDSWELL_API UOddsWellOddsBucksSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	int32 SchemaVersion = 4;

	UPROPERTY(SaveGame)
	TArray<FOddsWellOddsBucksEntry> Entries;

	UPROPERTY(SaveGame)
	int64 NextJobPayoutUnixSeconds = 0;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerRequestRecord> MatchWinnerRequests;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerLockRecord> MatchWinnerLocks;
};

class FOddsWellOddsBucksLedger
{
public:
	EOddsWellOddsBucksAppendResult Append(const FString& CommandId, int64 Delta, FName Reason);
	bool Restore(const TArray<FOddsWellOddsBucksEntry>& SavedEntries, FString& OutError);
	bool HasCommand(const FString& CommandId) const { return CommandIndexes.Contains(CommandId); }
	int64 GetBalance() const { return Balance; }
	const TArray<FOddsWellOddsBucksEntry>& GetEntries() const { return Entries; }

private:
	int64 Balance = 0;
	TArray<FOddsWellOddsBucksEntry> Entries;
	TMap<FString, int32> CommandIndexes;
};

ODDSWELL_API int64 GetOddsWellFirstJobPayout();
ODDSWELL_API int64 GetOddsWellJobPayoutIntervalSeconds();
ODDSWELL_API const FString& GetOddsWellFirstJobCommandId();
ODDSWELL_API FName GetOddsWellFirstJobReason();
ODDSWELL_API bool UseOddsWellOddsBucksQaSlot();
ODDSWELL_API bool WriteOddsWellOddsBucksReconciliation(const FOddsWellOddsBucksLedger& Ledger, int64 NextJobPayoutUnixSeconds, int64 ObservedNowUnixSeconds, bool bQaProjection, FString& OutPath, FString& OutError);
ODDSWELL_API bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, int64 NextJobPayoutUnixSeconds, bool bQaSlot, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksLedger(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksState(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksWagerState(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks, bool& bOutFound, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerRequestResult AcceptOddsWellMatchWinnerRequest(const FOddsWellMatchWinnerOffer& Offer, const FString& RequestCommandId, const FString& OfferedTeam, int64 Stake, int64 AcceptedUnixSeconds, bool bQaSlot, FOddsWellMatchWinnerRequestRecord& OutRecord, int64& OutBalance, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerLockResult LockOddsWellMatchWinnerRequest(const FString& RequestCommandId, const FString& LockCommandId, int32 SeasonNumber, int32 GameNumber, int64 AuthoritativeGameStartUnixSeconds, bool bQaSlot, FOddsWellMatchWinnerLockRecord& OutRecord, FString& OutError);
ODDSWELL_API bool ResetOddsWellQaOddsBucksAndVerify(FString& OutError);
