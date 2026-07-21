#include "PublicLeagueView.h"

#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 GamesPerPage = 5;

bool ReadInt(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field, int32& OutValue)
{
	double Number = 0.0;
	if (!Object.IsValid() || !Object->TryGetNumberField(Field, Number))
	{
		return false;
	}
	OutValue = static_cast<int32>(Number);
	return true;
}
}

bool LoadOddsWellPublicLeagueSnapshot(FOddsWellPublicLeagueSnapshot& OutSnapshot, FString& OutError)
{
	OutSnapshot = {};
	const FString Path = FPaths::Combine(FPaths::ProjectContentDir(), TEXT("League/PublicSeason1.json"));
	FString JsonText;
	if (!FFileHelper::LoadFileToString(JsonText, *Path))
	{
		OutError = FString::Printf(TEXT("Public league snapshot not found: %s"), *Path);
		return false;
	}

	TSharedPtr<FJsonObject> Root;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
	if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
	{
		OutError = TEXT("Public league snapshot is not valid JSON.");
		return false;
	}
	FString Schema;
	bool bPublicOnly = false;
	const TSharedPtr<FJsonObject>* Season = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Standings = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Teams = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Games = nullptr;
	if (!Root->TryGetStringField(TEXT("schema"), Schema)
		|| Schema != TEXT("oddswell-public-league-v1")
		|| !Root->TryGetBoolField(TEXT("public_only"), bPublicOnly)
		|| !bPublicOnly
		|| !Root->TryGetStringField(TEXT("boundary"), OutSnapshot.Boundary)
		|| !Root->TryGetObjectField(TEXT("season"), Season)
		|| !Root->TryGetArrayField(TEXT("standings"), Standings)
		|| !Root->TryGetArrayField(TEXT("teams"), Teams)
		|| !Root->TryGetArrayField(TEXT("games"), Games)
		|| !ReadInt(*Season, TEXT("number"), OutSnapshot.SeasonNumber)
		|| !(*Season)->TryGetStringField(TEXT("status"), OutSnapshot.SeasonStatus))
	{
		OutError = TEXT("Public league snapshot schema is incomplete or private.");
		return false;
	}

	for (const TSharedPtr<FJsonValue>& Value : *Standings)
	{
		const TSharedPtr<FJsonObject> Object = Value->AsObject();
		FOddsWellPublicStanding Standing;
		if (!Object.IsValid()
			|| !Object->TryGetStringField(TEXT("team"), Standing.Team)
			|| !ReadInt(Object, TEXT("wins"), Standing.Wins)
			|| !ReadInt(Object, TEXT("losses"), Standing.Losses)
			|| !ReadInt(Object, TEXT("point_difference"), Standing.PointDifference))
		{
			OutError = TEXT("Public league snapshot has an invalid standing.");
			return false;
		}
		OutSnapshot.Standings.Add(MoveTemp(Standing));
	}

	for (const TSharedPtr<FJsonValue>& Value : *Teams)
	{
		const TSharedPtr<FJsonObject> Object = Value->AsObject();
		const TArray<TSharedPtr<FJsonValue>>* Players = nullptr;
		FOddsWellPublicTeam Team;
		if (!Object.IsValid()
			|| !Object->TryGetStringField(TEXT("name"), Team.Name)
			|| !Object->TryGetArrayField(TEXT("players"), Players))
		{
			OutError = TEXT("Public league snapshot has an invalid team.");
			return false;
		}
		for (const TSharedPtr<FJsonValue>& PlayerValue : *Players)
		{
			const TSharedPtr<FJsonObject> Player = PlayerValue->AsObject();
			FOddsWellPublicAthlete Athlete;
			if (!Player.IsValid()
				|| !Player->TryGetStringField(TEXT("name"), Athlete.Name)
				|| !ReadInt(Player, TEXT("overall"), Athlete.Overall)
				|| !Player->TryGetBoolField(TEXT("available"), Athlete.bAvailable))
			{
				OutError = TEXT("Public league snapshot has an invalid athlete.");
				return false;
			}
			Team.Athletes.Add(MoveTemp(Athlete));
		}
		OutSnapshot.Teams.Add(MoveTemp(Team));
	}

	for (const TSharedPtr<FJsonValue>& Value : *Games)
	{
		const TSharedPtr<FJsonObject> Object = Value->AsObject();
		FOddsWellPublicGame Game;
		if (!Object.IsValid()
			|| !ReadInt(Object, TEXT("number"), Game.Number)
			|| !Object->TryGetStringField(TEXT("home"), Game.Home)
			|| !Object->TryGetStringField(TEXT("away"), Game.Away)
			|| !ReadInt(Object, TEXT("home_score"), Game.HomeScore)
			|| !ReadInt(Object, TEXT("away_score"), Game.AwayScore)
			|| !Object->TryGetStringField(TEXT("winner"), Game.Winner)
			|| !Object->TryGetStringField(TEXT("replay_sha256"), Game.ReplaySha256)
			|| Game.ReplaySha256.Len() != 64)
		{
			OutError = TEXT("Public league snapshot has an invalid completed game.");
			return false;
		}
		OutSnapshot.Games.Add(MoveTemp(Game));
	}

	int32 AthleteCount = 0;
	for (const FOddsWellPublicTeam& Team : OutSnapshot.Teams)
	{
		AthleteCount += Team.Athletes.Num();
	}
	if (OutSnapshot.SeasonNumber != 1
		|| OutSnapshot.SeasonStatus != TEXT("COMPLETE")
		|| OutSnapshot.Standings.Num() != 2
		|| OutSnapshot.Teams.Num() != 2
		|| AthleteCount != 12
		|| OutSnapshot.Games.Num() != 20)
	{
		OutError = TEXT("Public league snapshot does not match the frozen two-team development season.");
		return false;
	}
	OutError.Reset();
	return true;
}

int32 GetOddsWellPublicLeaguePageCount(const FOddsWellPublicLeagueSnapshot& Snapshot)
{
	return 1 + Snapshot.Teams.Num() + FMath::DivideAndRoundUp(Snapshot.Games.Num(), GamesPerPage);
}

FString BuildOddsWellPublicLeaguePage(const FOddsWellPublicLeagueSnapshot& Snapshot, const int32 PageIndex)
{
	const int32 PageCount = GetOddsWellPublicLeaguePageCount(Snapshot);
	if (PageCount <= 0 || PageIndex < 0 || PageIndex >= PageCount)
	{
		return TEXT("LEAGUE VIEW UNAVAILABLE");
	}

	FString Text = FString::Printf(
		TEXT("PUBLIC LEAGUE | SEASON %d %s | PAGE %d/%d\n"),
		Snapshot.SeasonNumber,
		*Snapshot.SeasonStatus,
		PageIndex + 1,
		PageCount);
	if (PageIndex == 0)
	{
		Text += TEXT("STANDINGS\n");
		for (int32 Index = 0; Index < Snapshot.Standings.Num(); ++Index)
		{
			const FOddsWellPublicStanding& Row = Snapshot.Standings[Index];
			Text += FString::Printf(
				TEXT("%d. %s  %d-%d  DIFF %+d\n"),
				Index + 1,
				*Row.Team,
				Row.Wins,
				Row.Losses,
				Row.PointDifference);
		}
		Text += FString::Printf(TEXT("\n%d TEAMS | 12 ATHLETES | %d VERIFIED RESULTS"), Snapshot.Teams.Num(), Snapshot.Games.Num());
	}
	else if (PageIndex <= Snapshot.Teams.Num())
	{
		const FOddsWellPublicTeam& Team = Snapshot.Teams[PageIndex - 1];
		Text += Team.Name + TEXT(" | PUBLIC ROSTER\n");
		for (const FOddsWellPublicAthlete& Athlete : Team.Athletes)
		{
			Text += FString::Printf(
				TEXT("%s  OVR %d  %s\n"),
				*Athlete.Name,
				Athlete.Overall,
				Athlete.bAvailable ? TEXT("AVAILABLE") : TEXT("OUT"));
		}
	}
	else
	{
		const int32 SchedulePage = PageIndex - 1 - Snapshot.Teams.Num();
		const int32 Start = SchedulePage * GamesPerPage;
		Text += TEXT("SCHEDULE / IMMUTABLE COMPLETED HISTORY\n");
		for (int32 Index = Start; Index < FMath::Min(Start + GamesPerPage, Snapshot.Games.Num()); ++Index)
		{
			const FOddsWellPublicGame& Game = Snapshot.Games[Index];
			Text += FString::Printf(
				TEXT("G%02d  %s %d - %d %s\n       WINNER: %s | REPLAY %s\n"),
				Game.Number,
				*Game.Away,
				Game.AwayScore,
				Game.HomeScore,
				*Game.Home,
				*Game.Winner,
				*Game.ReplaySha256.Left(10));
		}
	}
	return Text + TEXT("\n[L] CLOSE   [,] PREVIOUS   [.] NEXT");
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellPublicLeagueViewTest,
	"OddsWell.Character.PublicLeagueView",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellPublicLeagueViewTest::RunTest(const FString& Parameters)
{
	FOddsWellPublicLeagueSnapshot Snapshot;
	FString Error;
	TestTrue(TEXT("Frozen public league snapshot loads"), LoadOddsWellPublicLeagueSnapshot(Snapshot, Error));
	TestEqual(TEXT("Two public teams"), Snapshot.Teams.Num(), 2);
	TestEqual(TEXT("Twenty completed games"), Snapshot.Games.Num(), 20);
	TestEqual(TEXT("Seven readable pages"), GetOddsWellPublicLeaguePageCount(Snapshot), 7);
	TestTrue(TEXT("Standings page names Harbor City"), BuildOddsWellPublicLeaguePage(Snapshot, 0).Contains(TEXT("Harbor City Waves")));
	TestTrue(TEXT("Roster exposes availability"), BuildOddsWellPublicLeaguePage(Snapshot, 2).Contains(TEXT("OUT")));
	TestTrue(TEXT("History exposes the final game"), BuildOddsWellPublicLeaguePage(Snapshot, 6).Contains(TEXT("G20")));
	return true;
}
#endif
