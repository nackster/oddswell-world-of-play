#include "OddsBucksLedger.h"

#include "Misc/AutomationTest.h"

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
	return true;
}

#endif
