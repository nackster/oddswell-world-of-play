// Builds the career home in the Studio level from the player's apartment tier and owned furniture
// (graybox boxes; final interiors and separate bedroom walls are M4 work). Larger tiers grow around the
// spawn point at the room centre, bedrooms share a wing behind a partition with one doorway per bedroom,
// and the Penthouse gets a glass wall.
#include "Career/OddsWellHome.h"

#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/PointLight.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
	constexpr float WallThickness = 20.0f;
	constexpr float DoorwayWidth = 170.0f;
	constexpr float DoorwayHeight = 220.0f;

	struct FHomeBuilder
	{
		UWorld& World;
		UStaticMesh* Cube = nullptr;
		UMaterialInterface* Material = nullptr;
		int32 Boxes = 0;

		void Box(const FVector& Center, const FVector& Size, const FLinearColor& Color, const bool bCollide, const float Yaw = 0.0f, const FName Tag = NAME_None)
		{
			FActorSpawnParameters Parameters;
			Parameters.ObjectFlags |= RF_Transient;
			AStaticMeshActor* Actor = World.SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(),
				FTransform(FRotator(0.0, Yaw, 0.0), Center, Size / 100.0), Parameters);
			if (!Actor)
			{
				return;
			}
			Actor->SetMobility(EComponentMobility::Movable);
			UStaticMeshComponent* Mesh = Actor->GetStaticMeshComponent();
			Mesh->SetStaticMesh(Cube);
			Mesh->SetCollisionProfileName(bCollide ? TEXT("BlockAll") : TEXT("NoCollision"));
			if (UMaterialInstanceDynamic* Instance = Material ? UMaterialInstanceDynamic::Create(Material, Actor) : nullptr)
			{
				Instance->SetVectorParameterValue(TEXT("Color"), Color);
				Instance->SetVectorParameterValue(TEXT("BaseColor"), Color);
				Mesh->SetMaterial(0, Instance);
			}
			Actor->Tags.Add(TEXT("OddsWellCareerHome"));
			if (!Tag.IsNone())
			{
				Actor->Tags.Add(Tag);
			}
			++Boxes;
		}
	};
}

int32 BuildOddsWellCareerHome(UWorld& World, const int32 Tier, const TArray<FName>& Furniture, int32& OutFurniturePlaced)
{
	FHomeBuilder Builder{World};
	Builder.Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	Builder.Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	OutFurniturePlaced = 0;
	if (!Builder.Cube)
	{
		return 0;
	}
	const FOddsWellHomeLayout Layout = GetOddsWellHomeLayout(Tier);
	const double HX = Layout.HalfExtents.X;
	const double HY = Layout.HalfExtents.Y;
	const double H = Layout.Height;
	const FLinearColor Floor = FLinearColor::FromSRGBColor(FColor(150, 132, 112));
	const FLinearColor Wall = FLinearColor::FromSRGBColor(FColor(214, 208, 196));
	const FLinearColor Accent = FLinearColor::FromSRGBColor(FColor(64, 120, 128));
	const FLinearColor Glass = FLinearColor::FromSRGBColor(FColor(150, 196, 220));

	// Shell: floor, ceiling and four walls (the Penthouse's door-side wall is glass).
	Builder.Box(FVector(0, 0, -10), FVector(HX * 2, HY * 2, 20), Floor, true);
	Builder.Box(FVector(0, 0, H), FVector(HX * 2, HY * 2, 20), Wall, true);
	Builder.Box(FVector(-HX, 0, H * 0.5 - 5), FVector(WallThickness, HY * 2, H), Wall, true);
	Builder.Box(FVector(HX, 0, H * 0.5 - 5), FVector(WallThickness, HY * 2, H), Layout.bGlassWall ? Glass : Wall, true);
	Builder.Box(FVector(0, -HY, H * 0.5 - 5), FVector(HX * 2, WallThickness, H), Wall, true);
	Builder.Box(FVector(0, HY, H * 0.5 - 5), FVector(HX * 2, WallThickness, H), Wall, true);
	// A skirting stripe so the room reads as finished, and a feature strip on the back wall.
	Builder.Box(FVector(-HX + 12, 0, 8), FVector(4, HY * 2 - 20, 16), Accent, false);
	Builder.Box(FVector(-HX + 12, 0, H * 0.62), FVector(4, HY * 1.2, 30), Accent, false);

	// Bedrooms: a partition across the back of the home with one doorway per bedroom.
	if (Layout.Bedrooms > 0)
	{
		const double PartitionX = -0.375 * HX;
		const double Span = HY * 2.0 / Layout.Bedrooms;
		double Cursor = -HY;
		for (int32 Room = 0; Room < Layout.Bedrooms; ++Room)
		{
			const double DoorCenter = -HY + Span * (Room + 0.5);
			const double DoorStart = DoorCenter - DoorwayWidth * 0.5;
			if (DoorStart > Cursor)
			{
				Builder.Box(FVector(PartitionX, (Cursor + DoorStart) * 0.5, H * 0.5 - 5), FVector(WallThickness, DoorStart - Cursor, H), Wall, true);
			}
			Builder.Box(FVector(PartitionX, DoorCenter, (DoorwayHeight + H) * 0.5), FVector(WallThickness, DoorwayWidth, H - DoorwayHeight), Wall, true);
			Cursor = DoorCenter + DoorwayWidth * 0.5;
		}
		Builder.Box(FVector(PartitionX, (Cursor + HY) * 0.5, H * 0.5 - 5), FVector(WallThickness, HY - Cursor, H), Wall, true);
	}

	// Furniture at its anchor, scaled to this home's size.
	for (const FName Id : Furniture)
	{
		const FOddsWellCatalogItem* Item = FindOddsWellCatalogItem(Id);
		if (!Item || Item->Kind != EOddsWellCatalogKind::Furniture || Item->Tier > Tier)
		{
			continue;
		}
		const FVector Anchor(Item->Anchor.X * (HX - 20.0), Item->Anchor.Y * (HY - 20.0), 0.0);
		const FRotator Rotation(0.0, Item->Yaw, 0.0);
		for (const FOddsWellFurniturePart& Part : Item->Parts)
		{
			// Rugs stay walkable; everything else blocks like real furniture.
			Builder.Box(Anchor + Rotation.RotateVector(Part.Offset), Part.Size, Part.Color, Part.Size.Z > 4.0, Item->Yaw, Id);
		}
		++OutFurniturePlaced;
	}

	// Lights: one per bedroom wing and the living area, brighter in bigger homes.
	FActorSpawnParameters Parameters;
	Parameters.ObjectFlags |= RF_Transient;
	const TArray<FVector> Lights = Layout.Bedrooms > 0
		? TArray<FVector>{FVector(HX * 0.3, 0, H - 60), FVector(-HX * 0.7, 0, H - 60)}
		: TArray<FVector>{FVector(0, 0, H - 60)};
	for (const FVector& Location : Lights)
	{
		if (APointLight* Light = World.SpawnActor<APointLight>(Location, FRotator::ZeroRotator, Parameters))
		{
			Light->PointLightComponent->SetIntensity(5000.0f + 900.0f * Tier);
			Light->PointLightComponent->SetAttenuationRadius(FMath::Max(HX, HY) * 2.2f);
			Light->PointLightComponent->SetUseTemperature(true);
			Light->PointLightComponent->SetTemperature(3600.0f);
		}
	}
	return Builder.Boxes;
}
