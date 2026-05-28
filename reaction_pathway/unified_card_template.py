"""Generate standalone Inkscape-safe pathway SVGs from complete Path packages."""

from __future__ import annotations

import argparse
import base64
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from .from_assets import build_spec_data
from .from_readme import extract_equation, extract_title
from .schema import PathwaySpec


W = 1456
H = 1024
LEFT_X = 150
CARD_W = 610
RIGHT_X = 930

PALETTE = [
    ("#087b78", "#93c7c4", "#e9f2f1"),
    ("#6652a1", "#beb2dd", "#f2effa"),
    ("#9b6616", "#f1c66e", "#fff5df"),
    ("#c4554a", "#efaaa2", "#fff0ed"),
    ("#4d8f8a", "#9bc7c0", "#edf8f5"),
    ("#7a678f", "#c7bad7", "#f5f1fa"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate unified standalone pathway SVGs.")
    parser.add_argument(
        "path_dir",
        help=(
            "One Path folder containing the complete input package: reaction "
            "equation, molecule images, and a template/template implementation."
        ),
    )
    parser.add_argument("--output-dir", help="Output directory. Defaults to <path_dir>/unified_svg.")
    parser.add_argument("--svg-name", default="pathway_unified.svg")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path_dir = Path(args.path_dir)
    readme = path_dir / "README.md"
    if not readme.exists():
        raise FileNotFoundError(f"README.md not found: {readme}")

    text = readme.read_text(encoding="utf-8")
    equation = extract_equation(text)
    title = extract_title(text) or path_dir.name
    output_dir = Path(args.output_dir) if args.output_dir else path_dir / "unified_svg"
    output_dir.mkdir(parents=True, exist_ok=True)

    spec_data = build_spec_data(
        equation=equation,
        asset_dir=path_dir,
        asset_map={},
        title=title,
        width=W,
        height=H,
    )
    spec = PathwaySpec.from_dict(spec_data)

    svg_path = output_dir / args.svg_name
    svg_path.write_text(render_svg(spec), encoding="utf-8")
    spec_path = output_dir / "generated_spec.json"
    spec_path.write_text(json.dumps(spec_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Generated SVG: {svg_path.resolve()}")
    print(f"Generated spec: {spec_path.resolve()}")
    return 0


def render_svg(spec: PathwaySpec) -> str:
    chain = spec.main_chain or infer_chain_from_reactions(spec)
    if len(chain) < 2:
        raise ValueError(f"Need at least two main-chain molecules for {spec.title}")

    card_h = card_height(len(chain))
    y_positions = card_positions(len(chain), card_h)
    colors = {mol_id: PALETTE[i % len(PALETTE)] for i, mol_id in enumerate(chain)}
    for mol_id in spec.molecules:
        colors.setdefault(mol_id, PALETTE[len(colors) % len(PALETTE)])

    parts = [svg_header(spec)]
    for idx, mol_id in enumerate(chain):
        mol = spec.molecules[mol_id]
        color, pale, fill = colors[mol_id]
        desc = "starting species" if idx == 0 else ("final product" if idx == len(chain) - 1 else "intermediate")
        parts.append(
            molecule_card(
                group_id=f"card-{safe_id(mol_id)}",
                x=LEFT_X,
                y=y_positions[idx],
                w=CARD_W,
                h=card_h,
                color=color,
                pale=pale,
                fill=fill,
                image=Path(mol.asset_path or ""),
                name=mol.display_label,
                formula=compact_label(mol.display_label),
                desc=desc,
            )
        )

    for idx in range(len(chain) - 1):
        source = chain[idx]
        target = chain[idx + 1]
        color, _, _ = colors[source]
        y_start = y_positions[idx] + card_h + 8
        y_end = y_positions[idx + 1] - 22
        parts.append(
            f'<path id="main-arrow-{idx + 1}" d="M376 {y_start:.1f} V{y_end:.1f}" '
            f'stroke="{color}" stroke-width="5" stroke-linecap="round" fill="none" '
            f'marker-end="url(#arrow-{idx % len(PALETTE)})"/>'
        )

    for idx, reaction in enumerate(spec.reactions):
        if not reaction.sources or not reaction.targets:
            continue
        source = reaction.sources[0]
        if source not in chain:
            continue
        step_idx = min(chain.index(source), len(chain) - 2)
        color, pale, fill = colors.get(source, PALETTE[step_idx % len(PALETTE)])
        gap_y = (y_positions[step_idx] + card_h + y_positions[step_idx + 1]) / 2
        step_y = gap_y - 66
        parts.append(step_label(105, step_y, color, str(step_idx + 1), f"Step {step_idx + 1}"))
        eq = reaction_equation_text(spec, reaction)
        parts.append(equation_box(f"eq-step-{step_idx + 1}", 423, gap_y - 42, 372, 58, color, eq))

        side_ids = [sid for sid in reaction.side_products if sid in spec.molecules]
        for side_index, side_id in enumerate(side_ids[:2]):
            y = gap_y + 30 + side_index * 75
            if y + 86 > H:
                y = gap_y - 120 - side_index * 75
            side = spec.molecules[side_id]
            parts.append(
                f'<path id="side-arrow-{safe_id(side_id)}" d="M392 {y + 32:.1f} H685" '
                f'stroke="{color}" stroke-width="1.5" stroke-linecap="round" '
                f'stroke-dasharray="7 7" marker-end="url(#side-arrow-{step_idx % len(PALETTE)})"/>'
            )
            parts.append(
                side_card(
                    f"side-{safe_id(side_id)}",
                    690,
                    y,
                    color,
                    pale,
                    fill,
                    Path(side.asset_path or ""),
                    side.display_label,
                )
            )

    parts.append(right_title(spec.title, spec.equation or ""))
    parts.append(legend_panel(spec, colors))
    parts.append("</svg>")
    return "\n".join(parts)


def svg_header(spec: PathwaySpec) -> str:
    markers = []
    for idx, (color, _, _) in enumerate(PALETTE):
        markers.append(
            f'<marker id="arrow-{idx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
        )
        markers.append(
            f'<marker id="side-arrow-{idx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
  <title>{xml_escape(spec.title)}</title>
  <defs>
    <style>
      text {{ font-family: "Times New Roman", Times, serif; letter-spacing: 0; }}
      .title {{ font-size: 42px; font-weight: 700; fill: #102536; }}
      .subtitle {{ font-size: 24px; font-style: italic; fill: #087b78; }}
      .card-name {{ font-size: 42px; font-weight: 700; }}
      .pill {{ font-size: 21px; font-weight: 700; }}
      .desc {{ font-size: 20px; fill: #283546; }}
      .eq {{ font-size: 21px; font-weight: 700; font-style: italic; }}
      .side-label {{ font-size: 26px; font-weight: 700; font-style: italic; }}
      .step {{ font-size: 21px; font-weight: 700; }}
      .step-desc {{ font-size: 18px; font-style: italic; fill: #283546; }}
      .legend-head {{ font-size: 24px; font-weight: 700; fill: #087b78; }}
      .legend-text {{ font-size: 21px; fill: #283546; }}
      .legend-formula {{ font-size: 21px; font-style: italic; fill: #283546; }}
    </style>
    {"".join(markers)}
  </defs>
  <rect width="100%" height="100%" fill="#fbfbf9"/>
  <rect x="910" y="0" width="546" height="{H}" fill="#f7faf9"/>
  <g id="background-chemistry" opacity="0.10" stroke="#9aa8b4" fill="none" stroke-width="4">
    <path d="M976 277 V350 L950 405 H1038 L1012 350 V277"/>
    <path d="M1051 318 V404 L1024 457 H1132 L1105 404 V318"/>
    <path d="M1220 300 L1280 334 L1280 405 L1220 440 L1160 405 L1160 334 Z"/>
    <path d="M1180 333 L1220 310 L1260 333 M1180 405 L1220 428 L1260 405"/>
    <circle cx="1130" cy="360" r="10"/><circle cx="1165" cy="340" r="10"/><circle cx="1140" cy="315" r="9"/>
  </g>"""


def molecule_card(group_id: str, x: float, y: float, w: float, h: float, color: str, pale: str, fill: str, image: Path, name: str, formula: str, desc: str) -> str:
    image_h = min(120, h - 56)
    image_w = 160
    circle_r = min(86, h / 2 - 12)
    return f"""
  <g id="{group_id}">
    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="17" fill="#ffffff" stroke="{pale}" stroke-width="2"/>
    <circle cx="{x + 114:.1f}" cy="{y + h / 2:.1f}" r="{circle_r:.1f}" fill="{fill}" stroke="{pale}" stroke-width="2"/>
    {image_element(image, x + 34, y + (h - image_h) / 2, image_w, image_h)}
    <text class="card-name" x="{x + 360:.1f}" y="{y + h * 0.34:.1f}" text-anchor="middle" fill="{color}">{xml_escape(name)}</text>
    <rect x="{x + 290:.1f}" y="{y + h * 0.46:.1f}" width="140" height="40" rx="15" fill="{fill}"/>
    <text class="pill" x="{x + 360:.1f}" y="{y + h * 0.46 + 27:.1f}" text-anchor="middle" fill="{color}">{xml_escape(formula)}</text>
    <text class="desc" x="{x + 360:.1f}" y="{y + h - 22:.1f}" text-anchor="middle">{xml_escape(desc)}</text>
  </g>"""


def step_label(x: float, y: float, color: str, num: str, title: str) -> str:
    return f"""
  <g id="step-{num}">
    <circle cx="{x + 16:.1f}" cy="{y + 16:.1f}" r="16" fill="{color}"/>
    <text x="{x + 16:.1f}" y="{y + 24:.1f}" text-anchor="middle" font-size="22" font-weight="700" fill="#ffffff">{num}</text>
    <text class="step" x="{x + 46:.1f}" y="{y + 24:.1f}" fill="{color}">{xml_escape(title)}</text>
    <text class="step-desc" x="{x + 16:.1f}" y="{y + 58:.1f}">reaction step</text>
  </g>"""


def equation_box(group_id: str, x: float, y: float, w: float, h: float, color: str, text: str) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" fill="#ffffff" stroke="{color}" stroke-width="2.2"/>
    <text class="eq" x="{x + w / 2:.1f}" y="{y + h / 2 + 8:.1f}" text-anchor="middle" fill="{color}">{xml_escape(text)}</text>
  </g>"""


def side_card(group_id: str, x: float, y: float, color: str, pale: str, fill: str, image: Path, name: str) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x:.1f}" y="{y:.1f}" width="198" height="66" rx="16" fill="{fill}" stroke="{pale}" stroke-width="2"/>
    <text class="side-label" x="{x + 66:.1f}" y="{y + 42:.1f}" text-anchor="middle" fill="{color}">{xml_escape(compact_label(name))}</text>
    {image_element(image, x + 128, y + 14, 48, 38)}
    <text class="step-desc" x="{x + 42:.1f}" y="{y + 90:.1f}">by-product</text>
  </g>"""


def right_title(title: str, equation: str) -> str:
    title_text = title.split("(")[0].strip()
    return f"""
  <g id="right-title">
    <text class="title" x="{RIGHT_X + 30}" y="110">{xml_escape(title_text)}</text>
    <text class="subtitle" x="{RIGHT_X + 30}" y="170">{xml_escape(short_equation(equation))}</text>
  </g>"""


def legend_panel(spec: PathwaySpec, colors: dict[str, tuple[str, str, str]]) -> str:
    molecules = list(spec.molecules.values())
    row_gap = min(60, max(42, int(330 / max(1, len(molecules)))))
    y0 = 666
    parts = [
        '<g id="species-formulas">',
        '<rect x="965" y="520" width="420" height="470" rx="16" fill="#ffffff" stroke="#e1e6ea" stroke-width="1"/>',
        '<circle cx="1035" cy="582" r="32" fill="#087b78"/>',
        '<path d="M1024 604 L1034 566 V555 H1044 V566 L1055 604 Z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
        '<circle cx="1036" cy="590" r="4" fill="#fff"/><circle cx="1047" cy="604" r="4" fill="#fff"/>',
        '<text class="legend-head" x="1090" y="590">Species and formulas</text>',
        '<path d="M1004 630 H1358" stroke="#087b78" stroke-width="2"/>',
    ]
    for idx, mol in enumerate(molecules[:7]):
        color = colors.get(mol.id, PALETTE[idx % len(PALETTE)])[0]
        y = y0 + idx * row_gap
        name = compact_label(mol.display_label)
        parts.append(f'<circle cx="1017" cy="{y - 4}" r="8" fill="{color}"/>')
        parts.append(f'<text class="legend-text" x="1050" y="{y + 4}" font-style="italic" fill="{color}">{xml_escape(name)}:</text>')
        parts.append(f'<text class="legend-formula" x="1210" y="{y + 4}">{xml_escape(name)}</text>')
        if idx < min(len(molecules), 7) - 1:
            parts.append(f'<path d="M1005 {y + 26} H1352" stroke="#d6dde0" stroke-width="1.3" stroke-dasharray="5 4"/>')
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


def card_height(count: int) -> int:
    if count <= 3:
        return 185
    if count == 4:
        return 150
    return 124


def card_positions(count: int, card_h: int) -> list[float]:
    top = 38 if count > 3 else 44
    bottom = 28
    if count == 1:
        return [(H - card_h) / 2]
    gap = (H - top - bottom - count * card_h) / (count - 1)
    return [top + i * (card_h + gap) for i in range(count)]


def reaction_equation_text(spec: PathwaySpec, reaction) -> str:
    source = compact_label(spec.molecules[reaction.sources[0]].display_label)
    products = [compact_label(spec.molecules[item].display_label) for item in reaction.targets + reaction.side_products if item in spec.molecules]
    return f"{source}  →  {' + '.join(products)}"


def infer_chain_from_reactions(spec: PathwaySpec) -> list[str]:
    chain: list[str] = []
    for reaction in spec.reactions:
        if not reaction.sources or not reaction.targets:
            continue
        if not chain:
            chain.append(reaction.sources[0])
        chain.append(reaction.targets[0])
    return chain


def compact_label(label: str) -> str:
    if "(" in label and ")" in label:
        inside = label[label.find("(") + 1:label.find(")")].strip()
        if inside and all(ord(ch) < 128 for ch in inside):
            return inside
    return label.split("(")[0].strip()


def short_equation(equation: str) -> str:
    if not equation:
        return "Chemical reaction pathway"
    return "Chemical reaction pathway"


def safe_id(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value).strip("-") or "species"


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


if __name__ == "__main__":
    raise SystemExit(main())
