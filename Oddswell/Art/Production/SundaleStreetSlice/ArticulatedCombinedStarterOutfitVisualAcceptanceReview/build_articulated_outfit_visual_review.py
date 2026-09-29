"""Build or validate the evidence-only Phase 1L.5cn outfit review."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "Art/Production/SundaleStreetSlice/ShoulderSleeveHemArticulationCorrectionWalkProof"
SOURCE_MANIFEST = SOURCE / "shoulder_sleeve_hem_articulation_walk_custody.json"
WAIST_MANIFEST = ROOT / "Art/Production/SundaleStreetSlice/LateralWaistTaperStarterTopWalkProof/lateral_waist_taper_starter_top_walk_custody.json"
BOARD = HERE / "Review/ArticulatedCombinedStarterOutfitVisualAcceptance.png"
VERDICT = HERE / "articulated_combined_starter_outfit_visual_acceptance.json"
PROVENANCE = HERE / "PROVENANCE.md"
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")
EXPECTED = {
    "blend": "10315DEC1E2F1EAB3F3D7DDA6828AB5B9867957B9D108C5A2F462201D3E059FC",
    "semantic": "6E219986ED018BFF27BB61AD308346C33217795B5C883893806E661D589579B0",
    "body": "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD",
    "top": "9ED01AAA3F060F237D2CCADCD5ED7E15F65E864F013DC0BCB51266A31A34FA58",
    "bottom": "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170",
    "action": "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020",
    "waist": "38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD",
}
SMALLEST_CORRECTION = (
    "Correct only the top outer sleeve/armhole block geometry within |X| >= 0.389245 m and "
    "1.20 m <= Z <= 1.40 m into a continuous rounded cap; preserve the 1L.5cm articulation "
    "weights, central torso, waist and neckline boundaries, four-opening contract and all non-target assets."
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def receipt(path):
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


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
        receipt(SOURCE / "RefinedSundaleShoulderSleeveHemArticulatedTopWalk.blend") == source["files"]["blend"],
        waist["semantic"]["identity_sha256"] == EXPECTED["waist"],
        top["connected_components"] == 1 and top["boundary_loops"] == 4 and top["non_manifold_edges_excluding_openings"] == 0,
        bottom["connected_components"] == 1 and bottom["boundary_loops"] == 3 and bottom["non_manifold_edges_excluding_openings"] == 0,
        semantic["boundaries"]["final_acceptance_verdict"] is None,
        semantic["boundaries"]["export_import_preparation_stopped"] is True,
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5cm custody drift")
    views = {}
    for name in VIEWS:
        filename = f"After_{name}.png"
        path = SOURCE / "Review" / filename
        if receipt(path) != source["files"]["reviews"][filename]:
            raise RuntimeError(f"1L.5cm review custody drift: {filename}")
        views[name] = receipt(path)
    return source, waist, views


def measurements(source, waist):
    semantic = source["semantic"]
    correction = semantic["correction"]
    widths = waist["semantic"]["correction"]["half_width_m"]
    waist_inset = (widths["upper"]["derived"] - widths["lower"]["derived"]) / widths["upper"]["derived"]
    return {
        "neutral_body_width_m": correction["body_width_m"],
        "neutral_top_width_m": correction["derived_top_width_m"],
        "top_to_body_width_ratio": correction["derived_top_to_body_width_ratio"],
        "maximum_top_to_body_width_ratio": correction["maximum_top_to_body_width_ratio"],
        "waist_inset_ratio": round(waist_inset, 9),
        "minimum_waist_inset_ratio": 0.08,
        "outer_sleeve_armhole_x_min_m": 0.389245,
        "outer_sleeve_armhole_z_range_m": [1.20, 1.40],
    }


def visual_observations(views):
    return {
        "view_identity_sha256": identity(views),
        "neckline_shoulders_sleeves_hem": {
            "pass": False,
            "views": list(VIEWS),
            "evidence": (
                "The corrected shoulder line and hem remain stable, but both outer sleeves still terminate "
                "as abrupt rectangular blocks instead of continuous rounded armhole caps."
            ),
        },
        "no_rejected_silhouettes": {
            "pass": False,
            "views": list(VIEWS),
            "evidence": (
                "The numeric width and waist-taper gates pass, but the neutral and opposing-extreme views "
                "retain detached-looking sleeve blocks and an armor-like outer top silhouette."
            ),
        },
        "stable_opposing_extremes": {
            "pass": True,
            "views": ["WalkExtremeFront", "WalkExtremeRear"],
            "evidence": (
                "Frames 6 and 16 keep the corrected shoulder line and lower hem near the neutral silhouette; "
                "the prior raised plates and uneven hem collapse do not recur."
            ),
        },
        "coverage": {
            "pass": True,
            "views": list(VIEWS),
            "evidence": "All five exact views retain body coverage without visible interpenetration.",
        },
    }


def criteria(source, measured, observations):
    semantic = source["semantic"]
    frames = semantic["deformation"]["frames"]
    zero_overlap = all(all(value == 0 for value in frame["intersections"].values()) for frame in frames)
    mechanical_stability = semantic["deformation"]["loop_endpoint_equal"] and all(
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
        {"criterion": "neckline_shoulders_sleeves_hem", "status": status(top_contract and neckline["pass"]), "evidence": f"The one-component/four-opening contract passes, but the unchanged qualitative criterion fails: {neckline['evidence']}"},
        {"criterion": "waistband_rise_crotch_legs", "status": status(shorts_contract), "evidence": "The exact accepted shorts retain one component, three openings, zero other non-manifold edges and two readable legs."},
        {"criterion": "proportions", "status": status(proportion_pass), "evidence": f"Neutral top width is {measured['neutral_top_width_m']:.6f} m versus body width {measured['neutral_body_width_m']:.6f} m, ratio {measured['top_to_body_width_ratio']:.6f}; the unchanged ceiling is {measured['maximum_top_to_body_width_ratio']:.6f}. This numeric pass does not override qualitative failures."},
        {"criterion": "no_rejected_silhouettes", "status": status(top_contract and proportion_pass and taper_pass and silhouette["pass"]), "evidence": f"Width ratio {measured['top_to_body_width_ratio']:.6f} and waist inset {measured['waist_inset_ratio']:.6f} pass their numeric gates, but the unchanged qualitative criterion fails: {silhouette['evidence']}"},
        {"criterion": "no_exposure_or_collision", "status": status(zero_overlap and coverage["pass"]), "evidence": coverage["evidence"] + " The retained ledger also reports zero evaluated intersections."},
        {"criterion": "stable_opposing_extremes", "status": status(mechanical_stability and stable["pass"]), "evidence": stable["evidence"] + " Root/armature translation remains zero and frame 21 equals frame 1."},
    ]


def expected_result(source, waist, views):
    measured = measurements(source, waist)
    observations = visual_observations(views)
    checks = criteria(source, measured, observations)
    accepted = all(row["status"] == "PASS" for row in checks)
    verdict = "ACCEPTED_FOR_EXPORT_IMPORT_PREPARATION" if accepted else "REJECTED_VISUAL_CORRECTION_REQUIRED"
    semantic = source["semantic"]
    result = {
        "phase": "Phase 1L.5cn articulated combined starter-outfit offline visual acceptance review",
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
            "asset_changes": 0,
            "runtime_input_changes": 0,
            "geometry_changes": 0,
            "weight_changes": 0,
            "topology_changes": 0,
            "material_changes": 0,
            "action_changes": 0,
            "skeleton_changes": 0,
            "export_changes": 0,
            "unreal_changes": 0,
            "client_changes": 0,
            "package_input_changes": 0,
            "readiness_claim": False,
            "export_import_preparation_eligible": accepted,
        },
    }
    result["identity_sha256"] = identity(result)
    return result


def build_board(result):
    BOARD.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (2400, 1840), (24, 26, 31))
    draw = ImageDraw.Draw(canvas)
    positions = ((0, 0), (800, 0), (1600, 0), (400, 800), (1200, 800))
    labels = ("ARTICULATED NEUTRAL FRONT", "ARTICULATED NEUTRAL REAR", "ARTICULATED NEUTRAL PROFILE", "ARTICULATED WALK EXTREME — FRAME 6", "ARTICULATED WALK EXTREME — FRAME 16")
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
    draw.text((30, 1630), f"PHASE 1L.5cn VERDICT: {result['verdict']}", fill=color)
    draw.text((30, 1670), f"FAILED: {failed}", fill=color)
    if rejected:
        draw.text((30, 1710), result["smallest_correction"], fill=(255, 235, 235))
        boundary = "This rejection stops export/import preparation."
    else:
        draw.text((30, 1710), "All seven unchanged criteria pass; separately gated export/import preparation may follow.", fill=(235, 255, 240))
        boundary = "Acceptance is not export, runtime, final art, Phase 1L exit or beta readiness."
    draw.text((30, 1750), "Exact 1L.5cm custody, views, topology/openings, metrics and 21-frame ledger retained.", fill=(225, 225, 225))
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
            raise RuntimeError("recorded articulated outfit review drift")
        print(f"PHASE_1L5CN_VALIDATE_PASS {recorded['verdict']} {recorded['identity_sha256']} {sha256(BOARD)}")
        return
    build_board(result)
    result["files"] = files()
    VERDICT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PHASE_1L5CN_BUILD_PASS {result['verdict']} {result['identity_sha256']} {sha256(BOARD)}")


if __name__ == "__main__":
    main()
