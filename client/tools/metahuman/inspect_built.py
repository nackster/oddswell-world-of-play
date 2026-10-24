"""Print the component tree of a built MetaHuman blueprint and the skeletons involved."""
import os
import unreal

PRESET = os.environ.get("ODDSWELL_MH_PRESET", "Isaiah")
log = lambda message: unreal.log(f"ODDSWELL_MH_INSPECT|{message}")
blueprint_path = f"/Game/OddsWell/Characters/MetaHumans/{PRESET}/Built/MHC_{PRESET}/BP_MHC_{PRESET}"
blueprint = unreal.EditorAssetLibrary.load_asset(blueprint_path)
log(f"blueprint={blueprint_path}|loaded={blueprint is not None}")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
handles = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)
for handle in handles:
    data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
    component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
    if not component:
        continue
    details = f"name={component.get_name()}|class={component.get_class().get_name()}"
    if isinstance(component, unreal.SkeletalMeshComponent):
        mesh = component.get_editor_property("skeletal_mesh_asset")
        anim = component.get_editor_property("anim_class")
        details += f"|mesh={mesh.get_path_name() if mesh else None}|skeleton={mesh.skeleton.get_path_name() if mesh and mesh.skeleton else None}|anim_class={anim.get_path_name() if anim else None}"
    if component.get_class().get_name() == "GroomComponent":
        details += f"|groom={component.get_editor_property('groom_asset').get_path_name() if component.get_editor_property('groom_asset') else None}|binding={component.get_editor_property('binding_asset').get_path_name() if component.get_editor_property('binding_asset') else None}"
    parent = component.get_attach_parent() if hasattr(component, "get_attach_parent") else None
    log(details + (f"|parent={parent.get_name()}" if parent else ""))
for name in ("SKM_MHC_{0}_BodyMesh", "MHC_{0}_Outfits", "SKM_MHC_{0}_FaceMesh"):
    folder = "Clothing" if "Outfits" in name else "Face" if "Face" in name else "Body"
    mesh = unreal.EditorAssetLibrary.load_asset(f"/Game/OddsWell/Characters/MetaHumans/{PRESET}/Built/MHC_{PRESET}/{folder}/{name.format(PRESET)}")
    if mesh:
        log(f"mesh={mesh.get_name()}|skeleton={mesh.skeleton.get_path_name() if mesh.skeleton else None}|bones={len(mesh.skeleton.get_editor_property('compatible_skeletons')) if mesh.skeleton else 0}_compatible")
log("done")
