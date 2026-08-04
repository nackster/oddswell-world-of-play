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
	return FString::Printf(
		TEXT("=== READING GUIDE | MEANS / DOES NOT MEAN ===\n")
		TEXT("ABILITY | MEANS: %s + PUBLISHED RATINGS (OVR %d) = LONG-TERM ABILITY. | DOES NOT MEAN: ONE RESULT.\n")
		TEXT("BASELINE: %s / %s; %s role, %s consistency, %.2f public MPG.\n")
		TEXT("FORM | MEANS: %s = %.2f RECENT vs %.2f SEASON PPG. | DOES NOT MEAN: PERMANENT ABILITY.\n")
		TEXT("LIFE | MEANS: G%d %s = RECORDED CONTEXT. | DOES NOT MEAN: PROOF IT CAUSED PERFORMANCE.\n")
		TEXT("OUT | MEANS: PUBLIC UNAVAILABILITY ONLY; CURRENT %s. | DOES NOT MEAN: DIAGNOSIS.\n")
		TEXT("=== END READING GUIDE ==="),
		*Athlete.TalentTier.ToUpper(),
		Athlete.Overall,
		*Athlete.TalentTier.ToUpper(),
		*Athlete.Specialty.ToUpper(),
		*Athlete.OffensiveRole.ToUpper(),
		*Athlete.Consistency.ToUpper(),
		Athlete.RecentMinutesPerGame,
		*Athlete.Form,
		Athlete.RecentPointsPerGame,
		Athlete.SeasonPointsPerGame,
		Athlete.LifeGame,
		*Athlete.LifeChoice,
		Athlete.bAvailable ? TEXT("AVAILABLE") : TEXT("OUT"));
}

#if UE_BUILD_DEVELOPMENT
enum class EOddsWellAthleteComprehensionConcept : uint8
{
	DurableAbility,
	Specialty,
	Opportunity,
	RecentForm,
	LifeContext,
	Availability,
};

struct FOddsWellAthleteComprehensionItem
{
	FString Text;
	TCHAR Expected = TEXT('?');
	EOddsWellAthleteComprehensionConcept Concept = EOddsWellAthleteComprehensionConcept::DurableAbility;
};

const FString AthleteComprehensionKey(TEXT("ABBAAB"));
const FString AthleteComprehensionFormBKey(TEXT("BABBAA"));
const FString AthleteComprehensionFormCKey(TEXT("AABBBA"));

const FString& GetAthleteComprehensionKey(const bool bUseFormB, const bool bUseFormC = false)
{
	return bUseFormC ? AthleteComprehensionFormCKey : bUseFormB ? AthleteComprehensionFormBKey : AthleteComprehensionKey;
}

bool BuildAthleteComprehensionItems(
	const FOddsWellPublicLeagueSnapshot& Snapshot,
	const bool bUseFormB,
	TArray<FOddsWellAthleteComprehensionItem>& OutItems,
	const bool bUseFormC = false)
{
	OutItems.Reset();
	if (bUseFormC)
	{
		const FOddsWellPublicTeam* MicahTeam = nullptr;
		const FOddsWellPublicTeam* KellanTeam = nullptr;
		const FOddsWellPublicTeam* AndreTeam = nullptr;
		const FOddsWellPublicTeam* NicoTeam = nullptr;
		const FOddsWellPublicTeam* CalTeam = nullptr;
		const FOddsWellPublicAthlete* Micah = FindAthlete(Snapshot, 1, MicahTeam);
		const FOddsWellPublicAthlete* Kellan = FindAthlete(Snapshot, 3, KellanTeam);
		const FOddsWellPublicAthlete* Andre = FindAthlete(Snapshot, 4, AndreTeam);
		const FOddsWellPublicAthlete* Nico = FindAthlete(Snapshot, 6, NicoTeam);
		const FOddsWellPublicAthlete* Cal = FindAthlete(Snapshot, 10, CalTeam);
		if (!Micah || !Kellan || !Andre || !Nico || !Cal
			|| !MicahTeam || !KellanTeam || !AndreTeam || !NicoTeam || !CalTeam
			|| Snapshot.Games.IsEmpty()
			|| Micah->Name != TEXT("Micah Vale") || Kellan->Name != TEXT("Kellan Shore")
			|| Andre->Name != TEXT("Andre North") || Nico->Name != TEXT("Nico Reyes")
			|| Cal->Name != TEXT("Cal Brooks")
			|| Andre->RecentPointsPerGame >= Andre->SeasonPointsPerGame
			|| Nico->LifeChoice != TEXT("REST") || Cal->bAvailable)
		{
			return false;
		}
		const FOddsWellPublicGame& RecentGame = Snapshot.Games.Last();
		OutItems = {
			{FString::Printf(TEXT("FOR %s, WHICH PUBLIC LINE IS LONG-TERM ABILITY, NOT ONE RESULT?  A %s + OVR %d  B G%d RESULT %d-%d"), *Micah->Name, *Micah->TalentTier.ToUpper(), Micah->Overall, RecentGame.Number, RecentGame.AwayScore, RecentGame.HomeScore), TEXT('A'), EOddsWellAthleteComprehensionConcept::DurableAbility},
			{FString::Printf(TEXT("WHICH FIELD SAYS WHAT %s DOES BEST?  A %s  B %s TIER"), *Kellan->Name, *Kellan->Specialty.ToUpper(), *Kellan->TalentTier.ToUpper()), TEXT('A'), EOddsWellAthleteComprehensionConcept::Specialty},
			{FString::Printf(TEXT("%s ROLE + %.2f PUBLIC MPG DESCRIBES?  A GUARANTEED %.2f PPG  B OPPORTUNITY TO CONTRIBUTE"), *Micah->OffensiveRole.ToUpper(), Micah->RecentMinutesPerGame, Micah->SeasonPointsPerGame), TEXT('B'), EOddsWellAthleteComprehensionConcept::Opportunity},
			{FString::Printf(TEXT("%s: %.2f RECENT vs %.2f SEASON + %s MEANS?  A PERMANENT ABILITY LOST  B RECENT OUTPUT BELOW SEASON"), *Andre->Name, Andre->RecentPointsPerGame, Andre->SeasonPointsPerGame, *Andre->Form), TEXT('B'), EOddsWellAthleteComprehensionConcept::RecentForm},
			{FString::Printf(TEXT("%s'S G%d %s RECORD IS?  A PROOF IT CAUSED HIS OUTPUT  B CONTEXT, NOT PROOF OF CAUSE"), *Nico->Name, Nico->LifeGame, *Nico->LifeChoice), TEXT('B'), EOddsWellAthleteComprehensionConcept::LifeContext},
			{FString::Printf(TEXT("%s OUT PUBLISHES?  A UNAVAILABLE ONLY, NOT A DIAGNOSIS  B A DIAGNOSIS"), *Cal->Name), TEXT('A'), EOddsWellAthleteComprehensionConcept::Availability},
		};
		return true;
	}
	if (bUseFormB)
	{
		const FOddsWellPublicTeam* TariqTeam = nullptr;
		const FOddsWellPublicTeam* DorianTeam = nullptr;
		const FOddsWellPublicTeam* MalikTeam = nullptr;
		const FOddsWellPublicTeam* MateoTeam = nullptr;
		const FOddsWellPublicTeam* CalTeam = nullptr;
		const FOddsWellPublicAthlete* Tariq = FindAthlete(Snapshot, 7, TariqTeam);
		const FOddsWellPublicAthlete* Dorian = FindAthlete(Snapshot, 2, DorianTeam);
		const FOddsWellPublicAthlete* Malik = FindAthlete(Snapshot, 5, MalikTeam);
		const FOddsWellPublicAthlete* Mateo = FindAthlete(Snapshot, 11, MateoTeam);
		const FOddsWellPublicAthlete* Cal = FindAthlete(Snapshot, 10, CalTeam);
		if (!Tariq || !Dorian || !Malik || !Mateo || !Cal
			|| !TariqTeam || !DorianTeam || !MalikTeam || !MateoTeam || !CalTeam
			|| Snapshot.Games.IsEmpty()
			|| Tariq->Name != TEXT("Tariq Stone") || Dorian->Name != TEXT("Dorian Pike")
			|| Malik->Name != TEXT("Malik Frost") || Mateo->Name != TEXT("Mateo Cruz")
			|| Cal->Name != TEXT("Cal Brooks") || Mateo->RecentPointsPerGame <= Mateo->SeasonPointsPerGame
			|| Malik->LifeChoice != TEXT("SOCIALIZE") || Cal->bAvailable)
		{
			return false;
		}
		const FOddsWellPublicGame& RecentGame = Snapshot.Games.Last();
		OutItems = {
			{FString::Printf(TEXT("WHICH LINE SHOULD OUTLAST ONE RESULT?  A G%d %d-%d  B %s TIER"), RecentGame.Number, RecentGame.AwayScore, RecentGame.HomeScore, *Tariq->TalentTier.ToUpper()), TEXT('B'), EOddsWellAthleteComprehensionConcept::DurableAbility},
			{FString::Printf(TEXT("WHAT DOES %s DO BEST?  A %s  B OVR %d"), *Dorian->Name, *Dorian->Specialty.ToUpper(), Dorian->Overall), TEXT('A'), EOddsWellAthleteComprehensionConcept::Specialty},
			{FString::Printf(TEXT("%s ROLE + %.2f RECENT MPG PROVIDES?  A GUARANTEED TOTAL  B A CHANCE TO CONTRIBUTE"), *Malik->OffensiveRole.ToUpper(), Malik->RecentMinutesPerGame), TEXT('B'), EOddsWellAthleteComprehensionConcept::Opportunity},
			{FString::Printf(TEXT("%s: %.2f RECENT PPG vs %.2f SEASON + %s?  A BELOW HIS SEASON RATE  B RECENT OUTPUT ABOVE IT"), *Mateo->Name, Mateo->RecentPointsPerGame, Mateo->SeasonPointsPerGame, *Mateo->Form), TEXT('B'), EOddsWellAthleteComprehensionConcept::RecentForm},
			{FString::Printf(TEXT("%s'S G%d %s RECORD SHOULD BE READ AS?  A RECORDED BACKGROUND ONLY  B PROOF IT CAUSED PERFORMANCE"), *Malik->Name, Malik->LifeGame, *Malik->LifeChoice), TEXT('A'), EOddsWellAthleteComprehensionConcept::LifeContext},
			{FString::Printf(TEXT("%s OUT PUBLICLY TELLS YOU?  A UNAVAILABLE; NO DIAGNOSIS PUBLISHED  B HIS DIAGNOSIS"), *Cal->Name), TEXT('A'), EOddsWellAthleteComprehensionConcept::Availability},
		};
		return true;
	}

	const FOddsWellPublicTeam* JalenTeam = nullptr;
	const FOddsWellPublicTeam* CalTeam = nullptr;
	const FOddsWellPublicAthlete* Jalen = FindAthlete(Snapshot, 0, JalenTeam);
	const FOddsWellPublicAthlete* Cal = FindAthlete(Snapshot, 10, CalTeam);
	if (!Jalen || !Cal || !JalenTeam || !CalTeam || Snapshot.Games.IsEmpty()
		|| Jalen->Name != TEXT("Jalen Cross") || Cal->Name != TEXT("Cal Brooks")
		|| Jalen->RecentPointsPerGame >= Jalen->SeasonPointsPerGame || Cal->bAvailable)
	{
		return false;
	}
	const FOddsWellPublicGame& RecentGame = Snapshot.Games.Last();
	OutItems = {
		{FString::Printf(TEXT("DURABLE ABILITY?  A %s  B G%d TEAM RESULT %d-%d"), *Jalen->TalentTier.ToUpper(), RecentGame.Number, RecentGame.AwayScore, RecentGame.HomeScore), TEXT('A'), EOddsWellAthleteComprehensionConcept::DurableAbility},
		{FString::Printf(TEXT("SPECIALTY FIELD?  A OVR %d  B %s"), Jalen->Overall, *Jalen->Specialty.ToUpper()), TEXT('B'), EOddsWellAthleteComprehensionConcept::Specialty},
		{FString::Printf(TEXT("%s + %.2f MPG MEANS?  A GUARANTEED POINTS  B OPPORTUNITY"), *Jalen->OffensiveRole.ToUpper(), Jalen->RecentMinutesPerGame), TEXT('B'), EOddsWellAthleteComprehensionConcept::Opportunity},
		{FString::Printf(TEXT("%.2f RECENT vs %.2f SEASON + %s?  A BELOW BASELINE  B ABOVE"), Jalen->RecentPointsPerGame, Jalen->SeasonPointsPerGame, *Jalen->Form), TEXT('A'), EOddsWellAthleteComprehensionConcept::RecentForm},
		{FString::Printf(TEXT("G%d %s MEANS?  A RECORDED CONTEXT  B PROVEN CAUSE"), Jalen->LifeGame, *Jalen->LifeChoice), TEXT('A'), EOddsWellAthleteComprehensionConcept::LifeContext},
		{FString::Printf(TEXT("%s OUT MEANS?  A DIAGNOSIS  B PUBLIC UNAVAILABILITY ONLY"), *Cal->Name), TEXT('B'), EOddsWellAthleteComprehensionConcept::Availability},
	};
	return true;
}

bool HasAthleteComprehensionKeyParity(
	const TArray<FOddsWellAthleteComprehensionItem>& Items,
	const bool bUseFormB,
	const bool bUseFormC = false)
{
	const FString& Key = GetAthleteComprehensionKey(bUseFormB, bUseFormC);
	if (Items.Num() != Key.Len())
	{
		return false;
	}
	for (int32 Index = 0; Index < Items.Num(); ++Index)
	{
		if (Items[Index].Expected != Key[Index])
		{
			return false;
		}
	}
	return true;
}
#endif

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

#if UE_BUILD_DEVELOPMENT
FString BuildOddsWellAthleteComprehensionCheck(const FOddsWellPublicLeagueSnapshot& Snapshot)
{
	TArray<FOddsWellAthleteComprehensionItem> Items;
	if (!BuildAthleteComprehensionItems(Snapshot, false, Items))
	{
		return TEXT("DEVELOPMENT ATHLETE COMPREHENSION CHECK UNAVAILABLE");
	}
	FString Text = TEXT("DEVELOPMENT QA | ATHLETE STORY COMPREHENSION | FIXED 6 ITEMS\nINSTRUMENT VALIDATION ONLY - NOT HUMAN COMPREHENSION\n\n");
	for (int32 Index = 0; Index < Items.Num(); ++Index)
	{
		Text += FString::Printf(TEXT("%d %s  | EXPECT %c\n"), Index + 1, *Items[Index].Text, Items[Index].Expected);
	}
	return Text + TEXT("\nEXPECTED KEY: A B B A A B | PUBLIC FIXTURE ONLY | NO HIDDEN VALUES USED");
}

int32 GetOddsWellAthleteComprehensionItemCount(const bool bUseFormB, const bool bUseFormC)
{
	return GetAthleteComprehensionKey(bUseFormB, bUseFormC).Len();
}

bool SubmitOddsWellAthleteComprehensionAnswer(
	const FOddsWellPublicLeagueSnapshot& Snapshot,
	FString& Answers,
	const TCHAR Answer,
	FString& OutError,
	const bool bUseFormB,
	const bool bUseFormC)
{
	TArray<FOddsWellAthleteComprehensionItem> Items;
	if (!BuildAthleteComprehensionItems(Snapshot, bUseFormB, Items, bUseFormC)
		|| Items.Num() != GetAthleteComprehensionKey(bUseFormB, bUseFormC).Len())
	{
		OutError = TEXT("The fixed public comprehension fixture is unavailable.");
		return false;
	}
	if (Answer != TEXT('A') && Answer != TEXT('B'))
	{
		OutError = TEXT("Answer must be A or B.");
		return false;
	}
	if (Answers.Len() >= Items.Num())
	{
		OutError = TEXT("The six-item session is already complete.");
		return false;
	}
	Answers.AppendChar(Answer);
	OutError.Reset();
	return true;
}

int32 ScoreOddsWellAthleteComprehensionAnswers(const FString& Answers, const bool bUseFormB, const bool bUseFormC)
{
	const FString& Key = GetAthleteComprehensionKey(bUseFormB, bUseFormC);
	if (Answers.Len() != Key.Len())
	{
		return INDEX_NONE;
	}
	int32 Score = 0;
	for (int32 Index = 0; Index < Answers.Len(); ++Index)
	{
		if (Answers[Index] != TEXT('A') && Answers[Index] != TEXT('B'))
		{
			return INDEX_NONE;
		}
		Score += Answers[Index] == Key[Index] ? 1 : 0;
	}
	return Score;
}

FString BuildOddsWellAthleteComprehensionSessionPage(
	const FOddsWellPublicLeagueSnapshot& Snapshot,
	const FString& Answers,
	const bool bUseFormB,
	const bool bUseFormC)
{
	TArray<FOddsWellAthleteComprehensionItem> Items;
	if (!BuildAthleteComprehensionItems(Snapshot, bUseFormB, Items, bUseFormC) || Answers.Len() > Items.Num())
	{
		return TEXT("DEVELOPMENT PLAYER-BLIND COMPREHENSION SESSION UNAVAILABLE");
	}
	if (Answers.Len() == Items.Num())
	{
		const int32 Score = ScoreOddsWellAthleteComprehensionAnswers(Answers, bUseFormB, bUseFormC);
		return Score == INDEX_NONE
			? TEXT("DEVELOPMENT PLAYER-BLIND COMPREHENSION SESSION UNAVAILABLE")
			: FString::Printf(
				TEXT("DEVELOPMENT QA | PLAYER-BLIND ATHLETE STORY SESSION\nSESSION COMPLETE\n\nSUBMITTED: %s\nSCORE: %d/6\n\nPUBLIC FIXTURE ONLY | NO HIDDEN VALUES USED\nMECHANISM VALIDATION ONLY - HUMAN COMPREHENSION UNPROVEN"),
				*Answers,
				Score);
	}
	for (const TCHAR Answer : Answers)
	{
		if (Answer != TEXT('A') && Answer != TEXT('B'))
		{
			return TEXT("DEVELOPMENT PLAYER-BLIND COMPREHENSION SESSION UNAVAILABLE");
		}
	}
	return FString::Printf(
		TEXT("DEVELOPMENT QA | PLAYER-BLIND ATHLETE STORY SESSION\n")
		TEXT("ITEM %d/6\n\n%s\n\nPRESS A OR B ONCE\nNO CORRECTNESS FEEDBACK UNTIL ALL SIX ITEMS\nPUBLIC FIXTURE ONLY | NO HIDDEN VALUES USED"),
		Answers.Len() + 1,
		*Items[Answers.Len()].Text);
}
#endif

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
	TestTrue(TEXT("Athlete story keeps private state hidden"), JalenStory.Contains(TEXT("PRIVATE: fatigue, recovery, injury details, RNG, and resolver state are withheld.")));
	int32 AthletePage = 3;
	int32 GuidedAthletes = 0;
	for (const FOddsWellPublicTeam& Team : Snapshot.Teams)
	{
		for (const FOddsWellPublicAthlete& Athlete : Team.Athletes)
		{
			const FString Story = BuildOddsWellPublicLeaguePage(Snapshot, AthletePage++);
			const FString Guide = BuildPublicAthleteExplanation(Athlete);
			const FString Label = FString::Printf(TEXT("%s reading guide"), *Athlete.Name);
			TArray<FString> GuideSections;
			Story.ParseIntoArray(GuideSections, TEXT("=== READING GUIDE | MEANS / DOES NOT MEAN ==="), false);
			TestEqual(*FString::Printf(TEXT("%s appears exactly once"), *Label), GuideSections.Num() - 1, 1);
			TestTrue(
				*FString::Printf(TEXT("%s explains exact durable ability"), *Label),
				Guide.Contains(FString::Printf(
					TEXT("ABILITY | MEANS: %s + PUBLISHED RATINGS (OVR %d) = LONG-TERM ABILITY. | DOES NOT MEAN: ONE RESULT."),
					*Athlete.TalentTier.ToUpper(),
					Athlete.Overall)));
			TestTrue(
				*FString::Printf(TEXT("%s preserves specialty and opportunity"), *Label),
				Guide.Contains(FString::Printf(
					TEXT("BASELINE: %s / %s; %s role, %s consistency, %.2f public MPG."),
					*Athlete.TalentTier.ToUpper(),
					*Athlete.Specialty.ToUpper(),
					*Athlete.OffensiveRole.ToUpper(),
					*Athlete.Consistency.ToUpper(),
					Athlete.RecentMinutesPerGame))
				&& Story.Contains(FString::Printf(
					TEXT("SPECIALTY: %s | OFFENSIVE ROLE: %s"),
					*Athlete.Specialty.ToUpper(),
					*Athlete.OffensiveRole.ToUpper())));
			TestTrue(
				*FString::Printf(TEXT("%s explains exact recent form"), *Label),
				Guide.Contains(FString::Printf(
					TEXT("FORM | MEANS: %s = %.2f RECENT vs %.2f SEASON PPG. | DOES NOT MEAN: PERMANENT ABILITY."),
					*Athlete.Form,
					Athlete.RecentPointsPerGame,
					Athlete.SeasonPointsPerGame)));
			TestTrue(
				*FString::Printf(TEXT("%s keeps life context non-causal"), *Label),
				Guide.Contains(FString::Printf(
					TEXT("LIFE | MEANS: G%d %s = RECORDED CONTEXT. | DOES NOT MEAN: PROOF IT CAUSED PERFORMANCE."),
					Athlete.LifeGame,
					*Athlete.LifeChoice)));
			TestTrue(
				*FString::Printf(TEXT("%s keeps OUT non-diagnostic"), *Label),
				Guide.Contains(FString::Printf(
					TEXT("OUT | MEANS: PUBLIC UNAVAILABILITY ONLY; CURRENT %s. | DOES NOT MEAN: DIAGNOSIS."),
					Athlete.bAvailable ? TEXT("AVAILABLE") : TEXT("OUT"))));
			TestFalse(
				*FString::Printf(TEXT("%s guide excludes hidden fields"), *Label),
				Guide.Contains(TEXT("FATIGUE"))
				|| Guide.Contains(TEXT("RECOVERY"))
				|| Guide.Contains(TEXT("INJURY"))
				|| Guide.Contains(TEXT("RNG"))
				|| Guide.Contains(TEXT("RESOLVER")));
			++GuidedAthletes;
		}
	}
	TestEqual(TEXT("All twelve athlete pages have the four-concept guide"), GuidedAthletes, 12);
	const FString CalStory = BuildOddsWellPublicLeaguePage(Snapshot, 13);
	TestTrue(TEXT("Unavailable athlete avoids an invented diagnosis"), CalStory.Contains(TEXT("CURRENT OUT. | DOES NOT MEAN: DIAGNOSIS.")));
	TestTrue(TEXT("Roman athlete story remains available"), BuildOddsWellPublicLeaguePage(Snapshot, 12).Contains(TEXT("Roman Voss")));
	const FString MateoStory = BuildOddsWellPublicLeaguePage(Snapshot, 14);
	TestTrue(TEXT("Last athlete story exposes Mateo"), MateoStory.Contains(TEXT("Mateo Cruz")));
	TestTrue(TEXT("Rising athlete guide uses exact public values"), MateoStory.Contains(TEXT("FORM | MEANS: RISING = 14.40 RECENT vs 11.35 SEASON PPG.")));
	TestTrue(TEXT("History exposes the final game"), BuildOddsWellPublicLeaguePage(Snapshot, 18).Contains(TEXT("G20")));
#if UE_BUILD_DEVELOPMENT
	const FString ComprehensionCheck = BuildOddsWellAthleteComprehensionCheck(Snapshot);
	TestTrue(TEXT("Comprehension instrument labels its six fixed items"), ComprehensionCheck.Contains(TEXT("FIXED 6 ITEMS")));
	TArray<FString> ComprehensionAnswers;
	ComprehensionCheck.ParseIntoArray(ComprehensionAnswers, TEXT("| EXPECT"));
	TestEqual(TEXT("Comprehension instrument has six expected answers"), ComprehensionAnswers.Num() - 1, 6);
	TestTrue(TEXT("Comprehension instrument distinguishes durable ability from a recent game"), ComprehensionCheck.Contains(TEXT("1 DURABLE ABILITY?  A CORE STARTER  B G20 TEAM RESULT 88-72  | EXPECT A")));
	TestTrue(TEXT("Comprehension instrument distinguishes specialty from overall quality"), ComprehensionCheck.Contains(TEXT("2 SPECIALTY FIELD?  A OVR 76  B SCORING CREATOR  | EXPECT B")));
	TestTrue(TEXT("Comprehension instrument distinguishes opportunity from guaranteed production"), ComprehensionCheck.Contains(TEXT("3 FEATURED + 43.10 MPG MEANS?  A GUARANTEED POINTS  B OPPORTUNITY  | EXPECT B")));
	TestTrue(TEXT("Comprehension instrument distinguishes recent form from season baseline"), ComprehensionCheck.Contains(TEXT("4 20.20 RECENT vs 23.50 SEASON + COOLING?  A BELOW BASELINE  B ABOVE  | EXPECT A")));
	TestTrue(TEXT("Comprehension instrument treats life choice as context"), ComprehensionCheck.Contains(TEXT("5 G20 REST MEANS?  A RECORDED CONTEXT  B PROVEN CAUSE  | EXPECT A")));
	TestTrue(TEXT("Comprehension instrument avoids diagnosis and hidden state"), ComprehensionCheck.Contains(TEXT("6 Cal Brooks OUT MEANS?  A DIAGNOSIS  B PUBLIC UNAVAILABILITY ONLY  | EXPECT B")));
	TestFalse(TEXT("Comprehension instrument contains no hidden field names"), ComprehensionCheck.Contains(TEXT("FATIGUE")) || ComprehensionCheck.Contains(TEXT("RECOVERY")) || ComprehensionCheck.Contains(TEXT("INJURY RISK")) || ComprehensionCheck.Contains(TEXT("RNG")) || ComprehensionCheck.Contains(TEXT("RESOLVER")));
	TestTrue(TEXT("Comprehension instrument does not claim human comprehension"), ComprehensionCheck.Contains(TEXT("NOT HUMAN COMPREHENSION")));
	TArray<FOddsWellAthleteComprehensionItem> SessionItems;
	TestTrue(TEXT("Blind session key matches all six instrument answers"), BuildAthleteComprehensionItems(Snapshot, false, SessionItems) && HasAthleteComprehensionKeyParity(SessionItems, false));
	TestEqual(TEXT("Blind session reuses all six instrument items"), GetOddsWellAthleteComprehensionItemCount(), 6);
	FString SessionAnswers;
	const FString FirstQuestion = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, SessionAnswers);
	TestTrue(TEXT("Blind session starts at one item"), FirstQuestion.Contains(TEXT("ITEM 1/6")) && FirstQuestion.Contains(TEXT("DURABLE ABILITY?")));
	TestFalse(TEXT("Blind session leaks no expected answer before completion"), FirstQuestion.Contains(TEXT("EXPECT")) || FirstQuestion.Contains(TEXT("KEY")) || FirstQuestion.Contains(TEXT("SCORE")) || FirstQuestion.Contains(TEXT("SUBMITTED")));
	TestFalse(TEXT("Blind session rejects a non A/B response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, SessionAnswers, TEXT('C'), Error));
	TestEqual(TEXT("Rejected blind response does not advance"), SessionAnswers, FString());
	TestTrue(TEXT("Blind session accepts first ordered response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, SessionAnswers, TEXT('A'), Error));
	const FString SecondQuestion = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, SessionAnswers);
	TestTrue(TEXT("Blind session advances exactly one item"), SecondQuestion.Contains(TEXT("ITEM 2/6")) && SecondQuestion.Contains(TEXT("SPECIALTY FIELD?")));
	TestFalse(TEXT("Blind session shows only the current item"), SecondQuestion.Contains(TEXT("DURABLE ABILITY?")) || SecondQuestion.Contains(TEXT("EXPECT")) || SecondQuestion.Contains(TEXT("KEY")));
	for (const TCHAR Answer : FString(TEXT("BBAAB")))
	{
		TestTrue(TEXT("Blind session accepts one bounded A/B response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, SessionAnswers, Answer, Error));
	}
	TestEqual(TEXT("Blind session preserves submitted order"), SessionAnswers, FString(TEXT("ABBAAB")));
	const FString CompletedSession = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, SessionAnswers);
	TestTrue(TEXT("Blind session reveals only submitted answers and score after completion"), CompletedSession.Contains(TEXT("SUBMITTED: ABBAAB")) && CompletedSession.Contains(TEXT("SCORE: 6/6")));
	TestFalse(TEXT("Completed blind session still withholds the expected key"), CompletedSession.Contains(TEXT("EXPECT")) || CompletedSession.Contains(TEXT("KEY")));
	TestFalse(TEXT("Blind session rejects a seventh response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, SessionAnswers, TEXT('A'), Error));
	TestEqual(TEXT("Rejected seventh response does not mutate answers"), SessionAnswers, FString(TEXT("ABBAAB")));
	TestEqual(TEXT("Blind session scores responses in fixed order"), ScoreOddsWellAthleteComprehensionAnswers(TEXT("BBBBBB")), 3);

	TArray<FOddsWellAthleteComprehensionItem> FormBItems;
	TestTrue(TEXT("Equivalent blind form is supported by the approved public fixture"), BuildAthleteComprehensionItems(Snapshot, true, FormBItems));
	TestEqual(TEXT("Equivalent blind form has exactly six items"), FormBItems.Num(), 6);
	TestTrue(TEXT("Equivalent blind form has key parity"), HasAthleteComprehensionKeyParity(FormBItems, true));
	const TArray<EOddsWellAthleteComprehensionConcept> ExpectedConcepts = {
		EOddsWellAthleteComprehensionConcept::DurableAbility,
		EOddsWellAthleteComprehensionConcept::Specialty,
		EOddsWellAthleteComprehensionConcept::Opportunity,
		EOddsWellAthleteComprehensionConcept::RecentForm,
		EOddsWellAthleteComprehensionConcept::LifeContext,
		EOddsWellAthleteComprehensionConcept::Availability,
	};
	for (int32 Index = 0; Index < ExpectedConcepts.Num(); ++Index)
	{
		const FString ConceptTest = FString::Printf(TEXT("Equivalent blind item %d keeps its internal concept mapping"), Index + 1);
		TestEqual(
			*ConceptTest,
			static_cast<uint8>(FormBItems[Index].Concept),
			static_cast<uint8>(ExpectedConcepts[Index]));
		const FString WordingTest = FString::Printf(TEXT("Equivalent blind item %d uses changed wording and examples"), Index + 1);
		TestNotEqual(
			*WordingTest,
			FormBItems[Index].Text,
			SessionItems[Index].Text);
	}
	TestTrue(TEXT("Equivalent blind form uses changed public athletes"), FormBItems[0].Text.Contains(TEXT("FEATURED STARTER")) && FormBItems[1].Text.Contains(TEXT("Dorian Pike")) && FormBItems[2].Text.Contains(TEXT("24.20")) && FormBItems[3].Text.Contains(TEXT("Mateo Cruz")) && FormBItems[4].Text.Contains(TEXT("SOCIALIZE")) && FormBItems[5].Text.Contains(TEXT("Cal Brooks")));
	TestNotEqual(TEXT("Equivalent blind form cannot reuse the prior response sequence"), GetAthleteComprehensionKey(true), GetAthleteComprehensionKey(false));
	bool bDirectComplement = true;
	for (int32 Index = 0; Index < GetAthleteComprehensionKey(true).Len(); ++Index)
	{
		bDirectComplement &= GetAthleteComprehensionKey(true)[Index] != GetAthleteComprehensionKey(false)[Index];
	}
	TestFalse(TEXT("Equivalent blind response sides are not a predictable full inversion"), bDirectComplement);
	FString FormBAnswers;
	const FString FormBFirstQuestion = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, FormBAnswers, true);
	TestTrue(TEXT("Equivalent blind form starts unanswered on one item"), FormBFirstQuestion.Contains(TEXT("ITEM 1/6")) && FormBFirstQuestion.Contains(TEXT("WHICH LINE SHOULD OUTLAST ONE RESULT?")));
	TestFalse(TEXT("Equivalent blind form leaks no pre-completion evaluation data"), FormBFirstQuestion.Contains(TEXT("EXPECT")) || FormBFirstQuestion.Contains(TEXT("KEY")) || FormBFirstQuestion.Contains(TEXT("SCORE")) || FormBFirstQuestion.Contains(TEXT("SUBMITTED")) || FormBFirstQuestion.Contains(TEXT("CORRECT:")) || FormBFirstQuestion.Contains(TEXT("INCORRECT")) || FormBFirstQuestion.Contains(TEXT("CONCEPT:")));
	TestFalse(TEXT("Equivalent blind form rejects a non A/B response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, FormBAnswers, TEXT('C'), Error, true));
	for (const FOddsWellAthleteComprehensionItem& Item : FormBItems)
	{
		TestTrue(TEXT("Equivalent blind form accepts one bounded A/B response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, FormBAnswers, Item.Expected, Error, true));
	}
	const FString FormBCompletion = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, FormBAnswers, true);
	TestTrue(TEXT("Equivalent blind form completes deterministically after six responses"), FormBCompletion.Contains(TEXT("SESSION COMPLETE")) && FormBCompletion.Contains(TEXT("SCORE: 6/6")));
	TestEqual(TEXT("Equivalent blind form completion is deterministic"), BuildOddsWellAthleteComprehensionSessionPage(Snapshot, FormBAnswers, true), FormBCompletion);
	TestFalse(TEXT("Equivalent blind form rejects a seventh response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, FormBAnswers, TEXT('A'), Error, true));

	TArray<FOddsWellAthleteComprehensionItem> FormCItems;
	TestTrue(TEXT("Fresh post-clarification form uses the approved public fixture"), BuildAthleteComprehensionItems(Snapshot, false, FormCItems, true));
	TestEqual(TEXT("Fresh post-clarification form has exactly six items"), FormCItems.Num(), 6);
	TestTrue(TEXT("Fresh post-clarification form has key parity"), HasAthleteComprehensionKeyParity(FormCItems, false, true));
	TestEqual(TEXT("Retired original response sequence is unchanged"), GetAthleteComprehensionKey(false), FString(TEXT("ABBAAB")));
	TestEqual(TEXT("Retired equivalent response sequence is unchanged"), GetAthleteComprehensionKey(true), FString(TEXT("BABBAA")));
	for (int32 Index = 0; Index < ExpectedConcepts.Num(); ++Index)
	{
		const FString ConceptTest = FString::Printf(TEXT("Fresh blind item %d keeps one exact concept mapping"), Index + 1);
		TestEqual(
			*ConceptTest,
			static_cast<uint8>(FormCItems[Index].Concept),
			static_cast<uint8>(ExpectedConcepts[Index]));
		const FString FreshWordingTest = FString::Printf(TEXT("Fresh blind item %d differs from both retired forms"), Index + 1);
		TestTrue(
			*FreshWordingTest,
			FormCItems[Index].Text != SessionItems[Index].Text
			&& FormCItems[Index].Text != FormBItems[Index].Text);
		const FString PublicOnlyTest = FString::Printf(TEXT("Fresh blind item %d contains public claims only"), Index + 1);
		TestFalse(
			*PublicOnlyTest,
			FormCItems[Index].Text.Contains(TEXT("FATIGUE"))
			|| FormCItems[Index].Text.Contains(TEXT("RECOVERY"))
			|| FormCItems[Index].Text.Contains(TEXT("INJURY"))
			|| FormCItems[Index].Text.Contains(TEXT("RNG"))
			|| FormCItems[Index].Text.Contains(TEXT("RESOLVER")));
	}
	TestTrue(
		TEXT("Fresh blind form materially changes public examples"),
		FormCItems[0].Text.Contains(TEXT("Micah Vale"))
		&& FormCItems[1].Text.Contains(TEXT("Kellan Shore"))
		&& FormCItems[3].Text.Contains(TEXT("Andre North"))
		&& FormCItems[4].Text.Contains(TEXT("Nico Reyes")));
	TestNotEqual(TEXT("Fresh response sequence differs from original"), GetAthleteComprehensionKey(false, true), GetAthleteComprehensionKey(false));
	TestNotEqual(TEXT("Fresh response sequence differs from equivalent"), GetAthleteComprehensionKey(false, true), GetAthleteComprehensionKey(true));
	bool bFreshComplementsOriginal = true;
	bool bFreshComplementsEquivalent = true;
	for (int32 Index = 0; Index < GetAthleteComprehensionKey(false, true).Len(); ++Index)
	{
		bFreshComplementsOriginal &= GetAthleteComprehensionKey(false, true)[Index] != GetAthleteComprehensionKey(false)[Index];
		bFreshComplementsEquivalent &= GetAthleteComprehensionKey(false, true)[Index] != GetAthleteComprehensionKey(true)[Index];
	}
	TestFalse(TEXT("Fresh response sides are not a full inversion of original"), bFreshComplementsOriginal);
	TestFalse(TEXT("Fresh response sides are not a full inversion of equivalent"), bFreshComplementsEquivalent);
	FString FormCAnswers;
	const FString FormCFirstQuestion = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, FormCAnswers, false, true);
	TestTrue(TEXT("Fresh blind form starts unanswered on one item"), FormCFirstQuestion.Contains(TEXT("ITEM 1/6")) && FormCFirstQuestion.Contains(FormCItems[0].Text));
	TestFalse(TEXT("Fresh blind form leaks no pre-completion evaluation data"), FormCFirstQuestion.Contains(TEXT("EXPECT")) || FormCFirstQuestion.Contains(TEXT("KEY")) || FormCFirstQuestion.Contains(TEXT("SCORE")) || FormCFirstQuestion.Contains(TEXT("SUBMITTED")) || FormCFirstQuestion.Contains(TEXT("CORRECT:")) || FormCFirstQuestion.Contains(TEXT("INCORRECT")) || FormCFirstQuestion.Contains(TEXT("CONCEPT:")));
	TestFalse(TEXT("Fresh blind form rejects a non A/B response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, FormCAnswers, TEXT('C'), Error, false, true));
	TestEqual(TEXT("Rejected fresh-form response does not advance"), FormCAnswers, FString());
	for (const TCHAR Answer : FString(TEXT("AAAAAA")))
	{
		TestTrue(TEXT("Fresh blind form accepts one bounded A/B response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, FormCAnswers, Answer, Error, false, true));
	}
	const FString FormCCompletion = BuildOddsWellAthleteComprehensionSessionPage(Snapshot, FormCAnswers, false, true);
	TestTrue(TEXT("Fresh blind form completes deterministically after six responses"), FormCCompletion.Contains(TEXT("SESSION COMPLETE")) && FormCCompletion.Contains(TEXT("SUBMITTED: AAAAAA")) && FormCCompletion.Contains(TEXT("SCORE:")));
	TestEqual(TEXT("Fresh blind form completion is deterministic"), BuildOddsWellAthleteComprehensionSessionPage(Snapshot, FormCAnswers, false, true), FormCCompletion);
	TestFalse(TEXT("Fresh blind form rejects a seventh response"), SubmitOddsWellAthleteComprehensionAnswer(Snapshot, FormCAnswers, TEXT('A'), Error, false, true));
	TestEqual(TEXT("Rejected fresh-form seventh response does not mutate answers"), FormCAnswers, FString(TEXT("AAAAAA")));
#endif

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
