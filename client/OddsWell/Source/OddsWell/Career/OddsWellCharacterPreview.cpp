#include "Career/OddsWellCharacterPreview.h"

#include "Camera/CameraComponent.h"
#include "Career/OddsWellMetaHuman.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GroomComponent.h"

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

	// Framed like a fashion shot: the whole figure on the right of the screen, cards on the left.
	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(Root);
	Camera->SetRelativeLocation(FVector(330.0, 95.0, 105.0));
	Camera->SetRelativeRotation(FRotator(-4.0, 180.0, 0.0));
	Camera->FieldOfView = 42.0f;

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
}

bool AOddsWellCharacterPreview::ShowPreset(const FName PresetId)
{
	if (PresetId == ShownPreset)
	{
		return Body != nullptr;
	}
	ShownPreset = PresetId;
	return AssembleOddsWellMetaHuman(*this, *Turntable, FTransform(FRotator(0.0, -90.0, 0.0)), PresetId, Body, Face, Outfit, Grooms);
}
