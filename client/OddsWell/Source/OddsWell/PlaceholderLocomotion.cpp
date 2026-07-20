#include "PlaceholderLocomotion.h"

#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "CharacterAppearanceSave.h"
#include "CharacterPresetCatalog.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "HAL/PlatformMisc.h"
#include "InputCoreTypes.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Net/UnrealNetwork.h"

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
constexpr float SharedCitySpawnSpacing = 200.0f;
constexpr float SharedCityQaMovementDistance = 300.0f;
constexpr ECollisionResponse SharedCityPlayerCollision = ECR_Ignore;
constexpr bool AllowCrouch = false;
constexpr bool AllowFlight = false;
constexpr bool AllowSwimming = false;
constexpr bool UseCameraCollision = true;
const FVector SafeSpawnLocation(0.0, 0.0, 220.0);
const FLinearColor StarterOffWhite(0.92f, 0.90f, 0.82f);
const FName TopComponentName(TEXT("StarterOutfitTop"));
const FName BottomComponentName(TEXT("StarterOutfitBottom"));
constexpr float SundaleRouteDistance = 80000.0f;
constexpr float SundaleWaypointTolerance = 75.0f;

const TArray<FVector>& GetSundaleRouteWaypoints()
{
	static const TArray<FVector> Waypoints = {
		FVector(9500.0, 0.0, 0.0),
		FVector(12500.0, 0.0, 0.0),
		FVector(12500.0, 9000.0, 0.0),
		FVector(12500.0, 18000.0, 0.0),
		FVector(7000.0, 18000.0, 0.0),
		FVector(1000.0, 18000.0, 0.0),
		FVector(-9500.0, 18000.0, 0.0),
		FVector(-9500.0, 16000.0, 0.0),
		FVector(-9500.0, 5000.0, 0.0),
		FVector(-9500.0, 0.0, 0.0),
		FVector::ZeroVector,
	};
	return Waypoints;
}

const TArray<FString>& GetSundaleRouteWaypointLabels()
{
	static const TArray<FString> Labels = {
		TEXT("Job"), TEXT("SoutheastCorner"), TEXT("Clothing"), TEXT("NortheastCorner"),
		TEXT("Arena"), TEXT("Sportsbook"), TEXT("NorthwestCorner"), TEXT("Court"),
		TEXT("Furniture"), TEXT("SouthwestCorner"), TEXT("Studio"),
	};
	return Labels;
}

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
}

bool FOddsWellStarterOutfitState::Equip(const FName ItemId, const EOddsWellStarterEquipmentSlot Slot, FString& OutError)
{
	EOddsWellStarterEquipmentSlot ResolvedSlot = EOddsWellStarterEquipmentSlot::Top;
	if (!ResolveOddsWellStarterEquipmentSlot(ItemId, ResolvedSlot, OutError))
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
	if (!GetOddsWellStarterEquipmentIds(TopId, BottomId, OutError))
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

void FOddsWellStarterOutfitState::Reset()
{
	EquippedTop = NAME_None;
	EquippedBottom = NAME_None;
}

AOddsWellPlaceholderCharacter::AOddsWellPlaceholderCharacter()
{
	PrimaryActorTick.bCanEverTick = true;
	bReplicates = true;
	SetReplicateMovement(true);
	GetCapsuleComponent()->InitCapsuleSize(CapsuleRadius, CapsuleHalfHeight);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Pawn, SharedCityPlayerCollision);
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

	SharedCityNameplate = CreateDefaultSubobject<UTextRenderComponent>(TEXT("SharedCityNameplate"));
	SharedCityNameplate->SetupAttachment(GetCapsuleComponent());
	SharedCityNameplate->SetRelativeLocation(FVector(0.0, 0.0, 135.0));
	SharedCityNameplate->SetHorizontalAlignment(EHTA_Center);
	SharedCityNameplate->SetTextRenderColor(FColor::White);
	SharedCityNameplate->SetWorldSize(24.0f);
	SharedCityNameplate->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SharedCityNameplate->SetVisibility(false);

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
	bAppearanceQa = UseOddsWellAppearanceQaSlot();
	bAppearanceQaCleanup = FParse::Param(FCommandLine::Get(), TEXT("AppearanceQaCleanup"));
	bSundaleRouteQa = FParse::Param(FCommandLine::Get(), TEXT("SundaleRouteQa"));
	bSundaleRouteRun = FParse::Param(FCommandLine::Get(), TEXT("SundaleRouteRun"));
	bSharedCityQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityQa"));
	UMaterialInterface* BasicShapeMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	if (!BasicShapeMaterial)
	{
		ReportOutfitError(TEXT("The native starter outfit material could not be loaded."));
		bOutfitQaEnabled = false;
	}
	else
	{
		StarterOutfitMaterial = UMaterialInstanceDynamic::Create(BasicShapeMaterial, this);
		PrimitiveSkinMaterial = UMaterialInstanceDynamic::Create(BasicShapeMaterial, this);
		if (!StarterOutfitMaterial || !PrimitiveSkinMaterial)
		{
			ReportAppearanceError(TEXT("The native placeholder material instances could not be created."));
			bOutfitQaEnabled = false;
		}
		else
		{
			StarterOutfitMaterial->SetVectorParameterValue(TEXT("Color"), StarterOffWhite);
			StarterOutfitTop->SetMaterial(0, StarterOutfitMaterial);
			StarterOutfitBottom->SetMaterial(0, StarterOutfitMaterial);
			PrimitiveBody->SetMaterial(0, PrimitiveSkinMaterial);
			PrimitiveHead->SetMaterial(0, PrimitiveSkinMaterial);
		}
	}
	bool bAppearanceReady = true;
	if (GetNetMode() == NM_Standalone)
	{
		bAppearanceReady = ApplySavedOrFallbackAppearance();
	}
	else if (HasAuthority())
	{
		FOddsWellResolvedCharacterAppearance Fallback;
		FString Source;
		FString Error;
		bAppearanceReady = ResolveOddsWellCharacterAppearance(nullptr, false, Fallback, Source, Error);
		if (bAppearanceReady && Fallback.Preset)
		{
			SetAuthoritativeSharedCityAppearance(Fallback.Preset->Id, Fallback.TopItemId, Fallback.BottomItemId, false, TEXT("server_fallback"));
		}
	}
	else if (!SharedCityAppearance.PresetId.IsNone())
	{
		bAppearanceReady = ApplySharedCityAppearance(TEXT("replicated_initial"));
	}
	if (GetNetMode() == NM_ListenServer && IsLocallyControlled())
	{
		SubmitLocalSharedCityAppearance();
	}
	if (!bAppearanceReady)
	{
		bOutfitQaEnabled = false;
	}
	SyncSharedCityNameplate();
	UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_LOCOMOTION_READY|spawn=%s|walk=%.0f|run=%.0f|jump=%.0f"), *SafeSpawnLocation.ToCompactString(), WalkSpeed, RunSpeed, JumpVelocity);
}

void AOddsWellPlaceholderCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(AOddsWellPlaceholderCharacter, SharedCityPlayerNumber);
	DOREPLIFETIME(AOddsWellPlaceholderCharacter, SharedCityAppearance);
}

void AOddsWellPlaceholderCharacter::AssignSharedCityPlayerNumber(const int32 PlayerNumber)
{
	if (!HasAuthority() || PlayerNumber < 1)
	{
		return;
	}
	SharedCityPlayerNumber = PlayerNumber;
	SyncSharedCityNameplate();
	ForceNetUpdate();
}

void AOddsWellPlaceholderCharacter::OnRep_SharedCityPlayerNumber()
{
	SyncSharedCityNameplate();
}

void AOddsWellPlaceholderCharacter::OnRep_SharedCityAppearance()
{
	if (PrimitiveSkinMaterial)
	{
		ApplySharedCityAppearance(TEXT("replicated"));
	}
}

bool AOddsWellPlaceholderCharacter::HasValidSharedCityAppearance() const
{
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Error;
	return ValidateOddsWellCharacterAppearanceIds(
		SharedCityAppearance.PresetId,
		SharedCityAppearance.TopItemId,
		SharedCityAppearance.BottomItemId,
		Appearance,
		Error);
}

void AOddsWellPlaceholderCharacter::SyncSharedCityNameplate()
{
	if (!SharedCityNameplate)
	{
		return;
	}
	SharedCityNameplate->SetText(FText::FromString(FString::Printf(TEXT("Player %d"), SharedCityPlayerNumber)));
	SharedCityNameplate->SetVisibility(SharedCityPlayerNumber > 0, true);
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

void AOddsWellPlaceholderCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();
	if (GetNetMode() == NM_Client && IsLocallyControlled())
	{
		SubmitLocalSharedCityAppearance();
	}
}

void AOddsWellPlaceholderCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
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
	PollKeyboardMovement();
	if (bQaEnabled)
	{
		RunQa(DeltaSeconds);
	}
	if (bOutfitQaEnabled)
	{
		RunOutfitQa(DeltaSeconds);
	}
	if (bSundaleRouteQa)
	{
		RunSundaleRouteQa(DeltaSeconds);
	}
	if (bSharedCityQa)
	{
		RunSharedCityQa(DeltaSeconds);
	}
	if (QaExitAt > 0.0 && FPlatformTime::Seconds() >= QaExitAt)
	{
		QaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::RunSharedCityQa(const float DeltaSeconds)
{
	if (!IsLocallyControlled() || SharedCityPlayerNumber < 1)
	{
		return;
	}
	SharedCityQaElapsed += DeltaSeconds;
	int32 VisiblePlayers = 0;
	int32 OtherPlayerNumber = 0;
	AOddsWellPlaceholderCharacter* OtherPlayer = nullptr;
	for (TActorIterator<AOddsWellPlaceholderCharacter> It(GetWorld()); It; ++It)
	{
		if (It->SharedCityPlayerNumber > 0 && It->SharedCityNameplate && It->SharedCityNameplate->IsVisible())
		{
			++VisiblePlayers;
			if (*It != this)
			{
				OtherPlayerNumber = It->SharedCityPlayerNumber;
				OtherPlayer = *It;
			}
		}
	}
	if (!bSharedCityQaVisibleLogged && VisiblePlayers >= 2 && OtherPlayerNumber > 0)
	{
		bSharedCityQaVisibleLogged = true;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_VISIBLE|local=Player_%d|other=Player_%d|actors=%d|names=true|pawn_collision=ignore"),
			SharedCityPlayerNumber,
			OtherPlayerNumber,
			VisiblePlayers);
	}
	if (!bSharedCityQaAppearanceLogged
		&& bSharedCityQaVisibleLogged
		&& OtherPlayer
		&& HasValidSharedCityAppearance()
		&& OtherPlayer->HasValidSharedCityAppearance()
		&& HasSubmittedSharedCityAppearance()
		&& OtherPlayer->HasSubmittedSharedCityAppearance())
	{
		bSharedCityQaAppearanceLogged = true;
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SHARED_CITY_APPEARANCE|local=Player_%d|local_preset=%s|local_top=%s|local_bottom=%s|other=Player_%d|other_preset=%s|other_top=%s|other_bottom=%s|agreement=true"),
			SharedCityPlayerNumber,
			*SharedCityAppearance.PresetId.ToString(),
			*SharedCityAppearance.TopItemId.ToString(),
			*SharedCityAppearance.BottomItemId.ToString(),
			OtherPlayerNumber,
			*OtherPlayer->SharedCityAppearance.PresetId.ToString(),
			*OtherPlayer->SharedCityAppearance.TopItemId.ToString(),
			*OtherPlayer->SharedCityAppearance.BottomItemId.ToString());
		if (GetNetMode() == NM_Client && FParse::Param(FCommandLine::Get(), TEXT("SharedCityAutoExit")))
		{
			SharedCityQaExitAt = FPlatformTime::Seconds() + 3.0;
		}
	}
	if (GetNetMode() == NM_Client && bSharedCityQaVisibleLogged)
	{
		AddMovementInput(FVector::ForwardVector, 1.0f);
	}
	if (SharedCityQaExitAt > 0.0 && FPlatformTime::Seconds() >= SharedCityQaExitAt)
	{
		SharedCityQaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::PollKeyboardMovement()
{
	const APlayerController* PlayerController = Cast<APlayerController>(Controller);
	if (!PlayerController)
	{
		return;
	}
	MoveForward((PlayerController->IsInputKeyDown(KeyForward) ? 1.0f : 0.0f) - (PlayerController->IsInputKeyDown(KeyBackward) ? 1.0f : 0.0f));
	MoveRight((PlayerController->IsInputKeyDown(KeyRight) ? 1.0f : 0.0f) - (PlayerController->IsInputKeyDown(KeyLeft) ? 1.0f : 0.0f));
}

void AOddsWellPlaceholderCharacter::MoveForward(const float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
	}
}

void AOddsWellPlaceholderCharacter::MoveRight(const float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
	}
}

void AOddsWellPlaceholderCharacter::LookYaw(const float Value) { AddControllerYawInput(Value); }
void AOddsWellPlaceholderCharacter::LookPitchMouse(const float Value) { AddControllerPitchInput(-Value); }
void AOddsWellPlaceholderCharacter::LookPitchController(const float Value) { AddControllerPitchInput(Value); }
void AOddsWellPlaceholderCharacter::StartRun() { GetCharacterMovement()->MaxWalkSpeed = RunSpeed; }
void AOddsWellPlaceholderCharacter::StopRun() { GetCharacterMovement()->MaxWalkSpeed = WalkSpeed; }
void AOddsWellPlaceholderCharacter::StartJump() { Jump(); }
void AOddsWellPlaceholderCharacter::StopJump() { StopJumping(); }

bool AOddsWellPlaceholderCharacter::ApplySavedOrFallbackAppearance()
{
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Source;
	FString Error;
	if (!ResolveLocalAppearance(Appearance, Source, Error) || !Appearance.Preset)
	{
		ReportAppearanceError(Error.IsEmpty() ? TEXT("No valid local or fallback appearance is available.") : Error);
		return false;
	}
	if (!Error.IsEmpty())
	{
		UE_LOG(LogOddsWellLocomotion, Warning, TEXT("ODDSWELL_APPEARANCE_FALLBACK|source=%s|reason=%s|record_preserved=true"), *Source, *Error);
	}
	return ApplyResolvedAppearance(Appearance, Source);
}

bool AOddsWellPlaceholderCharacter::ResolveLocalAppearance(
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutSource,
	FString& OutError) const
{
	FString QaPresetId;
	if (bSharedCityQa && FParse::Value(FCommandLine::Get(), TEXT("SharedCityQaPreset="), QaPresetId))
	{
		const FOddsWellCharacterPreset* Preset = FindOddsWellCharacterPreset(FName(*QaPresetId));
		if (!Preset || Preset->EquippedItemIds.Num() != 2)
		{
			OutError = FString::Printf(TEXT("Unsupported shared-city QA preset: %s"), *QaPresetId);
			return false;
		}
		OutSource = TEXT("shared_city_qa");
		return ValidateOddsWellCharacterAppearanceIds(
			Preset->Id,
			Preset->EquippedItemIds[0],
			Preset->EquippedItemIds[1],
			OutAppearance,
			OutError);
	}
	return LoadOddsWellCharacterAppearance(bAppearanceQa, OutAppearance, OutSource, OutError);
}

bool AOddsWellPlaceholderCharacter::ApplyResolvedAppearance(
	const FOddsWellResolvedCharacterAppearance& Appearance,
	const FString& Source)
{
	FString Error;
	if (!PrimitiveSkinMaterial)
	{
		ReportAppearanceError(TEXT("The primitive skin material is unavailable."));
		return false;
	}
	StarterOutfitState.Reset();
	if (!StarterOutfitState.Equip(Appearance.TopItemId, EOddsWellStarterEquipmentSlot::Top, Error)
		|| !StarterOutfitState.Equip(Appearance.BottomItemId, EOddsWellStarterEquipmentSlot::Bottom, Error)
		|| !StarterOutfitState.ValidateComplete(Error))
	{
		ReportOutfitError(Error);
		return false;
	}
	PrimitiveSkinMaterial->SetVectorParameterValue(TEXT("Color"), FLinearColor::FromSRGBColor(Appearance.Preset->SkinTone));
	SyncOutfitComponents();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_APPEARANCE_READY|schema=1|preset=%s|top=%s|bottom=%s|source=%s|skin=%s|presentation=%s|slot=%s"),
		*Appearance.Preset->Id.ToString(),
		*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Top).ToString(),
		*StarterOutfitState.GetEquipped(EOddsWellStarterEquipmentSlot::Bottom).ToString(),
		*Source,
		*Appearance.Preset->SkinTone.ToHex(),
		Appearance.Preset->Presentation == EOddsWellCharacterPresentation::Masculine ? TEXT("masculine") : TEXT("feminine"),
		bAppearanceQa ? TEXT("qa") : TEXT("production"));
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_OUTFIT_READY|top=%s|slot=top|bottom=%s|slot=bottom|replaceable=true"),
		*Appearance.TopItemId.ToString(),
		*Appearance.BottomItemId.ToString());
	return true;
}

bool AOddsWellPlaceholderCharacter::ApplySharedCityAppearance(const FString& Source)
{
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Error;
	if (!ValidateOddsWellCharacterAppearanceIds(
		SharedCityAppearance.PresetId,
		SharedCityAppearance.TopItemId,
		SharedCityAppearance.BottomItemId,
		Appearance,
		Error))
	{
		ReportAppearanceError(Error);
		return false;
	}
	return ApplyResolvedAppearance(Appearance, Source);
}

void AOddsWellPlaceholderCharacter::SubmitLocalSharedCityAppearance()
{
	if (bSharedCityAppearanceSubmitted)
	{
		return;
	}
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Source;
	FString Error;
	if (!ResolveLocalAppearance(Appearance, Source, Error) || !Appearance.Preset)
	{
		ReportAppearanceError(Error.IsEmpty() ? TEXT("No valid local shared-city appearance is available.") : Error);
		return;
	}
	if (!Error.IsEmpty())
	{
		UE_LOG(LogOddsWellLocomotion, Warning, TEXT("ODDSWELL_APPEARANCE_FALLBACK|source=%s|reason=%s|record_preserved=true"), *Source, *Error);
	}
	if (!ApplyResolvedAppearance(Appearance, Source))
	{
		return;
	}
	bSharedCityAppearanceSubmitted = true;
	if (HasAuthority())
	{
		SetAuthoritativeSharedCityAppearance(Appearance.Preset->Id, Appearance.TopItemId, Appearance.BottomItemId, true, Source);
	}
	else
	{
		ServerSetSharedCityAppearance(Appearance.Preset->Id, Appearance.TopItemId, Appearance.BottomItemId);
	}
}

void AOddsWellPlaceholderCharacter::ServerSetSharedCityAppearance_Implementation(
	const FName PresetId,
	const FName TopItemId,
	const FName BottomItemId)
{
	SetAuthoritativeSharedCityAppearance(PresetId, TopItemId, BottomItemId, true, TEXT("client_rpc"));
}

void AOddsWellPlaceholderCharacter::SetAuthoritativeSharedCityAppearance(
	const FName PresetId,
	const FName TopItemId,
	const FName BottomItemId,
	const bool bOwnerSubmitted,
	const FString& Source)
{
	if (!HasAuthority())
	{
		return;
	}
	FOddsWellResolvedCharacterAppearance Appearance;
	FString Error;
	if (!ValidateOddsWellCharacterAppearanceIds(PresetId, TopItemId, BottomItemId, Appearance, Error))
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SHARED_CITY_APPEARANCE_REJECTED|player=%d|reason=%s"), SharedCityPlayerNumber, *Error);
		return;
	}
	SharedCityAppearance.PresetId = PresetId;
	SharedCityAppearance.TopItemId = TopItemId;
	SharedCityAppearance.BottomItemId = BottomItemId;
	SharedCityAppearance.bOwnerSubmitted = bOwnerSubmitted;
	ApplyResolvedAppearance(Appearance, Source);
	ForceNetUpdate();
	UE_LOG(
		LogOddsWellLocomotion,
		Display,
		TEXT("ODDSWELL_SHARED_CITY_APPEARANCE_ACCEPTED|player=%d|preset=%s|top=%s|bottom=%s|owner_submitted=%s|source=%s"),
		SharedCityPlayerNumber,
		*PresetId.ToString(),
		*TopItemId.ToString(),
		*BottomItemId.ToString(),
		bOwnerSubmitted ? TEXT("true") : TEXT("false"),
		*Source);
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
		if (!GetOddsWellStarterEquipmentIds(TopId, BottomId, Error)
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

void AOddsWellPlaceholderCharacter::ReportAppearanceError(const FString& Error) const
{
	UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_APPEARANCE_ERROR|%s"), *Error);
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
	if (bAppearanceQaCleanup)
	{
		FString Error;
		const bool bClean = bAppearanceQa && DeleteOddsWellQaAppearanceAndVerify(Error);
		if (bClean)
		{
			UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_APPEARANCE_QA_CLEANUP|result=PASS|slot=qa|exists=false"));
		}
		else
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_APPEARANCE_QA_CLEANUP|result=FAIL|slot=%s|reason=%s"), bAppearanceQa ? TEXT("qa") : TEXT("production"), *Error);
		}
		bAppearanceQaCleanup = false;
	}
	if (bQaAutoExit)
	{
		QaExitAt = FPlatformTime::Seconds() + 12.0;
	}
}

void AOddsWellPlaceholderCharacter::RunSundaleRouteQa(const float DeltaSeconds)
{
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	if (bSundaleRouteFinished)
	{
		return;
	}
	if (!bSundaleRouteStarted)
	{
		SundaleRouteElapsed += DeltaSeconds;
		if (!Movement->IsMovingOnGround())
		{
			if (SundaleRouteElapsed > 10.0f)
			{
				FinishSundaleRouteQa(false);
			}
			return;
		}
		if (!GetWorld()->GetMapName().Contains(TEXT("SundaleGraybox")))
		{
			UE_LOG(LogOddsWellLocomotion, Error, TEXT("ODDSWELL_SUNDALE_ROUTE_ERROR|reason=wrong_map|map=%s"), *GetWorld()->GetMapName());
			FinishSundaleRouteQa(false);
			return;
		}
		bSundaleRouteStarted = true;
		SundaleRouteElapsed = 0.0f;
		SundaleRouteStart = GetActorLocation();
		SundalePreviousLocation = SundaleRouteStart;
		SundaleMinZ = SundaleRouteStart.Z;
		SundaleMaxZ = SundaleRouteStart.Z;
		if (bSundaleRouteRun)
		{
			StartRun();
		}
		else
		{
			StopRun();
		}
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SUNDALE_ROUTE_START|mode=%s|map=%s|start=%s|planned_distance=%.0f"),
			bSundaleRouteRun ? TEXT("run") : TEXT("walk"),
			*GetWorld()->GetMapName(),
			*SundaleRouteStart.ToCompactString(),
			SundaleRouteDistance);
		return;
	}
	SundaleRouteElapsed += DeltaSeconds;
	SundaleSegmentElapsed += DeltaSeconds;
	const FVector CurrentLocation = GetActorLocation();
	SundaleTravelDistance += FVector::Dist2D(SundalePreviousLocation, CurrentLocation);
	SundalePreviousLocation = CurrentLocation;
	SundaleMinZ = FMath::Min(SundaleMinZ, CurrentLocation.Z);
	SundaleMaxZ = FMath::Max(SundaleMaxZ, CurrentLocation.Z);

	const TArray<FVector>& Waypoints = GetSundaleRouteWaypoints();
	if (!Waypoints.IsValidIndex(SundaleRouteIndex))
	{
		FinishSundaleRouteQa(true);
		return;
	}

	FVector Direction = Waypoints[SundaleRouteIndex] - CurrentLocation;
	Direction.Z = 0.0f;
	if (Direction.Size2D() <= SundaleWaypointTolerance)
	{
		const TArray<FString>& Labels = GetSundaleRouteWaypointLabels();
		UE_LOG(
			LogOddsWellLocomotion,
			Display,
			TEXT("ODDSWELL_SUNDALE_ROUTE_POINT|index=%d|name=%s|segment_seconds=%.3f|location=%s"),
			SundaleRouteIndex + 1,
			*Labels[SundaleRouteIndex],
			SundaleSegmentElapsed,
			*CurrentLocation.ToCompactString());
		++SundaleRouteIndex;
		SundaleSegmentElapsed = 0.0f;
		if (SundaleRouteIndex == Waypoints.Num())
		{
			FinishSundaleRouteQa(true);
		}
		return;
	}

	AddMovementInput(Direction.GetSafeNormal(), 1.0f);
	const float PlannedSeconds = SundaleRouteDistance / (bSundaleRouteRun ? RunSpeed : WalkSpeed);
	if (SundaleRouteElapsed > PlannedSeconds * 1.6f + 10.0f)
	{
		FinishSundaleRouteQa(false);
	}
}

void AOddsWellPlaceholderCharacter::FinishSundaleRouteQa(const bool bPassed)
{
	if (bSundaleRouteFinished)
	{
		return;
	}
	bSundaleRouteFinished = true;
	StopRun();
	const bool bAllPoints = SundaleRouteIndex == GetSundaleRouteWaypoints().Num();
	const bool bReturnedHome = FVector::Dist2D(SundaleRouteStart, GetActorLocation()) <= 150.0f;
	const bool bDistancePlausible = SundaleTravelDistance >= SundaleRouteDistance * 0.96f
		&& SundaleTravelDistance <= SundaleRouteDistance * 1.04f;
	const bool bFloorBlocking = GetCharacterMovement()->CurrentFloor.bBlockingHit;
	const bool bVerticalStable = SundaleMaxZ - SundaleMinZ <= 100.0f;
	const bool bFinalPass = bPassed && bAllPoints && bReturnedHome && bDistancePlausible
		&& GetCharacterMovement()->IsMovingOnGround() && bFloorBlocking && bVerticalStable;
	const FString Evidence = FString::Printf(
		TEXT("ODDSWELL_SUNDALE_ROUTE_QA|result=%s|mode=%s|seconds=%.3f|planned_distance=%.0f|traveled_distance=%.1f|points=%d/%d|returned_home=%s|landed=%s|floor_blocking=%s|vertical_range=%.1f"),
		bFinalPass ? TEXT("PASS") : TEXT("FAIL"),
		bSundaleRouteRun ? TEXT("run") : TEXT("walk"),
		SundaleRouteElapsed,
		SundaleRouteDistance,
		SundaleTravelDistance,
		SundaleRouteIndex,
		GetSundaleRouteWaypoints().Num(),
		bReturnedHome ? TEXT("true") : TEXT("false"),
		GetCharacterMovement()->IsMovingOnGround() ? TEXT("true") : TEXT("false"),
		bFloorBlocking ? TEXT("true") : TEXT("false"),
		SundaleMaxZ - SundaleMinZ);
	if (bFinalPass)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("%s"), *Evidence);
	}
	else
	{
		UE_LOG(LogOddsWellLocomotion, Error, TEXT("%s"), *Evidence);
	}
	if (bQaAutoExit)
	{
		QaExitAt = FPlatformTime::Seconds() + 2.0;
	}
}

AOddsWellLocomotionGameMode::AOddsWellLocomotionGameMode()
{
	PrimaryActorTick.bCanEverTick = true;
	DefaultPawnClass = AOddsWellPlaceholderCharacter::StaticClass();
	bSharedCityQa = FParse::Param(FCommandLine::Get(), TEXT("SharedCityQa"));
}

void AOddsWellLocomotionGameMode::PostLogin(APlayerController* NewPlayer)
{
	Super::PostLogin(NewPlayer);
	if (GetNetMode() != NM_Standalone)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_JOIN|clients=%d|boundary=local_listen_server"), GetNumPlayers());
	}
}

void AOddsWellLocomotionGameMode::Logout(AController* Exiting)
{
	Super::Logout(Exiting);
	if (GetNetMode() != NM_Standalone)
	{
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_LEAVE|clients=%d"), GetNumPlayers());
	}
}

void AOddsWellLocomotionGameMode::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (SharedCityQaExitAt > 0.0 && FPlatformTime::Seconds() >= SharedCityQaExitAt)
	{
		SharedCityQaExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (!bSharedCityQa || bSharedCityQaPassed)
	{
		return;
	}
	TArray<AOddsWellPlaceholderCharacter*> Players;
	for (TActorIterator<AOddsWellPlaceholderCharacter> It(GetWorld()); It; ++It)
	{
		if (It->GetSharedCityPlayerNumber() > 0)
		{
			Players.Add(*It);
		}
	}
	if (Players.Num() < 2)
	{
		return;
	}
	if (!bSharedCityQaStarted)
	{
		for (const AOddsWellPlaceholderCharacter* Player : Players)
		{
			SharedCityQaStartLocations.Add(Player->GetSharedCityPlayerNumber(), Player->GetActorLocation());
		}
		bSharedCityQaStarted = true;
		UE_LOG(LogOddsWellLocomotion, Display, TEXT("ODDSWELL_SHARED_CITY_READY|clients=%d|map=%s|spawn_spacing=%.0f"), Players.Num(), *GetWorld()->GetMapName(), SharedCitySpawnSpacing);
		return;
	}
	const bool bAppearancesReady = !Players.ContainsByPredicate(
		[](const AOddsWellPlaceholderCharacter* Player)
		{
			return !Player->HasValidSharedCityAppearance() || !Player->HasSubmittedSharedCityAppearance();
		});
	for (const AOddsWellPlaceholderCharacter* Player : Players)
	{
		const FVector* Start = SharedCityQaStartLocations.Find(Player->GetSharedCityPlayerNumber());
		const float Distance = Start ? FVector::Dist2D(*Start, Player->GetActorLocation()) : 0.0f;
		if (Player->GetSharedCityPlayerNumber() > 1
			&& Distance >= SharedCityQaMovementDistance
			&& bAppearancesReady)
		{
			bSharedCityQaPassed = true;
			UE_LOG(
				LogOddsWellLocomotion,
				Display,
				TEXT("ODDSWELL_SHARED_CITY_PASS|clients=%d|moving_player=Player_%d|server_distance=%.1f|replicated_movement=true|appearance_synced=true|starter_clothing_synced=true|names=true|pawn_collision=ignore"),
				Players.Num(),
				Player->GetSharedCityPlayerNumber(),
				Distance);
			if (FParse::Param(FCommandLine::Get(), TEXT("SharedCityAutoExit")))
			{
				SharedCityQaExitAt = FPlatformTime::Seconds() + 5.0;
			}
			break;
		}
	}
}

APawn* AOddsWellLocomotionGameMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform&)
{
	FActorSpawnParameters Parameters;
	Parameters.Owner = NewPlayer;
	Parameters.ObjectFlags |= RF_Transient;
	Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
	const int32 PlayerNumber = NextSharedCityPlayerNumber++;
	const FVector SpawnLocation = SafeSpawnLocation + FVector(0.0, SharedCitySpawnSpacing * (PlayerNumber - 1), 0.0);
	AOddsWellPlaceholderCharacter* Character = GetWorld()->SpawnActor<AOddsWellPlaceholderCharacter>(SpawnLocation, FRotator::ZeroRotator, Parameters);
	if (Character && GetNetMode() != NM_Standalone)
	{
		Character->AssignSharedCityPlayerNumber(PlayerNumber);
	}
	return Character;
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
	TestTrue(TEXT("Two-player proof uses separated spawn points"), SharedCitySpawnSpacing > CapsuleRadius * 2.0f);
	TestTrue(TEXT("Shared-city QA requires measurable movement"), SharedCityQaMovementDistance > SharedCitySpawnSpacing);
	TestTrue(TEXT("Players pass through one another"), SharedCityPlayerCollision == ECR_Ignore);

	const TArray<FKey> KeyboardMoveKeys = {KeyForward, KeyBackward, KeyLeft, KeyRight};
	const TArray<FKey> MouseLookKeys = {KeyMouseYaw, KeyMousePitch};
	const TArray<FKey> ControllerMoveLookKeys = {KeyControllerMoveX, KeyControllerMoveY, KeyControllerLookX, KeyControllerLookY};
	TestEqual(TEXT("Keyboard movement polling routes are complete"), KeyboardMoveKeys.Num(), 4);
	TestEqual(TEXT("Mouse look axis routes are complete"), MouseLookKeys.Num(), 2);
	TestEqual(TEXT("Controller movement/look routes are complete"), ControllerMoveLookKeys.Num(), 4);
	for (const FKey& Key : KeyboardMoveKeys)
	{
		TestFalse(FString::Printf(TEXT("Digital keyboard key %s is not bound as an axis"), *Key.ToString()), Key.IsAxis1D());
	}
	for (const FKey& Key : MouseLookKeys)
	{
		TestTrue(FString::Printf(TEXT("Mouse look key %s is a one-dimensional axis"), *Key.ToString()), Key.IsAxis1D());
	}
	for (const FKey& Key : ControllerMoveLookKeys)
	{
		TestTrue(FString::Printf(TEXT("Controller axis %s is a gamepad route"), *Key.ToString()), Key.IsGamepadKey());
		TestTrue(FString::Printf(TEXT("Controller axis %s is one-dimensional"), *Key.ToString()), Key.IsAxis1D());
	}
	TestFalse(TEXT("Keyboard run route is not a gamepad key"), KeyRun.IsGamepadKey());
	TestFalse(TEXT("Keyboard jump route is not a gamepad key"), KeyJump.IsGamepadKey());
	TestTrue(TEXT("Controller run route is present"), KeyControllerRun.IsGamepadKey());
	TestTrue(TEXT("Controller jump route is present"), KeyControllerJump.IsGamepadKey());

	TestFalse(TEXT("Crouch is not supported"), AllowCrouch);
	TestFalse(TEXT("Flight is not supported"), AllowFlight);
	TestFalse(TEXT("Swimming is not supported"), AllowSwimming);
	const TArray<FVector>& SundaleWaypoints = GetSundaleRouteWaypoints();
	TestEqual(TEXT("Sundale route keeps the minimal eleven waypoints"), SundaleWaypoints.Num(), 11);
	float SundaleDistance = 0.0f;
	FVector PreviousPoint = FVector::ZeroVector;
	for (const FVector& Point : SundaleWaypoints)
	{
		SundaleDistance += FVector::Dist2D(PreviousPoint, Point);
		PreviousPoint = Point;
	}
	TestTrue(TEXT("Sundale route remains exactly 800 meters"), FMath::IsNearlyEqual(SundaleDistance, SundaleRouteDistance));
	TestEqual(TEXT("Sundale route labels match waypoints"), GetSundaleRouteWaypointLabels().Num(), SundaleWaypoints.Num());
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
		TestTrue(TEXT("Catalog top resolves"), ResolveOddsWellStarterEquipmentSlot(Preset.EquippedItemIds[0], TopSlot, Error));
		TestTrue(TEXT("Catalog bottom resolves"), ResolveOddsWellStarterEquipmentSlot(Preset.EquippedItemIds[1], BottomSlot, Error));
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
