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

enum class EOddsWellMatchWinnerResultLinkResult : uint8
{
	Linked,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerCanceledGameResult : uint8
{
	Recorded,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerVoidDecisionResult : uint8
{
	Decided,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerVoidFinalizationResult : uint8
{
	Finalized,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerSettlementDecisionResult : uint8
{
	Decided,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerLossFinalizationResult : uint8
{
	Finalized,
	Duplicate,
	Rejected
};

enum class EOddsWellMatchWinnerWinFinalizationResult : uint8
{
	Finalized,
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
	int32 EvidenceVersion = 0;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString StakeLedgerCommandId;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	FString OfferSchema;

	UPROPERTY(SaveGame)
	FString Market;

	UPROPERTY(SaveGame)
	FString Currency;

	UPROPERTY(SaveGame)
	FString SourcePredictionVersion;

	UPROPERTY(SaveGame)
	FString SourceSnapshotVersion;

	UPROPERTY(SaveGame)
	FString SourceModel;

	UPROPERTY(SaveGame)
	FString SourceCommitmentSha256;

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
	int64 SelectedWinProbabilityE8 = 0;

	UPROPERTY(SaveGame)
	int64 SelectedDecimalOddsE4 = 0;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	FString PayoutFormula;

	UPROPERTY(SaveGame)
	int64 GrossReturn = 0;

	UPROPERTY(SaveGame)
	int64 AcceptedUnixSeconds = 0;

	UPROPERTY(SaveGame)
	int64 LockUnixSeconds = 0;

	UPROPERTY(SaveGame)
	FName Status;
};

USTRUCT()
struct FOddsWellPendingQaMatchWinnerReceipt
{
	GENERATED_BODY()

	FString RequestId;
	FString OfferId;
	FString OfferVersion;
	FString SelectedTeam;
	int64 Stake = 0;
	int64 AcceptedUnixSeconds = 0;
	int64 LockUnixSeconds = 0;
	FName Status;
	int64 LedgerSequence = 0;
	int64 LedgerDelta = 0;
	FName LedgerReason;
	int64 CurrentBalance = 0;
};

enum class EOddsWellCanonicalPendingReceiptResult : uint8
{
	Missing,
	Ready,
	Rejected
};

struct FOddsWellCanonicalPendingMatchWinnerReceipt
{
	FString RequestId;
	FString OfferId;
	FString SelectedTeam;
	int64 SelectedWinProbabilityE8 = 0;
	int64 SelectedDecimalOddsE4 = 0;
	int64 Stake = 0;
	int64 GrossReturn = 0;
	int64 AcceptedUnixSeconds = 0;
	int64 LockUnixSeconds = 0;
	FName Status;
	int64 CurrentBalance = 0;
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

USTRUCT()
struct FOddsWellMatchWinnerResultLinkRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString ResultCommandId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString ResultSchema;

	UPROPERTY(SaveGame)
	FString ResultVersion;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	FString HomeTeam;

	UPROPERTY(SaveGame)
	FString AwayTeam;

	UPROPERTY(SaveGame)
	int32 HomeScore = 0;

	UPROPERTY(SaveGame)
	int32 AwayScore = 0;

	UPROPERTY(SaveGame)
	FString Winner;

	UPROPERTY(SaveGame)
	FString ReplaySealSha256;
};

USTRUCT()
struct FOddsWellMatchWinnerCanceledGameRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString CancellationCommandId;

	UPROPERTY(SaveGame)
	FString CancellationEvidenceId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString DispositionSchema;

	UPROPERTY(SaveGame)
	FString DispositionVersion;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	int64 AuthoritativeCancellationUnixSeconds = 0;

	UPROPERTY(SaveGame)
	FName ReasonCode;

	UPROPERTY(SaveGame)
	FName Status;
};

USTRUCT()
struct FOddsWellMatchWinnerVoidDecisionRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString VoidDecisionCommandId;

	UPROPERTY(SaveGame)
	FString CancellationCommandId;

	UPROPERTY(SaveGame)
	FString CancellationEvidenceId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString DecisionSchema;

	UPROPERTY(SaveGame)
	FString DecisionVersion;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferSchema;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	FString SelectedTeam;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	FName CancellationReason;

	UPROPERTY(SaveGame)
	FName Outcome;

	UPROPERTY(SaveGame)
	int64 RefundDue = 0;

	UPROPERTY(SaveGame)
	FName Status;
};

USTRUCT()
struct FOddsWellMatchWinnerVoidFinalizationRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString FinalizationCommandId;

	UPROPERTY(SaveGame)
	FString VoidDecisionCommandId;

	UPROPERTY(SaveGame)
	FString CancellationCommandId;

	UPROPERTY(SaveGame)
	FString CancellationEvidenceId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString FinalizationSchema;

	UPROPERTY(SaveGame)
	FString FinalizationVersion;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferSchema;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	int32 SeasonNumber = 0;

	UPROPERTY(SaveGame)
	int32 GameNumber = 0;

	UPROPERTY(SaveGame)
	FString SelectedTeam;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	FName CancellationReason;

	UPROPERTY(SaveGame)
	FName Outcome;

	UPROPERTY(SaveGame)
	int64 RefundDue = 0;

	UPROPERTY(SaveGame)
	int64 RefundApplied = 0;

	UPROPERTY(SaveGame)
	FString RefundLedgerCommandId;

	UPROPERTY(SaveGame)
	FName Status;

	UPROPERTY(SaveGame)
	int64 ObservedFinalBalance = 0;

	UPROPERTY(SaveGame)
	int32 ObservedLedgerEntryCount = 0;
};

USTRUCT()
struct FOddsWellMatchWinnerSettlementDecisionRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString DecisionCommandId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString ResultCommandId;

	UPROPERTY(SaveGame)
	FString DecisionSchema;

	UPROPERTY(SaveGame)
	FString DecisionVersion;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	FString SelectedTeam;

	UPROPERTY(SaveGame)
	FString AuthoritativeWinner;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	FName Outcome;

	UPROPERTY(SaveGame)
	int64 GrossReturnDue = 0;

	UPROPERTY(SaveGame)
	int64 SelectedWinProbabilityE8 = 0;

	UPROPERTY(SaveGame)
	FString PayoutFormula;

	UPROPERTY(SaveGame)
	FName Status;
};

USTRUCT()
struct FOddsWellMatchWinnerLossFinalizationRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString FinalizationCommandId;

	UPROPERTY(SaveGame)
	FString DecisionCommandId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString ResultCommandId;

	UPROPERTY(SaveGame)
	FString FinalizationSchema;

	UPROPERTY(SaveGame)
	FString FinalizationVersion;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	FString SelectedTeam;

	UPROPERTY(SaveGame)
	FString AuthoritativeWinner;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	FName Outcome;

	UPROPERTY(SaveGame)
	int64 GrossReturnApplied = 0;

	UPROPERTY(SaveGame)
	FName Status;

	UPROPERTY(SaveGame)
	int64 ObservedFinalBalance = 0;

	UPROPERTY(SaveGame)
	int32 ObservedLedgerEntryCount = 0;
};

USTRUCT()
struct FOddsWellMatchWinnerWinFinalizationRecord
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	FString FinalizationCommandId;

	UPROPERTY(SaveGame)
	FString DecisionCommandId;

	UPROPERTY(SaveGame)
	FString RequestCommandId;

	UPROPERTY(SaveGame)
	FString LockCommandId;

	UPROPERTY(SaveGame)
	FString ResultCommandId;

	UPROPERTY(SaveGame)
	FString FinalizationSchema;

	UPROPERTY(SaveGame)
	FString FinalizationVersion;

	UPROPERTY(SaveGame)
	FString OfferId;

	UPROPERTY(SaveGame)
	FString OfferVersion;

	UPROPERTY(SaveGame)
	FString SelectedTeam;

	UPROPERTY(SaveGame)
	FString AuthoritativeWinner;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	FName Outcome;

	UPROPERTY(SaveGame)
	int64 GrossReturnApplied = 0;

	UPROPERTY(SaveGame)
	FString PayoutLedgerCommandId;

	UPROPERTY(SaveGame)
	FName Status;

	UPROPERTY(SaveGame)
	int64 ObservedFinalBalance = 0;

	UPROPERTY(SaveGame)
	int32 ObservedLedgerEntryCount = 0;
};

UCLASS()
class ODDSWELL_API UOddsWellOddsBucksSaveGame final : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	int32 SchemaVersion = 12;

	UPROPERTY(SaveGame)
	TArray<FOddsWellOddsBucksEntry> Entries;

	UPROPERTY(SaveGame)
	int64 NextJobPayoutUnixSeconds = 0;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerRequestRecord> MatchWinnerRequests;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerLockRecord> MatchWinnerLocks;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerResultLinkRecord> MatchWinnerResultLinks;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> MatchWinnerSettlementDecisions;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> MatchWinnerLossFinalizations;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> MatchWinnerWinFinalizations;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerCanceledGameRecord> MatchWinnerCanceledGames;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> MatchWinnerVoidDecisions;

	UPROPERTY(SaveGame)
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> MatchWinnerVoidFinalizations;
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
ODDSWELL_API const FString& GetOddsWellUpcomingQaMatchWinnerRequestCommandId();
ODDSWELL_API int64 GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds();
ODDSWELL_API const FString& GetOddsWellUpcomingQaMatchWinnerLockCommandId();
ODDSWELL_API int64 GetOddsWellUpcomingQaMatchWinnerLockUnixSeconds();
ODDSWELL_API const FString& GetOddsWellUpcomingQaMatchWinnerCancellationCommandId();
ODDSWELL_API const FString& GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId();
ODDSWELL_API int64 GetOddsWellUpcomingQaMatchWinnerCancellationUnixSeconds();
ODDSWELL_API const FString& GetOddsWellUpcomingQaMatchWinnerVoidDecisionCommandId();
ODDSWELL_API const FString& GetOddsWellUpcomingQaMatchWinnerVoidFinalizationCommandId();
ODDSWELL_API bool FinalizeOddsWellMatchWinnerOfferIdentity(
	FOddsWellMatchWinnerOffer& InOutOffer,
	FString& OutCanonicalJson,
	FString& OutError);
ODDSWELL_API bool BuildOddsWellUpcomingQaMatchWinnerOffer(FOddsWellMatchWinnerOffer& OutOffer, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerRequestResult AcceptOddsWellUpcomingQaMatchWinnerRequest(const FOddsWellMatchWinnerOffer& Offer, const FString& RequestCommandId, const FString& OfferedTeam, int64 Stake, int64 AcceptedUnixSeconds, FOddsWellMatchWinnerRequestRecord& OutRecord, int64& OutBalance, FString& OutError);
ODDSWELL_API bool RunOddsWellUpcomingQaMatchWinnerAudit(int32& OutLedgerEntries, int32& OutRequests, int64& OutBalance, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerLockResult LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(FOddsWellMatchWinnerLockRecord& OutRecord, FString& OutError);
ODDSWELL_API bool RunOddsWellUpcomingQaMatchWinnerLockAudit(int32& OutLedgerEntries, int32& OutRequests, int32& OutLocks, int64& OutBalance, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerCanceledGameResult RecordOddsWellUpcomingQaMatchWinnerCancellation(FOddsWellMatchWinnerCanceledGameRecord& OutRecord, FString& OutError);
ODDSWELL_API bool RunOddsWellUpcomingQaMatchWinnerCancellationAudit(int32& OutLedgerEntries, int32& OutRequests, int32& OutLocks, int32& OutCancellations, int64& OutBalance, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerVoidDecisionResult DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(FOddsWellMatchWinnerVoidDecisionRecord& OutRecord, FString& OutError);
ODDSWELL_API bool RunOddsWellUpcomingQaMatchWinnerVoidDecisionAudit(int32& OutLedgerEntries, int32& OutRequests, int32& OutLocks, int32& OutCancellations, int32& OutVoidDecisions, int64& OutBalance, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerVoidFinalizationResult FinalizeOddsWellUpcomingQaMatchWinnerVoidRefund(FOddsWellMatchWinnerVoidFinalizationRecord& OutRecord, FString& OutError);
ODDSWELL_API bool RunOddsWellUpcomingQaMatchWinnerVoidFinalizationAudit(int32& OutLedgerEntries, int32& OutRequests, int32& OutLocks, int32& OutCancellations, int32& OutVoidDecisions, int32& OutVoidFinalizations, int64& OutBalance, FString& OutError);
ODDSWELL_API bool LoadOddsWellPendingQaMatchWinnerReceipt(FOddsWellPendingQaMatchWinnerReceipt& OutReceipt, FString& OutError);
ODDSWELL_API EOddsWellCanonicalPendingReceiptResult LoadOddsWellCanonicalPendingMatchWinnerReceiptEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	int64 OfferEligibleUnixSeconds,
	int64 ObservedServerUnixSeconds,
	bool bQaSlot,
	FOddsWellCanonicalPendingMatchWinnerReceipt& OutReceipt,
	FString& OutError);
ODDSWELL_API bool WriteOddsWellOddsBucksReconciliation(const FOddsWellOddsBucksLedger& Ledger, int64 NextJobPayoutUnixSeconds, int64 ObservedNowUnixSeconds, bool bQaProjection, FString& OutPath, FString& OutError);
ODDSWELL_API bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, int64 NextJobPayoutUnixSeconds, bool bQaSlot, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksLedger(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksState(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksWagerState(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksWagerEvidence(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks, TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksWagerDecisionState(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks, TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks, TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& OutMatchWinnerSettlementDecisions, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellOddsBucksWagerFinalizationState(bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests, TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks, TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks, TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& OutMatchWinnerSettlementDecisions, TArray<FOddsWellMatchWinnerLossFinalizationRecord>& OutMatchWinnerLossFinalizations, TArray<FOddsWellMatchWinnerWinFinalizationRecord>& OutMatchWinnerWinFinalizations, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellMatchWinnerCanceledGames(bool bQaSlot, TArray<FOddsWellMatchWinnerCanceledGameRecord>& OutCanceledGames, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellMatchWinnerVoidDecisions(bool bQaSlot, TArray<FOddsWellMatchWinnerVoidDecisionRecord>& OutVoidDecisions, bool& bOutFound, FString& OutError);
ODDSWELL_API bool LoadOddsWellMatchWinnerVoidFinalizations(bool bQaSlot, TArray<FOddsWellMatchWinnerVoidFinalizationRecord>& OutVoidFinalizations, bool& bOutFound, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerRequestResult AcceptOddsWellMatchWinnerRequest(const FOddsWellMatchWinnerOffer& Offer, const FString& RequestCommandId, const FString& OfferedTeam, int64 Stake, int64 AcceptedUnixSeconds, bool bQaSlot, FOddsWellMatchWinnerRequestRecord& OutRecord, int64& OutBalance, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerLockResult LockOddsWellMatchWinnerRequest(const FString& RequestCommandId, const FString& LockCommandId, int32 SeasonNumber, int32 GameNumber, int64 AuthoritativeGameStartUnixSeconds, bool bQaSlot, FOddsWellMatchWinnerLockRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerResultLinkResult LinkOddsWellMatchWinnerResult(const FString& ResultCommandId, const FString& RequestCommandId, const FString& LockCommandId, const FString& ResultSchema, const FString& ResultVersion, int32 SeasonNumber, int32 GameNumber, const FString& HomeTeam, const FString& AwayTeam, int32 HomeScore, int32 AwayScore, const FString& Winner, const FString& ReplaySealSha256, bool bQaSlot, FOddsWellMatchWinnerResultLinkRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerCanceledGameResult RecordOddsWellMatchWinnerCanceledGame(const FString& CancellationCommandId, const FString& CancellationEvidenceId, const FString& RequestCommandId, const FString& LockCommandId, const FString& DispositionSchema, const FString& DispositionVersion, int32 SeasonNumber, int32 GameNumber, int64 AuthoritativeCancellationUnixSeconds, FName ReasonCode, bool bQaSlot, FOddsWellMatchWinnerCanceledGameRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerVoidDecisionResult DecideOddsWellMatchWinnerVoidRefundDue(const FString& VoidDecisionCommandId, const FString& CancellationCommandId, const FString& CancellationEvidenceId, bool bQaSlot, FOddsWellMatchWinnerVoidDecisionRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerVoidFinalizationResult FinalizeOddsWellMatchWinnerVoidRefund(const FString& FinalizationCommandId, const FString& VoidDecisionCommandId, bool bQaSlot, FOddsWellMatchWinnerVoidFinalizationRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellMatchWinnerSettlement(const FString& DecisionCommandId, const FString& RequestCommandId, const FString& LockCommandId, const FString& ResultCommandId, bool bQaSlot, FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellMatchWinnerSettlement(const FOddsWellMatchWinnerOffer& ExactOffer, const FString& DecisionCommandId, const FString& RequestCommandId, const FString& LockCommandId, const FString& ResultCommandId, bool bQaSlot, FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerLossFinalizationResult FinalizeOddsWellMatchWinnerLoss(const FString& FinalizationCommandId, const FString& DecisionCommandId, bool bQaSlot, FOddsWellMatchWinnerLossFinalizationRecord& OutRecord, FString& OutError);
ODDSWELL_API EOddsWellMatchWinnerWinFinalizationResult FinalizeOddsWellMatchWinnerWin(const FString& FinalizationCommandId, const FString& DecisionCommandId, bool bQaSlot, FOddsWellMatchWinnerWinFinalizationRecord& OutRecord, FString& OutError);
ODDSWELL_API bool ResetOddsWellQaOddsBucksAndVerify(FString& OutError);
