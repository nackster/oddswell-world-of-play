"""Build or validate the evidence-only Phase 1L.5cr outfit review."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "Art/Production/SundaleStreetSlice/YokeCapTransitionBlendCorrectionWalkProof"
SOURCE_MANIFEST = SOURCE / "yoke_cap_transition_blend_walk_custody.json"
WAIST_MANIFEST = ROOT / "Art/Production/SundaleStreetSlice/LateralWaistTaperStarterTopWalkProof/lateral_waist_taper_starter_top_walk_custody.json"
BOARD = HERE / "Review/YokeBlendedCombinedStarterOutfitVisualAcceptance.png"
VERDICT = HERE / "yoke_blended_combined_starter_outfit_visual_acceptance.json"
PROVENANCE = HERE / "PROVENANCE.md"
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")
EXPECTED = {
    "blend": "A256E5F7B1B0750623A9B9F9B5085A45850AE1E525B0CD32F07447C791568A1E",
    "semantic": "D9ABDAF676F2352EA8629EE4FC375A1F5567830AD5D721093669D942CB91F78A",
    "body": "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD",
    "top": "EAB37355BDA56874B10BCA2BEE45BD4FDAFAE9F0B7B7826BFDBA85C1BB9807E8",
    "bottom": "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170",
    "action": "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020",
    "waist": "38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD",
}
SMALLEST_CORRECTION = (
    "Correct only the top side/underarm-to-hem transition coordinates and normalized spine/matching-upper-arm blend, "
    "symmetrically reducing the neutral profile slab and removing the frame-6 lateral bulge, frame-16 triangular spike "
    "and hem tilt; preserve the neckline, corrected yoke/caps, central front/rear pattern, waist opening, outer width, "
    "topology and every non-target asset."
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def receipt(path):
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def identity(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def source_custody():
    source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    waist = json.loads(WAIST_MANIFEST.read_text(encoding="utf-8"))
    semantic = source["semantic"]
    top = semantic["topology"]["starter_offwhite_top"]
    bottom = semantic["topology"]["starter_offwhite_bottom"]
    checks = (
        semantic["identity_sha256"] == EXPECTED["semantic"],
        semantic["accepted_mesh_sha256"]["BODY__refined_sundale_derivative_v1"] == EXPECTED["body"],
        semantic["derived_mesh_sha256"]["starter_offwhite_top"] == EXPECTED["top"],
        semantic["accepted_mesh_sha256"]["starter_offwhite_bottom"] == EXPECTED["bottom"],
        semantic["action"]["identity_sha256"] == EXPECTED["action"],
        semantic["armature"]["bone_count"] == 12,
        source["files"]["blend"]["sha256"] == EXPECTED["blend"],
        receipt(SOURCE / "RefinedSundaleYokeCapTransitionBlendedTopWalk.blend") == source["files"]["blend"],
        waist["semantic"]["identity_sha256"] == EXPECTED["waist"],
        top["connected_components"] == 1 and top["boundary_loops"] == 4 and top["non_manifold_edges_excluding_openings"] == 0,
        bottom["connected_components"] == 1 and bottom["boundary_loops"] == 3 and bottom["non_manifold_edges_excluding_openings"] == 0,
        semantic["boundaries"]["final_acceptance_verdict"] is None,
        semantic["boundaries"]["export_import_preparation_stopped"] is True,
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5cq custody drift")
    views = {}
    for name in VIEWS:
        filename = f"After_{name}.png"
        path = SOURCE / "Review" / filename
        if receipt(path) != source["files"]["reviews"][filename]:
            raise RuntimeError(f"Phase 1L.5cq view custody drift: {filename}")
        views[name] = receipt(path)
    return source, waist, views


def measurements(source, waist):
    correction = source["semantic"]["correction"]
    frames = source["semantic"]["deformation"]["frames"]
    widths = waist["semantic"]["correction"]["half_width_m"]
    waist_inset = (widths["upper"]["derived"] - widths["lower"]["derived"]) / widths["upper"]["derived"]
    return {
        "neutral_body_width_m": correction["body_width_m"],
        "neutral_top_width_m": correction["derived_top_width_m"],
        "top_to_body_width_ratio": correction["derived_top_to_body_width_ratio"],
        "maximum_top_to_body_width_ratio": 1.4,
        "waist_inset_ratio": round(waist_inset, 9),
        "minimum_waist_inset_ratio": 0.08,
        "minimum_sampled_clearance_m": min(
            garment["vertex_sampled_min_m"]
            for frame in frames
            for garment in frame["vertex_sampled_clearance"].values()
        ),
    }


def visual_observations(views):
    return {
        "view_identity_sha256": identity(views),
        "neckline_shoulders_sleeves_hem": {
            "pass": False,
            "views": list(VIEWS),
            "evidence": (
                "The yoke blend softens the neutral shoulder transition, but the retained frame-6 left sleeve/side forms "
                "a large angular bulge and frame 16 retains a sharp right triangular spike with a visibly tilted lower hem."
            ),
        },
        "no_rejected_silhouettes": {
            "pass": False,
            "views": list(VIEWS),
            "evidence": (
                "The exact neutral profile still reads as a broad horizontal slab with a detached mid-torso ledge, and "
                "the front/rear remain box/poncho-like despite passing the numeric width and waist gates."
            ),
        },
        "stable_opposing_extremes": {
            "pass": False,
            "views": ["WalkExtremeFront", "WalkExtremeRear"],
            "evidence": (
                "The exact frame-6 view carries its dominant deformation as a left lateral bulge, while frame 16 changes "
                "to a right outward spike and diagonal hem; mechanical loop closure does not establish qualitative stability."
            ),
        },
        "coverage": {
            "pass": True,
            "views": list(VIEWS),
            "evidence": "All five exact views retain coverage without visible body/garment or garment/garment penetration.",
        },
    }


def criteria(source, measured, observations):
    semantic = source["semantic"]
    frames = semantic["deformation"]["frames"]
    zero_overlap = all(all(value == 0 for value in frame["intersections"].values()) for frame in frames)
    mechanical = semantic["deformation"]["loop_endpoint_equal"] and all(
        frame["root_bone_translation_m"] == [0.0, 0.0, 0.0]
        and frame["armature_translation_m"] == [0.0, 0.0, 0.0]
        for frame in frames
    )
    top = semantic["topology"]["starter_offwhite_top"]
    bottom = semantic["topology"]["starter_offwhite_bottom"]
    top_contract = top["connected_components"] == 1 and top["boundary_loops"] == 4 and top["non_manifold_edges_excluding_openings"] == 0 and all(semantic["panel_roles"].values())
    shorts_contract = bottom["connected_components"] == 1 and bottom["boundary_loops"] == 3 and bottom["non_manifold_edges_excluding_openings"] == 0
    proportion_pass = measured["top_to_body_width_ratio"] <= measured["maximum_top_to_body_width_ratio"]
    taper_pass = measured["waist_inset_ratio"] >= measured["minimum_waist_inset_ratio"]
    status = lambda passed: "PASS" if passed else "FAIL"
    neckline = observations["neckline_shoulders_sleeves_hem"]
    silhouette = observations["no_rejected_silhouettes"]
    stable = observations["stable_opposing_extremes"]
    coverage = observations["coverage"]
    return [
        {"criterion": "separation", "status": status(zero_overlap), "evidence": "The exact retained 21-frame ledger reports zero body/top, body/bottom and top/bottom evaluated intersections."},
        {"criterion": "neckline_shoulders_sleeves_hem", "status": status(top_contract and neckline["pass"]), "evidence": "The topology/opening contract passes, but the unchanged qualitative criterion fails: " + neckline["evidence"]},
        {"criterion": "waistband_rise_crotch_legs", "status": status(shorts_contract), "evidence": "The exact accepted shorts retain one component, three openings, zero other non-manifold edges and two readable legs."},
        {"criterion": "proportions", "status": status(proportion_pass), "evidence": f"Neutral top width is {measured['neutral_top_width_m']:.9f} m versus body width {measured['neutral_body_width_m']:.6f} m, ratio {measured['top_to_body_width_ratio']:.9f}; the unchanged ceiling is {measured['maximum_top_to_body_width_ratio']:.1f}. This numeric pass does not override qualitative failures."},
        {"criterion": "no_rejected_silhouettes", "status": status(top_contract and proportion_pass and taper_pass and silhouette["pass"]), "evidence": f"Width ratio {measured['top_to_body_width_ratio']:.9f} and waist inset {measured['waist_inset_ratio']:.9f} pass their numeric gates, but the unchanged qualitative criterion fails: {silhouette['evidence']}"},
        {"criterion": "no_exposure_or_collision", "status": status(zero_overlap and coverage["pass"]), "evidence": coverage["evidence"] + f" The retained ledger reports zero evaluated intersections and minimum sampled clearance {measured['minimum_sampled_clearance_m']:.9f} m."},
        {"criterion": "stable_opposing_extremes", "status": status(mechanical and stable["pass"]), "evidence": stable["evidence"] + " Root/armature translation remains zero and frame 21 equals frame 1."},
    ]


def expected_result(source, waist, views):
    measured = measurements(source, waist)
    observations = visual_observations(views)
    checks = criteria(source, measured, observations)
    accepted = all(row["status"] == "PASS" for row in checks)
    verdict = "ACCEPTED_FOR_EXPORT_IMPORT_PREPARATION" if accepted else "REJECTED_VISUAL_CORRECTION_REQUIRED"
    semantic = source["semantic"]
    result = {
        "phase": "Phase 1L.5cr yoke-blended combined starter-outfit offline visual acceptance review",
        "verdict": verdict,
        "criteria": checks,
        "measurements": measured,
        "visual_observations": observations,
        "smallest_correction": None if accepted else SMALLEST_CORRECTION,
        "source_custody": {
            "blend": source["files"]["blend"],
            "semantic_identity_sha256": EXPECTED["semantic"],
            "mesh_sha256": {"body": EXPECTED["body"], "top": EXPECTED["top"], "bottom": EXPECTED["bottom"]},
            "armature_bone_count": 12,
            "action_identity_sha256": EXPECTED["action"],
            "view_files": views,
            "frame_ledger_identity_sha256": identity(semantic["deformation"]),
            "topology_identity_sha256": identity(semantic["topology"]),
            "opening_identity_sha256": identity(semantic["opening_geometry"]["derived"]),
        },
        "boundaries": {
            "asset_changes": 0, "runtime_input_changes": 0, "geometry_changes": 0, "weight_changes": 0,
            "topology_changes": 0, "material_changes": 0, "action_changes": 0, "skeleton_changes": 0,
            "export_changes": 0, "unreal_changes": 0, "client_changes": 0, "package_input_changes": 0,
            "readiness_claim": False, "export_import_preparation_eligible": accepted,
        },
    }
    result["identity_sha256"] = identity(result)
    return result


def build_board(result):
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (2400, 1840), (24, 26, 31))
    draw = ImageDraw.Draw(canvas)
    positions = ((0, 0), (800, 0), (1600, 0), (400, 800), (1200, 800))
    labels = (
        "YOKE-BLENDED NEUTRAL FRONT", "YOKE-BLENDED NEUTRAL REAR", "YOKE-BLENDED NEUTRAL PROFILE",
        "YOKE-BLENDED WALK EXTREME — FRAME 6", "YOKE-BLENDED WALK EXTREME — FRAME 16",
    )
    for name, position, label in zip(VIEWS, positions, labels):
        image = Image.open(SOURCE / "Review" / f"After_{name}.png").convert("RGB")
        if image.size != (800, 800):
            raise RuntimeError(f"unexpected source view size: {name} {image.size}")
        canvas.paste(image, position)
        draw.rectangle((position[0], position[1], position[0] + 800, position[1] + 34), fill=(24, 26, 31))
        draw.text((position[0] + 12, position[1] + 10), label, fill=(245, 245, 245))
    rejected = result["verdict"] == "REJECTED_VISUAL_CORRECTION_REQUIRED"
    draw.rectangle((0, 1600, 2400, 1840), fill=(58, 23, 28) if rejected else (20, 55, 38))
    failed = "; ".join(row["criterion"] for row in result["criteria"] if row["status"] == "FAIL") or "none"
    color = (255, 214, 214) if rejected else (220, 255, 230)
    draw.text((30, 1630), f"PHASE 1L.5cr VERDICT: {result['verdict']}", fill=color)
    draw.text((30, 1670), f"FAILED: {failed}", fill=color)
    if rejected:
        draw.text((30, 1710), result["smallest_correction"], fill=(255, 235, 235))
        boundary = "This rejection stops export/import preparation; no correction follows in this nightly batch."
    else:
        draw.text((30, 1710), "All seven unchanged criteria pass; separately gated export/import preparation may follow.", fill=(235, 255, 240))
        boundary = "Acceptance is not export, runtime, final art, Phase 1L exit or beta readiness."
    draw.text((30, 1750), "Exact 1L.5cq custody, views, topology/openings, metrics and 21-frame ledger retained.", fill=(225, 225, 225))
    draw.text((30, 1790), boundary, fill=(225, 225, 225))
    canvas.save(BOARD, format="PNG", optimize=False, compress_level=9)


def files():
    return {"board": receipt(BOARD), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    source, waist, views = source_custody()
    result = expected_result(source, waist, views)
    if args.validate:
        result["files"] = files()
        recorded = json.loads(VERDICT.read_text(encoding="utf-8"))
        if recorded != result:
            raise RuntimeError("recorded yoke-blended outfit review drift")
        print(f"PHASE_1L5CR_VALIDATE_PASS {recorded['verdict']} {recorded['identity_sha256']} {sha256(BOARD)}")
        return
    build_board(result)
    PROVENANCE.write_text(
        "# Phase 1L.5cr provenance\n\n"
        "- Evidence-only review of exact Phase 1L.5cq custody, five retained views and the retained 21-frame ledger.\n"
        "- Applies the exact unchanged seven criteria; numeric gates cannot override qualitative failures.\n"
        "- Changes no asset, geometry, weight, material, action, skeleton, Unreal/client file, package input or runtime behavior.\n"
        "- A rejection names exactly one smallest future correction and keeps export/import preparation stopped.\n"
        "- This is the final phase in the nightly batch; no correction, export or Phase 7 follows.\n",
        encoding="utf-8",
    )
    result["files"] = files()
    VERDICT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PHASE_1L5CR_BUILD_PASS {result['verdict']} {result['identity_sha256']} {sha256(BOARD)}")


if __name__ == "__main__":
    main()
