"""Run in Unreal Editor Python; use ODDSWELL_CHARACTER_MODE=verify for cold validation."""
import hashlib
import json
import math
import os
from pathlib import Path

import unreal

PLAYER = Path(__file__).resolve().parents[1]
ROOT = PLAYER.parents[3]
BASE = "/Game/OddsWell/Characters/Player"
REPORT = Path(os.environ["ODDSWELL_CHARACTER_REPORT"])
MODE = os.environ.get("ODDSWELL_CHARACTER_MODE", "import")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def preflight():
    require(MODE in ("import", "verify"), "unknown mode")
    mapping = json.loads((PLAYER / "character_unreal_import_contract.json").read_text())
    source_path = PLAYER / mapping["source_contract"]
    manifest_path = PLAYER / mapping["export_manifest"]
    require(digest(source_path) == mapping["source_contract_sha256"], "frozen source contract changed")
    require(digest(manifest_path) == mapping["export_manifest_sha256"], "export manifest changed")
    source = json.loads(source_path.read_text())
    exports = json.loads(manifest_path.read_text())["exports"]
    for name, hash_key in (("blend", "blend_sha256"), ("custody_manifest", "custody_manifest_sha256")):
        require(digest(PLAYER / source["source"][name]) == source["source"][hash_key], "Blender source changed")
    names = mapping["source_to_unreal_bone_names"]
    require(set(names) == set(source["shared_skeleton"]["bone_names"]), "source bone set differs")
    require(len(set(names.values())) == 12, "mapping must be one-to-one")
    require(all(value == key.replace(".", "_") for key, value in names.items()), "unexpected bone mapping")
    partitions = source["minimum_fbx_partition"]
    require(len(exports) == 8 and {x["file"] for x in exports} == {x["file"] for x in partitions}, "export partition differs")
    for row in exports:
        partition = next(x for x in partitions if x["file"] == row["file"])
        require(all(row[key] == value for key, value in partition.items()), "asset destination or identity differs")
        path = manifest_path.parent / row["file"]
        require(path.stat().st_size == row["bytes"] and digest(path) == row["sha256"], "FBX changed: " + row["file"])
        require((manifest_path.parent / row["sha256_record"]).read_text("ascii") == f"{row['sha256']}  {row['file']}\n", "sidecar differs")
    return mapping, source, manifest_path.parent, exports


def import_assets(source, folder, exports):
    library = unreal.EditorAssetLibrary
    require(not library.list_assets(BASE, recursive=True), "destination contains assets; overwrite refused")
    disk = ROOT / "client/OddsWell/Content/OddsWell/Characters/Player"
    require(not disk.exists() or not any(disk.rglob("*.uasset")), "destination contains files; overwrite refused")
    # FbxImportUI is the legacy import contract; do not silently route it through Interchange.
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    skeleton = None
    for row in exports:
        is_mesh = row["file"].startswith("SK_")
        options = unreal.FbxImportUI()
        import_type = unreal.FBXImportType.FBXIT_SKELETAL_MESH if is_mesh else unreal.FBXImportType.FBXIT_ANIMATION
        for key, value in {"automated_import_should_detect_type": False, "import_as_skeletal": True,
                           "import_mesh": is_mesh, "import_animations": not is_mesh, "import_materials": False,
                           "import_textures": False, "create_physics_asset": False,
                           "mesh_type_to_import": import_type, "original_import_type": import_type}.items():
            options.set_editor_property(key, value)
        if skeleton:
            options.set_editor_property("skeleton", skeleton)
        data = options.get_editor_property("skeletal_mesh_import_data" if is_mesh else "anim_sequence_import_data")
        data.set_editor_property("import_uniform_scale", 1.0)
        data.set_editor_property("convert_scene", True)
        data.set_editor_property("convert_scene_unit", True)
        if not is_mesh:
            data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
            data.set_editor_property("use_default_sample_rate", False)
            data.set_editor_property("custom_sample_rate", row["timing"]["fps"])
            data.set_editor_property("snap_to_closest_frame_boundary", True)
        task = unreal.AssetImportTask()
        for key, value in {"filename": str(folder / row["file"]), "destination_path": row["unreal_asset"].rsplit("/", 1)[0],
                           "destination_name": row["unreal_asset"].rsplit("/", 1)[1], "automated": True,
                           "replace_existing": False, "save": False, "options": options,
                           "factory": unreal.FbxFactory()}.items():
            task.set_editor_property(key, value)
        asset_tools.import_asset_tasks([task])
        asset = unreal.load_asset(row["unreal_asset"])
        require(asset is not None, "import failed: " + row["file"])
        if skeleton is None:
            skeleton = asset.get_editor_property("skeleton")
            target = source["shared_skeleton"]["unreal_asset"]
            require(library.rename_asset(skeleton.get_path_name().split(".")[0], target), "skeleton move failed")
            skeleton = unreal.load_asset(target)


def validate(mapping, source, exports):
    skel_path = source["shared_skeleton"]["unreal_asset"]
    expected = sorted([skel_path] + [r["unreal_asset"] for r in exports])
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    paths = sorted(str(x.package_name) for x in registry.get_assets_by_path(BASE, recursive=True))
    require(paths == expected, "unexpected/missing asset paths: " + repr(paths))
    require(isinstance(unreal.load_asset(skel_path), unreal.Skeleton), "shared skeleton missing")
    names = mapping["source_to_unreal_bone_names"]
    parents = {names[k]: names[v] if v else None for k, v in mapping["source_bone_parents"].items()}
    records = []
    animation_failures = []
    for row in exports:
        asset = unreal.load_asset(row["unreal_asset"])
        is_mesh = row["file"].startswith("SK_")
        require(isinstance(asset, unreal.SkeletalMesh if is_mesh else unreal.AnimSequence), "wrong asset type")
        require(asset.get_editor_property("skeleton").get_path_name().split(".")[0] == skel_path, "skeleton reference differs")
        record = {"path": row["unreal_asset"], "type": asset.get_class().get_name()}
        if is_mesh:
            bones = ["root"]
            for bone in bones:
                bones.extend(str(x) for x in asset.get_bone_children(bone) if str(x) not in bones)
            require(len(bones) == 12 and set(bones) == set(names.values()), "mesh bone set differs")
            actual = {bone: None if bone == "root" else str(asset.get_bone_parent(bone)) for bone in bones}
            require(actual == parents, "mesh bone hierarchy differs")
            bounds = asset.get_bounds()
            height = float(bounds.box_extent.z) * 2
            require(math.isfinite(height) and height > 0, "invalid mesh bounds")
            if row["import_role"] == "create_shared_skeleton_and_body_mesh":
                require(abs(height - 180.0) <= 0.5, f"body stature differs: {height} cm")
            record.update(height_cm=height, bones=bones, parents=actual)
        else:
            library = unreal.AnimationLibrary
            tracks = [str(x) for x in library.get_animation_track_names(asset)]
            # FName identity is case-insensitive; retain observed spellings in the report.
            require(len(tracks) == 12 and {x.casefold() for x in tracks} == {x.casefold() for x in names.values()},
                    "animation tracks differ: " + asset.get_name() + ": " + repr(tracks))
            seconds = float(asset.get_play_length())
            frames = library.get_num_frames(asset)
            if abs(seconds - row["timing"]["seconds"]) >= 1e-5 or frames != row["timing"]["frames"]:
                animation_failures.append(f"{asset.get_name()}: duration={seconds}, frames={frames}, expected={row['timing']}")
            max_root = 0.0
            first_rotations = {}
            rotation_span = 0.0
            for frame in range(frames + 1):
                for bone in tracks:
                    pose = library.get_bone_pose_for_frame(asset, bone, frame, False)
                    vectors = (pose.translation, pose.scale3d, pose.rotation)
                    require(all(math.isfinite(float(getattr(v, axis))) for v in vectors for axis in ("x", "y", "z")), "nonfinite pose")
                    require(math.isfinite(float(pose.rotation.w)), "nonfinite rotation")
                    rotation = tuple(float(getattr(pose.rotation, axis)) for axis in ("x", "y", "z", "w"))
                    first_rotations.setdefault(bone, rotation)
                    dot = sum(a * b for a, b in zip(rotation, first_rotations[bone]))
                    rotation_span = max(rotation_span, 2 * math.acos(min(1.0, abs(dot))))
                    if bone == "root":
                        max_root = max(max_root, abs(pose.translation.x), abs(pose.translation.y), abs(pose.translation.z))
            require(max_root < 1e-4, "root motion differs")
            require(rotation_span > 0.001, "animation has no changing bone rotations")
            record.update(seconds=seconds, frames=frames, bone_tracks=tracks, max_root_translation_cm=max_root,
                          max_rotation_change_radians=rotation_span)
            imported_settings = asset.get_editor_property("asset_import_data")
            unreal.log("ODDSWELL_ANIM_DIAGNOSTIC " + json.dumps({**record,
                "length_mode": str(imported_settings.get_editor_property("animation_length")),
                "sample_rate": imported_settings.get_editor_property("custom_sample_rate")}))
        records.append(record)
    require(not animation_failures, "animation timing differs: " + repr(animation_failures))
    return {"status": "PASS", "mode": MODE, "asset_count": 9, "meshes": 4, "animations": 4, "skeletons": 1,
            "bone_mapping": names, "assets": records, "runtime_wiring": False}


try:
    mapping, source, folder, exports = preflight()
    if MODE == "import":
        import_assets(source, folder, exports)
    result = validate(mapping, source, exports)
    if MODE == "import":
        require(unreal.EditorAssetLibrary.save_directory(BASE, only_if_is_dirty=False, recursive=True), "asset save failed")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    unreal.log("ODDSWELL_CHARACTER_IMPORT_PASS " + MODE)
except Exception as error:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"status": "FAIL", "mode": MODE, "error": str(error)}, indent=2) + "\n", encoding="utf-8")
    raise
