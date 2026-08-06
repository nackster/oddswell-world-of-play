#include "HousingTierCatalog.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

const TArray<FOddsWellHousingTier>& GetOddsWellHousingTiers()
{
	static const TArray<FOddsWellHousingTier> Tiers = {
		{TEXT("studio"), TEXT("Studio"), true, 0},
		{TEXT("one_bedroom"), TEXT("One-bedroom"), true, 500},
		{TEXT("two_bedroom"), TEXT("Two-bedroom"), false, 0},
		{TEXT("three_bedroom"), TEXT("Three-bedroom"), false, 0},
		{TEXT("four_bedroom"), TEXT("Four-bedroom"), false, 0},
		{TEXT("penthouse"), TEXT("Penthouse"), false, 0},
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
		if (Tier.bInteriorAvailable != (Index <= 1))
		{
			OutError = TEXT("Only the Studio and One-bedroom interiors may be available.");
			return false;
		}
		if (Tier.UpgradePrice != (Index == 1 ? 500 : 0))
		{
			OutError = TEXT("Only the One-bedroom may have the approved 500 Odds Bucks price.");
			return false;
		}
	}
	if (Tiers[0].Id != TEXT("studio") || Tiers[1].Id != TEXT("one_bedroom") || AvailableInteriors != 2)
	{
		OutError = TEXT("The Studio and One-bedroom must be the only built interiors.");
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

FString BuildOddsWellHousingProgressionText(const bool bOwnsStudio, const bool bOwnsOneBedroom)
{
	FString Text(TEXT("HOME PROGRESSION"));
	for (const FOddsWellHousingTier& Tier : GetOddsWellHousingTiers())
	{
		FString Status(TEXT("LOCKED / INTERIOR NOT BUILT"));
		if (Tier.Id == TEXT("studio"))
		{
			Status = bOwnsStudio ? TEXT("OWNED / AVAILABLE") : TEXT("AVAILABLE / NOT OWNED");
		}
		else if (Tier.Id == TEXT("one_bedroom"))
		{
			Status = bOwnsOneBedroom
				? TEXT("OWNED / AVAILABLE")
				: TEXT("AVAILABLE FOR 500 ODDS BUCKS / REQUIRES STUDIO");
		}
		Text += FString::Printf(
			TEXT("\n%s - %s"),
			*Tier.DisplayName,
			*Status);
	}
	Text += TEXT("\nLater-tier prices and requirements are not set");
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
	const FOddsWellHousingTier* OneBedroom = FindOddsWellHousingTier(TEXT("one_bedroom"));
	const FOddsWellHousingTier* Penthouse = FindOddsWellHousingTier(TEXT("penthouse"));
	TestTrue(TEXT("Studio is available"), Studio && Studio->bInteriorAvailable);
	TestTrue(TEXT("One-bedroom is built"), OneBedroom && OneBedroom->bInteriorAvailable);
	TestEqual(TEXT("One-bedroom price is approved"), OneBedroom ? OneBedroom->UpgradePrice : int64{-1}, int64{500});
	TestTrue(TEXT("Penthouse exists but remains unavailable"), Penthouse && !Penthouse->bInteriorAvailable);
	TestNull(TEXT("Unknown housing tiers are not invented"), FindOddsWellHousingTier(TEXT("mansion")));
	const FString ProgressionText = BuildOddsWellHousingProgressionText(true, false);
	TestTrue(TEXT("Progression text shows the owned Studio"), ProgressionText.Contains(TEXT("Studio - OWNED / AVAILABLE")));
	TestTrue(TEXT("Progression text shows the exact One-bedroom gate"), ProgressionText.Contains(TEXT("One-bedroom - AVAILABLE FOR 500 ODDS BUCKS / REQUIRES STUDIO")));
	for (int32 Index = 2; Index < ExpectedNames.Num(); ++Index)
	{
		TestTrue(
			FString::Printf(TEXT("%s is visibly locked and unbuilt"), *ExpectedNames[Index]),
			ProgressionText.Contains(ExpectedNames[Index] + TEXT(" - LOCKED / INTERIOR NOT BUILT")));
	}
	TestTrue(TEXT("Later unknown prices and requirements are disclosed"), ProgressionText.Contains(TEXT("Later-tier prices and requirements are not set")));
	const FString OwnedProgressionText = BuildOddsWellHousingProgressionText(true, true);
	TestTrue(TEXT("Owned progression shows the One-bedroom available"), OwnedProgressionText.Contains(TEXT("One-bedroom - OWNED / AVAILABLE")));
	return !HasAnyErrors();
}
#endif
