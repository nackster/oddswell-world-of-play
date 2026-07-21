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
constexpr int32 OddsBucksSchemaVersion = 1;
constexpr int32 OddsBucksUserIndex = 0;
constexpr int64 FirstJobPayout = 100;
const FString OddsBucksSlot(TEXT("OddsWellOddsBucks"));
const FString OddsBucksQaSlot(TEXT("OddsWellOddsBucksQA"));
const FString FirstJobCommandId(TEXT("job:placeholder_shift:first_payout:v1"));
const FName FirstJobReason(TEXT("placeholder_job_payout"));

const FString& GetOddsBucksSlot(const bool bQaSlot)
{
	return bQaSlot ? OddsBucksQaSlot : OddsBucksSlot;
}

bool ValidateOddsBucksSave(const UObject* SaveObject, FOddsWellOddsBucksLedger& OutLedger, FString& OutError)
{
	const UOddsWellOddsBucksSaveGame* Record = Cast<UOddsWellOddsBucksSaveGame>(SaveObject);
	if (!Record)
	{
		OutError = TEXT("The Odds Bucks save is not the expected object type.");
		return false;
	}
	if (Record->SchemaVersion != OddsBucksSchemaVersion)
	{
		OutError = FString::Printf(TEXT("Unsupported Odds Bucks schema version: %d"), Record->SchemaVersion);
		return false;
	}
	return OutLedger.Restore(Record->Entries, OutError);
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
		|| FParse::Param(FCommandLine::Get(), TEXT("JobPayoutQaVerify"));
}

bool SaveOddsWellOddsBucksLedger(const FOddsWellOddsBucksLedger& Ledger, const bool bQaSlot, FString& OutError)
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
	FOddsWellOddsBucksLedger Validated;
	if (!ValidateOddsBucksSave(Record, Validated, OutError))
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

bool LoadOddsWellOddsBucksLedger(const bool bQaSlot, FOddsWellOddsBucksLedger& OutLedger, bool& bOutFound, FString& OutError)
{
	const FString& Slot = GetOddsBucksSlot(bQaSlot);
	bOutFound = UGameplayStatics::DoesSaveGameExist(Slot, OddsBucksUserIndex);
	if (!bOutFound)
	{
		OutLedger = FOddsWellOddsBucksLedger();
		OutError.Reset();
		return true;
	}
	return ValidateOddsBucksSave(UGameplayStatics::LoadGameFromSlot(Slot, OddsBucksUserIndex), OutLedger, OutError);
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
	TArray<uint8> Bytes;
	TestTrue(TEXT("Odds Bucks entries serialize"), UGameplayStatics::SaveGameToMemory(Record, Bytes));
	FOddsWellOddsBucksLedger MemoryLedger;
	TestTrue(TEXT("Odds Bucks entries validate after a memory round trip"), ValidateOddsBucksSave(UGameplayStatics::LoadGameFromMemory(Bytes), MemoryLedger, Error));
	TestEqual(TEXT("Memory round trip preserves balance"), MemoryLedger.GetBalance(), int64{15});
	Record->SchemaVersion++;
	TestFalse(TEXT("An unsupported Odds Bucks schema is rejected"), ValidateOddsBucksSave(Record, MemoryLedger, Error));
	TestFalse(TEXT("A wrong save type is rejected"), ValidateOddsBucksSave(NewObject<UStaticMesh>(), MemoryLedger, Error));

	ResetOddsWellQaOddsBucksAndVerify(Error);
	FOddsWellOddsBucksLedger JobLedger;
	TestEqual(TEXT("Provisional first job payout applies"), JobLedger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()), EOddsWellOddsBucksAppendResult::Applied);
	TestTrue(TEXT("Provisional job payout saves to the bounded QA slot"), SaveOddsWellOddsBucksLedger(JobLedger, true, Error));
	FOddsWellOddsBucksLedger DiskLedger;
	bool bFound = false;
	TestTrue(TEXT("Provisional job payout reloads from the QA slot"), LoadOddsWellOddsBucksLedger(true, DiskLedger, bFound, Error));
	TestTrue(TEXT("QA payout save was found"), bFound);
	TestEqual(TEXT("Disk round trip preserves one command"), DiskLedger.GetEntries().Num(), 1);
	TestEqual(TEXT("Disk round trip preserves 100 balance"), DiskLedger.GetBalance(), int64{100});
	TestEqual(TEXT("Restored retry stays idempotent"), DiskLedger.Append(GetOddsWellFirstJobCommandId(), GetOddsWellFirstJobPayout(), GetOddsWellFirstJobReason()), EOddsWellOddsBucksAppendResult::Duplicate);
	TestTrue(TEXT("QA Odds Bucks cleanup succeeds"), ResetOddsWellQaOddsBucksAndVerify(Error));
	return !HasAnyErrors();
}

#endif
