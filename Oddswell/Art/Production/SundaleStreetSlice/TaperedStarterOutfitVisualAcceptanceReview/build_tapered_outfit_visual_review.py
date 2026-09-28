"""Build or validate the evidence-only Phase 1L.5ch tapered-outfit review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "Art/Production/SundaleStreetSlice/CentralTorsoTaperStarterTopWalkProof"
SOURCE_MANIFEST = SOURCE / "central_torso_taper_starter_top_walk_custody.json"
BOARD = HERE / "Review/TaperedCombinedStarterOutfitVisualAcceptance.png"
VERDICT = HERE / "tapered_starter_outfit_visual_acceptance.json"
EXPECTED = {
    "blend": "4AE2F2B1E695F1DA7D09EB8D7F862CBADCFEB93D35413326A854A15169F03C35",
    "semantic": "8B8008D832BFB0D1C1753D24AE2AF99C5CAE6CE24B8ED30439438904A0A55A61",
    "body": "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD",
    "top": "1C7F8649211C44B9039F12902E266C438C5EF6DA4DF224D7FBD1FCF108AEC353",
    "bottom": "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170",
    "action": "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020",
}
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def receipt(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def identity(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def source_custody() -> tuple[dict, dict]:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    semantic = source["semantic"]
    checks = (
        semantic["identity_sha256"] == EXPECTED["semantic"],
        semantic["accepted_mesh_sha256"]["BODY__refined_sundale_derivative_v1"] == EXPECTED["body"],
        semantic["derived_mesh_sha256"]["starter_offwhite_top"] == EXPECTED["top"],
        semantic["accepted_mesh_sha256"]["starter_offwhite_bottom"] == EXPECTED["bottom"],
        semantic["armature"]["bone_count"] == 12,
        semantic["action"]["identity_sha256"] == EXPECTED["action"],
        receipt(SOURCE / "RefinedSundaleCentralTorsoTaperStarterTopWalk.blend") == source["files"]["blend"],
        source["files"]["blend"]["sha256"] == EXPECTED["blend"],
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5cg custody drift")
    views = {}
    for name in VIEWS:
        filename = f"After_{name}.png"
        path = SOURCE / "Review" / filename
        if receipt(path) != source["files"]["reviews"][filename]:
            raise RuntimeError(f"tapered review custody drift: {filename}")
        views[name] = receipt(path)
    return source, views


def criteria(source: dict) -> list[dict]:
    frames = source["semantic"]["deformation"]["frames"]
    zero_overlap = all(all(value == 0 for value in row["intersections"].values()) for row in frames)
    stable = source["semantic"]["deformation"]["loop_endpoint_equal"] and all(
        row["root_bone_translation_m"] == [0.0, 0.0, 0.0]
        and row["armature_translation_m"] == [0.0, 0.0, 0.0]
        for row in frames
    )
    return [
        {"criterion": "separation", "status": "PASS" if zero_overlap else "FAIL", "evidence": "The retained 21-frame ledger reports zero body/top, body/bottom and top/bottom evaluated intersections."},
        {"criterion": "neckline_shoulders_sleeves_hem", "status": "FAIL", "evidence": "The tapered views retain rounded shoulders, but the torso-to-sleeve width transition and rigid straight hem still read as one oversized rectangular slab."},
        {"criterion": "waistband_rise_crotch_legs", "status": "PASS", "evidence": "Neutral views retain the accepted waistband, balanced rise/crotch split and two tapered shorts legs."},
        {"criterion": "proportions", "status": "FAIL", "evidence": "Front/rear and both walk extremes show the top still substantially overpowering the body and shorts in lateral width."},
        {"criterion": "no_rejected_silhouettes", "status": "FAIL", "evidence": "The depth taper is visible in profile, but front/rear and opposing extremes still read as a broad box/poncho torso."},
        {"criterion": "no_exposure_or_collision", "status": "PASS" if zero_overlap else "FAIL", "evidence": "All five tapered views retain coverage and the 21-frame ledger reports zero evaluated intersections."},
        {"criterion": "stable_opposing_extremes", "status": "PASS" if stable else "FAIL", "evidence": "Tapered frames 6 and 16 retain coverage; root/armature translation is zero and frame 21 equals frame 1."},
    ]


def build_board(result: dict) -> None:
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (2400, 1840), (24, 26, 31))
    draw = ImageDraw.Draw(canvas)
    positions = ((0, 0), (800, 0), (1600, 0), (400, 800), (1200, 800))
    labels = ("TAPERED NEUTRAL FRONT", "TAPERED NEUTRAL REAR", "TAPERED NEUTRAL PROFILE", "TAPERED WALK EXTREME — FRAME 6", "TAPERED WALK EXTREME — FRAME 16")
    for name, position, label in zip(VIEWS, positions, labels):
        image = Image.open(SOURCE / "Review" / f"After_{name}.png").convert("RGB")
        if image.size != (800, 800):
            raise RuntimeError(f"unexpected tapered view size: {name} {image.size}")
        canvas.paste(image, position)
        draw.rectangle((position[0], position[1], position[0] + 800, position[1] + 34), fill=(24, 26, 31))
        draw.text((position[0] + 12, position[1] + 10), label, fill=(245, 245, 245))
    draw.rectangle((0, 1600, 2400, 1840), fill=(58, 23, 28))
    draw.text((30, 1630), f"PHASE 1L.5ch VERDICT: {result['verdict']}", fill=(255, 214, 214))
    draw.text((30, 1670), "FAILED: neckline/shoulders/sleeves/hem; proportions; no rejected silhouettes", fill=(255, 235, 235))
    draw.text((30, 1710), "SMALLEST CORRECTION: taper only the central front/rear lateral silhouette toward the waist.", fill=(255, 235, 235))
    draw.text((30, 1750), "Exact 1L.5cg body, tapered top, shorts, armature and action custody retained.", fill=(225, 225, 225))
    draw.text((30, 1790), "This rejection stops export/import preparation; no runtime, final-art or beta-readiness claim.", fill=(225, 225, 225))
    canvas.save(BOARD, format="PNG", optimize=False, compress_level=9)


def expected_result(source: dict, views: dict) -> dict:
    checks = criteria(source)
    verdict = "ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION" if all(row["status"] == "PASS" for row in checks) else "REJECTED_VISUAL_CORRECTION_REQUIRED"
    result = {
        "phase": "Phase 1L.5ch tapered combined starter-outfit offline visual acceptance review",
        "verdict": verdict,
        "criteria": checks,
        "smallest_correction": "Reshape only the top central front/rear lateral silhouette into a waist-tapered panel while preserving shoulders, sleeves, depth taper, openings and every other accepted identity.",
        "source_custody": {
            "blend_sha256": EXPECTED["blend"],
            "semantic_identity_sha256": EXPECTED["semantic"],
            "mesh_sha256": {"body": EXPECTED["body"], "top": EXPECTED["top"], "bottom": EXPECTED["bottom"]},
            "armature_bone_count": 12,
            "action_identity_sha256": EXPECTED["action"],
            "tapered_view_files": views,
            "frame_ledger_identity_sha256": identity(source["semantic"]["deformation"]),
        },
        "boundaries": {"geometry_changed": 0, "weights_changed": 0, "topology_changed": 0, "materials_changed": 0, "action_changed": 0, "skeleton_changed": 0, "export_changed": 0, "unreal_changed": 0, "client_changed": 0, "package_inputs_changed": 0, "runtime_claim": False, "final_art_claim": False, "beta_readiness_claim": False},
    }
    result["identity_sha256"] = identity(result)
    return result


def files() -> dict:
    return {"board": receipt(BOARD), "builder": receipt(Path(__file__)), "provenance": receipt(HERE / "PROVENANCE.md")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    source, views = source_custody()
    result = expected_result(source, views)
    if result["verdict"] not in {"ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION", "REJECTED_VISUAL_CORRECTION_REQUIRED"}:
        raise RuntimeError("invalid verdict state")
    if args.validate:
        result["files"] = files()
        recorded = json.loads(VERDICT.read_text(encoding="utf-8"))
        if recorded != result:
            raise RuntimeError("recorded tapered review drift")
        print(f"PHASE_1L5CH_VALIDATE_PASS {recorded['verdict']} {recorded['identity_sha256']} {sha256(BOARD)}")
        return
    build_board(result)
    result["files"] = files()
    VERDICT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PHASE_1L5CH_BUILD_PASS {result['verdict']} {result['identity_sha256']} {sha256(BOARD)}")


if __name__ == "__main__":
    main()
