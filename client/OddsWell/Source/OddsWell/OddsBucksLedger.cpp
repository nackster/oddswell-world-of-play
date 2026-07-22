#include "OddsBucksLedger.h"

#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/AutomationTest.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

#if PLATFORM_WINDOWS
#include "Windows/AllowWindowsPlatformTypes.h"
#include <bcrypt.h>
#include "Windows/HideWindowsPlatformTypes.h"
#pragma comment(lib, "bcrypt.lib")
#endif

#if WITH_DEV_AUTOMATION_TESTS
#include "Engine/StaticMesh.h"
#endif

namespace
{
constexpr int32 OddsBucksSchemaVersion = 8;
constexpr int32 OddsBucksUserIndex = 0;
constexpr int64 FirstJobPayout = 100;
constexpr int64 JobPayoutIntervalSeconds = 24 * 60 * 60;
constexpr int64 MatchWinnerProbabilityScale = 100000000;
constexpr int64 MatchWinnerMinimumStake = 10;
constexpr int64 MatchWinnerMaximumStake = 100;
constexpr int64 MatchWinnerStakeIncrement = 10;
const FString OddsBucksSlot(TEXT("OddsWellOddsBucks"));
const FString OddsBucksQaSlot(TEXT("OddsWellOddsBucksQA"));
const FString OddsBucksReconciliationFile(TEXT("OddsBucksReconciliation.json"));
const FString OddsBucksQaReconciliationFile(TEXT("OddsBucksReconciliationQA.json"));
const FString MatchWinnerReconciliationFile(TEXT("MatchWinnerReconciliation.json"));
const FString MatchWinnerQaReconciliationFile(TEXT("MatchWinnerReconciliationQA.json"));
const FString FirstJobCommandId(TEXT("job:placeholder_shift:first_payout:v1"));
const FName FirstJobReason(TEXT("placeholder_job_payout"));
const FName MatchWinnerStakeReason(TEXT("match_winner_stake"));
const FName MatchWinnerPayoutReason(TEXT("match_winner_payout"));
const FName AcceptedPendingLockStatus(TEXT("accepted_pending_lock"));
const FName MatchWinnerLockedDecision(TEXT("locked"));
const FString MatchWinnerOfferSchema(TEXT("oddswell-basketball-odds-offer-v1"));
const FString MatchWinnerOfferVersion(TEXT("basketball-match-winner-odds-v1"));
const FString MatchWinnerMarket(TEXT("match_winner"));
const FString OddsBucksCurrency(TEXT("odds_bucks"));
const FString MatchWinnerPredictionVersion(TEXT("phase0d4-v1"));
const FString MatchWinnerSnapshotVersion(TEXT("oddswell-public-pregame-v1"));
const FString MatchWinnerSourceModel(TEXT("public_elo_rotation"));
const FString MatchWinnerPayoutFormula(TEXT("floor(stake*100000000/win_probability_e8)"));
const FString ExactMatchWinnerOfferId(TEXT("9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459"));
const FString MatchWinnerResultSchema(TEXT("oddswell-sealed-match-winner-result-v1"));
const FString MatchWinnerResultVersion(TEXT("sealed-match-winner-result-v1"));
constexpr int32 SealedResultSeasonNumber = 1;
constexpr int32 SealedResultGameNumber = 1;
const FString SealedResultHomeTeam(TEXT("Harbor City Waves"));
const FString SealedResultAwayTeam(TEXT("Mesa Vista Sol"));
constexpr int32 SealedResultHomeScore = 101;
constexpr int32 SealedResultAwayScore = 104;
const FString SealedResultWinner(TEXT("Mesa Vista Sol"));
const FString SealedResultReplaySha(TEXT("00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75"));
const FString MatchWinnerSettlementDecisionSchema(TEXT("oddswell-match-winner-settlement-decision-v1"));
const FString MatchWinnerSettlementDecisionVersion(TEXT("match-winner-settlement-decision-v1"));
const FName MatchWinnerWonOutcome(TEXT("won"));
const FName MatchWinnerLostOutcome(TEXT("lost"));
const FName MatchWinnerDecidedPendingApplyStatus(TEXT("decided_pending_apply"));
const FString MatchWinnerLossFinalizationSchema(TEXT("oddswell-match-winner-loss-finalization-v1"));
const FString MatchWinnerLossFinalizationVersion(TEXT("match-winner-loss-finalization-v1"));
const FName MatchWinnerSettledLostStatus(TEXT("settled_lost"));
const FString MatchWinnerWinFinalizationSchema(TEXT("oddswell-match-winner-win-finalization-v1"));
const FString MatchWinnerWinFinalizationVersion(TEXT("match-winner-win-finalization-v1"));
const FName MatchWinnerSettledWonStatus(TEXT("settled_won"));
const FString MatchWinnerReconciliationSchema(TEXT("oddswell-match-winner-reconciliation-v1"));

const FString& GetOddsBucksSlot(const bool bQaSlot)
{
	return bQaSlot ? OddsBucksQaSlot : OddsBucksSlot;
}

FString GetOddsBucksReconciliationPath(const bool bQaProjection)
{
	return FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Admin"), bQaProjection ? OddsBucksQaReconciliationFile : OddsBucksReconciliationFile);
}

FString GetMatchWinnerReconciliationPath(const bool bQaProjection)
{
	return FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Admin"), bQaProjection ? MatchWinnerQaReconciliationFile : MatchWinnerReconciliationFile);
}

bool HasJobPayout(const FOddsWellOddsBucksLedger& Ledger)
{
	for (const FOddsWellOddsBucksEntry& Entry : Ledger.GetEntries())
	{
		if (Entry.Reason == FirstJobReason)
		{
			return true;
		}
	}
	return false;
}

bool IsLowerHexHash(const FString& Value)
{
	if (Value.Len() != 64)
	{
		return false;
	}
	for (const TCHAR Character : Value)
	{
		if (!FChar::IsHexDigit(Character) || (Character >= TEXT('A') && Character <= TEXT('F')))
		{
			return false;
		}
	}
	return true;
}

bool GetMatchWinnerOfferId(const FOddsWellMatchWinnerOffer& Offer, FString& OutOfferId, FString& OutError)
{
	FString CanonicalJson;
	const TSharedRef<TJsonWriter<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>> Writer =
		TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&CanonicalJson);
	Writer->WriteObjectStart();
	Writer->WriteValue(TEXT("away_team"), Offer.AwayTeam);
	Writer->WriteValue(TEXT("currency"), Offer.Currency);
	Writer->WriteValue(TEXT("game_number"), Offer.GameNumber);
	Writer->WriteValue(TEXT("home_team"), Offer.HomeTeam);
	Writer->WriteValue(TEXT("house_edge_bps"), Offer.HouseEdgeBps);
	Writer->WriteValue(TEXT("lock_unix"), Offer.LockUnixSeconds);
	Writer->WriteValue(TEXT("market"), Offer.Market);
	Writer->WriteValue(TEXT("maximum_stake"), Offer.MaximumStake);
	Writer->WriteValue(TEXT("minimum_stake"), Offer.MinimumStake);
	Writer->WriteValue(TEXT("offer_version"), Offer.OfferVersion);
	Writer->WriteValue(TEXT("payout_formula"), Offer.PayoutFormula);
	Writer->WriteValue(TEXT("schema"), Offer.Schema);
	Writer->WriteValue(TEXT("season_number"), Offer.SeasonNumber);
	Writer->WriteArrayStart(TEXT("selections"));
	for (const FOddsWellMatchWinnerSelection& Selection : Offer.Selections)
	{
		Writer->WriteObjectStart();
		Writer->WriteValue(TEXT("decimal_odds_e4"), Selection.DecimalOddsE4);
		Writer->WriteValue(TEXT("team"), Selection.Team);
		Writer->WriteValue(TEXT("win_probability_e8"), Selection.WinProbabilityE8);
		Writer->WriteObjectEnd();
	}
	Writer->WriteArrayEnd();
	Writer->WriteValue(TEXT("source_commitment_sha256"), Offer.SourceCommitmentSha256);
	Writer->WriteValue(TEXT("source_model"), Offer.SourceModel);
	Writer->WriteValue(TEXT("source_prediction_version"), Offer.SourcePredictionVersion);
	Writer->WriteValue(TEXT("source_snapshot_version"), Offer.SourceSnapshotVersion);
	Writer->WriteValue(TEXT("stake_increment"), Offer.StakeIncrement);
	Writer->WriteObjectEnd();
	if (!Writer->Close())
	{
		OutError = TEXT("The Match Winner offer identity could not be serialized.");
		return false;
	}
	const FTCHARToUTF8 Utf8(*CanonicalJson);
	uint8 Digest[32];
#if PLATFORM_WINDOWS
	BCRYPT_ALG_HANDLE Algorithm = nullptr;
	const NTSTATUS OpenStatus = ::BCryptOpenAlgorithmProvider(&Algorithm, BCRYPT_SHA256_ALGORITHM, nullptr, 0);
	const NTSTATUS HashStatus = OpenStatus >= 0
		? ::BCryptHash(Algorithm, nullptr, 0, reinterpret_cast<PUCHAR>(const_cast<ANSICHAR*>(Utf8.Get())), Utf8.Length(), Digest, UE_ARRAY_COUNT(Digest))
		: OpenStatus;
	if (Algorithm)
	{
		::BCryptCloseAlgorithmProvider(Algorithm, 0);
	}
	if (OpenStatus < 0 || HashStatus < 0)
	{
		OutError = TEXT("The Match Winner offer identity could not be hashed.");
		return false;
	}
	OutOfferId = BytesToHex(Digest, UE_ARRAY_COUNT(Digest)).ToLower();
#else
	OutError = TEXT("The Match Winner offer identity is not implemented for this platform.");
	return false;
#endif
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerOffer(const FOddsWellMatchWinnerOffer& Offer, FString& OutError)
{
	if (Offer.Schema != MatchWinnerOfferSchema
		|| Offer.OfferVersion != MatchWinnerOfferVersion
		|| Offer.Market != MatchWinnerMarket
		|| Offer.Currency != OddsBucksCurrency
		|| Offer.SourcePredictionVersion != MatchWinnerPredictionVersion
		|| Offer.SourceSnapshotVersion != MatchWinnerSnapshotVersion
		|| Offer.SourceModel != MatchWinnerSourceModel
		|| Offer.MinimumStake != MatchWinnerMinimumStake
		|| Offer.MaximumStake != MatchWinnerMaximumStake
		|| Offer.StakeIncrement != MatchWinnerStakeIncrement
		|| Offer.HouseEdgeBps != 0
		|| Offer.PayoutFormula != MatchWinnerPayoutFormula)
	{
		OutError = TEXT("The Match Winner offer uses an unsupported contract.");
		return false;
	}
	if (!IsLowerHexHash(Offer.SourceCommitmentSha256)
		|| Offer.SeasonNumber <= 0
		|| Offer.GameNumber <= 0
		|| Offer.HomeTeam.IsEmpty()
		|| Offer.AwayTeam.IsEmpty()
		|| Offer.HomeTeam == Offer.AwayTeam
		|| Offer.LockUnixSeconds <= 0
		|| Offer.Selections.Num() != 2
		|| Offer.Selections[0].Team != Offer.HomeTeam
		|| Offer.Selections[1].Team != Offer.AwayTeam)
	{
		OutError = TEXT("The Match Winner offer has invalid source, game, lock, or team identity.");
		return false;
	}
	int64 ProbabilityTotal = 0;
	for (const FOddsWellMatchWinnerSelection& Selection : Offer.Selections)
	{
		if (Selection.WinProbabilityE8 <= 0
			|| Selection.WinProbabilityE8 >= MatchWinnerProbabilityScale
			|| Selection.DecimalOddsE4 != MatchWinnerProbabilityScale * 10000 / Selection.WinProbabilityE8)
		{
			OutError = TEXT("The Match Winner offer has an invalid selection price.");
			return false;
		}
		ProbabilityTotal += Selection.WinProbabilityE8;
	}
	FString ExpectedOfferId;
	if (ProbabilityTotal != MatchWinnerProbabilityScale
		|| !IsLowerHexHash(Offer.OfferId)
		|| !GetMatchWinnerOfferId(Offer, ExpectedOfferId, OutError)
		|| Offer.OfferId != ExpectedOfferId)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The Match Winner offer identity does not verify.");
		}
		return false;
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerRequests(const FOddsWellOddsBucksLedger& Ledger, const TArray<FOddsWellMatchWinnerRequestRecord>& Requests, FString& OutError)
{
	TSet<FString> RequestIds;
	for (int32 Index = 0; Index < Requests.Num(); ++Index)
	{
		const FOddsWellMatchWinnerRequestRecord& Request = Requests[Index];
		if (Request.RequestCommandId.TrimStartAndEnd().IsEmpty()
			|| Request.StakeLedgerCommandId != Request.RequestCommandId
			|| RequestIds.Contains(Request.RequestCommandId)
			|| !IsLowerHexHash(Request.OfferId)
			|| Request.OfferVersion != MatchWinnerOfferVersion
			|| Request.SeasonNumber <= 0
			|| Request.GameNumber <= 0
			|| Request.HomeTeam.IsEmpty()
			|| Request.AwayTeam.IsEmpty()
			|| Request.HomeTeam == Request.AwayTeam
			|| (Request.OfferedTeam != Request.HomeTeam && Request.OfferedTeam != Request.AwayTeam)
			|| Request.Stake < MatchWinnerMinimumStake
			|| Request.Stake > MatchWinnerMaximumStake
			|| Request.Stake % MatchWinnerStakeIncrement != 0
			|| Request.AcceptedUnixSeconds <= 0
			|| Request.AcceptedUnixSeconds >= Request.LockUnixSeconds
			|| Request.Status != AcceptedPendingLockStatus)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner request at index %d."), Index);
			return false;
		}
		const FOddsWellOddsBucksEntry* StakeEntry = Ledger.GetEntries().FindByPredicate(
			[&Request](const FOddsWellOddsBucksEntry& Entry) { return Entry.CommandId == Request.StakeLedgerCommandId; });
		if (!StakeEntry || StakeEntry->Delta != -Request.Stake || StakeEntry->Reason != MatchWinnerStakeReason)
		{
			OutError = FString::Printf(TEXT("Match Winner request %d is not linked to its exact stake debit."), Index);
			return false;
		}
		RequestIds.Add(Request.RequestCommandId);
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerLocks(
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	FString& OutError)
{
	TSet<FString> LockIds;
	TSet<FString> LockedRequestIds;
	for (int32 Index = 0; Index < Locks.Num(); ++Index)
	{
		const FOddsWellMatchWinnerLockRecord& Lock = Locks[Index];
		const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
			[&Lock](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Lock.RequestCommandId;
			});
		if (Lock.LockCommandId.TrimStartAndEnd().IsEmpty()
			|| Lock.RequestCommandId.TrimStartAndEnd().IsEmpty()
			|| Lock.LockCommandId == Lock.RequestCommandId
			|| LockIds.Contains(Lock.LockCommandId)
			|| LockedRequestIds.Contains(Lock.RequestCommandId)
			|| !Request
			|| Request->Status != AcceptedPendingLockStatus
			|| Lock.SeasonNumber != Request->SeasonNumber
			|| Lock.GameNumber != Request->GameNumber
			|| Lock.AuthoritativeGameStartUnixSeconds != Request->LockUnixSeconds
			|| Lock.LockUnixSeconds != Request->LockUnixSeconds
			|| Lock.Decision != MatchWinnerLockedDecision)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner lock at index %d."), Index);
			return false;
		}
		LockIds.Add(Lock.LockCommandId);
		LockedRequestIds.Add(Lock.RequestCommandId);
	}
	OutError.Reset();
	return true;
}

bool IsExactSealedMatchWinnerResult(const FOddsWellMatchWinnerResultLinkRecord& Result)
{
	const FString DerivedWinner = Result.HomeScore > Result.AwayScore ? Result.HomeTeam : Result.AwayTeam;
	return Result.ResultSchema == MatchWinnerResultSchema
		&& Result.ResultVersion == MatchWinnerResultVersion
		&& Result.SeasonNumber == SealedResultSeasonNumber
		&& Result.GameNumber == SealedResultGameNumber
		&& Result.HomeTeam == SealedResultHomeTeam
		&& Result.AwayTeam == SealedResultAwayTeam
		&& Result.HomeScore == SealedResultHomeScore
		&& Result.AwayScore == SealedResultAwayScore
		&& Result.HomeScore != Result.AwayScore
		&& Result.Winner == DerivedWinner
		&& Result.Winner == SealedResultWinner
		&& Result.ReplaySealSha256 == SealedResultReplaySha
		&& IsLowerHexHash(Result.ReplaySealSha256);
}

bool ValidateMatchWinnerResultLinks(
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	FString& OutError)
{
	TSet<FString> ResultIds;
	TSet<FString> LinkedRequestIds;
	for (int32 Index = 0; Index < Results.Num(); ++Index)
	{
		const FOddsWellMatchWinnerResultLinkRecord& Result = Results[Index];
		const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
			[&Result](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Result.RequestCommandId;
			});
		const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
			[&Result](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Result.LockCommandId;
			});
		if (Result.ResultCommandId.TrimStartAndEnd().IsEmpty()
			|| Result.RequestCommandId.TrimStartAndEnd().IsEmpty()
			|| Result.LockCommandId.TrimStartAndEnd().IsEmpty()
			|| Result.ResultCommandId == Result.RequestCommandId
			|| Result.ResultCommandId == Result.LockCommandId
			|| ResultIds.Contains(Result.ResultCommandId)
			|| LinkedRequestIds.Contains(Result.RequestCommandId)
			|| !Request
			|| !Lock
			|| Lock->RequestCommandId != Result.RequestCommandId
			|| Result.SeasonNumber != Request->SeasonNumber
			|| Result.GameNumber != Request->GameNumber
			|| Result.HomeTeam != Request->HomeTeam
			|| Result.AwayTeam != Request->AwayTeam
			|| Result.SeasonNumber != Lock->SeasonNumber
			|| Result.GameNumber != Lock->GameNumber
			|| !IsExactSealedMatchWinnerResult(Result))
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner result link at index %d."), Index);
			return false;
		}
		ResultIds.Add(Result.ResultCommandId);
		LinkedRequestIds.Add(Result.RequestCommandId);
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerSettlementDecisions(
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	FString& OutError)
{
	TSet<FString> DecisionIds;
	TSet<FString> DecidedRequestIds;
	for (int32 Index = 0; Index < Decisions.Num(); ++Index)
	{
		const FOddsWellMatchWinnerSettlementDecisionRecord& Decision = Decisions[Index];
		const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
			[&Decision](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Decision.RequestCommandId;
			});
		const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
			[&Decision](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Decision.LockCommandId;
			});
		const FOddsWellMatchWinnerResultLinkRecord* Result = Results.FindByPredicate(
			[&Decision](const FOddsWellMatchWinnerResultLinkRecord& Candidate)
			{
				return Candidate.ResultCommandId == Decision.ResultCommandId;
			});
		const FName DerivedOutcome = Request && Result && Request->OfferedTeam == Result->Winner
			? MatchWinnerWonOutcome
			: MatchWinnerLostOutcome;
		const bool bExactWin = DerivedOutcome == MatchWinnerWonOutcome;
		const int64 ExpectedWinProbabilityE8 = bExactWin ? 40000000 : 0;
		const int64 ExpectedGrossReturnDue = bExactWin && Request
			? Request->Stake * MatchWinnerProbabilityScale / ExpectedWinProbabilityE8
			: 0;
		if (Decision.DecisionCommandId.TrimStartAndEnd().IsEmpty()
			|| Decision.RequestCommandId.TrimStartAndEnd().IsEmpty()
			|| Decision.LockCommandId.TrimStartAndEnd().IsEmpty()
			|| Decision.ResultCommandId.TrimStartAndEnd().IsEmpty()
			|| Decision.DecisionCommandId == Decision.RequestCommandId
			|| Decision.DecisionCommandId == Decision.LockCommandId
			|| Decision.DecisionCommandId == Decision.ResultCommandId
			|| DecisionIds.Contains(Decision.DecisionCommandId)
			|| DecidedRequestIds.Contains(Decision.RequestCommandId)
			|| !Request
			|| !Lock
			|| !Result
			|| Lock->RequestCommandId != Decision.RequestCommandId
			|| Result->RequestCommandId != Decision.RequestCommandId
			|| Result->LockCommandId != Decision.LockCommandId
			|| Decision.DecisionSchema != MatchWinnerSettlementDecisionSchema
			|| Decision.DecisionVersion != MatchWinnerSettlementDecisionVersion
			|| Decision.OfferId != Request->OfferId
			|| Decision.OfferVersion != Request->OfferVersion
			|| Decision.SelectedTeam != Request->OfferedTeam
			|| Decision.AuthoritativeWinner != Result->Winner
			|| Decision.Stake != Request->Stake
			|| Decision.Outcome != DerivedOutcome
			|| (bExactWin && (Request->OfferId != ExactMatchWinnerOfferId || Request->OfferedTeam != SealedResultAwayTeam || Request->Stake != 40))
			|| Decision.GrossReturnDue != ExpectedGrossReturnDue
			|| Decision.SelectedWinProbabilityE8 != ExpectedWinProbabilityE8
			|| Decision.PayoutFormula != (bExactWin ? MatchWinnerPayoutFormula : FString())
			|| Decision.Status != MatchWinnerDecidedPendingApplyStatus)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner settlement decision at index %d."), Index);
			return false;
		}
		DecisionIds.Add(Decision.DecisionCommandId);
		DecidedRequestIds.Add(Decision.RequestCommandId);
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerLossFinalizations(
	const FOddsWellOddsBucksLedger& Ledger,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& Finalizations,
	FString& OutError)
{
	TSet<FString> FinalizationIds;
	TSet<FString> FinalizedDecisionIds;
	for (int32 Index = 0; Index < Finalizations.Num(); ++Index)
	{
		const FOddsWellMatchWinnerLossFinalizationRecord& Finalization = Finalizations[Index];
		const FOddsWellMatchWinnerSettlementDecisionRecord* Decision = Decisions.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerSettlementDecisionRecord& Candidate)
			{
				return Candidate.DecisionCommandId == Finalization.DecisionCommandId;
			});
		const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Finalization.RequestCommandId;
			});
		const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Finalization.LockCommandId;
			});
		const FOddsWellMatchWinnerResultLinkRecord* Result = Results.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerResultLinkRecord& Candidate)
			{
				return Candidate.ResultCommandId == Finalization.ResultCommandId;
			});
		if (Finalization.FinalizationCommandId.TrimStartAndEnd().IsEmpty()
			|| Finalization.DecisionCommandId.TrimStartAndEnd().IsEmpty()
			|| Finalization.FinalizationCommandId == Finalization.DecisionCommandId
			|| Finalization.FinalizationCommandId == Finalization.RequestCommandId
			|| Finalization.FinalizationCommandId == Finalization.LockCommandId
			|| Finalization.FinalizationCommandId == Finalization.ResultCommandId
			|| FinalizationIds.Contains(Finalization.FinalizationCommandId)
			|| FinalizedDecisionIds.Contains(Finalization.DecisionCommandId)
			|| !Decision
			|| !Request
			|| !Lock
			|| !Result
			|| Decision->RequestCommandId != Finalization.RequestCommandId
			|| Decision->LockCommandId != Finalization.LockCommandId
			|| Decision->ResultCommandId != Finalization.ResultCommandId
			|| Lock->RequestCommandId != Finalization.RequestCommandId
			|| Result->RequestCommandId != Finalization.RequestCommandId
			|| Result->LockCommandId != Finalization.LockCommandId
			|| Finalization.FinalizationSchema != MatchWinnerLossFinalizationSchema
			|| Finalization.FinalizationVersion != MatchWinnerLossFinalizationVersion
			|| Decision->Outcome != MatchWinnerLostOutcome
			|| Decision->GrossReturnDue != 0
			|| Decision->Status != MatchWinnerDecidedPendingApplyStatus
			|| Finalization.OfferId != Decision->OfferId
			|| Finalization.OfferVersion != Decision->OfferVersion
			|| Finalization.SelectedTeam != Decision->SelectedTeam
			|| Finalization.AuthoritativeWinner != Decision->AuthoritativeWinner
			|| Finalization.Stake != Decision->Stake
			|| Finalization.Outcome != MatchWinnerLostOutcome
			|| Finalization.GrossReturnApplied != 0
			|| Finalization.Status != MatchWinnerSettledLostStatus
			|| Finalization.ObservedFinalBalance != Ledger.GetBalance()
			|| Finalization.ObservedLedgerEntryCount != Ledger.GetEntries().Num()
			|| Finalization.ObservedFinalBalance != 60
			|| Finalization.ObservedLedgerEntryCount != 2)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner loss finalization at index %d."), Index);
			return false;
		}
		FinalizationIds.Add(Finalization.FinalizationCommandId);
		FinalizedDecisionIds.Add(Finalization.DecisionCommandId);
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerWinFinalizations(
	const FOddsWellOddsBucksLedger& Ledger,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	FString& OutError)
{
	TSet<FString> FinalizationIds;
	TSet<FString> FinalizedDecisionIds;
	for (int32 Index = 0; Index < WinFinalizations.Num(); ++Index)
	{
		const FOddsWellMatchWinnerWinFinalizationRecord& Finalization = WinFinalizations[Index];
		const FOddsWellMatchWinnerSettlementDecisionRecord* Decision = Decisions.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerSettlementDecisionRecord& Candidate)
			{
				return Candidate.DecisionCommandId == Finalization.DecisionCommandId;
			});
		const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Finalization.RequestCommandId;
			});
		const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Finalization.LockCommandId;
			});
		const FOddsWellMatchWinnerResultLinkRecord* Result = Results.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerResultLinkRecord& Candidate)
			{
				return Candidate.ResultCommandId == Finalization.ResultCommandId;
			});
		const FOddsWellOddsBucksEntry* Payout = Ledger.GetEntries().FindByPredicate(
			[&Finalization](const FOddsWellOddsBucksEntry& Entry)
			{
				return Entry.CommandId == Finalization.PayoutLedgerCommandId;
			});
		if (Finalization.FinalizationCommandId.TrimStartAndEnd().IsEmpty()
			|| Finalization.DecisionCommandId.TrimStartAndEnd().IsEmpty()
			|| Finalization.FinalizationCommandId == Finalization.DecisionCommandId
			|| Finalization.FinalizationCommandId == Finalization.RequestCommandId
			|| Finalization.FinalizationCommandId == Finalization.LockCommandId
			|| Finalization.FinalizationCommandId == Finalization.ResultCommandId
			|| Finalization.PayoutLedgerCommandId != Finalization.FinalizationCommandId
			|| FinalizationIds.Contains(Finalization.FinalizationCommandId)
			|| FinalizedDecisionIds.Contains(Finalization.DecisionCommandId)
			|| LossFinalizations.ContainsByPredicate(
				[&Finalization](const FOddsWellMatchWinnerLossFinalizationRecord& Loss)
				{
					return Loss.DecisionCommandId == Finalization.DecisionCommandId;
				})
			|| !Decision
			|| !Request
			|| !Lock
			|| !Result
			|| !Payout
			|| Decision->RequestCommandId != Finalization.RequestCommandId
			|| Decision->LockCommandId != Finalization.LockCommandId
			|| Decision->ResultCommandId != Finalization.ResultCommandId
			|| Lock->RequestCommandId != Finalization.RequestCommandId
			|| Result->RequestCommandId != Finalization.RequestCommandId
			|| Result->LockCommandId != Finalization.LockCommandId
			|| Finalization.FinalizationSchema != MatchWinnerWinFinalizationSchema
			|| Finalization.FinalizationVersion != MatchWinnerWinFinalizationVersion
			|| Decision->OfferId != ExactMatchWinnerOfferId
			|| Decision->Outcome != MatchWinnerWonOutcome
			|| Decision->GrossReturnDue != 100
			|| Decision->SelectedWinProbabilityE8 != 40000000
			|| Decision->PayoutFormula != MatchWinnerPayoutFormula
			|| Decision->Status != MatchWinnerDecidedPendingApplyStatus
			|| Finalization.OfferId != Decision->OfferId
			|| Finalization.OfferVersion != Decision->OfferVersion
			|| Finalization.SelectedTeam != Decision->SelectedTeam
			|| Finalization.AuthoritativeWinner != Decision->AuthoritativeWinner
			|| Finalization.Stake != Decision->Stake
			|| Finalization.Outcome != MatchWinnerWonOutcome
			|| Finalization.GrossReturnApplied != 100
			|| Finalization.Status != MatchWinnerSettledWonStatus
			|| Request->OfferedTeam != SealedResultAwayTeam
			|| Request->Stake != 40
			|| Result->Winner != SealedResultAwayTeam
			|| Payout->Sequence != 3
			|| Payout->Delta != 100
			|| Payout->BalanceAfter != 160
			|| Payout->Reason != MatchWinnerPayoutReason
			|| Finalization.ObservedFinalBalance != Ledger.GetBalance()
			|| Finalization.ObservedLedgerEntryCount != Ledger.GetEntries().Num()
			|| Finalization.ObservedFinalBalance != 160
			|| Finalization.ObservedLedgerEntryCount != 3)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner win finalization at index %d."), Index);
			return false;
		}
		FinalizationIds.Add(Finalization.FinalizationCommandId);
		FinalizedDecisionIds.Add(Finalization.DecisionCommandId);
	}
	OutError.Reset();
	return true;
}

bool ValidateOddsBucksSave(
	const UObject* SaveObject,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
	TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks,
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& OutMatchWinnerSettlementDecisions,
	TArray<FOddsWellMatchWinnerLossFinalizationRecord>& OutMatchWinnerLossFinalizations,
	TArray<FOddsWellMatchWinnerWinFinalizationRecord>& OutMatchWinnerWinFinalizations,
	bool& bOutNeedsMigration,
	FString& OutError)
{
	const UOddsWellOddsBucksSaveGame* Record = Cast<UOddsWellOddsBucksSaveGame>(SaveObject);
	if (!Record)
	{
		OutError = TEXT("The Odds Bucks save is not the expected object type.");
		return false;
	}
	if (Record->SchemaVersion < 1 || Record->SchemaVersion > OddsBucksSchemaVersion)
	{
		OutError = FString::Printf(TEXT("Unsupported Odds Bucks schema version: %d"), Record->SchemaVersion);
		return false;
	}
	if (!OutLedger.Restore(Record->Entries, OutError))
	{
		return false;
	}
	bOutNeedsMigration = Record->SchemaVersion != OddsBucksSchemaVersion;
	OutNextJobPayoutUnixSeconds = Record->SchemaVersion == 1 && HasJobPayout(OutLedger)
		? FDateTime::UtcNow().ToUnixTimestamp() + JobPayoutIntervalSeconds
		: Record->NextJobPayoutUnixSeconds;
	OutMatchWinnerRequests = Record->SchemaVersion >= 3
		? Record->MatchWinnerRequests
		: TArray<FOddsWellMatchWinnerRequestRecord>();
	OutMatchWinnerLocks = Record->SchemaVersion >= 4
		? Record->MatchWinnerLocks
		: TArray<FOddsWellMatchWinnerLockRecord>();
	OutMatchWinnerResultLinks = Record->SchemaVersion >= 5
		? Record->MatchWinnerResultLinks
		: TArray<FOddsWellMatchWinnerResultLinkRecord>();
	OutMatchWinnerSettlementDecisions = Record->SchemaVersion >= 6
		? Record->MatchWinnerSettlementDecisions
		: TArray<FOddsWellMatchWinnerSettlementDecisionRecord>();
	OutMatchWinnerLossFinalizations = Record->SchemaVersion >= 7
		? Record->MatchWinnerLossFinalizations
		: TArray<FOddsWellMatchWinnerLossFinalizationRecord>();
	OutMatchWinnerWinFinalizations = Record->SchemaVersion >= 8
		? Record->MatchWinnerWinFinalizations
		: TArray<FOddsWellMatchWinnerWinFinalizationRecord>();
	if (OutNextJobPayoutUnixSeconds < 0
		|| (HasJobPayout(OutLedger) && OutNextJobPayoutUnixSeconds == 0)
		|| (!HasJobPayout(OutLedger) && OutNextJobPayoutUnixSeconds != 0))
	{
		OutError = TEXT("The Odds Bucks job payout schedule is inconsistent with its ledger.");
		return false;
	}
	if (!ValidateMatchWinnerRequests(OutLedger, OutMatchWinnerRequests, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerLocks(OutMatchWinnerRequests, OutMatchWinnerLocks, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerResultLinks(OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerSettlementDecisions(OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutMatchWinnerSettlementDecisions, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerLossFinalizations(OutLedger, OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutMatchWinnerSettlementDecisions, OutMatchWinnerLossFinalizations, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerWinFinalizations(OutLedger, OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutMatchWinnerSettlementDecisions, OutMatchWinnerLossFinalizations, OutMatchWinnerWinFinalizations, OutError))
	{
		return false;
	}
	OutError.Reset();
	return true;
}
}

EOddsWellOddsBucksAppendResult FOddsWellOddsBucksLedger::Append(const FString& CommandId, const int64 Delta, const FName Reason)
{
	if (CommandId.TrimStartAndEnd().IsEmpty() || Reason.IsNone() || Delta == 0)
	{
		return EOddsWellOddsBucksAppendResult::Rejected;
	}

	if (const int32* ExistingIndex = CommandIndexes.Find(CommandId))
	{
		const FOddsWellOddsBucksEntry& Existing = Entries[*ExistingIndex];
		return Existing.Delta == Delta && Existing.Reason == Reason
			? EOddsWellOddsBucksAppendResult::Duplicate
			: EOddsWellOddsBucksAppendResult::Rejected;
	}

	if ((Delta < 0 && (Delta == TNumericLimits<int64>::Lowest() || -Delta > Balance))
		|| (Delta > 0 && Balance > TNumericLimits<int64>::Max() - Delta))
	{
		return EOddsWellOddsBucksAppendResult::Rejected;
	}

	Balance += Delta;
	FOddsWellOddsBucksEntry& Entry = Entries.AddDefaulted_GetRef();
	Entry.Sequence = Entries.Num();
	Entry.CommandId = CommandId;
	Entry.Delta = Delta;
	Entry.BalanceAfter = Balance;
	Entry.Reason = Reason;
	CommandIndexes.Add(CommandId, Entries.Num() - 1);
	return EOddsWellOddsBucksAppendResult::Applied;
}

bool FOddsWellOddsBucksLedger::Restore(const TArray<FOddsWellOddsBucksEntry>& SavedEntries, FString& OutError)
{
	FOddsWellOddsBucksLedger Candidate;
	for (int32 Index = 0; Index < SavedEntries.Num(); ++Index)
	{
		const FOddsWellOddsBucksEntry& Saved = SavedEntries[Index];
		if (Saved.Sequence != Index + 1
			|| Candidate.Append(Saved.CommandId, Saved.Delta, Saved.Reason) != EOddsWellOddsBucksAppendResult::Applied
			|| Candidate.GetEntries().Last().BalanceAfter != Saved.BalanceAfter)
		{
			OutError = FString::Printf(TEXT("Invalid Odds Bucks ledger entry at index %d."), Index);
			return false;
		}
	}
	*this = MoveTemp(Candidate);
	OutError.Reset();
	return true;
}

int64 GetOddsWellFirstJobPayout()
{
	return FirstJobPayout;
}

int64 GetOddsWellJobPayoutIntervalSeconds()
{
	return JobPayoutIntervalSeconds;
}

const FString& GetOddsWellFirstJobCommandId()
{
	return FirstJobCommandId;
}

FName GetOddsWellFirstJobReason()
{
	return FirstJobReason;
}

bool UseOddsWellOddsBucksQaSlot()
{
	return FParse::Param(FCommandLine::Get(), TEXT("JobQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQaVerify"));
}

bool WriteOddsWellOddsBucksReconciliation(const FOddsWellOddsBucksLedger& Ledger, const int64 NextJobPayoutUnixSeconds, const int64 ObservedNowUnixSeconds, const bool bQaProjection, FString& OutPath, FString& OutError)
{
	FOddsWellOddsBucksLedger Validated;
	if (!Validated.Restore(Ledger.GetEntries(), OutError)
		|| ObservedNowUnixSeconds <= 0
		|| NextJobPayoutUnixSeconds < 0
		|| (HasJobPayout(Validated) && NextJobPayoutUnixSeconds == 0)
		|| (!HasJobPayout(Validated) && NextJobPayoutUnixSeconds != 0))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The Odds Bucks reconciliation inputs are inconsistent.");
		}
		return false;
	}

	const TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
	Root->SetStringField(TEXT("schema"), TEXT("oddswell-odds-bucks-reconciliation-v1"));
	Root->SetStringField(TEXT("generated_at_utc"), FDateTime::UtcNow().ToIso8601());
	Root->SetStringField(TEXT("authority"), TEXT("server"));
	Root->SetStringField(TEXT("currency"), TEXT("odds_bucks"));
	Root->SetStringField(TEXT("profile_scope"), TEXT("machine_local"));
	Root->SetStringField(TEXT("time_authority"), TEXT("local_machine_utc"));
	Root->SetBoolField(TEXT("read_only_projection"), true);
	Root->SetBoolField(TEXT("qa"), bQaProjection);
	Root->SetNumberField(TEXT("observed_now_unix"), static_cast<double>(ObservedNowUnixSeconds));
	Root->SetNumberField(TEXT("balance"), static_cast<double>(Validated.GetBalance()));
	Root->SetNumberField(TEXT("entry_count"), Validated.GetEntries().Num());
	Root->SetNumberField(TEXT("next_job_payout_unix"), static_cast<double>(NextJobPayoutUnixSeconds));
	Root->SetNumberField(TEXT("job_payout"), static_cast<double>(FirstJobPayout));
	Root->SetNumberField(TEXT("payout_interval_seconds"), static_cast<double>(JobPayoutIntervalSeconds));
	Root->SetBoolField(TEXT("accumulation"), true);
	Root->SetBoolField(TEXT("allowance"), false);

	TArray<TSharedPtr<FJsonValue>> EntryValues;
	for (const FOddsWellOddsBucksEntry& Entry : Validated.GetEntries())
	{
		const TSharedRef<FJsonObject> EntryObject = MakeShared<FJsonObject>();
		EntryObject->SetNumberField(TEXT("sequence"), static_cast<double>(Entry.Sequence));
		EntryObject->SetStringField(TEXT("command_id"), Entry.CommandId);
		EntryObject->SetNumberField(TEXT("delta"), static_cast<double>(Entry.Delta));
		EntryObject->SetStringField(TEXT("reason"), Entry.Reason.ToString());
		EntryObject->SetNumberField(TEXT("balance_after"), static_cast<double>(Entry.BalanceAfter));
		EntryValues.Add(MakeShared<FJsonValueObject>(EntryObject));
	}
	Root->SetArrayField(TEXT("entries"), EntryValues);

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
	if (!FJsonSerializer::Serialize(Root, Writer))
	{
		OutError = TEXT("The Odds Bucks reconciliation projection could not be serialized.");
		return false;
	}
	OutPath = GetOddsBucksReconciliationPath(bQaProjection);
	IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
	const FString TemporaryPath = OutPath + TEXT(".tmp");
	if (!FFileHelper::SaveStringToFile(Json, *TemporaryPath)
		|| !IFileManager::Get().Move(*OutPath, *TemporaryPath, true, true, false, true))
	{
		IFileManager::Get().Delete(*TemporaryPath, false, true, true);
		OutError = TEXT("The Odds Bucks reconciliation projection could not be written atomically.");
		return false;
	}
	OutError.Reset();
	return true;
}

namespace
{
bool WriteMatchWinnerReconciliationFromValidatedState(
	const FOddsWellOddsBucksLedger& Ledger,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	const bool bQaProjection,
	FString& OutError)
{
	if (Requests.Num() != 1
		|| Locks.Num() != 1
		|| Results.Num() != 1
		|| Decisions.Num() != 1
		|| LossFinalizations.Num() + WinFinalizations.Num() != 1)
	{
		OutError = TEXT("The Match Winner reconciliation requires one complete exact finalized chain.");
		return false;
	}
	const FOddsWellMatchWinnerRequestRecord& Request = Requests[0];
	const FOddsWellMatchWinnerLockRecord& Lock = Locks[0];
	const FOddsWellMatchWinnerResultLinkRecord& Result = Results[0];
	const FOddsWellMatchWinnerSettlementDecisionRecord& Decision = Decisions[0];
	const bool bWin = WinFinalizations.Num() == 1;
	FString FinalizationCommandId;
	FString FinalizationDecisionCommandId;
	FString FinalizationRequestCommandId;
	FString FinalizationLockCommandId;
	FString FinalizationResultCommandId;
	FString FinalizationSchema;
	FString FinalizationVersion;
	FString FinalizationOfferId;
	FString FinalizationOfferVersion;
	FName FinalizationStatus;
	int64 GrossReturnApplied = 0;
	const FOddsWellOddsBucksEntry* PayoutEntry = nullptr;
	if (bWin)
	{
		const FOddsWellMatchWinnerWinFinalizationRecord& Finalization = WinFinalizations[0];
		FinalizationCommandId = Finalization.FinalizationCommandId;
		FinalizationDecisionCommandId = Finalization.DecisionCommandId;
		FinalizationRequestCommandId = Finalization.RequestCommandId;
		FinalizationLockCommandId = Finalization.LockCommandId;
		FinalizationResultCommandId = Finalization.ResultCommandId;
		FinalizationSchema = Finalization.FinalizationSchema;
		FinalizationVersion = Finalization.FinalizationVersion;
		FinalizationOfferId = Finalization.OfferId;
		FinalizationOfferVersion = Finalization.OfferVersion;
		FinalizationStatus = Finalization.Status;
		GrossReturnApplied = Finalization.GrossReturnApplied;
		PayoutEntry = Ledger.GetEntries().FindByPredicate(
			[&Finalization](const FOddsWellOddsBucksEntry& Entry)
			{
				return Entry.CommandId == Finalization.PayoutLedgerCommandId;
			});
	}
	else
	{
		const FOddsWellMatchWinnerLossFinalizationRecord& Finalization = LossFinalizations[0];
		FinalizationCommandId = Finalization.FinalizationCommandId;
		FinalizationDecisionCommandId = Finalization.DecisionCommandId;
		FinalizationRequestCommandId = Finalization.RequestCommandId;
		FinalizationLockCommandId = Finalization.LockCommandId;
		FinalizationResultCommandId = Finalization.ResultCommandId;
		FinalizationSchema = Finalization.FinalizationSchema;
		FinalizationVersion = Finalization.FinalizationVersion;
		FinalizationOfferId = Finalization.OfferId;
		FinalizationOfferVersion = Finalization.OfferVersion;
		FinalizationStatus = Finalization.Status;
		GrossReturnApplied = Finalization.GrossReturnApplied;
	}
	const FOddsWellOddsBucksEntry* StakeEntry = Ledger.GetEntries().FindByPredicate(
		[&Request](const FOddsWellOddsBucksEntry& Entry)
		{
			return Entry.CommandId == Request.StakeLedgerCommandId;
		});
	if (!StakeEntry
		|| Request.Stake != 40
		|| StakeEntry->Sequence != 2
		|| StakeEntry->Delta != -40
		|| StakeEntry->Reason != MatchWinnerStakeReason
		|| StakeEntry->BalanceAfter != 60
		|| Result.Winner != SealedResultWinner
		|| Decision.Status != MatchWinnerDecidedPendingApplyStatus)
	{
		OutError = TEXT("The Match Winner reconciliation does not match the exact finalized chain.");
		return false;
	}
	if ((!bWin && (Request.OfferedTeam != SealedResultHomeTeam
			|| Decision.Outcome != MatchWinnerLostOutcome
			|| Decision.GrossReturnDue != 0
			|| FinalizationStatus != MatchWinnerSettledLostStatus
			|| GrossReturnApplied != 0
			|| Ledger.GetEntries().Num() != 2
			|| Ledger.GetBalance() != 60))
		|| (bWin && (Request.OfferedTeam != SealedResultAwayTeam
			|| Decision.Outcome != MatchWinnerWonOutcome
			|| Decision.SelectedWinProbabilityE8 != 40000000
			|| Decision.PayoutFormula != MatchWinnerPayoutFormula
			|| Decision.GrossReturnDue != 100
			|| FinalizationStatus != MatchWinnerSettledWonStatus
			|| GrossReturnApplied != 100
			|| !PayoutEntry
			|| PayoutEntry->CommandId != FinalizationCommandId
			|| PayoutEntry->Sequence != 3
			|| PayoutEntry->Delta != 100
			|| PayoutEntry->Reason != MatchWinnerPayoutReason
			|| PayoutEntry->BalanceAfter != 160
			|| Ledger.GetEntries().Num() != 3
			|| Ledger.GetBalance() != 160)))
	{
		OutError = TEXT("The Match Winner reconciliation outcome does not match its exact finalization and ledger.");
		return false;
	}

	const TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
	Root->SetStringField(TEXT("schema"), MatchWinnerReconciliationSchema);
	Root->SetStringField(TEXT("generated_at_utc"), FDateTime::UtcNow().ToIso8601());
	Root->SetStringField(TEXT("authority"), TEXT("server"));
	Root->SetStringField(TEXT("profile_scope"), TEXT("machine_local"));
	Root->SetBoolField(TEXT("read_only_projection"), true);
	Root->SetBoolField(TEXT("qa"), bQaProjection);
	Root->SetStringField(TEXT("market"), MatchWinnerMarket);
	Root->SetStringField(TEXT("offer_id"), Request.OfferId);
	Root->SetStringField(TEXT("offer_version"), Request.OfferVersion);
	Root->SetStringField(TEXT("request_command_id"), Request.RequestCommandId);
	Root->SetStringField(TEXT("selected_team"), Request.OfferedTeam);
	Root->SetNumberField(TEXT("stake"), static_cast<double>(Request.Stake));
	Root->SetStringField(TEXT("request_status"), Request.Status.ToString());
	Root->SetStringField(TEXT("stake_ledger_command_id"), StakeEntry->CommandId);
	Root->SetNumberField(TEXT("stake_sequence"), static_cast<double>(StakeEntry->Sequence));
	Root->SetNumberField(TEXT("stake_delta"), static_cast<double>(StakeEntry->Delta));
	Root->SetStringField(TEXT("stake_reason"), StakeEntry->Reason.ToString());
	Root->SetNumberField(TEXT("stake_balance_after"), static_cast<double>(StakeEntry->BalanceAfter));
	Root->SetStringField(TEXT("lock_command_id"), Lock.LockCommandId);
	Root->SetStringField(TEXT("lock_request_command_id"), Lock.RequestCommandId);
	Root->SetNumberField(TEXT("season_number"), Lock.SeasonNumber);
	Root->SetNumberField(TEXT("game_number"), Lock.GameNumber);
	Root->SetNumberField(TEXT("game_start_unix"), static_cast<double>(Lock.AuthoritativeGameStartUnixSeconds));
	Root->SetNumberField(TEXT("lock_unix"), static_cast<double>(Lock.LockUnixSeconds));
	Root->SetStringField(TEXT("lock_decision"), Lock.Decision.ToString());
	Root->SetStringField(TEXT("result_command_id"), Result.ResultCommandId);
	Root->SetStringField(TEXT("result_request_command_id"), Result.RequestCommandId);
	Root->SetStringField(TEXT("result_lock_command_id"), Result.LockCommandId);
	Root->SetStringField(TEXT("result_schema"), Result.ResultSchema);
	Root->SetStringField(TEXT("result_version"), Result.ResultVersion);
	Root->SetStringField(TEXT("home_team"), Result.HomeTeam);
	Root->SetStringField(TEXT("away_team"), Result.AwayTeam);
	Root->SetNumberField(TEXT("home_score"), Result.HomeScore);
	Root->SetNumberField(TEXT("away_score"), Result.AwayScore);
	Root->SetStringField(TEXT("winner"), Result.Winner);
	Root->SetStringField(TEXT("replay_seal_sha256"), Result.ReplaySealSha256);
	Root->SetStringField(TEXT("decision_command_id"), Decision.DecisionCommandId);
	Root->SetStringField(TEXT("decision_request_command_id"), Decision.RequestCommandId);
	Root->SetStringField(TEXT("decision_lock_command_id"), Decision.LockCommandId);
	Root->SetStringField(TEXT("decision_result_command_id"), Decision.ResultCommandId);
	Root->SetStringField(TEXT("decision_schema"), Decision.DecisionSchema);
	Root->SetStringField(TEXT("decision_version"), Decision.DecisionVersion);
	Root->SetStringField(TEXT("decision_offer_id"), Decision.OfferId);
	Root->SetStringField(TEXT("decision_offer_version"), Decision.OfferVersion);
	Root->SetStringField(TEXT("decision_status"), Decision.Status.ToString());
	Root->SetStringField(TEXT("outcome"), Decision.Outcome.ToString());
	Root->SetNumberField(TEXT("gross_return_due"), static_cast<double>(Decision.GrossReturnDue));
	if (bWin)
	{
		Root->SetNumberField(TEXT("selected_win_probability_e8"), static_cast<double>(Decision.SelectedWinProbabilityE8));
		Root->SetStringField(TEXT("payout_formula"), Decision.PayoutFormula);
		Root->SetStringField(TEXT("payout_ledger_command_id"), PayoutEntry->CommandId);
		Root->SetNumberField(TEXT("payout_sequence"), static_cast<double>(PayoutEntry->Sequence));
		Root->SetNumberField(TEXT("payout_delta"), static_cast<double>(PayoutEntry->Delta));
		Root->SetStringField(TEXT("payout_reason"), PayoutEntry->Reason.ToString());
		Root->SetNumberField(TEXT("payout_balance_after"), static_cast<double>(PayoutEntry->BalanceAfter));
	}
	Root->SetStringField(TEXT("finalization_command_id"), FinalizationCommandId);
	Root->SetStringField(TEXT("finalization_decision_command_id"), FinalizationDecisionCommandId);
	Root->SetStringField(TEXT("finalization_request_command_id"), FinalizationRequestCommandId);
	Root->SetStringField(TEXT("finalization_lock_command_id"), FinalizationLockCommandId);
	Root->SetStringField(TEXT("finalization_result_command_id"), FinalizationResultCommandId);
	Root->SetStringField(TEXT("finalization_schema"), FinalizationSchema);
	Root->SetStringField(TEXT("finalization_version"), FinalizationVersion);
	Root->SetStringField(TEXT("finalization_offer_id"), FinalizationOfferId);
	Root->SetStringField(TEXT("finalization_offer_version"), FinalizationOfferVersion);
	Root->SetStringField(TEXT("finalization_status"), FinalizationStatus.ToString());
	Root->SetNumberField(TEXT("gross_return_applied"), static_cast<double>(GrossReturnApplied));
	Root->SetNumberField(TEXT("ledger_entry_count"), Ledger.GetEntries().Num());
	Root->SetNumberField(TEXT("final_balance"), static_cast<double>(Ledger.GetBalance()));
	Root->SetNumberField(TEXT("net"), static_cast<double>(StakeEntry->Delta + (PayoutEntry ? PayoutEntry->Delta : 0)));

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
	if (!FJsonSerializer::Serialize(Root, Writer))
	{
		OutError = TEXT("The Match Winner reconciliation projection could not be serialized.");
		return false;
	}
	const FString Path = GetMatchWinnerReconciliationPath(bQaProjection);
	IFileManager::Get().MakeDirectory(*FPaths::GetPath(Path), true);
	const FString TemporaryPath = Path + TEXT(".tmp");
	if (!FFileHelper::SaveStringToFile(Json, *TemporaryPath)
		|| !IFileManager::Get().Move(*Path, *TemporaryPath, true, true, false, true))
	{
		IFileManager::Get().Delete(*TemporaryPath, false, true, true);
		OutError = TEXT("The Match Winner reconciliation projection could not be written atomically.");
		return false;
	}
	OutError.Reset();
	return true;
}

bool SaveOddsWellOddsBucksState(
	const FOddsWellOddsBucksLedger& Ledger,
	const int64 NextJobPayoutUnixSeconds,
	const TArray<FOddsWellMatchWinnerRequestRecord>& MatchWinnerRequests,
	const TArray<FOddsWellMatchWinnerLockRecord>& MatchWinnerLocks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& MatchWinnerResultLinks,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& MatchWinnerSettlementDecisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& MatchWinnerLossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& MatchWinnerWinFinalizations,
	const bool bQaSlot,
	FString& OutError)
{
	UOddsWellOddsBucksSaveGame* Record = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::CreateSaveGameObject(UOddsWellOddsBucksSaveGame::StaticClass()));
	if (!Record)
	{
		OutError = TEXT("The native Odds Bucks save object could not be created.");
		return false;
	}
	Record->SchemaVersion = OddsBucksSchemaVersion;
	Record->Entries = Ledger.GetEntries();
	Record->NextJobPayoutUnixSeconds = NextJobPayoutUnixSeconds;
	Record->MatchWinnerRequests = MatchWinnerRequests;
	Record->MatchWinnerLocks = MatchWinnerLocks;
	Record->MatchWinnerResultLinks = MatchWinnerResultLinks;
	Record->MatchWinnerSettlementDecisions = MatchWinnerSettlementDecisions;
	Record->MatchWinnerLossFinalizations = MatchWinnerLossFinalizations;
	Record->MatchWinnerWinFinalizations = MatchWinnerWinFinalizations;
	FOddsWellOddsBucksLedger Validated;
	int64 ValidatedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> ValidatedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> ValidatedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ValidatedResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> ValidatedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> ValidatedFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> ValidatedWinFinalizations;
	bool bNeedsMigration = false;
	if (!ValidateOddsBucksSave(Record, Validated, ValidatedNextJobPayout, ValidatedRequests, ValidatedLocks, ValidatedResultLinks, ValidatedDecisions, ValidatedFinalizations, ValidatedWinFinalizations, bNeedsMigration, OutError))
	{
		return false;
	}
	if (!UGameplayStatics::SaveGameToSlot(Record, GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex))
	{
		OutError = TEXT("Native SaveGameToSlot failed for the Odds Bucks ledger.");
		return false;
	}
	OutError.Reset();
	return true;
}

bool LoadOddsWellOddsBucksStateRaw(
	const bool bQaSlot,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
	TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks,
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& OutMatchWinnerSettlementDecisions,
	TArray<FOddsWellMatchWinnerLossFinalizationRecord>& OutMatchWinnerLossFinalizations,
	TArray<FOddsWellMatchWinnerWinFinalizationRecord>& OutMatchWinnerWinFinalizations,
	bool& bOutFound,
	bool& bOutNeedsMigration,
	FString& OutError)
{
	const FString& Slot = GetOddsBucksSlot(bQaSlot);
	bOutFound = UGameplayStatics::DoesSaveGameExist(Slot, OddsBucksUserIndex);
	if (!bOutFound)
	{
		OutLedger = FOddsWellOddsBucksLedger();
		OutNextJobPayoutUnixSeconds = 0;
		OutMatchWinnerRequests.Reset();
		OutMatchWinnerLocks.Reset();
		OutMatchWinnerResultLinks.Reset();
		OutMatchWinnerSettlementDecisions.Reset();
		OutMatchWinnerLossFinalizations.Reset();
		OutMatchWinnerWinFinalizations.Reset();
		bOutNeedsMigration = false;
		OutError.Reset();
		return true;
	}
	return ValidateOddsBucksSave(
		UGameplayStatics::LoadGameFromSlot(Slot, OddsBucksUserIndex),
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		OutMatchWinnerSettlementDecisions,
		OutMatchWinnerLossFinalizations,
		OutMatchWinnerWinFinalizations,
		bOutNeedsMigration,
		OutError);
}
}

bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, const int64 NextJobPayoutUnixSeconds, const bool bQaSlot, FString& OutError)
{
	TArray<FOddsWellMatchWinnerRequestRecord> ExistingRequests;
	TArray<FOddsWellMatchWinnerLockRecord> ExistingLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ExistingResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> ExistingDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> ExistingFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> ExistingWinFinalizations;
	if (UGameplayStatics::DoesSaveGameExist(GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex))
	{
		FOddsWellOddsBucksLedger ExistingLedger;
		int64 ExistingNextJobPayout = 0;
		bool bFound = false;
		bool bNeedsMigration = false;
		if (!LoadOddsWellOddsBucksStateRaw(bQaSlot, ExistingLedger, ExistingNextJobPayout, ExistingRequests, ExistingLocks, ExistingResultLinks, ExistingDecisions, ExistingFinalizations, ExistingWinFinalizations, bFound, bNeedsMigration, OutError))
		{
			return false;
		}
	}
	return SaveOddsWellOddsBucksState(Ledger, NextJobPayoutUnixSeconds, ExistingRequests, ExistingLocks, ExistingResultLinks, ExistingDecisions, ExistingFinalizations, ExistingWinFinalizations, bQaSlot, OutError);
}

bool LoadOddsWellOddsBucksWagerFinalizationState(
	const bool bQaSlot,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
	TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks,
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& OutMatchWinnerSettlementDecisions,
	TArray<FOddsWellMatchWinnerLossFinalizationRecord>& OutMatchWinnerLossFinalizations,
	TArray<FOddsWellMatchWinnerWinFinalizationRecord>& OutMatchWinnerWinFinalizations,
	bool& bOutFound,
	FString& OutError)
{
	const FString ProjectionPath = GetMatchWinnerReconciliationPath(bQaSlot);
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		OutMatchWinnerSettlementDecisions,
		OutMatchWinnerLossFinalizations,
		OutMatchWinnerWinFinalizations,
		bOutFound,
		bNeedsMigration,
		OutError))
	{
		IFileManager::Get().Delete(*ProjectionPath, false, true, true);
		return false;
	}
	if (bNeedsMigration && !SaveOddsWellOddsBucksState(
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		OutMatchWinnerSettlementDecisions,
		OutMatchWinnerLossFinalizations,
		OutMatchWinnerWinFinalizations,
		bQaSlot,
		OutError))
	{
		IFileManager::Get().Delete(*ProjectionPath, false, true, true);
		return false;
	}
	if (!bOutFound || (OutMatchWinnerLossFinalizations.IsEmpty() && OutMatchWinnerWinFinalizations.IsEmpty()))
	{
		if (IFileManager::Get().FileExists(*ProjectionPath)
			&& !IFileManager::Get().Delete(*ProjectionPath, false, true, true))
		{
			OutError = TEXT("The stale Match Winner reconciliation projection could not be removed.");
			return false;
		}
		OutError.Reset();
		return true;
	}
	if (!WriteMatchWinnerReconciliationFromValidatedState(
		OutLedger,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		OutMatchWinnerSettlementDecisions,
		OutMatchWinnerLossFinalizations,
		OutMatchWinnerWinFinalizations,
		bQaSlot,
		OutError))
	{
		IFileManager::Get().Delete(*ProjectionPath, false, true, true);
		return false;
	}
	return true;
}

bool LoadOddsWellOddsBucksWagerDecisionState(
	const bool bQaSlot,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
	TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks,
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& OutMatchWinnerSettlementDecisions,
	bool& bOutFound,
	FString& OutError)
{
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> Finalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	return LoadOddsWellOddsBucksWagerFinalizationState(
		bQaSlot,
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		OutMatchWinnerSettlementDecisions,
		Finalizations,
		WinFinalizations,
		bOutFound,
		OutError);
}

bool LoadOddsWellOddsBucksWagerEvidence(
	const bool bQaSlot,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
	TArray<FOddsWellMatchWinnerResultLinkRecord>& OutMatchWinnerResultLinks,
	bool& bOutFound,
	FString& OutError)
{
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	return LoadOddsWellOddsBucksWagerDecisionState(
		bQaSlot,
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		Decisions,
		bOutFound,
		OutError);
}

bool LoadOddsWellOddsBucksWagerState(
	const bool bQaSlot,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
	bool& bOutFound,
	FString& OutError)
{
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	return LoadOddsWellOddsBucksWagerEvidence(
		bQaSlot,
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		ResultLinks,
		bOutFound,
		OutError);
}

bool LoadOddsWellOddsBucksState(
	const bool bQaSlot,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	bool& bOutFound,
	FString& OutError)
{
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	return LoadOddsWellOddsBucksWagerState(
		bQaSlot,
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		Locks,
		bOutFound,
		OutError);
}

bool LoadOddsWellOddsBucksLedger(const bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, bool& bOutFound, FString& OutError)
{
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	return LoadOddsWellOddsBucksState(bQaSlot, OutLedger, OutNextJobPayoutUnixSeconds, Requests, bOutFound, OutError);
}

EOddsWellMatchWinnerRequestResult AcceptOddsWellMatchWinnerRequest(
	const FOddsWellMatchWinnerOffer& Offer,
	const FString& RequestCommandId,
	const FString& OfferedTeam,
	const int64 Stake,
	const int64 AcceptedUnixSeconds,
	const bool bQaSlot,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerRequestRecord();
	OutBalance = 0;
	if (!ValidateMatchWinnerOffer(Offer, OutError)
		|| RequestCommandId.TrimStartAndEnd().IsEmpty()
		|| (OfferedTeam != Offer.HomeTeam && OfferedTeam != Offer.AwayTeam)
		|| Stake < MatchWinnerMinimumStake
		|| Stake > MatchWinnerMaximumStake
		|| Stake % MatchWinnerStakeIncrement != 0
		|| AcceptedUnixSeconds <= 0)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The Match Winner request has an invalid command, team, stake, or accepted time.");
		}
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> Finalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		ResultLinks,
		Decisions,
		Finalizations,
		WinFinalizations,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	OutBalance = Ledger.GetBalance();
	if (const FOddsWellMatchWinnerRequestRecord* Existing = Requests.FindByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerRequestRecord& Request)
		{
			return Request.RequestCommandId == RequestCommandId;
		}))
	{
		const bool bExact = Existing->StakeLedgerCommandId == RequestCommandId
			&& Existing->OfferId == Offer.OfferId
			&& Existing->OfferVersion == Offer.OfferVersion
			&& Existing->SeasonNumber == Offer.SeasonNumber
			&& Existing->GameNumber == Offer.GameNumber
			&& Existing->HomeTeam == Offer.HomeTeam
			&& Existing->AwayTeam == Offer.AwayTeam
			&& Existing->OfferedTeam == OfferedTeam
			&& Existing->Stake == Stake
			&& Existing->LockUnixSeconds == Offer.LockUnixSeconds
			&& Existing->Status == AcceptedPendingLockStatus;
		if (!bExact)
		{
			OutError = TEXT("The Match Winner request command was already used with different data.");
			return EOddsWellMatchWinnerRequestResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerRequestResult::Duplicate;
	}
	if (AcceptedUnixSeconds >= Offer.LockUnixSeconds)
	{
		OutError = TEXT("The Match Winner request reached or passed the offer lock.");
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}

	FOddsWellOddsBucksLedger CandidateLedger = Ledger;
	if (CandidateLedger.Append(RequestCommandId, -Stake, MatchWinnerStakeReason) != EOddsWellOddsBucksAppendResult::Applied)
	{
		OutError = TEXT("The Match Winner stake debit was rejected, including for insufficient balance or command reuse.");
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	FOddsWellMatchWinnerRequestRecord CandidateRecord;
	CandidateRecord.RequestCommandId = RequestCommandId;
	CandidateRecord.StakeLedgerCommandId = RequestCommandId;
	CandidateRecord.OfferId = Offer.OfferId;
	CandidateRecord.OfferVersion = Offer.OfferVersion;
	CandidateRecord.SeasonNumber = Offer.SeasonNumber;
	CandidateRecord.GameNumber = Offer.GameNumber;
	CandidateRecord.HomeTeam = Offer.HomeTeam;
	CandidateRecord.AwayTeam = Offer.AwayTeam;
	CandidateRecord.OfferedTeam = OfferedTeam;
	CandidateRecord.Stake = Stake;
	CandidateRecord.AcceptedUnixSeconds = AcceptedUnixSeconds;
	CandidateRecord.LockUnixSeconds = Offer.LockUnixSeconds;
	CandidateRecord.Status = AcceptedPendingLockStatus;
	TArray<FOddsWellMatchWinnerRequestRecord> CandidateRequests = Requests;
	CandidateRequests.Add(CandidateRecord);
	if (!SaveOddsWellOddsBucksState(
		CandidateLedger,
		NextJobPayoutUnixSeconds,
		CandidateRequests,
		Locks,
		ResultLinks,
		Decisions,
		Finalizations,
		WinFinalizations,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	OutRecord = MoveTemp(CandidateRecord);
	OutBalance = CandidateLedger.GetBalance();
	OutError.Reset();
	return EOddsWellMatchWinnerRequestResult::Accepted;
}

EOddsWellMatchWinnerLockResult LockOddsWellMatchWinnerRequest(
	const FString& RequestCommandId,
	const FString& LockCommandId,
	const int32 SeasonNumber,
	const int32 GameNumber,
	const int64 AuthoritativeGameStartUnixSeconds,
	const bool bQaSlot,
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerLockRecord();
	if (RequestCommandId.TrimStartAndEnd().IsEmpty()
		|| LockCommandId.TrimStartAndEnd().IsEmpty()
		|| LockCommandId == RequestCommandId
		|| SeasonNumber <= 0
		|| GameNumber <= 0
		|| AuthoritativeGameStartUnixSeconds <= 0)
	{
		OutError = TEXT("The Match Winner lock command has invalid identity, game, or start time.");
		return EOddsWellMatchWinnerLockResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> Finalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		ResultLinks,
		Decisions,
		Finalizations,
		WinFinalizations,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	if (const FOddsWellMatchWinnerLockRecord* Existing = Locks.FindByPredicate(
		[&LockCommandId](const FOddsWellMatchWinnerLockRecord& Lock)
		{
			return Lock.LockCommandId == LockCommandId;
		}))
	{
		const bool bExact = Existing->RequestCommandId == RequestCommandId
			&& Existing->SeasonNumber == SeasonNumber
			&& Existing->GameNumber == GameNumber
			&& Existing->AuthoritativeGameStartUnixSeconds == AuthoritativeGameStartUnixSeconds
			&& Existing->LockUnixSeconds == AuthoritativeGameStartUnixSeconds
			&& Existing->Decision == MatchWinnerLockedDecision;
		if (!bExact)
		{
			OutError = TEXT("The Match Winner lock command was already used with different data.");
			return EOddsWellMatchWinnerLockResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerLockResult::Duplicate;
	}
	if (Locks.ContainsByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerLockRecord& Lock)
		{
			return Lock.RequestCommandId == RequestCommandId;
		}))
	{
		OutError = TEXT("The Match Winner request already has a different lock command.");
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerRequestRecord& Candidate)
		{
			return Candidate.RequestCommandId == RequestCommandId;
		});
	if (!Request)
	{
		OutError = TEXT("The Match Winner lock command references an unknown accepted request.");
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	if (Request->SeasonNumber != SeasonNumber
		|| Request->GameNumber != GameNumber
		|| Request->LockUnixSeconds != AuthoritativeGameStartUnixSeconds)
	{
		OutError = TEXT("The Match Winner lock command does not match the accepted game start.");
		return EOddsWellMatchWinnerLockResult::Rejected;
	}

	FOddsWellMatchWinnerLockRecord CandidateRecord;
	CandidateRecord.LockCommandId = LockCommandId;
	CandidateRecord.RequestCommandId = RequestCommandId;
	CandidateRecord.SeasonNumber = SeasonNumber;
	CandidateRecord.GameNumber = GameNumber;
	CandidateRecord.AuthoritativeGameStartUnixSeconds = AuthoritativeGameStartUnixSeconds;
	CandidateRecord.LockUnixSeconds = Request->LockUnixSeconds;
	CandidateRecord.Decision = MatchWinnerLockedDecision;
	TArray<FOddsWellMatchWinnerLockRecord> CandidateLocks = Locks;
	CandidateLocks.Add(CandidateRecord);
	if (!SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		CandidateLocks,
		ResultLinks,
		Decisions,
		Finalizations,
		WinFinalizations,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	OutRecord = MoveTemp(CandidateRecord);
	OutError.Reset();
	return EOddsWellMatchWinnerLockResult::Locked;
}

EOddsWellMatchWinnerResultLinkResult LinkOddsWellMatchWinnerResult(
	const FString& ResultCommandId,
	const FString& RequestCommandId,
	const FString& LockCommandId,
	const FString& ResultSchema,
	const FString& ResultVersion,
	const int32 SeasonNumber,
	const int32 GameNumber,
	const FString& HomeTeam,
	const FString& AwayTeam,
	const int32 HomeScore,
	const int32 AwayScore,
	const FString& Winner,
	const FString& ReplaySealSha256,
	const bool bQaSlot,
	FOddsWellMatchWinnerResultLinkRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerResultLinkRecord();
	if (ResultCommandId.TrimStartAndEnd().IsEmpty()
		|| RequestCommandId.TrimStartAndEnd().IsEmpty()
		|| LockCommandId.TrimStartAndEnd().IsEmpty()
		|| ResultCommandId == RequestCommandId
		|| ResultCommandId == LockCommandId)
	{
		OutError = TEXT("The Match Winner result link has invalid command identity.");
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> Finalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		ResultLinks,
		Decisions,
		Finalizations,
		WinFinalizations,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}

	FOddsWellMatchWinnerResultLinkRecord Candidate;
	Candidate.ResultCommandId = ResultCommandId;
	Candidate.RequestCommandId = RequestCommandId;
	Candidate.LockCommandId = LockCommandId;
	Candidate.ResultSchema = ResultSchema;
	Candidate.ResultVersion = ResultVersion;
	Candidate.SeasonNumber = SeasonNumber;
	Candidate.GameNumber = GameNumber;
	Candidate.HomeTeam = HomeTeam;
	Candidate.AwayTeam = AwayTeam;
	Candidate.HomeScore = HomeScore;
	Candidate.AwayScore = AwayScore;
	Candidate.Winner = Winner;
	Candidate.ReplaySealSha256 = ReplaySealSha256;
	if (const FOddsWellMatchWinnerResultLinkRecord* Existing = ResultLinks.FindByPredicate(
		[&ResultCommandId](const FOddsWellMatchWinnerResultLinkRecord& Result)
		{
			return Result.ResultCommandId == ResultCommandId;
		}))
	{
		const bool bExact = Existing->RequestCommandId == Candidate.RequestCommandId
			&& Existing->LockCommandId == Candidate.LockCommandId
			&& Existing->ResultSchema == Candidate.ResultSchema
			&& Existing->ResultVersion == Candidate.ResultVersion
			&& Existing->SeasonNumber == Candidate.SeasonNumber
			&& Existing->GameNumber == Candidate.GameNumber
			&& Existing->HomeTeam == Candidate.HomeTeam
			&& Existing->AwayTeam == Candidate.AwayTeam
			&& Existing->HomeScore == Candidate.HomeScore
			&& Existing->AwayScore == Candidate.AwayScore
			&& Existing->Winner == Candidate.Winner
			&& Existing->ReplaySealSha256 == Candidate.ReplaySealSha256;
		if (!bExact)
		{
			OutError = TEXT("The Match Winner result command was already used with different data.");
			return EOddsWellMatchWinnerResultLinkResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerResultLinkResult::Duplicate;
	}
	if (ResultLinks.ContainsByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerResultLinkRecord& Result)
		{
			return Result.RequestCommandId == RequestCommandId;
		}))
	{
		OutError = TEXT("The Match Winner request already has a different result link.");
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}
	const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerRequestRecord& Entry)
		{
			return Entry.RequestCommandId == RequestCommandId;
		});
	const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
		[&LockCommandId](const FOddsWellMatchWinnerLockRecord& Entry)
		{
			return Entry.LockCommandId == LockCommandId;
		});
	if (!Request
		|| !Lock
		|| Lock->RequestCommandId != RequestCommandId
		|| Candidate.SeasonNumber != Request->SeasonNumber
		|| Candidate.GameNumber != Request->GameNumber
		|| Candidate.HomeTeam != Request->HomeTeam
		|| Candidate.AwayTeam != Request->AwayTeam
		|| Candidate.SeasonNumber != Lock->SeasonNumber
		|| Candidate.GameNumber != Lock->GameNumber
		|| !IsExactSealedMatchWinnerResult(Candidate))
	{
		OutError = TEXT("The Match Winner result does not match the exact verified archive, accepted request, and lock.");
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}

	TArray<FOddsWellMatchWinnerResultLinkRecord> CandidateResultLinks = ResultLinks;
	CandidateResultLinks.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		CandidateResultLinks,
		Decisions,
		Finalizations,
		WinFinalizations,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerResultLinkResult::Linked;
}

namespace
{
EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellMatchWinnerSettlementInternal(
	const FOddsWellMatchWinnerOffer* ExactOffer,
	const FString& DecisionCommandId,
	const FString& RequestCommandId,
	const FString& LockCommandId,
	const FString& ResultCommandId,
	const bool bQaSlot,
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerSettlementDecisionRecord();
	if (DecisionCommandId.TrimStartAndEnd().IsEmpty()
		|| RequestCommandId.TrimStartAndEnd().IsEmpty()
		|| LockCommandId.TrimStartAndEnd().IsEmpty()
		|| ResultCommandId.TrimStartAndEnd().IsEmpty()
		|| DecisionCommandId == RequestCommandId
		|| DecisionCommandId == LockCommandId
		|| DecisionCommandId == ResultCommandId)
	{
		OutError = TEXT("The Match Winner settlement decision has invalid command identity.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> Finalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		Finalizations,
		WinFinalizations,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	const FOddsWellMatchWinnerSettlementDecisionRecord* ExistingDecision = Decisions.FindByPredicate(
		[&DecisionCommandId](const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
		{
			return Decision.DecisionCommandId == DecisionCommandId;
		});
	if (ExistingDecision)
	{
		if (ExistingDecision->RequestCommandId != RequestCommandId
			|| ExistingDecision->LockCommandId != LockCommandId
			|| ExistingDecision->ResultCommandId != ResultCommandId)
		{
			OutError = TEXT("The Match Winner settlement decision command was already used with different chain identity.");
			return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
		}
	}
	if (!ExistingDecision && Decisions.ContainsByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
		{
			return Decision.RequestCommandId == RequestCommandId;
		}))
	{
		OutError = TEXT("The Match Winner request already has a different settlement decision command.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerRequestRecord& Entry)
		{
			return Entry.RequestCommandId == RequestCommandId;
		});
	const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
		[&LockCommandId](const FOddsWellMatchWinnerLockRecord& Entry)
		{
			return Entry.LockCommandId == LockCommandId;
		});
	const FOddsWellMatchWinnerResultLinkRecord* Result = Results.FindByPredicate(
		[&ResultCommandId](const FOddsWellMatchWinnerResultLinkRecord& Entry)
		{
			return Entry.ResultCommandId == ResultCommandId;
		});
	if (!Request
		|| !Lock
		|| !Result
		|| Lock->RequestCommandId != RequestCommandId
		|| Result->RequestCommandId != RequestCommandId
		|| Result->LockCommandId != LockCommandId)
	{
		OutError = TEXT("The Match Winner settlement decision does not match one exact request, lock, and result chain.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	const FName DerivedOutcome = Request->OfferedTeam == Result->Winner
		? MatchWinnerWonOutcome
		: MatchWinnerLostOutcome;
	int64 GrossReturnDue = 0;
	int64 SelectedWinProbabilityE8 = 0;
	FString BoundPayoutFormula;
	if (DerivedOutcome == MatchWinnerWonOutcome)
	{
		const FOddsWellMatchWinnerSelection* SelectedOffer = ExactOffer
			? ExactOffer->Selections.FindByPredicate(
				[Request](const FOddsWellMatchWinnerSelection& Selection)
				{
					return Selection.Team == Request->OfferedTeam;
				})
			: nullptr;
		if (!ExactOffer
			|| !ValidateMatchWinnerOffer(*ExactOffer, OutError)
			|| ExactOffer->OfferId != Request->OfferId
			|| ExactOffer->OfferId != ExactMatchWinnerOfferId
			|| ExactOffer->OfferVersion != Request->OfferVersion
			|| ExactOffer->SeasonNumber != Request->SeasonNumber
			|| ExactOffer->GameNumber != Request->GameNumber
			|| ExactOffer->HomeTeam != Request->HomeTeam
			|| ExactOffer->AwayTeam != Request->AwayTeam
			|| ExactOffer->LockUnixSeconds != Request->LockUnixSeconds
			|| ExactOffer->PayoutFormula != MatchWinnerPayoutFormula
			|| Request->OfferedTeam != SealedResultAwayTeam
			|| Request->Stake != 40
			|| !SelectedOffer
			|| SelectedOffer->WinProbabilityE8 != 40000000)
		{
			if (OutError.IsEmpty())
			{
				OutError = TEXT("The exact winning decision requires the recomputed Mesa offer and approved payout formula.");
			}
			return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
		}
		SelectedWinProbabilityE8 = SelectedOffer->WinProbabilityE8;
		GrossReturnDue = Request->Stake * MatchWinnerProbabilityScale / SelectedWinProbabilityE8;
		BoundPayoutFormula = ExactOffer->PayoutFormula;
		if (GrossReturnDue != 100)
		{
			OutError = TEXT("The exact winning return does not recompute to 100 Odds Bucks.");
			return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
		}
	}
	if (ExistingDecision)
	{
		OutRecord = *ExistingDecision;
		OutError.Reset();
		return EOddsWellMatchWinnerSettlementDecisionResult::Duplicate;
	}

	FOddsWellMatchWinnerSettlementDecisionRecord Candidate;
	Candidate.DecisionCommandId = DecisionCommandId;
	Candidate.RequestCommandId = RequestCommandId;
	Candidate.LockCommandId = LockCommandId;
	Candidate.ResultCommandId = ResultCommandId;
	Candidate.DecisionSchema = MatchWinnerSettlementDecisionSchema;
	Candidate.DecisionVersion = MatchWinnerSettlementDecisionVersion;
	Candidate.OfferId = Request->OfferId;
	Candidate.OfferVersion = Request->OfferVersion;
	Candidate.SelectedTeam = Request->OfferedTeam;
	Candidate.AuthoritativeWinner = Result->Winner;
	Candidate.Stake = Request->Stake;
	Candidate.Outcome = DerivedOutcome;
	Candidate.GrossReturnDue = GrossReturnDue;
	Candidate.SelectedWinProbabilityE8 = SelectedWinProbabilityE8;
	Candidate.PayoutFormula = BoundPayoutFormula;
	Candidate.Status = MatchWinnerDecidedPendingApplyStatus;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> CandidateDecisions = Decisions;
	CandidateDecisions.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		CandidateDecisions,
		Finalizations,
		WinFinalizations,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerSettlementDecisionResult::Decided;
}
}

EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellMatchWinnerSettlement(
	const FString& DecisionCommandId,
	const FString& RequestCommandId,
	const FString& LockCommandId,
	const FString& ResultCommandId,
	const bool bQaSlot,
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	return DecideOddsWellMatchWinnerSettlementInternal(nullptr, DecisionCommandId, RequestCommandId, LockCommandId, ResultCommandId, bQaSlot, OutRecord, OutError);
}

EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellMatchWinnerSettlement(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const FString& DecisionCommandId,
	const FString& RequestCommandId,
	const FString& LockCommandId,
	const FString& ResultCommandId,
	const bool bQaSlot,
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	return DecideOddsWellMatchWinnerSettlementInternal(&ExactOffer, DecisionCommandId, RequestCommandId, LockCommandId, ResultCommandId, bQaSlot, OutRecord, OutError);
}

EOddsWellMatchWinnerLossFinalizationResult FinalizeOddsWellMatchWinnerLoss(
	const FString& FinalizationCommandId,
	const FString& DecisionCommandId,
	const bool bQaSlot,
	FOddsWellMatchWinnerLossFinalizationRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerLossFinalizationRecord();
	if (FinalizationCommandId.TrimStartAndEnd().IsEmpty()
		|| DecisionCommandId.TrimStartAndEnd().IsEmpty()
		|| FinalizationCommandId == DecisionCommandId)
	{
		OutError = TEXT("The Match Winner loss finalization has invalid command identity.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> Finalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		Finalizations,
		WinFinalizations,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	if (const FOddsWellMatchWinnerLossFinalizationRecord* Existing = Finalizations.FindByPredicate(
		[&FinalizationCommandId](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
		{
			return Finalization.FinalizationCommandId == FinalizationCommandId;
		}))
	{
		if (Existing->DecisionCommandId != DecisionCommandId)
		{
			OutError = TEXT("The Match Winner loss finalization command was already used with a different decision.");
			return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerLossFinalizationResult::Duplicate;
	}
	if (Finalizations.ContainsByPredicate(
		[&DecisionCommandId](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
		{
			return Finalization.DecisionCommandId == DecisionCommandId;
		}))
	{
		OutError = TEXT("The Match Winner decision already has a different loss finalization command.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	const FOddsWellMatchWinnerSettlementDecisionRecord* Decision = Decisions.FindByPredicate(
		[&DecisionCommandId](const FOddsWellMatchWinnerSettlementDecisionRecord& Entry)
		{
			return Entry.DecisionCommandId == DecisionCommandId;
		});
	if (!Decision
		|| Decision->Outcome != MatchWinnerLostOutcome
		|| Decision->GrossReturnDue != 0
		|| Decision->Status != MatchWinnerDecidedPendingApplyStatus
		|| Ledger.GetBalance() != 60
		|| Ledger.GetEntries().Num() != 2)
	{
		OutError = TEXT("The Match Winner finalization requires the exact pending loss decision and unchanged ledger evidence.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
		[Decision](const FOddsWellMatchWinnerRequestRecord& Entry)
		{
			return Entry.RequestCommandId == Decision->RequestCommandId;
		});
	const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
		[Decision](const FOddsWellMatchWinnerLockRecord& Entry)
		{
			return Entry.LockCommandId == Decision->LockCommandId;
		});
	const FOddsWellMatchWinnerResultLinkRecord* Result = Results.FindByPredicate(
		[Decision](const FOddsWellMatchWinnerResultLinkRecord& Entry)
		{
			return Entry.ResultCommandId == Decision->ResultCommandId;
		});
	if (!Request
		|| !Lock
		|| !Result
		|| Lock->RequestCommandId != Decision->RequestCommandId
		|| Result->RequestCommandId != Decision->RequestCommandId
		|| Result->LockCommandId != Decision->LockCommandId
		|| Request->OfferedTeam != Decision->SelectedTeam
		|| Result->Winner != Decision->AuthoritativeWinner)
	{
		OutError = TEXT("The Match Winner finalization decision chain does not match its authoritative evidence.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}

	FOddsWellMatchWinnerLossFinalizationRecord Candidate;
	Candidate.FinalizationCommandId = FinalizationCommandId;
	Candidate.DecisionCommandId = DecisionCommandId;
	Candidate.RequestCommandId = Decision->RequestCommandId;
	Candidate.LockCommandId = Decision->LockCommandId;
	Candidate.ResultCommandId = Decision->ResultCommandId;
	Candidate.FinalizationSchema = MatchWinnerLossFinalizationSchema;
	Candidate.FinalizationVersion = MatchWinnerLossFinalizationVersion;
	Candidate.OfferId = Decision->OfferId;
	Candidate.OfferVersion = Decision->OfferVersion;
	Candidate.SelectedTeam = Decision->SelectedTeam;
	Candidate.AuthoritativeWinner = Decision->AuthoritativeWinner;
	Candidate.Stake = Decision->Stake;
	Candidate.Outcome = Decision->Outcome;
	Candidate.GrossReturnApplied = 0;
	Candidate.Status = MatchWinnerSettledLostStatus;
	Candidate.ObservedFinalBalance = Ledger.GetBalance();
	Candidate.ObservedLedgerEntryCount = Ledger.GetEntries().Num();
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> CandidateFinalizations = Finalizations;
	CandidateFinalizations.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		CandidateFinalizations,
		WinFinalizations,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	FOddsWellOddsBucksLedger PublishedLedger;
	int64 PublishedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> PublishedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> PublishedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> PublishedResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> PublishedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> PublishedFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> PublishedWinFinalizations;
	bool bPublishedFound = false;
	FString ProjectionError;
	if (!LoadOddsWellOddsBucksWagerFinalizationState(
		bQaSlot,
		PublishedLedger,
		PublishedNextJobPayout,
		PublishedRequests,
		PublishedLocks,
		PublishedResults,
		PublishedDecisions,
		PublishedFinalizations,
		PublishedWinFinalizations,
		bPublishedFound,
		ProjectionError))
	{
		OutRecord = MoveTemp(Candidate);
		OutError = FString::Printf(TEXT("The loss was finalized, but its read-only reconciliation is unavailable: %s"), *ProjectionError);
		return EOddsWellMatchWinnerLossFinalizationResult::Finalized;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerLossFinalizationResult::Finalized;
}

EOddsWellMatchWinnerWinFinalizationResult FinalizeOddsWellMatchWinnerWin(
	const FString& FinalizationCommandId,
	const FString& DecisionCommandId,
	const bool bQaSlot,
	FOddsWellMatchWinnerWinFinalizationRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerWinFinalizationRecord();
	if (FinalizationCommandId.TrimStartAndEnd().IsEmpty()
		|| DecisionCommandId.TrimStartAndEnd().IsEmpty()
		|| FinalizationCommandId == DecisionCommandId)
	{
		OutError = TEXT("The Match Winner win finalization has invalid command identity.");
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		WinFinalizations,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}
	if (const FOddsWellMatchWinnerWinFinalizationRecord* Existing = WinFinalizations.FindByPredicate(
		[&FinalizationCommandId](const FOddsWellMatchWinnerWinFinalizationRecord& Finalization)
		{
			return Finalization.FinalizationCommandId == FinalizationCommandId;
		}))
	{
		if (Existing->DecisionCommandId != DecisionCommandId)
		{
			OutError = TEXT("The Match Winner win finalization command was already used with a different decision.");
			return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerWinFinalizationResult::Duplicate;
	}
	if (WinFinalizations.ContainsByPredicate(
		[&DecisionCommandId](const FOddsWellMatchWinnerWinFinalizationRecord& Finalization)
		{
			return Finalization.DecisionCommandId == DecisionCommandId;
		})
		|| LossFinalizations.ContainsByPredicate(
			[&FinalizationCommandId, &DecisionCommandId](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
			{
				return Finalization.FinalizationCommandId == FinalizationCommandId
					|| Finalization.DecisionCommandId == DecisionCommandId;
			}))
	{
		OutError = TEXT("The Match Winner win decision already has a finalization or the command identity is unavailable.");
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}
	const FOddsWellMatchWinnerSettlementDecisionRecord* Decision = Decisions.FindByPredicate(
		[&DecisionCommandId](const FOddsWellMatchWinnerSettlementDecisionRecord& Entry)
		{
			return Entry.DecisionCommandId == DecisionCommandId;
		});
	if (!Decision
		|| Decision->Outcome != MatchWinnerWonOutcome
		|| Decision->GrossReturnDue != 100
		|| Decision->SelectedWinProbabilityE8 != 40000000
		|| Decision->PayoutFormula != MatchWinnerPayoutFormula
		|| Decision->Status != MatchWinnerDecidedPendingApplyStatus
		|| Ledger.GetBalance() != 60
		|| Ledger.GetEntries().Num() != 2)
	{
		OutError = TEXT("The Match Winner win application requires the exact pending win decision and unchanged ledger evidence.");
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}
	const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
		[Decision](const FOddsWellMatchWinnerRequestRecord& Entry)
		{
			return Entry.RequestCommandId == Decision->RequestCommandId;
		});
	const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
		[Decision](const FOddsWellMatchWinnerLockRecord& Entry)
		{
			return Entry.LockCommandId == Decision->LockCommandId;
		});
	const FOddsWellMatchWinnerResultLinkRecord* Result = Results.FindByPredicate(
		[Decision](const FOddsWellMatchWinnerResultLinkRecord& Entry)
		{
			return Entry.ResultCommandId == Decision->ResultCommandId;
		});
	if (!Request
		|| !Lock
		|| !Result
		|| FinalizationCommandId == Decision->RequestCommandId
		|| FinalizationCommandId == Decision->LockCommandId
		|| FinalizationCommandId == Decision->ResultCommandId
		|| Lock->RequestCommandId != Decision->RequestCommandId
		|| Result->RequestCommandId != Decision->RequestCommandId
		|| Result->LockCommandId != Decision->LockCommandId
		|| Request->OfferId != ExactMatchWinnerOfferId
		|| Request->OfferedTeam != SealedResultAwayTeam
		|| Request->Stake != 40
		|| Result->Winner != SealedResultAwayTeam
		|| Request->OfferedTeam != Decision->SelectedTeam
		|| Result->Winner != Decision->AuthoritativeWinner)
	{
		OutError = TEXT("The Match Winner win application decision chain does not match its exact authoritative evidence.");
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}

	FOddsWellOddsBucksLedger CandidateLedger = Ledger;
	if (CandidateLedger.Append(FinalizationCommandId, Decision->GrossReturnDue, MatchWinnerPayoutReason) != EOddsWellOddsBucksAppendResult::Applied
		|| CandidateLedger.GetEntries().Num() != 3
		|| CandidateLedger.GetBalance() != 160)
	{
		OutError = TEXT("The exact Match Winner win payout ledger entry could not be applied.");
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}

	FOddsWellMatchWinnerWinFinalizationRecord Candidate;
	Candidate.FinalizationCommandId = FinalizationCommandId;
	Candidate.DecisionCommandId = DecisionCommandId;
	Candidate.RequestCommandId = Decision->RequestCommandId;
	Candidate.LockCommandId = Decision->LockCommandId;
	Candidate.ResultCommandId = Decision->ResultCommandId;
	Candidate.FinalizationSchema = MatchWinnerWinFinalizationSchema;
	Candidate.FinalizationVersion = MatchWinnerWinFinalizationVersion;
	Candidate.OfferId = Decision->OfferId;
	Candidate.OfferVersion = Decision->OfferVersion;
	Candidate.SelectedTeam = Decision->SelectedTeam;
	Candidate.AuthoritativeWinner = Decision->AuthoritativeWinner;
	Candidate.Stake = Decision->Stake;
	Candidate.Outcome = Decision->Outcome;
	Candidate.GrossReturnApplied = Decision->GrossReturnDue;
	Candidate.PayoutLedgerCommandId = FinalizationCommandId;
	Candidate.Status = MatchWinnerSettledWonStatus;
	Candidate.ObservedFinalBalance = CandidateLedger.GetBalance();
	Candidate.ObservedLedgerEntryCount = CandidateLedger.GetEntries().Num();
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> CandidateWinFinalizations = WinFinalizations;
	CandidateWinFinalizations.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		CandidateLedger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		CandidateWinFinalizations,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerWinFinalizationResult::Rejected;
	}
	FOddsWellOddsBucksLedger PublishedLedger;
	int64 PublishedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> PublishedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> PublishedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> PublishedResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> PublishedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> PublishedLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> PublishedWinFinalizations;
	bool bPublishedFound = false;
	FString ProjectionError;
	if (!LoadOddsWellOddsBucksWagerFinalizationState(
		bQaSlot,
		PublishedLedger,
		PublishedNextJobPayout,
		PublishedRequests,
		PublishedLocks,
		PublishedResults,
		PublishedDecisions,
		PublishedLossFinalizations,
		PublishedWinFinalizations,
		bPublishedFound,
		ProjectionError))
	{
		OutRecord = MoveTemp(Candidate);
		OutError = FString::Printf(TEXT("The win was finalized and its return applied, but its read-only reconciliation is unavailable: %s"), *ProjectionError);
		return EOddsWellMatchWinnerWinFinalizationResult::Finalized;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerWinFinalizationResult::Finalized;
}

bool ResetOddsWellQaOddsBucksAndVerify(FString& OutError)
{
	if (UGameplayStatics::DoesSaveGameExist(OddsBucksQaSlot, OddsBucksUserIndex)
		&& !UGameplayStatics::DeleteGameInSlot(OddsBucksQaSlot, OddsBucksUserIndex))
	{
		OutError = TEXT("The QA Odds Bucks save could not be deleted.");
		return false;
	}
	if (UGameplayStatics::DoesSaveGameExist(OddsBucksQaSlot, OddsBucksUserIndex))
	{
		OutError = TEXT("The QA Odds Bucks save still exists after cleanup.");
		return false;
	}
	const FString QaProjection = GetOddsBucksReconciliationPath(true);
	if (IFileManager::Get().FileExists(*QaProjection)
		&& !IFileManager::Get().Delete(*QaProjection, false, true, true))
	{
		OutError = TEXT("The QA Odds Bucks reconciliation projection could not be deleted.");
		return false;
	}
	const FString QaMatchWinnerProjection = GetMatchWinnerReconciliationPath(true);
	if (IFileManager::Get().FileExists(*QaMatchWinnerProjection)
		&& !IFileManager::Get().Delete(*QaMatchWinnerProjection, false, true, true))
	{
		OutError = TEXT("The QA Match Winner reconciliation projection could not be deleted.");
		return false;
	}
	OutError.Reset();
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
FOddsWellMatchWinnerOffer MakeMatchWinnerTestOffer()
{
	FOddsWellMatchWinnerOffer Offer;
	Offer.OfferId = ExactMatchWinnerOfferId;
	Offer.Schema = MatchWinnerOfferSchema;
	Offer.OfferVersion = MatchWinnerOfferVersion;
	Offer.Market = MatchWinnerMarket;
	Offer.Currency = OddsBucksCurrency;
	Offer.SourcePredictionVersion = MatchWinnerPredictionVersion;
	Offer.SourceSnapshotVersion = MatchWinnerSnapshotVersion;
	Offer.SourceModel = MatchWinnerSourceModel;
	Offer.SourceCommitmentSha256 = TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
	Offer.SeasonNumber = 1;
	Offer.GameNumber = 1;
	Offer.HomeTeam = TEXT("Harbor City Waves");
	Offer.AwayTeam = TEXT("Mesa Vista Sol");
	Offer.LockUnixSeconds = 2000000000;
	Offer.MinimumStake = MatchWinnerMinimumStake;
	Offer.MaximumStake = MatchWinnerMaximumStake;
	Offer.StakeIncrement = MatchWinnerStakeIncrement;
	Offer.HouseEdgeBps = 0;
	Offer.PayoutFormula = MatchWinnerPayoutFormula;
	FOddsWellMatchWinnerSelection& Home = Offer.Selections.AddDefaulted_GetRef();
	Home.Team = Offer.HomeTeam;
	Home.WinProbabilityE8 = 60000000;
	Home.DecimalOddsE4 = 16666;
	FOddsWellMatchWinnerSelection& Away = Offer.Selections.AddDefaulted_GetRef();
	Away.Team = Offer.AwayTeam;
	Away.WinProbabilityE8 = 40000000;
	Away.DecimalOddsE4 = 25000;
	return Offer;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellOddsBucksLedgerTest,
	"OddsWell.Economy.OddsBucksLedger",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellOddsBucksLedgerTest::RunTest(const FString& Parameters)
{
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(TEXT("New ledger balance is zero"), Ledger.GetBalance(), int64{0});
	TestEqual(TEXT("New ledger has no entries"), Ledger.GetEntries().Num(), 0);

	TestEqual(TEXT("First server command applies"), Ledger.Append(TEXT("test-credit-1"), 25, TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Applied);
	TestEqual(TEXT("Applied balance"), Ledger.GetBalance(), int64{25});
	TestEqual(TEXT("One append-only entry"), Ledger.GetEntries().Num(), 1);
	TestEqual(TEXT("First sequence"), Ledger.GetEntries()[0].Sequence, int64{1});

	TestEqual(TEXT("Exact retry is idempotent"), Ledger.Append(TEXT("test-credit-1"), 25, TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Duplicate);
	TestEqual(TEXT("Retry does not append"), Ledger.GetEntries().Num(), 1);
	TestEqual(TEXT("Retry does not change balance"), Ledger.GetBalance(), int64{25});
	TestEqual(TEXT("Conflicting command reuse is rejected"), Ledger.Append(TEXT("test-credit-1"), 20, TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Rejected);

	TestEqual(TEXT("Valid debit applies"), Ledger.Append(TEXT("test-debit-1"), -10, TEXT("test_debit")), EOddsWellOddsBucksAppendResult::Applied);
	TestEqual(TEXT("Debit balance"), Ledger.GetBalance(), int64{15});
	TestEqual(TEXT("Overspend is rejected"), Ledger.Append(TEXT("test-debit-2"), -16, TEXT("test_debit")), EOddsWellOddsBucksAppendResult::Rejected);
	TestEqual(TEXT("Rejected command does not append"), Ledger.GetEntries().Num(), 2);

	TestEqual(TEXT("Blank command is rejected"), Ledger.Append(TEXT("  "), 1, TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Rejected);
	TestEqual(TEXT("Missing reason is rejected"), Ledger.Append(TEXT("test-credit-2"), 1, NAME_None), EOddsWellOddsBucksAppendResult::Rejected);
	TestEqual(TEXT("Zero delta is rejected"), Ledger.Append(TEXT("test-zero"), 0, TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Rejected);

	FOddsWellOddsBucksLedger OverflowLedger;
	TestEqual(TEXT("Maximum balance applies"), OverflowLedger.Append(TEXT("test-max"), TNumericLimits<int64>::Max(), TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Applied);
	TestEqual(TEXT("Overflow is rejected"), OverflowLedger.Append(TEXT("test-overflow"), 1, TEXT("test_credit")), EOddsWellOddsBucksAppendResult::Rejected);
	TestEqual(TEXT("Overflow does not append"), OverflowLedger.GetEntries().Num(), 1);

	FOddsWellOddsBucksLedger Restored;
	FString Error;
	TestTrue(TEXT("Exact append-only entries restore"), Restored.Restore(Ledger.GetEntries(), Error));
	TestEqual(TEXT("Restored balance remains exact"), Restored.GetBalance(), int64{15});
	TArray<FOddsWellOddsBucksEntry> CorruptEntries = Ledger.GetEntries();
	CorruptEntries[1].BalanceAfter++;
	TestFalse(TEXT("A corrupt running balance is rejected"), Restored.Restore(CorruptEntries, Error));
	TestEqual(TEXT("Rejected restore leaves the prior ledger unchanged"), Restored.GetBalance(), int64{15});

	UOddsWellOddsBucksSaveGame* Record = NewObject<UOddsWellOddsBucksSaveGame>();
	Record->SchemaVersion = OddsBucksSchemaVersion;
	Record->Entries = Ledger.GetEntries();
	Record->NextJobPayoutUnixSeconds = 0;
	TArray<uint8> Bytes;
	TestTrue(TEXT("Odds Bucks entries serialize"), UGameplayStatics::SaveGameToMemory(Record, Bytes));
	FOddsWellOddsBucksLedger MemoryLedger;
	int64 MemoryNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> MemoryRequests;
	TArray<FOddsWellMatchWinnerLockRecord> MemoryLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> MemoryResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> MemoryDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> MemoryFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> MemoryWinFinalizations;
	bool bNeedsMigration = false;
	TestTrue(TEXT("Odds Bucks entries validate after a memory round trip"), ValidateOddsBucksSave(UGameplayStatics::LoadGameFromMemory(Bytes), MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
	TestEqual(TEXT("Memory round trip preserves balance"), MemoryLedger.GetBalance(), int64{15});
	Record->SchemaVersion++;
	TestFalse(TEXT("An unsupported Odds Bucks schema is rejected"), ValidateOddsBucksSave(Record, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
	TestFalse(TEXT("A wrong save type is rejected"), ValidateOddsBucksSave(NewObject<UStaticMesh>(), MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));

	ResetOddsWellQaOddsBucksAndVerify(Error);
	FOddsWellOddsBucksLedger JobLedger;
	TestEqual(TEXT("Provisional first job payout applies"), JobLedger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()), EOddsWellOddsBucksAppendResult::Applied);
	const int64 ExpectedNextJobPayout = 2000000000 + GetOddsWellJobPayoutIntervalSeconds();
	TestTrue(TEXT("Provisional job payout saves to the bounded QA slot"), SaveOddsWellOddsBucksLedger(JobLedger, ExpectedNextJobPayout, true, Error));
	FString ReconciliationPath;
	TestTrue(TEXT("Read-only Odds Bucks reconciliation projection writes"), WriteOddsWellOddsBucksReconciliation(JobLedger, ExpectedNextJobPayout, 2000000000, true, ReconciliationPath, Error));
	TestTrue(TEXT("Read-only Odds Bucks reconciliation projection exists"), IFileManager::Get().FileExists(*ReconciliationPath));
	FOddsWellOddsBucksLedger DiskLedger;
	int64 DiskNextJobPayout = 0;
	bool bFound = false;
	TestTrue(TEXT("Provisional job payout reloads from the QA slot"), LoadOddsWellOddsBucksLedger(true, DiskLedger, DiskNextJobPayout, bFound, Error));
	TestTrue(TEXT("QA payout save was found"), bFound);
	TestEqual(TEXT("Disk round trip preserves one command"), DiskLedger.GetEntries().Num(), 1);
	TestEqual(TEXT("Disk round trip preserves 100 balance"), DiskLedger.GetBalance(), int64{100});
	TestEqual(TEXT("Disk round trip preserves the next payout time"), DiskNextJobPayout, ExpectedNextJobPayout);
	TestEqual(TEXT("Restored retry stays idempotent"), DiskLedger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()), EOddsWellOddsBucksAppendResult::Duplicate);
	TestTrue(TEXT("QA Odds Bucks cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));

	UOddsWellOddsBucksSaveGame* LegacyRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	LegacyRecord->SchemaVersion = 1;
	LegacyRecord->Entries = JobLedger.GetEntries();
	TestTrue(TEXT("Legacy first-payout save writes to the QA slot"), UGameplayStatics::SaveGameToSlot(LegacyRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	const int64 MigrationStartedAt = FDateTime::UtcNow().ToUnixTimestamp();
	FOddsWellOddsBucksLedger MigratedLedger;
	int64 MigratedNextJobPayout = 0;
	TestTrue(TEXT("Legacy first-payout save migrates"), LoadOddsWellOddsBucksLedger(true, MigratedLedger, MigratedNextJobPayout, bFound, Error));
	TestEqual(TEXT("Migration preserves the first payout"), MigratedLedger.GetBalance(), int64{100});
	TestTrue(TEXT("Migration starts a fresh 24-hour wait"), MigratedNextJobPayout >= MigrationStartedAt + GetOddsWellJobPayoutIntervalSeconds());
	const UOddsWellOddsBucksSaveGame* MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
	TestTrue(TEXT("Migrated QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));

	UOddsWellOddsBucksSaveGame* VersionTwoRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionTwoRecord->SchemaVersion = 2;
	VersionTwoRecord->Entries = JobLedger.GetEntries();
	VersionTwoRecord->NextJobPayoutUnixSeconds = ExpectedNextJobPayout;
	TestTrue(TEXT("Schema v2 job save writes to the QA slot"), UGameplayStatics::SaveGameToSlot(VersionTwoRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TArray<FOddsWellMatchWinnerRequestRecord> MigratedRequests;
	TestTrue(TEXT("Schema v2 job save migrates"), LoadOddsWellOddsBucksState(true, MigratedLedger, MigratedNextJobPayout, MigratedRequests, bFound, Error));
	TestEqual(TEXT("Schema v2 migration preserves job balance"), MigratedLedger.GetBalance(), int64{100});
	TestEqual(TEXT("Schema v2 migration preserves job cooldown"), MigratedNextJobPayout, ExpectedNextJobPayout);
	TestEqual(TEXT("Schema v2 migration invents no wager"), MigratedRequests.Num(), 0);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v2 migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
	TestTrue(TEXT("Migrated schema v2 cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));

	TestEqual(TEXT("Existing valid job path funds wager QA"), JobLedger.GetBalance(), int64{100});
	TestTrue(TEXT("Funded job state saves for wager QA"), SaveOddsWellOddsBucksLedger(JobLedger, ExpectedNextJobPayout, true, Error));
	const FOddsWellMatchWinnerOffer Offer = MakeMatchWinnerTestOffer();
	FString CalculatedOfferId;
	TestTrue(TEXT("Exact Phase 1H.2 offer identity hashes"), GetMatchWinnerOfferId(Offer, CalculatedOfferId, Error));
	TestEqual(TEXT("Exact Phase 1H.2 offer identity matches Python canonical SHA-256"), CalculatedOfferId, Offer.OfferId);
	FOddsWellMatchWinnerRequestRecord AcceptedRequest;
	int64 WagerBalance = 0;
	TestEqual(
		TEXT("Valid pre-lock Match Winner request is accepted"),
		AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-1"), Offer.HomeTeam, 40, Offer.LockUnixSeconds - 100, true, AcceptedRequest, WagerBalance, Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	TestEqual(TEXT("Accepted stake debits the job-funded balance"), WagerBalance, int64{60});
	TestEqual(TEXT("Accepted record remains pending lock"), AcceptedRequest.Status, AcceptedPendingLockStatus);
	TestEqual(TEXT("Accepted record links the exact offer"), AcceptedRequest.OfferId, Offer.OfferId);
	TestEqual(TEXT("Accepted record links the exact ledger command"), AcceptedRequest.StakeLedgerCommandId, AcceptedRequest.RequestCommandId);

	FOddsWellOddsBucksLedger WagerLedger;
	int64 WagerNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> WagerRequests;
	TestTrue(TEXT("Accepted wager cold-restores from one state record"), LoadOddsWellOddsBucksState(true, WagerLedger, WagerNextJobPayout, WagerRequests, bFound, Error));
	TestEqual(TEXT("Cold restore preserves job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);
	TestEqual(TEXT("Cold restore preserves credit plus one debit"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Cold restore preserves debited balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Cold restore preserves exactly one request"), WagerRequests.Num(), 1);
	TestEqual(TEXT("Cold restore preserves accepted time"), WagerRequests[0].AcceptedUnixSeconds, Offer.LockUnixSeconds - 100);

	FOddsWellMatchWinnerRequestRecord RetryRecord;
	TestEqual(
		TEXT("Exact retry after lock is idempotent"),
		AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-1"), Offer.HomeTeam, 40, Offer.LockUnixSeconds, true, RetryRecord, WagerBalance, Error),
		EOddsWellMatchWinnerRequestResult::Duplicate);
	TestEqual(TEXT("Exact retry does not debit again"), WagerBalance, int64{60});
	TestEqual(
		TEXT("Conflicting request command reuse is rejected"),
		AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-1"), Offer.HomeTeam, 50, Offer.LockUnixSeconds - 50, true, RetryRecord, WagerBalance, Error),
		EOddsWellMatchWinnerRequestResult::Rejected);

	FOddsWellMatchWinnerOffer TamperedOffer = Offer;
	TamperedOffer.GameNumber++;
	TestEqual(TEXT("Tampered offer identity is rejected"), AcceptOddsWellMatchWinnerRequest(TamperedOffer, TEXT("wager:match_winner:test-2"), TamperedOffer.HomeTeam, 10, TamperedOffer.LockUnixSeconds - 1, true, RetryRecord, WagerBalance, Error), EOddsWellMatchWinnerRequestResult::Rejected);
	TestEqual(TEXT("Invalid stake is rejected"), AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-3"), Offer.HomeTeam, 15, Offer.LockUnixSeconds - 1, true, RetryRecord, WagerBalance, Error), EOddsWellMatchWinnerRequestResult::Rejected);
	TestEqual(TEXT("Invalid team is rejected"), AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-4"), TEXT("Not Offered"), 10, Offer.LockUnixSeconds - 1, true, RetryRecord, WagerBalance, Error), EOddsWellMatchWinnerRequestResult::Rejected);
	TestEqual(TEXT("At-lock request is rejected"), AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-5"), Offer.AwayTeam, 10, Offer.LockUnixSeconds, true, RetryRecord, WagerBalance, Error), EOddsWellMatchWinnerRequestResult::Rejected);
	TestEqual(TEXT("Insufficient balance is rejected"), AcceptOddsWellMatchWinnerRequest(Offer, TEXT("wager:match_winner:test-6"), Offer.AwayTeam, 100, Offer.LockUnixSeconds - 1, true, RetryRecord, WagerBalance, Error), EOddsWellMatchWinnerRequestResult::Rejected);
	TestTrue(TEXT("Rejected requests leave persisted state readable"), LoadOddsWellOddsBucksState(true, WagerLedger, WagerNextJobPayout, WagerRequests, bFound, Error));
	TestEqual(TEXT("Rejected requests append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Rejected requests preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Rejected requests append no request record"), WagerRequests.Num(), 1);

	UOddsWellOddsBucksSaveGame* VersionThreeRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionThreeRecord->SchemaVersion = 3;
	VersionThreeRecord->Entries = WagerLedger.GetEntries();
	VersionThreeRecord->NextJobPayoutUnixSeconds = WagerNextJobPayout;
	VersionThreeRecord->MatchWinnerRequests = WagerRequests;
	TestTrue(TEXT("Schema v3 accepted request writes to the QA slot"), UGameplayStatics::SaveGameToSlot(VersionThreeRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TArray<FOddsWellMatchWinnerLockRecord> WagerLocks;
	TestTrue(TEXT("Schema v3 accepted request migrates"), LoadOddsWellOddsBucksWagerState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, bFound, Error));
	TestEqual(TEXT("Schema v3 migration preserves one request"), WagerRequests.Num(), 1);
	TestEqual(TEXT("Schema v3 migration preserves pending request evidence"), WagerRequests[0].Status, AcceptedPendingLockStatus);
	TestEqual(TEXT("Schema v3 migration invents no lock"), WagerLocks.Num(), 0);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v3 migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	FOddsWellMatchWinnerLockRecord LockRecord;
	const FString RequestCommandId(TEXT("wager:match_winner:test-1"));
	const FString LockCommandId(TEXT("wager:match_winner:lock:test-1"));
	const FString ResultCommandId(TEXT("wager:match_winner:result:test-1"));
	FOddsWellMatchWinnerResultLinkRecord ExactResultInput;
	ExactResultInput.ResultCommandId = ResultCommandId;
	ExactResultInput.RequestCommandId = RequestCommandId;
	ExactResultInput.LockCommandId = LockCommandId;
	ExactResultInput.ResultSchema = MatchWinnerResultSchema;
	ExactResultInput.ResultVersion = MatchWinnerResultVersion;
	ExactResultInput.SeasonNumber = SealedResultSeasonNumber;
	ExactResultInput.GameNumber = SealedResultGameNumber;
	ExactResultInput.HomeTeam = SealedResultHomeTeam;
	ExactResultInput.AwayTeam = SealedResultAwayTeam;
	ExactResultInput.HomeScore = SealedResultHomeScore;
	ExactResultInput.AwayScore = SealedResultAwayScore;
	ExactResultInput.Winner = SealedResultWinner;
	ExactResultInput.ReplaySealSha256 = SealedResultReplaySha;
	auto LinkResult = [&Error](const FOddsWellMatchWinnerResultLinkRecord& Input, FOddsWellMatchWinnerResultLinkRecord& Output)
	{
		return LinkOddsWellMatchWinnerResult(
			Input.ResultCommandId,
			Input.RequestCommandId,
			Input.LockCommandId,
			Input.ResultSchema,
			Input.ResultVersion,
			Input.SeasonNumber,
			Input.GameNumber,
			Input.HomeTeam,
			Input.AwayTeam,
			Input.HomeScore,
			Input.AwayScore,
			Input.Winner,
			Input.ReplaySealSha256,
			true,
			Output,
			Error);
	};
	FOddsWellMatchWinnerResultLinkRecord ResultRecord;
	TestEqual(TEXT("Accepted but unlocked request cannot link a result"), LinkResult(ExactResultInput, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TestEqual(TEXT("Unknown accepted request cannot lock"), LockOddsWellMatchWinnerRequest(TEXT("wager:match_winner:unknown"), TEXT("wager:match_winner:lock:unknown"), Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds, true, LockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestEqual(TEXT("Wrong game identity cannot lock"), LockOddsWellMatchWinnerRequest(RequestCommandId, TEXT("wager:match_winner:lock:wrong-game"), Offer.SeasonNumber, Offer.GameNumber + 1, Offer.LockUnixSeconds, true, LockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestEqual(TEXT("Prestart time cannot lock"), LockOddsWellMatchWinnerRequest(RequestCommandId, TEXT("wager:match_winner:lock:prestart"), Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds - 1, true, LockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestEqual(TEXT("Post-start mismatch cannot lock"), LockOddsWellMatchWinnerRequest(RequestCommandId, TEXT("wager:match_winner:lock:late"), Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds + 1, true, LockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestEqual(TEXT("Malformed lock identity is rejected"), LockOddsWellMatchWinnerRequest(RequestCommandId, RequestCommandId, Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds, true, LockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestTrue(TEXT("Rejected lock commands leave state readable"), LoadOddsWellOddsBucksWagerState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, bFound, Error));
	TestEqual(TEXT("Rejected lock commands append no lock"), WagerLocks.Num(), 0);
	TestEqual(TEXT("Rejected lock commands preserve balance"), WagerLedger.GetBalance(), int64{60});

	TestEqual(TEXT("Exact game-start command locks the accepted request"), LockOddsWellMatchWinnerRequest(RequestCommandId, LockCommandId, Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds, true, LockRecord, Error), EOddsWellMatchWinnerLockResult::Locked);
	TestEqual(TEXT("Lock record links the accepted request"), LockRecord.RequestCommandId, RequestCommandId);
	TestEqual(TEXT("Lock record stores the exact decision"), LockRecord.Decision, MatchWinnerLockedDecision);
	TestEqual(TEXT("Lock record stores the authoritative game start"), LockRecord.AuthoritativeGameStartUnixSeconds, Offer.LockUnixSeconds);
	TestTrue(TEXT("Locked wager cold-restores from the shared state"), LoadOddsWellOddsBucksWagerState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, bFound, Error));
	TestEqual(TEXT("Cold restore preserves exactly one lock"), WagerLocks.Num(), 1);
	TestEqual(TEXT("Cold restore preserves the exact lock command"), WagerLocks[0].LockCommandId, LockCommandId);
	TestEqual(TEXT("Lock does not rewrite accepted request evidence"), WagerRequests[0].Status, AcceptedPendingLockStatus);
	TestEqual(TEXT("Lock appends no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Lock preserves debited balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Lock preserves job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	FOddsWellMatchWinnerLockRecord RetryLockRecord;
	TestEqual(TEXT("Exact lock retry is idempotent"), LockOddsWellMatchWinnerRequest(RequestCommandId, LockCommandId, Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds, true, RetryLockRecord, Error), EOddsWellMatchWinnerLockResult::Duplicate);
	TestEqual(TEXT("Conflicting lock command reuse is rejected"), LockOddsWellMatchWinnerRequest(RequestCommandId, LockCommandId, Offer.SeasonNumber, Offer.GameNumber + 1, Offer.LockUnixSeconds, true, RetryLockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestEqual(TEXT("A second lock command for one request is rejected"), LockOddsWellMatchWinnerRequest(RequestCommandId, TEXT("wager:match_winner:lock:test-2"), Offer.SeasonNumber, Offer.GameNumber, Offer.LockUnixSeconds, true, RetryLockRecord, Error), EOddsWellMatchWinnerLockResult::Rejected);
	TestTrue(TEXT("Lock retries and conflicts leave state readable"), LoadOddsWellOddsBucksWagerState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, bFound, Error));
	TestEqual(TEXT("Lock retries and conflicts append no lock"), WagerLocks.Num(), 1);
	TestEqual(TEXT("Lock retries and conflicts append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Lock retries and conflicts preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Lock retries and conflicts preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	UOddsWellOddsBucksSaveGame* VersionFourRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionFourRecord->SchemaVersion = 4;
	VersionFourRecord->Entries = WagerLedger.GetEntries();
	VersionFourRecord->NextJobPayoutUnixSeconds = WagerNextJobPayout;
	VersionFourRecord->MatchWinnerRequests = WagerRequests;
	VersionFourRecord->MatchWinnerLocks = WagerLocks;
	TestTrue(TEXT("Schema v4 locked request writes to the QA slot"), UGameplayStatics::SaveGameToSlot(VersionFourRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TArray<FOddsWellMatchWinnerResultLinkRecord> WagerResultLinks;
	TestTrue(TEXT("Schema v4 locked request migrates"), LoadOddsWellOddsBucksWagerEvidence(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, bFound, Error));
	TestEqual(TEXT("Schema v4 migration preserves one request"), WagerRequests.Num(), 1);
	TestEqual(TEXT("Schema v4 migration preserves one lock"), WagerLocks.Num(), 1);
	TestEqual(TEXT("Schema v4 migration invents no result link"), WagerResultLinks.Num(), 0);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v4 migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	FOddsWellMatchWinnerResultLinkRecord TamperedResult = ExactResultInput;
	TamperedResult.RequestCommandId = TEXT("wager:match_winner:unknown");
	TestEqual(TEXT("Unknown request cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.LockCommandId = TEXT("wager:match_winner:lock:unknown");
	TestEqual(TEXT("Wrong lock cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.AwayScore = TamperedResult.HomeScore;
	TamperedResult.Winner = TamperedResult.HomeTeam;
	TestEqual(TEXT("Tied archive data cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.HomeScore++;
	TestEqual(TEXT("Wrong score cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.Winner = TamperedResult.HomeTeam;
	TestEqual(TEXT("Wrong winner cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.ReplaySealSha256 = TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
	TestEqual(TEXT("Wrong replay seal cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.GameNumber++;
	TestEqual(TEXT("Wrong archive game cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.HomeTeam = TEXT("Wrong Team");
	TestEqual(TEXT("Wrong archive team cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.ResultSchema = TEXT("wrong-schema");
	TestEqual(TEXT("Wrong result schema cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.ResultVersion = TEXT("wrong-version");
	TestEqual(TEXT("Wrong result version cannot link a result"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.ResultCommandId = RequestCommandId;
	TestEqual(TEXT("Malformed result command identity is rejected"), LinkResult(TamperedResult, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TestTrue(TEXT("Rejected result links leave evidence readable"), LoadOddsWellOddsBucksWagerEvidence(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, bFound, Error));
	TestEqual(TEXT("Rejected result links append no link"), WagerResultLinks.Num(), 0);
	TestEqual(TEXT("Rejected result links append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Rejected result links preserve debited balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Rejected result links preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	TestEqual(TEXT("Exact verified archive links to the locked request"), LinkResult(ExactResultInput, ResultRecord), EOddsWellMatchWinnerResultLinkResult::Linked);
	TestEqual(TEXT("Result link stores exact request command"), ResultRecord.RequestCommandId, RequestCommandId);
	TestEqual(TEXT("Result link stores exact lock command"), ResultRecord.LockCommandId, LockCommandId);
	TestEqual(TEXT("Result link stores archive winner"), ResultRecord.Winner, SealedResultWinner);
	TestEqual(TEXT("Result link stores replay seal"), ResultRecord.ReplaySealSha256, SealedResultReplaySha);
	TestTrue(TEXT("Result link cold-restores from shared state"), LoadOddsWellOddsBucksWagerEvidence(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, bFound, Error));
	TestEqual(TEXT("Cold restore preserves exactly one result link"), WagerResultLinks.Num(), 1);
	TestEqual(TEXT("Result link does not rewrite request evidence"), WagerRequests[0].Status, AcceptedPendingLockStatus);
	TestEqual(TEXT("Result link does not rewrite lock evidence"), WagerLocks[0].Decision, MatchWinnerLockedDecision);
	TestEqual(TEXT("Result link appends no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Result link preserves debited balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Result link preserves job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	FOddsWellMatchWinnerResultLinkRecord RetryResultRecord;
	TestEqual(TEXT("Exact result-link retry is idempotent"), LinkResult(ExactResultInput, RetryResultRecord), EOddsWellMatchWinnerResultLinkResult::Duplicate);
	TamperedResult = ExactResultInput;
	TamperedResult.HomeScore++;
	TestEqual(TEXT("Conflicting result command reuse is rejected"), LinkResult(TamperedResult, RetryResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TamperedResult = ExactResultInput;
	TamperedResult.ResultCommandId = TEXT("wager:match_winner:result:test-2");
	TestEqual(TEXT("A second result command for one request is rejected"), LinkResult(TamperedResult, RetryResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
	TestTrue(TEXT("Result retries and conflicts leave evidence readable"), LoadOddsWellOddsBucksWagerEvidence(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, bFound, Error));
	TestEqual(TEXT("Result retries and conflicts preserve one result link"), WagerResultLinks.Num(), 1);
	TestEqual(TEXT("Result retries and conflicts append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Result retries and conflicts preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Result retries and conflicts preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	UOddsWellOddsBucksSaveGame* VersionFiveRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionFiveRecord->SchemaVersion = 5;
	VersionFiveRecord->Entries = WagerLedger.GetEntries();
	VersionFiveRecord->NextJobPayoutUnixSeconds = WagerNextJobPayout;
	VersionFiveRecord->MatchWinnerRequests = WagerRequests;
	VersionFiveRecord->MatchWinnerLocks = WagerLocks;
	VersionFiveRecord->MatchWinnerResultLinks = WagerResultLinks;
	TestTrue(TEXT("Schema v5 result-linked request writes to the QA slot"), UGameplayStatics::SaveGameToSlot(VersionFiveRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> WagerDecisions;
	TestTrue(TEXT("Schema v5 result-linked request migrates"), LoadOddsWellOddsBucksWagerDecisionState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, bFound, Error));
	TestEqual(TEXT("Schema v5 migration preserves one request"), WagerRequests.Num(), 1);
	TestEqual(TEXT("Schema v5 migration preserves one lock"), WagerLocks.Num(), 1);
	TestEqual(TEXT("Schema v5 migration preserves one result link"), WagerResultLinks.Num(), 1);
	TestEqual(TEXT("Schema v5 migration invents no settlement decision"), WagerDecisions.Num(), 0);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v5 migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	const FString DecisionCommandId(TEXT("wager:match_winner:decision:test-1"));
	FOddsWellMatchWinnerSettlementDecisionRecord DecisionRecord;
	TestEqual(TEXT("Unknown request cannot produce a settlement decision"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, TEXT("wager:match_winner:unknown"), LockCommandId, ResultCommandId, true, DecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("Wrong lock cannot produce a settlement decision"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, RequestCommandId, TEXT("wager:match_winner:lock:unknown"), ResultCommandId, true, DecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("Wrong result cannot produce a settlement decision"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, RequestCommandId, LockCommandId, TEXT("wager:match_winner:result:unknown"), true, DecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("Malformed settlement decision identity is rejected"), DecideOddsWellMatchWinnerSettlement(RequestCommandId, RequestCommandId, LockCommandId, ResultCommandId, true, DecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestTrue(TEXT("Rejected decisions leave evidence readable"), LoadOddsWellOddsBucksWagerDecisionState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, bFound, Error));
	TestEqual(TEXT("Rejected decisions append no decision"), WagerDecisions.Num(), 0);
	TestEqual(TEXT("Rejected decisions append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Rejected decisions preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Rejected decisions preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	TestEqual(TEXT("Exact request-lock-result chain creates one decision"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, RequestCommandId, LockCommandId, ResultCommandId, true, DecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Decided);
	TestEqual(TEXT("Decision stores exact offer identity"), DecisionRecord.OfferId, Offer.OfferId);
	TestEqual(TEXT("Decision stores selected Harbor team"), DecisionRecord.SelectedTeam, SealedResultHomeTeam);
	TestEqual(TEXT("Decision stores authoritative Mesa winner"), DecisionRecord.AuthoritativeWinner, SealedResultWinner);
	TestEqual(TEXT("Decision stores exact stake"), DecisionRecord.Stake, int64{40});
	TestEqual(TEXT("Decision derives lost outcome"), DecisionRecord.Outcome, MatchWinnerLostOutcome);
	TestEqual(TEXT("Lost decision has zero gross return due"), DecisionRecord.GrossReturnDue, int64{0});
	TestEqual(TEXT("Lost decision binds no win probability"), DecisionRecord.SelectedWinProbabilityE8, int64{0});
	TestTrue(TEXT("Lost decision binds no payout formula"), DecisionRecord.PayoutFormula.IsEmpty());
	TestEqual(TEXT("Decision remains pending application"), DecisionRecord.Status, MatchWinnerDecidedPendingApplyStatus);
	TestTrue(TEXT("Settlement decision cold-restores from shared state"), LoadOddsWellOddsBucksWagerDecisionState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, bFound, Error));
	TestEqual(TEXT("Cold restore preserves exactly one decision"), WagerDecisions.Num(), 1);
	TestEqual(TEXT("Decision does not rewrite request evidence"), WagerRequests[0].Status, AcceptedPendingLockStatus);
	TestEqual(TEXT("Decision does not rewrite lock evidence"), WagerLocks[0].Decision, MatchWinnerLockedDecision);
	TestEqual(TEXT("Decision does not rewrite result evidence"), WagerResultLinks[0].ReplaySealSha256, SealedResultReplaySha);
	TestEqual(TEXT("Decision appends no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Decision preserves debited balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Decision preserves job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	FOddsWellMatchWinnerSettlementDecisionRecord RetryDecisionRecord;
	TestEqual(TEXT("Exact settlement decision retry is idempotent"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, RequestCommandId, LockCommandId, ResultCommandId, true, RetryDecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Duplicate);
	TestEqual(TEXT("Conflicting settlement decision command reuse is rejected"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, RequestCommandId, LockCommandId, TEXT("wager:match_winner:result:unknown"), true, RetryDecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("A second settlement decision for one request is rejected"), DecideOddsWellMatchWinnerSettlement(TEXT("wager:match_winner:decision:test-2"), RequestCommandId, LockCommandId, ResultCommandId, true, RetryDecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestTrue(TEXT("Decision retries and conflicts leave evidence readable"), LoadOddsWellOddsBucksWagerDecisionState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, bFound, Error));
	TestEqual(TEXT("Decision retries preserve one decision"), WagerDecisions.Num(), 1);
	TestEqual(TEXT("Decision retries append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Decision retries preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Decision retries preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	UOddsWellOddsBucksSaveGame* VersionSixRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionSixRecord->SchemaVersion = 6;
	VersionSixRecord->Entries = WagerLedger.GetEntries();
	VersionSixRecord->NextJobPayoutUnixSeconds = WagerNextJobPayout;
	VersionSixRecord->MatchWinnerRequests = WagerRequests;
	VersionSixRecord->MatchWinnerLocks = WagerLocks;
	VersionSixRecord->MatchWinnerResultLinks = WagerResultLinks;
	VersionSixRecord->MatchWinnerSettlementDecisions = WagerDecisions;
	TestTrue(TEXT("Schema v6 pending loss decision writes to the QA slot"), UGameplayStatics::SaveGameToSlot(VersionSixRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> WagerFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WagerWinFinalizations;
	TestTrue(TEXT("Schema v6 pending loss decision migrates"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Schema v6 migration preserves one request"), WagerRequests.Num(), 1);
	TestEqual(TEXT("Schema v6 migration preserves one lock"), WagerLocks.Num(), 1);
	TestEqual(TEXT("Schema v6 migration preserves one result link"), WagerResultLinks.Num(), 1);
	TestEqual(TEXT("Schema v6 migration preserves one decision"), WagerDecisions.Num(), 1);
	TestEqual(TEXT("Schema v6 migration invents no finalization"), WagerFinalizations.Num(), 0);
	TestEqual(TEXT("Schema v6 migration invents no win finalization"), WagerWinFinalizations.Num(), 0);
	TestFalse(TEXT("Pending decision publishes no finalized-loss reconciliation"), IFileManager::Get().FileExists(*GetMatchWinnerReconciliationPath(true)));
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v6 migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	const FString FinalizationCommandId(TEXT("wager:match_winner:finalization:test-1"));
	FOddsWellMatchWinnerLossFinalizationRecord FinalizationRecord;
	TestEqual(TEXT("Unknown decision cannot finalize a loss"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, TEXT("wager:match_winner:decision:unknown"), true, FinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestEqual(TEXT("Malformed finalization identity is rejected"), FinalizeOddsWellMatchWinnerLoss(DecisionCommandId, DecisionCommandId, true, FinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestTrue(TEXT("Rejected finalizations leave evidence readable"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Rejected finalizations append no record"), WagerFinalizations.Num(), 0);
	TestEqual(TEXT("Rejected finalizations append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Rejected finalizations preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Rejected finalizations preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	TestEqual(TEXT("Exact pending loss finalizes once"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, DecisionCommandId, true, FinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Finalized);
	TestEqual(TEXT("Finalization links exact decision"), FinalizationRecord.DecisionCommandId, DecisionCommandId);
	TestEqual(TEXT("Finalization links exact request"), FinalizationRecord.RequestCommandId, RequestCommandId);
	TestEqual(TEXT("Finalization links exact lock"), FinalizationRecord.LockCommandId, LockCommandId);
	TestEqual(TEXT("Finalization links exact result"), FinalizationRecord.ResultCommandId, ResultCommandId);
	TestEqual(TEXT("Finalization stores Harbor selection"), FinalizationRecord.SelectedTeam, SealedResultHomeTeam);
	TestEqual(TEXT("Finalization stores Mesa winner"), FinalizationRecord.AuthoritativeWinner, SealedResultWinner);
	TestEqual(TEXT("Finalization stores exact stake"), FinalizationRecord.Stake, int64{40});
	TestEqual(TEXT("Finalization stores lost outcome"), FinalizationRecord.Outcome, MatchWinnerLostOutcome);
	TestEqual(TEXT("Loss finalization applies zero gross return"), FinalizationRecord.GrossReturnApplied, int64{0});
	TestEqual(TEXT("Loss finalization stores final status"), FinalizationRecord.Status, MatchWinnerSettledLostStatus);
	TestEqual(TEXT("Loss finalization observes balance 60"), FinalizationRecord.ObservedFinalBalance, int64{60});
	TestEqual(TEXT("Loss finalization observes two ledger entries"), FinalizationRecord.ObservedLedgerEntryCount, 2);
	const FString MatchWinnerProjectionPath = GetMatchWinnerReconciliationPath(true);
	TestTrue(TEXT("Exact loss finalization publishes reconciliation atomically"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString MatchWinnerProjectionJson;
	FString NormalizedMatchWinnerProjectionJson;
	TSharedPtr<FJsonObject> MatchWinnerProjection;
	TestTrue(TEXT("Exact loss reconciliation reads"), FFileHelper::LoadFileToString(MatchWinnerProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> MatchWinnerProjectionReader = TJsonReaderFactory<>::Create(MatchWinnerProjectionJson);
	TestTrue(TEXT("Exact loss reconciliation parses"), FJsonSerializer::Deserialize(MatchWinnerProjectionReader, MatchWinnerProjection) && MatchWinnerProjection.IsValid());
	if (MatchWinnerProjection.IsValid())
	{
		TestEqual(TEXT("Reconciliation schema is separate v1"), MatchWinnerProjection->GetStringField(TEXT("schema")), MatchWinnerReconciliationSchema);
		TestEqual(TEXT("Reconciliation selected Harbor"), MatchWinnerProjection->GetStringField(TEXT("selected_team")), SealedResultHomeTeam);
		TestEqual(TEXT("Reconciliation winner is Mesa"), MatchWinnerProjection->GetStringField(TEXT("winner")), SealedResultWinner);
		TestEqual(TEXT("Reconciliation stake debit command is exact"), MatchWinnerProjection->GetStringField(TEXT("stake_ledger_command_id")), RequestCommandId);
		TestEqual(TEXT("Reconciliation stake debit sequence is two"), static_cast<int64>(MatchWinnerProjection->GetNumberField(TEXT("stake_sequence"))), int64{2});
		TestEqual(TEXT("Reconciliation stake debit is minus forty"), static_cast<int64>(MatchWinnerProjection->GetNumberField(TEXT("stake_delta"))), int64{-40});
		TestEqual(TEXT("Reconciliation decision remains pending"), MatchWinnerProjection->GetStringField(TEXT("decision_status")), MatchWinnerDecidedPendingApplyStatus.ToString());
		TestEqual(TEXT("Reconciliation finalization is settled lost"), MatchWinnerProjection->GetStringField(TEXT("finalization_status")), MatchWinnerSettledLostStatus.ToString());
		TestEqual(TEXT("Reconciliation links exact replay seal"), MatchWinnerProjection->GetStringField(TEXT("replay_seal_sha256")), SealedResultReplaySha);
		TestEqual(TEXT("Reconciliation reports two ledger entries"), static_cast<int32>(MatchWinnerProjection->GetNumberField(TEXT("ledger_entry_count"))), 2);
		TestEqual(TEXT("Reconciliation reports balance sixty"), static_cast<int64>(MatchWinnerProjection->GetNumberField(TEXT("final_balance"))), int64{60});
		TestEqual(TEXT("Reconciliation reports net minus forty"), static_cast<int64>(MatchWinnerProjection->GetNumberField(TEXT("net"))), int64{-40});
		TestTrue(TEXT("Reconciliation is read only"), MatchWinnerProjection->GetBoolField(TEXT("read_only_projection")));
		TestTrue(TEXT("Reconciliation is labeled QA"), MatchWinnerProjection->GetBoolField(TEXT("qa")));
		MatchWinnerProjection->RemoveField(TEXT("generated_at_utc"));
		const TSharedRef<TJsonWriter<>> NormalizedProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedMatchWinnerProjectionJson);
		TestTrue(TEXT("Exact loss reconciliation normalizes"), FJsonSerializer::Serialize(MatchWinnerProjection.ToSharedRef(), NormalizedProjectionWriter));
	}
	TestTrue(TEXT("QA can remove finalized-loss projection for cold-load proof"), IFileManager::Get().Delete(*MatchWinnerProjectionPath, false, true, true));
	TestFalse(TEXT("Finalized-loss projection is absent before cold load"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	TestTrue(TEXT("Loss finalization cold-restores from shared state"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestTrue(TEXT("Validated cold load regenerates finalized-loss reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString RegeneratedProjectionJson;
	TSharedPtr<FJsonObject> RegeneratedProjection;
	TestTrue(TEXT("Regenerated exact loss reconciliation reads"), FFileHelper::LoadFileToString(RegeneratedProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> RegeneratedProjectionReader = TJsonReaderFactory<>::Create(RegeneratedProjectionJson);
	TestTrue(TEXT("Regenerated exact loss reconciliation parses"), FJsonSerializer::Deserialize(RegeneratedProjectionReader, RegeneratedProjection) && RegeneratedProjection.IsValid());
	if (RegeneratedProjection.IsValid())
	{
		RegeneratedProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedRegeneratedProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedRegeneratedProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedRegeneratedProjectionJson);
		TestTrue(TEXT("Regenerated exact loss reconciliation normalizes"), FJsonSerializer::Serialize(RegeneratedProjection.ToSharedRef(), NormalizedRegeneratedProjectionWriter));
		TestEqual(TEXT("Cold load regenerates identical reconciliation data"), NormalizedRegeneratedProjectionJson, NormalizedMatchWinnerProjectionJson);
	}
	TestEqual(TEXT("Cold restore preserves exactly one finalization"), WagerFinalizations.Num(), 1);
	TestEqual(TEXT("Finalization does not rewrite pending decision"), WagerDecisions[0].Status, MatchWinnerDecidedPendingApplyStatus);
	TestEqual(TEXT("Finalization does not rewrite result evidence"), WagerResultLinks[0].ReplaySealSha256, SealedResultReplaySha);
	TestEqual(TEXT("Finalization appends no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Finalization preserves balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Finalization preserves job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);

	FOddsWellMatchWinnerLossFinalizationRecord RetryFinalizationRecord;
	TestEqual(TEXT("Exact loss finalization retry is idempotent"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, DecisionCommandId, true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Duplicate);
	TestEqual(TEXT("Conflicting finalization command reuse is rejected"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, TEXT("wager:match_winner:decision:unknown"), true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestEqual(TEXT("A second finalization for one decision is rejected"), FinalizeOddsWellMatchWinnerLoss(TEXT("wager:match_winner:finalization:test-2"), DecisionCommandId, true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestTrue(TEXT("Finalization retries and conflicts leave evidence readable"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Finalization retries preserve one finalization"), WagerFinalizations.Num(), 1);
	TestEqual(TEXT("Finalization retries append no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Finalization retries preserve balance"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Finalization retries preserve job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);
	UOddsWellOddsBucksSaveGame* VersionSevenLossRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionSevenLossRecord->SchemaVersion = 7;
	VersionSevenLossRecord->Entries = WagerLedger.GetEntries();
	VersionSevenLossRecord->NextJobPayoutUnixSeconds = WagerNextJobPayout;
	VersionSevenLossRecord->MatchWinnerRequests = WagerRequests;
	VersionSevenLossRecord->MatchWinnerLocks = WagerLocks;
	VersionSevenLossRecord->MatchWinnerResultLinks = WagerResultLinks;
	VersionSevenLossRecord->MatchWinnerSettlementDecisions = WagerDecisions;
	VersionSevenLossRecord->MatchWinnerLossFinalizations = WagerFinalizations;
	TestTrue(TEXT("Schema v7 finalized loss writes before migration"), UGameplayStatics::SaveGameToSlot(VersionSevenLossRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v7 finalized loss migrates"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Schema v7 migration preserves loss history"), WagerFinalizations.Num(), 1);
	TestEqual(TEXT("Schema v7 migration invents no win finalization"), WagerWinFinalizations.Num(), 0);
	TestEqual(TEXT("Schema v7 migration preserves loss balance"), WagerLedger.GetBalance(), int64{60});
	TArray<uint8> ExactLossProfileBytes;
	TestTrue(TEXT("Exact finalized loss profile is preserved before isolated win QA"), UGameplayStatics::SaveGameToMemory(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex), ExactLossProfileBytes));

	UOddsWellOddsBucksSaveGame* MalformedFinalizationRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved finalization is available for corruption test"), MalformedFinalizationRecord && MalformedFinalizationRecord->MatchWinnerLossFinalizations.Num() == 1);
	if (MalformedFinalizationRecord && MalformedFinalizationRecord->MatchWinnerLossFinalizations.Num() == 1)
	{
		MalformedFinalizationRecord->MatchWinnerLossFinalizations[0].ObservedFinalBalance = 61;
		TestFalse(TEXT("Malformed persisted finalization is rejected in memory"), ValidateOddsBucksSave(MalformedFinalizationRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
		TestTrue(TEXT("Malformed persisted finalization writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedFinalizationRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Malformed persisted finalization rejects finalization command"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, DecisionCommandId, true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
		const UOddsWellOddsBucksSaveGame* PersistedMalformedFinalization = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected command does not rewrite malformed persisted finalization"), PersistedMalformedFinalization
			&& PersistedMalformedFinalization->MatchWinnerLossFinalizations.Num() == 1
			&& PersistedMalformedFinalization->MatchWinnerLossFinalizations[0].ObservedFinalBalance == 61);
		MalformedFinalizationRecord->MatchWinnerLossFinalizations[0].ObservedFinalBalance = 60;
		TestTrue(TEXT("Valid finalization evidence restores after corruption QA"), UGameplayStatics::SaveGameToSlot(MalformedFinalizationRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Restored finalization evidence validates"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	}

	UOddsWellOddsBucksSaveGame* MalformedDecisionRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved decision is available for corruption test"), MalformedDecisionRecord && MalformedDecisionRecord->MatchWinnerSettlementDecisions.Num() == 1);
	if (MalformedDecisionRecord && MalformedDecisionRecord->MatchWinnerSettlementDecisions.Num() == 1)
	{
		MalformedDecisionRecord->MatchWinnerSettlementDecisions[0].GrossReturnDue = 1;
		TestFalse(TEXT("Malformed persisted decision is rejected in memory"), ValidateOddsBucksSave(MalformedDecisionRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
		TestTrue(TEXT("Malformed persisted decision writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedDecisionRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Malformed persisted decision rejects a decision command"), DecideOddsWellMatchWinnerSettlement(DecisionCommandId, RequestCommandId, LockCommandId, ResultCommandId, true, RetryDecisionRecord, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestEqual(TEXT("Nonzero-return decision rejects loss finalization"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, DecisionCommandId, true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
		const UOddsWellOddsBucksSaveGame* PersistedMalformedDecision = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected command does not rewrite malformed persisted decision"), PersistedMalformedDecision
			&& PersistedMalformedDecision->MatchWinnerSettlementDecisions.Num() == 1
			&& PersistedMalformedDecision->MatchWinnerSettlementDecisions[0].GrossReturnDue == 1);
		MalformedDecisionRecord->MatchWinnerSettlementDecisions[0].GrossReturnDue = 0;
		TestTrue(TEXT("Valid decision evidence restores after corruption QA"), UGameplayStatics::SaveGameToSlot(MalformedDecisionRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Restored decision evidence validates"), LoadOddsWellOddsBucksWagerDecisionState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, bFound, Error));

		MalformedDecisionRecord->MatchWinnerSettlementDecisions[0].Outcome = MatchWinnerWonOutcome;
		TestFalse(TEXT("Nonloss persisted decision is rejected in memory"), ValidateOddsBucksSave(MalformedDecisionRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
		TestTrue(TEXT("Nonloss persisted decision writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedDecisionRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Nonloss decision rejects loss finalization"), FinalizeOddsWellMatchWinnerLoss(FinalizationCommandId, DecisionCommandId, true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
		const UOddsWellOddsBucksSaveGame* PersistedNonlossDecision = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected loss finalization does not rewrite nonloss decision"), PersistedNonlossDecision
			&& PersistedNonlossDecision->MatchWinnerSettlementDecisions.Num() == 1
			&& PersistedNonlossDecision->MatchWinnerSettlementDecisions[0].Outcome == MatchWinnerWonOutcome);
		MalformedDecisionRecord->MatchWinnerSettlementDecisions[0].Outcome = MatchWinnerLostOutcome;
		TestTrue(TEXT("Valid lost decision restores after nonloss QA"), UGameplayStatics::SaveGameToSlot(MalformedDecisionRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Restored loss finalization chain validates"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	}

	UOddsWellOddsBucksSaveGame* MalformedLockRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved lock record is available for corruption test"), MalformedLockRecord && MalformedLockRecord->MatchWinnerLocks.Num() == 1);
	if (MalformedLockRecord && MalformedLockRecord->MatchWinnerLocks.Num() == 1)
	{
		MalformedLockRecord->MatchWinnerLocks[0].GameNumber++;
		TestFalse(TEXT("Malformed persisted lock is rejected"), ValidateOddsBucksSave(MalformedLockRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
	}
	UOddsWellOddsBucksSaveGame* MalformedResultRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved result link is available for corruption test"), MalformedResultRecord && MalformedResultRecord->MatchWinnerResultLinks.Num() == 1);
	if (MalformedResultRecord && MalformedResultRecord->MatchWinnerResultLinks.Num() == 1)
	{
		const FString MalformedSeal(TEXT("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"));
		MalformedResultRecord->MatchWinnerResultLinks[0].ReplaySealSha256 = MalformedSeal;
		TestFalse(TEXT("Malformed persisted result link is rejected in memory"), ValidateOddsBucksSave(MalformedResultRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
		TestTrue(TEXT("Malformed persisted result link writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedResultRecord, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Malformed persisted result link rejects a link command"), LinkResult(ExactResultInput, RetryResultRecord), EOddsWellMatchWinnerResultLinkResult::Rejected);
		const UOddsWellOddsBucksSaveGame* PersistedMalformedResult = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected command does not rewrite malformed persisted evidence"), PersistedMalformedResult
			&& PersistedMalformedResult->MatchWinnerResultLinks.Num() == 1
			&& PersistedMalformedResult->MatchWinnerResultLinks[0].ReplaySealSha256 == MalformedSeal);
	}
	TestTrue(TEXT("Loss-profile QA cleanup succeeds before isolated win profile"), ResetOddsWellQaOddsBucksAndVerify(Error));

	TestTrue(TEXT("Existing job path funds isolated win QA"), SaveOddsWellOddsBucksLedger(JobLedger, ExpectedNextJobPayout, true, Error));
	const FString WinRequestCommandId(TEXT("wager:match_winner:win:request:test-1"));
	const FString WinLockCommandId(TEXT("wager:match_winner:win:lock:test-1"));
	const FString WinResultCommandId(TEXT("wager:match_winner:win:result:test-1"));
	const FString WinDecisionCommandId(TEXT("wager:match_winner:win:decision:test-1"));
	FOddsWellMatchWinnerRequestRecord WinRequest;
	int64 WinBalance = 0;
	TestEqual(TEXT("Exact Mesa request is accepted in isolated QA profile"), AcceptOddsWellMatchWinnerRequest(Offer, WinRequestCommandId, Offer.AwayTeam, 40, Offer.LockUnixSeconds - 100, true, WinRequest, WinBalance, Error), EOddsWellMatchWinnerRequestResult::Accepted);
	TestEqual(TEXT("Isolated win QA debits stake once"), WinBalance, int64{60});
	FOddsWellMatchWinnerLockRecord WinLock;
	TestEqual(TEXT("Exact Mesa request locks at game start"), LockOddsWellMatchWinnerRequest(WinRequestCommandId, WinLockCommandId, 1, 1, Offer.LockUnixSeconds, true, WinLock, Error), EOddsWellMatchWinnerLockResult::Locked);
	FOddsWellMatchWinnerResultLinkRecord WinResult;
	TestEqual(TEXT("Exact Mesa request links sealed 101-104 result"), LinkOddsWellMatchWinnerResult(
		WinResultCommandId,
		WinRequestCommandId,
		WinLockCommandId,
		MatchWinnerResultSchema,
		MatchWinnerResultVersion,
		1,
		1,
		SealedResultHomeTeam,
		SealedResultAwayTeam,
		SealedResultHomeScore,
		SealedResultAwayScore,
		SealedResultWinner,
		SealedResultReplaySha,
		true,
		WinResult,
		Error), EOddsWellMatchWinnerResultLinkResult::Linked);

	FOddsWellOddsBucksLedger WinLedger;
	int64 WinNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> WinRequests;
	TArray<FOddsWellMatchWinnerLockRecord> WinLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> WinResults;
	TestTrue(TEXT("Isolated win chain reloads before decision"), LoadOddsWellOddsBucksWagerEvidence(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, bFound, Error));
	UOddsWellOddsBucksSaveGame* VersionFiveWinRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionFiveWinRecord->SchemaVersion = 5;
	VersionFiveWinRecord->Entries = WinLedger.GetEntries();
	VersionFiveWinRecord->NextJobPayoutUnixSeconds = WinNextJobPayout;
	VersionFiveWinRecord->MatchWinnerRequests = WinRequests;
	VersionFiveWinRecord->MatchWinnerLocks = WinLocks;
	VersionFiveWinRecord->MatchWinnerResultLinks = WinResults;
	TestTrue(TEXT("Schema v5 isolated win chain writes before decision"), UGameplayStatics::SaveGameToSlot(VersionFiveWinRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> WinDecisions;
	TestTrue(TEXT("Schema v5 isolated win chain migrates without invention"), LoadOddsWellOddsBucksWagerDecisionState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, bFound, Error));
	TestEqual(TEXT("Win-profile migration invents no decision"), WinDecisions.Num(), 0);
	TestEqual(TEXT("Win-profile migration preserves two ledger entries"), WinLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Win-profile migration preserves balance 60"), WinLedger.GetBalance(), int64{60});

	FOddsWellMatchWinnerSettlementDecisionRecord WinDecision;
	TestEqual(TEXT("Winning decision without exact offer is rejected"), DecideOddsWellMatchWinnerSettlement(WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, WinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	FOddsWellMatchWinnerOffer TamperedWinProbabilityOffer = Offer;
	TamperedWinProbabilityOffer.Selections[1].WinProbabilityE8++;
	TestEqual(TEXT("Tampered winning probability is rejected"), DecideOddsWellMatchWinnerSettlement(TamperedWinProbabilityOffer, WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, WinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	FOddsWellMatchWinnerOffer TamperedWinFormulaOffer = Offer;
	TamperedWinFormulaOffer.PayoutFormula = TEXT("stake/probability");
	TestEqual(TEXT("Tampered payout formula is rejected"), DecideOddsWellMatchWinnerSettlement(TamperedWinFormulaOffer, WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, WinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("Mismatched winning lock is rejected"), DecideOddsWellMatchWinnerSettlement(Offer, WinDecisionCommandId, WinRequestCommandId, TEXT("wager:match_winner:win:lock:unknown"), WinResultCommandId, true, WinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("Exact Mesa chain creates one winning decision"), DecideOddsWellMatchWinnerSettlement(Offer, WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, WinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Decided);
	TestEqual(TEXT("Winning decision selects Mesa"), WinDecision.SelectedTeam, SealedResultAwayTeam);
	TestEqual(TEXT("Winning decision binds exact offer"), WinDecision.OfferId, ExactMatchWinnerOfferId);
	TestEqual(TEXT("Winning decision binds probability 40000000"), WinDecision.SelectedWinProbabilityE8, int64{40000000});
	TestEqual(TEXT("Winning decision binds approved payout formula"), WinDecision.PayoutFormula, MatchWinnerPayoutFormula);
	TestEqual(TEXT("Winning decision derives won"), WinDecision.Outcome, MatchWinnerWonOutcome);
	TestEqual(TEXT("Winning decision recomputes gross return due 100"), WinDecision.GrossReturnDue, int64{100});
	TestEqual(TEXT("Winning decision remains pending application"), WinDecision.Status, MatchWinnerDecidedPendingApplyStatus);

	TArray<FOddsWellMatchWinnerLossFinalizationRecord> WinLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TestTrue(TEXT("Winning decision cold-restores"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestEqual(TEXT("Cold win profile has one decision"), WinDecisions.Num(), 1);
	TestEqual(TEXT("Cold win profile preserves due 100"), WinDecisions[0].GrossReturnDue, int64{100});
	TestEqual(TEXT("Cold win profile has no loss finalization"), WinLossFinalizations.Num(), 0);
	TestEqual(TEXT("Cold win profile has no win finalization"), WinFinalizations.Num(), 0);
	TestEqual(TEXT("Winning decision adds no ledger entry"), WinLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Winning decision preserves balance 60"), WinLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Winning decision preserves job cooldown"), WinNextJobPayout, ExpectedNextJobPayout);
	UOddsWellOddsBucksSaveGame* VersionSevenWinRecord = NewObject<UOddsWellOddsBucksSaveGame>();
	VersionSevenWinRecord->SchemaVersion = 7;
	VersionSevenWinRecord->Entries = WinLedger.GetEntries();
	VersionSevenWinRecord->NextJobPayoutUnixSeconds = WinNextJobPayout;
	VersionSevenWinRecord->MatchWinnerRequests = WinRequests;
	VersionSevenWinRecord->MatchWinnerLocks = WinLocks;
	VersionSevenWinRecord->MatchWinnerResultLinks = WinResults;
	VersionSevenWinRecord->MatchWinnerSettlementDecisions = WinDecisions;
	VersionSevenWinRecord->MatchWinnerLossFinalizations = WinLossFinalizations;
	TestTrue(TEXT("Schema v7 pending win writes before application"), UGameplayStatics::SaveGameToSlot(VersionSevenWinRecord, OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v7 pending win migrates without invention"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestEqual(TEXT("Schema v7 migration invents no win finalization"), WinFinalizations.Num(), 0);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v7 migration rewrites schema v8"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	FOddsWellMatchWinnerSettlementDecisionRecord RetryWinDecision;
	TestEqual(TEXT("Exact winning decision retry is idempotent"), DecideOddsWellMatchWinnerSettlement(Offer, WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, RetryWinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Duplicate);
	TestEqual(TEXT("Winning decision command conflict is rejected"), DecideOddsWellMatchWinnerSettlement(Offer, WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, TEXT("wager:match_winner:win:result:unknown"), true, RetryWinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestEqual(TEXT("Second winning decision is rejected"), DecideOddsWellMatchWinnerSettlement(Offer, TEXT("wager:match_winner:win:decision:test-2"), WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, RetryWinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	FOddsWellMatchWinnerLossFinalizationRecord InvalidWinFinalization;
	TestEqual(TEXT("Winning decision cannot use loss finalization"), FinalizeOddsWellMatchWinnerLoss(TEXT("wager:match_winner:win:finalization:invalid"), WinDecisionCommandId, true, InvalidWinFinalization, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestTrue(TEXT("Winning retry rejection preserves cold state"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestEqual(TEXT("Winning retries preserve one decision"), WinDecisions.Num(), 1);
	TestEqual(TEXT("Winning retries preserve no loss finalization"), WinLossFinalizations.Num(), 0);
	TestEqual(TEXT("Winning retries preserve no win finalization"), WinFinalizations.Num(), 0);
	TestEqual(TEXT("Winning retries preserve balance"), WinLedger.GetBalance(), int64{60});

	UOddsWellOddsBucksSaveGame* MalformedWinDecision = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved winning decision is available for tamper QA"), MalformedWinDecision && MalformedWinDecision->MatchWinnerSettlementDecisions.Num() == 1);
	if (MalformedWinDecision && MalformedWinDecision->MatchWinnerSettlementDecisions.Num() == 1)
	{
		MalformedWinDecision->MatchWinnerSettlementDecisions[0].GrossReturnDue = 99;
		TestFalse(TEXT("Tampered winning return is rejected in memory"), ValidateOddsBucksSave(MalformedWinDecision, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
		TestTrue(TEXT("Tampered winning decision writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedWinDecision, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Tampered persisted winning decision fails closed"), DecideOddsWellMatchWinnerSettlement(Offer, WinDecisionCommandId, WinRequestCommandId, WinLockCommandId, WinResultCommandId, true, RetryWinDecision, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		const UOddsWellOddsBucksSaveGame* PersistedMalformedWin = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected command does not rewrite tampered winning due"), PersistedMalformedWin
			&& PersistedMalformedWin->MatchWinnerSettlementDecisions.Num() == 1
			&& PersistedMalformedWin->MatchWinnerSettlementDecisions[0].GrossReturnDue == 99);
		MalformedWinDecision->MatchWinnerSettlementDecisions[0].GrossReturnDue = 100;
		TestTrue(TEXT("Exact winning decision restores after tamper QA"), UGameplayStatics::SaveGameToSlot(MalformedWinDecision, OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Restored winning decision validates"), LoadOddsWellOddsBucksWagerDecisionState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, bFound, Error));
	}
	const FString WinFinalizationCommandId(TEXT("wager:match_winner:win:finalization:test-1"));
	FOddsWellMatchWinnerWinFinalizationRecord WinFinalization;
	TestEqual(TEXT("Unknown decision cannot finalize a win"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, TEXT("wager:match_winner:win:decision:unknown"), true, WinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TestEqual(TEXT("Malformed win finalization identity is rejected"), FinalizeOddsWellMatchWinnerWin(WinDecisionCommandId, WinDecisionCommandId, true, WinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TestTrue(TEXT("Rejected win applications preserve pending state"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestEqual(TEXT("Rejected win applications add no finalization"), WinFinalizations.Num(), 0);
	TestEqual(TEXT("Rejected win applications add no ledger entry"), WinLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Rejected win applications preserve balance 60"), WinLedger.GetBalance(), int64{60});
	UOddsWellOddsBucksSaveGame* WrongFormulaWin = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Pending win is available for wrong-formula QA"), WrongFormulaWin && WrongFormulaWin->MatchWinnerSettlementDecisions.Num() == 1);
	if (WrongFormulaWin && WrongFormulaWin->MatchWinnerSettlementDecisions.Num() == 1)
	{
		WrongFormulaWin->MatchWinnerSettlementDecisions[0].PayoutFormula = TEXT("stake/probability");
		TestTrue(TEXT("Wrong persisted payout formula writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(WrongFormulaWin, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Wrong persisted payout formula rejects win application"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, WinDecisionCommandId, true, WinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
		WrongFormulaWin->MatchWinnerSettlementDecisions[0].PayoutFormula = MatchWinnerPayoutFormula;
		TestTrue(TEXT("Exact payout formula restores after fail-closed QA"), UGameplayStatics::SaveGameToSlot(WrongFormulaWin, OddsBucksQaSlot, OddsBucksUserIndex));
	}
	UOddsWellOddsBucksSaveGame* WrongChainWin = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Pending win is available for wrong-chain QA"), WrongChainWin && WrongChainWin->MatchWinnerSettlementDecisions.Num() == 1);
	if (WrongChainWin && WrongChainWin->MatchWinnerSettlementDecisions.Num() == 1)
	{
		const FString ExactResultCommandId = WrongChainWin->MatchWinnerSettlementDecisions[0].ResultCommandId;
		WrongChainWin->MatchWinnerSettlementDecisions[0].ResultCommandId = TEXT("wager:match_winner:win:result:wrong");
		TestTrue(TEXT("Wrong persisted decision chain writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(WrongChainWin, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Wrong persisted decision chain rejects win application"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, WinDecisionCommandId, true, WinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
		WrongChainWin->MatchWinnerSettlementDecisions[0].ResultCommandId = ExactResultCommandId;
		TestTrue(TEXT("Exact decision chain restores after fail-closed QA"), UGameplayStatics::SaveGameToSlot(WrongChainWin, OddsBucksQaSlot, OddsBucksUserIndex));
	}

	TestEqual(TEXT("Exact pending win applies and finalizes once"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, WinDecisionCommandId, true, WinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Finalized);
	TestEqual(TEXT("Win finalization links exact decision"), WinFinalization.DecisionCommandId, WinDecisionCommandId);
	TestEqual(TEXT("Win finalization stores Mesa selection"), WinFinalization.SelectedTeam, SealedResultAwayTeam);
	TestEqual(TEXT("Win finalization stores Mesa winner"), WinFinalization.AuthoritativeWinner, SealedResultAwayTeam);
	TestEqual(TEXT("Win finalization stores stake 40"), WinFinalization.Stake, int64{40});
	TestEqual(TEXT("Win finalization stores won outcome"), WinFinalization.Outcome, MatchWinnerWonOutcome);
	TestEqual(TEXT("Win finalization applies gross return 100"), WinFinalization.GrossReturnApplied, int64{100});
	TestEqual(TEXT("Win finalization binds payout command"), WinFinalization.PayoutLedgerCommandId, WinFinalizationCommandId);
	TestEqual(TEXT("Win finalization stores settled won"), WinFinalization.Status, MatchWinnerSettledWonStatus);
	TestEqual(TEXT("Win finalization observes balance 160"), WinFinalization.ObservedFinalBalance, int64{160});
	TestEqual(TEXT("Win finalization observes three entries"), WinFinalization.ObservedLedgerEntryCount, 3);
	TestTrue(TEXT("Exact win finalization publishes reconciliation atomically"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString MatchWinnerWinProjectionJson;
	FString NormalizedMatchWinnerWinProjectionJson;
	TSharedPtr<FJsonObject> MatchWinnerWinProjection;
	TestTrue(TEXT("Exact win reconciliation reads"), FFileHelper::LoadFileToString(MatchWinnerWinProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> MatchWinnerWinProjectionReader = TJsonReaderFactory<>::Create(MatchWinnerWinProjectionJson);
	TestTrue(TEXT("Exact win reconciliation parses"), FJsonSerializer::Deserialize(MatchWinnerWinProjectionReader, MatchWinnerWinProjection) && MatchWinnerWinProjection.IsValid());
	if (MatchWinnerWinProjection.IsValid())
	{
		TestEqual(TEXT("Win reconciliation reuses v1 schema"), MatchWinnerWinProjection->GetStringField(TEXT("schema")), MatchWinnerReconciliationSchema);
		TestEqual(TEXT("Win reconciliation selected Mesa"), MatchWinnerWinProjection->GetStringField(TEXT("selected_team")), SealedResultAwayTeam);
		TestEqual(TEXT("Win reconciliation binds probability 40m"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("selected_win_probability_e8"))), int64{40000000});
		TestEqual(TEXT("Win reconciliation binds approved formula"), MatchWinnerWinProjection->GetStringField(TEXT("payout_formula")), MatchWinnerPayoutFormula);
		TestEqual(TEXT("Win reconciliation binds sealed home score"), static_cast<int32>(MatchWinnerWinProjection->GetNumberField(TEXT("home_score"))), 101);
		TestEqual(TEXT("Win reconciliation binds sealed away score"), static_cast<int32>(MatchWinnerWinProjection->GetNumberField(TEXT("away_score"))), 104);
		TestEqual(TEXT("Win reconciliation binds winner Mesa"), MatchWinnerWinProjection->GetStringField(TEXT("winner")), SealedResultAwayTeam);
		TestEqual(TEXT("Win reconciliation binds won outcome"), MatchWinnerWinProjection->GetStringField(TEXT("outcome")), MatchWinnerWonOutcome.ToString());
		TestEqual(TEXT("Win reconciliation binds return due 100"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("gross_return_due"))), int64{100});
		TestEqual(TEXT("Win reconciliation binds stake sequence two"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("stake_sequence"))), int64{2});
		TestEqual(TEXT("Win reconciliation binds stake command"), MatchWinnerWinProjection->GetStringField(TEXT("stake_ledger_command_id")), WinRequestCommandId);
		TestEqual(TEXT("Win reconciliation binds minus forty stake"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("stake_delta"))), int64{-40});
		TestEqual(TEXT("Win reconciliation binds stake reason"), MatchWinnerWinProjection->GetStringField(TEXT("stake_reason")), MatchWinnerStakeReason.ToString());
		TestEqual(TEXT("Win reconciliation binds stake balance 60"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("stake_balance_after"))), int64{60});
		TestEqual(TEXT("Win reconciliation binds payout sequence three"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("payout_sequence"))), int64{3});
		TestEqual(TEXT("Win reconciliation binds payout command"), MatchWinnerWinProjection->GetStringField(TEXT("payout_ledger_command_id")), WinFinalizationCommandId);
		TestEqual(TEXT("Win reconciliation binds plus 100 payout"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("payout_delta"))), int64{100});
		TestEqual(TEXT("Win reconciliation binds payout reason"), MatchWinnerWinProjection->GetStringField(TEXT("payout_reason")), MatchWinnerPayoutReason.ToString());
		TestEqual(TEXT("Win reconciliation binds payout balance 160"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("payout_balance_after"))), int64{160});
		TestEqual(TEXT("Win reconciliation binds settled won"), MatchWinnerWinProjection->GetStringField(TEXT("finalization_status")), MatchWinnerSettledWonStatus.ToString());
		TestEqual(TEXT("Win reconciliation binds return applied 100"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("gross_return_applied"))), int64{100});
		TestEqual(TEXT("Win reconciliation reports three entries"), static_cast<int32>(MatchWinnerWinProjection->GetNumberField(TEXT("ledger_entry_count"))), 3);
		TestEqual(TEXT("Win reconciliation reports balance 160"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("final_balance"))), int64{160});
		TestEqual(TEXT("Win reconciliation reports net plus 60"), static_cast<int64>(MatchWinnerWinProjection->GetNumberField(TEXT("net"))), int64{60});
		MatchWinnerWinProjection->RemoveField(TEXT("generated_at_utc"));
		const TSharedRef<TJsonWriter<>> NormalizedWinProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedMatchWinnerWinProjectionJson);
		TestTrue(TEXT("Exact win reconciliation normalizes"), FJsonSerializer::Serialize(MatchWinnerWinProjection.ToSharedRef(), NormalizedWinProjectionWriter));
	}
	TestTrue(TEXT("QA can remove finalized-win projection for cold-load proof"), IFileManager::Get().Delete(*MatchWinnerProjectionPath, false, true, true));
	TestFalse(TEXT("Finalized-win projection is absent before cold load"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	TestTrue(TEXT("Exact win application cold-restores"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestTrue(TEXT("Validated cold load regenerates finalized-win reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString RegeneratedWinProjectionJson;
	TSharedPtr<FJsonObject> RegeneratedWinProjection;
	TestTrue(TEXT("Regenerated exact win reconciliation reads"), FFileHelper::LoadFileToString(RegeneratedWinProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> RegeneratedWinProjectionReader = TJsonReaderFactory<>::Create(RegeneratedWinProjectionJson);
	TestTrue(TEXT("Regenerated exact win reconciliation parses"), FJsonSerializer::Deserialize(RegeneratedWinProjectionReader, RegeneratedWinProjection) && RegeneratedWinProjection.IsValid());
	if (RegeneratedWinProjection.IsValid())
	{
		RegeneratedWinProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedRegeneratedWinProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedRegeneratedWinProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedRegeneratedWinProjectionJson);
		TestTrue(TEXT("Regenerated exact win reconciliation normalizes"), FJsonSerializer::Serialize(RegeneratedWinProjection.ToSharedRef(), NormalizedRegeneratedWinProjectionWriter));
		TestEqual(TEXT("Cold load regenerates identical win reconciliation data"), NormalizedRegeneratedWinProjectionJson, NormalizedMatchWinnerWinProjectionJson);
	}
	TestEqual(TEXT("Cold win application has one finalization"), WinFinalizations.Num(), 1);
	TestEqual(TEXT("Cold win application has no loss finalization"), WinLossFinalizations.Num(), 0);
	TestEqual(TEXT("Cold win application has three ledger entries"), WinLedger.GetEntries().Num(), 3);
	TestEqual(TEXT("Cold win application balance is 160"), WinLedger.GetBalance(), int64{160});
	TestEqual(TEXT("Cold win application preserves job cooldown"), WinNextJobPayout, ExpectedNextJobPayout);
	TestEqual(TEXT("Cold win decision remains pending apply"), WinDecisions[0].Status, MatchWinnerDecidedPendingApplyStatus);
	const FOddsWellOddsBucksEntry& WinPayoutEntry = WinLedger.GetEntries()[2];
	TestEqual(TEXT("Win payout is sequence three"), WinPayoutEntry.Sequence, int64{3});
	TestEqual(TEXT("Win payout command is finalization command"), WinPayoutEntry.CommandId, WinFinalizationCommandId);
	TestEqual(TEXT("Win payout appends exactly plus 100"), WinPayoutEntry.Delta, int64{100});
	TestEqual(TEXT("Win payout reaches balance 160"), WinPayoutEntry.BalanceAfter, int64{160});
	TestEqual(TEXT("Win payout uses match winner payout reason"), WinPayoutEntry.Reason, MatchWinnerPayoutReason);

	FOddsWellMatchWinnerWinFinalizationRecord RetryWinFinalization;
	TestEqual(TEXT("Exact win finalization retry is idempotent"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, WinDecisionCommandId, true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Duplicate);
	TestEqual(TEXT("Conflicting win finalization command reuse is rejected"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, TEXT("wager:match_winner:win:decision:unknown"), true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TestEqual(TEXT("Second win finalization is rejected"), FinalizeOddsWellMatchWinnerWin(TEXT("wager:match_winner:win:finalization:test-2"), WinDecisionCommandId, true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TestTrue(TEXT("Win finalization retries preserve exact cold state"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestEqual(TEXT("Win finalization retries preserve one record"), WinFinalizations.Num(), 1);
	TestEqual(TEXT("Win finalization retries preserve three entries"), WinLedger.GetEntries().Num(), 3);
	TestEqual(TEXT("Win finalization retries preserve balance 160"), WinLedger.GetBalance(), int64{160});

	TArray<uint8> ExactWinFinalizedBytes;
	TestTrue(TEXT("Exact finalized win profile is preserved before malformed QA"), UGameplayStatics::SaveGameToMemory(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex), ExactWinFinalizedBytes));
	UOddsWellOddsBucksSaveGame* MalformedWinFinalization = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved win finalization is available for tamper QA"), MalformedWinFinalization && MalformedWinFinalization->MatchWinnerWinFinalizations.Num() == 1);
	if (MalformedWinFinalization && MalformedWinFinalization->MatchWinnerWinFinalizations.Num() == 1)
	{
		MalformedWinFinalization->MatchWinnerWinFinalizations[0].GrossReturnApplied = 99;
		TestFalse(TEXT("Malformed win finalization is rejected in memory"), ValidateOddsBucksSave(MalformedWinFinalization, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, bNeedsMigration, Error));
		TestTrue(TEXT("Malformed win finalization writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedWinFinalization, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Malformed persisted win finalization fails closed"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, WinDecisionCommandId, true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
		TestFalse(TEXT("Malformed persisted win finalization publishes no reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		const UOddsWellOddsBucksSaveGame* PersistedMalformedWinFinalization = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected retry does not rewrite malformed win finalization"), PersistedMalformedWinFinalization
			&& PersistedMalformedWinFinalization->MatchWinnerWinFinalizations.Num() == 1
			&& PersistedMalformedWinFinalization->MatchWinnerWinFinalizations[0].GrossReturnApplied == 99);
		TestTrue(TEXT("Exact finalized win restores after tamper QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactWinFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	UOddsWellOddsBucksSaveGame* ExtraMutationWin = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Exact finalized win is available for extra-mutation QA"), ExtraMutationWin && ExtraMutationWin->Entries.Num() == 3);
	if (ExtraMutationWin && ExtraMutationWin->Entries.Num() == 3)
	{
		FOddsWellOddsBucksEntry ExtraEntry;
		ExtraEntry.Sequence = 4;
		ExtraEntry.CommandId = TEXT("qa:unexpected-extra-mutation");
		ExtraEntry.Delta = 1;
		ExtraEntry.BalanceAfter = 161;
		ExtraEntry.Reason = FName(TEXT("qa_unexpected_credit"));
		ExtraMutationWin->Entries.Add(ExtraEntry);
		TestTrue(TEXT("Unexpected extra mutation writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(ExtraMutationWin, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Unexpected extra mutation rejects win retry"), FinalizeOddsWellMatchWinnerWin(WinFinalizationCommandId, WinDecisionCommandId, true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
		TestFalse(TEXT("Unexpected extra mutation publishes no reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		const UOddsWellOddsBucksSaveGame* PersistedExtraMutation = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected retry does not rewrite extra mutation"), PersistedExtraMutation && PersistedExtraMutation->Entries.Num() == 4);
		TestTrue(TEXT("Exact finalized win restores after extra-mutation QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactWinFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TestTrue(TEXT("Restored exact win finalization validates"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	TestEqual(TEXT("Restored exact win balance remains 160"), WinLedger.GetBalance(), int64{160});
	TestTrue(TEXT("Restored exact win republishes reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	TestTrue(TEXT("Isolated win QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));

	USaveGame* PreservedLossProfile = UGameplayStatics::LoadGameFromMemory(ExactLossProfileBytes);
	TestTrue(TEXT("Preserved exact loss profile restores after win QA"), PreservedLossProfile && UGameplayStatics::SaveGameToSlot(PreservedLossProfile, OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Restored loss chain validates after winning decision proof"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	FString RestoredLossProjectionJson;
	TSharedPtr<FJsonObject> RestoredLossProjection;
	TestTrue(TEXT("Restored exact loss reconciliation still reads"), FFileHelper::LoadFileToString(RestoredLossProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> RestoredLossProjectionReader = TJsonReaderFactory<>::Create(RestoredLossProjectionJson);
	TestTrue(TEXT("Restored exact loss reconciliation still parses"), FJsonSerializer::Deserialize(RestoredLossProjectionReader, RestoredLossProjection) && RestoredLossProjection.IsValid());
	if (RestoredLossProjection.IsValid())
	{
		RestoredLossProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedRestoredLossProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedRestoredLossProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedRestoredLossProjectionJson);
		TestTrue(TEXT("Restored exact loss reconciliation normalizes"), FJsonSerializer::Serialize(RestoredLossProjection.ToSharedRef(), NormalizedRestoredLossProjectionWriter));
		TestEqual(TEXT("Exact-loss projection remains unchanged after win proof"), NormalizedRestoredLossProjectionJson, NormalizedMatchWinnerProjectionJson);
	}
	TestEqual(TEXT("Restored loss profile preserves one lost decision"), WagerDecisions.Num(), 1);
	TestEqual(TEXT("Restored loss decision remains lost"), WagerDecisions[0].Outcome, MatchWinnerLostOutcome);
	TestEqual(TEXT("Restored loss decision binds no win probability"), WagerDecisions[0].SelectedWinProbabilityE8, int64{0});
	TestTrue(TEXT("Restored loss decision binds no payout formula"), WagerDecisions[0].PayoutFormula.IsEmpty());
	TestEqual(TEXT("Restored loss profile preserves one finalization"), WagerFinalizations.Num(), 1);
	TestEqual(TEXT("Restored loss finalization remains settled lost"), WagerFinalizations[0].Status, MatchWinnerSettledLostStatus);
	TestEqual(TEXT("Restored loss profile invents no win finalization"), WagerWinFinalizations.Num(), 0);
	TestEqual(TEXT("Lost decision rejects win finalization"), FinalizeOddsWellMatchWinnerWin(TEXT("wager:match_winner:loss:win-finalization:invalid"), DecisionCommandId, true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TestTrue(TEXT("Rejected loss-to-win application preserves loss chain"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Rejected loss-to-win application preserves balance 60"), WagerLedger.GetBalance(), int64{60});
	TestTrue(TEXT("Final wager QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

#endif
