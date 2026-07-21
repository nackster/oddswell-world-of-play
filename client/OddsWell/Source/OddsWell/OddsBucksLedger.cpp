#include "OddsBucksLedger.h"

#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Engine/StaticMesh.h"
#endif

namespace
{
constexpr int32 OddsBucksSchemaVersion = 2;
constexpr int32 OddsBucksUserIndex = 0;
constexpr int64 FirstJobPayout = 100;
constexpr int64 JobPayoutIntervalSeconds = 24 * 60 * 60;
const FString OddsBucksSlot(TEXT("OddsWellOddsBucks"));
const FString OddsBucksQaSlot(TEXT("OddsWellOddsBucksQA"));
const FString FirstJobCommandId(TEXT("job:placeholder_shift:first_payout:v1"));
const FName FirstJobReason(TEXT("placeholder_job_payout"));

const FString& GetOddsBucksSlot(const bool bQaSlot)
{
	return bQaSlot ? OddsBucksQaSlot : OddsBucksSlot;
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

bool ValidateOddsBucksSave(const UObject* SaveObject, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, bool& bOutNeedsMigration, FString& OutError)
{
	const UOddsWellOddsBucksSaveGame* Record = Cast<UOddsWellOddsBucksSaveGame>(SaveObject);
	if (!Record)
	{
		OutError = TEXT("The Odds Bucks save is not the expected object type.");
		return false;
	}
	if (Record->SchemaVersion != 1 && Record->SchemaVersion != OddsBucksSchemaVersion)
	{
		OutError = FString::Printf(TEXT("Unsupported Odds Bucks schema version: %d"), Record->SchemaVersion);
		return false;
	}
	if (!OutLedger.Restore(Record->Entries, OutError))
	{
		return false;
	}
	bOutNeedsMigration = Record->SchemaVersion == 1;
	OutNextJobPayoutUnixSeconds = bOutNeedsMigration && HasJobPayout(OutLedger)
		? FDateTime::UtcNow().ToUnixTimestamp() + JobPayoutIntervalSeconds
		: Record->NextJobPayoutUnixSeconds;
	if (OutNextJobPayoutUnixSeconds < 0
		|| (HasJobPayout(OutLedger) && OutNextJobPayoutUnixSeconds == 0)
		|| (!HasJobPayout(OutLedger) && OutNextJobPayoutUnixSeconds != 0))
	{
		OutError = TEXT("The Odds Bucks job payout schedule is inconsistent with its ledger.");
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

bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, const int64 NextJobPayoutUnixSeconds, const bool bQaSlot, FString& OutError)
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
	FOddsWellOddsBucksLedger Validated;
	int64 ValidatedNextJobPayout = 0;
	bool bNeedsMigration = false;
	if (!ValidateOddsBucksSave(Record, Validated, ValidatedNextJobPayout, bNeedsMigration, OutError))
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

bool LoadOddsWellOddsBucksLedger(const bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, int64& OutNextJobPayoutUnixSeconds, bool& bOutFound, FString& OutError)
{
	const FString& Slot = GetOddsBucksSlot(bQaSlot);
	bOutFound = UGameplayStatics::DoesSaveGameExist(Slot, OddsBucksUserIndex);
	if (!bOutFound)
	{
		OutLedger = FOddsWellOddsBucksLedger();
		OutNextJobPayoutUnixSeconds = 0;
		OutError.Reset();
		return true;
	}
	bool bNeedsMigration = false;
	if (!ValidateOddsBucksSave(UGameplayStatics::LoadGameFromSlot(Slot, OddsBucksUserIndex), OutLedger, OutNextJobPayoutUnixSeconds, bNeedsMigration, OutError))
	{
		return false;
	}
	return !bNeedsMigration || SaveOddsWellOddsBucksLedger(OutLedger, OutNextJobPayoutUnixSeconds, bQaSlot, OutError);
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
	OutError.Reset();
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS

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
	bool bNeedsMigration = false;
	TestTrue(TEXT("Odds Bucks entries validate after a memory round trip"), ValidateOddsBucksSave(UGameplayStatics::LoadGameFromMemory(Bytes), MemoryLedger, MemoryNextJobPayout, bNeedsMigration, Error));
	TestEqual(TEXT("Memory round trip preserves balance"), MemoryLedger.GetBalance(), int64{15});
	Record->SchemaVersion++;
	TestFalse(TEXT("An unsupported Odds Bucks schema is rejected"), ValidateOddsBucksSave(Record, MemoryLedger, MemoryNextJobPayout, bNeedsMigration, Error));
	TestFalse(TEXT("A wrong save type is rejected"), ValidateOddsBucksSave(NewObject<UStaticMesh>(), MemoryLedger, MemoryNextJobPayout, bNeedsMigration, Error));

	ResetOddsWellQaOddsBucksAndVerify(Error);
	FOddsWellOddsBucksLedger JobLedger;
	TestEqual(TEXT("Provisional first job payout applies"), JobLedger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()), EOddsWellOddsBucksAppendResult::Applied);
	const int64 ExpectedNextJobPayout = 2000000000 + GetOddsWellJobPayoutIntervalSeconds();
	TestTrue(TEXT("Provisional job payout saves to the bounded QA slot"), SaveOddsWellOddsBucksLedger(JobLedger, ExpectedNextJobPayout, true, Error));
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
	TestTrue(TEXT("Migration rewrites schema v2"), MigratedRecord && MigratedRecord->SchemaVersion == OddsBucksSchemaVersion);
	TestTrue(TEXT("Migrated QA cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

#endif
