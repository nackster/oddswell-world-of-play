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
constexpr int32 OddsBucksSchemaVersion = 12;
constexpr int32 MatchWinnerRequestEvidenceVersion = 1;
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
const FString UpcomingQaOfferId(TEXT("4a30feca21ab8dfb8a3f64ca642aadcdb33743b07a7cedf49b6b743f1c6f2f31"));
const FString UpcomingQaRequestCommandId(TEXT("qa:h17:match_winner:request:1"));
const FString UpcomingQaLockCommandId(TEXT("qa:h19:match_winner:lock:1"));
const FString UpcomingQaCancellationCommandId(TEXT("qa:h20:match_winner:cancellation:1"));
const FString UpcomingQaCancellationEvidenceId(TEXT("qa:h20:match_winner:cancellation:evidence:1"));
const FString UpcomingQaVoidDecisionCommandId(TEXT("qa:h21:match_winner:void-decision:1"));
const FString UpcomingQaVoidFinalizationCommandId(TEXT("qa:h22:match_winner:void-finalization:1"));
constexpr int32 UpcomingQaSeasonNumber = 100;
constexpr int32 UpcomingQaGameNumber = 1;
constexpr int64 UpcomingQaAcceptedUnixSeconds = 2100000000;
constexpr int64 UpcomingQaLockUnixSeconds = UpcomingQaAcceptedUnixSeconds + 24 * 60 * 60;
constexpr int64 UpcomingQaCancellationUnixSeconds = UpcomingQaLockUnixSeconds + 5 * 60;
const FString MatchWinnerResultSchema(TEXT("oddswell-sealed-match-winner-result-v1"));
const FString MatchWinnerResultVersion(TEXT("sealed-match-winner-result-v1"));
const FString PrivateCanonicalResultSchema(TEXT("oddswell-private-canonical-game-result-v1"));
const FString PrivateCanonicalResultRecorderVersion(TEXT("oddswell-private-game-result-recorder-v1"));
const FString PrivateCanonicalResultCommandPrefix(TEXT("canonical:h26l:match_winner:result:"));
const FString PrivateCanonicalLossDecisionCommandPrefix(TEXT("canonical:h26m:match_winner:decision:"));
const FString PrivateCanonicalLossFinalizationCommandPrefix(TEXT("canonical:h26n:match_winner:finalization:"));
const FString MatchWinnerCanceledGameSchema(TEXT("oddswell-match-winner-canceled-game-v1"));
const FString MatchWinnerCanceledGameVersion(TEXT("match-winner-canceled-game-v1"));
const FName MatchWinnerCanceledGameReason(TEXT("game_canceled"));
const FName MatchWinnerClosedCanceledStatus(TEXT("closed_canceled"));
const FString MatchWinnerVoidDecisionSchema(TEXT("oddswell-match-winner-void-decision-v1"));
const FString MatchWinnerVoidDecisionVersion(TEXT("match-winner-void-decision-v1"));
const FName MatchWinnerVoidedOutcome(TEXT("voided"));
const FName MatchWinnerDecidedVoidPendingRefundStatus(TEXT("decided_void_pending_refund"));
const FString MatchWinnerVoidFinalizationSchema(TEXT("oddswell-match-winner-void-finalization-v1"));
const FString MatchWinnerVoidFinalizationVersion(TEXT("match-winner-void-finalization-v1"));
const FName MatchWinnerRefundReason(TEXT("match_winner_refund"));
const FName MatchWinnerSettledVoidStatus(TEXT("settled_void"));
constexpr int32 CanceledQaSeasonNumber = 99;
constexpr int32 CanceledQaGameNumber = 1;
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

bool GetMatchWinnerOfferId(
	const FOddsWellMatchWinnerOffer& Offer,
	FString& OutOfferId,
	FString& OutError,
	FString* OutCanonicalJson = nullptr)
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
	if (OutCanonicalJson)
	{
		*OutCanonicalJson = CanonicalJson;
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

bool BuildUpcomingQaMatchWinnerOffer(FOddsWellMatchWinnerOffer& OutOffer, FString& OutError)
{
	OutOffer = FOddsWellMatchWinnerOffer();
	OutOffer.Schema = MatchWinnerOfferSchema;
	OutOffer.OfferVersion = MatchWinnerOfferVersion;
	OutOffer.Market = MatchWinnerMarket;
	OutOffer.Currency = OddsBucksCurrency;
	OutOffer.SourcePredictionVersion = MatchWinnerPredictionVersion;
	OutOffer.SourceSnapshotVersion = MatchWinnerSnapshotVersion;
	OutOffer.SourceModel = MatchWinnerSourceModel;
	OutOffer.SourceCommitmentSha256 = TEXT("cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc");
	OutOffer.SeasonNumber = UpcomingQaSeasonNumber;
	OutOffer.GameNumber = UpcomingQaGameNumber;
	OutOffer.HomeTeam = TEXT("Sundale Sparks");
	OutOffer.AwayTeam = TEXT("Red Mesa Rivals");
	OutOffer.LockUnixSeconds = UpcomingQaLockUnixSeconds;
	OutOffer.MinimumStake = MatchWinnerMinimumStake;
	OutOffer.MaximumStake = MatchWinnerMaximumStake;
	OutOffer.StakeIncrement = MatchWinnerStakeIncrement;
	OutOffer.HouseEdgeBps = 0;
	OutOffer.PayoutFormula = MatchWinnerPayoutFormula;
	FOddsWellMatchWinnerSelection& Home = OutOffer.Selections.AddDefaulted_GetRef();
	Home.Team = OutOffer.HomeTeam;
	Home.WinProbabilityE8 = 55000000;
	Home.DecimalOddsE4 = 18181;
	FOddsWellMatchWinnerSelection& Away = OutOffer.Selections.AddDefaulted_GetRef();
	Away.Team = OutOffer.AwayTeam;
	Away.WinProbabilityE8 = 45000000;
	Away.DecimalOddsE4 = 22222;
	return GetMatchWinnerOfferId(OutOffer, OutOffer.OfferId, OutError)
		&& ValidateMatchWinnerOffer(OutOffer, OutError);
}

FOddsWellMatchWinnerOffer BuildCompletedH16MatchWinnerOffer()
{
	FOddsWellMatchWinnerOffer Offer;
	Offer.OfferId = TEXT("29d3ab7c4fd2858b4cfa80f1f413a77aaa30fbdde1ca593b477d82f2e726617e");
	Offer.Schema = MatchWinnerOfferSchema;
	Offer.OfferVersion = MatchWinnerOfferVersion;
	Offer.Market = MatchWinnerMarket;
	Offer.Currency = OddsBucksCurrency;
	Offer.SourcePredictionVersion = MatchWinnerPredictionVersion;
	Offer.SourceSnapshotVersion = MatchWinnerSnapshotVersion;
	Offer.SourceModel = MatchWinnerSourceModel;
	Offer.SourceCommitmentSha256 = TEXT("898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f");
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
	Home.WinProbabilityE8 = 57586693;
	Home.DecimalOddsE4 = 17365;
	FOddsWellMatchWinnerSelection& Away = Offer.Selections.AddDefaulted_GetRef();
	Away.Team = Offer.AwayTeam;
	Away.WinProbabilityE8 = 42413307;
	Away.DecimalOddsE4 = 23577;
	return Offer;
}

bool ValidateMatchWinnerRequests(const FOddsWellOddsBucksLedger& Ledger, const TArray<FOddsWellMatchWinnerRequestRecord>& Requests, FString& OutError)
{
	TSet<FString> RequestIds;
	for (int32 Index = 0; Index < Requests.Num(); ++Index)
	{
		const FOddsWellMatchWinnerRequestRecord& Request = Requests[Index];
		const bool bLegacyEvidence =
			Request.EvidenceVersion == 0
			&& Request.OfferSchema.IsEmpty()
			&& Request.Market.IsEmpty()
			&& Request.Currency.IsEmpty()
			&& Request.SourcePredictionVersion.IsEmpty()
			&& Request.SourceSnapshotVersion.IsEmpty()
			&& Request.SourceModel.IsEmpty()
			&& Request.SourceCommitmentSha256.IsEmpty()
			&& Request.SelectedWinProbabilityE8 == 0
			&& Request.SelectedDecimalOddsE4 == 0
			&& Request.PayoutFormula.IsEmpty()
			&& Request.GrossReturn == 0;
		const bool bCurrentEvidence =
			Request.EvidenceVersion == MatchWinnerRequestEvidenceVersion
			&& Request.OfferSchema == MatchWinnerOfferSchema
			&& Request.Market == MatchWinnerMarket
			&& Request.Currency == OddsBucksCurrency
			&& Request.SourcePredictionVersion == MatchWinnerPredictionVersion
			&& Request.SourceSnapshotVersion == MatchWinnerSnapshotVersion
			&& Request.SourceModel == MatchWinnerSourceModel
			&& IsLowerHexHash(Request.SourceCommitmentSha256)
			&& Request.SelectedWinProbabilityE8 > 0
			&& Request.SelectedWinProbabilityE8 < MatchWinnerProbabilityScale
			&& Request.SelectedDecimalOddsE4
				== MatchWinnerProbabilityScale * 10000 / Request.SelectedWinProbabilityE8
			&& Request.PayoutFormula == MatchWinnerPayoutFormula
			&& Request.GrossReturn
				== Request.Stake * MatchWinnerProbabilityScale / Request.SelectedWinProbabilityE8;
		if ((!bLegacyEvidence && !bCurrentEvidence)
			|| Request.RequestCommandId.TrimStartAndEnd().IsEmpty()
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

bool IsExactPrivateCanonicalMatchWinnerResult(
	const FOddsWellMatchWinnerResultLinkRecord& Result)
{
	const FString RecordSha256 =
		Result.ResultCommandId.RightChop(
			PrivateCanonicalResultCommandPrefix.Len());
	const FString DerivedWinner =
		Result.HomeScore > Result.AwayScore
			? Result.HomeTeam
			: Result.AwayTeam;
	return Result.ResultCommandId.StartsWith(
			PrivateCanonicalResultCommandPrefix)
		&& IsLowerHexHash(RecordSha256)
		&& Result.ResultSchema == PrivateCanonicalResultSchema
		&& Result.ResultVersion
			== PrivateCanonicalResultRecorderVersion
		&& Result.SeasonNumber == 1
		&& Result.GameNumber == 1
		&& Result.HomeTeam == SealedResultHomeTeam
		&& Result.AwayTeam == SealedResultAwayTeam
		&& Result.HomeScore >= 0
		&& Result.AwayScore >= 0
		&& Result.HomeScore != Result.AwayScore
		&& Result.Winner == DerivedWinner
		&& IsLowerHexHash(Result.ReplaySealSha256);
}

bool IsSameMatchWinnerResultLink(
	const FOddsWellMatchWinnerResultLinkRecord& Left,
	const FOddsWellMatchWinnerResultLinkRecord& Right)
{
	return Left.ResultCommandId == Right.ResultCommandId
		&& Left.RequestCommandId == Right.RequestCommandId
		&& Left.LockCommandId == Right.LockCommandId
		&& Left.ResultSchema == Right.ResultSchema
		&& Left.ResultVersion == Right.ResultVersion
		&& Left.SeasonNumber == Right.SeasonNumber
		&& Left.GameNumber == Right.GameNumber
		&& Left.HomeTeam == Right.HomeTeam
		&& Left.AwayTeam == Right.AwayTeam
		&& Left.HomeScore == Right.HomeScore
		&& Left.AwayScore == Right.AwayScore
		&& Left.Winner == Right.Winner
		&& Left.ReplaySealSha256 == Right.ReplaySealSha256;
}

bool IsSameMatchWinnerSettlementDecision(
	const FOddsWellMatchWinnerSettlementDecisionRecord& Left,
	const FOddsWellMatchWinnerSettlementDecisionRecord& Right)
{
	return Left.DecisionCommandId == Right.DecisionCommandId
		&& Left.RequestCommandId == Right.RequestCommandId
		&& Left.LockCommandId == Right.LockCommandId
		&& Left.ResultCommandId == Right.ResultCommandId
		&& Left.DecisionSchema == Right.DecisionSchema
		&& Left.DecisionVersion == Right.DecisionVersion
		&& Left.OfferId == Right.OfferId
		&& Left.OfferVersion == Right.OfferVersion
		&& Left.SelectedTeam == Right.SelectedTeam
		&& Left.AuthoritativeWinner == Right.AuthoritativeWinner
		&& Left.Stake == Right.Stake
		&& Left.Outcome == Right.Outcome
		&& Left.GrossReturnDue == Right.GrossReturnDue
		&& Left.SelectedWinProbabilityE8 == Right.SelectedWinProbabilityE8
		&& Left.PayoutFormula == Right.PayoutFormula
		&& Left.Status == Right.Status;
}

bool IsSameMatchWinnerLossFinalization(
	const FOddsWellMatchWinnerLossFinalizationRecord& Left,
	const FOddsWellMatchWinnerLossFinalizationRecord& Right)
{
	return Left.FinalizationCommandId == Right.FinalizationCommandId
		&& Left.DecisionCommandId == Right.DecisionCommandId
		&& Left.RequestCommandId == Right.RequestCommandId
		&& Left.LockCommandId == Right.LockCommandId
		&& Left.ResultCommandId == Right.ResultCommandId
		&& Left.FinalizationSchema == Right.FinalizationSchema
		&& Left.FinalizationVersion == Right.FinalizationVersion
		&& Left.OfferId == Right.OfferId
		&& Left.OfferVersion == Right.OfferVersion
		&& Left.SelectedTeam == Right.SelectedTeam
		&& Left.AuthoritativeWinner == Right.AuthoritativeWinner
		&& Left.Stake == Right.Stake
		&& Left.Outcome == Right.Outcome
		&& Left.GrossReturnApplied == Right.GrossReturnApplied
		&& Left.Status == Right.Status
		&& Left.ObservedFinalBalance == Right.ObservedFinalBalance
		&& Left.ObservedLedgerEntryCount == Right.ObservedLedgerEntryCount;
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
			|| (!IsExactSealedMatchWinnerResult(Result)
				&& !IsExactPrivateCanonicalMatchWinnerResult(Result)))
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

bool ValidateMatchWinnerCanceledGames(
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& CanceledGames,
	FString& OutError)
{
	if (CanceledGames.Num() > 1)
	{
		OutError = TEXT("Only one Match Winner canceled-game QA record is supported.");
		return false;
	}
	TSet<FString> CancellationIds;
	TSet<FString> EvidenceIds;
	TSet<FString> CanceledRequestIds;
	for (int32 Index = 0; Index < CanceledGames.Num(); ++Index)
	{
		const FOddsWellMatchWinnerCanceledGameRecord& Canceled = CanceledGames[Index];
		const FOddsWellMatchWinnerRequestRecord* Request = Requests.FindByPredicate(
			[&Canceled](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Canceled.RequestCommandId;
			});
		const FOddsWellMatchWinnerLockRecord* Lock = Locks.FindByPredicate(
			[&Canceled](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Canceled.LockCommandId;
			});
		const bool bHasResult = Results.ContainsByPredicate(
			[&Canceled](const FOddsWellMatchWinnerResultLinkRecord& Result)
			{
				return Result.RequestCommandId == Canceled.RequestCommandId;
			});
		const bool bHasDecision = Decisions.ContainsByPredicate(
			[&Canceled](const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
			{
				return Decision.RequestCommandId == Canceled.RequestCommandId;
			});
		const bool bHasFinalization = LossFinalizations.ContainsByPredicate(
			[&Canceled](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
			{
				return Finalization.RequestCommandId == Canceled.RequestCommandId;
			})
			|| WinFinalizations.ContainsByPredicate(
				[&Canceled](const FOddsWellMatchWinnerWinFinalizationRecord& Finalization)
				{
					return Finalization.RequestCommandId == Canceled.RequestCommandId;
				});
		if (Canceled.CancellationCommandId.TrimStartAndEnd().IsEmpty()
			|| Canceled.CancellationEvidenceId.TrimStartAndEnd().IsEmpty()
			|| Canceled.RequestCommandId.TrimStartAndEnd().IsEmpty()
			|| Canceled.LockCommandId.TrimStartAndEnd().IsEmpty()
			|| Canceled.CancellationCommandId == Canceled.CancellationEvidenceId
			|| Canceled.CancellationCommandId == Canceled.RequestCommandId
			|| Canceled.CancellationCommandId == Canceled.LockCommandId
			|| CancellationIds.Contains(Canceled.CancellationCommandId)
			|| EvidenceIds.Contains(Canceled.CancellationEvidenceId)
			|| CanceledRequestIds.Contains(Canceled.RequestCommandId)
			|| !Request
			|| !Lock
			|| Lock->RequestCommandId != Canceled.RequestCommandId
			|| Canceled.DispositionSchema != MatchWinnerCanceledGameSchema
			|| Canceled.DispositionVersion != MatchWinnerCanceledGameVersion
			|| Canceled.SeasonNumber != Request->SeasonNumber
			|| Canceled.GameNumber != Request->GameNumber
			|| Canceled.SeasonNumber != Lock->SeasonNumber
			|| Canceled.GameNumber != Lock->GameNumber
			|| (Canceled.SeasonNumber == SealedResultSeasonNumber && Canceled.GameNumber == SealedResultGameNumber)
			|| Canceled.AuthoritativeCancellationUnixSeconds < Lock->AuthoritativeGameStartUnixSeconds
			|| Canceled.ReasonCode != MatchWinnerCanceledGameReason
			|| Canceled.Status != MatchWinnerClosedCanceledStatus
			|| bHasResult
			|| bHasDecision
			|| bHasFinalization)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner canceled-game record at index %d."), Index);
			return false;
		}
		CancellationIds.Add(Canceled.CancellationCommandId);
		EvidenceIds.Add(Canceled.CancellationEvidenceId);
		CanceledRequestIds.Add(Canceled.RequestCommandId);
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerVoidDecisions(
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& CanceledGames,
	const TArray<FOddsWellMatchWinnerVoidDecisionRecord>& VoidDecisions,
	FString& OutError)
{
	if (VoidDecisions.Num() > 1)
	{
		OutError = TEXT("Only one Match Winner void-decision QA record is supported.");
		return false;
	}
	for (int32 Index = 0; Index < VoidDecisions.Num(); ++Index)
	{
		const FOddsWellMatchWinnerVoidDecisionRecord& Decision = VoidDecisions[Index];
		const FOddsWellMatchWinnerCanceledGameRecord* Canceled = CanceledGames.FindByPredicate(
			[&Decision](const FOddsWellMatchWinnerCanceledGameRecord& Candidate)
			{
				return Candidate.CancellationCommandId == Decision.CancellationCommandId
					&& Candidate.CancellationEvidenceId == Decision.CancellationEvidenceId;
			});
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
		const bool bHasResult = Results.ContainsByPredicate(
			[&Decision](const FOddsWellMatchWinnerResultLinkRecord& Result)
			{
				return Result.RequestCommandId == Decision.RequestCommandId;
			});
		const bool bHasNormalDecision = Decisions.ContainsByPredicate(
			[&Decision](const FOddsWellMatchWinnerSettlementDecisionRecord& Candidate)
			{
				return Candidate.RequestCommandId == Decision.RequestCommandId;
			});
		const bool bHasFinalization = LossFinalizations.ContainsByPredicate(
			[&Decision](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
			{
				return Finalization.RequestCommandId == Decision.RequestCommandId;
			})
			|| WinFinalizations.ContainsByPredicate(
				[&Decision](const FOddsWellMatchWinnerWinFinalizationRecord& Finalization)
				{
					return Finalization.RequestCommandId == Decision.RequestCommandId;
				});
		const bool bSupportedCanceledQaGame = Canceled
			&& ((Canceled->SeasonNumber == CanceledQaSeasonNumber && Canceled->GameNumber == CanceledQaGameNumber)
				|| (Canceled->SeasonNumber == UpcomingQaSeasonNumber && Canceled->GameNumber == UpcomingQaGameNumber));
		if (Decision.VoidDecisionCommandId.TrimStartAndEnd().IsEmpty()
			|| Decision.CancellationCommandId.TrimStartAndEnd().IsEmpty()
			|| Decision.CancellationEvidenceId.TrimStartAndEnd().IsEmpty()
			|| Decision.VoidDecisionCommandId == Decision.CancellationCommandId
			|| Decision.VoidDecisionCommandId == Decision.CancellationEvidenceId
			|| Decision.VoidDecisionCommandId == Decision.RequestCommandId
			|| Decision.VoidDecisionCommandId == Decision.LockCommandId
			|| !Canceled
			|| !Request
			|| !Lock
			|| Canceled->RequestCommandId != Decision.RequestCommandId
			|| Canceled->LockCommandId != Decision.LockCommandId
			|| Lock->RequestCommandId != Decision.RequestCommandId
			|| !bSupportedCanceledQaGame
			|| Canceled->ReasonCode != MatchWinnerCanceledGameReason
			|| Canceled->Status != MatchWinnerClosedCanceledStatus
			|| Decision.DecisionSchema != MatchWinnerVoidDecisionSchema
			|| Decision.DecisionVersion != MatchWinnerVoidDecisionVersion
			|| Decision.OfferId != Request->OfferId
			|| Decision.OfferSchema != MatchWinnerOfferSchema
			|| Decision.OfferVersion != Request->OfferVersion
			|| Decision.SeasonNumber != Canceled->SeasonNumber
			|| Decision.GameNumber != Canceled->GameNumber
			|| Decision.SelectedTeam != Request->OfferedTeam
			|| Decision.Stake != Request->Stake
			|| Decision.Stake != 40
			|| Decision.CancellationReason != Canceled->ReasonCode
			|| Decision.Outcome != MatchWinnerVoidedOutcome
			|| Decision.RefundDue != Decision.Stake
			|| Decision.RefundDue != 40
			|| Decision.Status != MatchWinnerDecidedVoidPendingRefundStatus
			|| bHasResult
			|| bHasNormalDecision
			|| bHasFinalization)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner void decision at index %d."), Index);
			return false;
		}
	}
	OutError.Reset();
	return true;
}

bool ValidateMatchWinnerVoidFinalizations(
	const FOddsWellOddsBucksLedger& Ledger,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& CanceledGames,
	const TArray<FOddsWellMatchWinnerVoidDecisionRecord>& VoidDecisions,
	const TArray<FOddsWellMatchWinnerVoidFinalizationRecord>& VoidFinalizations,
	FString& OutError)
{
	if (VoidFinalizations.Num() > 1)
	{
		OutError = TEXT("Only one Match Winner void-finalization QA record is supported.");
		return false;
	}
	int32 RefundEntryCount = 0;
	for (const FOddsWellOddsBucksEntry& Entry : Ledger.GetEntries())
	{
		RefundEntryCount += Entry.Reason == MatchWinnerRefundReason ? 1 : 0;
	}
	if (RefundEntryCount != VoidFinalizations.Num())
	{
		OutError = TEXT("The Match Winner refund ledger evidence does not match its void finalization.");
		return false;
	}
	for (int32 Index = 0; Index < VoidFinalizations.Num(); ++Index)
	{
		const FOddsWellMatchWinnerVoidFinalizationRecord& Finalization = VoidFinalizations[Index];
		const FOddsWellMatchWinnerVoidDecisionRecord* Decision = VoidDecisions.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerVoidDecisionRecord& Candidate)
			{
				return Candidate.VoidDecisionCommandId == Finalization.VoidDecisionCommandId;
			});
		const FOddsWellMatchWinnerCanceledGameRecord* Canceled = CanceledGames.FindByPredicate(
			[&Finalization](const FOddsWellMatchWinnerCanceledGameRecord& Candidate)
			{
				return Candidate.CancellationCommandId == Finalization.CancellationCommandId
					&& Candidate.CancellationEvidenceId == Finalization.CancellationEvidenceId;
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
		const FOddsWellOddsBucksEntry* Refund = Ledger.GetEntries().FindByPredicate(
			[&Finalization](const FOddsWellOddsBucksEntry& Entry)
			{
				return Entry.CommandId == Finalization.RefundLedgerCommandId;
			});
		const bool bHasNormalOutcome = Results.ContainsByPredicate(
			[&Finalization](const FOddsWellMatchWinnerResultLinkRecord& Result)
			{
				return Result.RequestCommandId == Finalization.RequestCommandId;
			})
			|| Decisions.ContainsByPredicate(
				[&Finalization](const FOddsWellMatchWinnerSettlementDecisionRecord& Candidate)
				{
					return Candidate.RequestCommandId == Finalization.RequestCommandId;
				})
			|| LossFinalizations.ContainsByPredicate(
				[&Finalization](const FOddsWellMatchWinnerLossFinalizationRecord& Candidate)
				{
					return Candidate.RequestCommandId == Finalization.RequestCommandId;
				})
			|| WinFinalizations.ContainsByPredicate(
				[&Finalization](const FOddsWellMatchWinnerWinFinalizationRecord& Candidate)
				{
					return Candidate.RequestCommandId == Finalization.RequestCommandId;
				});
		const bool bSupportedCanceledQaGame =
			(Finalization.SeasonNumber == CanceledQaSeasonNumber && Finalization.GameNumber == CanceledQaGameNumber)
			|| (Finalization.SeasonNumber == UpcomingQaSeasonNumber && Finalization.GameNumber == UpcomingQaGameNumber);
		if (Finalization.FinalizationCommandId.TrimStartAndEnd().IsEmpty()
			|| Finalization.VoidDecisionCommandId.TrimStartAndEnd().IsEmpty()
			|| Finalization.FinalizationCommandId != Finalization.RefundLedgerCommandId
			|| Finalization.FinalizationCommandId == Finalization.VoidDecisionCommandId
			|| Finalization.FinalizationCommandId == Finalization.CancellationCommandId
			|| Finalization.FinalizationCommandId == Finalization.CancellationEvidenceId
			|| Finalization.FinalizationCommandId == Finalization.RequestCommandId
			|| Finalization.FinalizationCommandId == Finalization.LockCommandId
			|| !Decision
			|| !Canceled
			|| !Request
			|| !Lock
			|| !Refund
			|| Decision->CancellationCommandId != Finalization.CancellationCommandId
			|| Decision->CancellationEvidenceId != Finalization.CancellationEvidenceId
			|| Decision->RequestCommandId != Finalization.RequestCommandId
			|| Decision->LockCommandId != Finalization.LockCommandId
			|| Decision->Status != MatchWinnerDecidedVoidPendingRefundStatus
			|| Canceled->RequestCommandId != Finalization.RequestCommandId
			|| Canceled->LockCommandId != Finalization.LockCommandId
			|| Lock->RequestCommandId != Finalization.RequestCommandId
			|| Finalization.FinalizationSchema != MatchWinnerVoidFinalizationSchema
			|| Finalization.FinalizationVersion != MatchWinnerVoidFinalizationVersion
			|| Finalization.OfferId != Decision->OfferId
			|| Finalization.OfferSchema != Decision->OfferSchema
			|| Finalization.OfferVersion != Decision->OfferVersion
			|| !bSupportedCanceledQaGame
			|| Finalization.SeasonNumber != Decision->SeasonNumber
			|| Finalization.GameNumber != Decision->GameNumber
			|| Finalization.SelectedTeam != Decision->SelectedTeam
			|| Finalization.Stake != 40
			|| Finalization.Stake != Decision->Stake
			|| Finalization.CancellationReason != MatchWinnerCanceledGameReason
			|| Finalization.CancellationReason != Decision->CancellationReason
			|| Finalization.Outcome != MatchWinnerVoidedOutcome
			|| Finalization.Outcome != Decision->Outcome
			|| Finalization.RefundDue != 40
			|| Finalization.RefundDue != Decision->RefundDue
			|| Finalization.RefundApplied != Finalization.RefundDue
			|| Finalization.Status != MatchWinnerSettledVoidStatus
			|| Refund->Sequence != 3
			|| Refund->Delta != 40
			|| Refund->BalanceAfter != 100
			|| Refund->Reason != MatchWinnerRefundReason
			|| Ledger.GetEntries().Num() != 3
			|| Ledger.GetBalance() != 100
			|| Finalization.ObservedLedgerEntryCount != 3
			|| Finalization.ObservedFinalBalance != 100
			|| bHasNormalOutcome)
		{
			OutError = FString::Printf(TEXT("Invalid Match Winner void finalization at index %d."), Index);
			return false;
		}
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord>& OutMatchWinnerCanceledGames,
	TArray<FOddsWellMatchWinnerVoidDecisionRecord>& OutMatchWinnerVoidDecisions,
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
	OutMatchWinnerCanceledGames = Record->SchemaVersion >= 9
		? Record->MatchWinnerCanceledGames
		: TArray<FOddsWellMatchWinnerCanceledGameRecord>();
	OutMatchWinnerVoidDecisions = Record->SchemaVersion >= 10
		? Record->MatchWinnerVoidDecisions
		: TArray<FOddsWellMatchWinnerVoidDecisionRecord>();
	const TArray<FOddsWellMatchWinnerVoidFinalizationRecord> MatchWinnerVoidFinalizations = Record->SchemaVersion >= 11
		? Record->MatchWinnerVoidFinalizations
		: TArray<FOddsWellMatchWinnerVoidFinalizationRecord>();
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
	if (!ValidateMatchWinnerCanceledGames(OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutMatchWinnerSettlementDecisions, OutMatchWinnerLossFinalizations, OutMatchWinnerWinFinalizations, OutMatchWinnerCanceledGames, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerVoidDecisions(OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutMatchWinnerSettlementDecisions, OutMatchWinnerLossFinalizations, OutMatchWinnerWinFinalizations, OutMatchWinnerCanceledGames, OutMatchWinnerVoidDecisions, OutError))
	{
		return false;
	}
	if (!ValidateMatchWinnerVoidFinalizations(OutLedger, OutMatchWinnerRequests, OutMatchWinnerLocks, OutMatchWinnerResultLinks, OutMatchWinnerSettlementDecisions, OutMatchWinnerLossFinalizations, OutMatchWinnerWinFinalizations, OutMatchWinnerCanceledGames, OutMatchWinnerVoidDecisions, MatchWinnerVoidFinalizations, OutError))
	{
		return false;
	}
	OutError.Reset();
	return true;
}

bool HasExactCanonicalRequestEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const int64 ObservedServerUnixSeconds,
	const FOddsWellOddsBucksLedger& Ledger,
	const UOddsWellOddsBucksSaveGame& Record,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& ResultLinks,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& CanceledGames,
	const TArray<FOddsWellMatchWinnerVoidDecisionRecord>& VoidDecisions,
	const bool bAllowExactLock,
	const FOddsWellMatchWinnerResultLinkRecord* ExactAllowedResult = nullptr,
	const FOddsWellMatchWinnerSettlementDecisionRecord* ExactAllowedDecision = nullptr,
	const FOddsWellMatchWinnerLossFinalizationRecord* ExactAllowedLossFinalization = nullptr)
{
	const bool bResultEvidenceExact =
		ResultLinks.IsEmpty()
		|| (ExactAllowedResult
			&& ResultLinks.Num() == 1
			&& IsSameMatchWinnerResultLink(
				ResultLinks[0],
				*ExactAllowedResult));
	const bool bDecisionEvidenceExact =
		Decisions.IsEmpty()
		|| (ExactAllowedDecision
			&& Decisions.Num() == 1
			&& IsSameMatchWinnerSettlementDecision(
				Decisions[0],
				*ExactAllowedDecision));
	const bool bLossFinalizationEvidenceExact =
		LossFinalizations.IsEmpty()
		|| (ExactAllowedLossFinalization
			&& LossFinalizations.Num() == 1
			&& IsSameMatchWinnerLossFinalization(
				LossFinalizations[0],
				*ExactAllowedLossFinalization));
	if (ObservedServerUnixSeconds < OfferEligibleUnixSeconds
		|| Requests.Num() != 1
		|| Ledger.GetEntries().Num() != 2
		|| Ledger.GetBalance() != 60
		|| !bResultEvidenceExact
		|| !bDecisionEvidenceExact
		|| !bLossFinalizationEvidenceExact
		|| !WinFinalizations.IsEmpty()
		|| !CanceledGames.IsEmpty()
		|| !VoidDecisions.IsEmpty()
		|| !Record.MatchWinnerVoidFinalizations.IsEmpty()
		|| ExactOffer.Selections.Num() != 2)
	{
		return false;
	}

	const FOddsWellOddsBucksEntry& Credit = Ledger.GetEntries()[0];
	const FOddsWellOddsBucksEntry& Debit = Ledger.GetEntries()[1];
	const FOddsWellMatchWinnerRequestRecord& Request = Requests[0];
	const FOddsWellMatchWinnerSelection& Selection = ExactOffer.Selections[0];
	const FString ExpectedRequestId =
		TEXT("canonical:h26e:match_winner:request:") + ExactOffer.OfferId;
	const FString ExpectedLockId =
		TEXT("canonical:h26g:match_winner:lock:") + ExactOffer.OfferId;
	const bool bLockEvidenceExact = Locks.IsEmpty()
		|| (bAllowExactLock
			&& Locks.Num() == 1
			&& Locks[0].LockCommandId == ExpectedLockId
			&& Locks[0].RequestCommandId == ExpectedRequestId
			&& Locks[0].SeasonNumber == ExactOffer.SeasonNumber
			&& Locks[0].GameNumber == ExactOffer.GameNumber
			&& Locks[0].AuthoritativeGameStartUnixSeconds == ExactOffer.LockUnixSeconds
			&& Locks[0].LockUnixSeconds == ExactOffer.LockUnixSeconds
			&& Locks[0].Decision == MatchWinnerLockedDecision);
	return bLockEvidenceExact
		&& Credit.Sequence == 1
		&& Credit.CommandId == FirstJobCommandId
		&& Credit.Delta == 100
		&& Credit.BalanceAfter == 100
		&& Credit.Reason == FirstJobReason
		&& Debit.Sequence == 2
		&& Debit.CommandId == ExpectedRequestId
		&& Debit.Delta == -40
		&& Debit.BalanceAfter == 60
		&& Debit.Reason == MatchWinnerStakeReason
		&& Request.EvidenceVersion == MatchWinnerRequestEvidenceVersion
		&& Request.RequestCommandId == ExpectedRequestId
		&& Request.StakeLedgerCommandId == ExpectedRequestId
		&& Request.OfferId == ExactOffer.OfferId
		&& Request.OfferVersion == ExactOffer.OfferVersion
		&& Request.OfferSchema == ExactOffer.Schema
		&& Request.Market == ExactOffer.Market
		&& Request.Currency == ExactOffer.Currency
		&& Request.SourcePredictionVersion == ExactOffer.SourcePredictionVersion
		&& Request.SourceSnapshotVersion == ExactOffer.SourceSnapshotVersion
		&& Request.SourceModel == ExactOffer.SourceModel
		&& Request.SourceCommitmentSha256 == ExactOffer.SourceCommitmentSha256
		&& Request.SeasonNumber == ExactOffer.SeasonNumber
		&& Request.GameNumber == ExactOffer.GameNumber
		&& Request.HomeTeam == ExactOffer.HomeTeam
		&& Request.AwayTeam == ExactOffer.AwayTeam
		&& Request.OfferedTeam == ExactOffer.HomeTeam
		&& Request.OfferedTeam == Selection.Team
		&& Request.SelectedWinProbabilityE8 == Selection.WinProbabilityE8
		&& Request.SelectedDecimalOddsE4 == Selection.DecimalOddsE4
		&& Request.Stake == 40
		&& Request.PayoutFormula == ExactOffer.PayoutFormula
		&& Request.GrossReturn == 69
		&& Request.AcceptedUnixSeconds >= OfferEligibleUnixSeconds
		&& Request.AcceptedUnixSeconds <= ObservedServerUnixSeconds
		&& Request.AcceptedUnixSeconds < Request.LockUnixSeconds
		&& Request.LockUnixSeconds == ExactOffer.LockUnixSeconds
		&& Request.Status == AcceptedPendingLockStatus;
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

bool FinalizeOddsWellMatchWinnerOfferIdentity(
	FOddsWellMatchWinnerOffer& InOutOffer,
	FString& OutCanonicalJson,
	FString& OutError)
{
	return GetMatchWinnerOfferId(
			InOutOffer,
			InOutOffer.OfferId,
			OutError,
			&OutCanonicalJson)
		&& ValidateMatchWinnerOffer(InOutOffer, OutError);
}

bool UseOddsWellOddsBucksQaSlot()
{
	return FParse::Param(FCommandLine::Get(), TEXT("JobQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("JobRecoveryQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookWagerQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookReceiptQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookLockQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookLockQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookCancellationQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookCancellationQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidDecisionQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidDecisionQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidFinalizationQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("SportsbookVoidFinalizationQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerRequestQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerRequestQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalPendingReceiptQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLockQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLockQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalPostLockQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalExecutionCommitmentQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalExecutionCommitmentQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerResultLinkQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerResultLinkQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLossDecisionQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLossDecisionQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLossFinalizationQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLossFinalizationQaVerify"));
}

const FString& GetOddsWellUpcomingQaMatchWinnerRequestCommandId()
{
	return UpcomingQaRequestCommandId;
}

int64 GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds()
{
	return UpcomingQaAcceptedUnixSeconds;
}

const FString& GetOddsWellUpcomingQaMatchWinnerLockCommandId()
{
	return UpcomingQaLockCommandId;
}

int64 GetOddsWellUpcomingQaMatchWinnerLockUnixSeconds()
{
	return UpcomingQaLockUnixSeconds;
}

const FString& GetOddsWellUpcomingQaMatchWinnerCancellationCommandId()
{
	return UpcomingQaCancellationCommandId;
}

const FString& GetOddsWellUpcomingQaMatchWinnerCancellationEvidenceId()
{
	return UpcomingQaCancellationEvidenceId;
}

int64 GetOddsWellUpcomingQaMatchWinnerCancellationUnixSeconds()
{
	return UpcomingQaCancellationUnixSeconds;
}

const FString& GetOddsWellUpcomingQaMatchWinnerVoidDecisionCommandId()
{
	return UpcomingQaVoidDecisionCommandId;
}

const FString& GetOddsWellUpcomingQaMatchWinnerVoidFinalizationCommandId()
{
	return UpcomingQaVoidFinalizationCommandId;
}

bool BuildOddsWellUpcomingQaMatchWinnerOffer(FOddsWellMatchWinnerOffer& OutOffer, FString& OutError)
{
	return BuildUpcomingQaMatchWinnerOffer(OutOffer, OutError);
}

bool LoadOddsWellPendingQaMatchWinnerReceipt(
	FOddsWellPendingQaMatchWinnerReceipt& OutReceipt,
	FString& OutError)
{
	OutReceipt = FOddsWellPendingQaMatchWinnerReceipt();
	const auto FailClosed = [&OutError]()
	{
		OutError = TEXT("Pending Match Winner receipt unavailable.");
		return false;
	};
	if (!UGameplayStatics::DoesSaveGameExist(OddsBucksQaSlot, OddsBucksUserIndex))
	{
		return FailClosed();
	}

	const UOddsWellOddsBucksSaveGame* Record = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion)
	{
		return FailClosed();
	}

	FOddsWellMatchWinnerOffer Offer;
	if (!BuildUpcomingQaMatchWinnerOffer(Offer, ValidationError)
		|| Ledger.GetEntries().Num() != 2
		|| Ledger.GetBalance() != 60
		|| NextJobPayoutUnixSeconds != UpcomingQaLockUnixSeconds
		|| Requests.Num() != 1
		|| !Locks.IsEmpty()
		|| !ResultLinks.IsEmpty()
		|| !Decisions.IsEmpty()
		|| !LossFinalizations.IsEmpty()
		|| !WinFinalizations.IsEmpty()
		|| !CanceledGames.IsEmpty()
		|| !VoidDecisions.IsEmpty()
		|| !Record->MatchWinnerVoidFinalizations.IsEmpty())
	{
		return FailClosed();
	}

	const FOddsWellOddsBucksEntry& Credit = Ledger.GetEntries()[0];
	const FOddsWellOddsBucksEntry& Debit = Ledger.GetEntries()[1];
	const FOddsWellMatchWinnerRequestRecord& Request = Requests[0];
	if (Credit.Sequence != 1
		|| Credit.CommandId != FirstJobCommandId
		|| Credit.Delta != FirstJobPayout
		|| Credit.BalanceAfter != FirstJobPayout
		|| Credit.Reason != FirstJobReason
		|| Debit.Sequence != 2
		|| Debit.CommandId != UpcomingQaRequestCommandId
		|| Debit.Delta != -40
		|| Debit.BalanceAfter != 60
		|| Debit.Reason != MatchWinnerStakeReason
		|| Request.RequestCommandId != UpcomingQaRequestCommandId
		|| Request.StakeLedgerCommandId != UpcomingQaRequestCommandId
		|| Request.OfferId != Offer.OfferId
		|| Request.OfferVersion != Offer.OfferVersion
		|| Request.SeasonNumber != Offer.SeasonNumber
		|| Request.GameNumber != Offer.GameNumber
		|| Request.HomeTeam != Offer.HomeTeam
		|| Request.AwayTeam != Offer.AwayTeam
		|| Request.OfferedTeam != Offer.HomeTeam
		|| Request.Stake != 40
		|| Request.AcceptedUnixSeconds != UpcomingQaAcceptedUnixSeconds
		|| Request.LockUnixSeconds != Offer.LockUnixSeconds
		|| Request.AcceptedUnixSeconds >= Request.LockUnixSeconds
		|| Request.Status != AcceptedPendingLockStatus)
	{
		return FailClosed();
	}

	FOddsWellPendingQaMatchWinnerReceipt Candidate;
	Candidate.RequestId = Request.RequestCommandId;
	Candidate.OfferId = Request.OfferId;
	Candidate.OfferVersion = Request.OfferVersion;
	Candidate.SelectedTeam = Request.OfferedTeam;
	Candidate.Stake = Request.Stake;
	Candidate.AcceptedUnixSeconds = Request.AcceptedUnixSeconds;
	Candidate.LockUnixSeconds = Request.LockUnixSeconds;
	Candidate.Status = Request.Status;
	Candidate.LedgerSequence = Debit.Sequence;
	Candidate.LedgerDelta = Debit.Delta;
	Candidate.LedgerReason = Debit.Reason;
	Candidate.CurrentBalance = Ledger.GetBalance();
	OutReceipt = MoveTemp(Candidate);
	OutError.Reset();
	return true;
}

EOddsWellCanonicalPendingReceiptResult LoadOddsWellCanonicalPendingMatchWinnerReceiptEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const int64 ObservedServerUnixSeconds,
	const bool bQaSlot,
	FOddsWellCanonicalPendingMatchWinnerReceipt& OutReceipt,
	FString& OutError)
{
	OutReceipt = {};
	const auto Reject = [&OutError]()
	{
		OutError = TEXT("Canonical pending Match Winner receipt evidence is unavailable.");
		return EOddsWellCanonicalPendingReceiptResult::Rejected;
	};
	const FString& Slot = GetOddsBucksSlot(bQaSlot);
	if (!UGameplayStatics::DoesSaveGameExist(Slot, OddsBucksUserIndex))
	{
		OutError.Reset();
		return EOddsWellCanonicalPendingReceiptResult::Missing;
	}

	const UOddsWellOddsBucksSaveGame* Record =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(Slot, OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion)
	{
		return Reject();
	}
	if (Requests.IsEmpty())
	{
		const bool bHasStakeDebit = Ledger.GetEntries().ContainsByPredicate(
			[](const FOddsWellOddsBucksEntry& Entry)
			{
				return Entry.Reason == MatchWinnerStakeReason;
			});
		if (bHasStakeDebit
			|| !Locks.IsEmpty()
			|| !ResultLinks.IsEmpty()
			|| !Decisions.IsEmpty()
			|| !LossFinalizations.IsEmpty()
			|| !WinFinalizations.IsEmpty()
			|| !CanceledGames.IsEmpty()
			|| !VoidDecisions.IsEmpty()
			|| !Record->MatchWinnerVoidFinalizations.IsEmpty())
		{
			return Reject();
		}
		OutError.Reset();
		return EOddsWellCanonicalPendingReceiptResult::Missing;
	}
	if (ObservedServerUnixSeconds >= ExactOffer.LockUnixSeconds
		|| !HasExactCanonicalRequestEvidence(
			ExactOffer,
			OfferEligibleUnixSeconds,
			ObservedServerUnixSeconds,
			Ledger,
			*Record,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			false))
	{
		return Reject();
	}

	const FOddsWellMatchWinnerRequestRecord& Request = Requests[0];

	FOddsWellCanonicalPendingMatchWinnerReceipt Candidate;
	Candidate.RequestId = Request.RequestCommandId;
	Candidate.OfferId = Request.OfferId;
	Candidate.SelectedTeam = Request.OfferedTeam;
	Candidate.SelectedWinProbabilityE8 = Request.SelectedWinProbabilityE8;
	Candidate.SelectedDecimalOddsE4 = Request.SelectedDecimalOddsE4;
	Candidate.Stake = Request.Stake;
	Candidate.GrossReturn = Request.GrossReturn;
	Candidate.AcceptedUnixSeconds = Request.AcceptedUnixSeconds;
	Candidate.LockUnixSeconds = Request.LockUnixSeconds;
	Candidate.Status = Request.Status;
	Candidate.CurrentBalance = Ledger.GetBalance();
	OutReceipt = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellCanonicalPendingReceiptResult::Ready;
}

EOddsWellMatchWinnerLockResult LockOddsWellCanonicalMatchWinnerRequestEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const int64 ObservedServerUnixSeconds,
	const bool bQaSlot,
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	const FString& Slot = GetOddsBucksSlot(bQaSlot);
	const UOddsWellOddsBucksSaveGame* Record =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(Slot, OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion
		|| ObservedServerUnixSeconds != ExactOffer.LockUnixSeconds
		|| !HasExactCanonicalRequestEvidence(
			ExactOffer,
			OfferEligibleUnixSeconds,
			ObservedServerUnixSeconds,
			Ledger,
			*Record,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			true))
	{
		OutError = TEXT("Canonical Match Winner lock requires the exact current H26E request at H26A tipoff.");
		return EOddsWellMatchWinnerLockResult::Rejected;
	}

	return LockOddsWellMatchWinnerRequest(
		TEXT("canonical:h26e:match_winner:request:") + ExactOffer.OfferId,
		TEXT("canonical:h26g:match_winner:lock:") + ExactOffer.OfferId,
		ExactOffer.SeasonNumber,
		ExactOffer.GameNumber,
		ExactOffer.LockUnixSeconds,
		bQaSlot,
		OutRecord,
		OutError);
}

bool LoadOddsWellCanonicalMatchWinnerLockEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const bool bQaSlot,
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	const UOddsWellOddsBucksSaveGame* Record =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				GetOddsBucksSlot(bQaSlot),
				OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion
		|| Locks.Num() != 1
		|| !HasExactCanonicalRequestEvidence(
			ExactOffer,
			OfferEligibleUnixSeconds,
			ExactOffer.LockUnixSeconds,
			Ledger,
			*Record,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			true))
	{
		OutError = TEXT("Canonical active-game execution requires the exact current H26G lock with no downstream evidence.");
		return false;
	}
	OutRecord = Locks[0];
	OutError.Reset();
	return true;
}

bool ValidateOddsWellCanonicalMatchWinnerResultLinkPrerequisites(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const FOddsWellMatchWinnerResultLinkRecord& ExactResult,
	const bool bQaSlot,
	FString& OutError)
{
	const UOddsWellOddsBucksSaveGame* Record =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				GetOddsBucksSlot(bQaSlot),
				OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	const FString ExpectedRequestId =
		TEXT("canonical:h26e:match_winner:request:")
		+ ExactOffer.OfferId;
	const FString ExpectedLockId =
		TEXT("canonical:h26g:match_winner:lock:")
		+ ExactOffer.OfferId;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion
		|| Locks.Num() != 1
		|| ExactResult.RequestCommandId != ExpectedRequestId
		|| ExactResult.LockCommandId != ExpectedLockId
		|| !IsExactPrivateCanonicalMatchWinnerResult(ExactResult)
		|| !HasExactCanonicalRequestEvidence(
			ExactOffer,
			OfferEligibleUnixSeconds,
			ExactOffer.LockUnixSeconds,
			Ledger,
			*Record,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			true,
			&ExactResult))
	{
		OutError =
			TEXT("Canonical Match Winner result linking requires exact schema-12 H26E/H26G evidence and no downstream state.");
		return false;
	}
	OutError.Reset();
	return true;
}

EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellCanonicalMatchWinnerLossDecisionEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const bool bQaSlot,
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	const UOddsWellOddsBucksSaveGame* Record =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				GetOddsBucksSlot(bQaSlot),
				OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	const FString ExpectedRequestId =
		TEXT("canonical:h26e:match_winner:request:")
		+ ExactOffer.OfferId;
	const FString ExpectedLockId =
		TEXT("canonical:h26g:match_winner:lock:")
		+ ExactOffer.OfferId;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion
		|| Locks.Num() != 1
		|| ResultLinks.Num() != 1
		|| !IsExactPrivateCanonicalMatchWinnerResult(ResultLinks[0])
		|| ResultLinks[0].RequestCommandId != ExpectedRequestId
		|| ResultLinks[0].LockCommandId != ExpectedLockId
		|| ResultLinks[0].Winner != ExactOffer.AwayTeam)
	{
		OutError =
			TEXT("Canonical Match Winner loss decision requires the exact current H26E/H26G/H26L chain.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}

	const FOddsWellMatchWinnerResultLinkRecord& Result = ResultLinks[0];
	const FString ResultRecordSha256 =
		Result.ResultCommandId.RightChop(
			PrivateCanonicalResultCommandPrefix.Len());
	FOddsWellMatchWinnerSettlementDecisionRecord ExactDecision;
	ExactDecision.DecisionCommandId =
		PrivateCanonicalLossDecisionCommandPrefix
		+ ResultRecordSha256;
	ExactDecision.RequestCommandId = ExpectedRequestId;
	ExactDecision.LockCommandId = ExpectedLockId;
	ExactDecision.ResultCommandId = Result.ResultCommandId;
	ExactDecision.DecisionSchema =
		MatchWinnerSettlementDecisionSchema;
	ExactDecision.DecisionVersion =
		MatchWinnerSettlementDecisionVersion;
	ExactDecision.OfferId = ExactOffer.OfferId;
	ExactDecision.OfferVersion = ExactOffer.OfferVersion;
	ExactDecision.SelectedTeam = ExactOffer.HomeTeam;
	ExactDecision.AuthoritativeWinner = ExactOffer.AwayTeam;
	ExactDecision.Stake = 40;
	ExactDecision.Outcome = MatchWinnerLostOutcome;
	ExactDecision.GrossReturnDue = 0;
	ExactDecision.SelectedWinProbabilityE8 = 0;
	ExactDecision.PayoutFormula.Reset();
	ExactDecision.Status = MatchWinnerDecidedPendingApplyStatus;
	if (!HasExactCanonicalRequestEvidence(
			ExactOffer,
			OfferEligibleUnixSeconds,
			ExactOffer.LockUnixSeconds,
			Ledger,
			*Record,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			true,
			&Result,
			&ExactDecision))
	{
		OutError =
			TEXT("Canonical Match Winner loss decision requires exact schema-12 evidence and no later state.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}

	const EOddsWellMatchWinnerSettlementDecisionResult DecisionResult =
		DecideOddsWellMatchWinnerSettlement(
			ExactOffer,
			ExactDecision.DecisionCommandId,
			ExactDecision.RequestCommandId,
			ExactDecision.LockCommandId,
			ExactDecision.ResultCommandId,
			bQaSlot,
			OutRecord,
			OutError);
	if ((DecisionResult
			!= EOddsWellMatchWinnerSettlementDecisionResult::Decided
			&& DecisionResult
				!= EOddsWellMatchWinnerSettlementDecisionResult::Duplicate)
		|| !IsSameMatchWinnerSettlementDecision(
			OutRecord,
			ExactDecision))
	{
		OutRecord = {};
		if (OutError.IsEmpty())
		{
			OutError =
				TEXT("The canonical Match Winner loss decision primitive returned non-exact evidence.");
		}
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	OutError.Reset();
	return DecisionResult;
}

EOddsWellMatchWinnerLossFinalizationResult FinalizeOddsWellCanonicalMatchWinnerLossEvidence(
	const FOddsWellMatchWinnerOffer& ExactOffer,
	const int64 OfferEligibleUnixSeconds,
	const bool bQaSlot,
	FOddsWellMatchWinnerLossFinalizationRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	const UOddsWellOddsBucksSaveGame* Record =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				GetOddsBucksSlot(bQaSlot),
				OddsBucksUserIndex));
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bNeedsMigration = false;
	FString ValidationError;
	const FString ExpectedRequestId =
		TEXT("canonical:h26e:match_winner:request:")
		+ ExactOffer.OfferId;
	const FString ExpectedLockId =
		TEXT("canonical:h26g:match_winner:lock:")
		+ ExactOffer.OfferId;
	if (!Record
		|| !ValidateOddsBucksSave(
			Record,
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bNeedsMigration,
			ValidationError)
		|| bNeedsMigration
		|| Record->SchemaVersion != OddsBucksSchemaVersion
		|| Locks.Num() != 1
		|| ResultLinks.Num() != 1
		|| Decisions.Num() != 1
		|| !IsExactPrivateCanonicalMatchWinnerResult(ResultLinks[0])
		|| ResultLinks[0].RequestCommandId != ExpectedRequestId
		|| ResultLinks[0].LockCommandId != ExpectedLockId
		|| ResultLinks[0].Winner != ExactOffer.AwayTeam)
	{
		OutError =
			TEXT("Canonical Match Winner loss finalization requires the exact current H26E/H26G/H26L/H26M chain.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}

	const FOddsWellMatchWinnerResultLinkRecord& Result = ResultLinks[0];
	const FString ResultRecordSha256 =
		Result.ResultCommandId.RightChop(
			PrivateCanonicalResultCommandPrefix.Len());
	const FOddsWellMatchWinnerSettlementDecisionRecord& Decision =
		Decisions[0];
	const FString ExpectedDecisionCommandId =
		PrivateCanonicalLossDecisionCommandPrefix
		+ ResultRecordSha256;
	if (Decision.DecisionCommandId != ExpectedDecisionCommandId
		|| Decision.RequestCommandId != ExpectedRequestId
		|| Decision.LockCommandId != ExpectedLockId
		|| Decision.ResultCommandId != Result.ResultCommandId
		|| Decision.DecisionSchema != MatchWinnerSettlementDecisionSchema
		|| Decision.DecisionVersion != MatchWinnerSettlementDecisionVersion
		|| Decision.OfferId != ExactOffer.OfferId
		|| Decision.OfferVersion != ExactOffer.OfferVersion
		|| Decision.SelectedTeam != ExactOffer.HomeTeam
		|| Decision.AuthoritativeWinner != ExactOffer.AwayTeam
		|| Decision.Stake != 40
		|| Decision.Outcome != MatchWinnerLostOutcome
		|| Decision.GrossReturnDue != 0
		|| Decision.SelectedWinProbabilityE8 != 0
		|| !Decision.PayoutFormula.IsEmpty()
		|| Decision.Status != MatchWinnerDecidedPendingApplyStatus)
	{
		OutError =
			TEXT("Canonical Match Winner loss finalization requires the exact pending H26M loss decision.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}

	FOddsWellMatchWinnerLossFinalizationRecord ExactFinalization;
	ExactFinalization.FinalizationCommandId =
		PrivateCanonicalLossFinalizationCommandPrefix
		+ ResultRecordSha256;
	ExactFinalization.DecisionCommandId = Decision.DecisionCommandId;
	ExactFinalization.RequestCommandId = ExpectedRequestId;
	ExactFinalization.LockCommandId = ExpectedLockId;
	ExactFinalization.ResultCommandId = Result.ResultCommandId;
	ExactFinalization.FinalizationSchema =
		MatchWinnerLossFinalizationSchema;
	ExactFinalization.FinalizationVersion =
		MatchWinnerLossFinalizationVersion;
	ExactFinalization.OfferId = ExactOffer.OfferId;
	ExactFinalization.OfferVersion = ExactOffer.OfferVersion;
	ExactFinalization.SelectedTeam = ExactOffer.HomeTeam;
	ExactFinalization.AuthoritativeWinner = ExactOffer.AwayTeam;
	ExactFinalization.Stake = 40;
	ExactFinalization.Outcome = MatchWinnerLostOutcome;
	ExactFinalization.GrossReturnApplied = 0;
	ExactFinalization.Status = MatchWinnerSettledLostStatus;
	ExactFinalization.ObservedFinalBalance = 60;
	ExactFinalization.ObservedLedgerEntryCount = 2;
	if (!HasExactCanonicalRequestEvidence(
			ExactOffer,
			OfferEligibleUnixSeconds,
			ExactOffer.LockUnixSeconds,
			Ledger,
			*Record,
			Requests,
			Locks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			true,
			&Result,
			&Decision,
			&ExactFinalization))
	{
		OutError =
			TEXT("Canonical Match Winner loss finalization requires exact schema-12 evidence and no later state.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}

	const EOddsWellMatchWinnerLossFinalizationResult FinalizationResult =
		FinalizeOddsWellMatchWinnerLoss(
			ExactFinalization.FinalizationCommandId,
			ExactFinalization.DecisionCommandId,
			bQaSlot,
			OutRecord,
			OutError);
	if ((FinalizationResult
			!= EOddsWellMatchWinnerLossFinalizationResult::Finalized
			&& FinalizationResult
				!= EOddsWellMatchWinnerLossFinalizationResult::Duplicate)
		|| !IsSameMatchWinnerLossFinalization(
			OutRecord,
			ExactFinalization))
	{
		OutRecord = {};
		if (OutError.IsEmpty())
		{
			OutError =
				TEXT("The canonical Match Winner loss finalization primitive returned non-exact evidence.");
		}
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	OutError.Reset();
	return FinalizationResult;
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
bool WriteMatchWinnerVoidReconciliationFromValidatedState(
	const FOddsWellOddsBucksLedger& Ledger,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& CanceledGames,
	const TArray<FOddsWellMatchWinnerVoidDecisionRecord>& VoidDecisions,
	const TArray<FOddsWellMatchWinnerVoidFinalizationRecord>& VoidFinalizations,
	const bool bQaProjection,
	FString& OutError)
{
	if (Requests.Num() != 1
		|| Locks.Num() != 1
		|| CanceledGames.Num() != 1
		|| VoidDecisions.Num() != 1
		|| VoidFinalizations.Num() != 1)
	{
		OutError = TEXT("The Match Winner void reconciliation requires one complete exact finalized chain.");
		return false;
	}
	const FOddsWellMatchWinnerRequestRecord& Request = Requests[0];
	const FOddsWellMatchWinnerLockRecord& Lock = Locks[0];
	const FOddsWellMatchWinnerCanceledGameRecord& Canceled = CanceledGames[0];
	const FOddsWellMatchWinnerVoidDecisionRecord& Decision = VoidDecisions[0];
	const FOddsWellMatchWinnerVoidFinalizationRecord& Finalization = VoidFinalizations[0];
	const FOddsWellOddsBucksEntry* StakeEntry = Ledger.GetEntries().FindByPredicate(
		[&Request](const FOddsWellOddsBucksEntry& Entry)
		{
			return Entry.CommandId == Request.StakeLedgerCommandId;
		});
	const FOddsWellOddsBucksEntry* RefundEntry = Ledger.GetEntries().FindByPredicate(
		[&Finalization](const FOddsWellOddsBucksEntry& Entry)
		{
			return Entry.CommandId == Finalization.RefundLedgerCommandId;
		});
	const bool bCanceledQaChain = Lock.SeasonNumber == CanceledQaSeasonNumber
		&& Lock.GameNumber == CanceledQaGameNumber;
	const bool bUpcomingQaChain = Lock.SeasonNumber == UpcomingQaSeasonNumber
		&& Lock.GameNumber == UpcomingQaGameNumber
		&& Request.OfferId == UpcomingQaOfferId
		&& Request.OfferVersion == MatchWinnerOfferVersion
		&& Request.RequestCommandId == UpcomingQaRequestCommandId
		&& Request.StakeLedgerCommandId == UpcomingQaRequestCommandId
		&& Request.HomeTeam == TEXT("Sundale Sparks")
		&& Request.AwayTeam == TEXT("Red Mesa Rivals")
		&& Request.OfferedTeam == TEXT("Sundale Sparks")
		&& Request.AcceptedUnixSeconds == UpcomingQaAcceptedUnixSeconds
		&& Request.LockUnixSeconds == UpcomingQaLockUnixSeconds
		&& Lock.LockCommandId == UpcomingQaLockCommandId
		&& Lock.RequestCommandId == UpcomingQaRequestCommandId
		&& Lock.AuthoritativeGameStartUnixSeconds == UpcomingQaLockUnixSeconds
		&& Lock.LockUnixSeconds == UpcomingQaLockUnixSeconds
		&& Canceled.CancellationCommandId == UpcomingQaCancellationCommandId
		&& Canceled.CancellationEvidenceId == UpcomingQaCancellationEvidenceId
		&& Canceled.AuthoritativeCancellationUnixSeconds == UpcomingQaCancellationUnixSeconds
		&& Decision.VoidDecisionCommandId == UpcomingQaVoidDecisionCommandId
		&& Finalization.FinalizationCommandId == UpcomingQaVoidFinalizationCommandId;
	if (!bQaProjection
		|| !StakeEntry
		|| !RefundEntry
		|| Request.Stake != 40
		|| Request.Status != AcceptedPendingLockStatus
		|| Request.AcceptedUnixSeconds <= 0
		|| Request.AcceptedUnixSeconds >= Request.LockUnixSeconds
		|| Request.LockUnixSeconds != Lock.LockUnixSeconds
		|| StakeEntry->Sequence != 2
		|| StakeEntry->Delta != -40
		|| StakeEntry->Reason != MatchWinnerStakeReason
		|| StakeEntry->BalanceAfter != 60
		|| Lock.RequestCommandId != Request.RequestCommandId
		|| (!bCanceledQaChain && !bUpcomingQaChain)
		|| Lock.AuthoritativeGameStartUnixSeconds != Lock.LockUnixSeconds
		|| Lock.Decision != MatchWinnerLockedDecision
		|| Canceled.RequestCommandId != Request.RequestCommandId
		|| Canceled.LockCommandId != Lock.LockCommandId
		|| Canceled.SeasonNumber != Lock.SeasonNumber
		|| Canceled.GameNumber != Lock.GameNumber
		|| Canceled.DispositionSchema != MatchWinnerCanceledGameSchema
		|| Canceled.DispositionVersion != MatchWinnerCanceledGameVersion
		|| Canceled.AuthoritativeCancellationUnixSeconds < Lock.AuthoritativeGameStartUnixSeconds
		|| Canceled.ReasonCode != MatchWinnerCanceledGameReason
		|| Canceled.Status != MatchWinnerClosedCanceledStatus
		|| Decision.CancellationCommandId != Canceled.CancellationCommandId
		|| Decision.CancellationEvidenceId != Canceled.CancellationEvidenceId
		|| Decision.RequestCommandId != Request.RequestCommandId
		|| Decision.LockCommandId != Lock.LockCommandId
		|| Decision.SeasonNumber != Lock.SeasonNumber
		|| Decision.GameNumber != Lock.GameNumber
		|| Decision.DecisionSchema != MatchWinnerVoidDecisionSchema
		|| Decision.DecisionVersion != MatchWinnerVoidDecisionVersion
		|| Decision.OfferId != Request.OfferId
		|| Decision.OfferSchema != MatchWinnerOfferSchema
		|| Decision.OfferVersion != Request.OfferVersion
		|| Decision.SelectedTeam != Request.OfferedTeam
		|| Decision.Stake != Request.Stake
		|| Decision.CancellationReason != Canceled.ReasonCode
		|| Decision.Outcome != MatchWinnerVoidedOutcome
		|| Decision.RefundDue != 40
		|| Decision.Status != MatchWinnerDecidedVoidPendingRefundStatus
		|| Finalization.VoidDecisionCommandId != Decision.VoidDecisionCommandId
		|| Finalization.CancellationCommandId != Canceled.CancellationCommandId
		|| Finalization.CancellationEvidenceId != Canceled.CancellationEvidenceId
		|| Finalization.RequestCommandId != Request.RequestCommandId
		|| Finalization.LockCommandId != Lock.LockCommandId
		|| Finalization.SeasonNumber != Lock.SeasonNumber
		|| Finalization.GameNumber != Lock.GameNumber
		|| Finalization.FinalizationSchema != MatchWinnerVoidFinalizationSchema
		|| Finalization.FinalizationVersion != MatchWinnerVoidFinalizationVersion
		|| Finalization.OfferId != Request.OfferId
		|| Finalization.OfferSchema != MatchWinnerOfferSchema
		|| Finalization.OfferVersion != Request.OfferVersion
		|| Finalization.SelectedTeam != Request.OfferedTeam
		|| Finalization.Stake != Request.Stake
		|| Finalization.CancellationReason != Canceled.ReasonCode
		|| Finalization.Outcome != Decision.Outcome
		|| Finalization.RefundDue != Decision.RefundDue
		|| Finalization.RefundLedgerCommandId != Finalization.FinalizationCommandId
		|| Finalization.Status != MatchWinnerSettledVoidStatus
		|| Finalization.RefundApplied != 40
		|| Finalization.ObservedLedgerEntryCount != 3
		|| Finalization.ObservedFinalBalance != 100
		|| RefundEntry->Sequence != 3
		|| RefundEntry->Delta != 40
		|| RefundEntry->Reason != MatchWinnerRefundReason
		|| RefundEntry->BalanceAfter != 100
		|| Ledger.GetEntries().Num() != 3
		|| Ledger.GetBalance() != 100)
	{
		OutError = TEXT("The Match Winner void reconciliation does not match the exact finalized chain.");
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
	Root->SetStringField(TEXT("offer_schema"), Decision.OfferSchema);
	Root->SetStringField(TEXT("offer_version"), Request.OfferVersion);
	Root->SetStringField(TEXT("request_command_id"), Request.RequestCommandId);
	Root->SetStringField(TEXT("selected_team"), Request.OfferedTeam);
	Root->SetNumberField(TEXT("stake"), static_cast<double>(Request.Stake));
	Root->SetNumberField(TEXT("request_accepted_unix"), static_cast<double>(Request.AcceptedUnixSeconds));
	Root->SetNumberField(TEXT("request_lock_unix"), static_cast<double>(Request.LockUnixSeconds));
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
	Root->SetStringField(TEXT("lock_decision"), bUpcomingQaChain ? TEXT("locked") : Lock.Decision.ToString());
	Root->SetStringField(TEXT("cancellation_command_id"), Canceled.CancellationCommandId);
	Root->SetStringField(TEXT("cancellation_evidence_id"), Canceled.CancellationEvidenceId);
	Root->SetStringField(TEXT("cancellation_request_command_id"), Canceled.RequestCommandId);
	Root->SetStringField(TEXT("cancellation_lock_command_id"), Canceled.LockCommandId);
	Root->SetStringField(TEXT("cancellation_schema"), Canceled.DispositionSchema);
	Root->SetStringField(TEXT("cancellation_version"), Canceled.DispositionVersion);
	Root->SetNumberField(TEXT("cancellation_unix"), static_cast<double>(Canceled.AuthoritativeCancellationUnixSeconds));
	Root->SetStringField(TEXT("cancellation_reason"), Canceled.ReasonCode.ToString());
	Root->SetStringField(TEXT("cancellation_status"), Canceled.Status.ToString());
	Root->SetStringField(TEXT("decision_command_id"), Decision.VoidDecisionCommandId);
	Root->SetStringField(TEXT("decision_cancellation_command_id"), Decision.CancellationCommandId);
	Root->SetStringField(TEXT("decision_cancellation_evidence_id"), Decision.CancellationEvidenceId);
	Root->SetStringField(TEXT("decision_request_command_id"), Decision.RequestCommandId);
	Root->SetStringField(TEXT("decision_lock_command_id"), Decision.LockCommandId);
	Root->SetStringField(TEXT("decision_schema"), Decision.DecisionSchema);
	Root->SetStringField(TEXT("decision_version"), Decision.DecisionVersion);
	Root->SetStringField(TEXT("decision_offer_id"), Decision.OfferId);
	Root->SetStringField(TEXT("decision_offer_schema"), Decision.OfferSchema);
	Root->SetStringField(TEXT("decision_offer_version"), Decision.OfferVersion);
	Root->SetStringField(TEXT("decision_status"), Decision.Status.ToString());
	Root->SetStringField(TEXT("outcome"), Decision.Outcome.ToString());
	Root->SetNumberField(TEXT("refund_due"), static_cast<double>(Decision.RefundDue));
	Root->SetStringField(TEXT("refund_ledger_command_id"), RefundEntry->CommandId);
	Root->SetNumberField(TEXT("refund_sequence"), static_cast<double>(RefundEntry->Sequence));
	Root->SetNumberField(TEXT("refund_delta"), static_cast<double>(RefundEntry->Delta));
	Root->SetStringField(TEXT("refund_reason"), RefundEntry->Reason.ToString());
	Root->SetNumberField(TEXT("refund_balance_after"), static_cast<double>(RefundEntry->BalanceAfter));
	Root->SetStringField(TEXT("finalization_command_id"), Finalization.FinalizationCommandId);
	Root->SetStringField(TEXT("finalization_decision_command_id"), Finalization.VoidDecisionCommandId);
	Root->SetStringField(TEXT("finalization_cancellation_command_id"), Finalization.CancellationCommandId);
	Root->SetStringField(TEXT("finalization_cancellation_evidence_id"), Finalization.CancellationEvidenceId);
	Root->SetStringField(TEXT("finalization_request_command_id"), Finalization.RequestCommandId);
	Root->SetStringField(TEXT("finalization_lock_command_id"), Finalization.LockCommandId);
	Root->SetStringField(TEXT("finalization_schema"), Finalization.FinalizationSchema);
	Root->SetStringField(TEXT("finalization_version"), Finalization.FinalizationVersion);
	Root->SetStringField(TEXT("finalization_offer_id"), Finalization.OfferId);
	Root->SetStringField(TEXT("finalization_offer_schema"), Finalization.OfferSchema);
	Root->SetStringField(TEXT("finalization_offer_version"), Finalization.OfferVersion);
	Root->SetStringField(TEXT("finalization_status"), Finalization.Status.ToString());
	Root->SetNumberField(TEXT("refund_applied"), static_cast<double>(Finalization.RefundApplied));
	Root->SetNumberField(TEXT("ledger_entry_count"), Ledger.GetEntries().Num());
	Root->SetNumberField(TEXT("final_balance"), static_cast<double>(Ledger.GetBalance()));
	Root->SetNumberField(TEXT("net"), static_cast<double>(StakeEntry->Delta + RefundEntry->Delta));

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
	if (!FJsonSerializer::Serialize(Root, Writer))
	{
		OutError = TEXT("The Match Winner void reconciliation projection could not be serialized.");
		return false;
	}
	const FString Path = GetMatchWinnerReconciliationPath(bQaProjection);
	IFileManager::Get().MakeDirectory(*FPaths::GetPath(Path), true);
	const FString TemporaryPath = Path + TEXT(".tmp");
	if (!FFileHelper::SaveStringToFile(Json, *TemporaryPath)
		|| !IFileManager::Get().Move(*Path, *TemporaryPath, true, true, false, true))
	{
		IFileManager::Get().Delete(*TemporaryPath, false, true, true);
		OutError = TEXT("The Match Winner void reconciliation projection could not be written atomically.");
		return false;
	}
	OutError.Reset();
	return true;
}

bool WriteMatchWinnerReconciliationFromValidatedState(
	const FOddsWellOddsBucksLedger& Ledger,
	const TArray<FOddsWellMatchWinnerRequestRecord>& Requests,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const TArray<FOddsWellMatchWinnerResultLinkRecord>& Results,
	const TArray<FOddsWellMatchWinnerSettlementDecisionRecord>& Decisions,
	const TArray<FOddsWellMatchWinnerLossFinalizationRecord>& LossFinalizations,
	const TArray<FOddsWellMatchWinnerWinFinalizationRecord>& WinFinalizations,
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& CanceledGames,
	const TArray<FOddsWellMatchWinnerVoidDecisionRecord>& VoidDecisions,
	const TArray<FOddsWellMatchWinnerVoidFinalizationRecord>& VoidFinalizations,
	const bool bQaProjection,
	FString& OutError)
{
	if (!CanceledGames.IsEmpty() || !VoidDecisions.IsEmpty() || !VoidFinalizations.IsEmpty())
	{
		if (!Results.IsEmpty()
			|| !Decisions.IsEmpty()
			|| !LossFinalizations.IsEmpty()
			|| !WinFinalizations.IsEmpty())
		{
			OutError = TEXT("The Match Winner reconciliation cannot mix void and normal outcome evidence.");
			return false;
		}
		return WriteMatchWinnerVoidReconciliationFromValidatedState(
			Ledger,
			Requests,
			Locks,
			CanceledGames,
			VoidDecisions,
			VoidFinalizations,
			bQaProjection,
			OutError);
	}
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
	const TArray<FOddsWellMatchWinnerCanceledGameRecord>& MatchWinnerCanceledGames,
	const TArray<FOddsWellMatchWinnerVoidDecisionRecord>& MatchWinnerVoidDecisions,
	const bool bQaSlot,
	FString& OutError,
	const TArray<FOddsWellMatchWinnerVoidFinalizationRecord>* MatchWinnerVoidFinalizations = nullptr)
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
	Record->MatchWinnerCanceledGames = MatchWinnerCanceledGames;
	Record->MatchWinnerVoidDecisions = MatchWinnerVoidDecisions;
	if (MatchWinnerVoidFinalizations)
	{
		Record->MatchWinnerVoidFinalizations = *MatchWinnerVoidFinalizations;
	}
	else if (const UOddsWellOddsBucksSaveGame* Existing = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex)))
	{
		Record->MatchWinnerVoidFinalizations = Existing->SchemaVersion >= 11
			? Existing->MatchWinnerVoidFinalizations
			: TArray<FOddsWellMatchWinnerVoidFinalizationRecord>();
	}
	FOddsWellOddsBucksLedger Validated;
	int64 ValidatedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> ValidatedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> ValidatedLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> ValidatedResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> ValidatedDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> ValidatedFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> ValidatedWinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> ValidatedCanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> ValidatedVoidDecisions;
	bool bNeedsMigration = false;
	if (!ValidateOddsBucksSave(Record, Validated, ValidatedNextJobPayout, ValidatedRequests, ValidatedLocks, ValidatedResultLinks, ValidatedDecisions, ValidatedFinalizations, ValidatedWinFinalizations, ValidatedCanceledGames, ValidatedVoidDecisions, bNeedsMigration, OutError))
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord>& OutMatchWinnerCanceledGames,
	TArray<FOddsWellMatchWinnerVoidDecisionRecord>& OutMatchWinnerVoidDecisions,
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
		OutMatchWinnerCanceledGames.Reset();
		OutMatchWinnerVoidDecisions.Reset();
		bOutNeedsMigration = false;
		OutError.Reset();
		return true;
	}
	const bool bValid = ValidateOddsBucksSave(
		UGameplayStatics::LoadGameFromSlot(Slot, OddsBucksUserIndex),
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		OutMatchWinnerResultLinks,
		OutMatchWinnerSettlementDecisions,
		OutMatchWinnerLossFinalizations,
		OutMatchWinnerWinFinalizations,
		OutMatchWinnerCanceledGames,
		OutMatchWinnerVoidDecisions,
		bOutNeedsMigration,
		OutError);
	if (!bValid)
	{
		IFileManager::Get().Delete(*GetMatchWinnerReconciliationPath(bQaSlot), false, true, true);
	}
	return bValid;
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> ExistingCanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> ExistingVoidDecisions;
	if (UGameplayStatics::DoesSaveGameExist(GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex))
	{
		FOddsWellOddsBucksLedger ExistingLedger;
		int64 ExistingNextJobPayout = 0;
		bool bFound = false;
		bool bNeedsMigration = false;
		if (!LoadOddsWellOddsBucksStateRaw(bQaSlot, ExistingLedger, ExistingNextJobPayout, ExistingRequests, ExistingLocks, ExistingResultLinks, ExistingDecisions, ExistingFinalizations, ExistingWinFinalizations, ExistingCanceledGames, ExistingVoidDecisions, bFound, bNeedsMigration, OutError))
		{
			return false;
		}
	}
	return SaveOddsWellOddsBucksState(Ledger, NextJobPayoutUnixSeconds, ExistingRequests, ExistingLocks, ExistingResultLinks, ExistingDecisions, ExistingFinalizations, ExistingWinFinalizations, ExistingCanceledGames, ExistingVoidDecisions, bQaSlot, OutError);
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> VoidFinalizations;
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
		CanceledGames,
		VoidDecisions,
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
		CanceledGames,
		VoidDecisions,
		bQaSlot,
		OutError))
	{
		IFileManager::Get().Delete(*ProjectionPath, false, true, true);
		return false;
	}
	if (bOutFound && !LoadOddsWellMatchWinnerVoidFinalizations(bQaSlot, VoidFinalizations, bOutFound, OutError))
	{
		IFileManager::Get().Delete(*ProjectionPath, false, true, true);
		return false;
	}
	if (!bOutFound || (OutMatchWinnerLossFinalizations.IsEmpty() && OutMatchWinnerWinFinalizations.IsEmpty() && VoidFinalizations.IsEmpty()))
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
		CanceledGames,
		VoidDecisions,
		VoidFinalizations,
		bQaSlot,
		OutError))
	{
		IFileManager::Get().Delete(*ProjectionPath, false, true, true);
		return false;
	}
	return true;
}

bool LoadOddsWellMatchWinnerCanceledGames(
	const bool bQaSlot,
	TArray<FOddsWellMatchWinnerCanceledGameRecord>& OutCanceledGames,
	bool& bOutFound,
	FString& OutError)
{
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		OutCanceledGames,
		VoidDecisions,
		bOutFound,
		bNeedsMigration,
		OutError))
	{
		return false;
	}
	return !bNeedsMigration || SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		WinFinalizations,
		OutCanceledGames,
		VoidDecisions,
		bQaSlot,
		OutError);
}

bool LoadOddsWellMatchWinnerVoidDecisions(
	const bool bQaSlot,
	TArray<FOddsWellMatchWinnerVoidDecisionRecord>& OutVoidDecisions,
	bool& bOutFound,
	FString& OutError)
{
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
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
		CanceledGames,
		OutVoidDecisions,
		bOutFound,
		bNeedsMigration,
		OutError))
	{
		return false;
	}
	return !bNeedsMigration || SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		WinFinalizations,
		CanceledGames,
		OutVoidDecisions,
		bQaSlot,
		OutError);
}

bool LoadOddsWellMatchWinnerVoidFinalizations(
	const bool bQaSlot,
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord>& OutVoidFinalizations,
	bool& bOutFound,
	FString& OutError)
{
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	if (!LoadOddsWellMatchWinnerVoidDecisions(bQaSlot, VoidDecisions, bOutFound, OutError))
	{
		return false;
	}
	OutVoidFinalizations.Reset();
	if (!bOutFound)
	{
		OutError.Reset();
		return true;
	}
	const UOddsWellOddsBucksSaveGame* Record = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex));
	if (!Record || Record->SchemaVersion != OddsBucksSchemaVersion)
	{
		OutError = TEXT("The Match Winner void-finalization state could not be loaded after validation.");
		return false;
	}
	OutVoidFinalizations = Record->MatchWinnerVoidFinalizations;
	OutError.Reset();
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
	const FOddsWellMatchWinnerSelection* Selected =
		Offer.Selections.FindByPredicate(
			[&OfferedTeam](const FOddsWellMatchWinnerSelection& Selection)
			{
				return Selection.Team == OfferedTeam;
			});
	if (!Selected)
	{
		OutError = TEXT("The Match Winner request does not match an offered selection.");
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
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
		const bool bExactCurrentEvidence =
			Existing->EvidenceVersion == MatchWinnerRequestEvidenceVersion
			&& Existing->OfferSchema == Offer.Schema
			&& Existing->Market == Offer.Market
			&& Existing->Currency == Offer.Currency
			&& Existing->SourcePredictionVersion == Offer.SourcePredictionVersion
			&& Existing->SourceSnapshotVersion == Offer.SourceSnapshotVersion
			&& Existing->SourceModel == Offer.SourceModel
			&& Existing->SourceCommitmentSha256 == Offer.SourceCommitmentSha256
			&& Existing->SelectedWinProbabilityE8 == Selected->WinProbabilityE8
			&& Existing->SelectedDecimalOddsE4 == Selected->DecimalOddsE4
			&& Existing->PayoutFormula == Offer.PayoutFormula
			&& Existing->GrossReturn
				== Stake * MatchWinnerProbabilityScale / Selected->WinProbabilityE8;
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
			&& Existing->Status == AcceptedPendingLockStatus
			&& (Existing->EvidenceVersion == 0 || bExactCurrentEvidence);
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
	CandidateRecord.EvidenceVersion = MatchWinnerRequestEvidenceVersion;
	CandidateRecord.RequestCommandId = RequestCommandId;
	CandidateRecord.StakeLedgerCommandId = RequestCommandId;
	CandidateRecord.OfferId = Offer.OfferId;
	CandidateRecord.OfferVersion = Offer.OfferVersion;
	CandidateRecord.OfferSchema = Offer.Schema;
	CandidateRecord.Market = Offer.Market;
	CandidateRecord.Currency = Offer.Currency;
	CandidateRecord.SourcePredictionVersion = Offer.SourcePredictionVersion;
	CandidateRecord.SourceSnapshotVersion = Offer.SourceSnapshotVersion;
	CandidateRecord.SourceModel = Offer.SourceModel;
	CandidateRecord.SourceCommitmentSha256 = Offer.SourceCommitmentSha256;
	CandidateRecord.SeasonNumber = Offer.SeasonNumber;
	CandidateRecord.GameNumber = Offer.GameNumber;
	CandidateRecord.HomeTeam = Offer.HomeTeam;
	CandidateRecord.AwayTeam = Offer.AwayTeam;
	CandidateRecord.OfferedTeam = OfferedTeam;
	CandidateRecord.SelectedWinProbabilityE8 = Selected->WinProbabilityE8;
	CandidateRecord.SelectedDecimalOddsE4 = Selected->DecimalOddsE4;
	CandidateRecord.Stake = Stake;
	CandidateRecord.PayoutFormula = Offer.PayoutFormula;
	CandidateRecord.GrossReturn =
		Stake * MatchWinnerProbabilityScale / Selected->WinProbabilityE8;
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
		CanceledGames,
		VoidDecisions,
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

EOddsWellMatchWinnerRequestResult AcceptOddsWellUpcomingQaMatchWinnerRequest(
	const FOddsWellMatchWinnerOffer& Offer,
	const FString& RequestCommandId,
	const FString& OfferedTeam,
	const int64 Stake,
	const int64 AcceptedUnixSeconds,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	FOddsWellMatchWinnerOffer Expected;
	if (!BuildUpcomingQaMatchWinnerOffer(Expected, OutError)
		|| Offer.OfferId != Expected.OfferId
		|| !ValidateMatchWinnerOffer(Offer, OutError))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("Only the exact isolated upcoming QA offer may be accepted.");
		}
		OutRecord = FOddsWellMatchWinnerRequestRecord();
		OutBalance = 0;
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	return AcceptOddsWellMatchWinnerRequest(
		Offer,
		RequestCommandId,
		OfferedTeam,
		Stake,
		AcceptedUnixSeconds,
		true,
		OutRecord,
		OutBalance,
		OutError);
}

bool RunOddsWellUpcomingQaMatchWinnerAudit(
	int32& OutLedgerEntries,
	int32& OutRequests,
	int64& OutBalance,
	FString& OutError)
{
	FOddsWellOddsBucksLedger BeforeLedger;
	int64 BeforeNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> BeforeRequests;
	bool bFound = false;
	if (!LoadOddsWellOddsBucksState(true, BeforeLedger, BeforeNextJobPayout, BeforeRequests, bFound, OutError)
		|| !bFound
		|| BeforeLedger.GetEntries().Num() != 2
		|| BeforeLedger.GetBalance() != 60
		|| BeforeRequests.Num() != 1)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The isolated upcoming QA request baseline is not exact.");
		}
		return false;
	}

	FOddsWellMatchWinnerOffer Offer;
	if (!BuildUpcomingQaMatchWinnerOffer(Offer, OutError))
	{
		return false;
	}
	FOddsWellMatchWinnerRequestRecord Record;
	int64 ObservedBalance = 0;
	if (AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			UpcomingQaRequestCommandId,
			Offer.HomeTeam,
			40,
			UpcomingQaLockUnixSeconds,
			Record,
			ObservedBalance,
			OutError) != EOddsWellMatchWinnerRequestResult::Duplicate
		|| Record.AcceptedUnixSeconds != UpcomingQaAcceptedUnixSeconds
		|| Record.AcceptedUnixSeconds >= Record.LockUnixSeconds
		|| ObservedBalance != 60)
	{
		OutError = TEXT("The exact cold retry was not idempotent.");
		return false;
	}

	auto Reject = [&Record, &ObservedBalance, &OutError](
		const FOddsWellMatchWinnerOffer& Attempt,
		const FString& CommandId,
		const FString& Team,
		const int64 Stake,
		const int64 AcceptedAt)
	{
		return AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Attempt,
			CommandId,
			Team,
			Stake,
			AcceptedAt,
			Record,
			ObservedBalance,
			OutError) == EOddsWellMatchWinnerRequestResult::Rejected;
	};

	FOddsWellMatchWinnerOffer Stale = Offer;
	Stale.OfferVersion = TEXT("basketball-match-winner-odds-v0");
	FOddsWellMatchWinnerOffer Tampered = Offer;
	Tampered.Selections[0].WinProbabilityE8++;
	FString CompletedOfferError;
	const FOddsWellMatchWinnerOffer CompletedH16 = BuildCompletedH16MatchWinnerOffer();
	if (!ValidateMatchWinnerOffer(CompletedH16, CompletedOfferError)
		|| !Reject(Stale, TEXT("qa:h17:reject:stale"), Stale.HomeTeam, 10, UpcomingQaAcceptedUnixSeconds)
		|| !Reject(Tampered, TEXT("qa:h17:reject:tampered"), Tampered.HomeTeam, 10, UpcomingQaAcceptedUnixSeconds)
		|| !Reject(Offer, TEXT("qa:h17:reject:team"), TEXT("Not Offered"), 10, UpcomingQaAcceptedUnixSeconds)
		|| !Reject(Offer, TEXT("qa:h17:reject:stake"), Offer.HomeTeam, 15, UpcomingQaAcceptedUnixSeconds)
		|| !Reject(Offer, TEXT("qa:h17:reject:late"), Offer.HomeTeam, 10, Offer.LockUnixSeconds)
		|| !Reject(Offer, UpcomingQaRequestCommandId, Offer.HomeTeam, 50, UpcomingQaAcceptedUnixSeconds)
		|| !Reject(CompletedH16, TEXT("qa:h17:reject:completed-h16"), CompletedH16.HomeTeam, 10, UpcomingQaAcceptedUnixSeconds)
		|| !Reject(Offer, TEXT("qa:h17:reject:balance"), Offer.AwayTeam, 100, UpcomingQaAcceptedUnixSeconds))
	{
		if (OutError.IsEmpty())
		{
			OutError = CompletedOfferError.IsEmpty()
				? TEXT("An isolated upcoming QA rejection invariant failed.")
				: CompletedOfferError;
		}
		return false;
	}

	FOddsWellOddsBucksLedger AfterLedger;
	int64 AfterNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> AfterRequests;
	if (!LoadOddsWellOddsBucksState(true, AfterLedger, AfterNextJobPayout, AfterRequests, bFound, OutError)
		|| !bFound
		|| AfterNextJobPayout != BeforeNextJobPayout
		|| AfterLedger.GetEntries().Num() != BeforeLedger.GetEntries().Num()
		|| AfterLedger.GetBalance() != BeforeLedger.GetBalance()
		|| AfterRequests.Num() != BeforeRequests.Num())
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("A rejected isolated upcoming QA request mutated persisted state.");
		}
		return false;
	}
	OutLedgerEntries = AfterLedger.GetEntries().Num();
	OutRequests = AfterRequests.Num();
	OutBalance = AfterLedger.GetBalance();
	OutError.Reset();
	return true;
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
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
		CanceledGames,
		VoidDecisions,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	OutRecord = MoveTemp(CandidateRecord);
	OutError.Reset();
	return EOddsWellMatchWinnerLockResult::Locked;
}

namespace
{
bool LoadExactUpcomingQaLockState(
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutLocks,
	FString& OutError,
	TArray<FOddsWellMatchWinnerCanceledGameRecord>* OutCanceledGames = nullptr,
	TArray<FOddsWellMatchWinnerVoidDecisionRecord>* OutVoidDecisions = nullptr,
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord>* OutVoidFinalizations = nullptr)
{
	TArray<FOddsWellMatchWinnerResultLinkRecord> ResultLinks;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	bool bFound = false;
	bool bNeedsMigration = false;
	const UOddsWellOddsBucksSaveGame* Save = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	FOddsWellMatchWinnerOffer Offer;
	const bool bHasVoidFinalization =
		OutVoidFinalizations && Save && Save->MatchWinnerVoidFinalizations.Num() == 1;
	if (!LoadOddsWellOddsBucksStateRaw(
			true,
			OutLedger,
			OutNextJobPayoutUnixSeconds,
			OutRequests,
			OutLocks,
			ResultLinks,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			CanceledGames,
			VoidDecisions,
			bFound,
			bNeedsMigration,
			OutError)
		|| !bFound
		|| bNeedsMigration
		|| !Save
		|| Save->SchemaVersion != OddsBucksSchemaVersion
		|| !BuildUpcomingQaMatchWinnerOffer(Offer, OutError)
		|| OutLedger.GetEntries().Num() != (bHasVoidFinalization ? 3 : 2)
		|| OutLedger.GetBalance() != (bHasVoidFinalization ? 100 : 60)
		|| OutNextJobPayoutUnixSeconds != UpcomingQaLockUnixSeconds
		|| OutRequests.Num() != 1
		|| OutLocks.Num() > 1
		|| !ResultLinks.IsEmpty()
		|| !Decisions.IsEmpty()
		|| !LossFinalizations.IsEmpty()
		|| !WinFinalizations.IsEmpty()
		|| (!OutCanceledGames && !CanceledGames.IsEmpty())
		|| (OutCanceledGames && CanceledGames.Num() > 1)
		|| (!OutVoidDecisions && !VoidDecisions.IsEmpty())
		|| (OutVoidDecisions && VoidDecisions.Num() > 1)
		|| (!OutVoidFinalizations && !Save->MatchWinnerVoidFinalizations.IsEmpty())
		|| (OutVoidFinalizations && Save->MatchWinnerVoidFinalizations.Num() > 1))
	{
		OutError = TEXT("The isolated upcoming QA lock baseline is not exact.");
		return false;
	}

	const FOddsWellOddsBucksEntry& Credit = OutLedger.GetEntries()[0];
	const FOddsWellOddsBucksEntry& Debit = OutLedger.GetEntries()[1];
	const FOddsWellMatchWinnerRequestRecord& Request = OutRequests[0];
	if (Credit.Sequence != 1
		|| Credit.CommandId != FirstJobCommandId
		|| Credit.Delta != FirstJobPayout
		|| Credit.BalanceAfter != FirstJobPayout
		|| Credit.Reason != FirstJobReason
		|| Debit.Sequence != 2
		|| Debit.CommandId != UpcomingQaRequestCommandId
		|| Debit.Delta != -40
		|| Debit.BalanceAfter != 60
		|| Debit.Reason != MatchWinnerStakeReason
		|| Request.RequestCommandId != UpcomingQaRequestCommandId
		|| Request.StakeLedgerCommandId != UpcomingQaRequestCommandId
		|| Request.OfferId != Offer.OfferId
		|| Request.OfferVersion != Offer.OfferVersion
		|| Request.SeasonNumber != UpcomingQaSeasonNumber
		|| Request.GameNumber != UpcomingQaGameNumber
		|| Request.HomeTeam != Offer.HomeTeam
		|| Request.AwayTeam != Offer.AwayTeam
		|| Request.OfferedTeam != Offer.HomeTeam
		|| Request.Stake != 40
		|| Request.AcceptedUnixSeconds != UpcomingQaAcceptedUnixSeconds
		|| Request.LockUnixSeconds != UpcomingQaLockUnixSeconds
		|| Request.Status != AcceptedPendingLockStatus)
	{
		OutError = TEXT("The isolated upcoming QA request, offer, debit, or cooldown changed before lock.");
		return false;
	}
	if (OutLocks.Num() == 1)
	{
		const FOddsWellMatchWinnerLockRecord& Lock = OutLocks[0];
		if (Lock.LockCommandId != UpcomingQaLockCommandId
			|| Lock.RequestCommandId != UpcomingQaRequestCommandId
			|| Lock.SeasonNumber != UpcomingQaSeasonNumber
			|| Lock.GameNumber != UpcomingQaGameNumber
			|| Lock.AuthoritativeGameStartUnixSeconds != UpcomingQaLockUnixSeconds
			|| Lock.LockUnixSeconds != UpcomingQaLockUnixSeconds
			|| Lock.Decision != MatchWinnerLockedDecision)
		{
			OutError = TEXT("The isolated upcoming QA lock evidence is not exact.");
			return false;
		}
	}
	if (OutCanceledGames && CanceledGames.Num() == 1)
	{
		const FOddsWellMatchWinnerCanceledGameRecord& Canceled = CanceledGames[0];
		if (Canceled.CancellationCommandId != UpcomingQaCancellationCommandId
			|| Canceled.CancellationEvidenceId != UpcomingQaCancellationEvidenceId
			|| Canceled.RequestCommandId != UpcomingQaRequestCommandId
			|| Canceled.LockCommandId != UpcomingQaLockCommandId
			|| Canceled.DispositionSchema != MatchWinnerCanceledGameSchema
			|| Canceled.DispositionVersion != MatchWinnerCanceledGameVersion
			|| Canceled.SeasonNumber != UpcomingQaSeasonNumber
			|| Canceled.GameNumber != UpcomingQaGameNumber
			|| Canceled.AuthoritativeCancellationUnixSeconds != UpcomingQaCancellationUnixSeconds
			|| Canceled.ReasonCode != MatchWinnerCanceledGameReason
			|| Canceled.Status != MatchWinnerClosedCanceledStatus)
		{
			OutError = TEXT("The isolated upcoming QA cancellation evidence is not exact.");
			return false;
		}
	}
	if (OutVoidDecisions && VoidDecisions.Num() == 1)
	{
		const FOddsWellMatchWinnerVoidDecisionRecord& Decision = VoidDecisions[0];
		if (CanceledGames.Num() != 1
			|| Decision.VoidDecisionCommandId != UpcomingQaVoidDecisionCommandId
			|| Decision.CancellationCommandId != UpcomingQaCancellationCommandId
			|| Decision.CancellationEvidenceId != UpcomingQaCancellationEvidenceId
			|| Decision.RequestCommandId != UpcomingQaRequestCommandId
			|| Decision.LockCommandId != UpcomingQaLockCommandId
			|| Decision.DecisionSchema != MatchWinnerVoidDecisionSchema
			|| Decision.DecisionVersion != MatchWinnerVoidDecisionVersion
			|| Decision.OfferId != Offer.OfferId
			|| Decision.OfferSchema != MatchWinnerOfferSchema
			|| Decision.OfferVersion != Offer.OfferVersion
			|| Decision.SeasonNumber != UpcomingQaSeasonNumber
			|| Decision.GameNumber != UpcomingQaGameNumber
			|| Decision.SelectedTeam != Offer.HomeTeam
			|| Decision.Stake != 40
			|| Decision.CancellationReason != MatchWinnerCanceledGameReason
			|| Decision.Outcome != MatchWinnerVoidedOutcome
			|| Decision.RefundDue != 40
			|| Decision.Status != MatchWinnerDecidedVoidPendingRefundStatus)
		{
			OutError = TEXT("The isolated upcoming QA void/refund-due decision is not exact.");
			return false;
		}
	}
	if (bHasVoidFinalization)
	{
		const FOddsWellOddsBucksEntry& Refund = OutLedger.GetEntries()[2];
		const FOddsWellMatchWinnerVoidFinalizationRecord& Finalization =
			Save->MatchWinnerVoidFinalizations[0];
		if (CanceledGames.Num() != 1
			|| VoidDecisions.Num() != 1
			|| Refund.Sequence != 3
			|| Refund.CommandId != UpcomingQaVoidFinalizationCommandId
			|| Refund.Delta != 40
			|| Refund.BalanceAfter != 100
			|| Refund.Reason != MatchWinnerRefundReason
			|| Finalization.FinalizationCommandId != UpcomingQaVoidFinalizationCommandId
			|| Finalization.VoidDecisionCommandId != UpcomingQaVoidDecisionCommandId
			|| Finalization.CancellationCommandId != UpcomingQaCancellationCommandId
			|| Finalization.CancellationEvidenceId != UpcomingQaCancellationEvidenceId
			|| Finalization.RequestCommandId != UpcomingQaRequestCommandId
			|| Finalization.LockCommandId != UpcomingQaLockCommandId
			|| Finalization.FinalizationSchema != MatchWinnerVoidFinalizationSchema
			|| Finalization.FinalizationVersion != MatchWinnerVoidFinalizationVersion
			|| Finalization.OfferId != Offer.OfferId
			|| Finalization.OfferSchema != MatchWinnerOfferSchema
			|| Finalization.OfferVersion != Offer.OfferVersion
			|| Finalization.SeasonNumber != UpcomingQaSeasonNumber
			|| Finalization.GameNumber != UpcomingQaGameNumber
			|| Finalization.SelectedTeam != Offer.HomeTeam
			|| Finalization.Stake != 40
			|| Finalization.CancellationReason != MatchWinnerCanceledGameReason
			|| Finalization.Outcome != MatchWinnerVoidedOutcome
			|| Finalization.RefundDue != 40
			|| Finalization.RefundApplied != 40
			|| Finalization.RefundLedgerCommandId != UpcomingQaVoidFinalizationCommandId
			|| Finalization.Status != MatchWinnerSettledVoidStatus
			|| Finalization.ObservedLedgerEntryCount != 3
			|| Finalization.ObservedFinalBalance != 100)
		{
			OutError = TEXT("The isolated upcoming QA refund finalization is not exact.");
			return false;
		}
	}
	if (OutCanceledGames)
	{
		*OutCanceledGames = MoveTemp(CanceledGames);
	}
	if (OutVoidDecisions)
	{
		*OutVoidDecisions = MoveTemp(VoidDecisions);
	}
	if (OutVoidFinalizations)
	{
		*OutVoidFinalizations = Save->MatchWinnerVoidFinalizations;
	}
	OutError.Reset();
	return true;
}
}

EOddsWellMatchWinnerLockResult LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	if (!LoadExactUpcomingQaLockState(Ledger, NextJobPayoutUnixSeconds, Requests, Locks, OutError))
	{
		OutRecord = FOddsWellMatchWinnerLockRecord();
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	return LockOddsWellMatchWinnerRequest(
		UpcomingQaRequestCommandId,
		UpcomingQaLockCommandId,
		UpcomingQaSeasonNumber,
		UpcomingQaGameNumber,
		UpcomingQaLockUnixSeconds,
		true,
		OutRecord,
		OutError);
}

bool RunOddsWellUpcomingQaMatchWinnerLockAudit(
	int32& OutLedgerEntries,
	int32& OutRequests,
	int32& OutLocks,
	int64& OutBalance,
	FString& OutError)
{
	TArray<uint8> BeforeBytes;
	if (!UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			BeforeBytes))
	{
		OutError = TEXT("The exact locked QA state could not be captured.");
		return false;
	}

	FOddsWellMatchWinnerLockRecord Record;
	if (LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Record, OutError)
			!= EOddsWellMatchWinnerLockResult::Duplicate
		|| Record.LockCommandId != UpcomingQaLockCommandId)
	{
		OutError = TEXT("The exact cold game-start lock retry was not idempotent.");
		return false;
	}

	auto Reject = [&Record, &OutError](
		const FString& RequestCommandId,
		const FString& LockCommandId,
		const int32 SeasonNumber,
		const int32 GameNumber,
		const int64 StartUnixSeconds)
	{
		return LockOddsWellMatchWinnerRequest(
			RequestCommandId,
			LockCommandId,
			SeasonNumber,
			GameNumber,
			StartUnixSeconds,
			true,
			Record,
			OutError) == EOddsWellMatchWinnerLockResult::Rejected;
	};
	if (!Reject(TEXT("qa:h19:unknown-request"), TEXT("qa:h19:reject:unknown"), UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaLockUnixSeconds)
		|| !Reject(UpcomingQaRequestCommandId, TEXT("qa:h19:reject:wrong-game"), UpcomingQaSeasonNumber, UpcomingQaGameNumber + 1, UpcomingQaLockUnixSeconds)
		|| !Reject(UpcomingQaRequestCommandId, TEXT("qa:h19:reject:early"), UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaLockUnixSeconds - 1)
		|| !Reject(UpcomingQaRequestCommandId, TEXT("qa:h19:reject:late"), UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaLockUnixSeconds + 1)
		|| !Reject(UpcomingQaRequestCommandId, UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber + 1, UpcomingQaLockUnixSeconds)
		|| !Reject(UpcomingQaRequestCommandId, TEXT("qa:h19:reject:second-lock"), UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaLockUnixSeconds)
		|| !Reject(TEXT("wager:match_winner:test-1"), TEXT("qa:h19:reject:completed-h16"), 1, 1, 2000000000)
		|| !Reject(UpcomingQaRequestCommandId, TEXT("qa:h19:reject:invented-time"), UpcomingQaSeasonNumber, UpcomingQaGameNumber, 2200000000))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("An isolated upcoming QA lock rejection invariant failed.");
		}
		return false;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<uint8> AfterBytes;
	if (!LoadExactUpcomingQaLockState(Ledger, NextJobPayoutUnixSeconds, Requests, Locks, OutError)
		|| Locks.Num() != 1
		|| !UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			AfterBytes)
		|| BeforeBytes != AfterBytes)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("A rejected isolated upcoming QA lock mutated persisted state.");
		}
		return false;
	}
	OutLedgerEntries = Ledger.GetEntries().Num();
	OutRequests = Requests.Num();
	OutLocks = Locks.Num();
	OutBalance = Ledger.GetBalance();
	OutError.Reset();
	return true;
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
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
		if (!IsSameMatchWinnerResultLink(*Existing, Candidate))
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
		|| (!IsExactSealedMatchWinnerResult(Candidate)
			&& !IsExactPrivateCanonicalMatchWinnerResult(Candidate)))
	{
		OutError = TEXT("The Match Winner result does not match an exact separately supported result contract, accepted request, and lock.");
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
		CanceledGames,
		VoidDecisions,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerResultLinkResult::Linked;
}

EOddsWellMatchWinnerCanceledGameResult RecordOddsWellMatchWinnerCanceledGame(
	const FString& CancellationCommandId,
	const FString& CancellationEvidenceId,
	const FString& RequestCommandId,
	const FString& LockCommandId,
	const FString& DispositionSchema,
	const FString& DispositionVersion,
	const int32 SeasonNumber,
	const int32 GameNumber,
	const int64 AuthoritativeCancellationUnixSeconds,
	const FName ReasonCode,
	const bool bQaSlot,
	FOddsWellMatchWinnerCanceledGameRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerCanceledGameRecord();
	if (!bQaSlot
		|| CancellationCommandId.TrimStartAndEnd().IsEmpty()
		|| CancellationEvidenceId.TrimStartAndEnd().IsEmpty()
		|| RequestCommandId.TrimStartAndEnd().IsEmpty()
		|| LockCommandId.TrimStartAndEnd().IsEmpty()
		|| CancellationCommandId == CancellationEvidenceId
		|| CancellationCommandId == RequestCommandId
		|| CancellationCommandId == LockCommandId
		|| DispositionSchema != MatchWinnerCanceledGameSchema
		|| DispositionVersion != MatchWinnerCanceledGameVersion
		|| SeasonNumber <= 0
		|| GameNumber <= 0
		|| (SeasonNumber == SealedResultSeasonNumber && GameNumber == SealedResultGameNumber)
		|| AuthoritativeCancellationUnixSeconds <= 0
		|| ReasonCode != MatchWinnerCanceledGameReason)
	{
		OutError = TEXT("The Match Winner canceled-game evidence is not the supported noncanonical QA contract.");
		return EOddsWellMatchWinnerCanceledGameResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerCanceledGameResult::Rejected;
	}

	FOddsWellMatchWinnerCanceledGameRecord Candidate;
	Candidate.CancellationCommandId = CancellationCommandId;
	Candidate.CancellationEvidenceId = CancellationEvidenceId;
	Candidate.RequestCommandId = RequestCommandId;
	Candidate.LockCommandId = LockCommandId;
	Candidate.DispositionSchema = DispositionSchema;
	Candidate.DispositionVersion = DispositionVersion;
	Candidate.SeasonNumber = SeasonNumber;
	Candidate.GameNumber = GameNumber;
	Candidate.AuthoritativeCancellationUnixSeconds = AuthoritativeCancellationUnixSeconds;
	Candidate.ReasonCode = ReasonCode;
	Candidate.Status = MatchWinnerClosedCanceledStatus;
	if (const FOddsWellMatchWinnerCanceledGameRecord* Existing = CanceledGames.FindByPredicate(
		[&CancellationCommandId](const FOddsWellMatchWinnerCanceledGameRecord& Canceled)
		{
			return Canceled.CancellationCommandId == CancellationCommandId;
		}))
	{
		const bool bExact = Existing->CancellationEvidenceId == Candidate.CancellationEvidenceId
			&& Existing->RequestCommandId == Candidate.RequestCommandId
			&& Existing->LockCommandId == Candidate.LockCommandId
			&& Existing->DispositionSchema == Candidate.DispositionSchema
			&& Existing->DispositionVersion == Candidate.DispositionVersion
			&& Existing->SeasonNumber == Candidate.SeasonNumber
			&& Existing->GameNumber == Candidate.GameNumber
			&& Existing->AuthoritativeCancellationUnixSeconds == Candidate.AuthoritativeCancellationUnixSeconds
			&& Existing->ReasonCode == Candidate.ReasonCode
			&& Existing->Status == Candidate.Status;
		if (!bExact)
		{
			OutError = TEXT("The Match Winner cancellation command was already used with different evidence.");
			return EOddsWellMatchWinnerCanceledGameResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerCanceledGameResult::Duplicate;
	}
	if (!CanceledGames.IsEmpty())
	{
		OutError = TEXT("The isolated Match Winner QA profile already has a canceled-game disposition.");
		return EOddsWellMatchWinnerCanceledGameResult::Rejected;
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
	const bool bHasResult = Results.ContainsByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerResultLinkRecord& Result)
		{
			return Result.RequestCommandId == RequestCommandId;
		});
	const bool bHasDecision = Decisions.ContainsByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
		{
			return Decision.RequestCommandId == RequestCommandId;
		});
	const bool bHasFinalization = LossFinalizations.ContainsByPredicate(
		[&RequestCommandId](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
		{
			return Finalization.RequestCommandId == RequestCommandId;
		})
		|| WinFinalizations.ContainsByPredicate(
			[&RequestCommandId](const FOddsWellMatchWinnerWinFinalizationRecord& Finalization)
			{
				return Finalization.RequestCommandId == RequestCommandId;
			});
	if (!Request
		|| !Lock
		|| Lock->RequestCommandId != RequestCommandId
		|| Request->Status != AcceptedPendingLockStatus
		|| Lock->Decision != MatchWinnerLockedDecision
		|| SeasonNumber != Request->SeasonNumber
		|| GameNumber != Request->GameNumber
		|| SeasonNumber != Lock->SeasonNumber
		|| GameNumber != Lock->GameNumber
		|| AuthoritativeCancellationUnixSeconds < Lock->AuthoritativeGameStartUnixSeconds
		|| bHasResult
		|| bHasDecision
		|| bHasFinalization)
	{
		OutError = TEXT("The Match Winner canceled-game evidence requires the exact unresolved request and lock only.");
		return EOddsWellMatchWinnerCanceledGameResult::Rejected;
	}

	TArray<FOddsWellMatchWinnerCanceledGameRecord> CandidateCanceledGames;
	CandidateCanceledGames.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		WinFinalizations,
		CandidateCanceledGames,
		VoidDecisions,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerCanceledGameResult::Rejected;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerCanceledGameResult::Recorded;
}

EOddsWellMatchWinnerCanceledGameResult RecordOddsWellUpcomingQaMatchWinnerCancellation(
	FOddsWellMatchWinnerCanceledGameRecord& OutRecord,
	FString& OutError)
{
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	if (!LoadExactUpcomingQaLockState(
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			OutError,
			&CanceledGames)
		|| Locks.Num() != 1)
	{
		OutRecord = FOddsWellMatchWinnerCanceledGameRecord();
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The isolated upcoming QA cancellation requires the exact game-start lock.");
		}
		return EOddsWellMatchWinnerCanceledGameResult::Rejected;
	}
	return RecordOddsWellMatchWinnerCanceledGame(
		UpcomingQaCancellationCommandId,
		UpcomingQaCancellationEvidenceId,
		UpcomingQaRequestCommandId,
		UpcomingQaLockCommandId,
		MatchWinnerCanceledGameSchema,
		MatchWinnerCanceledGameVersion,
		UpcomingQaSeasonNumber,
		UpcomingQaGameNumber,
		UpcomingQaCancellationUnixSeconds,
		MatchWinnerCanceledGameReason,
		true,
		OutRecord,
		OutError);
}

bool RunOddsWellUpcomingQaMatchWinnerCancellationAudit(
	int32& OutLedgerEntries,
	int32& OutRequests,
	int32& OutLocks,
	int32& OutCancellations,
	int64& OutBalance,
	FString& OutError)
{
	TArray<uint8> BeforeBytes;
	if (!UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			BeforeBytes))
	{
		OutError = TEXT("The exact canceled QA state could not be captured.");
		return false;
	}

	FOddsWellMatchWinnerCanceledGameRecord Canceled;
	if (RecordOddsWellUpcomingQaMatchWinnerCancellation(Canceled, OutError)
			!= EOddsWellMatchWinnerCanceledGameResult::Duplicate
		|| Canceled.CancellationCommandId != UpcomingQaCancellationCommandId)
	{
		OutError = TEXT("The exact cold cancellation retry was not idempotent.");
		return false;
	}

	auto RejectCancellation = [&Canceled, &OutError](
		const FString& CommandId,
		const FString& EvidenceId,
		const FString& RequestId,
		const FString& LockId,
		const int32 SeasonNumber,
		const int32 GameNumber,
		const int64 CancellationUnixSeconds)
	{
		return RecordOddsWellMatchWinnerCanceledGame(
			CommandId,
			EvidenceId,
			RequestId,
			LockId,
			MatchWinnerCanceledGameSchema,
			MatchWinnerCanceledGameVersion,
			SeasonNumber,
			GameNumber,
			CancellationUnixSeconds,
			MatchWinnerCanceledGameReason,
			true,
			Canceled,
			OutError) == EOddsWellMatchWinnerCanceledGameResult::Rejected;
	};
	if (!RejectCancellation(UpcomingQaCancellationCommandId, UpcomingQaCancellationEvidenceId, TEXT("qa:h20:unknown-request"), UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(UpcomingQaCancellationCommandId, UpcomingQaCancellationEvidenceId, UpcomingQaRequestCommandId, TEXT("qa:h20:unknown-lock"), UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(UpcomingQaCancellationCommandId, UpcomingQaCancellationEvidenceId, UpcomingQaRequestCommandId, UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber + 1, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(UpcomingQaCancellationCommandId, UpcomingQaCancellationEvidenceId, UpcomingQaRequestCommandId, UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds + 1)
		|| !RejectCancellation(UpcomingQaCancellationCommandId, TEXT("qa:h20:wrong-evidence"), UpcomingQaRequestCommandId, UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(UpcomingQaCancellationCommandId, TEXT("qa:h20:conflict-evidence"), TEXT("qa:h20:conflict-request"), UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(TEXT("qa:h20:second-cancellation"), TEXT("qa:h20:second-evidence"), UpcomingQaRequestCommandId, UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(FString(), FString(), UpcomingQaRequestCommandId, UpcomingQaLockCommandId, UpcomingQaSeasonNumber, UpcomingQaGameNumber, UpcomingQaCancellationUnixSeconds)
		|| !RejectCancellation(TEXT("qa:h20:completed-h16"), TEXT("qa:h20:completed-h16-evidence"), TEXT("wager:match_winner:test-1"), TEXT("wager:match_winner:lock:test-1"), SealedResultSeasonNumber, SealedResultGameNumber, UpcomingQaCancellationUnixSeconds))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("An isolated upcoming QA cancellation rejection invariant failed.");
		}
		return false;
	}

	FOddsWellMatchWinnerResultLinkRecord NormalResult;
	if (LinkOddsWellMatchWinnerResult(
			TEXT("qa:h20:normal-result"),
			UpcomingQaRequestCommandId,
			UpcomingQaLockCommandId,
			MatchWinnerResultSchema,
			MatchWinnerResultVersion,
			UpcomingQaSeasonNumber,
			UpcomingQaGameNumber,
			TEXT("Sundale Sparks"),
			TEXT("Red Mesa Rivals"),
			101,
			100,
			TEXT("Sundale Sparks"),
			FString::ChrN(64, TEXT('a')),
			true,
			NormalResult,
			OutError) != EOddsWellMatchWinnerResultLinkResult::Rejected)
	{
		OutError = TEXT("A canceled upcoming QA game accepted a fabricated normal result.");
		return false;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<uint8> AfterBytes;
	if (!LoadExactUpcomingQaLockState(
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			OutError,
			&CanceledGames)
		|| CanceledGames.Num() != 1
		|| !UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			AfterBytes)
		|| BeforeBytes != AfterBytes)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("A rejected isolated upcoming QA cancellation mutated persisted state.");
		}
		return false;
	}
	OutLedgerEntries = Ledger.GetEntries().Num();
	OutRequests = Requests.Num();
	OutLocks = Locks.Num();
	OutCancellations = CanceledGames.Num();
	OutBalance = Ledger.GetBalance();
	OutError.Reset();
	return true;
}

EOddsWellMatchWinnerVoidDecisionResult DecideOddsWellMatchWinnerVoidRefundDue(
	const FString& VoidDecisionCommandId,
	const FString& CancellationCommandId,
	const FString& CancellationEvidenceId,
	const bool bQaSlot,
	FOddsWellMatchWinnerVoidDecisionRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerVoidDecisionRecord();
	if (!bQaSlot
		|| VoidDecisionCommandId.TrimStartAndEnd().IsEmpty()
		|| CancellationCommandId.TrimStartAndEnd().IsEmpty()
		|| CancellationEvidenceId.TrimStartAndEnd().IsEmpty()
		|| VoidDecisionCommandId == CancellationCommandId
		|| VoidDecisionCommandId == CancellationEvidenceId)
	{
		OutError = TEXT("The Match Winner void decision requires one valid noncanonical QA cancellation identity.");
		return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	}
	if (const FOddsWellMatchWinnerVoidDecisionRecord* Existing = VoidDecisions.FindByPredicate(
		[&VoidDecisionCommandId](const FOddsWellMatchWinnerVoidDecisionRecord& Decision)
		{
			return Decision.VoidDecisionCommandId == VoidDecisionCommandId;
		}))
	{
		if (Existing->CancellationCommandId != CancellationCommandId
			|| Existing->CancellationEvidenceId != CancellationEvidenceId)
		{
			OutError = TEXT("The Match Winner void-decision command was already used with different cancellation evidence.");
			return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerVoidDecisionResult::Duplicate;
	}
	if (!VoidDecisions.IsEmpty())
	{
		OutError = TEXT("The isolated Match Winner QA profile already has a different void decision.");
		return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	}
	const FOddsWellMatchWinnerCanceledGameRecord* Canceled = CanceledGames.FindByPredicate(
		[&CancellationCommandId, &CancellationEvidenceId](const FOddsWellMatchWinnerCanceledGameRecord& Candidate)
		{
			return Candidate.CancellationCommandId == CancellationCommandId
				&& Candidate.CancellationEvidenceId == CancellationEvidenceId;
		});
	const FOddsWellMatchWinnerRequestRecord* Request = Canceled
		? Requests.FindByPredicate(
			[Canceled](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Canceled->RequestCommandId;
			})
		: nullptr;
	const FOddsWellMatchWinnerLockRecord* Lock = Canceled
		? Locks.FindByPredicate(
			[Canceled](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Canceled->LockCommandId;
			})
		: nullptr;
	const bool bHasResult = Canceled && Results.ContainsByPredicate(
		[Canceled](const FOddsWellMatchWinnerResultLinkRecord& Result)
		{
			return Result.RequestCommandId == Canceled->RequestCommandId;
		});
	const bool bHasNormalDecision = Canceled && Decisions.ContainsByPredicate(
		[Canceled](const FOddsWellMatchWinnerSettlementDecisionRecord& Decision)
		{
			return Decision.RequestCommandId == Canceled->RequestCommandId;
		});
	const bool bHasFinalization = Canceled && (
		LossFinalizations.ContainsByPredicate(
			[Canceled](const FOddsWellMatchWinnerLossFinalizationRecord& Finalization)
			{
				return Finalization.RequestCommandId == Canceled->RequestCommandId;
			})
		|| WinFinalizations.ContainsByPredicate(
			[Canceled](const FOddsWellMatchWinnerWinFinalizationRecord& Finalization)
			{
				return Finalization.RequestCommandId == Canceled->RequestCommandId;
			}));
	const bool bSupportedCanceledQaGame = Canceled
		&& ((Canceled->SeasonNumber == CanceledQaSeasonNumber && Canceled->GameNumber == CanceledQaGameNumber)
			|| (Canceled->SeasonNumber == UpcomingQaSeasonNumber && Canceled->GameNumber == UpcomingQaGameNumber));
	if (!Canceled
		|| !Request
		|| !Lock
		|| VoidDecisionCommandId == Request->RequestCommandId
		|| VoidDecisionCommandId == Lock->LockCommandId
		|| !bSupportedCanceledQaGame
		|| Canceled->ReasonCode != MatchWinnerCanceledGameReason
		|| Canceled->Status != MatchWinnerClosedCanceledStatus
		|| Request->Status != AcceptedPendingLockStatus
		|| Request->Stake != 40
		|| Lock->RequestCommandId != Request->RequestCommandId
		|| Lock->Decision != MatchWinnerLockedDecision
		|| bHasResult
		|| bHasNormalDecision
		|| bHasFinalization)
	{
		OutError = TEXT("The Match Winner void decision requires the exact closed canceled-wager chain only.");
		return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	}

	FOddsWellMatchWinnerVoidDecisionRecord Candidate;
	Candidate.VoidDecisionCommandId = VoidDecisionCommandId;
	Candidate.CancellationCommandId = Canceled->CancellationCommandId;
	Candidate.CancellationEvidenceId = Canceled->CancellationEvidenceId;
	Candidate.RequestCommandId = Request->RequestCommandId;
	Candidate.LockCommandId = Lock->LockCommandId;
	Candidate.DecisionSchema = MatchWinnerVoidDecisionSchema;
	Candidate.DecisionVersion = MatchWinnerVoidDecisionVersion;
	Candidate.OfferId = Request->OfferId;
	Candidate.OfferSchema = MatchWinnerOfferSchema;
	Candidate.OfferVersion = Request->OfferVersion;
	Candidate.SeasonNumber = Canceled->SeasonNumber;
	Candidate.GameNumber = Canceled->GameNumber;
	Candidate.SelectedTeam = Request->OfferedTeam;
	Candidate.Stake = Request->Stake;
	Candidate.CancellationReason = Canceled->ReasonCode;
	Candidate.Outcome = MatchWinnerVoidedOutcome;
	Candidate.RefundDue = Request->Stake;
	Candidate.Status = MatchWinnerDecidedVoidPendingRefundStatus;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> CandidateVoidDecisions;
	CandidateVoidDecisions.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		WinFinalizations,
		CanceledGames,
		CandidateVoidDecisions,
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerVoidDecisionResult::Decided;
}

EOddsWellMatchWinnerVoidDecisionResult DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(
	FOddsWellMatchWinnerVoidDecisionRecord& OutRecord,
	FString& OutError)
{
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	if (!LoadExactUpcomingQaLockState(
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			OutError,
			&CanceledGames,
			&VoidDecisions)
		|| Locks.Num() != 1
		|| CanceledGames.Num() != 1)
	{
		OutRecord = FOddsWellMatchWinnerVoidDecisionRecord();
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The isolated upcoming QA void decision requires the exact canceled chain.");
		}
		return EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	}
	return DecideOddsWellMatchWinnerVoidRefundDue(
		UpcomingQaVoidDecisionCommandId,
		UpcomingQaCancellationCommandId,
		UpcomingQaCancellationEvidenceId,
		true,
		OutRecord,
		OutError);
}

bool RunOddsWellUpcomingQaMatchWinnerVoidDecisionAudit(
	int32& OutLedgerEntries,
	int32& OutRequests,
	int32& OutLocks,
	int32& OutCancellations,
	int32& OutVoidDecisions,
	int64& OutBalance,
	FString& OutError)
{
	TArray<uint8> BeforeBytes;
	if (!UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			BeforeBytes))
	{
		OutError = TEXT("The exact pending-refund QA state could not be captured.");
		return false;
	}

	FOddsWellMatchWinnerVoidDecisionRecord Decision;
	if (DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(Decision, OutError)
			!= EOddsWellMatchWinnerVoidDecisionResult::Duplicate
		|| Decision.VoidDecisionCommandId != UpcomingQaVoidDecisionCommandId)
	{
		OutError = TEXT("The exact cold void-decision retry was not idempotent.");
		return false;
	}
	auto RejectDecision = [&Decision, &OutError](
		const FString& DecisionCommandId,
		const FString& CancellationCommandId,
		const FString& CancellationEvidenceId)
	{
		return DecideOddsWellMatchWinnerVoidRefundDue(
			DecisionCommandId,
			CancellationCommandId,
			CancellationEvidenceId,
			true,
			Decision,
			OutError) == EOddsWellMatchWinnerVoidDecisionResult::Rejected;
	};
	if (!RejectDecision(UpcomingQaVoidDecisionCommandId, TEXT("qa:h21:wrong-cancellation"), UpcomingQaCancellationEvidenceId)
		|| !RejectDecision(UpcomingQaVoidDecisionCommandId, UpcomingQaCancellationCommandId, TEXT("qa:h21:wrong-evidence"))
		|| !RejectDecision(UpcomingQaVoidDecisionCommandId, TEXT("qa:h21:conflict-cancellation"), TEXT("qa:h21:conflict-evidence"))
		|| !RejectDecision(TEXT("qa:h21:second-decision"), UpcomingQaCancellationCommandId, UpcomingQaCancellationEvidenceId)
		|| !RejectDecision(FString(), UpcomingQaCancellationCommandId, UpcomingQaCancellationEvidenceId))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("An isolated upcoming QA void-decision rejection invariant failed.");
		}
		return false;
	}

	FOddsWellMatchWinnerResultLinkRecord NormalResult;
	if (LinkOddsWellMatchWinnerResult(
			TEXT("qa:h21:normal-result"),
			UpcomingQaRequestCommandId,
			UpcomingQaLockCommandId,
			MatchWinnerResultSchema,
			MatchWinnerResultVersion,
			UpcomingQaSeasonNumber,
			UpcomingQaGameNumber,
			TEXT("Sundale Sparks"),
			TEXT("Red Mesa Rivals"),
			101,
			100,
			TEXT("Sundale Sparks"),
			FString::ChrN(64, TEXT('b')),
			true,
			NormalResult,
			OutError) != EOddsWellMatchWinnerResultLinkResult::Rejected)
	{
		OutError = TEXT("A pending-refund upcoming QA game accepted a fabricated normal result.");
		return false;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	TArray<uint8> AfterBytes;
	if (!LoadExactUpcomingQaLockState(
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			OutError,
			&CanceledGames,
			&VoidDecisions)
		|| VoidDecisions.Num() != 1
		|| !UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			AfterBytes)
		|| BeforeBytes != AfterBytes)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("A rejected isolated upcoming QA void decision mutated persisted state.");
		}
		return false;
	}
	OutLedgerEntries = Ledger.GetEntries().Num();
	OutRequests = Requests.Num();
	OutLocks = Locks.Num();
	OutCancellations = CanceledGames.Num();
	OutVoidDecisions = VoidDecisions.Num();
	OutBalance = Ledger.GetBalance();
	OutError.Reset();
	return true;
}

EOddsWellMatchWinnerVoidFinalizationResult FinalizeOddsWellUpcomingQaMatchWinnerVoidRefund(
	FOddsWellMatchWinnerVoidFinalizationRecord& OutRecord,
	FString& OutError)
{
	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> VoidFinalizations;
	if (!LoadExactUpcomingQaLockState(
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			OutError,
			&CanceledGames,
			&VoidDecisions,
			&VoidFinalizations)
		|| Locks.Num() != 1
		|| CanceledGames.Num() != 1
		|| VoidDecisions.Num() != 1)
	{
		OutRecord = FOddsWellMatchWinnerVoidFinalizationRecord();
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The isolated upcoming QA refund requires the exact pending void decision.");
		}
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	}
	const EOddsWellMatchWinnerVoidFinalizationResult Result = FinalizeOddsWellMatchWinnerVoidRefund(
		UpcomingQaVoidFinalizationCommandId,
		UpcomingQaVoidDecisionCommandId,
		true,
		OutRecord,
		OutError);
	if (Result == EOddsWellMatchWinnerVoidFinalizationResult::Finalized)
	{
		OutError.Reset();
	}
	return Result;
}

bool RunOddsWellUpcomingQaMatchWinnerVoidFinalizationAudit(
	int32& OutLedgerEntries,
	int32& OutRequests,
	int32& OutLocks,
	int32& OutCancellations,
	int32& OutVoidDecisions,
	int32& OutVoidFinalizations,
	int64& OutBalance,
	FString& OutError)
{
	TArray<uint8> BeforeBytes;
	if (!UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			BeforeBytes))
	{
		OutError = TEXT("The exact refunded QA state could not be captured.");
		return false;
	}

	FOddsWellMatchWinnerVoidFinalizationRecord Finalization;
	if (FinalizeOddsWellUpcomingQaMatchWinnerVoidRefund(Finalization, OutError)
			!= EOddsWellMatchWinnerVoidFinalizationResult::Duplicate
		|| Finalization.FinalizationCommandId != UpcomingQaVoidFinalizationCommandId)
	{
		OutError = TEXT("The exact cold refund-finalization retry was not idempotent.");
		return false;
	}
	auto RejectFinalization = [&Finalization, &OutError](
		const FString& FinalizationCommandId,
		const FString& VoidDecisionCommandId)
	{
		return FinalizeOddsWellMatchWinnerVoidRefund(
			FinalizationCommandId,
			VoidDecisionCommandId,
			true,
			Finalization,
			OutError) == EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	};
	if (!RejectFinalization(UpcomingQaVoidFinalizationCommandId, TEXT("qa:h22:wrong-decision"))
		|| !RejectFinalization(UpcomingQaVoidFinalizationCommandId, TEXT("qa:h22:conflict-decision"))
		|| !RejectFinalization(TEXT("qa:h22:second-finalization"), UpcomingQaVoidDecisionCommandId)
		|| !RejectFinalization(FString(), UpcomingQaVoidDecisionCommandId)
		|| !RejectFinalization(UpcomingQaVoidDecisionCommandId, UpcomingQaVoidDecisionCommandId))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("An isolated upcoming QA refund-finalization rejection invariant failed.");
		}
		return false;
	}

	FOddsWellMatchWinnerResultLinkRecord NormalResult;
	if (LinkOddsWellMatchWinnerResult(
			TEXT("qa:h22:normal-result"),
			UpcomingQaRequestCommandId,
			UpcomingQaLockCommandId,
			MatchWinnerResultSchema,
			MatchWinnerResultVersion,
			UpcomingQaSeasonNumber,
			UpcomingQaGameNumber,
			TEXT("Sundale Sparks"),
			TEXT("Red Mesa Rivals"),
			101,
			100,
			TEXT("Sundale Sparks"),
			FString::ChrN(64, TEXT('c')),
			true,
			NormalResult,
			OutError) != EOddsWellMatchWinnerResultLinkResult::Rejected)
	{
		OutError = TEXT("A refunded upcoming QA game accepted a fabricated normal result.");
		return false;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> VoidFinalizations;
	TArray<uint8> AfterBytes;
	if (!LoadExactUpcomingQaLockState(
			Ledger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			OutError,
			&CanceledGames,
			&VoidDecisions,
			&VoidFinalizations)
		|| VoidFinalizations.Num() != 1
		|| !UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			AfterBytes)
		|| BeforeBytes != AfterBytes)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("A rejected isolated upcoming QA refund finalization mutated persisted state.");
		}
		return false;
	}
	OutLedgerEntries = Ledger.GetEntries().Num();
	OutRequests = Requests.Num();
	OutLocks = Locks.Num();
	OutCancellations = CanceledGames.Num();
	OutVoidDecisions = VoidDecisions.Num();
	OutVoidFinalizations = VoidFinalizations.Num();
	OutBalance = Ledger.GetBalance();
	OutError.Reset();
	return true;
}

EOddsWellMatchWinnerVoidFinalizationResult FinalizeOddsWellMatchWinnerVoidRefund(
	const FString& FinalizationCommandId,
	const FString& VoidDecisionCommandId,
	const bool bQaSlot,
	FOddsWellMatchWinnerVoidFinalizationRecord& OutRecord,
	FString& OutError)
{
	OutRecord = FOddsWellMatchWinnerVoidFinalizationRecord();
	if (!bQaSlot
		|| FinalizationCommandId.TrimStartAndEnd().IsEmpty()
		|| VoidDecisionCommandId.TrimStartAndEnd().IsEmpty()
		|| FinalizationCommandId == VoidDecisionCommandId)
	{
		OutError = TEXT("The Match Winner void finalization requires one valid noncanonical QA decision identity.");
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	}

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
		bFound,
		bNeedsMigration,
		OutError))
	{
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	}
	const UOddsWellOddsBucksSaveGame* SavedRecord = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex));
	const TArray<FOddsWellMatchWinnerVoidFinalizationRecord> ExistingFinalizations = SavedRecord && SavedRecord->SchemaVersion >= 11
		? SavedRecord->MatchWinnerVoidFinalizations
		: TArray<FOddsWellMatchWinnerVoidFinalizationRecord>();
	if (const FOddsWellMatchWinnerVoidFinalizationRecord* Existing = ExistingFinalizations.FindByPredicate(
		[&FinalizationCommandId](const FOddsWellMatchWinnerVoidFinalizationRecord& Finalization)
		{
			return Finalization.FinalizationCommandId == FinalizationCommandId;
		}))
	{
		if (Existing->VoidDecisionCommandId != VoidDecisionCommandId)
		{
			OutError = TEXT("The Match Winner void-finalization command was already used with a different decision.");
			return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
		}
		OutRecord = *Existing;
		OutError.Reset();
		return EOddsWellMatchWinnerVoidFinalizationResult::Duplicate;
	}
	if (!ExistingFinalizations.IsEmpty())
	{
		OutError = TEXT("The isolated Match Winner QA profile already has a different void finalization.");
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	}
	const FOddsWellMatchWinnerVoidDecisionRecord* Decision = VoidDecisions.FindByPredicate(
		[&VoidDecisionCommandId](const FOddsWellMatchWinnerVoidDecisionRecord& Candidate)
		{
			return Candidate.VoidDecisionCommandId == VoidDecisionCommandId;
		});
	const FOddsWellMatchWinnerCanceledGameRecord* Canceled = Decision
		? CanceledGames.FindByPredicate(
			[Decision](const FOddsWellMatchWinnerCanceledGameRecord& Candidate)
			{
				return Candidate.CancellationCommandId == Decision->CancellationCommandId
					&& Candidate.CancellationEvidenceId == Decision->CancellationEvidenceId;
			})
		: nullptr;
	const FOddsWellMatchWinnerRequestRecord* Request = Decision
		? Requests.FindByPredicate(
			[Decision](const FOddsWellMatchWinnerRequestRecord& Candidate)
			{
				return Candidate.RequestCommandId == Decision->RequestCommandId;
			})
		: nullptr;
	const FOddsWellMatchWinnerLockRecord* Lock = Decision
		? Locks.FindByPredicate(
			[Decision](const FOddsWellMatchWinnerLockRecord& Candidate)
			{
				return Candidate.LockCommandId == Decision->LockCommandId;
			})
		: nullptr;
	const bool bSupportedCanceledQaGame = Decision
		&& ((Decision->SeasonNumber == CanceledQaSeasonNumber && Decision->GameNumber == CanceledQaGameNumber)
			|| (Decision->SeasonNumber == UpcomingQaSeasonNumber && Decision->GameNumber == UpcomingQaGameNumber));
	if (!Decision
		|| !Canceled
		|| !Request
		|| !Lock
		|| FinalizationCommandId == Decision->CancellationCommandId
		|| FinalizationCommandId == Decision->CancellationEvidenceId
		|| FinalizationCommandId == Decision->RequestCommandId
		|| FinalizationCommandId == Decision->LockCommandId
		|| Ledger.HasCommand(FinalizationCommandId)
		|| Ledger.GetEntries().Num() != 2
		|| Ledger.GetBalance() != 60
		|| !bSupportedCanceledQaGame
		|| Decision->Stake != 40
		|| Decision->RefundDue != 40
		|| Decision->CancellationReason != MatchWinnerCanceledGameReason
		|| Decision->Outcome != MatchWinnerVoidedOutcome
		|| Decision->Status != MatchWinnerDecidedVoidPendingRefundStatus
		|| Canceled->Status != MatchWinnerClosedCanceledStatus
		|| Canceled->RequestCommandId != Decision->RequestCommandId
		|| Canceled->LockCommandId != Decision->LockCommandId
		|| Request->RequestCommandId != Decision->RequestCommandId
		|| Request->OfferId != Decision->OfferId
		|| Request->OfferVersion != Decision->OfferVersion
		|| Request->OfferedTeam != Decision->SelectedTeam
		|| Request->Stake != Decision->Stake
		|| Lock->LockCommandId != Decision->LockCommandId
		|| Lock->RequestCommandId != Decision->RequestCommandId
		|| !Results.IsEmpty()
		|| !Decisions.IsEmpty()
		|| !LossFinalizations.IsEmpty()
		|| !WinFinalizations.IsEmpty())
	{
		OutError = TEXT("The Match Winner void refund requires the exact pending canceled-wager decision and unchanged ledger evidence.");
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	}

	FOddsWellOddsBucksLedger CandidateLedger = Ledger;
	if (CandidateLedger.Append(FinalizationCommandId, Decision->RefundDue, MatchWinnerRefundReason) != EOddsWellOddsBucksAppendResult::Applied
		|| CandidateLedger.GetEntries().Num() != 3
		|| CandidateLedger.GetBalance() != 100)
	{
		OutError = TEXT("The exact Match Winner refund ledger entry could not be applied.");
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
	}

	FOddsWellMatchWinnerVoidFinalizationRecord Candidate;
	Candidate.FinalizationCommandId = FinalizationCommandId;
	Candidate.VoidDecisionCommandId = VoidDecisionCommandId;
	Candidate.CancellationCommandId = Decision->CancellationCommandId;
	Candidate.CancellationEvidenceId = Decision->CancellationEvidenceId;
	Candidate.RequestCommandId = Decision->RequestCommandId;
	Candidate.LockCommandId = Decision->LockCommandId;
	Candidate.FinalizationSchema = MatchWinnerVoidFinalizationSchema;
	Candidate.FinalizationVersion = MatchWinnerVoidFinalizationVersion;
	Candidate.OfferId = Decision->OfferId;
	Candidate.OfferSchema = Decision->OfferSchema;
	Candidate.OfferVersion = Decision->OfferVersion;
	Candidate.SeasonNumber = Decision->SeasonNumber;
	Candidate.GameNumber = Decision->GameNumber;
	Candidate.SelectedTeam = Decision->SelectedTeam;
	Candidate.Stake = Decision->Stake;
	Candidate.CancellationReason = Decision->CancellationReason;
	Candidate.Outcome = Decision->Outcome;
	Candidate.RefundDue = Decision->RefundDue;
	Candidate.RefundApplied = Decision->RefundDue;
	Candidate.RefundLedgerCommandId = FinalizationCommandId;
	Candidate.Status = MatchWinnerSettledVoidStatus;
	Candidate.ObservedFinalBalance = CandidateLedger.GetBalance();
	Candidate.ObservedLedgerEntryCount = CandidateLedger.GetEntries().Num();
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> CandidateFinalizations;
	CandidateFinalizations.Add(Candidate);
	if (!SaveOddsWellOddsBucksState(
		CandidateLedger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
		Results,
		Decisions,
		LossFinalizations,
		WinFinalizations,
		CanceledGames,
		VoidDecisions,
		bQaSlot,
		OutError,
		&CandidateFinalizations))
	{
		return EOddsWellMatchWinnerVoidFinalizationResult::Rejected;
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
		OutError = FString::Printf(TEXT("The void refund was finalized and applied, but its read-only reconciliation is unavailable: %s"), *ProjectionError);
		return EOddsWellMatchWinnerVoidFinalizationResult::Finalized;
	}
	OutRecord = MoveTemp(Candidate);
	OutError.Reset();
	return EOddsWellMatchWinnerVoidFinalizationResult::Finalized;
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
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
		CanceledGames,
		VoidDecisions,
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
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
		CanceledGames,
		VoidDecisions,
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
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
		CanceledGames,
		VoidDecisions,
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
		CanceledGames,
		VoidDecisions,
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
	TArray<FOddsWellMatchWinnerCanceledGameRecord> MemoryCanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> MemoryVoidDecisions;
	bool bNeedsMigration = false;
	TestTrue(TEXT("Odds Bucks entries validate after a memory round trip"), ValidateOddsBucksSave(UGameplayStatics::LoadGameFromMemory(Bytes), MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
	TestEqual(TEXT("Memory round trip preserves balance"), MemoryLedger.GetBalance(), int64{15});
	Record->SchemaVersion++;
	TestFalse(TEXT("An unsupported Odds Bucks schema is rejected"), ValidateOddsBucksSave(Record, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
	TestFalse(TEXT("A wrong save type is rejected"), ValidateOddsBucksSave(NewObject<UStaticMesh>(), MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));

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
	TestTrue(TEXT("Migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
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
	TestTrue(TEXT("Schema v2 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
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
	TestTrue(TEXT("Schema v3 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

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
	TestTrue(TEXT("Schema v4 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

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
	TestTrue(TEXT("Schema v5 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

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
	TestTrue(TEXT("Schema v6 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

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
		TestFalse(TEXT("Malformed persisted finalization is rejected in memory"), ValidateOddsBucksSave(MalformedFinalizationRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
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
		TestFalse(TEXT("Malformed persisted decision is rejected in memory"), ValidateOddsBucksSave(MalformedDecisionRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
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
		TestFalse(TEXT("Nonloss persisted decision is rejected in memory"), ValidateOddsBucksSave(MalformedDecisionRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
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
		TestFalse(TEXT("Malformed persisted lock is rejected"), ValidateOddsBucksSave(MalformedLockRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
	}
	UOddsWellOddsBucksSaveGame* MalformedResultRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved result link is available for corruption test"), MalformedResultRecord && MalformedResultRecord->MatchWinnerResultLinks.Num() == 1);
	if (MalformedResultRecord && MalformedResultRecord->MatchWinnerResultLinks.Num() == 1)
	{
		const FString MalformedSeal(TEXT("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"));
		MalformedResultRecord->MatchWinnerResultLinks[0].ReplaySealSha256 = MalformedSeal;
		TestFalse(TEXT("Malformed persisted result link is rejected in memory"), ValidateOddsBucksSave(MalformedResultRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
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
	TestTrue(TEXT("Schema v7 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

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
		TestFalse(TEXT("Tampered winning return is rejected in memory"), ValidateOddsBucksSave(MalformedWinDecision, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
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
		TestFalse(TEXT("Malformed win finalization is rejected in memory"), ValidateOddsBucksSave(MalformedWinFinalization, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
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
	FOddsWellMatchWinnerCanceledGameRecord CanceledGame;
	TestEqual(TEXT("Canonical sealed Game 1 can never be relabeled canceled"), RecordOddsWellMatchWinnerCanceledGame(
		TEXT("wager:match_winner:canceled:canonical:invalid"),
		TEXT("server:cancellation:evidence:canonical:invalid"),
		RequestCommandId,
		LockCommandId,
		MatchWinnerCanceledGameSchema,
		MatchWinnerCanceledGameVersion,
		SealedResultSeasonNumber,
		SealedResultGameNumber,
		Offer.LockUnixSeconds + 300,
		MatchWinnerCanceledGameReason,
		true,
		CanceledGame,
		Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestTrue(TEXT("Canceled-game QA starts from a clean isolated profile"), ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(TEXT("Canceled-game QA funds the isolated profile once"), SaveOddsWellOddsBucksLedger(JobLedger, ExpectedNextJobPayout, true, Error));

	FOddsWellMatchWinnerOffer CanceledOffer = Offer;
	CanceledOffer.SeasonNumber = 99;
	CanceledOffer.GameNumber = 1;
	CanceledOffer.HomeTeam = TEXT("QA Canceled Home");
	CanceledOffer.AwayTeam = TEXT("QA Canceled Away");
	CanceledOffer.LockUnixSeconds = 2100000000;
	CanceledOffer.SourceCommitmentSha256 = TEXT("cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc");
	CanceledOffer.Selections[0].Team = CanceledOffer.HomeTeam;
	CanceledOffer.Selections[1].Team = CanceledOffer.AwayTeam;
	TestTrue(TEXT("Noncanonical canceled-game QA offer identity computes"), GetMatchWinnerOfferId(CanceledOffer, CanceledOffer.OfferId, Error));
	const FString CanceledRequestCommandId(TEXT("wager:match_winner:canceled:request:test-1"));
	const FString CanceledLockCommandId(TEXT("wager:match_winner:canceled:lock:test-1"));
	const FString CancellationCommandId(TEXT("wager:match_winner:canceled:disposition:test-1"));
	const FString CancellationEvidenceId(TEXT("server:cancellation:evidence:test-1"));
	const int64 CancellationUnixSeconds = CanceledOffer.LockUnixSeconds + 300;
	FOddsWellMatchWinnerRequestRecord CanceledRequest;
	int64 CanceledBalance = 0;
	TestEqual(TEXT("Noncanonical canceled-game QA request is accepted"), AcceptOddsWellMatchWinnerRequest(CanceledOffer, CanceledRequestCommandId, CanceledOffer.HomeTeam, 40, CanceledOffer.LockUnixSeconds - 60, true, CanceledRequest, CanceledBalance, Error), EOddsWellMatchWinnerRequestResult::Accepted);
	FOddsWellMatchWinnerLockRecord CanceledLock;
	TestEqual(TEXT("Noncanonical canceled-game QA request locks"), LockOddsWellMatchWinnerRequest(CanceledRequestCommandId, CanceledLockCommandId, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CanceledOffer.LockUnixSeconds, true, CanceledLock, Error), EOddsWellMatchWinnerLockResult::Locked);

	UOddsWellOddsBucksSaveGame* VersionEightCanceledBase = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v8 canceled-game base is available"), VersionEightCanceledBase != nullptr);
	if (VersionEightCanceledBase)
	{
		VersionEightCanceledBase->SchemaVersion = 8;
		TestTrue(TEXT("Schema v8 canceled-game base writes"), UGameplayStatics::SaveGameToSlot(VersionEightCanceledBase, OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> VoidDecisions;
	TestTrue(TEXT("Schema v8 canceled-game base migrates"), LoadOddsWellMatchWinnerCanceledGames(true, CanceledGames, bFound, Error));
	TestEqual(TEXT("Schema v8 migration invents no canceled game"), CanceledGames.Num(), 0);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v8 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	TestEqual(TEXT("Canceled game requires the QA profile"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, false, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Unknown request cannot record a canceled game"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, TEXT("wager:match_winner:canceled:request:unknown"), CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Wrong lock cannot record a canceled game"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, TEXT("wager:match_winner:canceled:lock:unknown"), MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Wrong game cannot record a canceled game"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber + 1, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Prestart time cannot record a canceled game"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CanceledOffer.LockUnixSeconds - 1, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Wrong version cannot record a canceled game"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, TEXT("match-winner-canceled-game-v2"), CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Wrong reason cannot record a canceled game"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, TEXT("weather"), true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);

	TestEqual(TEXT("Exact noncanonical canceled-game evidence records once"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Recorded);
	TestEqual(TEXT("Canceled-game record binds request"), CanceledGame.RequestCommandId, CanceledRequestCommandId);
	TestEqual(TEXT("Canceled-game record binds lock"), CanceledGame.LockCommandId, CanceledLockCommandId);
	TestEqual(TEXT("Canceled-game record binds server evidence"), CanceledGame.CancellationEvidenceId, CancellationEvidenceId);
	TestEqual(TEXT("Canceled-game record stores neutral reason"), CanceledGame.ReasonCode, MatchWinnerCanceledGameReason);
	TestEqual(TEXT("Canceled-game record stores closed status"), CanceledGame.Status, MatchWinnerClosedCanceledStatus);
	TestTrue(TEXT("Canceled-game record cold-loads"), LoadOddsWellMatchWinnerCanceledGames(true, CanceledGames, bFound, Error));
	TestEqual(TEXT("Cold load preserves exactly one canceled-game record"), CanceledGames.Num(), 1);
	TestEqual(TEXT("Cold load preserves cancellation command"), CanceledGames[0].CancellationCommandId, CancellationCommandId);
	TestEqual(TEXT("Exact canceled-game retry is idempotent"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, CancellationEvidenceId, CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Duplicate);
	TestEqual(TEXT("Conflicting cancellation command reuse is rejected"), RecordOddsWellMatchWinnerCanceledGame(CancellationCommandId, TEXT("server:cancellation:evidence:conflict"), CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestEqual(TEXT("Second canceled-game disposition is rejected"), RecordOddsWellMatchWinnerCanceledGame(TEXT("wager:match_winner:canceled:disposition:test-2"), TEXT("server:cancellation:evidence:test-2"), CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerCanceledGameSchema, MatchWinnerCanceledGameVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CancellationUnixSeconds, MatchWinnerCanceledGameReason, true, CanceledGame, Error), EOddsWellMatchWinnerCanceledGameResult::Rejected);
	TestTrue(TEXT("Canceled game leaves wager state readable"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Canceled game adds no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Canceled game adds no credit"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Canceled game creates no sealed result"), WagerResultLinks.Num(), 0);
	TestEqual(TEXT("Canceled game creates no settlement"), WagerDecisions.Num(), 0);
	TestEqual(TEXT("Canceled game creates no loss finalization"), WagerFinalizations.Num(), 0);
	TestEqual(TEXT("Canceled game creates no win finalization"), WagerWinFinalizations.Num(), 0);
	TestFalse(TEXT("Canceled game publishes no Admin reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));

	TArray<uint8> ExactCanceledGameBytes;
	TestTrue(TEXT("Exact canceled-game profile is preserved before malformed QA"), UGameplayStatics::SaveGameToMemory(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex), ExactCanceledGameBytes));
	UOddsWellOddsBucksSaveGame* MalformedCanceledGame = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved canceled-game record is available for malformed QA"), MalformedCanceledGame && MalformedCanceledGame->MatchWinnerCanceledGames.Num() == 1);
	if (MalformedCanceledGame && MalformedCanceledGame->MatchWinnerCanceledGames.Num() == 1)
	{
		MalformedCanceledGame->MatchWinnerCanceledGames[0].Status = TEXT("open");
		TestTrue(TEXT("Malformed canceled-game status writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(MalformedCanceledGame, OddsBucksQaSlot, OddsBucksUserIndex));
		TestFalse(TEXT("Malformed canceled-game status fails cold load"), LoadOddsWellMatchWinnerCanceledGames(true, CanceledGames, bFound, Error));
		TestTrue(TEXT("Exact canceled-game profile restores after malformed QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactCanceledGameBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TestTrue(TEXT("Restored canceled-game profile validates"), LoadOddsWellMatchWinnerCanceledGames(true, CanceledGames, bFound, Error));
	TestEqual(TEXT("Restored canceled-game profile remains exact"), CanceledGames.Num(), 1);

	UOddsWellOddsBucksSaveGame* VersionNineVoidBase = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v9 canceled-game base is available"), VersionNineVoidBase != nullptr);
	if (VersionNineVoidBase)
	{
		VersionNineVoidBase->SchemaVersion = 9;
		TestTrue(TEXT("Schema v9 canceled-game base writes"), UGameplayStatics::SaveGameToSlot(VersionNineVoidBase, OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TestTrue(TEXT("Schema v9 canceled-game base migrates for void decisions"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
	TestEqual(TEXT("Schema v9 migration invents no void decision"), VoidDecisions.Num(), 0);
	TestTrue(TEXT("Schema v9 migration preserves canceled-game evidence"), LoadOddsWellMatchWinnerCanceledGames(true, CanceledGames, bFound, Error));
	TestEqual(TEXT("Schema v9 migration preserves one canceled game"), CanceledGames.Num(), 1);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v9 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	const FString VoidDecisionCommandId(TEXT("wager:match_winner:canceled:void-decision:test-1"));
	FOddsWellMatchWinnerVoidDecisionRecord VoidDecision;
	TestEqual(TEXT("Void decision requires the QA profile"), DecideOddsWellMatchWinnerVoidRefundDue(VoidDecisionCommandId, CancellationCommandId, CancellationEvidenceId, false, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Rejected);
	TestEqual(TEXT("Unknown cancellation cannot create a void decision"), DecideOddsWellMatchWinnerVoidRefundDue(VoidDecisionCommandId, TEXT("wager:match_winner:canceled:disposition:unknown"), CancellationEvidenceId, true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Rejected);
	TestEqual(TEXT("Mismatched cancellation evidence cannot create a void decision"), DecideOddsWellMatchWinnerVoidRefundDue(VoidDecisionCommandId, CancellationCommandId, TEXT("server:cancellation:evidence:mismatch"), true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Rejected);
	TestEqual(TEXT("Empty void-decision command is rejected"), DecideOddsWellMatchWinnerVoidRefundDue(FString(), CancellationCommandId, CancellationEvidenceId, true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Rejected);
	FOddsWellMatchWinnerResultLinkRecord RejectedCanceledResult;
	TestEqual(TEXT("Canceled chain cannot receive a normal result link"), LinkOddsWellMatchWinnerResult(TEXT("wager:match_winner:canceled:result:invalid"), CanceledRequestCommandId, CanceledLockCommandId, MatchWinnerResultSchema, MatchWinnerResultVersion, CanceledOffer.SeasonNumber, CanceledOffer.GameNumber, CanceledOffer.HomeTeam, CanceledOffer.AwayTeam, 90, 89, CanceledOffer.HomeTeam, TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"), true, RejectedCanceledResult, Error), EOddsWellMatchWinnerResultLinkResult::Rejected);
	FOddsWellMatchWinnerSettlementDecisionRecord RejectedCanceledSettlement;
	TestEqual(TEXT("Canceled chain cannot receive a normal settlement decision"), DecideOddsWellMatchWinnerSettlement(TEXT("wager:match_winner:canceled:settlement:invalid"), CanceledRequestCommandId, CanceledLockCommandId, TEXT("wager:match_winner:canceled:result:invalid"), true, RejectedCanceledSettlement, Error), EOddsWellMatchWinnerSettlementDecisionResult::Rejected);

	TestEqual(TEXT("Exact canceled wager receives one refund-due decision"), DecideOddsWellMatchWinnerVoidRefundDue(VoidDecisionCommandId, CancellationCommandId, CancellationEvidenceId, true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Decided);
	TestEqual(TEXT("Void decision binds cancellation command"), VoidDecision.CancellationCommandId, CancellationCommandId);
	TestEqual(TEXT("Void decision binds cancellation evidence"), VoidDecision.CancellationEvidenceId, CancellationEvidenceId);
	TestEqual(TEXT("Void decision binds request"), VoidDecision.RequestCommandId, CanceledRequestCommandId);
	TestEqual(TEXT("Void decision binds lock"), VoidDecision.LockCommandId, CanceledLockCommandId);
	TestEqual(TEXT("Void decision binds exact offer"), VoidDecision.OfferId, CanceledOffer.OfferId);
	TestEqual(TEXT("Void decision binds offer schema"), VoidDecision.OfferSchema, MatchWinnerOfferSchema);
	TestEqual(TEXT("Void decision binds offer version"), VoidDecision.OfferVersion, CanceledOffer.OfferVersion);
	TestEqual(TEXT("Void decision binds selected team"), VoidDecision.SelectedTeam, CanceledOffer.HomeTeam);
	TestEqual(TEXT("Void decision binds stake 40"), VoidDecision.Stake, int64{40});
	TestEqual(TEXT("Void decision binds neutral cancellation reason"), VoidDecision.CancellationReason, MatchWinnerCanceledGameReason);
	TestEqual(TEXT("Void decision stores voided outcome"), VoidDecision.Outcome, MatchWinnerVoidedOutcome);
	TestEqual(TEXT("Void decision records refund due 40"), VoidDecision.RefundDue, int64{40});
	TestEqual(TEXT("Void decision remains pending refund"), VoidDecision.Status, MatchWinnerDecidedVoidPendingRefundStatus);
	TestTrue(TEXT("Void decision cold-loads"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
	TestEqual(TEXT("Cold load preserves exactly one void decision"), VoidDecisions.Num(), 1);
	TestEqual(TEXT("Exact void-decision retry is idempotent"), DecideOddsWellMatchWinnerVoidRefundDue(VoidDecisionCommandId, CancellationCommandId, CancellationEvidenceId, true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Duplicate);
	TestEqual(TEXT("Conflicting void-decision command reuse is rejected"), DecideOddsWellMatchWinnerVoidRefundDue(VoidDecisionCommandId, TEXT("wager:match_winner:canceled:disposition:conflict"), CancellationEvidenceId, true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Rejected);
	TestEqual(TEXT("Second void decision is rejected"), DecideOddsWellMatchWinnerVoidRefundDue(TEXT("wager:match_winner:canceled:void-decision:test-2"), CancellationCommandId, CancellationEvidenceId, true, VoidDecision, Error), EOddsWellMatchWinnerVoidDecisionResult::Rejected);
	TestTrue(TEXT("Void decision leaves wager state readable"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Void decision adds no ledger entry"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Void decision applies no refund"), WagerLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Void decision creates no sealed result"), WagerResultLinks.Num(), 0);
	TestEqual(TEXT("Void decision creates no normal settlement"), WagerDecisions.Num(), 0);
	TestEqual(TEXT("Void decision creates no loss finalization"), WagerFinalizations.Num(), 0);
	TestEqual(TEXT("Void decision creates no win finalization"), WagerWinFinalizations.Num(), 0);
	TestEqual(TEXT("Void decision cannot use normal loss finalization"), FinalizeOddsWellMatchWinnerLoss(TEXT("wager:match_winner:canceled:loss-finalization:invalid"), VoidDecisionCommandId, true, RetryFinalizationRecord, Error), EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestEqual(TEXT("Void decision cannot use normal win finalization"), FinalizeOddsWellMatchWinnerWin(TEXT("wager:match_winner:canceled:win-finalization:invalid"), VoidDecisionCommandId, true, RetryWinFinalization, Error), EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TestFalse(TEXT("Void decision publishes no Admin reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));

	TArray<uint8> ExactVoidDecisionBytes;
	TestTrue(TEXT("Exact void-decision profile is preserved before tamper QA"), UGameplayStatics::SaveGameToMemory(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex), ExactVoidDecisionBytes));
	UOddsWellOddsBucksSaveGame* MalformedVoidDecision = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved void decision is available for value tamper QA"), MalformedVoidDecision && MalformedVoidDecision->MatchWinnerVoidDecisions.Num() == 1);
	if (MalformedVoidDecision && MalformedVoidDecision->MatchWinnerVoidDecisions.Num() == 1)
	{
		MalformedVoidDecision->MatchWinnerVoidDecisions[0].RefundDue = 41;
		TestFalse(TEXT("Wrong persisted refund-due value is rejected in memory"), ValidateOddsBucksSave(MalformedVoidDecision, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
		MalformedVoidDecision->MatchWinnerVoidDecisions[0].RefundDue = 40;
		MalformedVoidDecision->MatchWinnerVoidDecisions[0].Status = TEXT("settled_void");
		TestTrue(TEXT("Malformed void-decision status writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(MalformedVoidDecision, OddsBucksQaSlot, OddsBucksUserIndex));
		TestFalse(TEXT("Malformed void-decision status fails cold load"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
		TestTrue(TEXT("Exact void-decision profile restores after malformed QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactVoidDecisionBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	UOddsWellOddsBucksSaveGame* NonclosedCanceledDecision = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Canceled evidence is available for nonclosed decision QA"), NonclosedCanceledDecision && NonclosedCanceledDecision->MatchWinnerCanceledGames.Num() == 1);
	if (NonclosedCanceledDecision && NonclosedCanceledDecision->MatchWinnerCanceledGames.Num() == 1)
	{
		NonclosedCanceledDecision->MatchWinnerCanceledGames[0].Status = TEXT("open");
		TestTrue(TEXT("Nonclosed canceled evidence writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(NonclosedCanceledDecision, OddsBucksQaSlot, OddsBucksUserIndex));
		TestFalse(TEXT("Void decision rejects nonclosed cancellation on cold load"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
		TestTrue(TEXT("Exact void-decision profile restores after nonclosed QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactVoidDecisionBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TestTrue(TEXT("Restored void-decision profile validates"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
	TestEqual(TEXT("Restored void-decision profile remains exact"), VoidDecisions.Num(), 1);

	UOddsWellOddsBucksSaveGame* VersionTenVoidFinalizationBase = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v10 void-decision base is available"), VersionTenVoidFinalizationBase != nullptr);
	if (VersionTenVoidFinalizationBase)
	{
		VersionTenVoidFinalizationBase->SchemaVersion = 10;
		TestTrue(TEXT("Schema v10 void-decision base writes"), UGameplayStatics::SaveGameToSlot(VersionTenVoidFinalizationBase, OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> VoidFinalizations;
	TestTrue(TEXT("Schema v10 void-decision base migrates for void finalizations"), LoadOddsWellMatchWinnerVoidFinalizations(true, VoidFinalizations, bFound, Error));
	TestEqual(TEXT("Schema v10 migration invents no void finalization"), VoidFinalizations.Num(), 0);
	TestTrue(TEXT("Schema v10 migration preserves pending void decision"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
	TestEqual(TEXT("Schema v10 migration preserves one void decision"), VoidDecisions.Num(), 1);
	MigratedRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Schema v10 migration rewrites schema v12"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	const FString VoidFinalizationCommandId(TEXT("wager:match_winner:canceled:void-finalization:test-1"));
	FOddsWellMatchWinnerVoidFinalizationRecord VoidFinalization;
	TestEqual(TEXT("Void finalization requires the QA profile"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, VoidDecisionCommandId, false, VoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
	TestEqual(TEXT("Empty void-finalization command is rejected"), FinalizeOddsWellMatchWinnerVoidRefund(FString(), VoidDecisionCommandId, true, VoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
	TestEqual(TEXT("Unknown void decision cannot apply a refund"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, TEXT("wager:match_winner:canceled:void-decision:unknown"), true, VoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
	TestEqual(TEXT("Finalization and decision identities must differ"), FinalizeOddsWellMatchWinnerVoidRefund(VoidDecisionCommandId, VoidDecisionCommandId, true, VoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);

	TestEqual(TEXT("Exact pending void decision applies and finalizes one refund"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, VoidDecisionCommandId, true, VoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Finalized);
	TestEqual(TEXT("Void finalization binds decision"), VoidFinalization.VoidDecisionCommandId, VoidDecisionCommandId);
	TestEqual(TEXT("Void finalization binds cancellation command"), VoidFinalization.CancellationCommandId, CancellationCommandId);
	TestEqual(TEXT("Void finalization binds cancellation evidence"), VoidFinalization.CancellationEvidenceId, CancellationEvidenceId);
	TestEqual(TEXT("Void finalization binds request"), VoidFinalization.RequestCommandId, CanceledRequestCommandId);
	TestEqual(TEXT("Void finalization binds lock"), VoidFinalization.LockCommandId, CanceledLockCommandId);
	TestEqual(TEXT("Void finalization binds exact offer"), VoidFinalization.OfferId, CanceledOffer.OfferId);
	TestEqual(TEXT("Void finalization binds offer schema"), VoidFinalization.OfferSchema, MatchWinnerOfferSchema);
	TestEqual(TEXT("Void finalization binds offer version"), VoidFinalization.OfferVersion, CanceledOffer.OfferVersion);
	TestEqual(TEXT("Void finalization binds selected team"), VoidFinalization.SelectedTeam, CanceledOffer.HomeTeam);
	TestEqual(TEXT("Void finalization binds stake 40"), VoidFinalization.Stake, int64{40});
	TestEqual(TEXT("Void finalization preserves refund due 40"), VoidFinalization.RefundDue, int64{40});
	TestEqual(TEXT("Void finalization applies refund 40"), VoidFinalization.RefundApplied, int64{40});
	TestEqual(TEXT("Void finalization binds refund ledger command"), VoidFinalization.RefundLedgerCommandId, VoidFinalizationCommandId);
	TestEqual(TEXT("Void finalization stores settled void"), VoidFinalization.Status, MatchWinnerSettledVoidStatus);
	TestEqual(TEXT("Void finalization observes three ledger entries"), VoidFinalization.ObservedLedgerEntryCount, 3);
	TestEqual(TEXT("Void finalization observes balance 100"), VoidFinalization.ObservedFinalBalance, int64{100});
	TestTrue(TEXT("Void finalization cold-loads"), LoadOddsWellMatchWinnerVoidFinalizations(true, VoidFinalizations, bFound, Error));
	TestEqual(TEXT("Cold load preserves exactly one void finalization"), VoidFinalizations.Num(), 1);
	TestTrue(TEXT("Finalized void chain remains readable"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Void refund appends exactly one ledger entry"), WagerLedger.GetEntries().Num(), 3);
	TestEqual(TEXT("Void refund restores balance 100"), WagerLedger.GetBalance(), int64{100});
	TestEqual(TEXT("Void refund preserves job cooldown"), WagerNextJobPayout, ExpectedNextJobPayout);
	const FOddsWellOddsBucksEntry& RefundEntry = WagerLedger.GetEntries()[2];
	TestEqual(TEXT("Void refund is sequence three"), RefundEntry.Sequence, int64{3});
	TestEqual(TEXT("Void refund command is finalization command"), RefundEntry.CommandId, VoidFinalizationCommandId);
	TestEqual(TEXT("Void refund appends exactly plus 40"), RefundEntry.Delta, int64{40});
	TestEqual(TEXT("Void refund reaches balance 100"), RefundEntry.BalanceAfter, int64{100});
	TestEqual(TEXT("Void refund uses match winner refund reason"), RefundEntry.Reason, MatchWinnerRefundReason);
	TestEqual(TEXT("Void refund creates no sealed result"), WagerResultLinks.Num(), 0);
	TestEqual(TEXT("Void refund creates no normal settlement"), WagerDecisions.Num(), 0);
	TestEqual(TEXT("Void refund creates no loss finalization"), WagerFinalizations.Num(), 0);
	TestEqual(TEXT("Void refund creates no win finalization"), WagerWinFinalizations.Num(), 0);
	TestTrue(TEXT("Void decision remains cold-readable after finalization"), LoadOddsWellMatchWinnerVoidDecisions(true, VoidDecisions, bFound, Error));
	TestEqual(TEXT("Void decision remains pending after finalization"), VoidDecisions[0].Status, MatchWinnerDecidedVoidPendingRefundStatus);
	TestTrue(TEXT("Void finalization publishes exact read-only reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString MatchWinnerVoidProjectionJson;
	TSharedPtr<FJsonObject> MatchWinnerVoidProjection;
	TestTrue(TEXT("Exact void reconciliation reads"), FFileHelper::LoadFileToString(MatchWinnerVoidProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> MatchWinnerVoidProjectionReader = TJsonReaderFactory<>::Create(MatchWinnerVoidProjectionJson);
	TestTrue(TEXT("Exact void reconciliation parses"), FJsonSerializer::Deserialize(MatchWinnerVoidProjectionReader, MatchWinnerVoidProjection) && MatchWinnerVoidProjection.IsValid());
	FString NormalizedMatchWinnerVoidProjectionJson;
	if (MatchWinnerVoidProjection.IsValid())
	{
		TestEqual(TEXT("Void reconciliation keeps v1 schema"), MatchWinnerVoidProjection->GetStringField(TEXT("schema")), MatchWinnerReconciliationSchema);
		TestEqual(TEXT("Void reconciliation binds exact noncanonical offer"), MatchWinnerVoidProjection->GetStringField(TEXT("offer_id")), CanceledOffer.OfferId);
		TestEqual(TEXT("Void reconciliation binds request"), MatchWinnerVoidProjection->GetStringField(TEXT("request_command_id")), CanceledRequestCommandId);
		TestEqual(TEXT("Void reconciliation binds stake debit command"), MatchWinnerVoidProjection->GetStringField(TEXT("stake_ledger_command_id")), CanceledRequestCommandId);
		TestEqual(TEXT("Void reconciliation binds stake sequence two"), static_cast<int32>(MatchWinnerVoidProjection->GetNumberField(TEXT("stake_sequence"))), 2);
		TestEqual(TEXT("Void reconciliation binds stake minus 40"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("stake_delta"))), int64{-40});
		TestEqual(TEXT("Void reconciliation binds stake balance 60"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("stake_balance_after"))), int64{60});
		TestEqual(TEXT("Void reconciliation binds lock"), MatchWinnerVoidProjection->GetStringField(TEXT("lock_command_id")), CanceledLockCommandId);
		TestEqual(TEXT("Void reconciliation binds Season 99"), static_cast<int32>(MatchWinnerVoidProjection->GetNumberField(TEXT("season_number"))), 99);
		TestEqual(TEXT("Void reconciliation binds Game 1"), static_cast<int32>(MatchWinnerVoidProjection->GetNumberField(TEXT("game_number"))), 1);
		TestEqual(TEXT("Void reconciliation binds cancellation command"), MatchWinnerVoidProjection->GetStringField(TEXT("cancellation_command_id")), CancellationCommandId);
		TestEqual(TEXT("Void reconciliation binds cancellation evidence"), MatchWinnerVoidProjection->GetStringField(TEXT("cancellation_evidence_id")), CancellationEvidenceId);
		TestEqual(TEXT("Void reconciliation binds cancellation schema"), MatchWinnerVoidProjection->GetStringField(TEXT("cancellation_schema")), MatchWinnerCanceledGameSchema);
		TestEqual(TEXT("Void reconciliation binds cancellation version"), MatchWinnerVoidProjection->GetStringField(TEXT("cancellation_version")), MatchWinnerCanceledGameVersion);
		TestEqual(TEXT("Void reconciliation binds cancellation time"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("cancellation_unix"))), CancellationUnixSeconds);
		TestEqual(TEXT("Void reconciliation binds game canceled"), MatchWinnerVoidProjection->GetStringField(TEXT("cancellation_reason")), MatchWinnerCanceledGameReason.ToString());
		TestEqual(TEXT("Void reconciliation binds closed canceled"), MatchWinnerVoidProjection->GetStringField(TEXT("cancellation_status")), MatchWinnerClosedCanceledStatus.ToString());
		TestEqual(TEXT("Void reconciliation binds decision"), MatchWinnerVoidProjection->GetStringField(TEXT("decision_command_id")), VoidDecisionCommandId);
		TestEqual(TEXT("Void reconciliation binds voided outcome"), MatchWinnerVoidProjection->GetStringField(TEXT("outcome")), MatchWinnerVoidedOutcome.ToString());
		TestEqual(TEXT("Void reconciliation binds refund due 40"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("refund_due"))), int64{40});
		TestEqual(TEXT("Void reconciliation keeps H13 pending"), MatchWinnerVoidProjection->GetStringField(TEXT("decision_status")), MatchWinnerDecidedVoidPendingRefundStatus.ToString());
		TestEqual(TEXT("Void reconciliation binds refund ledger command"), MatchWinnerVoidProjection->GetStringField(TEXT("refund_ledger_command_id")), VoidFinalizationCommandId);
		TestEqual(TEXT("Void reconciliation binds refund sequence three"), static_cast<int32>(MatchWinnerVoidProjection->GetNumberField(TEXT("refund_sequence"))), 3);
		TestEqual(TEXT("Void reconciliation binds refund plus 40"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("refund_delta"))), int64{40});
		TestEqual(TEXT("Void reconciliation binds refund reason"), MatchWinnerVoidProjection->GetStringField(TEXT("refund_reason")), MatchWinnerRefundReason.ToString());
		TestEqual(TEXT("Void reconciliation binds refund balance 100"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("refund_balance_after"))), int64{100});
		TestEqual(TEXT("Void reconciliation binds finalization"), MatchWinnerVoidProjection->GetStringField(TEXT("finalization_command_id")), VoidFinalizationCommandId);
		TestEqual(TEXT("Void reconciliation binds settled void"), MatchWinnerVoidProjection->GetStringField(TEXT("finalization_status")), MatchWinnerSettledVoidStatus.ToString());
		TestEqual(TEXT("Void reconciliation binds applied refund 40"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("refund_applied"))), int64{40});
		TestEqual(TEXT("Void reconciliation reports count three"), static_cast<int32>(MatchWinnerVoidProjection->GetNumberField(TEXT("ledger_entry_count"))), 3);
		TestEqual(TEXT("Void reconciliation reports balance 100"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("final_balance"))), int64{100});
		TestEqual(TEXT("Void reconciliation reports net zero"), static_cast<int64>(MatchWinnerVoidProjection->GetNumberField(TEXT("net"))), int64{0});
		TestFalse(TEXT("Void reconciliation invents no result command"), MatchWinnerVoidProjection->HasField(TEXT("result_command_id")));
		TestFalse(TEXT("Void reconciliation invents no winner"), MatchWinnerVoidProjection->HasField(TEXT("winner")));
		TestFalse(TEXT("Void reconciliation invents no score"), MatchWinnerVoidProjection->HasField(TEXT("home_score")) || MatchWinnerVoidProjection->HasField(TEXT("away_score")));
		TestFalse(TEXT("Void reconciliation invents no replay"), MatchWinnerVoidProjection->HasField(TEXT("replay_seal_sha256")));
		TestFalse(TEXT("Void reconciliation invents no payout ledger"), MatchWinnerVoidProjection->HasField(TEXT("payout_ledger_command_id")));
		TestFalse(TEXT("Void reconciliation invents no gross return due"), MatchWinnerVoidProjection->HasField(TEXT("gross_return_due")));
		TestFalse(TEXT("Void reconciliation invents no gross return applied"), MatchWinnerVoidProjection->HasField(TEXT("gross_return_applied")));
		MatchWinnerVoidProjection->RemoveField(TEXT("generated_at_utc"));
		const TSharedRef<TJsonWriter<>> NormalizedMatchWinnerVoidProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedMatchWinnerVoidProjectionJson);
		TestTrue(TEXT("Exact void reconciliation normalizes"), FJsonSerializer::Serialize(MatchWinnerVoidProjection.ToSharedRef(), NormalizedMatchWinnerVoidProjectionWriter));
	}
	TestTrue(TEXT("QA can remove finalized-void projection for cold-load proof"), IFileManager::Get().Delete(*MatchWinnerProjectionPath, false, true, true));
	TestFalse(TEXT("Finalized-void projection is absent before cold load"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	TestTrue(TEXT("Exact void finalization cold-restores reconciliation"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestTrue(TEXT("Validated cold load regenerates finalized-void reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString RegeneratedVoidProjectionJson;
	TSharedPtr<FJsonObject> RegeneratedVoidProjection;
	TestTrue(TEXT("Regenerated exact void reconciliation reads"), FFileHelper::LoadFileToString(RegeneratedVoidProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> RegeneratedVoidProjectionReader = TJsonReaderFactory<>::Create(RegeneratedVoidProjectionJson);
	TestTrue(TEXT("Regenerated exact void reconciliation parses"), FJsonSerializer::Deserialize(RegeneratedVoidProjectionReader, RegeneratedVoidProjection) && RegeneratedVoidProjection.IsValid());
	if (RegeneratedVoidProjection.IsValid())
	{
		RegeneratedVoidProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedRegeneratedVoidProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedRegeneratedVoidProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedRegeneratedVoidProjectionJson);
		TestTrue(TEXT("Regenerated exact void reconciliation normalizes"), FJsonSerializer::Serialize(RegeneratedVoidProjection.ToSharedRef(), NormalizedRegeneratedVoidProjectionWriter));
		TestEqual(TEXT("Cold load regenerates identical void reconciliation data"), NormalizedRegeneratedVoidProjectionJson, NormalizedMatchWinnerVoidProjectionJson);
	}

	FOddsWellMatchWinnerVoidFinalizationRecord RetryVoidFinalization;
	TestEqual(TEXT("Exact void finalization retry is idempotent"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, VoidDecisionCommandId, true, RetryVoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Duplicate);
	TestEqual(TEXT("Conflicting void-finalization command reuse is rejected"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, TEXT("wager:match_winner:canceled:void-decision:unknown"), true, RetryVoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
	TestEqual(TEXT("Second void finalization is rejected"), FinalizeOddsWellMatchWinnerVoidRefund(TEXT("wager:match_winner:canceled:void-finalization:test-2"), VoidDecisionCommandId, true, RetryVoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
	TestTrue(TEXT("Void finalization retries preserve exact cold state"), LoadOddsWellMatchWinnerVoidFinalizations(true, VoidFinalizations, bFound, Error));
	TestEqual(TEXT("Void finalization retries preserve one record"), VoidFinalizations.Num(), 1);
	TestTrue(TEXT("Void finalization retries preserve ledger state"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	TestEqual(TEXT("Void finalization retries preserve three entries"), WagerLedger.GetEntries().Num(), 3);
	TestEqual(TEXT("Void finalization retries preserve balance 100"), WagerLedger.GetBalance(), int64{100});

	TArray<uint8> ExactVoidFinalizedBytes;
	TestTrue(TEXT("Exact finalized void profile is preserved before tamper QA"), UGameplayStatics::SaveGameToMemory(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex), ExactVoidFinalizedBytes));
	UOddsWellOddsBucksSaveGame* MalformedVoidFinalization = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved void finalization is available for tamper QA"), MalformedVoidFinalization && MalformedVoidFinalization->MatchWinnerVoidFinalizations.Num() == 1);
	if (MalformedVoidFinalization && MalformedVoidFinalization->MatchWinnerVoidFinalizations.Num() == 1)
	{
		MalformedVoidFinalization->MatchWinnerVoidFinalizations[0].RefundApplied = 39;
		TestFalse(TEXT("Wrong persisted refund-applied value is rejected in memory"), ValidateOddsBucksSave(MalformedVoidFinalization, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, MemoryResultLinks, MemoryDecisions, MemoryFinalizations, MemoryWinFinalizations, MemoryCanceledGames, MemoryVoidDecisions, bNeedsMigration, Error));
		TestTrue(TEXT("Malformed void finalization writes for no-mutation QA"), UGameplayStatics::SaveGameToSlot(MalformedVoidFinalization, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Malformed persisted void finalization fails closed"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, VoidDecisionCommandId, true, RetryVoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
		TestFalse(TEXT("Malformed void finalization removes stale reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		const UOddsWellOddsBucksSaveGame* PersistedMalformedVoidFinalization = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected retry does not rewrite malformed void finalization"), PersistedMalformedVoidFinalization
			&& PersistedMalformedVoidFinalization->MatchWinnerVoidFinalizations.Num() == 1
			&& PersistedMalformedVoidFinalization->MatchWinnerVoidFinalizations[0].RefundApplied == 39);
		TestTrue(TEXT("Exact finalized void restores after value tamper QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactVoidFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	UOddsWellOddsBucksSaveGame* MalformedVoidLedger = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved void ledger is available for anomaly QA"), MalformedVoidLedger && MalformedVoidLedger->Entries.Num() == 3);
	if (MalformedVoidLedger && MalformedVoidLedger->Entries.Num() == 3)
	{
		MalformedVoidLedger->Entries[2].Reason = TEXT("match_winner_payout");
		TestTrue(TEXT("Malformed void refund reason writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(MalformedVoidLedger, OddsBucksQaSlot, OddsBucksUserIndex));
		TestFalse(TEXT("Malformed void refund reason fails cold load"), LoadOddsWellMatchWinnerVoidFinalizations(true, VoidFinalizations, bFound, Error));
		TestFalse(TEXT("Malformed void refund reason removes stale reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		TestTrue(TEXT("Exact finalized void restores after ledger anomaly QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactVoidFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	UOddsWellOddsBucksSaveGame* MalformedVoidStatus = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved void finalization is available for status QA"), MalformedVoidStatus && MalformedVoidStatus->MatchWinnerVoidFinalizations.Num() == 1);
	if (MalformedVoidStatus && MalformedVoidStatus->MatchWinnerVoidFinalizations.Num() == 1)
	{
		MalformedVoidStatus->MatchWinnerVoidFinalizations[0].Status = TEXT("open");
		TestTrue(TEXT("Malformed void-finalization status writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(MalformedVoidStatus, OddsBucksQaSlot, OddsBucksUserIndex));
		TestFalse(TEXT("Malformed void-finalization status fails cold load"), LoadOddsWellMatchWinnerVoidFinalizations(true, VoidFinalizations, bFound, Error));
		TestFalse(TEXT("Malformed void-finalization status removes stale reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		TestTrue(TEXT("Exact finalized void restores after status QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactVoidFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	UOddsWellOddsBucksSaveGame* ExtraVoidMutation = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Exact finalized void is available for extra-mutation QA"), ExtraVoidMutation && ExtraVoidMutation->Entries.Num() == 3);
	if (ExtraVoidMutation && ExtraVoidMutation->Entries.Num() == 3)
	{
		FOddsWellOddsBucksEntry ExtraEntry;
		ExtraEntry.Sequence = 4;
		ExtraEntry.CommandId = TEXT("qa:unexpected-void-extra-mutation");
		ExtraEntry.Delta = 1;
		ExtraEntry.BalanceAfter = 101;
		ExtraEntry.Reason = FName(TEXT("qa_unexpected_credit"));
		ExtraVoidMutation->Entries.Add(ExtraEntry);
		TestTrue(TEXT("Unexpected void extra mutation writes for fail-closed QA"), UGameplayStatics::SaveGameToSlot(ExtraVoidMutation, OddsBucksQaSlot, OddsBucksUserIndex));
		TestEqual(TEXT("Unexpected void extra mutation rejects retry"), FinalizeOddsWellMatchWinnerVoidRefund(VoidFinalizationCommandId, VoidDecisionCommandId, true, RetryVoidFinalization, Error), EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
		TestFalse(TEXT("Unexpected void extra mutation removes stale reconciliation"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		const UOddsWellOddsBucksSaveGame* PersistedExtraVoidMutation = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
		TestTrue(TEXT("Rejected retry does not rewrite unexpected void mutation"), PersistedExtraVoidMutation && PersistedExtraVoidMutation->Entries.Num() == 4);
		TestTrue(TEXT("Exact finalized void restores after extra-mutation QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactVoidFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	}
	TestTrue(TEXT("Restored exact void finalization validates"), LoadOddsWellMatchWinnerVoidFinalizations(true, VoidFinalizations, bFound, Error));
	TestEqual(TEXT("Restored exact void finalization remains one record"), VoidFinalizations.Num(), 1);
	TestTrue(TEXT("Canceled-game QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));

	TestTrue(TEXT("Exact loss profile restores after canceled-game QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactLossProfileBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Exact loss remains valid after schema v12"), LoadOddsWellOddsBucksWagerFinalizationState(true, WagerLedger, WagerNextJobPayout, WagerRequests, WagerLocks, WagerResultLinks, WagerDecisions, WagerFinalizations, WagerWinFinalizations, bFound, Error));
	FString H15LossProjectionJson;
	TSharedPtr<FJsonObject> H15LossProjection;
	TestTrue(TEXT("H15 restored exact loss reconciliation reads"), FFileHelper::LoadFileToString(H15LossProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> H15LossProjectionReader = TJsonReaderFactory<>::Create(H15LossProjectionJson);
	TestTrue(TEXT("H15 restored exact loss reconciliation parses"), FJsonSerializer::Deserialize(H15LossProjectionReader, H15LossProjection) && H15LossProjection.IsValid());
	if (H15LossProjection.IsValid())
	{
		H15LossProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedH15LossProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedH15LossProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedH15LossProjectionJson);
		TestTrue(TEXT("H15 restored exact loss reconciliation normalizes"), FJsonSerializer::Serialize(H15LossProjection.ToSharedRef(), NormalizedH15LossProjectionWriter));
		TestEqual(TEXT("H15 leaves exact loss reconciliation unchanged"), NormalizedH15LossProjectionJson, NormalizedMatchWinnerProjectionJson);
	}
	TestEqual(TEXT("Exact loss remains two ledger entries"), WagerLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Exact loss balance remains 60"), WagerLedger.GetBalance(), int64{60});
	TestTrue(TEXT("Exact win profile restores after canceled-game QA"), UGameplayStatics::SaveGameToSlot(UGameplayStatics::LoadGameFromMemory(ExactWinFinalizedBytes), OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Exact win remains valid after schema v12"), LoadOddsWellOddsBucksWagerFinalizationState(true, WinLedger, WinNextJobPayout, WinRequests, WinLocks, WinResults, WinDecisions, WinLossFinalizations, WinFinalizations, bFound, Error));
	FString H15WinProjectionJson;
	TSharedPtr<FJsonObject> H15WinProjection;
	TestTrue(TEXT("H15 restored exact win reconciliation reads"), FFileHelper::LoadFileToString(H15WinProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> H15WinProjectionReader = TJsonReaderFactory<>::Create(H15WinProjectionJson);
	TestTrue(TEXT("H15 restored exact win reconciliation parses"), FJsonSerializer::Deserialize(H15WinProjectionReader, H15WinProjection) && H15WinProjection.IsValid());
	if (H15WinProjection.IsValid())
	{
		H15WinProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedH15WinProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedH15WinProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedH15WinProjectionJson);
		TestTrue(TEXT("H15 restored exact win reconciliation normalizes"), FJsonSerializer::Serialize(H15WinProjection.ToSharedRef(), NormalizedH15WinProjectionWriter));
		TestEqual(TEXT("H15 leaves exact win reconciliation unchanged"), NormalizedH15WinProjectionJson, NormalizedMatchWinnerWinProjectionJson);
	}
	TestEqual(TEXT("Exact win remains three ledger entries"), WinLedger.GetEntries().Num(), 3);
	TestEqual(TEXT("Exact win balance remains 160"), WinLedger.GetBalance(), int64{160});
	TestTrue(TEXT("Final wager QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellUpcomingQaMatchWinnerRequestTest,
	"OddsWell.Economy.UpcomingQaMatchWinnerRequest",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellUpcomingQaMatchWinnerRequestTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H17 QA starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(
		TEXT("Existing job ledger funds H17 QA"),
		Ledger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Job-funded H17 baseline persists"),
		SaveOddsWellOddsBucksLedger(
			Ledger,
			UpcomingQaAcceptedUnixSeconds + GetOddsWellJobPayoutIntervalSeconds(),
			true,
			Error));

	FOddsWellMatchWinnerOffer Offer;
	TestTrue(TEXT("Exact isolated upcoming QA offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, Error));
	TestEqual(TEXT("QA offer is noncanonical"), Offer.SeasonNumber, UpcomingQaSeasonNumber);
	TestTrue(TEXT("Fixed QA acceptance precedes lock"), UpcomingQaAcceptedUnixSeconds < Offer.LockUnixSeconds);
	FOddsWellMatchWinnerRequestRecord Record;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact H17 request is accepted"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
			Offer.HomeTeam,
			40,
			GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
			Record,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	TestEqual(TEXT("One stake leaves 60 Odds Bucks"), Balance, int64{60});
	TestEqual(TEXT("Accepted status remains pending lock"), Record.Status, AcceptedPendingLockStatus);

	int32 Entries = 0;
	int32 Requests = 0;
	TestTrue(TEXT("Cold retry and every rejection remain mutation-free"), RunOddsWellUpcomingQaMatchWinnerAudit(Entries, Requests, Balance, Error));
	TestEqual(TEXT("H17 persists job credit plus one stake debit"), Entries, 2);
	TestEqual(TEXT("H17 persists exactly one request"), Requests, 1);
	TestEqual(TEXT("H17 audit preserves resulting balance"), Balance, int64{60});
	TestTrue(TEXT("H17 QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellPendingQaMatchWinnerReceiptTest,
	"OddsWell.Economy.PendingQaMatchWinnerReceipt",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellPendingQaMatchWinnerReceiptTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H18 QA starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(
		TEXT("Existing job ledger funds H18 QA"),
		Ledger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Job-funded H18 baseline persists"),
		SaveOddsWellOddsBucksLedger(
			Ledger,
			UpcomingQaAcceptedUnixSeconds + GetOddsWellJobPayoutIntervalSeconds(),
			true,
			Error));
	FOddsWellMatchWinnerOffer Offer;
	TestTrue(TEXT("Exact H18 offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact pending request exists for receipt QA"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
			Offer.HomeTeam,
			40,
			GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);

	TArray<uint8> ExactBytes;
	TestTrue(
		TEXT("Exact pending receipt state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			ExactBytes));
	FOddsWellPendingQaMatchWinnerReceipt Receipt;
	TestTrue(TEXT("Exact pending receipt cold-loads"), LoadOddsWellPendingQaMatchWinnerReceipt(Receipt, Error));
	TestEqual(TEXT("Receipt request identity is exact"), Receipt.RequestId, UpcomingQaRequestCommandId);
	TestEqual(TEXT("Receipt offer identity is exact"), Receipt.OfferId, Offer.OfferId);
	TestEqual(TEXT("Receipt offer version is exact"), Receipt.OfferVersion, Offer.OfferVersion);
	TestEqual(TEXT("Receipt selected team is exact"), Receipt.SelectedTeam, Offer.HomeTeam);
	TestEqual(TEXT("Receipt stake is 40"), Receipt.Stake, int64{40});
	TestEqual(TEXT("Receipt accepted time is exact"), Receipt.AcceptedUnixSeconds, UpcomingQaAcceptedUnixSeconds);
	TestEqual(TEXT("Receipt lock time is exact"), Receipt.LockUnixSeconds, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("Receipt remains pending lock"), Receipt.Status, AcceptedPendingLockStatus);
	TestEqual(TEXT("Receipt links ledger sequence two"), Receipt.LedgerSequence, int64{2});
	TestEqual(TEXT("Receipt links the 40 debit"), Receipt.LedgerDelta, int64{-40});
	TestEqual(TEXT("Receipt links the stake reason"), Receipt.LedgerReason, MatchWinnerStakeReason);
	TestEqual(TEXT("Receipt shows current balance 60"), Receipt.CurrentBalance, int64{60});
	TArray<uint8> AfterReadBytes;
	TestTrue(
		TEXT("Exact state serializes after receipt read"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			AfterReadBytes));
	TestTrue(TEXT("Receipt read does not mutate exact state"), ExactBytes == AfterReadBytes);

	auto RestoreExact = [&]()
	{
		return UGameplayStatics::SaveGameToSlot(
			UGameplayStatics::LoadGameFromMemory(ExactBytes),
			OddsBucksQaSlot,
			OddsBucksUserIndex);
	};
	auto RejectMutation = [&](const TCHAR* Label, TFunctionRef<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Mutated = Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromMemory(ExactBytes));
		TestNotNull(FString::Printf(TEXT("%s mutation loads"), Label), Mutated);
		if (!Mutated)
		{
			return;
		}
		Mutate(*Mutated);
		TestTrue(
			FString::Printf(TEXT("%s mutation persists"), Label),
			UGameplayStatics::SaveGameToSlot(Mutated, OddsBucksQaSlot, OddsBucksUserIndex));
		Receipt.RequestId = TEXT("partial");
		Receipt.CurrentBalance = 999;
		Error.Reset();
		TestFalse(
			FString::Printf(TEXT("%s fails closed"), Label),
			LoadOddsWellPendingQaMatchWinnerReceipt(Receipt, Error));
		TestTrue(
			FString::Printf(TEXT("%s exposes no partial values"), Label),
			Receipt.RequestId.IsEmpty() && Receipt.CurrentBalance == 0);
		TestEqual(
			FString::Printf(TEXT("%s returns the generic receipt error"), Label),
			Error,
			FString(TEXT("Pending Match Winner receipt unavailable.")));
		TestTrue(FString::Printf(TEXT("%s exact state restores"), Label), RestoreExact());
	};

	TestTrue(TEXT("Missing-state setup removes the QA save"), ResetOddsWellQaOddsBucksAndVerify(Error));
	Receipt.RequestId = TEXT("partial");
	Receipt.CurrentBalance = 999;
	TestFalse(TEXT("Missing request state fails closed"), LoadOddsWellPendingQaMatchWinnerReceipt(Receipt, Error));
	TestTrue(TEXT("Missing state exposes no partial values"), Receipt.RequestId.IsEmpty() && Receipt.CurrentBalance == 0);
	TestTrue(TEXT("Exact state restores after missing-state QA"), RestoreExact());

	RejectMutation(TEXT("Multiple request evidence"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		const FOddsWellMatchWinnerRequestRecord Duplicate = Save.MatchWinnerRequests[0];
		Save.MatchWinnerRequests.Add(Duplicate);
	});
	RejectMutation(TEXT("Mismatched request identity"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].RequestCommandId += TEXT(":other");
	});
	RejectMutation(TEXT("Mismatched debit identity"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.Entries[1].CommandId += TEXT(":other");
	});
	RejectMutation(TEXT("Mismatched offer identity"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].OfferId = FString::ChrN(64, TEXT('d'));
	});
	RejectMutation(TEXT("Mismatched accepted time"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].AcceptedUnixSeconds++;
	});
	RejectMutation(TEXT("Mismatched request status"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].Status = TEXT("open");
	});
	RejectMutation(TEXT("Wrong debit delta"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.Entries[1].Delta = -39;
		Save.Entries[1].BalanceAfter = 61;
	});
	RejectMutation(TEXT("Wrong debit sequence"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.Entries[1].Sequence = 3;
	});
	RejectMutation(TEXT("Wrong debit balance"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.Entries[1].BalanceAfter = 59;
	});
	RejectMutation(TEXT("Stale offer version"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].OfferVersion = TEXT("basketball-match-winner-odds-v0");
	});
	RejectMutation(TEXT("Duplicate debit evidence"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		const FOddsWellOddsBucksEntry Duplicate = Save.Entries[1];
		Save.Entries.Add(Duplicate);
	});
	RejectMutation(TEXT("Invented lock evidence"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		FOddsWellMatchWinnerLockRecord& Lock = Save.MatchWinnerLocks.AddDefaulted_GetRef();
		Lock.LockCommandId = TEXT("qa:h18:invented-lock");
		Lock.RequestCommandId = UpcomingQaRequestCommandId;
		Lock.SeasonNumber = UpcomingQaSeasonNumber;
		Lock.GameNumber = UpcomingQaGameNumber;
		Lock.AuthoritativeGameStartUnixSeconds = UpcomingQaLockUnixSeconds;
		Lock.LockUnixSeconds = UpcomingQaLockUnixSeconds;
		Lock.Decision = MatchWinnerLockedDecision;
	});
	RejectMutation(TEXT("Invented result evidence"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerResultLinks.AddDefaulted();
	});

	TestTrue(TEXT("Exact receipt restores after fail-closed matrix"), LoadOddsWellPendingQaMatchWinnerReceipt(Receipt, Error));
	TestTrue(TEXT("H18 QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellUpcomingQaMatchWinnerLockTest,
	"OddsWell.Economy.UpcomingQaMatchWinnerLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellUpcomingQaMatchWinnerLockTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H19 QA starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(
		TEXT("Existing job ledger funds H19 QA"),
		Ledger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Job-funded H19 baseline persists"),
		SaveOddsWellOddsBucksLedger(Ledger, UpcomingQaLockUnixSeconds, true, Error));
	FOddsWellMatchWinnerOffer Offer;
	TestTrue(TEXT("Exact H19 offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact H17 request exists before H19 lock"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			UpcomingQaRequestCommandId,
			Offer.HomeTeam,
			40,
			UpcomingQaAcceptedUnixSeconds,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);

	TArray<uint8> PendingBytes;
	TestTrue(
		TEXT("Exact pre-lock state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			PendingBytes));
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("Server-owned exact game-start command locks once"),
		LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Lock, Error),
		EOddsWellMatchWinnerLockResult::Locked);
	TestEqual(TEXT("H19 lock command identity is fixed"), Lock.LockCommandId, UpcomingQaLockCommandId);
	TestEqual(TEXT("H19 lock request identity is fixed"), Lock.RequestCommandId, UpcomingQaRequestCommandId);
	TestEqual(TEXT("H19 lock season is isolated"), Lock.SeasonNumber, UpcomingQaSeasonNumber);
	TestEqual(TEXT("H19 lock game is isolated"), Lock.GameNumber, UpcomingQaGameNumber);
	TestEqual(TEXT("H19 authority time is exact"), Lock.AuthoritativeGameStartUnixSeconds, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H19 stored lock time is exact"), Lock.LockUnixSeconds, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H19 decision is immutable locked"), Lock.Decision, MatchWinnerLockedDecision);

	FOddsWellOddsBucksLedger LockedLedger;
	int64 LockedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> LockedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> LockedLocks;
	TestTrue(
		TEXT("Exact locked chain reloads"),
		LoadExactUpcomingQaLockState(
			LockedLedger,
			LockedNextJobPayout,
			LockedRequests,
			LockedLocks,
			Error));
	TestEqual(TEXT("H17 job credit and debit remain the only ledger entries"), LockedLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("H17 balance remains 60"), LockedLedger.GetBalance(), int64{60});
	TestEqual(TEXT("H17 cooldown remains byte-for-value"), LockedNextJobPayout, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H17 request count remains one"), LockedRequests.Num(), 1);
	TestEqual(TEXT("H19 lock count is exactly one"), LockedLocks.Num(), 1);
	if (LockedLedger.GetEntries().Num() == 2 && LockedRequests.Num() == 1)
	{
		const FOddsWellOddsBucksEntry& Credit = LockedLedger.GetEntries()[0];
		const FOddsWellOddsBucksEntry& Debit = LockedLedger.GetEntries()[1];
		const FOddsWellMatchWinnerRequestRecord& SavedRequest = LockedRequests[0];
		TestEqual(TEXT("Credit sequence remains one"), Credit.Sequence, int64{1});
		TestEqual(TEXT("Credit command remains exact"), Credit.CommandId, GetOddsWellFirstJobCommandId());
		TestEqual(TEXT("Credit delta remains 100"), Credit.Delta, int64{100});
		TestEqual(TEXT("Credit balance remains 100"), Credit.BalanceAfter, int64{100});
		TestEqual(TEXT("Debit sequence remains two"), Debit.Sequence, int64{2});
		TestEqual(TEXT("Debit command remains the H17 request"), Debit.CommandId, UpcomingQaRequestCommandId);
		TestEqual(TEXT("Debit remains minus 40"), Debit.Delta, int64{-40});
		TestEqual(TEXT("Debit balance remains 60"), Debit.BalanceAfter, int64{60});
		TestEqual(TEXT("Debit reason remains match winner stake"), Debit.Reason, MatchWinnerStakeReason);
		TestEqual(TEXT("Request offer identity remains exact"), SavedRequest.OfferId, Offer.OfferId);
		TestEqual(TEXT("Request offer version remains exact"), SavedRequest.OfferVersion, Offer.OfferVersion);
		TestEqual(TEXT("Request home team remains Sparks"), SavedRequest.HomeTeam, Offer.HomeTeam);
		TestEqual(TEXT("Request away team remains Rivals"), SavedRequest.AwayTeam, Offer.AwayTeam);
		TestEqual(TEXT("Selected team remains Sparks"), SavedRequest.OfferedTeam, Offer.HomeTeam);
		TestEqual(TEXT("Stake remains 40"), SavedRequest.Stake, int64{40});
		TestEqual(TEXT("Accepted time remains exact"), SavedRequest.AcceptedUnixSeconds, UpcomingQaAcceptedUnixSeconds);
		TestEqual(TEXT("Request lock time remains exact"), SavedRequest.LockUnixSeconds, UpcomingQaLockUnixSeconds);
		TestEqual(TEXT("Request remains accepted pending lock"), SavedRequest.Status, AcceptedPendingLockStatus);
	}

	const UOddsWellOddsBucksSaveGame* ExactLocked = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestNotNull(TEXT("Exact locked save reloads for zero-result proof"), ExactLocked);
	if (ExactLocked)
	{
		TestTrue(TEXT("H19 adds no result links"), ExactLocked->MatchWinnerResultLinks.IsEmpty());
		TestTrue(TEXT("H19 adds no settlement decisions"), ExactLocked->MatchWinnerSettlementDecisions.IsEmpty());
		TestTrue(TEXT("H19 adds no loss finalizations"), ExactLocked->MatchWinnerLossFinalizations.IsEmpty());
		TestTrue(TEXT("H19 adds no win finalizations"), ExactLocked->MatchWinnerWinFinalizations.IsEmpty());
		TestTrue(TEXT("H19 adds no cancellations"), ExactLocked->MatchWinnerCanceledGames.IsEmpty());
		TestTrue(TEXT("H19 adds no void decisions"), ExactLocked->MatchWinnerVoidDecisions.IsEmpty());
		TestTrue(TEXT("H19 adds no void finalizations"), ExactLocked->MatchWinnerVoidFinalizations.IsEmpty());
	}

	TArray<uint8> LockedBytes;
	TestTrue(
		TEXT("Exact locked state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			LockedBytes));
	int32 Entries = 0;
	int32 Requests = 0;
	int32 Locks = 0;
	TestTrue(
		TEXT("Cold retry and lock rejection matrix are byte-stable"),
		RunOddsWellUpcomingQaMatchWinnerLockAudit(Entries, Requests, Locks, Balance, Error));
	TestEqual(TEXT("H19 audit preserves two ledger entries"), Entries, 2);
	TestEqual(TEXT("H19 audit preserves one request"), Requests, 1);
	TestEqual(TEXT("H19 audit preserves one lock"), Locks, 1);
	TestEqual(TEXT("H19 audit preserves balance 60"), Balance, int64{60});

	auto RestoreExactLocked = [&]()
	{
		return UGameplayStatics::SaveGameToSlot(
			UGameplayStatics::LoadGameFromMemory(LockedBytes),
			OddsBucksQaSlot,
			OddsBucksUserIndex);
	};
	auto RejectMutation = [&](const TCHAR* Label, TFunctionRef<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Mutated = Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromMemory(LockedBytes));
		TestNotNull(FString::Printf(TEXT("%s mutation loads"), Label), Mutated);
		if (!Mutated)
		{
			return;
		}
		Mutate(*Mutated);
		TestTrue(
			FString::Printf(TEXT("%s mutation persists"), Label),
			UGameplayStatics::SaveGameToSlot(Mutated, OddsBucksQaSlot, OddsBucksUserIndex));
		Error.Reset();
		TestEqual(
			FString::Printf(TEXT("%s rejects exact H19 command"), Label),
			LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Lock, Error),
			EOddsWellMatchWinnerLockResult::Rejected);
		TestTrue(FString::Printf(TEXT("%s exact locked state restores"), Label), RestoreExactLocked());
	};
	RejectMutation(TEXT("Malformed request"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].RequestCommandId += TEXT(":malformed");
	});
	RejectMutation(TEXT("Malformed debit"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.Entries[1].Delta = -39;
		Save.Entries[1].BalanceAfter = 61;
	});
	RejectMutation(TEXT("Malformed offer"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].OfferId = FString::ChrN(64, TEXT('d'));
	});
	TArray<uint8> RestoredLockedBytes;
	TestTrue(
		TEXT("Restored exact lock state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			RestoredLockedBytes));
	TestTrue(TEXT("All tamper rejections preserve the exact locked bytes"), RestoredLockedBytes == LockedBytes);
	TestTrue(TEXT("H19 QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellUpcomingQaMatchWinnerCancellationTest,
	"OddsWell.Economy.UpcomingQaMatchWinnerCancellation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellUpcomingQaMatchWinnerCancellationTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H20 QA starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(
		TEXT("Existing job ledger funds H20 QA"),
		Ledger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Job-funded H20 baseline persists"),
		SaveOddsWellOddsBucksLedger(Ledger, UpcomingQaLockUnixSeconds, true, Error));
	FOddsWellMatchWinnerOffer Offer;
	TestTrue(TEXT("Exact H20 offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact H17 request exists before H20 cancellation"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			UpcomingQaRequestCommandId,
			Offer.HomeTeam,
			40,
			UpcomingQaAcceptedUnixSeconds,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("Exact H19 lock exists before H20 cancellation"),
		LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Lock, Error),
		EOddsWellMatchWinnerLockResult::Locked);

	TArray<uint8> LockedBytes;
	TestTrue(
		TEXT("Exact H19 locked state serializes before H20"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			LockedBytes));
	FOddsWellMatchWinnerCanceledGameRecord Cancellation;
	TestEqual(
		TEXT("Server-owned exact post-lock cancellation records once"),
		RecordOddsWellUpcomingQaMatchWinnerCancellation(Cancellation, Error),
		EOddsWellMatchWinnerCanceledGameResult::Recorded);
	TestEqual(TEXT("H20 cancellation command identity is fixed"), Cancellation.CancellationCommandId, UpcomingQaCancellationCommandId);
	TestEqual(TEXT("H20 cancellation evidence identity is fixed"), Cancellation.CancellationEvidenceId, UpcomingQaCancellationEvidenceId);
	TestEqual(TEXT("H20 request link is exact"), Cancellation.RequestCommandId, UpcomingQaRequestCommandId);
	TestEqual(TEXT("H20 lock link is exact"), Cancellation.LockCommandId, UpcomingQaLockCommandId);
	TestEqual(TEXT("H20 season is isolated"), Cancellation.SeasonNumber, UpcomingQaSeasonNumber);
	TestEqual(TEXT("H20 game is isolated"), Cancellation.GameNumber, UpcomingQaGameNumber);
	TestEqual(TEXT("H20 cancellation time is exact"), Cancellation.AuthoritativeCancellationUnixSeconds, UpcomingQaCancellationUnixSeconds);
	TestTrue(TEXT("H20 cancellation is strictly post-lock"), Cancellation.AuthoritativeCancellationUnixSeconds > UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H20 reason is neutral game canceled"), Cancellation.ReasonCode, MatchWinnerCanceledGameReason);
	TestEqual(TEXT("H20 status is immutable closed canceled"), Cancellation.Status, MatchWinnerClosedCanceledStatus);

	FOddsWellOddsBucksLedger CanceledLedger;
	int64 CanceledNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> CanceledRequests;
	TArray<FOddsWellMatchWinnerLockRecord> CanceledLocks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> CanceledGames;
	TestTrue(
		TEXT("Exact canceled chain reloads"),
		LoadExactUpcomingQaLockState(
			CanceledLedger,
			CanceledNextJobPayout,
			CanceledRequests,
			CanceledLocks,
			Error,
			&CanceledGames));
	TestEqual(TEXT("H17 ledger remains exactly two entries"), CanceledLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("H17 balance remains 60"), CanceledLedger.GetBalance(), int64{60});
	TestEqual(TEXT("H17 cooldown remains byte-for-value"), CanceledNextJobPayout, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H17 request count remains one"), CanceledRequests.Num(), 1);
	TestEqual(TEXT("H19 lock count remains one"), CanceledLocks.Num(), 1);
	TestEqual(TEXT("H20 cancellation count is exactly one"), CanceledGames.Num(), 1);
	if (CanceledLedger.GetEntries().Num() == 2 && CanceledRequests.Num() == 1 && CanceledLocks.Num() == 1)
	{
		const FOddsWellOddsBucksEntry& Credit = CanceledLedger.GetEntries()[0];
		const FOddsWellOddsBucksEntry& Debit = CanceledLedger.GetEntries()[1];
		const FOddsWellMatchWinnerRequestRecord& SavedRequest = CanceledRequests[0];
		const FOddsWellMatchWinnerLockRecord& SavedLock = CanceledLocks[0];
		TestEqual(TEXT("Credit sequence remains one"), Credit.Sequence, int64{1});
		TestEqual(TEXT("Credit command remains exact"), Credit.CommandId, GetOddsWellFirstJobCommandId());
		TestEqual(TEXT("Credit delta remains 100"), Credit.Delta, int64{100});
		TestEqual(TEXT("Credit balance remains 100"), Credit.BalanceAfter, int64{100});
		TestEqual(TEXT("Debit sequence remains two"), Debit.Sequence, int64{2});
		TestEqual(TEXT("Debit command remains H17 request"), Debit.CommandId, UpcomingQaRequestCommandId);
		TestEqual(TEXT("Debit remains minus 40"), Debit.Delta, int64{-40});
		TestEqual(TEXT("Debit balance remains 60"), Debit.BalanceAfter, int64{60});
		TestEqual(TEXT("Debit reason remains match winner stake"), Debit.Reason, MatchWinnerStakeReason);
		TestEqual(TEXT("Request offer remains exact"), SavedRequest.OfferId, Offer.OfferId);
		TestEqual(TEXT("Request selected team remains Sparks"), SavedRequest.OfferedTeam, Offer.HomeTeam);
		TestEqual(TEXT("Request stake remains 40"), SavedRequest.Stake, int64{40});
		TestEqual(TEXT("Request accepted time remains exact"), SavedRequest.AcceptedUnixSeconds, UpcomingQaAcceptedUnixSeconds);
		TestEqual(TEXT("Request lock time remains exact"), SavedRequest.LockUnixSeconds, UpcomingQaLockUnixSeconds);
		TestEqual(TEXT("Request remains accepted pending lock"), SavedRequest.Status, AcceptedPendingLockStatus);
		TestEqual(TEXT("Lock command remains exact"), SavedLock.LockCommandId, UpcomingQaLockCommandId);
		TestEqual(TEXT("Lock authority time remains exact"), SavedLock.AuthoritativeGameStartUnixSeconds, UpcomingQaLockUnixSeconds);
		TestEqual(TEXT("Lock decision remains locked"), SavedLock.Decision, MatchWinnerLockedDecision);
	}

	const UOddsWellOddsBucksSaveGame* ExactCanceled = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestNotNull(TEXT("Exact canceled save reloads for zero-downstream proof"), ExactCanceled);
	if (ExactCanceled)
	{
		TestTrue(TEXT("H20 adds no result links"), ExactCanceled->MatchWinnerResultLinks.IsEmpty());
		TestTrue(TEXT("H20 adds no settlement decisions"), ExactCanceled->MatchWinnerSettlementDecisions.IsEmpty());
		TestTrue(TEXT("H20 adds no loss finalizations"), ExactCanceled->MatchWinnerLossFinalizations.IsEmpty());
		TestTrue(TEXT("H20 adds no win finalizations"), ExactCanceled->MatchWinnerWinFinalizations.IsEmpty());
		TestTrue(TEXT("H20 adds no void decisions"), ExactCanceled->MatchWinnerVoidDecisions.IsEmpty());
		TestTrue(TEXT("H20 adds no refund/finalization"), ExactCanceled->MatchWinnerVoidFinalizations.IsEmpty());
	}

	TArray<uint8> CanceledBytes;
	TestTrue(
		TEXT("Exact H20 canceled state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			CanceledBytes));
	int32 Entries = 0;
	int32 Requests = 0;
	int32 Locks = 0;
	int32 Cancellations = 0;
	TestTrue(
		TEXT("Cold retry and cancellation rejection matrix are byte-stable"),
		RunOddsWellUpcomingQaMatchWinnerCancellationAudit(
			Entries,
			Requests,
			Locks,
			Cancellations,
			Balance,
			Error));
	TestEqual(TEXT("H20 audit preserves two ledger entries"), Entries, 2);
	TestEqual(TEXT("H20 audit preserves one request"), Requests, 1);
	TestEqual(TEXT("H20 audit preserves one lock"), Locks, 1);
	TestEqual(TEXT("H20 audit preserves one cancellation"), Cancellations, 1);
	TestEqual(TEXT("H20 audit preserves balance 60"), Balance, int64{60});

	auto RestoreExactCanceled = [&]()
	{
		return UGameplayStatics::SaveGameToSlot(
			UGameplayStatics::LoadGameFromMemory(CanceledBytes),
			OddsBucksQaSlot,
			OddsBucksUserIndex);
	};
	auto RejectMutation = [&](const TCHAR* Label, TFunctionRef<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Mutated = Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromMemory(CanceledBytes));
		TestNotNull(FString::Printf(TEXT("%s mutation loads"), Label), Mutated);
		if (!Mutated)
		{
			return;
		}
		Mutate(*Mutated);
		TestTrue(
			FString::Printf(TEXT("%s mutation persists"), Label),
			UGameplayStatics::SaveGameToSlot(Mutated, OddsBucksQaSlot, OddsBucksUserIndex));
		Error.Reset();
		TestEqual(
			FString::Printf(TEXT("%s rejects exact H20 command"), Label),
			RecordOddsWellUpcomingQaMatchWinnerCancellation(Cancellation, Error),
			EOddsWellMatchWinnerCanceledGameResult::Rejected);
		TestTrue(FString::Printf(TEXT("%s exact canceled state restores"), Label), RestoreExactCanceled());
	};
	RejectMutation(TEXT("Malformed H17 request"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].Stake = 39;
	});
	RejectMutation(TEXT("Malformed H19 lock"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerLocks[0].AuthoritativeGameStartUnixSeconds += 1;
	});
	RejectMutation(TEXT("Malformed H20 cancellation"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerCanceledGames[0].Status = TEXT("open");
	});
	RejectMutation(TEXT("Fabricated normal result"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerResultLinks.AddDefaulted();
	});
	TArray<uint8> RestoredCanceledBytes;
	TestTrue(
		TEXT("Restored exact cancellation state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			RestoredCanceledBytes));
	TestTrue(TEXT("Every tamper rejection preserves exact canceled bytes"), RestoredCanceledBytes == CanceledBytes);
	TestTrue(TEXT("H20 QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellUpcomingQaMatchWinnerVoidDecisionTest,
	"OddsWell.Economy.UpcomingQaMatchWinnerVoidDecision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellUpcomingQaMatchWinnerVoidDecisionTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H21 QA starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(
		TEXT("Existing job ledger funds H21 QA"),
		Ledger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Job-funded H21 baseline persists"),
		SaveOddsWellOddsBucksLedger(Ledger, UpcomingQaLockUnixSeconds, true, Error));
	FOddsWellMatchWinnerOffer Offer;
	TestTrue(TEXT("Exact H21 offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact H17 request exists before H21"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			UpcomingQaRequestCommandId,
			Offer.HomeTeam,
			40,
			UpcomingQaAcceptedUnixSeconds,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("Exact H19 lock exists before H21"),
		LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Lock, Error),
		EOddsWellMatchWinnerLockResult::Locked);
	FOddsWellMatchWinnerCanceledGameRecord Cancellation;
	TestEqual(
		TEXT("Exact H20 cancellation exists before H21"),
		RecordOddsWellUpcomingQaMatchWinnerCancellation(Cancellation, Error),
		EOddsWellMatchWinnerCanceledGameResult::Recorded);

	TArray<uint8> CanceledBytes;
	TestTrue(
		TEXT("Exact H20 canceled state serializes before H21"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			CanceledBytes));
	FOddsWellMatchWinnerVoidDecisionRecord Decision;
	TestEqual(
		TEXT("Server-owned exact void/refund-due decision records once"),
		DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(Decision, Error),
		EOddsWellMatchWinnerVoidDecisionResult::Decided);
	TestEqual(TEXT("H21 decision command is fixed"), Decision.VoidDecisionCommandId, UpcomingQaVoidDecisionCommandId);
	TestEqual(TEXT("H21 cancellation command link is exact"), Decision.CancellationCommandId, UpcomingQaCancellationCommandId);
	TestEqual(TEXT("H21 cancellation evidence link is exact"), Decision.CancellationEvidenceId, UpcomingQaCancellationEvidenceId);
	TestEqual(TEXT("H21 request link is exact"), Decision.RequestCommandId, UpcomingQaRequestCommandId);
	TestEqual(TEXT("H21 lock link is exact"), Decision.LockCommandId, UpcomingQaLockCommandId);
	TestEqual(TEXT("H21 offer identity is exact"), Decision.OfferId, Offer.OfferId);
	TestEqual(TEXT("H21 offer schema is exact"), Decision.OfferSchema, MatchWinnerOfferSchema);
	TestEqual(TEXT("H21 offer version is exact"), Decision.OfferVersion, Offer.OfferVersion);
	TestEqual(TEXT("H21 season is isolated"), Decision.SeasonNumber, UpcomingQaSeasonNumber);
	TestEqual(TEXT("H21 game is isolated"), Decision.GameNumber, UpcomingQaGameNumber);
	TestEqual(TEXT("H21 selected team remains Sparks"), Decision.SelectedTeam, Offer.HomeTeam);
	TestEqual(TEXT("H21 stake remains 40"), Decision.Stake, int64{40});
	TestEqual(TEXT("H21 reason remains game canceled"), Decision.CancellationReason, MatchWinnerCanceledGameReason);
	TestEqual(TEXT("H21 outcome is voided"), Decision.Outcome, MatchWinnerVoidedOutcome);
	TestEqual(TEXT("H21 refund due is exactly the stake"), Decision.RefundDue, int64{40});
	TestEqual(TEXT("H21 remains pending refund"), Decision.Status, MatchWinnerDecidedVoidPendingRefundStatus);

	FOddsWellOddsBucksLedger DecidedLedger;
	int64 DecidedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> DecidedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> DecidedLocks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> DecidedCancellations;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> DecidedVoidDecisions;
	TestTrue(
		TEXT("Exact H21 chain reloads"),
		LoadExactUpcomingQaLockState(
			DecidedLedger,
			DecidedNextJobPayout,
			DecidedRequests,
			DecidedLocks,
			Error,
			&DecidedCancellations,
			&DecidedVoidDecisions));
	TestEqual(TEXT("H17 ledger remains exactly two entries"), DecidedLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("H17/H21 balance remains 60"), DecidedLedger.GetBalance(), int64{60});
	TestEqual(TEXT("H17 cooldown remains exact"), DecidedNextJobPayout, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H17 request remains singular"), DecidedRequests.Num(), 1);
	TestEqual(TEXT("H19 lock remains singular"), DecidedLocks.Num(), 1);
	TestEqual(TEXT("H20 cancellation remains singular"), DecidedCancellations.Num(), 1);
	TestEqual(TEXT("H21 decision count is one"), DecidedVoidDecisions.Num(), 1);
	if (DecidedLedger.GetEntries().Num() == 2 && DecidedRequests.Num() == 1 && DecidedLocks.Num() == 1)
	{
		const FOddsWellOddsBucksEntry& Debit = DecidedLedger.GetEntries()[1];
		TestEqual(TEXT("Stake debit sequence remains two"), Debit.Sequence, int64{2});
		TestEqual(TEXT("Stake debit command remains H17 request"), Debit.CommandId, UpcomingQaRequestCommandId);
		TestEqual(TEXT("Stake debit remains minus 40"), Debit.Delta, int64{-40});
		TestEqual(TEXT("Stake debit balance remains 60"), Debit.BalanceAfter, int64{60});
		TestEqual(TEXT("H17 request selection remains Sparks"), DecidedRequests[0].OfferedTeam, Offer.HomeTeam);
		TestEqual(TEXT("H17 request stake remains 40"), DecidedRequests[0].Stake, int64{40});
		TestEqual(TEXT("H19 lock command remains exact"), DecidedLocks[0].LockCommandId, UpcomingQaLockCommandId);
		TestEqual(TEXT("H19 lock decision remains locked"), DecidedLocks[0].Decision, MatchWinnerLockedDecision);
	}
	const UOddsWellOddsBucksSaveGame* ExactDecision = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestNotNull(TEXT("Exact H21 save reloads for no-application proof"), ExactDecision);
	if (ExactDecision)
	{
		TestTrue(TEXT("H21 has no normal result"), ExactDecision->MatchWinnerResultLinks.IsEmpty());
		TestTrue(TEXT("H21 has no normal settlement"), ExactDecision->MatchWinnerSettlementDecisions.IsEmpty());
		TestTrue(TEXT("H21 has no loss finalization"), ExactDecision->MatchWinnerLossFinalizations.IsEmpty());
		TestTrue(TEXT("H21 has no win finalization"), ExactDecision->MatchWinnerWinFinalizations.IsEmpty());
		TestTrue(TEXT("H21 applies no refund or void finalization"), ExactDecision->MatchWinnerVoidFinalizations.IsEmpty());
	}

	TArray<uint8> DecisionBytes;
	TestTrue(
		TEXT("Exact H21 decision state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			DecisionBytes));
	int32 Entries = 0;
	int32 Requests = 0;
	int32 Locks = 0;
	int32 Cancellations = 0;
	int32 VoidDecisions = 0;
	TestTrue(
		TEXT("Cold retry and void-decision rejection matrix are byte-stable"),
		RunOddsWellUpcomingQaMatchWinnerVoidDecisionAudit(
			Entries,
			Requests,
			Locks,
			Cancellations,
			VoidDecisions,
			Balance,
			Error));
	TestEqual(TEXT("H21 audit preserves two ledger entries"), Entries, 2);
	TestEqual(TEXT("H21 audit preserves one request"), Requests, 1);
	TestEqual(TEXT("H21 audit preserves one lock"), Locks, 1);
	TestEqual(TEXT("H21 audit preserves one cancellation"), Cancellations, 1);
	TestEqual(TEXT("H21 audit preserves one void decision"), VoidDecisions, 1);
	TestEqual(TEXT("H21 audit preserves balance 60"), Balance, int64{60});

	auto RestoreExactDecision = [&]()
	{
		return UGameplayStatics::SaveGameToSlot(
			UGameplayStatics::LoadGameFromMemory(DecisionBytes),
			OddsBucksQaSlot,
			OddsBucksUserIndex);
	};
	auto RejectMutation = [&](const TCHAR* Label, TFunctionRef<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Mutated = Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromMemory(DecisionBytes));
		TestNotNull(FString::Printf(TEXT("%s mutation loads"), Label), Mutated);
		if (!Mutated)
		{
			return;
		}
		Mutate(*Mutated);
		TestTrue(
			FString::Printf(TEXT("%s mutation persists"), Label),
			UGameplayStatics::SaveGameToSlot(Mutated, OddsBucksQaSlot, OddsBucksUserIndex));
		Error.Reset();
		TestEqual(
			FString::Printf(TEXT("%s rejects exact H21 command"), Label),
			DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(Decision, Error),
			EOddsWellMatchWinnerVoidDecisionResult::Rejected);
		TestTrue(FString::Printf(TEXT("%s exact H21 state restores"), Label), RestoreExactDecision());
	};
	RejectMutation(TEXT("Wrong cancellation status"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerCanceledGames.IsEmpty())
		{
			Save.MatchWinnerCanceledGames[0].Status = TEXT("open");
		}
	});
	RejectMutation(TEXT("Wrong refund amount"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidDecisions.IsEmpty())
		{
			Save.MatchWinnerVoidDecisions[0].RefundDue = 41;
		}
	});
	RejectMutation(TEXT("Wrong decision status"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidDecisions.IsEmpty())
		{
			Save.MatchWinnerVoidDecisions[0].Status = TEXT("settled_void");
		}
	});
	RejectMutation(TEXT("Wrong decision link"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidDecisions.IsEmpty())
		{
			Save.MatchWinnerVoidDecisions[0].CancellationEvidenceId = TEXT("qa:h21:invented-evidence");
		}
	});
	RejectMutation(TEXT("Normal result overlap"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerResultLinks.AddDefaulted();
	});
	TArray<uint8> RestoredDecisionBytes;
	TestTrue(
		TEXT("Restored exact H21 state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			RestoredDecisionBytes));
	TestTrue(TEXT("Every H21 tamper rejection preserves exact bytes"), RestoredDecisionBytes == DecisionBytes);
	TestTrue(TEXT("H21 QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellUpcomingQaMatchWinnerVoidFinalizationTest,
	"OddsWell.Economy.UpcomingQaMatchWinnerVoidFinalization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellUpcomingQaMatchWinnerVoidFinalizationTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H22 QA starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Ledger;
	TestEqual(
		TEXT("Existing job ledger funds H22 QA"),
		Ledger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Job-funded H22 baseline persists"),
		SaveOddsWellOddsBucksLedger(Ledger, UpcomingQaLockUnixSeconds, true, Error));
	FOddsWellMatchWinnerOffer Offer;
	TestTrue(TEXT("Exact H22 offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(Offer, Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact H17 request exists before H22"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			Offer,
			UpcomingQaRequestCommandId,
			Offer.HomeTeam,
			40,
			UpcomingQaAcceptedUnixSeconds,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("Exact H19 lock exists before H22"),
		LockOddsWellUpcomingQaMatchWinnerRequestAtGameStart(Lock, Error),
		EOddsWellMatchWinnerLockResult::Locked);
	FOddsWellMatchWinnerCanceledGameRecord Cancellation;
	TestEqual(
		TEXT("Exact H20 cancellation exists before H22"),
		RecordOddsWellUpcomingQaMatchWinnerCancellation(Cancellation, Error),
		EOddsWellMatchWinnerCanceledGameResult::Recorded);
	FOddsWellMatchWinnerVoidDecisionRecord Decision;
	TestEqual(
		TEXT("Exact H21 refund-due decision exists before H22"),
		DecideOddsWellUpcomingQaMatchWinnerVoidRefundDue(Decision, Error),
		EOddsWellMatchWinnerVoidDecisionResult::Decided);

	FOddsWellMatchWinnerVoidFinalizationRecord Finalization;
	TestEqual(
		TEXT("Server-owned exact refund applies and finalizes once"),
		FinalizeOddsWellUpcomingQaMatchWinnerVoidRefund(Finalization, Error),
		EOddsWellMatchWinnerVoidFinalizationResult::Finalized);
	TestEqual(TEXT("H22 finalization command is fixed"), Finalization.FinalizationCommandId, UpcomingQaVoidFinalizationCommandId);
	TestEqual(TEXT("H22 decision link is exact"), Finalization.VoidDecisionCommandId, UpcomingQaVoidDecisionCommandId);
	TestEqual(TEXT("H22 cancellation command link is exact"), Finalization.CancellationCommandId, UpcomingQaCancellationCommandId);
	TestEqual(TEXT("H22 cancellation evidence link is exact"), Finalization.CancellationEvidenceId, UpcomingQaCancellationEvidenceId);
	TestEqual(TEXT("H22 request link is exact"), Finalization.RequestCommandId, UpcomingQaRequestCommandId);
	TestEqual(TEXT("H22 lock link is exact"), Finalization.LockCommandId, UpcomingQaLockCommandId);
	TestEqual(TEXT("H22 offer identity is exact"), Finalization.OfferId, Offer.OfferId);
	TestEqual(TEXT("H22 offer schema is exact"), Finalization.OfferSchema, MatchWinnerOfferSchema);
	TestEqual(TEXT("H22 offer version is exact"), Finalization.OfferVersion, Offer.OfferVersion);
	TestEqual(TEXT("H22 season is isolated"), Finalization.SeasonNumber, UpcomingQaSeasonNumber);
	TestEqual(TEXT("H22 game is isolated"), Finalization.GameNumber, UpcomingQaGameNumber);
	TestEqual(TEXT("H22 selected team remains Sparks"), Finalization.SelectedTeam, Offer.HomeTeam);
	TestEqual(TEXT("H22 stake remains 40"), Finalization.Stake, int64{40});
	TestEqual(TEXT("H22 reason remains game canceled"), Finalization.CancellationReason, MatchWinnerCanceledGameReason);
	TestEqual(TEXT("H22 outcome remains voided"), Finalization.Outcome, MatchWinnerVoidedOutcome);
	TestEqual(TEXT("H22 refund due remains 40"), Finalization.RefundDue, int64{40});
	TestEqual(TEXT("H22 refund applies exactly 40"), Finalization.RefundApplied, int64{40});
	TestEqual(TEXT("H22 refund ledger command is fixed"), Finalization.RefundLedgerCommandId, UpcomingQaVoidFinalizationCommandId);
	TestEqual(TEXT("H22 status is settled void"), Finalization.Status, MatchWinnerSettledVoidStatus);
	TestEqual(TEXT("H22 observes three ledger entries"), Finalization.ObservedLedgerEntryCount, 3);
	TestEqual(TEXT("H22 observes balance 100"), Finalization.ObservedFinalBalance, int64{100});

	FOddsWellOddsBucksLedger FinalizedLedger;
	int64 FinalizedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> FinalizedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> FinalizedLocks;
	TArray<FOddsWellMatchWinnerCanceledGameRecord> FinalizedCancellations;
	TArray<FOddsWellMatchWinnerVoidDecisionRecord> FinalizedVoidDecisions;
	TArray<FOddsWellMatchWinnerVoidFinalizationRecord> FinalizedVoidFinalizations;
	TestTrue(
		TEXT("Exact H22 chain reloads"),
		LoadExactUpcomingQaLockState(
			FinalizedLedger,
			FinalizedNextJobPayout,
			FinalizedRequests,
			FinalizedLocks,
			Error,
			&FinalizedCancellations,
			&FinalizedVoidDecisions,
			&FinalizedVoidFinalizations));
	TestEqual(TEXT("H22 ledger has exactly three entries"), FinalizedLedger.GetEntries().Num(), 3);
	TestEqual(TEXT("H22 balance is exactly 100"), FinalizedLedger.GetBalance(), int64{100});
	TestEqual(TEXT("H17 cooldown remains exact"), FinalizedNextJobPayout, UpcomingQaLockUnixSeconds);
	TestEqual(TEXT("H17 request remains singular"), FinalizedRequests.Num(), 1);
	TestEqual(TEXT("H19 lock remains singular"), FinalizedLocks.Num(), 1);
	TestEqual(TEXT("H20 cancellation remains singular"), FinalizedCancellations.Num(), 1);
	TestEqual(TEXT("H21 decision remains singular"), FinalizedVoidDecisions.Num(), 1);
	TestEqual(TEXT("H22 finalization remains singular"), FinalizedVoidFinalizations.Num(), 1);
	if (FinalizedLedger.GetEntries().Num() == 3 && FinalizedVoidDecisions.Num() == 1)
	{
		const FOddsWellOddsBucksEntry& Refund = FinalizedLedger.GetEntries()[2];
		TestEqual(TEXT("Refund entry is sequence three"), Refund.Sequence, int64{3});
		TestEqual(TEXT("Refund entry command is H22"), Refund.CommandId, UpcomingQaVoidFinalizationCommandId);
		TestEqual(TEXT("Refund entry is plus 40"), Refund.Delta, int64{40});
		TestEqual(TEXT("Refund entry reaches 100"), Refund.BalanceAfter, int64{100});
		TestEqual(TEXT("Refund entry reason is exact"), Refund.Reason, MatchWinnerRefundReason);
		TestEqual(TEXT("H21 remains pending and immutable"), FinalizedVoidDecisions[0].Status, MatchWinnerDecidedVoidPendingRefundStatus);
		TestEqual(TEXT("H21 refund due remains 40"), FinalizedVoidDecisions[0].RefundDue, int64{40});
	}
	const FString MatchWinnerProjectionPath = GetMatchWinnerReconciliationPath(true);
	TestTrue(TEXT("H25 publishes exact upcoming QA history"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString UpcomingVoidProjectionJson;
	TSharedPtr<FJsonObject> UpcomingVoidProjection;
	TestTrue(TEXT("H25 exact upcoming QA history reads"), FFileHelper::LoadFileToString(UpcomingVoidProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> UpcomingVoidProjectionReader = TJsonReaderFactory<>::Create(UpcomingVoidProjectionJson);
	TestTrue(TEXT("H25 exact upcoming QA history parses"), FJsonSerializer::Deserialize(UpcomingVoidProjectionReader, UpcomingVoidProjection) && UpcomingVoidProjection.IsValid());
	FString NormalizedUpcomingVoidProjectionJson;
	if (UpcomingVoidProjection.IsValid())
	{
		TestEqual(TEXT("H25 keeps reconciliation v1"), UpcomingVoidProjection->GetStringField(TEXT("schema")), MatchWinnerReconciliationSchema);
		TestEqual(TEXT("H25 binds exact offer"), UpcomingVoidProjection->GetStringField(TEXT("offer_id")), UpcomingQaOfferId);
		TestEqual(TEXT("H25 binds H17 request"), UpcomingVoidProjection->GetStringField(TEXT("request_command_id")), UpcomingQaRequestCommandId);
		TestEqual(TEXT("H25 binds H19 lock"), UpcomingVoidProjection->GetStringField(TEXT("lock_command_id")), UpcomingQaLockCommandId);
		TestEqual(TEXT("H25 canonicalizes H19 locked decision"), UpcomingVoidProjection->GetStringField(TEXT("lock_decision")), TEXT("locked"));
		TestEqual(TEXT("H25 binds H20 cancellation"), UpcomingVoidProjection->GetStringField(TEXT("cancellation_command_id")), UpcomingQaCancellationCommandId);
		TestEqual(TEXT("H25 binds H20 evidence"), UpcomingVoidProjection->GetStringField(TEXT("cancellation_evidence_id")), UpcomingQaCancellationEvidenceId);
		TestEqual(TEXT("H25 binds H21 decision"), UpcomingVoidProjection->GetStringField(TEXT("decision_command_id")), UpcomingQaVoidDecisionCommandId);
		TestEqual(TEXT("H25 binds H22 finalization"), UpcomingVoidProjection->GetStringField(TEXT("finalization_command_id")), UpcomingQaVoidFinalizationCommandId);
		TestEqual(TEXT("H25 keeps settled void"), UpcomingVoidProjection->GetStringField(TEXT("finalization_status")), MatchWinnerSettledVoidStatus.ToString());
		TestEqual(TEXT("H25 keeps ledger count three"), static_cast<int32>(UpcomingVoidProjection->GetNumberField(TEXT("ledger_entry_count"))), 3);
		TestEqual(TEXT("H25 keeps final balance 100"), static_cast<int64>(UpcomingVoidProjection->GetNumberField(TEXT("final_balance"))), int64{100});
		TestEqual(TEXT("H25 keeps net zero"), static_cast<int64>(UpcomingVoidProjection->GetNumberField(TEXT("net"))), int64{0});
		TestFalse(TEXT("H25 invents no result"), UpcomingVoidProjection->HasField(TEXT("result_command_id")));
		TestFalse(TEXT("H25 invents no winner"), UpcomingVoidProjection->HasField(TEXT("winner")));
		TestFalse(TEXT("H25 invents no replay"), UpcomingVoidProjection->HasField(TEXT("replay_seal_sha256")));
		UpcomingVoidProjection->RemoveField(TEXT("generated_at_utc"));
		const TSharedRef<TJsonWriter<>> NormalizedUpcomingVoidProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedUpcomingVoidProjectionJson);
		TestTrue(TEXT("H25 exact upcoming QA history normalizes"), FJsonSerializer::Serialize(UpcomingVoidProjection.ToSharedRef(), NormalizedUpcomingVoidProjectionWriter));
	}
	TestTrue(TEXT("H25 projection can be removed for cold-load proof"), IFileManager::Get().Delete(*MatchWinnerProjectionPath, false, true, true));
	FOddsWellOddsBucksLedger HistoryLedger;
	int64 HistoryNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> HistoryRequests;
	TArray<FOddsWellMatchWinnerLockRecord> HistoryLocks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> HistoryResults;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> HistoryDecisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> HistoryLossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> HistoryWinFinalizations;
	bool bHistoryFound = false;
	TestTrue(TEXT("H25 cold load accepts only the exact finalized chain"), LoadOddsWellOddsBucksWagerFinalizationState(
		true,
		HistoryLedger,
		HistoryNextJobPayout,
		HistoryRequests,
		HistoryLocks,
		HistoryResults,
		HistoryDecisions,
		HistoryLossFinalizations,
		HistoryWinFinalizations,
		bHistoryFound,
		Error));
	TestTrue(TEXT("H25 cold load regenerates exact upcoming QA history"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	FString ColdUpcomingVoidProjectionJson;
	TSharedPtr<FJsonObject> ColdUpcomingVoidProjection;
	TestTrue(TEXT("H25 regenerated history reads"), FFileHelper::LoadFileToString(ColdUpcomingVoidProjectionJson, *MatchWinnerProjectionPath));
	const TSharedRef<TJsonReader<>> ColdUpcomingVoidProjectionReader = TJsonReaderFactory<>::Create(ColdUpcomingVoidProjectionJson);
	TestTrue(TEXT("H25 regenerated history parses"), FJsonSerializer::Deserialize(ColdUpcomingVoidProjectionReader, ColdUpcomingVoidProjection) && ColdUpcomingVoidProjection.IsValid());
	if (ColdUpcomingVoidProjection.IsValid())
	{
		ColdUpcomingVoidProjection->RemoveField(TEXT("generated_at_utc"));
		FString NormalizedColdUpcomingVoidProjectionJson;
		const TSharedRef<TJsonWriter<>> NormalizedColdUpcomingVoidProjectionWriter = TJsonWriterFactory<>::Create(&NormalizedColdUpcomingVoidProjectionJson);
		TestTrue(TEXT("H25 regenerated history normalizes"), FJsonSerializer::Serialize(ColdUpcomingVoidProjection.ToSharedRef(), NormalizedColdUpcomingVoidProjectionWriter));
		TestEqual(TEXT("H25 cold history is byte-equivalent after timestamp removal"), NormalizedColdUpcomingVoidProjectionJson, NormalizedUpcomingVoidProjectionJson);
	}
	const UOddsWellOddsBucksSaveGame* ExactFinalized = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestNotNull(TEXT("Exact H22 save reloads"), ExactFinalized);
	if (ExactFinalized)
	{
		TestTrue(TEXT("H22 has no normal result"), ExactFinalized->MatchWinnerResultLinks.IsEmpty());
		TestTrue(TEXT("H22 has no normal settlement"), ExactFinalized->MatchWinnerSettlementDecisions.IsEmpty());
		TestTrue(TEXT("H22 has no loss finalization"), ExactFinalized->MatchWinnerLossFinalizations.IsEmpty());
		TestTrue(TEXT("H22 has no win finalization"), ExactFinalized->MatchWinnerWinFinalizations.IsEmpty());
		TestEqual(TEXT("H22 has one void finalization"), ExactFinalized->MatchWinnerVoidFinalizations.Num(), 1);
	}

	TArray<uint8> FinalizedBytes;
	TestTrue(
		TEXT("Exact H22 finalized state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			FinalizedBytes));
	int32 Entries = 0;
	int32 Requests = 0;
	int32 Locks = 0;
	int32 Cancellations = 0;
	int32 VoidDecisions = 0;
	int32 VoidFinalizations = 0;
	TestTrue(
		TEXT("Cold retry and refund-finalization rejection matrix are byte-stable"),
		RunOddsWellUpcomingQaMatchWinnerVoidFinalizationAudit(
			Entries,
			Requests,
			Locks,
			Cancellations,
			VoidDecisions,
			VoidFinalizations,
			Balance,
			Error));
	TestEqual(TEXT("H22 audit preserves three ledger entries"), Entries, 3);
	TestEqual(TEXT("H22 audit preserves one request"), Requests, 1);
	TestEqual(TEXT("H22 audit preserves one lock"), Locks, 1);
	TestEqual(TEXT("H22 audit preserves one cancellation"), Cancellations, 1);
	TestEqual(TEXT("H22 audit preserves one void decision"), VoidDecisions, 1);
	TestEqual(TEXT("H22 audit preserves one void finalization"), VoidFinalizations, 1);
	TestEqual(TEXT("H22 audit preserves balance 100"), Balance, int64{100});

	auto RestoreExactFinalization = [&]()
	{
		return UGameplayStatics::SaveGameToSlot(
			UGameplayStatics::LoadGameFromMemory(FinalizedBytes),
			OddsBucksQaSlot,
			OddsBucksUserIndex);
	};
	auto RejectMutation = [&](const TCHAR* Label, TFunctionRef<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Mutated = Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromMemory(FinalizedBytes));
		TestNotNull(FString::Printf(TEXT("%s mutation loads"), Label), Mutated);
		if (!Mutated)
		{
			return;
		}
		Mutate(*Mutated);
		TestTrue(
			FString::Printf(TEXT("%s mutation persists"), Label),
			UGameplayStatics::SaveGameToSlot(Mutated, OddsBucksQaSlot, OddsBucksUserIndex));
		Error.Reset();
		TestEqual(
			FString::Printf(TEXT("%s rejects exact H22 command"), Label),
			FinalizeOddsWellUpcomingQaMatchWinnerVoidRefund(Finalization, Error),
			EOddsWellMatchWinnerVoidFinalizationResult::Rejected);
		TestFalse(FString::Printf(TEXT("%s exposes no stale H25 history"), Label), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
		TestTrue(FString::Printf(TEXT("%s exact H22 state restores"), Label), RestoreExactFinalization());
	};
	RejectMutation(TEXT("Wrong H21 decision link"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidDecisions.IsEmpty())
		{
			Save.MatchWinnerVoidDecisions[0].CancellationEvidenceId = TEXT("qa:h22:invented-evidence");
		}
	});
	RejectMutation(TEXT("Wrong H22 finalization link"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidFinalizations.IsEmpty())
		{
			Save.MatchWinnerVoidFinalizations[0].VoidDecisionCommandId = TEXT("qa:h22:invented-decision");
		}
	});
	RejectMutation(TEXT("Wrong applied refund"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidFinalizations.IsEmpty())
		{
			Save.MatchWinnerVoidFinalizations[0].RefundApplied = 39;
		}
	});
	RejectMutation(TEXT("Wrong finalization status"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (!Save.MatchWinnerVoidFinalizations.IsEmpty())
		{
			Save.MatchWinnerVoidFinalizations[0].Status = TEXT("open");
		}
	});
	RejectMutation(TEXT("Unexpected refund ledger evidence"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		if (Save.Entries.Num() == 3)
		{
			Save.Entries[2].Reason = TEXT("qa_unexpected_credit");
		}
	});
	RejectMutation(TEXT("Normal result overlap"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerResultLinks.AddDefaulted();
	});
	TArray<uint8> RestoredFinalizedBytes;
	TestTrue(
		TEXT("Restored exact H22 state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex),
			RestoredFinalizedBytes));
	TestTrue(TEXT("Every H22 tamper rejection preserves exact bytes"), RestoredFinalizedBytes == FinalizedBytes);
	TestTrue(TEXT("H25 restored exact state cold-publishes again"), LoadOddsWellOddsBucksWagerFinalizationState(
		true,
		HistoryLedger,
		HistoryNextJobPayout,
		HistoryRequests,
		HistoryLocks,
		HistoryResults,
		HistoryDecisions,
		HistoryLossFinalizations,
		HistoryWinFinalizations,
		bHistoryFound,
		Error));
	TestTrue(TEXT("H25 restored exact state exposes one read-only history"), IFileManager::Get().FileExists(*MatchWinnerProjectionPath));
	TestTrue(TEXT("H22 QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

#endif
