"""Generate pathway figures from a Path directory README."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .from_assets import build_spec_data, generate_pathway_svg, render_molecule_assets
from .schema import PathwaySpec
import json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract the first reaction equation from README.md and stitch local molecule images."
    )
    parser.add_argument("path_dir", help="Path directory containing README.md and molecule images.")
    parser.add_argument("--output-dir", "-o", help="Output directory. Defaults to <path_dir>/autopathway.")
    parser.add_argument("--title", help="Override figure title.")
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--height", type=int, default=620)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path_dir = Path(args.path_dir)
    readme = path_dir / "README.md"
    if not readme.exists():
        raise FileNotFoundError(f"README.md not found in: {path_dir}")

    text = readme.read_text(encoding="utf-8")
    equation = extract_equation(text)
    title = args.title or extract_title(text) or path_dir.name
    output_dir = Path(args.output_dir) if args.output_dir else path_dir / "autopathway"
    output_dir.mkdir(parents=True, exist_ok=True)

    spec_data = build_spec_data(
        equation=equation,
        asset_dir=path_dir,
        asset_map={},
        title=title,
        width=args.width,
        height=args.height,
    )
    spec_path = output_dir / "generated_spec.json"
    spec_path.write_text(json.dumps(spec_data, indent=2, ensure_ascii=False), encoding="utf-8")

    spec = PathwaySpec.from_dict(spec_data)
    assets = render_molecule_assets(spec, output_dir / "molecules", backend="placeholder")
    svg_path = generate_pathway_svg(spec, assets, output_dir / "pathway.svg")
    manifest = {
        "title": spec.title,
        "equation": spec.equation,
        "readme": str(readme.resolve()),
        "generated_spec": str(spec_path.resolve()),
        "svg": str(svg_path.resolve()),
        "assets": {
            mol_id: {
                "path": str(asset.path.resolve()),
                "mime_type": asset.mime_type,
                "backend": asset.backend,
            }
            for mol_id, asset in assets.items()
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    safe_print(f"Equation: {equation}")
    safe_print(f"Generated spec: {spec_path.resolve()}")
    safe_print(f"Generated SVG: {svg_path.resolve()}")
    safe_print(f"Manifest: {manifest_path.resolve()}")
    return 0


def extract_equation(text: str) -> str:
    match = re.search(r"##\s*反应方程式.*?```(?:\w+)?\s*(.*?)\s*```", text, re.S)
    if not match:
        match = re.search(r"```(?:\w+)?\s*([^`]*?→[^`]*?)\s*```", text, re.S)
    if not match:
        raise ValueError("Could not find a fenced reaction equation in README.md.")
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    equation_lines = [line for line in lines if "→" in line or "->" in line or "=>" in line]
    if not equation_lines:
        raise ValueError("Found code block, but it does not contain a reaction arrow.")
    return " ".join(equation_lines)


def extract_title(text: str) -> str | None:
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else None


def safe_print(value: str) -> None:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    sys.stdout.write(value.encode(encoding, errors="replace").decode(encoding) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
