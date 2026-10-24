#include "Career/OddsWellCharacterPreview.h"

#include "Camera/CameraComponent.h"
#include "Career/OddsWellMetaHuman.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GroomAsset.h"
#include "GroomComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
	constexpr float TurntableDegreesPerSecond = 14.0f;
}

AOddsWellCharacterPreview::AOddsWellCharacterPreview()
{
	PrimaryActorTick.bCanEverTick = true;
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
	Turntable = CreateDefaultSubobject<USceneComponent>(TEXT("Turntable"));
	Turntable->SetupAttachment(Root);

	Stand = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Stand"));
	Stand->SetupAttachment(Root);
	Stand->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
	Stand->SetRelativeLocation(FVector(0.0, 0.0, -6.0));
	Stand->SetRelativeScale3D(FVector(1.6, 1.6, 0.12));
	Stand->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	// Framed like a fashion shot: the whole figure, head to feet, in the right half of the screen
	// (the chooser cards cover the left half).
	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(Root);
	Camera->SetRelativeLocation(FVector(560.0, 118.0, 98.0));
	Camera->SetRelativeRotation(FRotator(-1.0, 180.0, 0.0));
	Camera->FieldOfView = 42.0f;

	// A soft backdrop instead of the void.
	Backdrop = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Backdrop"));
	Backdrop->SetupAttachment(Root);
	Backdrop->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
	Backdrop->SetRelativeLocation(FVector(-260.0, 0.0, 200.0));
	Backdrop->SetRelativeScale3D(FVector(0.1, 16.0, 8.0));
	Backdrop->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	KeyLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("KeyLight"));
	KeyLight->SetupAttachment(Root);
	KeyLight->SetRelativeLocation(FVector(220.0, -160.0, 240.0));
	KeyLight->SetIntensity(9000.0f);
	KeyLight->SetAttenuationRadius(900.0f);
	KeyLight->SetLightColor(FLinearColor(1.0f, 0.92f, 0.82f));

	FillLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("FillLight"));
	FillLight->SetupAttachment(Root);
	FillLight->SetRelativeLocation(FVector(200.0, 220.0, 150.0));
	FillLight->SetIntensity(3500.0f);
	FillLight->SetAttenuationRadius(900.0f);
	FillLight->SetLightColor(FLinearColor(0.70f, 0.85f, 1.0f));
}

void AOddsWellCharacterPreview::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	Turntable->AddLocalRotation(FRotator(0.0, TurntableDegreesPerSecond * DeltaSeconds, 0.0));
	// One diagnostic line per preset about its hair, a moment after it appears.
	ShownSeconds += DeltaSeconds;
	if (!bGroomsLogged && ShownSeconds > 2.0f)
	{
		bGroomsLogged = true;
		for (const UGroomComponent* Groom : Grooms)
		{
			if (Groom)
			{
				UE_LOG(LogTemp, Display, TEXT("ODDSWELL_METAHUMAN_GROOM|preset=%s|groom=%s|visible=%s|registered=%s|lod=%d|bounds=%s|parent=%s"),
					*ShownPreset.ToString(), Groom->GroomAsset ? *Groom->GroomAsset->GetName() : TEXT("none"),
					Groom->IsVisible() ? TEXT("true") : TEXT("false"), Groom->IsRegistered() ? TEXT("true") : TEXT("false"),
					Groom->GetDesiredSyncLOD(), *Groom->Bounds.BoxExtent.ToString(), Groom->GetAttachParent() ? *Groom->GetAttachParent()->GetName() : TEXT("none"));
			}
		}
	}
}

void AOddsWellCharacterPreview::BeginPlay()
{
	Super::BeginPlay();
	UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (UMaterialInstanceDynamic* Instance = Material ? UMaterialInstanceDynamic::Create(Material, this) : nullptr)
	{
		const FLinearColor Color = FLinearColor::FromSRGBColor(FColor(38, 58, 66));
		Instance->SetVectorParameterValue(TEXT("Color"), Color);
		Instance->SetVectorParameterValue(TEXT("BaseColor"), Color);
		Backdrop->SetMaterial(0, Instance);
	}
}

bool AOddsWellCharacterPreview::ShowPreset(const FName PresetId)
{
	if (PresetId == ShownPreset)
	{
		return Body != nullptr;
	}
	ShownPreset = PresetId;
	ShownSeconds = 0.0f;
	bGroomsLogged = false;
	return AssembleOddsWellMetaHuman(*this, *Turntable, FTransform(FRotator(0.0, -90.0, 0.0)), PresetId, Body, Face, Outfit, Grooms);
}
