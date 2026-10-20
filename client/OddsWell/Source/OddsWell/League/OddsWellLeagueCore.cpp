#include "OddsWellLeagueCore.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>
#include <sstream>

// Results must match the Python reference bit for bit, so never contract or reorder floating point here.
#if defined(_MSC_VER)
#pragma float_control(precise, on, push)
#pragma fp_contract(off)
#endif

namespace OddsWellLeague
{
namespace
{
	const char* EngineVersion = "phase05h-v1";
	const char* BrainVersion = "baseline-v2";
	constexpr int RegulationSeconds = 48 * 60;
	constexpr int RotationSegmentSeconds = RegulationSeconds / 10;
	constexpr int PossessionSeconds = 14;
	constexpr double MaxGameFatigue = 0.45;
	constexpr double MaxCarryoverFatigue = 0.35;
	constexpr double RecoveryPerDay = 0.04;
	constexpr double MaxReadiness = 0.02;
	constexpr double HighFatigue = 0.24;
	constexpr double MaxInjuryRisk = 0.04;
	constexpr uint64_t InjurySeedSalt = 0x1A11AB1E;
	constexpr int OffseasonRestDays = 7;
	constexpr double EloK = 20.0;
	constexpr double HomeAdvantageElo = 55.0;
	constexpr double RatingDifferenceElo = 6.0;
	const int InjuryRecoveryDays[] = {2, 3, 5, 7};
	const double InjuryRecoveryWeights[] = {50, 30, 15, 5};

	double Clamp(double Value, double Minimum, double Maximum)
	{
		return std::max(Minimum, std::min(Maximum, Value));
	}

	double ConsistencyStrength(EConsistencyTier Tier)
	{
		switch (Tier)
		{
		case EConsistencyTier::Normal: return 0.15;
		case EConsistencyTier::Steady: return 0.30;
		case EConsistencyTier::Elite: return 0.50;
		default: return 0.0;
		}
	}

	double ConsistencyCap(EConsistencyTier Tier)
	{
		switch (Tier)
		{
		case EConsistencyTier::Normal: return 0.03;
		case EConsistencyTier::Steady: return 0.06;
		case EConsistencyTier::Elite: return 0.10;
		default: return 0.0;
		}
	}

	double InvolvementWeight(EInvolvementTier Tier)
	{
		switch (Tier)
		{
		case EInvolvementTier::Low: return 0.85;
		case EInvolvementTier::Featured: return 1.15;
		default: return 1.0;
		}
	}

	std::string Fixed6(double Value)
	{
		return FormatFixed(Value, 6);
	}

	template <typename TValue>
	std::string SortedDict(std::vector<std::pair<std::string, TValue>> Items, std::string (*Format)(const TValue&))
	{
		std::sort(Items.begin(), Items.end(), [](const auto& A, const auto& B) { return A.first < B.first; });
		std::string Text = "{";
		for (size_t Index = 0; Index < Items.size(); ++Index)
		{
			if (Index)
			{
				Text += ";";
			}
			Text += Items[Index].first + ":" + Format(Items[Index].second);
		}
		return Text + "}";
	}

	std::string FormatDouble(const double& Value) { return Fixed6(Value); }
	std::string FormatInt(const int& Value) { return std::to_string(Value); }
	std::string FormatString(const std::string& Value) { return Value; }
}

// ---- Random -------------------------------------------------------------------------------

FPyRandom::FPyRandom(uint64_t Seed)
{
	State[0] = 19650218u;
	for (int I = 1; I < 624; ++I)
	{
		State[I] = 1812433253u * (State[I - 1] ^ (State[I - 1] >> 30)) + static_cast<uint32_t>(I);
	}
	uint32_t Key[2] = {static_cast<uint32_t>(Seed & 0xFFFFFFFFu), static_cast<uint32_t>(Seed >> 32)};
	const int KeyLength = Key[1] ? 2 : 1;
	int I = 1;
	int J = 0;
	for (int K = 624 > KeyLength ? 624 : KeyLength; K; --K)
	{
		State[I] = (State[I] ^ ((State[I - 1] ^ (State[I - 1] >> 30)) * 1664525u)) + Key[J] + static_cast<uint32_t>(J);
		++I;
		++J;
		if (I >= 624)
		{
			State[0] = State[623];
			I = 1;
		}
		if (J >= KeyLength)
		{
			J = 0;
		}
	}
	for (int K = 623; K; --K)
	{
		State[I] = (State[I] ^ ((State[I - 1] ^ (State[I - 1] >> 30)) * 1566083941u)) - static_cast<uint32_t>(I);
		++I;
		if (I >= 624)
		{
			State[0] = State[623];
			I = 1;
		}
	}
	State[0] = 0x80000000u;
	Index = 624;
}

uint32_t FPyRandom::NextUInt32()
{
	static const uint32_t Mag01[2] = {0x0u, 0x9908b0dfu};
	if (Index >= 624)
	{
		int K = 0;
		uint32_t Y;
		for (; K < 624 - 397; ++K)
		{
			Y = (State[K] & 0x80000000u) | (State[K + 1] & 0x7fffffffu);
			State[K] = State[K + 397] ^ (Y >> 1) ^ Mag01[Y & 0x1u];
		}
		for (; K < 623; ++K)
		{
			Y = (State[K] & 0x80000000u) | (State[K + 1] & 0x7fffffffu);
			State[K] = State[K + (397 - 624)] ^ (Y >> 1) ^ Mag01[Y & 0x1u];
		}
		Y = (State[623] & 0x80000000u) | (State[0] & 0x7fffffffu);
		State[623] = State[396] ^ (Y >> 1) ^ Mag01[Y & 0x1u];
		Index = 0;
	}
	uint32_t Y = State[Index++];
	Y ^= (Y >> 11);
	Y ^= (Y << 7) & 0x9d2c5680u;
	Y ^= (Y << 15) & 0xefc60000u;
	Y ^= (Y >> 18);
	return Y;
}

double FPyRandom::Random()
{
	const uint32_t A = NextUInt32() >> 5;
	const uint32_t B = NextUInt32() >> 6;
	return (A * 67108864.0 + B) * (1.0 / 9007199254740992.0);
}

int FPyRandom::Choice(const double* Weights, int Count)
{
	std::vector<double> Cumulative(static_cast<size_t>(Count));
	double Running = 0.0;
	for (int I = 0; I < Count; ++I)
	{
		Running = I == 0 ? Weights[0] : Running + Weights[I];
		Cumulative[static_cast<size_t>(I)] = Running;
	}
	const double Total = Cumulative[static_cast<size_t>(Count - 1)] + 0.0;
	const double Target = Random() * Total;
	int Low = 0;
	int High = Count - 1;
	while (Low < High)
	{
		const int Mid = (Low + High) / 2;
		if (Target < Cumulative[static_cast<size_t>(Mid)])
		{
			High = Mid;
		}
		else
		{
			Low = Mid + 1;
		}
	}
	return Low;
}

std::string FormatFixed(double Value, int Digits)
{
	char Buffer[64];
	std::snprintf(Buffer, sizeof(Buffer), "%.*f", Digits, Value);
	return Buffer;
}

double PyRound(double Value, int Digits)
{
	return std::strtod(FormatFixed(Value, Digits).c_str(), nullptr);
}

// ---- Game simulation ------------------------------------------------------------------------

const char* EventTypeName(EEventType Type)
{
	switch (Type)
	{
	case EEventType::GameStarted: return "game_started";
	case EEventType::LineupChanged: return "lineup_changed";
	case EEventType::PossessionStarted: return "possession_started";
	case EEventType::BrainDecision: return "brain_decision";
	case EEventType::Turnover: return "turnover";
	case EEventType::PassCompleted: return "pass_completed";
	case EEventType::ShotMade: return "shot_made";
	case EEventType::ShotMissed: return "shot_missed";
	case EEventType::OffensiveRebound: return "offensive_rebound";
	case EEventType::DefensiveRebound: return "defensive_rebound";
	case EEventType::ShotClockViolation: return "shot_clock_violation";
	case EEventType::OvertimeStarted: return "overtime_started";
	default: return "game_ended";
	}
}

const char* ActionKindName(int ActionKind)
{
	static const char* Names[] = {"pass", "drive", "shoot_2", "shoot_3", "defend"};
	return ActionKind >= 0 && ActionKind <= 4 ? Names[ActionKind] : "";
}

const FPlayer& FGameResult::PlayerAt(int RosterIndex) const
{
	const int HomeCount = static_cast<int>(Home.Players.size());
	return RosterIndex < HomeCount ? Home.Players[static_cast<size_t>(RosterIndex)] : Away.Players[static_cast<size_t>(RosterIndex - HomeCount)];
}

int FGameResult::PointsFor(int RosterIndex) const
{
	int Points = 0;
	for (const FEvent& Event : Events)
	{
		if (Event.Type == EEventType::ShotMade && Event.Player == RosterIndex)
		{
			Points += Event.Points;
		}
	}
	return Points;
}

bool SimulateGame(uint64_t Seed, const FTeam& Home, const FTeam& Away, const FGameInputs& Inputs, FGameResult& OutResult, std::string& OutError)
{
	OutResult = FGameResult();
	OutResult.Seed = Seed;
	OutResult.Home = Home;
	OutResult.Away = Away;
	OutResult.Inputs = Inputs;
	const int HomeCount = static_cast<int>(Home.Players.size());
	const int RosterCount = HomeCount + static_cast<int>(Away.Players.size());
	std::vector<const FPlayer*> Roster;
	for (const FPlayer& Player : Home.Players)
	{
		Roster.push_back(&Player);
	}
	for (const FPlayer& Player : Away.Players)
	{
		Roster.push_back(&Player);
	}
	auto SizeMatches = [RosterCount](bool bEnabled, size_t Size) { return !bEnabled || static_cast<int>(Size) == RosterCount; };
	if (!SizeMatches(Inputs.bHasFatigue, Inputs.Fatigue.size())
		|| !SizeMatches(Inputs.bHasAvailability, Inputs.Availability.size())
		|| !SizeMatches(Inputs.bHasReadiness, Inputs.Readiness.size())
		|| !SizeMatches(Inputs.bHasConsistency, Inputs.ConsistencyStrength.size())
		|| !SizeMatches(Inputs.bHasConsistency, Inputs.ConsistencyCap.size())
		|| !SizeMatches(Inputs.bHasInvolvement, Inputs.Involvement.size()))
	{
		OutError = "game inputs must cover every matchup player exactly once";
		return false;
	}

	std::vector<double> Fatigue(static_cast<size_t>(RosterCount), 0.0);
	std::vector<bool> Unavailable(static_cast<size_t>(RosterCount), false);
	std::vector<double> Readiness(static_cast<size_t>(RosterCount), 0.0);
	std::vector<double> Strength(static_cast<size_t>(RosterCount), 0.0);
	std::vector<double> Cap(static_cast<size_t>(RosterCount), 0.0);
	std::vector<double> Involvement(static_cast<size_t>(RosterCount), 1.0);
	for (int I = 0; I < RosterCount; ++I)
	{
		const size_t S = static_cast<size_t>(I);
		if (Inputs.bHasFatigue)
		{
			Fatigue[S] = Inputs.Fatigue[S];
		}
		if (Inputs.bHasAvailability)
		{
			Unavailable[S] = Inputs.Availability[S] != 0;
		}
		if (Inputs.bHasReadiness)
		{
			Readiness[S] = Inputs.Readiness[S];
		}
		if (Inputs.bHasConsistency)
		{
			Strength[S] = Inputs.ConsistencyStrength[S];
			Cap[S] = Inputs.ConsistencyCap[S];
		}
		if (Inputs.bHasInvolvement)
		{
			Involvement[S] = Inputs.Involvement[S];
		}
	}
	for (int Side = 0; Side < 2; ++Side)
	{
		const int First = Side == 0 ? 0 : HomeCount;
		const int Last = Side == 0 ? HomeCount : RosterCount;
		int Available = 0;
		for (int I = First; I < Last; ++I)
		{
			Available += Unavailable[static_cast<size_t>(I)] ? 0 : 1;
		}
		if (Available < 5)
		{
			OutError = (Side == 0 ? Home.Name : Away.Name) + " needs at least five available players";
			return false;
		}
	}

	FPyRandom DecisionRng(Seed ^ 0xA11CEull);
	FPyRandom OutcomeRng(Seed ^ 0xDDF00Dull);
	std::vector<int> SecondsPlayed(static_cast<size_t>(RosterCount), 0);
	std::vector<double> ExpectedPoints(static_cast<size_t>(RosterCount), 0.0);
	std::vector<int> ActualPoints(static_cast<size_t>(RosterCount), 0);
	std::vector<int> PreviousLineup[2];
	int Score[2] = {0, 0};
	int Clock = RegulationSeconds;
	int PossessionNumber = 0;
	int OffenseSide = 0;
	int Overtime = 0;
	std::vector<FEvent>& Events = OutResult.Events;

	auto Record = [&Events, &Score](EEventType Type) -> FEvent&
	{
		FEvent Event;
		Event.Type = Type;
		Event.Sequence = static_cast<int>(Events.size()) + 1;
		Event.HomeScore = Score[0];
		Event.AwayScore = Score[1];
		Events.push_back(Event);
		return Events.back();
	};

	auto RotationLineup = [&](int Side) -> std::vector<int>
	{
		const int First = Side == 0 ? 0 : HomeCount;
		const int Last = Side == 0 ? HomeCount : RosterCount;
		std::vector<int> Available;
		for (int I = First; I < Last; ++I)
		{
			if (!Unavailable[static_cast<size_t>(I)])
			{
				Available.push_back(I);
			}
		}
		std::vector<int> Starters(Available.begin(), Available.begin() + 5);
		if (Available.size() == 5 || Overtime)
		{
			return Starters;
		}
		const int Segment = std::min(9, (RegulationSeconds - Clock) / RotationSegmentSeconds);
		if (Segment % 2 == 0)
		{
			return Starters;
		}
		const int Resting = Segment / 2;
		std::vector<int> Lineup;
		for (int I = 0; I < 5; ++I)
		{
			if (I != Resting)
			{
				Lineup.push_back(Starters[static_cast<size_t>(I)]);
			}
		}
		Lineup.push_back(Available[5]);
		return Lineup;
	};

	Record(EEventType::GameStarted);
	while (Clock > 0 || Score[0] == Score[1])
	{
		if (Clock == 0)
		{
			++Overtime;
			Clock = 5 * 60;
			Record(EEventType::OvertimeStarted).Overtime = Overtime;
		}
		std::vector<int> Lineups[2] = {RotationLineup(0), RotationLineup(1)};
		for (int Side = 0; Side < 2; ++Side)
		{
			if (PreviousLineup[Side] != Lineups[Side])
			{
				FEvent& Event = Record(EEventType::LineupChanged);
				Event.Team = Side;
				Event.Lineup = Lineups[Side];
				Event.ClockSeconds = Clock;
				PreviousLineup[Side] = Lineups[Side];
			}
		}
		const std::vector<int>& Offense = Lineups[OffenseSide];
		const std::vector<int>& Defense = Lineups[1 - OffenseSide];
		++PossessionNumber;
		std::vector<double> Weights;
		for (int Player : Offense)
		{
			const FPlayer& Ratings = *Roster[static_cast<size_t>(Player)];
			double Weight = static_cast<double>(Ratings.Passing + Ratings.Shooting);
			if (Inputs.bHasInvolvement)
			{
				Weight = Weight * Involvement[static_cast<size_t>(Player)];
			}
			Weights.push_back(Weight);
		}
		int Ballhandler = Offense[static_cast<size_t>(OutcomeRng.Choice(Weights))];
		{
			FEvent& Event = Record(EEventType::PossessionStarted);
			Event.Possession = PossessionNumber;
			Event.Team = OffenseSide;
			Event.Player = Ballhandler;
			Event.ClockSeconds = Clock;
		}

		bool bEnded = false;
		for (int DecisionNumber = 1; DecisionNumber <= 4; ++DecisionNumber)
		{
			Weights.clear();
			for (int Player : Defense)
			{
				Weights.push_back(static_cast<double>(Roster[static_cast<size_t>(Player)]->Defense));
			}
			const int Defender = Defense[static_cast<size_t>(DecisionRng.Choice(Weights))];
			{
				FEvent& Event = Record(EEventType::BrainDecision);
				Event.bDefenseDecision = true;
				Event.ActionKind = 4;
				Event.Player = Defender;
				Event.Other = Ballhandler;
				Event.Possession = PossessionNumber;
				Event.ClockSeconds = Clock;
			}

			const FPlayer& Handler = *Roster[static_cast<size_t>(Ballhandler)];
			const bool bTrailing = Score[OffenseSide] < Score[1 - OffenseSide];
			const double KindWeights[4] = {
				static_cast<double>(std::max(10, Handler.Passing - 45)),
				24.0,
				static_cast<double>(std::max(10, Handler.Shooting - 45)),
				static_cast<double>(std::max(8, Handler.Shooting - (bTrailing ? 52 : 58))),
			};
			const int Kind = DecisionRng.Choice(KindWeights, 4);
			int PassTarget = -1;
			if (Kind == 0)
			{
				std::vector<int> Targets;
				Weights.clear();
				for (int Player : Offense)
				{
					if (Player != Ballhandler)
					{
						Targets.push_back(Player);
						const double Shooting = static_cast<double>(Roster[static_cast<size_t>(Player)]->Shooting);
						Weights.push_back(Inputs.bHasInvolvement ? Shooting * Involvement[static_cast<size_t>(Player)] : Shooting);
					}
				}
				PassTarget = Targets[static_cast<size_t>(DecisionRng.Choice(Weights))];
			}
			{
				FEvent& Event = Record(EEventType::BrainDecision);
				Event.ActionKind = Kind;
				Event.Player = Ballhandler;
				Event.Other = PassTarget;
				Event.Possession = PossessionNumber;
				Event.ClockSeconds = Clock;
			}

			const FPlayer& DefenderRatings = *Roster[static_cast<size_t>(Defender)];
			const double AttackerFatigue = Fatigue[static_cast<size_t>(Ballhandler)];
			if (Kind == 0)
			{
				const double TurnoverChance = Clamp(
					0.17
					+ static_cast<double>(DefenderRatings.Defense - Handler.Passing) / 250.0
					+ AttackerFatigue * 0.12
					- Readiness[static_cast<size_t>(Ballhandler)]
					+ 0.0
					- 0.0,
					0.05,
					0.32);
				if (OutcomeRng.Random() < TurnoverChance)
				{
					FEvent& Event = Record(EEventType::Turnover);
					Event.Possession = PossessionNumber;
					Event.Player = Ballhandler;
					Event.Other = Defender;
					bEnded = true;
					break;
				}
				FEvent& Event = Record(EEventType::PassCompleted);
				Event.Possession = PossessionNumber;
				Event.Player = Ballhandler;
				Event.Other = PassTarget;
				Ballhandler = PassTarget;
				continue;
			}

			const int Points = Kind == 3 ? 3 : 2;
			const double BaseChance = Kind == 1 ? 0.52 : Kind == 2 ? 0.45 : 0.34;
			const double BaseMakeChance = Clamp(
				BaseChance
				+ static_cast<double>(Handler.Shooting - DefenderRatings.Defense) / 220.0
				- AttackerFatigue * 0.15
				+ Readiness[static_cast<size_t>(Ballhandler)]
				+ 0.0
				- 0.0,
				0.08,
				0.78);
			const size_t H = static_cast<size_t>(Ballhandler);
			const double Residual = ExpectedPoints[H] - static_cast<double>(ActualPoints[H]);
			const double Correction = Clamp((Residual / 2.0) * Strength[H], -Cap[H], Cap[H]);
			const double MakeChance = Clamp(BaseMakeChance + Correction, 0.08, 0.78);
			const bool bMade = OutcomeRng.Random() < MakeChance;
			{
				FEvent& Event = Record(bMade ? EEventType::ShotMade : EEventType::ShotMissed);
				Event.Possession = PossessionNumber;
				Event.Player = Ballhandler;
				Event.Other = Defender;
				Event.ActionKind = Kind;
				Event.Points = Points;
				Event.Probability = PyRound(MakeChance, 4);
				Event.BaseProbability = PyRound(BaseMakeChance, 4);
				Event.ConsistencyCorrection = PyRound(Correction, 4);
				Event.PerformanceResidual = PyRound(Residual, 4);
			}
			ExpectedPoints[H] += BaseMakeChance * Points;
			if (bMade)
			{
				ActualPoints[H] += Points;
				Score[OffenseSide] += Points;
				Events.back().HomeScore = Score[0];
				Events.back().AwayScore = Score[1];
				bEnded = true;
				break;
			}

			int OffenseRebounding = 0;
			int DefenseRebounding = 0;
			for (int Player : Offense)
			{
				OffenseRebounding += Roster[static_cast<size_t>(Player)]->Rebounding;
			}
			for (int Player : Defense)
			{
				DefenseRebounding += Roster[static_cast<size_t>(Player)]->Rebounding;
			}
			const double OffenseAverage = static_cast<double>(OffenseRebounding) / static_cast<double>(Offense.size());
			const double DefenseAverage = static_cast<double>(DefenseRebounding) / static_cast<double>(Defense.size());
			const double ReboundChance = Clamp(0.24 + (OffenseAverage - DefenseAverage) / 400.0, 0.12, 0.42);
			if (DecisionNumber < 4 && OutcomeRng.Random() < ReboundChance)
			{
				Weights.clear();
				for (int Player : Offense)
				{
					Weights.push_back(static_cast<double>(Roster[static_cast<size_t>(Player)]->Rebounding));
				}
				const int Rebounder = Offense[static_cast<size_t>(OutcomeRng.Choice(Weights))];
				Ballhandler = Rebounder;
				FEvent& Event = Record(EEventType::OffensiveRebound);
				Event.Possession = PossessionNumber;
				Event.Player = Rebounder;
				continue;
			}
			Weights.clear();
			for (int Player : Defense)
			{
				Weights.push_back(static_cast<double>(Roster[static_cast<size_t>(Player)]->Rebounding));
			}
			const int Rebounder = Defense[static_cast<size_t>(OutcomeRng.Choice(Weights))];
			FEvent& Event = Record(EEventType::DefensiveRebound);
			Event.Possession = PossessionNumber;
			Event.Player = Rebounder;
			bEnded = true;
			break;
		}
		if (!bEnded)
		{
			FEvent& Event = Record(EEventType::ShotClockViolation);
			Event.Possession = PossessionNumber;
			Event.Team = OffenseSide;
		}

		const int Elapsed = std::min(PossessionSeconds, Clock);
		for (int Side = 0; Side < 2; ++Side)
		{
			for (int Player : Lineups[Side])
			{
				const size_t P = static_cast<size_t>(Player);
				SecondsPlayed[P] += Elapsed;
				const double PerPossession = 0.0015 + static_cast<double>(100 - Roster[P]->Stamina) / 50000.0;
				Fatigue[P] = std::min(MaxGameFatigue, Fatigue[P] + PerPossession * (static_cast<double>(Elapsed) / static_cast<double>(PossessionSeconds)));
			}
		}
		Clock -= Elapsed;
		OffenseSide = 1 - OffenseSide;
	}

	for (int I = 0; I < RosterCount; ++I)
	{
		const size_t S = static_cast<size_t>(I);
		OutResult.MinutesPlayed.push_back(PyRound(static_cast<double>(SecondsPlayed[S]) / 60.0, 4));
		OutResult.FinalFatigue.push_back(PyRound(Fatigue[S], 4));
	}
	FEvent& End = Record(EEventType::GameEnded);
	End.Possession = PossessionNumber;
	End.Overtime = Overtime;
	OutResult.HomeScore = Score[0];
	OutResult.AwayScore = Score[1];
	OutResult.Overtime = Overtime;
	OutResult.Possessions = PossessionNumber;
	return true;
}

std::string CanonicalEventLine(const FGameResult& Result, const FEvent& Event)
{
	auto Name = [&Result](int Index) -> std::string { return Index < 0 ? "null" : Result.PlayerAt(Index).Name; };
	auto ScoreDict = [&]()
	{
		return SortedDict<int>({{Result.Home.Name, Event.HomeScore}, {Result.Away.Name, Event.AwayScore}}, FormatInt);
	};
	const FGameInputs& Inputs = Result.Inputs;
	const int Count = Result.RosterSize();
	std::string Line = EventTypeName(Event.Type);
	auto Add = [&Line](const std::string& Key, const std::string& Value) { Line += "|" + Key + "=" + Value; };
	switch (Event.Type)
	{
	case EEventType::GameStarted:
	{
		Add("brain_version", BrainVersion);
		Add("engine_version", EngineVersion);
		if (Inputs.bHasAvailability)
		{
			std::vector<std::pair<std::string, int>> Items;
			for (int I = 0; I < Count; ++I)
			{
				Items.push_back({Name(I), Inputs.Availability[static_cast<size_t>(I)]});
			}
			Add("pregame_availability", SortedDict<int>(Items, FormatInt));
		}
		if (Inputs.bHasFatigue)
		{
			std::vector<std::pair<std::string, double>> Items;
			for (int I = 0; I < Count; ++I)
			{
				Items.push_back({Name(I), PyRound(Inputs.Fatigue[static_cast<size_t>(I)], 4)});
			}
			Add("pregame_fatigue", SortedDict<double>(Items, FormatDouble));
		}
		if (Inputs.bHasInvolvement)
		{
			std::vector<std::pair<std::string, double>> Items;
			for (int I = 0; I < Count; ++I)
			{
				Items.push_back({Name(I), Inputs.Involvement[static_cast<size_t>(I)]});
			}
			Add("pregame_offensive_involvement", SortedDict<double>(Items, FormatDouble));
		}
		if (Inputs.bHasReadiness)
		{
			std::vector<std::pair<std::string, double>> Items;
			for (int I = 0; I < Count; ++I)
			{
				Items.push_back({Name(I), PyRound(Inputs.Readiness[static_cast<size_t>(I)], 4)});
			}
			Add("pregame_readiness", SortedDict<double>(Items, FormatDouble));
		}
		if (Inputs.bHasConsistency)
		{
			std::vector<std::pair<std::string, std::string>> Items;
			for (int I = 0; I < Count; ++I)
			{
				Items.push_back({Name(I), "{cap:" + Fixed6(Inputs.ConsistencyCap[static_cast<size_t>(I)]) + ";strength:" + Fixed6(Inputs.ConsistencyStrength[static_cast<size_t>(I)]) + "}"});
			}
			Add("pregame_shooting_consistency", SortedDict<std::string>(Items, FormatString));
		}
		Add("seed", std::to_string(Result.Seed));
		break;
	}
	case EEventType::LineupChanged:
	{
		Add("clock_seconds", std::to_string(Event.ClockSeconds));
		std::string Players = "[";
		for (size_t I = 0; I < Event.Lineup.size(); ++I)
		{
			Players += (I ? "," : "") + Name(Event.Lineup[I]);
		}
		Add("players", Players + "]");
		Add("team", Result.TeamName(Event.Team));
		break;
	}
	case EEventType::PossessionStarted:
		Add("ballhandler", Name(Event.Player));
		Add("clock_seconds", std::to_string(Event.ClockSeconds));
		Add("offense", Result.TeamName(Event.Team));
		Add("possession", std::to_string(Event.Possession));
		break;
	case EEventType::BrainDecision:
		Add("action", "{actor:" + Name(Event.Player) + ";kind:" + ActionKindName(Event.ActionKind) + ";role:" + (Event.bDefenseDecision ? "defense" : "offense") + ";target:" + Name(Event.Other) + "}");
		Add("brain_version", BrainVersion);
		Add("clock_seconds", std::to_string(Event.ClockSeconds));
		Add("possession", std::to_string(Event.Possession));
		Add("score", ScoreDict());
		break;
	case EEventType::Turnover:
		Add("defense", Name(Event.Other));
		Add("player", Name(Event.Player));
		Add("possession", std::to_string(Event.Possession));
		break;
	case EEventType::PassCompleted:
		Add("passer", Name(Event.Player));
		Add("possession", std::to_string(Event.Possession));
		Add("receiver", Name(Event.Other));
		break;
	case EEventType::ShotMade:
	case EEventType::ShotMissed:
		Add("action", ActionKindName(Event.ActionKind));
		if (Inputs.bHasConsistency)
		{
			Add("base_probability", Fixed6(Event.BaseProbability));
			Add("consistency_correction", Fixed6(Event.ConsistencyCorrection));
		}
		Add("defense", Name(Event.Other));
		if (Inputs.bHasConsistency)
		{
			Add("performance_residual", Fixed6(Event.PerformanceResidual));
		}
		Add("player", Name(Event.Player));
		Add("points", std::to_string(Event.Points));
		Add("possession", std::to_string(Event.Possession));
		Add("probability", Fixed6(Event.Probability));
		break;
	case EEventType::OffensiveRebound:
	case EEventType::DefensiveRebound:
		Add("player", Name(Event.Player));
		Add("possession", std::to_string(Event.Possession));
		break;
	case EEventType::ShotClockViolation:
		Add("possession", std::to_string(Event.Possession));
		Add("team", Result.TeamName(Event.Team));
		break;
	case EEventType::OvertimeStarted:
		Add("overtime", std::to_string(Event.Overtime));
		break;
	case EEventType::GameEnded:
	{
		std::vector<std::pair<std::string, double>> Items;
		for (int I = 0; I < Count; ++I)
		{
			Items.push_back({Name(I), Result.MinutesPlayed[static_cast<size_t>(I)]});
		}
		Add("minutes_played", SortedDict<double>(Items, FormatDouble));
		Add("overtime", std::to_string(Event.Overtime));
		Add("possessions", std::to_string(Event.Possession));
		Add("score", ScoreDict());
		break;
	}
	}
	return Line;
}

// ---- League data ----------------------------------------------------------------------------

namespace
{
	FAthlete MakeAthlete(const char* Name, int Shooting, int Passing, int Defense, int Rebounding, int Stamina, EConsistencyTier Consistency, EInvolvementTier Involvement, EOffDayPreference OffDay)
	{
		FAthlete Athlete;
		Athlete.Ratings = FPlayer{Name, Shooting, Passing, Defense, Rebounding, Stamina};
		Athlete.Consistency = Consistency;
		Athlete.Involvement = Involvement;
		Athlete.OffDay = OffDay;
		return Athlete;
	}

	using CT = EConsistencyTier;
	using IT = EInvolvementTier;
	using OD = EOffDayPreference;

	FLeagueTeam HarborCityWaves()
	{
		return {"Harbor City Waves", "HCW", {
			MakeAthlete("Jalen Cross", 84, 78, 72, 58, 86, CT::Steady, IT::Featured, OD::Practice),
			MakeAthlete("Micah Vale", 76, 86, 75, 55, 88, CT::Normal, IT::Featured, OD::Social),
			MakeAthlete("Dorian Pike", 79, 71, 82, 70, 84, CT::Steady, IT::Standard, OD::Practice),
			MakeAthlete("Kellan Shore", 72, 69, 78, 84, 80, CT::Normal, IT::Low, OD::Social),
			MakeAthlete("Andre North", 68, 65, 80, 88, 78, CT::Normal, IT::Low, OD::Social),
			MakeAthlete("Malik Frost", 74, 72, 74, 63, 82, CT::Volatile, IT::Standard, OD::Practice),
		}};
	}

	FLeagueTeam MesaVistaSol()
	{
		return {"Mesa Vista Sol", "MVS", {
			MakeAthlete("Nico Reyes", 82, 80, 70, 56, 87, CT::Steady, IT::Featured, OD::Practice),
			MakeAthlete("Tariq Stone", 78, 75, 83, 68, 85, CT::Elite, IT::Standard, OD::Social),
			MakeAthlete("Eli Mercer", 75, 84, 74, 60, 89, CT::Normal, IT::Featured, OD::Practice),
			MakeAthlete("Roman Voss", 73, 67, 79, 86, 81, CT::Steady, IT::Low, OD::Social),
			MakeAthlete("Cal Brooks", 70, 64, 81, 89, 77, CT::Normal, IT::Low, OD::Practice),
			MakeAthlete("Mateo Cruz", 74, 73, 73, 65, 83, CT::Volatile, IT::Standard, OD::Social),
		}};
	}
}

FLeagueConfig PrototypeLeague()
{
	FLeagueConfig Config;
	Config.Teams = {HarborCityWaves(), MesaVistaSol()};
	return Config;
}

const FLeagueConfig& DefaultLeague()
{
	static const FLeagueConfig Config = []
	{
		FLeagueConfig League;
		League.Teams = {
			HarborCityWaves(),
			MesaVistaSol(),
			{"Sundale Signal", "SDL", {
				MakeAthlete("Theo Marsh", 86, 80, 74, 57, 88, CT::Elite, IT::Featured, OD::Practice),
				MakeAthlete("Ade Mensah", 74, 70, 84, 72, 85, CT::Steady, IT::Standard, OD::Practice),
				MakeAthlete("Rafael Duarte", 79, 82, 71, 58, 87, CT::Normal, IT::Featured, OD::Social),
				MakeAthlete("Bram Keller", 70, 66, 80, 85, 81, CT::Steady, IT::Low, OD::Practice),
				MakeAthlete("Jonah Wilde", 67, 63, 79, 90, 79, CT::Normal, IT::Low, OD::Social),
				MakeAthlete("Silas Moreau", 75, 74, 72, 64, 83, CT::Volatile, IT::Standard, OD::Social),
			}},
			{"Northgate Lanterns", "NGL", {
				MakeAthlete("Owen Sterling", 77, 79, 84, 62, 88, CT::Steady, IT::Featured, OD::Practice),
				MakeAthlete("Desmond Hale", 72, 68, 86, 74, 86, CT::Elite, IT::Standard, OD::Practice),
				MakeAthlete("Felix Arden", 80, 72, 76, 60, 84, CT::Normal, IT::Featured, OD::Social),
				MakeAthlete("Ivo Brandt", 69, 64, 83, 86, 82, CT::Steady, IT::Low, OD::Practice),
				MakeAthlete("Lucas Ferro", 66, 62, 81, 88, 80, CT::Normal, IT::Low, OD::Social),
				MakeAthlete("Ezra Quinn", 73, 71, 75, 66, 81, CT::Volatile, IT::Standard, OD::Social),
			}},
			{"Cobalt Bay Herons", "CBH", {
				MakeAthlete("Kai Navarro", 88, 76, 68, 55, 85, CT::Volatile, IT::Featured, OD::Social),
				MakeAthlete("Marcus Lind", 81, 78, 70, 57, 84, CT::Normal, IT::Featured, OD::Social),
				MakeAthlete("Tobias Grant", 79, 74, 72, 61, 83, CT::Volatile, IT::Standard, OD::Practice),
				MakeAthlete("Rhys Calder", 72, 66, 77, 82, 80, CT::Normal, IT::Low, OD::Practice),
				MakeAthlete("Ben Okoro", 70, 63, 78, 85, 78, CT::Normal, IT::Low, OD::Social),
				MakeAthlete("Leon Varga", 76, 75, 71, 62, 82, CT::Volatile, IT::Standard, OD::Social),
			}},
			{"Ridgeway Forge", "RWF", {
				MakeAthlete("Aaron Tull", 78, 74, 78, 66, 90, CT::Steady, IT::Featured, OD::Practice),
				MakeAthlete("Garrett Stroud", 74, 77, 75, 60, 89, CT::Normal, IT::Featured, OD::Practice),
				MakeAthlete("Hugo Lindqvist", 71, 67, 79, 87, 88, CT::Steady, IT::Low, OD::Practice),
				MakeAthlete("Nate Okonjo", 68, 64, 80, 91, 86, CT::Normal, IT::Low, OD::Social),
				MakeAthlete("Simon Hart", 73, 70, 77, 70, 87, CT::Normal, IT::Standard, OD::Social),
				MakeAthlete("Viktor Sand", 75, 72, 73, 65, 85, CT::Volatile, IT::Standard, OD::Social),
			}},
			{"Pinecrest Summit", "PCS", {
				MakeAthlete("Elias Ward", 80, 88, 73, 56, 86, CT::Steady, IT::Featured, OD::Practice),
				MakeAthlete("Jasper Cole", 77, 84, 72, 58, 87, CT::Normal, IT::Featured, OD::Social),
				MakeAthlete("Mateus Lima", 75, 80, 76, 63, 84, CT::Normal, IT::Standard, OD::Practice),
				MakeAthlete("Quentin Rhodes", 71, 69, 79, 83, 82, CT::Steady, IT::Low, OD::Practice),
				MakeAthlete("Dario Vance", 68, 65, 80, 87, 80, CT::Normal, IT::Low, OD::Social),
				MakeAthlete("Callum Price", 74, 76, 71, 61, 83, CT::Volatile, IT::Standard, OD::Social),
			}},
			{"Dune Harbor Comets", "DHC", {
				MakeAthlete("Idris Kane", 92, 81, 75, 60, 88, CT::Elite, IT::Featured, OD::Practice),
				MakeAthlete("Ryan Beck", 72, 70, 73, 59, 83, CT::Normal, IT::Standard, OD::Social),
				MakeAthlete("Tomas Ruiz", 70, 74, 72, 57, 84, CT::Volatile, IT::Standard, OD::Social),
				MakeAthlete("Cole Ashby", 68, 63, 76, 84, 80, CT::Normal, IT::Low, OD::Practice),
				MakeAthlete("Wes Holt", 66, 61, 78, 86, 79, CT::Normal, IT::Low, OD::Social),
				MakeAthlete("Arlo Finch", 71, 72, 70, 62, 82, CT::Volatile, IT::Standard, OD::Practice),
			}},
		};
		return League;
	}();
	return Config;
}

int AthleteIndex(const FLeagueConfig& Config, int Team, int RosterSlot)
{
	int Index = 0;
	for (int T = 0; T < Team; ++T)
	{
		Index += static_cast<int>(Config.Teams[static_cast<size_t>(T)].Roster.size());
	}
	return Index + RosterSlot;
}

int RegularSeasonDays(const FLeagueConfig& Config)
{
	return Config.RoundRobinCycles * (static_cast<int>(Config.Teams.size()) - 1);
}

FTeam TeamForGame(const FLeagueConfig& Config, int Team)
{
	FTeam Result;
	const FLeagueTeam& Source = Config.Teams[static_cast<size_t>(Team)];
	Result.Name = Source.Name;
	for (const FAthlete& Athlete : Source.Roster)
	{
		Result.Players.push_back(Athlete.Ratings);
	}
	return Result;
}

const char* LifeChoiceName(ELifeChoice Choice)
{
	switch (Choice)
	{
	case ELifeChoice::Train: return "train";
	case ELifeChoice::Rest: return "rest";
	case ELifeChoice::Recover: return "recover";
	default: return "socialize";
	}
}

const char* StageName(EGameStage Stage)
{
	switch (Stage)
	{
	case EGameStage::Semifinal: return "Semifinal";
	case EGameStage::Final: return "Final";
	default: return "Regular season";
	}
}

// ---- League steps ---------------------------------------------------------------------------

void RecoverDays(FLeagueState& State, int Days, int FirstAthlete, int AthleteCount)
{
	for (int Index = FirstAthlete; Index < FirstAthlete + AthleteCount; ++Index)
	{
		FAthleteState& Athlete = State.Athletes[static_cast<size_t>(Index)];
		Athlete.Fatigue = PyRound(std::max(0.0, Athlete.Fatigue - RecoveryPerDay * Days), 4);
		Athlete.RecoveryDays = std::max(0, Athlete.RecoveryDays - Days);
	}
}

namespace
{
	enum class EScoringForm : uint8_t { Below, Typical, Above };

	EScoringForm RecentScoringForm(const std::vector<std::pair<int, double>>& History)
	{
		if (History.empty() || History.back().second <= 0)
		{
			return EScoringForm::Typical;
		}
		int Sum = 0;
		int Count = 0;
		for (size_t Index = 0; Index + 1 < History.size(); ++Index)
		{
			if (History[Index].second > 0)
			{
				Sum += History[Index].first;
				++Count;
			}
		}
		if (Count < 3)
		{
			return EScoringForm::Typical;
		}
		const double Difference = History.back().first - static_cast<double>(Sum) / static_cast<double>(Count);
		return Difference > 2 ? EScoringForm::Above : Difference < -2 ? EScoringForm::Below : EScoringForm::Typical;
	}

	int NextRoutineStreak(int Streak, ELifeChoice Choice)
	{
		if (Choice == ELifeChoice::Train)
		{
			return Streak > 0 ? std::min(2, Streak + 1) : 1;
		}
		if (Choice == ELifeChoice::Socialize)
		{
			return Streak < 0 ? std::max(-2, Streak - 1) : -1;
		}
		return 0;
	}
}

void ApplyLifeDay(const FLeagueConfig& Config, FLeagueState& State, int Day, bool bUseScoringForm)
{
	(void)Day;
	int Index = 0;
	for (const FLeagueTeam& Team : Config.Teams)
	{
		for (const FAthlete& Profile : Team.Roster)
		{
			FAthleteState& Athlete = State.Athletes[static_cast<size_t>(Index++)];
			const EScoringForm Form = bUseScoringForm ? RecentScoringForm(Athlete.ScoringHistory) : EScoringForm::Typical;
			ELifeChoice Choice;
			if (Athlete.RecoveryDays > 0)
			{
				Choice = ELifeChoice::Recover;
			}
			else if (Athlete.Fatigue >= HighFatigue)
			{
				Choice = ELifeChoice::Rest;
			}
			else if (Athlete.RoutineStreak == 2)
			{
				Choice = ELifeChoice::Socialize;
			}
			else if (Athlete.RoutineStreak == -2)
			{
				Choice = ELifeChoice::Train;
			}
			else if (Form != EScoringForm::Typical)
			{
				Choice = Form == EScoringForm::Below ? ELifeChoice::Train : ELifeChoice::Socialize;
			}
			else
			{
				Choice = Profile.OffDay == EOffDayPreference::Practice ? ELifeChoice::Train : ELifeChoice::Socialize;
			}
			double FatigueAfter = Athlete.Fatigue;
			int RecoveryAfter = Athlete.RecoveryDays;
			double Readiness = 0.0;
			switch (Choice)
			{
			case ELifeChoice::Recover:
				RecoveryAfter -= 1;
				break;
			case ELifeChoice::Rest:
				FatigueAfter = std::max(0.0, Athlete.Fatigue - 0.03);
				break;
			case ELifeChoice::Train:
				FatigueAfter = std::min(0.35, Athlete.Fatigue + 0.02);
				Readiness = 0.015;
				break;
			case ELifeChoice::Socialize:
				FatigueAfter = std::min(0.35, Athlete.Fatigue + 0.01);
				Readiness = 0.01;
				break;
			}
			Athlete.Fatigue = PyRound(PyRound(FatigueAfter, 4), 4);
			Athlete.RecoveryDays = RecoveryAfter;
			Athlete.Readiness = PyRound(PyRound(Clamp(Readiness, -MaxReadiness, MaxReadiness), 4), 4);
			Athlete.RoutineStreak = NextRoutineStreak(Athlete.RoutineStreak, Choice);
			Athlete.LastChoice = Choice;
			Athlete.bHasLastChoice = true;
		}
	}
}

void BuildGameInputs(const FLeagueConfig& Config, const FLeagueState& State, int Home, int Away, FGameInputs& OutInputs)
{
	OutInputs = FGameInputs();
	OutInputs.bHasFatigue = OutInputs.bHasAvailability = OutInputs.bHasReadiness = true;
	OutInputs.bHasConsistency = OutInputs.bHasInvolvement = true;
	for (const int Team : {Home, Away})
	{
		const FLeagueTeam& Source = Config.Teams[static_cast<size_t>(Team)];
		for (int Slot = 0; Slot < static_cast<int>(Source.Roster.size()); ++Slot)
		{
			const FAthlete& Profile = Source.Roster[static_cast<size_t>(Slot)];
			const FAthleteState& Athlete = State.Athletes[static_cast<size_t>(AthleteIndex(Config, Team, Slot))];
			OutInputs.Fatigue.push_back(Athlete.Fatigue);
			OutInputs.Availability.push_back(Athlete.RecoveryDays);
			OutInputs.Readiness.push_back(Athlete.Readiness);
			OutInputs.ConsistencyStrength.push_back(ConsistencyStrength(Profile.Consistency));
			OutInputs.ConsistencyCap.push_back(ConsistencyCap(Profile.Consistency));
			OutInputs.Involvement.push_back(InvolvementWeight(Profile.Involvement));
		}
	}
}

void ApplyGameAftermath(const FLeagueConfig& Config, FLeagueState& State, const FScheduledGame& Game, const FGameResult& Result)
{
	// Fatigue load and minor injuries both read the pregame state; injuries visit teams in league order.
	const int HomeCount = static_cast<int>(Config.Teams[static_cast<size_t>(Game.Home)].Roster.size());
	FPyRandom InjuryRng(Game.Seed ^ InjurySeedSalt);
	for (const int Team : {std::min(Game.Home, Game.Away), std::max(Game.Home, Game.Away)})
	{
		const FLeagueTeam& Source = Config.Teams[static_cast<size_t>(Team)];
		const int Offset = Team == Game.Home ? 0 : HomeCount;
		int AvailableCount = 0;
		for (int Slot = 0; Slot < static_cast<int>(Source.Roster.size()); ++Slot)
		{
			AvailableCount += State.Athletes[static_cast<size_t>(AthleteIndex(Config, Team, Slot))].RecoveryDays == 0 ? 1 : 0;
		}
		for (int Slot = 0; Slot < static_cast<int>(Source.Roster.size()); ++Slot)
		{
			if (AvailableCount <= 5)
			{
				break;
			}
			FAthleteState& Athlete = State.Athletes[static_cast<size_t>(AthleteIndex(Config, Team, Slot))];
			const double Minutes = Result.MinutesPlayed[static_cast<size_t>(Offset + Slot)];
			if (Athlete.RecoveryDays || Minutes <= 0)
			{
				continue;
			}
			const double Risk = Minutes <= 0 ? 0.0 : std::min(MaxInjuryRisk, std::max(0.0,
				0.002 + 0.006 * Minutes / 48 + 0.04 * Athlete.Fatigue + 0.012 * std::max(0.0, Minutes - 36) / 12));
			if (InjuryRng.Random() < Risk)
			{
				Athlete.RecoveryDays = InjuryRecoveryDays[InjuryRng.Choice(InjuryRecoveryWeights, 4)];
				--AvailableCount;
			}
		}
	}
	for (const int Team : {Game.Home, Game.Away})
	{
		const FLeagueTeam& Source = Config.Teams[static_cast<size_t>(Team)];
		const int Offset = Team == Game.Home ? 0 : HomeCount;
		for (int Slot = 0; Slot < static_cast<int>(Source.Roster.size()); ++Slot)
		{
			FAthleteState& Athlete = State.Athletes[static_cast<size_t>(AthleteIndex(Config, Team, Slot))];
			const double Minutes = Result.MinutesPlayed[static_cast<size_t>(Offset + Slot)];
			const double Load = (0.05 + static_cast<double>(100 - Source.Roster[static_cast<size_t>(Slot)].Ratings.Stamina) / 1000.0) * (Minutes / 48.0);
			Athlete.Fatigue = PyRound(std::min(MaxCarryoverFatigue, Athlete.Fatigue + Load), 4);
			const int Points = Result.PointsFor(Offset + Slot);
			Athlete.ScoringHistory.push_back({Points, Minutes});
			if (Minutes > 0)
			{
				++Athlete.SeasonGames;
			}
			Athlete.SeasonPoints += Points;
			Athlete.SeasonMinutes += Minutes;
		}
	}
}

// ---- Odds -----------------------------------------------------------------------------------

namespace
{
	double TeamStrength(const FTeam& Team, const std::vector<int>& Availability)
	{
		std::vector<double> Minutes(Team.Players.size(), 0.0);
		std::vector<size_t> Available;
		for (size_t Index = 0; Index < Team.Players.size(); ++Index)
		{
			if (Availability[Index] == 0)
			{
				Available.push_back(Index);
			}
		}
		if (Available.size() == 5)
		{
			for (size_t Index : Available)
			{
				Minutes[Index] = 48.0;
			}
		}
		else
		{
			for (size_t Index = 0; Index < 5; ++Index)
			{
				Minutes[Available[Index]] = 43.2;
			}
			Minutes[Available[5]] = 24.0;
		}
		double Strength = 0.0;
		for (size_t Index = 0; Index < Team.Players.size(); ++Index)
		{
			const FPlayer& Player = Team.Players[Index];
			const double Sum = 0.0 + Player.Shooting + Player.Passing + Player.Defense + Player.Rebounding + Player.Stamina;
			Strength = Index == 0 ? Sum / 5 * Minutes[Index] / 240 : Strength + Sum / 5 * Minutes[Index] / 240;
		}
		return Strength;
	}

	double EloProbability(double Difference)
	{
		return 1 / (1 + std::pow(10.0, -Difference / 400));
	}
}

std::pair<double, double> PredictHomeWin(const FTeam& Home, const FTeam& Away, const std::vector<int>& HomeAvailability, const std::vector<int>& AwayAvailability, double HomeElo, double AwayElo)
{
	const double BaseDifference = HomeElo - AwayElo + HomeAdvantageElo;
	const double HomeStrength = TeamStrength(Home, HomeAvailability);
	const double AwayStrength = TeamStrength(Away, AwayAvailability);
	return {
		PyRound(EloProbability(BaseDifference), 8),
		PyRound(EloProbability(BaseDifference + RatingDifferenceElo * (HomeStrength - AwayStrength)), 8),
	};
}

int64_t ProbabilityToE8(double RoundedProbability)
{
	const std::string Text = FormatFixed(RoundedProbability, 8);
	int64_t Value = 0;
	for (const char Character : Text)
	{
		if (Character >= '0' && Character <= '9')
		{
			Value = Value * 10 + (Character - '0');
		}
	}
	return std::max<int64_t>(1, std::min<int64_t>(ProbabilityScale - 1, Value));
}

int64_t DecimalOddsE4(int64_t WinProbabilityE8)
{
	return ProbabilityScale * 10000 / WinProbabilityE8;
}

bool IsValidStake(int64_t Stake)
{
	return Stake >= MinimumStake && Stake <= MaximumStake && Stake % StakeIncrement == 0;
}

int64_t GrossReturn(int64_t Stake, int64_t WinProbabilityE8)
{
	return Stake * ProbabilityScale / WinProbabilityE8;
}

// ---- Season flow ----------------------------------------------------------------------------

namespace
{
	uint64_t SeasonSeedBase(uint64_t CareerSeed, int Season)
	{
		return (CareerSeed % 1000000007ull) * 4099ull + static_cast<uint64_t>(Season) * 100003ull;
	}

	void BuildRegularSeason(const FLeagueConfig& Config, FLeagueState& State)
	{
		const int TeamCount = static_cast<int>(Config.Teams.size());
		const int RoundsPerCycle = TeamCount - 1;
		std::vector<std::vector<std::pair<int, int>>> Rounds;
		for (int Cycle = 0; Cycle < Config.RoundRobinCycles; ++Cycle)
		{
			std::vector<int> Order(static_cast<size_t>(TeamCount));
			for (int Team = 0; Team < TeamCount; ++Team)
			{
				Order[static_cast<size_t>(Team)] = Team;
			}
			for (int Round = 0; Round < RoundsPerCycle; ++Round)
			{
				std::vector<std::pair<int, int>> Pairs;
				for (int Slot = 0; Slot < TeamCount / 2; ++Slot)
				{
					int Home = Order[static_cast<size_t>(Slot)];
					int Away = Order[static_cast<size_t>(TeamCount - 1 - Slot)];
					if ((Slot == 0 && Round % 2 == 1) != (Cycle % 2 == 1))
					{
						std::swap(Home, Away);
					}
					Pairs.push_back({Home, Away});
				}
				Rounds.push_back(Pairs);
				// Circle method: keep the first team fixed and rotate the rest.
				std::rotate(Order.begin() + 1, Order.end() - 1, Order.end());
			}
		}
		FPyRandom Shuffle(SeasonSeedBase(State.CareerSeed, State.SeasonNumber) ^ 0x5C4EDull);
		for (int Index = static_cast<int>(Rounds.size()) - 1; Index > 0; --Index)
		{
			const int Swap = static_cast<int>(Shuffle.Random() * (Index + 1));
			std::swap(Rounds[static_cast<size_t>(Index)], Rounds[static_cast<size_t>(Swap)]);
		}
		State.Games.clear();
		const uint64_t Base = SeasonSeedBase(State.CareerSeed, State.SeasonNumber);
		for (size_t Round = 0; Round < Rounds.size(); ++Round)
		{
			for (const auto& Pair : Rounds[Round])
			{
				FScheduledGame Game;
				Game.Id = static_cast<int>(State.Games.size()) + 1;
				Game.Day = static_cast<int>(Round) + 1;
				Game.Home = Pair.first;
				Game.Away = Pair.second;
				Game.Seed = Base + static_cast<uint64_t>(Game.Id);
				State.Games.push_back(Game);
			}
		}
	}

	void AddPlayoffGame(FLeagueState& State, int Day, EGameStage Stage, int Series, const FSeriesState& Pairing)
	{
		FScheduledGame Game;
		Game.Id = static_cast<int>(State.Games.size()) + 1;
		Game.Day = Day;
		Game.Stage = Stage;
		Game.Series = Series;
		Game.SeriesGame = Pairing.HighWins + Pairing.LowWins + 1;
		// Higher seed hosts games 1 and 3.
		const bool bHighHome = Game.SeriesGame != 2;
		Game.Home = bHighHome ? Pairing.HighSeed : Pairing.LowSeed;
		Game.Away = bHighHome ? Pairing.LowSeed : Pairing.HighSeed;
		Game.Seed = SeasonSeedBase(State.CareerSeed, State.SeasonNumber) + 50000ull + static_cast<uint64_t>(Game.Id);
		State.Games.push_back(Game);
	}

	void StartSeason(const FLeagueConfig& Config, FLeagueState& State, bool bOffseasonRecovery)
	{
		State.Day = 1;
		State.bDayPrepared = false;
		State.bDayPlayed = false;
		State.Phase = ESeasonPhase::Regular;
		State.Standings.assign(Config.Teams.size(), FStanding());
		State.Semifinals[0] = State.Semifinals[1] = State.FinalSeries = FSeriesState();
		State.Champion = -1;
		if (bOffseasonRecovery)
		{
			RecoverDays(State, OffseasonRestDays, 0, static_cast<int>(State.Athletes.size()));
		}
		for (FAthleteState& Athlete : State.Athletes)
		{
			Athlete.Readiness = 0.0;
			Athlete.RoutineStreak = 0;
			Athlete.ScoringHistory.clear();
			Athlete.SeasonGames = 0;
			Athlete.SeasonPoints = 0;
			Athlete.SeasonMinutes = 0.0;
		}
		BuildRegularSeason(Config, State);
	}

	std::vector<int> TeamAvailability(const FLeagueConfig& Config, const FLeagueState& State, int Team)
	{
		std::vector<int> Values;
		for (int Slot = 0; Slot < static_cast<int>(Config.Teams[static_cast<size_t>(Team)].Roster.size()); ++Slot)
		{
			Values.push_back(State.Athletes[static_cast<size_t>(AthleteIndex(Config, Team, Slot))].RecoveryDays);
		}
		return Values;
	}
}

void NewLeague(const FLeagueConfig& Config, uint64_t CareerSeed, FLeagueState& OutState)
{
	OutState = FLeagueState();
	OutState.CareerSeed = CareerSeed;
	OutState.SeasonNumber = 1;
	OutState.Athletes.assign(static_cast<size_t>(AthleteIndex(Config, static_cast<int>(Config.Teams.size()), 0)), FAthleteState());
	OutState.Elo.assign(Config.Teams.size(), 1500.0);
	StartSeason(Config, OutState, false);
}

std::vector<int> GamesOnDay(const FLeagueState& State, int Day)
{
	std::vector<int> Ids;
	for (const FScheduledGame& Game : State.Games)
	{
		if (Game.Day == Day)
		{
			Ids.push_back(Game.Id);
		}
	}
	return Ids;
}

std::vector<int> RankedTeams(const FLeagueConfig& Config, const FLeagueState& State)
{
	std::vector<int> Teams(Config.Teams.size());
	for (size_t Team = 0; Team < Teams.size(); ++Team)
	{
		Teams[Team] = static_cast<int>(Team);
	}
	std::sort(Teams.begin(), Teams.end(), [&](int A, int B)
	{
		const FStanding& SA = State.Standings[static_cast<size_t>(A)];
		const FStanding& SB = State.Standings[static_cast<size_t>(B)];
		if (SA.Wins != SB.Wins) return SA.Wins > SB.Wins;
		const int DiffA = SA.PointsFor - SA.PointsAgainst;
		const int DiffB = SB.PointsFor - SB.PointsAgainst;
		if (DiffA != DiffB) return DiffA > DiffB;
		if (SA.PointsFor != SB.PointsFor) return SA.PointsFor > SB.PointsFor;
		return Config.Teams[static_cast<size_t>(A)].Name < Config.Teams[static_cast<size_t>(B)].Name;
	});
	return Teams;
}

void PrepareDay(const FLeagueConfig& Config, FLeagueState& State)
{
	if (State.bDayPrepared)
	{
		return;
	}
	if (State.Day > 1)
	{
		RecoverDays(State, 1, 0, static_cast<int>(State.Athletes.size()));
		ApplyLifeDay(Config, State, State.Day, true);
	}
	for (FScheduledGame& Game : State.Games)
	{
		if (Game.Day != State.Day || Game.bPlayed)
		{
			continue;
		}
		const std::pair<double, double> Probabilities = PredictHomeWin(
			TeamForGame(Config, Game.Home), TeamForGame(Config, Game.Away),
			TeamAvailability(Config, State, Game.Home), TeamAvailability(Config, State, Game.Away),
			State.Elo[static_cast<size_t>(Game.Home)], State.Elo[static_cast<size_t>(Game.Away)]);
		Game.PublicEloProbability = Probabilities.first;
		Game.HomeWinProbabilityE8 = ProbabilityToE8(Probabilities.second);
		Game.bOddsPublished = true;
	}
	State.bDayPrepared = true;
}

bool PlayDay(const FLeagueConfig& Config, FLeagueState& State, std::vector<FGameResult>* OutResults, std::string& OutError)
{
	PrepareDay(Config, State);
	if (State.bDayPlayed)
	{
		return true;
	}
	for (FScheduledGame& Game : State.Games)
	{
		if (Game.Day != State.Day || Game.bPlayed)
		{
			continue;
		}
		FGameInputs Inputs;
		BuildGameInputs(Config, State, Game.Home, Game.Away, Inputs);
		Game.PregameFatigue = Inputs.Fatigue;
		Game.PregameAvailability = Inputs.Availability;
		Game.PregameReadiness = Inputs.Readiness;
		FGameResult Result;
		if (!SimulateGame(Game.Seed, TeamForGame(Config, Game.Home), TeamForGame(Config, Game.Away), Inputs, Result, OutError))
		{
			return false;
		}
		ApplyGameAftermath(Config, State, Game, Result);
		Game.bPlayed = true;
		Game.HomeScore = Result.HomeScore;
		Game.AwayScore = Result.AwayScore;
		Game.Overtime = Result.Overtime;
		const bool bHomeWin = Result.HomeScore > Result.AwayScore;
		const int Winner = bHomeWin ? Game.Home : Game.Away;
		const int Loser = bHomeWin ? Game.Away : Game.Home;
		if (Game.Stage == EGameStage::Regular)
		{
			FStanding& HomeRow = State.Standings[static_cast<size_t>(Game.Home)];
			FStanding& AwayRow = State.Standings[static_cast<size_t>(Game.Away)];
			State.Standings[static_cast<size_t>(Winner)].Wins += 1;
			State.Standings[static_cast<size_t>(Loser)].Losses += 1;
			HomeRow.PointsFor += Result.HomeScore;
			HomeRow.PointsAgainst += Result.AwayScore;
			AwayRow.PointsFor += Result.AwayScore;
			AwayRow.PointsAgainst += Result.HomeScore;
		}
		else
		{
			FSeriesState& Series = Game.Stage == EGameStage::Final ? State.FinalSeries : State.Semifinals[Game.Series];
			(Winner == Series.HighSeed ? Series.HighWins : Series.LowWins) += 1;
		}
		const double Change = EloK * ((bHomeWin ? 1 : 0) - Game.PublicEloProbability);
		State.Elo[static_cast<size_t>(Game.Home)] += Change;
		State.Elo[static_cast<size_t>(Game.Away)] -= Change;
		if (OutResults)
		{
			OutResults->push_back(Result);
		}
	}
	if (State.Phase == ESeasonPhase::Final && State.FinalSeries.Winner() >= 0)
	{
		State.Champion = State.FinalSeries.Winner();
	}
	State.bDayPlayed = true;
	return true;
}

void AdvanceDay(const FLeagueConfig& Config, FLeagueState& State)
{
	if (!State.bDayPlayed)
	{
		return;
	}
	const int NextDay = State.Day + 1;
	if (State.Phase == ESeasonPhase::Regular && State.Day >= RegularSeasonDays(Config))
	{
		const std::vector<int> Ranked = RankedTeams(Config, State);
		State.Semifinals[0] = FSeriesState{Ranked[0], Ranked[3], 0, 0};
		State.Semifinals[1] = FSeriesState{Ranked[1], Ranked[2], 0, 0};
		State.Phase = ESeasonPhase::Semifinals;
		AddPlayoffGame(State, NextDay, EGameStage::Semifinal, 0, State.Semifinals[0]);
		AddPlayoffGame(State, NextDay, EGameStage::Semifinal, 1, State.Semifinals[1]);
	}
	else if (State.Phase == ESeasonPhase::Semifinals)
	{
		const int WinnerA = State.Semifinals[0].Winner();
		const int WinnerB = State.Semifinals[1].Winner();
		if (WinnerA >= 0 && WinnerB >= 0)
		{
			const std::vector<int> Ranked = RankedTeams(Config, State);
			const auto Rank = [&Ranked](int Team) { return std::find(Ranked.begin(), Ranked.end(), Team) - Ranked.begin(); };
			State.FinalSeries = Rank(WinnerA) < Rank(WinnerB) ? FSeriesState{WinnerA, WinnerB, 0, 0} : FSeriesState{WinnerB, WinnerA, 0, 0};
			State.Phase = ESeasonPhase::Final;
			AddPlayoffGame(State, NextDay, EGameStage::Final, 0, State.FinalSeries);
		}
		else
		{
			for (int Series = 0; Series < 2; ++Series)
			{
				if (State.Semifinals[Series].Winner() < 0)
				{
					AddPlayoffGame(State, NextDay, EGameStage::Semifinal, Series, State.Semifinals[Series]);
				}
			}
		}
	}
	else if (State.Phase == ESeasonPhase::Final)
	{
		if (State.FinalSeries.Winner() >= 0)
		{
			State.Champion = State.FinalSeries.Winner();
			State.LastChampion = State.Champion;
			State.CompletedSeasons += 1;
			State.SeasonNumber += 1;
			StartSeason(Config, State, true);
			return;
		}
		AddPlayoffGame(State, NextDay, EGameStage::Final, 0, State.FinalSeries);
	}
	State.Day = NextDay;
	State.bDayPrepared = false;
	State.bDayPlayed = false;
}

bool ReplayGame(const FLeagueConfig& Config, const FLeagueState& State, int GameId, FGameResult& OutResult, std::string& OutError)
{
	for (const FScheduledGame& Game : State.Games)
	{
		if (Game.Id != GameId)
		{
			continue;
		}
		if (!Game.bPlayed)
		{
			OutError = "game has not been played";
			return false;
		}
		FGameInputs Inputs;
		BuildGameInputs(Config, State, Game.Home, Game.Away, Inputs);
		Inputs.Fatigue = Game.PregameFatigue;
		Inputs.Availability = Game.PregameAvailability;
		Inputs.Readiness = Game.PregameReadiness;
		if (!SimulateGame(Game.Seed, TeamForGame(Config, Game.Home), TeamForGame(Config, Game.Away), Inputs, OutResult, OutError))
		{
			return false;
		}
		if (OutResult.HomeScore != Game.HomeScore || OutResult.AwayScore != Game.AwayScore)
		{
			OutError = "replay does not match the recorded result";
			return false;
		}
		return true;
	}
	OutError = "unknown game";
	return false;
}

// ---- Persistence ----------------------------------------------------------------------------

namespace
{
	const char* LeagueSchema = "oddswell-league-state-v1";

	std::string Exact(double Value)
	{
		char Buffer[64];
		std::snprintf(Buffer, sizeof(Buffer), "%.17g", Value);
		return Buffer;
	}

	std::vector<std::string> Split(const std::string& Text, char Separator)
	{
		std::vector<std::string> Parts;
		std::string Current;
		for (const char Character : Text)
		{
			if (Character == Separator)
			{
				Parts.push_back(Current);
				Current.clear();
			}
			else
			{
				Current += Character;
			}
		}
		Parts.push_back(Current);
		return Parts;
	}

	template <typename T>
	std::string JoinValues(const std::vector<T>& Values, std::string (*Format)(T))
	{
		std::string Text;
		for (size_t Index = 0; Index < Values.size(); ++Index)
		{
			Text += (Index ? "/" : "") + Format(Values[Index]);
		}
		return Text;
	}

	std::string FormatIntValue(int Value) { return std::to_string(Value); }
	std::string FormatDoubleValue(double Value) { return Exact(Value); }

	bool ParseInt64(const std::string& Text, int64_t& Out)
	{
		if (Text.empty())
		{
			return false;
		}
		char* End = nullptr;
		Out = std::strtoll(Text.c_str(), &End, 10);
		return End && *End == '\0';
	}

	bool ParseUInt64(const std::string& Text, uint64_t& Out)
	{
		if (Text.empty())
		{
			return false;
		}
		char* End = nullptr;
		Out = std::strtoull(Text.c_str(), &End, 10);
		return End && *End == '\0';
	}

	bool ParseInt(const std::string& Text, int& Out)
	{
		int64_t Value = 0;
		if (!ParseInt64(Text, Value))
		{
			return false;
		}
		Out = static_cast<int>(Value);
		return true;
	}

	bool ParseDouble(const std::string& Text, double& Out)
	{
		if (Text.empty())
		{
			return false;
		}
		char* End = nullptr;
		Out = std::strtod(Text.c_str(), &End);
		return End && *End == '\0';
	}

	template <typename T>
	bool ParseList(const std::string& Text, std::vector<T>& Out, bool (*Parse)(const std::string&, T&))
	{
		Out.clear();
		if (Text.empty())
		{
			return true;
		}
		for (const std::string& Part : Split(Text, '/'))
		{
			T Value{};
			if (!Parse(Part, Value))
			{
				return false;
			}
			Out.push_back(Value);
		}
		return true;
	}
}

std::string SerializeLeague(const FLeagueState& State)
{
	std::ostringstream Out;
	Out << LeagueSchema << "\n";
	Out << "career_seed=" << State.CareerSeed << "\n";
	Out << "season=" << State.SeasonNumber << "\n";
	Out << "day=" << State.Day << "\n";
	Out << "prepared=" << (State.bDayPrepared ? 1 : 0) << "\n";
	Out << "played=" << (State.bDayPlayed ? 1 : 0) << "\n";
	Out << "phase=" << static_cast<int>(State.Phase) << "\n";
	Out << "champion=" << State.Champion << "\n";
	Out << "completed=" << State.CompletedSeasons << "\n";
	Out << "last_champion=" << State.LastChampion << "\n";
	Out << "elo=" << JoinValues<double>(State.Elo, FormatDoubleValue) << "\n";
	for (const FStanding& Row : State.Standings)
	{
		Out << "standing=" << Row.Wins << "," << Row.Losses << "," << Row.PointsFor << "," << Row.PointsAgainst << "\n";
	}
	for (const FSeriesState* Series : {&State.Semifinals[0], &State.Semifinals[1], &State.FinalSeries})
	{
		Out << "series=" << Series->HighSeed << "," << Series->LowSeed << "," << Series->HighWins << "," << Series->LowWins << "\n";
	}
	for (const FAthleteState& Athlete : State.Athletes)
	{
		std::vector<int> Points;
		std::vector<double> Minutes;
		for (const auto& Entry : Athlete.ScoringHistory)
		{
			Points.push_back(Entry.first);
			Minutes.push_back(Entry.second);
		}
		Out << "athlete=" << Exact(Athlete.Fatigue) << "," << Athlete.RecoveryDays << "," << Exact(Athlete.Readiness) << ","
			<< Athlete.RoutineStreak << "," << static_cast<int>(Athlete.LastChoice) << "," << (Athlete.bHasLastChoice ? 1 : 0) << ","
			<< Athlete.SeasonGames << "," << Athlete.SeasonPoints << "," << Exact(Athlete.SeasonMinutes) << ","
			<< JoinValues<int>(Points, FormatIntValue) << "," << JoinValues<double>(Minutes, FormatDoubleValue) << "\n";
	}
	for (const FScheduledGame& Game : State.Games)
	{
		Out << "game=" << Game.Id << "," << Game.Day << "," << Game.Home << "," << Game.Away << "," << Game.Seed << ","
			<< static_cast<int>(Game.Stage) << "," << Game.Series << "," << Game.SeriesGame << "," << (Game.bPlayed ? 1 : 0) << ","
			<< Game.HomeScore << "," << Game.AwayScore << "," << Game.Overtime << "," << (Game.bOddsPublished ? 1 : 0) << ","
			<< Game.HomeWinProbabilityE8 << "," << Exact(Game.PublicEloProbability) << ","
			<< JoinValues<double>(Game.PregameFatigue, FormatDoubleValue) << "," << JoinValues<int>(Game.PregameAvailability, FormatIntValue) << ","
			<< JoinValues<double>(Game.PregameReadiness, FormatDoubleValue) << "\n";
	}
	return Out.str();
}

bool DeserializeLeague(const FLeagueConfig& Config, const std::string& Text, FLeagueState& OutState, std::string& OutError)
{
	FLeagueState State;
	std::vector<std::string> Lines = Split(Text, '\n');
	if (Lines.empty() || Lines[0] != LeagueSchema)
	{
		OutError = "unsupported league save";
		return false;
	}
	int SeriesIndex = 0;
	for (size_t LineIndex = 1; LineIndex < Lines.size(); ++LineIndex)
	{
		const std::string& Line = Lines[LineIndex];
		if (Line.empty())
		{
			continue;
		}
		const size_t Equals = Line.find('=');
		if (Equals == std::string::npos)
		{
			OutError = "malformed league save line";
			return false;
		}
		const std::string Key = Line.substr(0, Equals);
		const std::string Value = Line.substr(Equals + 1);
		const std::vector<std::string> Fields = Split(Value, ',');
		int Number = 0;
		bool bOk = true;
		if (Key == "career_seed") bOk = ParseUInt64(Value, State.CareerSeed);
		else if (Key == "season") bOk = ParseInt(Value, State.SeasonNumber);
		else if (Key == "day") bOk = ParseInt(Value, State.Day);
		else if (Key == "prepared") { bOk = ParseInt(Value, Number); State.bDayPrepared = Number != 0; }
		else if (Key == "played") { bOk = ParseInt(Value, Number); State.bDayPlayed = Number != 0; }
		else if (Key == "phase") { bOk = ParseInt(Value, Number) && Number >= 0 && Number <= 3; State.Phase = static_cast<ESeasonPhase>(Number); }
		else if (Key == "champion") bOk = ParseInt(Value, State.Champion);
		else if (Key == "completed") bOk = ParseInt(Value, State.CompletedSeasons);
		else if (Key == "last_champion") bOk = ParseInt(Value, State.LastChampion);
		else if (Key == "elo") bOk = ParseList<double>(Value, State.Elo, ParseDouble);
		else if (Key == "standing")
		{
			FStanding Row;
			bOk = Fields.size() == 4 && ParseInt(Fields[0], Row.Wins) && ParseInt(Fields[1], Row.Losses) && ParseInt(Fields[2], Row.PointsFor) && ParseInt(Fields[3], Row.PointsAgainst);
			State.Standings.push_back(Row);
		}
		else if (Key == "series")
		{
			FSeriesState Series;
			bOk = SeriesIndex < 3 && Fields.size() == 4 && ParseInt(Fields[0], Series.HighSeed) && ParseInt(Fields[1], Series.LowSeed) && ParseInt(Fields[2], Series.HighWins) && ParseInt(Fields[3], Series.LowWins);
			if (bOk)
			{
				(SeriesIndex < 2 ? State.Semifinals[SeriesIndex] : State.FinalSeries) = Series;
				++SeriesIndex;
			}
		}
		else if (Key == "athlete")
		{
			FAthleteState Athlete;
			int Choice = 0;
			int HasChoice = 0;
			std::vector<int> Points;
			std::vector<double> Minutes;
			bOk = Fields.size() == 11
				&& ParseDouble(Fields[0], Athlete.Fatigue) && ParseInt(Fields[1], Athlete.RecoveryDays) && ParseDouble(Fields[2], Athlete.Readiness)
				&& ParseInt(Fields[3], Athlete.RoutineStreak) && ParseInt(Fields[4], Choice) && ParseInt(Fields[5], HasChoice)
				&& ParseInt(Fields[6], Athlete.SeasonGames) && ParseInt(Fields[7], Athlete.SeasonPoints) && ParseDouble(Fields[8], Athlete.SeasonMinutes)
				&& ParseList<int>(Fields[9], Points, ParseInt) && ParseList<double>(Fields[10], Minutes, ParseDouble)
				&& Points.size() == Minutes.size() && Choice >= 0 && Choice <= 3;
			Athlete.LastChoice = static_cast<ELifeChoice>(Choice);
			Athlete.bHasLastChoice = HasChoice != 0;
			for (size_t Index = 0; bOk && Index < Points.size(); ++Index)
			{
				Athlete.ScoringHistory.push_back({Points[Index], Minutes[Index]});
			}
			State.Athletes.push_back(Athlete);
		}
		else if (Key == "game")
		{
			FScheduledGame Game;
			int Stage = 0;
			int Played = 0;
			int Published = 0;
			bOk = Fields.size() == 18
				&& ParseInt(Fields[0], Game.Id) && ParseInt(Fields[1], Game.Day) && ParseInt(Fields[2], Game.Home) && ParseInt(Fields[3], Game.Away)
				&& ParseUInt64(Fields[4], Game.Seed) && ParseInt(Fields[5], Stage) && ParseInt(Fields[6], Game.Series) && ParseInt(Fields[7], Game.SeriesGame)
				&& ParseInt(Fields[8], Played) && ParseInt(Fields[9], Game.HomeScore) && ParseInt(Fields[10], Game.AwayScore) && ParseInt(Fields[11], Game.Overtime)
				&& ParseInt(Fields[12], Published) && ParseInt64(Fields[13], Game.HomeWinProbabilityE8) && ParseDouble(Fields[14], Game.PublicEloProbability)
				&& ParseList<double>(Fields[15], Game.PregameFatigue, ParseDouble) && ParseList<int>(Fields[16], Game.PregameAvailability, ParseInt)
				&& ParseList<double>(Fields[17], Game.PregameReadiness, ParseDouble) && Stage >= 0 && Stage <= 2;
			Game.Stage = static_cast<EGameStage>(Stage);
			Game.bPlayed = Played != 0;
			Game.bOddsPublished = Published != 0;
			State.Games.push_back(Game);
		}
		if (!bOk)
		{
			OutError = "invalid league save field: " + Key;
			return false;
		}
	}
	const size_t AthleteCount = static_cast<size_t>(AthleteIndex(Config, static_cast<int>(Config.Teams.size()), 0));
	if (State.Athletes.size() != AthleteCount || State.Elo.size() != Config.Teams.size() || State.Standings.size() != Config.Teams.size() || State.Games.empty())
	{
		OutError = "league save does not match this league";
		return false;
	}
	for (const FScheduledGame& Game : State.Games)
	{
		const int TeamCount = static_cast<int>(Config.Teams.size());
		if (Game.Home < 0 || Game.Home >= TeamCount || Game.Away < 0 || Game.Away >= TeamCount || Game.Home == Game.Away)
		{
			OutError = "league save has an invalid game";
			return false;
		}
	}
	OutState = State;
	return true;
}
}

#if defined(_MSC_VER)
#pragma float_control(pop)
#endif
