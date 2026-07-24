#include "CanonicalPregameCommitment.h"

#include "CanonicalScheduledGame.h"
#include "Kismet/GameplayStatics.h"

#if PLATFORM_WINDOWS
#include "Windows/AllowWindowsPlatformTypes.h"
#include <bcrypt.h>
#include "Windows/HideWindowsPlatformTypes.h"
#pragma comment(lib, "bcrypt.lib")
#endif

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 CanonicalPregameCommitmentVersion = 1;
constexpr int32 CanonicalPregameCommitmentUserIndex = 0;
const FString CanonicalPregameCommitmentSchema(TEXT("oddswell-canonical-pregame-commitment-v1"));
const FString CanonicalScheduledGameSchema(TEXT("oddswell-canonical-scheduled-game-v1"));
const FString PublicSnapshotVersion(TEXT("oddswell-public-pregame-v1"));
const FString PredictionVersion(TEXT("phase0d4-v1"));
const FString InputClass(TEXT("public_elo_rotation"));
const FString CommittedPregameStatus(TEXT("committed_pregame"));
const FString LocalBetaEnvironment(TEXT("local_beta"));
const FString ExpectedCommitmentSha256(TEXT("898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f"));
const FString CanonicalPregameCommitmentSlot(TEXT("OddsWellCanonicalPregameCommitment"));
const FString CanonicalScheduledGameSlot(TEXT("OddsWellCanonicalScheduledGame"));
const FString CanonicalPregameCommitmentQaSlot(TEXT("OddsWellCanonicalPregameCommitmentH26BQA"));
const FString CanonicalScheduledGameQaSlot(TEXT("OddsWellCanonicalScheduledGameH26BQA"));
// Frozen from default_teams() and public_pregame_snapshot(); no completed archive is read.
const FString FrozenCommitmentJson(TEXT(R"JSON({"predictions":{"coin":0.5,"public_elo":0.57849675,"public_elo_rotation":0.57586693},"snapshot":{"away_team":"Mesa Vista Sol","game_number":1,"home_team":"Harbor City Waves","rest_days":{"Harbor City Waves":7,"Mesa Vista Sol":7},"rosters":{"Harbor City Waves":[{"available":true,"defense":72,"name":"Jalen Cross","passing":78,"projected_minutes":43.2,"rebounding":58,"shooting":84,"stamina":86},{"available":true,"defense":75,"name":"Micah Vale","passing":86,"projected_minutes":43.2,"rebounding":55,"shooting":76,"stamina":88},{"available":true,"defense":82,"name":"Dorian Pike","passing":71,"projected_minutes":43.2,"rebounding":70,"shooting":79,"stamina":84},{"available":true,"defense":78,"name":"Kellan Shore","passing":69,"projected_minutes":43.2,"rebounding":84,"shooting":72,"stamina":80},{"available":true,"defense":80,"name":"Andre North","passing":65,"projected_minutes":43.2,"rebounding":88,"shooting":68,"stamina":78},{"available":true,"defense":74,"name":"Malik Frost","passing":72,"projected_minutes":24.0,"rebounding":63,"shooting":74,"stamina":82}],"Mesa Vista Sol":[{"available":true,"defense":70,"name":"Nico Reyes","passing":80,"projected_minutes":43.2,"rebounding":56,"shooting":82,"stamina":87},{"available":true,"defense":83,"name":"Tariq Stone","passing":75,"projected_minutes":43.2,"rebounding":68,"shooting":78,"stamina":85},{"available":true,"defense":74,"name":"Eli Mercer","passing":84,"projected_minutes":43.2,"rebounding":60,"shooting":75,"stamina":89},{"available":true,"defense":79,"name":"Roman Voss","passing":67,"projected_minutes":43.2,"rebounding":86,"shooting":73,"stamina":81},{"available":true,"defense":81,"name":"Cal Brooks","passing":64,"projected_minutes":43.2,"rebounding":89,"shooting":70,"stamina":77},{"available":true,"defense":73,"name":"Mateo Cruz","passing":73,"projected_minutes":24.0,"rebounding":65,"shooting":74,"stamina":83}]},"season_number":1,"standings":[{"games":0,"losses":0,"team":"Harbor City Waves","wins":0},{"games":0,"losses":0,"team":"Mesa Vista Sol","wins":0}],"version":"oddswell-public-pregame-v1"}})JSON"));

bool HashSha256(const FString& Value, FString& OutHash, FString& OutError)
{
	const FTCHARToUTF8 Utf8(*Value);
	uint8 Digest[32];
#if PLATFORM_WINDOWS
	BCRYPT_ALG_HANDLE Algorithm = nullptr;
	const NTSTATUS OpenStatus =
		::BCryptOpenAlgorithmProvider(&Algorithm, BCRYPT_SHA256_ALGORITHM, nullptr, 0);
	const NTSTATUS HashStatus = OpenStatus >= 0
		? ::BCryptHash(
			Algorithm,
			nullptr,
			0,
			reinterpret_cast<PUCHAR>(const_cast<ANSICHAR*>(Utf8.Get())),
			Utf8.Length(),
			Digest,
			UE_ARRAY_COUNT(Digest))
		: OpenStatus;
	if (Algorithm)
	{
		::BCryptCloseAlgorithmProvider(Algorithm, 0);
	}
	if (OpenStatus < 0 || HashStatus < 0)
	{
		OutError = TEXT("The canonical pregame commitment could not be hashed.");
		return false;
	}
	OutHash = BytesToHex(Digest, UE_ARRAY_COUNT(Digest)).ToLower();
	OutError.Reset();
	return true;
#else
	OutError = TEXT("The canonical pregame commitment hash is not implemented for this platform.");
	return false;
#endif
}

bool IsSameCanonicalPregameCommitment(
	const FOddsWellCanonicalPregameCommitmentRecord& Left,
	const FOddsWellCanonicalPregameCommitmentRecord& Right)
{
	return Left.Schema == Right.Schema
		&& Left.RecordVersion == Right.RecordVersion
		&& Left.ScheduleSchema == Right.ScheduleSchema
		&& Left.ScheduleRecordVersion == Right.ScheduleRecordVersion
		&& Left.SeasonNumber == Right.SeasonNumber
		&& Left.GameNumber == Right.GameNumber
		&& Left.HomeTeam == Right.HomeTeam
		&& Left.AwayTeam == Right.AwayTeam
		&& Left.ScheduleCreatedUnixSeconds == Right.ScheduleCreatedUnixSeconds
		&& Left.ScheduleTipoffUnixSeconds == Right.ScheduleTipoffUnixSeconds
		&& Left.SnapshotVersion == Right.SnapshotVersion
		&& Left.PredictionVersion == Right.PredictionVersion
		&& Left.InputClass == Right.InputClass
		&& Left.CommitmentJson == Right.CommitmentJson
		&& Left.CommitmentSha256 == Right.CommitmentSha256
		&& Left.Status == Right.Status
		&& Left.Environment == Right.Environment;
}

bool ValidateCanonicalPregameCommitment(
	const UObject* SaveObject,
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	FOddsWellCanonicalPregameCommitmentRecord& OutRecord,
	FString& OutError)
{
	const UOddsWellCanonicalPregameCommitmentSaveGame* Saved =
		Cast<UOddsWellCanonicalPregameCommitmentSaveGame>(SaveObject);
	if (!Saved)
	{
		OutError = TEXT("The canonical pregame commitment save is not the expected object type.");
		return false;
	}
	if (Saved->Schema != CanonicalPregameCommitmentSchema
		|| Saved->RecordVersion != CanonicalPregameCommitmentVersion
		|| Saved->ScheduleSchema != Schedule.Schema
		|| Saved->ScheduleRecordVersion != Schedule.RecordVersion
		|| Saved->SeasonNumber != Schedule.SeasonNumber
		|| Saved->GameNumber != Schedule.GameNumber
		|| Saved->HomeTeam != Schedule.HomeTeam
		|| Saved->AwayTeam != Schedule.AwayTeam
		|| Saved->ScheduleCreatedUnixSeconds != Schedule.SeasonCreatedUnixSeconds
		|| Saved->ScheduleTipoffUnixSeconds != Schedule.TipoffUnixSeconds)
	{
		OutError = TEXT("The canonical pregame commitment conflicts with the active scheduled game.");
		return false;
	}
	if (Saved->SnapshotVersion != PublicSnapshotVersion
		|| Saved->PredictionVersion != PredictionVersion
		|| Saved->InputClass != InputClass
		|| Saved->CommitmentJson != FrozenCommitmentJson
		|| Saved->CommitmentSha256 != ExpectedCommitmentSha256
		|| Saved->Status != CommittedPregameStatus
		|| Saved->Environment != LocalBetaEnvironment)
	{
		OutError = TEXT("The canonical pregame commitment is not the approved equal-public input.");
		return false;
	}
	FString ComputedHash;
	if (!HashSha256(Saved->CommitmentJson, ComputedHash, OutError)
		|| ComputedHash != Saved->CommitmentSha256)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The canonical pregame commitment hash does not verify.");
		}
		return false;
	}
	OutRecord = {
		Saved->Schema,
		Saved->RecordVersion,
		Saved->ScheduleSchema,
		Saved->ScheduleRecordVersion,
		Saved->SeasonNumber,
		Saved->GameNumber,
		Saved->HomeTeam,
		Saved->AwayTeam,
		Saved->ScheduleCreatedUnixSeconds,
		Saved->ScheduleTipoffUnixSeconds,
		Saved->SnapshotVersion,
		Saved->PredictionVersion,
		Saved->InputClass,
		Saved->CommitmentJson,
		Saved->CommitmentSha256,
		Saved->Status,
		Saved->Environment};
	OutError.Reset();
	return true;
}

bool LoadScheduledGame(
	const FString& Slot,
	FOddsWellCanonicalScheduledGameRecord& OutSchedule,
	FString& OutError)
{
	if (!UGameplayStatics::DoesSaveGameExist(Slot, CanonicalPregameCommitmentUserIndex))
	{
		OutError = TEXT("The canonical scheduled-game prerequisite does not exist.");
		return false;
	}
	return ValidateOddsWellCanonicalScheduledGameSave(
		UGameplayStatics::LoadGameFromSlot(Slot, CanonicalPregameCommitmentUserIndex),
		OutSchedule,
		OutError);
}

EOddsWellCanonicalPregameCommitmentResult PersistCanonicalPregameCommitment(
	const FString& ScheduleSlot,
	const FString& CommitmentSlot,
	FOddsWellCanonicalPregameCommitmentRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	if (!LoadScheduledGame(ScheduleSlot, Schedule, OutError))
	{
		return EOddsWellCanonicalPregameCommitmentResult::Rejected;
	}
	if (UGameplayStatics::DoesSaveGameExist(
		CommitmentSlot,
		CanonicalPregameCommitmentUserIndex))
	{
		return ValidateCanonicalPregameCommitment(
			UGameplayStatics::LoadGameFromSlot(
				CommitmentSlot,
				CanonicalPregameCommitmentUserIndex),
			Schedule,
			OutRecord,
			OutError)
			? EOddsWellCanonicalPregameCommitmentResult::Duplicate
			: EOddsWellCanonicalPregameCommitmentResult::Rejected;
	}
	UOddsWellCanonicalPregameCommitmentSaveGame* Saved =
		Cast<UOddsWellCanonicalPregameCommitmentSaveGame>(
			UGameplayStatics::CreateSaveGameObject(
				UOddsWellCanonicalPregameCommitmentSaveGame::StaticClass()));
	if (!Saved)
	{
		OutError = TEXT("The canonical pregame commitment save object could not be created.");
		return EOddsWellCanonicalPregameCommitmentResult::Rejected;
	}
	Saved->Schema = CanonicalPregameCommitmentSchema;
	Saved->RecordVersion = CanonicalPregameCommitmentVersion;
	Saved->ScheduleSchema = Schedule.Schema;
	Saved->ScheduleRecordVersion = Schedule.RecordVersion;
	Saved->SeasonNumber = Schedule.SeasonNumber;
	Saved->GameNumber = Schedule.GameNumber;
	Saved->HomeTeam = Schedule.HomeTeam;
	Saved->AwayTeam = Schedule.AwayTeam;
	Saved->ScheduleCreatedUnixSeconds = Schedule.SeasonCreatedUnixSeconds;
	Saved->ScheduleTipoffUnixSeconds = Schedule.TipoffUnixSeconds;
	Saved->SnapshotVersion = PublicSnapshotVersion;
	Saved->PredictionVersion = PredictionVersion;
	Saved->InputClass = InputClass;
	Saved->CommitmentJson = FrozenCommitmentJson;
	Saved->CommitmentSha256 = ExpectedCommitmentSha256;
	Saved->Status = CommittedPregameStatus;
	Saved->Environment = LocalBetaEnvironment;
	if (!ValidateCanonicalPregameCommitment(Saved, Schedule, OutRecord, OutError))
	{
		return EOddsWellCanonicalPregameCommitmentResult::Rejected;
	}
	if (!UGameplayStatics::SaveGameToSlot(
		Saved,
		CommitmentSlot,
		CanonicalPregameCommitmentUserIndex))
	{
		OutError = TEXT("Native SaveGameToSlot failed for the canonical pregame commitment.");
		return EOddsWellCanonicalPregameCommitmentResult::Rejected;
	}
	OutError.Reset();
	return EOddsWellCanonicalPregameCommitmentResult::Created;
}
}

EOddsWellCanonicalPregameCommitmentResult CreateOddsWellCanonicalPregameCommitment(
	FOddsWellCanonicalPregameCommitmentRecord& OutRecord,
	FString& OutError)
{
	return PersistCanonicalPregameCommitment(
		CanonicalScheduledGameSlot,
		CanonicalPregameCommitmentSlot,
		OutRecord,
		OutError);
}

bool LoadOddsWellCanonicalPregameCommitment(
	FOddsWellCanonicalPregameCommitmentRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	if (!LoadScheduledGame(CanonicalScheduledGameSlot, Schedule, OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			CanonicalPregameCommitmentSlot,
			CanonicalPregameCommitmentUserIndex))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("No canonical pregame commitment save exists.");
		}
		return false;
	}
	return ValidateCanonicalPregameCommitment(
		UGameplayStatics::LoadGameFromSlot(
			CanonicalPregameCommitmentSlot,
			CanonicalPregameCommitmentUserIndex),
		Schedule,
		OutRecord,
		OutError);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalPregameCommitmentPersistenceTest,
	"OddsWell.League.CanonicalPregameCommitment",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalPregameCommitmentPersistenceTest::RunTest(const FString& Parameters)
{
	UGameplayStatics::DeleteGameInSlot(
		CanonicalPregameCommitmentQaSlot,
		CanonicalPregameCommitmentUserIndex);
	UGameplayStatics::DeleteGameInSlot(
		CanonicalScheduledGameQaSlot,
		CanonicalPregameCommitmentUserIndex);

	UOddsWellCanonicalScheduledGameSaveGame* Schedule =
		NewObject<UOddsWellCanonicalScheduledGameSaveGame>();
	Schedule->Schema = CanonicalScheduledGameSchema;
	Schedule->RecordVersion = 1;
	Schedule->SeasonNumber = 1;
	Schedule->GameNumber = 1;
	Schedule->HomeTeam = TEXT("Harbor City Waves");
	Schedule->AwayTeam = TEXT("Mesa Vista Sol");
	Schedule->SeasonCreatedUnixSeconds = 2200000000;
	Schedule->TipoffUnixSeconds = 2200001800;
	Schedule->OfferEligibleUnixSeconds = 2200000000;
	Schedule->Status = TEXT("scheduled_unplayed");
	Schedule->Environment = LocalBetaEnvironment;
	Schedule->TimingAuthority = TEXT("server");
	Schedule->bProductionTiming = false;
	Schedule->bOfferPublished = false;
	TestTrue(
		TEXT("Exact H26A prerequisite saves"),
		UGameplayStatics::SaveGameToSlot(
			Schedule,
			CanonicalScheduledGameQaSlot,
			CanonicalPregameCommitmentUserIndex));
	TArray<uint8> ScheduleBytesBefore;
	TestTrue(
		TEXT("H26A prerequisite serializes before commitment"),
		UGameplayStatics::SaveGameToMemory(Schedule, ScheduleBytesBefore));

	FOddsWellCanonicalPregameCommitmentRecord Created;
	FString Error;
	TestEqual(
		TEXT("Equal-public commitment creates"),
		PersistCanonicalPregameCommitment(
			CanonicalScheduledGameQaSlot,
			CanonicalPregameCommitmentQaSlot,
			Created,
			Error),
		EOddsWellCanonicalPregameCommitmentResult::Created);
	TestEqual(TEXT("Snapshot version is exact"), Created.SnapshotVersion, PublicSnapshotVersion);
	TestEqual(TEXT("Prediction version is exact"), Created.PredictionVersion, PredictionVersion);
	TestEqual(TEXT("Input class is exact"), Created.InputClass, InputClass);
	TestEqual(TEXT("Commitment hash is deterministic"), Created.CommitmentSha256, ExpectedCommitmentSha256);
	TestEqual(TEXT("Frozen commitment is canonical"), Created.CommitmentJson, FrozenCommitmentJson);
	TestEqual(TEXT("Commitment links H26A creation"), Created.ScheduleCreatedUnixSeconds, int64{2200000000});
	TestEqual(TEXT("Commitment links H26A tipoff"), Created.ScheduleTipoffUnixSeconds, int64{2200001800});
	TestEqual(TEXT("Commitment status is immutable pregame"), Created.Status, CommittedPregameStatus);
	for (const FString Forbidden : {
		TEXT("\"seed\""),
		TEXT("\"rng\""),
		TEXT("\"fatigue\""),
		TEXT("\"score\""),
		TEXT("\"winner\""),
		TEXT("\"replay\""),
		TEXT("\"result\""),
		TEXT("\"offer\""),
		TEXT("\"odds\""),
		TEXT("\"economy\""),
		TEXT("\"user\"")})
	{
		TestFalse(
			FString::Printf(TEXT("Commitment excludes %s"), *Forbidden),
			Created.CommitmentJson.Contains(Forbidden));
	}

	UOddsWellCanonicalScheduledGameSaveGame* ScheduleAfter =
		Cast<UOddsWellCanonicalScheduledGameSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalScheduledGameQaSlot,
				CanonicalPregameCommitmentUserIndex));
	TArray<uint8> ScheduleBytesAfter;
	TestTrue(
		TEXT("H26A prerequisite reloads after commitment"),
		ScheduleAfter
			&& UGameplayStatics::SaveGameToMemory(
				ScheduleAfter,
				ScheduleBytesAfter));
	TestTrue(
		TEXT("H26A prerequisite remains byte-for-byte"),
		ScheduleBytesBefore == ScheduleBytesAfter);

	FOddsWellCanonicalPregameCommitmentRecord Duplicate;
	TestEqual(
		TEXT("Cold exact retry is duplicate-safe"),
		PersistCanonicalPregameCommitment(
			CanonicalScheduledGameQaSlot,
			CanonicalPregameCommitmentQaSlot,
			Duplicate,
			Error),
		EOddsWellCanonicalPregameCommitmentResult::Duplicate);
	TestTrue(
		TEXT("Cold retry restores every field"),
		IsSameCanonicalPregameCommitment(Created, Duplicate));

	UOddsWellCanonicalPregameCommitmentSaveGame* Tampered =
		Cast<UOddsWellCanonicalPregameCommitmentSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalPregameCommitmentQaSlot,
				CanonicalPregameCommitmentUserIndex));
	TestNotNull(TEXT("Commitment reloads for rejection proof"), Tampered);
	if (Tampered)
	{
		Tampered->CommitmentSha256 =
			TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
		TestTrue(
			TEXT("Tampered commitment saves for rejection proof"),
			UGameplayStatics::SaveGameToSlot(
				Tampered,
				CanonicalPregameCommitmentQaSlot,
				CanonicalPregameCommitmentUserIndex));
		TestEqual(
			TEXT("Tampered commitment fails closed"),
			PersistCanonicalPregameCommitment(
				CanonicalScheduledGameQaSlot,
				CanonicalPregameCommitmentQaSlot,
				Duplicate,
				Error),
			EOddsWellCanonicalPregameCommitmentResult::Rejected);
		const UOddsWellCanonicalPregameCommitmentSaveGame* Unchanged =
			Cast<UOddsWellCanonicalPregameCommitmentSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					CanonicalPregameCommitmentQaSlot,
					CanonicalPregameCommitmentUserIndex));
		TestTrue(
			TEXT("Rejected tamper is not rewritten"),
			Unchanged
				&& Unchanged->CommitmentSha256
					== TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"));
	}

	TestTrue(
		TEXT("Commitment QA cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalPregameCommitmentQaSlot,
			CanonicalPregameCommitmentUserIndex));
	TestTrue(
		TEXT("Schedule QA cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalScheduledGameQaSlot,
			CanonicalPregameCommitmentUserIndex));
	TestFalse(
		TEXT("Native test leaves no commitment QA save behind"),
		UGameplayStatics::DoesSaveGameExist(
			CanonicalPregameCommitmentQaSlot,
			CanonicalPregameCommitmentUserIndex));
	TestFalse(
		TEXT("Native test leaves no schedule QA save behind"),
		UGameplayStatics::DoesSaveGameExist(
			CanonicalScheduledGameQaSlot,
			CanonicalPregameCommitmentUserIndex));
	return !HasAnyErrors();
}
#endif
