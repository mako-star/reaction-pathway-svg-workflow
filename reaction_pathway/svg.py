"""Generate editable SVG reaction pathway figures."""

from __future__ import annotations

import base64
import html
from pathlib import Path

from .layout import NodeBox, compute_layout
from .rendering import MoleculeAsset
from .schema import PathwaySpec


def generate_pathway_svg(
    spec: PathwaySpec,
    assets: dict[str, MoleculeAsset],
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    layout = compute_layout(spec)
    style = spec.style
    canvas = spec.canvas

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{canvas.width}" height="{canvas.height}" '
            f'viewBox="0 0 {canvas.width} {canvas.height}" role="img">'
        ),
        f"<title>{html.escape(spec.title)}</title>",
        "<defs>",
        _marker("arrow-main", style.arrow_color),
        _marker("arrow-side", style.side_arrow_color),
        _css(style.font_family),
        "</defs>",
        f'<rect width="100%" height="100%" fill="{canvas.background}"/>',
    ]

    if canvas.title:
        parts.append(
            f'<text class="figure-title" x="{canvas.width / 2:.1f}" y="44" '
            f'text-anchor="middle">{html.escape(spec.title)}</text>'
        )
        if spec.equation:
            parts.append(
                f'<text class="equation" x="{canvas.width / 2:.1f}" y="72" '
                f'text-anchor="middle">{html.escape(spec.equation)}</text>'
            )

    parts.append('<g id="arrows">')
    for edge in layout.edges:
        if edge.source not in layout.nodes or edge.target not in layout.nodes:
            continue
        source = layout.nodes[edge.source]
        target = layout.nodes[edge.target]
        parts.append(_arrow(source, target, edge.kind))
        if edge.label:
            lx = (source.cx + target.cx) / 2
            ly = (source.cy + target.cy) / 2 - 14
            parts.append(
                f'<text class="arrow-label" x="{lx:.1f}" y="{ly:.1f}" '
                f'text-anchor="middle">{html.escape(edge.label)}</text>'
            )
        if edge.conditions:
            lx = (source.cx + target.cx) / 2
            ly = (source.cy + target.cy) / 2 + 18
            parts.append(
                f'<text class="condition-label" x="{lx:.1f}" y="{ly:.1f}" '
                f'text-anchor="middle">{html.escape(edge.conditions)}</text>'
            )
    parts.append("</g>")

    parts.append('<g id="molecules">')
    for mol_id, box in layout.nodes.items():
        mol = spec.molecules[mol_id]
        asset = assets[mol_id]
        parts.append(f'<g id="node-{_xml_id(mol_id)}" class="molecule-node {box.role}">')
        parts.append(_image(asset, box))
        label_y = box.y - 10 if box.role == "main" else box.y + box.h + 22
        parts.append(
            f'<text class="molecule-label" x="{box.cx:.1f}" y="{label_y:.1f}" '
            f'text-anchor="middle">{html.escape(mol.display_label)}</text>'
        )
        if mol.formula and mol.formula != mol.display_label:
            parts.append(
                f'<text class="formula-label" x="{box.cx:.1f}" y="{label_y + 19:.1f}" '
                f'text-anchor="middle">{html.escape(mol.formula)}</text>'
            )
        parts.append("</g>")
    parts.append("</g>")

    if spec.note:
        parts.append(
            f'<text class="note" x="{canvas.width / 2:.1f}" y="{canvas.height - 24}" '
            f'text-anchor="middle">{html.escape(spec.note)}</text>'
        )

    parts.append("</svg>")
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path


def _image(asset: MoleculeAsset, box: NodeBox) -> str:
    data = base64.b64encode(asset.path.read_bytes()).decode("ascii")
    href = f"data:{asset.mime_type};base64,{data}"
    return (
        f'<image x="{box.x:.1f}" y="{box.y:.1f}" width="{box.w:.1f}" height="{box.h:.1f}" '
        f'preserveAspectRatio="xMidYMid meet" href="{href}" xlink:href="{href}"/>'
    )


def _arrow(source: NodeBox, target: NodeBox, kind: str) -> str:
    color_class = "side-arrow" if kind == "side" else "main-arrow"
    marker = "arrow-side" if kind == "side" else "arrow-main"
    dashed = ' stroke-dasharray="7 5"' if kind == "side" else ""

    if abs(source.cy - target.cy) < 36:
        x1 = source.x + source.w + 10 if target.cx > source.cx else source.x - 10
        x2 = target.x - 10 if target.cx > source.cx else target.x + target.w + 10
        return (
            f'<line class="{color_class}" x1="{x1:.1f}" y1="{source.cy:.1f}" '
            f'x2="{x2:.1f}" y2="{target.cy:.1f}" marker-end="url(#{marker})"{dashed}/>'
        )

    sx = source.cx
    sy = source.y if target.cy < source.cy else source.y + source.h
    tx = target.cx
    ty = target.y + target.h if target.cy < source.cy else target.y
    c1y = sy + (ty - sy) * 0.45
    c2y = sy + (ty - sy) * 0.75
    d = f"M {sx:.1f},{sy:.1f} C {sx:.1f},{c1y:.1f} {tx:.1f},{c2y:.1f} {tx:.1f},{ty:.1f}"
    return f'<path class="{color_class}" d="{d}" marker-end="url(#{marker})"{dashed}/>'


def _marker(marker_id: str, color: str) -> str:
    return f"""
  <marker id="{marker_id}" viewBox="0 0 10 10" refX="9.4" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/>
  </marker>"""


def _css(font_family: str) -> str:
    return f"""<style>
  text {{
    font-family: {font_family};
    letter-spacing: 0;
  }}
  .figure-title {{ font-size: 24px; font-weight: 600; fill: #111111; }}
  .equation {{ font-size: 15px; fill: #5f6368; }}
  .molecule-label {{ font-size: 17px; font-style: italic; fill: #111111; }}
  .formula-label {{ font-size: 13px; fill: #5f6368; }}
  .arrow-label {{ font-size: 14px; fill: #3d3d3d; }}
  .condition-label {{ font-size: 12px; fill: #5f6368; }}
  .note {{ font-size: 12px; fill: #777777; }}
  .main-arrow {{
    stroke: #2c2c2c;
    stroke-width: 2.0;
    fill: none;
    stroke-linecap: round;
  }}
  .side-arrow {{
    stroke: #8a8a8a;
    stroke-width: 1.6;
    fill: none;
    stroke-linecap: round;
  }}
</style>"""


def _xml_id(value: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in value)
    return safe or "molecule"
