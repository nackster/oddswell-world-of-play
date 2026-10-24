#!/usr/bin/env python3
"""Build and validate the Phase 1L.3l current-camera composition SVG board."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
BUILDER = Path(__file__).name
MANIFEST = "manifest.json"
PROVENANCE = "PROVENANCE.md"
UNIFIED = "Unified_CurrentBetaCameraComposition.svg"
CITY = "City_CurrentBetaCameraComposition.svg"
STADIUM = "Stadium_CurrentBetaCameraComposition.svg"
GENERATED = (MANIFEST, PROVENANCE, UNIFIED, CITY, STADIUM)
EXPECTED_FILES = {BUILDER, *GENERATED}

PALETTE = ("#2C4250", "#50B3AD", "#FAE595", "#999EA2", "#FAF8F0")
DARK, TEAL, YELLOW, GRAY, CREAM = PALETTE
CITY_SOURCE = Path("client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp")
CITY_SHA = "22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298"
STADIUM_SOURCE = Path("client/OddsWell/Source/OddsWell/ReplayBenchmarkActor.cpp")
STADIUM_SHA = "CE070D7EC2EF7D94093B5CD943C271426BCF8A10B7D31D287BC32235FD8F3116"
SCENARIOS = (
    "CITY_AVATAR_CLOTHING_READ",
    "CITY_DESTINATION_LANDMARK_READ",
    "STADIUM_FULL_COURT_ACTION_READ",
    "STADIUM_SCORE_EVENT_SAFE_AREA",
)
CLAIMS = {
    "production_claim": False,
    "camera_change": False,
    "lens_lock": False,
    "accessibility_ready": False,
    "gameplay_change": False,
}
FORBIDDEN_TAGS = {
    "script", "image", "foreignObject", "animate", "animateMotion", "animateTransform", "set", "style"
}
HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: str, size: int, *, fill: str = DARK, bg: str = CREAM,
         anchor: str = "start", weight: int = 600) -> str:
    return (f'<text x="{x:g}" y="{y:g}" fill="{fill}" data-bg="{bg}" '
            f'font-family="sans-serif" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(value)}</text>')


def boxed(kind: str, identifier: str, x: float, y: float, w: float, h: float, body: str) -> str:
    return (f'<g data-kind="{kind}" data-id="{identifier}" data-box="{x:g} {y:g} {w:g} {h:g}">'
            f'{body}</g>')


def label(identifier: str, x: float, y: float, w: float, h: float, title: str, detail: str) -> str:
    body = (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="12" fill="{CREAM}" '
            f'stroke="{GRAY}" stroke-width="3"/>'
            + text(x + 18, y + 31, title, 18, weight=800)
            + text(x + 18, y + 58, detail, 14, weight=600))
    return boxed("label", identifier, x, y, w, h, body)


def avatar_proxy(identifier: str, x: float, y: float, w: float, h: float) -> str:
    cx = x + w / 2
    body = (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="18" fill="{DARK}"/>'
            f'<circle cx="{cx:g}" cy="{y + 54:g}" r="28" fill="{YELLOW}" data-graphic-bg="{DARK}"/>'
            f'<path d="M {cx - 54:g} {y + 112:g} L {cx:g} {y + 82:g} L {cx + 54:g} {y + 112:g} '
            f'L {cx + 40:g} {y + 222:g} L {cx - 40:g} {y + 222:g} Z" fill="{TEAL}" data-graphic-bg="{DARK}"/>'
            f'<rect x="{cx - 38:g}" y="{y + 134:g}" width="76" height="18" fill="{YELLOW}" data-graphic-bg="{DARK}"/>'
            f'<line x1="{cx - 24:g}" y1="{y + 222:g}" x2="{cx - 35:g}" y2="{y + h - 18:g}" stroke="{YELLOW}" '
            f'stroke-width="16" data-graphic-bg="{DARK}"/>'
            f'<line x1="{cx + 24:g}" y1="{y + 222:g}" x2="{cx + 35:g}" y2="{y + h - 18:g}" stroke="{YELLOW}" '
            f'stroke-width="16" data-graphic-bg="{DARK}"/>')
    return boxed("proxy", identifier, x, y, w, h, body)


def landmark_proxy(identifier: str, x: float, y: float, w: float, h: float) -> str:
    body = (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="18" fill="{DARK}"/>'
            f'<polygon points="{x + w/2:g},{y + 24:g} {x + w - 24:g},{y + 104:g} {x + 24:g},{y + 104:g}" '
            f'fill="{YELLOW}" data-graphic-bg="{DARK}"/>'
            f'<rect x="{x + 50:g}" y="{y + 104:g}" width="{w - 100:g}" height="{h - 130:g}" '
            f'fill="{TEAL}" data-graphic-bg="{DARK}"/>'
            f'<rect x="{x + w/2 - 24:g}" y="{y + 158:g}" width="48" height="{h - 184:g}" '
            f'fill="{DARK}" data-graphic-bg="{TEAL}"/>')
    return boxed("proxy", identifier, x, y, w, h, body)


def court_proxy(identifier: str, x: float, y: float, w: float, h: float) -> str:
    body = (f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="14" fill="{DARK}"/>'
            f'<rect x="{x + 20:g}" y="{y + 20:g}" width="{w - 40:g}" height="{h - 40:g}" fill="none" '
            f'stroke="{YELLOW}" stroke-width="8" data-graphic-bg="{DARK}"/>'
            f'<line x1="{x + w/2:g}" y1="{y + 20:g}" x2="{x + w/2:g}" y2="{y + h - 20:g}" '
            f'stroke="{YELLOW}" stroke-width="6" data-graphic-bg="{DARK}"/>'
            f'<circle cx="{x + w/2:g}" cy="{y + h/2:g}" r="44" fill="none" stroke="{YELLOW}" '
            f'stroke-width="6" data-graphic-bg="{DARK}"/>'
            f'<circle cx="{x + w*.38:g}" cy="{y + h*.38:g}" r="15" fill="{TEAL}" data-graphic-bg="{DARK}"/>'
            f'<circle cx="{x + w*.62:g}" cy="{y + h*.62:g}" r="15" fill="{GRAY}" data-graphic-bg="{DARK}"/>')
    return boxed("proxy", identifier, x, y, w, h, body)


def palette_row(x: float, y: float) -> str:
    return "".join(f'<rect x="{x + i*34:g}" y="{y:g}" width="26" height="12" fill="{color}"/>'
                   for i, color in enumerate(PALETTE))


def svg(width: int, height: int, context: str, content: str, *, stadium_hud: bool = False) -> str:
    margin_x, margin_y = width * .05, height * .05
    hud = ' data-stadium-hud-reserved-top-percent="18"' if stadium_hud else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" data-context="{context}" data-margin-percent="5"{hud}>\n'
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="{DARK}"/>\n'
            f'<rect data-content-frame="true" x="{margin_x:g}" y="{margin_y:g}" '
            f'width="{width - 2*margin_x:g}" height="{height - 2*margin_y:g}" rx="22" fill="{CREAM}"/>\n'
            f'{content}\n</svg>')


def city_content(x: float, y: float, w: float, h: float, prefix: str) -> str:
    proxy_y, proxy_h = y + 118, h - 246
    pw = (w - 78) / 2
    return "".join((
        text(x + 28, y + 44, "CITY / THIRD-PERSON TRAILING", 25, weight=800),
        text(x + 28, y + 76, "420 BOOM  |  ATTACH +65  |  COLLISION TRUE", 15),
        text(x + 28, y + 100, "PITCH -65..65  |  YAW CONTINUOUS  |  FOV ENGINE_DEFAULT_UNSET", 14),
        avatar_proxy(prefix + "_avatar", x + 26, proxy_y, pw, proxy_h),
        landmark_proxy(prefix + "_landmark", x + 52 + pw, proxy_y, pw, proxy_h),
        label(prefix + "_avatar_label", x + 26, y + h - 106, pw, 78,
              "CITY_AVATAR_CLOTHING_READ", "Complete silhouette and clothing bands"),
        label(prefix + "_landmark_label", x + 52 + pw, y + h - 106, pw, 78,
              "CITY_DESTINATION_LANDMARK_READ", "Complete destination silhouette"),
        palette_row(x + w - 190, y + 28),
    ))


def stadium_content(x: float, y: float, w: float, h: float, prefix: str) -> str:
    hud_h = h * .18
    court_y = y + hud_h + 72
    court_h = h - hud_h - 198
    return "".join((
        f'<rect data-hud-band="true" x="{x:g}" y="{y:g}" width="{w:g}" height="{hud_h:g}" '
        f'fill="{GRAY}" opacity="1"/>',
        text(x + 28, y + 38, "STADIUM / FIXED BROADCAST", 25, weight=800),
        text(x + 28, y + 68, "LOC (2400,-3000,1800)  |  ROT (-25,129,0)  |  FOV 55 FIXED", 14),
        text(x + w - 28, y + hud_h - 18, "TOP 18% RESERVED HUD BAND", 14, anchor="end", weight=800),
        court_proxy(prefix + "_court", x + 26, court_y, w - 52, court_h),
        label(prefix + "_court_label", x + 26, y + h - 106, (w - 78) / 2, 78,
              "STADIUM_FULL_COURT_ACTION_READ", "Complete court and two action markers"),
        label(prefix + "_score_label", x + 52 + (w - 78) / 2, y + h - 106, (w - 78) / 2, 78,
              "STADIUM_SCORE_EVENT_SAFE_AREA", "Action remains below reserved band"),
        palette_row(x + w - 190, y + 20),
    ))


def render_unified() -> str:
    content = "".join((
        text(124, 106, "CURRENT BETA CAMERA COMPOSITION", 34, weight=800),
        text(1796, 106, "SOURCE-LOCKED REVIEW PROXIES", 17, anchor="end", weight=800),
        city_content(116, 150, 814, 858, "unified_city"),
        stadium_content(990, 150, 814, 858, "unified_stadium"),
    ))
    return svg(1920, 1080, "UNIFIED", content, stadium_hud=True)


def render_city() -> str:
    return svg(1280, 720, "CITY", city_content(84, 56, 1112, 608, "city"))


def render_stadium() -> str:
    return svg(1280, 720, "STADIUM", stadium_content(84, 56, 1112, 608, "stadium"), stadium_hud=True)


def provenance_text() -> str:
    return f"""# Current Beta Camera Composition Review Board Provenance

- Phase: `Phase 1L.3l`.
- Status: source-locked, nonproduction composition review evidence.
- Generator: `{BUILDER}` using the Python standard library only.
- City authority: `{CITY_SOURCE.as_posix()}` at SHA-256 `{CITY_SHA}`.
- City facts: `CITY_THIRD_PERSON_TRAILING`; boom `420`; attachment `+65`; collision `true`; pitch `-65..65`; continuous yaw; FOV literal `ENGINE_DEFAULT_UNSET` because the source does not set a camera FOV.
- Stadium authority: `{STADIUM_SOURCE.as_posix()}` at SHA-256 `{STADIUM_SHA}`.
- Stadium facts: `STADIUM_FIXED_BROADCAST`; location `(2400,-3000,1800)`; rotation `(-25,129,0)`; fixed FOV `55`.
- Scenarios: `{SCENARIOS[0]}`, `{SCENARIOS[1]}`, `{SCENARIOS[2]}`, `{SCENARIOS[3]}`.
- Palette: `{PALETTE[0]}`, `{PALETTE[1]}`, `{PALETTE[2]}`, `{PALETTE[3]}`, `{PALETTE[4]}` only.
- Geometry: native SVG geometric proxies only; five-percent outer content margin; complete proxy and label containment; zero proxy-label overlap; stadium top eighteen percent reserved as a HUD band.
- Accessibility measurement: text contrast floor `4.5:1`; graphic contrast floor `3.0:1`. These measurements do not claim accessibility readiness.
- External references, images, fonts, textures, brands, scripts, animation, and runtime changes: none.
- Claim flags: `production_claim=false`, `camera_change=false`, `lens_lock=false`, `accessibility_ready=false`, `gameplay_change=false`.
"""


def artifact(path: Path) -> dict[str, object]:
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def source_contract() -> dict[str, object]:
    return {
        "city": {
            "id": "CITY_THIRD_PERSON_TRAILING", "source": CITY_SOURCE.as_posix(), "source_sha256": CITY_SHA,
            "boom": 420, "attachment_z": 65, "collision": True, "pitch_min": -65, "pitch_max": 65,
            "yaw": "continuous", "fov": "ENGINE_DEFAULT_UNSET",
        },
        "stadium": {
            "id": "STADIUM_FIXED_BROADCAST", "source": STADIUM_SOURCE.as_posix(), "source_sha256": STADIUM_SHA,
            "location": [2400, -3000, 1800], "rotation": [-25, 129, 0], "fov": 55, "fixed": True,
        },
    }


def manifest_data() -> dict[str, object]:
    outputs = (ROOT / UNIFIED, ROOT / CITY, ROOT / STADIUM)
    return {
        "schema": "oddswell-current-beta-camera-composition-v1",
        "phase": "Phase 1L.3l",
        "status": "nonproduction_review_evidence",
        "renderer": "python_stdlib_native_svg",
        "sources": source_contract(),
        "scenarios": list(SCENARIOS),
        "palette": list(PALETTE),
        "layout_contract": {
            "outer_margin_percent": 5, "stadium_reserved_hud_top_percent": 18,
            "proxy_containment": True, "label_containment": True, "proxy_label_overlap_count": 0,
        },
        "contrast_contract": {"text_minimum": 4.5, "graphic_minimum": 3.0},
        "claim_flags": CLAIMS,
        "boundaries": {
            "external_references": 0, "images": 0, "external_fonts": 0, "textures": 0, "brands": 0,
            "scripts": 0, "foreign_objects": 0, "animation": 0, "interiors": 0,
        },
        "builder": artifact(ROOT / BUILDER),
        "provenance": artifact(ROOT / PROVENANCE),
        "outputs": [artifact(path) | {
            "width": 1920 if path.name == UNIFIED else 1280,
            "height": 1080 if path.name == UNIFIED else 720,
        } for path in outputs],
    }


def luminance(color: str) -> float:
    values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + .05) / (low + .05)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_box(value: str) -> tuple[float, float, float, float]:
    return tuple(map(float, value.split()))  # type: ignore[return-value]


def overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def validate_sources() -> None:
    city = REPO / CITY_SOURCE
    stadium = REPO / STADIUM_SOURCE
    assert sha256(city) == CITY_SHA and sha256(stadium) == STADIUM_SHA
    city_raw = city.read_text(encoding="utf-8")
    stadium_raw = stadium.read_text(encoding="utf-8")
    for literal in ("constexpr float CameraDistance = 420.0f;", "constexpr float CameraPitchMin = -65.0f;",
                    "constexpr float CameraPitchMax = 65.0f;", "CameraBoom->SetRelativeLocation(FVector(0.0, 0.0, 65.0));",
                    "CameraBoom->bDoCollisionTest = UseCameraCollision;", "void AOddsWellPlaceholderCharacter::LookYaw"):
        assert literal in city_raw
    assert "constexpr bool UseCameraCollision = true;" in city_raw
    assert not re.search(r"FollowCamera->(?:FieldOfView|SetFieldOfView)", city_raw)
    for literal in ("FVector(2400.0, -3000.0, 1800.0)", "FRotator(-25.0, 129.0, 0.0)",
                    "BenchmarkCamera->FieldOfView = 55.0f;"):
        assert literal in stadium_raw


def validate_svg(path: Path, width: int, height: int, expected_scenarios: set[str]) -> tuple[float, float]:
    raw = path.read_text(encoding="utf-8")
    assert raw.isascii(), f"{path.name}: non-ASCII/mojibake risk"
    root = ET.fromstring(raw)
    assert local(root.tag) == "svg" and root.get("viewBox") == f"0 0 {width} {height}"
    assert root.get("data-margin-percent") == "5"
    assert {c.upper() for c in HEX.findall(raw)} == set(PALETTE)
    text_ratios, graphic_ratios = [], []
    boxes = {"proxy": [], "label": []}
    margin_x, margin_y = width * .05, height * .05
    for node in root.iter():
        tag = local(node.tag)
        assert tag not in FORBIDDEN_TAGS
        for key, value in node.attrib.items():
            name, lowered = local(key).lower(), str(value).lower()
            assert name not in {"href", "src"} and not name.startswith("on")
            assert "url(" not in lowered and "javascript:" not in lowered and "data:" not in lowered
        if tag == "text":
            assert node.get("font-family") == "sans-serif"
            ratio = contrast(node.get("fill", ""), node.get("data-bg", ""))
            text_ratios.append(ratio)
        if node.get("data-graphic-bg"):
            color = node.get("fill") if node.get("fill") not in (None, "none") else node.get("stroke")
            graphic_ratios.append(contrast(str(color), str(node.get("data-graphic-bg"))))
        kind = node.get("data-kind")
        if kind in boxes:
            box = parse_box(str(node.get("data-box")))
            x, y, w, h = box
            assert x >= margin_x and y >= margin_y and x + w <= width - margin_x and y + h <= height - margin_y
            boxes[kind].append(box)
    assert text_ratios and min(text_ratios) >= 4.5
    assert graphic_ratios and min(graphic_ratios) >= 3.0
    assert not any(overlaps(proxy, label_box) for proxy in boxes["proxy"] for label_box in boxes["label"])
    visible = set(root.itertext())
    assert expected_scenarios <= visible
    if path.name in {UNIFIED, STADIUM}:
        assert root.get("data-stadium-hud-reserved-top-percent") == "18"
        bands = [node for node in root.iter() if node.get("data-hud-band") == "true"]
        assert len(bands) == 1
    return min(text_ratios), min(graphic_ratios)


def validate_manifest() -> None:
    data = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    assert data["sources"] == source_contract()
    assert data["scenarios"] == list(SCENARIOS) and data["palette"] == list(PALETTE)
    assert data["claim_flags"] == CLAIMS and all(value is False for value in data["claim_flags"].values())
    assert all(value == 0 for value in data["boundaries"].values())
    for record in [data["builder"], data["provenance"], *data["outputs"]]:
        path = ROOT / record["file"]
        assert path.stat().st_size == record["bytes"] and sha256(path) == record["sha256"]


def validate() -> tuple[float, float]:
    assert {p.name for p in ROOT.iterdir() if p.is_file()} == EXPECTED_FILES
    validate_sources()
    ratios = (
        validate_svg(ROOT / UNIFIED, 1920, 1080, set(SCENARIOS)),
        validate_svg(ROOT / CITY, 1280, 720, set(SCENARIOS[:2])),
        validate_svg(ROOT / STADIUM, 1280, 720, set(SCENARIOS[2:])),
    )
    validate_manifest()
    return min(r[0] for r in ratios), min(r[1] for r in ratios)


def clean() -> None:
    for name in GENERATED:
        path = ROOT / name
        if path.exists():
            path.unlink()


def build(clean_first: bool = False) -> tuple[float, float]:
    if clean_first:
        clean()
    write(ROOT / UNIFIED, render_unified())
    write(ROOT / CITY, render_city())
    write(ROOT / STADIUM, render_stadium())
    write(ROOT / PROVENANCE, provenance_text())
    write(ROOT / MANIFEST, json.dumps(manifest_data(), indent=2, sort_keys=True))
    return validate()


def snapshot() -> dict[str, tuple[int, int, str]]:
    return {name: ((ROOT / name).stat().st_size, (ROOT / name).stat().st_mtime_ns, sha256(ROOT / name))
            for name in EXPECTED_FILES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=("build", "clean-build", "reopen", "focused"), default="build")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--focused-validate", action="store_true")
    args = parser.parse_args()
    mode = "focused" if args.focused_validate else "reopen" if args.validate_only else "clean-build" if args.clean else args.mode
    if mode in {"reopen", "focused"}:
        before = snapshot()
        text_min, graphic_min = validate()
        assert snapshot() == before, f"{mode} mutated review artifacts"
        marker = "FOCUSED" if mode == "focused" else "REOPEN_XML"
    else:
        text_min, graphic_min = build(mode == "clean-build")
        marker = "BUILD"
    print(f"ODDSWELL_CURRENT_CAMERA_COMPOSITION_{marker}|result=PASS|files=6|renders=3|scenarios=4|"
          f"text_contrast_min={text_min:.4f}|graphic_contrast_min={graphic_min:.4f}|"
          "outer_margin_percent=5|stadium_hud_top_percent=18|proxy_label_overlap=0|forbidden=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
