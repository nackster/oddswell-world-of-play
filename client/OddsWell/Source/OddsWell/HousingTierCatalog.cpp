#include "HousingTierCatalog.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

const TArray<FOddsWellHousingTier>& GetOddsWellHousingTiers()
{
	static const TArray<FOddsWellHousingTier> Tiers = {
		{TEXT("studio"), TEXT("Studio"), true},
		{TEXT("one_bedroom"), TEXT("One-bedroom"), false},
		{TEXT("two_bedroom"), TEXT("Two-bedroom"), false},
		{TEXT("three_bedroom"), TEXT("Three-bedroom"), false},
		{TEXT("four_bedroom"), TEXT("Four-bedroom"), false},
		{TEXT("penthouse"), TEXT("Penthouse"), false},
	};
	return Tiers;
}

bool ValidateOddsWellHousingTiers(FString& OutError)
{
	const TArray<FOddsWellHousingTier>& Tiers = GetOddsWellHousingTiers();
	if (Tiers.Num() != 6)
	{
		OutError = TEXT("Expected exactly six housing tiers.");
		return false;
	}
	TSet<FName> Ids;
	int32 AvailableInteriors = 0;
	for (int32 Index = 0; Index < Tiers.Num(); ++Index)
	{
		const FOddsWellHousingTier& Tier = Tiers[Index];
		if (Tier.Id.IsNone() || Tier.DisplayName.IsEmpty() || Ids.Contains(Tier.Id))
		{
			OutError = TEXT("Housing tier IDs and names must be present and unique.");
			return false;
		}
		Ids.Add(Tier.Id);
		AvailableInteriors += Tier.bInteriorAvailable ? 1 : 0;
		if (Tier.bInteriorAvailable != (Index == 0))
		{
			OutError = TEXT("Only the first Studio interior may be available.");
			return false;
		}
	}
	if (Tiers[0].Id != TEXT("studio") || AvailableInteriors != 1)
	{
		OutError = TEXT("The Studio must be the sole available starting tier.");
		return false;
	}
	OutError.Reset();
	return true;
}

const FOddsWellHousingTier* FindOddsWellHousingTier(const FName TierId)
{
	return GetOddsWellHousingTiers().FindByPredicate(
		[TierId](const FOddsWellHousingTier& Tier) { return Tier.Id == TierId; });
}

FString BuildOddsWellHousingProgressionText(const bool bOwnsStudio)
{
	FString Text(TEXT("HOME PROGRESSION"));
	for (const FOddsWellHousingTier& Tier : GetOddsWellHousingTiers())
	{
		Text += FString::Printf(
			TEXT("\n%s - %s"),
			*Tier.DisplayName,
			Tier.bInteriorAvailable
				? (bOwnsStudio ? TEXT("OWNED / AVAILABLE") : TEXT("AVAILABLE / NOT OWNED"))
				: TEXT("LOCKED / INTERIOR NOT BUILT"));
	}
	Text += TEXT("\nPrices and requirements are not set");
	return Text;
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellHousingTierCatalogTest,
	"OddsWell.Character.HousingTierCatalog",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellHousingTierCatalogTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("The six-tier housing catalog is valid"), ValidateOddsWellHousingTiers(Error));
	const TArray<FOddsWellHousingTier>& Tiers = GetOddsWellHousingTiers();
	const TArray<FName> ExpectedIds = {
		TEXT("studio"), TEXT("one_bedroom"), TEXT("two_bedroom"),
		TEXT("three_bedroom"), TEXT("four_bedroom"), TEXT("penthouse")};
	const TArray<FString> ExpectedNames = {
		TEXT("Studio"), TEXT("One-bedroom"), TEXT("Two-bedroom"),
		TEXT("Three-bedroom"), TEXT("Four-bedroom"), TEXT("Penthouse")};
	for (int32 Index = 0; Index < Tiers.Num() && Index < ExpectedNames.Num(); ++Index)
	{
		TestEqual(FString::Printf(TEXT("Tier %d keeps its stable ID"), Index + 1), Tiers[Index].Id, ExpectedIds[Index]);
		TestEqual(FString::Printf(TEXT("Tier %d keeps its approved name"), Index + 1), Tiers[Index].DisplayName, ExpectedNames[Index]);
	}
	const FOddsWellHousingTier* Studio = FindOddsWellHousingTier(TEXT("studio"));
	const FOddsWellHousingTier* Penthouse = FindOddsWellHousingTier(TEXT("penthouse"));
	TestTrue(TEXT("Studio is available"), Studio && Studio->bInteriorAvailable);
	TestTrue(TEXT("Penthouse exists but remains unavailable"), Penthouse && !Penthouse->bInteriorAvailable);
	TestNull(TEXT("Unknown housing tiers are not invented"), FindOddsWellHousingTier(TEXT("mansion")));
	const FString ProgressionText = BuildOddsWellHousingProgressionText(true);
	TestTrue(TEXT("Progression text shows the owned Studio"), ProgressionText.Contains(TEXT("Studio - OWNED / AVAILABLE")));
	for (int32 Index = 1; Index < ExpectedNames.Num(); ++Index)
	{
		TestTrue(
			FString::Printf(TEXT("%s is visibly locked and unbuilt"), *ExpectedNames[Index]),
			ProgressionText.Contains(ExpectedNames[Index] + TEXT(" - LOCKED / INTERIOR NOT BUILT")));
	}
	TestTrue(TEXT("Unknown prices and requirements are disclosed"), ProgressionText.Contains(TEXT("Prices and requirements are not set")));
	TestFalse(TEXT("Progression text invents no Odds Bucks amount"), ProgressionText.Contains(TEXT("Odds Bucks")));
	return !HasAnyErrors();
}
#endif
