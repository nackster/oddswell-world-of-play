"""Build or validate the evidence-only Phase 1L.5cf corrected-outfit review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "Art/Production/SundaleStreetSlice/RoundedStarterTopSilhouetteWalkProof"
SOURCE_MANIFEST = SOURCE / "rounded_starter_top_walk_custody.json"
BOARD = HERE / "Review/CorrectedCombinedStarterOutfitVisualAcceptance.png"
VERDICT = HERE / "corrected_starter_outfit_visual_acceptance.json"
EXPECTED = {
    "blend": "5E4C42EA159EAA4777B3A9D087D1FDAB0AF417C27F3129B022F31E9A2D26F788",
    "semantic": "7F5D0C4606DF10318372771F7D431AC3884B7858F5304BB22D198BC63301F220",
    "body": "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD",
    "top": "A9DD780C47AC50F1383BA23F4393167E0EC51C62616D868E421C5CD5C3CAAADB",
    "bottom": "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170",
    "action": "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020",
}
VIEWS = ["Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear"]


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
        receipt(SOURCE / "RefinedSundaleRoundedStarterTopWalk.blend") == source["files"]["blend"],
        source["files"]["blend"]["sha256"] == EXPECTED["blend"],
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5ce custody drift")
    views = {}
    for name in VIEWS:
        filename = f"After_{name}.png"
        path = SOURCE / "Review" / filename
        if receipt(path) != source["files"]["reviews"][filename]:
            raise RuntimeError(f"corrected review custody drift: {filename}")
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
        {"criterion": "neckline_shoulders_sleeves_hem", "status": "FAIL", "evidence": "Corrected neutral views show rounded shoulders and shorter sleeves, but the central torso remains a flat slab with a rigid straight hem rather than believable cloth continuity."},
        {"criterion": "waistband_rise_crotch_legs", "status": "PASS", "evidence": "Corrected neutral views retain the previously evidenced waistband, balanced rise/crotch split and two tapered legs."},
        {"criterion": "proportions", "status": "FAIL", "evidence": "The corrected top still dominates the accepted body and shorts through excessive flat upper-torso volume in front/rear/profile."},
        {"criterion": "no_rejected_silhouettes", "status": "FAIL", "evidence": "The armor corners are removed, but front/rear/profile still read as a broad box/poncho torso, so the unchanged rejection criterion does not pass."},
        {"criterion": "no_exposure_or_collision", "status": "PASS" if zero_overlap else "FAIL", "evidence": "All corrected views retain coverage and the 21-frame ledger reports zero evaluated intersections."},
        {"criterion": "stable_opposing_extremes", "status": "PASS" if stable else "FAIL", "evidence": "Corrected frames 6 and 16 retain coverage; root/armature translation is zero and frame 21 equals frame 1."},
    ]


def build_board(result: dict) -> None:
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (2400, 1840), (24, 26, 31))
    draw = ImageDraw.Draw(canvas)
    positions = [(0, 0), (800, 0), (1600, 0), (400, 800), (1200, 800)]
    labels = ["CORRECTED NEUTRAL FRONT", "CORRECTED NEUTRAL REAR", "CORRECTED NEUTRAL PROFILE", "CORRECTED WALK EXTREME — FRAME 6", "CORRECTED WALK EXTREME — FRAME 16"]
    for name, pos, label in zip(VIEWS, positions, labels):
        image = Image.open(SOURCE / "Review" / f"After_{name}.png").convert("RGB")
        if image.size != (800, 800):
            raise RuntimeError(f"unexpected corrected view size: {name} {image.size}")
        canvas.paste(image, pos)
        draw.rectangle((pos[0], pos[1], pos[0] + 800, pos[1] + 34), fill=(24, 26, 31))
        draw.text((pos[0] + 12, pos[1] + 10), label, fill=(245, 245, 245))
    draw.rectangle((0, 1600, 2400, 1840), fill=(58, 23, 28))
    draw.text((30, 1630), f"PHASE 1L.5cf VERDICT: {result['verdict']}", fill=(255, 214, 214))
    draw.text((30, 1670), "FAILED: neckline/shoulders/sleeves/hem; proportions; no rejected silhouettes", fill=(255, 235, 235))
    draw.text((30, 1710), "SMALLEST CORRECTION: reshape only central front/rear torso depth into tapered body-following volume.", fill=(255, 235, 235))
    draw.text((30, 1750), "Exact 1L.5ce body, corrected top, shorts, armature and action custody retained.", fill=(225, 225, 225))
    draw.text((30, 1790), "This rejection stops export/import preparation; no runtime, final-art or beta-readiness claim.", fill=(225, 225, 225))
    canvas.save(BOARD, format="PNG", optimize=False, compress_level=9)


def expected_result(source: dict, views: dict) -> dict:
    checks = criteria(source)
    verdict = "ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION" if all(row["status"] == "PASS" for row in checks) else "REJECTED_VISUAL_CORRECTION_REQUIRED"
    result = {
        "phase": "Phase 1L.5cf corrected combined starter-outfit offline visual acceptance review",
        "verdict": verdict,
        "criteria": checks,
        "smallest_correction": "Reshape only the top central front/rear torso depth into tapered body-following volume while preserving the corrected shoulders/sleeves/sides and every other accepted identity.",
        "source_custody": {"blend_sha256": EXPECTED["blend"], "semantic_identity_sha256": EXPECTED["semantic"], "mesh_sha256": {"body": EXPECTED["body"], "top": EXPECTED["top"], "bottom": EXPECTED["bottom"]}, "armature_bone_count": 12, "action_identity_sha256": EXPECTED["action"], "corrected_view_files": views, "frame_ledger_identity_sha256": identity(source["semantic"]["deformation"])},
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
            raise RuntimeError("recorded corrected review drift")
        print(f"PHASE_1L5CF_VALIDATE_PASS {recorded['verdict']} {recorded['identity_sha256']} {sha256(BOARD)}")
        return
    build_board(result)
    result["files"] = files()
    VERDICT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PHASE_1L5CF_BUILD_PASS {result['verdict']} {result['identity_sha256']} {sha256(BOARD)}")


if __name__ == "__main__":
    main()
