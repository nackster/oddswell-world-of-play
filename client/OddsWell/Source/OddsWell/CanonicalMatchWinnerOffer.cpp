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
		|| FParse::Param(FCommandLine::Get(), TEXT("CanonicalPostLockQa"));
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
#endif
