#include "CharacterSelectionScreen.h"

#include "CharacterAppearanceSave.h"
#include "CharacterPresetCatalog.h"
#include "Components/InputComponent.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"
#include "HAL/PlatformMisc.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogOddsWellCharacterSelection, Log, All);

namespace
{
const TArray<FKey> KeyboardNavigationKeys = {EKeys::Left, EKeys::Right, EKeys::Up, EKeys::Down, EKeys::A, EKeys::D, EKeys::W, EKeys::S};
const TArray<FKey> ControllerNavigationKeys = {EKeys::Gamepad_DPad_Left, EKeys::Gamepad_DPad_Right, EKeys::Gamepad_DPad_Up, EKeys::Gamepad_DPad_Down};
const TArray<FKey> KeyboardConfirmKeys = {EKeys::Enter, EKeys::SpaceBar};
const TArray<FKey> ControllerConfirmKeys = {EKeys::Gamepad_FaceButton_Bottom};
const FLinearColor OffWhite(0.92f, 0.90f, 0.82f);
}

FOddsWellCharacterSelectionState::FOddsWellCharacterSelectionState()
{
	if (ValidateOddsWellCharacterPresets(Error))
	{
		SelectedIndex = 0;
	}
	else
	{
		UE_LOG(LogOddsWellCharacterSelection, Error, TEXT("Catalog validation failed: %s"), *Error);
	}
}

bool FOddsWellCharacterSelectionState::Navigate(const int32 Delta)
{
	if (!IsValid() || IsConfirmed())
	{
		return false;
	}

	const int32 Count = GetOddsWellCharacterPresets().Num();
	SelectedIndex = ((SelectedIndex + Delta) % Count + Count) % Count;
	return true;
}

bool FOddsWellCharacterSelectionState::Confirm()
{
	const FOddsWellCharacterPreset* Preset = GetSelectedPreset();
	if (!Preset || IsConfirmed())
	{
		return false;
	}

	ConfirmedPresetId = Preset->Id;
	return true;
}

const FOddsWellCharacterPreset* FOddsWellCharacterSelectionState::GetSelectedPreset() const
{
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	return Presets.IsValidIndex(SelectedIndex) ? &Presets[SelectedIndex] : nullptr;
}

AOddsWellCharacterSelectionHUD::AOddsWellCharacterSelectionHUD()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AOddsWellCharacterSelectionHUD::BeginPlay()
{
	Super::BeginPlay();
	if (!State.IsValid())
	{
		return;
	}

	APlayerController* Controller = GetOwningPlayerController();
	if (!Controller)
	{
		UE_LOG(LogOddsWellCharacterSelection, Error, TEXT("No local player controller; selection remains unconfirmed."));
		return;
	}
	EnableInput(Controller);
	if (!InputComponent)
	{
		UE_LOG(LogOddsWellCharacterSelection, Error, TEXT("Input initialization failed; selection remains unconfirmed."));
		return;
	}

	InputComponent->BindKey(EKeys::Left, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveLeft);
	InputComponent->BindKey(EKeys::A, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveLeft);
	InputComponent->BindKey(EKeys::Gamepad_DPad_Left, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveLeft);
	InputComponent->BindKey(EKeys::Right, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveRight);
	InputComponent->BindKey(EKeys::D, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveRight);
	InputComponent->BindKey(EKeys::Gamepad_DPad_Right, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveRight);
	InputComponent->BindKey(EKeys::Up, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveUp);
	InputComponent->BindKey(EKeys::W, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveUp);
	InputComponent->BindKey(EKeys::Gamepad_DPad_Up, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveUp);
	InputComponent->BindKey(EKeys::Down, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveDown);
	InputComponent->BindKey(EKeys::S, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveDown);
	InputComponent->BindKey(EKeys::Gamepad_DPad_Down, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::MoveDown);
	InputComponent->BindKey(EKeys::Enter, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::ConfirmSelection);
	InputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::ConfirmSelection);
	InputComponent->BindKey(EKeys::Gamepad_FaceButton_Bottom, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::ConfirmSelection);

	int32 QaSteps = 0;
	if (FParse::Value(FCommandLine::Get(), TEXT("CharacterSelectQaSteps="), QaSteps))
	{
		State.Navigate(QaSteps);
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("CharacterSelectAutoConfirm")))
	{
		ConfirmSelection();
	}
	float AutoExitSeconds = 0.0f;
	if (FParse::Value(FCommandLine::Get(), TEXT("CharacterSelectAutoExit="), AutoExitSeconds) && AutoExitSeconds > 0.0f)
	{
		AutoExitAt = FPlatformTime::Seconds() + AutoExitSeconds;
	}
}

void AOddsWellCharacterSelectionHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas)
	{
		return;
	}

	DrawRect(FLinearColor(0.025f, 0.035f, 0.055f), 0.0f, 0.0f, Canvas->ClipX, Canvas->ClipY);
	DrawText(TEXT("CHOOSE YOUR PLACEHOLDER"), FLinearColor::White, 64.0f, 28.0f, GEngine->GetLargeFont(), 1.15f);
	DrawText(TEXT("8 GAMEPLAY-IDENTICAL OPTIONS  |  NONCANONICAL ART  |  LOCAL APPEARANCE SAVE"), FLinearColor(0.65f, 0.78f, 0.92f), 64.0f, 72.0f);

	if (!State.IsValid())
	{
		DrawText(FString::Printf(TEXT("LOCAL CATALOG ERROR: %s"), *State.GetError()), FLinearColor::Red, 64.0f, 140.0f, GEngine->GetMediumFont());
		DrawText(TEXT("No preset can be confirmed."), FLinearColor::White, 64.0f, 180.0f);
		return;
	}

	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	const float Gap = 16.0f;
	const float CardWidth = FMath::Min(270.0f, (Canvas->ClipX - 128.0f - Gap * 3.0f) / 4.0f);
	const float CardHeight = FMath::Min(205.0f, (Canvas->ClipY - 230.0f - Gap) / 2.0f);
	for (int32 Index = 0; Index < Presets.Num(); ++Index)
	{
		const int32 Column = Index % 4;
		const int32 Row = Index / 4;
		DrawCard(Presets[Index], Index, 64.0f + Column * (CardWidth + Gap), 112.0f + Row * (CardHeight + Gap), CardWidth, CardHeight);
	}

	const FString Help = !HandoffError.IsEmpty()
		? FString::Printf(TEXT("LOCAL SAVE ERROR - NOT ENTERING WORLD: %s"), *HandoffError)
		: State.IsConfirmed()
		? FString::Printf(TEXT("SAVED LOCALLY: %s  |  ENTERING PLACEHOLDER WORLD"), *State.GetConfirmedPresetId().ToString())
		: TEXT("ARROWS / WASD / CONTROLLER D-PAD TO NAVIGATE     ENTER / SPACE / CONTROLLER A TO CONFIRM");
	DrawText(Help, !HandoffError.IsEmpty() ? FLinearColor::Red : State.IsConfirmed() ? FLinearColor(0.45f, 1.0f, 0.55f) : FLinearColor::White, 64.0f, Canvas->ClipY - 54.0f, GEngine->GetMediumFont());
}

void AOddsWellCharacterSelectionHUD::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (AutoExitAt > 0.0 && FPlatformTime::Seconds() >= AutoExitAt)
	{
		AutoExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellCharacterSelectionHUD::MoveLeft() { State.Navigate(-1); }
void AOddsWellCharacterSelectionHUD::MoveRight() { State.Navigate(1); }
void AOddsWellCharacterSelectionHUD::MoveUp() { State.Navigate(-4); }
void AOddsWellCharacterSelectionHUD::MoveDown() { State.Navigate(4); }

void AOddsWellCharacterSelectionHUD::ConfirmSelection()
{
	const FOddsWellCharacterPreset* Preset = State.GetSelectedPreset();
	if (!Preset || State.IsConfirmed())
	{
		return;
	}
	HandoffError.Reset();
	const bool bQaSlot = UseOddsWellAppearanceQaSlot();
	if (!SaveOddsWellCharacterAppearance(Preset->Id, bQaSlot, HandoffError))
	{
		UE_LOG(LogOddsWellCharacterSelection, Error, TEXT("ODDSWELL_APPEARANCE_SAVE|result=FAIL|preset=%s|slot=%s|reason=%s"), *Preset->Id.ToString(), bQaSlot ? TEXT("qa") : TEXT("production"), *HandoffError);
		return;
	}
	if (!State.Confirm())
	{
		HandoffError = TEXT("Selection confirmation failed after the appearance save completed.");
		UE_LOG(LogOddsWellCharacterSelection, Error, TEXT("ODDSWELL_APPEARANCE_SAVE|result=FAIL|preset=%s|slot=%s|reason=%s"), *Preset->Id.ToString(), bQaSlot ? TEXT("qa") : TEXT("production"), *HandoffError);
		return;
	}
	UE_LOG(
		LogOddsWellCharacterSelection,
		Display,
		TEXT("ODDSWELL_APPEARANCE_SAVE|result=PASS|schema=1|preset=%s|top=%s|bottom=%s|slot=%s|confirmed_once=true"),
		*Preset->Id.ToString(),
		*Preset->EquippedItemIds[0].ToString(),
		*Preset->EquippedItemIds[1].ToString(),
		bQaSlot ? TEXT("qa") : TEXT("production"));
	UGameplayStatics::OpenLevel(
		this,
		FName(TEXT("/Game/Maps/SundaleGraybox")),
		true,
		TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode"));
}

void AOddsWellCharacterSelectionHUD::DrawCard(const FOddsWellCharacterPreset& Preset, const int32 Index, const float X, const float Y, const float Width, const float Height)
{
	const bool bSelected = Index == State.GetSelectedIndex();
	DrawRect(bSelected ? FLinearColor(0.15f, 0.38f, 0.66f) : FLinearColor(0.09f, 0.12f, 0.18f), X, Y, Width, Height);
	const float Border = bSelected ? 4.0f : 1.0f;
	const FLinearColor BorderColor = bSelected ? FLinearColor(0.35f, 0.8f, 1.0f) : FLinearColor(0.25f, 0.3f, 0.4f);
	DrawRect(BorderColor, X, Y, Width, Border);
	DrawRect(BorderColor, X, Y + Height - Border, Width, Border);
	DrawRect(BorderColor, X, Y, Border, Height);
	DrawRect(BorderColor, X + Width - Border, Y, Border, Height);

	const float CenterX = X + Width * 0.5f;
	DrawRect(FLinearColor(Preset.SkinTone), CenterX - 18.0f, Y + 30.0f, 36.0f, 36.0f);
	DrawRect(OffWhite, CenterX - 30.0f, Y + 70.0f, 60.0f, 42.0f);
	DrawRect(OffWhite * 0.82f, CenterX - 28.0f, Y + 116.0f, 24.0f, 38.0f);
	DrawRect(OffWhite * 0.82f, CenterX + 4.0f, Y + 116.0f, 24.0f, 38.0f);

	const TCHAR* Presentation = Preset.Presentation == EOddsWellCharacterPresentation::Masculine ? TEXT("MASCULINE") : TEXT("FEMININE");
	DrawText(Preset.Id.ToString(), FLinearColor::White, X + 12.0f, Y + 8.0f, GEngine->GetSmallFont(), 0.9f);
	DrawText(FString::Printf(TEXT("%s  |  SKIN #%s"), Presentation, *Preset.SkinTone.ToHex()), FLinearColor(0.75f, 0.84f, 0.95f), X + 12.0f, Y + Height - 42.0f, GEngine->GetSmallFont(), 0.72f);
	DrawText(TEXT("OFF-WHITE TOP + BOTTOM  |  REPLACEABLE"), OffWhite, X + 12.0f, Y + Height - 23.0f, GEngine->GetSmallFont(), 0.62f);
}

AOddsWellCharacterSelectionGameMode::AOddsWellCharacterSelectionGameMode()
{
	DefaultPawnClass = nullptr;
	HUDClass = AOddsWellCharacterSelectionHUD::StaticClass();
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCharacterSelectionTest,
	"OddsWell.Character.SelectionState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCharacterSelectionTest::RunTest(const FString& Parameters)
{
	FString CatalogError;
	TestTrue(TEXT("Catalog validation runs before selection"), ValidateOddsWellCharacterPresets(CatalogError));
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	TestEqual(TEXT("Screen consumes all catalog entries"), Presets.Num(), 8);

	FOddsWellCharacterSelectionState DefaultState;
	TestTrue(TEXT("Safe default is valid"), DefaultState.IsValid());
	TestEqual(TEXT("Safe default is deterministic first catalog entry"), DefaultState.GetSelectedIndex(), 0);
	TestEqual(TEXT("Safe default ID comes from catalog"), DefaultState.GetSelectedPreset()->Id, Presets[0].Id);
	TestTrue(TEXT("Safe default confirms immediately"), DefaultState.Confirm());
	TestEqual(TEXT("Immediate confirmation records safe default"), DefaultState.GetConfirmedPresetId(), Presets[0].Id);

	FOddsWellCharacterSelectionState State;
	TestTrue(TEXT("Left navigation wraps inside catalog"), State.Navigate(-1));
	TestEqual(TEXT("Wrapped selection is last catalog entry"), State.GetSelectedIndex(), 7);
	TestTrue(TEXT("Right navigation wraps back"), State.Navigate(1));
	TestEqual(TEXT("Selection returns to first catalog entry"), State.GetSelectedIndex(), 0);
	TestTrue(TEXT("Grid navigation stays bounded"), State.Navigate(12));
	TestEqual(TEXT("Down-grid navigation wraps deterministically"), State.GetSelectedIndex(), 4);
	TestTrue(TEXT("One valid selection confirms"), State.Confirm());
	TestEqual(TEXT("Confirmed ID is current catalog ID"), State.GetConfirmedPresetId(), Presets[4].Id);
	TestFalse(TEXT("A session cannot confirm twice"), State.Confirm());
	TestFalse(TEXT("Confirmed state cannot navigate"), State.Navigate(1));

	TestEqual(TEXT("Keyboard navigation routes are represented"), KeyboardNavigationKeys.Num(), 8);
	TestEqual(TEXT("Controller navigation routes are represented"), ControllerNavigationKeys.Num(), 4);
	for (const FKey& Key : ControllerNavigationKeys)
	{
		TestTrue(FString::Printf(TEXT("Controller navigation key %s is a gamepad key"), *Key.ToString()), Key.IsGamepadKey());
	}
	TestEqual(TEXT("Keyboard confirm routes are represented"), KeyboardConfirmKeys.Num(), 2);
	TestEqual(TEXT("Controller confirm route is represented"), ControllerConfirmKeys.Num(), 1);
	TestTrue(TEXT("Controller confirm is a gamepad key"), ControllerConfirmKeys[0].IsGamepadKey());

	return !HasAnyErrors();
}
#endif
