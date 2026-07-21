#include "StudioHomeSave.h"

#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
#include "Engine/StaticMesh.h"
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 StudioHomeSchemaVersion = 1;
constexpr int32 StudioHomeUserIndex = 0;
constexpr double MaximumReturnCoordinate = 1000000.0;
const FString StudioHomeSlot(TEXT("OddsWellStudioHome"));
const FString StudioHomeQaSlot(TEXT("OddsWellStudioHomeQA"));

const FString& GetStudioHomeSlot(const bool bQaSlot)
{
	return bQaSlot ? StudioHomeQaSlot : StudioHomeSlot;
}

bool IsValidReturnLocation(const FVector& Location)
{
	return !Location.ContainsNaN()
		&& FMath::Abs(Location.X) <= MaximumReturnCoordinate
		&& FMath::Abs(Location.Y) <= MaximumReturnCoordinate
		&& FMath::Abs(Location.Z) <= MaximumReturnCoordinate;
}

bool ValidateStudioHomeSave(const UObject* SaveObject, FOddsWellStudioHomeState& OutState, FString& OutError)
{
	const UOddsWellStudioHomeSaveGame* Record = Cast<UOddsWellStudioHomeSaveGame>(SaveObject);
	if (!Record)
	{
		OutError = TEXT("The Studio home save is not the expected object type.");
		return false;
	}
	if (Record->SchemaVersion != StudioHomeSchemaVersion)
	{
		OutError = FString::Printf(TEXT("Unsupported Studio home schema version: %d"), Record->SchemaVersion);
		return false;
	}
	if (!Record->bOwnsStudio)
	{
		OutError = TEXT("The Studio home record does not prove ownership.");
		return false;
	}
	if (!IsValidReturnLocation(Record->SundaleReturnLocation))
	{
		OutError = TEXT("The Studio home return location is invalid.");
		return false;
	}
	OutState = {true, Record->SundaleReturnLocation};
	OutError.Reset();
	return true;
}
}

bool UseOddsWellStudioHomeQaSlot()
{
	return FParse::Param(FCommandLine::Get(), TEXT("StudioPersistenceQa"))
		|| FParse::Param(FCommandLine::Get(), TEXT("StudioPersistenceQaVerify"));
}

bool SaveOwnedOddsWellStudio(const FVector& SundaleReturnLocation, const bool bQaSlot, FString& OutError)
{
	if (!IsValidReturnLocation(SundaleReturnLocation))
	{
		OutError = TEXT("The Studio home return location is invalid.");
		return false;
	}
	UOddsWellStudioHomeSaveGame* Record = Cast<UOddsWellStudioHomeSaveGame>(
		UGameplayStatics::CreateSaveGameObject(UOddsWellStudioHomeSaveGame::StaticClass()));
	if (!Record)
	{
		OutError = TEXT("The native Studio home save object could not be created.");
		return false;
	}
	Record->SchemaVersion = StudioHomeSchemaVersion;
	Record->bOwnsStudio = true;
	Record->SundaleReturnLocation = SundaleReturnLocation;
	FOddsWellStudioHomeState Validated;
	if (!ValidateStudioHomeSave(Record, Validated, OutError))
	{
		return false;
	}
	if (!UGameplayStatics::SaveGameToSlot(Record, GetStudioHomeSlot(bQaSlot), StudioHomeUserIndex))
	{
		OutError = TEXT("Native SaveGameToSlot failed for the Studio home record.");
		return false;
	}
	OutError.Reset();
	return true;
}

bool LoadOwnedOddsWellStudio(const bool bQaSlot, FOddsWellStudioHomeState& OutState, FString& OutError)
{
	const FString& Slot = GetStudioHomeSlot(bQaSlot);
	if (!UGameplayStatics::DoesSaveGameExist(Slot, StudioHomeUserIndex))
	{
		OutError = TEXT("No local Studio home save exists.");
		return false;
	}
	return ValidateStudioHomeSave(UGameplayStatics::LoadGameFromSlot(Slot, StudioHomeUserIndex), OutState, OutError);
}

bool DeleteOddsWellQaStudioHomeAndVerify(FString& OutError)
{
	if (!UGameplayStatics::DoesSaveGameExist(StudioHomeQaSlot, StudioHomeUserIndex))
	{
		OutError = TEXT("The QA Studio home save did not exist at cleanup.");
		return false;
	}
	if (!UGameplayStatics::DeleteGameInSlot(StudioHomeQaSlot, StudioHomeUserIndex)
		|| UGameplayStatics::DoesSaveGameExist(StudioHomeQaSlot, StudioHomeUserIndex))
	{
		OutError = TEXT("The QA Studio home save could not be deleted and verified absent.");
		return false;
	}
	OutError.Reset();
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellStudioHomePersistenceTest,
	"OddsWell.Character.StudioHomePersistence",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellStudioHomePersistenceTest::RunTest(const FString& Parameters)
{
	const FVector ExpectedReturnLocation(125.0, 75.0, 96.0);
	UOddsWellStudioHomeSaveGame* Record = NewObject<UOddsWellStudioHomeSaveGame>();
	Record->SchemaVersion = StudioHomeSchemaVersion;
	Record->bOwnsStudio = true;
	Record->SundaleReturnLocation = ExpectedReturnLocation;
	TArray<uint8> Bytes;
	TestTrue(TEXT("Studio ownership serializes"), UGameplayStatics::SaveGameToMemory(Record, Bytes));
	FOddsWellStudioHomeState State;
	FString Error;
	TestTrue(TEXT("Studio ownership validates after a memory round trip"), ValidateStudioHomeSave(UGameplayStatics::LoadGameFromMemory(Bytes), State, Error));
	TestTrue(TEXT("Studio ownership remains true"), State.bOwnsStudio);
	TestTrue(TEXT("Sundale return location remains exact"), State.SundaleReturnLocation.Equals(ExpectedReturnLocation));

	Record->bOwnsStudio = false;
	TestFalse(TEXT("An unowned Studio record is rejected"), ValidateStudioHomeSave(Record, State, Error));
	Record->bOwnsStudio = true;
	Record->SchemaVersion = 2;
	TestFalse(TEXT("An unsupported Studio home schema is rejected"), ValidateStudioHomeSave(Record, State, Error));
	Record->SchemaVersion = StudioHomeSchemaVersion;
	Record->SundaleReturnLocation.X = std::numeric_limits<double>::quiet_NaN();
	TestFalse(TEXT("A corrupt Studio return location is rejected"), ValidateStudioHomeSave(Record, State, Error));
	TestFalse(TEXT("A wrong save type is rejected"), ValidateStudioHomeSave(NewObject<UStaticMesh>(), State, Error));

	UGameplayStatics::DeleteGameInSlot(StudioHomeQaSlot, StudioHomeUserIndex);
	TestTrue(TEXT("Owned Studio saves to the bounded QA slot"), SaveOwnedOddsWellStudio(ExpectedReturnLocation, true, Error));
	TestTrue(TEXT("Owned Studio reloads from the QA slot"), LoadOwnedOddsWellStudio(true, State, Error));
	TestTrue(TEXT("QA disk round trip preserves the return location"), State.SundaleReturnLocation.Equals(ExpectedReturnLocation));
	TestTrue(TEXT("QA Studio home cleanup succeeds"), DeleteOddsWellQaStudioHomeAndVerify(Error));
	TestFalse(TEXT("Native test leaves no QA Studio home save behind"), UGameplayStatics::DoesSaveGameExist(StudioHomeQaSlot, StudioHomeUserIndex));
	return !HasAnyErrors();
}
#endif
