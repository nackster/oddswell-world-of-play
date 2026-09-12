"""Hash-bound unit or motion-axis correction of the four character animation imports."""
import hashlib
import json
import os
from pathlib import Path
import unreal

PLAYER = Path(__file__).resolve().parents[1]
ROOT = PLAYER.parents[3]
REPORT = Path(os.environ["ODDSWELL_CHARACTER_REPORT"])
mode = os.environ.get("ODDSWELL_CHARACTER_CORRECTION", "units")
assert mode in ("units", "motion_axes")
if mode == "units":
    old = json.loads((PLAYER / "UnrealImport/character_import_evidence.json").read_text())
    before = [r for r in old["uassets"] if "/Animations/" in r["path"]]
    folder = PLAYER / "CharacterFBXTimingCorrection"
    manifest_name = "timed_export_custody.json"
else:
    before = json.loads((PLAYER / "UnrealImport/animation_unit_correction_evidence.json").read_text())["after"]
    folder = PLAYER / "CharacterMotionAxisCorrection"
    manifest_name = "motion_axis_custody.json"
manifest = json.loads((folder / manifest_name).read_text())
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert len(before) == 4
assert all(digest(ROOT / r["path"]) == r["sha256"] for r in before), "Refuse changes to unrecognized animation bytes"
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
skeleton = unreal.load_asset("/Game/OddsWell/Characters/Player/Skeleton/SKEL_OddsWell_Player_v1")
rows = []
for row in manifest["exports"]:
    if not row["file"].startswith("AN_"):
        continue
    source = folder / row["file"]
    assert digest(source).upper() == row["sha256"]
    existing = unreal.load_asset(row["unreal_asset"])
    # Legacy animation reimport reads settings from the existing asset.
    existing.get_editor_property("asset_import_data").set_editor_property("import_uniform_scale", 100.0)
    options = unreal.FbxImportUI()
    for key, value in {"automated_import_should_detect_type": False, "import_as_skeletal": True,
                       "import_mesh": False, "import_animations": True, "import_materials": False,
                       "import_textures": False, "create_physics_asset": False, "skeleton": skeleton,
                       "mesh_type_to_import": unreal.FBXImportType.FBXIT_ANIMATION,
                       "original_import_type": unreal.FBXImportType.FBXIT_ANIMATION}.items():
        options.set_editor_property(key, value)
    for key, value in {"convert_scene": True, "convert_scene_unit": True, "import_uniform_scale": 100.0,
                       "animation_length": unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME,
                       "use_default_sample_rate": False, "custom_sample_rate": row["timing"]["fps"],
                       "snap_to_closest_frame_boundary": True}.items():
        options.anim_sequence_import_data.set_editor_property(key, value)
    task = unreal.AssetImportTask()
    for key, value in {"filename": str(source), "destination_path": row["unreal_asset"].rsplit("/", 1)[0],
                       "destination_name": row["unreal_asset"].rsplit("/", 1)[1], "automated": True,
                       "replace_existing": True, "replace_existing_settings": True, "save": False, "options": options,
                       "factory": unreal.FbxFactory()}.items():
        task.set_editor_property(key, value)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    asset = unreal.load_asset(row["unreal_asset"])
    assert asset.get_editor_property("skeleton") == skeleton
    frames = unreal.AnimationLibrary.get_num_frames(asset)
    assert frames == row["timing"]["frames"]
    assert abs(asset.get_play_length() - row["timing"]["seconds"]) < 1e-5
    for frame in range(frames + 1):
        pose = unreal.AnimationLibrary.get_bone_pose_for_frame(asset, "root", frame, False)
        assert max(abs(getattr(pose.scale3d, axis) - 100.0) for axis in ("x", "y", "z")) < 0.001
        assert max(abs(getattr(pose.translation, axis)) for axis in ("x", "y", "z")) < 0.0001
    rows.append({"asset": row["unreal_asset"], "frames": frames, "seconds": asset.get_play_length(), "root_scale": 100})
assert len(rows) == 4
for row in rows:
    assert unreal.EditorAssetLibrary.save_asset(row["asset"], only_if_is_dirty=False)
REPORT.write_text(json.dumps({"status": "PASS", "correction": mode, "before": before, "clips": rows,
    "after": [{"path": r["path"], "sha256": digest(ROOT / r["path"])} for r in before]}, indent=2) + "\n")
unreal.log("ODDSWELL_CHARACTER_ANIMATION_CORRECTION_PASS " + mode)
