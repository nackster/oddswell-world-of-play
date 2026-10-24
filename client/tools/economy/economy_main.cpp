// Economy check: plays whole careers' worth of seasons with the real league core and reports the
// return on flat-betting every outcome of every market, so prices and rewards can be balanced.
// Usage: league_economy [seasons]
#include "../../OddsWell/Source/OddsWell/League/OddsWellLeagueCore.h"

#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

using namespace OddsWellLeague;

namespace
{
	struct FTally
	{
		double Staked = 0.0;
		double Returned = 0.0;
		int Bets = 0;
		int Wins = 0;
		double ExpectedWins = 0.0;
	};

	const char* OutcomeName(EMarket Market, int Outcome)
	{
		static const char* Margin[6] = {"home by 1-5", "home by 6-10", "home by 11+", "away by 1-5", "away by 6-10", "away by 11+"};
		switch (Market)
		{
		case EMarket::MatchWinner: return Outcome == 0 ? "match: home" : "match: away";
		case EMarket::Margin: return Margin[Outcome];
		case EMarket::Overtime: return Outcome == 0 ? "overtime: yes" : "overtime: no";
		case EMarket::HomeStarPoints: return Outcome == 0 ? "home star: over" : "home star: under";
		case EMarket::AwayStarPoints: return Outcome == 0 ? "away star: over" : "away star: under";
		default: return "?";
		}
	}
}

int main(int Argc, char** Argv)
{
	const int Seasons = Argc > 1 ? std::atoi(Argv[1]) : 10;
	const FLeagueConfig& League = DefaultLeague();
	std::vector<std::vector<FTally>> Tallies(static_cast<size_t>(EMarket::Count));
	for (int Market = 0; Market < static_cast<int>(EMarket::Count); ++Market)
	{
		Tallies[static_cast<size_t>(Market)].resize(static_cast<size_t>(MarketOutcomeCount(static_cast<EMarket>(Market))));
	}
	FTally Favourite;
	FTally Underdog;
	int Days = 0;
	int Games = 0;
	for (int Season = 0; Season < Seasons; ++Season)
	{
		FLeagueState State;
		NewLeague(League, 900001ull + static_cast<uint64_t>(Season) * 7919ull, State);
		while (State.CompletedSeasons == 0)
		{
			PrepareDay(League, State);
			std::string Error;
			if (!PlayDay(League, State, nullptr, Error))
			{
				std::printf("play failed: %s\n", Error.c_str());
				return 1;
			}
			for (const int Id : GamesOnDay(State, State.Day))
			{
				const FScheduledGame& Game = State.Games[static_cast<size_t>(Id - 1)];
				++Games;
				for (int Market = 0; Market < static_cast<int>(EMarket::Count); ++Market)
				{
					const EMarket Kind = static_cast<EMarket>(Market);
					if (!IsOutcomeAvailable(Game, Kind))
					{
						continue;
					}
					for (int Outcome = 0; Outcome < MarketOutcomeCount(Kind); ++Outcome)
					{
						bool bWon = false;
						if (!DidOutcomeWin(Game, Kind, Outcome, bWon))
						{
							continue;
						}
						const int64_t Probability = OutcomeProbabilityE8(Game, Kind, Outcome);
						FTally& Tally = Tallies[static_cast<size_t>(Market)][static_cast<size_t>(Outcome)];
						Tally.Staked += 100.0;
						Tally.Returned += bWon ? static_cast<double>(GrossReturn(100, Probability)) : 0.0;
						Tally.Bets += 1;
						Tally.Wins += bWon ? 1 : 0;
						Tally.ExpectedWins += static_cast<double>(FairProbabilityE8(Game, Kind, Outcome)) / ProbabilityScale;
						if (Kind == EMarket::MatchWinner)
						{
							FTally& Side = (Probability >= ProbabilityScale / 2) ? Favourite : Underdog;
							Side.Staked += 100.0;
							Side.Returned += bWon ? static_cast<double>(GrossReturn(100, Probability)) : 0.0;
							Side.Bets += 1;
							Side.Wins += bWon ? 1 : 0;
							Side.ExpectedWins += static_cast<double>(FairProbabilityE8(Game, Kind, Outcome)) / ProbabilityScale;
						}
					}
				}
			}
			AdvanceDay(League, State);
			++Days;
		}
	}
	std::printf("%d seasons, %d days (%.1f per season), %d games\n", Seasons, Days, static_cast<double>(Days) / Seasons, Games);
	std::printf("%-20s %6s %8s %8s %8s\n", "outcome", "bets", "wins", "priced", "return");
	auto Print = [](const char* Name, const FTally& Tally)
	{
		std::printf("%-20s %6d %8d %8.1f %7.1f%%\n", Name, Tally.Bets, Tally.Wins, Tally.ExpectedWins, Tally.Staked > 0 ? 100.0 * Tally.Returned / Tally.Staked : 0.0);
	};
	for (int Market = 0; Market < static_cast<int>(EMarket::Count); ++Market)
	{
		for (int Outcome = 0; Outcome < MarketOutcomeCount(static_cast<EMarket>(Market)); ++Outcome)
		{
			Print(OutcomeName(static_cast<EMarket>(Market), Outcome), Tallies[static_cast<size_t>(Market)][static_cast<size_t>(Outcome)]);
		}
	}
	Print("match: favourite", Favourite);
	Print("match: underdog", Underdog);
	return 0;
}
