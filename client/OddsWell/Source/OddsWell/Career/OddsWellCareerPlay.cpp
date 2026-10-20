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
		EKeys::Gamepad_LeftShoulder, EKeys::Gamepad_RightShoulder,
	};
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
	if (Career && Career->IsReady())
	{
		if (!Career->GetMorningReport().IsEmpty())
		{
			bCareerBoardOpen = false;
			if (CareerKeyPressed(*OwnerController, EKeys::Enter) || CareerKeyPressed(*OwnerController, EKeys::Gamepad_FaceButton_Bottom))
			{
				Career->DismissMorningReport();
			}
		}
		else if (IsSundale(GetWorld()))
		{
			PollCareerBoard(*OwnerController);
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
				const TArray<int32> Games = Career->GetTodaysGameIds();
				const FOddsWellCareerWager* Wager = Games.Num() ? Career->FindWagerForGame(Games[0]) : nullptr;
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
	const FOddsWellCareerWager* Existing = Career->FindWagerForGame(GameId);
	if (CareerBoardRow != PreviousRow)
	{
		CareerBoardSelection = Existing ? Existing->Selection : INDEX_NONE;
	}
	if (Existing || Career->HaveTodaysGamesTippedOff())
	{
		return;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Left) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Left))
	{
		CareerBoardSelection = 1;
	}
	if (CareerKeyPressed(OwnerController, EKeys::Right) || CareerKeyPressed(OwnerController, EKeys::Gamepad_DPad_Right))
	{
		CareerBoardSelection = 0;
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
			ShowCareerNotice(TEXT("Pick a team first: Left for the away team, Right for the home team."));
			return;
		}
		FString Error;
		if (!Career->PlaceWager(GameId, CareerBoardSelection, CareerBoardStake, Error))
		{
			ShowCareerNotice(Error);
			return;
		}
		const OddsWellLeague::FScheduledGame* Game = Career->FindGame(GameId);
		const FOddsWellCareerWager* Placed = Career->FindWagerForGame(GameId);
		if (Game && Placed)
		{
			ShowCareerNotice(FString::Printf(TEXT("Bet placed: %lld on %s at %s. Pays %lld if they win. Balance: %lld"),
				Placed->Stake,
				*Career->GetTeamName(Placed->Selection == 0 ? Game->Home : Game->Away),
				*OddsText(Placed->WinProbabilityE8),
				OddsWellLeague::GrossReturn(Placed->Stake, Placed->WinProbabilityE8),
				Career->GetBalance()));
		}
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
			if (Games.Num() != 4 || !Career->PlaceWager(Games[0], 0, 40, Error))
			{
				CareerSmokeFail(FString::Printf(TEXT("wager_failed:%s"), *Error));
				return;
			}
			FString Duplicate;
			if (Career->PlaceWager(Games[0], 1, 10, Duplicate))
			{
				CareerSmokeFail(TEXT("duplicate_wager_accepted"));
				return;
			}
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=wager|game=%d|stake=40|balance=%lld|duplicate_rejected=true"), Games[0], Career->GetBalance());
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
			if (Career->PlaceWager(Career->GetTodaysGameIds()[1], 0, 10, Late))
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
			const FOddsWellCareerWager Wager = *Career->FindWagerForGame(Career->GetTodaysGameIds()[0]);
			if (!Career->SleepUntilTomorrow(Error))
			{
				CareerSmokeFail(FString::Printf(TEXT("sleep_failed:%s"), *Error));
				return;
			}
			const TArray<FOddsWellCareerWager> DayWagers = Career->GetWagersForDay(Career->GetSeason(), DayBefore);
			const FOddsWellCareerWager* Settled = DayWagers.FindByPredicate([&Wager](const FOddsWellCareerWager& Candidate) { return Candidate.Id == Wager.Id; });
			const int64 Expected = GCareerSmokeStartBalance + 100 - 40 + (Settled && Settled->Status == EOddsWellCareerWagerStatus::Won ? Settled->Payout : 0);
			const bool bPass = Settled && Settled->Status != EOddsWellCareerWagerStatus::Pending && Career->GetDay() == DayBefore + 1 && Career->GetBalance() == Expected && !Career->HasWorkedToday();
			UE_LOG(LogTemp, Display, TEXT("ODDSWELL_CAREER_SMOKE|step=sleep|day=%d|wager=%s|payout=%lld|balance=%lld|expected=%lld|result=%s"),
				Career->GetDay(), Settled ? (Settled->Status == EOddsWellCareerWagerStatus::Won ? TEXT("won") : TEXT("lost")) : TEXT("missing"),
				Settled ? Settled->Payout : 0, Career->GetBalance(), Expected, bPass ? TEXT("PASS") : TEXT("FAIL"));
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

void AOddsWellSportsbookHUD::DrawCareerPanel(const TArray<FString>& Lines, const float X, const float Y, const float Width, const FLinearColor& Accent, const float Scale, const int32 HighlightLine)
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
	DrawCareerPanel({
		FString::Printf(TEXT("SEASON %d   %s"), Career->GetSeason(), *Career->GetPhaseText()),
		FString::Printf(TEXT("Balance: %lld Odds Bucks"), Career->GetBalance()),
		Career->HasWorkedToday() ? FString(TEXT("Shift: done for today")) : FString(TEXT("Shift: available at the Job marker (+100)")),
		Today.IsEmpty() ? FString(TEXT("No games today"))
			: FString::Printf(TEXT("Today: %d game%s - %s"), Today.Num(), Today.Num() == 1 ? TEXT("") : TEXT("s"),
				Career->HaveTodaysGamesTippedOff() ? TEXT("final scores in") : TEXT("betting open")),
		TEXT("L: standings"),
	}, 24.0f, Character.GetCareerReplay() ? 140.0f : 24.0f, 470.0f * Scale, Teal, Scale * 0.85f);

	const float CenterWidth = FMath::Min(900.0f, CanvasWidth - 48.0f);
	const float CenterX = (CanvasWidth - CenterWidth) * 0.5f;

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
		TArray<FString> Lines = {TEXT("TODAY'S BOARD - MATCH WINNER"), TEXT("")};
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
					*Career->GetTeamName(Game->Away), *OddsText(UOddsWellCareerSubsystem::SelectionProbabilityE8(*Game, 1)),
					*Career->GetTeamName(Game->Home), *OddsText(UOddsWellCareerSubsystem::SelectionProbabilityE8(*Game, 0)));
			}
			if (const FOddsWellCareerWager* Wager = Career->FindWagerForGame(Game->Id))
			{
				Line += FString::Printf(TEXT("    [your bet: %lld on %s]"), Wager->Stake, *Career->GetTeamShortName(Wager->Selection == 0 ? Game->Home : Game->Away));
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
			if (Game && Career->FindWagerForGame(Game->Id))
			{
				Lines.Add(TEXT("You already have a bet on this game."));
			}
			else if (Game && Selection != INDEX_NONE)
			{
				const int64 Probability = UOddsWellCareerSubsystem::SelectionProbabilityE8(*Game, Selection);
				Lines.Add(FString::Printf(TEXT("Pick: %s   Stake: %lld   Pays: %lld if they win"),
					*Career->GetTeamName(Selection == 0 ? Game->Home : Game->Away), Character.GetCareerBoardStake(),
					OddsWellLeague::GrossReturn(Character.GetCareerBoardStake(), Probability)));
			}
			else
			{
				Lines.Add(FString::Printf(TEXT("Pick a team.   Stake: %lld"), Character.GetCareerBoardStake()));
			}
			Lines.Add(TEXT("Up/Down: game   Left: away team   Right: home team   - / =: stake   Enter: place bet"));
		}
		Lines.Add(TEXT("Odds are fixed from public information before tipoff. E or Esc: close"));
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
