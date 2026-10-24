"""Probe MetaHuman Creator availability: create one character, try the cloud steps, report, clean up."""
import unreal

log = lambda m: unreal.log(f"ODDSWELL_MH_PROBE|{m}")
subsystem = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
character = tools.create_asset(asset_name="MH_Probe", package_path="/Game/OddsWell/Characters/MetaHumans/Probe",
                               asset_class=unreal.MetaHumanCharacter, factory=unreal.new_object(type=unreal.MetaHumanCharacterFactoryNew))
log(f"created={character is not None}")
if character and subsystem.try_add_object_to_edit(character=character):
    log("editing=true")
    params = unreal.MetaHumanCharacterTextureRequestParams()
    params.blocking = True
    params.report_progress = False
    subsystem.request_texture_sources(character=character, params=params)
    log(f"high_res_textures={character.has_high_resolution_textures}")
    rig = unreal.MetaHumanCharacterAutoRiggingRequestParams()
    rig.blocking = True
    rig.report_progress = False
    rig.rig_type = unreal.MetaHumanRigType.JOINTS_ONLY
    subsystem.request_auto_rigging(character=character, params=rig)
    log(f"can_build={subsystem.can_build_meta_human(character=character)}")
    subsystem.remove_object_to_edit(character=character)
unreal.EditorAssetLibrary.delete_directory("/Game/OddsWell/Characters/MetaHumans/Probe")
log("done")
