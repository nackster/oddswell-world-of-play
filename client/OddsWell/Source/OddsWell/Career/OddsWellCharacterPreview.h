#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OddsWellCharacterPreview.generated.h"

class UCameraComponent;
class UGroomComponent;
class UPointLightComponent;
class USkeletalMeshComponent;
class UStaticMeshComponent;

// Character-chooser stage: shows the selected preset's MetaHuman on a slowly turning stand.
UCLASS()
class ODDSWELL_API AOddsWellCharacterPreview final : public AActor
{
	GENERATED_BODY()

public:
	AOddsWellCharacterPreview();
	virtual void Tick(float DeltaSeconds) override;
	bool ShowPreset(FName PresetId);
	UCameraComponent* GetCamera() const { return Camera; }

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USceneComponent> Turntable;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Stand;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UCameraComponent> Camera;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UPointLightComponent> KeyLight;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UPointLightComponent> FillLight;

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> Body;

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> Face;

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> Outfit;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UGroomComponent>> Grooms;

	FName ShownPreset;
};
