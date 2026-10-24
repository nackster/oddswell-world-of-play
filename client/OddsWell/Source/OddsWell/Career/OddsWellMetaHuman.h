#pragma once

#include "CoreMinimal.h"

class AActor;
class UGroomComponent;
class USceneComponent;
class USkeletalMeshComponent;

// Which built MetaHuman (DEC-038) represents each of the eight character presets.
ODDSWELL_API const TCHAR* GetOddsWellMetaHumanForPreset(FName PresetId);

// Builds (or rebuilds) a MetaHuman on Owner under AttachParent: the body runs the standard locomotion
// animation, the face and outfit follow the body, and the hair/brow/beard grooms attach to the face.
// Existing components passed in are reused. Returns false when the preset's MetaHuman is not available.
ODDSWELL_API bool AssembleOddsWellMetaHuman(
	AActor& Owner,
	USceneComponent& AttachParent,
	const FTransform& RelativeTransform,
	FName PresetId,
	TObjectPtr<USkeletalMeshComponent>& InOutBody,
	TObjectPtr<USkeletalMeshComponent>& InOutFace,
	TObjectPtr<USkeletalMeshComponent>& InOutOutfit,
	TArray<TObjectPtr<UGroomComponent>>& InOutGrooms);
