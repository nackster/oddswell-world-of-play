#!/usr/bin/env python3
"""Deterministically build or read-only validate the Sundale review board."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
SOURCE_REL = Path("client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp")
SOURCE = REPO / SOURCE_REL
SOURCE_SHA256 = "22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298"
WEATHER_ID = "SUNDALE_DRY_LATE_AFTERNOON"
SCENARIOS = ("COMMONS_OPEN_SUN", "AWNING_PATTERNED_SHADE", "ROUTE_LONG_VIEW_WARM_HAZE")
TARGETS = (
    "STARTER_OFFWHITE_READ",
    "SIGNAL_JACKET_READ",
    "COBALT_ROUTE_MARK_READ",
    "BURNT_ORANGE_THRESHOLD_READ",
    "LIMESTONE_TERRACOTTA_SURFACE_READ",
)
PALETTE = ("#D8C8A9", "#A65F47", "#B9A783", "#6D7F62", "#315F79", "#C46D3B", "#4D5051")
ATMOSPHERE = {
    "directional_intensity": 5.0,
    "directional_temperature_kelvin": 5000,
    "skylight_intensity": 0.8,
    "skylight_color": "#D8E4F0",
    "fog_density": 0.003,
    "fog_color": "#E8C9A5",
    "expected_directional_lights": 1,
    "expected_skylights": 1,
    "expected_exponential_height_fogs": 1,
}
FLAGS = {
    "production_claim": False,
    "photometric_claim": False,
    "lighting_change": False,
    "weather_system": False,
    "weather_variants": 0,
    "time_of_day_system": False,
    "accessibility_ready": False,
    "gameplay_change": False,
    "gameplay_additions": 0,
}
MATERIAL_INPUTS = {
    "starter_offwhite_rgba": [0.92, 0.90, 0.82, 1],
    "signal_jacket_slate_rgba": [0.12, 0.18, 0.22, 1],
    "signal_jacket_teal_rgba": [0.08, 0.72, 0.68, 1],
}
SOURCE_BINDINGS = (
    (80, "const FLinearColor StarterOffWhite(0.92f, 0.90f, 0.82f);"),
    (81, "const FLinearColor SignalJacketSlate(0.12f, 0.18f, 0.22f);"),
    (82, "const FLinearColor SignalJacketTeal(0.08f, 0.72f, 0.68f);"),
    (1030, "const FLinearColor SundaleWarmLimestone = FLinearColor::FromSRGBColor(FColor(0xD8, 0xC8, 0xA9));"),
    (1031, "const FLinearColor SundaleMutedTerracotta = FLinearColor::FromSRGBColor(FColor(0xA6, 0x5F, 0x47));"),
    (1032, "const FLinearColor SundaleSandConcrete = FLinearColor::FromSRGBColor(FColor(0xB9, 0xA7, 0x83));"),
    (1033, "const FLinearColor SundaleSageGreen = FLinearColor::FromSRGBColor(FColor(0x6D, 0x7F, 0x62));"),
    (1034, "const FLinearColor SundaleRestrainedCobalt = FLinearColor::FromSRGBColor(FColor(0x31, 0x5F, 0x79));"),
    (1035, "const FLinearColor SundaleBurntOrange = FLinearColor::FromSRGBColor(FColor(0xC4, 0x6D, 0x3B));"),
    (1036, "const FLinearColor SundaleCharcoalGray = FLinearColor::FromSRGBColor(FColor(0x4D, 0x50, 0x51));"),
    (1224, "struct FSundaleAtmosphereSpec"),
    (1225, "{"),
    (1226, "\tfloat DirectionalIntensity;"),
    (1227, "\tfloat DirectionalTemperatureKelvin;"),
    (1228, "\tfloat SkyLightIntensity;"),
    (1229, "\tFLinearColor SkyLightColor;"),
    (1230, "\tfloat FogDensity;"),
    (1231, "\tFLinearColor FogInscatteringColor;"),
    (1232, "\tint32 ExpectedDirectionalLights;"),
    (1233, "\tint32 ExpectedSkyLights;"),
    (1234, "\tint32 ExpectedHeightFogs;"),
    (1235, "};"),
    (1236, ""),
    (1237, "const FSundaleAtmosphereSpec& GetSundaleAtmosphereSpec()"),
    (1238, "{"),
    (1239, "\tstatic const FSundaleAtmosphereSpec Spec = {"),
    (1240, "\t\t5.0f,"),
    (1241, "\t\t5000.0f,"),
    (1242, "\t\t0.8f,"),
    (1243, "\t\tFLinearColor::FromSRGBColor(FColor(0xD8, 0xE4, 0xF0)),"),
    (1244, "\t\t0.003f,"),
    (1245, "\t\tFLinearColor::FromSRGBColor(FColor(0xE8, 0xC9, 0xA5)),"),
    (1246, "\t\t1,"),
    (1247, "\t\t1,"),
    (1248, "\t\t1,"),
)
GENERATED = ("manifest.json", "PROVENANCE.md", "Unified.svg") + tuple(f"{s}.svg" for s in SCENARIOS)
EXPECTED_FILES = {Path(__file__).name, *GENERATED}
SVG_NS = "http://www.w3.org/2000/svg"
FORBIDDEN_TAGS = {
    "a", "animate", "animateMotion", "animateTransform", "audio", "embed", "foreignObject",
    "iframe", "image", "link", "object", "script", "set", "style", "use", "video",
}
FORBIDDEN_ATTRIBUTES = {"href", "src", "style"}
FORBIDDEN_RAW = re.compile(r"(?:@font-face|url\s*\(|https?://|download|runtime_import|texture|brand|interior)", re.I)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def rgb(color: str) -> tuple[float, float, float]:
    return tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))


def luminance(color: str) -> float:
    values = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb(color))
    return .2126 * values[0] + .7152 * values[1] + .0722 * values[2]


def contrast(foreground: str, background: str) -> float:
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + .05) / (low + .05)


def text(x: int, y: int, value: str, size: int, fill: str, background: str, weight: int = 400) -> str:
    ratio = contrast(fill, background)
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="sans-serif" font-size="{size}" '
        f'font-weight="{weight}" data-contrast-kind="text/background" data-foreground="{fill}" '
        f'data-background="{background}" data-contrast-ratio="{ratio:.4f}">{esc(value)}</text>'
    )


def svg_open(width: int, height: int, label: str) -> list[str]:
    return [
        f'<svg xmlns="{SVG_NS}" version="1.1" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#D8C8A9"/>',
    ]


CARDS = (
    ("STARTER_OFFWHITE_READ", 50, "#315F79", "#EBE6D1", "STARTER OFFWHITE", "RGBA 0.92 / 0.90 / 0.82 / 1"),
    ("SIGNAL_JACKET_READ", 292, "#EBE6D1", "#1F2E38", "SIGNAL JACKET", "SLATE + TEAL"),
    ("COBALT_ROUTE_MARK_READ", 534, "#D8C8A9", "#315F79", "COBALT ROUTE", "MARK READ"),
    ("BURNT_ORANGE_THRESHOLD_READ", 776, "#1F2E38", "#C46D3B", "BURNT ORANGE", "THRESHOLD READ"),
    ("LIMESTONE_TERRACOTTA_SURFACE_READ", 1018, "#4D5051", "#B9A783", "LIMESTONE", "TERRACOTTA SURFACE"),
)
TARGET_DIAGNOSTICS = (
    ("STARTER_OFFWHITE_READ", "#EBE6D1", "#315F79"),
    ("SIGNAL_JACKET_READ", "#14B8AD", "#1F2E38"),
    ("COBALT_ROUTE_MARK_READ", "#315F79", "#D8C8A9"),
    ("BURNT_ORANGE_THRESHOLD_READ", "#C46D3B", "#1F2E38"),
    ("LIMESTONE_TERRACOTTA_SURFACE_READ", "#B9A783", "#4D5051"),
)


def scenario_svg(scenario: str) -> str:
    lines = svg_open(1280, 720, f"{scenario} lighting and atmosphere review")
    lines += [
        '<rect x="0" y="0" width="1280" height="170" fill="#315F79"/>',
        text(54, 64, "SUNDALE / DRY LATE AFTERNOON", 24, "#EBE6D1", "#315F79", 700),
        text(54, 112, scenario.replace("_", " "), 36, "#EBE6D1", "#315F79", 700),
        text(940, 62, "5.0 / 5000 K", 20, "#EBE6D1", "#315F79", 700),
        text(940, 98, "SKY 0.8 / FOG 0.003", 16, "#EBE6D1", "#315F79"),
        '<rect x="0" y="170" width="1280" height="550" fill="#B9A783"/>',
    ]
    if scenario == SCENARIOS[0]:
        lines += ['<circle cx="1100" cy="245" r="48" fill="#E8C9A5"/>', '<polygon points="0,530 1280,300 1280,720 0,720" fill="#D8C8A9"/>', '<polygon points="0,585 1280,390 1280,720 0,720" fill="#6D7F62" opacity="0.38"/>']
    elif scenario == SCENARIOS[1]:
        lines += ['<polygon points="0,170 920,170 650,410 0,500" fill="#315F79" opacity="0.30"/>', '<polygon points="80,170 170,170 0,365 0,270" fill="#4D5051" opacity="0.42"/>', '<polygon points="280,170 370,170 70,510 0,510 0,470" fill="#4D5051" opacity="0.42"/>', '<polygon points="480,170 570,170 260,520 160,520" fill="#4D5051" opacity="0.42"/>', '<polygon points="680,170 770,170 460,520 360,520" fill="#4D5051" opacity="0.42"/>']
    else:
        lines += ['<polygon points="0,560 1280,350 1280,720 0,720" fill="#E8C9A5" opacity="0.70"/>', '<polygon points="0,650 1280,475 1280,720 0,720" fill="#A65F47" opacity="0.32"/>', '<line x1="0" y1="610" x2="1280" y2="440" stroke="#315F79" stroke-width="20" opacity="0.72"/>']
    diagnostics = {target: (foreground, background) for target, foreground, background in TARGET_DIAGNOSTICS}
    for target_id, x, backdrop, swatch, title, note in CARDS:
        foreground, background = diagnostics[target_id]
        lines += [
            f'<g id="{target_id}" data-contrast-kind="target/background" data-foreground="{foreground}" '
            f'data-background="{background}" data-contrast-ratio="{contrast(foreground, background):.4f}">',
            f'<rect x="{x}" y="470" width="212" height="198" rx="8" fill="{backdrop}" stroke="#4D5051" stroke-width="2"/>',
            f'<rect x="{x + 18}" y="488" width="176" height="82" rx="4" fill="{swatch}"/>',
        ]
        if target_id == TARGETS[1]:
            lines.append(f'<rect x="{x + 113}" y="488" width="81" height="82" fill="#14B8AD"/>')
        label_fill = "#EBE6D1" if backdrop in ("#315F79", "#4D5051", "#1F2E38") else "#4D5051"
        lines += [text(x + 18, 608, title, 14, label_fill, backdrop, 700), text(x + 18, 636, note, 11, label_fill, backdrop), "</g>"]
    lines += [text(50, 700, "REVIEW ARTIFACT / NO PRODUCTION, PHOTOMETRIC, ACCESSIBILITY, LIGHTING, OR GAMEPLAY CLAIM", 13, "#1F2E38", "#B9A783", 700), "</svg>"]
    return "\n".join(lines) + "\n"


def unified_svg() -> str:
    lines = svg_open(1920, 1080, "Unified Sundale late-afternoon review board")
    lines += [
        '<rect x="0" y="0" width="1920" height="150" fill="#315F79"/>',
        text(70, 65, "SUNDALE LATE-AFTERNOON", 38, "#EBE6D1", "#315F79", 700),
        text(70, 110, "LIGHTING + ATMOSPHERE REVIEW BOARD", 22, "#EBE6D1", "#315F79", 700),
        text(1480, 62, "DIRECTIONAL 5.0 / 5000 K", 18, "#EBE6D1", "#315F79", 700),
        text(1480, 100, "SKY 0.8 / FOG 0.003", 18, "#EBE6D1", "#315F79"),
    ]
    for scenario, x in zip(SCENARIOS, (60, 680, 1300)):
        lines += [
            f'<rect x="{x}" y="210" width="560" height="650" rx="12" fill="#B9A783" stroke="#4D5051" stroke-width="3"/>',
            f'<rect x="{x}" y="210" width="560" height="86" rx="12" fill="#4D5051"/>',
            text(x + 28, 263, scenario.replace("_", " "), 19, "#EBE6D1", "#4D5051", 700),
            f'<polygon points="{x + 28},720 {x + 532},480 {x + 532},690 {x + 28},820" fill="#E8C9A5" opacity="0.68"/>',
            f'<line x1="{x + 36}" y1="760" x2="{x + 524}" y2="548" stroke="#315F79" stroke-width="18"/>',
            f'<circle cx="{x + 468}" cy="372" r="42" fill="#C46D3B" opacity="0.82"/>',
            text(x + 28, 835, "5 READ TARGETS / GEOMETRY STUDY", 15, "#1F2E38", "#B9A783", 700),
        ]
    lines += ['<rect x="60" y="918" width="1800" height="106" rx="8" fill="#D8C8A9" stroke="#4D5051" stroke-width="2"/>', text(88, 958, "PALETTE", 14, "#4D5051", "#D8C8A9", 700)]
    for i, color in enumerate(PALETTE):
        x = 220 + i * 225
        lines += [f'<rect x="{x}" y="940" width="54" height="54" fill="{color}" stroke="#4D5051"/>', text(x + 68, 974, color, 15, "#4D5051", "#D8C8A9", 700)]
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def provenance_md() -> str:
    bindings = "\n".join(f"- `{SOURCE_REL.as_posix()}:{line}` = `{literal}`" for line, literal in SOURCE_BINDINGS)
    flags = "\n".join(f"- `{key}={str(value).lower() if isinstance(value, bool) else value}`" for key, value in FLAGS.items())
    return f"""# Provenance

Deterministic standard-library/native-geometry review artifact.

- Direct source authority: `{SOURCE_REL.as_posix()}`
- Source SHA-256: `{SOURCE_SHA256}`
- Weather ID: `{WEATHER_ID}`
- Scenario IDs: {", ".join(f'`{item}`' for item in SCENARIOS)}
- Target IDs: {", ".join(f'`{item}`' for item in TARGETS)}

## Exact source bindings

{bindings}

## Scope flags

{flags}
"""


def base_payloads() -> dict[str, bytes]:
    values = {"PROVENANCE.md": provenance_md(), "Unified.svg": unified_svg(), **{f"{s}.svg": scenario_svg(s) for s in SCENARIOS}}
    return {name: value.encode("utf-8") for name, value in values.items()}


def identity(name: str, data: bytes) -> dict[str, object]:
    return {"file": name, "bytes": len(data), "sha256": sha(data)}


def manifest(base: dict[str, bytes]) -> dict[str, object]:
    builder = Path(__file__).read_bytes()
    identity_names = ("PROVENANCE.md", "Unified.svg") + tuple(f"{s}.svg" for s in SCENARIOS)
    return {
        "artifact": "SundaleLateAfternoonLightingAtmosphereReviewBoard",
        "weather_id": WEATHER_ID,
        "source_authority": {"repo_path": SOURCE_REL.as_posix(), "sha256": SOURCE_SHA256, "bindings": [{"line": line, "literal": literal} for line, literal in SOURCE_BINDINGS]},
        "palette": list(PALETTE),
        "material_inputs": MATERIAL_INPUTS,
        "atmosphere": ATMOSPHERE,
        "scenarios": [{"id": s, "file": f"{s}.svg", "viewBox": [0, 0, 1280, 720], "targets": list(TARGETS)} for s in SCENARIOS],
        "unified": {"file": "Unified.svg", "viewBox": [0, 0, 1920, 1080]},
        "flags": FLAGS,
        "diagnostics": {
            "minimum_text_background_contrast": 4.5,
            "minimum_target_background_contrast": 3.0,
            "target_background": [{"target_id": target, "foreground": fg, "background": bg, "contrast": round(contrast(fg, bg), 4)} for target, fg, bg in TARGET_DIAGNOSTICS],
            "containment_failures": 0,
            "overlap_failures": 0,
            "clipping_failures": 0,
        },
        "file_identities": [identity(Path(__file__).name, builder)] + [identity(name, base[name]) for name in identity_names],
    }


def payloads() -> dict[str, bytes]:
    base = base_payloads()
    data = json.dumps(manifest(base), indent=2, sort_keys=True).encode("utf-8") + b"\n"
    return {"manifest.json": data, **base}


def validate_source() -> None:
    raw = SOURCE.read_bytes()
    assert sha(raw) == SOURCE_SHA256
    lines = raw.decode("utf-8").splitlines()
    for line, literal in SOURCE_BINDINGS:
        assert lines[line - 1] == literal, f"source binding mismatch at {SOURCE_REL.as_posix()}:{line}"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_svg(path: Path, expected_viewbox: str, expected_ids: tuple[str, ...]) -> None:
    raw = path.read_text(encoding="utf-8")
    assert not FORBIDDEN_RAW.search(raw.replace(f'xmlns="{SVG_NS}"', ""))
    root = ET.fromstring(raw)
    assert root.tag == f"{{{SVG_NS}}}svg" and root.attrib.get("viewBox") == expected_viewbox
    ids = tuple(node.attrib["id"] for node in root.iter() if "id" in node.attrib)
    assert ids == expected_ids
    for node in root.iter():
        assert local_name(node.tag) not in FORBIDDEN_TAGS
        for attribute in node.attrib:
            plain = local_name(attribute)
            assert plain not in FORBIDDEN_ATTRIBUTES and not plain.lower().startswith("on")
        if local_name(node.tag) == "text":
            assert node.attrib.get("font-family") == "sans-serif"
        kind = node.attrib.get("data-contrast-kind")
        if kind:
            foreground, background = node.attrib["data-foreground"], node.attrib["data-background"]
            ratio = float(node.attrib["data-contrast-ratio"])
            assert abs(ratio - contrast(foreground, background)) < .0001
            assert ratio >= (4.5 if kind == "text/background" else 3.0)
    boxes = []
    for node in root.iter():
        if node.attrib.get("id") in TARGETS:
            rect = next(child for child in node if local_name(child.tag) == "rect")
            box = tuple(float(rect.attrib[key]) for key in ("x", "y", "width", "height"))
            boxes.append(box)
    if expected_ids:
        width, height = (float(value) for value in expected_viewbox.split()[2:])
        assert len(boxes) == len(TARGETS)
        assert all(x >= 0 and y >= 0 and x + w <= width and y + h <= height for x, y, w, h in boxes)
        for i, (ax, ay, aw, ah) in enumerate(boxes):
            for bx, by, bw, bh in boxes[i + 1:]:
                assert ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay


def validate(directory: Path, focused: bool = False) -> None:
    validate_source()
    assert {path.name for path in directory.iterdir() if path.is_file()} == EXPECTED_FILES
    data = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    assert data == manifest(base_payloads())
    assert data["weather_id"] == WEATHER_ID and tuple(data["palette"]) == PALETTE
    assert data["material_inputs"] == MATERIAL_INPUTS and data["atmosphere"] == ATMOSPHERE and data["flags"] == FLAGS
    assert tuple(item["id"] for item in data["scenarios"]) == SCENARIOS
    assert all(tuple(item["targets"]) == TARGETS for item in data["scenarios"])
    for record in data["file_identities"]:
        actual = (directory / record["file"]).read_bytes()
        assert record["bytes"] == len(actual) and record["sha256"] == sha(actual)
    names = tuple(f"{scenario}.svg" for scenario in SCENARIOS) if focused else ("Unified.svg",) + tuple(f"{scenario}.svg" for scenario in SCENARIOS)
    for name in names:
        validate_svg(directory / name, "0 0 1280 720" if name != "Unified.svg" else "0 0 1920 1080", TARGETS if name != "Unified.svg" else ())


def clean_build() -> None:
    shutil.rmtree(ROOT / "__pycache__", ignore_errors=True)
    for path in ROOT.iterdir():
        if path.is_file() and path.name != Path(__file__).name:
            path.unlink()
    for name, data in payloads().items():
        (ROOT / name).write_bytes(data)
    validate(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("clean-build", "reopen", "focused"))
    args = parser.parse_args()
    if args.mode == "clean-build":
        clean_build()
    else:
        validate(ROOT, focused=args.mode == "focused")
    print(f"OK mode={args.mode} files=7 builder_bytes={Path(__file__).stat().st_size} builder_sha256={sha(Path(__file__).read_bytes())}")


if __name__ == "__main__":
    main()
