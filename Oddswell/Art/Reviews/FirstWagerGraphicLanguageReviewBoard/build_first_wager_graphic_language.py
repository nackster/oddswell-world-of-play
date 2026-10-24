"""Build and validate the noncanonical Phase 1L.3k first-wager graphic-language SVG board."""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

OUTPUTS = {
    "Unified_FirstWagerGraphicLanguage.svg": (1920, 1080, "UNIFIED"),
    "Context_TicketBoothPrompt.svg": (1280, 720, "ticket_booth_prompt"),
    "Context_MatchWinnerSelection.svg": (1280, 720, "match_winner_selection"),
    "Context_PrecommitConfirmation.svg": (1280, 720, "precommit_confirmation"),
    "Context_SettledReceipt.svg": (1280, 720, "settled_receipt"),
}

STATE_SHAPES = {
    "INTERACT": "OPEN_CIRCLE_DOT",
    "ACTIVE": "TRIANGLE",
    "LOCKED": "BARRED_SQUARE",
    "SELECTED": "DIAMOND",
    "CONFIRM": "DOUBLE_CHEVRON",
    "SETTLED": "RING_CHECK",
}
TYPE_ROLES = ("DISPLAY_TITLE", "STATE_LABEL", "PRIMARY_VALUE", "INSTRUCTION")

# Exact current production linear RGBA anchors, deterministically converted to sRGB.
PALETTE = {
    "dark_navy": "#2C4250",
    "teal": "#50B3AD",
    "warm_gold": "#FAE595",
    "muted": "#999EA2",
    "white": "#FAF8F0",
}
PALETTE_SOURCE = "client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp"
PALETTE_SOURCE_SHA256 = "22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298"
PALETTE_CONVERSIONS = {
    "dark_navy": {"source_line": 9133, "source_expression": "FLinearColor(0.025f, 0.055f, 0.08f)", "linear_rgba": [0.025, 0.055, 0.08, 1.0], "srgb_hex": "#2C4250"},
    "teal": {"source_line": 9134, "source_expression": "FLinearColor(0.08f, 0.45f, 0.42f)", "linear_rgba": [0.08, 0.45, 0.42, 1.0], "srgb_hex": "#50B3AD"},
    "warm_gold": {"source_line": 8932, "source_expression": "FLinearColor(0.96f, 0.78f, 0.30f)", "linear_rgba": [0.96, 0.78, 0.30, 1.0], "srgb_hex": "#FAE595"},
    "muted": {"source_line": 9136, "source_expression": "FLinearColor(0.32f, 0.34f, 0.36f)", "linear_rgba": [0.32, 0.34, 0.36, 1.0], "srgb_hex": "#999EA2"},
    "white": {"source_line": 9126, "source_expression": "FLinearColor(0.96f, 0.94f, 0.87f, 1.0f)", "linear_rgba": [0.96, 0.94, 0.87, 1.0], "srgb_hex": "#FAF8F0"},
}

CURRENT_COPY = {
    "teams": ("Harbor City Waves", "Mesa Vista Sol"),
    "match": "Harbor City Waves vs Mesa Vista Sol",
    "ticket_prompt": "Press E to open betting odds",
    "stake": "40 Odds Bucks",
    "payout": "94 Odds Bucks",
    "balance": "154 Odds Bucks",
}

EXPECTED_STATE_COUNTS = {
    "Unified_FirstWagerGraphicLanguage.svg": Counter({state: 1 for state in STATE_SHAPES}),
    "Context_TicketBoothPrompt.svg": Counter({"INTERACT": 1}),
    "Context_MatchWinnerSelection.svg": Counter({"ACTIVE": 1, "LOCKED": 1, "SELECTED": 1}),
    "Context_PrecommitConfirmation.svg": Counter({"SELECTED": 1, "CONFIRM": 1}),
    "Context_SettledReceipt.svg": Counter({"SETTLED": 1}),
}
EXPECTED_TYPE_COUNTS = {
    "Unified_FirstWagerGraphicLanguage.svg": Counter(
        {"DISPLAY_TITLE": 1, "STATE_LABEL": 6, "PRIMARY_VALUE": 4, "INSTRUCTION": 1}
    ),
    "Context_TicketBoothPrompt.svg": Counter(
        {"DISPLAY_TITLE": 1, "STATE_LABEL": 1, "PRIMARY_VALUE": 1, "INSTRUCTION": 1}
    ),
    "Context_MatchWinnerSelection.svg": Counter(
        {"DISPLAY_TITLE": 1, "STATE_LABEL": 3, "PRIMARY_VALUE": 2, "INSTRUCTION": 1}
    ),
    "Context_PrecommitConfirmation.svg": Counter(
        {"DISPLAY_TITLE": 1, "STATE_LABEL": 2, "PRIMARY_VALUE": 3, "INSTRUCTION": 1}
    ),
    "Context_SettledReceipt.svg": Counter(
        {"DISPLAY_TITLE": 1, "STATE_LABEL": 1, "PRIMARY_VALUE": 3, "INSTRUCTION": 1}
    ),
}

FORBIDDEN_TEXT = (
    "place bet",
    "live odds",
    "cash",
    "credit card",
    "real money",
    "alcohol",
    "new market",
    "new state",
    "probability",
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4))


def relative_luminance(value):
    channels = []
    for channel in hex_rgb(value):
        channels.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(foreground, background):
    lighter, darker = sorted((relative_luminance(foreground), relative_luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def text_node(identifier, role, x, y, value, size, fill="dark_navy", anchor="start", weight=600):
    return (
        f'<text id="{identifier}" data-type-role="{role}" x="{x}" y="{y}" '
        f'font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}" fill="{PALETTE[fill]}">{esc(value)}</text>'
    )


def state_marker(state, x, y, size, instance):
    color_name = {
        "INTERACT": "teal",
        "ACTIVE": "warm_gold",
        "LOCKED": "muted",
        "SELECTED": "white",
        "CONFIRM": "warm_gold",
        "SETTLED": "teal",
    }[state]
    color = PALETTE[color_name]
    stroke = max(3.0, size * 0.09)
    center = size / 2
    shape = STATE_SHAPES[state]
    prefix = f"mark_{instance}_{state}"
    parts = [
        f'<g id="{prefix}" data-state-id="{state}" data-shape-id="{shape}" '
        f'data-marker-color="{color}" data-marker-background="{PALETTE["dark_navy"]}">',
        f'<rect x="{x - 12}" y="{y - 12}" width="{size + 24}" height="{size + 24}" rx="18" '
        f'fill="{PALETTE["dark_navy"]}"/>',
    ]
    if state == "INTERACT":
        parts.append(
            f'<circle cx="{x + center}" cy="{y + center}" r="{size * 0.36}" fill="none" '
            f'stroke="{color}" stroke-width="{stroke}"/>'
        )
        parts.append(f'<circle cx="{x + center}" cy="{y + center}" r="{size * 0.10}" fill="{color}"/>')
    elif state == "ACTIVE":
        points = (
            f"{x + center},{y + size * 0.10} "
            f"{x + size * 0.90},{y + size * 0.86} "
            f"{x + size * 0.10},{y + size * 0.86}"
        )
        parts.append(f'<polygon points="{points}" fill="{color}"/>')
    elif state == "LOCKED":
        parts.append(
            f'<rect x="{x + size * 0.14}" y="{y + size * 0.14}" width="{size * 0.72}" '
            f'height="{size * 0.72}" rx="{size * 0.05}" fill="none" stroke="{color}" stroke-width="{stroke}"/>'
        )
        parts.append(
            f'<line x1="{x + size * 0.22}" y1="{y + size * 0.78}" '
            f'x2="{x + size * 0.78}" y2="{y + size * 0.22}" stroke="{color}" stroke-width="{stroke}"/>'
        )
    elif state == "SELECTED":
        points = (
            f"{x + center},{y + size * 0.08} "
            f"{x + size * 0.92},{y + center} "
            f"{x + center},{y + size * 0.92} "
            f"{x + size * 0.08},{y + center}"
        )
        parts.append(f'<polygon points="{points}" fill="{color}"/>')
    elif state == "CONFIRM":
        for offset in (0.05, 0.40):
            points = (
                f"{x + size * offset},{y + size * 0.14} "
                f"{x + size * (offset + 0.34)},{y + center} "
                f"{x + size * offset},{y + size * 0.86}"
            )
            parts.append(
                f'<polyline points="{points}" fill="none" stroke="{color}" '
                f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>'
            )
    elif state == "SETTLED":
        parts.append(
            f'<circle cx="{x + center}" cy="{y + center}" r="{size * 0.38}" fill="none" '
            f'stroke="{color}" stroke-width="{stroke}"/>'
        )
        points = (
            f"{x + size * 0.25},{y + size * 0.52} "
            f"{x + size * 0.44},{y + size * 0.70} "
            f"{x + size * 0.77},{y + size * 0.31}"
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    parts.append("</g>")
    return "".join(parts)


def shell(width, height, context, body):
    return "\n".join(
        (
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="{SVG_NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'data-phase="Phase 1L.3k" data-context="{context}" data-canonical="false">',
            f'<rect id="background" x="0" y="0" width="{width}" height="{height}" fill="{PALETTE["dark_navy"]}"/>',
            body,
            "</svg>",
            "",
        )
    )


def card(x, y, width, height, identifier):
    return (
        f'<rect id="{identifier}" x="{x}" y="{y}" width="{width}" height="{height}" rx="24" '
        f'fill="{PALETTE["white"]}" stroke="{PALETTE["muted"]}" stroke-width="4"/>'
    )


def caption_node(identifier, x, y, value, size):
    return (
        f'<text id="{identifier}" x="{x}" y="{y}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="500" fill="{PALETTE["dark_navy"]}">{esc(value)}</text>'
    )


def unified_svg():
    parts = [
        card(64, 56, 1792, 968, "unified_board"),
        text_node("title", "DISPLAY_TITLE", 112, 132, "FIRST-WAGER GRAPHIC LANGUAGE", 42),
        text_node(
            "instruction",
            "INSTRUCTION",
            112,
            180,
            "Review-only state shapes using the current Harbor / Mesa first-wager values",
            22,
            "dark_navy",
            weight=500,
        ),
    ]
    for index, state in enumerate(STATE_SHAPES):
        column = index % 3
        row = index // 3
        x = 112 + column * 570
        y = 240 + row * 240
        parts.append(card(x, y, 520, 196, f"state_card_{state}"))
        parts.append(state_marker(state, x + 34, y + 44, 108, f"unified_{index + 1}"))
        parts.append(text_node(f"state_label_{state}", "STATE_LABEL", x + 172, y + 82, state, 25))
        parts.append(
            caption_node(f"shape_caption_{state}", x + 172, y + 126, STATE_SHAPES[state].replace("_", " "), 18)
        )
    values = (
        (CURRENT_COPY["match"], 112, 22),
        (CURRENT_COPY["stake"], 720, 24),
        (CURRENT_COPY["payout"], 1110, 24),
        (CURRENT_COPY["balance"], 1470, 24),
    )
    for index, (value, x, size) in enumerate(values):
        parts.append(text_node(f"current_value_{index + 1}", "PRIMARY_VALUE", x, 810, value, size))
    parts.append(
        f'<line id="baseline_rule" x1="112" y1="850" x2="1808" y2="850" '
        f'stroke="{PALETTE["muted"]}" stroke-width="3"/>'
    )
    return shell(1920, 1080, "UNIFIED", "\n".join(parts))


def context_header(identifier, title, instruction):
    return [
        card(56, 48, 1168, 624, f"{identifier}_panel"),
        text_node(f"{identifier}_title", "DISPLAY_TITLE", 104, 124, title, 36),
        text_node(f"{identifier}_instruction", "INSTRUCTION", 104, 166, instruction, 19, "dark_navy", weight=500),
    ]


def ticket_booth_svg():
    parts = context_header(
        "ticket_booth_prompt",
        "TICKET BOOTH",
        "Current interaction prompt language - review only",
    )
    parts.extend(
        (
            state_marker("INTERACT", 152, 248, 156, "ticket_booth"),
            text_node("ticket_state", "STATE_LABEL", 360, 306, "INTERACT", 28),
            text_node("ticket_value", "PRIMARY_VALUE", 360, 360, CURRENT_COPY["ticket_prompt"], 34),
        )
    )
    return shell(1280, 720, "ticket_booth_prompt", "\n".join(parts))


def winner_selection_svg():
    parts = context_header(
        "match_winner_selection",
        "MATCH WINNER",
        "Current Harbor / Mesa selection language - review only",
    )
    cards = (
        (CURRENT_COPY["teams"][0], "SELECTED", 104),
        (CURRENT_COPY["teams"][1], "ACTIVE", 464),
    )
    for index, (team, state, x) in enumerate(cards, 1):
        parts.append(card(x, 222, 312, 304, f"team_card_{index}"))
        parts.append(state_marker(state, x + 28, 250, 112, f"team_{index}"))
        parts.append(text_node(f"team_state_{index}", "STATE_LABEL", x + 164, 300, state, 22))
        parts.append(text_node(f"team_value_{index}", "PRIMARY_VALUE", x + 28, 458, team, 26))
    parts.append(state_marker("LOCKED", 928, 276, 128, "selection_lock"))
    parts.append(text_node("selection_lock_label", "STATE_LABEL", 992, 452, "LOCKED", 22, anchor="middle"))
    return shell(1280, 720, "match_winner_selection", "\n".join(parts))


def precommit_svg():
    parts = context_header(
        "precommit_confirmation",
        "REVIEW AND CONFIRM",
        "Current first-wager values before confirmation - behavior unchanged",
    )
    parts.extend(
        (
            state_marker("SELECTED", 104, 250, 116, "precommit_selected"),
            text_node("precommit_selected_label", "STATE_LABEL", 246, 306, "SELECTED", 22),
            text_node("precommit_match", "PRIMARY_VALUE", 104, 448, CURRENT_COPY["match"], 31),
            text_node("precommit_stake", "PRIMARY_VALUE", 104, 500, CURRENT_COPY["stake"], 27, "dark_navy"),
            state_marker("CONFIRM", 828, 250, 164, "precommit_confirm"),
            text_node("precommit_confirm_label", "STATE_LABEL", 910, 450, "CONFIRM", 22, anchor="middle"),
            text_node("precommit_payout", "PRIMARY_VALUE", 104, 552, CURRENT_COPY["payout"], 27, "dark_navy"),
        )
    )
    return shell(1280, 720, "precommit_confirmation", "\n".join(parts))


def settled_svg():
    parts = context_header(
        "settled_receipt",
        "SETTLED RECEIPT",
        "Current settled first-wager values - immutable history unchanged",
    )
    parts.extend(
        (
            state_marker("SETTLED", 104, 238, 176, "settled_receipt"),
            text_node("settled_state", "STATE_LABEL", 336, 306, "SETTLED", 26),
            text_node("settled_match", "PRIMARY_VALUE", 336, 366, CURRENT_COPY["match"], 33),
            text_node("settled_payout", "PRIMARY_VALUE", 336, 424, CURRENT_COPY["payout"], 29, "dark_navy"),
            text_node("settled_balance", "PRIMARY_VALUE", 336, 482, CURRENT_COPY["balance"], 29, "dark_navy"),
        )
    )
    return shell(1280, 720, "settled_receipt", "\n".join(parts))


def write_outputs():
    renderers = {
        "Unified_FirstWagerGraphicLanguage.svg": unified_svg,
        "Context_TicketBoothPrompt.svg": ticket_booth_svg,
        "Context_MatchWinnerSelection.svg": winner_selection_svg,
        "Context_PrecommitConfirmation.svg": precommit_svg,
        "Context_SettledReceipt.svg": settled_svg,
    }
    for path in ROOT.glob("*.svg"):
        path.unlink()
    for name, renderer in renderers.items():
        (ROOT / name).write_text(renderer(), encoding="utf-8", newline="\n")
    write_provenance()
    write_manifest()


def write_provenance():
    PROVENANCE_PATH.write_text(
        "# First-Wager Graphic-Language Review Board Provenance\n\n"
        "- Phase: Phase 1L.3k\n"
        "- Status: noncanonical graphic-language owner review only\n"
        "- Builder: build_first_wager_graphic_language.py\n"
        "- Output: five deterministic stdlib-authored SVG documents\n"
        f"- Palette source: {PALETTE_SOURCE} at SHA-256 {PALETTE_SOURCE_SHA256}\n"
        "- Palette: exactly five current production linear RGBA anchors converted to sRGB hex\n"
        "- Copy: full current Harbor City Waves / Mesa Vista Sol labels and existing first-wager values only\n"
        "- External libraries, images, fonts, textures, brands, URLs, scripts, and paid inputs: none\n"
        "- Production UI, code, runtime, interaction, wagering, settlement, ledger, history, and gameplay changes: none\n\n"
        "INTERACT, ACTIVE, LOCKED, SELECTED, CONFIRM, and SETTLED are review-state labels paired with exact distinct shapes. They do not add runtime states or behavior. DISPLAY_TITLE, STATE_LABEL, PRIMARY_VALUE, and INSTRUCTION are review typography roles, not a production component system. Promotion and placement remain owner-gated.\n",
        encoding="utf-8",
        newline="\n",
    )


def artifact_record(path):
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_manifest():
    validation = validate_svgs(check_manifest=False)
    artifacts = [ROOT / name for name in OUTPUTS] + [Path(__file__).resolve(), PROVENANCE_PATH]
    manifest = {
        "phase": "Phase 1L.3k",
        "status": "noncanonical_owner_review_board",
        "manual_input": False,
        "format": "SVG_1_1",
        "renderer": "stdlib_deterministic_svg",
        "palette": PALETTE,
        "palette_conversion": {
            "method": "IEC_61966_2_1_linear_to_sRGB_then_nearest_8_bit",
            "source_path": PALETTE_SOURCE,
            "source_sha256": PALETTE_SOURCE_SHA256,
            "anchors": PALETTE_CONVERSIONS,
        },
        "current_copy": CURRENT_COPY,
        "state_contract": {
            "state_count": len(STATE_SHAPES),
            "states": STATE_SHAPES,
            "expected_counts_by_output": {name: dict(counts) for name, counts in EXPECTED_STATE_COUNTS.items()},
            "shape_distinct": True,
            "color_only": False,
        },
        "typography_contract": {
            "role_count": len(TYPE_ROLES),
            "roles": list(TYPE_ROLES),
            "expected_counts_by_output": {name: dict(counts) for name, counts in EXPECTED_TYPE_COUNTS.items()},
        },
        "contrast_contract": {
            "text_minimum": 4.5,
            "marker_minimum": 3.0,
            "measured_text_minimum": validation["text_minimum"],
            "measured_marker_minimum": validation["marker_minimum"],
        },
        "boundaries": {
            "external_references": 0,
            "images": 0,
            "fonts": 0,
            "textures": 0,
            "scripts": 0,
            "brands": 0,
            "new_states": 0,
            "gameplay_changes": 0,
            "wagering_changes": 0,
            "settlement_changes": 0,
            "production_ui_changes": 0,
            "phase_1l3j_symbols_reused": 0,
            "phase_1l3j_wave_symbol_occurrences": 0,
            "phase_1l3j_sun_symbol_occurrences": 0,
        },
        "outputs": [
            {
                "file": name,
                "width": width,
                "height": height,
                "context": context,
                "sha256": sha256(ROOT / name),
            }
            for name, (width, height, context) in OUTPUTS.items()
        ],
        "artifacts": [artifact_record(path) for path in artifacts],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def linear_to_srgb_hex(linear_rgba):
    channels = []
    for value in linear_rgba[:3]:
        srgb = 12.92 * value if value <= 0.0031308 else 1.055 * (value ** (1.0 / 2.4)) - 0.055
        channels.append(round(srgb * 255))
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def validate_svgs(check_manifest=True):
    errors = []
    source_path = ROOT.parents[3] / PALETTE_SOURCE
    if not source_path.exists() or sha256(source_path) != PALETTE_SOURCE_SHA256:
        errors.append("production palette source identity differs")
    source_lines = source_path.read_text(encoding="utf-8").splitlines() if source_path.exists() else []
    if set(PALETTE) != set(PALETTE_CONVERSIONS) or len(PALETTE) != 5:
        errors.append("exact five palette anchors differ")
    for name, record in PALETTE_CONVERSIONS.items():
        if PALETTE.get(name) != record["srgb_hex"] or linear_to_srgb_hex(record["linear_rgba"]) != record["srgb_hex"]:
            errors.append(f"palette conversion differs: {name}")
        line_number = record["source_line"]
        if line_number > len(source_lines) or record["source_expression"] not in source_lines[line_number - 1]:
            errors.append(f"palette source line differs: {name}")
    actual = {path.name for path in ROOT.glob("*.svg")}
    if actual != set(OUTPUTS):
        errors.append(f"exactly five SVG outputs are required: {sorted(actual)}")
    all_ids = {}
    text_ratios = []
    marker_ratios = []
    for name, (width, height, context) in OUTPUTS.items():
        path = ROOT / name
        if not path.exists():
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{name} XML parse failed: {exc}")
            continue
        if local_name(root.tag) != "svg":
            errors.append(f"{name} root must be svg")
        if root.get("width") != str(width) or root.get("height") != str(height):
            errors.append(f"{name} dimensions differ")
        if root.get("viewBox") != f"0 0 {width} {height}" or root.get("data-context") != context:
            errors.append(f"{name} viewBox/context differs")
        if root.get("data-canonical") != "false":
            errors.append(f"{name} must remain noncanonical")

        ids = [element.get("id") for element in root.iter() if element.get("id")]
        if len(ids) != len(set(ids)):
            errors.append(f"{name} contains duplicate XML IDs")
        all_ids[name] = ids
        state_counts = Counter(element.get("data-state-id") for element in root.iter() if element.get("data-state-id"))
        if state_counts != EXPECTED_STATE_COUNTS[name]:
            errors.append(f"{name} state counts differ: {state_counts}")
        for element in root.iter():
            state = element.get("data-state-id")
            if state and element.get("data-shape-id") != STATE_SHAPES.get(state):
                errors.append(f"{name} state/shape mapping differs for {state}")
            if state:
                marker_ratios.append(contrast(element.get("data-marker-color"), element.get("data-marker-background")))
        type_counts = Counter(element.get("data-type-role") for element in root.iter() if element.get("data-type-role"))
        if type_counts != EXPECTED_TYPE_COUNTS[name]:
            errors.append(f"{name} typography counts differ: {type_counts}")
        for element in root.iter():
            if element.get("data-type-role"):
                text_ratios.append(contrast(element.get("fill"), PALETTE["white"]))
            tag = local_name(element.tag)
            if tag in {"image", "script", "foreignObject", "style"}:
                errors.append(f"{name} contains forbidden {tag}")
            for key, value in element.attrib.items():
                lowered = str(value).lower()
                if key.endswith("href") or "url(" in lowered or "data:" in lowered:
                    errors.append(f"{name} contains an external/resource reference")
                if str(value).startswith("#") and value not in PALETTE.values():
                    errors.append(f"{name} contains a noncontract palette value: {value}")
            if element.get("data-symbol-id"):
                errors.append(f"{name} reuses a Phase 1L.3j symbol")
        lowered_text = " ".join("".join(root.itertext()).lower().split())
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in lowered_text:
                errors.append(f"{name} contains forbidden text: {forbidden}")

    text_minimum = min(text_ratios) if text_ratios else 0.0
    marker_minimum = min(marker_ratios) if marker_ratios else 0.0
    if text_minimum < 4.5:
        errors.append(f"text contrast below 4.5: {text_minimum:.4f}")
    if marker_minimum < 3.0:
        errors.append(f"marker contrast below 3.0: {marker_minimum:.4f}")
    if set(STATE_SHAPES.values()) != {
        "OPEN_CIRCLE_DOT",
        "TRIANGLE",
        "BARRED_SQUARE",
        "DIAMOND",
        "DOUBLE_CHEVRON",
        "RING_CHECK",
    }:
        errors.append("the exact six state shapes differ")

    if check_manifest:
        if not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists():
            errors.append("manifest and provenance are required")
        else:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            if manifest.get("state_contract", {}).get("states") != STATE_SHAPES:
                errors.append("manifest state contract differs")
            if manifest.get("typography_contract", {}).get("roles") != list(TYPE_ROLES):
                errors.append("manifest typography roles differ")
            if manifest.get("boundaries", {}).get("phase_1l3j_symbols_reused") != 0:
                errors.append("Phase 1L.3j symbols must not be reused")
            if manifest.get("palette_conversion", {}).get("anchors") != PALETTE_CONVERSIONS:
                errors.append("manifest palette conversion differs")
            for artifact in manifest.get("artifacts", []):
                path = ROOT / artifact["file"]
                if not path.exists() or path.stat().st_size != artifact["bytes"] or sha256(path) != artifact["sha256"]:
                    errors.append(f"artifact identity differs: {artifact['file']}")
            for output in manifest.get("outputs", []):
                path = ROOT / output["file"]
                if not path.exists() or sha256(path) != output["sha256"]:
                    errors.append(f"output identity differs: {output['file']}")
    if errors:
        raise RuntimeError("\n".join(errors))
    return {
        "text_minimum": round(text_minimum, 4),
        "marker_minimum": round(marker_minimum, 4),
        "xml_ids": all_ids,
    }


def clean_generated():
    for path in [*ROOT.glob("*.svg"), MANIFEST_PATH, PROVENANCE_PATH]:
        if path.exists():
            path.unlink()


def output_hashes():
    return {
        path.name: sha256(path)
        for path in sorted([*ROOT.glob("*.svg"), MANIFEST_PATH, PROVENANCE_PATH])
        if path.exists()
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="build", choices=("build", "validate", "focused", "clean-build"))
    args = parser.parse_args()
    if args.mode in {"build", "clean-build"}:
        if args.mode == "clean-build":
            clean_generated()
        write_outputs()
        result = validate_svgs()
        print(
            "ODDSWELL_FIRST_WAGER_GRAPHIC_LANGUAGE_BUILD|result=PASS|outputs=5|states=6|"
            f"type_roles=4|text_contrast_min={result['text_minimum']:.4f}|"
            f"marker_contrast_min={result['marker_minimum']:.4f}|external_refs=0|forbidden=0"
        )
        print(json.dumps(output_hashes(), sort_keys=True))
    else:
        result = validate_svgs()
        label = "FOCUSED" if args.mode == "focused" else "XML"
        print(
            f"ODDSWELL_FIRST_WAGER_GRAPHIC_LANGUAGE_{label}|result=PASS|outputs=5|states=6|"
            f"type_roles=4|text_contrast_min={result['text_minimum']:.4f}|"
            f"marker_contrast_min={result['marker_minimum']:.4f}|external_refs=0|forbidden=0"
        )


if __name__ == "__main__":
    main()
