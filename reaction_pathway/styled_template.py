"""Reference-style pathway SVG generator for the HMF formaldehyde path."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W = 1448
H = 1086


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a reference-style editable SVG from existing molecular images."
    )
    parser.add_argument("--reference-image", required=True)
    parser.add_argument("--path-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ref = Path(args.reference_image)
    path_dir = Path(args.path_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    assets = {
        "hmf": path_dir / "HMF_S1350_bond1.2.png",
        "c3h5o2": path_dir / "C3H5O2_S3400_bond1.2.png",
        "ch2o": path_dir / "CH2O_S596_bond1.2.png",
        "c3ho": path_dir / "C3HO_S3573_bond1.2.png",
        "c2h3o": path_dir / "C2H3O_S2044_bond1.2.png",
    }
    missing = [str(path) for path in assets.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing molecule images: " + ", ".join(missing))

    boxes = component_boxes()
    write_samed_overlay(ref, out_dir / "samed.png", boxes)
    (out_dir / "boxlib.json").write_text(
        json.dumps({"image": str(ref.resolve()), "boxes": boxes}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    svg = render_svg(assets)
    svg_path = out_dir / "styled_pathway.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"Generated SVG: {svg_path.resolve()}")
    print(f"Generated SAM-style overlay: {(out_dir / 'samed.png').resolve()}")
    print(f"Generated box library: {(out_dir / 'boxlib.json').resolve()}")
    return 0


def component_boxes() -> list[dict]:
    raw = [
        ("AF01", "title", 30, 20, 430, 120),
        ("AF02", "main molecule node: HMF", 318, 140, 520, 360),
        ("AF03", "step label: step 1", 548, 140, 910, 220),
        ("AF04", "reaction equation box: step 1", 690, 250, 1180, 370),
        ("AF05", "main molecule node: C3H5O2", 560, 420, 780, 640),
        ("AF06", "side product node: C3HO", 225, 525, 385, 690),
        ("AF07", "step label: step 2", 850, 490, 1235, 570),
        ("AF08", "reaction equation box: step 2", 870, 590, 1325, 710),
        ("AF09", "final molecule node: CH2O", 800, 770, 1015, 990),
        ("AF10", "side product node: C2H3O", 1195, 755, 1355, 925),
        ("AF11", "species key legend", 60, 740, 510, 1010),
        ("AF12", "curved pathway arrows", 440, 300, 915, 810),
    ]
    return [
        {
            "id": label,
            "prompt": prompt,
            "box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "score": 1.0,
            "source": "manual-template",
        }
        for label, prompt, x1, y1, x2, y2 in raw
    ]


def write_samed_overlay(reference: Path, output: Path, boxes: list[dict]) -> None:
    img = Image.open(reference).convert("RGBA").resize((W, H))
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    for item in boxes:
        box = item["box"]
        x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]
        draw.rectangle([x1, y1, x2, y2], outline=(30, 30, 30, 255), width=4)
        draw.rectangle([x1, y1 - 30, x1 + 74, y1], fill=(30, 30, 30, 230))
        draw.text((x1 + 8, y1 - 27), item["id"], fill=(255, 255, 255, 255), font=font)
    img.save(output)


def render_svg(assets: dict[str, Path]) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
  <title>Formaldehyde Path</title>
  <defs>
    <style>
      text {{ font-family: "Times New Roman", Times, serif; letter-spacing: 0; }}
      .title {{ font-size: 48px; font-weight: 700; fill: #102536; }}
      .subtitle {{ font-size: 26px; font-style: italic; fill: #5e9a94; }}
      .node-title {{ font-size: 20px; font-weight: 700; fill: #17202a; }}
      .node-sub {{ font-size: 17px; font-style: italic; fill: #2d2d2d; }}
      .step-title {{ font-size: 26px; font-weight: 700; }}
      .step-sub {{ font-size: 20px; font-style: italic; font-weight: 600; }}
      .equation {{ font-size: 32px; font-style: italic; fill: #171717; }}
      .legend {{ font-size: 20px; fill: #17202a; }}
      .legend i {{ font-style: italic; }}
    </style>
    <marker id="arrow-teal" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="9" markerHeight="9" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#2b7c78"/>
    </marker>
    <marker id="arrow-gold" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#bc8c45"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="8" markerHeight="8" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#f16052"/>
    </marker>
    <linearGradient id="path-teal" x1="400" y1="230" x2="640" y2="520" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#78b8b2" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#2e827e" stop-opacity="0.72"/>
    </linearGradient>
    <linearGradient id="path-red" x1="680" y1="585" x2="885" y2="835" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#d1a15d" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#f16052" stop-opacity="0.62"/>
    </linearGradient>
    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#16413e" flood-opacity="0.16"/>
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#fbfbf9"/>

  <g id="AF01-title">
    <text class="title" x="34" y="66">Formaldehyde Path</text>
    <path d="M35 84 H202" stroke="#efb2a6" stroke-width="4" stroke-linecap="round"/>
    <path d="M35 86 H207" stroke="#287a77" stroke-width="4" stroke-linecap="round"/>
    <circle cx="212" cy="86" r="4" fill="#287a77"/>
    <text class="subtitle" x="38" y="121">HMF-derived pathway toward CH₂O</text>
  </g>

  <g id="AF12-curved-pathway-arrows">
    <path d="M477 322 C514 352 557 386 597 425 C624 452 637 485 650 518"
          stroke="url(#path-teal)" stroke-width="76" fill="none" stroke-linecap="round"/>
    <path d="M508 331 C548 372 584 410 624 458" stroke="#2b7c78" stroke-width="18"
          fill="none" marker-end="url(#arrow-teal)" opacity="0.72"/>
    <path d="M710 632 C733 675 766 726 816 786 C838 812 856 832 875 851"
          stroke="url(#path-red)" stroke-width="72" fill="none" stroke-linecap="round"/>
    <path d="M731 637 C764 714 805 774 848 814" stroke="#f16052" stroke-width="16"
          fill="none" marker-end="url(#arrow-red)" opacity="0.85"/>
  </g>

  {node_group("AF02-node-HMF", 430, 248, 105, "#287a77", "#b8d7d3", assets["hmf"], "HMF", "(C₆H₆O₃)")}
  {node_group("AF05-node-C3H5O2", 670, 545, 100, "#9a6f36", "#e5cfa6", assets["c3h5o2"], "C₃H₅O₂", "(intermediate)")}
  {node_group("AF09-node-CH2O", 910, 895, 105, "#e34d42", "#f3aaa3", assets["ch2o"], "CH₂O", "(formaldehyde)")}

  <g id="AF06-side-C3HO">
    <circle cx="305" cy="610" r="82" fill="#fffdfa" stroke="#bc8c45" stroke-width="3" stroke-dasharray="9 8"/>
    <image x="250" y="530" width="110" height="86" preserveAspectRatio="xMidYMid meet" href="{data_uri(assets["c3ho"])}"/>
    <text class="node-title" x="305" y="644" text-anchor="middle" fill="#9a6f36">C₃HO</text>
    <text class="node-sub" x="305" y="672" text-anchor="middle">by-product</text>
  </g>
  <path id="AF06-side-C3HO-arrow" d="M575 555 C490 548 435 553 385 584" stroke="#bc8c45" stroke-width="3"
        stroke-dasharray="8 8" fill="none" marker-end="url(#arrow-gold)"/>

  <g id="AF10-side-C2H3O">
    <circle cx="1268" cy="848" r="80" fill="#fffdfa" stroke="#f16052" stroke-width="3" stroke-dasharray="9 8"/>
    <image x="1215" y="775" width="108" height="82" preserveAspectRatio="xMidYMid meet" href="{data_uri(assets["c2h3o"])}"/>
    <text class="node-title" x="1268" y="880" text-anchor="middle" fill="#e34d42">C₂H₃O</text>
    <text class="node-sub" x="1268" y="908" text-anchor="middle">by-product</text>
  </g>
  <path id="AF10-side-C2H3O-arrow" d="M1015 878 C1090 873 1145 844 1185 842" stroke="#f16052" stroke-width="3"
        stroke-dasharray="8 8" fill="none" marker-end="url(#arrow-red)"/>

  {step_box("AF03-step-1", 560, 145, "#287a77", "1", "Step ①:", "ring-opening decomposition")}
  {equation_box("AF04-eq-1", 695, 255, 485, 110, "#287a77", "HMF  →  C₃H₅O₂  +  C₃HO")}
  {step_box("AF07-step-2", 850, 495, "#f16052", "2", "Step ②:", "further fragmentation")}
  {equation_box("AF08-eq-2", 875, 595, 455, 110, "#f16052", "C₃H₅O₂  →  CH₂O  +  C₂H₃O")}

  <g id="AF11-species-key">
    <rect x="60" y="738" width="450" height="280" rx="8" fill="#f7fbf9" stroke="#6f9c99" stroke-width="1.5"/>
    <path d="M93 756 V798 L104 788 L116 798 V756 Z" fill="#287a77"/>
    <text x="145" y="782" font-size="26" font-weight="700" fill="#287a77">Species key</text>
    <path d="M91 797 H484" stroke="#287a77" stroke-width="2" stroke-dasharray="4 5"/>
    {legend_row(103, 828, "#77b8b0", "HMF", "C₆H₆O₃ (5-hydroxymethylfurfural)")}
    {legend_row(103, 868, "#d0a25d", "C₃H₅O₂", "intermediate")}
    {legend_row(103, 908, "#f4dfb5", "C₃HO", "by-product fragment")}
    {legend_row(103, 948, "#f3aaa3", "C₂H₃O", "by-product fragment")}
    {legend_row(103, 988, "#f16052", "CH₂O", "final product (formaldehyde)")}
  </g>
</svg>
"""


def node_group(group_id: str, cx: int, cy: int, r: int, color: str, pale: str, img: Path, title: str, sub: str) -> str:
    return f"""
  <g id="{group_id}" filter="url(#soft-shadow)">
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="#fffefa" stroke="{pale}" stroke-width="16"/>
    <circle cx="{cx}" cy="{cy}" r="{r - 16}" fill="none" stroke="{color}" stroke-width="4"/>
    <circle cx="{cx}" cy="{cy}" r="{r - 26}" fill="#ffffff" stroke="{pale}" stroke-width="2"/>
    <image x="{cx - 70}" y="{cy - 72}" width="140" height="104" preserveAspectRatio="xMidYMid meet" href="{data_uri(img)}"/>
    <text class="node-title" x="{cx}" y="{cy + 50}" text-anchor="middle" fill="{color}">{title}</text>
    <text class="node-sub" x="{cx}" y="{cy + 78}" text-anchor="middle">{sub}</text>
  </g>"""


def step_box(group_id: str, x: int, y: int, color: str, num: str, title: str, sub: str) -> str:
    return f"""
  <g id="{group_id}">
    <path d="M{x - 42},{y + 40} H{x - 10}" stroke="{color}" stroke-width="3" stroke-dasharray="7 8"/>
    <rect x="{x}" y="{y}" width="350" height="74" rx="8" fill="#fbfdfb" stroke="{color}" stroke-width="2"/>
    <path d="M{x + 20},{y + 8} H{x + 62} L{x + 82},{y + 37} L{x + 62},{y + 66} H{x + 20} L{x},{y + 37} Z" fill="{color}"/>
    <text x="{x + 42}" y="{y + 53}" text-anchor="middle" font-size="46" fill="#fff" font-weight="700">{num}</text>
    <text class="step-title" x="{x + 110}" y="{y + 36}" fill="{color}">{title}</text>
    <text class="step-sub" x="{x + 110}" y="{y + 60}" fill="{color}">{sub}</text>
  </g>"""


def equation_box(group_id: str, x: int, y: int, w: int, h: int, color: str, text: str) -> str:
    return f"""
  <g id="{group_id}">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#fffefa" stroke="{color}" stroke-width="1.5"/>
    <path d="M{x + 15},{y + 18} H{x + w - 15}" stroke="{color}" stroke-width="2" stroke-dasharray="3 6"/>
    <text class="equation" x="{x + w / 2}" y="{y + 72}" text-anchor="middle">{text}</text>
  </g>"""


def legend_row(x: int, y: int, color: str, name: str, desc: str) -> str:
    return f"""
    <circle cx="{x}" cy="{y}" r="12" fill="{color}" stroke="#8b6b31" stroke-width="1.5"/>
    <text class="legend" x="{x + 34}" y="{y + 7}"><tspan font-style="italic" font-weight="700">{name}:</tspan> {desc}</text>"""


def data_uri(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


if __name__ == "__main__":
    raise SystemExit(main())
