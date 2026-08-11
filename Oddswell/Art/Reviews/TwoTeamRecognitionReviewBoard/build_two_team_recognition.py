#!/usr/bin/env python3
"""Build and validate the Phase 1L.3j two-team SVG recognition review board."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
BUILDER = Path(__file__).name
UNIFIED = "TwoTeamRecognitionReviewBoard.svg"
HARBOR_CLOSEUP = "HarborCityWaves.svg"
MESA_CLOSEUP = "MesaVistaSol.svg"
MANIFEST = "manifest.json"
PROVENANCE = "PROVENANCE.md"
OUTPUTS = (UNIFIED, HARBOR_CLOSEUP, MESA_CLOSEUP, MANIFEST, PROVENANCE)

CHARCOAL = "#20272B"
OFF_WHITE = "#F7F3EA"
HARBOR_PRIMARY = "#315F79"
HARBOR_SECONDARY = "#D8C8A9"
MESA_PRIMARY = "#A65F47"
MESA_SECONDARY = "#B9A783"
SUPPORT = (CHARCOAL, OFF_WHITE)

CONTEXTS = (
    ("identity_tile", "Identity tile"),
    ("compact_matchup_row", "Compact matchup row"),
    ("match_winner_selection_card", "Match Winner selection card"),
    ("score_receipt_token", "Score / receipt token"),
)

TEAMS = (
    {
        "team_id": "harbor_city_waves",
        "label": "Harbor City Waves",
        "primary": HARBOR_PRIMARY,
        "secondary": HARBOR_SECONDARY,
        "system": "three_band_wave",
        "shape_label": "THREE-BAND WAVE",
        "shape_semantics": "three parallel wave bands",
    },
    {
        "team_id": "mesa_vista_sol",
        "label": "Mesa Vista Sol",
        "primary": MESA_PRIMARY,
        "secondary": MESA_SECONDARY,
        "system": "radial_sun",
        "shape_label": "RADIAL SUN",
        "shape_semantics": "central disc with twelve rays",
    },
)
TEAM_BY_ID = {team["team_id"]: team for team in TEAMS}
HEX_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def text(
    x: float,
    y: float,
    value: str,
    size: int,
    *,
    fill: str = CHARCOAL,
    background: str = OFF_WHITE,
    weight: int = 600,
    anchor: str = "start",
    letter_spacing: float = 0,
) -> str:
    return (
        f'<text x="{x:g}" y="{y:g}" fill="{fill}" data-bg="{background}" '
        f'font-family="sans-serif" font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}" letter-spacing="{letter_spacing:g}">{escape(value)}</text>'
    )


def wave_shape(team: dict[str, str], x: float, y: float, width: float, height: float) -> str:
    paths = []
    for index, fraction in enumerate((0.27, 0.50, 0.73)):
        baseline = y + height * fraction
        amplitude = height * 0.14
        d = (
            f"M {x:g} {baseline:g} "
            f"C {x + width * 0.17:g} {baseline - amplitude:g}, "
            f"{x + width * 0.33:g} {baseline - amplitude:g}, {x + width * 0.50:g} {baseline:g} "
            f"S {x + width * 0.83:g} {baseline + amplitude:g}, {x + width:g} {baseline:g}"
        )
        color = team["primary"] if index != 1 else team["secondary"]
        paths.append(
            f'<path class="semantic-band" d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{max(5, height * 0.075):g}" stroke-linecap="round"/>'
        )
    return "".join(paths)


def sun_shape(team: dict[str, str], x: float, y: float, width: float, height: float) -> str:
    cx, cy = x + width / 2, y + height / 2
    inner, outer = min(width, height) * 0.29, min(width, height) * 0.46
    rays = []
    for index in range(12):
        angle = math.radians(index * 30 - 90)
        x1, y1 = cx + inner * math.cos(angle), cy + inner * math.sin(angle)
        x2, y2 = cx + outer * math.cos(angle), cy + outer * math.sin(angle)
        rays.append(
            f'<line class="semantic-ray" x1="{x1:.3f}" y1="{y1:.3f}" '
            f'x2="{x2:.3f}" y2="{y2:.3f}" stroke="{team["secondary"]}" '
            f'stroke-width="{max(5, min(width, height) * 0.06):g}" stroke-linecap="round"/>'
        )
    core = (
        f'<circle class="semantic-core" cx="{cx:g}" cy="{cy:g}" '
        f'r="{min(width, height) * 0.23:g}" fill="{team["primary"]}"/>'
    )
    return "".join(rays) + core


def recognition_shape(team: dict[str, str], x: float, y: float, width: float, height: float) -> str:
    if team["system"] == "three_band_wave":
        return wave_shape(team, x, y, width, height)
    return sun_shape(team, x, y, width, height)


def context_card(
    team: dict[str, str],
    context_id: str,
    context_label: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> str:
    icon_width = min(226, width * 0.34)
    icon_height = min(138, height - 54)
    icon_x = x + 28
    icon_y = y + (height - icon_height) / 2
    copy_x = icon_x + icon_width + 32
    team_size = 27 if width >= 800 else 23
    context_size = 18 if width >= 800 else 16
    body_size = 16 if width >= 800 else 14
    shape = recognition_shape(team, icon_x, icon_y, icon_width, icon_height)
    return "".join(
        (
            f'<g data-team-id="{team["team_id"]}" data-context="{context_id}" '
            f'data-system="{team["system"]}" data-shape-semantics="{team["shape_semantics"]}">',
            f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" rx="18" '
            f'fill="{OFF_WHITE}" stroke="{team["primary"]}" stroke-width="3"/>',
            f'<rect x="{x:g}" y="{y:g}" width="12" height="{height:g}" rx="6" fill="{team["primary"]}"/>',
            shape,
            text(copy_x, y + 38, context_label.upper(), context_size, weight=700, letter_spacing=1.1),
            text(copy_x, y + 78, team["label"], team_size, weight=800),
            text(copy_x, y + 110, team["shape_label"], body_size, weight=800, letter_spacing=0.8),
            text(copy_x, y + 138, "WRITTEN LABEL + DISTINCT SHAPE", body_size, weight=600),
            text(copy_x, y + height - 22, "NONCANONICAL IDENTITY REVIEW", 13, weight=700, letter_spacing=0.7),
            "</g>",
        )
    )


def svg_document(width: int, height: int, title: str, content: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(title)}">\n'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{CHARCOAL}"/>\n'
        f"{content}\n"
        "</svg>"
    )


def render_unified() -> str:
    parts = [
        text(52, 62, "TWO-TEAM COLOR + SHAPE RECOGNITION", 36, fill=OFF_WHITE, background=CHARCOAL, weight=800),
        text(52, 100, "PHASE 1L.3j / STATIC REVIEW BOARD / NONCANONICAL", 17, fill=OFF_WHITE, background=CHARCOAL, weight=600, letter_spacing=1.3),
        text(1868, 62, "2 TEAMS / 8 CONTEXTS", 19, fill=OFF_WHITE, background=CHARCOAL, weight=700, anchor="end"),
    ]
    for column, team in enumerate(TEAMS):
        x = 30 + column * 940
        for row, (context_id, context_label) in enumerate(CONTEXTS):
            parts.append(context_card(team, context_id, context_label, x, 132 + row * 218, 920, 206))
    parts.extend(
        (
            text(52, 1046, "Recognition does not depend on color: every use pairs the full team name with its wave or sun system.", 17, fill=OFF_WHITE, background=CHARCOAL, weight=600),
            text(1868, 1046, "OWNER IDENTITY LOCK REQUIRED FOR PROMOTION", 15, fill=OFF_WHITE, background=CHARCOAL, weight=700, anchor="end"),
        )
    )
    return svg_document(1920, 1080, "Two-Team Recognition Review Board", "\n".join(parts))


def render_closeup(team: dict[str, str]) -> str:
    parts = [
        text(34, 50, team["label"].upper(), 34, fill=OFF_WHITE, background=CHARCOAL, weight=800),
        text(34, 84, f'{team["shape_label"]} / FOUR STATIC REVIEW CONTEXTS', 16, fill=OFF_WHITE, background=CHARCOAL, weight=600, letter_spacing=1.0),
        text(1246, 50, "NONCANONICAL REVIEW", 15, fill=OFF_WHITE, background=CHARCOAL, weight=700, anchor="end"),
    ]
    positions = ((30, 112), (650, 112), (30, 392), (650, 392))
    for (context_id, context_label), (x, y) in zip(CONTEXTS, positions):
        parts.append(context_card(team, context_id, context_label, x, y, 600, 258))
    parts.append(
        text(34, 690, "Full label and distinct geometry remain legible without relying on palette.", 15, fill=OFF_WHITE, background=CHARCOAL, weight=600)
    )
    return svg_document(1280, 720, f'{team["label"]} Recognition Closeup', "\n".join(parts))


def luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground: str, background: str) -> float:
    first, second = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (first + 0.05) / (second + 0.05)


def expected_contexts(team_id: str) -> set[tuple[str, str]]:
    return {(team_id, context_id) for context_id, _ in CONTEXTS}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_svg(path: Path, viewbox: str, team_ids: set[str]) -> None:
    raw = path.read_text(encoding="utf-8")
    root = ET.fromstring(raw)
    assert local_name(root.tag) == "svg"
    assert root.attrib.get("viewBox") == viewbox
    assert root.attrib.get("width") == viewbox.split()[2]
    assert root.attrib.get("height") == viewbox.split()[3]

    forbidden_tags = {"script", "foreignObject", "image", "animate", "animateMotion", "animateTransform", "set"}
    for element in root.iter():
        assert local_name(element.tag) not in forbidden_tags
        for name, value in element.attrib.items():
            attribute = local_name(name).lower()
            lowered = value.lower()
            assert attribute not in {"href", "src"}
            assert not attribute.startswith("on")
            assert "url(" not in lowered

    assert "@font-face" not in raw.lower()
    assert "javascript:" not in raw.lower()
    groups = [element for element in root.iter() if "data-context" in element.attrib]
    expected_count = len(team_ids) * len(CONTEXTS)
    assert len(groups) == expected_count
    found = Counter((group.attrib["data-team-id"], group.attrib["data-context"]) for group in groups)
    expected = set().union(*(expected_contexts(team_id) for team_id in team_ids))
    assert set(found) == expected
    assert all(count == 1 for count in found.values())

    context_labels = dict(CONTEXTS)
    for group in groups:
        team = TEAM_BY_ID[group.attrib["data-team-id"]]
        assert group.attrib["data-system"] == team["system"]
        assert group.attrib["data-shape-semantics"] == team["shape_semantics"]
        visible = " ".join(value.strip() for value in group.itertext() if value.strip())
        assert team["label"] in visible
        assert context_labels[group.attrib["data-context"]].upper() in visible
        assert team["shape_label"] in visible
        assert "WRITTEN LABEL + DISTINCT SHAPE" in visible
        if team["system"] == "three_band_wave":
            assert sum(element.attrib.get("class") == "semantic-band" for element in group.iter()) == 3
        else:
            assert sum(element.attrib.get("class") == "semantic-core" for element in group.iter()) == 1
            assert sum(element.attrib.get("class") == "semantic-ray" for element in group.iter()) == 12

    text_nodes = [element for element in root.iter() if local_name(element.tag) == "text"]
    assert text_nodes
    for node in text_nodes:
        assert node.attrib.get("font-family") == "sans-serif"
        assert contrast(node.attrib["fill"], node.attrib["data-bg"]) >= 4.5

    used_colors = {color.upper() for color in HEX_PATTERN.findall(raw)}
    permitted = {color.upper() for color in SUPPORT}
    for team_id in team_ids:
        team = TEAM_BY_ID[team_id]
        permitted.update((team["primary"], team["secondary"]))
    assert used_colors == permitted


def provenance_text() -> str:
    return """# Two-Team Recognition Review Board Provenance

- Phase: `Phase 1L.3j`, new-nightly Phase `3/6`.
- Generator: `build_two_team_recognition.py`, Python standard library only.
- Authority: approved Phase 1L.3j Scope Director gate; existing labels `Harbor City Waves` and `Mesa Vista Sol`; approved palettes Harbor `#315F79` / `#D8C8A9` and Mesa `#A65F47` / `#B9A783`.
- Recognition systems: Harbor three-band wave; Mesa radial sun. Written team labels accompany every system instance so recognition does not depend on color.
- Generated outputs: one `1920x1080` unified SVG, two `1280x720` team closeup SVGs, this provenance file, and `manifest.json`.
- External assets, images, textures, references, libraries, downloads, fonts, brands, and trade dress: `0`.
- Jerseys, mascots, arenas, crowds, animation, runtime imports, gameplay changes, and production changes: `0`.
- Status: deterministic native SVG review evidence only; noncanonical and not approved for production promotion.
"""


def manifest_data() -> dict[str, object]:
    teams = [
        {
            "team_id": team["team_id"],
            "label": team["label"],
            "palette": {"primary": team["primary"], "secondary": team["secondary"]},
            "recognition_system": team["system"],
            "shape_label": team["shape_label"],
            "shape_semantics": team["shape_semantics"],
        }
        for team in TEAMS
    ]
    contexts = [
        {"team_id": team["team_id"], "context_id": context_id, "context_label": context_label}
        for team in TEAMS
        for context_id, context_label in CONTEXTS
    ]
    renders = [
        {"file": UNIFIED, "viewBox": "0 0 1920 1080", "width": 1920, "height": 1080, "teams": 2, "contexts": 8},
        {"file": HARBOR_CLOSEUP, "viewBox": "0 0 1280 720", "width": 1280, "height": 720, "teams": 1, "contexts": 4},
        {"file": MESA_CLOSEUP, "viewBox": "0 0 1280 720", "width": 1280, "height": 720, "teams": 1, "contexts": 4},
    ]
    constraints = {
        "external_assets": 0,
        "external_images": 0,
        "external_textures": 0,
        "external_references": 0,
        "external_libraries": 0,
        "downloads": 0,
        "external_fonts": 0,
        "external_brands": 0,
        "trade_dress": 0,
        "jerseys": 0,
        "mascots": 0,
        "arenas": 0,
        "crowds": 0,
        "animation": 0,
        "runtime_imports": 0,
        "gameplay_changes": 0,
        "production_changes": 0,
    }
    return {
        "schema": "oddswell-two-team-recognition-review-v1",
        "phase": "Phase 1L.3j",
        "new_nightly_phase": "3/6",
        "status": "NONCANONICAL REVIEW",
        "team_count": 2,
        "recognition_system_count": 2,
        "contexts_per_team": 4,
        "context_count": 8,
        "teams": teams,
        "contexts": contexts,
        "support_palette": {"charcoal": CHARCOAL, "off_white": OFF_WHITE},
        "minimum_text_contrast": round(contrast(CHARCOAL, OFF_WHITE), 4),
        "renders": renders,
        "constraints": constraints,
        "authority": {
            "labels": [team["label"] for team in TEAMS],
            "team_ids": [team["team_id"] for team in TEAMS],
            "palette_source": "approved Phase 1L.3j Scope Director gate",
        },
        "builder": {"file": BUILDER, "sha256": sha256(ROOT / BUILDER), "runtime": "Python standard library"},
        "output_sha256": {name: sha256(ROOT / name) for name in (UNIFIED, HARBOR_CLOSEUP, MESA_CLOSEUP, PROVENANCE)},
    }


def validate_manifest() -> None:
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    assert manifest["schema"] == "oddswell-two-team-recognition-review-v1"
    assert manifest["phase"] == "Phase 1L.3j"
    assert manifest["new_nightly_phase"] == "3/6"
    assert manifest["status"] == "NONCANONICAL REVIEW"
    assert (manifest["team_count"], manifest["recognition_system_count"]) == (2, 2)
    assert (manifest["contexts_per_team"], manifest["context_count"]) == (4, 8)
    assert [team["team_id"] for team in manifest["teams"]] == [team["team_id"] for team in TEAMS]
    assert [team["label"] for team in manifest["teams"]] == [team["label"] for team in TEAMS]
    assert [team["recognition_system"] for team in manifest["teams"]] == [team["system"] for team in TEAMS]
    assert manifest["teams"][0]["palette"] == {"primary": HARBOR_PRIMARY, "secondary": HARBOR_SECONDARY}
    assert manifest["teams"][1]["palette"] == {"primary": MESA_PRIMARY, "secondary": MESA_SECONDARY}
    assert len(manifest["contexts"]) == 8
    assert Counter(item["team_id"] for item in manifest["contexts"]) == Counter({"harbor_city_waves": 4, "mesa_vista_sol": 4})
    assert all(value == 0 for value in manifest["constraints"].values())
    assert manifest["minimum_text_contrast"] >= 4.5
    assert manifest["builder"] == {"file": BUILDER, "sha256": sha256(ROOT / BUILDER), "runtime": "Python standard library"}
    expected_hashes = {name: sha256(ROOT / name) for name in (UNIFIED, HARBOR_CLOSEUP, MESA_CLOSEUP, PROVENANCE)}
    assert manifest["output_sha256"] == expected_hashes


def validate() -> None:
    expected = {BUILDER, *OUTPUTS}
    actual = {path.name for path in ROOT.iterdir() if path.is_file()}
    assert actual == expected, f"unexpected review-root files: {sorted(actual ^ expected)}"
    validate_svg(ROOT / UNIFIED, "0 0 1920 1080", {team["team_id"] for team in TEAMS})
    validate_svg(ROOT / HARBOR_CLOSEUP, "0 0 1280 720", {"harbor_city_waves"})
    validate_svg(ROOT / MESA_CLOSEUP, "0 0 1280 720", {"mesa_vista_sol"})
    validate_manifest()


def build() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_text(ROOT / UNIFIED, render_unified())
    write_text(ROOT / HARBOR_CLOSEUP, render_closeup(TEAMS[0]))
    write_text(ROOT / MESA_CLOSEUP, render_closeup(TEAMS[1]))
    write_text(ROOT / PROVENANCE, provenance_text())
    write_text(ROOT / MANIFEST, json.dumps(manifest_data(), indent=2, sort_keys=True))
    validate()


def clean_outputs() -> None:
    for name in OUTPUTS:
        path = ROOT / name
        if path.exists():
            path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="remove generated outputs before rebuilding")
    parser.add_argument("--validate-only", action="store_true", help="reopen and validate existing outputs")
    args = parser.parse_args()
    if args.clean:
        clean_outputs()
    if args.validate_only:
        validate()
        print("ODDSWELL_TWO_TEAM_RECOGNITION_FOCUSED|result=PASS|ids=2|systems=2|contexts=8|forbidden=0")
        return
    build()
    print("ODDSWELL_TWO_TEAM_RECOGNITION_BUILD|result=PASS|renders=3|contexts=8|manual_input=false")


if __name__ == "__main__":
    main()
