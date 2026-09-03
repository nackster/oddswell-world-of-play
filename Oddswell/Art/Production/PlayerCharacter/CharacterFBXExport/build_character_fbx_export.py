import hashlib
import importlib.util
import json
import os
import shutil
import sys
import datetime
from pathlib import Path

import bpy
import io_scene_fbx.export_fbx_bin as export_fbx_bin
import io_scene_fbx.fbx_utils as fbx_utils


ROOT = Path(__file__).resolve().parent
PLAYER_ROOT = ROOT.parent
SOURCE_DIR = PLAYER_ROOT / "LandingActionCandidate"
SOURCE_BLEND = SOURCE_DIR / "LandingActionCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "landing_action_custody.json"
SOURCE_BUILDER = SOURCE_DIR / "build_landing_action_candidate.py"
CONTRACT_PATH = PLAYER_ROOT / "character_fbx_unreal_contract.json"
MANIFEST_PATH = ROOT / "character_fbx_export_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

SOURCE_HASHES = {
    SOURCE_BLEND: "B837C11190DE64F5848F4880FA0098473DFAA3C8BA4E5D8564566587E11721FE",
    SOURCE_MANIFEST: "499A4622BF744B936513BD6BC42309A3C83FB1D52DA70C4196FB5D4C2B898ABC",
    SOURCE_BUILDER: "859E9F9FC5E212013B8567CBB4711750AAFE1EDE3F70E5E30033D8E88FF7D42E",
    CONTRACT_PATH: "3DAA1D94A19148F03D31682D15B2FA40D9D43133008A1DA099097FCC4AAD88C6",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAND = load_module("oddswell_landing_source", SOURCE_BUILDER)


class FixedDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 9, 3, 0, 0, 0, tzinfo=tz)


export_fbx_bin.datetime.datetime = FixedDateTime


def stable_fbx_uuid(key):
    uuid = fbx_utils._keys_to_uuids.get(key)
    if uuid is None:
        if isinstance(key, int) and 0 <= key < 2**63:
            value = key
        else:
            value = int.from_bytes(hashlib.sha256(repr(key).encode("utf-8")).digest()[:8], "big") & (2**63 - 1)
        while value in fbx_utils._uuids_to_keys and fbx_utils._uuids_to_keys[value] != key:
            value += 1
        uuid = fbx_utils.UUID(value)
        fbx_utils._keys_to_uuids[key] = uuid
        fbx_utils._uuids_to_keys[uuid] = key
    return uuid


fbx_utils.get_fbx_uuid_from_key = stable_fbx_uuid
export_fbx_bin.get_fbx_uuid_from_key = stable_fbx_uuid


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def source_custody():
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("PYTHONHASHSEED=0 is required for deterministic FBX object identifiers")
    for path, expected in SOURCE_HASHES.items():
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"source custody differs: {path}")
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if manifest["semantic"]["identity_sha256"] != contract["source"]["semantic_sha256"]:
        raise RuntimeError("source semantic custody differs")
    return manifest, contract


def select_only(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def common_export(path, object_types, bake_anim):
    bpy.ops.export_scene.fbx(
        filepath=str(path),
        use_selection=True,
        object_types=object_types,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        use_space_transform=True,
        bake_space_transform=False,
        axis_forward="-Y",
        axis_up="Z",
        use_mesh_modifiers=True,
        mesh_smooth_type="OFF",
        use_subsurf=False,
        use_mesh_edges=False,
        use_tspace=False,
        primary_bone_axis="Y",
        secondary_bone_axis="X",
        armature_nodetype="NULL",
        use_armature_deform_only=False,
        add_leaf_bones=False,
        bake_anim=bake_anim,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,
        path_mode="STRIP",
        embed_textures=False,
        batch_mode="OFF",
        use_batch_own_dir=False,
    )


def export_pass(directory, contract):
    directory.mkdir(parents=True, exist_ok=True)
    armature = bpy.data.objects[contract["shared_skeleton"]["source_object"]]
    outputs = {}
    for partition in contract["minimum_fbx_partition"]:
        path = directory / partition["file"]
        contents = partition["contents"]
        if partition["file"].startswith("SK_"):
            mesh = bpy.data.objects[contents[1]]
            select_only([armature, mesh])
            common_export(path, {"ARMATURE", "MESH"}, False)
        else:
            action = bpy.data.actions[contents[1]]
            select_only([armature])
            armature.animation_data.action = action
            bpy.context.scene.frame_start = int(action.frame_range[0])
            bpy.context.scene.frame_end = int(action.frame_range[1])
            common_export(path, {"ARMATURE"}, True)
        outputs[path.name] = sha256(path)
    return outputs


def write_outputs(first_dir, hashes, contract, source_manifest):
    if first_dir.resolve() != ROOT.resolve():
        for old in ROOT.glob("*.fbx"):
            old.unlink()
    for old in ROOT.glob("*.fbx.sha256"):
        old.unlink()
    records = []
    for partition in contract["minimum_fbx_partition"]:
        filename = partition["file"]
        destination = ROOT / filename
        source = first_dir / filename
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        digest = hashes[filename]
        sidecar = ROOT / partition["sha256_record"]
        sidecar.write_text(f"{digest}  {filename}\n", encoding="ascii", newline="\n")
        records.append({
            "file": filename,
            "bytes": destination.stat().st_size,
            "sha256": digest,
            "sha256_record": sidecar.name,
            "sha256_record_sha256": sha256(sidecar),
            "contents": partition["contents"],
            "unreal_asset": partition["unreal_asset"],
            "import_role": partition["import_role"],
        })
    evidence = {
        "phase": "1L.5bs",
        "status": "deterministic_eight_file_fbx_export_source_custody_only_not_unreal_import",
        "blender_version": bpy.app.version_string,
        "source": contract["source"],
        "contract_sha256": SOURCE_HASHES[CONTRACT_PATH],
        "shared_skeleton": contract["shared_skeleton"],
        "mesh_identities": contract["mesh_identities"],
        "animation_identities": contract["animation_identities"],
        "coordinate_contract": contract["coordinate_contract"],
        "root_translation_zero": all(
            value == 0.0
            for key in ("preserved_walk_action", "preserved_run_action", "preserved_jump_action", "landing_action")
            for value in source_manifest["semantic"][key]["root_translation_m"]
        ),
        "repeat_export_binary_hashes_equal": True,
        "exports": records,
        "boundaries": {
            "fbx": 8,
            "sha256_sidecars": 8,
            "uasset": 0,
            "unreal_imports": 0,
            "runtime_changes": 0,
            "client_changes": 0,
            "package_input_changes": 0,
            "root_motion": 0,
            "new_bones": 0,
            "leaf_bones": 0,
            "new_actions": 0,
            "new_geometry_or_clothing": 0,
            "final_art_claim": False,
            "readiness_claim": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def validate_outputs():
    source_manifest, contract = source_custody()
    LAND.validate_outputs()
    expected = {item["file"] for item in contract["minimum_fbx_partition"]}
    actual = {path.name for path in ROOT.glob("*.fbx")}
    if actual != expected or len(actual) != 8:
        raise RuntimeError("exact eight-file FBX partition differs")
    sidecars = {path.name for path in ROOT.glob("*.fbx.sha256")}
    if sidecars != {item["sha256_record"] for item in contract["minimum_fbx_partition"]}:
        raise RuntimeError("exact eight SHA-256 sidecars differ")
    evidence = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if evidence["source"] != contract["source"] or not evidence["root_translation_zero"]:
        raise RuntimeError("source or root-translation evidence differs")
    if evidence["shared_skeleton"] != contract["shared_skeleton"] or len(evidence["exports"]) != 8:
        raise RuntimeError("shared skeleton or export evidence differs")
    for record in evidence["exports"]:
        path = ROOT / record["file"]
        sidecar = ROOT / record["sha256_record"]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"FBX identity differs: {path.name}")
        if sidecar.read_text(encoding="ascii") != f"{record['sha256']}  {record['file']}\n" or sha256(sidecar) != record["sha256_record_sha256"]:
            raise RuntimeError(f"sidecar identity differs: {sidecar.name}")
    if any(path.suffix.lower() == ".uasset" for path in ROOT.rglob("*")):
        raise RuntimeError("UAsset output is forbidden")
    print("ODDSWELL_CHARACTER_FBX_EXPORT_VALIDATION|result=PASS|source=exact_1L.5bq|skeleton=1|bones=12|meshes=4|animations=4|fbx=8|sidecars=8|repeat_hashes=true|root_translation=0|leaf_bones=0|uasset=0|imports=0|runtime=0|client=0")


def build():
    source_manifest, contract = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    LAND.validate_outputs()
    first_hashes = export_pass(ROOT, contract)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    LAND.validate_outputs()
    second_hashes = export_pass(ROOT, contract)
    if first_hashes != second_hashes:
        raise RuntimeError("repeat FBX binary hashes differ")
    write_outputs(ROOT, second_hashes, contract, source_manifest)
    validate_outputs()
    print(f"ODDSWELL_CHARACTER_FBX_EXPORT_BUILD|result=PASS|fbx=8|sidecars=8|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false")


def main():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        validate_outputs()
        return
    build()


if __name__ == "__main__":
    main()
