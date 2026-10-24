#pragma once

#include "CoreMinimal.h"
#include "Career/OddsWellCatalog.h"
#include "GameFramework/SaveGame.h"
#include "League/OddsWellLeagueCore.h"
#include "OddsBucksLedger.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "OddsWellCareer.generated.h"

// Normal play runs the single-player career (DEC-037). The older evidence lanes launched with
// a "...Qa" command-line flag keep their original fixed-scenario behaviour untouched.
ODDSWELL_API bool IsOddsWellCareerMode();

UENUM()
enum class EOddsWellCareerWagerStatus : uint8
{
	Pending,
	Won,
	Lost,
};

USTRUCT()
struct FOddsWellCareerWager
{
	GENERATED_BODY()

	UPROPERTY(SaveGame)
	int32 Id = 0;

	UPROPERTY(SaveGame)
	int32 Season = 0;

	UPROPERTY(SaveGame)
	int32 GameId = 0;

	// OddsWellLeague::EMarket; saves from before M3 load as Match Winner.
	UPROPERTY(SaveGame)
	int32 Market = 0;

	// Outcome index within the market (Match Winner: 0 = home team, 1 = away team).
	UPROPERTY(SaveGame)
	int32 Selection = 0;

	UPROPERTY(SaveGame)
	int64 Stake = 0;

	UPROPERTY(SaveGame)
	int64 WinProbabilityE8 = 0;

	UPROPERTY(SaveGame)
	EOddsWellCareerWagerStatus Status = EOddsWellCareerWagerStatus::Pending;

	UPROPERTY(SaveGame)
	int64 Payout = 0;
};

UCLASS()
class ODDSWELL_API UOddsWellCareerSave : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame)
	int32 Schema = 1;

	UPROPERTY(SaveGame)
	FString League;

	UPROPERTY(SaveGame)
	TArray<FOddsWellOddsBucksEntry> Ledger;

	UPROPERTY(SaveGame)
	TArray<FOddsWellCareerWager> Wagers;

	UPROPERTY(SaveGame)
	FString LastShiftKey;

	UPROPERTY(SaveGame)
	int32 NextWagerId = 1;

	UPROPERTY(SaveGame)
	FString MorningReport;

	UPROPERTY(SaveGame)
	int32 TutorialFlags = 0;

	UPROPERTY(SaveGame)
	int32 ShiftsWorked = 0;

	UPROPERTY(SaveGame)
	int32 GamesWatched = 0;

	UPROPERTY(SaveGame)
	FName EquippedTop;

	UPROPERTY(SaveGame)
	FName EquippedBottom;

	UPROPERTY(SaveGame)
	TArray<FName> Achievements;
};

// The job ladder (D7): one shift a day, and shifts worked unlock better-paid jobs.
struct FOddsWellJob
{
	const TCHAR* Title;
	int64 Pay;
	int32 ShiftsRequired;
};
ODDSWELL_API TConstArrayView<FOddsWellJob> GetOddsWellJobs();

// First-day guide steps, in order.
enum class EOddsWellTutorialStep : int32
{
	Shift = 1 << 0,
	Bet = 1 << 1,
	Watch = 1 << 2,
	Sleep = 1 << 3,
	All = Shift | Bet | Watch | Sleep,
};

struct FOddsWellCareerReplayFrame
{
	FString Kind;
	FString Label;
	FString Offense;
	FString Actor;
	FString Target;
	int32 ClockSeconds = 0;
	int32 Period = 1; // 1-4 quarters, 5+ overtime periods
	int32 HomeScore = 0;
	int32 AwayScore = 0;
};

struct FOddsWellCareerReplay
{
	int32 GameId = 0;
	FString HomeTeam;
	FString AwayTeam;
	TArray<FString> HomePlayers;
	TArray<FString> AwayPlayers;
	TArray<FOddsWellCareerReplayFrame> Frames;
	int32 HomeScore = 0;
	int32 AwayScore = 0;
	int32 Overtime = 0;
};

UCLASS()
class ODDSWELL_API UOddsWellCareerSubsystem final : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	static UOddsWellCareerSubsystem* Get(const UObject* WorldContext);

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	bool IsReady() const { return bReady; }
	const FString& GetLoadError() const { return LoadError; }

	// League queries.
	const OddsWellLeague::FLeagueConfig& GetConfig() const { return OddsWellLeague::DefaultLeague(); }
	const OddsWellLeague::FLeagueState& GetLeague() const { return League; }
	int32 GetSeason() const { return League.SeasonNumber; }
	int32 GetDay() const { return League.Day; }
	bool HaveTodaysGamesTippedOff() const { return League.bDayPlayed; }
	TArray<int32> GetTodaysGameIds() const;
	const OddsWellLeague::FScheduledGame* FindGame(int32 GameId) const;
	FString GetTeamName(int32 Team) const;
	FString GetTeamShortName(int32 Team) const;
	FString GetPhaseText() const;
	FString DescribeGame(const OddsWellLeague::FScheduledGame& Game) const;
	TArray<FString> BuildStandingsLines() const;

	// Odds Bucks.
	int64 GetBalance() const { return Ledger.GetBalance(); }
	const FOddsWellOddsBucksLedger& GetLedger() const { return Ledger; }
	// Replace the ledger with a candidate that extends it (shop purchases), then save.
	bool CommitLedger(const FOddsWellOddsBucksLedger& Candidate, FString& OutError);

	// Work: one paid shift per in-game day.
	bool HasWorkedToday() const;
	bool WorkShift(bool& bOutCredited, int64& OutBalance, FString& OutError);
	int32 GetShiftsWorked() const { return ShiftsWorked; }
	int32 GetJobLevel() const;
	const FOddsWellJob& GetJob() const { return GetOddsWellJobs()[GetJobLevel()]; }
	FString GetShiftPrompt() const;
	const FString& GetLastShiftMessage() const { return LastShiftMessage; }

	// Wagers: one per market per game on today's games until tipoff.
	const FOddsWellCareerWager* FindWager(int32 GameId, OddsWellLeague::EMarket Market) const;
	int32 CountWagersOnGame(int32 GameId) const;
	int32 GetWagerCount() const { return Wagers.Num(); }
	TArray<FOddsWellCareerWager> GetWagersForDay(int32 Season, int32 Day) const;
	bool PlaceWager(int32 GameId, OddsWellLeague::EMarket Market, int32 Selection, int64 Stake, FString& OutError);
	FString GetMarketName(const OddsWellLeague::FScheduledGame& Game, OddsWellLeague::EMarket Market) const;
	FString DescribeOutcome(const OddsWellLeague::FScheduledGame& Game, OddsWellLeague::EMarket Market, int32 Outcome) const;
	FString DescribeWager(const FOddsWellCareerWager& Wager) const;

	// Day flow.
	bool TipOffToday(FString& OutError);
	// A tipped-off game's score stays hidden, and its bets unsettled, until it is watched or the day ends.
	void RevealGame(int32 GameId);
	bool IsGameRevealed(int32 GameId) const;
	FString DescribeGameForPlayer(const OddsWellLeague::FScheduledGame& Game) const;
	bool SleepUntilTomorrow(FString& OutError);
	const FString& GetMorningReport() const { return MorningReport; }
	void DismissMorningReport();
	int32 GetTutorialFlags() const { return TutorialFlags; }
	bool IsTutorialComplete() const { return (TutorialFlags & static_cast<int32>(EOddsWellTutorialStep::All)) == static_cast<int32>(EOddsWellTutorialStep::All); }

	// Shopping (D7): homes, furniture and clothing, owned through the Odds Bucks ledger.
	bool OwnsItem(FName ItemId) const;
	// Why an item cannot be bought right now (empty when it can).
	FString GetPurchaseBlocker(const FOddsWellCatalogItem& Item) const;
	bool BuyItem(FName ItemId, FString& OutError);
	int32 GetHomeTier() const;
	int32 CountOwned(EOddsWellCatalogKind Kind) const;
	TArray<FName> GetOwnedFurniture() const;
	FName GetEquipped(EOddsWellCatalogKind Kind) const;
	bool EquipItem(FName ItemId, FString& OutError);
	bool IsSeasonGoalComplete() const { return GetHomeTier() >= GetOddsWellApartmentTierCount() - 1; }

	// Achievements (local for now; mirrored to Epic Online Services in M6).
	bool HasAchievement(FName Id) const { return Achievements.Contains(Id); }
	int32 GetAchievementCount() const { return Achievements.Num(); }
	// The next "achievement unlocked" message to show, or empty.
	FString PopAchievementToast();

	// Watching.
	bool BuildReplay(int32 GameId, FOddsWellCareerReplay& OutReplay, FString& OutError) const;
	void SetGameToWatch(int32 GameId) { GameToWatch = GameId; }
	int32 GetGameToWatch() const { return GameToWatch; }

	// Starts a brand-new career (used by tests and a future "new game" menu).
	bool StartNewCareer(uint64 CareerSeed, FString& OutError);
	bool HasCareer() const { return bReady; }
	bool EnsureCareerStarted(FString& OutError);
	static uint64 DefaultNewCareerSeed();

private:
	bool Save(FString& OutError);
	bool LoadOrCreate(FString& OutError);
	void SettleWagers(int32 OnlyGameId);
	void MarkTutorial(EOddsWellTutorialStep Step) { TutorialFlags |= static_cast<int32>(Step); }
	// Unlocks any newly earned achievements and saves when something changed.
	void CheckAchievements();

	OddsWellLeague::FLeagueState League;
	FOddsWellOddsBucksLedger Ledger;
	TArray<FOddsWellCareerWager> Wagers;
	FString LastShiftKey;
	FString MorningReport;
	FString LastShiftMessage;
	FString LoadError;
	TSet<int32> RevealedGames;
	int32 NextWagerId = 1;
	int32 GameToWatch = 0;
	int32 TutorialFlags = 0;
	int32 ShiftsWorked = 0;
	int32 GamesWatched = 0;
	FName EquippedTop;
	FName EquippedBottom;
	TArray<FName> Achievements;
	TArray<FString> PendingToasts;
	bool bReady = false;
};
