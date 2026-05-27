"""Vertical card-style pathway SVG template."""

from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image


W = 1456
H = 1024
CARD_W = 600
CARD_H = 185
CARD_X = 160
CARD_Y = [44, 430, 816]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate vertical card-style HMF pathway SVG.")
    parser.add_argument("--path-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--molecule-svg-dir",
        help="Optional directory containing molecule SVG wrappers. If provided, SVG assets are preferred over PNG.",
    )
    parser.add_argument(
        "--asset-mode",
        choices=["embed", "link"],
        default="embed",
        help="Embed assets as data URIs, or link files for Inkscape-friendly editing.",
    )
    parser.add_argument(
        "--inkscape-safe",
        action="store_true",
        help="Disable card filters and prefer lightweight linked assets.",
    )
    parser.add_argument(
        "--standalone-inkscape",
        action="store_true",
        help="Create one complete SVG file with embedded PNG assets in an Inkscape-friendly form.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path_dir = Path(args.path_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_dir = Path(args.molecule_svg_dir) if args.molecule_svg_dir else None

    asset_names = {
        "hmf": "HMF_S1350_bond1.2",
        "c3h5o2": "C3H5O2_S3400_bond1.2",
        "ch2o": "CH2O_S596_bond1.2",
        "c3ho": "C3HO_S3573_bond1.2",
        "c2h3o": "C2H3O_S2044_bond1.2",
    }
    assets = {
        key: choose_asset(path_dir, svg_dir, stem)
        for key, stem in asset_names.items()
    }
    missing = [str(path) for path in assets.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing molecule images: " + ", ".join(missing))
    if args.standalone_inkscape:
        args.asset_mode = "embed"
        args.inkscape_safe = True
    if args.asset_mode == "link":
        assets = prepare_linked_assets(assets, out_dir)

    svg = render_svg(
        assets,
        asset_mode=args.asset_mode,
        card_filter=not args.inkscape_safe,
        standalone_inkscape=args.standalone_inkscape,
    )
    if args.inkscape_safe:
        svg = svg.replace(' filter="url(#card-shadow)"', "")
        svg = svg.replace(' filter="url(#soft-shadow)"', "")
    check_bounds(svg)
    svg_path = out_dir / "vertical_card_pathway.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"Generated SVG: {svg_path.resolve()}")
    return 0


def render_svg(
    assets: dict[str, Path],
    asset_mode: str = "embed",
    card_filter: bool = True,
    standalone_inkscape: bool = False,
) -> str:
    card_w = CARD_W
    card_h = CARD_H
    card_x = CARD_X
    y1, y2, y3 = CARD_Y
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
  <title>Formaldehyde Path</title>
  <defs>
    <style>
      text {{ font-family: "Times New Roman", Times, serif; letter-spacing: 0; }}
      .title {{ font-size: 46px; font-weight: 700; fill: #102536; }}
      .subtitle {{ font-size: 27px; font-style: italic; fill: #087b78; }}
      .card-name {{ font-size: 48px; font-weight: 700; }}
      .pill {{ font-size: 24px; font-weight: 700; }}
      .desc {{ font-size: 22px; fill: #283546; }}
      .eq {{ font-size: 23px; font-weight: 700; font-style: italic; }}
      .side-label {{ font-size: 28px; font-weight: 700; font-style: italic; }}
      .step {{ font-size: 22px; font-weight: 700; }}
      .step-desc {{ font-size: 20px; font-style: italic; fill: #283546; }}
      .legend-head {{ font-size: 25px; font-weight: 700; fill: #087b78; }}
      .legend-text {{ font-size: 23px; fill: #283546; }}
      .legend-formula {{ font-size: 23px; font-style: italic; fill: #283546; }}
    </style>
    <filter id="card-shadow" x="-15%" y="-15%" width="130%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#102536" flood-opacity="0.14"/>
    </filter>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#102536" flood-opacity="0.10"/>
    </filter>
    <marker id="arrow-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#087b78"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#6652a1"/>
    </marker>
    <marker id="arrow-side-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#0b8b88"/>
    </marker>
    <marker id="arrow-side-purple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#7860ad"/>
    </marker>
  </defs>

  <rect width="100%" height="100%" fill="#fbfbf9"/>
  <rect x="920" y="0" width="536" height="{H}" fill="#f7faf9"/>

  <g id="background-chemistry" opacity="0.12" stroke="#9aa8b4" fill="none" stroke-width="4">
    <path d="M976 277 V350 L950 405 H1038 L1012 350 V277"/>
    <path d="M1051 318 V404 L1024 457 H1132 L1105 404 V318"/>
    <path d="M1220 300 L1280 334 L1280 405 L1220 440 L1160 405 L1160 334 Z"/>
    <path d="M1180 333 L1220 310 L1260 333 M1180 405 L1220 428 L1260 405"/>
    <circle cx="1130" cy="360" r="10"/><circle cx="1165" cy="340" r="10"/><circle cx="1140" cy="315" r="9"/>
    <circle cx="1295" cy="440" r="10"/><circle cx="1395" cy="315" r="10"/><circle cx="1290" cy="235" r="10"/>
  </g>

  {molecule_card("card-hmf", card_x, y1, card_w, card_h, "#087b78", "#93c7c4", "#e9f2f1", assets["hmf"], "HMF", "C₆H₆O₃", "5-hydroxymethylfurfural", asset_mode, card_filter, standalone_inkscape)}
  {molecule_card("card-c3h5o2", card_x, y2, card_w, card_h, "#6652a1", "#beb2dd", "#f2effa", assets["c3h5o2"], "C₃H₅O₂", "C₃H₅O₂", "intermediate", asset_mode, card_filter, standalone_inkscape)}
  {molecule_card("card-ch2o", card_x, y3, card_w, card_h, "#9b6616", "#f1c66e", "#fff5df", assets["ch2o"], "CH₂O", "CH₂O", "formaldehyde, final product", asset_mode, card_filter, standalone_inkscape)}

  <path id="main-arrow-1" d="M376 {y1 + card_h + 8} V{y2 - 24}" stroke="#087b78" stroke-width="5" stroke-linecap="round" fill="none" marker-end="url(#arrow-teal)"/>
  <path id="main-arrow-2" d="M376 {y2 + card_h + 8} V{y3 - 24}" stroke="#6652a1" stroke-width="5" stroke-linecap="round" fill="none" marker-end="url(#arrow-purple)"/>

  {step_label(110, 305, "#087b78", "1", "Step ①", "HMF ring-opening", "decomposition")}
  {step_label(110, 690, "#6652a1", "2", "Step ②", "Further", "fragmentation")}

  {equation_box("eq-step-1", 423, 292, 360, 58, "#087b78", "HMF  →  C₃H₅O₂ + C₃HO")}
  <path id="side-arrow-c3ho" d="M392 390 H685" stroke="#087b78" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="7 7" marker-end="url(#arrow-side-teal)"/>
  {side_card("side-c3ho", 690, 358, "#087b78", "#93c7c4", "#e9f2f1", assets["c3ho"], "C₃HO", "by-product", asset_mode, standalone_inkscape)}

  {equation_box("eq-step-2", 423, 675, 360, 58, "#6652a1", "C₃H₅O₂  →  CH₂O + C₂H₃O")}
  <path id="side-arrow-c2h3o" d="M392 770 H685" stroke="#6652a1" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="7 7" marker-end="url(#arrow-side-purple)"/>
  {side_card("side-c2h3o", 690, 736, "#6652a1", "#beb2dd", "#f2effa", assets["c2h3o"], "C₂H₃O", "by-product", asset_mode, standalone_inkscape)}

  <g id="right-title">
    <text class="title" x="960" y="110">Formaldehyde Path</text>
    <text class="subtitle" x="960" y="170">Chemical reaction pathway to CH₂O</text>
  </g>

  {legend_panel()}
</svg>
"""


def molecule_card(
    group_id: str,
    x: int,
    y: int,
    w: int,
    h: int,
    color: str,
    pale: str,
    fill: str,
    image: Path,
    name: str,
    formula: str,
    desc: str,
    asset_mode: str,
    card_filter: bool,
    standalone_inkscape: bool,
) -> str:
    filter_attr = ' filter="url(#card-shadow)"' if card_filter else ""
    return f"""
  <g id="{group_id}"{filter_attr}>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="17" fill="#ffffff" stroke="{pale}" stroke-width="2"/>
    <circle cx="{x + 114}" cy="{y + 92}" r="86" fill="{fill}" stroke="{pale}" stroke-width="2"/>
    {asset_image(image, x + 34, y + 31, 160, 120, asset_mode, standalone_inkscape)}
    <text class="card-name" x="{x + 355}" y="{y + 70}" text-anchor="middle" fill="{color}">{name}</text>
    <rect x="{x + 286}" y="{y + 86}" width="140" height="44" rx="15" fill="{fill}"/>
    <text class="pill" x="{x + 356}" y="{y + 116}" text-anchor="middle" fill="{color}">{formula}</text>
    <text class="desc" x="{x + 356}" y="{y + 163}" text-anchor="middle">{desc}</text>
  </g>"""


def step_label(x: int, y: int, color: str, num: str, title: str, line1: str, line2: str) -> str:
    return f"""
  <g id="step-{num}">
    <circle cx="{x + 16}" cy="{y + 16}" r="17" fill="{color}" filter="url(#soft-shadow)"/>
    <text x="{x + 16}" y="{y + 25}" text-anchor="middle" font-size="24" font-weight="700" fill="#ffffff">{num}</text>
    <text class="step" x="{x + 46}" y="{y + 24}" fill="{color}">{title}</text>
    <text class="step-desc" x="{x + 16}" y="{y + 61}">{line1}</text>
    <text class="step-desc" x="{x + 16}" y="{y + 91}">{line2}</text>
  </g>"""


def equation_box(group_id: str, x: int, y: int, w: int, h: int, color: str, text: str) -> str:
    return f"""
  <g id="{group_id}" filter="url(#soft-shadow)">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="17" fill="#ffffff" stroke="{color}" stroke-width="2.5"/>
    <text class="eq" x="{x + w / 2}" y="{y + h / 2 + 9}" text-anchor="middle" fill="{color}">{text}</text>
  </g>"""


def side_card(
    group_id: str,
    x: int,
    y: int,
    color: str,
    pale: str,
    fill: str,
    image: Path,
    name: str,
    desc: str,
    asset_mode: str,
    standalone_inkscape: bool,
) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x}" y="{y}" width="198" height="66" rx="16" fill="{fill}" stroke="{pale}" stroke-width="2"/>
    <text class="side-label" x="{x + 66}" y="{y + 42}" text-anchor="middle" fill="{color}">{name}</text>
    {asset_image(image, x + 128, y + 14, 48, 38, asset_mode, standalone_inkscape)}
    <text class="step-desc" x="{x + 42}" y="{y + 90}">{desc}</text>
  </g>"""


def legend_panel() -> str:
    rows = [
        ("#087b78", "HMF:", "C₆H₆O₃"),
        ("#6652a1", "C₃H₅O₂:", "C₃H₅O₂"),
        ("#57aaa4", "C₃HO:", "C₃HO"),
        ("#7860ad", "C₂H₃O:", "C₂H₃O"),
        ("#e4ad3f", "CH₂O:", "CH₂O"),
    ]
    y0 = 668
    parts = [
        '<g id="species-formulas" filter="url(#card-shadow)">',
        '<rect x="965" y="520" width="420" height="470" rx="16" fill="#ffffff" stroke="#e1e6ea" stroke-width="1"/>',
        '<circle cx="1035" cy="582" r="32" fill="#087b78"/>',
        '<path d="M1024 604 L1034 566 V555 H1044 V566 L1055 604 Z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
        '<circle cx="1036" cy="590" r="4" fill="#fff"/><circle cx="1047" cy="604" r="4" fill="#fff"/>',
        '<text class="legend-head" x="1090" y="590">Species and formulas</text>',
        '<path d="M1004 630 H1358" stroke="#087b78" stroke-width="2"/>',
    ]
    for idx, (color, name, formula) in enumerate(rows):
        y = y0 + idx * 68
        parts.append(f'<circle cx="1017" cy="{y - 4}" r="9" fill="{color}"/>')
        parts.append(f'<text class="legend-text" x="1050" y="{y + 4}" font-style="italic" fill="{color}">{name}</text>')
        parts.append(f'<text class="legend-formula" x="1208" y="{y + 4}">{formula}</text>')
        if idx < len(rows) - 1:
            parts.append(f'<path d="M1005 {y + 30} H1352" stroke="#d6dde0" stroke-width="1.5" stroke-dasharray="5 4"/>')
    parts.append("</g>")
    return "\n    ".join(parts)


def data_uri(path: Path, wrap: bool = False) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    if wrap:
        encoded = "\n".join(encoded[i:i + 76] for i in range(0, len(encoded), 76))
    return f"data:{mime};base64,{encoded}"


def asset_image(
    path: Path,
    x: int,
    y: int,
    width: int,
    height: int,
    asset_mode: str,
    standalone_inkscape: bool,
) -> str:
    if asset_mode == "link":
        href = path.as_posix()
        return (
            f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'preserveAspectRatio="xMidYMid meet" href="{href}"/>'
        )

    if path.suffix.lower() != ".svg":
        if standalone_inkscape:
            href = resized_png_data_uri(path, width, height, scale=3)
            return (
                f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
                f'preserveAspectRatio="xMidYMid meet" xlink:href="{href}"/>'
            )
        return (
            f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'preserveAspectRatio="xMidYMid meet" href="{data_uri(path)}"/>'
        )

    content = path.read_text(encoding="utf-8")
    href = extract_svg_image_href(content)
    if href:
        if standalone_inkscape:
            href = resized_data_uri_from_svg_wrapper(path, width, height, scale=3) or href
            return (
                f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
                f'preserveAspectRatio="xMidYMid meet" xlink:href="{href}"/>'
            )
        return (
            f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'preserveAspectRatio="xMidYMid meet" href="{href}"/>'
        )

    # Fallback for true vector SVGs: inline the SVG body.
    svg_width, svg_height = extract_svg_size(content)
    inner = extract_svg_inner(content)
    inner = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', "", inner)
    return (
        f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
        f'viewBox="0 0 {svg_width:g} {svg_height:g}" preserveAspectRatio="xMidYMid meet">'
        f'{inner}</svg>'
    )


def extract_svg_size(content: str) -> tuple[float, float]:
    viewbox = re.search(r'viewBox="([^"]+)"', content)
    if viewbox:
        parts = [float(item) for item in viewbox.group(1).replace(",", " ").split()]
        if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
            return parts[2], parts[3]
    width = re.search(r'\bwidth="([\d.]+)', content)
    height = re.search(r'\bheight="([\d.]+)', content)
    if width and height:
        return float(width.group(1)), float(height.group(1))
    return 800.0, 600.0


def extract_svg_inner(content: str) -> str:
    match = re.search(r"<svg\b[^>]*>(.*)</svg>", content, re.S)
    if not match:
        return f"<text>{html.escape('Invalid nested SVG')}</text>"
    inner = match.group(1)
    inner = re.sub(r"<\?xml[^>]*>\s*", "", inner)
    return inner.strip()


def extract_svg_image_href(content: str) -> str | None:
    match = re.search(r'\bhref="(data:image/[^"]+)"', content)
    if match:
        return match.group(1)
    match = re.search(r'\bxlink:href="(data:image/[^"]+)"', content)
    return match.group(1) if match else None


def resized_png_data_uri(path: Path, width: int, height: int, scale: int = 3) -> str:
    with Image.open(path) as img:
        img = img.convert("RGBA")
        img.thumbnail((width * scale, height * scale), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (width * scale, height * scale), (255, 255, 255, 0))
        x = (canvas.width - img.width) // 2
        y = (canvas.height - img.height) // 2
        canvas.alpha_composite(img, (x, y))
        buf = BytesIO()
        canvas.save(buf, format="PNG", optimize=True)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def resized_data_uri_from_svg_wrapper(path: Path, width: int, height: int, scale: int = 3) -> str | None:
    content = path.read_text(encoding="utf-8")
    href = extract_svg_image_href(content)
    if not href or not href.startswith("data:image/png;base64,"):
        return None
    raw = base64.b64decode(href.split(",", 1)[1])
    with Image.open(BytesIO(raw)) as img:
        img = img.convert("RGBA")
        img.thumbnail((width * scale, height * scale), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (width * scale, height * scale), (255, 255, 255, 0))
        x = (canvas.width - img.width) // 2
        y = (canvas.height - img.height) // 2
        canvas.alpha_composite(img, (x, y))
        buf = BytesIO()
        canvas.save(buf, format="PNG", optimize=True)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def choose_asset(path_dir: Path, svg_dir: Path | None, stem: str) -> Path:
    if svg_dir:
        svg_path = svg_dir / f"{stem}.svg"
        if svg_path.exists():
            return svg_path
    png_path = path_dir / f"{stem}.png"
    return png_path


def prepare_linked_assets(assets: dict[str, Path], output_dir: Path) -> dict[str, Path]:
    asset_dir = output_dir / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    linked: dict[str, Path] = {}
    for key, source in assets.items():
        target = asset_dir / source.name
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        linked[key] = Path("assets") / source.name
    return linked


def check_bounds(svg: str) -> None:
    import re

    attrs = re.findall(r'\b(?:x|y|cx|cy|x1|x2|y1|y2)="(-?\d+(?:\.\d+)?)"', svg)
    values = [float(v) for v in attrs]
    if not values:
        return
    # Coarse guard: explicit coordinates should not be outside the canvas.
    for attr, raw in re.findall(r'\b(x|cx|x1|x2)="(-?\d+(?:\.\d+)?)"', svg):
        value = float(raw)
        if value < 0 or value > W:
            raise ValueError(f"SVG x-coordinate out of bounds: {attr}={value}")
    for attr, raw in re.findall(r'\b(y|cy|y1|y2)="(-?\d+(?:\.\d+)?)"', svg):
        value = float(raw)
        if value < 0 or value > H:
            raise ValueError(f"SVG y-coordinate out of bounds: {attr}={value}")


if __name__ == "__main__":
    raise SystemExit(main())
