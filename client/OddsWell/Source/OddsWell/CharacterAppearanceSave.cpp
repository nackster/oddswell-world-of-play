#include "CharacterAppearanceSave.h"

#include "CharacterPresetCatalog.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Engine/StaticMesh.h"
#include "Misc/AutomationTest.h"
#endif

namespace
{
constexpr int32 AppearanceSchemaVersion = 1;
constexpr int32 AppearanceUserIndex = 0;
const FString AppearanceSlot(TEXT("OddsWellCharacterAppearance"));
const FString AppearanceQaSlot(TEXT("OddsWellCharacterAppearanceQA"));

const FString& GetAppearanceSlot(const bool bQaSlot)
{
	return bQaSlot ? AppearanceQaSlot : AppearanceSlot;
}

bool BuildFallbackAppearance(FOddsWellResolvedCharacterAppearance& OutAppearance, FString& OutError)
{
	if (!ValidateOddsWellCharacterPresets(OutError))
	{
		return false;
	}
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	if (Presets.IsEmpty() || Presets[0].EquippedItemIds.Num() != 2)
	{
		OutError = TEXT("No complete deterministic fallback appearance is available.");
		return false;
	}
	OutAppearance = {&Presets[0], Presets[0].EquippedItemIds[0], Presets[0].EquippedItemIds[1]};
	return true;
}
}

bool UseOddsWellAppearanceQaSlot()
{
	return FParse::Param(FCommandLine::Get(), TEXT("AppearanceQa"));
}

bool ValidateOddsWellCharacterAppearanceSave(
	const UObject* SaveObject,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutError)
{
	const UOddsWellCharacterAppearanceSaveGame* Record = Cast<UOddsWellCharacterAppearanceSaveGame>(SaveObject);
	if (!Record)
	{
		OutError = TEXT("The appearance save is not the expected object type.");
		return false;
	}
	if (Record->SchemaVersion != AppearanceSchemaVersion)
	{
		OutError = FString::Printf(TEXT("Unsupported appearance schema version: %d"), Record->SchemaVersion);
		return false;
	}
	return ValidateOddsWellCharacterAppearanceIds(
		Record->PresetId,
		Record->TopItemId,
		Record->BottomItemId,
		OutAppearance,
		OutError);
}

bool ValidateOddsWellCharacterAppearanceIds(
	const FName PresetId,
	const FName TopItemId,
	const FName BottomItemId,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutError)
{
	if (!ValidateOddsWellCharacterPresets(OutError))
	{
		return false;
	}
	const FOddsWellCharacterPreset* Preset = FindOddsWellCharacterPreset(PresetId);
	if (!Preset)
	{
		OutError = FString::Printf(TEXT("Unknown appearance preset ID: %s"), *PresetId.ToString());
		return false;
	}
	if (TopItemId.IsNone() || BottomItemId.IsNone())
	{
		OutError = TEXT("The appearance record is incomplete.");
		return false;
	}
	if (TopItemId == BottomItemId)
	{
		OutError = TEXT("The appearance record assigns one item to both slots.");
		return false;
	}
	EOddsWellStarterEquipmentSlot TopSlot = EOddsWellStarterEquipmentSlot::Bottom;
	EOddsWellStarterEquipmentSlot BottomSlot = EOddsWellStarterEquipmentSlot::Top;
	if (!ResolveOddsWellStarterEquipmentSlot(TopItemId, TopSlot, OutError)
		|| !ResolveOddsWellStarterEquipmentSlot(BottomItemId, BottomSlot, OutError))
	{
		return false;
	}
	if (TopSlot != EOddsWellStarterEquipmentSlot::Top || BottomSlot != EOddsWellStarterEquipmentSlot::Bottom)
	{
		OutError = TEXT("The appearance record assigns starter equipment to the wrong slot.");
		return false;
	}
	if (Preset->EquippedItemIds.Num() != 2
		|| TopItemId != Preset->EquippedItemIds[0]
		|| BottomItemId != Preset->EquippedItemIds[1])
	{
		OutError = TEXT("The appearance record does not match the selected preset's complete starter outfit.");
		return false;
	}
	OutAppearance = {Preset, TopItemId, BottomItemId};
	OutError.Reset();
	return true;
}

bool ResolveOddsWellCharacterAppearance(
	const UObject* SaveObject,
	const bool bSaveExists,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutSource,
	FString& OutError)
{
	FOddsWellResolvedCharacterAppearance Fallback;
	if (!BuildFallbackAppearance(Fallback, OutError))
	{
		return false;
	}
	if (!bSaveExists)
	{
		OutAppearance = Fallback;
		OutSource = TEXT("fallback_missing");
		OutError = TEXT("No local appearance save exists.");
		return true;
	}
	if (!SaveObject)
	{
		OutAppearance = Fallback;
		OutSource = TEXT("fallback_unreadable");
		OutError = TEXT("The local appearance save could not be read.");
		return true;
	}
	FOddsWellResolvedCharacterAppearance Loaded;
	if (!ValidateOddsWellCharacterAppearanceSave(SaveObject, Loaded, OutError))
	{
		OutAppearance = Fallback;
		OutSource = TEXT("fallback_rejected");
		return true;
	}
	OutAppearance = Loaded;
	OutSource = TEXT("loaded");
	OutError.Reset();
	return true;
}

bool SaveOddsWellCharacterAppearance(const FName PresetId, const bool bQaSlot, FString& OutError)
{
	const FOddsWellCharacterPreset* Preset = FindOddsWellCharacterPreset(PresetId);
	if (!Preset || !ValidateOddsWellCharacterPresets(OutError) || Preset->EquippedItemIds.Num() != 2)
	{
		OutError = Preset ? OutError : FString::Printf(TEXT("Unknown appearance preset ID: %s"), *PresetId.ToString());
		return false;
	}
	UOddsWellCharacterAppearanceSaveGame* Record = Cast<UOddsWellCharacterAppearanceSaveGame>(
		UGameplayStatics::CreateSaveGameObject(UOddsWellCharacterAppearanceSaveGame::StaticClass()));
	if (!Record)
	{
		OutError = TEXT("The native appearance save object could not be created.");
		return false;
	}
	Record->SchemaVersion = AppearanceSchemaVersion;
	Record->PresetId = Preset->Id;
	Record->TopItemId = Preset->EquippedItemIds[0];
	Record->BottomItemId = Preset->EquippedItemIds[1];
	FOddsWellResolvedCharacterAppearance Validated;
	if (!ValidateOddsWellCharacterAppearanceSave(Record, Validated, OutError))
	{
		return false;
	}
	if (!UGameplayStatics::SaveGameToSlot(Record, GetAppearanceSlot(bQaSlot), AppearanceUserIndex))
	{
		OutError = TEXT("Native SaveGameToSlot failed for the local appearance record.");
		return false;
	}
	OutError.Reset();
	return true;
}

bool LoadOddsWellCharacterAppearance(
	const bool bQaSlot,
	FOddsWellResolvedCharacterAppearance& OutAppearance,
	FString& OutSource,
	FString& OutError)
{
	const FString& Slot = GetAppearanceSlot(bQaSlot);
	const bool bExists = UGameplayStatics::DoesSaveGameExist(Slot, AppearanceUserIndex);
	USaveGame* SaveGame = bExists ? UGameplayStatics::LoadGameFromSlot(Slot, AppearanceUserIndex) : nullptr;
	return ResolveOddsWellCharacterAppearance(SaveGame, bExists, OutAppearance, OutSource, OutError);
}

bool DeleteOddsWellQaAppearanceAndVerify(FString& OutError)
{
	if (!UGameplayStatics::DoesSaveGameExist(AppearanceQaSlot, AppearanceUserIndex))
	{
		OutError = TEXT("The QA appearance save did not exist at cleanup.");
		return false;
	}
	if (!UGameplayStatics::DeleteGameInSlot(AppearanceQaSlot, AppearanceUserIndex)
		|| UGameplayStatics::DoesSaveGameExist(AppearanceQaSlot, AppearanceUserIndex))
	{
		OutError = TEXT("The QA appearance save could not be deleted and verified absent.");
		return false;
	}
	OutError.Reset();
	return true;
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCharacterAppearancePersistenceTest,
	"OddsWell.Character.AppearancePersistence",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCharacterAppearancePersistenceTest::RunTest(const FString& Parameters)
{
	FString Error;
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	TestTrue(TEXT("Catalog remains valid before persistence tests"), ValidateOddsWellCharacterPresets(Error));
	if (Presets.Num() != 8)
	{
		AddError(TEXT("Appearance persistence requires the exact eight-preset catalog."));
		return false;
	}

	auto MakeRecord = [](const FOddsWellCharacterPreset& Preset)
	{
		UOddsWellCharacterAppearanceSaveGame* Record = NewObject<UOddsWellCharacterAppearanceSaveGame>();
		Record->SchemaVersion = AppearanceSchemaVersion;
		Record->PresetId = Preset.Id;
		Record->TopItemId = Preset.EquippedItemIds[0];
		Record->BottomItemId = Preset.EquippedItemIds[1];
		return Record;
	};
	auto TestRoundTrip = [this, &Error, &MakeRecord](const TCHAR* Label, const FOddsWellCharacterPreset& Preset)
	{
		TArray<uint8> Bytes;
		TestTrue(FString::Printf(TEXT("%s serializes"), Label), UGameplayStatics::SaveGameToMemory(MakeRecord(Preset), Bytes));
		USaveGame* Loaded = UGameplayStatics::LoadGameFromMemory(Bytes);
		FOddsWellResolvedCharacterAppearance Appearance;
		if (!TestTrue(FString::Printf(TEXT("%s validates after round trip"), Label), ValidateOddsWellCharacterAppearanceSave(Loaded, Appearance, Error)))
		{
			return;
		}
		TestEqual(FString::Printf(TEXT("%s preserves preset"), Label), Appearance.Preset->Id, Preset.Id);
		TestEqual(FString::Printf(TEXT("%s preserves top"), Label), Appearance.TopItemId, Preset.EquippedItemIds[0]);
		TestEqual(FString::Printf(TEXT("%s preserves bottom"), Label), Appearance.BottomItemId, Preset.EquippedItemIds[1]);
	};
	TestRoundTrip(TEXT("Default appearance"), Presets[0]);
	TestRoundTrip(TEXT("Non-default appearance"), Presets[5]);

	FOddsWellResolvedCharacterAppearance Appearance;
	FString Source;
	TestTrue(
		TEXT("Shared-city IDs use the same validator as saved appearances"),
		ValidateOddsWellCharacterAppearanceIds(
			Presets[7].Id,
			Presets[7].EquippedItemIds[0],
			Presets[7].EquippedItemIds[1],
			Appearance,
			Error));
	TestEqual(TEXT("Shared-city validation preserves the selected preset"), Appearance.Preset->Id, Presets[7].Id);
	TestFalse(
		TEXT("Shared-city validation rejects an unknown preset"),
		ValidateOddsWellCharacterAppearanceIds(
			TEXT("unknown_preset"),
			Presets[0].EquippedItemIds[0],
			Presets[0].EquippedItemIds[1],
			Appearance,
			Error));
	TestTrue(TEXT("Missing save resolves safely"), ResolveOddsWellCharacterAppearance(nullptr, false, Appearance, Source, Error));
	TestEqual(TEXT("Missing save uses deterministic source"), Source, FString(TEXT("fallback_missing")));
	TestEqual(TEXT("Missing save uses first preset"), Appearance.Preset->Id, Presets[0].Id);
	TestTrue(TEXT("Unreadable save resolves safely"), ResolveOddsWellCharacterAppearance(nullptr, true, Appearance, Source, Error));
	TestEqual(TEXT("Unreadable save is distinguished"), Source, FString(TEXT("fallback_unreadable")));

	auto TestRejectedFallback = [this, &Appearance, &Source, &Error, &Presets](const TCHAR* Label, UObject* Record)
	{
		TestTrue(FString::Printf(TEXT("%s resolves without crash"), Label), ResolveOddsWellCharacterAppearance(Record, true, Appearance, Source, Error));
		TestEqual(FString::Printf(TEXT("%s is rejected as a whole"), Label), Source, FString(TEXT("fallback_rejected")));
		TestEqual(FString::Printf(TEXT("%s falls back to first preset"), Label), Appearance.Preset->Id, Presets[0].Id);
		TestEqual(FString::Printf(TEXT("%s falls back to complete top"), Label), Appearance.TopItemId, Presets[0].EquippedItemIds[0]);
		TestEqual(FString::Printf(TEXT("%s falls back to complete bottom"), Label), Appearance.BottomItemId, Presets[0].EquippedItemIds[1]);
		TestFalse(FString::Printf(TEXT("%s reports a reason"), Label), Error.IsEmpty());
	};
	TestRejectedFallback(TEXT("Wrong object"), NewObject<UStaticMesh>());
	UOddsWellCharacterAppearanceSaveGame* Unsupported = MakeRecord(Presets[1]);
	Unsupported->SchemaVersion = 2;
	TestRejectedFallback(TEXT("Unsupported version"), Unsupported);
	UOddsWellCharacterAppearanceSaveGame* UnknownPreset = MakeRecord(Presets[1]);
	UnknownPreset->PresetId = TEXT("unknown_preset");
	TestRejectedFallback(TEXT("Unknown preset"), UnknownPreset);
	UOddsWellCharacterAppearanceSaveGame* UnknownItem = MakeRecord(Presets[1]);
	UnknownItem->TopItemId = TEXT("unknown_item");
	TestRejectedFallback(TEXT("Unknown item"), UnknownItem);
	UOddsWellCharacterAppearanceSaveGame* WrongSlots = MakeRecord(Presets[1]);
	Swap(WrongSlots->TopItemId, WrongSlots->BottomItemId);
	TestRejectedFallback(TEXT("Wrong slots"), WrongSlots);
	UOddsWellCharacterAppearanceSaveGame* Duplicate = MakeRecord(Presets[1]);
	Duplicate->BottomItemId = Duplicate->TopItemId;
	TestRejectedFallback(TEXT("Duplicate item"), Duplicate);
	UOddsWellCharacterAppearanceSaveGame* Incomplete = MakeRecord(Presets[1]);
	Incomplete->BottomItemId = NAME_None;
	TestRejectedFallback(TEXT("Incomplete record"), Incomplete);

	UGameplayStatics::DeleteGameInSlot(AppearanceQaSlot, AppearanceUserIndex);
	TestTrue(TEXT("Non-default appearance saves to the bounded QA slot"), SaveOddsWellCharacterAppearance(Presets[5].Id, true, Error));
	TestTrue(TEXT("Saved QA appearance loads"), LoadOddsWellCharacterAppearance(true, Appearance, Source, Error));
	TestEqual(TEXT("QA load source is loaded"), Source, FString(TEXT("loaded")));
	TestEqual(TEXT("QA disk round trip preserves non-default preset"), Appearance.Preset->Id, Presets[5].Id);
	TestTrue(TEXT("QA slot cleanup succeeds"), DeleteOddsWellQaAppearanceAndVerify(Error));
	TestFalse(TEXT("Native test leaves no QA save behind"), UGameplayStatics::DoesSaveGameExist(AppearanceQaSlot, AppearanceUserIndex));
	return !HasAnyErrors();
}
#endif
