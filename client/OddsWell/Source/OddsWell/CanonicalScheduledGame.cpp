#include "CanonicalScheduledGame.h"

#include "Kismet/GameplayStatics.h"
#include "Misc/DateTime.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 CanonicalScheduledGameVersion = 1;
constexpr int32 CanonicalSeasonNumber = 1;
constexpr int32 CanonicalGameNumber = 1;
constexpr int64 TipoffDelaySeconds = 30 * 60;
constexpr int32 CanonicalScheduledGameUserIndex = 0;
const FString CanonicalScheduledGameSchema(TEXT("oddswell-canonical-scheduled-game-v1"));
const FString CanonicalHomeTeam(TEXT("Harbor City Waves"));
const FString CanonicalAwayTeam(TEXT("Mesa Vista Sol"));
const FString ScheduledUnplayedStatus(TEXT("scheduled_unplayed"));
const FString LocalBetaEnvironment(TEXT("local_beta"));
const FString ServerTimingAuthority(TEXT("server"));
const FString CanonicalScheduledGameSlot(TEXT("OddsWellCanonicalScheduledGame"));
const FString CanonicalScheduledGameQaSlot(TEXT("OddsWellCanonicalScheduledGameQA"));

bool IsSameCanonicalScheduledGame(
	const FOddsWellCanonicalScheduledGameRecord& Left,
	const FOddsWellCanonicalScheduledGameRecord& Right)
{
	return Left.Schema == Right.Schema
		&& Left.RecordVersion == Right.RecordVersion
		&& Left.SeasonNumber == Right.SeasonNumber
		&& Left.GameNumber == Right.GameNumber
		&& Left.HomeTeam == Right.HomeTeam
		&& Left.AwayTeam == Right.AwayTeam
		&& Left.SeasonCreatedUnixSeconds == Right.SeasonCreatedUnixSeconds
		&& Left.TipoffUnixSeconds == Right.TipoffUnixSeconds
		&& Left.OfferEligibleUnixSeconds == Right.OfferEligibleUnixSeconds
		&& Left.Status == Right.Status
		&& Left.Environment == Right.Environment
		&& Left.TimingAuthority == Right.TimingAuthority
		&& Left.bProductionTiming == Right.bProductionTiming
		&& Left.bOfferPublished == Right.bOfferPublished;
}

bool ValidateCanonicalScheduledGame(
	const UObject* SaveObject,
	FOddsWellCanonicalScheduledGameRecord& OutRecord,
	FString& OutError)
{
	const UOddsWellCanonicalScheduledGameSaveGame* Saved =
		Cast<UOddsWellCanonicalScheduledGameSaveGame>(SaveObject);
	if (!Saved)
	{
		OutError = TEXT("The canonical scheduled-game save is not the expected object type.");
		return false;
	}
	if (Saved->Schema != CanonicalScheduledGameSchema
		|| Saved->RecordVersion != CanonicalScheduledGameVersion)
	{
		OutError = TEXT("The canonical scheduled-game schema or version is unsupported.");
		return false;
	}
	if (Saved->SeasonNumber != CanonicalSeasonNumber
		|| Saved->GameNumber != CanonicalGameNumber
		|| Saved->HomeTeam != CanonicalHomeTeam
		|| Saved->AwayTeam != CanonicalAwayTeam)
	{
		OutError = TEXT("The canonical scheduled-game identity conflicts with the approved local-beta game.");
		return false;
	}
	if (Saved->SeasonCreatedUnixSeconds <= 0
		|| Saved->SeasonCreatedUnixSeconds > TNumericLimits<int64>::Max() - TipoffDelaySeconds
		|| Saved->TipoffUnixSeconds != Saved->SeasonCreatedUnixSeconds + TipoffDelaySeconds
		|| Saved->OfferEligibleUnixSeconds != Saved->SeasonCreatedUnixSeconds)
	{
		OutError = TEXT("The canonical scheduled-game timing is invalid.");
		return false;
	}
	if (Saved->Status != ScheduledUnplayedStatus
		|| Saved->Environment != LocalBetaEnvironment
		|| Saved->TimingAuthority != ServerTimingAuthority
		|| Saved->bProductionTiming
		|| Saved->bOfferPublished)
	{
		OutError = TEXT("The canonical scheduled-game state is not an unpublished local-beta scheduled game.");
		return false;
	}
	OutRecord = {
		Saved->Schema,
		Saved->RecordVersion,
		Saved->SeasonNumber,
		Saved->GameNumber,
		Saved->HomeTeam,
		Saved->AwayTeam,
		Saved->SeasonCreatedUnixSeconds,
		Saved->TipoffUnixSeconds,
		Saved->OfferEligibleUnixSeconds,
		Saved->Status,
		Saved->Environment,
		Saved->TimingAuthority,
		Saved->bProductionTiming,
		Saved->bOfferPublished};
	OutError.Reset();
	return true;
}

EOddsWellCanonicalScheduledGameResult PersistCanonicalScheduledGame(
	const FString& Slot,
	const int64 ServerUnixSeconds,
	FOddsWellCanonicalScheduledGameRecord& OutRecord,
	FString& OutError)
{
	if (UGameplayStatics::DoesSaveGameExist(Slot, CanonicalScheduledGameUserIndex))
	{
		return ValidateCanonicalScheduledGame(
			UGameplayStatics::LoadGameFromSlot(Slot, CanonicalScheduledGameUserIndex),
			OutRecord,
			OutError)
			? EOddsWellCanonicalScheduledGameResult::Duplicate
			: EOddsWellCanonicalScheduledGameResult::Rejected;
	}
	if (ServerUnixSeconds <= 0
		|| ServerUnixSeconds > TNumericLimits<int64>::Max() - TipoffDelaySeconds)
	{
		OutError = TEXT("The authoritative server time cannot create the canonical scheduled game.");
		return EOddsWellCanonicalScheduledGameResult::Rejected;
	}
	UOddsWellCanonicalScheduledGameSaveGame* Saved =
		Cast<UOddsWellCanonicalScheduledGameSaveGame>(
			UGameplayStatics::CreateSaveGameObject(UOddsWellCanonicalScheduledGameSaveGame::StaticClass()));
	if (!Saved)
	{
		OutError = TEXT("The canonical scheduled-game save object could not be created.");
		return EOddsWellCanonicalScheduledGameResult::Rejected;
	}
	Saved->Schema = CanonicalScheduledGameSchema;
	Saved->RecordVersion = CanonicalScheduledGameVersion;
	Saved->SeasonNumber = CanonicalSeasonNumber;
	Saved->GameNumber = CanonicalGameNumber;
	Saved->HomeTeam = CanonicalHomeTeam;
	Saved->AwayTeam = CanonicalAwayTeam;
	Saved->SeasonCreatedUnixSeconds = ServerUnixSeconds;
	Saved->TipoffUnixSeconds = ServerUnixSeconds + TipoffDelaySeconds;
	Saved->OfferEligibleUnixSeconds = ServerUnixSeconds;
	Saved->Status = ScheduledUnplayedStatus;
	Saved->Environment = LocalBetaEnvironment;
	Saved->TimingAuthority = ServerTimingAuthority;
	Saved->bProductionTiming = false;
	Saved->bOfferPublished = false;
	if (!ValidateCanonicalScheduledGame(Saved, OutRecord, OutError))
	{
		return EOddsWellCanonicalScheduledGameResult::Rejected;
	}
	if (!UGameplayStatics::SaveGameToSlot(Saved, Slot, CanonicalScheduledGameUserIndex))
	{
		OutError = TEXT("Native SaveGameToSlot failed for the canonical scheduled game.");
		return EOddsWellCanonicalScheduledGameResult::Rejected;
	}
	OutError.Reset();
	return EOddsWellCanonicalScheduledGameResult::Created;
}
}

EOddsWellCanonicalScheduledGameResult CreateOddsWellCanonicalLocalBetaScheduledGame(
	FOddsWellCanonicalScheduledGameRecord& OutRecord,
	FString& OutError)
{
	return PersistCanonicalScheduledGame(
		CanonicalScheduledGameSlot,
		FDateTime::UtcNow().ToUnixTimestamp(),
		OutRecord,
		OutError);
}

bool LoadOddsWellCanonicalLocalBetaScheduledGame(
	FOddsWellCanonicalScheduledGameRecord& OutRecord,
	FString& OutError)
{
	if (!UGameplayStatics::DoesSaveGameExist(
		CanonicalScheduledGameSlot,
		CanonicalScheduledGameUserIndex))
	{
		OutError = TEXT("No canonical local-beta scheduled-game save exists.");
		return false;
	}
	return ValidateCanonicalScheduledGame(
		UGameplayStatics::LoadGameFromSlot(
			CanonicalScheduledGameSlot,
			CanonicalScheduledGameUserIndex),
		OutRecord,
		OutError);
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCanonicalScheduledGamePersistenceTest,
	"OddsWell.League.CanonicalScheduledGame",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCanonicalScheduledGamePersistenceTest::RunTest(const FString& Parameters)
{
	constexpr int64 ServerUnixSeconds = 2200000000;
	UGameplayStatics::DeleteGameInSlot(
		CanonicalScheduledGameQaSlot,
		CanonicalScheduledGameUserIndex);
	FOddsWellCanonicalScheduledGameRecord Created;
	FString Error;
	TestEqual(
		TEXT("Server-owned transition creates one canonical scheduled game"),
		PersistCanonicalScheduledGame(
			CanonicalScheduledGameQaSlot,
			ServerUnixSeconds,
			Created,
			Error),
		EOddsWellCanonicalScheduledGameResult::Created);
	TestEqual(TEXT("Schema is exact"), Created.Schema, CanonicalScheduledGameSchema);
	TestEqual(TEXT("Record version is exact"), Created.RecordVersion, CanonicalScheduledGameVersion);
	TestEqual(TEXT("Season is fresh Season 1"), Created.SeasonNumber, CanonicalSeasonNumber);
	TestEqual(TEXT("Game is fresh Game 1"), Created.GameNumber, CanonicalGameNumber);
	TestEqual(TEXT("Home team is exact"), Created.HomeTeam, CanonicalHomeTeam);
	TestEqual(TEXT("Away team is exact"), Created.AwayTeam, CanonicalAwayTeam);
	TestEqual(TEXT("Creation time is server-owned"), Created.SeasonCreatedUnixSeconds, ServerUnixSeconds);
	TestEqual(TEXT("Tipoff is exactly thirty minutes later"), Created.TipoffUnixSeconds, ServerUnixSeconds + TipoffDelaySeconds);
	TestEqual(TEXT("Offer eligibility begins at creation"), Created.OfferEligibleUnixSeconds, ServerUnixSeconds);
	TestEqual(TEXT("Game remains scheduled and unplayed"), Created.Status, ScheduledUnplayedStatus);
	TestEqual(TEXT("Environment is explicit"), Created.Environment, LocalBetaEnvironment);
	TestEqual(TEXT("Timing authority is explicit"), Created.TimingAuthority, ServerTimingAuthority);
	TestFalse(TEXT("Timing is not production timing"), Created.bProductionTiming);
	TestFalse(TEXT("No offer is published"), Created.bOfferPublished);

	FOddsWellCanonicalScheduledGameRecord Duplicate;
	TestEqual(
		TEXT("Exact retry is duplicate-safe"),
		PersistCanonicalScheduledGame(
			CanonicalScheduledGameQaSlot,
			ServerUnixSeconds + 999,
			Duplicate,
			Error),
		EOddsWellCanonicalScheduledGameResult::Duplicate);
	TestEqual(TEXT("Retry preserves the original creation time"), Duplicate.SeasonCreatedUnixSeconds, ServerUnixSeconds);
	TestEqual(TEXT("Retry preserves the original tipoff"), Duplicate.TipoffUnixSeconds, ServerUnixSeconds + TipoffDelaySeconds);
	TestTrue(TEXT("Retry restores every original field"), IsSameCanonicalScheduledGame(Duplicate, Created));

	FOddsWellCanonicalScheduledGameRecord Cold;
	TestTrue(
		TEXT("Cold disk restore validates"),
		ValidateCanonicalScheduledGame(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalScheduledGameQaSlot,
				CanonicalScheduledGameUserIndex),
			Cold,
			Error));
	TestTrue(TEXT("Cold restore preserves every field"), IsSameCanonicalScheduledGame(Cold, Created));

	UOddsWellCanonicalScheduledGameSaveGame* Conflicting =
		Cast<UOddsWellCanonicalScheduledGameSaveGame>(
			UGameplayStatics::LoadGameFromSlot(
				CanonicalScheduledGameQaSlot,
				CanonicalScheduledGameUserIndex));
	TestNotNull(TEXT("Saved record reloads for conflict proof"), Conflicting);
	if (Conflicting)
	{
		Conflicting->HomeTeam = TEXT("Wrong Team");
		TestTrue(
			TEXT("Conflicting state saves for rejection proof"),
			UGameplayStatics::SaveGameToSlot(
				Conflicting,
				CanonicalScheduledGameQaSlot,
				CanonicalScheduledGameUserIndex));
		TestEqual(
			TEXT("Conflicting preexisting identity fails closed"),
			PersistCanonicalScheduledGame(
				CanonicalScheduledGameQaSlot,
				ServerUnixSeconds,
				Cold,
				Error),
			EOddsWellCanonicalScheduledGameResult::Rejected);

		Conflicting->HomeTeam = CanonicalHomeTeam;
		Conflicting->Status = TEXT("completed");
		TestTrue(
			TEXT("Preexisting result state saves for rejection proof"),
			UGameplayStatics::SaveGameToSlot(
				Conflicting,
				CanonicalScheduledGameQaSlot,
				CanonicalScheduledGameUserIndex));
		TestEqual(
			TEXT("Preexisting result state fails closed"),
			PersistCanonicalScheduledGame(
				CanonicalScheduledGameQaSlot,
				ServerUnixSeconds,
				Cold,
				Error),
			EOddsWellCanonicalScheduledGameResult::Rejected);
		const UOddsWellCanonicalScheduledGameSaveGame* Unchanged =
			Cast<UOddsWellCanonicalScheduledGameSaveGame>(
				UGameplayStatics::LoadGameFromSlot(
					CanonicalScheduledGameQaSlot,
					CanonicalScheduledGameUserIndex));
		TestNotNull(TEXT("Rejected result state remains readable as evidence"), Unchanged);
		if (Unchanged)
		{
			TestEqual(TEXT("Rejected result state is not rewritten"), Unchanged->Status, FString(TEXT("completed")));
		}
	}

	TestTrue(
		TEXT("QA record cleanup succeeds"),
		UGameplayStatics::DeleteGameInSlot(
			CanonicalScheduledGameQaSlot,
			CanonicalScheduledGameUserIndex));
	TestFalse(
		TEXT("Native test leaves no QA record behind"),
		UGameplayStatics::DoesSaveGameExist(
			CanonicalScheduledGameQaSlot,
			CanonicalScheduledGameUserIndex));
	return !HasAnyErrors();
}
#endif
