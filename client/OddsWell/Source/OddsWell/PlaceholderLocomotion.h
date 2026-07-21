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

USTRUCT()
struct FOddsWellSharedCityAppearance
{
	GENERATED_BODY()

	UPROPERTY()
	FName PresetId;

	UPROPERTY()
	FName TopItemId;

	UPROPERTY()
	FName BottomItemId;

	UPROPERTY()
	bool bOwnerSubmitted = false;
};

class FOddsWellStarterOutfitState
{
public:
	bool Equip(FName ItemId, EOddsWellStarterEquipmentSlot Slot, FString& OutError);
	bool Unequip(EOddsWellStarterEquipmentSlot Slot, FString& OutError);
	bool ValidateComplete(FString& OutError) const;
	FName GetEquipped(EOddsWellStarterEquipmentSlot Slot) const;
	void Reset();

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
	virtual void PawnClientRestart() override;
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	void AssignSharedCityPlayerNumber(int32 PlayerNumber);
	int32 GetSharedCityPlayerNumber() const { return SharedCityPlayerNumber; }
	const FOddsWellSharedCityAppearance& GetSharedCityAppearance() const { return SharedCityAppearance; }
	bool HasValidSharedCityAppearance() const;
	bool HasSubmittedSharedCityAppearance() const { return SharedCityAppearance.bOwnerSubmitted; }

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
	void PollStudioInteraction();
	void RunStudioQa(float DeltaSeconds);
	void RunCameraOrbitQa(float DeltaSeconds);
	bool ApplySavedOrFallbackAppearance();
	bool ResolveLocalAppearance(FOddsWellResolvedCharacterAppearance& OutAppearance, FString& OutSource, FString& OutError) const;
	bool ApplyResolvedAppearance(const FOddsWellResolvedCharacterAppearance& Appearance, const FString& Source);
	bool ApplySharedCityAppearance(const FString& Source);
	void SubmitLocalSharedCityAppearance();
	void SetAuthoritativeSharedCityAppearance(FName PresetId, FName TopItemId, FName BottomItemId, bool bOwnerSubmitted, const FString& Source);
	void SyncOutfitComponents();
	void SyncSharedCityNameplate();
	void RunOutfitQa(float DeltaSeconds);
	void ReportOutfitError(const FString& Error) const;
	void ReportAppearanceError(const FString& Error) const;

	UFUNCTION()
	void OnRep_SharedCityPlayerNumber();

	UFUNCTION()
	void OnRep_SharedCityAppearance();

	UFUNCTION(Server, Reliable)
	void ServerSetSharedCityAppearance(FName PresetId, FName TopItemId, FName BottomItemId);

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

	UPROPERTY(ReplicatedUsing=OnRep_SharedCityAppearance)
	FOddsWellSharedCityAppearance SharedCityAppearance;

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
	int32 SharedCityQaTargetClients = 2;
	bool bSharedCityQa = false;
	bool bSharedCityCapacityQa = false;
	bool bSharedCityCapacityLogged = false;
	bool bSharedCityQaVisibleLogged = false;
	bool bSharedCityQaAppearanceLogged = false;
	bool bSharedCityAppearanceSubmitted = false;
	FVector StudioQaStartLocation = FVector::ZeroVector;
	float StudioQaElapsed = 0.0f;
	bool bStudioInteractionArmed = false;
	bool bStudioQa = false;
	bool bStudioQaInteriorStarted = false;
	FVector CameraOrbitQaStartLocation = FVector::ZeroVector;
	float CameraOrbitQaElapsed = 0.0f;
	float CameraOrbitQaPreviousYaw = 0.0f;
	float CameraOrbitQaSweep = 0.0f;
	bool bCameraOrbitQa = false;
	bool bCameraOrbitQaStarted = false;
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
	FOddsWellSharedCityAppearance SharedCityReconnectExpectedAppearance;
	double SharedCityQaExitAt = 0.0;
	int32 NextSharedCityPlayerNumber = 1;
	int32 SharedCityQaTargetClients = 2;
	int32 SharedCityReconnectExpectedPlayerNumber = 0;
	bool bSharedCityQa = false;
	bool bSharedCityQaStarted = false;
	bool bSharedCityQaPassed = false;
	bool bSharedCityReconnectQa = false;
	bool bSharedCityReconnectLeaveObserved = false;
	bool bSharedCityReconnectPassed = false;
	bool bSharedCityCapacityQa = false;
};

UCLASS()
class ODDSWELL_API AOddsWellStudioGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellStudioGameMode();
	virtual void BeginPlay() override;
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&) override;
};
