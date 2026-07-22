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
constexpr int32 OddsBucksSchemaVersion = 4;
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
const FString FirstJobCommandId(TEXT("job:placeholder_shift:first_payout:v1"));
const FName FirstJobReason(TEXT("placeholder_job_payout"));
const FName MatchWinnerStakeReason(TEXT("match_winner_stake"));
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

const FString& GetOddsBucksSlot(const bool bQaSlot)
{
	return bQaSlot ? OddsBucksQaSlot : OddsBucksSlot;
}

FString GetOddsBucksReconciliationPath(const bool bQaProjection)
{
	return FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("Admin"), bQaProjection ? OddsBucksQaReconciliationFile : OddsBucksReconciliationFile);
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

bool ValidateOddsBucksSave(
	const UObject* SaveObject,
	FOddsWellOddsBucksLedger& OutLedger,
	int64& OutNextJobPayoutUnixSeconds,
	TArray<FOddsWellMatchWinnerRequestRecord>& OutMatchWinnerRequests,
	TArray<FOddsWellMatchWinnerLockRecord>& OutMatchWinnerLocks,
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
	OutMatchWinnerLocks = Record->SchemaVersion >= OddsBucksSchemaVersion
		? Record->MatchWinnerLocks
		: TArray<FOddsWellMatchWinnerLockRecord>();
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
bool SaveOddsWellOddsBucksState(
	const FOddsWellOddsBucksLedger& Ledger,
	const int64 NextJobPayoutUnixSeconds,
	const TArray<FOddsWellMatchWinnerRequestRecord>& MatchWinnerRequests,
	const TArray<FOddsWellMatchWinnerLockRecord>& MatchWinnerLocks,
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
	FOddsWellOddsBucksLedger Validated;
	int64 ValidatedNextJobPayout = 0;
	TArray<FOddsWellMatchWinnerRequestRecord> ValidatedRequests;
	TArray<FOddsWellMatchWinnerLockRecord> ValidatedLocks;
	bool bNeedsMigration = false;
	if (!ValidateOddsBucksSave(Record, Validated, ValidatedNextJobPayout, ValidatedRequests, ValidatedLocks, bNeedsMigration, OutError))
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
		bOutNeedsMigration,
		OutError);
}
}

bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, const int64 NextJobPayoutUnixSeconds, const bool bQaSlot, FString& OutError)
{
	TArray<FOddsWellMatchWinnerRequestRecord> ExistingRequests;
	TArray<FOddsWellMatchWinnerLockRecord> ExistingLocks;
	if (UGameplayStatics::DoesSaveGameExist(GetOddsBucksSlot(bQaSlot), OddsBucksUserIndex))
	{
		FOddsWellOddsBucksLedger ExistingLedger;
		int64 ExistingNextJobPayout = 0;
		bool bFound = false;
		bool bNeedsMigration = false;
		if (!LoadOddsWellOddsBucksStateRaw(bQaSlot, ExistingLedger, ExistingNextJobPayout, ExistingRequests, ExistingLocks, bFound, bNeedsMigration, OutError))
		{
			return false;
		}
	}
	return SaveOddsWellOddsBucksState(Ledger, NextJobPayoutUnixSeconds, ExistingRequests, ExistingLocks, bQaSlot, OutError);
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
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		bOutFound,
		bNeedsMigration,
		OutError))
	{
		return false;
	}
	return !bNeedsMigration || SaveOddsWellOddsBucksState(
		OutLedger,
		OutNextJobPayoutUnixSeconds,
		OutMatchWinnerRequests,
		OutMatchWinnerLocks,
		bQaSlot,
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
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
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
	bool bFound = false;
	bool bNeedsMigration = false;
	if (!LoadOddsWellOddsBucksStateRaw(
		bQaSlot,
		Ledger,
		NextJobPayoutUnixSeconds,
		Requests,
		Locks,
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
		bQaSlot,
		OutError))
	{
		return EOddsWellMatchWinnerLockResult::Rejected;
	}
	OutRecord = MoveTemp(CandidateRecord);
	OutError.Reset();
	return EOddsWellMatchWinnerLockResult::Locked;
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
	OutError.Reset();
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS

namespace
{
FOddsWellMatchWinnerOffer MakeMatchWinnerTestOffer()
{
	FOddsWellMatchWinnerOffer Offer;
	Offer.OfferId = TEXT("9e6870420528e2a821591b763471c47f71b198c063cbdcbecd9ee180f9ea2459");
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
	bool bNeedsMigration = false;
	TestTrue(TEXT("Odds Bucks entries validate after a memory round trip"), ValidateOddsBucksSave(UGameplayStatics::LoadGameFromMemory(Bytes), MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, bNeedsMigration, Error));
	TestEqual(TEXT("Memory round trip preserves balance"), MemoryLedger.GetBalance(), int64{15});
	Record->SchemaVersion++;
	TestFalse(TEXT("An unsupported Odds Bucks schema is rejected"), ValidateOddsBucksSave(Record, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, bNeedsMigration, Error));
	TestFalse(TEXT("A wrong save type is rejected"), ValidateOddsBucksSave(NewObject<UStaticMesh>(), MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, bNeedsMigration, Error));

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
	TestTrue(TEXT("Migration rewrites schema v4"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
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
	TestTrue(TEXT("Schema v2 migration rewrites schema v4"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
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
	TestTrue(TEXT("Schema v3 migration rewrites schema v4"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);

	FOddsWellMatchWinnerLockRecord LockRecord;
	const FString RequestCommandId(TEXT("wager:match_winner:test-1"));
	const FString LockCommandId(TEXT("wager:match_winner:lock:test-1"));
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

	UOddsWellOddsBucksSaveGame* MalformedLockRecord = Cast<UOddsWellOddsBucksSaveGame>(UGameplayStatics::LoadGameFromSlot(OddsBucksQaSlot, OddsBucksUserIndex));
	TestTrue(TEXT("Saved lock record is available for corruption test"), MalformedLockRecord && MalformedLockRecord->MatchWinnerLocks.Num() == 1);
	if (MalformedLockRecord && MalformedLockRecord->MatchWinnerLocks.Num() == 1)
	{
		MalformedLockRecord->MatchWinnerLocks[0].GameNumber++;
		TestFalse(TEXT("Malformed persisted lock is rejected"), ValidateOddsBucksSave(MalformedLockRecord, MemoryLedger, MemoryNextJobPayout, MemoryRequests, MemoryLocks, bNeedsMigration, Error));
	}
	TestTrue(TEXT("Wager QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

#endif
