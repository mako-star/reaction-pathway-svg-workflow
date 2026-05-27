"""Custom enlarged convergent SVG for HMF -> hydroxyacetone-like pathway."""

from __future__ import annotations

import argparse
import base64
import json
from io import BytesIO
from pathlib import Path

from PIL import Image


W = 2400
H = 1600
LEFT_X = 170
CARD_W = 700
CARD_H = 170
RIGHT_X = 1660

PALETTE = [
    ("#087b78", "#93c7c4", "#e9f2f1"),
    ("#6652a1", "#beb2dd", "#f2effa"),
    ("#9b6616", "#f1c66e", "#fff5df"),
    ("#c4554a", "#efaaa2", "#fff0ed"),
    ("#4d8f8a", "#9bc7c0", "#edf8f5"),
    ("#6f7f89", "#cad3d8", "#f3f6f7"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate custom convergent hydroxyacetone pathway SVG.")
    parser.add_argument("--path-dir", default=r"examples\openclaw_reacnet\HMF_Hydroxyacetone_like_Path")
    parser.add_argument("--output-dir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path_dir = Path(args.path_dir)
    output_dir = Path(args.output_dir) if args.output_dir else path_dir / "unified_svg"
    output_dir.mkdir(parents=True, exist_ok=True)

    spec = build_spec(path_dir)
    spec_path = output_dir / "generated_spec.json"
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")

    svg_path = output_dir / "pathway_unified.svg"
    svg_path.write_text(render_svg(spec), encoding="utf-8")
    print(f"Generated SVG: {svg_path.resolve()}")
    print(f"Generated spec: {spec_path.resolve()}")
    return 0


def build_spec(path_dir: Path) -> dict:
    def asset(name: str) -> str:
        path = path_dir / name
        if not path.exists():
            raise FileNotFoundError(path)
        return str(path)

    return {
        "title": "HMF → 羟基丙酮 (Hydroxyacetone-like) 反应路径",
        "equation": (
            "C₆H₆O₃ → C₃H₅O₂ + C₃HO; "
            "C₃H₅O₂ → CH₂O + C₂H₃O; "
            "CH₂O + H· → CH₃O; "
            "C₂H₃O + CH₃O → C₃H₆O₂"
        ),
        "topology": "convergent",
        "molecules": [
            {"id": "HMF", "label": "HMF", "formula": "C₆H₆O₃", "asset_path": asset("HMF_S1350_bond1.2.png")},
            {"id": "C3H5O2", "label": "C₃H₅O₂", "formula": "C₃H₅O₂", "asset_path": asset("C3H5O2_S3400_bond1.2.png")},
            {"id": "C3HO", "label": "C₃HO", "formula": "C₃HO", "asset_path": asset("C3HO_S3573_bond1.2.png")},
            {"id": "CH2O", "label": "CH₂O", "formula": "CH₂O", "asset_path": asset("CH2O_S596_bond1.2.png")},
            {"id": "C2H3O", "label": "C₂H₃O", "formula": "C₂H₃O", "asset_path": asset("C2H3O_S2044_bond1.2.png")},
            {"id": "H", "label": "H·", "formula": "H·", "asset_path": asset("H_S3830_bond1.2.png")},
            {"id": "CH3O", "label": "CH₃O", "formula": "CH₃O", "asset_path": asset("CH3O_S3359_bond1.2.png")},
            {"id": "C3H6O2", "label": "C₃H₆O₂", "formula": "C₃H₆O₂", "asset_path": asset("C3H6O2_S2140_bond1.2.png")},
        ],
        "main_chain": ["HMF", "C3H5O2", "CH2O", "CH3O", "C3H6O2"],
        "reactions": [
            {"from": ["HMF"], "to": ["C3H5O2"], "side_products": ["C3HO"], "label": "+ C₃HO"},
            {"from": ["C3H5O2"], "to": ["CH2O"], "side_products": ["C2H3O"], "label": "+ C₂H₃O"},
            {"from": ["CH2O", "H"], "to": ["CH3O"], "side_products": [], "label": "+ H·"},
            {"from": ["C2H3O", "CH3O"], "to": ["C3H6O2"], "side_products": [], "label": "convergent recombination"},
        ],
    }


def render_svg(spec: dict) -> str:
    molecules = {m["id"]: m for m in spec["molecules"]}
    chain = spec["main_chain"]
    y_positions = [60, 335, 610, 885, 1160]
    colors = {mol_id: PALETTE[i % len(PALETTE)] for i, mol_id in enumerate(chain)}
    colors.update({"C3HO": PALETTE[0], "C2H3O": PALETTE[1], "H": PALETTE[5]})

    parts = [svg_header(spec["title"])]

    descriptions = ["starting species", "intermediate", "formaldehyde branch", "methoxy radical", "final product"]
    for i, mol_id in enumerate(chain):
        mol = molecules[mol_id]
        color, pale, fill = colors[mol_id]
        parts.append(
            molecule_card(
                f"card-{safe_id(mol_id)}",
                LEFT_X,
                y_positions[i],
                CARD_W,
                CARD_H,
                color,
                pale,
                fill,
                Path(mol["asset_path"]),
                mol["label"],
                mol["formula"],
                descriptions[i],
            )
        )

    for i in range(len(chain) - 1):
        color = colors[chain[i]][0]
        y_start = y_positions[i] + CARD_H + 10
        y_end = y_positions[i + 1] - 26
        parts.append(
            f'<path id="main-arrow-{i + 1}" d="M430 {y_start:.1f} V{y_end:.1f}" '
            f'stroke="{color}" stroke-width="7" stroke-linecap="round" fill="none" '
            f'marker-end="url(#arrow-{i})"/>'
        )

    parts.append(side_arrow("C3HO", 452, 285, 1260, "#087b78", 0))
    parts.append(side_arrow("C2H3O", 452, 560, 1260, "#6652a1", 1))
    parts.append(
        '<path id="convergent-arrow-C2H3O-to-final" '
        'd="M1528 562 C1640 720 1570 1190 880 1245" '
        'stroke="#7860ad" stroke-width="3.2" stroke-linecap="round" '
        'stroke-dasharray="10 8" fill="none" marker-end="url(#side-arrow-1)"/>'
    )

    steps = [
        (1, 285, "#087b78", "C₆H₆O₃ → C₃H₅O₂ + C₃HO"),
        (2, 560, "#6652a1", "C₃H₅O₂ → CH₂O + C₂H₃O"),
        (3, 835, "#9b6616", "CH₂O + H· → CH₃O"),
        (4, 1110, "#c4554a", "C₂H₃O + CH₃O → C₃H₆O₂"),
    ]
    for num, y, color, eq in steps:
        parts.append(step_label(90, y - 60, color, str(num), f"Step {num}"))
        parts.append(equation_box(f"eq-step-{num}", 560, y - 42, 660, 62, color, eq))

    parts.append(side_arrow("H", 1270, 835, 1220, "#6f7f89", 5))
    parts.append(side_card("side-C3HO", 1270, 244, "#087b78", "#93c7c4", "#e9f2f1", Path(molecules["C3HO"]["asset_path"]), "C₃HO", "by-product"))
    parts.append(side_card("side-C2H3O", 1270, 519, "#6652a1", "#beb2dd", "#f2effa", Path(molecules["C2H3O"]["asset_path"]), "C₂H₃O", "parallel branch"))
    parts.append(side_card("input-H", 1270, 794, "#6f7f89", "#cad3d8", "#f3f6f7", Path(molecules["H"]["asset_path"]), "H·", "parallel input"))

    parts.append(right_title(spec["title"]))
    parts.append(legend_panel(molecules, colors))
    parts.append("</svg>")
    return "\n".join(parts)


def svg_header(title: str) -> str:
    markers = []
    for idx, (color, _, _) in enumerate(PALETTE):
        markers.append(
            f'<marker id="arrow-{idx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
        )
        markers.append(
            f'<marker id="side-arrow-{idx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
  <title>{xml_escape(title)}</title>
  <defs>
    <style>
      text {{ font-family: "Times New Roman", Times, serif; letter-spacing: 0; }}
      .title {{ font-size: 54px; font-weight: 700; fill: #102536; }}
      .subtitle {{ font-size: 30px; font-style: italic; fill: #087b78; }}
      .card-name {{ font-size: 46px; font-weight: 700; }}
      .pill {{ font-size: 23px; font-weight: 700; }}
      .desc {{ font-size: 22px; fill: #283546; }}
      .eq {{ font-size: 25px; font-weight: 700; font-style: italic; }}
      .side-label {{ font-size: 31px; font-weight: 700; font-style: italic; }}
      .step {{ font-size: 25px; font-weight: 700; }}
      .step-desc {{ font-size: 21px; font-style: italic; fill: #283546; }}
      .legend-head {{ font-size: 28px; font-weight: 700; fill: #087b78; }}
      .legend-text {{ font-size: 24px; fill: #283546; }}
      .legend-formula {{ font-size: 24px; font-style: italic; fill: #283546; }}
    </style>
    {"".join(markers)}
  </defs>
  <rect width="100%" height="100%" fill="#fbfbf9"/>
  <rect x="{RIGHT_X - 45}" y="0" width="{W - RIGHT_X + 45}" height="{H}" fill="#f7faf9"/>
  <g id="background-chemistry" opacity="0.10" stroke="#9aa8b4" fill="none" stroke-width="5">
    <path d="M1720 320 V420 L1685 495 H1810 L1775 420 V320"/>
    <path d="M1850 375 V485 L1810 570 H1960 L1922 485 V375"/>
    <path d="M2050 350 L2130 396 L2130 490 L2050 536 L1970 490 L1970 396 Z"/>
    <path d="M1995 396 L2050 365 L2105 396 M1995 490 L2050 520 L2105 490"/>
  </g>"""


def molecule_card(group_id: str, x: float, y: float, w: float, h: float, color: str, pale: str, fill: str, image: Path, name: str, formula: str, desc: str) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="18" fill="#ffffff" stroke="{pale}" stroke-width="2.2"/>
    <circle cx="{x + 126:.1f}" cy="{y + h / 2:.1f}" r="78" fill="{fill}" stroke="{pale}" stroke-width="2"/>
    {image_element(image, x + 48, y + 30, 156, 116)}
    <text class="card-name" x="{x + 420:.1f}" y="{y + 62:.1f}" text-anchor="middle" fill="{color}">{xml_escape(name)}</text>
    <rect x="{x + 350:.1f}" y="{y + 82:.1f}" width="140" height="42" rx="15" fill="{fill}"/>
    <text class="pill" x="{x + 420:.1f}" y="{y + 110:.1f}" text-anchor="middle" fill="{color}">{xml_escape(formula)}</text>
    <text class="desc" x="{x + 420:.1f}" y="{y + 150:.1f}" text-anchor="middle">{xml_escape(desc)}</text>
  </g>"""


def step_label(x: float, y: float, color: str, num: str, title: str) -> str:
    return f"""
  <g id="step-{num}">
    <circle cx="{x + 17:.1f}" cy="{y + 17:.1f}" r="18" fill="{color}"/>
    <text x="{x + 17:.1f}" y="{y + 26:.1f}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff">{num}</text>
    <text class="step" x="{x + 50:.1f}" y="{y + 26:.1f}" fill="{color}">{xml_escape(title)}</text>
    <text class="step-desc" x="{x + 17:.1f}" y="{y + 62:.1f}">reaction step</text>
  </g>"""


def equation_box(group_id: str, x: float, y: float, w: float, h: float, color: str, text: str) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" fill="#ffffff" stroke="{color}" stroke-width="2.4"/>
    <text class="eq" x="{x + w / 2:.1f}" y="{y + h / 2 + 9:.1f}" text-anchor="middle" fill="{color}">{xml_escape(text)}</text>
  </g>"""


def side_arrow(name: str, x1: float, y: float, x2: float, color: str, marker_idx: int) -> str:
    return (
        f'<path id="side-arrow-{safe_id(name)}" d="M{x1:.1f} {y:.1f} H{x2:.1f}" '
        f'stroke="{color}" stroke-width="2.3" stroke-linecap="round" '
        f'stroke-dasharray="10 8" fill="none" marker-end="url(#side-arrow-{marker_idx})"/>'
    )


def side_card(group_id: str, x: float, y: float, color: str, pale: str, fill: str, image: Path, name: str, desc: str) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x:.1f}" y="{y:.1f}" width="250" height="86" rx="18" fill="{fill}" stroke="{pale}" stroke-width="2.2"/>
    <text class="side-label" x="{x + 84:.1f}" y="{y + 53:.1f}" text-anchor="middle" fill="{color}">{xml_escape(name)}</text>
    {image_element(image, x + 164, y + 18, 66, 52)}
    <text class="step-desc" x="{x + 42:.1f}" y="{y + 118:.1f}">{xml_escape(desc)}</text>
  </g>"""


def right_title(title: str) -> str:
    return f"""
  <g id="right-title">
    <text class="title" x="{RIGHT_X}" y="120">{xml_escape(title.split('(')[0].strip())}</text>
    <text class="subtitle" x="{RIGHT_X}" y="178">Convergent reaction pathway to C₃H₆O₂</text>
  </g>"""


def legend_panel(molecules: dict, colors: dict) -> str:
    order = ["HMF", "C3H5O2", "CH2O", "CH3O", "C2H3O", "H", "C3H6O2"]
    row_gap = 62
    y0 = 705
    parts = [
        '<g id="species-formulas">',
        f'<rect x="{RIGHT_X}" y="565" width="590" height="710" rx="18" fill="#ffffff" stroke="#e1e6ea" stroke-width="1"/>',
        f'<circle cx="{RIGHT_X + 70}" cy="632" r="38" fill="#087b78"/>',
        f'<path d="M{RIGHT_X + 56} 658 L{RIGHT_X + 68} 612 V600 H{RIGHT_X + 81} V612 L{RIGHT_X + 95} 658 Z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
        f'<circle cx="{RIGHT_X + 72}" cy="642" r="4" fill="#fff"/><circle cx="{RIGHT_X + 87}" cy="658" r="4" fill="#fff"/>',
        f'<text class="legend-head" x="{RIGHT_X + 130}" y="642">Species and formulas</text>',
        f'<path d="M{RIGHT_X + 40} 682 H{RIGHT_X + 550}" stroke="#087b78" stroke-width="2"/>',
    ]
    for idx, mol_id in enumerate(order):
        mol = molecules[mol_id]
        color = colors.get(mol_id, PALETTE[idx % len(PALETTE)])[0]
        y = y0 + idx * row_gap
        parts.append(f'<circle cx="{RIGHT_X + 55}" cy="{y - 4}" r="9" fill="{color}"/>')
        parts.append(f'<text class="legend-text" x="{RIGHT_X + 95}" y="{y + 5}" font-style="italic" fill="{color}">{xml_escape(mol["label"])}:</text>')
        parts.append(f'<text class="legend-formula" x="{RIGHT_X + 315}" y="{y + 5}">{xml_escape(mol["formula"])}</text>')
        if idx < len(order) - 1:
            parts.append(f'<path d="M{RIGHT_X + 40} {y + 32} H{RIGHT_X + 550}" stroke="#d6dde0" stroke-width="1.2" stroke-dasharray="5 4"/>')
    parts.append("</g>")
    return "\n    ".join(parts)


def image_element(path: Path, x: float, y: float, width: float, height: float) -> str:
    href = resized_png_data_uri(path, int(width), int(height), scale=3)
    return (
        f'<image x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'preserveAspectRatio="xMidYMid meet" xlink:href="{href}"/>'
    )


def resized_png_data_uri(path: Path, width: int, height: int, scale: int = 3) -> str:
    with Image.open(path) as img:
        img = img.convert("RGBA")
        img.thumbnail((width * scale, height * scale), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (width * scale, height * scale), (255, 255, 255, 0))
        canvas.alpha_composite(img, ((canvas.width - img.width) // 2, (canvas.height - img.height) // 2))
        buf = BytesIO()
        canvas.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def safe_id(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value).strip("-") or "species"


def xml_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


if __name__ == "__main__":
    raise SystemExit(main())
