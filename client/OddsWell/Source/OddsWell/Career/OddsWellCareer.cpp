#include "Career/OddsWellCareer.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

DEFINE_LOG_CATEGORY_STATIC(LogOddsWellCareer, Log, All);

namespace
{
	const FName ShiftReason(TEXT("career_shift"));
	const FName StakeReason(TEXT("career_wager_stake"));
	const FName PurchaseReason(TEXT("career_purchase"));

	FString PurchaseCommand(const FName ItemId)
	{
		return FString::Printf(TEXT("career:buy:%s"), *ItemId.ToString());
	}
	const FName PayoutReason(TEXT("career_wager_payout"));

	FString ToFString(const std::string& Text)
	{
		return FString(UTF8_TO_TCHAR(Text.c_str()));
	}

	std::string ToStdString(const FString& Text)
	{
		return std::string(TCHAR_TO_UTF8(*Text));
	}

	FString SlotName()
	{
		FString Slot = TEXT("OddsWellCareer");
		FParse::Value(FCommandLine::Get(), TEXT("CareerSlot="), Slot);
		return Slot;
	}

	FString ShiftKey(const OddsWellLeague::FLeagueState& State)
	{
		return FString::Printf(TEXT("s%d:d%d"), State.SeasonNumber, State.Day);
	}
}

TConstArrayView<FOddsWellJob> GetOddsWellJobs()
{
	static const FOddsWellJob Jobs[] = {
		{TEXT("Corner store clerk"), 100, 0},
		{TEXT("Arena usher"), 130, 6},
		{TEXT("Stats desk assistant"), 170, 14},
		{TEXT("Team scout"), 220, 26},
	};
	return Jobs;
}

bool IsOddsWellCareerMode()
{
	static const bool bCareer = !FString(FCommandLine::Get()).Contains(TEXT("Qa"), ESearchCase::CaseSensitive)
		&& !FParse::Param(FCommandLine::Get(), TEXT("LegacyCanonical"));
	return bCareer;
}

UOddsWellCareerSubsystem* UOddsWellCareerSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	UGameInstance* GameInstance = World ? World->GetGameInstance() : nullptr;
	return GameInstance ? GameInstance->GetSubsystem<UOddsWellCareerSubsystem>() : nullptr;
}

void UOddsWellCareerSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	if (!IsOddsWellCareerMode())
	{
		return;
	}
	if (!LoadOrCreate(LoadError))
	{
		UE_LOG(LogOddsWellCareer, Error, TEXT("ODDSWELL_CAREER|result=FAIL|reason=%s"), *LoadError);
		return;
	}
	if (!bReady)
	{
		UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER|result=NO_SAVE|slot=%s"), *SlotName());
		return;
	}
	UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER|result=READY|season=%d|day=%d|balance=%lld|wagers=%d|slot=%s"),
		League.SeasonNumber, League.Day, Ledger.GetBalance(), Wagers.Num(), *SlotName());
}

bool UOddsWellCareerSubsystem::LoadOrCreate(FString& OutError)
{
	const FString Slot = SlotName();
	if (!FParse::Param(FCommandLine::Get(), TEXT("NewCareer")) && UGameplayStatics::DoesSaveGameExist(Slot, 0))
	{
		const UOddsWellCareerSave* Saved = Cast<UOddsWellCareerSave>(UGameplayStatics::LoadGameFromSlot(Slot, 0));
		if (!Saved || Saved->Schema != 1)
		{
			OutError = TEXT("The career save could not be read.");
			return false;
		}
		std::string Error;
		OddsWellLeague::FLeagueState Loaded;
		if (!OddsWellLeague::DeserializeLeague(GetConfig(), ToStdString(Saved->League), Loaded, Error))
		{
			OutError = ToFString(Error);
			return false;
		}
		FOddsWellOddsBucksLedger LoadedLedger;
		if (!LoadedLedger.Restore(Saved->Ledger, OutError))
		{
			return false;
		}
		League = MoveTemp(Loaded);
		Ledger = MoveTemp(LoadedLedger);
		Wagers = Saved->Wagers;
		LastShiftKey = Saved->LastShiftKey;
		NextWagerId = FMath::Max(1, Saved->NextWagerId);
		MorningReport = Saved->MorningReport;
		TutorialFlags = Saved->TutorialFlags;
		ShiftsWorked = Saved->ShiftsWorked;
		GamesWatched = Saved->GamesWatched;
		EquippedTop = Saved->EquippedTop;
		EquippedBottom = Saved->EquippedBottom;
		Achievements = Saved->Achievements;
		if (ShiftsWorked == 0)
		{
			// Saves from before the job ladder: count the shifts already paid.
			for (const FOddsWellOddsBucksEntry& Entry : Ledger.GetEntries())
			{
				ShiftsWorked += Entry.Reason == ShiftReason ? 1 : 0;
			}
		}
		bReady = true;
		if (!League.bDayPrepared)
		{
			OddsWellLeague::PrepareDay(GetConfig(), League);
			return Save(OutError);
		}
		// A save from before the extra markets: price today's open games now.
		bool bPriced = false;
		for (OddsWellLeague::FScheduledGame& Game : League.Games)
		{
			if (Game.Day == League.Day && !Game.bPlayed && Game.bOddsPublished && !Game.bMarketsPublished)
			{
				OddsWellLeague::PriceGameMarkets(GetConfig(), League, Game);
				bPriced = true;
			}
		}
		return !bPriced || Save(OutError);
	}
	// Without a save, the career starts when the player chooses New career (tests may force it with -NewCareer).
	if (FParse::Param(FCommandLine::Get(), TEXT("NewCareer")))
	{
		return StartNewCareer(DefaultNewCareerSeed(), OutError);
	}
	return true;
}

uint64 UOddsWellCareerSubsystem::DefaultNewCareerSeed()
{
	uint64 Seed = static_cast<uint64>(FDateTime::UtcNow().GetTicks() % 1000000007);
	FParse::Value(FCommandLine::Get(), TEXT("CareerSeed="), Seed);
	return Seed;
}

bool UOddsWellCareerSubsystem::EnsureCareerStarted(FString& OutError)
{
	return bReady || (IsOddsWellCareerMode() && StartNewCareer(DefaultNewCareerSeed(), OutError));
}

bool UOddsWellCareerSubsystem::StartNewCareer(const uint64 CareerSeed, FString& OutError)
{
	OddsWellLeague::NewLeague(GetConfig(), CareerSeed, League);
	OddsWellLeague::PrepareDay(GetConfig(), League);
	Ledger = FOddsWellOddsBucksLedger();
	Wagers.Reset();
	LastShiftKey.Reset();
	NextWagerId = 1;
	GameToWatch = 0;
	TutorialFlags = 0;
	ShiftsWorked = 0;
	GamesWatched = 0;
	EquippedTop = NAME_None;
	EquippedBottom = NAME_None;
	Achievements.Reset();
	PendingToasts.Reset();
	LastShiftMessage.Reset();
	MorningReport = FString::Printf(
		TEXT("Welcome to Sundale.\nSeason 1 of the league starts today: 8 teams, 28 games each, then the playoffs.\nWork a shift at the Job marker, check today's odds at the ticket booth, and watch games at the arena.\nSleep in your Studio to start the next day."));
	bReady = true;
	return Save(OutError);
}

bool UOddsWellCareerSubsystem::Save(FString& OutError)
{
	UOddsWellCareerSave* Saved = Cast<UOddsWellCareerSave>(UGameplayStatics::CreateSaveGameObject(UOddsWellCareerSave::StaticClass()));
	if (!Saved)
	{
		OutError = TEXT("The career save object could not be created.");
		return false;
	}
	Saved->League = ToFString(OddsWellLeague::SerializeLeague(League));
	Saved->Ledger = Ledger.GetEntries();
	Saved->Wagers = Wagers;
	Saved->LastShiftKey = LastShiftKey;
	Saved->NextWagerId = NextWagerId;
	Saved->MorningReport = MorningReport;
	Saved->TutorialFlags = TutorialFlags;
	Saved->ShiftsWorked = ShiftsWorked;
	Saved->GamesWatched = GamesWatched;
	Saved->EquippedTop = EquippedTop;
	Saved->EquippedBottom = EquippedBottom;
	Saved->Achievements = Achievements;
	if (!UGameplayStatics::SaveGameToSlot(Saved, SlotName(), 0))
	{
		OutError = TEXT("The career could not be saved.");
		return false;
	}
	return true;
}

TArray<int32> UOddsWellCareerSubsystem::GetTodaysGameIds() const
{
	TArray<int32> Ids;
	for (const int Id : OddsWellLeague::GamesOnDay(League, League.Day))
	{
		Ids.Add(Id);
	}
	return Ids;
}

const OddsWellLeague::FScheduledGame* UOddsWellCareerSubsystem::FindGame(const int32 GameId) const
{
	for (const OddsWellLeague::FScheduledGame& Game : League.Games)
	{
		if (Game.Id == GameId)
		{
			return &Game;
		}
	}
	return nullptr;
}

FString UOddsWellCareerSubsystem::GetTeamName(const int32 Team) const
{
	return Team >= 0 && Team < static_cast<int32>(GetConfig().Teams.size())
		? ToFString(GetConfig().Teams[static_cast<size_t>(Team)].Name)
		: FString(TEXT("TBD"));
}

FString UOddsWellCareerSubsystem::GetTeamShortName(const int32 Team) const
{
	return Team >= 0 && Team < static_cast<int32>(GetConfig().Teams.size())
		? ToFString(GetConfig().Teams[static_cast<size_t>(Team)].ShortName)
		: FString(TEXT("TBD"));
}

FString UOddsWellCareerSubsystem::GetPhaseText() const
{
	switch (League.Phase)
	{
	case OddsWellLeague::ESeasonPhase::Semifinals: return TEXT("Playoff semifinals");
	case OddsWellLeague::ESeasonPhase::Final: return TEXT("League final");
	default:
		return FString::Printf(TEXT("Regular season day %d of %d"), League.Day, OddsWellLeague::RegularSeasonDays(GetConfig()));
	}
}

FString UOddsWellCareerSubsystem::DescribeGame(const OddsWellLeague::FScheduledGame& Game) const
{
	FString Stage;
	if (Game.Stage != OddsWellLeague::EGameStage::Regular)
	{
		Stage = FString::Printf(TEXT(" (%s game %d)"), UTF8_TO_TCHAR(OddsWellLeague::StageName(Game.Stage)), Game.SeriesGame);
	}
	if (Game.bPlayed)
	{
		return FString::Printf(TEXT("%s %d - %d %s%s%s"),
			*GetTeamName(Game.Away), Game.AwayScore, Game.HomeScore, *GetTeamName(Game.Home),
			Game.Overtime ? TEXT(" (OT)") : TEXT(""), *Stage);
	}
	return FString::Printf(TEXT("%s at %s%s"), *GetTeamName(Game.Away), *GetTeamName(Game.Home), *Stage);
}

TArray<FString> UOddsWellCareerSubsystem::BuildStandingsLines() const
{
	TArray<FString> Lines;
	int32 Rank = 1;
	for (const int Team : OddsWellLeague::RankedTeams(GetConfig(), League))
	{
		const OddsWellLeague::FStanding& Row = League.Standings[static_cast<size_t>(Team)];
		Lines.Add(FString::Printf(TEXT("%d. %-20s %2d-%-2d  %+d"), Rank++, *GetTeamName(Team), Row.Wins, Row.Losses, Row.PointsFor - Row.PointsAgainst));
	}
	return Lines;
}

bool UOddsWellCareerSubsystem::CommitLedger(const FOddsWellOddsBucksLedger& Candidate, FString& OutError)
{
	const TArray<FOddsWellOddsBucksEntry>& Current = Ledger.GetEntries();
	const TArray<FOddsWellOddsBucksEntry>& Next = Candidate.GetEntries();
	bool bExtends = Next.Num() >= Current.Num();
	for (int32 Index = 0; bExtends && Index < Current.Num(); ++Index)
	{
		bExtends = Current[Index].CommandId == Next[Index].CommandId && Current[Index].Delta == Next[Index].Delta;
	}
	if (!bExtends)
	{
		OutError = TEXT("The Odds Bucks ledger changed before this purchase was saved.");
		return false;
	}
	const FOddsWellOddsBucksLedger Previous = Ledger;
	Ledger = Candidate;
	if (!Save(OutError))
	{
		Ledger = Previous;
		return false;
	}
	return true;
}

bool UOddsWellCareerSubsystem::HasWorkedToday() const
{
	return LastShiftKey == ShiftKey(League);
}

int32 UOddsWellCareerSubsystem::GetJobLevel() const
{
	const TConstArrayView<FOddsWellJob> Jobs = GetOddsWellJobs();
	int32 Level = 0;
	while (Level + 1 < Jobs.Num() && ShiftsWorked >= Jobs[Level + 1].ShiftsRequired)
	{
		++Level;
	}
	return Level;
}

FString UOddsWellCareerSubsystem::GetShiftPrompt() const
{
	if (HasWorkedToday())
	{
		return TEXT("You already worked today. Sleep in your Studio to start a new day.");
	}
	return FString::Printf(TEXT("Press E to work your shift as %s (+%lld Odds Bucks)"), GetJob().Title, GetJob().Pay);
}

bool UOddsWellCareerSubsystem::WorkShift(bool& bOutCredited, int64& OutBalance, FString& OutError)
{
	bOutCredited = false;
	OutBalance = Ledger.GetBalance();
	if (!bReady)
	{
		OutError = TEXT("The career is not loaded.");
		return false;
	}
	if (HasWorkedToday())
	{
		LastShiftMessage = FString::Printf(TEXT("You already worked today - sleep in your Studio to start a new day | Balance: %lld"), OutBalance);
		return true;
	}
	const FOddsWellJob& Job = GetJob();
	FOddsWellOddsBucksLedger Candidate = Ledger;
	const FString CommandId = FString::Printf(TEXT("career:shift:%s"), *ShiftKey(League));
	if (Candidate.Append(CommandId, Job.Pay, ShiftReason) != EOddsWellOddsBucksAppendResult::Applied)
	{
		OutError = TEXT("The shift payout was rejected.");
		return false;
	}
	const FOddsWellOddsBucksLedger Previous = Ledger;
	const FString PreviousShift = LastShiftKey;
	const int32 PreviousLevel = GetJobLevel();
	Ledger = MoveTemp(Candidate);
	LastShiftKey = ShiftKey(League);
	++ShiftsWorked;
	MarkTutorial(EOddsWellTutorialStep::Shift);
	if (!Save(OutError))
	{
		Ledger = Previous;
		LastShiftKey = PreviousShift;
		--ShiftsWorked;
		return false;
	}
	bOutCredited = true;
	OutBalance = Ledger.GetBalance();
	LastShiftMessage = FString::Printf(TEXT("Shift complete as %s: +%lld Odds Bucks | Balance: %lld"), Job.Title, Job.Pay, OutBalance);
	if (GetJobLevel() > PreviousLevel)
	{
		LastShiftMessage += FString::Printf(TEXT("\nPromoted to %s! Shifts now pay %lld."), GetJob().Title, GetJob().Pay);
	}
	UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_SHIFT|season=%d|day=%d|job=%d|credited=%lld|shifts=%d|balance=%lld"),
		League.SeasonNumber, League.Day, PreviousLevel, Job.Pay, ShiftsWorked, OutBalance);
	CheckAchievements();
	return true;
}

const FOddsWellCareerWager* UOddsWellCareerSubsystem::FindWager(const int32 GameId, const OddsWellLeague::EMarket Market) const
{
	for (const FOddsWellCareerWager& Wager : Wagers)
	{
		if (Wager.Season == League.SeasonNumber && Wager.GameId == GameId && Wager.Market == static_cast<int32>(Market))
		{
			return &Wager;
		}
	}
	return nullptr;
}

int32 UOddsWellCareerSubsystem::CountWagersOnGame(const int32 GameId) const
{
	int32 Count = 0;
	for (const FOddsWellCareerWager& Wager : Wagers)
	{
		Count += Wager.Season == League.SeasonNumber && Wager.GameId == GameId ? 1 : 0;
	}
	return Count;
}

FString UOddsWellCareerSubsystem::GetMarketName(const OddsWellLeague::FScheduledGame& Game, const OddsWellLeague::EMarket Market) const
{
	switch (Market)
	{
	case OddsWellLeague::EMarket::MatchWinner: return TEXT("Match winner");
	case OddsWellLeague::EMarket::Margin: return TEXT("Winning margin");
	case OddsWellLeague::EMarket::Overtime: return TEXT("Overtime");
	case OddsWellLeague::EMarket::HomeStarPoints:
	case OddsWellLeague::EMarket::AwayStarPoints:
	{
		const int32 Side = Market == OddsWellLeague::EMarket::HomeStarPoints ? 0 : 1;
		const int32 Team = Side == 0 ? Game.Home : Game.Away;
		const OddsWellLeague::FPointsProp& Prop = Game.Props[Side];
		const OddsWellLeague::FLeagueTeam& Source = GetConfig().Teams[static_cast<size_t>(Team)];
		const FString Player = Prop.RosterSlot >= 0 && Prop.RosterSlot < static_cast<int32>(Source.Roster.size())
			? ToFString(Source.Roster[static_cast<size_t>(Prop.RosterSlot)].Ratings.Name) : FString(TEXT("Star"));
		return FString::Printf(TEXT("%s (%s) points"), *Player, *GetTeamShortName(Team));
	}
	default: return FString();
	}
}

FString UOddsWellCareerSubsystem::DescribeOutcome(const OddsWellLeague::FScheduledGame& Game, const OddsWellLeague::EMarket Market, const int32 Outcome) const
{
	switch (Market)
	{
	case OddsWellLeague::EMarket::MatchWinner:
		return FString::Printf(TEXT("%s to win"), *GetTeamName(Outcome == 0 ? Game.Home : Game.Away));
	case OddsWellLeague::EMarket::Margin:
	{
		static const TCHAR* Bands[3] = {TEXT("1-5"), TEXT("6-10"), TEXT("11+")};
		return FString::Printf(TEXT("%s by %s"), *GetTeamShortName(Outcome < 3 ? Game.Home : Game.Away), Bands[FMath::Clamp(Outcome, 0, 5) % 3]);
	}
	case OddsWellLeague::EMarket::Overtime:
		return Outcome == 0 ? TEXT("Goes to overtime") : TEXT("No overtime");
	case OddsWellLeague::EMarket::HomeStarPoints:
	case OddsWellLeague::EMarket::AwayStarPoints:
	{
		const OddsWellLeague::FPointsProp& Prop = Game.Props[Market == OddsWellLeague::EMarket::HomeStarPoints ? 0 : 1];
		return FString::Printf(TEXT("%s %d.%d"), Outcome == 0 ? TEXT("Over") : TEXT("Under"), Prop.LineTenths / 10, Prop.LineTenths % 10);
	}
	default: return FString();
	}
}

FString UOddsWellCareerSubsystem::DescribeWager(const FOddsWellCareerWager& Wager) const
{
	const OddsWellLeague::FScheduledGame* Game = Wager.Season == League.SeasonNumber ? FindGame(Wager.GameId) : nullptr;
	if (!Game)
	{
		return TEXT("Bet");
	}
	const OddsWellLeague::EMarket Market = static_cast<OddsWellLeague::EMarket>(Wager.Market);
	return Market == OddsWellLeague::EMarket::MatchWinner
		? DescribeOutcome(*Game, Market, Wager.Selection)
		: FString::Printf(TEXT("%s: %s"), *GetMarketName(*Game, Market), *DescribeOutcome(*Game, Market, Wager.Selection));
}

TArray<FOddsWellCareerWager> UOddsWellCareerSubsystem::GetWagersForDay(const int32 Season, const int32 Day) const
{
	TArray<FOddsWellCareerWager> Result;
	for (const FOddsWellCareerWager& Wager : Wagers)
	{
		const OddsWellLeague::FScheduledGame* Game = Wager.Season == League.SeasonNumber ? FindGame(Wager.GameId) : nullptr;
		if (Wager.Season == Season && Game && Game->Day == Day)
		{
			Result.Add(Wager);
		}
	}
	return Result;
}

bool UOddsWellCareerSubsystem::PlaceWager(const int32 GameId, const OddsWellLeague::EMarket Market, const int32 Selection, const int64 Stake, FString& OutError)
{
	const OddsWellLeague::FScheduledGame* Game = FindGame(GameId);
	if (!bReady || !Game)
	{
		OutError = TEXT("That game is not on the board.");
		return false;
	}
	if (Game->Day != League.Day || Game->bPlayed || League.bDayPlayed || !Game->bOddsPublished)
	{
		OutError = TEXT("Betting on that game is closed.");
		return false;
	}
	if (Market >= OddsWellLeague::EMarket::Count || !OddsWellLeague::IsOutcomeAvailable(*Game, Market))
	{
		OutError = TEXT("That market is not open on this game.");
		return false;
	}
	if (Selection < 0 || Selection >= OddsWellLeague::MarketOutcomeCount(Market))
	{
		OutError = TEXT("Pick an outcome first.");
		return false;
	}
	if (!OddsWellLeague::IsValidStake(Stake))
	{
		OutError = TEXT("Stakes are 10 to 100 Odds Bucks in steps of 10.");
		return false;
	}
	if (FindWager(GameId, Market))
	{
		OutError = TEXT("You already have a bet in this market.");
		return false;
	}
	FOddsWellCareerWager Wager;
	Wager.Id = NextWagerId;
	Wager.Season = League.SeasonNumber;
	Wager.GameId = GameId;
	Wager.Market = static_cast<int32>(Market);
	Wager.Selection = Selection;
	Wager.Stake = Stake;
	Wager.WinProbabilityE8 = OddsWellLeague::OutcomeProbabilityE8(*Game, Market, Selection);
	FOddsWellOddsBucksLedger Candidate = Ledger;
	if (Candidate.Append(FString::Printf(TEXT("career:wager:%d:stake"), Wager.Id), -Stake, StakeReason) != EOddsWellOddsBucksAppendResult::Applied)
	{
		OutError = FString::Printf(TEXT("You need %lld Odds Bucks for that stake."), Stake);
		return false;
	}
	const FOddsWellOddsBucksLedger Previous = Ledger;
	Ledger = MoveTemp(Candidate);
	Wagers.Add(Wager);
	++NextWagerId;
	MarkTutorial(EOddsWellTutorialStep::Bet);
	if (!Save(OutError))
	{
		Ledger = Previous;
		Wagers.Pop();
		--NextWagerId;
		return false;
	}
	UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_WAGER|id=%d|season=%d|game=%d|market=%d|selection=%d|stake=%lld|probability_e8=%lld|balance=%lld"),
		Wager.Id, Wager.Season, GameId, Wager.Market, Selection, Stake, Wager.WinProbabilityE8, Ledger.GetBalance());
	CheckAchievements();
	return true;
}

void UOddsWellCareerSubsystem::SettleWagers(const int32 OnlyGameId)
{
	for (FOddsWellCareerWager& Wager : Wagers)
	{
		if (Wager.Status != EOddsWellCareerWagerStatus::Pending || Wager.Season != League.SeasonNumber || (OnlyGameId && Wager.GameId != OnlyGameId))
		{
			continue;
		}
		const OddsWellLeague::FScheduledGame* Game = FindGame(Wager.GameId);
		if (!Game || !Game->bPlayed)
		{
			continue;
		}
		bool bWon = false;
		if (!OddsWellLeague::DidOutcomeWin(*Game, static_cast<OddsWellLeague::EMarket>(Wager.Market), Wager.Selection, bWon))
		{
			continue;
		}
		const FString Team = DescribeWager(Wager);
		if (bWon)
		{
			const int64 Gross = OddsWellLeague::GrossReturn(Wager.Stake, Wager.WinProbabilityE8);
			const EOddsWellOddsBucksAppendResult Result = Ledger.Append(FString::Printf(TEXT("career:wager:%d:payout"), Wager.Id), Gross, PayoutReason);
			if (Result == EOddsWellOddsBucksAppendResult::Rejected)
			{
				UE_LOG(LogOddsWellCareer, Error, TEXT("ODDSWELL_CAREER_SETTLEMENT|result=FAIL|wager=%d"), Wager.Id);
				continue;
			}
			Wager.Status = EOddsWellCareerWagerStatus::Won;
			Wager.Payout = Gross;
			UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_SETTLEMENT|wager=%d|bet=%s|result=won|payout=%lld|balance=%lld"), Wager.Id, *Team, Gross, Ledger.GetBalance());
		}
		else
		{
			Wager.Status = EOddsWellCareerWagerStatus::Lost;
			UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_SETTLEMENT|wager=%d|bet=%s|result=lost|balance=%lld"), Wager.Id, *Team, Ledger.GetBalance());
		}
	}
}

bool UOddsWellCareerSubsystem::TipOffToday(FString& OutError)
{
	if (!bReady)
	{
		OutError = TEXT("The career is not loaded.");
		return false;
	}
	if (League.bDayPlayed)
	{
		return true;
	}
	std::string Error;
	if (!OddsWellLeague::PlayDay(GetConfig(), League, nullptr, Error))
	{
		OutError = ToFString(Error);
		return false;
	}
	RevealedGames.Reset();
	UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_TIPOFF|season=%d|day=%d|games=%d|balance=%lld"), League.SeasonNumber, League.Day, GetTodaysGameIds().Num(), Ledger.GetBalance());
	return Save(OutError);
}

bool UOddsWellCareerSubsystem::SleepUntilTomorrow(FString& OutError)
{
	if (!TipOffToday(OutError))
	{
		return false;
	}
	SettleWagers(0);
	const int32 Season = League.SeasonNumber;
	const int32 Day = League.Day;
	FString Report = FString::Printf(TEXT("Results from season %d, day %d:\n"), Season, Day);
	for (const int32 Id : GetTodaysGameIds())
	{
		if (const OddsWellLeague::FScheduledGame* Game = FindGame(Id))
		{
			Report += DescribeGame(*Game) + TEXT("\n");
		}
	}
	const TArray<FOddsWellCareerWager> DayWagers = GetWagersForDay(Season, Day);
	if (DayWagers.Num())
	{
		Report += TEXT("\nYour bets:\n");
		for (const FOddsWellCareerWager& Wager : DayWagers)
		{
			const FString Team = DescribeWager(Wager);
			Report += Wager.Status == EOddsWellCareerWagerStatus::Won
				? FString::Printf(TEXT("WON  %s: +%lld (staked %lld)\n"), *Team, Wager.Payout, Wager.Stake)
				: FString::Printf(TEXT("LOST %s: staked %lld\n"), *Team, Wager.Stake);
		}
	}
	const int32 PreviousChampionSeasons = League.CompletedSeasons;
	OddsWellLeague::AdvanceDay(GetConfig(), League);
	if (League.CompletedSeasons > PreviousChampionSeasons && League.LastChampion >= 0)
	{
		Report += FString::Printf(TEXT("\n%s are the season %d champions!\nSeason %d starts today.\n"), *GetTeamName(League.LastChampion), Season, League.SeasonNumber);
	}
	else if (League.Phase == OddsWellLeague::ESeasonPhase::Semifinals && League.Day == OddsWellLeague::RegularSeasonDays(GetConfig()) + 1)
	{
		Report += TEXT("\nThe regular season is over. The top four teams start the playoffs today.\n");
	}
	OddsWellLeague::PrepareDay(GetConfig(), League);
	Report += FString::Printf(TEXT("\nBalance: %lld Odds Bucks. Today is %s."), Ledger.GetBalance(), *GetPhaseText());
	MorningReport = Report;
	GameToWatch = 0;
	MarkTutorial(EOddsWellTutorialStep::Sleep);
	UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_SLEEP|season=%d|day=%d|phase=%d|balance=%lld"), League.SeasonNumber, League.Day, static_cast<int32>(League.Phase), Ledger.GetBalance());
	if (!Save(OutError))
	{
		return false;
	}
	CheckAchievements();
	return true;
}

void UOddsWellCareerSubsystem::RevealGame(const int32 GameId)
{
	const OddsWellLeague::FScheduledGame* Game = FindGame(GameId);
	if (!Game || !Game->bPlayed || RevealedGames.Contains(GameId))
	{
		return;
	}
	RevealedGames.Add(GameId);
	++GamesWatched;
	SettleWagers(GameId);
	MarkTutorial(EOddsWellTutorialStep::Watch);
	FString Error;
	Save(Error);
	CheckAchievements();
}

bool UOddsWellCareerSubsystem::IsGameRevealed(const int32 GameId) const
{
	return RevealedGames.Contains(GameId);
}

FString UOddsWellCareerSubsystem::DescribeGameForPlayer(const OddsWellLeague::FScheduledGame& Game) const
{
	if (Game.bPlayed && !RevealedGames.Contains(Game.Id))
	{
		return FString::Printf(TEXT("%s at %s - final (watch to see the score)"), *GetTeamName(Game.Away), *GetTeamName(Game.Home));
	}
	return DescribeGame(Game);
}

bool UOddsWellCareerSubsystem::OwnsItem(const FName ItemId) const
{
	const FOddsWellCatalogItem* Item = FindOddsWellCatalogItem(ItemId);
	if (!Item)
	{
		return false;
	}
	if (Item->Price == 0 || Ledger.HasCommand(PurchaseCommand(ItemId)))
	{
		return true;
	}
	// Items bought at the original stores before the career catalog.
	return (ItemId == GetOddsWellSignalJacketId() && OwnsOddsWellSignalJacket(Ledger))
		|| (ItemId == TEXT("furniture_modular_chair") && OwnsOddsWellModularChair(Ledger))
		|| (ItemId == TEXT("home_one_bedroom") && OwnsOddsWellOneBedroomUpgrade(Ledger));
}

int32 UOddsWellCareerSubsystem::GetHomeTier() const
{
	int32 Tier = 0;
	for (const FOddsWellCatalogItem* Item : GetOddsWellCatalogItems(EOddsWellCatalogKind::Apartment))
	{
		Tier = OwnsItem(Item->Id) ? FMath::Max(Tier, Item->Tier) : Tier;
	}
	return Tier;
}

int32 UOddsWellCareerSubsystem::CountOwned(const EOddsWellCatalogKind Kind) const
{
	int32 Count = 0;
	for (const FOddsWellCatalogItem* Item : GetOddsWellCatalogItems(Kind))
	{
		Count += OwnsItem(Item->Id) ? 1 : 0;
	}
	return Count;
}

TArray<FName> UOddsWellCareerSubsystem::GetOwnedFurniture() const
{
	TArray<FName> Owned;
	for (const FOddsWellCatalogItem* Item : GetOddsWellCatalogItems(EOddsWellCatalogKind::Furniture))
	{
		if (OwnsItem(Item->Id))
		{
			Owned.Add(Item->Id);
		}
	}
	return Owned;
}

FString UOddsWellCareerSubsystem::GetPurchaseBlocker(const FOddsWellCatalogItem& Item) const
{
	if (OwnsItem(Item.Id))
	{
		return TEXT("Owned");
	}
	if (Item.Kind == EOddsWellCatalogKind::Apartment && !OwnsItem(GetOddsWellApartmentTier(Item.Tier - 1).Id))
	{
		return FString::Printf(TEXT("Needs the %s first"), *GetOddsWellApartmentTier(Item.Tier - 1).Name);
	}
	if (Item.Kind == EOddsWellCatalogKind::Furniture && GetHomeTier() < Item.Tier)
	{
		return FString::Printf(TEXT("Fits a %s or bigger"), *GetOddsWellApartmentTier(Item.Tier).Name);
	}
	if (Ledger.GetBalance() < Item.Price)
	{
		return FString::Printf(TEXT("Needs %lld more Odds Bucks"), Item.Price - Ledger.GetBalance());
	}
	return FString();
}

bool UOddsWellCareerSubsystem::BuyItem(const FName ItemId, FString& OutError)
{
	const FOddsWellCatalogItem* Item = FindOddsWellCatalogItem(ItemId);
	if (!bReady || !Item)
	{
		OutError = TEXT("That item is not for sale.");
		return false;
	}
	const FString Blocker = GetPurchaseBlocker(*Item);
	if (!Blocker.IsEmpty())
	{
		OutError = Blocker == TEXT("Owned") ? FString::Printf(TEXT("You already own the %s."), *Item->Name) : Blocker + TEXT(".");
		return false;
	}
	FOddsWellOddsBucksLedger Candidate = Ledger;
	if (Candidate.Append(PurchaseCommand(ItemId), -Item->Price, PurchaseReason) != EOddsWellOddsBucksAppendResult::Applied)
	{
		OutError = FString::Printf(TEXT("You need %lld Odds Bucks for the %s."), Item->Price, *Item->Name);
		return false;
	}
	const FOddsWellOddsBucksLedger Previous = Ledger;
	Ledger = MoveTemp(Candidate);
	const FName PreviousTop = EquippedTop;
	const FName PreviousBottom = EquippedBottom;
	// New clothes go straight on.
	EquippedTop = Item->Kind == EOddsWellCatalogKind::Top ? ItemId : EquippedTop;
	EquippedBottom = Item->Kind == EOddsWellCatalogKind::Bottom ? ItemId : EquippedBottom;
	if (!Save(OutError))
	{
		Ledger = Previous;
		EquippedTop = PreviousTop;
		EquippedBottom = PreviousBottom;
		return false;
	}
	UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_CAREER_PURCHASE|item=%s|price=%lld|balance=%lld|home_tier=%d"), *ItemId.ToString(), Item->Price, Ledger.GetBalance(), GetHomeTier());
	CheckAchievements();
	return true;
}

FName UOddsWellCareerSubsystem::GetEquipped(const EOddsWellCatalogKind Kind) const
{
	const FName Equipped = Kind == EOddsWellCatalogKind::Top ? EquippedTop : EquippedBottom;
	return !Equipped.IsNone() && OwnsItem(Equipped) ? Equipped
		: Kind == EOddsWellCatalogKind::Top ? GetOddsWellStarterTopId() : GetOddsWellStarterBottomId();
}

bool UOddsWellCareerSubsystem::EquipItem(const FName ItemId, FString& OutError)
{
	const FOddsWellCatalogItem* Item = FindOddsWellCatalogItem(ItemId);
	if (!Item || (Item->Kind != EOddsWellCatalogKind::Top && Item->Kind != EOddsWellCatalogKind::Bottom) || !OwnsItem(ItemId))
	{
		OutError = TEXT("You can only wear clothes you own.");
		return false;
	}
	(Item->Kind == EOddsWellCatalogKind::Top ? EquippedTop : EquippedBottom) = ItemId;
	return Save(OutError);
}

FString UOddsWellCareerSubsystem::PopAchievementToast()
{
	return PendingToasts.Num() ? PendingToasts.Pop(EAllowShrinking::No) : FString();
}

void UOddsWellCareerSubsystem::CheckAchievements()
{
	if (!bReady)
	{
		return;
	}
	int32 Won = 0;
	int32 Streak = 0;
	int32 BestStreak = 0;
	int32 Markets = 0;
	bool bLongShot = false;
	int64 BiggestPayout = 0;
	for (const FOddsWellCareerWager& Wager : Wagers)
	{
		Markets |= 1 << FMath::Clamp(Wager.Market, 0, 30);
		if (Wager.Status == EOddsWellCareerWagerStatus::Pending)
		{
			continue;
		}
		const bool bWon = Wager.Status == EOddsWellCareerWagerStatus::Won;
		Won += bWon ? 1 : 0;
		Streak = bWon ? Streak + 1 : 0;
		BestStreak = FMath::Max(BestStreak, Streak);
		bLongShot |= bWon && Wager.WinProbabilityE8 <= OddsWellLeague::ProbabilityScale / 5;
		BiggestPayout = FMath::Max(BiggestPayout, Wager.Payout);
	}
	const int32 Level = GetJobLevel();
	const int32 Tier = GetHomeTier();
	const int32 Clothes = CountOwned(EOddsWellCatalogKind::Top) + CountOwned(EOddsWellCatalogKind::Bottom);
	bool bBoughtClothes = false;
	for (const EOddsWellCatalogKind Kind : {EOddsWellCatalogKind::Top, EOddsWellCatalogKind::Bottom})
	{
		for (const FOddsWellCatalogItem* Item : GetOddsWellCatalogItems(Kind))
		{
			bBoughtClothes |= Item->Price > 0 && OwnsItem(Item->Id);
		}
	}
	const int32 Furniture = CountOwned(EOddsWellCatalogKind::Furniture);
	const TMap<FName, bool> Earned = {
		{TEXT("first_shift"), ShiftsWorked >= 1},
		{TEXT("first_bet"), Wagers.Num() >= 1},
		{TEXT("first_win"), Won >= 1},
		{TEXT("watched_game"), GamesWatched >= 1},
		{TEXT("first_night"), (TutorialFlags & static_cast<int32>(EOddsWellTutorialStep::Sleep)) != 0},
		{TEXT("promoted"), Level >= 1},
		{TEXT("team_scout"), Level >= GetOddsWellJobs().Num() - 1},
		{TEXT("shifts_40"), ShiftsWorked >= 40},
		{TEXT("all_markets"), Markets == (1 << static_cast<int32>(OddsWellLeague::EMarket::Count)) - 1},
		{TEXT("long_shot"), bLongShot},
		{TEXT("big_ticket"), BiggestPayout >= 500},
		{TEXT("hot_hand"), BestStreak >= 5},
		{TEXT("bets_100"), Wagers.Num() >= 100},
		{TEXT("fresh_fit"), bBoughtClothes},
		{TEXT("wardrobe"), Clothes >= 10},
		{TEXT("make_it_home"), Furniture >= 1},
		{TEXT("interior_designer"), Furniture >= 10},
		{TEXT("one_bedroom"), Tier >= 1},
		{TEXT("four_bedroom"), Tier >= 4},
		{TEXT("penthouse"), Tier >= GetOddsWellApartmentTierCount() - 1},
		{TEXT("full_season"), League.CompletedSeasons >= 1},
		{TEXT("bankroll"), Ledger.GetBalance() >= 3000},
	};
	bool bChanged = false;
	for (const FOddsWellAchievement& Achievement : GetOddsWellAchievements())
	{
		const bool* bEarned = Earned.Find(Achievement.Id);
		if (bEarned && *bEarned && !Achievements.Contains(Achievement.Id))
		{
			Achievements.Add(Achievement.Id);
			PendingToasts.Insert(FString::Printf(TEXT("Achievement unlocked: %s - %s"), *Achievement.Name, *Achievement.Description), 0);
			bChanged = true;
			UE_LOG(LogOddsWellCareer, Display, TEXT("ODDSWELL_ACHIEVEMENT|id=%s|unlocked=%d|total=%d"), *Achievement.Id.ToString(), Achievements.Num(), GetOddsWellAchievements().Num());
		}
	}
	if (bChanged)
	{
		FString Error;
		Save(Error);
	}
}

void UOddsWellCareerSubsystem::DismissMorningReport()
{
	if (MorningReport.IsEmpty())
	{
		return;
	}
	MorningReport.Reset();
	FString Error;
	Save(Error);
}

bool UOddsWellCareerSubsystem::BuildReplay(const int32 GameId, FOddsWellCareerReplay& OutReplay, FString& OutError) const
{
	OddsWellLeague::FGameResult Result;
	std::string Error;
	if (!OddsWellLeague::ReplayGame(GetConfig(), League, GameId, Result, Error))
	{
		OutError = ToFString(Error);
		return false;
	}
	OutReplay = FOddsWellCareerReplay();
	OutReplay.GameId = GameId;
	OutReplay.HomeTeam = ToFString(Result.Home.Name);
	OutReplay.AwayTeam = ToFString(Result.Away.Name);
	for (const OddsWellLeague::FPlayer& Player : Result.Home.Players)
	{
		OutReplay.HomePlayers.Add(ToFString(Player.Name));
	}
	for (const OddsWellLeague::FPlayer& Player : Result.Away.Players)
	{
		OutReplay.AwayPlayers.Add(ToFString(Player.Name));
	}
	OutReplay.HomeScore = Result.HomeScore;
	OutReplay.AwayScore = Result.AwayScore;
	OutReplay.Overtime = Result.Overtime;
	auto Name = [&Result](int Index) { return Index < 0 ? FString() : ToFString(Result.PlayerAt(Index).Name); };
	FString Offense;
	int32 PossessionClock = 0;
	int32 OvertimePeriod = 0;
	for (const OddsWellLeague::FEvent& Event : Result.Events)
	{
		using OddsWellLeague::EEventType;
		if (Event.Type == EEventType::PossessionStarted)
		{
			Offense = ToFString(Result.TeamName(Event.Team));
			PossessionClock = Event.ClockSeconds;
			continue;
		}
		FOddsWellCareerReplayFrame Frame;
		Frame.Kind = UTF8_TO_TCHAR(OddsWellLeague::EventTypeName(Event.Type));
		Frame.ClockSeconds = PossessionClock;
		Frame.HomeScore = Event.HomeScore;
		Frame.AwayScore = Event.AwayScore;
		Frame.Offense = Offense;
		switch (Event.Type)
		{
		case EEventType::PassCompleted:
			Frame.Actor = Name(Event.Player);
			Frame.Target = Name(Event.Other);
			Frame.Label = FString::Printf(TEXT("Pass - %s to %s"), *Frame.Actor, *Frame.Target);
			break;
		case EEventType::Turnover:
			Frame.Actor = Name(Event.Player);
			Frame.Label = FString::Printf(TEXT("Turnover - %s"), *Frame.Actor);
			break;
		case EEventType::ShotMade:
			Frame.Actor = Name(Event.Player);
			Frame.Label = FString::Printf(TEXT("%d points - %s"), Event.Points, *Frame.Actor);
			break;
		case EEventType::ShotMissed:
			Frame.Actor = Name(Event.Player);
			Frame.Label = FString::Printf(TEXT("Missed %s - %s"), Event.ActionKind == 3 ? TEXT("three") : Event.ActionKind == 1 ? TEXT("drive") : TEXT("jumper"), *Frame.Actor);
			break;
		case EEventType::OffensiveRebound:
			Frame.Actor = Name(Event.Player);
			Frame.Label = FString::Printf(TEXT("Offensive rebound - %s"), *Frame.Actor);
			break;
		case EEventType::DefensiveRebound:
			Frame.Actor = Name(Event.Player);
			Frame.Label = FString::Printf(TEXT("Defensive rebound - %s"), *Frame.Actor);
			break;
		case EEventType::ShotClockViolation:
			Frame.Actor = Offense;
			Frame.Label = FString::Printf(TEXT("Shot-clock violation - %s"), *Offense);
			break;
		case EEventType::OvertimeStarted:
			OvertimePeriod = Event.Overtime;
			Frame.Label = FString::Printf(TEXT("Overtime %d"), Event.Overtime);
			Frame.ClockSeconds = 300;
			break;
		default:
			continue;
		}
		Frame.Period = OvertimePeriod > 0 ? 4 + OvertimePeriod : FMath::Clamp((2880 - Frame.ClockSeconds) / 720 + 1, 1, 4);
		OutReplay.Frames.Add(MoveTemp(Frame));
	}
	FOddsWellCareerReplayFrame Final;
	Final.Kind = TEXT("final");
	Final.Label = TEXT("Final");
	Final.Period = 4 + Result.Overtime;
	Final.HomeScore = Result.HomeScore;
	Final.AwayScore = Result.AwayScore;
	OutReplay.Frames.Add(MoveTemp(Final));
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellLeagueCoreSeasonTest,
	"OddsWell.Career.LeagueSeason",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellLeagueCoreSeasonTest::RunTest(const FString& Parameters)
{
	using namespace OddsWellLeague;
	const FLeagueConfig& Config = DefaultLeague();
	FLeagueState State;
	NewLeague(Config, 424242, State);
	TestEqual(TEXT("Eight teams play a 28-day regular season"), RegularSeasonDays(Config), 28);
	TestEqual(TEXT("Four games are scheduled every regular-season day"), static_cast<int32>(GamesOnDay(State, 1).size()), 4);
	int32 Days = 0;
	std::string Error;
	while (State.CompletedSeasons == 0 && Days < 60)
	{
		PrepareDay(Config, State);
		for (const int Id : GamesOnDay(State, State.Day))
		{
			const FScheduledGame& Game = State.Games[static_cast<size_t>(Id - 1)];
			TestTrue(TEXT("Odds are published before tipoff"), Game.bOddsPublished && Game.HomeWinProbabilityE8 > 0 && Game.HomeWinProbabilityE8 < ProbabilityScale);
		}
		TestTrue(TEXT("Every day resolves"), PlayDay(Config, State, nullptr, Error));
		for (const int Id : GamesOnDay(State, State.Day))
		{
			FGameResult Replay;
			TestTrue(TEXT("Replays reproduce the recorded result"), ReplayGame(Config, State, Id, Replay, Error));
		}
		AdvanceDay(Config, State);
		++Days;
	}
	TestEqual(TEXT("A season with playoffs completes"), State.CompletedSeasons, 1);
	TestTrue(TEXT("The playoffs add between four and six days"), Days >= 30 && Days <= 34);
	TestTrue(TEXT("A champion is crowned and remembered into the next season"), State.LastChampion >= 0 && State.SeasonNumber == 2);
	FLeagueState Loaded;
	TestTrue(TEXT("League state survives a save round trip"), DeserializeLeague(Config, SerializeLeague(State), Loaded, Error) && SerializeLeague(Loaded) == SerializeLeague(State));
	TestEqual(TEXT("A winning 40 stake at 50% returns 80"), GrossReturn(40, ProbabilityScale / 2), static_cast<int64>(80));
	TestFalse(TEXT("Stakes must be in steps of ten"), IsValidStake(45));
	return true;
}
#endif
