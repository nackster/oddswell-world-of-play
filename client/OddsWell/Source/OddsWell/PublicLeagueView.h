#pragma once

#include "CoreMinimal.h"

struct FOddsWellPublicAthlete
{
	FString Name;
	int32 Overall = 0;
	int32 Shooting = 0;
	int32 Passing = 0;
	int32 Defense = 0;
	int32 Rebounding = 0;
	int32 Stamina = 0;
	bool bAvailable = false;
	FString TalentTier;
	FString Specialty;
	FString Consistency;
	FString OffensiveRole;
	FString Form;
	double SeasonPointsPerGame = 0.0;
	double RecentPointsPerGame = 0.0;
	double RecentMinutesPerGame = 0.0;
	FString LifeChoice;
	int32 LifeGame = 0;
	FString LifeBrainVersion;
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

struct FOddsWellMatchWinnerSelectionPreview
{
	FString Team;
	int64 WinProbabilityE8 = 0;
	int64 DecimalOddsE4 = 0;
	int64 MinimumStakeGrossReturn = 0;
	int64 MaximumStakeGrossReturn = 0;
};

struct FOddsWellMatchWinnerOfferPreview
{
	FString OfferId;
	FString OfferVersion;
	FString SourcePredictionVersion;
	FString SourceSnapshotVersion;
	FString SourceModel;
	FString SourceCommitmentSha256;
	int32 SeasonNumber = 0;
	int32 GameNumber = 0;
	FString HomeTeam;
	FString AwayTeam;
	int64 LockUnix = 0;
	int64 MinimumStake = 0;
	int64 MaximumStake = 0;
	int64 StakeIncrement = 0;
	TArray<FOddsWellMatchWinnerSelectionPreview> Selections;
};

ODDSWELL_API bool LoadOddsWellPublicLeagueSnapshot(FOddsWellPublicLeagueSnapshot& OutSnapshot, FString& OutError);
ODDSWELL_API int32 GetOddsWellPublicLeaguePageCount(const FOddsWellPublicLeagueSnapshot& Snapshot);
ODDSWELL_API FString BuildOddsWellPublicLeaguePage(const FOddsWellPublicLeagueSnapshot& Snapshot, int32 PageIndex);
#if UE_BUILD_DEVELOPMENT
ODDSWELL_API FString BuildOddsWellAthleteComprehensionCheck(const FOddsWellPublicLeagueSnapshot& Snapshot);
ODDSWELL_API int32 GetOddsWellAthleteComprehensionItemCount();
ODDSWELL_API bool SubmitOddsWellAthleteComprehensionAnswer(const FOddsWellPublicLeagueSnapshot& Snapshot, FString& Answers, TCHAR Answer, FString& OutError);
ODDSWELL_API int32 ScoreOddsWellAthleteComprehensionAnswers(const FString& Answers);
ODDSWELL_API FString BuildOddsWellAthleteComprehensionSessionPage(const FOddsWellPublicLeagueSnapshot& Snapshot, const FString& Answers);
#endif
ODDSWELL_API bool LoadOddsWellMatchWinnerOfferPreview(FOddsWellMatchWinnerOfferPreview& OutPreview, FString& OutError);
ODDSWELL_API FString BuildOddsWellMatchWinnerOfferPreview(const FOddsWellMatchWinnerOfferPreview& Preview);
