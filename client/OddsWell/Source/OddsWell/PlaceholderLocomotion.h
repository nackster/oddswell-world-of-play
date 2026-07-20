#pragma once

#include "CoreMinimal.h"
#include "CharacterPresetCatalog.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "PlaceholderLocomotion.generated.h"

struct FOddsWellResolvedCharacterAppearance;

class UCameraComponent;
class UMaterialInstanceDynamic;
class USpringArmComponent;
class UStaticMeshComponent;
class UTextRenderComponent;

class FOddsWellStarterOutfitState
{
public:
	bool Equip(FName ItemId, EOddsWellStarterEquipmentSlot Slot, FString& OutError);
	bool Unequip(EOddsWellStarterEquipmentSlot Slot, FString& OutError);
	bool ValidateComplete(FString& OutError) const;
	FName GetEquipped(EOddsWellStarterEquipmentSlot Slot) const;

private:
	FName EquippedTop;
	FName EquippedBottom;
};

UCLASS()
class ODDSWELL_API AOddsWellPlaceholderCharacter final : public ACharacter
{
	GENERATED_BODY()

public:
	AOddsWellPlaceholderCharacter();
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void PossessedBy(AController* NewController) override;
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	void AssignSharedCityPlayerNumber(int32 PlayerNumber);
	int32 GetSharedCityPlayerNumber() const { return SharedCityPlayerNumber; }

protected:
	virtual void BeginPlay() override;

private:
	void MoveForward(float Value);
	void MoveRight(float Value);
	void PollKeyboardMovement();
	void LookYaw(float Value);
	void LookPitchMouse(float Value);
	void LookPitchController(float Value);
	void StartRun();
	void StopRun();
	void StartJump();
	void StopJump();
	void RunQa(float DeltaSeconds);
	void FinishQa(bool bPassed);
	void RunSundaleRouteQa(float DeltaSeconds);
	void FinishSundaleRouteQa(bool bPassed);
	void RunSharedCityQa(float DeltaSeconds);
	bool ApplySavedOrFallbackAppearance();
	void SyncOutfitComponents();
	void SyncSharedCityNameplate();
	void RunOutfitQa(float DeltaSeconds);
	void ReportOutfitError(const FString& Error) const;
	void ReportAppearanceError(const FString& Error) const;

	UFUNCTION()
	void OnRep_SharedCityPlayerNumber();

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> PrimitiveBody;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> PrimitiveHead;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> StarterOutfitTop;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> StarterOutfitBottom;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> StarterOutfitMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> PrimitiveSkinMaterial;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UTextRenderComponent> SharedCityNameplate;

	UPROPERTY(ReplicatedUsing=OnRep_SharedCityPlayerNumber)
	int32 SharedCityPlayerNumber = 0;

	FOddsWellStarterOutfitState StarterOutfitState;
	FVector QaStartLocation = FVector::ZeroVector;
	float QaElapsed = 0.0f;
	float QaMaxZ = 0.0f;
	float QaWalkPeak = 0.0f;
	float QaRunPeak = 0.0f;
	float QaStartYaw = 0.0f;
	double QaExitAt = 0.0;
	bool bQaEnabled = false;
	bool bQaStarted = false;
	bool bQaJumpIssued = false;
	bool bQaFinished = false;
	bool bQaAutoExit = false;
	float OutfitQaElapsed = 0.0f;
	int32 OutfitQaStage = 0;
	bool bOutfitQaEnabled = false;
	bool bAppearanceQa = false;
	bool bAppearanceQaCleanup = false;
	FVector SundaleRouteStart = FVector::ZeroVector;
	FVector SundalePreviousLocation = FVector::ZeroVector;
	float SundaleRouteElapsed = 0.0f;
	float SundaleSegmentElapsed = 0.0f;
	float SundaleTravelDistance = 0.0f;
	float SundaleMinZ = 0.0f;
	float SundaleMaxZ = 0.0f;
	int32 SundaleRouteIndex = 0;
	bool bSundaleRouteQa = false;
	bool bSundaleRouteRun = false;
	bool bSundaleRouteStarted = false;
	bool bSundaleRouteFinished = false;
	float SharedCityQaElapsed = 0.0f;
	double SharedCityQaExitAt = 0.0;
	bool bSharedCityQa = false;
	bool bSharedCityQaVisibleLogged = false;
};

UCLASS()
class ODDSWELL_API AOddsWellLocomotionGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellLocomotionGameMode();
	virtual void Tick(float DeltaSeconds) override;
	virtual void PostLogin(APlayerController* NewPlayer) override;
	virtual void Logout(AController* Exiting) override;
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&) override;

private:
	TMap<int32, FVector> SharedCityQaStartLocations;
	double SharedCityQaExitAt = 0.0;
	int32 NextSharedCityPlayerNumber = 1;
	bool bSharedCityQa = false;
	bool bSharedCityQaStarted = false;
	bool bSharedCityQaPassed = false;
};
