#pragma once

#include "CoreMinimal.h"

struct FOddsWellPublicAthlete
{
	FString Name;
	int32 Overall = 0;
	bool bAvailable = false;
};

struct FOddsWellPublicTeam
{
	FString Name;
	TArray<FOddsWellPublicAthlete> Athletes;
};

struct FOddsWellPublicStanding
{
	FString Team;
	int32 Wins = 0;
	int32 Losses = 0;
	int32 PointDifference = 0;
};

struct FOddsWellPublicGame
{
	int32 Number = 0;
	FString Home;
	FString Away;
	int32 HomeScore = 0;
	int32 AwayScore = 0;
	FString Winner;
	FString ReplaySha256;
};

struct FOddsWellPublicLeagueSnapshot
{
	int32 SeasonNumber = 0;
	FString SeasonStatus;
	FString Boundary;
	TArray<FOddsWellPublicStanding> Standings;
	TArray<FOddsWellPublicTeam> Teams;
	TArray<FOddsWellPublicGame> Games;
};

ODDSWELL_API bool LoadOddsWellPublicLeagueSnapshot(FOddsWellPublicLeagueSnapshot& OutSnapshot, FString& OutError);
ODDSWELL_API int32 GetOddsWellPublicLeaguePageCount(const FOddsWellPublicLeagueSnapshot& Snapshot);
ODDSWELL_API FString BuildOddsWellPublicLeaguePage(const FOddsWellPublicLeagueSnapshot& Snapshot, int32 PageIndex);
