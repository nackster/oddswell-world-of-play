#include "PlaceholderLocomotion.h"

#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "CharacterPresetCatalog.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "HAL/PlatformMisc.h"
#include "InputCoreTypes.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogOddsWellLocomotion, Log, All);

namespace
{
constexpr float WalkSpeed = 260.0f;
constexpr float RunSpeed = 520.0f;
constexpr float JumpVelocity = 520.0f;
constexpr float CameraDistance = 420.0f;
constexpr float CameraPitchMin = -65.0f;
constexpr float CameraPitchMax = 65.0f;
constexpr float CameraYawMin = -180.0f;
constexpr float CameraYawMax = 180.0f;
constexpr float CapsuleRadius = 42.0f;
constexpr float CapsuleHalfHeight = 96.0f;
constexpr bool AllowCrouch = false;
constexpr bool AllowFlight = false;
constexpr bool AllowSwimming = false;
constexpr bool UseCameraCollision = true;
const FVector SafeSpawnLocation(0.0, 0.0, 220.0);
const FLinearColor StarterOffWhite(0.92f, 0.90f, 0.82f);
const FName TopComponentName(TEXT("StarterOutfitTop"));
const FName BottomComponentName(TEXT("StarterOutfitBottom"));

const FKey KeyForward = EKeys::W;
const FKey KeyBackward = EKeys::S;
const FKey KeyLeft = EKeys::A;
const FKey KeyRight = EKeys::D;
const FKey KeyMouseYaw = EKeys::MouseX;
const FKey KeyMousePitch = EKeys::MouseY;
const FKey KeyRun = EKeys::LeftShift;
const FKey KeyJump = EKeys::SpaceBar;
const FKey KeyControllerMoveX = EKeys::Gamepad_LeftX;
const FKey KeyControllerMoveY = EKeys::Gamepad_LeftY;
const FKey KeyControllerLookX = EKeys::Gamepad_RightX;
const FKey KeyControllerLookY = EKeys::Gamepad_RightY;
const FKey KeyControllerRun = EKeys::Gamepad_LeftThumbstick;
const FKey KeyControllerJump = EKeys::Gamepad_FaceButton_Bottom;

bool GetStarterEquipmentIds(FName& OutTop, FName& OutBottom, FString& OutError)
{
	if (!ValidateOddsWellCharacterPresets(OutError))
	{
		return false;
	}
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	if (Presets.IsEmpty() || Presets[0].EquippedItemIds.Num() != 2)
	{
		OutError = TEXT("The safe preset must contain one starter top and one starter bottom.");
		return false;
	}
	OutTop = Presets[0].EquippedItemIds[0];
	OutBottom = Presets[0].EquippedItemIds[1];
	OutError.Reset();
	return true;
}

bool ResolveStarterEquipmentSlot(const FName ItemId, EOddsWellStarterEquipmentSlot& OutSlot, FString& OutError)
{
	FName TopId;
	FName BottomId;
	if (!GetStarterEquipmentIds(TopId, BottomId, OutError))
	{
		return false;
	}
	if (ItemId == TopId)
	{
		OutSlot = EOddsWellStarterEquipmentSlot::Top;
		return true;
	}
	if (ItemId == BottomId)
	{
		OutSlot = EOddsWellStarterEquipmentSlot::Bottom;
		return true;
	}
	OutError = FString::Printf(TEXT("Unsupported starter equipment ID: %s"), *ItemId.ToString());
	return false;
}
}

bool FOddsWellStarterOutfitState::Equip(const FName ItemId, const EOddsWellStarterEquipmentSlot Slot, FString& OutError)
{
	EOddsWellStarterEquipmentSlot ResolvedSlot = EOddsWellStarterEquipmentSlot::Top;
	if (!ResolveStarterEquipmentSlot(ItemId, ResolvedSlot, OutError))
	{
		return false;
	}
	if (ResolvedSlot != Slot)
	{
		OutError = FString::Printf(TEXT("Starter equipment %s does not belong in the requested slot."), *ItemId.ToString());
		return false;
	}
	FName& Equipped = Slot == EOddsWellStarterEquipmentSlot::Top ? EquippedTop : EquippedBottom;
	if (!Equipped.IsNone())
	{
		OutError = TEXT("The requested starter equipment slot is already occupied.");
		return false;
	}
	Equipped = ItemId;
	OutError.Reset();
	return true;
}

bool FOddsWellStarterOutfitState::Unequip(const EOddsWellStarterEquipmentSlot Slot, FString& OutError)
{
	FName& Equipped = Slot == EOddsWellStarterEquipmentSlot::Top ? EquippedTop : EquippedBottom;
	if (Equipped.IsNone())
	{
		OutError = TEXT("The requested starter equipment slot is already empty.");
		return false;
	}
	Equipped = NAME_None;
	OutError.Reset();
	return true;
}

bool FOddsWellStarterOutfitState::ValidateComplete(FString& OutError) const
{
	FName TopId;
	FName BottomId;
	if (!GetStarterEquipmentIds(TopId, BottomId, OutError))
	{
		return false;
	}
	if (EquippedTop != TopId || EquippedBottom != BottomId)
	{
		OutError = TEXT("The starter outfit requires one valid top and one valid bottom.");
		return false;
	}
	OutError.Reset();
	return true;
}

FName FOddsWellStarterOutfitState::GetEquipped(const EOddsWellStarterEquipmentSlot Slot) const
{
	return Slot == EOddsWellStarterEquipmentSlot::Top ? EquippedTop : EquippedBottom;
}

AOddsWellPlaceholderCharacter::AOddsWellPlaceholderCharacter()
{
	PrimaryActorTick.bCanEverTick = true;
	GetCapsuleComponent()->InitCapsuleSize(CapsuleRadius, CapsuleHalfHeight);
	GetMesh()->SetHiddenInGame(true);
	GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	PrimitiveBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NeutralPrimitiveBody"));
	PrimitiveBody->SetupAttachment(GetCapsuleComponent());
	PrimitiveBody->SetStaticMesh(Cylinder);
	PrimitiveBody->SetRelativeLocation(FVector(0.0, 0.0, -20.0));
	PrimitiveBody->SetRelativeScale3D(FVector(0.46, 0.46, 1.28));
	PrimitiveBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	PrimitiveHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NeutralPrimitiveHead"));
	PrimitiveHead->SetupAttachment(GetCapsuleComponent());
	PrimitiveHead->SetStaticMesh(Cube);
	PrimitiveHead->SetRelativeLocation(FVector(0.0, 0.0, 65.0));
	PrimitiveHead->SetRelativeScale3D(FVector(0.55));
	PrimitiveHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	StarterOutfitTop = CreateDefaultSubobject<UStaticMeshComponent>(TopComponentName);
	StarterOutfitTop->SetupAttachment(GetCapsuleComponent());
	StarterOutfitTop->SetStaticMesh(Cube);
	StarterOutfitTop->SetRelativeLocation(FVector(0.0, 0.0, 5.0));
	StarterOutfitTop->SetRelativeScale3D(FVector(0.62, 0.50, 0.50));
	StarterOutfitTop->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	StarterOutfitTop->SetVisibility(false);

	StarterOutfitBottom = CreateDefaultSubobject<UStaticMeshComponent>(BottomComponentName);
	StarterOutfitBottom->SetupAttachment(GetCapsuleComponent());
	StarterOutfitBottom->SetStaticMesh(Cube);
	StarterOutfitBottom->SetRelativeLocation(FVector(0.0, 0.0, -52.0));
	StarterOutfitBottom->SetRelativeScale3D(FVector(0.56, 0.46, 0.48));
	StarterOutfitBottom->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	StarterOutfitBottom->SetVisibility(false);

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("ThirdPersonCameraBoom"));
	CameraBoom->SetupAttachment(GetCapsuleComponent());
	CameraBoom->SetRelativeLocation(FVector(0.0, 0.0, 65.0));
	CameraBoom->TargetArmLength = CameraDistance;
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bDoCollisionTest = UseCameraCollision;
	CameraBoom->ProbeChannel = ECC_Camera;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ThirdPersonFollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.0f, 500.0f, 0.0f);
	Movement->MaxWalkSpeed = WalkSpeed;
	Movement->JumpZVelocity = JumpVelocity;
	Movement->AirControl = 0.2f;
	Movement->NavAgentProps.bCanJump = true;
	Movement->NavAgentProps.bCanCrouch = AllowCrouch;
	Movement->NavAgentProps.bCanFly = AllowFlight;
	Movement->NavAgentProps.bCanSwim = AllowSwimming;
}

void AOddsWellPlaceholderCharacter::BeginPlay()
{
	Super::BeginPlay();
	bQaEnabled = FParse::Param(FCommandLine::Get(), TEXT("LocomotionQa"));
	bQaAutoExit = FParse::Param(FCommandLine::Get(), TEXT("LocomotionAutoExit"));
	bOutfitQaEnabled = FParse::Param(FCommandLine::Get(), TEXT("OutfitQa"));
	UMaterialInterface* BasicShapeMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (!BasicShapeMaterial)
	{
		ReportOutfitError(TEXT("The native starter outfit material could not be loaded."));
		bOutfitQaEnabled = false;
	}
	else
	{
		StarterOutfitMaterial = UMaterialInstanceDynamic::Create(BasicShapeMaterial, this);
		if (!StarterOutfitMaterial)
		{
			ReportOutfitError(TEXT("The native starter outfit material instance could not be created."));
			bOutfitQaEnabled = false;
		}
		else
		{
			StarterOutfitMaterial->SetVectorParameterValue(TEXT("Color"), StarterOffWhite);
			StarterOutfitTop->SetMaterial(0, StarterOutfitMaterial);
			StarterOutfitBottom->SetMaterial(0, StarterOutfitMaterial);
		}
	}
	if (!ApplySafeStarterOutfit())
	{
		bOutfitQaEnabled = false;
	}
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_LOCOMOTION_READY|spawn=%s|walk=%.0f|run=%.0f|jump=%.0f"), *SafeSpawnLocation.ToCompactString(), WalkSpeed, RunSpeed, JumpVelocity);
}

void AOddsWellPlaceholderCharacter::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);
	if (APlayerController* PlayerController = Cast<APlayerController>(NewController))
	{
		PlayerController->SetControlRotation(FRotator(-12.0f, 0.0f, 0.0f));
		if (PlayerController->PlayerCameraManager)
		{
			PlayerController->PlayerCameraManager->ViewPitchMin = CameraPitchMin;
			PlayerController->PlayerCameraManager->ViewPitchMax = CameraPitchMax;
			PlayerController->PlayerCameraManager->ViewYawMin = CameraYawMin;
			PlayerController->PlayerCameraManager->ViewYawMax = CameraYawMax;
		}
	}
}

void AOddsWellPlaceholderCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	PlayerInputComponent->BindAxisKey(KeyForward, this, &AOddsWellPlaceholderCharacter::MoveForward);
	PlayerInputComponent->BindAxisKey(KeyBackward, this, &AOddsWellPlaceholderCharacter::MoveBackward);
	PlayerInputComponent->BindAxisKey(KeyRight, this, &AOddsWellPlaceholderCharacter::MoveRight);
	PlayerInputComponent->BindAxisKey(KeyLeft, this, &AOddsWellPlaceholderCharacter::MoveLeft);
	PlayerInputComponent->BindAxisKey(KeyMouseYaw, this, &AOddsWellPlaceholderCharacter::LookYaw);
	PlayerInputComponent->BindAxisKey(KeyMousePitch, this, &AOddsWellPlaceholderCharacter::LookPitchMouse);
	PlayerInputComponent->BindKey(KeyRun, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartRun);
	PlayerInputComponent->BindKey(KeyRun, IE_Released, this, &AOddsWellPlaceholderCharacter::StopRun);
	PlayerInputComponent->BindKey(KeyJump, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartJump);
	PlayerInputComponent->BindKey(KeyJump, IE_Released, this, &AOddsWellPlaceholderCharacter::StopJump);

	PlayerInputComponent->BindAxisKey(KeyControllerMoveY, this, &AOddsWellPlaceholderCharacter::MoveForward);
	PlayerInputComponent->BindAxisKey(KeyControllerMoveX, this, &AOddsWellPlaceholderCharacter::MoveRight);
	PlayerInputComponent->BindAxisKey(KeyControllerLookX, this, &AOddsWellPlaceholderCharacter::LookYaw);
	PlayerInputComponent->BindAxisKey(KeyControllerLookY, this, &AOddsWellPlaceholderCharacter::LookPitchController);
	PlayerInputComponent->BindKey(KeyControllerRun, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartRun);
	PlayerInputComponent->BindKey(KeyControllerRun, IE_Released, this, &AOddsWellPlaceholderCharacter::StopRun);
	PlayerInputComponent->BindKey(KeyControllerJump, IE_Pressed, this, &AOddsWellPlaceholderCharacter::StartJump);
	PlayerInputComponent->BindKey(KeyControllerJump, IE_Released, this, &AOddsWellPlaceholderCharacter::StopJump);
}

void AOddsWellPlaceholderCharacter::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bQaEnabled)
	{
		RunQa(DeltaSeconds);
	}
	if (bOutfitQaEnabled)
	{
		RunOutfitQa(DeltaSeconds);
	}
	if (QaExitAt > 0.0 && FPlatformTime::Seconds() >= QaExitAt)
	{
		QaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::MoveForward(const float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
	}
}

void AOddsWellPlaceholderCharacter::MoveBackward(const float Value) { MoveForward(-Value); }

void AOddsWellPlaceholderCharacter::MoveRight(const float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
	}
}

void AOddsWellPlaceholderCharacter::MoveLeft(const float Value) { MoveRight(-Value); }
void AOddsWellPlaceholderCharacter::LookYaw(const float Value) { AddControllerYawInput(Value); }
void AOddsWellPlaceholderCharacter::LookPitchMouse(const float Value) { AddControllerPitchInput(-Value); }
void AOddsWellPlaceholderCharacter::LookPitchController(const float Value) { AddControllerPitchInput(Value); }
void AOddsWellPlaceholderCharacter::StartRun() { GetCharacterMovement()->MaxWalkSpeed = RunSpeed; }
void AOddsWellPlaceholderCharacter::StopRun() { GetCharacterMovement()->MaxWalkSpeed = WalkSpeed; }
void AOddsWellPlaceholderCharacter::StartJump() { Jump(); }
void AOddsWellPlaceholderCharacter::StopJump() { StopJumping(); }

bool AOddsWellPlaceholderCharacter::ApplySafeStarterOutfit()
{
	FString Error;
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	if (!ValidateOddsWellCharacterPresets(Error) || Presets.IsEmpty() || Presets[0].EquippedItemIds.Num() != 2)
	{
		ReportOutfitError(Error.IsEmpty() ? TEXT("No valid safe starter outfit is available.") : Error);
		return false;
	}
	if (!StarterOutfitState.Equip(Presets[0].EquippedItemIds[0], EOddsWellStarterEquipmentSlot::Top, Error)
		|| !StarterOutfitState.Equip(Presets[0].EquippedItemIds[1], EOddsWellStarterEquipmentSlot::Bottom, Error)
		|| !StarterOutfitState.ValidateComplete(Error))
	{
		ReportOutfitError(Error);
		return false;
	}
	SyncOutfitComponents();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_OUTFIT_READY|top=%s|slot=top|bottom=%s|slot=bottom|replaceable=true"),
		*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).ToString(),
		*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString());
	return true;
}

void AOddsWellPlaceholderCharacter::SyncOutfitComponents()
{
	StarterOutfitTop->SetVisibility(!StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).IsNone(), true);
	StarterOutfitBottom->SetVisibility(!StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).IsNone(), true);
}

void AOddsWellPlaceholderCharacter::RunOutfitQa(const float DeltaSeconds)
{
	OutfitQaElapsed += DeltaSeconds;
	FString Error;
	if (OutfitQaStage == 0 && OutfitQaElapsed >= 0.75f)
	{
		if (!StarterOutfitState.Unequip(EOddsWellStarterEquipmentSlot::Top, Error))
		{
			ReportOutfitError(Error);
			bOutfitQaEnabled = false;
			return;
		}
		SyncOutfitComponents();
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_OUTFIT_UNEQUIP|slot=top|top=none|bottom=%s|base_body=true"), *StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString());
		OutfitQaStage = 1;
	}
	else if (OutfitQaStage == 1 && OutfitQaElapsed >= 1.75f)
	{
		FName TopId;
		FName BottomId;
		if (!GetStarterEquipmentIds(TopId, BottomId, Error)
			|| !StarterOutfitState.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error)
			|| !StarterOutfitState.ValidateComplete(Error))
		{
			ReportOutfitError(Error);
			bOutfitQaEnabled = false;
			return;
		}
		SyncOutfitComponents();
		const bool bPassed = PrimitiveBody->IsVisible()
			&& StarterOutfitTop->IsVisible()
			&& StarterOutfitBottom->IsVisible()
			&& GetCharacterMovement()->MaxWalkSpeed == WalkSpeed
			&& RunSpeed == 520.0f
			&& GetCharacterMovement()->JumpZVelocity == JumpVelocity;
		const FString Evidence = FString::Printf(
			TEXT("ODDSWELL_OUTFIT_QA|result=%s|top=%s|bottom=%s|replaceable=true|base_body=%s|top_component=%s|top_visible=%s|bottom_component=%s|bottom_visible=%s|walk=%.0f|run=%.0f|jump=%.0f"),
			bPassed ? TEXT("PASS") : TEXT("FAIL"),
			*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).ToString(),
			*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString(),
			PrimitiveBody->IsVisible() ? TEXT("true") : TEXT("false"),
			*StarterOutfitTop->GetFName().ToString(),
			StarterOutfitTop->IsVisible() ? TEXT("true") : TEXT("false"),
			*StarterOutfitBottom->GetFName().ToString(),
			StarterOutfitBottom->IsVisible() ? TEXT("true") : TEXT("false"),
			WalkSpeed,
			RunSpeed,
			JumpVelocity);
		if (bPassed)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
		}
		bOutfitQaEnabled = false;
		OutfitQaStage = 2;
	}
}

void AOddsWellPlaceholderCharacter::ReportOutfitError(const FString& Error) const
{
	UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_OUTFIT_ERROR|%s"), *Error);
}

void AOddsWellPlaceholderCharacter::RunQa(const float DeltaSeconds)
{
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	if (!bQaStarted)
	{
		QaElapsed += DeltaSeconds;
		if (!Movement->IsMovingOnGround())
		{
			if (QaElapsed > 5.0f)
			{
				QaStartLocation = GetActorLocation();
				QaMaxZ = QaStartLocation.Z;
				FinishQa(false);
			}
			return;
		}
		bQaStarted = true;
		QaElapsed = 0.0f;
		QaStartLocation = GetActorLocation();
		QaMaxZ = QaStartLocation.Z;
		if (Controller)
		{
			Controller->SetControlRotation(FRotator(-12.0f, 0.0f, 0.0f));
		}
		QaStartYaw = Controller ? Controller->GetControlRotation().Yaw : 0.0f;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_LOCOMOTION_QA_START|location=%s|yaw=%.1f"), *QaStartLocation.ToCompactString(), QaStartYaw);
	}

	if (bQaFinished)
	{
		return;
	}
	QaElapsed += DeltaSeconds;
	QaMaxZ = FMath::Max(QaMaxZ, GetActorLocation().Z);
	const float HorizontalSpeed = GetVelocity().Size2D();
	if (QaElapsed < 1.5f)
	{
		StopRun();
		MoveForward(1.0f);
		QaWalkPeak = FMath::Max(QaWalkPeak, HorizontalSpeed);
	}
	else if (QaElapsed < 2.0f)
	{
		if (Controller)
		{
			FRotator View = Controller->GetControlRotation();
			View.Yaw += (QaStartYaw > 0.0f ? -70.0f : 70.0f) * DeltaSeconds;
			View.Pitch = FMath::Clamp(View.Pitch + 20.0f * DeltaSeconds, CameraPitchMin, CameraPitchMax);
			Controller->SetControlRotation(View);
		}
	}
	else if (QaElapsed < 3.5f)
	{
		StartRun();
		MoveForward(1.0f);
		QaRunPeak = FMath::Max(QaRunPeak, HorizontalSpeed);
	}
	else
	{
		StopRun();
		if (!bQaJumpIssued)
		{
			bQaJumpIssued = true;
			Jump();
		}
		if (!Movement->IsMovingOnGround())
		{
			MoveForward(1.0f);
		}
		else if (QaElapsed > 3.7f && QaMaxZ - QaStartLocation.Z > 50.0f)
		{
			const float YawDelta = Controller ? FMath::Abs(FMath::FindDeltaAngleDegrees(QaStartYaw, Controller->GetControlRotation().Yaw)) : 0.0f;
			const bool bFloorBlocking = Movement->CurrentFloor.bBlockingHit;
			const bool bPassed = FVector::Dist2D(QaStartLocation, GetActorLocation()) > 100.0f
				&& QaRunPeak > QaWalkPeak + 50.0f
				&& QaMaxZ - QaStartLocation.Z > 50.0f
				&& FMath::Abs(GetActorLocation().Z - QaStartLocation.Z) < 25.0f
				&& YawDelta > 10.0f
				&& bFloorBlocking
				&& FMath::IsNearlyEqual(Movement->MaxWalkSpeed, WalkSpeed);
			FinishQa(bPassed);
		}
	}

	if (QaElapsed > 8.0f && !bQaFinished)
	{
		FinishQa(false);
	}
}

void AOddsWellPlaceholderCharacter::FinishQa(const bool bPassed)
{
	bQaFinished = true;
	const float YawDelta = Controller ? FMath::Abs(FMath::FindDeltaAngleDegrees(QaStartYaw, Controller->GetControlRotation().Yaw)) : 0.0f;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_LOCOMOTION_QA|result=%s|start=%s|end=%s|walk_peak=%.1f|run_peak=%.1f|walk_limit=%.0f|run_limit=%.0f|max_jump=%.1f|landed=%s|floor_blocking=%s|yaw_delta=%.1f"),
		bPassed ? TEXT("PASS") : TEXT("FAIL"),
		*QaStartLocation.ToCompactString(),
		*GetActorLocation().ToCompactString(),
		QaWalkPeak,
		QaRunPeak,
		WalkSpeed,
		RunSpeed,
		QaMaxZ - QaStartLocation.Z,
		GetCharacterMovement()->IsMovingOnGround() ? TEXT("true") : TEXT("false"),
		GetCharacterMovement()->CurrentFloor.bBlockingHit ? TEXT("true") : TEXT("false"),
		YawDelta);
	if (bPassed)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	if (bQaAutoExit)
	{
		QaExitAt = FPlatformTime::Seconds() + 12.0;
	}
}

AOddsWellLocomotionGameMode::AOddsWellLocomotionGameMode()
{
	DefaultPawnClass = AOddsWellPlaceholderCharacter::StaticClass();
}

APawn* AOddsWellLocomotionGameMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&)
{
	FActorSpawnParameters Parameters;
	Parameters.Owner = NewPlayer;
	Parameters.ObjectFlags |= RF_Transient;
	Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	return GetWorld()->SpawnActor<AOddsWellPlaceholderCharacter>(SafeSpawnLocation, FRotator::ZeroRotator, Parameters);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellLocomotionDefaultsTest,
	"OddsWell.Character.LocomotionDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellLocomotionDefaultsTest::RunTest(const FString& Parameters)
{
	TestTrue(TEXT("Walk speed is positive"), WalkSpeed > 0.0f);
	TestTrue(TEXT("Held run is faster than walk"), RunSpeed > WalkSpeed);
	TestTrue(TEXT("Native jump has positive velocity"), JumpVelocity > 0.0f);
	TestTrue(TEXT("Trailing camera has positive distance"), CameraDistance > 0.0f);
	TestTrue(TEXT("Spring arm collision remains enabled"), UseCameraCollision);
	TestTrue(TEXT("Safe spawn starts above the capsule"), SafeSpawnLocation.Z > CapsuleHalfHeight && CapsuleRadius > 0.0f);
	TestTrue(TEXT("Camera pitch is bounded"), CameraPitchMin > -90.0f && CameraPitchMax < 90.0f && CameraPitchMin < CameraPitchMax);
	TestTrue(TEXT("Camera yaw is bounded"), CameraYawMin == -180.0f && CameraYawMax == 180.0f);

	const TArray<FKey> KeyboardMoveLookKeys = {KeyForward, KeyBackward, KeyLeft, KeyRight, KeyMouseYaw, KeyMousePitch};
	const TArray<FKey> ControllerMoveLookKeys = {KeyControllerMoveX, KeyControllerMoveY, KeyControllerLookX, KeyControllerLookY};
	TestEqual(TEXT("Keyboard and mouse movement/look routes are complete"), KeyboardMoveLookKeys.Num(), 6);
	TestEqual(TEXT("Controller movement/look routes are complete"), ControllerMoveLookKeys.Num(), 4);
	for (const FKey& Key : ControllerMoveLookKeys)
	{
		TestTrue(FString::Printf(TEXT("Controller axis %s is a gamepad route"), *Key.ToString()), Key.IsGamepadKey());
	}
	TestFalse(TEXT("Keyboard run route is not a gamepad key"), KeyRun.IsGamepadKey());
	TestFalse(TEXT("Keyboard jump route is not a gamepad key"), KeyJump.IsGamepadKey());
	TestTrue(TEXT("Controller run route is present"), KeyControllerRun.IsGamepadKey());
	TestTrue(TEXT("Controller jump route is present"), KeyControllerJump.IsGamepadKey());

	TestFalse(TEXT("Crouch is not supported"), AllowCrouch);
	TestFalse(TEXT("Flight is not supported"), AllowFlight);
	TestFalse(TEXT("Swimming is not supported"), AllowSwimming);
	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellStarterOutfitTest,
	"OddsWell.Character.StarterOutfit",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellStarterOutfitTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("Character preset catalog remains valid"), ValidateOddsWellCharacterPresets(Error));
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	TestEqual(TEXT("All eight presets remain available"), Presets.Num(), 8);
	if (Presets.Num() != 8)
	{
		return false;
	}
	for (const FOddsWellCharacterPreset& Preset : Presets)
	{
		TestEqual(TEXT("Every preset has exactly two equipment IDs"), Preset.EquippedItemIds.Num(), 2);
		if (Preset.EquippedItemIds.Num() != 2)
		{
			continue;
		}
		TestEqual(TEXT("Every preset top uses the exact approved ID"), Preset.EquippedItemIds[0], FName(TEXT("starter_offwhite_top")));
		TestEqual(TEXT("Every preset bottom uses the exact approved ID"), Preset.EquippedItemIds[1], FName(TEXT("starter_offwhite_bottom")));
		EOddsWellStarterEquipmentSlot TopSlot = EOddsWellStarterEquipmentSlot::Bottom;
		EOddsWellStarterEquipmentSlot BottomSlot = EOddsWellStarterEquipmentSlot::Top;
		TestTrue(TEXT("Catalog top resolves"), ResolveStarterEquipmentSlot(Preset.EquippedItemIds[0], TopSlot, Error));
		TestTrue(TEXT("Catalog bottom resolves"), ResolveStarterEquipmentSlot(Preset.EquippedItemIds[1], BottomSlot, Error));
		TestTrue(TEXT("Top maps only to Top"), TopSlot == EOddsWellStarterEquipmentSlot::Top);
		TestTrue(TEXT("Bottom maps only to Bottom"), BottomSlot == EOddsWellStarterEquipmentSlot::Bottom);
	}

	FOddsWellStarterOutfitState State;
	const FName TopId = Presets[0].EquippedItemIds[0];
	const FName BottomId = Presets[0].EquippedItemIds[1];
	TestFalse(TEXT("Unknown equipment is rejected"), State.Equip(FName(TEXT("unknown_item")), EOddsWellStarterEquipmentSlot::Top, Error));
	TestFalse(TEXT("Unknown equipment reports an error"), Error.IsEmpty());
	TestFalse(TEXT("Top cannot be applied to Bottom"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestFalse(TEXT("Wrong-slot application reports an error"), Error.IsEmpty());
	TestFalse(TEXT("Incomplete outfit is rejected"), State.ValidateComplete(Error));
	TestFalse(TEXT("Missing slot reports an error"), Error.IsEmpty());
	TestTrue(TEXT("Top equips in Top"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error));
	TestFalse(TEXT("Duplicate Top assignment is rejected"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error));
	TestFalse(TEXT("Duplicate slot reports an error"), Error.IsEmpty());
	TestTrue(TEXT("Bottom equips in Bottom"), State.Equip(BottomId, EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestTrue(TEXT("Complete outfit validates"), State.ValidateComplete(Error));
	TestTrue(TEXT("Top removes independently"), State.Unequip(EOddsWellStarterEquipmentSlot::Top, Error));
	TestEqual(TEXT("Bottom remains after Top removal"), State.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom), BottomId);
	TestTrue(TEXT("Top restores independently"), State.Equip(TopId, EOddsWellStarterEquipmentSlot::Top, Error));
	TestTrue(TEXT("Bottom removes independently"), State.Unequip(EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestEqual(TEXT("Top remains after Bottom removal"), State.GetEquipped(EOddsWellStarterEquipmentSlot::Top), TopId);
	TestTrue(TEXT("Bottom restores independently"), State.Equip(BottomId, EOddsWellStarterEquipmentSlot::Bottom, Error));
	TestTrue(TEXT("Restored outfit validates"), State.ValidateComplete(Error));
	TestTrue(TEXT("Top and Bottom component identities stay separate"), TopComponentName != BottomComponentName);
	TestEqual(TEXT("Walk calibration is unchanged"), WalkSpeed, 260.0f);
	TestEqual(TEXT("Run calibration is unchanged"), RunSpeed, 520.0f);
	TestEqual(TEXT("Jump calibration is unchanged"), JumpVelocity, 520.0f);
	return !HasAnyErrors();
}
#endif
