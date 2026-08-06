#include "CanonicalActiveGameExecutionCommitment.h"

#include "CanonicalMatchWinnerOffer.h"
#include "CanonicalPregameCommitment.h"
#include "CanonicalScheduledGame.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "OddsBucksLedger.h"
#include "Serialization/JsonSerializer.h"

#include <initializer_list>

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
const FString PrivateSealSchema(
	TEXT("oddswell-private-game-execution-digest-seal-v1"));
const FString PrivateSealStatus(TEXT("sealed_pending_result"));
const FString PrivateExecutorVersion(
	TEXT("oddswell-private-game-executor-v1"));
const FString PrivateVerifierVersion(
	TEXT("oddswell-private-game-digest-verifier-v1"));
const FString PrivateResultSchema(
	TEXT("oddswell-private-canonical-game-result-v1"));
const FString PrivateResultRecorderVersion(
	TEXT("oddswell-private-game-result-recorder-v1"));
const FString PrivateResultStatus(TEXT("recorded_pending_decision"));
const FString PrivateResultCommandPrefix(
	TEXT("canonical:h26l:match_winner:result:"));

struct FPrivateCanonicalResultEvidence
{
	int32 HomeScore = 0;
	int32 AwayScore = 0;
	FString Winner;
	FString RecordSha256;
	FString ReplaySha256;
};

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

bool IsLowerHexHash(const FString& Value)
{
	if (Value.Len() != 64)
	{
		return false;
	}
	for (const TCHAR Character : Value)
	{
		if (!((Character >= TEXT('0') && Character <= TEXT('9'))
			|| (Character >= TEXT('a') && Character <= TEXT('f'))))
		{
			return false;
		}
	}
	return true;
}

bool HasExactKeys(
	const TSharedPtr<FJsonObject>& Object,
	std::initializer_list<const TCHAR*> ExpectedKeys)
{
	if (!Object.IsValid()
		|| Object->Values.Num()
			!= static_cast<int32>(ExpectedKeys.size()))
	{
		return false;
	}
	for (const TCHAR* Key : ExpectedKeys)
	{
		if (!Object->HasField(Key))
		{
			return false;
		}
	}
	return true;
}

bool TryGetExactString(
	const TSharedPtr<FJsonObject>& Object,
	const TCHAR* Key,
	FString& OutValue)
{
	const TSharedPtr<FJsonValue>* Value = Object->Values.Find(Key);
	if (!Value || !Value->IsValid() || (*Value)->Type != EJson::String)
	{
		return false;
	}
	OutValue = (*Value)->AsString();
	return true;
}

bool TryGetExactInt32(
	const TSharedPtr<FJsonObject>& Object,
	const TCHAR* Key,
	int32& OutValue)
{
	const TSharedPtr<FJsonValue>* Value = Object->Values.Find(Key);
	if (!Value || !Value->IsValid() || (*Value)->Type != EJson::Number)
	{
		return false;
	}
	const double Number = (*Value)->AsNumber();
	if (!FMath::IsFinite(Number)
		|| Number < static_cast<double>(TNumericLimits<int32>::Min())
		|| Number > static_cast<double>(TNumericLimits<int32>::Max()))
	{
		return false;
	}
	const int32 Integer = static_cast<int32>(Number);
	if (Number != static_cast<double>(Integer))
	{
		return false;
	}
	OutValue = Integer;
	return true;
}

bool ParseExactJson(
	const FString& Raw,
	std::initializer_list<const TCHAR*> ExpectedKeys,
	TSharedPtr<FJsonObject>& OutObject)
{
	OutObject.Reset();
	const TSharedRef<TJsonReader<>> Reader =
		TJsonReaderFactory<>::Create(Raw);
	return FJsonSerializer::Deserialize(Reader, OutObject)
		&& HasExactKeys(OutObject, ExpectedKeys);
}

bool LoadOnlyCommitmentFile(
	const FString& Directory,
	const FString& CommitmentSha256,
	FString& OutRaw,
	FString& OutError)
{
	const FString ExpectedName = CommitmentSha256 + TEXT(".json");
	TArray<FString> Names;
	IFileManager::Get().FindFiles(
		Names,
		*FPaths::Combine(Directory, TEXT("*.json")),
		true,
		false);
	Names.Sort();
	if (Names.Num() != 1 || Names[0] != ExpectedName)
	{
		OutError =
			TEXT("Exactly one commitment-keyed private JSON record is required.");
		return false;
	}
	if (!FFileHelper::LoadFileToString(
		OutRaw,
		*FPaths::Combine(Directory, ExpectedName)))
	{
		OutError = TEXT("The private JSON record could not be read.");
		return false;
	}
	return true;
}

bool LoadPrivateCanonicalResultEvidence(
	const FOddsWellCanonicalActiveGameExecutionCommitmentRecord& Commitment,
	const FString& SealDirectory,
	const FString& ResultDirectory,
	FPrivateCanonicalResultEvidence& OutEvidence,
	FString& OutError)
{
	OutEvidence = {};
	FString SealRaw;
	if (!LoadOnlyCommitmentFile(
		SealDirectory,
		Commitment.CommitmentSha256,
		SealRaw,
		OutError))
	{
		return false;
	}
	TSharedPtr<FJsonObject> Seal;
	FString SealCommitmentSha256;
	FString SealExecutionInputSha256;
	FString ExecutorVersion;
	FString ReceiptSha256;
	int32 SealRecordVersion = 0;
	FString SealSchema;
	FString SealSha256;
	FString SealStatus;
	FString VerifiedDigestSha256;
	FString VerifierVersion;
	if (!ParseExactJson(
			SealRaw,
			{
				TEXT("commitment_sha256"),
				TEXT("execution_input_sha256"),
				TEXT("executor_version"),
				TEXT("receipt_sha256"),
				TEXT("record_version"),
				TEXT("schema"),
				TEXT("seal_sha256"),
				TEXT("status"),
				TEXT("verified_output_digest_sha256"),
				TEXT("verifier_version")},
			Seal)
		|| !TryGetExactString(
			Seal,
			TEXT("commitment_sha256"),
			SealCommitmentSha256)
		|| !TryGetExactString(
			Seal,
			TEXT("execution_input_sha256"),
			SealExecutionInputSha256)
		|| !TryGetExactString(
			Seal,
			TEXT("executor_version"),
			ExecutorVersion)
		|| !TryGetExactString(
			Seal,
			TEXT("receipt_sha256"),
			ReceiptSha256)
		|| !TryGetExactInt32(
			Seal,
			TEXT("record_version"),
			SealRecordVersion)
		|| !TryGetExactString(Seal, TEXT("schema"), SealSchema)
		|| !TryGetExactString(
			Seal,
			TEXT("seal_sha256"),
			SealSha256)
		|| !TryGetExactString(Seal, TEXT("status"), SealStatus)
		|| !TryGetExactString(
			Seal,
			TEXT("verified_output_digest_sha256"),
			VerifiedDigestSha256)
		|| !TryGetExactString(
			Seal,
			TEXT("verifier_version"),
			VerifierVersion))
	{
		OutError =
			TEXT("The private H26J seal has invalid keys or JSON types.");
		return false;
	}
	const FString SealBody = FString::Printf(
		TEXT("{\"commitment_sha256\":\"%s\",\"execution_input_sha256\":\"%s\",\"executor_version\":\"%s\",\"receipt_sha256\":\"%s\",\"record_version\":%d,\"schema\":\"%s\",\"status\":\"%s\",\"verified_output_digest_sha256\":\"%s\",\"verifier_version\":\"%s\"}"),
		*SealCommitmentSha256,
		*SealExecutionInputSha256,
		*ExecutorVersion,
		*ReceiptSha256,
		SealRecordVersion,
		*SealSchema,
		*SealStatus,
		*VerifiedDigestSha256,
		*VerifierVersion);
	FString ExpectedSealSha256;
	if (SealCommitmentSha256 != Commitment.CommitmentSha256
		|| SealExecutionInputSha256
			!= Commitment.ExecutionInputSha256
		|| ExecutorVersion != PrivateExecutorVersion
		|| !IsLowerHexHash(ReceiptSha256)
		|| SealRecordVersion != 1
		|| SealSchema != PrivateSealSchema
		|| SealStatus != PrivateSealStatus
		|| !IsLowerHexHash(VerifiedDigestSha256)
		|| VerifierVersion != PrivateVerifierVersion
		|| !HashSha256(
			SealBody,
			ExpectedSealSha256,
			OutError)
		|| SealSha256 != ExpectedSealSha256
		|| !IsLowerHexHash(SealSha256))
	{
		if (OutError.IsEmpty())
		{
			OutError =
				TEXT("The private H26J seal conflicts with exact H26H evidence.");
		}
		return false;
	}
	const FString ExpectedSealRaw = FString::Printf(
		TEXT("{\"commitment_sha256\":\"%s\",\"execution_input_sha256\":\"%s\",\"executor_version\":\"%s\",\"receipt_sha256\":\"%s\",\"record_version\":%d,\"schema\":\"%s\",\"seal_sha256\":\"%s\",\"status\":\"%s\",\"verified_output_digest_sha256\":\"%s\",\"verifier_version\":\"%s\"}"),
		*SealCommitmentSha256,
		*SealExecutionInputSha256,
		*ExecutorVersion,
		*ReceiptSha256,
		SealRecordVersion,
		*SealSchema,
		*SealSha256,
		*SealStatus,
		*VerifiedDigestSha256,
		*VerifierVersion);
	if (SealRaw != ExpectedSealRaw)
	{
		OutError = TEXT("The private H26J seal is not exact canonical JSON.");
		return false;
	}

	FString ResultRaw;
	if (!LoadOnlyCommitmentFile(
		ResultDirectory,
		Commitment.CommitmentSha256,
		ResultRaw,
		OutError))
	{
		return false;
	}
	TSharedPtr<FJsonObject> Result;
	int32 AwayScore = 0;
	FString AwayTeam;
	FString ResultCommitmentSha256;
	int32 GameNumber = 0;
	int32 HomeScore = 0;
	FString HomeTeam;
	FString RecordSha256;
	int32 ResultRecordVersion = 0;
	FString RecorderVersion;
	FString ReplaySha256;
	FString ResultSchema;
	FString ResultSealSha256;
	int32 SeasonNumber = 0;
	FString ResultStatus;
	FString Winner;
	if (!ParseExactJson(
			ResultRaw,
			{
				TEXT("away_score"),
				TEXT("away_team"),
				TEXT("commitment_sha256"),
				TEXT("game_number"),
				TEXT("home_score"),
				TEXT("home_team"),
				TEXT("record_sha256"),
				TEXT("record_version"),
				TEXT("recorder_version"),
				TEXT("replay_sha256"),
				TEXT("schema"),
				TEXT("seal_sha256"),
				TEXT("season_number"),
				TEXT("status"),
				TEXT("winner")},
			Result)
		|| !TryGetExactInt32(Result, TEXT("away_score"), AwayScore)
		|| !TryGetExactString(Result, TEXT("away_team"), AwayTeam)
		|| !TryGetExactString(
			Result,
			TEXT("commitment_sha256"),
			ResultCommitmentSha256)
		|| !TryGetExactInt32(Result, TEXT("game_number"), GameNumber)
		|| !TryGetExactInt32(Result, TEXT("home_score"), HomeScore)
		|| !TryGetExactString(Result, TEXT("home_team"), HomeTeam)
		|| !TryGetExactString(
			Result,
			TEXT("record_sha256"),
			RecordSha256)
		|| !TryGetExactInt32(
			Result,
			TEXT("record_version"),
			ResultRecordVersion)
		|| !TryGetExactString(
			Result,
			TEXT("recorder_version"),
			RecorderVersion)
		|| !TryGetExactString(
			Result,
			TEXT("replay_sha256"),
			ReplaySha256)
		|| !TryGetExactString(Result, TEXT("schema"), ResultSchema)
		|| !TryGetExactString(
			Result,
			TEXT("seal_sha256"),
			ResultSealSha256)
		|| !TryGetExactInt32(
			Result,
			TEXT("season_number"),
			SeasonNumber)
		|| !TryGetExactString(Result, TEXT("status"), ResultStatus)
		|| !TryGetExactString(Result, TEXT("winner"), Winner))
	{
		OutError =
			TEXT("The private H26K result has invalid keys or JSON types.");
		return false;
	}
	const FString DerivedWinner =
		HomeScore > AwayScore ? HomeTeam : AwayTeam;
	const FString ResultBody = FString::Printf(
		TEXT("{\"away_score\":%d,\"away_team\":\"%s\",\"commitment_sha256\":\"%s\",\"game_number\":%d,\"home_score\":%d,\"home_team\":\"%s\",\"record_version\":%d,\"recorder_version\":\"%s\",\"replay_sha256\":\"%s\",\"schema\":\"%s\",\"seal_sha256\":\"%s\",\"season_number\":%d,\"status\":\"%s\",\"winner\":\"%s\"}"),
		AwayScore,
		*AwayTeam,
		*ResultCommitmentSha256,
		GameNumber,
		HomeScore,
		*HomeTeam,
		ResultRecordVersion,
		*RecorderVersion,
		*ReplaySha256,
		*ResultSchema,
		*ResultSealSha256,
		SeasonNumber,
		*ResultStatus,
		*Winner);
	FString ExpectedRecordSha256;
	if (AwayScore < 0
		|| HomeScore < 0
		|| AwayScore == HomeScore
		|| AwayTeam != Commitment.AwayTeam
		|| HomeTeam != Commitment.HomeTeam
		|| ResultCommitmentSha256
			!= Commitment.CommitmentSha256
		|| GameNumber != Commitment.GameNumber
		|| ResultRecordVersion != 1
		|| RecorderVersion != PrivateResultRecorderVersion
		|| ReplaySha256 != VerifiedDigestSha256
		|| !IsLowerHexHash(ReplaySha256)
		|| ResultSchema != PrivateResultSchema
		|| ResultSealSha256 != SealSha256
		|| SeasonNumber != Commitment.SeasonNumber
		|| ResultStatus != PrivateResultStatus
		|| Winner != DerivedWinner
		|| !HashSha256(
			ResultBody,
			ExpectedRecordSha256,
			OutError)
		|| RecordSha256 != ExpectedRecordSha256
		|| !IsLowerHexHash(RecordSha256))
	{
		if (OutError.IsEmpty())
		{
			OutError =
				TEXT("The private H26K result conflicts with exact H26H/H26J evidence.");
		}
		return false;
	}
	const FString ExpectedResultRaw = FString::Printf(
		TEXT("{\"away_score\":%d,\"away_team\":\"%s\",\"commitment_sha256\":\"%s\",\"game_number\":%d,\"home_score\":%d,\"home_team\":\"%s\",\"record_sha256\":\"%s\",\"record_version\":%d,\"recorder_version\":\"%s\",\"replay_sha256\":\"%s\",\"schema\":\"%s\",\"seal_sha256\":\"%s\",\"season_number\":%d,\"status\":\"%s\",\"winner\":\"%s\"}"),
		AwayScore,
		*AwayTeam,
		*ResultCommitmentSha256,
		GameNumber,
		HomeScore,
		*HomeTeam,
		*RecordSha256,
		ResultRecordVersion,
		*RecorderVersion,
		*ReplaySha256,
		*ResultSchema,
		*ResultSealSha256,
		SeasonNumber,
		*ResultStatus,
		*Winner);
	if (ResultRaw != ExpectedResultRaw)
	{
		OutError =
			TEXT("The private H26K result is not exact canonical JSON.");
		return false;
	}
	OutEvidence.HomeScore = HomeScore;
	OutEvidence.AwayScore = AwayScore;
	OutEvidence.Winner = MoveTemp(Winner);
	OutEvidence.RecordSha256 = MoveTemp(RecordSha256);
	OutEvidence.ReplaySha256 = MoveTemp(ReplaySha256);
	OutError.Reset();
	return true;
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

FString BuildExecutionHandoffJson(
	const FOddsWellCanonicalActiveGameExecutionCommitmentRecord& Record)
{
	return FString::Printf(
		TEXT("{\"away_team\":\"%s\",\"commitment\":%s,\"commitment_sha256\":\"%s\",\"environment\":\"%s\",\"execution_input\":%s,\"execution_input_sha256\":\"%s\",\"execution_seed\":%lld,\"game_number\":%d,\"home_team\":\"%s\",\"offer_eligible_unix\":%lld,\"pregame_commitment_sha256\":\"%s\",\"record_version\":%d,\"schedule_created_unix\":%lld,\"schedule_record_version\":%d,\"schedule_schema\":\"%s\",\"schedule_tipoff_unix\":%lld,\"schema\":\"%s\",\"season_number\":%d,\"seed_derivation_version\":\"%s\",\"seed_material\":%s,\"seed_material_sha256\":\"%s\",\"status\":\"%s\"}"),
		*Record.AwayTeam,
		*Record.CommitmentJson,
		*Record.CommitmentSha256,
		*Record.Environment,
		*Record.ExecutionInputJson,
		*Record.ExecutionInputSha256,
		Record.ExecutionSeed,
		Record.GameNumber,
		*Record.HomeTeam,
		Record.OfferEligibleUnixSeconds,
		*Record.PregameCommitmentSha256,
		Record.RecordVersion,
		Record.ScheduleCreatedUnixSeconds,
		Record.ScheduleRecordVersion,
		*Record.ScheduleSchema,
		Record.ScheduleTipoffUnixSeconds,
		*Record.Schema,
		Record.SeasonNumber,
		*Record.SeedDerivationVersion,
		*Record.SeedMaterialJson,
		*Record.SeedMaterialSha256,
		*Record.Status);
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

EOddsWellCanonicalGameExecutionHandoffResult
WriteOddsWellCanonicalGameExecutionHandoff(
	FString& OutPath,
	FString& OutSha256,
	FString& OutError)
{
	OutPath.Reset();
	OutSha256.Reset();
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalActiveGameExecutionCommitment(
		Commitment,
		OutError))
	{
		return EOddsWellCanonicalGameExecutionHandoffResult::Rejected;
	}
	const FString Json = BuildExecutionHandoffJson(Commitment);
	if (!HashSha256(Json, OutSha256, OutError))
	{
		return EOddsWellCanonicalGameExecutionHandoffResult::Rejected;
	}
	OutPath = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("PrivateExecution"),
		TEXT("Handoff"),
		TEXT("OddsWellCanonicalActiveGameExecutionHandoff.json"));
	if (IFileManager::Get().FileExists(*OutPath))
	{
		FString Existing;
		if (!FFileHelper::LoadFileToString(Existing, *OutPath)
			|| Existing != Json)
		{
			OutError =
				TEXT("The private execution handoff conflicts with exact H26H evidence.");
			return EOddsWellCanonicalGameExecutionHandoffResult::Rejected;
		}
		OutError.Reset();
		return EOddsWellCanonicalGameExecutionHandoffResult::Duplicate;
	}
	IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutPath), true);
	const FString TemporaryPath = OutPath + TEXT(".tmp");
	if (!FFileHelper::SaveStringToFile(
			Json,
			*TemporaryPath,
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)
		|| !IFileManager::Get().Move(
			*OutPath,
			*TemporaryPath,
			true,
			true,
			false,
			true))
	{
		IFileManager::Get().Delete(*TemporaryPath, false, true, true);
		OutError = TEXT("The private execution handoff could not be written atomically.");
		return EOddsWellCanonicalGameExecutionHandoffResult::Rejected;
	}
	FString Persisted;
	if (!FFileHelper::LoadFileToString(Persisted, *OutPath)
		|| Persisted != Json)
	{
		OutError = TEXT("The private execution handoff did not persist exactly.");
		return EOddsWellCanonicalGameExecutionHandoffResult::Rejected;
	}
	OutError.Reset();
	return EOddsWellCanonicalGameExecutionHandoffResult::Created;
}

EOddsWellMatchWinnerResultLinkResult
LinkOddsWellCanonicalMatchWinnerResult(
	FOddsWellMatchWinnerResultLinkRecord& OutRecord,
	FString& OutError)
{
	OutRecord = {};
	FOddsWellCanonicalScheduledGameRecord Schedule;
	FOddsWellCanonicalPregameCommitmentRecord PregameCommitment;
	FOddsWellCanonicalMatchWinnerOfferRecord Offer;
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
	if (!LoadOddsWellCanonicalLocalBetaScheduledGame(
			Schedule,
			OutError)
		|| !LoadOddsWellCanonicalPregameCommitment(
			PregameCommitment,
			OutError)
		|| !LoadOddsWellCanonicalMatchWinnerOffer(
			Offer,
			OutError)
		|| !LoadOddsWellCanonicalActiveGameExecutionCommitment(
			Commitment,
			OutError)
		|| !HasExactH26AB(Schedule, PregameCommitment)
		|| Commitment.SeasonNumber != Schedule.SeasonNumber
		|| Commitment.GameNumber != Schedule.GameNumber
		|| Commitment.HomeTeam != Schedule.HomeTeam
		|| Commitment.AwayTeam != Schedule.AwayTeam)
	{
		if (OutError.IsEmpty())
		{
			OutError =
				TEXT("Canonical result linking requires exact H26A/B/C/H evidence.");
		}
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}

	FPrivateCanonicalResultEvidence Evidence;
	if (!LoadPrivateCanonicalResultEvidence(
			Commitment,
			FPaths::Combine(
				FPaths::ProjectSavedDir(),
				TEXT("PrivateExecution"),
				TEXT("Seals")),
			FPaths::Combine(
				FPaths::ProjectSavedDir(),
				TEXT("PrivateExecution"),
				TEXT("Results")),
			Evidence,
			OutError))
	{
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}

	FOddsWellMatchWinnerResultLinkRecord Candidate;
	Candidate.ResultCommandId =
		PrivateResultCommandPrefix + Evidence.RecordSha256;
	Candidate.RequestCommandId =
		TEXT("canonical:h26e:match_winner:request:")
		+ Offer.OfferId;
	Candidate.LockCommandId =
		TEXT("canonical:h26g:match_winner:lock:")
		+ Offer.OfferId;
	Candidate.ResultSchema = PrivateResultSchema;
	Candidate.ResultVersion = PrivateResultRecorderVersion;
	Candidate.SeasonNumber = Schedule.SeasonNumber;
	Candidate.GameNumber = Schedule.GameNumber;
	Candidate.HomeTeam = Schedule.HomeTeam;
	Candidate.AwayTeam = Schedule.AwayTeam;
	Candidate.HomeScore = Evidence.HomeScore;
	Candidate.AwayScore = Evidence.AwayScore;
	Candidate.Winner = Evidence.Winner;
	Candidate.ReplaySealSha256 = Evidence.ReplaySha256;
	if (!ValidateOddsWellCanonicalMatchWinnerResultLinkPrerequisites(
			Candidate,
			OutError))
	{
		return EOddsWellMatchWinnerResultLinkResult::Rejected;
	}
	return LinkOddsWellMatchWinnerResult(
		Candidate.ResultCommandId,
		Candidate.RequestCommandId,
		Candidate.LockCommandId,
		Candidate.ResultSchema,
		Candidate.ResultVersion,
		Candidate.SeasonNumber,
		Candidate.GameNumber,
		Candidate.HomeTeam,
		Candidate.AwayTeam,
		Candidate.HomeScore,
		Candidate.AwayScore,
		Candidate.Winner,
		Candidate.ReplaySealSha256,
		UseOddsWellOddsBucksQaSlot(),
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalGameExecutionHandoffTest,
	"OddsWell.League.CanonicalGameExecutionHandoff",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalGameExecutionHandoffTest::RunTest(
	const FString& Parameters)
{
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
	FString Error;
	TestTrue(
		TEXT("Exact fixture builds"),
		BuildExpectedCommitment(
			TestSchedule(),
			TestPregameCommitment(),
			Commitment,
			Error));
	const FString Handoff = BuildExecutionHandoffJson(Commitment);
	FString HandoffSha256;
	TestTrue(
		TEXT("Handoff hashes"),
		HashSha256(Handoff, HandoffSha256, Error));
	TestEqual(TEXT("Canonical handoff length is fixed"), Handoff.Len(), 7099);
	TestEqual(
		TEXT("Native handoff matches independent Python canonical SHA"),
		HandoffSha256,
		FString(
			TEXT("6337d3fa64e88ab2c0372c74616e45a96f2523c084fe111d0bd9a41a671a9667")));
	TestTrue(
		TEXT("Handoff embeds exact commitment object"),
		Handoff.Contains(
			TEXT("\"commitment\":{\"away_team\":\"Mesa Vista Sol\"")));
	TestTrue(
		TEXT("Handoff embeds exact frozen input object"),
		Handoff.Contains(
			TEXT("\"execution_input\":{\"brain_version\":\"baseline-v2\"")));
	TestTrue(
		TEXT("Handoff embeds exact seed material object"),
		Handoff.Contains(
			TEXT("\"seed_material\":{\"away_team\":\"Mesa Vista Sol\"")));
	for (const TCHAR* Forbidden : {
		TEXT("\"offer_id\""),
		TEXT("\"request\""),
		TEXT("\"selection\""),
		TEXT("\"stake\""),
		TEXT("\"balance\""),
		TEXT("\"ledger\""),
		TEXT("\"lock_command\""),
		TEXT("\"accepted_unix\""),
		TEXT("\"output\""),
		TEXT("\"score\""),
		TEXT("\"winner\""),
		TEXT("\"tape\""),
		TEXT("\"event_log\""),
		TEXT("\"replay\""),
		TEXT("\"settlement\""),
		TEXT("\"odds_bucks\"")})
	{
		TestFalse(
			FString::Printf(TEXT("Private handoff excludes %s"), Forbidden),
			Handoff.Contains(Forbidden));
	}
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalMatchWinnerResultLinkEvidenceTest,
	"OddsWell.League.CanonicalMatchWinnerResultLink",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalMatchWinnerResultLinkEvidenceTest::RunTest(
	const FString& Parameters)
{
	FOddsWellCanonicalActiveGameExecutionCommitmentRecord Commitment;
	FString Error;
	TestTrue(
		TEXT("Exact H26H fixture builds"),
		BuildExpectedCommitment(
			TestSchedule(),
			TestPregameCommitment(),
			Commitment,
			Error));
	const FString Root = FPaths::Combine(
		FPaths::ProjectSavedDir(),
		TEXT("Automation"),
		TEXT("H26L"));
	const FString SealDirectory =
		FPaths::Combine(Root, TEXT("Seals"));
	const FString ResultDirectory =
		FPaths::Combine(Root, TEXT("Results"));
	IFileManager::Get().DeleteDirectory(*Root, false, true);
	TestTrue(
		TEXT("Private fixture directories create"),
		IFileManager::Get().MakeDirectory(
			*SealDirectory,
			true)
			&& IFileManager::Get().MakeDirectory(
				*ResultDirectory,
				true));
	const FString EvidenceName =
		Commitment.CommitmentSha256 + TEXT(".json");
	const FString SealPath =
		FPaths::Combine(SealDirectory, EvidenceName);
	const FString ResultPath =
		FPaths::Combine(ResultDirectory, EvidenceName);
	const FString ReceiptSha256 = FString::ChrN(64, TEXT('1'));
	const FString ReplaySha256 = FString::ChrN(64, TEXT('2'));
	const FString SealBody = FString::Printf(
		TEXT("{\"commitment_sha256\":\"%s\",\"execution_input_sha256\":\"%s\",\"executor_version\":\"%s\",\"receipt_sha256\":\"%s\",\"record_version\":1,\"schema\":\"%s\",\"status\":\"%s\",\"verified_output_digest_sha256\":\"%s\",\"verifier_version\":\"%s\"}"),
		*Commitment.CommitmentSha256,
		*Commitment.ExecutionInputSha256,
		*PrivateExecutorVersion,
		*ReceiptSha256,
		*PrivateSealSchema,
		*PrivateSealStatus,
		*ReplaySha256,
		*PrivateVerifierVersion);
	FString SealSha256;
	TestTrue(
		TEXT("Exact H26J fixture hashes"),
		HashSha256(SealBody, SealSha256, Error));
	const FString SealRaw = FString::Printf(
		TEXT("{\"commitment_sha256\":\"%s\",\"execution_input_sha256\":\"%s\",\"executor_version\":\"%s\",\"receipt_sha256\":\"%s\",\"record_version\":1,\"schema\":\"%s\",\"seal_sha256\":\"%s\",\"status\":\"%s\",\"verified_output_digest_sha256\":\"%s\",\"verifier_version\":\"%s\"}"),
		*Commitment.CommitmentSha256,
		*Commitment.ExecutionInputSha256,
		*PrivateExecutorVersion,
		*ReceiptSha256,
		*PrivateSealSchema,
		*SealSha256,
		*PrivateSealStatus,
		*ReplaySha256,
		*PrivateVerifierVersion);
	const FString ResultBody = FString::Printf(
		TEXT("{\"away_score\":104,\"away_team\":\"%s\",\"commitment_sha256\":\"%s\",\"game_number\":1,\"home_score\":99,\"home_team\":\"%s\",\"record_version\":1,\"recorder_version\":\"%s\",\"replay_sha256\":\"%s\",\"schema\":\"%s\",\"seal_sha256\":\"%s\",\"season_number\":1,\"status\":\"%s\",\"winner\":\"%s\"}"),
		*Commitment.AwayTeam,
		*Commitment.CommitmentSha256,
		*Commitment.HomeTeam,
		*PrivateResultRecorderVersion,
		*ReplaySha256,
		*PrivateResultSchema,
		*SealSha256,
		*PrivateResultStatus,
		*Commitment.AwayTeam);
	FString RecordSha256;
	TestTrue(
		TEXT("Exact H26K fixture hashes"),
		HashSha256(ResultBody, RecordSha256, Error));
	const FString ResultRaw = FString::Printf(
		TEXT("{\"away_score\":104,\"away_team\":\"%s\",\"commitment_sha256\":\"%s\",\"game_number\":1,\"home_score\":99,\"home_team\":\"%s\",\"record_sha256\":\"%s\",\"record_version\":1,\"recorder_version\":\"%s\",\"replay_sha256\":\"%s\",\"schema\":\"%s\",\"seal_sha256\":\"%s\",\"season_number\":1,\"status\":\"%s\",\"winner\":\"%s\"}"),
		*Commitment.AwayTeam,
		*Commitment.CommitmentSha256,
		*Commitment.HomeTeam,
		*RecordSha256,
		*PrivateResultRecorderVersion,
		*ReplaySha256,
		*PrivateResultSchema,
		*SealSha256,
		*PrivateResultStatus,
		*Commitment.AwayTeam);
	auto WriteExact = [this](
		const FString& Path,
		const FString& Raw,
		const TCHAR* Label)
	{
		TestTrue(
			Label,
			FFileHelper::SaveStringToFile(
				Raw,
				*Path,
				FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM));
	};
	WriteExact(SealPath, SealRaw, TEXT("Exact H26J fixture writes"));
	WriteExact(ResultPath, ResultRaw, TEXT("Exact H26K fixture writes"));
	FPrivateCanonicalResultEvidence Evidence;
	TestTrue(
		TEXT("Exact private H26J/H26K chain validates"),
		LoadPrivateCanonicalResultEvidence(
			Commitment,
			SealDirectory,
			ResultDirectory,
			Evidence,
			Error));
	TestEqual(TEXT("H26K home score is exact"), Evidence.HomeScore, 99);
	TestEqual(TEXT("H26K away score is exact"), Evidence.AwayScore, 104);
	TestEqual(TEXT("H26K winner is exact"), Evidence.Winner, Commitment.AwayTeam);
	TestEqual(TEXT("H26K record hash is exact"), Evidence.RecordSha256, RecordSha256);
	TestEqual(TEXT("H26K replay hash is exact"), Evidence.ReplaySha256, ReplaySha256);

	auto RejectRawWithoutRepair =
		[this,
			&Commitment,
			&SealDirectory,
			&ResultDirectory,
			&Evidence,
			&Error,
			&WriteExact](
			const FString& Path,
			const FString& Raw,
			const TCHAR* Label)
	{
		WriteExact(Path, Raw, Label);
		TestFalse(
			Label,
			LoadPrivateCanonicalResultEvidence(
				Commitment,
				SealDirectory,
				ResultDirectory,
				Evidence,
				Error));
		FString After;
		TestTrue(
			TEXT("Rejected private evidence remains readable"),
			FFileHelper::LoadFileToString(After, *Path));
		TestEqual(
			TEXT("Rejected private evidence is not repaired"),
			After,
			Raw);
	};
	for (const TPair<FString, FString>& Mutation : {
		TPair<FString, FString>(
			TEXT("H26J wrong schema rejects"),
			SealRaw.Replace(
				*PrivateSealSchema,
				TEXT("wrong-seal-schema"))),
		TPair<FString, FString>(
			TEXT("H26J wrong status rejects"),
			SealRaw.Replace(
				*PrivateSealStatus,
				TEXT("wrong_status"))),
		TPair<FString, FString>(
			TEXT("H26J wrong version rejects"),
			SealRaw.Replace(
				TEXT("\"record_version\":1"),
				TEXT("\"record_version\":2"))),
		TPair<FString, FString>(
			TEXT("H26J wrong commitment rejects"),
			SealRaw.Replace(
				*Commitment.CommitmentSha256,
				*FString::ChrN(64, TEXT('3')))),
		TPair<FString, FString>(
			TEXT("H26J wrong input hash rejects"),
			SealRaw.Replace(
				*Commitment.ExecutionInputSha256,
				*FString::ChrN(64, TEXT('4')))),
		TPair<FString, FString>(
			TEXT("H26J wrong receipt hash rejects"),
			SealRaw.Replace(
				*ReceiptSha256,
				*FString::ChrN(64, TEXT('5')))),
		TPair<FString, FString>(
			TEXT("H26J wrong digest rejects"),
			SealRaw.Replace(
				*ReplaySha256,
				*FString::ChrN(64, TEXT('6')))),
		TPair<FString, FString>(
			TEXT("H26J wrong seal hash rejects"),
			SealRaw.Replace(
				*SealSha256,
				*FString::ChrN(64, TEXT('7')))),
		TPair<FString, FString>(
			TEXT("H26J extra key rejects"),
			SealRaw.LeftChop(1) + TEXT(",\"extra\":0}")),
		TPair<FString, FString>(
			TEXT("H26J noncanonical bytes reject"),
			SealRaw + TEXT(" "))})
	{
		RejectRawWithoutRepair(
			SealPath,
			Mutation.Value,
			*Mutation.Key);
		WriteExact(
			SealPath,
			SealRaw,
			TEXT("Exact H26J fixture restores"));
	}
	for (const TPair<FString, FString>& Mutation : {
		TPair<FString, FString>(
			TEXT("H26K wrong schema rejects"),
			ResultRaw.Replace(
				*PrivateResultSchema,
				TEXT("wrong-result-schema"))),
		TPair<FString, FString>(
			TEXT("H26K wrong recorder rejects"),
			ResultRaw.Replace(
				*PrivateResultRecorderVersion,
				TEXT("wrong-recorder"))),
		TPair<FString, FString>(
			TEXT("H26K wrong status rejects"),
			ResultRaw.Replace(
				*PrivateResultStatus,
				TEXT("wrong_status"))),
		TPair<FString, FString>(
			TEXT("H26K wrong version rejects"),
			ResultRaw.Replace(
				TEXT("\"record_version\":1"),
				TEXT("\"record_version\":2"))),
		TPair<FString, FString>(
			TEXT("H26K wrong commitment rejects"),
			ResultRaw.Replace(
				*Commitment.CommitmentSha256,
				*FString::ChrN(64, TEXT('3')))),
		TPair<FString, FString>(
			TEXT("H26K wrong seal rejects"),
			ResultRaw.Replace(
				*SealSha256,
				*FString::ChrN(64, TEXT('4')))),
		TPair<FString, FString>(
			TEXT("H26K wrong replay rejects"),
			ResultRaw.Replace(
				*ReplaySha256,
				*FString::ChrN(64, TEXT('5')))),
		TPair<FString, FString>(
			TEXT("H26K wrong home team rejects"),
			ResultRaw.Replace(
				*Commitment.HomeTeam,
				TEXT("Wrong Home"))),
		TPair<FString, FString>(
			TEXT("H26K wrong away team rejects"),
			ResultRaw.Replace(
				*Commitment.AwayTeam,
				TEXT("Wrong Away"))),
		TPair<FString, FString>(
			TEXT("H26K wrong game rejects"),
			ResultRaw.Replace(
				TEXT("\"game_number\":1"),
				TEXT("\"game_number\":2"))),
		TPair<FString, FString>(
			TEXT("H26K wrong season rejects"),
			ResultRaw.Replace(
				TEXT("\"season_number\":1"),
				TEXT("\"season_number\":2"))),
		TPair<FString, FString>(
			TEXT("H26K tie rejects"),
			ResultRaw.Replace(
				TEXT("\"home_score\":99"),
				TEXT("\"home_score\":104"))),
		TPair<FString, FString>(
			TEXT("H26K fractional score rejects"),
			ResultRaw.Replace(
				TEXT("\"home_score\":99"),
				TEXT("\"home_score\":99.5"))),
		TPair<FString, FString>(
			TEXT("H26K wrong winner rejects"),
			ResultRaw.Replace(
				TEXT("\"winner\":\"Mesa Vista Sol\""),
				TEXT("\"winner\":\"Harbor City Waves\""))),
		TPair<FString, FString>(
			TEXT("H26K wrong record hash rejects"),
			ResultRaw.Replace(
				*RecordSha256,
				*FString::ChrN(64, TEXT('6')))),
		TPair<FString, FString>(
			TEXT("H26K extra key rejects"),
			ResultRaw.LeftChop(1) + TEXT(",\"extra\":0}")),
		TPair<FString, FString>(
			TEXT("H26K noncanonical bytes reject"),
			ResultRaw + TEXT(" "))})
	{
		RejectRawWithoutRepair(
			ResultPath,
			Mutation.Value,
			*Mutation.Key);
		WriteExact(
			ResultPath,
			ResultRaw,
			TEXT("Exact H26K fixture restores"));
	}
	WriteExact(
		FPaths::Combine(ResultDirectory, TEXT("extra.json")),
		ResultRaw,
		TEXT("Conflicting second H26K result writes"));
	TestFalse(
		TEXT("Multiple H26K results reject"),
		LoadPrivateCanonicalResultEvidence(
			Commitment,
			SealDirectory,
			ResultDirectory,
			Evidence,
			Error));
	TestTrue(
		TEXT("Conflicting H26K result deletes"),
		IFileManager::Get().Delete(
			*FPaths::Combine(ResultDirectory, TEXT("extra.json"))));
	TestTrue(
		TEXT("Exact private chain restores after rejection matrix"),
		LoadPrivateCanonicalResultEvidence(
			Commitment,
			SealDirectory,
			ResultDirectory,
			Evidence,
			Error));
	TestTrue(
		TEXT("Private evidence test cleanup succeeds"),
		IFileManager::Get().DeleteDirectory(*Root, false, true));
	return !HasAnyErrors();
}
#endif
