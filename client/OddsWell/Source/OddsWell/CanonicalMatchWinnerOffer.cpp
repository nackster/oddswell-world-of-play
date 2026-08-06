#include "CanonicalMatchWinnerOffer.h"

#include "CanonicalPregameCommitment.h"
#include "CanonicalScheduledGame.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformFileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "OddsBucksLedger.h"
#include "PublicLeagueView.h"
#include "Serialization/JsonSerializer.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 CanonicalOfferUserIndex = 0;
constexpr int64 HomeProbabilityE8 = 57586693;
constexpr int64 AwayProbabilityE8 = 42413307;
const FString CanonicalOfferSlot(TEXT("OddsWellCanonicalMatchWinnerOffer"));
const FString CanonicalOfferQaSlot(TEXT("OddsWellCanonicalMatchWinnerOfferH26CQA"));
const FString CanonicalRequestQaOfferSlot(TEXT("OddsWellCanonicalMatchWinnerOfferH26EQA"));
const FString ExpectedCommitmentSha256(TEXT("898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f"));

bool HasForbiddenValue(const TSharedPtr<FJsonValue>& Value);

bool HasForbiddenFields(const TSharedPtr<FJsonObject>& Object)
{
	static const TSet<FString> Forbidden = {
		TEXT("seed"),
		TEXT("rng"),
		TEXT("fatigue"),
		TEXT("life"),
		TEXT("private"),
		TEXT("score"),
		TEXT("winner"),
		TEXT("replay"),
		TEXT("result"),
		TEXT("simulation"),
		TEXT("request"),
		TEXT("debit"),
		TEXT("settlement"),
		TEXT("economy"),
		TEXT("user")};
	for (const TPair<FString, TSharedPtr<FJsonValue>>& Field : Object->Values)
	{
		if (Forbidden.Contains(Field.Key))
		{
			return true;
		}
		if (HasForbiddenValue(Field.Value))
		{
			return true;
		}
	}
	return false;
}

bool HasForbiddenValue(const TSharedPtr<FJsonValue>& Value)
{
	if (Value->Type == EJson::Object)
	{
		return HasForbiddenFields(Value->AsObject());
	}
	if (Value->Type == EJson::Array)
	{
		for (const TSharedPtr<FJsonValue>& Item : Value->AsArray())
		{
			if (HasForbiddenValue(Item))
			{
				return true;
			}
		}
	}
	return false;
}

bool BuildExpectedOffer(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	FOddsWellMatchWinnerOffer& OutOffer,
	FString& OutCanonicalJson,
	FString& OutError)
{
	if (Schedule.Schema != TEXT("oddswell-canonical-scheduled-game-v1")
		|| Schedule.RecordVersion != 1
		|| Schedule.SeasonNumber != 1
		|| Schedule.GameNumber != 1
		|| Schedule.HomeTeam != TEXT("Harbor City Waves")
		|| Schedule.AwayTeam != TEXT("Mesa Vista Sol")
		|| Schedule.SeasonCreatedUnixSeconds <= 0
		|| Schedule.TipoffUnixSeconds != Schedule.SeasonCreatedUnixSeconds + 1800
		|| Schedule.OfferEligibleUnixSeconds != Schedule.SeasonCreatedUnixSeconds
		|| Schedule.Status != TEXT("scheduled_unplayed")
		|| Schedule.Environment != TEXT("local_beta")
		|| Schedule.TimingAuthority != TEXT("server")
		|| Schedule.bProductionTiming
		|| Schedule.bOfferPublished
		|| Commitment.Schema != TEXT("oddswell-canonical-pregame-commitment-v1")
		|| Commitment.RecordVersion != 1
		|| Commitment.ScheduleSchema != Schedule.Schema
		|| Commitment.ScheduleRecordVersion != Schedule.RecordVersion
		|| Commitment.SeasonNumber != Schedule.SeasonNumber
		|| Commitment.GameNumber != Schedule.GameNumber
		|| Commitment.HomeTeam != Schedule.HomeTeam
		|| Commitment.AwayTeam != Schedule.AwayTeam
		|| Commitment.ScheduleCreatedUnixSeconds != Schedule.SeasonCreatedUnixSeconds
		|| Commitment.ScheduleTipoffUnixSeconds != Schedule.TipoffUnixSeconds
		|| Commitment.SnapshotVersion != TEXT("oddswell-public-pregame-v1")
		|| Commitment.PredictionVersion != TEXT("phase0d4-v1")
		|| Commitment.InputClass != TEXT("public_elo_rotation")
		|| Commitment.CommitmentJson.IsEmpty()
		|| Commitment.CommitmentSha256 != ExpectedCommitmentSha256
		|| Commitment.Status != TEXT("committed_pregame")
		|| Commitment.Environment != TEXT("local_beta"))
	{
		OutError = TEXT("The canonical Match Winner offer requires exact H26A and H26B inputs.");
		return false;
	}

	OutOffer = FOddsWellMatchWinnerOffer();
	OutOffer.Schema = TEXT("oddswell-basketball-odds-offer-v1");
	OutOffer.OfferVersion = TEXT("basketball-match-winner-odds-v1");
	OutOffer.Market = TEXT("match_winner");
	OutOffer.Currency = TEXT("odds_bucks");
	OutOffer.SourcePredictionVersion = Commitment.PredictionVersion;
	OutOffer.SourceSnapshotVersion = Commitment.SnapshotVersion;
	OutOffer.SourceModel = Commitment.InputClass;
	OutOffer.SourceCommitmentSha256 = Commitment.CommitmentSha256;
	OutOffer.SeasonNumber = Schedule.SeasonNumber;
	OutOffer.GameNumber = Schedule.GameNumber;
	OutOffer.HomeTeam = Schedule.HomeTeam;
	OutOffer.AwayTeam = Schedule.AwayTeam;
	OutOffer.LockUnixSeconds = Schedule.TipoffUnixSeconds;
	OutOffer.MinimumStake = 10;
	OutOffer.MaximumStake = 100;
	OutOffer.StakeIncrement = 10;
	OutOffer.HouseEdgeBps = 0;
	OutOffer.PayoutFormula = TEXT("floor(stake*100000000/win_probability_e8)");
	FOddsWellMatchWinnerSelection& Home = OutOffer.Selections.AddDefaulted_GetRef();
	Home.Team = OutOffer.HomeTeam;
	Home.WinProbabilityE8 = HomeProbabilityE8;
	Home.DecimalOddsE4 = 17365;
	FOddsWellMatchWinnerSelection& Away = OutOffer.Selections.AddDefaulted_GetRef();
	Away.Team = OutOffer.AwayTeam;
	Away.WinProbabilityE8 = AwayProbabilityE8;
	Away.DecimalOddsE4 = 23577;
	if (!FinalizeOddsWellMatchWinnerOfferIdentity(
		OutOffer,
		OutCanonicalJson,
		OutError))
	{
		return false;
	}

	TSharedPtr<FJsonObject> Root;
	const TSharedRef<TJsonReader<>> Reader =
		TJsonReaderFactory<>::Create(OutCanonicalJson);
	if (!FJsonSerializer::Deserialize(Reader, Root)
		|| !Root.IsValid()
		|| HasForbiddenFields(Root))
	{
		OutError = TEXT("The canonical Match Winner offer failed its recursive public-field audit.");
		return false;
	}
	OutError.Reset();
	return true;
}

bool RestoreExactOffer(
	const UObject* SaveObject,
	const FOddsWellMatchWinnerOffer& Expected,
	const FString& ExpectedCanonicalJson,
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError)
{
	const UOddsWellCanonicalMatchWinnerOfferSaveGame* Saved =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(SaveObject);
	if (!Saved
		|| Saved->OfferId != Expected.OfferId
		|| Saved->CanonicalOfferJson != ExpectedCanonicalJson)
	{
		OutError = TEXT("The canonical Match Winner offer conflicts with the exact public offer.");
		return false;
	}
	OutRecord = {
		Saved->OfferId,
		Saved->CanonicalOfferJson,
		Expected.LockUnixSeconds};
	OutError.Reset();
	return true;
}

bool LoadPreview(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& Slot,
	const int64 ObservedNowUnixSeconds,
	FOddsWellMatchWinnerOfferPreview& OutPreview,
	FString& OutError)
{
	OutPreview = {};
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord Persisted;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| ObservedNowUnixSeconds < Schedule.SeasonCreatedUnixSeconds
		|| ObservedNowUnixSeconds >= Schedule.TipoffUnixSeconds
		|| !UGameplayStatics::DoesSaveGameExist(Slot, CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(Slot, CanonicalOfferUserIndex),
			Expected,
			ExpectedCanonicalJson,
			Persisted,
			OutError))
	{
		OutPreview = {};
		OutError = TEXT("The canonical Match Winner offer is unavailable or locked.");
		return false;
	}

	OutPreview.OfferId = Expected.OfferId;
	OutPreview.OfferVersion = Expected.OfferVersion;
	OutPreview.SourcePredictionVersion = Expected.SourcePredictionVersion;
	OutPreview.SourceSnapshotVersion = Expected.SourceSnapshotVersion;
	OutPreview.SourceModel = Expected.SourceModel;
	OutPreview.SourceCommitmentSha256 = Expected.SourceCommitmentSha256;
	OutPreview.SeasonNumber = Expected.SeasonNumber;
	OutPreview.GameNumber = Expected.GameNumber;
	OutPreview.HomeTeam = Expected.HomeTeam;
	OutPreview.AwayTeam = Expected.AwayTeam;
	OutPreview.LockUnix = Expected.LockUnixSeconds;
	OutPreview.MinimumStake = Expected.MinimumStake;
	OutPreview.MaximumStake = Expected.MaximumStake;
	OutPreview.StakeIncrement = Expected.StakeIncrement;
	for (const FOddsWellMatchWinnerSelection& Selection : Expected.Selections)
	{
		FOddsWellMatchWinnerSelectionPreview& Preview =
			OutPreview.Selections.AddDefaulted_GetRef();
		Preview.Team = Selection.Team;
		Preview.WinProbabilityE8 = Selection.WinProbabilityE8;
		Preview.DecimalOddsE4 = Selection.DecimalOddsE4;
		Preview.MinimumStakeGrossReturn =
			Expected.MinimumStake * 100000000 / Selection.WinProbabilityE8;
		Preview.MaximumStakeGrossReturn =
			Expected.MaximumStake * 100000000 / Selection.WinProbabilityE8;
	}
	OutError.Reset();
	return true;
}

EOddsWellCanonicalPendingReceiptResult LoadPendingReceipt(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& OfferSlot,
	const int64 ObservedServerUnixSeconds,
	const bool bOddsBucksQaSlot,
	FOddsWellCanonicalPendingMatchWinnerReceipt& OutReceipt,
	FString& OutError)
{
	OutReceipt = {};
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord Persisted;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| ObservedServerUnixSeconds < Schedule.OfferEligibleUnixSeconds
		|| !UGameplayStatics::DoesSaveGameExist(
			OfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				OfferSlot,
				CanonicalOfferUserIndex),
			Expected,
			ExpectedCanonicalJson,
			Persisted,
			OutError))
	{
		OutReceipt = {};
		OutError = TEXT("Canonical pending Match Winner receipt failed exact H26A/B/C validation.");
		return EOddsWellCanonicalPendingReceiptResult::Rejected;
	}
	return LoadOddsWellCanonicalPendingMatchWinnerReceiptEvidence(
		Expected,
		Schedule.OfferEligibleUnixSeconds,
		ObservedServerUnixSeconds,
		bOddsBucksQaSlot,
		OutReceipt,
		OutError);
}

EOddsWellMatchWinnerRequestResult AcceptCanonicalRequest(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& OfferSlot,
	const int64 ServerNowUnixSeconds,
	const bool bOddsBucksQaSlot,
	const FString& OfferedOfferId,
	const FString& OfferedTeam,
	const int64 Stake,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	OutRecord = {};
	OutBalance = 0;
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord Persisted;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| ServerNowUnixSeconds < Schedule.SeasonCreatedUnixSeconds
		|| ServerNowUnixSeconds >= Schedule.TipoffUnixSeconds
		|| OfferedOfferId != Expected.OfferId
		|| !UGameplayStatics::DoesSaveGameExist(
			OfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				OfferSlot,
				CanonicalOfferUserIndex),
			Expected,
			ExpectedCanonicalJson,
			Persisted,
			OutError))
	{
		OutRecord = {};
		OutBalance = 0;
		OutError = TEXT("The canonical Match Winner request failed exact pre-tipoff server validation.");
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	return AcceptOddsWellMatchWinnerRequest(
		Expected,
		TEXT("canonical:h26e:match_winner:request:") + Expected.OfferId,
		OfferedTeam,
		Stake,
		ServerNowUnixSeconds,
		bOddsBucksQaSlot,
		OutRecord,
		OutBalance,
		OutError);
}

EOddsWellMatchWinnerLockResult LockCanonicalRequestAtGameStart(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& OfferSlot,
	const int64 ObservedServerUnixSeconds,
	const bool bOddsBucksQaSlot,
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord Persisted;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| ObservedServerUnixSeconds != Schedule.TipoffUnixSeconds
		|| !UGameplayStatics::DoesSaveGameExist(
			OfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				OfferSlot,
				CanonicalOfferUserIndex),
			Expected,
			ExpectedCanonicalJson,
			Persisted,
			OutError))
	{
		OutRecord = {};
		OutError = TEXT("The canonical Match Winner lock failed exact H26A/B/C game-start validation.");
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	return LockOddsWellCanonicalMatchWinnerRequestEvidence(
		Expected,
		Schedule.OfferEligibleUnixSeconds,
		ObservedServerUnixSeconds,
		bOddsBucksQaSlot,
		OutRecord,
		OutError);
}

EOddsWellMatchWinnerSettlementDecisionResult DecideCanonicalMatchWinnerLoss(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& OfferSlot,
	const bool bOddsBucksQaSlot,
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord PersistedOffer;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactCanonicalJson,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			OfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				OfferSlot,
				CanonicalOfferUserIndex),
			ExactOffer,
			ExactCanonicalJson,
			PersistedOffer,
			OutError))
	{
		OutError =
			TEXT("Canonical Match Winner loss decision failed exact H26A/B/C validation.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	return DecideOddsWellCanonicalMatchWinnerLossDecisionEvidence(
		ExactOffer,
		Schedule.OfferEligibleUnixSeconds,
		bOddsBucksQaSlot,
		OutRecord,
		OutError);
}

EOddsWellMatchWinnerSettlementDecisionResult DecideCanonicalMatchWinnerCurrentMesaWin(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& OfferSlot,
	const bool bOddsBucksQaSlot,
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord PersistedOffer;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactCanonicalJson,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			OfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				OfferSlot,
				CanonicalOfferUserIndex),
			ExactOffer,
			ExactCanonicalJson,
			PersistedOffer,
			OutError))
	{
		OutError =
			TEXT("Canonical Match Winner Mesa decision failed exact H26A/B/C validation.");
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	const FString ResultSha =
		TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	return DecideOddsWellMatchWinnerSettlement(
		ExactOffer,
		TEXT("canonical:h26an:match_winner:win-decision:") + ResultSha,
		TEXT("canonical:h26e:match_winner:request:") + ExactOffer.OfferId,
		TEXT("canonical:h26g:match_winner:lock:") + ExactOffer.OfferId,
		TEXT("canonical:h26l:match_winner:result:") + ResultSha,
		bOddsBucksQaSlot,
		OutRecord,
		OutError);
}

EOddsWellMatchWinnerLossFinalizationResult FinalizeCanonicalMatchWinnerLoss(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& OfferSlot,
	const bool bOddsBucksQaSlot,
	FOddsWellMatchWinnerLossFinalizationRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord PersistedOffer;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactCanonicalJson,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			OfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				OfferSlot,
				CanonicalOfferUserIndex),
			ExactOffer,
			ExactCanonicalJson,
			PersistedOffer,
			OutError))
	{
		OutError =
			TEXT("Canonical Match Winner loss finalization failed exact H26A/B/C validation.");
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	return FinalizeOddsWellCanonicalMatchWinnerLossEvidence(
		ExactOffer,
		Schedule.OfferEligibleUnixSeconds,
		bOddsBucksQaSlot,
		OutRecord,
		OutError);
}

EOddsWellCanonicalMatchWinnerOfferResult PersistOffer(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FString& Slot,
	const int64 ObservedNowUnixSeconds,
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError)
{
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| ObservedNowUnixSeconds < Schedule.SeasonCreatedUnixSeconds
		|| ObservedNowUnixSeconds >= Schedule.TipoffUnixSeconds)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The canonical Match Winner offer may only be created before tipoff.");
		}
		return EOddsWellCanonicalMatchWinnerOfferResult::Rejected;
	}
	if (UGameplayStatics::DoesSaveGameExist(Slot, CanonicalOfferUserIndex))
	{
		return RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(Slot, CanonicalOfferUserIndex),
			Expected,
			ExpectedCanonicalJson,
			OutRecord,
			OutError)
			? EOddsWellCanonicalMatchWinnerOfferResult::Duplicate
			: EOddsWellCanonicalMatchWinnerOfferResult::Rejected;
	}
	UOddsWellCanonicalMatchWinnerOfferSaveGame* Saved =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
			UGameplayStatics::CreateSaveGameObject(
				UOddsWellCanonicalMatchWinnerOfferSaveGame::StaticClass()));
	if (!Saved)
	{
		OutError = TEXT("The canonical Match Winner offer save object could not be created.");
		return EOddsWellCanonicalMatchWinnerOfferResult::Rejected;
	}
	Saved->OfferId = Expected.OfferId;
	Saved->CanonicalOfferJson = ExpectedCanonicalJson;
	if (!RestoreExactOffer(
			Saved,
			Expected,
			ExpectedCanonicalJson,
			OutRecord,
			OutError)
		|| !UGameplayStatics::SaveGameToSlot(
			Saved,
			Slot,
			CanonicalOfferUserIndex))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("Native SaveGameToSlot failed for the canonical Match Winner offer.");
		}
		return EOddsWellCanonicalMatchWinnerOfferResult::Rejected;
	}
	OutError.Reset();
	return EOddsWellCanonicalMatchWinnerOfferResult::Created;
}

FOddsWellCanonicalScheduledGameRecord TestSchedule()
{
	return {
		TEXT("oddswell-canonical-scheduled-game-v1"),
		1,
		1,
		1,
		TEXT("Harbor City Waves"),
		TEXT("Mesa Vista Sol"),
		2200000000,
		2200001800,
		2200000000,
		TEXT("scheduled_unplayed"),
		TEXT("local_beta"),
		TEXT("server"),
		false,
		false};
}

FOddsWellCanonicalPregameCommitmentRecord TestCommitment()
{
	return {
		TEXT("oddswell-canonical-pregame-commitment-v1"),
		1,
		TEXT("oddswell-canonical-scheduled-game-v1"),
		1,
		1,
		1,
		TEXT("Harbor City Waves"),
		TEXT("Mesa Vista Sol"),
		2200000000,
		2200001800,
		TEXT("oddswell-public-pregame-v1"),
		TEXT("phase0d4-v1"),
		TEXT("public_elo_rotation"),
		TEXT("validated-by-h26b"),
		ExpectedCommitmentSha256,
		TEXT("committed_pregame"),
		TEXT("local_beta")};
}
}

EOddsWellCanonicalMatchWinnerOfferResult CreateOddsWellCanonicalMatchWinnerOffer(
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError))
	{
		return EOddsWellCanonicalMatchWinnerOfferResult::Rejected;
	}
	return PersistOffer(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		FDateTime::UtcNow().ToUnixTimestamp(),
		OutRecord,
		OutError);
}

bool LoadOddsWellCanonicalMatchWinnerOffer(
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError)
		|| !BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			CanonicalOfferSlot,
			CanonicalOfferUserIndex))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("No canonical Match Winner offer save exists.");
		}
		return false;
	}
	return RestoreExactOffer(
		UGameplayStatics::LoadGameFromSlot(
			CanonicalOfferSlot,
			CanonicalOfferUserIndex),
		Expected,
		ExpectedCanonicalJson,
		OutRecord,
		OutError);
}

bool ValidateOddsWellCanonicalMatchWinnerOfferEvidence(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FOddsWellCanonicalMatchWinnerOfferRecord& Record,
	FString& OutError)
{
	FOddsWellMatchWinnerOffer Expected;
	FString ExpectedCanonicalJson;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			ExpectedCanonicalJson,
			OutError)
		|| Record.OfferId != Expected.OfferId
		|| Record.CanonicalOfferJson != ExpectedCanonicalJson
		|| Record.LockUnixSeconds != Expected.LockUnixSeconds)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The canonical Match Winner offer is not exact H26C evidence.");
		}
		return false;
	}
	OutError.Reset();
	return true;
}

bool BuildOddsWellCanonicalMatchWinnerOfferEvidence(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	FOddsWellCanonicalMatchWinnerOfferRecord& OutRecord,
	FString& OutError)
{
	FOddsWellMatchWinnerOffer Expected;
	if (!BuildExpectedOffer(
			Schedule,
			Commitment,
			Expected,
			OutRecord.CanonicalOfferJson,
			OutError))
	{
		OutRecord = {};
		return false;
	}
	OutRecord.OfferId = Expected.OfferId;
	OutRecord.LockUnixSeconds = Expected.LockUnixSeconds;
	return true;
}

bool LoadOddsWellCanonicalMatchWinnerOfferPreview(
	FOddsWellMatchWinnerOfferPreview& OutPreview,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError)
		|| !LoadPreview(
			Schedule,
			Commitment,
			CanonicalOfferSlot,
			FDateTime::UtcNow().ToUnixTimestamp(),
			OutPreview,
			OutError))
	{
		OutPreview = {};
		OutError = TEXT("The canonical Match Winner offer is unavailable or locked.");
		return false;
	}
	return true;
}

EOddsWellCanonicalPendingReceiptResult LoadOddsWellCanonicalPendingMatchWinnerReceipt(
	FOddsWellCanonicalPendingMatchWinnerReceipt& OutReceipt,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError))
	{
		OutReceipt = {};
		return EOddsWellCanonicalPendingReceiptResult::Rejected;
	}
	return LoadPendingReceipt(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		FDateTime::UtcNow().ToUnixTimestamp(),
		UseOddsWellOddsBucksQaSlot(),
		OutReceipt,
		OutError);
}

EOddsWellCanonicalSettledLossReceiptResult
LoadOddsWellCanonicalSettledLossReceipt(
	FOddsWellCanonicalSettledLossReceipt& OutReceipt,
	FString& OutError)
{
	OutReceipt = {};
	FOddsWellCanonicalMatchWinnerOfferRecord ExactOffer;
	if (!LoadOddsWellCanonicalMatchWinnerOffer(ExactOffer, OutError))
	{
		return EOddsWellCanonicalSettledLossReceiptResult::Rejected;
	}
	return LoadOddsWellCanonicalSettledLossReceiptEvidence(
		UseOddsWellOddsBucksQaSlot(),
		OutReceipt,
		OutError);
}

bool LoadOddsWellCanonicalMatchWinnerLock(
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord PersistedOffer;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError)
		|| !BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactCanonicalJson,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			CanonicalOfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalOfferSlot,
				CanonicalOfferUserIndex),
			ExactOffer,
			ExactCanonicalJson,
			PersistedOffer,
			OutError)
		|| !LoadOddsWellCanonicalMatchWinnerLockEvidence(
			ExactOffer,
			Schedule.OfferEligibleUnixSeconds,
			UseOddsWellOddsBucksQaSlot(),
			OutRecord,
			OutError))
	{
		OutRecord = {};
		return false;
	}
	return true;
}

bool ValidateOddsWellCanonicalMatchWinnerResultLinkPrerequisites(
	const FOddsWellMatchWinnerResultLinkRecord& ExactResult,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactCanonicalJson;
	FOddsWellCanonicalMatchWinnerOfferRecord PersistedOffer;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError)
		|| !BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactCanonicalJson,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			CanonicalOfferSlot,
			CanonicalOfferUserIndex)
		|| !RestoreExactOffer(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalOfferSlot,
				CanonicalOfferUserIndex),
			ExactOffer,
			ExactCanonicalJson,
			PersistedOffer,
			OutError)
		|| !::ValidateOddsWellCanonicalMatchWinnerResultLinkPrerequisites(
			ExactOffer,
			Schedule.OfferEligibleUnixSeconds,
			ExactResult,
			UseOddsWellOddsBucksQaSlot(),
			OutError))
	{
		OutError =
			TEXT("Canonical Match Winner result prerequisites failed exact H26A/B/C/E/G validation.");
		return false;
	}
	OutError.Reset();
	return true;
}

EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellCanonicalMatchWinnerLossDecision(
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(
			Schedule,
			OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(
			Commitment,
			OutError))
	{
		OutRecord = {};
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	return DecideCanonicalMatchWinnerLoss(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		UseOddsWellOddsBucksQaSlot(),
		OutRecord,
		OutError);
}

EOddsWellMatchWinnerSettlementDecisionResult DecideOddsWellCanonicalMatchWinnerCurrentMesaWinDecision(
	FOddsWellMatchWinnerSettlementDecisionRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(
			Schedule,
			OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(
			Commitment,
			OutError))
	{
		OutRecord = {};
		return EOddsWellMatchWinnerSettlementDecisionResult::Rejected;
	}
	return DecideCanonicalMatchWinnerCurrentMesaWin(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		UseOddsWellOddsBucksQaSlot(),
		OutRecord,
		OutError);
}

EOddsWellMatchWinnerLossFinalizationResult FinalizeOddsWellCanonicalMatchWinnerLoss(
	FOddsWellMatchWinnerLossFinalizationRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(
			Schedule,
			OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(
			Commitment,
			OutError))
	{
		OutRecord = {};
		return EOddsWellMatchWinnerLossFinalizationResult::Rejected;
	}
	return FinalizeCanonicalMatchWinnerLoss(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		UseOddsWellOddsBucksQaSlot(),
		OutRecord,
		OutError);
}

EOddsWellMatchWinnerRequestResult AcceptOddsWellCanonicalMatchWinnerRequest(
	const FString& OfferedOfferId,
	const FString& OfferedTeam,
	const int64 Stake,
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError))
	{
		OutRecord = {};
		OutBalance = 0;
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	return AcceptCanonicalRequest(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		FDateTime::UtcNow().ToUnixTimestamp(),
		UseOddsWellOddsBucksQaSlot(),
		OfferedOfferId,
		OfferedTeam,
		Stake,
		OutRecord,
		OutBalance,
		OutError);
}

EOddsWellMatchWinnerRequestResult AcceptOddsWellCanonicalHarborFortyRequest(
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	FOddsWellCanonicalMatchWinnerOfferRecord Offer;
	if (!LoadOddsWellCanonicalMatchWinnerOffer(Offer, OutError))
	{
		OutRecord = {};
		OutBalance = 0;
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	return AcceptOddsWellCanonicalMatchWinnerRequest(
		Offer.OfferId,
		TEXT("Harbor City Waves"),
		40,
		OutRecord,
		OutBalance,
		OutError);
}

EOddsWellMatchWinnerRequestResult AcceptOddsWellCanonicalMesaFortyRequest(
	FOddsWellMatchWinnerRequestRecord& OutRecord,
	int64& OutBalance,
	FString& OutError)
{
	FOddsWellCanonicalMatchWinnerOfferRecord Offer;
	if (!LoadOddsWellCanonicalMatchWinnerOffer(Offer, OutError))
	{
		OutRecord = {};
		OutBalance = 0;
		return EOddsWellMatchWinnerRequestResult::Rejected;
	}
	return AcceptOddsWellCanonicalMatchWinnerRequest(
		Offer.OfferId,
		TEXT("Mesa Vista Sol"),
		40,
		OutRecord,
		OutBalance,
		OutError);
}

EOddsWellMatchWinnerLockResult LockOddsWellCanonicalMatchWinnerRequestAtGameStart(
	FOddsWellMatchWinnerLockRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(Commitment, OutError))
	{
		OutRecord = {};
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	const bool bQaClock =
		FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLockQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalMatchWinnerLockQaVerify"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalPostLockQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalAutomaticTipoffLockQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalAutomaticTipoffLockQaVerify"));
	return LockCanonicalRequestAtGameStart(
		Schedule,
		Commitment,
		CanonicalOfferSlot,
		bQaClock
			? Schedule.TipoffUnixSeconds
			: FDateTime::UtcNow().ToUnixTimestamp(),
		UseOddsWellOddsBucksQaSlot(),
		OutRecord,
		OutError);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerOfferPersistenceTest,
	"OddsWell.League.CanonicalMatchWinnerOffer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerOfferPersistenceTest::RunTest(
	const FString& Parameters)
{
	UGameplayStatics::DeleteGameInSlot(
		CanonicalOfferQaSlot,
		CanonicalOfferUserIndex);
	const FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord Commitment = TestCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord Created;
	FString Error;
	TestEqual(
		TEXT("Exact pre-tipoff offer creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			2200000100,
			Created,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);
	TestEqual(
		TEXT("Offer ID matches the Python canonical contract"),
		Created.OfferId,
		FString(TEXT("354679a800e9a8ed31eccd04591310defc8ec6413d81891bb5b595e9d9d88606")));
	TestEqual(TEXT("Canonical offer length is exact"), Created.CanonicalOfferJson.Len(), 808);
	TestEqual(TEXT("Offer locks at H26A tipoff"), Created.LockUnixSeconds, int64{2200001800});
	TestTrue(TEXT("Home probability is exact"), Created.CanonicalOfferJson.Contains(TEXT("\"win_probability_e8\":57586693")));
	TestTrue(TEXT("Away probability is exact"), Created.CanonicalOfferJson.Contains(TEXT("\"win_probability_e8\":42413307")));
	TestTrue(TEXT("Home decimal odds are exact"), Created.CanonicalOfferJson.Contains(TEXT("\"decimal_odds_e4\":17365")));
	TestTrue(TEXT("Away decimal odds are exact"), Created.CanonicalOfferJson.Contains(TEXT("\"decimal_odds_e4\":23577")));

	FOddsWellMatchWinnerOfferPreview Preview;
	TestTrue(
		TEXT("Exact persisted offer loads into the read-only preview before tipoff"),
		LoadPreview(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			2200000100,
			Preview,
			Error));
	TestEqual(TEXT("Preview exposes Harbor home"), Preview.HomeTeam, FString(TEXT("Harbor City Waves")));
	TestEqual(TEXT("Preview exposes Mesa away"), Preview.AwayTeam, FString(TEXT("Mesa Vista Sol")));
	TestEqual(TEXT("Preview exposes exactly two selections"), Preview.Selections.Num(), 2);
	if (Preview.Selections.Num() == 2)
	{
		TestEqual(TEXT("Harbor integer odds stay exact"), Preview.Selections[0].DecimalOddsE4, int64{17365});
		TestEqual(TEXT("Mesa integer odds stay exact"), Preview.Selections[1].DecimalOddsE4, int64{23577});
		TestEqual(TEXT("Harbor minimum gross return uses exact floor convention"), Preview.Selections[0].MinimumStakeGrossReturn, int64{17});
		TestEqual(TEXT("Mesa maximum gross return uses exact floor convention"), Preview.Selections[1].MaximumStakeGrossReturn, int64{235});
	}
	const UOddsWellCanonicalMatchWinnerOfferSaveGame* AfterPreview =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalOfferQaSlot,
				CanonicalOfferUserIndex));
	TestTrue(
		TEXT("Preview read leaves persisted identity and JSON unchanged"),
		AfterPreview
			&& AfterPreview->OfferId == Created.OfferId
			&& AfterPreview->CanonicalOfferJson == Created.CanonicalOfferJson);
	TestFalse(
		TEXT("Preview rejects a clock before canonical schedule creation"),
		LoadPreview(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			Schedule.SeasonCreatedUnixSeconds - 1,
			Preview,
			Error));
	TestTrue(
		TEXT("Before-creation preview exposes no partial teams or prices"),
		Preview.HomeTeam.IsEmpty()
			&& Preview.AwayTeam.IsEmpty()
			&& Preview.Selections.IsEmpty());
	TestFalse(
		TEXT("Preview locks at exact server tipoff"),
		LoadPreview(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			Schedule.TipoffUnixSeconds,
			Preview,
			Error));
	TestTrue(
		TEXT("Locked preview exposes no partial teams or prices"),
		Preview.HomeTeam.IsEmpty()
			&& Preview.AwayTeam.IsEmpty()
			&& Preview.Selections.IsEmpty());

	FOddsWellCanonicalMatchWinnerOfferRecord Duplicate;
	TestEqual(
		TEXT("Cold exact retry is duplicate-safe"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			2200000200,
			Duplicate,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Duplicate);
	TestEqual(TEXT("Duplicate offer ID is unchanged"), Duplicate.OfferId, Created.OfferId);
	TestEqual(TEXT("Duplicate canonical JSON is unchanged"), Duplicate.CanonicalOfferJson, Created.CanonicalOfferJson);

	FOddsWellCanonicalPregameCommitmentRecord MismatchedCommitment = Commitment;
	MismatchedCommitment.ScheduleTipoffUnixSeconds++;
	TestFalse(
		TEXT("Mismatched upstream commitment is unavailable to the preview"),
		LoadPreview(
			Schedule,
			MismatchedCommitment,
			CanonicalOfferQaSlot,
			2200000300,
			Preview,
			Error));
	TestTrue(
		TEXT("Mismatched preview exposes no partial teams or prices"),
		Preview.HomeTeam.IsEmpty()
			&& Preview.AwayTeam.IsEmpty()
			&& Preview.Selections.IsEmpty());

	UOddsWellCanonicalMatchWinnerOfferSaveGame* Tampered =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalOfferQaSlot,
				CanonicalOfferUserIndex));
	TestNotNull(TEXT("Offer reloads for conflict proof"), Tampered);
	if (Tampered)
	{
		Tampered->CanonicalOfferJson += TEXT(" ");
		TestTrue(
			TEXT("Tampered offer saves for conflict proof"),
			UGameplayStatics::SaveGameToSlot(
				Tampered,
				CanonicalOfferQaSlot,
				CanonicalOfferUserIndex));
		TestEqual(
			TEXT("Conflicting persisted offer rejects"),
			PersistOffer(
				Schedule,
				Commitment,
				CanonicalOfferQaSlot,
				2200000300,
				Duplicate,
				Error),
			EOddsWellCanonicalMatchWinnerOfferResult::Rejected);
		TestFalse(
			TEXT("Tampered persisted offer is unavailable to the preview"),
			LoadPreview(
				Schedule,
				Commitment,
				CanonicalOfferQaSlot,
				2200000300,
				Preview,
				Error));
		TestTrue(
			TEXT("Tampered preview exposes no partial teams or prices"),
			Preview.HomeTeam.IsEmpty()
				&& Preview.AwayTeam.IsEmpty()
				&& Preview.Selections.IsEmpty());
		const UOddsWellCanonicalMatchWinnerOfferSaveGame* Unchanged =
			Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					CanonicalOfferQaSlot,
					CanonicalOfferUserIndex));
		TestTrue(
			TEXT("Rejected conflict is not rewritten"),
			Unchanged && Unchanged->CanonicalOfferJson.EndsWith(TEXT(" ")));
	}

	TestTrue(
		TEXT("Conflict fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalOfferQaSlot,
			CanonicalOfferUserIndex));
	TestFalse(
		TEXT("Missing canonical offer has no archived fallback"),
		LoadPreview(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			2200000300,
			Preview,
			Error));
	TestTrue(
		TEXT("Missing preview exposes no partial teams or prices"),
		Preview.HomeTeam.IsEmpty()
			&& Preview.AwayTeam.IsEmpty()
			&& Preview.Selections.IsEmpty());
	TestEqual(
		TEXT("Creation before the H26A creation time rejects"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			Schedule.SeasonCreatedUnixSeconds - 1,
			Duplicate,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Rejected);
	TestEqual(
		TEXT("Creation at tipoff rejects"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalOfferQaSlot,
			Schedule.TipoffUnixSeconds,
			Duplicate,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Rejected);
	TestFalse(
		TEXT("Late rejection writes no offer"),
		UGameplayStatics::DoesSaveGameExist(
			CanonicalOfferQaSlot,
			CanonicalOfferUserIndex));

	FOddsWellCanonicalPregameCommitmentRecord WrongCommitment = Commitment;
	WrongCommitment.CommitmentSha256 =
		TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
	TestEqual(
		TEXT("Wrong H26B commitment rejects"),
		PersistOffer(
			Schedule,
			WrongCommitment,
			CanonicalOfferQaSlot,
			2200000100,
			Duplicate,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Rejected);
	TestFalse(
		TEXT("Input rejection writes no offer"),
		UGameplayStatics::DoesSaveGameExist(
			CanonicalOfferQaSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerRequestTest,
	"OddsWell.League.CanonicalMatchWinnerRequest",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerRequestTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	TestTrue(
		TEXT("Isolated QA ledger starts clean"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	UGameplayStatics::DeleteGameInSlot(
		CanonicalRequestQaOfferSlot,
		CanonicalOfferUserIndex);

	const FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord Commitment = TestCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	TestEqual(
		TEXT("Exact canonical request fixture offer creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000100,
			OfferRecord,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);

	FOddsWellOddsBucksLedger Funded;
	TestEqual(
		TEXT("Existing local job credit funds the request"),
		Funded.Append(
			GetOddsWellFirstJobCommandId(),
			GetOddsWellFirstJobPayout(),
			GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Funded isolated ledger persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			2200086400,
			true,
			Error));

	FOddsWellMatchWinnerRequestRecord Accepted;
	int64 Balance = 0;
	TestEqual(
		TEXT("Exact server-authoritative canonical request accepts"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000100,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Accepted,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	TestEqual(TEXT("Accepted request leaves balance 60"), Balance, int64{60});
	TestEqual(TEXT("Request evidence version is current"), Accepted.EvidenceVersion, 1);
	TestEqual(TEXT("Request binds exact H26C offer"), Accepted.OfferId, OfferRecord.OfferId);
	TestEqual(TEXT("Request binds offer schema"), Accepted.OfferSchema, FString(TEXT("oddswell-basketball-odds-offer-v1")));
	TestEqual(TEXT("Request binds market"), Accepted.Market, FString(TEXT("match_winner")));
	TestEqual(TEXT("Request binds currency"), Accepted.Currency, FString(TEXT("odds_bucks")));
	TestEqual(TEXT("Request binds source prediction"), Accepted.SourcePredictionVersion, FString(TEXT("phase0d4-v1")));
	TestEqual(TEXT("Request binds source snapshot"), Accepted.SourceSnapshotVersion, FString(TEXT("oddswell-public-pregame-v1")));
	TestEqual(TEXT("Request binds source model"), Accepted.SourceModel, FString(TEXT("public_elo_rotation")));
	TestEqual(TEXT("Request binds exact H26B commitment"), Accepted.SourceCommitmentSha256, ExpectedCommitmentSha256);
	TestEqual(TEXT("Request binds selected probability"), Accepted.SelectedWinProbabilityE8, HomeProbabilityE8);
	TestEqual(TEXT("Request binds selected integer odds"), Accepted.SelectedDecimalOddsE4, int64{17365});
	TestEqual(TEXT("Request binds approved stake"), Accepted.Stake, int64{40});
	TestEqual(TEXT("Request binds server acceptance time"), Accepted.AcceptedUnixSeconds, int64{2200000100});
	TestEqual(TEXT("Request binds exact game-start lock"), Accepted.LockUnixSeconds, Schedule.TipoffUnixSeconds);
	TestEqual(TEXT("Request binds exact floor gross return"), Accepted.GrossReturn, int64{69});
	TestEqual(TEXT("Request is accepted pending lock"), Accepted.Status, FName(TEXT("accepted_pending_lock")));

	FOddsWellOddsBucksLedger AcceptedLedger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> AcceptedRequests;
	bool bFound = false;
	TestTrue(
		TEXT("Accepted state cold-loads"),
		LoadOddsWellOddsBucksState(
			true,
			AcceptedLedger,
			NextJobPayoutUnixSeconds,
			AcceptedRequests,
			bFound,
			Error));
	TestTrue(TEXT("Accepted state exists"), bFound);
	TestEqual(TEXT("Accepted ledger has job credit and stake debit"), AcceptedLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("Accepted ledger balance remains 60"), AcceptedLedger.GetBalance(), int64{60});
	TestEqual(TEXT("Exactly one request persists"), AcceptedRequests.Num(), 1);
	if (AcceptedLedger.GetEntries().Num() == 2)
	{
		const FOddsWellOddsBucksEntry& Debit = AcceptedLedger.GetEntries()[1];
		TestEqual(TEXT("Stake debit is ledger sequence 2"), Debit.Sequence, int64{2});
		TestEqual(TEXT("Stake debit is -40"), Debit.Delta, int64{-40});
		TestEqual(TEXT("Stake debit reason is exact"), Debit.Reason, FName(TEXT("match_winner_stake")));
		TestEqual(TEXT("Stake debit links the request command"), Debit.CommandId, Accepted.RequestCommandId);
	}

	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	TArray<uint8> AcceptedBytes;
	TestTrue(
		TEXT("Accepted state bytes are readable"),
		FFileHelper::LoadFileToArray(AcceptedBytes, *QaLedgerPath));
	auto TestLedgerBytesUnchanged = [this, &AcceptedBytes, &QaLedgerPath](const TCHAR* Label)
	{
		TArray<uint8> After;
		TestTrue(
			FString::Printf(TEXT("%s state remains readable"), Label),
			FFileHelper::LoadFileToArray(After, *QaLedgerPath));
		TestTrue(
			FString::Printf(TEXT("%s causes zero persisted mutation"), Label),
			After == AcceptedBytes);
	};

	FOddsWellMatchWinnerRequestRecord Retry;
	TestEqual(
		TEXT("Cold exact retry is duplicate-safe"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Retry,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Duplicate);
	TestEqual(TEXT("Retry preserves original server acceptance time"), Retry.AcceptedUnixSeconds, int64{2200000100});
	TestLedgerBytesUnchanged(TEXT("Exact duplicate"));

	auto TestRejected = [this,
		&Schedule,
		&Commitment,
		&OfferRecord,
		&Retry,
		&Balance,
		&Error,
		&TestLedgerBytesUnchanged](
			const TCHAR* Label,
			const FOddsWellCanonicalScheduledGameRecord& CandidateSchedule,
			const FOddsWellCanonicalPregameCommitmentRecord& CandidateCommitment,
			const int64 ServerNow,
			const FString& OfferedOfferId,
			const FString& Team,
			const int64 Stake)
	{
		TestEqual(
			Label,
			AcceptCanonicalRequest(
				CandidateSchedule,
				CandidateCommitment,
				CanonicalRequestQaOfferSlot,
				ServerNow,
				true,
				OfferedOfferId,
				Team,
				Stake,
				Retry,
				Balance,
				Error),
			EOddsWellMatchWinnerRequestResult::Rejected);
		TestLedgerBytesUnchanged(Label);
	};
	TestRejected(
		TEXT("Wrong offer ID rejects"),
		Schedule,
		Commitment,
		2200000200,
		TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
		Schedule.HomeTeam,
		40);
	TestRejected(
		TEXT("Unapproved team rejects"),
		Schedule,
		Commitment,
		2200000200,
		OfferRecord.OfferId,
		TEXT("Not Offered"),
		40);
	TestRejected(
		TEXT("Changed approved team conflicts with the server command"),
		Schedule,
		Commitment,
		2200000200,
		OfferRecord.OfferId,
		Schedule.AwayTeam,
		40);
	TestRejected(
		TEXT("Nonincrement stake rejects"),
		Schedule,
		Commitment,
		2200000200,
		OfferRecord.OfferId,
		Schedule.HomeTeam,
		15);
	TestRejected(
		TEXT("Changed valid stake conflicts with the server command"),
		Schedule,
		Commitment,
		2200000200,
		OfferRecord.OfferId,
		Schedule.HomeTeam,
		50);
	TestRejected(
		TEXT("At-tipoff request rejects"),
		Schedule,
		Commitment,
		Schedule.TipoffUnixSeconds,
		OfferRecord.OfferId,
		Schedule.HomeTeam,
		40);
	TestRejected(
		TEXT("Before-creation server time rejects"),
		Schedule,
		Commitment,
		Schedule.SeasonCreatedUnixSeconds - 1,
		OfferRecord.OfferId,
		Schedule.HomeTeam,
		40);
	FOddsWellCanonicalScheduledGameRecord WrongSchedule = Schedule;
	WrongSchedule.GameNumber++;
	TestRejected(
		TEXT("Tampered H26A input rejects"),
		WrongSchedule,
		Commitment,
		2200000200,
		OfferRecord.OfferId,
		Schedule.HomeTeam,
		40);
	FOddsWellCanonicalPregameCommitmentRecord WrongCommitment = Commitment;
	WrongCommitment.InputClass = TEXT("private_model");
	TestRejected(
		TEXT("Tampered H26B input rejects"),
		Schedule,
		WrongCommitment,
		2200000200,
		OfferRecord.OfferId,
		Schedule.HomeTeam,
		40);

	UOddsWellCanonicalMatchWinnerOfferSaveGame* TamperedOffer =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
	TestNotNull(TEXT("H26C fixture reloads for tamper rejection"), TamperedOffer);
	if (TamperedOffer)
	{
		const FString ExactJson = TamperedOffer->CanonicalOfferJson;
		TamperedOffer->CanonicalOfferJson += TEXT(" ");
		TestTrue(
			TEXT("Tampered H26C fixture writes"),
			UGameplayStatics::SaveGameToSlot(
				TamperedOffer,
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
		TestRejected(
			TEXT("Tampered H26C record rejects"),
			Schedule,
			Commitment,
			2200000200,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40);
		TamperedOffer->CanonicalOfferJson = ExactJson;
		TestTrue(
			TEXT("Exact H26C fixture restores"),
			UGameplayStatics::SaveGameToSlot(
				TamperedOffer,
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
	}

	TestTrue(
		TEXT("Accepted profile resets for underfunded proof"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	FOddsWellOddsBucksLedger Underfunded;
	TestEqual(
		TEXT("Underfunded fixture credit applies"),
		Underfunded.Append(
			TEXT("qa:h26e:underfunded-credit"),
			10,
			FName(TEXT("qa_fixture_credit"))),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("Underfunded fixture persists"),
		SaveOddsWellOddsBucksLedger(
			Underfunded,
			0,
			true,
			Error));
	TArray<uint8> UnderfundedBytes;
	TestTrue(
		TEXT("Underfunded bytes are readable"),
		FFileHelper::LoadFileToArray(
			UnderfundedBytes,
			*QaLedgerPath));
	TestEqual(
		TEXT("Underfunded canonical request rejects"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Retry,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Rejected);
	TArray<uint8> UnderfundedAfter;
	TestTrue(
		TEXT("Underfunded rejection remains readable"),
		FFileHelper::LoadFileToArray(
			UnderfundedAfter,
			*QaLedgerPath));
	TestTrue(
		TEXT("Underfunded rejection causes zero mutation"),
		UnderfundedAfter == UnderfundedBytes);

	TestTrue(
		TEXT("Underfunded profile resets for atomic save-failure proof"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("Atomic failure fixture starts funded"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			2200086400,
			true,
			Error));
	TArray<uint8> BeforeAtomicFailure;
	TestTrue(
		TEXT("Atomic failure fixture bytes are readable"),
		FFileHelper::LoadFileToArray(
			BeforeAtomicFailure,
			*QaLedgerPath));
	TestTrue(
		TEXT("Atomic failure fixture becomes read-only"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			true));
	const EOddsWellMatchWinnerRequestResult AtomicFailureResult =
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Retry,
			Balance,
			Error);
	TestTrue(
		TEXT("Atomic failure fixture returns writable for cleanup"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			false));
	TestEqual(
		TEXT("Native persistence failure rejects the whole request"),
		AtomicFailureResult,
		EOddsWellMatchWinnerRequestResult::Rejected);
	TArray<uint8> AfterAtomicFailure;
	TestTrue(
		TEXT("Atomic failure fixture remains readable"),
		FFileHelper::LoadFileToArray(
			AfterAtomicFailure,
			*QaLedgerPath));
	TestTrue(
		TEXT("Native persistence failure leaves ledger and requests byte-stable"),
		AfterAtomicFailure == BeforeAtomicFailure);
	FOddsWellOddsBucksLedger AtomicFailureLedger;
	TArray<FOddsWellMatchWinnerRequestRecord> AtomicFailureRequests;
	TestTrue(
		TEXT("Atomic failure state cold-loads"),
		LoadOddsWellOddsBucksState(
			true,
			AtomicFailureLedger,
			NextJobPayoutUnixSeconds,
			AtomicFailureRequests,
			bFound,
			Error));
	TestEqual(TEXT("Atomic failure keeps only job credit"), AtomicFailureLedger.GetEntries().Num(), 1);
	TestEqual(TEXT("Atomic failure keeps balance 100"), AtomicFailureLedger.GetBalance(), int64{100});
	TestEqual(TEXT("Atomic failure persists no request"), AtomicFailureRequests.Num(), 0);
	TestTrue(
		TEXT("Atomic failure profile cleanup succeeds"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("Canonical request offer cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalPendingMatchWinnerReceiptTest,
	"OddsWell.League.CanonicalPendingMatchWinnerReceipt",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalPendingMatchWinnerReceiptTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	TestTrue(
		TEXT("H26F isolated ledger starts clean"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	UGameplayStatics::DeleteGameInSlot(
		CanonicalRequestQaOfferSlot,
		CanonicalOfferUserIndex);

	const FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord Commitment = TestCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	TestEqual(
		TEXT("H26F exact H26C fixture creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000100,
			OfferRecord,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);

	FOddsWellOddsBucksLedger Funded;
	TestEqual(
		TEXT("H26F job credit applies"),
		Funded.Append(
			GetOddsWellFirstJobCommandId(),
			GetOddsWellFirstJobPayout(),
			GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("H26F funded ledger persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			2200086400,
			true,
			Error));

	FOddsWellMatchWinnerRequestRecord Accepted;
	int64 Balance = 0;
	TestEqual(
		TEXT("H26F exact H26E request fixture accepts"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000100,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Accepted,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);

	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	auto ReadLedgerBytes = [this, &QaLedgerPath](
		const TCHAR* Label,
		TArray<uint8>& OutBytes)
	{
		TestTrue(
			Label,
			FFileHelper::LoadFileToArray(OutBytes, *QaLedgerPath));
	};
	auto TestBytesUnchanged = [this, &ReadLedgerBytes](
		const TCHAR* Label,
		const TArray<uint8>& Before)
	{
		TArray<uint8> After;
		ReadLedgerBytes(Label, After);
		TestTrue(
			FString::Printf(TEXT("%s remains byte-stable"), Label),
			After == Before);
	};

	TArray<uint8> ExactDiskBytes;
	ReadLedgerBytes(TEXT("H26F exact state bytes read"), ExactDiskBytes);
	const UOddsWellOddsBucksSaveGame* ExactState =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				TEXT("OddsWellOddsBucksQA"),
				0));
	TestNotNull(TEXT("H26F exact schema-12 state reloads"), ExactState);
	TArray<uint8> ExactMemoryBytes;
	TestTrue(
		TEXT("H26F exact state serializes to memory"),
		ExactState
			&& UGameplayStatics::SaveGameToMemory(
				const_cast<UOddsWellOddsBucksSaveGame*>(ExactState),
				ExactMemoryBytes));
	auto RestoreExactState = [this, &ExactMemoryBytes]()
	{
		USaveGame* Restored =
			UGameplayStatics::LoadGameFromMemory(ExactMemoryBytes);
		TestTrue(
			TEXT("H26F exact state restores"),
			Restored
				&& UGameplayStatics::SaveGameToSlot(
					Restored,
					TEXT("OddsWellOddsBucksQA"),
					0));
	};

	FOddsWellCanonicalPendingMatchWinnerReceipt Receipt;
	TestEqual(
		TEXT("H26F exact pending receipt cold-loads"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Ready);
	TestEqual(TEXT("H26F selection is Harbor"), Receipt.SelectedTeam, Schedule.HomeTeam);
	TestEqual(TEXT("H26F selected probability is exact"), Receipt.SelectedWinProbabilityE8, int64{57586693});
	TestEqual(TEXT("H26F selected odds are exact"), Receipt.SelectedDecimalOddsE4, int64{17365});
	TestEqual(TEXT("H26F stake is 40"), Receipt.Stake, int64{40});
	TestEqual(TEXT("H26F gross return is 69"), Receipt.GrossReturn, int64{69});
	TestEqual(TEXT("H26F balance is 60"), Receipt.CurrentBalance, int64{60});
	TestEqual(TEXT("H26F server acceptance time is retained"), Receipt.AcceptedUnixSeconds, int64{2200000100});
	TestEqual(TEXT("H26F canonical tipoff is retained"), Receipt.LockUnixSeconds, Schedule.TipoffUnixSeconds);
	TestEqual(TEXT("H26F status remains pending lock"), Receipt.Status, FName(TEXT("accepted_pending_lock")));
	TestBytesUnchanged(TEXT("H26F cold read"), ExactDiskBytes);
	TestEqual(
		TEXT("H26F repeated cold read remains ready"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Ready);
	TestBytesUnchanged(TEXT("H26F repeated cold read"), ExactDiskBytes);

	TestEqual(
		TEXT("H26F at-tipoff request fails closed without a lock claim"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Rejected);
	TestTrue(TEXT("H26F post-tipoff rejection exposes no partial receipt"), Receipt.RequestId.IsEmpty() && Receipt.Stake == 0);
	TestBytesUnchanged(TEXT("H26F at-tipoff rejection"), ExactDiskBytes);

	FOddsWellCanonicalScheduledGameRecord WrongSchedule = Schedule;
	WrongSchedule.HomeTeam = TEXT("Archive Harbor");
	TestEqual(
		TEXT("H26F tampered H26A rejects"),
		LoadPendingReceipt(
			WrongSchedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Rejected);
	FOddsWellCanonicalPregameCommitmentRecord WrongCommitment = Commitment;
	WrongCommitment.InputClass = TEXT("private_model");
	TestEqual(
		TEXT("H26F tampered H26B rejects"),
		LoadPendingReceipt(
			Schedule,
			WrongCommitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Rejected);
	TestBytesUnchanged(TEXT("H26F H26A/B rejections"), ExactDiskBytes);

	UOddsWellCanonicalMatchWinnerOfferSaveGame* TamperedOffer =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
	TestNotNull(TEXT("H26F H26C state reloads for tamper"), TamperedOffer);
	if (TamperedOffer)
	{
		const FString ExactJson = TamperedOffer->CanonicalOfferJson;
		TamperedOffer->CanonicalOfferJson += TEXT(" ");
		TestTrue(
			TEXT("H26F tampered H26C fixture writes"),
			UGameplayStatics::SaveGameToSlot(
				TamperedOffer,
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
		TestEqual(
			TEXT("H26F tampered H26C rejects"),
			LoadPendingReceipt(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				2200000200,
				true,
				Receipt,
				Error),
			EOddsWellCanonicalPendingReceiptResult::Rejected);
		TamperedOffer->CanonicalOfferJson = ExactJson;
		TestTrue(
			TEXT("H26F exact H26C fixture restores"),
			UGameplayStatics::SaveGameToSlot(
				TamperedOffer,
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
	}
	TestBytesUnchanged(TEXT("H26F H26C rejection"), ExactDiskBytes);

	auto TestRejectedMutation =
		[this,
			&Schedule,
			&Commitment,
			&Receipt,
			&Error,
			&ExactMemoryBytes,
			&RestoreExactState,
			&ReadLedgerBytes,
			&TestBytesUnchanged](
			const TCHAR* Label,
			TFunction<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Candidate =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromMemory(ExactMemoryBytes));
		TestNotNull(
			FString::Printf(TEXT("%s fixture reloads"), Label),
			Candidate);
		if (!Candidate)
		{
			return;
		}
		Mutate(*Candidate);
		TestTrue(
			FString::Printf(TEXT("%s fixture persists"), Label),
			UGameplayStatics::SaveGameToSlot(
				Candidate,
				TEXT("OddsWellOddsBucksQA"),
				0));
		TArray<uint8> Before;
		ReadLedgerBytes(Label, Before);
		TestEqual(
			Label,
			LoadPendingReceipt(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				2200000200,
				true,
				Receipt,
				Error),
			EOddsWellCanonicalPendingReceiptResult::Rejected);
		TestTrue(
			FString::Printf(TEXT("%s exposes no partial"), Label),
			Receipt.RequestId.IsEmpty()
				&& Receipt.SelectedTeam.IsEmpty()
				&& Receipt.Stake == 0
				&& Receipt.CurrentBalance == 0);
		TestBytesUnchanged(Label, Before);
		RestoreExactState();
	};
	TestRejectedMutation(
		TEXT("H26F tampered request"),
		[](UOddsWellOddsBucksSaveGame& Save)
		{
			Save.MatchWinnerRequests[0].GrossReturn = 70;
		});
	TestRejectedMutation(
		TEXT("H26F multiple requests"),
		[](UOddsWellOddsBucksSaveGame& Save)
		{
			FOddsWellMatchWinnerRequestRecord Duplicate =
				Save.MatchWinnerRequests[0];
			Duplicate.RequestCommandId += TEXT(":duplicate");
			Duplicate.StakeLedgerCommandId = Duplicate.RequestCommandId;
			Save.MatchWinnerRequests.Add(Duplicate);
		});
	TestRejectedMutation(
		TEXT("H26F missing request with debit"),
		[](UOddsWellOddsBucksSaveGame& Save)
		{
			Save.MatchWinnerRequests.Reset();
		});
	TestRejectedMutation(
		TEXT("H26F migration-required schema"),
		[](UOddsWellOddsBucksSaveGame& Save)
		{
			Save.SchemaVersion = 11;
		});
	TestRejectedMutation(
		TEXT("H26F archive identity"),
		[](UOddsWellOddsBucksSaveGame& Save)
		{
			const FString ArchiveOfferId(
				TEXT("9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459"));
			Save.MatchWinnerRequests[0].OfferId = ArchiveOfferId;
		});

	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("H26F valid downstream lock fixture persists"),
		LockOddsWellMatchWinnerRequest(
			Accepted.RequestCommandId,
			TEXT("qa:h26f:downstream-lock"),
			Schedule.SeasonNumber,
			Schedule.GameNumber,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Locked);
	TArray<uint8> LockedBytes;
	ReadLedgerBytes(TEXT("H26F downstream bytes read"), LockedBytes);
	TestEqual(
		TEXT("H26F authoritative downstream evidence rejects pending receipt"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Rejected);
	TestBytesUnchanged(TEXT("H26F downstream rejection"), LockedBytes);
	RestoreExactState();

	TestTrue(
		TEXT("H26F exact state resets for missing-request proof"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26F valid funded no-request state persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			2200086400,
			true,
			Error));
	TArray<uint8> MissingBytes;
	ReadLedgerBytes(TEXT("H26F no-request bytes read"), MissingBytes);
	TestEqual(
		TEXT("H26F valid no-request state preserves the H26D offer path"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Missing);
	TestTrue(TEXT("H26F missing state exposes no receipt"), Receipt.RequestId.IsEmpty() && Receipt.Stake == 0);
	TestBytesUnchanged(TEXT("H26F no-request read"), MissingBytes);

	TestTrue(
		TEXT("H26F no-request state resets for old QA rejection"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26F old QA funded state persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			GetOddsWellUpcomingQaMatchWinnerLockUnixSeconds(),
			true,
			Error));
	FOddsWellMatchWinnerOffer OldQaOffer;
	TestTrue(
		TEXT("H26F old QA offer builds"),
		BuildOddsWellUpcomingQaMatchWinnerOffer(
			OldQaOffer,
			Error));
	FOddsWellMatchWinnerRequestRecord OldQaRequest;
	TestEqual(
		TEXT("H26F old QA request fixture accepts"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			OldQaOffer,
			GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
			OldQaOffer.HomeTeam,
			40,
			GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
			OldQaRequest,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	TArray<uint8> OldQaBytes;
	ReadLedgerBytes(TEXT("H26F old QA bytes read"), OldQaBytes);
	TestEqual(
		TEXT("H26F old QA request cannot masquerade as canonical"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			2200000200,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Rejected);
	TestBytesUnchanged(TEXT("H26F old QA rejection"), OldQaBytes);

	TestTrue(
		TEXT("H26F QA ledger cleanup succeeds"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26F offer fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerLockTest,
	"OddsWell.League.CanonicalMatchWinnerLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerLockTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H26G QA ledger starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	UGameplayStatics::DeleteGameInSlot(CanonicalRequestQaOfferSlot, CanonicalOfferUserIndex);

	const FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord Commitment = TestCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	TestEqual(
		TEXT("H26G exact H26C fixture creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			OfferRecord,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactOfferJson;
	TestTrue(
		TEXT("H26G exact offer rebuilds"),
		BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactOfferJson,
			Error));

	FOddsWellOddsBucksLedger Funded;
	TestEqual(
		TEXT("H26G job credit applies"),
		Funded.Append(
			GetOddsWellFirstJobCommandId(),
			GetOddsWellFirstJobPayout(),
			GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("H26G funded ledger persists"),
		SaveOddsWellOddsBucksLedger(Funded, 2200086400, true, Error));
	FOddsWellMatchWinnerRequestRecord Accepted;
	int64 Balance = 0;
	TestEqual(
		TEXT("H26G exact H26E request accepts"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Accepted,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);

	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	const FString QaOfferPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		CanonicalRequestQaOfferSlot + TEXT(".sav"));
	TArray<uint8> PendingDiskBytes;
	TArray<uint8> PendingMemoryBytes;
	TArray<uint8> OfferBytes;
	TestTrue(TEXT("H26G pending bytes read"), FFileHelper::LoadFileToArray(PendingDiskBytes, *QaLedgerPath));
	TestTrue(TEXT("H26G H26C bytes read"), FFileHelper::LoadFileToArray(OfferBytes, *QaOfferPath));
	TestTrue(
		TEXT("H26G pending state serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(TEXT("OddsWellOddsBucksQA"), 0),
			PendingMemoryBytes));
	auto RestorePending = [this, &PendingMemoryBytes]()
	{
		USaveGame* State = UGameplayStatics::LoadGameFromMemory(PendingMemoryBytes);
		TestTrue(
			TEXT("H26G pending state restores"),
			State && UGameplayStatics::SaveGameToSlot(State, TEXT("OddsWellOddsBucksQA"), 0));
	};
	auto TestLedgerUnchanged = [this, &QaLedgerPath](const TCHAR* Label, const TArray<uint8>& Before)
	{
		TArray<uint8> After;
		TestTrue(
			FString::Printf(TEXT("%s state remains readable"), Label),
			FFileHelper::LoadFileToArray(After, *QaLedgerPath));
		TestTrue(FString::Printf(TEXT("%s causes zero mutation"), Label), After == Before);
	};

	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("H26G early server observation rejects"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds - 1,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Rejected);
	TestLedgerUnchanged(TEXT("H26G early rejection"), PendingDiskBytes);
	TestEqual(
		TEXT("H26G late server observation rejects"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds + 1,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Rejected);
	TestLedgerUnchanged(TEXT("H26G late rejection"), PendingDiskBytes);

	FOddsWellCanonicalScheduledGameRecord WrongSchedule = Schedule;
	WrongSchedule.GameNumber++;
	TestEqual(
		TEXT("H26G tampered H26A rejects"),
		LockCanonicalRequestAtGameStart(
			WrongSchedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Rejected);
	FOddsWellCanonicalPregameCommitmentRecord WrongCommitment = Commitment;
	WrongCommitment.InputClass = TEXT("private_model");
	TestEqual(
		TEXT("H26G tampered H26B rejects"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			WrongCommitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Rejected);
	TestLedgerUnchanged(TEXT("H26G upstream rejections"), PendingDiskBytes);

	UOddsWellCanonicalMatchWinnerOfferSaveGame* TamperedOffer =
		Cast<UOddsWellCanonicalMatchWinnerOfferSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
	TestNotNull(TEXT("H26G H26C reloads for tamper"), TamperedOffer);
	if (TamperedOffer)
	{
		TamperedOffer->CanonicalOfferJson += TEXT(" ");
		TestTrue(
			TEXT("H26G tampered H26C persists"),
			UGameplayStatics::SaveGameToSlot(
				TamperedOffer,
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
		TestEqual(
			TEXT("H26G tampered H26C rejects"),
			LockCanonicalRequestAtGameStart(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				Schedule.TipoffUnixSeconds,
				true,
				Lock,
				Error),
			EOddsWellMatchWinnerLockResult::Rejected);
		TamperedOffer->CanonicalOfferJson = ExactOfferJson;
		TestTrue(
			TEXT("H26G exact H26C restores"),
			UGameplayStatics::SaveGameToSlot(
				TamperedOffer,
				CanonicalRequestQaOfferSlot,
				CanonicalOfferUserIndex));
	}
	TestLedgerUnchanged(TEXT("H26G H26C rejection"), PendingDiskBytes);

	TestEqual(
		TEXT("H26G exact server-owned transition locks"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Locked);
	const FString ExpectedRequestId =
		TEXT("canonical:h26e:match_winner:request:") + ExactOffer.OfferId;
	const FString ExpectedLockId =
		TEXT("canonical:h26g:match_winner:lock:") + ExactOffer.OfferId;
	TestEqual(TEXT("H26G request identity is fixed"), Lock.RequestCommandId, ExpectedRequestId);
	TestEqual(TEXT("H26G lock identity is fixed"), Lock.LockCommandId, ExpectedLockId);
	TestEqual(TEXT("H26G season remains one"), Lock.SeasonNumber, 1);
	TestEqual(TEXT("H26G game remains one"), Lock.GameNumber, 1);
	TestEqual(TEXT("H26G authority time is H26A tipoff"), Lock.AuthoritativeGameStartUnixSeconds, Schedule.TipoffUnixSeconds);
	TestEqual(TEXT("H26G stored lock time is H26A tipoff"), Lock.LockUnixSeconds, Schedule.TipoffUnixSeconds);
	TestEqual(TEXT("H26G decision is locked"), Lock.Decision, FName(TEXT("locked")));

	UOddsWellOddsBucksSaveGame* LockedState =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(TEXT("OddsWellOddsBucksQA"), 0));
	TestNotNull(TEXT("H26G locked state cold-loads"), LockedState);
	if (LockedState)
	{
		TestEqual(TEXT("H26G schema remains 12"), LockedState->SchemaVersion, 12);
		TestEqual(TEXT("H26G keeps two ledger entries"), LockedState->Entries.Num(), 2);
		TestEqual(TEXT("H26G keeps one request"), LockedState->MatchWinnerRequests.Num(), 1);
		TestEqual(TEXT("H26G adds exactly one lock"), LockedState->MatchWinnerLocks.Num(), 1);
		TestEqual(TEXT("H26G preserves cooldown"), LockedState->NextJobPayoutUnixSeconds, int64{2200086400});
		TestTrue(TEXT("H26G adds no result"), LockedState->MatchWinnerResultLinks.IsEmpty());
		TestTrue(TEXT("H26G adds no decision"), LockedState->MatchWinnerSettlementDecisions.IsEmpty());
		TestTrue(TEXT("H26G adds no loss finalization"), LockedState->MatchWinnerLossFinalizations.IsEmpty());
		TestTrue(TEXT("H26G adds no win finalization"), LockedState->MatchWinnerWinFinalizations.IsEmpty());
		TestTrue(TEXT("H26G adds no cancellation"), LockedState->MatchWinnerCanceledGames.IsEmpty());
		TestTrue(TEXT("H26G adds no void decision"), LockedState->MatchWinnerVoidDecisions.IsEmpty());
		TestTrue(TEXT("H26G adds no void finalization"), LockedState->MatchWinnerVoidFinalizations.IsEmpty());
		if (LockedState->Entries.Num() == 2 && LockedState->MatchWinnerRequests.Num() == 1)
		{
			TestEqual(TEXT("H26G credit remains +100"), LockedState->Entries[0].Delta, int64{100});
			TestEqual(TEXT("H26G debit remains -40"), LockedState->Entries[1].Delta, int64{-40});
			TestEqual(TEXT("H26G balance remains 60"), LockedState->Entries[1].BalanceAfter, int64{60});
			TestEqual(TEXT("H26G request remains pending lock"), LockedState->MatchWinnerRequests[0].Status, FName(TEXT("accepted_pending_lock")));
			TestEqual(TEXT("H26G request retains gross 69"), LockedState->MatchWinnerRequests[0].GrossReturn, int64{69});
		}
	}
	TArray<uint8> LockedDiskBytes;
	TArray<uint8> LockedMemoryBytes;
	TestTrue(TEXT("H26G locked bytes read"), FFileHelper::LoadFileToArray(LockedDiskBytes, *QaLedgerPath));
	TestTrue(
		TEXT("H26G locked state serializes"),
		LockedState && UGameplayStatics::SaveGameToMemory(LockedState, LockedMemoryBytes));
	TArray<uint8> OfferAfter;
	TestTrue(TEXT("H26G H26C remains readable"), FFileHelper::LoadFileToArray(OfferAfter, *QaOfferPath));
	TestTrue(TEXT("H26G leaves H26C bytes invariant"), OfferAfter == OfferBytes);

	FOddsWellCanonicalPendingMatchWinnerReceipt Receipt;
	TestEqual(
		TEXT("H26G post-lock pending receipt fails closed"),
		LoadPendingReceipt(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Receipt,
			Error),
		EOddsWellCanonicalPendingReceiptResult::Rejected);
	TestTrue(TEXT("H26G post-lock exposes no pending values"), Receipt.RequestId.IsEmpty() && Receipt.Stake == 0);
	FOddsWellMatchWinnerOfferPreview Preview;
	TestFalse(
		TEXT("H26G post-lock offer is unavailable"),
		LoadPreview(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			Preview,
			Error));
	TestTrue(TEXT("H26G post-lock exposes no teams or prices"), Preview.HomeTeam.IsEmpty() && Preview.AwayTeam.IsEmpty() && Preview.Selections.IsEmpty());
	TestLedgerUnchanged(TEXT("H26G post-lock reads"), LockedDiskBytes);

	FOddsWellMatchWinnerLockRecord Duplicate;
	TestEqual(
		TEXT("H26G cold exact retry is duplicate-safe"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Duplicate,
			Error),
		EOddsWellMatchWinnerLockResult::Duplicate);
	TestEqual(TEXT("H26G duplicate returns the same lock"), Duplicate.LockCommandId, ExpectedLockId);
	TestLedgerUnchanged(TEXT("H26G cold duplicate"), LockedDiskBytes);

	auto RejectMutation =
		[this,
			&Schedule,
			&Commitment,
			&Lock,
			&Error,
			&PendingMemoryBytes,
			&RestorePending,
			&QaLedgerPath,
			&TestLedgerUnchanged](
			const TCHAR* Label,
			TFunction<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* Candidate =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromMemory(PendingMemoryBytes));
		TestNotNull(FString::Printf(TEXT("%s fixture loads"), Label), Candidate);
		if (!Candidate)
		{
			return;
		}
		Mutate(*Candidate);
		TestTrue(
			FString::Printf(TEXT("%s fixture persists"), Label),
			UGameplayStatics::SaveGameToSlot(Candidate, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> Before;
		TestTrue(
			FString::Printf(TEXT("%s bytes read"), Label),
			FFileHelper::LoadFileToArray(Before, *QaLedgerPath));
		TestEqual(
			Label,
			LockCanonicalRequestAtGameStart(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				Schedule.TipoffUnixSeconds,
				true,
				Lock,
				Error),
			EOddsWellMatchWinnerLockResult::Rejected);
		TestLedgerUnchanged(Label, Before);
		RestorePending();
	};
	RejectMutation(TEXT("H26G request tamper"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].SelectedDecimalOddsE4++;
	});
	RejectMutation(TEXT("H26G ledger tamper"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.Entries[1].Delta = -39;
		Save.Entries[1].BalanceAfter = 61;
	});
	RejectMutation(TEXT("H26G multiple requests"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		const FOddsWellMatchWinnerRequestRecord Duplicate = Save.MatchWinnerRequests[0];
		Save.MatchWinnerRequests.Add(Duplicate);
	});
	RejectMutation(TEXT("H26G migration-required schema"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.SchemaVersion = 11;
	});
	RejectMutation(TEXT("H26G archive request identity"), [](UOddsWellOddsBucksSaveGame& Save)
	{
		Save.MatchWinnerRequests[0].OfferId =
			TEXT("9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459");
	});
	RejectMutation(TEXT("H26G conflicting lock"), [&ExpectedRequestId, &Schedule](UOddsWellOddsBucksSaveGame& Save)
	{
		FOddsWellMatchWinnerLockRecord& Conflict = Save.MatchWinnerLocks.AddDefaulted_GetRef();
		Conflict.LockCommandId = TEXT("conflict:h26g:lock");
		Conflict.RequestCommandId = ExpectedRequestId;
		Conflict.SeasonNumber = Schedule.SeasonNumber;
		Conflict.GameNumber = Schedule.GameNumber;
		Conflict.AuthoritativeGameStartUnixSeconds = Schedule.TipoffUnixSeconds;
		Conflict.LockUnixSeconds = Schedule.TipoffUnixSeconds;
		Conflict.Decision = TEXT("locked");
	});
	RejectMutation(TEXT("H26G multiple locks"), [&ExpectedRequestId, &ExpectedLockId, &Schedule](UOddsWellOddsBucksSaveGame& Save)
	{
		for (const FString& LockId : {ExpectedLockId, FString(TEXT("conflict:h26g:lock"))})
		{
			FOddsWellMatchWinnerLockRecord& Extra = Save.MatchWinnerLocks.AddDefaulted_GetRef();
			Extra.LockCommandId = LockId;
			Extra.RequestCommandId = ExpectedRequestId;
			Extra.SeasonNumber = Schedule.SeasonNumber;
			Extra.GameNumber = Schedule.GameNumber;
			Extra.AuthoritativeGameStartUnixSeconds = Schedule.TipoffUnixSeconds;
			Extra.LockUnixSeconds = Schedule.TipoffUnixSeconds;
			Extra.Decision = TEXT("locked");
		}
	});

	TestEqual(
		TEXT("H26G exact lock restores for downstream proof"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Locked);
	FOddsWellMatchWinnerResultLinkRecord Result;
	TestEqual(
		TEXT("H26G downstream result fixture links"),
		LinkOddsWellMatchWinnerResult(
			TEXT("qa:h26g:downstream-result"),
			ExpectedRequestId,
			ExpectedLockId,
			TEXT("oddswell-sealed-match-winner-result-v1"),
			TEXT("sealed-match-winner-result-v1"),
			1,
			1,
			TEXT("Harbor City Waves"),
			TEXT("Mesa Vista Sol"),
			101,
			104,
			TEXT("Mesa Vista Sol"),
			TEXT("00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75"),
			true,
			Result,
			Error),
		EOddsWellMatchWinnerResultLinkResult::Linked);
	TArray<uint8> DownstreamBytes;
	TestTrue(TEXT("H26G downstream bytes read"), FFileHelper::LoadFileToArray(DownstreamBytes, *QaLedgerPath));
	TestEqual(
		TEXT("H26G downstream evidence rejects lock retry"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Rejected);
	TestLedgerUnchanged(TEXT("H26G downstream rejection"), DownstreamBytes);
	RestorePending();

	TestTrue(TEXT("H26G pending state resets for old QA proof"), ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26G old QA funded state persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			GetOddsWellUpcomingQaMatchWinnerLockUnixSeconds(),
			true,
			Error));
	FOddsWellMatchWinnerOffer OldQaOffer;
	TestTrue(TEXT("H26G old QA offer builds"), BuildOddsWellUpcomingQaMatchWinnerOffer(OldQaOffer, Error));
	FOddsWellMatchWinnerRequestRecord OldQaRequest;
	TestEqual(
		TEXT("H26G old QA request accepts"),
		AcceptOddsWellUpcomingQaMatchWinnerRequest(
			OldQaOffer,
			GetOddsWellUpcomingQaMatchWinnerRequestCommandId(),
			OldQaOffer.HomeTeam,
			40,
			GetOddsWellUpcomingQaMatchWinnerAcceptedUnixSeconds(),
			OldQaRequest,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	TArray<uint8> OldQaBytes;
	TestTrue(TEXT("H26G old QA bytes read"), FFileHelper::LoadFileToArray(OldQaBytes, *QaLedgerPath));
	TestEqual(
		TEXT("H26G old QA chain cannot masquerade as canonical"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Rejected);
	TestLedgerUnchanged(TEXT("H26G old QA rejection"), OldQaBytes);
	RestorePending();

	TestTrue(
		TEXT("H26G pending fixture becomes read-only"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*QaLedgerPath, true));
	const EOddsWellMatchWinnerLockResult PersistenceFailure =
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error);
	TestTrue(
		TEXT("H26G pending fixture returns writable"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*QaLedgerPath, false));
	TestEqual(
		TEXT("H26G persistence failure rejects atomically"),
		PersistenceFailure,
		EOddsWellMatchWinnerLockResult::Rejected);
	TestLedgerUnchanged(TEXT("H26G persistence failure"), PendingDiskBytes);

	TestTrue(TEXT("H26G QA ledger cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26G offer fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerLossDecisionTest,
	"OddsWell.League.CanonicalMatchWinnerLossDecision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerLossDecisionTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	TestTrue(
		TEXT("H26M QA ledger starts clean"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	UGameplayStatics::DeleteGameInSlot(
		CanonicalRequestQaOfferSlot,
		CanonicalOfferUserIndex);
	const FOddsWellCanonicalScheduledGameRecord Schedule =
		TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord Commitment =
		TestCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	TestEqual(
		TEXT("H26M exact H26C fixture creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			OfferRecord,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactOfferJson;
	TestTrue(
		TEXT("H26M exact offer rebuilds"),
		BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactOfferJson,
			Error));
	FOddsWellOddsBucksLedger Funded;
	TestEqual(
		TEXT("H26M job credit applies"),
		Funded.Append(
			GetOddsWellFirstJobCommandId(),
			GetOddsWellFirstJobPayout(),
			GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("H26M funded ledger persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			2200086400,
			true,
			Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("H26M exact H26E request accepts Harbor 40"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("H26M exact H26G lock persists"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Locked);
	const FString ResultRecordSha256(
		TEXT(
			"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"));
	const FString ResultCommandId =
		TEXT("canonical:h26l:match_winner:result:")
		+ ResultRecordSha256;
	FOddsWellMatchWinnerResultLinkRecord ResultLink;
	TestEqual(
		TEXT("H26M exact H26L result link persists"),
		LinkOddsWellMatchWinnerResult(
			ResultCommandId,
			Request.RequestCommandId,
			Lock.LockCommandId,
			TEXT("oddswell-private-canonical-game-result-v1"),
			TEXT("oddswell-private-game-result-recorder-v1"),
			1,
			1,
			Schedule.HomeTeam,
			Schedule.AwayTeam,
			97,
			101,
			Schedule.AwayTeam,
			TEXT(
				"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"),
			true,
			ResultLink,
			Error),
		EOddsWellMatchWinnerResultLinkResult::Linked);

	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	TArray<uint8> ExactMemoryBytes;
	TestTrue(
		TEXT("H26M exact H26L baseline serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(
				TEXT("OddsWellOddsBucksQA"),
				0),
			ExactMemoryBytes));
	auto RestoreExactState =
		[this, &ExactMemoryBytes]()
	{
		USaveGame* State =
			UGameplayStatics::LoadGameFromMemory(
				ExactMemoryBytes);
		TestTrue(
			TEXT("H26M exact H26L baseline restores"),
			State
				&& UGameplayStatics::SaveGameToSlot(
					State,
					TEXT("OddsWellOddsBucksQA"),
					0));
	};
	auto TestZeroMutation =
		[this, &QaLedgerPath](
			const FString& Label,
			const TArray<uint8>& Before)
	{
		TArray<uint8> After;
		TestTrue(
			Label + TEXT(" remains readable"),
			FFileHelper::LoadFileToArray(
				After,
				*QaLedgerPath));
		TestTrue(
			Label + TEXT(" causes zero mutation"),
			After == Before);
	};
	auto RejectMutation =
		[this,
			&Schedule,
			&Commitment,
			&Error,
			&ExactMemoryBytes,
			&QaLedgerPath,
			&RestoreExactState,
			&TestZeroMutation](
			const FString& Label,
			TFunction<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* State =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromMemory(
					ExactMemoryBytes));
		TestNotNull(Label + TEXT(" fixture loads"), State);
		if (!State)
		{
			return;
		}
		Mutate(*State);
		TestTrue(
			Label + TEXT(" fixture persists"),
			UGameplayStatics::SaveGameToSlot(
				State,
				TEXT("OddsWellOddsBucksQA"),
				0));
		TArray<uint8> Before;
		TestTrue(
			Label + TEXT(" fixture bytes read"),
			FFileHelper::LoadFileToArray(
				Before,
				*QaLedgerPath));
		FOddsWellMatchWinnerSettlementDecisionRecord Rejected;
		TestEqual(
			Label,
			DecideCanonicalMatchWinnerLoss(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				true,
				Rejected,
				Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestTrue(
			Label + TEXT(" exposes no decision"),
			Rejected.DecisionCommandId.IsEmpty());
		TestZeroMutation(Label, Before);
		RestoreExactState();
	};
	RejectMutation(
		TEXT("H26M stale schema"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.SchemaVersion = 11;
		});
	RejectMutation(
		TEXT("H26M changed H26E request"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerRequests[0].GrossReturn++;
		});
	RejectMutation(
		TEXT("H26M changed stake debit"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.Entries[1].Delta = -50;
			State.Entries[1].BalanceAfter = 50;
		});
	RejectMutation(
		TEXT("H26M changed H26G lock"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerLocks[0].LockUnixSeconds++;
		});
	RejectMutation(
		TEXT("H26M archive result cannot relabel as H26L"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			FOddsWellMatchWinnerResultLinkRecord& Result =
				State.MatchWinnerResultLinks[0];
			Result.ResultSchema =
				TEXT("oddswell-sealed-match-winner-result-v1");
			Result.ResultVersion =
				TEXT("sealed-match-winner-result-v1");
			Result.HomeScore = 101;
			Result.AwayScore = 104;
			Result.Winner = TEXT("Mesa Vista Sol");
			Result.ReplaySealSha256 =
				TEXT(
					"00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75");
		});
	RejectMutation(
		TEXT("H26M non-loss outcome"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			FOddsWellMatchWinnerResultLinkRecord& Result =
				State.MatchWinnerResultLinks[0];
			Result.HomeScore = 101;
			Result.AwayScore = 97;
			Result.Winner = TEXT("Harbor City Waves");
		});
	RejectMutation(
		TEXT("H26M downstream cancellation"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerCanceledGames.AddDefaulted();
		});
	RejectMutation(
		TEXT("H26M downstream void"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerVoidDecisions.AddDefaulted();
		});

	FOddsWellMatchWinnerSettlementDecisionRecord ForeignDecision;
	TestEqual(
		TEXT("H26M valid foreign decision fixture persists"),
		DecideOddsWellMatchWinnerSettlement(
			ExactOffer,
			TEXT("qa:h26m:foreign-decision"),
			Request.RequestCommandId,
			Lock.LockCommandId,
			ResultLink.ResultCommandId,
			true,
			ForeignDecision,
			Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Decided);
	TArray<uint8> ForeignDecisionBytes;
	TestTrue(
		TEXT("H26M foreign decision bytes read"),
		FFileHelper::LoadFileToArray(
			ForeignDecisionBytes,
			*QaLedgerPath));
	FOddsWellMatchWinnerSettlementDecisionRecord RejectedDecision;
	TestEqual(
		TEXT("H26M foreign decision identity rejects"),
		DecideCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			RejectedDecision,
			Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestZeroMutation(
		TEXT("H26M foreign decision rejection"),
		ForeignDecisionBytes);
	FOddsWellMatchWinnerLossFinalizationRecord ForeignFinalization;
	TestEqual(
		TEXT("H26M valid finalization fixture persists"),
		FinalizeOddsWellMatchWinnerLoss(
			TEXT("qa:h26m:foreign-finalization"),
			ForeignDecision.DecisionCommandId,
			true,
			ForeignFinalization,
			Error),
		EOddsWellMatchWinnerLossFinalizationResult::Finalized);
	TArray<uint8> FinalizationBytes;
	TestTrue(
		TEXT("H26M finalization bytes read"),
		FFileHelper::LoadFileToArray(
			FinalizationBytes,
			*QaLedgerPath));
	TestEqual(
		TEXT("H26M finalized chain rejects"),
		DecideCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			RejectedDecision,
			Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestZeroMutation(
		TEXT("H26M finalized chain rejection"),
		FinalizationBytes);
	RestoreExactState();

	TArray<uint8> BeforeWriteFailure;
	TestTrue(
		TEXT("H26M pre-write-failure bytes read"),
		FFileHelper::LoadFileToArray(
			BeforeWriteFailure,
			*QaLedgerPath));
	TestTrue(
		TEXT("H26M fixture becomes read-only"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			true));
	const EOddsWellMatchWinnerSettlementDecisionResult
		WriteFailure =
			DecideCanonicalMatchWinnerLoss(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				true,
				RejectedDecision,
				Error);
	TestTrue(
		TEXT("H26M fixture returns writable"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			false));
	TestEqual(
		TEXT("H26M persistence failure rejects"),
		WriteFailure,
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestZeroMutation(
		TEXT("H26M persistence failure"),
		BeforeWriteFailure);

	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	TestEqual(
		TEXT("H26M exact loss decision appends"),
		DecideCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Decision,
			Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Decided);
	const FString ExpectedDecisionCommandId =
		TEXT("canonical:h26m:match_winner:decision:")
		+ ResultRecordSha256;
	TestEqual(
		TEXT("H26M decision identity derives only from H26K"),
		Decision.DecisionCommandId,
		ExpectedDecisionCommandId);
	TestEqual(
		TEXT("H26M request link is exact"),
		Decision.RequestCommandId,
		Request.RequestCommandId);
	TestEqual(
		TEXT("H26M lock link is exact"),
		Decision.LockCommandId,
		Lock.LockCommandId);
	TestEqual(
		TEXT("H26M result link is exact"),
		Decision.ResultCommandId,
		ResultLink.ResultCommandId);
	TestEqual(
		TEXT("H26M decision schema is approved"),
		Decision.DecisionSchema,
		FString(
			TEXT(
				"oddswell-match-winner-settlement-decision-v1")));
	TestEqual(
		TEXT("H26M decision version is approved"),
		Decision.DecisionVersion,
		FString(
			TEXT(
				"match-winner-settlement-decision-v1")));
	TestEqual(
		TEXT("H26M selected Harbor"),
		Decision.SelectedTeam,
		Schedule.HomeTeam);
	TestEqual(
		TEXT("H26M authoritative winner is Mesa"),
		Decision.AuthoritativeWinner,
		Schedule.AwayTeam);
	TestEqual(TEXT("H26M stake remains 40"), Decision.Stake, int64{40});
	TestEqual(
		TEXT("H26M outcome is lost"),
		Decision.Outcome,
		FName(TEXT("lost")));
	TestEqual(
		TEXT("H26M loss return due is zero"),
		Decision.GrossReturnDue,
		int64{0});
	TestEqual(
		TEXT("H26M status is pending apply"),
		Decision.Status,
		FName(TEXT("decided_pending_apply")));

	FOddsWellOddsBucksLedger AfterLedger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	bool bFound = false;
	TestTrue(
		TEXT("H26M decided state reloads"),
		LoadOddsWellOddsBucksWagerDecisionState(
			true,
			AfterLedger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			Results,
			Decisions,
			bFound,
			Error));
	TestTrue(TEXT("H26M decided state exists"), bFound);
	TestEqual(
		TEXT("H26M keeps two ledger entries"),
		AfterLedger.GetEntries().Num(),
		2);
	TestEqual(
		TEXT("H26M keeps stake debit -40"),
		AfterLedger.GetEntries()[1].Delta,
		int64{-40});
	TestEqual(
		TEXT("H26M keeps balance 60"),
		AfterLedger.GetBalance(),
		int64{60});
	TestEqual(TEXT("H26M keeps one request"), Requests.Num(), 1);
	TestEqual(TEXT("H26M keeps one lock"), Locks.Num(), 1);
	TestEqual(TEXT("H26M keeps one result link"), Results.Num(), 1);
	TestEqual(TEXT("H26M appends one decision"), Decisions.Num(), 1);
	const UOddsWellOddsBucksSaveGame* DecidedState =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				TEXT("OddsWellOddsBucksQA"),
				0));
	TestTrue(
		TEXT("H26M creates no later state"),
		DecidedState
			&& DecidedState->MatchWinnerLossFinalizations.IsEmpty()
			&& DecidedState->MatchWinnerWinFinalizations.IsEmpty()
			&& DecidedState->MatchWinnerCanceledGames.IsEmpty()
			&& DecidedState->MatchWinnerVoidDecisions.IsEmpty()
			&& DecidedState->MatchWinnerVoidFinalizations.IsEmpty());
	TArray<uint8> BeforeDuplicate;
	TestTrue(
		TEXT("H26M duplicate baseline bytes read"),
		FFileHelper::LoadFileToArray(
			BeforeDuplicate,
			*QaLedgerPath));
	FOddsWellMatchWinnerSettlementDecisionRecord Duplicate;
	TestEqual(
		TEXT("H26M exact retry is duplicate"),
		DecideCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Duplicate,
			Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Duplicate);
	TestEqual(
		TEXT("H26M duplicate returns immutable identity"),
		Duplicate.DecisionCommandId,
		Decision.DecisionCommandId);
	TestZeroMutation(
		TEXT("H26M duplicate"),
		BeforeDuplicate);

	TestTrue(
		TEXT("H26M QA ledger cleanup succeeds"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26M offer fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerCurrentMesaWinDecisionTest,
	"OddsWell.League.CanonicalMatchWinnerCurrentMesaWinDecision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerCurrentMesaWinDecisionTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("H26AI QA ledger starts clean"), ResetOddsWellQaOddsBucksAndVerify(Error));
	UGameplayStatics::DeleteGameInSlot(CanonicalRequestQaOfferSlot, CanonicalOfferUserIndex);
	FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	Schedule.SeasonCreatedUnixSeconds = 1785271449;
	Schedule.TipoffUnixSeconds = 1785273249;
	Schedule.OfferEligibleUnixSeconds = 1785271449;
	FOddsWellCanonicalPregameCommitmentRecord Commitment = TestCommitment();
	Commitment.ScheduleCreatedUnixSeconds = Schedule.SeasonCreatedUnixSeconds;
	Commitment.ScheduleTipoffUnixSeconds = Schedule.TipoffUnixSeconds;
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	TestEqual(
		TEXT("H26AI exact H26C fixture creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			OfferRecord,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactOfferJson;
	TestTrue(
		TEXT("H26AI exact current offer rebuilds"),
		BuildExpectedOffer(Schedule, Commitment, ExactOffer, ExactOfferJson, Error));
	TestEqual(
		TEXT("H26AI current offer identity is fixed"),
		ExactOffer.OfferId,
		FString(TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d")));

	FOddsWellOddsBucksLedger Funded;
	TestEqual(
		TEXT("H26AI job credit applies"),
		Funded.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(TEXT("H26AI funded profile persists"), SaveOddsWellOddsBucksLedger(Funded, 2200086400, true, Error));
	const FString RequestId = TEXT("canonical:h26e:match_winner:request:") + ExactOffer.OfferId;
	const FString LockId = TEXT("canonical:h26g:match_winner:lock:") + ExactOffer.OfferId;
	const FString ResultSha(TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289"));
	const FString ResultId = TEXT("canonical:h26l:match_winner:result:") + ResultSha;
	const FString DecisionId = TEXT("canonical:h26ai:match_winner:win-decision:") + ResultSha;
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("H26AI exact Mesa 40 request accepts in isolation"),
		AcceptOddsWellMatchWinnerRequest(
			ExactOffer,
			RequestId,
			ExactOffer.AwayTeam,
			40,
			Schedule.SeasonCreatedUnixSeconds + 100,
			true,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	TestEqual(TEXT("H26AI stake leaves balance 60"), Balance, int64{60});
	TestEqual(TEXT("H26AI Mesa probability is exact"), Request.SelectedWinProbabilityE8, int64{42413307});
	TestEqual(TEXT("H26AI Mesa review return is 94"), Request.GrossReturn, int64{94});
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("H26AI exact request locks"),
		LockOddsWellMatchWinnerRequest(
			RequestId,
			LockId,
			1,
			1,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Locked);
	FOddsWellMatchWinnerResultLinkRecord Result;
	TestEqual(
		TEXT("H26AI exact current Mesa result links"),
		LinkOddsWellMatchWinnerResult(
			ResultId,
			RequestId,
			LockId,
			TEXT("oddswell-private-canonical-game-result-v1"),
			TEXT("oddswell-private-game-result-recorder-v1"),
			1,
			1,
			ExactOffer.HomeTeam,
			ExactOffer.AwayTeam,
			79,
			113,
			ExactOffer.AwayTeam,
			TEXT("35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db"),
			true,
			Result,
			Error),
		EOddsWellMatchWinnerResultLinkResult::Linked);

	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(), TEXT("SaveGames"), TEXT("OddsWellOddsBucksQA.sav"));
	TArray<uint8> ExactEvidenceBytes;
	TestTrue(TEXT("H26AI exact evidence bytes read"), FFileHelper::LoadFileToArray(ExactEvidenceBytes, *QaLedgerPath));
	TArray<uint8> ExactEvidenceMemory;
	TestTrue(
		TEXT("H26AI exact evidence serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(TEXT("OddsWellOddsBucksQA"), 0),
			ExactEvidenceMemory));
	auto RestoreExactEvidence = [this, &ExactEvidenceMemory]()
	{
		USaveGame* State = UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory);
		TestTrue(
			TEXT("H26AI exact evidence restores"),
			State && UGameplayStatics::SaveGameToSlot(State, TEXT("OddsWellOddsBucksQA"), 0));
	};
	auto TestUnchanged = [this, &QaLedgerPath](const FString& Label, const TArray<uint8>& Before)
	{
		TArray<uint8> After;
		TestTrue(Label + TEXT(" remains readable"), FFileHelper::LoadFileToArray(After, *QaLedgerPath));
		TestTrue(Label + TEXT(" causes zero mutation"), After == Before);
	};

	FOddsWellMatchWinnerSettlementDecisionRecord Rejected;
	TestEqual(
		TEXT("H26AI missing exact offer rejects"),
		DecideOddsWellMatchWinnerSettlement(DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestUnchanged(TEXT("H26AI missing exact offer"), ExactEvidenceBytes);
	FOddsWellMatchWinnerOffer TamperedOffer = ExactOffer;
	TamperedOffer.Selections[1].WinProbabilityE8++;
	TestEqual(
		TEXT("H26AI tampered offer rejects"),
		DecideOddsWellMatchWinnerSettlement(TamperedOffer, DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestUnchanged(TEXT("H26AI tampered offer"), ExactEvidenceBytes);
	UOddsWellOddsBucksSaveGame* MissingResultState = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory));
	TestNotNull(TEXT("H26AI missing-result fixture loads"), MissingResultState);
	if (MissingResultState)
	{
		MissingResultState->MatchWinnerResultLinks.Reset();
		TestTrue(TEXT("H26AI missing-result fixture persists"), UGameplayStatics::SaveGameToSlot(MissingResultState, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> MissingBytes;
		TestTrue(TEXT("H26AI missing-result bytes read"), FFileHelper::LoadFileToArray(MissingBytes, *QaLedgerPath));
		TestEqual(
			TEXT("H26AI missing result rejects"),
			DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestUnchanged(TEXT("H26AI missing result"), MissingBytes);
		RestoreExactEvidence();
	}
	UOddsWellOddsBucksSaveGame* MissingLockState = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory));
	TestNotNull(TEXT("H26AN missing-lock fixture loads"), MissingLockState);
	if (MissingLockState)
	{
		MissingLockState->MatchWinnerLocks.Reset();
		TestTrue(TEXT("H26AN missing-lock fixture persists"), UGameplayStatics::SaveGameToSlot(MissingLockState, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> MissingLockBytes;
		TestTrue(TEXT("H26AN missing-lock bytes read"), FFileHelper::LoadFileToArray(MissingLockBytes, *QaLedgerPath));
		TestEqual(
			TEXT("H26AN partial chain rejects"),
			DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestUnchanged(TEXT("H26AN partial chain"), MissingLockBytes);
		RestoreExactEvidence();
	}
	UOddsWellOddsBucksSaveGame* TamperedRequestState = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory));
	TestNotNull(TEXT("H26AI tampered-request fixture loads"), TamperedRequestState);
	if (TamperedRequestState)
	{
		FOddsWellMatchWinnerRequestRecord& TamperedRequest = TamperedRequestState->MatchWinnerRequests[0];
		TamperedRequest.SelectedWinProbabilityE8++;
		TamperedRequest.SelectedDecimalOddsE4 = 100000000LL * 10000 / TamperedRequest.SelectedWinProbabilityE8;
		TamperedRequest.GrossReturn = TamperedRequest.Stake * 100000000LL / TamperedRequest.SelectedWinProbabilityE8;
		TestTrue(TEXT("H26AI tampered-request fixture persists"), UGameplayStatics::SaveGameToSlot(TamperedRequestState, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> TamperedRequestBytes;
		TestTrue(TEXT("H26AI tampered-request bytes read"), FFileHelper::LoadFileToArray(TamperedRequestBytes, *QaLedgerPath));
		TestEqual(
			TEXT("H26AI tampered request price rejects"),
			DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestUnchanged(TEXT("H26AI tampered request"), TamperedRequestBytes);
		RestoreExactEvidence();
	}

	UOddsWellOddsBucksSaveGame* ForeignState = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory));
	TestNotNull(TEXT("H26AI foreign-result fixture loads"), ForeignState);
	if (ForeignState)
	{
		FOddsWellMatchWinnerResultLinkRecord& ForeignResult = ForeignState->MatchWinnerResultLinks[0];
		ForeignResult.ResultCommandId = TEXT("canonical:h26l:match_winner:result:e4b8b4e26126612e1173b4509c67666df44cfcf7082b51051e9de0097f45d0c6");
		ForeignResult.HomeScore = 97;
		ForeignResult.AwayScore = 101;
		ForeignResult.ReplaySealSha256 = TEXT("efe7575962c88e9b8b4fcfcb6357c5307c6eeedd828b4b8f532c6e5eae985f62");
		TestTrue(TEXT("H26AI foreign-result fixture persists"), UGameplayStatics::SaveGameToSlot(ForeignState, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> ForeignBytes;
		TestTrue(TEXT("H26AI foreign-result bytes read"), FFileHelper::LoadFileToArray(ForeignBytes, *QaLedgerPath));
		TestEqual(
			TEXT("H26AI foreign result rejects"),
			DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ForeignResult.ResultCommandId, true, Rejected, Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestUnchanged(TEXT("H26AI foreign result"), ForeignBytes);
		RestoreExactEvidence();
	}
	UOddsWellOddsBucksSaveGame* MixedState = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory));
	TestNotNull(TEXT("H26AN mixed-chain fixture loads"), MixedState);
	if (MixedState)
	{
		MixedState->MatchWinnerRequests[0].OfferId =
			TEXT("5473d2345a9d45193c4e622302148082db3b0b00b78c1c19154e7ec5ce8d84cc");
		TestTrue(TEXT("H26AN mixed-chain fixture persists"), UGameplayStatics::SaveGameToSlot(MixedState, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> MixedBytes;
		TestTrue(TEXT("H26AN mixed-chain bytes read"), FFileHelper::LoadFileToArray(MixedBytes, *QaLedgerPath));
		TestEqual(
			TEXT("H26AN mixed current and foreign evidence rejects"),
			DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestUnchanged(TEXT("H26AN mixed chain"), MixedBytes);
		RestoreExactEvidence();
	}
	UOddsWellOddsBucksSaveGame* WrongResultState = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(ExactEvidenceMemory));
	TestNotNull(TEXT("H26AN wrong-result fixture loads"), WrongResultState);
	if (WrongResultState)
	{
		WrongResultState->MatchWinnerResultLinks[0].Winner =
			TEXT("Harbor City Waves");
		TestTrue(TEXT("H26AN wrong-result fixture persists"), UGameplayStatics::SaveGameToSlot(WrongResultState, TEXT("OddsWellOddsBucksQA"), 0));
		TArray<uint8> WrongResultBytes;
		TestTrue(TEXT("H26AN wrong-result bytes read"), FFileHelper::LoadFileToArray(WrongResultBytes, *QaLedgerPath));
		TestEqual(
			TEXT("H26AN wrong authoritative result rejects"),
			DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Rejected, Error),
			EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
		TestUnchanged(TEXT("H26AN wrong result"), WrongResultBytes);
		RestoreExactEvidence();
	}

	TestTrue(
		TEXT("H26AN atomic failure fixture becomes read-only"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			true));
	const EOddsWellMatchWinnerSettlementDecisionResult FailedWriteResult =
		DecideOddsWellMatchWinnerSettlement(
			ExactOffer,
			DecisionId,
			RequestId,
			LockId,
			ResultId,
			true,
			Rejected,
			Error);
	TestTrue(
		TEXT("H26AN atomic failure fixture returns writable"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			false));
	TestEqual(
		TEXT("H26AN failed write rejects"),
		FailedWriteResult,
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestUnchanged(TEXT("H26AN failed write"), ExactEvidenceBytes);

	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	TestEqual(
		TEXT("H26AI exact Mesa decision persists"),
		DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Decision, Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Decided);
	TestEqual(TEXT("H26AI selected team is Mesa"), Decision.SelectedTeam, ExactOffer.AwayTeam);
	TestEqual(TEXT("H26AI authoritative winner is Mesa"), Decision.AuthoritativeWinner, ExactOffer.AwayTeam);
	TestEqual(TEXT("H26AI outcome is won"), Decision.Outcome, FName(TEXT("won")));
	TestEqual(TEXT("H26AI return due is 94"), Decision.GrossReturnDue, int64{94});
	TestEqual(TEXT("H26AI probability remains exact"), Decision.SelectedWinProbabilityE8, int64{42413307});
	TestEqual(TEXT("H26AI formula remains approved"), Decision.PayoutFormula, ExactOffer.PayoutFormula);
	TestEqual(TEXT("H26AI remains pending application"), Decision.Status, FName(TEXT("decided_pending_apply")));

	FOddsWellOddsBucksLedger AfterLedger;
	int64 NextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	TestTrue(
		TEXT("H26AI cold decision state reloads"),
		LoadOddsWellOddsBucksWagerFinalizationState(
			true,
			AfterLedger,
			NextJobPayout,
			Requests,
			Locks,
			Results,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			bFound,
			Error));
	TestEqual(TEXT("H26AI keeps two ledger entries"), AfterLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("H26AI keeps balance 60"), AfterLedger.GetBalance(), int64{60});
	TestEqual(TEXT("H26AI keeps one decision"), Decisions.Num(), 1);
	TestTrue(TEXT("H26AI applies no payout or finalization"), LossFinalizations.IsEmpty() && WinFinalizations.IsEmpty());
	TArray<uint8> DecidedBytes;
	TestTrue(TEXT("H26AI decided bytes read"), FFileHelper::LoadFileToArray(DecidedBytes, *QaLedgerPath));
	FOddsWellMatchWinnerSettlementDecisionRecord Duplicate;
	TestEqual(
		TEXT("H26AI exact retry is duplicate"),
		DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId, RequestId, LockId, ResultId, true, Duplicate, Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Duplicate);
	TestUnchanged(TEXT("H26AI duplicate"), DecidedBytes);
	TestEqual(
		TEXT("H26AI conflicting second decision rejects"),
		DecideOddsWellMatchWinnerSettlement(ExactOffer, DecisionId + TEXT(":conflict"), RequestId, LockId, ResultId, true, Rejected, Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Rejected);
	TestUnchanged(TEXT("H26AI conflicting decision"), DecidedBytes);

	TestTrue(TEXT("H26AI QA ledger cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26AI offer fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(CanonicalRequestQaOfferSlot, CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

bool SeedCurrentMesaWinDecision(
	FString& OutDecisionId,
	FString& OutError)
{
	if (!ResetOddsWellQaOddsBucksAndVerify(OutError))
	{
		return false;
	}
	UGameplayStatics::DeleteGameInSlot(
		CanonicalRequestQaOfferSlot,
		CanonicalOfferUserIndex);
	FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	Schedule.SeasonCreatedUnixSeconds = 1785271449;
	Schedule.TipoffUnixSeconds = 1785273249;
	Schedule.OfferEligibleUnixSeconds = 1785271449;
	FOddsWellCanonicalPregameCommitmentRecord Commitment = TestCommitment();
	Commitment.ScheduleCreatedUnixSeconds = Schedule.SeasonCreatedUnixSeconds;
	Commitment.ScheduleTipoffUnixSeconds = Schedule.TipoffUnixSeconds;
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	FOddsWellMatchWinnerOffer ExactOffer;
	FString ExactOfferJson;
	FOddsWellOddsBucksLedger Funded;
	if (PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			OfferRecord,
			OutError) != EOddsWellCanonicalMatchWinnerOfferResult::Created
		|| !BuildExpectedOffer(
			Schedule,
			Commitment,
			ExactOffer,
			ExactOfferJson,
			OutError)
		|| ExactOffer.OfferId
			!= TEXT("c929f90b9fe2a7962f34b88819fd5405db1dd400a6d24cd0d7110081c8fb3e5d")
		|| Funded.Append(
			GetOddsWellFirstJobCommandId(),
			GetOddsWellFirstJobPayout(),
			GetOddsWellFirstJobReason()) != EOddsWellOddsBucksAppendResult::Applied
		|| !SaveOddsWellOddsBucksLedger(Funded, 2200086400, true, OutError))
	{
		return false;
	}

	const FString RequestId =
		TEXT("canonical:h26e:match_winner:request:") + ExactOffer.OfferId;
	const FString LockId =
		TEXT("canonical:h26g:match_winner:lock:") + ExactOffer.OfferId;
	const FString ResultSha(
		TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289"));
	const FString ResultId =
		TEXT("canonical:h26l:match_winner:result:") + ResultSha;
	OutDecisionId =
		TEXT("canonical:h26ai:match_winner:win-decision:") + ResultSha;
	FOddsWellMatchWinnerRequestRecord Request;
	FOddsWellMatchWinnerLockRecord Lock;
	FOddsWellMatchWinnerResultLinkRecord Result;
	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	int64 Balance = 0;
	return AcceptOddsWellMatchWinnerRequest(
			ExactOffer,
			RequestId,
			ExactOffer.AwayTeam,
			40,
			Schedule.SeasonCreatedUnixSeconds + 100,
			true,
			Request,
			Balance,
			OutError) == EOddsWellMatchWinnerRequestResult::Accepted
		&& Balance == 60
		&& LockOddsWellMatchWinnerRequest(
			RequestId,
			LockId,
			1,
			1,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			OutError) == EOddsWellMatchWinnerLockResult::Locked
		&& LinkOddsWellMatchWinnerResult(
			ResultId,
			RequestId,
			LockId,
			TEXT("oddswell-private-canonical-game-result-v1"),
			TEXT("oddswell-private-game-result-recorder-v1"),
			1,
			1,
			ExactOffer.HomeTeam,
			ExactOffer.AwayTeam,
			79,
			113,
			ExactOffer.AwayTeam,
			TEXT("35e604f306b5b2709f2ca8c5a4ad8b892ac6a4012a2c595072f6e326fa4e25db"),
			true,
			Result,
			OutError) == EOddsWellMatchWinnerResultLinkResult::Linked
		&& DecideOddsWellMatchWinnerSettlement(
			ExactOffer,
			OutDecisionId,
			RequestId,
			LockId,
			ResultId,
			true,
			Decision,
			OutError) == EOddsWellMatchWinnerSettlementDecisionResult::Decided
		&& Decision.GrossReturnDue == 94;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerCurrentMesaWinFinalizationTest,
	"OddsWell.League.CanonicalMatchWinnerCurrentMesaWinFinalization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerCurrentMesaWinFinalizationTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	FString DecisionId;
	const bool bSeeded = SeedCurrentMesaWinDecision(DecisionId, Error);
	TestTrue(TEXT("H26AJ exact H26AI pending win seeds"), bSeeded);
	if (!bSeeded)
	{
		ResetOddsWellQaOddsBucksAndVerify(Error);
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex);
		return false;
	}

	const FString FinalizationId =
		FString(TEXT("canonical:h26aj:match_winner:win-finalization:"))
		+ TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	FOddsWellCanonicalSettledLossReceipt PendingReceipt;
	TestEqual(
		TEXT("H26AL pending win exposes no settled receipt"),
		LoadOddsWellCanonicalSettledLossReceiptEvidence(
			true,
			PendingReceipt,
			Error),
		EOddsWellCanonicalSettledLossReceiptResult::Rejected);
	TArray<uint8> PendingMemory;
	TestTrue(
		TEXT("H26AJ pending evidence serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(TEXT("OddsWellOddsBucksQA"), 0),
			PendingMemory));
	UOddsWellOddsBucksSaveGame* Tampered = Cast<UOddsWellOddsBucksSaveGame>(
		UGameplayStatics::LoadGameFromMemory(PendingMemory));
	TestNotNull(TEXT("H26AJ tamper fixture loads"), Tampered);
	if (Tampered)
	{
		Tampered->MatchWinnerSettlementDecisions[0].GrossReturnDue = 95;
		TestTrue(
			TEXT("H26AJ tampered pending evidence persists"),
			UGameplayStatics::SaveGameToSlot(
				Tampered,
				TEXT("OddsWellOddsBucksQA"),
				0));
		TArray<uint8> TamperedBytes;
		TestTrue(
			TEXT("H26AJ tampered bytes read"),
			FFileHelper::LoadFileToArray(TamperedBytes, *QaLedgerPath));
		FOddsWellMatchWinnerWinFinalizationRecord Rejected;
		TestEqual(
			TEXT("H26AJ altered return rejects"),
			FinalizeOddsWellMatchWinnerWin(
				FinalizationId,
				DecisionId,
				true,
				Rejected,
				Error),
			EOddsWellMatchWinnerWinFinalizationResult::Rejected);
		TArray<uint8> AfterRejected;
		TestTrue(
			TEXT("H26AJ rejected bytes remain readable"),
			FFileHelper::LoadFileToArray(AfterRejected, *QaLedgerPath));
		TestTrue(
			TEXT("H26AJ altered return causes zero mutation"),
			AfterRejected == TamperedBytes);
		TestTrue(
			TEXT("H26AJ exact pending evidence restores"),
			UGameplayStatics::SaveGameToSlot(
				UGameplayStatics::LoadGameFromMemory(PendingMemory),
				TEXT("OddsWellOddsBucksQA"),
				0));
	}

	TArray<uint8> PendingBytes;
	TestTrue(
		TEXT("H26AO pending bytes read before failed write"),
		FFileHelper::LoadFileToArray(PendingBytes, *QaLedgerPath));
	TestTrue(
		TEXT("H26AO pending fixture becomes read-only"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			true));
	FOddsWellMatchWinnerWinFinalizationRecord FailedWrite;
	const EOddsWellMatchWinnerWinFinalizationResult FailedWriteResult =
		FinalizeOddsWellMatchWinnerWin(
			FinalizationId,
			DecisionId,
			true,
			FailedWrite,
			Error);
	TestTrue(
		TEXT("H26AO pending fixture returns writable"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			false));
	TestEqual(
		TEXT("H26AO failed write rejects"),
		FailedWriteResult,
		EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TArray<uint8> AfterFailedWrite;
	TestTrue(
		TEXT("H26AO failed-write bytes reread"),
		FFileHelper::LoadFileToArray(
			AfterFailedWrite,
			*QaLedgerPath));
	TestTrue(
		TEXT("H26AO failed write causes zero mutation"),
		AfterFailedWrite == PendingBytes);

	FOddsWellMatchWinnerWinFinalizationRecord Finalization;
	TestEqual(
		TEXT("H26AJ exact return applies once"),
		FinalizeOddsWellMatchWinnerWin(
			FinalizationId,
			DecisionId,
			true,
			Finalization,
			Error),
		EOddsWellMatchWinnerWinFinalizationResult::Finalized);
	TestEqual(TEXT("H26AJ return applied is 94"), Finalization.GrossReturnApplied, int64{94});
	TestEqual(TEXT("H26AJ status is settled won"), Finalization.Status, FName(TEXT("settled_won")));
	TestEqual(TEXT("H26AJ final balance is 154"), Finalization.ObservedFinalBalance, int64{154});
	TestEqual(TEXT("H26AJ ledger count is three"), Finalization.ObservedLedgerEntryCount, 3);
	TArray<uint8> BeforeReceiptRead;
	TestTrue(
		TEXT("H26AL exact finalized source bytes read"),
		FFileHelper::LoadFileToArray(BeforeReceiptRead, *QaLedgerPath));
	FOddsWellCanonicalSettledLossReceipt PlayerReceipt;
	TestEqual(
		TEXT("H26AL exact current win exposes one settled receipt"),
		LoadOddsWellCanonicalSettledLossReceiptEvidence(
			true,
			PlayerReceipt,
			Error),
		EOddsWellCanonicalSettledLossReceiptResult::Ready);
	TestTrue(
		TEXT("H26AL receipt exposes only exact player-facing win values"),
		PlayerReceipt.Outcome == FName(TEXT("won"))
			&& PlayerReceipt.SelectedTeam == TEXT("Mesa Vista Sol")
			&& PlayerReceipt.HomeTeam == TEXT("Harbor City Waves")
			&& PlayerReceipt.AwayTeam == TEXT("Mesa Vista Sol")
			&& PlayerReceipt.Winner == TEXT("Mesa Vista Sol")
			&& PlayerReceipt.Stake == 40
			&& PlayerReceipt.HomeScore == 79
			&& PlayerReceipt.AwayScore == 113
			&& PlayerReceipt.Returned == 94
			&& PlayerReceipt.Net == 54
			&& PlayerReceipt.LedgerEntryCount == 3
			&& PlayerReceipt.CurrentBalance == 154);
	TArray<uint8> AfterReceiptRead;
	TestTrue(
		TEXT("H26AL source bytes reread"),
		FFileHelper::LoadFileToArray(AfterReceiptRead, *QaLedgerPath));
	TestTrue(
		TEXT("H26AL receipt read is byte stable"),
		AfterReceiptRead == BeforeReceiptRead);

	FOddsWellOddsBucksLedger Ledger;
	int64 NextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	TestTrue(
		TEXT("H26AJ finalized state cold reloads"),
		LoadOddsWellOddsBucksWagerFinalizationState(
			true,
			Ledger,
			NextJobPayout,
			Requests,
			Locks,
			Results,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			bFound,
			Error));
	TestTrue(TEXT("H26AJ finalized state exists"), bFound);
	TestEqual(TEXT("H26AJ finalized ledger has three entries"), Ledger.GetEntries().Num(), 3);
	TestEqual(TEXT("H26AJ payout delta is plus 94"), Ledger.GetEntries()[2].Delta, int64{94});
	TestEqual(TEXT("H26AJ payout balance is 154"), Ledger.GetEntries()[2].BalanceAfter, int64{154});
	TestEqual(TEXT("H26AJ final balance reloads as 154"), Ledger.GetBalance(), int64{154});
	TestEqual(TEXT("H26AJ has one win finalization"), WinFinalizations.Num(), 1);
	TestTrue(TEXT("H26AJ has no loss finalization"), LossFinalizations.IsEmpty());
	TestEqual(TEXT("H26AJ decision remains pending apply"), Decisions[0].Status, FName(TEXT("decided_pending_apply")));

	TArray<uint8> FinalizedBytes;
	TestTrue(TEXT("H26AJ finalized bytes read"), FFileHelper::LoadFileToArray(FinalizedBytes, *QaLedgerPath));
	FOddsWellMatchWinnerWinFinalizationRecord Duplicate;
	TestEqual(
		TEXT("H26AJ exact cold retry is duplicate"),
		FinalizeOddsWellMatchWinnerWin(
			FinalizationId,
			DecisionId,
			true,
			Duplicate,
			Error),
			EOddsWellMatchWinnerWinFinalizationResult::Duplicate);
	FOddsWellMatchWinnerWinFinalizationRecord Conflict;
	TestEqual(
		TEXT("H26AJ conflicting second finalization rejects"),
		FinalizeOddsWellMatchWinnerWin(
			FinalizationId + TEXT(":conflict"),
			DecisionId,
			true,
			Conflict,
			Error),
			EOddsWellMatchWinnerWinFinalizationResult::Rejected);
	TArray<uint8> AfterRetries;
	TestTrue(TEXT("H26AJ retry bytes read"), FFileHelper::LoadFileToArray(AfterRetries, *QaLedgerPath));
	TestTrue(TEXT("H26AJ duplicate and conflict are byte stable"), AfterRetries == FinalizedBytes);

	const FString ProjectionPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("Admin"),
		TEXT("MatchWinnerReconciliationQA.json"));
	FString ProjectionJson;
	TestTrue(TEXT("H26AJ existing projection writes"), FFileHelper::LoadFileToString(ProjectionJson, *ProjectionPath));
	TestTrue(TEXT("H26AJ projection contains probability 42413307"), ProjectionJson.Contains(TEXT("42413307")));
	TestTrue(TEXT("H26AJ projection contains return 94"), ProjectionJson.Contains(TEXT("\"gross_return_applied\": 94")));
	TestTrue(TEXT("H26AJ projection contains balance 154"), ProjectionJson.Contains(TEXT("\"final_balance\": 154")));

	UOddsWellOddsBucksSaveGame* Automatic =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				TEXT("OddsWellOddsBucksQA"),
				0));
	TestNotNull(TEXT("H26AQ automatic finalized source loads"), Automatic);
	if (Automatic)
	{
		const FString AutomaticDecisionId =
			FString(TEXT("canonical:h26an:match_winner:win-decision:"))
			+ TEXT("05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
		Automatic->MatchWinnerSettlementDecisions[0].DecisionCommandId =
			AutomaticDecisionId;
		Automatic->MatchWinnerWinFinalizations[0].DecisionCommandId =
			AutomaticDecisionId;
		TestTrue(
			TEXT("H26AQ exact automatic source persists"),
			UGameplayStatics::SaveGameToSlot(
				Automatic,
				TEXT("OddsWellOddsBucksQA"),
				0));
		TArray<uint8> AutomaticMemory;
		TestTrue(
			TEXT("H26AQ exact automatic source serializes"),
			UGameplayStatics::SaveGameToMemory(
				Automatic,
				AutomaticMemory));
		TestTrue(
			TEXT("H26AQ removes the H26AP projection dependency"),
			IFileManager::Get().Delete(*ProjectionPath));
		TestFalse(
			TEXT("H26AQ projection is absent before receipt read"),
			IFileManager::Get().FileExists(*ProjectionPath));
		TArray<uint8> BeforeAutomaticRead;
		const FDateTime BeforeAutomaticMtime =
			IFileManager::Get().GetTimeStamp(*QaLedgerPath);
		TestTrue(
			TEXT("H26AQ automatic source bytes read"),
			FFileHelper::LoadFileToArray(
				BeforeAutomaticRead,
				*QaLedgerPath));
		FOddsWellCanonicalSettledLossReceipt AutomaticReceipt;
		TestEqual(
			TEXT("H26AQ exact automatic win exposes one settled receipt"),
			LoadOddsWellCanonicalSettledLossReceiptEvidence(
				true,
				AutomaticReceipt,
				Error),
			EOddsWellCanonicalSettledLossReceiptResult::Ready);
		TestTrue(
			TEXT("H26AQ receipt exposes only exact automatic player values"),
			AutomaticReceipt.Outcome == FName(TEXT("won"))
				&& AutomaticReceipt.SelectedTeam == TEXT("Mesa Vista Sol")
				&& AutomaticReceipt.HomeTeam == TEXT("Harbor City Waves")
				&& AutomaticReceipt.AwayTeam == TEXT("Mesa Vista Sol")
				&& AutomaticReceipt.Winner == TEXT("Mesa Vista Sol")
				&& AutomaticReceipt.Stake == 40
				&& AutomaticReceipt.HomeScore == 79
				&& AutomaticReceipt.AwayScore == 113
				&& AutomaticReceipt.Returned == 94
				&& AutomaticReceipt.Net == 54
				&& AutomaticReceipt.LedgerEntryCount == 3
				&& AutomaticReceipt.CurrentBalance == 154);
		TArray<uint8> AfterAutomaticRead;
		TestTrue(
			TEXT("H26AQ automatic source bytes reread"),
			FFileHelper::LoadFileToArray(
				AfterAutomaticRead,
				*QaLedgerPath));
		TestTrue(
			TEXT("H26AQ receipt read preserves bytes and mtime"),
			AfterAutomaticRead == BeforeAutomaticRead
				&& IFileManager::Get().GetTimeStamp(*QaLedgerPath)
					== BeforeAutomaticMtime);
		TestFalse(
			TEXT("H26AQ receipt read does not recreate reconciliation"),
			IFileManager::Get().FileExists(*ProjectionPath));

		auto RejectAutomatic =
			[this, &AutomaticMemory, &QaLedgerPath, &Error](
				const TCHAR* Label,
				TFunctionRef<void(UOddsWellOddsBucksSaveGame&)> Mutate)
		{
			UOddsWellOddsBucksSaveGame* Changed =
				Cast<UOddsWellOddsBucksSaveGame>(
					UGameplayStatics::LoadGameFromMemory(
						AutomaticMemory));
			TestNotNull(
				FString::Printf(TEXT("%s fixture loads"), Label),
				Changed);
			if (!Changed)
			{
				return;
			}
			Mutate(*Changed);
			TestTrue(
				FString::Printf(TEXT("%s fixture persists"), Label),
				UGameplayStatics::SaveGameToSlot(
					Changed,
					TEXT("OddsWellOddsBucksQA"),
					0));
			TArray<uint8> Before;
			const FDateTime BeforeMtime =
				IFileManager::Get().GetTimeStamp(*QaLedgerPath);
			TestTrue(
				FString::Printf(TEXT("%s bytes read"), Label),
				FFileHelper::LoadFileToArray(Before, *QaLedgerPath));
			FOddsWellCanonicalSettledLossReceipt RejectedReceipt;
			TestEqual(
				FString::Printf(TEXT("%s receipt rejects"), Label),
				LoadOddsWellCanonicalSettledLossReceiptEvidence(
					true,
					RejectedReceipt,
					Error),
				EOddsWellCanonicalSettledLossReceiptResult::Rejected);
			TestTrue(
				FString::Printf(TEXT("%s exposes no partial receipt"), Label),
				RejectedReceipt.Outcome.IsNone()
					&& RejectedReceipt.SelectedTeam.IsEmpty()
					&& RejectedReceipt.HomeTeam.IsEmpty()
					&& RejectedReceipt.AwayTeam.IsEmpty()
					&& RejectedReceipt.Winner.IsEmpty()
					&& RejectedReceipt.Stake == 0
					&& RejectedReceipt.HomeScore == 0
					&& RejectedReceipt.AwayScore == 0
					&& RejectedReceipt.Returned == 0
					&& RejectedReceipt.Net == 0
					&& RejectedReceipt.LedgerEntryCount == 0
					&& RejectedReceipt.CurrentBalance == 0);
			TArray<uint8> After;
			TestTrue(
				FString::Printf(TEXT("%s bytes reread"), Label),
				FFileHelper::LoadFileToArray(After, *QaLedgerPath));
			TestTrue(
				FString::Printf(TEXT("%s read preserves source"), Label),
				After == Before
					&& IFileManager::Get().GetTimeStamp(*QaLedgerPath)
						== BeforeMtime);
		};
		RejectAutomatic(
			TEXT("H26AQ pending H26AN without H26AO"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerWinFinalizations.Reset();
				State.Entries.SetNum(2);
			});
		RejectAutomatic(
			TEXT("H26AQ partial automatic chain"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerWinFinalizations.Reset();
			});
		RejectAutomatic(
			TEXT("H26AQ mixed isolated automatic chain"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerWinFinalizations[0].DecisionCommandId =
					TEXT("canonical:h26ai:match_winner:win-decision:05a4a2a1488d4852318a398ff6e8eaf4a3cac47257b441feceb7426a4b5b0289");
			});
		RejectAutomatic(
			TEXT("H26AQ altered automatic return"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerWinFinalizations[0].GrossReturnApplied = 95;
			});
		RejectAutomatic(
			TEXT("H26AQ altered payout linkage"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerWinFinalizations[0].PayoutLedgerCommandId +=
					TEXT(":foreign");
			});
		RejectAutomatic(
			TEXT("H26AQ altered payout ledger"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.Entries[2].Delta = 93;
			});
		RejectAutomatic(
			TEXT("H26AQ altered final balance"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerWinFinalizations[0].ObservedFinalBalance = 153;
			});
		RejectAutomatic(
			TEXT("H26AQ altered result"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerResultLinks[0].HomeScore = 80;
			});
		RejectAutomatic(
			TEXT("H26AQ altered replay seal"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerResultLinks[0].ReplaySealSha256 =
					FString::ChrN(64, TCHAR('f'));
			});
		RejectAutomatic(
			TEXT("H26AQ altered decision link"),
			[](UOddsWellOddsBucksSaveGame& State)
			{
				State.MatchWinnerSettlementDecisions[0].ResultCommandId +=
					TEXT(":foreign");
			});
	}

	TestTrue(TEXT("H26AJ QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26AJ offer fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerLossFinalizationTest,
	"OddsWell.League.CanonicalMatchWinnerLossFinalization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerLossFinalizationTest::RunTest(
	const FString& Parameters)
{
	FString Error;
	TestTrue(
		TEXT("H26N QA ledger starts clean"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	UGameplayStatics::DeleteGameInSlot(
		CanonicalRequestQaOfferSlot,
		CanonicalOfferUserIndex);
	const FOddsWellCanonicalScheduledGameRecord Schedule =
		TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord Commitment =
		TestCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord OfferRecord;
	TestEqual(
		TEXT("H26N exact H26C fixture creates"),
		PersistOffer(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			OfferRecord,
			Error),
		EOddsWellCanonicalMatchWinnerOfferResult::Created);
	FOddsWellOddsBucksLedger Funded;
	TestEqual(
		TEXT("H26N job credit applies"),
		Funded.Append(
			GetOddsWellFirstJobCommandId(),
			GetOddsWellFirstJobPayout(),
			GetOddsWellFirstJobReason()),
		EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(
		TEXT("H26N funded ledger persists"),
		SaveOddsWellOddsBucksLedger(
			Funded,
			2200086400,
			true,
			Error));
	FOddsWellMatchWinnerRequestRecord Request;
	int64 Balance = 0;
	TestEqual(
		TEXT("H26N exact H26E request accepts Harbor 40"),
		AcceptCanonicalRequest(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.SeasonCreatedUnixSeconds + 100,
			true,
			OfferRecord.OfferId,
			Schedule.HomeTeam,
			40,
			Request,
			Balance,
			Error),
		EOddsWellMatchWinnerRequestResult::Accepted);
	FOddsWellMatchWinnerLockRecord Lock;
	TestEqual(
		TEXT("H26N exact H26G lock persists"),
		LockCanonicalRequestAtGameStart(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			Schedule.TipoffUnixSeconds,
			true,
			Lock,
			Error),
		EOddsWellMatchWinnerLockResult::Locked);
	const FString ResultRecordSha256(
		TEXT(
			"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"));
	FOddsWellMatchWinnerResultLinkRecord ResultLink;
	TestEqual(
		TEXT("H26N exact H26L result link persists"),
		LinkOddsWellMatchWinnerResult(
			TEXT("canonical:h26l:match_winner:result:")
				+ ResultRecordSha256,
			Request.RequestCommandId,
			Lock.LockCommandId,
			TEXT("oddswell-private-canonical-game-result-v1"),
			TEXT("oddswell-private-game-result-recorder-v1"),
			1,
			1,
			Schedule.HomeTeam,
			Schedule.AwayTeam,
			97,
			101,
			Schedule.AwayTeam,
			TEXT(
				"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"),
			true,
			ResultLink,
			Error),
		EOddsWellMatchWinnerResultLinkResult::Linked);
	FOddsWellMatchWinnerSettlementDecisionRecord Decision;
	TestEqual(
		TEXT("H26N exact H26M loss decision persists"),
		DecideCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Decision,
			Error),
		EOddsWellMatchWinnerSettlementDecisionResult::Decided);

	const FString QaLedgerPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("SaveGames"),
		TEXT("OddsWellOddsBucksQA.sav"));
	TArray<uint8> ExactH26MBytes;
	TestTrue(
		TEXT("H26N exact H26M baseline serializes"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(
				TEXT("OddsWellOddsBucksQA"),
				0),
			ExactH26MBytes));
	auto RestoreExactState =
		[this, &ExactH26MBytes]()
	{
		USaveGame* State =
			UGameplayStatics::LoadGameFromMemory(
				ExactH26MBytes);
		TestTrue(
			TEXT("H26N exact H26M baseline restores"),
			State
				&& UGameplayStatics::SaveGameToSlot(
					State,
					TEXT("OddsWellOddsBucksQA"),
					0));
	};
	auto TestZeroMutation =
		[this, &QaLedgerPath](
			const FString& Label,
			const TArray<uint8>& Before)
	{
		TArray<uint8> After;
		TestTrue(
			Label + TEXT(" remains readable"),
			FFileHelper::LoadFileToArray(
				After,
				*QaLedgerPath));
		TestTrue(
			Label + TEXT(" causes zero mutation"),
			After == Before);
	};
	auto RejectMutation =
		[this,
			&Schedule,
			&Commitment,
			&Error,
			&ExactH26MBytes,
			&RestoreExactState,
			&TestZeroMutation,
			&QaLedgerPath](
			const FString& Label,
			TFunction<void(UOddsWellOddsBucksSaveGame&)> Mutate)
	{
		UOddsWellOddsBucksSaveGame* State =
			Cast<UOddsWellOddsBucksSaveGame>(
				UGameplayStatics::LoadGameFromMemory(
					ExactH26MBytes));
		TestNotNull(Label + TEXT(" fixture loads"), State);
		if (!State)
		{
			return;
		}
		Mutate(*State);
		TestTrue(
			Label + TEXT(" fixture persists"),
			UGameplayStatics::SaveGameToSlot(
				State,
				TEXT("OddsWellOddsBucksQA"),
				0));
		TArray<uint8> Before;
		TestTrue(
			Label + TEXT(" fixture bytes read"),
			FFileHelper::LoadFileToArray(
				Before,
				*QaLedgerPath));
		FOddsWellMatchWinnerLossFinalizationRecord Rejected;
		TestEqual(
			Label,
			FinalizeCanonicalMatchWinnerLoss(
				Schedule,
				Commitment,
				CanonicalRequestQaOfferSlot,
				true,
				Rejected,
				Error),
			EOddsWellMatchWinnerLossFinalizationResult::Rejected);
		TestTrue(
			Label + TEXT(" exposes no finalization"),
			Rejected.FinalizationCommandId.IsEmpty());
		TestZeroMutation(Label, Before);
		RestoreExactState();
	};
	RejectMutation(
		TEXT("H26N stale schema"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.SchemaVersion = 11;
		});
	RejectMutation(
		TEXT("H26N changed H26E request"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerRequests[0].GrossReturn++;
		});
	RejectMutation(
		TEXT("H26N changed stake debit"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.Entries[1].Delta = -50;
			State.Entries[1].BalanceAfter = 50;
		});
	RejectMutation(
		TEXT("H26N changed H26G lock"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerLocks[0].LockUnixSeconds++;
		});
	RejectMutation(
		TEXT("H26N changed H26L result"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			FString& CommandId =
				State.MatchWinnerResultLinks[0].ResultCommandId;
			CommandId[CommandId.Len() - 1] = TCHAR('f');
		});
	RejectMutation(
		TEXT("H26N nonzero return due"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerSettlementDecisions[0].GrossReturnDue = 1;
		});
	RejectMutation(
		TEXT("H26N fresh Harbor win stops"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			FOddsWellMatchWinnerResultLinkRecord& Result =
				State.MatchWinnerResultLinks[0];
			Result.HomeScore = 115;
			Result.AwayScore = 101;
			Result.Winner = TEXT("Harbor City Waves");
			FOddsWellMatchWinnerSettlementDecisionRecord& ExistingDecision =
				State.MatchWinnerSettlementDecisions[0];
			ExistingDecision.AuthoritativeWinner =
				TEXT("Harbor City Waves");
			ExistingDecision.Outcome = TEXT("won");
			ExistingDecision.GrossReturnDue = 100;
			ExistingDecision.SelectedWinProbabilityE8 = 40000000;
			ExistingDecision.PayoutFormula =
				TEXT("floor(stake*100000000/win_probability_e8)");
		});
	RejectMutation(
		TEXT("H26N third ledger entry"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			FOddsWellOddsBucksEntry& Entry =
				State.Entries.AddDefaulted_GetRef();
			Entry.Sequence = 3;
			Entry.CommandId = TEXT("qa:h26n:foreign-ledger-entry");
			Entry.Delta = 1;
			Entry.BalanceAfter = 61;
			Entry.Reason = TEXT("foreign");
		});
	RejectMutation(
		TEXT("H26N downstream win finalization"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerWinFinalizations.AddDefaulted();
		});
	RejectMutation(
		TEXT("H26N downstream cancellation"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerCanceledGames.AddDefaulted();
		});
	RejectMutation(
		TEXT("H26N downstream void"),
		[](UOddsWellOddsBucksSaveGame& State)
		{
			State.MatchWinnerVoidDecisions.AddDefaulted();
		});

	FOddsWellMatchWinnerLossFinalizationRecord ForeignFinalization;
	TestEqual(
		TEXT("H26N valid foreign finalization fixture persists"),
		FinalizeOddsWellMatchWinnerLoss(
			TEXT("qa:h26n:foreign-finalization"),
			Decision.DecisionCommandId,
			true,
			ForeignFinalization,
			Error),
		EOddsWellMatchWinnerLossFinalizationResult::Finalized);
	TArray<uint8> ForeignFinalizationBytes;
	TestTrue(
		TEXT("H26N foreign finalization bytes read"),
		FFileHelper::LoadFileToArray(
			ForeignFinalizationBytes,
			*QaLedgerPath));
	FOddsWellMatchWinnerLossFinalizationRecord Rejected;
	TestEqual(
		TEXT("H26N foreign finalization identity rejects"),
		FinalizeCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Rejected,
			Error),
		EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestZeroMutation(
		TEXT("H26N foreign finalization rejection"),
		ForeignFinalizationBytes);
	RestoreExactState();

	TArray<uint8> BeforeWriteFailure;
	TestTrue(
		TEXT("H26N pre-write-failure bytes read"),
		FFileHelper::LoadFileToArray(
			BeforeWriteFailure,
			*QaLedgerPath));
	TestTrue(
		TEXT("H26N fixture becomes read-only"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			true));
	const EOddsWellMatchWinnerLossFinalizationResult WriteFailure =
		FinalizeCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Rejected,
			Error);
	TestTrue(
		TEXT("H26N fixture returns writable"),
		FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(
			*QaLedgerPath,
			false));
	TestEqual(
		TEXT("H26N persistence failure rejects"),
		WriteFailure,
		EOddsWellMatchWinnerLossFinalizationResult::Rejected);
	TestZeroMutation(
		TEXT("H26N persistence failure"),
		BeforeWriteFailure);

	FOddsWellMatchWinnerLossFinalizationRecord Finalization;
	TestEqual(
		TEXT("H26N exact loss finalization appends"),
		FinalizeCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Finalization,
			Error),
		EOddsWellMatchWinnerLossFinalizationResult::Finalized);
	TestEqual(
		TEXT("H26N identity derives only from H26M and H26K"),
		Finalization.FinalizationCommandId,
		TEXT("canonical:h26n:match_winner:finalization:")
			+ ResultRecordSha256);
	TestEqual(
		TEXT("H26N links exact H26M decision"),
		Finalization.DecisionCommandId,
		Decision.DecisionCommandId);
	TestEqual(
		TEXT("H26N links exact H26E request"),
		Finalization.RequestCommandId,
		Request.RequestCommandId);
	TestEqual(
		TEXT("H26N links exact H26G lock"),
		Finalization.LockCommandId,
		Lock.LockCommandId);
	TestEqual(
		TEXT("H26N links exact H26L result"),
		Finalization.ResultCommandId,
		ResultLink.ResultCommandId);
	TestEqual(
		TEXT("H26N schema is approved"),
		Finalization.FinalizationSchema,
		FString(TEXT("oddswell-match-winner-loss-finalization-v1")));
	TestEqual(
		TEXT("H26N version is approved"),
		Finalization.FinalizationVersion,
		FString(TEXT("match-winner-loss-finalization-v1")));
	TestEqual(
		TEXT("H26N selected Harbor"),
		Finalization.SelectedTeam,
		Schedule.HomeTeam);
	TestEqual(
		TEXT("H26N authoritative winner is Mesa"),
		Finalization.AuthoritativeWinner,
		Schedule.AwayTeam);
	TestEqual(TEXT("H26N stake remains 40"), Finalization.Stake, int64{40});
	TestEqual(
		TEXT("H26N outcome is lost"),
		Finalization.Outcome,
		FName(TEXT("lost")));
	TestEqual(
		TEXT("H26N applies zero gross return"),
		Finalization.GrossReturnApplied,
		int64{0});
	TestEqual(
		TEXT("H26N status is settled lost"),
		Finalization.Status,
		FName(TEXT("settled_lost")));
	TestEqual(
		TEXT("H26N observes balance 60"),
		Finalization.ObservedFinalBalance,
		int64{60});
	TestEqual(
		TEXT("H26N observes two ledger entries"),
		Finalization.ObservedLedgerEntryCount,
		2);

	FOddsWellOddsBucksLedger AfterLedger;
	int64 NextJobPayoutUnixSeconds = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> Requests;
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	TArray<FOddsWellMatchWinnerResultLinkRecord> Results;
	TArray<FOddsWellMatchWinnerSettlementDecisionRecord> Decisions;
	TArray<FOddsWellMatchWinnerLossFinalizationRecord> LossFinalizations;
	TArray<FOddsWellMatchWinnerWinFinalizationRecord> WinFinalizations;
	bool bFound = false;
	TestTrue(
		TEXT("H26N finalized state reloads"),
		LoadOddsWellOddsBucksWagerFinalizationState(
			true,
			AfterLedger,
			NextJobPayoutUnixSeconds,
			Requests,
			Locks,
			Results,
			Decisions,
			LossFinalizations,
			WinFinalizations,
			bFound,
			Error));
	TestTrue(TEXT("H26N finalized state exists"), bFound);
	TestEqual(TEXT("H26N keeps two ledger entries"), AfterLedger.GetEntries().Num(), 2);
	TestEqual(TEXT("H26N keeps credit +100"), AfterLedger.GetEntries()[0].Delta, int64{100});
	TestEqual(TEXT("H26N keeps debit -40"), AfterLedger.GetEntries()[1].Delta, int64{-40});
	TestEqual(TEXT("H26N keeps balance 60"), AfterLedger.GetBalance(), int64{60});
	TestEqual(TEXT("H26N keeps one request"), Requests.Num(), 1);
	TestEqual(TEXT("H26N keeps one lock"), Locks.Num(), 1);
	TestEqual(TEXT("H26N keeps one result"), Results.Num(), 1);
	TestEqual(TEXT("H26N keeps one decision"), Decisions.Num(), 1);
	TestEqual(TEXT("H26N appends one loss finalization"), LossFinalizations.Num(), 1);
	TestEqual(TEXT("H26N creates no win finalization"), WinFinalizations.Num(), 0);
	TestEqual(
		TEXT("H26N preserves H26M pending apply"),
		Decisions[0].Status,
		FName(TEXT("decided_pending_apply")));
	TestEqual(
		TEXT("H26N preserves H26M gross due zero"),
		Decisions[0].GrossReturnDue,
		int64{0});
	const UOddsWellOddsBucksSaveGame* FinalizedState =
		Cast<UOddsWellOddsBucksSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				TEXT("OddsWellOddsBucksQA"),
				0));
	TestTrue(
		TEXT("H26N creates no other downstream state"),
		FinalizedState
			&& FinalizedState->MatchWinnerCanceledGames.IsEmpty()
			&& FinalizedState->MatchWinnerVoidDecisions.IsEmpty()
			&& FinalizedState->MatchWinnerVoidFinalizations.IsEmpty());

	TArray<uint8> BeforeDuplicate;
	TestTrue(
		TEXT("H26N duplicate baseline bytes read"),
		FFileHelper::LoadFileToArray(
			BeforeDuplicate,
			*QaLedgerPath));
	FOddsWellMatchWinnerLossFinalizationRecord Duplicate;
	TestEqual(
		TEXT("H26N exact retry is duplicate"),
		FinalizeCanonicalMatchWinnerLoss(
			Schedule,
			Commitment,
			CanonicalRequestQaOfferSlot,
			true,
			Duplicate,
			Error),
		EOddsWellMatchWinnerLossFinalizationResult::Duplicate);
	TestEqual(
		TEXT("H26N duplicate returns immutable identity"),
		Duplicate.FinalizationCommandId,
		Finalization.FinalizationCommandId);
	TestZeroMutation(
		TEXT("H26N duplicate"),
		BeforeDuplicate);

	TestTrue(
		TEXT("H26N QA ledger cleanup succeeds"),
		ResetOddsWellQaOddsBucksAndVerify(Error));
	TestTrue(
		TEXT("H26N offer fixture cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalRequestQaOfferSlot,
			CanonicalOfferUserIndex));
	return !HasAnyErrors();
}
#endif
