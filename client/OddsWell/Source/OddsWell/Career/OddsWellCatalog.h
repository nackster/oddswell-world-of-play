#pragma once

#include "CoreMinimal.h"

// The career's things to buy (D7): apartment tiers, furniture and clothing, plus the achievements.
// Prices are balanced against the job ladder so the Penthouse (the season goal) takes about 50-60
// in-game days, see client/tools/economy and the M3 report.

enum class EOddsWellCatalogKind : uint8 { Apartment, Furniture, Top, Bottom };

// One graybox box of a furniture item, in room-local centimetres from the item's anchor.
struct FOddsWellFurniturePart
{
	FVector Offset;
	FVector Size;
	FLinearColor Color;
};

struct FOddsWellCatalogItem
{
	FName Id;
	EOddsWellCatalogKind Kind = EOddsWellCatalogKind::Furniture;
	FString Name;
	int64 Price = 0;
	// Apartment: its tier (0 = Studio). Furniture: the tier needed before it fits.
	int32 Tier = 0;
	// Clothing colour, or the furniture item's main colour.
	FLinearColor Color = FLinearColor::White;
	// Furniture: where it stands, as a fraction of the home's half-extents (X: -1 back wall, +1 door wall).
	FVector2D Anchor = FVector2D::ZeroVector;
	float Yaw = 0.0f;
	TArray<FOddsWellFurniturePart> Parts;
};

ODDSWELL_API const TArray<FOddsWellCatalogItem>& GetOddsWellCatalog();
ODDSWELL_API const FOddsWellCatalogItem* FindOddsWellCatalogItem(FName Id);
ODDSWELL_API TArray<const FOddsWellCatalogItem*> GetOddsWellCatalogItems(EOddsWellCatalogKind Kind);
ODDSWELL_API int32 GetOddsWellApartmentTierCount();
ODDSWELL_API const FOddsWellCatalogItem& GetOddsWellApartmentTier(int32 Tier);

// Home layout for a tier: half-extents of the floor (cm), ceiling height and the bedroom partitions.
struct FOddsWellHomeLayout
{
	FVector2D HalfExtents;
	float Height = 300.0f;
	int32 Bedrooms = 0;
	bool bGlassWall = false;
};
ODDSWELL_API FOddsWellHomeLayout GetOddsWellHomeLayout(int32 Tier);

// Starter clothing every career owns.
ODDSWELL_API FName GetOddsWellStarterTopId();
ODDSWELL_API FName GetOddsWellStarterBottomId();
ODDSWELL_API FName GetOddsWellSignalJacketId();

struct FOddsWellAchievement
{
	FName Id;
	FString Name;
	FString Description;
};
ODDSWELL_API const TArray<FOddsWellAchievement>& GetOddsWellAchievements();
