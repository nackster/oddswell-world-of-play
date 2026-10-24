#include "Career/OddsWellCatalog.h"

#include "OddsBucksLedger.h"

namespace
{
	FLinearColor Rgb(const uint8 R, const uint8 G, const uint8 B)
	{
		return FLinearColor::FromSRGBColor(FColor(R, G, B));
	}

	FOddsWellCatalogItem Apartment(const TCHAR* Id, const TCHAR* Name, const int32 Tier, const int64 Price)
	{
		FOddsWellCatalogItem Item;
		Item.Id = Id;
		Item.Kind = EOddsWellCatalogKind::Apartment;
		Item.Name = Name;
		Item.Tier = Tier;
		Item.Price = Price;
		return Item;
	}

	FOddsWellCatalogItem Clothing(const TCHAR* Id, const EOddsWellCatalogKind Kind, const TCHAR* Name, const int64 Price, const FLinearColor Color)
	{
		FOddsWellCatalogItem Item;
		Item.Id = Id;
		Item.Kind = Kind;
		Item.Name = Name;
		Item.Price = Price;
		Item.Color = Color;
		return Item;
	}

	FOddsWellCatalogItem Furniture(const TCHAR* Id, const TCHAR* Name, const int64 Price, const int32 Tier, const FVector2D Anchor, const float Yaw, TArray<FOddsWellFurniturePart> Parts)
	{
		FOddsWellCatalogItem Item;
		Item.Id = Id;
		Item.Kind = EOddsWellCatalogKind::Furniture;
		Item.Name = Name;
		Item.Price = Price;
		Item.Tier = Tier;
		Item.Anchor = Anchor;
		Item.Yaw = Yaw;
		Item.Color = Parts.Num() ? Parts[0].Color : FLinearColor::White;
		Item.Parts = MoveTemp(Parts);
		return Item;
	}

	TArray<FOddsWellCatalogItem> BuildCatalog()
	{
		const FLinearColor Oak = Rgb(150, 108, 70);
		const FLinearColor Walnut = Rgb(96, 64, 42);
		const FLinearColor Linen = Rgb(222, 214, 196);
		const FLinearColor Charcoal = Rgb(52, 54, 60);
		const FLinearColor Teal = Rgb(28, 132, 140);
		const FLinearColor Brass = Rgb(196, 160, 82);
		const FLinearColor Leaf = Rgb(64, 128, 70);
		TArray<FOddsWellCatalogItem> Items = {
			// Homes. Each tier needs the one before it; the Penthouse is the season goal.
			Apartment(TEXT("home_studio"), TEXT("Studio"), 0, 0),
			Apartment(TEXT("home_one_bedroom"), TEXT("One-bedroom"), 1, GetOddsWellOneBedroomUpgradePrice()),
			Apartment(TEXT("home_two_bedroom"), TEXT("Two-bedroom"), 2, 900),
			Apartment(TEXT("home_three_bedroom"), TEXT("Three-bedroom"), 3, 1400),
			Apartment(TEXT("home_four_bedroom"), TEXT("Four-bedroom"), 4, 2000),
			Apartment(TEXT("home_penthouse"), TEXT("Penthouse"), 5, 2800),

			// Tops.
			Clothing(TEXT("top_starter"), EOddsWellCatalogKind::Top, TEXT("Off-white Tee"), 0, Rgb(232, 228, 216)),
			Clothing(TEXT("top_signal_jacket"), EOddsWellCatalogKind::Top, TEXT("Signal Jacket"), GetOddsWellSignalJacketPrice(), Rgb(22, 128, 138)),
			Clothing(TEXT("top_navy"), EOddsWellCatalogKind::Top, TEXT("Navy Tee"), 40, Rgb(36, 50, 92)),
			Clothing(TEXT("top_black"), EOddsWellCatalogKind::Top, TEXT("Black Tee"), 40, Rgb(28, 28, 32)),
			Clothing(TEXT("top_forest"), EOddsWellCatalogKind::Top, TEXT("Forest Tee"), 70, Rgb(44, 92, 58)),
			Clothing(TEXT("top_lavender"), EOddsWellCatalogKind::Top, TEXT("Lavender Tee"), 70, Rgb(168, 146, 204)),
			Clothing(TEXT("top_red"), EOddsWellCatalogKind::Top, TEXT("Signal Red Tee"), 60, Rgb(184, 44, 48)),
			Clothing(TEXT("top_sundale_orange"), EOddsWellCatalogKind::Top, TEXT("Sundale Orange Tee"), 80, Rgb(232, 120, 40)),
			Clothing(TEXT("top_waves_jersey"), EOddsWellCatalogKind::Top, TEXT("Harbor City Waves Jersey"), 120, Rgb(30, 104, 196)),
			Clothing(TEXT("top_sol_jersey"), EOddsWellCatalogKind::Top, TEXT("Mesa Vista Sol Jersey"), 120, Rgb(236, 180, 40)),
			Clothing(TEXT("top_champion_gold"), EOddsWellCatalogKind::Top, TEXT("Champion Gold Tee"), 250, Rgb(212, 172, 60)),

			// Bottoms.
			Clothing(TEXT("bottom_starter"), EOddsWellCatalogKind::Bottom, TEXT("Stone Shorts"), 0, Rgb(200, 194, 178)),
			Clothing(TEXT("bottom_navy"), EOddsWellCatalogKind::Bottom, TEXT("Navy Shorts"), 30, Rgb(34, 46, 84)),
			Clothing(TEXT("bottom_black"), EOddsWellCatalogKind::Bottom, TEXT("Black Shorts"), 30, Rgb(30, 30, 34)),
			Clothing(TEXT("bottom_white"), EOddsWellCatalogKind::Bottom, TEXT("White Shorts"), 40, Rgb(240, 240, 236)),
			Clothing(TEXT("bottom_gray"), EOddsWellCatalogKind::Bottom, TEXT("Heather Gray Shorts"), 40, Rgb(140, 142, 146)),
			Clothing(TEXT("bottom_olive"), EOddsWellCatalogKind::Bottom, TEXT("Olive Shorts"), 50, Rgb(96, 102, 56)),
			Clothing(TEXT("bottom_red"), EOddsWellCatalogKind::Bottom, TEXT("Red Shorts"), 50, Rgb(160, 40, 44)),
			Clothing(TEXT("bottom_teal"), EOddsWellCatalogKind::Bottom, TEXT("Teal Shorts"), 60, Rgb(26, 120, 128)),
			Clothing(TEXT("bottom_denim"), EOddsWellCatalogKind::Bottom, TEXT("Denim Shorts"), 70, Rgb(70, 96, 140)),

			// Furniture: a few graybox boxes each. Offsets are from the item's anchor, sizes in cm.
			Furniture(TEXT("furniture_modular_chair"), TEXT("Modular Chair"), GetOddsWellModularChairPrice(), 0, FVector2D(0.78, 0.55), 180.0f, {
				{FVector(0, 0, 22), FVector(70, 70, 44), Rgb(110, 116, 124)},
				{FVector(-30, 0, 70), FVector(12, 70, 60), Teal}}),
			Furniture(TEXT("furniture_floor_lamp"), TEXT("Floor Lamp"), 40, 0, FVector2D(0.88, -0.85), 0.0f, {
				{FVector(0, 0, 4), FVector(36, 36, 8), Charcoal},
				{FVector(0, 0, 80), FVector(6, 6, 150), Charcoal},
				{FVector(0, 0, 160), FVector(40, 40, 30), Linen}}),
			Furniture(TEXT("furniture_rug"), TEXT("Woven Rug"), 50, 0, FVector2D(0.3, 0.05), 0.0f, {
				{FVector(0, 0, 1), FVector(220, 160, 2), Rgb(176, 84, 60)}}),
			Furniture(TEXT("furniture_plant"), TEXT("Fiddle-Leaf Plant"), 35, 0, FVector2D(0.9, 0.85), 0.0f, {
				{FVector(0, 0, 20), FVector(40, 40, 40), Rgb(190, 110, 70)},
				{FVector(0, 0, 90), FVector(60, 60, 100), Leaf}}),
			Furniture(TEXT("furniture_single_bed"), TEXT("Single Bed"), 120, 0, FVector2D(-0.72, -0.62), 0.0f, {
				{FVector(0, 0, 22), FVector(200, 100, 44), Oak},
				{FVector(0, 0, 50), FVector(190, 92, 14), Linen},
				{FVector(-92, 0, 70), FVector(12, 100, 70), Oak}}),
			Furniture(TEXT("furniture_bookshelf"), TEXT("Bookshelf"), 90, 0, FVector2D(-0.15, 0.9), 0.0f, {
				{FVector(0, 0, 90), FVector(120, 34, 180), Walnut},
				{FVector(0, -2, 60), FVector(110, 32, 30), Rgb(150, 60, 50)},
				{FVector(0, -2, 120), FVector(110, 32, 30), Rgb(60, 90, 140)}}),
			Furniture(TEXT("furniture_tv"), TEXT("TV and Stand"), 180, 0, FVector2D(0.3, -0.9), 0.0f, {
				{FVector(0, 0, 25), FVector(160, 44, 50), Walnut},
				{FVector(0, 0, 100), FVector(150, 8, 86), Charcoal}}),
			Furniture(TEXT("furniture_sofa"), TEXT("Two-Seat Sofa"), 220, 1, FVector2D(0.3, 0.6), 0.0f, {
				{FVector(0, 0, 22), FVector(190, 86, 44), Teal},
				{FVector(0, 34, 60), FVector(190, 18, 60), Teal},
				{FVector(-92, 0, 40), FVector(14, 86, 50), Teal},
				{FVector(92, 0, 40), FVector(14, 86, 50), Teal}}),
			Furniture(TEXT("furniture_coffee_table"), TEXT("Coffee Table"), 80, 1, FVector2D(0.32, 0.18), 0.0f, {
				{FVector(0, 0, 20), FVector(110, 60, 40), Oak}}),
			Furniture(TEXT("furniture_desk"), TEXT("Work Desk"), 150, 1, FVector2D(-0.75, 0.6), 0.0f, {
				{FVector(0, 0, 72), FVector(140, 70, 6), Oak},
				{FVector(-62, 0, 36), FVector(8, 64, 70), Charcoal},
				{FVector(62, 0, 36), FVector(8, 64, 70), Charcoal},
				{FVector(0, 20, 100), FVector(60, 4, 40), Charcoal}}),
			Furniture(TEXT("furniture_double_bed"), TEXT("Double Bed"), 300, 2, FVector2D(-0.7, -0.05), 0.0f, {
				{FVector(0, 0, 24), FVector(210, 160, 48), Walnut},
				{FVector(0, 0, 54), FVector(200, 152, 16), Linen},
				{FVector(-100, 0, 80), FVector(12, 160, 80), Walnut}}),
			Furniture(TEXT("furniture_dining"), TEXT("Dining Table"), 260, 2, FVector2D(0.65, -0.35), 0.0f, {
				{FVector(0, 0, 74), FVector(160, 90, 6), Oak},
				{FVector(0, 0, 37), FVector(20, 20, 72), Oak},
				{FVector(0, -70, 24), FVector(44, 44, 48), Charcoal},
				{FVector(0, 70, 24), FVector(44, 44, 48), Charcoal}}),
			Furniture(TEXT("furniture_arcade"), TEXT("Arcade Cabinet"), 350, 2, FVector2D(0.92, 0.2), 180.0f, {
				{FVector(0, 0, 85), FVector(70, 70, 170), Rgb(70, 40, 120)},
				{FVector(-36, 0, 120), FVector(4, 56, 44), Rgb(80, 220, 230)}}),
			Furniture(TEXT("furniture_trophy_case"), TEXT("Trophy Case"), 250, 3, FVector2D(-0.6, -0.92), 0.0f, {
				{FVector(0, 0, 90), FVector(140, 40, 180), Walnut},
				{FVector(-40, -4, 110), FVector(24, 24, 40), Brass},
				{FVector(40, -4, 110), FVector(24, 24, 40), Brass}}),
			Furniture(TEXT("furniture_aquarium"), TEXT("Aquarium"), 400, 3, FVector2D(-0.6, 0.9), 0.0f, {
				{FVector(0, 0, 40), FVector(160, 50, 80), Walnut},
				{FVector(0, 0, 115), FVector(150, 44, 70), Rgb(90, 170, 210)}}),
			Furniture(TEXT("furniture_piano"), TEXT("Upright Piano"), 600, 4, FVector2D(0.7, 0.9), 0.0f, {
				{FVector(0, 0, 65), FVector(150, 60, 130), Rgb(24, 22, 24)},
				{FVector(0, -40, 72), FVector(140, 30, 6), Linen}}),
		};
		return Items;
	}
}

const TArray<FOddsWellCatalogItem>& GetOddsWellCatalog()
{
	static const TArray<FOddsWellCatalogItem> Catalog = BuildCatalog();
	return Catalog;
}

const FOddsWellCatalogItem* FindOddsWellCatalogItem(const FName Id)
{
	return GetOddsWellCatalog().FindByPredicate([Id](const FOddsWellCatalogItem& Item) { return Item.Id == Id; });
}

TArray<const FOddsWellCatalogItem*> GetOddsWellCatalogItems(const EOddsWellCatalogKind Kind)
{
	TArray<const FOddsWellCatalogItem*> Items;
	for (const FOddsWellCatalogItem& Item : GetOddsWellCatalog())
	{
		if (Item.Kind == Kind)
		{
			Items.Add(&Item);
		}
	}
	return Items;
}

int32 GetOddsWellApartmentTierCount()
{
	return GetOddsWellCatalogItems(EOddsWellCatalogKind::Apartment).Num();
}

const FOddsWellCatalogItem& GetOddsWellApartmentTier(const int32 Tier)
{
	const TArray<const FOddsWellCatalogItem*> Tiers = GetOddsWellCatalogItems(EOddsWellCatalogKind::Apartment);
	return *Tiers[FMath::Clamp(Tier, 0, Tiers.Num() - 1)];
}

FOddsWellHomeLayout GetOddsWellHomeLayout(const int32 Tier)
{
	static const FOddsWellHomeLayout Layouts[] = {
		{FVector2D(400.0, 300.0), 300.0f, 0, false},
		{FVector2D(400.0, 300.0), 300.0f, 1, false},
		{FVector2D(520.0, 360.0), 300.0f, 2, false},
		{FVector2D(620.0, 420.0), 320.0f, 3, false},
		{FVector2D(720.0, 480.0), 320.0f, 4, false},
		{FVector2D(900.0, 560.0), 420.0f, 4, true},
	};
	return Layouts[FMath::Clamp(Tier, 0, static_cast<int32>(UE_ARRAY_COUNT(Layouts)) - 1)];
}

FName GetOddsWellStarterTopId() { return TEXT("top_starter"); }
FName GetOddsWellStarterBottomId() { return TEXT("bottom_starter"); }
FName GetOddsWellSignalJacketId() { return TEXT("top_signal_jacket"); }

const TArray<FOddsWellAchievement>& GetOddsWellAchievements()
{
	static const TArray<FOddsWellAchievement> Achievements = {
		{TEXT("first_shift"), TEXT("Clocked In"), TEXT("Work your first shift.")},
		{TEXT("first_bet"), TEXT("Ticket Holder"), TEXT("Place your first bet.")},
		{TEXT("first_win"), TEXT("Winner"), TEXT("Win a bet.")},
		{TEXT("watched_game"), TEXT("Courtside"), TEXT("Watch a game at the arena.")},
		{TEXT("first_night"), TEXT("Sweet Dreams"), TEXT("Sleep through your first night.")},
		{TEXT("promoted"), TEXT("Moving Up"), TEXT("Earn your first promotion.")},
		{TEXT("team_scout"), TEXT("Front Office"), TEXT("Become a Team scout.")},
		{TEXT("shifts_40"), TEXT("Workhorse"), TEXT("Work 40 shifts.")},
		{TEXT("all_markets"), TEXT("Spread Out"), TEXT("Bet in all five markets.")},
		{TEXT("long_shot"), TEXT("Long Shot"), TEXT("Win a bet at odds of 5.00 or longer.")},
		{TEXT("big_ticket"), TEXT("Big Ticket"), TEXT("Collect 500 Odds Bucks or more from one bet.")},
		{TEXT("hot_hand"), TEXT("Hot Hand"), TEXT("Win five bets in a row.")},
		{TEXT("bets_100"), TEXT("Regular"), TEXT("Place 100 bets.")},
		{TEXT("fresh_fit"), TEXT("Fresh Fit"), TEXT("Buy a piece of clothing.")},
		{TEXT("wardrobe"), TEXT("Wardrobe"), TEXT("Own ten pieces of clothing.")},
		{TEXT("make_it_home"), TEXT("Make It Home"), TEXT("Buy a piece of furniture.")},
		{TEXT("interior_designer"), TEXT("Interior Designer"), TEXT("Own ten pieces of furniture.")},
		{TEXT("one_bedroom"), TEXT("Room to Breathe"), TEXT("Move into a One-bedroom.")},
		{TEXT("four_bedroom"), TEXT("Room for Everyone"), TEXT("Move into a Four-bedroom.")},
		{TEXT("penthouse"), TEXT("Top of Sundale"), TEXT("Own the Penthouse - the season goal.")},
		{TEXT("full_season"), TEXT("Full Season"), TEXT("See a champion crowned.")},
		{TEXT("bankroll"), TEXT("Bankroll"), TEXT("Hold 3,000 Odds Bucks at once.")},
	};
	return Achievements;
}
