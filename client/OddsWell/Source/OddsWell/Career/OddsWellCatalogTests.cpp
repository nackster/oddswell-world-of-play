#if WITH_DEV_AUTOMATION_TESTS
#include "Career/OddsWellCareer.h"
#include "Career/OddsWellCatalog.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCatalogTest,
	"OddsWell.Career.Catalog",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

namespace
{
	// Footprint of a furniture item in a home, as a 2D box.
	FBox2D Footprint(const FOddsWellCatalogItem& Item, const FOddsWellHomeLayout& Layout)
	{
		const FVector Anchor(Item.Anchor.X * (Layout.HalfExtents.X - 20.0), Item.Anchor.Y * (Layout.HalfExtents.Y - 20.0), 0.0);
		const FRotator Rotation(0.0, Item.Yaw, 0.0);
		FBox2D Box(ForceInit);
		for (const FOddsWellFurniturePart& Part : Item.Parts)
		{
			if (Part.Size.Z <= 4.0)
			{
				continue; // rugs are walkable
			}
			const FVector Center = Anchor + Rotation.RotateVector(Part.Offset);
			const FVector Half = Rotation.RotateVector(Part.Size * 0.5).GetAbs();
			Box += FVector2D(Center.X - Half.X, Center.Y - Half.Y);
			Box += FVector2D(Center.X + Half.X, Center.Y + Half.Y);
		}
		return Box;
	}
}

bool FOddsWellCatalogTest::RunTest(const FString& Parameters)
{
	TSet<FName> Ids;
	for (const FOddsWellCatalogItem& Item : GetOddsWellCatalog())
	{
		TestFalse(FString::Printf(TEXT("Catalog id %s is unique"), *Item.Id.ToString()), Ids.Contains(Item.Id));
		Ids.Add(Item.Id);
		TestTrue(TEXT("Prices are not negative"), Item.Price >= 0);
	}
	const TArray<const FOddsWellCatalogItem*> Homes = GetOddsWellCatalogItems(EOddsWellCatalogKind::Apartment);
	TestEqual(TEXT("All six apartment tiers are on sale"), Homes.Num(), 6);
	for (int32 Tier = 0; Tier < Homes.Num(); ++Tier)
	{
		TestEqual(TEXT("Tiers are in order"), Homes[Tier]->Tier, Tier);
		TestTrue(TEXT("Each home costs more than the last"), Tier == 0 || Homes[Tier]->Price > Homes[Tier - 1]->Price);
	}
	TestEqual(TEXT("The Penthouse is the last tier"), Homes.Last()->Name, FString(TEXT("Penthouse")));
	const int32 Clothes = GetOddsWellCatalogItems(EOddsWellCatalogKind::Top).Num() + GetOddsWellCatalogItems(EOddsWellCatalogKind::Bottom).Num();
	TestTrue(TEXT("About twenty clothing items"), Clothes >= 18 && Clothes <= 24);
	const TArray<const FOddsWellCatalogItem*> Furniture = GetOddsWellCatalogItems(EOddsWellCatalogKind::Furniture);
	TestTrue(TEXT("About fifteen furniture items"), Furniture.Num() >= 14 && Furniture.Num() <= 20);
	TestNotNull(TEXT("The Signal Jacket is a top"), FindOddsWellCatalogItem(GetOddsWellSignalJacketId()));
	TestTrue(TEXT("Starter clothes are free"), FindOddsWellCatalogItem(GetOddsWellStarterTopId())->Price == 0 && FindOddsWellCatalogItem(GetOddsWellStarterBottomId())->Price == 0);

	// Every tier fits all the furniture it allows without overlaps, walls, the partition or the spawn point.
	for (int32 Tier = 0; Tier < Homes.Num(); ++Tier)
	{
		const FOddsWellHomeLayout Layout = GetOddsWellHomeLayout(Tier);
		const FBox2D Room(FVector2D(-Layout.HalfExtents.X + 10.0, -Layout.HalfExtents.Y + 10.0), FVector2D(Layout.HalfExtents.X - 10.0, Layout.HalfExtents.Y - 10.0));
		const FBox2D Spawn(FVector2D(-60.0, -60.0), FVector2D(60.0, 60.0));
		const double PartitionX = -0.375 * Layout.HalfExtents.X;
		TArray<TPair<FName, FBox2D>> Placed;
		for (const FOddsWellCatalogItem* Item : Furniture)
		{
			if (Item->Tier > Tier)
			{
				continue;
			}
			const FBox2D Box = Footprint(*Item, Layout);
			if (!Box.bIsValid)
			{
				continue; // only walkable parts, like a rug
			}
			const FString Where = FString::Printf(TEXT("%s in tier %d"), *Item->Id.ToString(), Tier);
			TestTrue(Where + TEXT(" stays inside the walls"), Room.IsInside(Box.Min) && Room.IsInside(Box.Max));
			TestFalse(Where + TEXT(" leaves the spawn point clear"), Box.Intersect(Spawn));
			TestFalse(Where + TEXT(" does not cross the bedroom partition"), Layout.Bedrooms > 0 && Box.Min.X < PartitionX + 15.0 && Box.Max.X > PartitionX - 15.0);
			for (const TPair<FName, FBox2D>& Other : Placed)
			{
				TestFalse(Where + TEXT(" does not overlap ") + Other.Key.ToString(), Box.Intersect(Other.Value));
			}
			Placed.Add({Item->Id, Box});
		}
	}

	TSet<FName> AchievementIds;
	for (const FOddsWellAchievement& Achievement : GetOddsWellAchievements())
	{
		TestFalse(TEXT("Achievement ids are unique"), AchievementIds.Contains(Achievement.Id));
		AchievementIds.Add(Achievement.Id);
	}
	TestTrue(TEXT("15-25 achievements (D7)"), AchievementIds.Num() >= 15 && AchievementIds.Num() <= 25);
	TestEqual(TEXT("Four jobs (D7)"), GetOddsWellJobs().Num(), 4);
	for (int32 Level = 1; Level < GetOddsWellJobs().Num(); ++Level)
	{
		TestTrue(TEXT("Each job pays more and needs more shifts"), GetOddsWellJobs()[Level].Pay > GetOddsWellJobs()[Level - 1].Pay
			&& GetOddsWellJobs()[Level].ShiftsRequired > GetOddsWellJobs()[Level - 1].ShiftsRequired);
	}
	return true;
}
#endif
