"""Create the local shared character material once in Unreal Editor Python."""
import unreal

PATH = "/Game/OddsWell/Characters/Player/Materials"
NAME = "M_OddsWell_Character"
assert not unreal.EditorAssetLibrary.does_asset_exist(PATH + "/" + NAME), "Refuse material overwrite"
material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    NAME, PATH, unreal.Material, unreal.MaterialFactoryNew())
assert material
color = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionVectorParameter, -300, 0)
color.set_editor_property("parameter_name", "Color")
color.set_editor_property("default_value", unreal.LinearColor(0.92, 0.90, 0.82, 1))
roughness = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionConstant, -300, 160)
roughness.set_editor_property("r", 0.85)
assert unreal.MaterialEditingLibrary.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
assert unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
material.set_editor_property("used_with_skeletal_mesh", True)
unreal.MaterialEditingLibrary.recompile_material(material)
assert unreal.EditorAssetLibrary.save_loaded_asset(material)
unreal.log("ODDSWELL_CHARACTER_MATERIAL_PASS")
