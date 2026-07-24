#include "CanonicalMatchWinnerOffer.h"

#include "CanonicalPregameCommitment.h"
#include "CanonicalScheduledGame.h"
#include "Dom/JsonObject.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/DateTime.h"
#include "OddsBucksLedger.h"
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
#endif
