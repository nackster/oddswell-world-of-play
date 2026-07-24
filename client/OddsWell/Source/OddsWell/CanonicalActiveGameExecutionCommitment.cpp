#include "CanonicalActiveGameExecutionCommitment.h"

#include "CanonicalMatchWinnerOffer.h"
#include "CanonicalPregameCommitment.h"
#include "CanonicalScheduledGame.h"
#include "Kismet/GameplayStatics.h"
#include "OddsBucksLedger.h"

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
constexpr int32 ExecutionCommitmentVersion = 1;
constexpr int32 ExecutionCommitmentUserIndex = 0;
const FString ExecutionCommitmentSchema(
	TEXT("oddswell-canonical-active-game-execution-commitment-v1"));
const FString ExecutionSeedVersion(
	TEXT("oddswell-canonical-active-game-seed-v1"));
const FString ExpectedPregameCommitmentSha256(
	TEXT("898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f"));
const FString CommittedForExecutionStatus(TEXT("committed_for_execution"));
const FString LocalBetaEnvironment(TEXT("local_beta"));
const FString ExecutionCommitmentSlot(
	TEXT("OddsWellCanonicalActiveGameExecutionCommitment"));
const FString ExecutionCommitmentQaSlot(
	TEXT("OddsWellCanonicalActiveGameExecutionCommitmentH26HQA"));

bool HashSha256(
	const FString& Value,
	FString& OutHash,
	FString& OutError,
	uint32* OutFirstWord = nullptr)
{
	const FTCHARToUTF8 Utf8(*Value);
	uint8 Digest[32];
#if PLATFORM_WINDOWS
	BCRYPT_ALG_HANDLE Algorithm = nullptr;
	const NTSTATUS OpenStatus =
		::BCryptOpenAlgorithmProvider(
			&Algorithm,
			BCRYPT_SHA256_ALGORITHM,
			nullptr,
			0);
	const NTSTATUS HashStatus = OpenStatus >= 0
		? ::BCryptHash(
			Algorithm,
			nullptr,
			0,
			reinterpret_cast<PUCHAR>(
				const_cast<ANSICHAR*>(Utf8.Get())),
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
		OutError = TEXT("The canonical execution commitment could not be hashed.");
		return false;
	}
	OutHash = BytesToHex(Digest, UE_ARRAY_COUNT(Digest)).ToLower();
	if (OutFirstWord)
	{
		*OutFirstWord =
			(static_cast<uint32>(Digest[0]) << 24)
			| (static_cast<uint32>(Digest[1]) << 16)
			| (static_cast<uint32>(Digest[2]) << 8)
			| static_cast<uint32>(Digest[3]);
	}
	OutError.Reset();
	return true;
#else
	OutError = TEXT("The canonical execution commitment hash is not implemented for this platform.");
	return false;
#endif
}

bool HasExactH26AB(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment)
{
	return Schedule.Schema == TEXT("oddswell-canonical-scheduled-game-v1")
		&& Schedule.RecordVersion == 1
		&& Schedule.SeasonNumber == 1
		&& Schedule.GameNumber == 1
		&& Schedule.HomeTeam == TEXT("Harbor City Waves")
		&& Schedule.AwayTeam == TEXT("Mesa Vista Sol")
		&& Schedule.SeasonCreatedUnixSeconds > 0
		&& Schedule.SeasonCreatedUnixSeconds
			<= TNumericLimits<int64>::Max() - 1800
		&& Schedule.TipoffUnixSeconds
			== Schedule.SeasonCreatedUnixSeconds + 1800
		&& Schedule.OfferEligibleUnixSeconds
			== Schedule.SeasonCreatedUnixSeconds
		&& Schedule.Status == TEXT("scheduled_unplayed")
		&& Schedule.Environment == LocalBetaEnvironment
		&& Schedule.TimingAuthority == TEXT("server")
		&& !Schedule.bProductionTiming
		&& !Schedule.bOfferPublished
		&& Commitment.Schema
			== TEXT("oddswell-canonical-pregame-commitment-v1")
		&& Commitment.RecordVersion == 1
		&& Commitment.ScheduleSchema == Schedule.Schema
		&& Commitment.ScheduleRecordVersion == Schedule.RecordVersion
		&& Commitment.SeasonNumber == Schedule.SeasonNumber
		&& Commitment.GameNumber == Schedule.GameNumber
		&& Commitment.HomeTeam == Schedule.HomeTeam
		&& Commitment.AwayTeam == Schedule.AwayTeam
		&& Commitment.ScheduleCreatedUnixSeconds
			== Schedule.SeasonCreatedUnixSeconds
		&& Commitment.ScheduleTipoffUnixSeconds
			== Schedule.TipoffUnixSeconds
		&& Commitment.SnapshotVersion
			== TEXT("oddswell-public-pregame-v1")
		&& Commitment.PredictionVersion == TEXT("phase0d4-v1")
		&& Commitment.InputClass == TEXT("public_elo_rotation")
		&& Commitment.CommitmentSha256
			== ExpectedPregameCommitmentSha256
		&& Commitment.Status == TEXT("committed_pregame")
		&& Commitment.Environment == LocalBetaEnvironment;
}

bool HasExactH26CG(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& Commitment,
	const FOddsWellCanonicalMatchWinnerOfferRecord& Offer,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const bool bCurrentWagerSchema,
	const bool bHasDownstreamEvidence,
	FString& OutError)
{
	if (!bCurrentWagerSchema
		|| bHasDownstreamEvidence
		|| !ValidateOddsWellCanonicalMatchWinnerOfferEvidence(
			Schedule,
			Commitment,
			Offer,
			OutError)
		|| Locks.Num() != 1)
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The execution commitment requires exact current H26C/H26G evidence.");
		}
		return false;
	}
	const FOddsWellMatchWinnerLockRecord& Lock = Locks[0];
	const FString RequestId =
		TEXT("canonical:h26e:match_winner:request:") + Offer.OfferId;
	return Lock.LockCommandId
			== TEXT("canonical:h26g:match_winner:lock:") + Offer.OfferId
		&& Lock.RequestCommandId == RequestId
		&& Lock.SeasonNumber == Schedule.SeasonNumber
		&& Lock.GameNumber == Schedule.GameNumber
		&& Lock.AuthoritativeGameStartUnixSeconds
			== Schedule.TipoffUnixSeconds
		&& Lock.LockUnixSeconds == Schedule.TipoffUnixSeconds
		&& Lock.Decision == FName(TEXT("locked"));
}

FString BuildExecutionInputJson(const int64 ExecutionSeed)
{
	return FString::Printf(
		TEXT(R"JSON({"brain_version":"baseline-v2","consistency_snapshot":[{"athlete":"Jalen Cross","cap":0.06,"strength":0.3,"tier":"steady"},{"athlete":"Micah Vale","cap":0.03,"strength":0.15,"tier":"normal"},{"athlete":"Dorian Pike","cap":0.06,"strength":0.3,"tier":"steady"},{"athlete":"Kellan Shore","cap":0.03,"strength":0.15,"tier":"normal"},{"athlete":"Andre North","cap":0.03,"strength":0.15,"tier":"normal"},{"athlete":"Malik Frost","cap":0.0,"strength":0.0,"tier":"volatile"},{"athlete":"Nico Reyes","cap":0.06,"strength":0.3,"tier":"steady"},{"athlete":"Tariq Stone","cap":0.1,"strength":0.5,"tier":"elite"},{"athlete":"Eli Mercer","cap":0.03,"strength":0.15,"tier":"normal"},{"athlete":"Roman Voss","cap":0.06,"strength":0.3,"tier":"steady"},{"athlete":"Cal Brooks","cap":0.03,"strength":0.15,"tier":"normal"},{"athlete":"Mateo Cruz","cap":0.0,"strength":0.0,"tier":"volatile"}],"consistency_version":"athlete-consistency-v2","engine_version":"phase05h-v1","fatigue_model_version":"minutes-workload-v1","injury_model_version":"minor-availability-v1","league_version":"phase06l-v1","life_decisions":[],"life_policy_version":"athlete-life-v4","matchup":[{"roster":[{"defense":72,"name":"Jalen Cross","passing":78,"rebounding":58,"shooting":84,"stamina":86},{"defense":75,"name":"Micah Vale","passing":86,"rebounding":55,"shooting":76,"stamina":88},{"defense":82,"name":"Dorian Pike","passing":71,"rebounding":70,"shooting":79,"stamina":84},{"defense":78,"name":"Kellan Shore","passing":69,"rebounding":84,"shooting":72,"stamina":80},{"defense":80,"name":"Andre North","passing":65,"rebounding":88,"shooting":68,"stamina":78},{"defense":74,"name":"Malik Frost","passing":72,"rebounding":63,"shooting":74,"stamina":82}],"side":"home","team":"Harbor City Waves"},{"roster":[{"defense":70,"name":"Nico Reyes","passing":80,"rebounding":56,"shooting":82,"stamina":87},{"defense":83,"name":"Tariq Stone","passing":75,"rebounding":68,"shooting":78,"stamina":85},{"defense":74,"name":"Eli Mercer","passing":84,"rebounding":60,"shooting":75,"stamina":89},{"defense":79,"name":"Roman Voss","passing":67,"rebounding":86,"shooting":73,"stamina":81},{"defense":81,"name":"Cal Brooks","passing":64,"rebounding":89,"shooting":70,"stamina":77},{"defense":73,"name":"Mateo Cruz","passing":73,"rebounding":65,"shooting":74,"stamina":83}],"side":"away","team":"Mesa Vista Sol"}],"offensive_involvement_snapshot":[{"athlete":"Jalen Cross","tier":"featured","weight":1.15},{"athlete":"Micah Vale","tier":"featured","weight":1.15},{"athlete":"Dorian Pike","tier":"standard","weight":1.0},{"athlete":"Kellan Shore","tier":"low","weight":0.85},{"athlete":"Andre North","tier":"low","weight":0.85},{"athlete":"Malik Frost","tier":"standard","weight":1.0},{"athlete":"Nico Reyes","tier":"featured","weight":1.15},{"athlete":"Tariq Stone","tier":"standard","weight":1.0},{"athlete":"Eli Mercer","tier":"featured","weight":1.15},{"athlete":"Roman Voss","tier":"low","weight":0.85},{"athlete":"Cal Brooks","tier":"low","weight":0.85},{"athlete":"Mateo Cruz","tier":"standard","weight":1.0}],"offensive_involvement_version":"offensive-involvement-v1","opening_availability":[{"athlete":"Jalen Cross","recovery_days":0},{"athlete":"Micah Vale","recovery_days":0},{"athlete":"Dorian Pike","recovery_days":0},{"athlete":"Kellan Shore","recovery_days":0},{"athlete":"Andre North","recovery_days":0},{"athlete":"Malik Frost","recovery_days":0},{"athlete":"Nico Reyes","recovery_days":0},{"athlete":"Tariq Stone","recovery_days":0},{"athlete":"Eli Mercer","recovery_days":0},{"athlete":"Roman Voss","recovery_days":0},{"athlete":"Cal Brooks","recovery_days":0},{"athlete":"Mateo Cruz","recovery_days":0}],"opening_fatigue":[{"athlete":"Jalen Cross","value":0.0},{"athlete":"Micah Vale","value":0.0},{"athlete":"Dorian Pike","value":0.0},{"athlete":"Kellan Shore","value":0.0},{"athlete":"Andre North","value":0.0},{"athlete":"Malik Frost","value":0.0},{"athlete":"Nico Reyes","value":0.0},{"athlete":"Tariq Stone","value":0.0},{"athlete":"Eli Mercer","value":0.0},{"athlete":"Roman Voss","value":0.0},{"athlete":"Cal Brooks","value":0.0},{"athlete":"Mateo Cruz","value":0.0}],"opening_readiness":[{"athlete":"Jalen Cross","value":0.0},{"athlete":"Micah Vale","value":0.0},{"athlete":"Dorian Pike","value":0.0},{"athlete":"Kellan Shore","value":0.0},{"athlete":"Andre North","value":0.0},{"athlete":"Malik Frost","value":0.0},{"athlete":"Nico Reyes","value":0.0},{"athlete":"Tariq Stone","value":0.0},{"athlete":"Eli Mercer","value":0.0},{"athlete":"Roman Voss","value":0.0},{"athlete":"Cal Brooks","value":0.0},{"athlete":"Mateo Cruz","value":0.0}],"player_points_capture":false,"schedule":{"away_team":"Mesa Vista Sol","game_number":1,"home_team":"Harbor City Waves","seed":%lld},"simulation_function":"simulate_scheduled_game"})JSON"),
		ExecutionSeed);
}

bool BuildExpectedCommitment(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& PregameCommitment,
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
	FString& OutError)
{
	if (!HasExactH26AB(Schedule, PregameCommitment))
	{
		OutError = TEXT("The execution commitment requires exact immutable H26A/H26B evidence.");
		return false;
	}
	const FString SeedMaterialJson = FString::Printf(
		TEXT("{\"away_team\":\"Mesa Vista Sol\",\"domain\":\"oddswell-canonical-active-game-seed-v1\",\"environment\":\"local_beta\",\"game_number\":1,\"home_team\":\"Harbor City Waves\",\"offer_eligible_unix\":%lld,\"offer_published\":false,\"pregame_commitment_sha256\":\"%s\",\"production_timing\":false,\"schedule_created_unix\":%lld,\"schedule_record_version\":1,\"schedule_schema\":\"oddswell-canonical-scheduled-game-v1\",\"schedule_status\":\"scheduled_unplayed\",\"schedule_tipoff_unix\":%lld,\"season_number\":1,\"timing_authority\":\"server\"}"),
		Schedule.OfferEligibleUnixSeconds,
		*PregameCommitment.CommitmentSha256,
		Schedule.SeasonCreatedUnixSeconds,
		Schedule.TipoffUnixSeconds);
	FString SeedMaterialSha256;
	uint32 SeedWord = 0;
	if (!HashSha256(
			SeedMaterialJson,
			SeedMaterialSha256,
			OutError,
			&SeedWord))
	{
		return false;
	}
	const int64 ExecutionSeed =
		static_cast<int64>(SeedWord & 0x7fffffffU);
	const FString ExecutionInputJson =
		BuildExecutionInputJson(ExecutionSeed);
	FString ExecutionInputSha256;
	if (!HashSha256(
			ExecutionInputJson,
			ExecutionInputSha256,
			OutError))
	{
		return false;
	}
	const FString CommitmentJson = FString::Printf(
		TEXT("{\"away_team\":\"Mesa Vista Sol\",\"environment\":\"local_beta\",\"execution_input_sha256\":\"%s\",\"execution_seed\":%lld,\"game_number\":1,\"home_team\":\"Harbor City Waves\",\"offer_eligible_unix\":%lld,\"pregame_commitment_sha256\":\"%s\",\"record_version\":1,\"schedule_created_unix\":%lld,\"schedule_record_version\":1,\"schedule_schema\":\"oddswell-canonical-scheduled-game-v1\",\"schedule_tipoff_unix\":%lld,\"schema\":\"oddswell-canonical-active-game-execution-commitment-v1\",\"season_number\":1,\"seed_derivation_version\":\"oddswell-canonical-active-game-seed-v1\",\"seed_material_sha256\":\"%s\",\"status\":\"committed_for_execution\"}"),
		*ExecutionInputSha256,
		ExecutionSeed,
		Schedule.OfferEligibleUnixSeconds,
		*PregameCommitment.CommitmentSha256,
		Schedule.SeasonCreatedUnixSeconds,
		Schedule.TipoffUnixSeconds,
		*SeedMaterialSha256);
	FString CommitmentSha256;
	if (!HashSha256(
			CommitmentJson,
			CommitmentSha256,
			OutError))
	{
		return false;
	}
	static const TCHAR* Forbidden[] = {
		TEXT("\"offer_id\""),
		TEXT("\"request\""),
		TEXT("\"selection\""),
		TEXT("\"stake\""),
		TEXT("\"balance\""),
		TEXT("\"ledger\""),
		TEXT("\"lock_command\""),
		TEXT("\"accepted_unix\"")};
	for (const TCHAR* Field : Forbidden)
	{
		if (SeedMaterialJson.Contains(Field)
			|| ExecutionInputJson.Contains(Field))
		{
			OutError = TEXT("The private execution commitment contains wager or economy input.");
			return false;
		}
	}
	OutRecord = {
		ExecutionCommitmentSchema,
		ExecutionCommitmentVersion,
		Schedule.Schema,
		Schedule.RecordVersion,
		Schedule.SeasonNumber,
		Schedule.GameNumber,
		Schedule.HomeTeam,
		Schedule.AwayTeam,
		Schedule.SeasonCreatedUnixSeconds,
		Schedule.TipoffUnixSeconds,
		Schedule.OfferEligibleUnixSeconds,
		PregameCommitment.CommitmentSha256,
		ExecutionSeedVersion,
		SeedMaterialJson,
		SeedMaterialSha256,
		ExecutionSeed,
		ExecutionInputJson,
		ExecutionInputSha256,
		CommitmentJson,
		CommitmentSha256,
		CommittedForExecutionStatus,
		LocalBetaEnvironment};
	OutError.Reset();
	return true;
}

bool IsSameCommitment(
	const FOddsWellCanonicalActiveGameExecutionCommitmentRecord& Left,
	const FOddsWellCanonicalActiveGameExecutionCommitmentRecord& Right)
{
	return Left.Schema == Right.Schema
		&& Left.RecordVersion == Right.RecordVersion
		&& Left.ScheduleSchema == Right.ScheduleSchema
		&& Left.ScheduleRecordVersion == Right.ScheduleRecordVersion
		&& Left.SeasonNumber == Right.SeasonNumber
		&& Left.GameNumber == Right.GameNumber
		&& Left.HomeTeam == Right.HomeTeam
		&& Left.AwayTeam == Right.AwayTeam
		&& Left.ScheduleCreatedUnixSeconds
			== Right.ScheduleCreatedUnixSeconds
		&& Left.ScheduleTipoffUnixSeconds
			== Right.ScheduleTipoffUnixSeconds
		&& Left.OfferEligibleUnixSeconds
			== Right.OfferEligibleUnixSeconds
		&& Left.PregameCommitmentSha256
			== Right.PregameCommitmentSha256
		&& Left.SeedDerivationVersion == Right.SeedDerivationVersion
		&& Left.SeedMaterialJson == Right.SeedMaterialJson
		&& Left.SeedMaterialSha256 == Right.SeedMaterialSha256
		&& Left.ExecutionSeed == Right.ExecutionSeed
		&& Left.ExecutionInputJson == Right.ExecutionInputJson
		&& Left.ExecutionInputSha256 == Right.ExecutionInputSha256
		&& Left.CommitmentJson == Right.CommitmentJson
		&& Left.CommitmentSha256 == Right.CommitmentSha256
		&& Left.Status == Right.Status
		&& Left.Environment == Right.Environment;
}

bool RestoreCommitment(
	const UObject* SaveObject,
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& PregameCommitment,
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
	FString& OutError)
{
	const UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame* Saved =
		Cast<UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame>(
			SaveObject);
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Expected;
	if (!Saved
		|| !BuildExpectedCommitment(
			Schedule,
			PregameCommitment,
			Expected,
			OutError))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The execution commitment save is not the expected object type.");
		}
		return false;
	}
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Persisted = {
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
		Saved->OfferEligibleUnixSeconds,
		Saved->PregameCommitmentSha256,
		Saved->SeedDerivationVersion,
		Saved->SeedMaterialJson,
		Saved->SeedMaterialSha256,
		Saved->ExecutionSeed,
		Saved->ExecutionInputJson,
		Saved->ExecutionInputSha256,
		Saved->CommitmentJson,
		Saved->CommitmentSha256,
		Saved->Status,
		Saved->Environment};
	if (!IsSameCommitment(Persisted, Expected))
	{
		OutError = TEXT("The persisted execution commitment conflicts with its exact canonical derivation.");
		return false;
	}
	OutRecord = MoveTemp(Persisted);
	OutError.Reset();
	return true;
}

EOddsWellCanonicalActiveGameExecutionCommitmentResult PersistCommitment(
	const FOddsWellCanonicalScheduledGameRecord& Schedule,
	const FOddsWellCanonicalPregameCommitmentRecord& PregameCommitment,
	const FOddsWellCanonicalMatchWinnerOfferRecord& Offer,
	const TArray<FOddsWellMatchWinnerLockRecord>& Locks,
	const bool bCurrentWagerSchema,
	const bool bHasDownstreamEvidence,
	const FString& Slot,
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
	FString& OutError)
{
	if (!HasExactH26AB(Schedule, PregameCommitment)
		|| !HasExactH26CG(
			Schedule,
			PregameCommitment,
			Offer,
			Locks,
			bCurrentWagerSchema,
			bHasDownstreamEvidence,
			OutError))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The execution commitment prerequisite chain is not exact.");
		}
		return EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
	}
	if (UGameplayStatics::DoesSaveGameExist(
		Slot,
		ExecutionCommitmentUserIndex))
	{
		return RestoreCommitment(
			UGameplayStatics::LoadGameFromSlot(
				Slot,
				ExecutionCommitmentUserIndex),
			Schedule,
			PregameCommitment,
			OutRecord,
			OutError)
			? EOddsWellCanonicalActiveGameExecutionCommitmentResult::Duplicate
			: EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
	}
	if (!BuildExpectedCommitment(
		Schedule,
		PregameCommitment,
		OutRecord,
		OutError))
	{
		return EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
	}
	UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame* Saved =
		Cast<UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame>(
			UGameplayStatics::CreateSaveGameObject(
				UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame::StaticClass()));
	if (!Saved)
	{
		OutError = TEXT("The execution commitment save object could not be created.");
		return EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
	}
	Saved->Schema = OutRecord.Schema;
	Saved->RecordVersion = OutRecord.RecordVersion;
	Saved->ScheduleSchema = OutRecord.ScheduleSchema;
	Saved->ScheduleRecordVersion = OutRecord.ScheduleRecordVersion;
	Saved->SeasonNumber = OutRecord.SeasonNumber;
	Saved->GameNumber = OutRecord.GameNumber;
	Saved->HomeTeam = OutRecord.HomeTeam;
	Saved->AwayTeam = OutRecord.AwayTeam;
	Saved->ScheduleCreatedUnixSeconds =
		OutRecord.ScheduleCreatedUnixSeconds;
	Saved->ScheduleTipoffUnixSeconds =
		OutRecord.ScheduleTipoffUnixSeconds;
	Saved->OfferEligibleUnixSeconds =
		OutRecord.OfferEligibleUnixSeconds;
	Saved->PregameCommitmentSha256 =
		OutRecord.PregameCommitmentSha256;
	Saved->SeedDerivationVersion = OutRecord.SeedDerivationVersion;
	Saved->SeedMaterialJson = OutRecord.SeedMaterialJson;
	Saved->SeedMaterialSha256 = OutRecord.SeedMaterialSha256;
	Saved->ExecutionSeed = OutRecord.ExecutionSeed;
	Saved->ExecutionInputJson = OutRecord.ExecutionInputJson;
	Saved->ExecutionInputSha256 = OutRecord.ExecutionInputSha256;
	Saved->CommitmentJson = OutRecord.CommitmentJson;
	Saved->CommitmentSha256 = OutRecord.CommitmentSha256;
	Saved->Status = OutRecord.Status;
	Saved->Environment = OutRecord.Environment;
	if (!UGameplayStatics::SaveGameToSlot(
		Saved,
		Slot,
		ExecutionCommitmentUserIndex))
	{
		OutError = TEXT("Native SaveGameToSlot failed for the execution commitment.");
		return EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
	}
	OutError.Reset();
	return EOddsWellCanonicalActiveGameExecutionCommitmentResult::Created;
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

FOddsWellCanonicalPregameCommitmentRecord TestPregameCommitment()
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
		ExpectedPregameCommitmentSha256,
		TEXT("committed_pregame"),
		TEXT("local_beta")};
}
}

EOddsWellCanonicalActiveGameExecutionCommitmentResult
CreateOddsWellCanonicalActiveGameExecutionCommitment(
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord PregameCommitment;
	FOddsWellCanonicalMatchWinnerOfferRecord Offer;
	FOddsWellMatchWinnerLockRecord Lock;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(
			PregameCommitment,
			OutError)
		|| !LoadOddsWellCanonicalMatchWinnerOffer(Offer, OutError)
		|| !LoadOddsWellCanonicalMatchWinnerLock(Lock, OutError))
	{
		OutRecord = {};
		return EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected;
	}
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	Locks.Add(Lock);
	return PersistCommitment(
		Schedule,
		PregameCommitment,
		Offer,
		Locks,
		true,
		false,
		ExecutionCommitmentSlot,
		OutRecord,
		OutError);
}

bool LoadOddsWellCanonicalActiveGameExecutionCommitment(
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord& OutRecord,
	FString& OutError)
{
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord PregameCommitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(Schedule, OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(
			PregameCommitment,
			OutError)
		|| !UGameplayStatics::DoesSaveGameExist(
			ExecutionCommitmentSlot,
			ExecutionCommitmentUserIndex))
	{
		if (OutError.IsEmpty())
		{
			OutError = TEXT("No canonical active-game execution commitment exists.");
		}
		OutRecord = {};
		return false;
	}
	return RestoreCommitment(
		UGameplayStatics::LoadGameFromSlot(
			ExecutionCommitmentSlot,
			ExecutionCommitmentUserIndex),
		Schedule,
		PregameCommitment,
		OutRecord,
		OutError);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalActiveGameExecutionCommitmentTest,
	"OddsWell.League.CanonicalActiveGameExecutionCommitment",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalActiveGameExecutionCommitmentTest::RunTest(
	const FString& Parameters)
{
	UGameplayStatics::DeleteGameInSlot(
		ExecutionCommitmentQaSlot,
		ExecutionCommitmentUserIndex);
	const FOddsWellCanonicalScheduledGameRecord Schedule = TestSchedule();
	const FOddsWellCanonicalPregameCommitmentRecord PregameCommitment =
		TestPregameCommitment();
	FOddsWellCanonicalMatchWinnerOfferRecord Offer;
	FString Error;
	TestTrue(
		TEXT("Exact H26C evidence reconstructs without persistence"),
		BuildOddsWellCanonicalMatchWinnerOfferEvidence(
			Schedule,
			PregameCommitment,
			Offer,
			Error));
	FOddsWellMatchWinnerLockRecord Lock;
	Lock.LockCommandId =
		TEXT("canonical:h26g:match_winner:lock:") + Offer.OfferId;
	Lock.RequestCommandId =
		TEXT("canonical:h26e:match_winner:request:") + Offer.OfferId;
	Lock.SeasonNumber = 1;
	Lock.GameNumber = 1;
	Lock.AuthoritativeGameStartUnixSeconds = 2200001800;
	Lock.LockUnixSeconds = 2200001800;
	Lock.Decision = FName(TEXT("locked"));
	TArray<FOddsWellMatchWinnerLockRecord> Locks;
	Locks.Add(Lock);

	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Created;
	TestEqual(
		TEXT("Exact post-H26G execution commitment creates"),
		PersistCommitment(
			Schedule,
			PregameCommitment,
			Offer,
			Locks,
			true,
			false,
			ExecutionCommitmentQaSlot,
			Created,
			Error),
		EOddsWellCanonicalActiveGameExecutionCommitmentResult::Created);
	TestEqual(TEXT("Schema is exact"), Created.Schema, ExecutionCommitmentSchema);
	TestEqual(TEXT("Record version is exact"), Created.RecordVersion, 1);
	TestEqual(TEXT("Status is exact"), Created.Status, CommittedForExecutionStatus);
	TestEqual(TEXT("Seed material length matches Python"), Created.SeedMaterialJson.Len(), 572);
	TestEqual(
		TEXT("Seed material hash matches independent Python"),
		Created.SeedMaterialSha256,
		FString(TEXT("0ee3e752bb9014911c7a535d08cf4fdb0c05f745a0d0ada28bb774a7fd19209b")));
	TestEqual(
		TEXT("Derived seed matches independent Python"),
		Created.ExecutionSeed,
		int64{249816914});
	TestEqual(TEXT("Execution input length matches Python"), Created.ExecutionInputJson.Len(), 4788);
	TestEqual(
		TEXT("Execution input hash matches independent Python"),
		Created.ExecutionInputSha256,
		FString(TEXT("b679a5269440bc53caed60d8c71b31e25ff076b14b0229d9a5739463f4ae9230")));
	TestEqual(TEXT("Commitment JSON length matches Python"), Created.CommitmentJson.Len(), 801);
	TestEqual(
		TEXT("Commitment hash matches independent Python"),
		Created.CommitmentSha256,
		FString(TEXT("c559694689831056b34c737e0dc2ac050635d3c424c8078032b6a47794a334f1")));
	TestTrue(TEXT("League version is bound"), Created.ExecutionInputJson.Contains(TEXT("\"league_version\":\"phase06l-v1\"")));
	TestTrue(TEXT("Engine version is bound"), Created.ExecutionInputJson.Contains(TEXT("\"engine_version\":\"phase05h-v1\"")));
	TestTrue(TEXT("Brain version is bound"), Created.ExecutionInputJson.Contains(TEXT("\"brain_version\":\"baseline-v2\"")));
	TestTrue(TEXT("Life v4 is bound"), Created.ExecutionInputJson.Contains(TEXT("\"life_policy_version\":\"athlete-life-v4\"")));
	TestTrue(TEXT("Consistency v2 is bound"), Created.ExecutionInputJson.Contains(TEXT("\"consistency_version\":\"athlete-consistency-v2\"")));
	TestTrue(TEXT("Involvement v1 is bound"), Created.ExecutionInputJson.Contains(TEXT("\"offensive_involvement_version\":\"offensive-involvement-v1\"")));
	TestTrue(TEXT("Fatigue model is bound"), Created.ExecutionInputJson.Contains(TEXT("\"fatigue_model_version\":\"minutes-workload-v1\"")));
	TestTrue(TEXT("Injury model is bound"), Created.ExecutionInputJson.Contains(TEXT("\"injury_model_version\":\"minor-availability-v1\"")));
	TestTrue(TEXT("No life decisions are bound"), Created.ExecutionInputJson.Contains(TEXT("\"life_decisions\":[]")));
	TestTrue(TEXT("Opening fatigue is zero"), Created.ExecutionInputJson.Contains(TEXT("\"opening_fatigue\":[{\"athlete\":\"Jalen Cross\",\"value\":0.0}")));
	TestTrue(TEXT("Opening recovery is zero"), Created.ExecutionInputJson.Contains(TEXT("\"opening_availability\":[{\"athlete\":\"Jalen Cross\",\"recovery_days\":0}")));
	TestTrue(TEXT("Opening readiness is zero"), Created.ExecutionInputJson.Contains(TEXT("\"opening_readiness\":[{\"athlete\":\"Jalen Cross\",\"value\":0.0}")));
	TestTrue(TEXT("Full default roster is bound"), Created.ExecutionInputJson.Contains(TEXT("\"name\":\"Mateo Cruz\"")));
	TestTrue(TEXT("Full consistency snapshot is bound"), Created.ExecutionInputJson.Contains(TEXT("\"athlete\":\"Tariq Stone\",\"cap\":0.1,\"strength\":0.5,\"tier\":\"elite\"")));
	TestTrue(TEXT("Full involvement snapshot is bound"), Created.ExecutionInputJson.Contains(TEXT("\"athlete\":\"Jalen Cross\",\"tier\":\"featured\",\"weight\":1.15")));

	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Duplicate;
	TestEqual(
		TEXT("Exact cold retry is duplicate-safe"),
		PersistCommitment(
			Schedule,
			PregameCommitment,
			Offer,
			Locks,
			true,
			false,
			ExecutionCommitmentQaSlot,
			Duplicate,
			Error),
		EOddsWellCanonicalActiveGameExecutionCommitmentResult::Duplicate);
	TestTrue(TEXT("Cold retry restores every field"), IsSameCommitment(Created, Duplicate));
	TArray<uint8> BeforeBytes;
	TestTrue(
		TEXT("Commitment serializes before rejection cases"),
		UGameplayStatics::SaveGameToMemory(
			UGameplayStatics::LoadGameFromSlot(
				ExecutionCommitmentQaSlot,
				ExecutionCommitmentUserIndex),
			BeforeBytes));

	const auto RejectWithoutMutation =
		[this, &Schedule, &PregameCommitment, &Offer, &Locks, &BeforeBytes, &Error](
			const FOddsWellCanonicalScheduledGameRecord& CandidateSchedule,
			const FOddsWellCanonicalPregameCommitmentRecord& CandidatePregame,
			const FOddsWellCanonicalMatchWinnerOfferRecord& CandidateOffer,
			const TArray<FOddsWellMatchWinnerLockRecord>& CandidateLocks,
			const bool bCurrentSchema,
			const bool bDownstream,
			const TCHAR* Label)
	{
		FOddsWellCanonicalActiveGameExecutionCommitmentRecord Rejected;
		TestEqual(
			Label,
			PersistCommitment(
				CandidateSchedule,
				CandidatePregame,
				CandidateOffer,
				CandidateLocks,
				bCurrentSchema,
				bDownstream,
				ExecutionCommitmentQaSlot,
				Rejected,
				Error),
			EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected);
		TArray<uint8> AfterBytes;
		TestTrue(
			TEXT("Rejected prerequisite reloads for byte comparison"),
			UGameplayStatics::SaveGameToMemory(
				UGameplayStatics::LoadGameFromSlot(
					ExecutionCommitmentQaSlot,
					ExecutionCommitmentUserIndex),
				AfterBytes));
		TestTrue(
			TEXT("Rejected prerequisite leaves commitment byte-identical"),
			BeforeBytes == AfterBytes);
	};

	FOddsWellCanonicalScheduledGameRecord WrongSchedule = Schedule;
	WrongSchedule.TipoffUnixSeconds += 1;
	RejectWithoutMutation(
		WrongSchedule,
		PregameCommitment,
		Offer,
		Locks,
		true,
		false,
		TEXT("Tampered H26A rejects"));
	FOddsWellCanonicalPregameCommitmentRecord WrongPregame =
		PregameCommitment;
	WrongPregame.CommitmentSha256 = FString::ChrN(64, TEXT('0'));
	RejectWithoutMutation(
		Schedule,
		WrongPregame,
		Offer,
		Locks,
		true,
		false,
		TEXT("Tampered H26B rejects"));
	FOddsWellCanonicalMatchWinnerOfferRecord WrongOffer = Offer;
	WrongOffer.OfferId = FString::ChrN(64, TEXT('a'));
	RejectWithoutMutation(
		Schedule,
		PregameCommitment,
		WrongOffer,
		Locks,
		true,
		false,
		TEXT("Tampered H26C rejects"));
	TArray<FOddsWellMatchWinnerLockRecord> NoLocks;
	RejectWithoutMutation(
		Schedule,
		PregameCommitment,
		Offer,
		NoLocks,
		true,
		false,
		TEXT("Missing H26G rejects"));
	TArray<FOddsWellMatchWinnerLockRecord> MultipleLocks = Locks;
	MultipleLocks.Add(Lock);
	RejectWithoutMutation(
		Schedule,
		PregameCommitment,
		Offer,
		MultipleLocks,
		true,
		false,
		TEXT("Multiple H26G locks reject"));
	RejectWithoutMutation(
		Schedule,
		PregameCommitment,
		Offer,
		Locks,
		false,
		false,
		TEXT("Migrated wager evidence rejects"));
	RejectWithoutMutation(
		Schedule,
		PregameCommitment,
		Offer,
		Locks,
		true,
		true,
		TEXT("Downstream evidence rejects"));

	UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame* Tampered =
		Cast<UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				ExecutionCommitmentQaSlot,
				ExecutionCommitmentUserIndex));
	TestNotNull(TEXT("Commitment reloads for persisted tamper proof"), Tampered);
	if (Tampered)
	{
		Tampered->ExecutionSeed += 1;
		TestTrue(
			TEXT("Tampered commitment saves for rejection proof"),
			UGameplayStatics::SaveGameToSlot(
				Tampered,
				ExecutionCommitmentQaSlot,
				ExecutionCommitmentUserIndex));
		TestEqual(
			TEXT("Persisted commitment tamper rejects without repair"),
			PersistCommitment(
				Schedule,
				PregameCommitment,
				Offer,
				Locks,
				true,
				false,
				ExecutionCommitmentQaSlot,
				Duplicate,
				Error),
			EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected);
		const UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame* Unchanged =
			Cast<UOddsWellCanonicalActiveGameExecutionCommitmentSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					ExecutionCommitmentQaSlot,
					ExecutionCommitmentUserIndex));
		TestTrue(
			TEXT("Persisted tamper is not silently rewritten"),
			Unchanged && Unchanged->ExecutionSeed
				== Created.ExecutionSeed + 1);
	}

	UGameplayStatics::DeleteGameInSlot(
		ExecutionCommitmentQaSlot,
		ExecutionCommitmentUserIndex);
	const FString InvalidSlot =
		TEXT("H26H/") + FString::ChrN(300, TEXT('x'));
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Failed;
	TestEqual(
		TEXT("Native persistence failure rejects"),
		PersistCommitment(
			Schedule,
			PregameCommitment,
			Offer,
			Locks,
			true,
			false,
			InvalidSlot,
			Failed,
			Error),
		EOddsWellCanonicalActiveGameExecutionCommitmentResult::Rejected);
	TestFalse(
		TEXT("Native persistence failure leaves no commitment"),
		UGameplayStatics::DoesSaveGameExist(
			InvalidSlot,
			ExecutionCommitmentUserIndex));
	UGameplayStatics::DeleteGameInSlot(
		InvalidSlot,
		ExecutionCommitmentUserIndex);
	TestFalse(
		TEXT("Native test leaves no H26H QA record"),
		UGameplayStatics::DoesSaveGameExist(
			ExecutionCommitmentQaSlot,
			ExecutionCommitmentUserIndex));
	return !HasAnyErrors();
}
#endif
