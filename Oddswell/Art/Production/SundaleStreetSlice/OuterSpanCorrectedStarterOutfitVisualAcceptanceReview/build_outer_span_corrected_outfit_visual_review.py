"""Build or validate the evidence-only Phase 1L.5cl outfit review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "Art/Production/SundaleStreetSlice/OuterShoulderSleeveSpanCorrectionWalkProof"
SOURCE_MANIFEST = SOURCE / "outer_shoulder_sleeve_span_correction_walk_custody.json"
WAIST_SOURCE = ROOT / "Art/Production/SundaleStreetSlice/LateralWaistTaperStarterTopWalkProof"
WAIST_MANIFEST = WAIST_SOURCE / "lateral_waist_taper_starter_top_walk_custody.json"
BOARD = HERE / "Review/OuterSpanCorrectedCombinedStarterOutfitVisualAcceptance.png"
VERDICT = HERE / "outer_span_corrected_starter_outfit_visual_acceptance.json"
EXPECTED = {
    "blend": "5A452DCF36B861D4271D6D9CD1303161330C112BCEBD32AF2548F2C2F35161C7",
    "semantic": "BB7BE19929C7C89270CC39D029FBE21D9D8140E57BB2A91B55DE96DCC75F8F18",
    "body": "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD",
    "top": "4D290EAEF2CDC94F6F68982C0166FF5E7B85C6B36200170FF2B24AFF4F379FBE",
    "bottom": "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170",
    "action": "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020",
    "waist_semantic": "38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD",
}
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")
MAXIMUM_TOP_TO_BODY_WIDTH_RATIO = 1.4
MINIMUM_WAIST_INSET_RATIO = 0.08
BOUNDED_CORRECTION = (
    "Correct only the top shoulder-cap, sleeve and hem articulation so the exact retained neutral and "
    "opposing-extreme views show a continuous garment silhouette without rigid raised plates or hem "
    "collapse; preserve custody, the accepted width ratio, topology, four openings and all non-target assets."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def receipt(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def identity(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def source_custody() -> tuple[dict, dict, dict]:
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    waist = json.loads(WAIST_MANIFEST.read_text(encoding="utf-8"))
    semantic = source["semantic"]
    checks = (
        semantic["identity_sha256"] == EXPECTED["semantic"],
        semantic["accepted_mesh_sha256"]["BODY__refined_sundale_derivative_v1"] == EXPECTED["body"],
        semantic["derived_mesh_sha256"]["starter_offwhite_top"] == EXPECTED["top"],
        semantic["accepted_mesh_sha256"]["starter_offwhite_bottom"] == EXPECTED["bottom"],
        semantic["armature"]["bone_count"] == 12,
        semantic["action"]["identity_sha256"] == EXPECTED["action"],
        receipt(SOURCE / "RefinedSundaleOuterShoulderSleeveSpanCorrectedTopWalk.blend") == source["files"]["blend"],
        source["files"]["blend"]["sha256"] == EXPECTED["blend"],
        semantic["accepted_phase_1l5ci"]["identity_sha256"] == EXPECTED["waist_semantic"],
        waist["semantic"]["identity_sha256"] == EXPECTED["waist_semantic"],
        semantic["boundaries"]["final_acceptance_verdict"] is None,
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5ck custody drift")
    views = {}
    for name in VIEWS:
        filename = f"After_{name}.png"
        path = SOURCE / "Review" / filename
        if receipt(path) != source["files"]["reviews"][filename]:
            raise RuntimeError(f"outer-span-corrected review custody drift: {filename}")
        views[name] = receipt(path)
    return source, waist, views


def measurements(source: dict, waist: dict) -> dict:
    semantic = source["semantic"]
    frame = semantic["deformation"]["frames"][0]
    body_bounds = frame["bounds_m"]["BODY__refined_sundale_derivative_v1"]
    top_bounds = frame["bounds_m"]["starter_offwhite_top"]
    body_width = body_bounds["max"][0] - body_bounds["min"][0]
    top_width = top_bounds["max"][0] - top_bounds["min"][0]
    widths = waist["semantic"]["correction"]["half_width_m"]
    waist_inset = (widths["upper"]["derived"] - widths["lower"]["derived"]) / widths["upper"]["derived"]
    top = semantic["topology"]["starter_offwhite_top"]
    bottom = semantic["topology"]["starter_offwhite_bottom"]
    roles = semantic["panel_roles"]
    return {
        "neutral_body_width_m": round(body_width, 9),
        "neutral_top_width_m": round(top_width, 9),
        "top_to_body_width_ratio": round(top_width / body_width, 9),
        "maximum_top_to_body_width_ratio": MAXIMUM_TOP_TO_BODY_WIDTH_RATIO,
        "waist_inset_ratio": round(waist_inset, 9),
        "minimum_waist_inset_ratio": MINIMUM_WAIST_INSET_RATIO,
        "top_contract_pass": top["connected_components"] == 1 and top["boundary_loops"] == 4 and top["non_manifold_edges_excluding_openings"] == 0 and all(roles.values()),
        "shorts_contract_pass": bottom["connected_components"] == 1 and bottom["boundary_loops"] == 3 and bottom["non_manifold_edges_excluding_openings"] == 0,
    }


def visual_observations(views: dict) -> dict:
    """Record the fail-closed human review of the exact custody-checked view set."""
    return {
        "view_identity_sha256": identity(views),
        "neckline_shoulders_sleeves_hem": {
            "pass": False,
            "views": ["Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear"],
            "evidence": (
                "The exact views show rigid squared shoulder caps, abrupt sleeve blocks and a hem that "
                "lifts or folds into disconnected-looking planes at both opposing walk extremes."
            ),
        },
        "no_rejected_silhouettes": {
            "pass": False,
            "views": ["Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear"],
            "evidence": (
                "Although the measured width and waist-taper thresholds pass, the neutral profile remains "
                "slab-like and both walk extremes retain an armor-like, plate-folded top silhouette."
            ),
        },
        "stable_opposing_extremes": {
            "pass": False,
            "views": ["WalkExtremeFront", "WalkExtremeRear"],
            "evidence": (
                "Mechanical loop and translation checks pass, but frames 6 and 16 do not support "
                "qualitative garment stability: shoulder caps rise into plates and the hem collapses unevenly."
            ),
        },
    }


def criteria(source: dict, measured: dict, observations: dict) -> list[dict]:
    semantic = source["semantic"]
    frames = semantic["deformation"]["frames"]
    zero_overlap = all(all(value == 0 for value in row["intersections"].values()) for row in frames)
    stable = semantic["deformation"]["loop_endpoint_equal"] and all(
        row["root_bone_translation_m"] == [0.0, 0.0, 0.0]
        and row["armature_translation_m"] == [0.0, 0.0, 0.0]
        for row in frames
    )
    proportion_pass = measured["top_to_body_width_ratio"] <= measured["maximum_top_to_body_width_ratio"]
    taper_pass = measured["waist_inset_ratio"] >= measured["minimum_waist_inset_ratio"]
    status = lambda passed: "PASS" if passed else "FAIL"
    ratio = measured["top_to_body_width_ratio"]
    ratio_limit = measured["maximum_top_to_body_width_ratio"]
    neckline = observations["neckline_shoulders_sleeves_hem"]
    silhouette = observations["no_rejected_silhouettes"]
    opposing = observations["stable_opposing_extremes"]
    neckline_pass = measured["top_contract_pass"] and proportion_pass and neckline["pass"]
    silhouette_pass = measured["top_contract_pass"] and taper_pass and proportion_pass and silhouette["pass"]
    opposing_pass = stable and opposing["pass"]
    return [
        {"criterion": "separation", "status": status(zero_overlap), "evidence": "The retained 21-frame ledger reports zero body/top, body/bottom and top/bottom evaluated intersections."},
        {"criterion": "neckline_shoulders_sleeves_hem", "status": status(neckline_pass), "evidence": f"The connected four-opening contract and {ratio:.6f} width ratio pass, but visual acceptance fails: {neckline['evidence']}"},
        {"criterion": "waistband_rise_crotch_legs", "status": status(measured["shorts_contract_pass"]), "evidence": "The exact accepted connected shorts retain three openings, zero other non-manifold edges, waistband/rise/crotch evidence and two legs."},
        {"criterion": "proportions", "status": status(proportion_pass), "evidence": f"Neutral top width is {measured['neutral_top_width_m']:.6f} m versus body width {measured['neutral_body_width_m']:.6f} m, ratio {ratio:.6f}; the unchanged review ceiling is {ratio_limit:.6f}."},
        {"criterion": "no_rejected_silhouettes", "status": status(silhouette_pass), "evidence": f"Waist inset {measured['waist_inset_ratio']:.6f} and outer width {ratio:.6f} pass their numeric gates, but visual acceptance fails: {silhouette['evidence']}"},
        {"criterion": "no_exposure_or_collision", "status": status(zero_overlap), "evidence": "All five exact views retain coverage and the 21-frame ledger reports zero evaluated intersections."},
        {"criterion": "stable_opposing_extremes", "status": status(opposing_pass), "evidence": opposing["evidence"]},
    ]


def expected_result(source: dict, waist: dict, views: dict) -> dict:
    measured = measurements(source, waist)
    observations = visual_observations(views)
    checks = criteria(source, measured, observations)
    verdict = "ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION" if all(row["status"] == "PASS" for row in checks) else "REJECTED_VISUAL_CORRECTION_REQUIRED"
    semantic = source["semantic"]
    result = {
        "phase": "Phase 1L.5cl outer-span-corrected combined starter-outfit offline visual acceptance review",
        "verdict": verdict,
        "criteria": checks,
        "visual_observations": observations,
        "measurements": measured,
        "smallest_correction": None if verdict == "ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION" else BOUNDED_CORRECTION,
        "source_custody": {
            "blend": source["files"]["blend"],
            "semantic_identity_sha256": EXPECTED["semantic"],
            "mesh_sha256": {"body": EXPECTED["body"], "top": EXPECTED["top"], "bottom": EXPECTED["bottom"]},
            "armature_bone_count": 12,
            "action_identity_sha256": EXPECTED["action"],
            "view_files": views,
            "frame_ledger_identity_sha256": identity(semantic["deformation"]),
            "opening_geometry_identity_sha256": identity(semantic["opening_geometry"]["derived"]),
            "opening_boundary_identity_sha256": identity(semantic["correction"]["source_opening_boundary_indices"]),
        },
        "boundaries": {"geometry_changed": 0, "weights_changed": 0, "topology_changed": 0, "materials_changed": 0, "action_changed": 0, "skeleton_changed": 0, "export_changed": 0, "unreal_changed": 0, "client_changed": 0, "package_inputs_changed": 0, "runtime_claim": False, "final_art_claim": False, "beta_readiness_claim": False, "future_technical_export_import_preparation_eligible": verdict == "ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION"},
    }
    result["identity_sha256"] = identity(result)
    return result


def build_board(result: dict) -> None:
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (2400, 1840), (24, 26, 31))
    draw = ImageDraw.Draw(canvas)
    positions = ((0, 0), (800, 0), (1600, 0), (400, 800), (1200, 800))
    labels = ("OUTER-SPAN-CORRECTED NEUTRAL FRONT", "OUTER-SPAN-CORRECTED NEUTRAL REAR", "OUTER-SPAN-CORRECTED NEUTRAL PROFILE", "OUTER-SPAN-CORRECTED WALK EXTREME — FRAME 6", "OUTER-SPAN-CORRECTED WALK EXTREME — FRAME 16")
    for name, position, label in zip(VIEWS, positions, labels):
        image = Image.open(SOURCE / "Review" / f"After_{name}.png").convert("RGB")
        if image.size != (800, 800):
            raise RuntimeError(f"unexpected corrected view size: {name} {image.size}")
        canvas.paste(image, position)
        draw.rectangle((position[0], position[1], position[0] + 800, position[1] + 34), fill=(24, 26, 31))
        draw.text((position[0] + 12, position[1] + 10), label, fill=(245, 245, 245))
    rejected = result["verdict"] == "REJECTED_VISUAL_CORRECTION_REQUIRED"
    draw.rectangle((0, 1600, 2400, 1840), fill=(58, 23, 28) if rejected else (20, 55, 38))
    failed = "; ".join(row["criterion"] for row in result["criteria"] if row["status"] == "FAIL") or "none"
    draw.text((30, 1630), f"PHASE 1L.5cl VERDICT: {result['verdict']}", fill=(255, 214, 214) if rejected else (220, 255, 230))
    draw.text((30, 1670), f"FAILED: {failed}", fill=(255, 235, 235) if rejected else (235, 255, 240))
    if rejected:
        draw.text((30, 1710), result["smallest_correction"], fill=(255, 235, 235))
        boundary = "This rejection stops export/import preparation."
    else:
        draw.text((30, 1710), "All seven unchanged criteria pass; only a future separately gated technical export/import preparation may follow.", fill=(235, 255, 240))
        boundary = "Acceptance is not export, runtime, final art, Phase 1L exit or beta readiness."
    draw.text((30, 1750), "Exact 1L.5ck custody, views, opening identities and 21-frame ledger retained.", fill=(225, 225, 225))
    draw.text((30, 1790), boundary, fill=(225, 225, 225))
    canvas.save(BOARD, format="PNG", optimize=False, compress_level=9)


def files() -> dict:
    return {"board": receipt(BOARD), "builder": receipt(Path(__file__)), "provenance": receipt(HERE / "PROVENANCE.md")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    source, waist, views = source_custody()
    result = expected_result(source, waist, views)
    allowed = {"ACCEPTED_FOR_TECHNICAL_EXPORT_IMPORT_PREPARATION", "REJECTED_VISUAL_CORRECTION_REQUIRED"}
    if result["verdict"] not in allowed:
        raise RuntimeError("invalid verdict state")
    if args.validate:
        result["files"] = files()
        recorded = json.loads(VERDICT.read_text(encoding="utf-8"))
        if recorded != result:
            raise RuntimeError("recorded outer-span-corrected review drift")
        print(f"PHASE_1L5CL_VALIDATE_PASS {recorded['verdict']} {recorded['identity_sha256']} {sha256(BOARD)}")
        return
    build_board(result)
    result["files"] = files()
    VERDICT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PHASE_1L5CL_BUILD_PASS {result['verdict']} {result['identity_sha256']} {sha256(BOARD)}")


if __name__ == "__main__":
    main()
