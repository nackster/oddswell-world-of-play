// Single-player career interactions and HUD: the ticket-booth betting board, the arena game
// menu and replays, sleeping in the Studio, standings, and the morning report.
#include "PlaceholderLocomotion.h"

#include "Career/OddsWellCareer.h"
#include "Career/OddsWellCareerReplayActor.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/PlatformMisc.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "StudioHomeSave.h"
#include "UnrealClient.h"

namespace
{
	const FKey CareerKeys[] = {
		EKeys::E, EKeys::Enter, EKeys::Escape, EKeys::Up, EKeys::Down, EKeys::Left, EKeys::Right,
		EKeys::Hyphen, EKeys::Equals, EKeys::Z,
		EKeys::Gamepad_FaceButton_Bottom, EKeys::Gamepad_FaceButton_Right, EKeys::Gamepad_FaceButton_Left,
		EKeys::Gamepad_DPad_Up, EKeys::Gamepad_DPad_Down, EKeys::Gamepad_DPad_Left, EKeys::Gamepad_DPad_Right,
		EKeys::Gamepad_LeftShoulder, EKeys::Gamepad_RightShoulder, EKeys::Gamepad_Special_Right,
		EKeys::Tab, EKeys::Q, EKeys::K, EKeys::Gamepad_FaceButton_Top,
	};
	constexpr double CareerToastSeconds = 4.0;
	constexpr float CareerShopRadius = 350.0f;

	struct FCareerShop
	{
		EOddsWellObjectivePlace Place;
		const TCHAR* Name;
	};
	const FCareerShop CareerShops[] = {
		{EOddsWellObjectivePlace::ClothingStore, TEXT("the clothing store")},
		{EOddsWellObjectivePlace::FurnitureStore, TEXT("the furniture store")},
		{EOddsWellObjectivePlace::ApartmentKiosk, TEXT("apartment listings")},
	};
	const TCHAR* PauseRows[] = {TEXT("Resume"), TEXT("Settings"), TEXT("Quit to title"), TEXT("Quit game")};
	constexpr double CareerNoticeSeconds = 5.0;
	const FLinearColor Teal(0.20f, 0.75f, 0.68f, 1.0f);
	const FLinearColor Amber(0.95f, 0.66f, 0.20f, 1.0f);
	const FLinearColor Coral(0.85f, 0.32f, 0.22f, 1.0f);
	const FLinearColor PanelColor(0.025f, 0.055f, 0.08f, 0.94f);

	bool IsSundale(const UWorld* World)
	{
		return World && World->GetMapName().Contains(TEXT("SundaleGraybox"));
	}

	FString OddsText(const int64 ProbabilityE8)
	{
		const int64 Odds = OddsWellLeague::DecimalOddsE4(ProbabilityE8);
		return FString::Printf(TEXT("%lld.%02lld"), Odds / 10000, (Odds % 10000) / 100);
	}

	FString ClockText(const FOddsWellCareerReplayFrame& Frame)
	{
		if (Frame.Kind == TEXT("final"))
		{
			return Frame.Period > 4 ? TEXT("FINAL/OT") : TEXT("FINAL");
		}
		if (Frame.Period > 4)
		{
			return FString::Printf(TEXT("OT%d %02d:%02d"), Frame.Period - 4, Frame.ClockSeconds / 60, Frame.ClockSeconds % 60);
		}
		const int32 Remaining = Frame.ClockSeconds - (4 - Frame.Period) * 720;
		return FString::Printf(TEXT("Q%d %02d:%02d"), Frame.Period, Remaining / 60, Remaining % 60);
	}

	TArray<FString> SplitLines(const FString& Text)
	{
		TArray<FString> Lines;
		Text.ParseIntoArray(Lines, TEXT("\n"), false);
		return Lines;
	}
}

// ---- Character ------------------------------------------------------------------------------

bool AOddsWellPlaceholderCharacter::CareerKeyPressed(const APlayerController& OwnerController, const FKey& Key)
{
	return OwnerController.IsInputKeyDown(Key) && !CareerHeldKeys.Contains(Key.GetFName());
}

void AOddsWellPlaceholderCharacter::ShowCareerNotice(const FString& Message)
{
	CareerNotice = Message;
	CareerNoticeExpiresAt = FPlatformTime::Seconds() + CareerNoticeSeconds;
}

FString AOddsWellPlaceholderCharacter::GetCareerNotice() const
{
	return FPlatformTime::Seconds() < CareerNoticeExpiresAt ? CareerNotice : FString();
}

void AOddsWellPlaceholderCharacter::PollCareer()
{
	if (!IsLocallyControlled())
	{
		return;
	}
	APlayerController* OwnerController = Cast<APlayerController>(GetController());
	if (!OwnerController)
	{
		return;
	}
	CareerPrompt.Reset();
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	const bool bMenuKey = CareerKeyPressed(*OwnerController, EKeys::Escape) || CareerKeyPressed(*OwnerController, EKeys::Gamepad_Special_Right);
	const bool bPanelOpen = (Career && !Career->GetMorningReport().IsEmpty()) || bCareerBoardOpen || bCareerStandingsOpen || CareerReplay.IsValid() || bCareerTipoffArmed
		|| CareerShopPlace != INDEX_NONE || bCareerAchievementsOpen;
	if (Career && FPlatformTime::Seconds() >= CareerToastExpiresAt)
	{
		CareerToast = Career->PopAchievementToast();
		CareerToastExpiresAt = CareerToast.IsEmpty() ? 0.0 : FPlatformTime::Seconds() + CareerToastSeconds;
	}
	if (bCareerPauseOpen)
	{
		PollCareerPause(*OwnerController);
	}
	else if (bMenuKey && !bPanelOpen)
	{
		SetCareerPauseOpen(true);
	}
	else if (Career && Career->IsReady())
	{
		if (!Career->GetMorningReport().IsEmpty())
		{
			bCareerBoardOpen = false;
			if (CareerKeyPressed(*OwnerController, EKeys::Enter) || CareerKeyPressed(*OwnerController, EKeys::Gamepad_FaceButton_Bottom))
			{
				Career->DismissMorningReport();
			}
		}
		else if (bCareerAchievementsOpen)
		{
			if (CareerKeyPressed(*OwnerController, EKeys::K) || CareerKeyPressed(*OwnerController, EKeys::Escape) || CareerKeyPressed(*OwnerController, EKeys::Gamepad_FaceButton_Right))
			{
				bCareerAchievementsOpen = false;
			}
		}
		else if (IsSundale(GetWorld()))
		{
			PollCareerShop(*OwnerController);
			if (CareerShopPlace == INDEX_NONE)
			{
				PollCareerBoard(*OwnerController);
			}
		}
		else if (GetWorld()->GetAuthGameMode<AOddsWellStadiumGameMode>())
		{
			PollCareerStadium(*OwnerController);
		}
		else if (GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>())
		{
			PollCareerStudio(*OwnerController);
		}
		if (bCareerStandingsOpen && CareerKeyPressed(*OwnerController, EKeys::Escape))
		{
			bCareerStandingsOpen = false;
		}
		if (!bPanelOpen && CareerKeyPressed(*OwnerController, EKeys::K))
		{
			bCareerAchievementsOpen = true;
		}
	}
	for (const FKey& Key : CareerKeys)
	{
		if (OwnerController->IsInputKeyDown(Key))
		{
			CareerHeldKeys.Add(Key.GetFName());
		}
		else
		{
			CareerHeldKeys.Remove(Key.GetFName());
		}
	}
}

void AOddsWellPlaceholderCharacter::SetCareerPauseOpen(const bool bOpen)
{
	if (bCareerPauseOpen == bOpen)
	{
		return;
	}
	bCareerPauseOpen = bOpen;
	bCareerPauseSettings = false;
	CareerPauseRow = 0;
	if (APlayerController* OwnerController = Cast<APlayerController>(GetController()))
	{
		OwnerController->SetIgnoreMoveInput(bOpen);
		OwnerController->SetIgnoreLookInput(bOpen);
	}
	if (AOddsWellCareerReplayActor* Replay = CareerReplay.Get())
	{
		Replay->CustomTimeDilation = bOpen ? 0.0f : 1.0f;
	}
}

void AOddsWellPlaceholderCharacter::PollCareerPause(APlayerController& OwnerController)
{
	const bool bUp = CareerKeyPressed(OwnerController, EKeys::Up) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Up);
	const bool bDown = CareerKeyPressed(OwnerController, EKeys::Down) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Down);
	const bool bConfirm = CareerKeyPressed(OwnerController, EKeys::Enter) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Bottom);
	const bool bBack = CareerKeyPressed(OwnerController, EKeys::Escape) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Right) || CareerKeyPressed(OwnerController, EKeys::Gamepad_Special_Right);
	if (bCareerPauseSettings)
	{
		if (bUp) { CareerSettingsMenu.MoveSelection(-1); }
		if (bDown) { CareerSettingsMenu.MoveSelection(1); }
		if (CareerKeyPressed(OwnerController, EKeys::Left) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Left)) { CareerSettingsMenu.ChangeValue(-1); }
		if (CareerKeyPressed(OwnerController, EKeys::Right) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Right)) { CareerSettingsMenu.ChangeValue(1); }
		if (bConfirm) { CareerSettingsMenu.Apply(); }
		if (bBack) { bCareerPauseSettings = false; }
		return;
	}
	const int32 RowCount = UE_ARRAY_COUNT(PauseRows);
	if (bUp) { CareerPauseRow = (CareerPauseRow - 1 + RowCount) % RowCount; }
	if (bDown) { CareerPauseRow = (CareerPauseRow + 1) % RowCount; }
	if (bBack)
	{
		SetCareerPauseOpen(false);
		return;
	}
	if (!bConfirm)
	{
		return;
	}
	switch (CareerPauseRow)
	{
	case 0:
		SetCareerPauseOpen(false);
		break;
	case 1:
		CareerSettingsMenu.Open();
		bCareerPauseSettings = true;
		break;
	case 2:
		SetCareerPauseOpen(false);
		UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/Bootstrap")), true);
		break;
	default:
		UKismetSystemLibrary::QuitGame(this, &OwnerController, EQuitPreference::Quit, false);
		break;
	}
}

void AOddsWellPlaceholderCharacter::PollCareerBoard(APlayerController& OwnerController)
{
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	if (!bCareerBoardOpen)
	{
		if (IsNearOddsWellTicketBooth(GetActorLocation()))
		{
			CareerPrompt = TEXT("Press E to open today's betting board");
			if (CareerKeyPressed(OwnerController, EKeys::E))
			{
				bCareerBoardOpen = true;
				bCareerStandingsOpen = false;
				CareerBoardRow = 0;
				CareerBoardMarket = 0;
				const TArray<int32> Games = Career->GetTodaysGameIds();
				const FOddsWellCareerWager* Wager = Games.Num() ? Career->FindWager(Games[0], OddsWellLeague::EMarket::MatchWinner) : nullptr;
				CareerBoardSelection = Wager ? Wager->Selection : INDEX_NONE;
			}
		}
		return;
	}
	if (!IsNearOddsWellTicketBooth(GetActorLocation(), 300.0f)
		|| CareerKeyPressed(OwnerController, EKeys::Escape)
		|| CareerKeyPressed(OwnerController, EKeys::E)
		|| CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Right))
	{
		bCareerBoardOpen = false;
		return;
	}
	const TArray<int32> Games = Career->GetTodaysGameIds();
	if (Games.IsEmpty())
	{
		return;
	}
	const int32 PreviousRow = CareerBoardRow;
	const int32 PreviousMarket = CareerBoardMarket;
	if (CareerKeyPressed(OwnerController, EKeys::Up) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Up))
	{
		CareerBoardRow = (CareerBoardRow - 1 + Games.Num()) % Games.Num();
	}
	if (CareerKeyPressed(OwnerController, EKeys::Down) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Down))
	{
		CareerBoardRow = (CareerBoardRow + 1) % Games.Num();
	}
	CareerBoardRow = FMath::Clamp(CareerBoardRow, 0, Games.Num() - 1);
	const int32 GameId = Games[CareerBoardRow];
	const OddsWellLeague::FScheduledGame* Game = Career->FindGame(GameId);
	if (!Game)
	{
		return;
	}
	// Tab (or Y) moves through the markets this game offers.
	const int32 MarketCount = static_cast<int32>(OddsWellLeague::EMarket::Count);
	const int32 MarketStep = CareerKeyPressed(OwnerController, EKeys::Tab) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Top) ? 1
		: CareerKeyPressed(OwnerController, EKeys::Q) ? MarketCount - 1 : 0;
	CareerBoardMarket = FMath::Clamp(CareerBoardMarket, 0, MarketCount - 1);
	for (int32 Attempt = 0; Attempt < MarketCount; ++Attempt)
	{
		if (Attempt || MarketStep)
		{
			CareerBoardMarket = (CareerBoardMarket + FMath::Max(1, MarketStep)) % MarketCount;
		}
		if (OddsWellLeague::IsOutcomeAvailable(*Game, static_cast<OddsWellLeague::EMarket>(CareerBoardMarket)) || Game->bPlayed)
		{
			break;
		}
	}
	const OddsWellLeague::EMarket Market = static_cast<OddsWellLeague::EMarket>(CareerBoardMarket);
	const FOddsWellCareerWager* Existing = Career->FindWager(GameId, Market);
	if (CareerBoardRow != PreviousRow || CareerBoardMarket != PreviousMarket)
	{
		CareerBoardSelection = Existing ? Existing->Selection : INDEX_NONE;
	}
	if (Existing || Career->HaveTodaysGamesTippedOff())
	{
		return;
	}
	const int32 Outcomes = OddsWellLeague::MarketOutcomeCount(Market);
	if (CareerKeyPressed(OwnerController, EKeys::Left) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Left))
	{
		CareerBoardSelection = CareerBoardSelection == INDEX_NONE ? Outcomes - 1 : (CareerBoardSelection - 1 + Outcomes) % Outcomes;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Right) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Right))
	{
		CareerBoardSelection = CareerBoardSelection == INDEX_NONE ? 0 : (CareerBoardSelection + 1) % Outcomes;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Hyphen) || CareerKeyPressed(OwnerController, EKeys::Gamepad_LeftShoulder))
	{
		CareerBoardStake = FMath::Max<int64>(OddsWellLeague::MinimumStake, CareerBoardStake - OddsWellLeague::StakeIncrement);
	}
	if (CareerKeyPressed(OwnerController, EKeys::Equals) || CareerKeyPressed(OwnerController, EKeys::Gamepad_RightShoulder))
	{
		CareerBoardStake = FMath::Min<int64>(OddsWellLeague::MaximumStake, CareerBoardStake + OddsWellLeague::StakeIncrement);
	}
	if (CareerKeyPressed(OwnerController, EKeys::Enter) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Bottom))
	{
		if (CareerBoardSelection == INDEX_NONE)
		{
			ShowCareerNotice(TEXT("Pick an outcome first with Left and Right."));
			return;
		}
		FString Error;
		if (!Career->PlaceWager(GameId, Market, CareerBoardSelection, CareerBoardStake, Error))
		{
			ShowCareerNotice(Error);
			return;
		}
		if (const FOddsWellCareerWager* Placed = Career->FindWager(GameId, Market))
		{
			ShowCareerNotice(FString::Printf(TEXT("Bet placed: %lld on %s at %s. Pays %lld if it wins. Balance: %lld"),
				Placed->Stake,
				*Career->DescribeWager(*Placed),
				*OddsText(Placed->WinProbabilityE8),
				OddsWellLeague::GrossReturn(Placed->Stake, Placed->WinProbabilityE8),
				Career->GetBalance()));
		}
	}
}

FString AOddsWellPlaceholderCharacter::GetCareerToast() const
{
	return FPlatformTime::Seconds() < CareerToastExpiresAt ? CareerToast : FString();
}

TArray<const FOddsWellCatalogItem*> AOddsWellPlaceholderCharacter::GetCareerShopItems() const
{
	TArray<const FOddsWellCatalogItem*> Items;
	switch (static_cast<EOddsWellObjectivePlace>(CareerShopPlace))
	{
	case EOddsWellObjectivePlace::ClothingStore:
		Items = GetOddsWellCatalogItems(EOddsWellCatalogKind::Top);
		Items.Append(GetOddsWellCatalogItems(EOddsWellCatalogKind::Bottom));
		break;
	case EOddsWellObjectivePlace::FurnitureStore:
		Items = GetOddsWellCatalogItems(EOddsWellCatalogKind::Furniture);
		break;
	case EOddsWellObjectivePlace::ApartmentKiosk:
		for (const FOddsWellCatalogItem* Item : GetOddsWellCatalogItems(EOddsWellCatalogKind::Apartment))
		{
			if (Item->Tier > 0)
			{
				Items.Add(Item);
			}
		}
		break;
	default:
		break;
	}
	return Items;
}

void AOddsWellPlaceholderCharacter::PollCareerShop(APlayerController& OwnerController)
{
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	if (CareerShopPlace == INDEX_NONE)
	{
		if (bCareerBoardOpen)
		{
			return;
		}
		for (const FCareerShop& Shop : CareerShops)
		{
			if (FVector::Dist2D(GetActorLocation(), GetOddsWellObjectiveLocation(Shop.Place)) <= CareerShopRadius)
			{
				CareerPrompt = FString::Printf(TEXT("Press E to browse %s"), Shop.Name);
				if (CareerKeyPressed(OwnerController, EKeys::E))
				{
					CareerShopPlace = static_cast<int32>(Shop.Place);
					CareerShopRow = 0;
					bCareerStandingsOpen = false;
				}
				return;
			}
		}
		return;
	}
	if (FVector::Dist2D(GetActorLocation(), GetOddsWellObjectiveLocation(static_cast<EOddsWellObjectivePlace>(CareerShopPlace))) > CareerShopRadius + 100.0f
		|| CareerKeyPressed(OwnerController, EKeys::Escape)
		|| CareerKeyPressed(OwnerController, EKeys::E)
		|| CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Right))
	{
		CareerShopPlace = INDEX_NONE;
		return;
	}
	const TArray<const FOddsWellCatalogItem*> Items = GetCareerShopItems();
	if (Items.IsEmpty())
	{
		return;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Up) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Up))
	{
		CareerShopRow = (CareerShopRow - 1 + Items.Num()) % Items.Num();
	}
	if (CareerKeyPressed(OwnerController, EKeys::Down) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Down))
	{
		CareerShopRow = (CareerShopRow + 1) % Items.Num();
	}
	CareerShopRow = FMath::Clamp(CareerShopRow, 0, Items.Num() - 1);
	if (!CareerKeyPressed(OwnerController, EKeys::Enter) && !CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Bottom))
	{
		return;
	}
	const FOddsWellCatalogItem& Item = *Items[CareerShopRow];
	FString Error;
	const bool bClothing = Item.Kind == EOddsWellCatalogKind::Top || Item.Kind == EOddsWellCatalogKind::Bottom;
	if (Career->OwnsItem(Item.Id))
	{
		if (!bClothing)
		{
			ShowCareerNotice(FString::Printf(TEXT("You already own the %s."), *Item.Name));
		}
		else if (Career->EquipItem(Item.Id, Error))
		{
			SyncOutfitComponents();
			ShowCareerNotice(FString::Printf(TEXT("Now wearing: %s"), *Item.Name));
		}
		else
		{
			ShowCareerNotice(Error);
		}
		return;
	}
	if (!Career->BuyItem(Item.Id, Error))
	{
		ShowCareerNotice(Error);
		return;
	}
	if (bClothing)
	{
		SyncOutfitComponents();
		ShowCareerNotice(FString::Printf(TEXT("Bought and wearing: %s. Balance: %lld"), *Item.Name, Career->GetBalance()));
	}
	else if (Item.Kind == EOddsWellCatalogKind::Apartment)
	{
		ShowCareerNotice(Career->IsSeasonGoalComplete()
			? FString::Printf(TEXT("You own the Penthouse - the top of Sundale! Season goal complete. Balance: %lld"), Career->GetBalance())
			: FString::Printf(TEXT("You moved into a %s. Your home is ready next time you go in. Balance: %lld"), *Item.Name, Career->GetBalance()));
	}
	else
	{
		ShowCareerNotice(FString::Printf(TEXT("Bought the %s - it will be in your home. Balance: %lld"), *Item.Name, Career->GetBalance()));
	}
}

void AOddsWellPlaceholderCharacter::CloseCareerReplay()
{
	if (AOddsWellCareerReplayActor* Replay = CareerReplay.Get())
	{
		Replay->Destroy();
	}
	CareerReplay.Reset();
	if (APlayerController* OwnerController = Cast<APlayerController>(GetController()))
	{
		OwnerController->SetViewTarget(this);
	}
	bCareerStadiumMenuOpen = true;
}

void AOddsWellPlaceholderCharacter::PollCareerStadium(APlayerController& OwnerController)
{
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	if (const AOddsWellCareerReplayActor* Replay = CareerReplay.Get())
	{
		bCareerStadiumMenuOpen = false;
		CareerPrompt = Replay->IsComplete()
			? TEXT("Final. Esc: back to tonight's games   E: leave the arena")
			: TEXT("S: skip to the final   Esc: back to tonight's games   E: leave the arena");
		if (CareerKeyPressed(OwnerController, EKeys::Escape) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Right))
		{
			CloseCareerReplay();
		}
		return;
	}
	bCareerStadiumMenuOpen = true;
	const TArray<int32> Games = Career->GetTodaysGameIds();
	if (Games.IsEmpty())
	{
		return;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Up) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Up))
	{
		CareerStadiumRow = (CareerStadiumRow - 1 + Games.Num()) % Games.Num();
		bCareerTipoffArmed = false;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Down) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Down))
	{
		CareerStadiumRow = (CareerStadiumRow + 1) % Games.Num();
		bCareerTipoffArmed = false;
	}
	CareerStadiumRow = FMath::Clamp(CareerStadiumRow, 0, Games.Num() - 1);
	if (CareerKeyPressed(OwnerController, EKeys::Escape) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Right))
	{
		bCareerTipoffArmed = false;
	}
	if (!CareerKeyPressed(OwnerController, EKeys::Enter) && !CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Bottom))
	{
		return;
	}
	FString Error;
	if (!Career->HaveTodaysGamesTippedOff())
	{
		if (!bCareerTipoffArmed)
		{
			bCareerTipoffArmed = true;
			return;
		}
		bCareerTipoffArmed = false;
		if (!Career->TipOffToday(Error))
		{
			ShowCareerNotice(Error);
			return;
		}
	}
	if (!StartCareerReplay(Games[CareerStadiumRow], Error))
	{
		ShowCareerNotice(Error);
	}
}

bool AOddsWellPlaceholderCharacter::StartCareerReplay(const int32 GameId, FString& OutError)
{
	FActorSpawnParameters Parameters;
	Parameters.ObjectFlags |= RF_Transient;
	AOddsWellCareerReplayActor* Replay = GetWorld()->SpawnActor<AOddsWellCareerReplayActor>(
		AOddsWellCareerReplayActor::StaticClass(), GetOddsWellStadiumReplayTransform(), Parameters);
	if (!Replay || !Replay->StartGame(GameId, OutError))
	{
		if (Replay)
		{
			Replay->Destroy();
		}
		if (OutError.IsEmpty())
		{
			OutError = TEXT("The game could not be shown.");
		}
		return false;
	}
	CareerReplay = Replay;
	bCareerStadiumMenuOpen = false;
	return true;
}

// ---- Scripted play-through (-CareerSmoke) ---------------------------------------------------
// Drives the same career functions the controls call, across city, arena and Studio, and saves
// a screenshot at each step so a build can be checked without hands on the keyboard.

namespace
{
	int32 GCareerSmokeStage = 0;
	float GCareerSmokeTimer = 0.0f;
	int64 GCareerSmokeStartBalance = 0;
	bool bGCareerSmokeShotTaken = false;
	float GCareerSmokeShotAge = 0.0f;

	void CareerSmokeShot(const TCHAR* Name)
	{
		FScreenshotRequest::RequestScreenshot(FString::Printf(TEXT("CareerSmoke_%s.png"), Name), true, false);
		UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|screenshot=%s"), Name);
	}

	void CareerSmokeFail(const FString& Reason)
	{
		UE_LOG(LogTemp, Error, TEXT("ODDSWELL_CAREER_SMOKE|result=FAIL|reason=%s"), *Reason);
		FPlatformMisc::RequestExit(false);
	}
}

void AOddsWellPlaceholderCharacter::RunCareerSmoke(const float DeltaSeconds)
{
	static const bool bSmoke = FParse::Param(FCommandLine::Get(), TEXT("CareerSmoke"));
	if (!bSmoke || !IsLocallyControlled())
	{
		return;
	}
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	if (!Career || !Career->IsReady())
	{
		CareerSmokeFail(TEXT("career_not_ready"));
		return;
	}
	static const bool bProgressSoak = FParse::Param(FCommandLine::Get(), TEXT("CareerProgressSoak"));
	if (bProgressSoak && GCareerSmokeStage < 3)
	{
		// First show the clothing store's catalog.
		GCareerSmokeTimer += DeltaSeconds;
		if (GCareerSmokeStage == 0 && GCareerSmokeTimer > 2.0f)
		{
			Career->DismissMorningReport();
			SetActorLocation(GetOddsWellObjectiveLocation(EOddsWellObjectivePlace::ClothingStore) + FVector(-300.0, 0.0, 220.0), false, nullptr, ETeleportType::TeleportPhysics);
			if (APlayerController* ShotController = Cast<APlayerController>(GetController()))
			{
				ShotController->SetControlRotation(FRotator::ZeroRotator);
			}
			CareerShopPlace = static_cast<int32>(EOddsWellObjectivePlace::ClothingStore);
			CareerShopRow = 1;
			GCareerSmokeStage = 1;
			GCareerSmokeTimer = 0.0f;
		}
		else if (GCareerSmokeStage == 1 && GCareerSmokeTimer > 2.0f)
		{
			CareerSmokeShot(TEXT("09_ClothingStore"));
			GCareerSmokeStage = 2;
			GCareerSmokeTimer = 0.0f;
		}
		else if (GCareerSmokeStage == 2 && GCareerSmokeTimer > 1.0f)
		{
			CareerShopPlace = INDEX_NONE;
			GCareerSmokeStage = 3;
		}
		return;
	}
	if (bProgressSoak && GCareerSmokeStage < 200)
	{
		// A casual player's career: a shift and two bets a day, buying the next home (or a small treat)
		// when affordable. Logs the day each home is reached, then shows the final home.
		FRandomStream Choices(20261024);
		FString SoakError;
		TArray<int32> TierDays = {1};
		int32 Day = 1;
		for (; Day <= 120 && !Career->IsSeasonGoalComplete(); ++Day)
		{
			bool bCredited = false;
			int64 Balance = 0;
			Career->WorkShift(bCredited, Balance, SoakError);
			const TArray<int32> Games = Career->GetTodaysGameIds();
			if (Games.Num() && Career->GetBalance() >= 200)
			{
				const OddsWellLeague::FScheduledGame* Game = Career->FindGame(Games[Choices.RandHelper(Games.Num())]);
				const int32 Favourite = OddsWellLeague::OutcomeProbabilityE8(*Game, OddsWellLeague::EMarket::MatchWinner, 0) >= OddsWellLeague::ProbabilityScale / 2 ? 0 : 1;
				Career->PlaceWager(Game->Id, OddsWellLeague::EMarket::MatchWinner, Favourite, 30, SoakError);
				const OddsWellLeague::EMarket Market = static_cast<OddsWellLeague::EMarket>(1 + Choices.RandHelper(4));
				Career->PlaceWager(Game->Id, Market, Choices.RandHelper(OddsWellLeague::MarketOutcomeCount(Market)), 20, SoakError);
			}
			const FOddsWellCatalogItem& NextHome = GetOddsWellApartmentTier(Career->GetHomeTier() + 1);
			if (Career->GetBalance() >= NextHome.Price + 150 && Career->BuyItem(NextHome.Id, SoakError))
			{
				TierDays.Add(Day);
			}
			else if (Day % 3 == 0)
			{
				// Furniture first (it shows in the final home), then clothes.
				TArray<const FOddsWellCatalogItem*> Treats = GetOddsWellCatalogItems(EOddsWellCatalogKind::Furniture);
				Treats.Append(GetOddsWellCatalogItems(EOddsWellCatalogKind::Top));
				Treats.Append(GetOddsWellCatalogItems(EOddsWellCatalogKind::Bottom));
				for (const FOddsWellCatalogItem* Item : Treats)
				{
					if (Item->Price > 0 && Career->GetPurchaseBlocker(*Item).IsEmpty()
						&& Career->GetBalance() - Item->Price >= 300 && Career->BuyItem(Item->Id, SoakError))
					{
						break;
					}
				}
			}
			if (!Career->SleepUntilTomorrow(SoakError))
			{
				CareerSmokeFail(FString::Printf(TEXT("progress_sleep_failed:%s"), *SoakError));
				return;
			}
			Career->DismissMorningReport();
		}
		TArray<FString> Days;
		for (const int32 TierDay : TierDays)
		{
			Days.Add(FString::FromInt(TierDay));
		}
		const bool bPass = Career->IsSeasonGoalComplete() && Career->HasAchievement(TEXT("penthouse"));
		UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_PROGRESS|result=%s|days=%d|tier_days=%s|job=%s|shifts=%d|bets=%d|furniture=%d|clothes=%d|achievements=%d/%d|balance=%lld"),
			bPass ? TEXT("PASS") : TEXT("FAIL"), Day - 1, *FString::Join(Days, TEXT(",")), Career->GetJob().Title, Career->GetShiftsWorked(),
			Career->GetWagerCount(), Career->CountOwned(EOddsWellCatalogKind::Furniture),
			Career->CountOwned(EOddsWellCatalogKind::Top) + Career->CountOwned(EOddsWellCatalogKind::Bottom),
			Career->GetAchievementCount(), GetOddsWellAchievements().Num(), Career->GetBalance());
		GCareerSmokeStage = 200;
		GCareerSmokeTimer = 0.0f;
		SaveOwnedOddsWellStudio(FVector(0.0, 0.0, 220.0), UseOddsWellStudioHomeQaSlot(), SoakError);
		UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/Bootstrap")), true, TEXT("game=/Script/OddsWell.OddsWellStudioGameMode"));
		return;
	}
	if (bProgressSoak)
	{
		GCareerSmokeTimer += DeltaSeconds;
		if (GCareerSmokeStage == 200 && GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>() && GCareerSmokeTimer > 3.0f)
		{
			CareerSmokeShot(TEXT("10_FinalHome"));
			GCareerSmokeStage = 201;
			GCareerSmokeTimer = 0.0f;
		}
		else if (GCareerSmokeStage == 201 && GCareerSmokeTimer > 2.0f)
		{
			bCareerAchievementsOpen = true;
			CareerSmokeShot(TEXT("11_Achievements"));
			GCareerSmokeStage = 202;
			GCareerSmokeTimer = 0.0f;
		}
		else if (GCareerSmokeStage == 202 && GCareerSmokeTimer > 2.0f)
		{
			FPlatformMisc::RequestExit(false);
		}
		return;
	}
	static const bool bSeasonSoak = FParse::Param(FCommandLine::Get(), TEXT("CareerSeasonSoak"));
	if (bSeasonSoak && GCareerSmokeStage != 100)
	{
		// Sleep through a whole season and its playoffs, saving every night, then exit.
		FString SoakError;
		int32 Nights = 0;
		while (Career->GetLeague().CompletedSeasons == 0 && Nights < 60)
		{
			if (!Career->SleepUntilTomorrow(SoakError))
			{
				CareerSmokeFail(FString::Printf(TEXT("soak_sleep_failed:%s"), *SoakError));
				return;
			}
			++Nights;
		}
		const bool bPass = Career->GetLeague().CompletedSeasons == 1 && Career->GetSeason() == 2 && Career->GetDay() == 1
			&& Career->GetLeague().LastChampion >= 0 && Career->GetMorningReport().Contains(TEXT("champions"));
		UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SOAK|result=%s|nights=%d|season=%d|day=%d|champion=%s|balance=%lld"),
			bPass ? TEXT("PASS") : TEXT("FAIL"), Nights, Career->GetSeason(), Career->GetDay(),
			*Career->GetTeamName(Career->GetLeague().LastChampion), Career->GetBalance());
		CareerSmokeShot(TEXT("09_Champion"));
		GCareerSmokeStage = 100;
		FPlatformMisc::RequestExit(false);
		return;
	}
	GCareerSmokeTimer += DeltaSeconds;
	GCareerSmokeShotAge += DeltaSeconds;
	auto Next = [](float) { ++GCareerSmokeStage; GCareerSmokeTimer = 0.0f; bGCareerSmokeShotTaken = false; };
	// Screenshots render on a later frame, so act only once the requested shot has been captured.
	auto ShotThenAct = [](const TCHAR* Name)
	{
		if (!bGCareerSmokeShotTaken)
		{
			CareerSmokeShot(Name);
			bGCareerSmokeShotTaken = true;
			GCareerSmokeShotAge = 0.0f;
			return false;
		}
		return GCareerSmokeShotAge > 0.75f;
	};
	FString Error;
	switch (GCareerSmokeStage)
	{
	case 0: // City arrival with the welcome report.
		if (GCareerSmokeTimer > 4.0f)
		{
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=arrival|metahuman=%s"), bMetaHumanActive ? TEXT("true") : TEXT("false"));
			CareerSmokeShot(TEXT("01_Welcome"));
			Next(0);
		}
		break;
	case 1:
		if (GCareerSmokeTimer > 1.0f)
		{
			Career->DismissMorningReport();
			GCareerSmokeStartBalance = Career->GetBalance();
			bool bCredited = false;
			int64 Balance = 0;
			AOddsWellLocomotionGameMode* GameMode = GetWorld()->GetAuthGameMode<AOddsWellLocomotionGameMode>();
			int64 Retry = 0;
			FString Command;
			if (!GameMode || !GameMode->TryCreditPlaceholderJob(bCredited, Balance, Retry, Command, Error) || !bCredited)
			{
				CareerSmokeFail(FString::Printf(TEXT("shift_failed:%s"), *Error));
				return;
			}
			bool bSecond = true;
			GameMode->TryCreditPlaceholderJob(bSecond, Balance, Retry, Command, Error);
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=shift|credited=true|second_shift_credited=%s|balance=%lld"), bSecond ? TEXT("true") : TEXT("false"), Career->GetBalance());
			if (bSecond)
			{
				CareerSmokeFail(TEXT("second_shift_paid"));
				return;
			}
			Next(0);
		}
		break;
	case 2: // Walk up to the ticket booth and open the board.
		if (GCareerSmokeTimer > 1.0f)
		{
			SetActorLocation(GetOddsWellTicketBoothLocation() + FVector(-150.0, 0.0, 220.0));
			bCareerBoardOpen = true;
			CareerBoardRow = 0;
			CareerBoardSelection = 0;
			CareerBoardStake = 40;
			Next(0);
		}
		break;
	case 3:
		if (GCareerSmokeTimer > 2.0f)
		{
			if (!ShotThenAct(TEXT("02_Board")))
			{
				break;
			}
			const TArray<int32> Games = Career->GetTodaysGameIds();
			if (Games.Num() != 4 || !Career->PlaceWager(Games[0], OddsWellLeague::EMarket::MatchWinner, 0, 30, Error)
				|| !Career->PlaceWager(Games[0], OddsWellLeague::EMarket::HomeStarPoints, 0, 10, Error))
			{
				CareerSmokeFail(FString::Printf(TEXT("wager_failed:%s"), *Error));
				return;
			}
			FString Duplicate;
			if (Career->PlaceWager(Games[0], OddsWellLeague::EMarket::MatchWinner, 1, 10, Duplicate))
			{
				CareerSmokeFail(TEXT("duplicate_wager_accepted"));
				return;
			}
			CareerBoardMarket = static_cast<int32>(OddsWellLeague::EMarket::HomeStarPoints);
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=wager|game=%d|stake=40|markets=2|balance=%lld|duplicate_rejected=true"), Games[0], Career->GetBalance());
			Next(0);
		}
		break;
	case 4:
		if (GCareerSmokeTimer > 1.5f)
		{
			if (!ShotThenAct(TEXT("03_BetPlaced")))
			{
				break;
			}
			bCareerBoardOpen = false;
			UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/Bootstrap")), true, TEXT("game=/Script/OddsWell.OddsWellStadiumGameMode"));
			Next(0);
		}
		break;
	case 5: // Arena: tonight's games.
		if (GetWorld()->GetAuthGameMode<AOddsWellStadiumGameMode>() && GCareerSmokeTimer > 3.0f)
		{
			if (!ShotThenAct(TEXT("04_ArenaMenu")))
			{
				break;
			}
			if (!Career->TipOffToday(Error) || !StartCareerReplay(Career->GetTodaysGameIds()[0], Error))
			{
				CareerSmokeFail(FString::Printf(TEXT("tipoff_failed:%s"), *Error));
				return;
			}
			FString Late;
			if (Career->PlaceWager(Career->GetTodaysGameIds()[1], OddsWellLeague::EMarket::MatchWinner, 0, 10, Late))
			{
				CareerSmokeFail(TEXT("wager_after_tipoff_accepted"));
				return;
			}
			if (Career->GetBalance() != GCareerSmokeStartBalance + 60)
			{
				CareerSmokeFail(TEXT("bet_settled_before_the_game_was_watched"));
				return;
			}
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=tipoff|late_wager_rejected=true|balance_unchanged_until_watched=%lld"), Career->GetBalance());
			Next(0);
		}
		break;
	case 6:
		if (GCareerSmokeTimer > 6.0f)
		{
			if (!ShotThenAct(TEXT("05_GameLive")))
			{
				break;
			}
			if (AOddsWellCareerReplayActor* Replay = CareerReplay.Get())
			{
				Replay->SkipToFinal();
			}
			Next(0);
		}
		break;
	case 7:
		if (GCareerSmokeTimer > 1.5f)
		{
			if (!ShotThenAct(TEXT("06_GameFinal")))
			{
				break;
			}
			SaveOwnedOddsWellStudio(FVector(0.0, 0.0, 220.0), UseOddsWellStudioHomeQaSlot(), Error);
			UGameplayStatics::OpenLevel(this, FName(TEXT("/Game/Maps/Bootstrap")), true, TEXT("game=/Script/OddsWell.OddsWellStudioGameMode"));
			Next(0);
		}
		break;
	case 8: // Studio: sleep until tomorrow.
		if (GetWorld()->GetAuthGameMode<AOddsWellStudioGameMode>() && GCareerSmokeTimer > 3.0f)
		{
			if (!ShotThenAct(TEXT("07_Studio")))
			{
				break;
			}
			const int32 DayBefore = Career->GetDay();
			if (!Career->SleepUntilTomorrow(Error))
			{
				CareerSmokeFail(FString::Printf(TEXT("sleep_failed:%s"), *Error));
				return;
			}
			const TArray<FOddsWellCareerWager> DayWagers = Career->GetWagersForDay(Career->GetSeason(), DayBefore);
			int64 Payouts = 0;
			int32 Won = 0;
			bool bAllSettled = DayWagers.Num() == 2;
			for (const FOddsWellCareerWager& Settled : DayWagers)
			{
				bAllSettled &= Settled.Status != EOddsWellCareerWagerStatus::Pending;
				Payouts += Settled.Status == EOddsWellCareerWagerStatus::Won ? Settled.Payout : 0;
				Won += Settled.Status == EOddsWellCareerWagerStatus::Won ? 1 : 0;
			}
			const int64 Expected = GCareerSmokeStartBalance + 100 - 40 + Payouts;
			const bool bPass = bAllSettled && Career->GetDay() == DayBefore + 1 && Career->GetBalance() == Expected && !Career->HasWorkedToday();
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=sleep|day=%d|wagers=%d|won=%d|payout=%lld|balance=%lld|expected=%lld|result=%s"),
				Career->GetDay(), DayWagers.Num(), Won, Payouts, Career->GetBalance(), Expected, bPass ? TEXT("PASS") : TEXT("FAIL"));
			if (!bPass)
			{
				CareerSmokeFail(TEXT("settlement_mismatch"));
				return;
			}
			Next(0);
		}
		break;
	case 9:
		if (GCareerSmokeTimer > 2.0f)
		{
			CareerSmokeShot(TEXT("08_MorningReport"));
			Next(0);
		}
		break;
	case 10:
		if (GCareerSmokeTimer > 2.0f)
		{
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|result=PASS|season=%d|day=%d|balance=%lld"), Career->GetSeason(), Career->GetDay(), Career->GetBalance());
			FPlatformMisc::RequestExit(false);
			Next(0);
		}
		break;
	default:
		break;
	}
}

void AOddsWellPlaceholderCharacter::PollCareerStudio(APlayerController& OwnerController)
{
	UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	CareerPrompt = Career->HaveTodaysGamesTippedOff()
		? TEXT("Press Z to sleep until tomorrow")
		: TEXT("Press Z to sleep until tomorrow - tonight's games will be played while you sleep");
	if (CareerKeyPressed(OwnerController, EKeys::Z) || CareerKeyPressed(OwnerController, EKeys::Gamepad_FaceButton_Left))
	{
		FString Error;
		if (!Career->SleepUntilTomorrow(Error))
		{
			ShowCareerNotice(Error);
		}
	}
}

// ---- HUD ------------------------------------------------------------------------------------

float AOddsWellSportsbookHUD::DrawCareerPanel(const TArray<FString>& Lines, const float X, const float Y, const float Width, const FLinearColor& Accent, const float Scale, const int32 HighlightLine)
{
	const float LineHeight = 26.0f * Scale;
	const float Padding = 16.0f * Scale;
	const float Height = Lines.Num() * LineHeight + Padding * 2.0f;
	DrawRect(PanelColor, X, Y, Width, Height);
	DrawRect(Accent, X, Y, 5.0f, Height);
	for (int32 Index = 0; Index < Lines.Num(); ++Index)
	{
		const float LineY = Y + Padding + Index * LineHeight;
		if (Index == HighlightLine)
		{
			DrawRect(FLinearColor(Accent.R, Accent.G, Accent.B, 0.28f), X + 8.0f, LineY - 2.0f, Width - 16.0f, LineHeight);
		}
		DrawText(Lines[Index], FLinearColor::White, X + 20.0f, LineY, nullptr, Scale);
	}
	return Y + Height;
}

void AOddsWellSportsbookHUD::DrawCareerOverlay(const AOddsWellPlaceholderCharacter& Character)
{
	const UOddsWellCareerSubsystem* Career = UOddsWellCareerSubsystem::Get(this);
	const float CanvasWidth = Canvas->SizeX;
	const float CanvasHeight = Canvas->SizeY;
	const float Scale = CanvasWidth < 1100.0f ? 0.82f : 1.0f;
	if (!Career || !Career->IsReady())
	{
		DrawCareerPanel({TEXT("Career unavailable"), Career ? Career->GetLoadError() : FString()}, 24.0f, 24.0f, 620.0f, Coral, Scale);
		return;
	}

	// Scoreboard while a game is on.
	if (const AOddsWellCareerReplayActor* Replay = Character.GetCareerReplay())
	{
		if (const FOddsWellCareerReplayFrame* Frame = Replay->GetCurrentFrame())
		{
			const FOddsWellCareerReplay& Game = Replay->GetReplay();
			const float Width = FMath::Min(760.0f, CanvasWidth - 48.0f);
			DrawCareerPanel({
				FString::Printf(TEXT("%s  %d   -   %d  %s"), *Game.AwayTeam, Frame->AwayScore, Frame->HomeScore, *Game.HomeTeam),
				FString::Printf(TEXT("%s    %s"), *ClockText(*Frame), *Frame->Label),
			}, (CanvasWidth - Width) * 0.5f, 20.0f, Width, Teal, Scale * 1.15f);
		}
	}

	// Day status.
	const TArray<int32> Today = Career->GetTodaysGameIds();
	const float StatusBottom = DrawCareerPanel({
		FString::Printf(TEXT("SEASON %d   %s"), Career->GetSeason(), *Career->GetPhaseText()),
		FString::Printf(TEXT("Balance: %lld Odds Bucks"), Career->GetBalance()),
		FString::Printf(TEXT("Job: %s - %s"), Career->GetJob().Title,
			Career->HasWorkedToday() ? TEXT("done for today") : *FString::Printf(TEXT("shift available (+%lld)"), Career->GetJob().Pay)),
		Today.IsEmpty() ? FString(TEXT("No games today"))
			: FString::Printf(TEXT("Today: %d game%s - %s"), Today.Num(), Today.Num() == 1 ? TEXT("") : TEXT("s"),
				Career->HaveTodaysGamesTippedOff() ? TEXT("final scores in") : TEXT("betting open")),
		FString::Printf(TEXT("Home: %s"), *GetOddsWellApartmentTier(Career->GetHomeTier()).Name),
		Career->IsSeasonGoalComplete() ? FString(TEXT("Goal complete: you own the Penthouse"))
			: FString::Printf(TEXT("Goal: own the Penthouse - next home %s (%lld)"),
				*GetOddsWellApartmentTier(Career->GetHomeTier() + 1).Name, GetOddsWellApartmentTier(Career->GetHomeTier() + 1).Price),
		FString::Printf(TEXT("L: standings   K: achievements (%d/%d)"), Career->GetAchievementCount(), GetOddsWellAchievements().Num()),
	}, 24.0f, Character.GetCareerReplay() ? 140.0f : 24.0f, 470.0f * Scale, Teal, Scale * 0.85f);

	if (Character.IsCareerPauseOpen())
	{
		DrawRect(FLinearColor(0.0f, 0.0f, 0.0f, 0.55f), 0.0f, 0.0f, CanvasWidth, CanvasHeight);
		const float Width = FMath::Min(640.0f, CanvasWidth - 48.0f);
		const float X = (CanvasWidth - Width) * 0.5f;
		if (Character.IsCareerPauseSettingsOpen())
		{
			const FOddsWellSettingsMenu& Menu = Character.GetCareerSettingsMenu();
			TArray<FString> Lines = {TEXT("SETTINGS"), TEXT("")};
			for (const FOddsWellSettingsRow& Row : Menu.BuildRows())
			{
				Lines.Add(FString::Printf(TEXT("%-22s <  %s  >"), *Row.Label, *Row.Value));
			}
			Lines.Add(TEXT(""));
			Lines.Add(Menu.HasPendingChanges() ? TEXT("Enter: apply changes   Esc: back") : TEXT("Left/Right: change   Enter: apply   Esc: back"));
			DrawCareerPanel(Lines, X, CanvasHeight * 0.2f, Width, Teal, Scale, Menu.GetSelectedRow() + 2);
		}
		else
		{
			TArray<FString> Lines = {TEXT("PAUSED"), TEXT("")};
			for (const TCHAR* Row : PauseRows)
			{
				Lines.Add(Row);
			}
			Lines.Add(TEXT(""));
			Lines.Add(TEXT("Your career saves automatically."));
			DrawCareerPanel(Lines, X, CanvasHeight * 0.26f, Width, Teal, Scale * 1.1f, Character.GetCareerPauseRow() + 2);
		}
		return;
	}

	// First-day guide: a checklist plus a marker toward the next place to go.
	const UOddsWellGameUserSettings* Settings = UOddsWellGameUserSettings::Get();
	if (!Career->IsTutorialComplete() && Career->GetMorningReport().IsEmpty() && !Character.GetCareerReplay())
	{
		struct FGuideStep { EOddsWellTutorialStep Step; const TCHAR* Text; EOddsWellObjectivePlace Place; const TCHAR* PlaceName; };
		const FGuideStep Steps[] = {
			{EOddsWellTutorialStep::Shift, TEXT("Work a shift at the Job marker"), EOddsWellObjectivePlace::Job, TEXT("Job")},
			{EOddsWellTutorialStep::Bet, TEXT("Place a bet at the ticket booth"), EOddsWellObjectivePlace::TicketBooth, TEXT("Ticket booth")},
			{EOddsWellTutorialStep::Watch, TEXT("Watch a game at the arena"), EOddsWellObjectivePlace::Arena, TEXT("Arena")},
			{EOddsWellTutorialStep::Sleep, TEXT("Sleep in your Studio"), EOddsWellObjectivePlace::Studio, TEXT("Studio")},
		};
		TArray<FString> Lines = {TEXT("GETTING STARTED")};
		const FGuideStep* Next = nullptr;
		int32 NextLine = INDEX_NONE;
		for (const FGuideStep& Step : Steps)
		{
			const bool bDone = (Career->GetTutorialFlags() & static_cast<int32>(Step.Step)) != 0;
			if (!bDone && !Next)
			{
				Next = &Step;
				NextLine = Lines.Num();
			}
			Lines.Add(FString::Printf(TEXT("%s  %s"), bDone ? TEXT("[x]") : TEXT("[  ]"), Step.Text));
		}
		const float GuideY = StatusBottom + 12.0f;
		DrawCareerPanel(Lines, 24.0f, GuideY, 470.0f * Scale, Amber, Scale * 0.85f, NextLine);

		const APawn* Pawn = GetOwningPawn();
		if (Next && Pawn && IsSundale(GetWorld()))
		{
			const FVector Target = GetOddsWellObjectiveLocation(Next->Place) + FVector(0.0, 0.0, 250.0);
			const float Meters = FVector::Dist2D(Pawn->GetActorLocation(), Target) / 100.0f;
			const FVector Screen = Project(Target);
			const FString Label = FString::Printf(TEXT("%s  %.0f m"), Next->PlaceName, Meters);
			if (Screen.Z > 0.0f && Screen.X > 0.0f && Screen.X < CanvasWidth && Screen.Y > 0.0f && Screen.Y < CanvasHeight)
			{
				DrawRect(Amber, Screen.X - 7.0f, Screen.Y - 7.0f, 14.0f, 14.0f);
				DrawText(Label, FLinearColor::White, Screen.X + 14.0f, Screen.Y - 10.0f, nullptr, Scale);
			}
			else if (PlayerOwner)
			{
				// Off screen: say which way to turn.
				const FRotator View = PlayerOwner->GetControlRotation();
				const FVector ToTarget = (Target - Pawn->GetActorLocation()).GetSafeNormal2D();
				const float Angle = FMath::FindDeltaAngleDegrees(View.Yaw, ToTarget.Rotation().Yaw);
				const TCHAR* Direction = FMath::Abs(Angle) > 135.0f ? TEXT("behind you") : Angle > 0.0f ? TEXT("to your right") : TEXT("to your left");
				DrawCareerPanel({FString::Printf(TEXT("%s - %s"), *Label, Direction)}, (CanvasWidth - 420.0f) * 0.5f, 24.0f, 420.0f, Amber, Scale);
			}
		}
	}
	(void)Settings;

	// Centre panels sit to the right of the status column when the screen allows it.
	const float CenterX = FMath::Max((CanvasWidth - 900.0f) * 0.5f, FMath::Min(24.0f + 470.0f * Scale + 20.0f, CanvasWidth * 0.3f));
	const float CenterWidth = FMath::Min(900.0f, CanvasWidth - CenterX - 24.0f);

	if (!Career->GetMorningReport().IsEmpty())
	{
		TArray<FString> Lines = SplitLines(Career->GetMorningReport());
		Lines.Add(TEXT(""));
		Lines.Add(TEXT("Press Enter to continue"));
		DrawCareerPanel(Lines, CenterX, FMath::Max(180.0f, CanvasHeight * 0.22f), CenterWidth, Amber, Scale);
		return;
	}

	if (Character.IsCareerStandingsOpen())
	{
		TArray<FString> Lines = {FString::Printf(TEXT("STANDINGS - SEASON %d"), Career->GetSeason())};
		Lines.Append(Career->BuildStandingsLines());
		const OddsWellLeague::FLeagueState& League = Career->GetLeague();
		if (League.Phase != OddsWellLeague::ESeasonPhase::Regular)
		{
			Lines.Add(TEXT(""));
			Lines.Add(TEXT("PLAYOFFS (best of three)"));
			for (const OddsWellLeague::FSeriesState* Series : {&League.Semifinals[0], &League.Semifinals[1]})
			{
				Lines.Add(FString::Printf(TEXT("Semifinal: %s %d - %d %s"), *Career->GetTeamName(Series->HighSeed), Series->HighWins, Series->LowWins, *Career->GetTeamName(Series->LowSeed)));
			}
			if (League.Phase == OddsWellLeague::ESeasonPhase::Final)
			{
				Lines.Add(FString::Printf(TEXT("Final: %s %d - %d %s"), *Career->GetTeamName(League.FinalSeries.HighSeed), League.FinalSeries.HighWins, League.FinalSeries.LowWins, *Career->GetTeamName(League.FinalSeries.LowSeed)));
			}
		}
		Lines.Add(TEXT(""));
		Lines.Add(TEXT("TODAY"));
		for (const int32 Id : Today)
		{
			if (const OddsWellLeague::FScheduledGame* Game = Career->FindGame(Id))
			{
				Lines.Add(Career->DescribeGameForPlayer(*Game));
			}
		}
		Lines.Add(TEXT(""));
		Lines.Add(TEXT("L or Esc: close"));
		DrawCareerPanel(Lines, CenterX, FMath::Max(180.0f, CanvasHeight * 0.22f), CenterWidth, Teal, Scale * 0.9f);
	}

	if (Character.IsCareerBoardOpen())
	{
		TArray<FString> Lines = {TEXT("TODAY'S BOARD"), TEXT("")};
		int32 Highlight = INDEX_NONE;
		for (int32 Row = 0; Row < Today.Num(); ++Row)
		{
			const OddsWellLeague::FScheduledGame* Game = Career->FindGame(Today[Row]);
			if (!Game)
			{
				continue;
			}
			if (Row == Character.GetCareerBoardRow())
			{
				Highlight = Lines.Num();
			}
			FString Line;
			if (Game->bPlayed)
			{
				Line = Career->DescribeGameForPlayer(*Game);
			}
			else
			{
				Line = FString::Printf(TEXT("%s  %s     at     %s  %s"),
					*Career->GetTeamName(Game->Away), *OddsText(OddsWellLeague::OutcomeProbabilityE8(*Game, OddsWellLeague::EMarket::MatchWinner, 1)),
					*Career->GetTeamName(Game->Home), *OddsText(OddsWellLeague::OutcomeProbabilityE8(*Game, OddsWellLeague::EMarket::MatchWinner, 0)));
			}
			if (const int32 Bets = Career->CountWagersOnGame(Game->Id))
			{
				Line += FString::Printf(TEXT("    [%d bet%s]"), Bets, Bets == 1 ? TEXT("") : TEXT("s"));
			}
			Lines.Add(Line);
		}
		Lines.Add(TEXT(""));
		if (Career->HaveTodaysGamesTippedOff())
		{
			Lines.Add(TEXT("Tonight's games have been played. Watch them at the arena, or sleep to see the results."));
		}
		else if (Today.IsValidIndex(Character.GetCareerBoardRow()))
		{
			const OddsWellLeague::FScheduledGame* Game = Career->FindGame(Today[Character.GetCareerBoardRow()]);
			const int32 Selection = Character.GetCareerBoardSelection();
			const OddsWellLeague::EMarket Market = static_cast<OddsWellLeague::EMarket>(Character.GetCareerBoardMarket());
			if (Game && OddsWellLeague::IsOutcomeAvailable(*Game, Market))
			{
				const FOddsWellCareerWager* Existing = Career->FindWager(Game->Id, Market);
				Lines.Add(FString::Printf(TEXT("MARKET %d OF %d: %s"), Character.GetCareerBoardMarket() + 1,
					static_cast<int32>(OddsWellLeague::EMarket::Count), *Career->GetMarketName(*Game, Market).ToUpper()));
				for (int32 Outcome = 0; Outcome < OddsWellLeague::MarketOutcomeCount(Market); ++Outcome)
				{
					const bool bPicked = Existing ? Existing->Selection == Outcome : Selection == Outcome;
					Lines.Add(FString::Printf(TEXT("%s %-28s %s%s"), bPicked ? TEXT(">") : TEXT(" "),
						*Career->DescribeOutcome(*Game, Market, Outcome),
						*OddsText(Existing && bPicked ? Existing->WinProbabilityE8 : OddsWellLeague::OutcomeProbabilityE8(*Game, Market, Outcome)),
						Existing && bPicked ? *FString::Printf(TEXT("    [your bet: %lld]"), Existing->Stake) : TEXT("")));
				}
				Lines.Add(TEXT(""));
				if (Existing)
				{
					Lines.Add(TEXT("You already have a bet in this market. Tab: another market."));
				}
				else if (Selection != INDEX_NONE)
				{
					const int64 Probability = OddsWellLeague::OutcomeProbabilityE8(*Game, Market, Selection);
					Lines.Add(FString::Printf(TEXT("Pick: %s   Stake: %lld   Pays: %lld if it wins"),
						*Career->DescribeOutcome(*Game, Market, Selection), Character.GetCareerBoardStake(),
						OddsWellLeague::GrossReturn(Character.GetCareerBoardStake(), Probability)));
				}
				else
				{
					Lines.Add(FString::Printf(TEXT("Pick an outcome.   Stake: %lld"), Character.GetCareerBoardStake()));
				}
			}
			Lines.Add(TEXT("Up/Down: game   Tab: market   Left/Right: outcome   - / =: stake   Enter: place bet"));
		}
		Lines.Add(TEXT("Odds are set before tipoff and include a small house margin. E or Esc: close"));
		DrawCareerPanel(Lines, CenterX, FMath::Max(180.0f, CanvasHeight * 0.22f), CenterWidth, Amber, Scale * 0.95f, Highlight);
	}

	if (Character.IsCareerStadiumMenuOpen())
	{
		TArray<FString> Lines = {TEXT("TONIGHT AT THE ARENA"), TEXT("")};
		int32 Highlight = INDEX_NONE;
		for (int32 Row = 0; Row < Today.Num(); ++Row)
		{
			if (const OddsWellLeague::FScheduledGame* Game = Career->FindGame(Today[Row]))
			{
				if (Row == Character.GetCareerStadiumRow())
				{
					Highlight = Lines.Num();
				}
				Lines.Add(Career->DescribeGameForPlayer(*Game));
			}
		}
		Lines.Add(TEXT(""));
		if (Today.IsEmpty())
		{
			Lines.Add(TEXT("No games tonight."));
		}
		else if (Character.IsCareerTipoffArmed())
		{
			Lines.Add(TEXT("Start tonight's games? Betting closes for today. Enter: tip off   Esc: not yet"));
		}
		else
		{
			Lines.Add(Career->HaveTodaysGamesTippedOff()
				? TEXT("Up/Down: game   Enter: watch the replay   E: leave the arena")
				: TEXT("Up/Down: game   Enter: watch live (starts tonight's games)   E: leave the arena"));
		}
		DrawCareerPanel(Lines, CenterX, FMath::Max(300.0f, CanvasHeight * 0.36f), CenterWidth, Teal, Scale, Highlight);
	}

	if (Character.GetCareerShopPlace() != INDEX_NONE)
	{
		const EOddsWellObjectivePlace Place = static_cast<EOddsWellObjectivePlace>(Character.GetCareerShopPlace());
		TArray<FString> Lines = {Place == EOddsWellObjectivePlace::ClothingStore ? TEXT("CLOTHING STORE")
			: Place == EOddsWellObjectivePlace::FurnitureStore ? TEXT("FURNITURE STORE") : TEXT("APARTMENT LISTINGS"), TEXT("")};
		int32 Highlight = INDEX_NONE;
		const TArray<const FOddsWellCatalogItem*> Items = Character.GetCareerShopItems();
		EOddsWellCatalogKind Section = Items.Num() ? Items[0]->Kind : EOddsWellCatalogKind::Top;
		for (int32 Row = 0; Row < Items.Num(); ++Row)
		{
			const FOddsWellCatalogItem& Item = *Items[Row];
			if (Item.Kind != Section)
			{
				Section = Item.Kind;
				Lines.Add(TEXT(""));
			}
			const bool bOwned = Career->OwnsItem(Item.Id);
			const bool bWorn = (Item.Kind == EOddsWellCatalogKind::Top || Item.Kind == EOddsWellCatalogKind::Bottom) && Career->GetEquipped(Item.Kind) == Item.Id;
			const FString Blocker = Career->GetPurchaseBlocker(Item);
			const FString Status = bWorn ? TEXT("wearing") : bOwned ? TEXT("owned")
				: Blocker.IsEmpty() ? FString::Printf(TEXT("%lld"), Item.Price) : FString::Printf(TEXT("%lld - %s"), Item.Price, *(Blocker.Left(1).ToLower() + Blocker.Mid(1)));
			if (Row == Character.GetCareerShopRow())
			{
				Highlight = Lines.Num();
			}
			Lines.Add(FString::Printf(TEXT("%-26s %s"), *Item.Name, *Status));
		}
		Lines.Add(TEXT(""));
		Lines.Add(FString::Printf(TEXT("Balance: %lld Odds Bucks"), Career->GetBalance()));
		Lines.Add(Place == EOddsWellObjectivePlace::ClothingStore ? TEXT("Up/Down: item   Enter: buy or wear   E or Esc: close") : TEXT("Up/Down: item   Enter: buy   E or Esc: close"));
		DrawCareerPanel(Lines, CenterX, FMath::Max(120.0f, CanvasHeight * 0.12f), CenterWidth, Amber, Scale * 0.85f, Highlight);
	}

	if (Character.IsCareerAchievementsOpen())
	{
		TArray<FString> Lines = {FString::Printf(TEXT("ACHIEVEMENTS - %d OF %d"), Career->GetAchievementCount(), GetOddsWellAchievements().Num()), TEXT("")};
		for (const FOddsWellAchievement& Achievement : GetOddsWellAchievements())
		{
			Lines.Add(FString::Printf(TEXT("%s %-20s %s"), Career->HasAchievement(Achievement.Id) ? TEXT("[x]") : TEXT("[ ]"), *Achievement.Name, *Achievement.Description));
		}
		Lines.Add(TEXT(""));
		Lines.Add(TEXT("K or Esc: close"));
		DrawCareerPanel(Lines, CenterX, FMath::Max(90.0f, CanvasHeight * 0.08f), CenterWidth, Teal, Scale * 0.8f);
	}

	const FString Toast = Character.GetCareerToast();
	if (!Toast.IsEmpty())
	{
		const float Width = FMath::Min(760.0f, CanvasWidth - 48.0f);
		DrawCareerPanel({Toast}, CanvasWidth - Width - 24.0f, 24.0f, Width, Amber, Scale * 0.9f);
	}

	const FString Prompt = Character.GetCareerPrompt();
	if (!Prompt.IsEmpty())
	{
		const float Width = FMath::Min(900.0f, CanvasWidth - 48.0f);
		DrawCareerPanel({Prompt}, (CanvasWidth - Width) * 0.5f, CanvasHeight - 190.0f, Width, Teal, Scale);
	}
	const FString Notice = Character.GetCareerNotice();
	if (!Notice.IsEmpty())
	{
		const float Width = FMath::Min(900.0f, CanvasWidth - 48.0f);
		DrawCareerPanel({Notice}, (CanvasWidth - Width) * 0.5f, CanvasHeight * 0.72f, Width, Amber, Scale);
	}
}
