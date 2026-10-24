"""Print each built MetaHuman outfit's material slots and their colour parameters (for the Signal Jacket tint)."""
import os
import unreal

PRESETS = os.environ.get("ODDSWELL_MH_PRESETS", "Kelvin,Lorenzo,Trey,Isaiah,Jelena,Grace,Sunita,Zuri").split(",")
log = lambda message: unreal.log(f"ODDSWELL_MH_OUTFIT|{message}")
for preset in PRESETS:
    mesh = unreal.EditorAssetLibrary.load_asset(f"/Game/OddsWell/Characters/MetaHumans/{preset}/Built/MHC_{preset}/Clothing/MHC_{preset}_Outfits")
    if not mesh:
        log(f"preset={preset}|outfit=None")
        continue
    for index, slot in enumerate(mesh.get_editor_property("materials")):
        material = slot.get_editor_property("material_interface")
        vectors = []
        if isinstance(material, unreal.MaterialInstance):
            for parameter in material.get_editor_property("vector_parameter_values"):
                info = parameter.get_editor_property("parameter_info")
                vectors.append(str(info.get_editor_property("name")))
        textures = []
        if isinstance(material, unreal.MaterialInstance):
            for parameter in material.get_editor_property("texture_parameter_values"):
                textures.append(str(parameter.get_editor_property("parameter_info").get_editor_property("name")))
        parent = material.get_editor_property("parent").get_path_name() if isinstance(material, unreal.MaterialInstance) and material.get_editor_property("parent") else None
        log(f"preset={preset}|slot={index}:{slot.get_editor_property('material_slot_name')}|material={material.get_path_name() if material else None}|parent={parent}|vectors={vectors}|textures={textures}")
log("done")
