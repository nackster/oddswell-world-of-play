#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "PlaceholderLocomotion.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;

UCLASS()
class ODDSWELL_API AOddsWellPlaceholderCharacter final : public ACharacter
{
	GENERATED_BODY()

public:
	AOddsWellPlaceholderCharacter();
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void PossessedBy(AController* NewController) override;

protected:
	virtual void BeginPlay() override;

private:
	void MoveForward(float Value);
	void MoveBackward(float Value);
	void MoveRight(float Value);
	void MoveLeft(float Value);
	void LookYaw(float Value);
	void LookPitchMouse(float Value);
	void LookPitchController(float Value);
	void StartRun();
	void StopRun();
	void StartJump();
	void StopJump();
	void RunQa(float DeltaSeconds);
	void FinishQa(bool bPassed);

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> PrimitiveBody;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> PrimitiveHead;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UCameraComponent> FollowCamera;

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
};

UCLASS()
class ODDSWELL_API AOddsWellLocomotionGameMode final : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOddsWellLocomotionGameMode();
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&) override;
};
