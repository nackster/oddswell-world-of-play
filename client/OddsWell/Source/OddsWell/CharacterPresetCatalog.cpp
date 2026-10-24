#include "CharacterPresetCatalog.h"

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

namespace
{
const FName StarterTop(TEXT("starter_offwhite_top"));
const FName StarterBottom(TEXT("starter_offwhite_bottom"));
}

const TArray<FOddsWellCharacterPreset>& GetOddsWellCharacterPresets()
{
	static const TArray<FOddsWellCharacterPreset> Presets = {
		{TEXT("masculine_tone_1"), EOddsWellCharacterPresentation::Masculine, FColor(246, 218, 194), {StarterTop, StarterBottom}},
		{TEXT("masculine_tone_2"), EOddsWellCharacterPresentation::Masculine, FColor(210, 160, 120), {StarterTop, StarterBottom}},
		{TEXT("masculine_tone_3"), EOddsWellCharacterPresentation::Masculine, FColor(145, 96, 68), {StarterTop, StarterBottom}},
		{TEXT("masculine_tone_4"), EOddsWellCharacterPresentation::Masculine, FColor(82, 52, 38), {StarterTop, StarterBottom}},
		{TEXT("feminine_tone_1"), EOddsWellCharacterPresentation::Feminine, FColor(246, 218, 194), {StarterTop, StarterBottom}},
		{TEXT("feminine_tone_2"), EOddsWellCharacterPresentation::Feminine, FColor(210, 160, 120), {StarterTop, StarterBottom}},
		{TEXT("feminine_tone_3"), EOddsWellCharacterPresentation::Feminine, FColor(145, 96, 68), {StarterTop, StarterBottom}},
		{TEXT("feminine_tone_4"), EOddsWellCharacterPresentation::Feminine, FColor(82, 52, 38), {StarterTop, StarterBottom}}
	};
	return Presets;
}

bool ValidateOddsWellCharacterPresets(FString& OutError)
{
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	if (Presets.Num() != 8)
	{
		OutError = TEXT("Expected exactly eight placeholder presets.");
		return false;
	}

	TSet<FName> Ids;
	TSet<FString> MasculineTones;
	TSet<FString> FeminineTones;
	TSet<FString> AllTones;
	int32 MasculineCount = 0;
	int32 FeminineCount = 0;
	for (const FOddsWellCharacterPreset& Preset : Presets)
	{
		if (Preset.Id.IsNone() || Ids.Contains(Preset.Id))
		{
			OutError = TEXT("Preset IDs must be present and unique.");
			return false;
		}
		Ids.Add(Preset.Id);
		AllTones.Add(Preset.SkinTone.ToHex());
		if (Preset.Presentation == EOddsWellCharacterPresentation::Masculine)
		{
			++MasculineCount;
			MasculineTones.Add(Preset.SkinTone.ToHex());
		}
		else
		{
			++FeminineCount;
			FeminineTones.Add(Preset.SkinTone.ToHex());
		}
		if (Preset.EquippedItemIds.Num() != 2
			|| Preset.EquippedItemIds[0] != StarterTop
			|| Preset.EquippedItemIds[1] != StarterBottom)
		{
			OutError = TEXT("Every preset must equip the same replaceable starter top and bottom.");
			return false;
		}
	}

	if (MasculineCount != 4
		|| FeminineCount != 4
		|| MasculineTones.Num() != 4
		|| FeminineTones.Num() != 4
		|| AllTones.Num() != 4)
	{
		OutError = TEXT("Expected four presets per presentation across four shared skin tones.");
		return false;
	}

	OutError.Reset();
	return true;
}

const FOddsWellCharacterPreset* FindOddsWellCharacterPreset(const FName PresetId)
{
	return GetOddsWellCharacterPresets().FindByPredicate(
		[PresetId](const FOddsWellCharacterPreset& Preset) { return Preset.Id == PresetId; });
}

bool GetOddsWellStarterEquipmentIds(FName& OutTop, FName& OutBottom, FString& OutError)
{
	if (!ValidateOddsWellCharacterPresets(OutError))
	{
		return false;
	}
	const TArray<FOddsWellCharacterPreset>& Presets = GetOddsWellCharacterPresets();
	if (Presets.IsEmpty() || Presets[0].EquippedItemIds.Num() != 2)
	{
		OutError = TEXT("The safe preset must contain one starter top and one starter bottom.");
		return false;
	}
	OutTop = Presets[0].EquippedItemIds[0];
	OutBottom = Presets[0].EquippedItemIds[1];
	OutError.Reset();
	return true;
}

bool ResolveOddsWellStarterEquipmentSlot(const FName ItemId, EOddsWellStarterEquipmentSlot& OutSlot, FString& OutError)
{
	FName TopId;
	FName BottomId;
	if (!GetOddsWellStarterEquipmentIds(TopId, BottomId, OutError))
	{
		return false;
	}
	if (ItemId == TopId)
	{
		OutSlot = EOddsWellStarterEquipmentSlot::Top;
		return true;
	}
	if (ItemId == BottomId)
	{
		OutSlot = EOddsWellStarterEquipmentSlot::Bottom;
		return true;
	}
	OutError = FString::Printf(TEXT("Unsupported starter equipment ID: %s"), *ItemId.ToString());
	return false;
}

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FOddsWellCharacterPresetCatalogTest,
	"OddsWell.Character.PresetCatalog",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FOddsWellCharacterPresetCatalogTest::RunTest(const FString& Parameters)
{
	FString Error;
	TestTrue(TEXT("Approved placeholder catalog is valid"), ValidateOddsWellCharacterPresets(Error));
	if (!Error.IsEmpty())
	{
		AddError(Error);
	}
	return !HasAnyErrors();
}
#endif
