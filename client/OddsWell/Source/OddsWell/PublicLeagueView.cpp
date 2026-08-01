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
constexpr int64 ProbabilityScale = 100000000;
constexpr int64 OddsDisplayScale = 10000;
constexpr int64 ExpectedLockUnix = 2000000000;
const FString ExpectedOfferId(TEXT("29d3ab7c4fd2858b4cfa80f1f413a77aaa30fbdde1ca593b477d82f2e726617e"));
const FString ExpectedCommitment(TEXT("898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f"));

int32 GetAthleteCount(const FOddsWellPublicLeagueSnapshot& Snapshot)
{
	int32 Count = 0;
	for (const FOddsWellPublicTeam& Team : Snapshot.Teams)
	{
		Count += Team.Athletes.Num();
	}
	return Count;
}

const FOddsWellPublicAthlete* FindAthlete(
	const FOddsWellPublicLeagueSnapshot& Snapshot,
	int32 AthleteIndex,
	const FOddsWellPublicTeam*& OutTeam)
{
	for (const FOddsWellPublicTeam& Team : Snapshot.Teams)
	{
		if (AthleteIndex < Team.Athletes.Num())
		{
			OutTeam = &Team;
			return &Team.Athletes[AthleteIndex];
		}
		AthleteIndex -= Team.Athletes.Num();
	}
	OutTeam = nullptr;
	return nullptr;
}

FString BuildPublicAthleteExplanation(const FOddsWellPublicAthlete& Athlete)
{
	const double ScoringDelta = Athlete.RecentPointsPerGame - Athlete.SeasonPointsPerGame;
	const FString RecentScoring = FMath::IsNearlyZero(ScoringDelta, 0.005)
		? FString::Printf(TEXT("RECENT: %.2f PPG matches the season rate; archive label %s."), Athlete.RecentPointsPerGame, *Athlete.Form)
		: FString::Printf(
			TEXT("RECENT: %.2f PPG is %.2f %s season %.2f; archive label %s."),
			Athlete.RecentPointsPerGame,
			FMath::Abs(ScoringDelta),
			ScoringDelta > 0.0 ? TEXT("above") : TEXT("below"),
			Athlete.SeasonPointsPerGame,
			*Athlete.Form);
	const FString PublicStatus = Athlete.bAvailable
		? TEXT("STATUS: AVAILABLE; no hidden health conclusion is published.")
		: TEXT("STATUS: OUT; the archive does not publish a cause.");
	return FString::Printf(
		TEXT("PUBLIC EXPLANATION | EVIDENCE, NOT DIAGNOSIS\n")
		TEXT("BASELINE: %s / %s; %s role, %s consistency, %.2f public MPG.\n")
		TEXT("%s\n")
		TEXT("LIFE: Game %d %s is recorded context, not a proven cause.\n")
		TEXT("%s"),
		*Athlete.TalentTier.ToUpper(),
		*Athlete.Specialty.ToUpper(),
		*Athlete.OffensiveRole.ToUpper(),
		*Athlete.Consistency.ToUpper(),
		Athlete.RecentMinutesPerGame,
		*RecentScoring,
		Athlete.LifeGame,
		*Athlete.LifeChoice,
		*PublicStatus);
}

bool LoadPublicLeagueRoot(TSharedPtr<FJsonObject>& OutRoot, FString& OutError)
{
	const FString Path = FPaths::Combine(FPaths::ProjectContentDir(), TEXT("League/PublicSeason1.json"));
	FString JsonText;
	if (!FFileHelper::LoadFileToString(JsonText, *Path))
	{
		OutError = FString::Printf(TEXT("Public league snapshot not found: %s"), *Path);
		return false;
	}
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
	if (!FJsonSerializer::Deserialize(Reader, OutRoot) || !OutRoot.IsValid())
	{
		OutError = TEXT("Public league snapshot is not valid JSON.");
		return false;
	}
	return true;
}

bool HasExactFields(const TSharedPtr<FJsonObject>& Object, const TArray<FString>& Expected)
{
	if (!Object.IsValid() || Object->Values.Num() != Expected.Num())
	{
		return false;
	}
	for (const FString& Field : Expected)
	{
		if (!Object->HasField(Field))
		{
			return false;
		}
	}
	return true;
}

bool ReadInt64(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field, int64& OutValue)
{
	double Number = 0.0;
	if (!Object.IsValid() || !Object->TryGetNumberField(Field, Number) || !FMath::IsFinite(Number))
	{
		return false;
	}
	OutValue = static_cast<int64>(Number);
	return static_cast<double>(OutValue) == Number;
}

bool ReadInt(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field, int32& OutValue)
{
	int64 Number = 0;
	if (!ReadInt64(Object, Field, Number) || Number < MIN_int32 || Number > MAX_int32)
	{
		return false;
	}
	OutValue = static_cast<int32>(Number);
	return true;
}

bool ValidateMatchWinnerOffer(
	const TSharedPtr<FJsonObject>& Root,
	FOddsWellMatchWinnerOfferPreview& OutPreview,
	FString& OutError)
{
	OutPreview = {};
	FString RootSchema;
	bool bPublicOnly = false;
	const TSharedPtr<FJsonObject>* Offer = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Games = nullptr;
	if (!Root.IsValid()
		|| !Root->TryGetStringField(TEXT("schema"), RootSchema)
		|| RootSchema != TEXT("oddswell-public-league-v1")
		|| !Root->TryGetBoolField(TEXT("public_only"), bPublicOnly)
		|| !bPublicOnly
		|| !Root->TryGetObjectField(TEXT("match_winner_offer"), Offer)
		|| !Root->TryGetArrayField(TEXT("games"), Games))
	{
		OutError = TEXT("Match Winner preview has no verified public envelope.");
		return false;
	}

	const TArray<FString> OfferFields = {
		TEXT("offer_id"), TEXT("schema"), TEXT("offer_version"), TEXT("market"), TEXT("currency"),
		TEXT("source_prediction_version"), TEXT("source_snapshot_version"), TEXT("source_model"),
		TEXT("source_commitment_sha256"), TEXT("season_number"), TEXT("game_number"), TEXT("home_team"),
		TEXT("away_team"), TEXT("lock_unix"), TEXT("minimum_stake"), TEXT("maximum_stake"),
		TEXT("stake_increment"), TEXT("house_edge_bps"), TEXT("payout_formula"), TEXT("selections")};
	if (!HasExactFields(*Offer, OfferFields))
	{
		OutError = TEXT("Match Winner preview offer has malformed or hidden fields.");
		return false;
	}

	FString OfferSchema;
	FString Market;
	FString Currency;
	FString PayoutFormula;
	int64 HouseEdgeBps = -1;
	const TArray<TSharedPtr<FJsonValue>>* Selections = nullptr;
	if (!(*Offer)->TryGetStringField(TEXT("offer_id"), OutPreview.OfferId)
		|| !(*Offer)->TryGetStringField(TEXT("schema"), OfferSchema)
		|| !(*Offer)->TryGetStringField(TEXT("offer_version"), OutPreview.OfferVersion)
		|| !(*Offer)->TryGetStringField(TEXT("market"), Market)
		|| !(*Offer)->TryGetStringField(TEXT("currency"), Currency)
		|| !(*Offer)->TryGetStringField(TEXT("source_prediction_version"), OutPreview.SourcePredictionVersion)
		|| !(*Offer)->TryGetStringField(TEXT("source_snapshot_version"), OutPreview.SourceSnapshotVersion)
		|| !(*Offer)->TryGetStringField(TEXT("source_model"), OutPreview.SourceModel)
		|| !(*Offer)->TryGetStringField(TEXT("source_commitment_sha256"), OutPreview.SourceCommitmentSha256)
		|| !ReadInt(*Offer, TEXT("season_number"), OutPreview.SeasonNumber)
		|| !ReadInt(*Offer, TEXT("game_number"), OutPreview.GameNumber)
		|| !(*Offer)->TryGetStringField(TEXT("home_team"), OutPreview.HomeTeam)
		|| !(*Offer)->TryGetStringField(TEXT("away_team"), OutPreview.AwayTeam)
		|| !ReadInt64(*Offer, TEXT("lock_unix"), OutPreview.LockUnix)
		|| !ReadInt64(*Offer, TEXT("minimum_stake"), OutPreview.MinimumStake)
		|| !ReadInt64(*Offer, TEXT("maximum_stake"), OutPreview.MaximumStake)
		|| !ReadInt64(*Offer, TEXT("stake_increment"), OutPreview.StakeIncrement)
		|| !ReadInt64(*Offer, TEXT("house_edge_bps"), HouseEdgeBps)
		|| !(*Offer)->TryGetStringField(TEXT("payout_formula"), PayoutFormula)
		|| !(*Offer)->TryGetArrayField(TEXT("selections"), Selections))
	{
		OutPreview = {};
		OutError = TEXT("Match Winner preview offer is incomplete.");
		return false;
	}
	if (OutPreview.OfferId != ExpectedOfferId
		|| OfferSchema != TEXT("oddswell-basketball-odds-offer-v1")
		|| OutPreview.OfferVersion != TEXT("basketball-match-winner-odds-v1")
		|| Market != TEXT("match_winner")
		|| Currency != TEXT("odds_bucks")
		|| OutPreview.SourcePredictionVersion != TEXT("phase0d4-v1")
		|| OutPreview.SourceSnapshotVersion != TEXT("oddswell-public-pregame-v1")
		|| OutPreview.SourceModel != TEXT("public_elo_rotation")
		|| OutPreview.SourceCommitmentSha256 != ExpectedCommitment
		|| OutPreview.SeasonNumber != 1
		|| OutPreview.GameNumber != 1
		|| OutPreview.HomeTeam != TEXT("Harbor City Waves")
		|| OutPreview.AwayTeam != TEXT("Mesa Vista Sol")
		|| OutPreview.LockUnix != ExpectedLockUnix
		|| OutPreview.MinimumStake != 10
		|| OutPreview.MaximumStake != 100
		|| OutPreview.StakeIncrement != 10
		|| HouseEdgeBps != 0
		|| PayoutFormula != TEXT("floor(stake*100000000/win_probability_e8)")
		|| Selections->Num() != 2)
	{
		OutPreview = {};
		OutError = TEXT("Match Winner preview offer is stale or tampered.");
		return false;
	}

	const TArray<FString> SelectionFields = {TEXT("team"), TEXT("win_probability_e8"), TEXT("decimal_odds_e4")};
	for (const TSharedPtr<FJsonValue>& Value : *Selections)
	{
		const TSharedPtr<FJsonObject> Selection = Value->AsObject();
		FOddsWellMatchWinnerSelectionPreview PreviewSelection;
		if (!HasExactFields(Selection, SelectionFields)
			|| !Selection->TryGetStringField(TEXT("team"), PreviewSelection.Team)
			|| !ReadInt64(Selection, TEXT("win_probability_e8"), PreviewSelection.WinProbabilityE8)
			|| !ReadInt64(Selection, TEXT("decimal_odds_e4"), PreviewSelection.DecimalOddsE4)
			|| PreviewSelection.WinProbabilityE8 <= 0
			|| PreviewSelection.WinProbabilityE8 >= ProbabilityScale
			|| PreviewSelection.DecimalOddsE4 != ProbabilityScale * OddsDisplayScale / PreviewSelection.WinProbabilityE8)
		{
			OutPreview = {};
			OutError = TEXT("Match Winner preview selection is malformed or tampered.");
			return false;
		}
		PreviewSelection.MinimumStakeGrossReturn = OutPreview.MinimumStake * ProbabilityScale / PreviewSelection.WinProbabilityE8;
		PreviewSelection.MaximumStakeGrossReturn = OutPreview.MaximumStake * ProbabilityScale / PreviewSelection.WinProbabilityE8;
		OutPreview.Selections.Add(MoveTemp(PreviewSelection));
	}
	if (OutPreview.Selections[0].Team != OutPreview.HomeTeam
		|| OutPreview.Selections[0].WinProbabilityE8 != 57586693
		|| OutPreview.Selections[1].Team != OutPreview.AwayTeam
		|| OutPreview.Selections[1].WinProbabilityE8 != 42413307
		|| OutPreview.Selections[0].WinProbabilityE8 + OutPreview.Selections[1].WinProbabilityE8 != ProbabilityScale)
	{
		OutPreview = {};
		OutError = TEXT("Match Winner preview selections do not match the exact verified offer.");
		return false;
	}

	TSharedPtr<FJsonObject> GameOne;
	for (const TSharedPtr<FJsonValue>& Value : *Games)
	{
		const TSharedPtr<FJsonObject> Game = Value->AsObject();
		int32 GameNumber = 0;
		if (ReadInt(Game, TEXT("number"), GameNumber) && GameNumber == 1)
		{
			GameOne = Game;
			break;
		}
	}
	FString GameHome;
	FString GameAway;
	FString GameCommitment;
	const TSharedPtr<FJsonObject>* Predictions = nullptr;
	double PublicProbability = 0.0;
	if (!GameOne
		|| !GameOne->TryGetStringField(TEXT("home"), GameHome)
		|| !GameOne->TryGetStringField(TEXT("away"), GameAway)
		|| !GameOne->TryGetStringField(TEXT("prediction_commitment_sha256"), GameCommitment)
		|| !GameOne->TryGetObjectField(TEXT("predictions"), Predictions)
		|| !(*Predictions)->TryGetNumberField(TEXT("public_elo_rotation"), PublicProbability)
		|| GameHome != OutPreview.HomeTeam
		|| GameAway != OutPreview.AwayTeam
		|| GameCommitment != OutPreview.SourceCommitmentSha256
		|| FMath::RoundToInt64(PublicProbability * ProbabilityScale) != OutPreview.Selections[0].WinProbabilityE8)
	{
		OutPreview = {};
		OutError = TEXT("Match Winner preview does not match public Season 1 Game 1 evidence.");
		return false;
	}
	OutError.Reset();
	return true;
}
}

bool LoadOddsWellPublicLeagueSnapshot(FOddsWellPublicLeagueSnapshot& OutSnapshot, FString& OutError)
{
	OutSnapshot = {};
	TSharedPtr<FJsonObject> Root;
	if (!LoadPublicLeagueRoot(Root, OutError))
	{
		return false;
	}
	FString Schema;
	bool bPublicOnly = false;
	const TSharedPtr<FJsonObject>* Season = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Standings = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Teams = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* Games = nullptr;
	const TArray<TSharedPtr<FJsonValue>>* AthleteStories = nullptr;
	if (!Root->TryGetStringField(TEXT("schema"), Schema)
		|| Schema != TEXT("oddswell-public-league-v1")
		|| !Root->TryGetBoolField(TEXT("public_only"), bPublicOnly)
		|| !bPublicOnly
		|| !Root->TryGetStringField(TEXT("boundary"), OutSnapshot.Boundary)
		|| !Root->TryGetObjectField(TEXT("season"), Season)
		|| !Root->TryGetArrayField(TEXT("standings"), Standings)
		|| !Root->TryGetArrayField(TEXT("teams"), Teams)
		|| !Root->TryGetArrayField(TEXT("games"), Games)
		|| !Root->TryGetArrayField(TEXT("athlete_stories"), AthleteStories)
		|| !ReadInt(*Season, TEXT("number"), OutSnapshot.SeasonNumber)
		|| !(*Season)->TryGetStringField(TEXT("status"), OutSnapshot.SeasonStatus))
	{
		OutError = TEXT("Public league snapshot schema is incomplete or private.");
		return false;
	}

	const TArray<FString> StoryFields = {
		TEXT("name"), TEXT("team"), TEXT("talent_tier"), TEXT("specialty"), TEXT("consistency"),
		TEXT("offensive_role"), TEXT("form"), TEXT("season_points_per_game"),
		TEXT("recent_points_per_game"), TEXT("recent_minutes_per_game"), TEXT("available"),
		TEXT("life_choice"), TEXT("life_game"), TEXT("life_brain_version")};
	TMap<FString, TSharedPtr<FJsonObject>> StoriesByAthlete;
	for (const TSharedPtr<FJsonValue>& Value : *AthleteStories)
	{
		const TSharedPtr<FJsonObject> Story = Value->AsObject();
		FString Name;
		if (!HasExactFields(Story, StoryFields)
			|| !Story->TryGetStringField(TEXT("name"), Name)
			|| Name.IsEmpty()
			|| StoriesByAthlete.Contains(Name))
		{
			OutError = TEXT("Public league snapshot has invalid athlete-story evidence.");
			return false;
		}
		StoriesByAthlete.Add(Name, Story);
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
			const TSharedPtr<FJsonObject>* Story = nullptr;
			FString StoryName;
			FString StoryTeam;
			bool bStoryAvailable = false;
			if (!Player.IsValid()
				|| !Player->TryGetStringField(TEXT("name"), Athlete.Name)
				|| !ReadInt(Player, TEXT("overall"), Athlete.Overall)
				|| !ReadInt(Player, TEXT("shooting"), Athlete.Shooting)
				|| !ReadInt(Player, TEXT("passing"), Athlete.Passing)
				|| !ReadInt(Player, TEXT("defense"), Athlete.Defense)
				|| !ReadInt(Player, TEXT("rebounding"), Athlete.Rebounding)
				|| !ReadInt(Player, TEXT("stamina"), Athlete.Stamina)
				|| !Player->TryGetBoolField(TEXT("available"), Athlete.bAvailable)
				|| !(Story = StoriesByAthlete.Find(Athlete.Name))
				|| !(*Story)->TryGetStringField(TEXT("name"), StoryName)
				|| !(*Story)->TryGetStringField(TEXT("team"), StoryTeam)
				|| !(*Story)->TryGetStringField(TEXT("talent_tier"), Athlete.TalentTier)
				|| !(*Story)->TryGetStringField(TEXT("specialty"), Athlete.Specialty)
				|| !(*Story)->TryGetStringField(TEXT("consistency"), Athlete.Consistency)
				|| !(*Story)->TryGetStringField(TEXT("offensive_role"), Athlete.OffensiveRole)
				|| !(*Story)->TryGetStringField(TEXT("form"), Athlete.Form)
				|| !(*Story)->TryGetNumberField(TEXT("season_points_per_game"), Athlete.SeasonPointsPerGame)
				|| !(*Story)->TryGetNumberField(TEXT("recent_points_per_game"), Athlete.RecentPointsPerGame)
				|| !(*Story)->TryGetNumberField(TEXT("recent_minutes_per_game"), Athlete.RecentMinutesPerGame)
				|| !(*Story)->TryGetBoolField(TEXT("available"), bStoryAvailable)
				|| !(*Story)->TryGetStringField(TEXT("life_choice"), Athlete.LifeChoice)
				|| !ReadInt(*Story, TEXT("life_game"), Athlete.LifeGame)
				|| !(*Story)->TryGetStringField(TEXT("life_brain_version"), Athlete.LifeBrainVersion)
				|| StoryName != Athlete.Name
				|| StoryTeam != Team.Name
				|| bStoryAvailable != Athlete.bAvailable
				|| Athlete.Overall < 0 || Athlete.Overall > 100
				|| Athlete.Shooting < 0 || Athlete.Shooting > 100
				|| Athlete.Passing < 0 || Athlete.Passing > 100
				|| Athlete.Defense < 0 || Athlete.Defense > 100
				|| Athlete.Rebounding < 0 || Athlete.Rebounding > 100
				|| Athlete.Stamina < 0 || Athlete.Stamina > 100
				|| !FMath::IsFinite(Athlete.SeasonPointsPerGame) || Athlete.SeasonPointsPerGame < 0.0
				|| !FMath::IsFinite(Athlete.RecentPointsPerGame) || Athlete.RecentPointsPerGame < 0.0
				|| !FMath::IsFinite(Athlete.RecentMinutesPerGame) || Athlete.RecentMinutesPerGame < 0.0
				|| !TArray<FString>{TEXT("Star"), TEXT("Featured starter"), TEXT("Core starter"), TEXT("Rotation contributor"), TEXT("Developmental")}.Contains(Athlete.TalentTier)
				|| !TArray<FString>{TEXT("elite"), TEXT("steady"), TEXT("normal"), TEXT("volatile")}.Contains(Athlete.Consistency)
				|| !TArray<FString>{TEXT("featured"), TEXT("standard"), TEXT("low")}.Contains(Athlete.OffensiveRole)
				|| !TArray<FString>{TEXT("RISING"), TEXT("STEADY"), TEXT("COOLING")}.Contains(Athlete.Form)
				|| !TArray<FString>{TEXT("TRAIN"), TEXT("REST"), TEXT("RECOVER"), TEXT("SOCIALIZE")}.Contains(Athlete.LifeChoice)
				|| Athlete.LifeGame != 20
				|| Athlete.LifeBrainVersion != TEXT("athlete-life-v4"))
			{
				OutError = TEXT("Public league snapshot has an invalid athlete or public story.");
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
		|| StoriesByAthlete.Num() != AthleteCount
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
	return 1 + Snapshot.Teams.Num() + GetAthleteCount(Snapshot)
		+ FMath::DivideAndRoundUp(Snapshot.Games.Num(), GamesPerPage);
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
	else if (PageIndex < 1 + Snapshot.Teams.Num() + GetAthleteCount(Snapshot))
	{
		const FOddsWellPublicTeam* Team = nullptr;
		const FOddsWellPublicAthlete* Athlete = FindAthlete(
			Snapshot,
			PageIndex - 1 - Snapshot.Teams.Num(),
			Team);
		if (!Athlete || !Team)
		{
			return TEXT("ATHLETE STORY UNAVAILABLE");
		}
		const FString Explanation = BuildPublicAthleteExplanation(*Athlete);
		Text += FString::Printf(
			TEXT("ATHLETE STORY | PUBLIC ARCHIVE\n")
			TEXT("%s | %s\n\n")
			TEXT("TALENT: %s | OVR %d | CONSISTENCY %s\n")
			TEXT("SPECIALTY: %s | OFFENSIVE ROLE: %s\n")
			TEXT("RATINGS: SHO %d | PAS %d | DEF %d | REB %d | STA %d\n\n")
			TEXT("FORM: %s | SEASON %.2f PPG | RECENT %.2f PPG\n")
			TEXT("STATUS: %s | PUBLIC WORKLOAD: %.2f MPG\n")
			TEXT("LIFE BRAIN: %s | GAME %d: %s\n\n")
			TEXT("%s\n\n")
			TEXT("PRIVATE: fatigue, recovery, injury details, RNG, and resolver state are withheld."),
			*Athlete->Name,
			*Team->Name,
			*Athlete->TalentTier.ToUpper(),
			Athlete->Overall,
			*Athlete->Consistency.ToUpper(),
			*Athlete->Specialty.ToUpper(),
			*Athlete->OffensiveRole.ToUpper(),
			Athlete->Shooting,
			Athlete->Passing,
			Athlete->Defense,
			Athlete->Rebounding,
			Athlete->Stamina,
			*Athlete->Form,
			Athlete->SeasonPointsPerGame,
			Athlete->RecentPointsPerGame,
			Athlete->bAvailable ? TEXT("AVAILABLE") : TEXT("OUT"),
			Athlete->RecentMinutesPerGame,
			*Athlete->LifeBrainVersion,
			Athlete->LifeGame,
			*Athlete->LifeChoice,
			*Explanation);
	}
	else
	{
		const int32 SchedulePage = PageIndex - 1 - Snapshot.Teams.Num() - GetAthleteCount(Snapshot);
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

bool LoadOddsWellMatchWinnerOfferPreview(FOddsWellMatchWinnerOfferPreview& OutPreview, FString& OutError)
{
	TSharedPtr<FJsonObject> Root;
	if (!LoadPublicLeagueRoot(Root, OutError))
	{
		OutPreview = {};
		return false;
	}
	return ValidateMatchWinnerOffer(Root, OutPreview, OutError);
}

FString BuildOddsWellMatchWinnerOfferPreview(const FOddsWellMatchWinnerOfferPreview& Preview)
{
	if (Preview.Selections.Num() != 2)
	{
		return TEXT("MATCH WINNER PREVIEW UNAVAILABLE");
	}
	const FOddsWellMatchWinnerSelectionPreview& Home = Preview.Selections[0];
	const FOddsWellMatchWinnerSelectionPreview& Away = Preview.Selections[1];
	return FString::Printf(
		TEXT("SPORTSBOOK | READ-ONLY MATCH WINNER PREVIEW\n")
		TEXT("SEASON %d GAME %d | %s vs %s\n")
		TEXT("%s  %.6f%% | %.4fx | 10 -> %lld | 100 -> %lld\n")
		TEXT("%s  %.6f%% | %.4fx | 10 -> %lld | 100 -> %lld\n")
		TEXT("STAKE RULE: 10-100 ODDS BUCKS | INCREMENTS OF 10\n")
		TEXT("LOCK: GAME START | UNIX %lld\n")
		TEXT("OFFER ID: %s\n")
		TEXT("SOURCE: %s | %s | %s\n")
		TEXT("COMMITMENT: %s\n")
		TEXT("READ ONLY - NO WAGER OR LEDGER CHANGE\n[E] CLOSE"),
		Preview.SeasonNumber,
		Preview.GameNumber,
		*Preview.AwayTeam,
		*Preview.HomeTeam,
		*Home.Team,
		static_cast<double>(Home.WinProbabilityE8) / 1000000.0,
		static_cast<double>(Home.DecimalOddsE4) / OddsDisplayScale,
		Home.MinimumStakeGrossReturn,
		Home.MaximumStakeGrossReturn,
		*Away.Team,
		static_cast<double>(Away.WinProbabilityE8) / 1000000.0,
		static_cast<double>(Away.DecimalOddsE4) / OddsDisplayScale,
		Away.MinimumStakeGrossReturn,
		Away.MaximumStakeGrossReturn,
		Preview.LockUnix,
		*Preview.OfferId,
		*Preview.OfferVersion,
		*Preview.SourcePredictionVersion,
		*Preview.SourceSnapshotVersion,
		*Preview.SourceCommitmentSha256);
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
	TestEqual(TEXT("Nineteen readable pages"), GetOddsWellPublicLeaguePageCount(Snapshot), 19);
	TestTrue(TEXT("Standings page names Harbor City"), BuildOddsWellPublicLeaguePage(Snapshot, 0).Contains(TEXT("Harbor City Waves")));
	TestTrue(TEXT("Roster exposes availability"), BuildOddsWellPublicLeaguePage(Snapshot, 2).Contains(TEXT("OUT")));
	const FString JalenStory = BuildOddsWellPublicLeaguePage(Snapshot, 3);
	TestTrue(TEXT("Athlete story exposes durable specialty"), JalenStory.Contains(TEXT("SCORING CREATOR")));
	TestTrue(TEXT("Athlete story exposes public form"), JalenStory.Contains(TEXT("FORM: COOLING")));
	TestTrue(TEXT("Athlete story exposes the bounded current choice"), JalenStory.Contains(TEXT("GAME 20: REST")));
	TestTrue(TEXT("Athlete story explains durable public baseline"), JalenStory.Contains(TEXT("BASELINE: CORE STARTER / SCORING CREATOR; FEATURED role, STEADY consistency, 43.10 public MPG.")));
	TestTrue(TEXT("Athlete story explains recent scoring difference"), JalenStory.Contains(TEXT("RECENT: 20.20 PPG is 3.30 below season 23.50; archive label COOLING.")));
	TestTrue(TEXT("Athlete story does not claim the life choice caused performance"), JalenStory.Contains(TEXT("Game 20 REST is recorded context, not a proven cause.")));
	TestTrue(TEXT("Athlete story keeps private state hidden"), JalenStory.Contains(TEXT("PRIVATE: fatigue, recovery, injury details, RNG, and resolver state are withheld.")));
	const FString CalStory = BuildOddsWellPublicLeaguePage(Snapshot, 13);
	TestTrue(TEXT("Unavailable athlete avoids an invented cause"), CalStory.Contains(TEXT("STATUS: OUT; the archive does not publish a cause.")));
	TestTrue(TEXT("Roman athlete story remains available"), BuildOddsWellPublicLeaguePage(Snapshot, 12).Contains(TEXT("Roman Voss")));
	const FString MateoStory = BuildOddsWellPublicLeaguePage(Snapshot, 14);
	TestTrue(TEXT("Last athlete story exposes Mateo"), MateoStory.Contains(TEXT("Mateo Cruz")));
	TestTrue(TEXT("Rising athlete explanation uses the public delta"), MateoStory.Contains(TEXT("RECENT: 14.40 PPG is 3.05 above season 11.35; archive label RISING.")));
	TestTrue(TEXT("History exposes the final game"), BuildOddsWellPublicLeaguePage(Snapshot, 18).Contains(TEXT("G20")));

	FOddsWellMatchWinnerOfferPreview Offer;
	TestTrue(TEXT("Exact public Match Winner offer loads"), LoadOddsWellMatchWinnerOfferPreview(Offer, Error));
	TestEqual(TEXT("Offer identity is exact"), Offer.OfferId, ExpectedOfferId);
	TestEqual(TEXT("Offer contains two selections"), Offer.Selections.Num(), 2);
	TestEqual(TEXT("Minimum Harbor return is exact"), Offer.Selections[0].MinimumStakeGrossReturn, int64{17});
	TestEqual(TEXT("Maximum Mesa return is exact"), Offer.Selections[1].MaximumStakeGrossReturn, int64{235});
	const FString OfferText = BuildOddsWellMatchWinnerOfferPreview(Offer);
	TestTrue(TEXT("Preview identifies read-only behavior"), OfferText.Contains(TEXT("READ ONLY - NO WAGER OR LEDGER CHANGE")));
	TestTrue(TEXT("Preview exposes the full offer ID"), OfferText.Contains(ExpectedOfferId));

	TSharedPtr<FJsonObject> Root;
	TestTrue(TEXT("Offer fixture reopens for fail-closed checks"), LoadPublicLeagueRoot(Root, Error));
	const TSharedPtr<FJsonObject>* MutableOffer = nullptr;
	Root->TryGetObjectField(TEXT("match_winner_offer"), MutableOffer);
	(*MutableOffer)->SetStringField(TEXT("offer_version"), TEXT("basketball-match-winner-odds-v0"));
	TestFalse(TEXT("Stale offer version fails closed"), ValidateMatchWinnerOffer(Root, Offer, Error));
	TestEqual(TEXT("Stale offer exposes no selections"), Offer.Selections.Num(), 0);

	TestTrue(TEXT("Offer fixture reopens for tamper check"), LoadPublicLeagueRoot(Root, Error));
	Root->TryGetObjectField(TEXT("match_winner_offer"), MutableOffer);
	const TArray<TSharedPtr<FJsonValue>>* MutableSelections = nullptr;
	(*MutableOffer)->TryGetArrayField(TEXT("selections"), MutableSelections);
	(*MutableSelections)[0]->AsObject()->SetNumberField(TEXT("win_probability_e8"), 57586694);
	TestFalse(TEXT("Tampered probability fails closed"), ValidateMatchWinnerOffer(Root, Offer, Error));

	TestTrue(TEXT("Offer fixture reopens for hidden-field check"), LoadPublicLeagueRoot(Root, Error));
	Root->TryGetObjectField(TEXT("match_winner_offer"), MutableOffer);
	(*MutableOffer)->SetNumberField(TEXT("fatigue"), 1);
	TestFalse(TEXT("Hidden offer field fails closed"), ValidateMatchWinnerOffer(Root, Offer, Error));

	TestTrue(TEXT("Offer fixture reopens for malformed check"), LoadPublicLeagueRoot(Root, Error));
	Root->TryGetObjectField(TEXT("match_winner_offer"), MutableOffer);
	(*MutableOffer)->RemoveField(TEXT("selections"));
	TestFalse(TEXT("Malformed offer fails closed"), ValidateMatchWinnerOffer(Root, Offer, Error));
	return true;
}
#endif
