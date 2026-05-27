"""Command line interface for reaction pathway figure generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .rendering import render_molecule_assets
from .spec_loader import load_pathway_spec
from .svg import generate_pathway_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate editable SVG reaction pathway figures from SMILES and reaction specs."
    )
    parser.add_argument("spec", help="Path to reaction spec (.json, .yaml, .yml)")
    parser.add_argument("--output-dir", "-o", default="outputs/reaction_pathway")
    parser.add_argument(
        "--backend",
        choices=["auto", "smiles-to-3d", "placeholder"],
        default="auto",
        help="Molecule rendering backend.",
    )
    parser.add_argument("--svg-name", default="pathway.svg")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    spec = load_pathway_spec(args.spec)
    output_dir = Path(args.output_dir)
    asset_dir = output_dir / "molecules"
    output_dir.mkdir(parents=True, exist_ok=True)

    assets = render_molecule_assets(spec, asset_dir, backend=args.backend)
    svg_path = generate_pathway_svg(spec, assets, output_dir / args.svg_name)
    manifest = {
        "title": spec.title,
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
    print(f"Generated SVG: {svg_path.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
