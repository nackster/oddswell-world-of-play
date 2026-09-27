"""Build or validate the evidence-only Phase 1L.5cd outfit review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "Art/Production/SundaleStreetSlice/TailoredStarterTopWalkProof"
SOURCE_MANIFEST = SOURCE / "tailored_starter_top_walk_custody.json"
BOARD = HERE / "Review/CombinedStarterOutfitVisualAcceptance.png"
VERDICT = HERE / "starter_outfit_visual_acceptance.json"
EXPECTED = {
    "blend": "253E2680478A30133A0DC49614D9C997FEC06B70B42C470372CD0AF0CF44D7EA",
    "body": "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD",
    "top": "20DEC799B15A77DC97EB4CCE521A84362AB952725ACD38C028918AABEC29C73C",
    "bottom": "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170",
    "armature_bones": 12,
    "action": "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020",
}
VIEWS = ["Front.png", "Rear.png", "Profile.png", "WalkExtremeFront.png", "WalkExtremeRear.png"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def receipt(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def identity(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def source_custody() -> tuple[dict, dict]:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    semantic = source["semantic"]
    assert sha256(SOURCE / "RefinedSundaleTailoredStarterTopWalk.blend") == EXPECTED["blend"]
    assert semantic["accepted_mesh_sha256"]["BODY__refined_sundale_derivative_v1"] == EXPECTED["body"]
    assert semantic["derived_mesh_sha256"]["starter_offwhite_top"] == EXPECTED["top"]
    assert semantic["accepted_mesh_sha256"]["starter_offwhite_bottom"] == EXPECTED["bottom"]
    assert semantic["armature"]["bone_count"] == EXPECTED["armature_bones"]
    assert semantic["action"]["identity_sha256"] == EXPECTED["action"]
    receipts = {}
    for name in VIEWS:
        path = SOURCE / "Review" / name
        receipt = source["files"]["reviews"][name]
        assert path.stat().st_size == receipt["bytes"] and sha256(path) == receipt["sha256"]
        receipts[name] = receipt
    return source, receipts


def criteria(source: dict) -> list[dict]:
    deformation = source["semantic"]["deformation"]
    frames = deformation["frames"]
    zero_overlap = all(all(value == 0 for value in row["intersections"].values()) for row in frames)
    stable = deformation["loop_endpoint_equal"] and all(
        row["root_bone_translation_m"] == [0.0, 0.0, 0.0]
        and row["armature_translation_m"] == [0.0, 0.0, 0.0]
        for row in frames
    )
    return [
        {"criterion": "separation", "status": "PASS" if zero_overlap else "FAIL", "evidence": "21/21 integer frames report zero body/top, body/bottom and top/bottom evaluated intersections."},
        {"criterion": "neckline_shoulders_sleeves_hem", "status": "FAIL", "evidence": "Neutral front/rear/profile show an over-wide, nearly orthogonal shoulder-to-sleeve transition and flat torso volume; the top remains a coarse shell rather than believable cloth."},
        {"criterion": "waistband_rise_crotch_legs", "status": "PASS", "evidence": "Neutral front/rear/profile retain readable waistband, balanced rise/crotch split and two distinct tapered legs."},
        {"criterion": "proportions", "status": "FAIL", "evidence": "The top span and straight side profile overpower the accepted body and fitted shorts, producing an unbalanced upper-body proportion."},
        {"criterion": "no_rejected_silhouettes", "status": "FAIL", "evidence": "Front/rear/profile still read as a broad box/armor-like top silhouette, which is explicitly rejected for visual acceptance."},
        {"criterion": "no_exposure_or_collision", "status": "PASS" if zero_overlap else "FAIL", "evidence": "All five retained views show body coverage; the 21-frame ledger reports zero evaluated intersections."},
        {"criterion": "stable_opposing_extremes", "status": "PASS" if stable else "FAIL", "evidence": "Frames 6 and 16 retain garment coverage; root and armature translation are zero and frame 21 equals frame 1."},
    ]


def build_board(receipts: dict, result: dict) -> None:
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (2400, 1840), (24, 26, 31))
    draw = ImageDraw.Draw(canvas)
    positions = [(0, 0), (800, 0), (1600, 0), (400, 800), (1200, 800)]
    labels = ["NEUTRAL FRONT", "NEUTRAL REAR", "NEUTRAL PROFILE", "WALK EXTREME — FRAME 6", "WALK EXTREME — FRAME 16"]
    for name, pos, label in zip(VIEWS, positions, labels):
        image = Image.open(SOURCE / "Review" / name).convert("RGB")
        assert image.size == (800, 800)
        canvas.paste(image, pos)
        draw.rectangle((pos[0], pos[1], pos[0] + 800, pos[1] + 34), fill=(24, 26, 31))
        draw.text((pos[0] + 12, pos[1] + 10), label, fill=(245, 245, 245))
    verdict = result["verdict"]
    draw.rectangle((0, 1600, 2400, 1840), fill=(58, 23, 28))
    draw.text((30, 1630), f"PHASE 1L.5cd VERDICT: {verdict}", fill=(255, 214, 214))
    draw.text((30, 1670), "FAILED: neckline/shoulders/sleeves/hem; proportions; no rejected silhouettes", fill=(255, 235, 235))
    draw.text((30, 1710), "SMALLEST CORRECTION: reshape only the top shoulder/sleeve/side profile into rounded body-conforming drape.", fill=(255, 235, 235))
    draw.text((30, 1750), "Evidence-only review. Exact 1L.5cc body, top, shorts, armature and action custody retained.", fill=(225, 225, 225))
    draw.text((30, 1790), "This rejection stops technical export/import preparation; no runtime, final-art or beta-readiness claim.", fill=(225, 225, 225))
    canvas.save(BOARD, format="PNG", optimize=False, compress_level=9)


def expected_result(source: dict, receipts: dict) -> dict:
    checks = criteria(source)
    verdict = "ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION" if all(row["status"] == "PASS" for row in checks) else "REJECTED_VISUAL_CORRECTION_REQUIRED"
    result = {
        "phase": "Phase 1L.5cd combined starter-outfit offline visual acceptance review",
        "verdict": verdict,
        "criteria": checks,
        "smallest_correction": "Replace only the top silhouette/profile with rounded, body-conforming shoulder, sleeve and side shaping; preserve the exact body, shorts, skeleton and walk action.",
        "source_custody": {"blend_sha256": EXPECTED["blend"], "mesh_sha256": {"body": EXPECTED["body"], "top": EXPECTED["top"], "bottom": EXPECTED["bottom"]}, "armature_bone_count": 12, "action_identity_sha256": EXPECTED["action"], "review_files": receipts},
        "boundaries": {"mesh_changed": 0, "weights_changed": 0, "materials_changed": 0, "action_changed": 0, "skeleton_changed": 0, "unreal_changed": 0, "client_changed": 0, "package_inputs_changed": 0, "runtime_claim": False, "final_art_claim": False, "beta_readiness_claim": False},
    }
    result["identity_sha256"] = identity(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    source, receipts = source_custody()
    result = expected_result(source, receipts)
    assert result["verdict"] == "REJECTED_VISUAL_CORRECTION_REQUIRED"
    if args.validate:
        recorded = json.loads(VERDICT.read_text(encoding="utf-8"))
        result["files"] = {"board": receipt(BOARD), "builder": receipt(Path(__file__)), "provenance": receipt(HERE / "PROVENANCE.md")}
        assert recorded == result and sha256(BOARD) == recorded["files"]["board"]["sha256"]
        print(f"PHASE_1L5CD_VALIDATE_PASS {recorded['identity_sha256']} {sha256(BOARD)}")
        return
    build_board(receipts, result)
    result["files"] = {"board": receipt(BOARD), "builder": receipt(Path(__file__)), "provenance": receipt(HERE / "PROVENANCE.md")}
    # The file receipt is outside the semantic identity so rebuilds remain stable.
    VERDICT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PHASE_1L5CD_BUILD_PASS {result['identity_sha256']} {sha256(BOARD)}")


if __name__ == "__main__":
    main()
