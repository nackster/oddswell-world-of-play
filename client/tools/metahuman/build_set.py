"""Build the OddsWell player MetaHumans from Creator presets: duplicate, rig and fetch textures (Epic cloud,
with retries), then assemble with the Optimized pipeline at medium quality. Set ODDSWELL_MH_PRESETS to a
comma-separated subset to rebuild only some."""
import os
import unreal

PRESETS = [name for name in os.environ.get("ODDSWELL_MH_PRESETS", "Kelvin,Lorenzo,Trey,Isaiah,Jelena,Grace,Sunita,Zuri").split(",") if name]

def build(PRESET):
    TARGET = f"/Game/OddsWell/Characters/MetaHumans/{PRESET}"
    log = lambda message: unreal.log(f"ODDSWELL_MH_BUILD|{message}")

    subsystem = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
    library = unreal.EditorAssetLibrary
    source = f"/MetaHumanCharacter/Optional/Presets/{PRESET}"
    character_path = f"{TARGET}/MHC_{PRESET}"
    if library.does_asset_exist(character_path):
        library.delete_asset(character_path)
    character = library.duplicate_asset(source, character_path)
    log(f"preset={PRESET}|duplicated={character is not None}|class={character.get_class().get_name() if character else None}")
    if not character:
        return False

    if not subsystem.try_add_object_to_edit(character=character):
        log("edit=false")
        return False

    for attempt in range(3):
        rig = unreal.MetaHumanCharacterAutoRiggingRequestParams()
        rig.blocking = True
        rig.report_progress = False
        rig.rig_type = unreal.MetaHumanRigType.JOINTS_ONLY
        subsystem.request_auto_rigging(character=character, params=rig)
        textures = unreal.MetaHumanCharacterTextureRequestParams()
        textures.blocking = True
        textures.report_progress = False
        subsystem.request_texture_sources(character=character, params=textures)
        ready = subsystem.can_build_meta_human(character=character)
        log(f"attempt={attempt + 1}|high_res={character.has_high_resolution_textures}|can_build={ready}")
        if ready:
            break

    params = unreal.MetaHumanCharacterEditorBuildParameters()
    params.pipeline_type = unreal.MetaHumanDefaultPipelineType.OPTIMIZED
    params.pipeline_quality = unreal.MetaHumanQualityLevel.MEDIUM
    params.absolute_build_path = f"{TARGET}/Built"
    params.common_folder_path = "/Game/OddsWell/Characters/MetaHumans/Common"
    params.enable_wardrobe_item_validation = True
    subsystem.build_meta_human(character=character, params=params)
    subsystem.remove_object_to_edit(character=character)
    library.save_directory(TARGET, only_if_is_dirty=False, recursive=True)
    library.save_directory("/Game/OddsWell/Characters/MetaHumans/Common", only_if_is_dirty=False, recursive=True)

    for path in library.list_assets(TARGET, recursive=True, include_folder=False):
        data = library.find_asset_data(path)
        log(f"asset={path}|class={data.asset_class_path.asset_name}")
    log("done")
    return True


results = {name: build(name) for name in PRESETS}
unreal.log(f"ODDSWELL_MH_BUILD_SET|{results}")
