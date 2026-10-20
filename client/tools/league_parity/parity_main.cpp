// Compares the C++ league core with Python reference output from golden.py.
// Usage: league_parity <golden dir>
#include "../../OddsWell/Source/OddsWell/League/OddsWellLeagueCore.h"

#include <cstdio>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

using namespace OddsWellLeague;

namespace
{
	int Failures = 0;

	std::vector<std::string> ReadLines(const std::string& Path)
	{
		std::ifstream File(Path);
		std::vector<std::string> Lines;
		std::string Line;
		while (std::getline(File, Line))
		{
			if (!Line.empty() && Line.back() == '\r')
			{
				Line.pop_back();
			}
			Lines.push_back(Line);
		}
		return Lines;
	}

	std::vector<std::string> Split(const std::string& Text, char Separator)
	{
		std::vector<std::string> Parts;
		std::stringstream Stream(Text);
		std::string Part;
		while (std::getline(Stream, Part, Separator))
		{
			Parts.push_back(Part);
		}
		return Parts;
	}

	std::string Fnv1a(const std::vector<std::string>& Lines)
	{
		uint64_t Value = 0xCBF29CE484222325ull;
		for (size_t Index = 0; Index < Lines.size(); ++Index)
		{
			if (Index)
			{
				Value ^= static_cast<unsigned char>('\n');
				Value *= 0x100000001B3ull;
			}
			for (const char Character : Lines[Index])
			{
				Value ^= static_cast<unsigned char>(Character);
				Value *= 0x100000001B3ull;
			}
		}
		char Buffer[32];
		std::snprintf(Buffer, sizeof(Buffer), "%016llx", static_cast<unsigned long long>(Value));
		return Buffer;
	}

	std::vector<std::string> Lines(const FGameResult& Result)
	{
		std::vector<std::string> Out;
		for (const FEvent& Event : Result.Events)
		{
			Out.push_back(CanonicalEventLine(Result, Event));
		}
		return Out;
	}

	void Expect(bool bCondition, const std::string& Label, const std::string& Detail = "")
	{
		if (!bCondition)
		{
			++Failures;
			std::printf("FAIL %s %s\n", Label.c_str(), Detail.c_str());
		}
	}

	void CompareGame(const std::string& Dir, const std::string& Name, const std::vector<std::string>& Actual, const std::string& ExpectedCount, const std::string& ExpectedHash)
	{
		const bool bMatch = std::to_string(Actual.size()) == ExpectedCount && Fnv1a(Actual) == ExpectedHash;
		Expect(bMatch, Name, "records/hash differ");
		if (bMatch)
		{
			return;
		}
		const std::vector<std::string> Expected = ReadLines(Dir + "/games/" + Name + ".txt");
		for (size_t Index = 0; Index < std::max(Expected.size(), Actual.size()); ++Index)
		{
			const std::string E = Index < Expected.size() ? Expected[Index] : "<none>";
			const std::string A = Index < Actual.size() ? Actual[Index] : "<none>";
			if (E != A)
			{
				std::printf("  first difference at record %zu\n  python: %s\n  c++   : %s\n", Index + 1, E.c_str(), A.c_str());
				break;
			}
		}
	}

	std::string Fixed(double Value, int Digits) { return FormatFixed(Value, Digits); }
}

int main(int Argc, char** Argv)
{
	if (Argc < 2)
	{
		std::printf("usage: league_parity <golden dir>\n");
		return 2;
	}
	const std::string Dir = Argv[1];
	const std::vector<std::string> Golden = ReadLines(Dir + "/golden.txt");
	std::map<std::string, std::string> Season; // "kind|number" -> rest
	const FLeagueConfig Config = PrototypeLeague();
	const FTeam Home = TeamForGame(Config, 0);
	const FTeam Away = TeamForGame(Config, 1);
	int Baselines = 0;
	for (const std::string& Line : Golden)
	{
		const std::vector<std::string> Parts = Split(Line, '|');
		if (Parts.empty())
		{
			continue;
		}
		if (Parts[0] == "baseline")
		{
			FGameResult Result;
			std::string Error;
			Expect(SimulateGame(std::stoull(Parts[1]), Home, Away, FGameInputs(), Result, Error), "baseline simulate", Error);
			Expect(std::to_string(Result.HomeScore) == Parts[2] && std::to_string(Result.AwayScore) == Parts[3], "baseline score " + Parts[1]);
			CompareGame(Dir, "baseline_" + Parts[1], Lines(Result), Parts[4], Parts[5]);
			++Baselines;
		}
		else if (Parts.size() >= 3)
		{
			const size_t Prefix = Parts[0].size() + Parts[1].size() + 2;
			Season[Parts[0] + "|" + Parts[1]] = Line.size() > Prefix ? Line.substr(Prefix) : "";
		}
	}

	// Two-team season, driven step by step exactly like phase0d.league.simulate_season(20, 10000).
	FLeagueState State;
	State.Athletes.assign(12, FAthleteState());
	State.Elo = {1500.0, 1500.0};
	State.Standings.assign(2, FStanding());
	auto Snapshot = [&](auto Value)
	{
		std::string Text;
		for (int Index = 0; Index < 12; ++Index)
		{
			const FAthlete& Athlete = Config.Teams[static_cast<size_t>(Index / 6)].Roster[static_cast<size_t>(Index % 6)];
			Text += (Index ? "," : "") + Athlete.Ratings.Name + "=" + Value(State.Athletes[static_cast<size_t>(Index)], Index);
		}
		return Text;
	};
	int SeasonGames = 0;
	for (int Index = 0; Index < 20; ++Index)
	{
		const int Number = Index + 1;
		const std::string Key = std::to_string(Number);
		FScheduledGame Game;
		Game.Id = Number;
		Game.Day = Number;
		Game.Seed = 10000 + Index;
		Game.Home = Index % 2 == 0 ? 0 : 1;
		Game.Away = 1 - Game.Home;
		std::string Life;
		if (Index)
		{
			RecoverDays(State, 1, 0, 12);
			ApplyLifeDay(Config, State, Number, true);
			for (int Athlete = 0; Athlete < 12; ++Athlete)
			{
				Life += (Athlete ? "," : "") + Config.Teams[static_cast<size_t>(Athlete / 6)].Roster[static_cast<size_t>(Athlete % 6)].Ratings.Name + "=" + LifeChoiceName(State.Athletes[static_cast<size_t>(Athlete)].LastChoice);
			}
		}
		Expect(Season["season_life|" + Key] == Life, "life " + Key, "\n  python: " + Season["season_life|" + Key] + "\n  c++   : " + Life);
		Expect(Season["season_pregame_fatigue|" + Key] == Snapshot([](const FAthleteState& A, int) { return Fixed(A.Fatigue, 6); }), "pregame fatigue " + Key);
		Expect(Season["season_pregame_availability|" + Key] == Snapshot([](const FAthleteState& A, int) { return std::to_string(A.RecoveryDays); }), "pregame availability " + Key);
		Expect(Season["season_pregame_readiness|" + Key] == Snapshot([](const FAthleteState& A, int) { return Fixed(A.Readiness, 6); }), "pregame readiness " + Key);

		std::vector<int> AvailabilityByTeam[2];
		for (int Athlete = 0; Athlete < 12; ++Athlete)
		{
			AvailabilityByTeam[Athlete / 6].push_back(State.Athletes[static_cast<size_t>(Athlete)].RecoveryDays);
		}
		const std::pair<double, double> Odds = PredictHomeWin(
			TeamForGame(Config, Game.Home), TeamForGame(Config, Game.Away),
			AvailabilityByTeam[Game.Home], AvailabilityByTeam[Game.Away], State.Elo[static_cast<size_t>(Game.Home)], State.Elo[static_cast<size_t>(Game.Away)]);
		const std::string OddsText = Fixed(Odds.first, 8) + "|" + Fixed(Odds.second, 8);
		Expect(Season["season_odds|" + Key] == OddsText, "odds " + Key, Season["season_odds|" + Key] + " vs " + OddsText);

		FGameInputs Inputs;
		BuildGameInputs(Config, State, Game.Home, Game.Away, Inputs);
		FGameResult Result;
		std::string Error;
		Expect(SimulateGame(Game.Seed, TeamForGame(Config, Game.Home), TeamForGame(Config, Game.Away), Inputs, Result, Error), "season simulate", Error);
		const std::vector<std::string> GameParts = Split(Season["season_game|" + Key], '|');
		if (GameParts.size() == 7)
		{
			Expect(std::to_string(Result.HomeScore) == GameParts[3] && std::to_string(Result.AwayScore) == GameParts[4], "season score " + Key);
			CompareGame(Dir, "season_" + Key, Lines(Result), GameParts[5], GameParts[6]);
		}
		else
		{
			Expect(false, "season game golden " + Key);
		}
		std::string Minutes;
		for (int Athlete = 0; Athlete < 12; ++Athlete)
		{
			const int Team = Athlete / 6;
			const int Offset = Team == Game.Home ? 0 : 6;
			Minutes += (Athlete ? "," : "") + Config.Teams[static_cast<size_t>(Team)].Roster[static_cast<size_t>(Athlete % 6)].Ratings.Name + "=" + Fixed(Result.MinutesPlayed[static_cast<size_t>(Offset + Athlete % 6)], 6);
		}
		Expect(Season["season_minutes|" + Key] == Minutes, "minutes " + Key);
		ApplyGameAftermath(Config, State, Game, Result);
		Expect(Season["season_postgame_fatigue|" + Key] == Snapshot([](const FAthleteState& A, int) { return Fixed(A.Fatigue, 6); }), "postgame fatigue " + Key);
		Expect(Season["season_postgame_availability|" + Key] == Snapshot([](const FAthleteState& A, int) { return std::to_string(A.RecoveryDays); }), "postgame availability " + Key);
		const bool bHomeWin = Result.HomeScore > Result.AwayScore;
		const double Change = 20.0 * ((bHomeWin ? 1 : 0) - Odds.first);
		State.Elo[static_cast<size_t>(Game.Home)] += Change;
		State.Elo[static_cast<size_t>(Game.Away)] -= Change;
		FStanding& Winner = State.Standings[static_cast<size_t>(bHomeWin ? Game.Home : Game.Away)];
		FStanding& Loser = State.Standings[static_cast<size_t>(bHomeWin ? Game.Away : Game.Home)];
		Winner.Wins += 1;
		Loser.Losses += 1;
		State.Standings[static_cast<size_t>(Game.Home)].PointsFor += Result.HomeScore;
		State.Standings[static_cast<size_t>(Game.Home)].PointsAgainst += Result.AwayScore;
		State.Standings[static_cast<size_t>(Game.Away)].PointsFor += Result.AwayScore;
		State.Standings[static_cast<size_t>(Game.Away)].PointsAgainst += Result.HomeScore;
		++SeasonGames;
	}
	for (int Team = 0; Team < 2; ++Team)
	{
		const FStanding& Row = State.Standings[static_cast<size_t>(Team)];
		const std::string Text = std::to_string(Row.Wins) + "|" + std::to_string(Row.Losses) + "|" + std::to_string(Row.PointsFor) + "|" + std::to_string(Row.PointsAgainst);
		Expect(Season["standing|" + Config.Teams[static_cast<size_t>(Team)].Name] == Text, "standing " + Config.Teams[static_cast<size_t>(Team)].Name);
	}

	// Eight-team league smoke: a full season with playoffs, save/load round trip, replay invariance.
	const FLeagueConfig& League = DefaultLeague();
	FLeagueState Live;
	NewLeague(League, 20261020ull, Live);
	Expect(Live.Games.size() == static_cast<size_t>(RegularSeasonDays(League) * 4), "schedule size");
	std::vector<int> HomeGames(8, 0), Played(8, 0);
	for (const FScheduledGame& Game : Live.Games)
	{
		HomeGames[static_cast<size_t>(Game.Home)] += 1;
		Played[static_cast<size_t>(Game.Home)] += 1;
		Played[static_cast<size_t>(Game.Away)] += 1;
	}
	for (int Team = 0; Team < 8; ++Team)
	{
		Expect(Played[static_cast<size_t>(Team)] == 28 && HomeGames[static_cast<size_t>(Team)] == 14, "balanced schedule team " + std::to_string(Team));
	}
	int Days = 0;
	int Overtimes = 0;
	int Upsets = 0;
	int Favorites = 0;
	while (Live.CompletedSeasons == 0 && Days < 60)
	{
		PrepareDay(League, Live);
		const std::string Saved = SerializeLeague(Live);
		FLeagueState Loaded;
		std::string Error;
		Expect(DeserializeLeague(League, Saved, Loaded, Error) && SerializeLeague(Loaded) == Saved, "save round trip day " + std::to_string(Live.Day), Error);
		std::vector<FGameResult> Results;
		Expect(PlayDay(League, Live, &Results, Error), "play day", Error);
		for (const FGameResult& Result : Results)
		{
			Overtimes += Result.Overtime > 0;
		}
		for (int Id : GamesOnDay(Live, Live.Day))
		{
			const FScheduledGame& Game = Live.Games[static_cast<size_t>(Id - 1)];
			const bool bHomeFavored = Game.HomeWinProbabilityE8 > ProbabilityScale / 2;
			((Game.HomeScore > Game.AwayScore) == bHomeFavored ? Favorites : Upsets) += 1;
			FGameResult Replay;
			Expect(ReplayGame(League, Live, Id, Replay, Error), "replay game " + std::to_string(Id), Error);
		}
		AdvanceDay(League, Live);
		++Days;
	}
	Expect(Live.CompletedSeasons == 1 && Live.SeasonNumber == 2, "season completes with playoffs");
	std::printf("8-team season: %d days, %d overtime games, favorites won %d of %d\n", Days, Overtimes, Favorites, Favorites + Upsets);

	std::printf("baseline games: %d, season games: %d\n", Baselines, SeasonGames);
	std::printf(Failures ? "PARITY_FAIL %d\n" : "PARITY_PASS\n", Failures);
	return Failures ? 1 : 0;
}
