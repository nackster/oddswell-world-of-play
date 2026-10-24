// Assembles the player's MetaHuman (DEC-038) on the existing character: the body runs the standard
// locomotion animation, the outfit follows the body, the face runs MetaHuman's face animation (which
// copies the body's pose, as in Epic's generated blueprint), and the grooms (hair, brows, beard) bind
// to the face. Movement, capsule, camera and saves are unchanged; the placeholder body and
// its clothing are hidden while a MetaHuman is shown.
#include "Career/OddsWellMetaHuman.h"

#include "AssetRegistry/AssetRegistryModule.h"
#include "Career/OddsWellCareer.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GroomBindingAsset.h"
#include "GroomComponent.h"
#include "PlaceholderLocomotion.h"

namespace
{
	FString MetaHumanBuiltPath(const TCHAR* Name, const FString& Relative)
	{
		return FString::Printf(TEXT("/Game/OddsWell/Characters/MetaHumans/%s/Built/MHC_%s/%s"), Name, Name, *Relative);
	}

	const TCHAR* LocomotionAnimClassPath = TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C");
	const TCHAR* FaceAnimClassPath = TEXT("/Game/OddsWell/Characters/MetaHumans/Common/Face/ABP_Face.ABP_Face_C");
}

const TCHAR* GetOddsWellMetaHumanForPreset(const FName PresetId)
{
	static const TMap<FName, const TCHAR*> Map = {
		{TEXT("masculine_tone_1"), TEXT("Kelvin")},
		{TEXT("masculine_tone_2"), TEXT("Lorenzo")},
		{TEXT("masculine_tone_3"), TEXT("Trey")},
		{TEXT("masculine_tone_4"), TEXT("Isaiah")},
		{TEXT("feminine_tone_1"), TEXT("Jelena")},
		{TEXT("feminine_tone_2"), TEXT("Grace")},
		{TEXT("feminine_tone_3"), TEXT("Sunita")},
		{TEXT("feminine_tone_4"), TEXT("Zuri")},
	};
	const TCHAR* const* Name = Map.Find(PresetId);
	return Name ? *Name : nullptr;
}

bool AssembleOddsWellMetaHuman(
	AActor& Owner,
	USceneComponent& AttachParent,
	const FTransform& RelativeTransform,
	const FName PresetId,
	TObjectPtr<USkeletalMeshComponent>& InOutBody,
	TObjectPtr<USkeletalMeshComponent>& InOutFace,
	TObjectPtr<USkeletalMeshComponent>& InOutOutfit,
	TArray<TObjectPtr<UGroomComponent>>& InOutGrooms)
{
	const TCHAR* Name = GetOddsWellMetaHumanForPreset(PresetId);
	if (!Name)
	{
		return false;
	}
	USkeletalMesh* BodyMesh = LoadObject<USkeletalMesh>(nullptr, *MetaHumanBuiltPath(Name, FString::Printf(TEXT("Body/SKM_MHC_%s_BodyMesh"), Name)));
	USkeletalMesh* FaceMesh = LoadObject<USkeletalMesh>(nullptr, *MetaHumanBuiltPath(Name, FString::Printf(TEXT("Face/SKM_MHC_%s_FaceMesh"), Name)));
	USkeletalMesh* OutfitMesh = LoadObject<USkeletalMesh>(nullptr, *MetaHumanBuiltPath(Name, FString::Printf(TEXT("Clothing/MHC_%s_Outfits"), Name)));
	UClass* LocomotionClass = LoadClass<UAnimInstance>(nullptr, LocomotionAnimClassPath);
	UClass* FaceClass = LoadClass<UAnimInstance>(nullptr, FaceAnimClassPath);
	if (!BodyMesh || !FaceMesh || !LocomotionClass || !FaceClass)
	{
		UE_LOG(LogTemp, Warning, TEXT("ODDSWELL_METAHUMAN|result=UNAVAILABLE|preset=%s|metahuman=%s|body=%s|face=%s|locomotion=%s"),
			*PresetId.ToString(), Name, BodyMesh ? TEXT("true") : TEXT("false"), FaceMesh ? TEXT("true") : TEXT("false"), LocomotionClass ? TEXT("true") : TEXT("false"));
		return false;
	}

	auto MakeMeshComponent = [&Owner](const TCHAR* ComponentName, USceneComponent* Parent) -> USkeletalMeshComponent*
	{
		USkeletalMeshComponent* Component = NewObject<USkeletalMeshComponent>(&Owner, ComponentName);
		Component->SetupAttachment(Parent);
		Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Component->SetGenerateOverlapEvents(false);
		Component->RegisterComponent();
		return Component;
	};
	if (!InOutBody)
	{
		InOutBody = MakeMeshComponent(TEXT("MetaHumanBody"), &AttachParent);
		InOutBody->SetRelativeTransform(RelativeTransform);
		InOutBody->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
		InOutFace = MakeMeshComponent(TEXT("MetaHumanFace"), InOutBody);
		InOutOutfit = MakeMeshComponent(TEXT("MetaHumanOutfit"), InOutBody);
	}
	InOutBody->SetSkeletalMesh(BodyMesh);
	InOutBody->SetAnimInstanceClass(LocomotionClass);
	InOutFace->SetSkeletalMesh(FaceMesh);
	InOutFace->SetAnimInstanceClass(FaceClass);
	// Hair binds to the face's skinned output, which MetaHumans take from the GPU skin cache.
	for (USkeletalMeshComponent* Mesh : {InOutBody.Get(), InOutFace.Get()})
	{
		Mesh->SkinCacheUsage.Init(ESkinCacheUsage::Enabled, Mesh->GetNumLODs());
		Mesh->MarkRenderStateDirty();
	}
	InOutOutfit->SetSkeletalMesh(OutfitMesh);
	InOutOutfit->SetLeaderPoseComponent(InOutBody, true);
	InOutOutfit->SetVisibility(OutfitMesh != nullptr);

	for (UGroomComponent* Groom : InOutGrooms)
	{
		if (Groom)
		{
			Groom->DestroyComponent();
		}
	}
	InOutGrooms.Reset();
	TArray<FAssetData> Assets;
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
	Registry.GetAssetsByPath(FName(*MetaHumanBuiltPath(Name, TEXT("Grooms"))), Assets, false);
	for (const FAssetData& Data : Assets)
	{
		UGroomBindingAsset* Binding = Data.IsInstanceOf(UGroomBindingAsset::StaticClass()) ? Cast<UGroomBindingAsset>(Data.GetAsset()) : nullptr;
		if (!Binding || !Binding->GetGroom())
		{
			continue;
		}
		UGroomComponent* Groom = NewObject<UGroomComponent>(&Owner);
		Groom->SetupAttachment(InOutFace);
		Groom->SetGroomAsset(Binding->GetGroom(), Binding);
		Groom->PrecachePSOs();
		Groom->RegisterComponent();
		InOutGrooms.Add(Groom);
	}
	UE_LOG(LogTemp, Display, TEXT("ODDSWELL_METAHUMAN|result=READY|owner=%s|preset=%s|metahuman=%s|outfit=%s|grooms=%d|locomotion=ABP_Unarmed"),
		*Owner.GetName(), *PresetId.ToString(), Name, OutfitMesh ? TEXT("true") : TEXT("false"), InOutGrooms.Num());
	return true;
}

bool AOddsWellPlaceholderCharacter::ApplyMetaHumanAppearance(const FName PresetId)
{
	if (!IsOddsWellCareerMode()
		|| !AssembleOddsWellMetaHuman(*this, *GetCapsuleComponent(), GetMesh()->GetRelativeTransform(), PresetId, MetaHumanBody, MetaHumanFace, MetaHumanOutfit, MetaHumanGrooms))
	{
		return false;
	}
	// The MetaHuman replaces the placeholder body and its clothing.
	GetMesh()->SetVisibility(false, true);
	bMetaHumanActive = true;
	SyncOutfitComponents();
	return true;
}
