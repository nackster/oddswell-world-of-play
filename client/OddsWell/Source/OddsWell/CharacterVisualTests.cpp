#if WITH_DEV_AUTOMATION_TESTS
#include "PlaceholderLocomotion.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "CharacterAppearanceSave.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FOddsWellSkeletalVisualTest,
	"OddsWell.Character.SkeletalVisualBridge",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellSkeletalVisualTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
	AOddsWellPlaceholderCharacter* Character = World->SpawnActor<AOddsWellPlaceholderCharacter>();
	if (!TestNotNull(TEXT("Character spawns"), Character))
	{
		World->DestroyWorld(false);
		return false;
	}
	USkeletalMeshComponent* Body = Character->GetMesh();
	TestTrue(TEXT("Required meshes and skeletal material load"), Character->InitializeCharacterMaterials());
	if (TestNotNull(TEXT("Accepted body is assigned"), Body->GetSkeletalMeshAsset()))
	{
		TestEqual(TEXT("Body is the accepted asset"), Body->GetSkeletalMeshAsset()->GetName(), FString(TEXT("SK_OddsWell_PlayerBody_v1")));
		TestEqual(TEXT("Body retains twelve bones"), Body->GetSkeletalMeshAsset()->GetRefSkeleton().GetNum(), 12);
		TestEqual(TEXT("Body stature is 180 cm"), Body->GetSkeletalMeshAsset()->GetBounds().BoxExtent.Z * 2.0, 180.0);
	}
	TestTrue(TEXT("Body is visible in game"), Body->IsVisible() && !Body->bHiddenInGame);
	TestTrue(TEXT("Visuals do not collide"), Body->GetCollisionEnabled() == ECollisionEnabled::NoCollision);
	TestEqual(TEXT("Capsule half-height stays 96 cm"), Character->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight(), 96.0f);
	TestEqual(TEXT("Capsule radius stays 42 cm"), Character->GetCapsuleComponent()->GetUnscaledCapsuleRadius(), 42.0f);
	TestTrue(TEXT("Mesh feet align with capsule bottom"), Body->GetRelativeLocation().Equals(FVector(0, 0, -96)));
	TestTrue(TEXT("Mesh forward aligns with movement"), Body->GetRelativeRotation().Equals(FRotator(0, -90, 0)));
	TestEqual(TEXT("Walk speed is unchanged"), Character->GetCharacterMovement()->MaxWalkSpeed, 260.0f);
	TestEqual(TEXT("Jump authority is unchanged"), Character->GetCharacterMovement()->JumpZVelocity, 520.0f);
	const FColor Tones[] = {FColor(246,218,194), FColor(210,160,120), FColor(145,96,68), FColor(82,52,38)};
	const auto& Presets = GetOddsWellCharacterPresets();
	TestEqual(TEXT("Eight presets remain"), Presets.Num(), 8);
	for (const auto& Preset : Presets)
	{
		FOddsWellResolvedCharacterAppearance Appearance;
		FString Error;
		TestTrue(TEXT("Preset and item IDs resolve"), ValidateOddsWellCharacterAppearanceIds(
			Preset.Id, Preset.EquippedItemIds[0], Preset.EquippedItemIds[1], Appearance, Error));
		TestTrue(TEXT("Resolved appearance reaches skeletal materials"), Character->ApplyResolvedAppearance(Appearance, TEXT("isolated_test")));
		TestTrue(TEXT("Skin matches exact preset color"), Character->PrimitiveSkinMaterial->K2_GetVectorParameterValue(TEXT("Color")).Equals(FLinearColor::FromSRGBColor(Preset.SkinTone)));
		TestTrue(TEXT("Preset uses an approved skin tone"), TArrayView<const FColor>(Tones).Contains(Preset.SkinTone));
		TestTrue(TEXT("Starter outfit is visible"), Character->StarterOutfitTop->IsVisible() && Character->StarterOutfitBottom->IsVisible());
		TestTrue(TEXT("Top follows body pose"), Character->StarterOutfitTop->LeaderPoseComponent.Get() == Body);
		TestTrue(TEXT("Bottom follows body pose"), Character->StarterOutfitBottom->LeaderPoseComponent.Get() == Body);
	}
	Character->SharedCityAppearance.bSignalJacketEquipped = true;
	Character->SyncOutfitComponents();
	TestTrue(TEXT("Jacket replaces top and shows teal slot"), Character->HasSignalJacketVisual());
	TestTrue(TEXT("Jacket keeps body skeleton"), Character->StarterOutfitTop->GetSkeletalMeshAsset()->GetSkeleton() == Body->GetSkeletalMeshAsset()->GetSkeleton());
	Character->SharedCityAppearance.bSignalJacketEquipped = false;
	Character->SyncOutfitComponents();
	TestTrue(TEXT("Starter top restores after jacket"), Character->StarterOutfitTop->GetSkeletalMeshAsset() == Character->StarterTopMesh);
	FString Error;
	Character->StarterOutfitState.Unequip(EOddsWellStarterEquipmentSlot::Top, Error);
	Character->SyncOutfitComponents();
	TestTrue(TEXT("Removing top preserves body and bottom"), !Character->StarterOutfitTop->IsVisible() && Body->IsVisible() && Character->StarterOutfitBottom->IsVisible());
	UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
	Movement->SetMovementMode(MOVE_Walking);
	Movement->Velocity = FVector::ZeroVector;
	Character->UpdateCharacterAnimation(0.016f);
	TestTrue(TEXT("Idle holds the neutral walk frame"), !Body->GetSingleNodeInstance()->IsPlaying());
	Body->TickAnimation(0.0f, false);
	Body->RefreshBoneTransforms();
	TestTrue(TEXT("Evaluated head remains at authored 166 cm"), FMath::IsNearlyEqual(
		Body->GetSocketTransform(TEXT("head"), RTS_Component).GetLocation().Z, 166.0, 0.1));
	TestTrue(TEXT("Animation root scale matches skeletal bind pose"),
		Body->GetSocketTransform(TEXT("root"), RTS_Component).GetScale3D().Equals(
			Body->GetSkeletalMeshAsset()->GetRefSkeleton().GetRefBonePose()[0].GetScale3D(), 0.001));
	const FVector NeutralKnee = Body->GetSocketTransform(TEXT("shin_L"), RTS_Component).GetLocation();
	Movement->Velocity = FVector(260, 0, 0);
	Character->UpdateCharacterAnimation(0.016f);
	TestTrue(TEXT("Actual walking velocity selects walk"), Body->GetSingleNodeInstance()->GetCurrentAsset() == Character->WalkAnimation);
	Body->SetPosition(Character->WalkAnimation->GetPlayLength() * 0.25f, false);
	Body->TickAnimation(0.0f, false);
	Body->RefreshBoneTransforms();
	TestTrue(TEXT("Walking swings the knee instead of only twisting the bone"), FVector::Dist(
		NeutralKnee, Body->GetSocketTransform(TEXT("shin_L"), RTS_Component).GetLocation()) > 10.0);
	Movement->Velocity = FVector(520, 0, 0);
	Character->UpdateCharacterAnimation(0.016f);
	TestTrue(TEXT("Actual running velocity selects run"), Body->GetSingleNodeInstance()->GetCurrentAsset() == Character->RunAnimation);
	TestTrue(TEXT("Walk to run preserves cycle phase"), FMath::IsNearlyEqual(Body->GetSingleNodeInstance()->GetCurrentTime(), Character->RunAnimation->GetPlayLength() * 0.25f));
	Movement->SetMovementMode(MOVE_Falling);
	Character->UpdateCharacterAnimation(0.016f);
	TestTrue(TEXT("Movement falling selects jump"), Body->GetSingleNodeInstance()->GetCurrentAsset() == Character->JumpAnimation);
	Movement->SetMovementMode(MOVE_Walking);
	Movement->Velocity = FVector::ZeroVector;
	Character->UpdateCharacterAnimation(0.016f);
	TestTrue(TEXT("Landing selects land once"), Body->GetSingleNodeInstance()->GetCurrentAsset() == Character->LandAnimation);
	Character->UpdateCharacterAnimation(0.5f);
	TestTrue(TEXT("Landing ends in stationary neutral pose"), Body->GetSingleNodeInstance()->GetCurrentAsset() == Character->WalkAnimation && !Body->GetSingleNodeInstance()->IsPlaying());
	TestTrue(TEXT("Visual animation never moves the capsule"), Movement->Velocity.IsNearlyZero());
	World->DestroyWorld(false);
	return !HasAnyErrors();
}
#endif
