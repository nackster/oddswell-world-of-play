// OddsWell league core: a dependency-free C++ port of the Python basketball simulator,
// league brains and Match Winner odds, extended from the two-team prototype to an N-team season.
//
// The game simulation, Athlete Life Brain v4, consistency v2, offensive involvement v1,
// fatigue/injury model and public Elo prediction reproduce phase0a/phase0d/phase1h exactly,
// including CPython's Mersenne Twister, so client/tools/league_parity can compare outputs.
// It uses only the standard library so it also builds outside Unreal for that check.
#pragma once

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace OddsWellLeague
{
	// ---- CPython-compatible random number generator -------------------------------------

	class FPyRandom
	{
	public:
		explicit FPyRandom(uint64_t Seed);
		double Random();
		// random.choices(population, weights, k=1)[0] for a population of Count items.
		int Choice(const double* Weights, int Count);
		int Choice(const std::vector<double>& Weights) { return Choice(Weights.data(), static_cast<int>(Weights.size())); }

	private:
		uint32_t NextUInt32();
		uint32_t State[624];
		int Index = 625;
	};

	// round(Value, Digits) with CPython's correctly rounded result.
	double PyRound(double Value, int Digits);
	std::string FormatFixed(double Value, int Digits);

	// ---- Game simulation ----------------------------------------------------------------

	struct FPlayer
	{
		std::string Name;
		int Shooting = 0;
		int Passing = 0;
		int Defense = 0;
		int Rebounding = 0;
		int Stamina = 0;
	};

	struct FTeam
	{
		std::string Name;
		std::vector<FPlayer> Players;
	};

	// Optional pregame inputs. Each enabled map is indexed like the matchup roster:
	// home players first, then away players.
	struct FGameInputs
	{
		bool bHasFatigue = false;
		bool bHasAvailability = false;
		bool bHasReadiness = false;
		bool bHasConsistency = false;
		bool bHasInvolvement = false;
		std::vector<double> Fatigue;
		std::vector<int> Availability;
		std::vector<double> Readiness;
		std::vector<double> ConsistencyStrength;
		std::vector<double> ConsistencyCap;
		std::vector<double> Involvement;
	};

	enum class EEventType : uint8_t
	{
		GameStarted,
		LineupChanged,
		PossessionStarted,
		BrainDecision,
		Turnover,
		PassCompleted,
		ShotMade,
		ShotMissed,
		OffensiveRebound,
		DefensiveRebound,
		ShotClockViolation,
		OvertimeStarted,
		GameEnded,
	};

	const char* EventTypeName(EEventType Type);

	// One authoritative event. Player fields hold matchup roster indexes (-1 when absent);
	// Team fields hold 0 for home and 1 for away.
	struct FEvent
	{
		EEventType Type = EEventType::GameStarted;
		int Sequence = 0;
		int Possession = 0;
		int ClockSeconds = 0;
		int HomeScore = 0;
		int AwayScore = 0;
		int Team = -1;
		int Player = -1;
		int Other = -1; // defender, pass receiver, or decision target
		int ActionKind = 0; // 0 pass, 1 drive, 2 shoot_2, 3 shoot_3, 4 defend
		bool bDefenseDecision = false;
		int Points = 0;
		double Probability = 0.0;
		double BaseProbability = 0.0;
		double ConsistencyCorrection = 0.0;
		double PerformanceResidual = 0.0;
		int Overtime = 0;
		std::vector<int> Lineup;
	};

	struct FGameResult
	{
		uint64_t Seed = 0;
		FTeam Home;
		FTeam Away;
		FGameInputs Inputs;
		int HomeScore = 0;
		int AwayScore = 0;
		int Overtime = 0;
		int Possessions = 0;
		std::vector<FEvent> Events;
		std::vector<double> MinutesPlayed; // rounded to 4 decimals, roster order
		std::vector<double> FinalFatigue;  // rounded to 4 decimals, roster order

		const FPlayer& PlayerAt(int Index) const;
		const std::string& TeamName(int Side) const { return Side == 0 ? Home.Name : Away.Name; }
		int RosterSize() const { return static_cast<int>(Home.Players.size() + Away.Players.size()); }
		int PointsFor(int RosterIndex) const;
	};

	bool SimulateGame(uint64_t Seed, const FTeam& Home, const FTeam& Away, const FGameInputs& Inputs, FGameResult& OutResult, std::string& OutError);

	// The Python simulator's canonical record line ("type|key=value|..."), used for parity checks.
	std::string CanonicalEventLine(const FGameResult& Result, const FEvent& Event);
	const char* ActionKindName(int ActionKind);

	// ---- League ---------------------------------------------------------------------------

	enum class EConsistencyTier : uint8_t { Volatile, Normal, Steady, Elite };
	enum class EInvolvementTier : uint8_t { Low, Standard, Featured };
	enum class EOffDayPreference : uint8_t { Practice, Social };
	enum class ELifeChoice : uint8_t { Train, Rest, Recover, Socialize };

	const char* LifeChoiceName(ELifeChoice Choice);

	struct FAthlete
	{
		FPlayer Ratings;
		EConsistencyTier Consistency = EConsistencyTier::Normal;
		EInvolvementTier Involvement = EInvolvementTier::Standard;
		EOffDayPreference OffDay = EOffDayPreference::Practice;
	};

	struct FLeagueTeam
	{
		std::string Name;
		std::string ShortName;
		std::vector<FAthlete> Roster;
	};

	struct FAthleteState
	{
		double Fatigue = 0.0;
		int RecoveryDays = 0;
		double Readiness = 0.0;
		int RoutineStreak = 0;
		ELifeChoice LastChoice = ELifeChoice::Rest;
		bool bHasLastChoice = false;
		std::vector<std::pair<int, double>> ScoringHistory; // (points, minutes) this season
		int SeasonGames = 0;
		int SeasonPoints = 0;
		double SeasonMinutes = 0.0;
	};

	enum class EGameStage : uint8_t { Regular, Semifinal, Final };

	// Bet markets. Every market is priced from a Monte Carlo of the matchup using the same pregame inputs as
	// the real game but different seeds (never the real game's seed), then quoted with a small house margin.
	// The public Elo probability stays on the game as a published reference number.
	enum class EMarket : uint8_t { MatchWinner = 0, Margin = 1, Overtime = 2, HomeStarPoints = 3, AwayStarPoints = 4, Count = 5 };
	constexpr int MarginBucketCount = 6; // home by 1-5, 6-10, 11+, then away by 1-5, 6-10, 11+
	constexpr int MarketPricingSimulations = 240;
	constexpr int64_t HouseMarginPercent = 4;

	struct FPointsProp
	{
		int RosterSlot = -1;   // within its team
		int LineTenths = 0;    // e.g. 225 means 22.5 points
		int64_t OverE8 = 0;
		int ActualPoints = -1; // filled once played
	};

	struct FScheduledGame
	{
		int Id = 0;
		int Day = 0;
		int Home = 0;
		int Away = 0;
		uint64_t Seed = 0;
		EGameStage Stage = EGameStage::Regular;
		int Series = 0;     // playoff series index (0 or 1 for semifinals)
		int SeriesGame = 0; // 1-based game within the series
		bool bPlayed = false;
		int HomeScore = 0;
		int AwayScore = 0;
		int Overtime = 0;
		// Frozen public pregame odds (public_elo_rotation), set when the day opens.
		bool bOddsPublished = false;
		int64_t HomeWinProbabilityE8 = 0;
		double PublicEloProbability = 0.0;
		// Pregame inputs captured at tipoff, so the replay can be regenerated deterministically.
		std::vector<double> PregameFatigue;
		std::vector<int> PregameAvailability;
		std::vector<double> PregameReadiness;
		// Additional markets, published with the Match Winner odds.
		bool bMarketsPublished = false;
		int64_t MatchWinnerHomeE8 = 0; // fair simulated home-win probability
		int64_t MarginE8[MarginBucketCount] = {};
		int64_t OvertimeE8 = 0;
		FPointsProp Props[2]; // home star, away star
	};

	struct FStanding
	{
		int Wins = 0;
		int Losses = 0;
		int PointsFor = 0;
		int PointsAgainst = 0;
	};

	struct FSeriesState
	{
		int HighSeed = -1;
		int LowSeed = -1;
		int HighWins = 0;
		int LowWins = 0;
		int Winner() const { return HighWins >= 2 ? HighSeed : LowWins >= 2 ? LowSeed : -1; }
	};

	enum class ESeasonPhase : uint8_t { Regular, Semifinals, Final, Complete };

	struct FLeagueState
	{
		uint64_t CareerSeed = 0;
		int SeasonNumber = 1;
		int Day = 1;            // current in-game day of this season, 1-based
		bool bDayPrepared = false;
		bool bDayPlayed = false;
		ESeasonPhase Phase = ESeasonPhase::Regular;
		std::vector<FAthleteState> Athletes; // team-major roster order
		std::vector<double> Elo;
		std::vector<FStanding> Standings;
		std::vector<FScheduledGame> Games;
		FSeriesState Semifinals[2];
		FSeriesState FinalSeries;
		int Champion = -1;     // this season, once the final is decided
		int LastChampion = -1; // most recently completed season
		int CompletedSeasons = 0;
	};

	struct FLeagueConfig
	{
		std::vector<FLeagueTeam> Teams;
		int RoundRobinCycles = 4; // 8 teams x 4 cycles = 28 regular-season games per team
	};

	// Built-in eight-team fictional league.
	const FLeagueConfig& DefaultLeague();
	// The original two-team prototype league (for parity checks).
	FLeagueConfig PrototypeLeague();

	int AthleteIndex(const FLeagueConfig& Config, int Team, int RosterSlot);
	int RegularSeasonDays(const FLeagueConfig& Config);

	// Create a fresh league for a new career.
	void NewLeague(const FLeagueConfig& Config, uint64_t CareerSeed, FLeagueState& OutState);
	// Morning: rest recovery and Athlete Life Brain choices, then publish today's odds. Idempotent per day.
	void PrepareDay(const FLeagueConfig& Config, FLeagueState& State);
	// Evening: resolve every game today, update standings, Elo, injuries and playoffs. Idempotent per day.
	bool PlayDay(const FLeagueConfig& Config, FLeagueState& State, std::vector<FGameResult>* OutResults, std::string& OutError);
	// Move to the next day (or start the next season after the final). Requires the day to be played.
	void AdvanceDay(const FLeagueConfig& Config, FLeagueState& State);

	std::vector<int> GamesOnDay(const FLeagueState& State, int Day);
	std::vector<int> RankedTeams(const FLeagueConfig& Config, const FLeagueState& State);
	// Regenerate the full authoritative game from its frozen pregame inputs.
	bool ReplayGame(const FLeagueConfig& Config, const FLeagueState& State, int GameId, FGameResult& OutResult, std::string& OutError);
	const char* StageName(EGameStage Stage);

	// ---- Match Winner odds (phase1h/odds.py) ----------------------------------------------

	constexpr int64_t ProbabilityScale = 100000000;
	constexpr int64_t MinimumStake = 10;
	constexpr int64_t MaximumStake = 100;
	constexpr int64_t StakeIncrement = 10;

	// Public pregame probabilities for a matchup: (public_elo, public_elo_rotation), each rounded to 8 decimals.
	std::pair<double, double> PredictHomeWin(const FTeam& Home, const FTeam& Away, const std::vector<int>& HomeAvailability, const std::vector<int>& AwayAvailability, double HomeElo, double AwayElo);
	int64_t ProbabilityToE8(double RoundedProbability);
	int64_t DecimalOddsE4(int64_t WinProbabilityE8);
	bool IsValidStake(int64_t Stake);
	int64_t GrossReturn(int64_t Stake, int64_t WinProbabilityE8);

	// Markets: outcome counts, prices and settlement.
	int MarketOutcomeCount(EMarket Market);
	int MarginBucket(int HomeScore, int AwayScore);
	// The fair simulated probability of an outcome.
	int64_t FairProbabilityE8(const FScheduledGame& Game, EMarket Market, int Outcome);
	// The quoted probability (fair plus the house margin) that sets the payout.
	int64_t OutcomeProbabilityE8(const FScheduledGame& Game, EMarket Market, int Outcome);
	bool IsOutcomeAvailable(const FScheduledGame& Game, EMarket Market);
	// Returns false while the game is unplayed.
	bool DidOutcomeWin(const FScheduledGame& Game, EMarket Market, int Outcome, bool& bOutWon);
	void PriceGameMarkets(const FLeagueConfig& Config, const FLeagueState& State, FScheduledGame& Game);

	// ---- Persistence ----------------------------------------------------------------------

	std::string SerializeLeague(const FLeagueState& State);
	bool DeserializeLeague(const FLeagueConfig& Config, const std::string& Text, FLeagueState& OutState, std::string& OutError);

	// ---- Lower-level league steps, exposed for the two-team parity check -----------------

	FTeam TeamForGame(const FLeagueConfig& Config, int Team);
	void RecoverDays(FLeagueState& State, int Days, int FirstAthlete, int AthleteCount);
	void ApplyLifeDay(const FLeagueConfig& Config, FLeagueState& State, int Day, bool bUseScoringForm);
	void BuildGameInputs(const FLeagueConfig& Config, const FLeagueState& State, int Home, int Away, FGameInputs& OutInputs);
	void ApplyGameAftermath(const FLeagueConfig& Config, FLeagueState& State, const FScheduledGame& Game, const FGameResult& Result);
}
