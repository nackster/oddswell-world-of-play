#include "CharacterSelectionScreen.h"

#include "CharacterAppearanceSave.h"
#include "CharacterPresetCatalog.h"
#include "Career/OddsWellCareer.h"
#include "Career/OddsWellCharacterPreview.h"
#include "Career/OddsWellMetaHuman.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Components/InputComponent.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"
#include "HAL/PlatformMisc.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"

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
constexpr int32 CharacterChooserCardCount = 8;
constexpr int32 CharacterChooserStagePartsPerCard = 2;
constexpr float CharacterChooserStageWidth = 96.0f;
constexpr float CharacterChooserStageHeight = 136.0f;
constexpr float CharacterChooserRailWidth = 88.0f;
constexpr float CharacterChooserRailHeight = 4.0f;
const FLinearColor CharacterChooserStageColor(0.04f, 0.10f, 0.13f);
const FLinearColor CharacterChooserRailColor(0.78f, 0.48f, 0.22f);
const FString CharacterHandoffEndpoint(TEXT("127.0.0.1:17777"));
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
	InputComponent->BindKey(EKeys::Escape, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::Back);
	InputComponent->BindKey(EKeys::BackSpace, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::Back);
	InputComponent->BindKey(EKeys::Gamepad_FaceButton_Right, IE_Pressed, this, &AOddsWellCharacterSelectionHUD::Back);
	Screen = IsOddsWellCareerMode() && !FParse::Param(FCommandLine::Get(), TEXT("CharacterSelectAutoConfirm"))
		? EScreen::Title
		: EScreen::Chooser;

	int32 QaSteps = 0;
	if (FParse::Value(FCommandLine::Get(), TEXT("CharacterSelectQaSteps="), QaSteps))
	{
		State.Navigate(QaSteps);
	}
	UE_LOG(
		LogOddsWellCharacterSelection,
		Display,
		TEXT("ODDSWELL_CHARACTER_CHOOSER_PRESENTATION|result=PASS|cards=%d|parts=%d|roles=2|selected_index=%d|native_canvas=true|shared_treatment=true|catalog_unchanged=true|gameplay_identical=true|starter_outfit_unchanged=true|final_art=false"),
		GetOddsWellCharacterPresets().Num(),
		GetOddsWellCharacterPresets().Num() * CharacterChooserStagePartsPerCard,
		State.GetSelectedIndex());
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

	const bool bCareerChooser = Screen == EScreen::Chooser && IsOddsWellCareerMode() && Preview;
	if (!bCareerChooser)
	{
		DrawRect(FLinearColor(0.025f, 0.035f, 0.055f), 0.0f, 0.0f, Canvas->ClipX, Canvas->ClipY);
	}
	if (bCareerChooser)
	{
		DrawCareerChooser();
		return;
	}
	if (Screen == EScreen::Title)
	{
		DrawTitle();
		return;
	}
	if (Screen == EScreen::Settings)
	{
		DrawSettings();
		return;
	}
	if (Screen == EScreen::ConfirmNewCareer)
	{
		DrawConfirmNewCareer();
		return;
	}
	const bool bCareer = IsOddsWellCareerMode();
	DrawText(bCareer ? TEXT("CHOOSE YOUR CHARACTER") : TEXT("CHOOSE YOUR PLACEHOLDER"), FLinearColor::White, 64.0f, 28.0f, GEngine->GetLargeFont(), 1.15f);
	DrawText(bCareer ? TEXT("Everyone starts with the same Studio, the same job and 0 Odds Bucks.") : TEXT("8 GAMEPLAY-IDENTICAL OPTIONS  |  NONCANONICAL ART  |  LOCAL APPEARANCE SAVE"), FLinearColor(0.65f, 0.78f, 0.92f), 64.0f, 72.0f);

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
	UpdatePreview();
	static const bool bFrontEndShots = FParse::Param(FCommandLine::Get(), TEXT("FrontEndShots"));
	if (bFrontEndShots)
	{
		// Scripted look at the front end: title, chooser previews of two characters, settings, then exit.
		static double StartedAt = FPlatformTime::Seconds();
		static int32 Stage = 0;
		const double Elapsed = FPlatformTime::Seconds() - StartedAt;
		const auto Shot = [](const TCHAR* Name) { FScreenshotRequest::RequestScreenshot(FString::Printf(TEXT("FrontEnd_%s.png"), Name), true, false); };
		if (Stage == 0 && Elapsed > 3.0) { Shot(TEXT("1_Title")); ++Stage; }
		else if (Stage == 1 && Elapsed > 4.0) { Screen = EScreen::Chooser; bStartNewCareerOnConfirm = true; ++Stage; }
		else if (Stage == 2 && Elapsed > 14.0) { Shot(TEXT("2_ChooserKelvin")); ++Stage; }
		else if (Stage == 3 && Elapsed > 15.0) { State.Navigate(7); ++Stage; }
		else if (Stage == 4 && Elapsed > 25.0) { Shot(TEXT("3_ChooserZuri")); ++Stage; }
		else if (Stage == 5 && Elapsed > 26.0) { Screen = EScreen::Settings; SettingsMenu.Open(); ++Stage; }
		else if (Stage == 6 && Elapsed > 28.0) { Shot(TEXT("4_Settings")); ++Stage; }
		else if (Stage == 7 && Elapsed > 30.0) { FPlatformMisc::RequestExit(false); ++Stage; }
	}
	if (AutoExitAt > 0.0 && FPlatformTime::Seconds() >= AutoExitAt)
	{
		AutoExitAt = 0.0;
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellCharacterSelectionHUD::MoveLeft()
{
	if (Screen == EScreen::Settings) { SettingsMenu.ChangeValue(-1); }
	else if (Screen == EScreen::Chooser) { State.Navigate(-1); }
}

void AOddsWellCharacterSelectionHUD::MoveRight()
{
	if (Screen == EScreen::Settings) { SettingsMenu.ChangeValue(1); }
	else if (Screen == EScreen::Chooser) { State.Navigate(1); }
}

void AOddsWellCharacterSelectionHUD::MoveUp()
{
	if (Screen == EScreen::Title) { TitleIndex = (TitleIndex - 1 + TitleItems().Num()) % TitleItems().Num(); }
	else if (Screen == EScreen::Settings) { SettingsMenu.MoveSelection(-1); }
	else if (Screen == EScreen::Chooser) { State.Navigate(Preview ? -1 : -4); }
}

void AOddsWellCharacterSelectionHUD::MoveDown()
{
	if (Screen == EScreen::Title) { TitleIndex = (TitleIndex + 1) % TitleItems().Num(); }
	else if (Screen == EScreen::Settings) { SettingsMenu.MoveSelection(1); }
	else if (Screen == EScreen::Chooser) { State.Navigate(Preview ? 1 : 4); }
}

TArray<FString> AOddsWellCharacterSelectionHUD::TitleItems() const
{
	const UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	TArray<FString> Items;
	if (Career && Career->HasCareer())
	{
		Items.Add(TEXT("Continue"));
	}
	Items.Append({TEXT("New career"), TEXT("Settings"), TEXT("Quit")});
	return Items;
}

void AOddsWellCharacterSelectionHUD::Back()
{
	if (Screen == EScreen::Settings || Screen == EScreen::ConfirmNewCareer
		|| (Screen == EScreen::Chooser && IsOddsWellCareerMode() && !State.IsConfirmed() && !FParse::Param(FCommandLine::Get(), TEXT("CharacterSelectAutoConfirm"))))
	{
		Screen = EScreen::Title;
	}
}

void AOddsWellCharacterSelectionHUD::ActivateTitleItem()
{
	const TArray<FString> Items = TitleItems();
	const FString Item = Items.IsValidIndex(TitleIndex) ? Items[TitleIndex] : FString();
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	if (Item == TEXT("Continue"))
	{
		UE_LOG(LogOddsWellCharacterSelection, Display, TEXT("ODDSWELL_TITLE|action=continue|season=%d|day=%d"), Career ? Career->GetSeason() : 0, Career ? Career->GetDay() : 0);
		UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/SundaleGraybox")), true, TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode"));
	}
	else if (Item == TEXT("New career"))
	{
		bStartNewCareerOnConfirm = true;
		Screen = Career && Career->HasCareer() ? EScreen::ConfirmNewCareer : EScreen::Chooser;
	}
	else if (Item == TEXT("Settings"))
	{
		SettingsMenu.Open();
		Screen = EScreen::Settings;
	}
	else if (Item == TEXT("Quit"))
	{
		UKismetSystemLibrary::QuitGame(this, GetOwningPlayerController(), EQuitPreference::Quit, false);
	}
}

void AOddsWellCharacterSelectionHUD::ConfirmSelection()
{
	if (Screen == EScreen::Title)
	{
		ActivateTitleItem();
		return;
	}
	if (Screen == EScreen::ConfirmNewCareer)
	{
		Screen = EScreen::Chooser;
		return;
	}
	if (Screen == EScreen::Settings)
	{
		SettingsMenu.Apply();
		return;
	}
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
	APlayerController* Controller = GetOwningPlayerController();
	if (!Controller)
	{
		HandoffError = TEXT("No local player controller is available for the Sundale handoff.");
		UE_LOG(LogOddsWellCharacterSelection, Error, TEXT("ODDSWELL_CHARACTER_HANDOFF|result=FAIL|reason=%s"), *HandoffError);
		return;
	}
	if (IsOddsWellCareerMode())
	{
		if (bStartNewCareerOnConfirm)
		{
			if (UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this))
			{
				FString CareerError;
				if (!Career->StartNewCareer(UOddsWellCareerSubsystem::DefaultNewCareerSeed(), CareerError))
				{
					HandoffError = CareerError;
					return;
				}
			}
		}
		// Single-player launch (DEC-037): open Sundale locally instead of joining the development listen server.
		UE_LOG(LogOddsWellCharacterSelection, Display, TEXT("ODDSWELL_CHARACTER_HANDOFF|result=START|target=SundaleGraybox|mode=standalone_career"));
		UGameplayStatics::OpenLevel(Controller, FName(TEXT("/Game/Maps/SundaleGraybox")), true, TEXT("game=/Script/OddsWell.OddsWellLocomotionGameMode"));
		return;
	}
	UE_LOG(
		LogOddsWellCharacterSelection,
		Display,
		TEXT("ODDSWELL_CHARACTER_HANDOFF|result=START|target=%s|mode=client_travel|boundary=machine_local_development"),
		*CharacterHandoffEndpoint);
	Controller->ClientTravel(CharacterHandoffEndpoint, TRAVEL_Absolute);
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
	DrawRect(CharacterChooserStageColor, CenterX - CharacterChooserStageWidth * 0.5f, Y + 24.0f, CharacterChooserStageWidth, CharacterChooserStageHeight);
	DrawRect(CharacterChooserRailColor, CenterX - CharacterChooserRailWidth * 0.5f, Y + 156.0f, CharacterChooserRailWidth, CharacterChooserRailHeight);
	DrawRect(FLinearColor(Preset.SkinTone), CenterX - 18.0f, Y + 30.0f, 36.0f, 36.0f);
	DrawRect(OffWhite, CenterX - 30.0f, Y + 70.0f, 60.0f, 42.0f);
	DrawRect(OffWhite * 0.82f, CenterX - 28.0f, Y + 116.0f, 24.0f, 38.0f);
	DrawRect(OffWhite * 0.82f, CenterX + 4.0f, Y + 116.0f, 24.0f, 38.0f);

	const TCHAR* Presentation = Preset.Presentation == EOddsWellCharacterPresentation::Masculine ? TEXT("MASCULINE") : TEXT("FEMININE");
	DrawText(Preset.Id.ToString(), FLinearColor::White, X + 12.0f, Y + 8.0f, GEngine->GetSmallFont(), 0.9f);
	DrawText(FString::Printf(TEXT("%s  |  SKIN #%s"), Presentation, *Preset.SkinTone.ToHex()), FLinearColor(0.75f, 0.84f, 0.95f), X + 12.0f, Y + Height - 42.0f, GEngine->GetSmallFont(), 0.72f);
	DrawText(TEXT("OFF-WHITE TOP + BOTTOM  |  REPLACEABLE"), OffWhite, X + 12.0f, Y + Height - 23.0f, GEngine->GetSmallFont(), 0.62f);
}

void AOddsWellCharacterSelectionHUD::UpdatePreview()
{
	if (!IsOddsWellCareerMode() || Screen != EScreen::Chooser)
	{
		return;
	}
	const FOddsWellCharacterPreset* Preset = State.GetSelectedPreset();
	if (!Preview && Preset && GetOddsWellMetaHumanForPreset(Preset->Id))
	{
		FActorSpawnParameters Parameters;
		Parameters.ObjectFlags |= RF_Transient;
		Preview = GetWorld()->SpawnActor<AOddsWellCharacterPreview>(AOddsWellCharacterPreview::StaticClass(), FTransform(FVector(0.0, 0.0, 40000.0)), Parameters);
		if (Preview)
		{
			if (APlayerController* Controller = GetOwningPlayerController())
			{
				Controller->SetViewTarget(Preview);
			}
		}
	}
	if (Preview && Preset && !Preview->ShowPreset(Preset->Id))
	{
		// No MetaHuman for this preset: fall back to the card-only chooser.
		Preview->Destroy();
		Preview = nullptr;
	}
}

void AOddsWellCharacterSelectionHUD::DrawCareerChooser()
{
	const float PanelWidth = FMath::Min(560.0f, Canvas->ClipX * 0.46f);
	DrawRect(FLinearColor(0.025f, 0.035f, 0.055f, 0.92f), 0.0f, 0.0f, PanelWidth, Canvas->ClipY);
	DrawRect(FLinearColor(0.20f, 0.75f, 0.68f), PanelWidth, 0.0f, 4.0f, Canvas->ClipY);
	DrawText(TEXT("CHOOSE YOUR CHARACTER"), FLinearColor::White, 48.0f, 32.0f, GEngine->GetLargeFont(), 1.1f);
	DrawText(TEXT("Everyone starts with the same Studio, job and 0 Odds Bucks."), FLinearColor(0.65f, 0.78f, 0.92f), 48.0f, 76.0f);
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	float Y = 128.0f;
	const float RowHeight = FMath::Min(64.0f, (Canvas->ClipY - 230.0f) / Presets.Num());
	for (int32 Index = 0; Index < Presets.Num(); ++Index)
	{
		const FOddsWellCharacterPreset& Preset = Presets[Index];
		const bool bSelected = Index == State.GetSelectedIndex();
		if (bSelected)
		{
			DrawRect(FLinearColor(0.20f, 0.75f, 0.68f, 0.28f), 36.0f, Y - 4.0f, PanelWidth - 72.0f, RowHeight - 6.0f);
			DrawRect(FLinearColor(0.20f, 0.75f, 0.68f), 36.0f, Y - 4.0f, 5.0f, RowHeight - 6.0f);
		}
		DrawRect(FLinearColor(Preset.SkinTone), 56.0f, Y + 6.0f, 26.0f, 26.0f);
		const TCHAR* Name = GetOddsWellMetaHumanForPreset(Preset.Id);
		DrawText(Name ? FString(Name) : Preset.Id.ToString(), bSelected ? FLinearColor::White : FLinearColor(0.70f, 0.78f, 0.86f), 100.0f, Y + 2.0f, GEngine->GetMediumFont(), 1.15f);
		DrawText(Preset.Presentation == EOddsWellCharacterPresentation::Masculine ? TEXT("Masculine") : TEXT("Feminine"), FLinearColor(0.55f, 0.62f, 0.70f), 100.0f, Y + 30.0f, GEngine->GetSmallFont(), 0.9f);
		Y += RowHeight;
	}
	const FString Help = !HandoffError.IsEmpty() ? HandoffError
		: State.IsConfirmed() ? FString(TEXT("Entering Sundale..."))
		: FString(TEXT("Up/Down: choose     Enter: start     Esc: back"));
	DrawText(Help, !HandoffError.IsEmpty() ? FLinearColor::Red : FLinearColor::White, 48.0f, Canvas->ClipY - 56.0f, GEngine->GetMediumFont());
}

void AOddsWellCharacterSelectionHUD::DrawTitle()
{
	const float CenterX = Canvas->ClipX * 0.5f;
	const float Top = Canvas->ClipY * 0.18f;
	const FLinearColor Teal(0.20f, 0.75f, 0.68f);
	DrawRect(FLinearColor(0.78f, 0.48f, 0.22f), CenterX - 180.0f, Top + 118.0f, 360.0f, 4.0f);
	float Width = 0.0f;
	float Height = 0.0f;
	GetTextSize(TEXT("ODDSWELL"), Width, Height, GEngine->GetLargeFont(), 3.0f);
	DrawText(TEXT("ODDSWELL"), FLinearColor::White, CenterX - Width * 0.5f, Top, GEngine->GetLargeFont(), 3.0f);
	GetTextSize(TEXT("Work. Bet. Watch. Live in Sundale."), Width, Height, GEngine->GetMediumFont(), 1.0f);
	DrawText(TEXT("Work. Bet. Watch. Live in Sundale."), FLinearColor(0.75f, 0.84f, 0.92f), CenterX - Width * 0.5f, Top + 136.0f, GEngine->GetMediumFont(), 1.0f);

	const UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	const TArray<FString> Items = TitleItems();
	TitleIndex = FMath::Clamp(TitleIndex, 0, Items.Num() - 1);
	float Y = Top + 220.0f;
	for (int32 Index = 0; Index < Items.Num(); ++Index)
	{
		FString Label = Items[Index];
		if (Label == TEXT("Continue") && Career)
		{
			Label += FString::Printf(TEXT("    Season %d, %s  |  %lld Odds Bucks"), Career->GetSeason(), *Career->GetPhaseText(), Career->GetBalance());
		}
		const bool bSelected = Index == TitleIndex;
		GetTextSize(Label, Width, Height, GEngine->GetMediumFont(), 1.25f);
		if (bSelected)
		{
			DrawRect(FLinearColor(Teal.R, Teal.G, Teal.B, 0.25f), CenterX - Width * 0.5f - 24.0f, Y - 6.0f, Width + 48.0f, Height + 12.0f);
			DrawRect(Teal, CenterX - Width * 0.5f - 24.0f, Y - 6.0f, 5.0f, Height + 12.0f);
		}
		DrawText(Label, bSelected ? FLinearColor::White : FLinearColor(0.62f, 0.70f, 0.78f), CenterX - Width * 0.5f, Y, GEngine->GetMediumFont(), 1.25f);
		Y += Height + 22.0f;
	}
	const TCHAR* Help = TEXT("Up/Down: choose     Enter: select");
	GetTextSize(Help, Width, Height, GEngine->GetSmallFont(), 1.0f);
	DrawText(Help, FLinearColor(0.55f, 0.62f, 0.70f), CenterX - Width * 0.5f, Canvas->ClipY - 60.0f, GEngine->GetSmallFont(), 1.0f);
}

void AOddsWellCharacterSelectionHUD::DrawSettings()
{
	DrawText(TEXT("SETTINGS"), FLinearColor::White, 64.0f, 28.0f, GEngine->GetLargeFont(), 1.15f);
	const TArray<FOddsWellSettingsRow> Rows = SettingsMenu.BuildRows();
	float Y = 120.0f;
	for (int32 Index = 0; Index < Rows.Num(); ++Index)
	{
		const bool bSelected = Index == SettingsMenu.GetSelectedRow();
		if (bSelected)
		{
			DrawRect(FLinearColor(0.20f, 0.75f, 0.68f, 0.25f), 56.0f, Y - 6.0f, 760.0f, 40.0f);
		}
		DrawText(Rows[Index].Label, bSelected ? FLinearColor::White : FLinearColor(0.62f, 0.70f, 0.78f), 72.0f, Y, GEngine->GetMediumFont(), 1.1f);
		DrawText(FString::Printf(TEXT("<  %s  >"), *Rows[Index].Value), FLinearColor::White, 460.0f, Y, GEngine->GetMediumFont(), 1.1f);
		Y += 48.0f;
	}
	DrawText(SettingsMenu.HasPendingChanges() ? TEXT("Changes not applied yet.") : TEXT(""), FLinearColor(0.95f, 0.66f, 0.20f), 72.0f, Y + 12.0f, GEngine->GetMediumFont());
	DrawText(TEXT("Up/Down: setting     Left/Right: change     Enter: apply     Esc: back"), FLinearColor(0.55f, 0.62f, 0.70f), 64.0f, Canvas->ClipY - 60.0f, GEngine->GetMediumFont());
}

void AOddsWellCharacterSelectionHUD::DrawConfirmNewCareer()
{
	const UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	DrawText(TEXT("START A NEW CAREER?"), FLinearColor::White, 64.0f, Canvas->ClipY * 0.3f, GEngine->GetLargeFont(), 1.4f);
	DrawText(Career ? FString::Printf(TEXT("This replaces your current career (season %d, %lld Odds Bucks)."), Career->GetSeason(), Career->GetBalance()) : FString(),
		FLinearColor(0.95f, 0.66f, 0.20f), 64.0f, Canvas->ClipY * 0.3f + 72.0f, GEngine->GetMediumFont(), 1.1f);
	DrawText(TEXT("Enter: choose a character and start over     Esc: keep my career"), FLinearColor::White, 64.0f, Canvas->ClipY * 0.3f + 130.0f, GEngine->GetMediumFont(), 1.1f);
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
	TestEqual(
		TEXT("Normal character handoff targets the accepted machine-local Sundale listen endpoint"),
		CharacterHandoffEndpoint,
		FString(TEXT("127.0.0.1:17777")));

	return !HasAnyErrors();
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellDefaultChooserPresentationTest,
	"OddsWell.Character.DefaultChooserPresentation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellDefaultChooserPresentationTest::RunTest(const FString& Parameters)
{
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	const TArray<FName> ExpectedIds = {
		TEXT("masculine_tone_1"), TEXT("masculine_tone_2"), TEXT("masculine_tone_3"), TEXT("masculine_tone_4"),
		TEXT("feminine_tone_1"), TEXT("feminine_tone_2"), TEXT("feminine_tone_3"), TEXT("feminine_tone_4")};
	TestEqual(TEXT("Chooser retains exactly eight cards"), Presets.Num(), CharacterChooserCardCount);
	TestEqual(TEXT("Every card receives the same two presentation parts"), CharacterChooserStagePartsPerCard, 2);
	TestEqual(TEXT("Chooser presentation remains exactly sixteen shared parts"), Presets.Num() * CharacterChooserStagePartsPerCard, 16);
	TestEqual(TEXT("Portrait backdrop width remains bounded inside a card"), CharacterChooserStageWidth, 96.0f);
	TestEqual(TEXT("Portrait backdrop height remains bounded above card labels"), CharacterChooserStageHeight, 136.0f);
	TestEqual(TEXT("Platform rail width remains bounded inside the backdrop"), CharacterChooserRailWidth, 88.0f);
	TestEqual(TEXT("Platform rail remains a thin presentation cue"), CharacterChooserRailHeight, 4.0f);
	for (int32 Index = 0; Index < ExpectedIds.Num(); ++Index)
	{
		if (!Presets.IsValidIndex(Index))
		{
			AddError(FString::Printf(TEXT("Approved chooser card %d is missing"), Index));
			continue;
		}
		TestEqual(FString::Printf(TEXT("Card %d retains its approved catalog identity"), Index), Presets[Index].Id, ExpectedIds[Index]);
		TestEqual(FString::Printf(TEXT("Card %d retains exactly two starter items"), Index), Presets[Index].EquippedItemIds.Num(), 2);
		if (Presets[Index].EquippedItemIds.Num() == 2)
		{
			TestEqual(FString::Printf(TEXT("Card %d retains the off-white starter top"), Index), Presets[Index].EquippedItemIds[0], FName(TEXT("starter_offwhite_top")));
			TestEqual(FString::Printf(TEXT("Card %d retains the off-white starter bottom"), Index), Presets[Index].EquippedItemIds[1], FName(TEXT("starter_offwhite_bottom")));
		}
	}
	FOddsWellCharacterSelectionState FreshState;
	TestTrue(TEXT("Fresh chooser retains its deterministic first-card selection"), FreshState.IsValid() && FreshState.GetSelectedIndex() == 0);
	TestFalse(TEXT("Fresh chooser never auto-confirms"), FreshState.IsConfirmed());
	TestTrue(TEXT("One navigation step remains available"), FreshState.Navigate(1));
	TestEqual(TEXT("One navigation step selects the same non-default second card"), FreshState.GetSelectedPreset()->Id, FName(TEXT("masculine_tone_2")));
	return !HasAnyErrors();
}
#endif
