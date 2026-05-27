"""Build reaction pathway figures from an equation and existing molecule images."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .rendering import render_molecule_assets
from .schema import PathwaySpec, normalize_species_name, species_tokens_from_equation
from .svg import generate_pathway_svg


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Stitch existing molecular structure images into an editable reaction pathway SVG."
        )
    )
    parser.add_argument("--equation", required=True, help="Reaction equation, e.g. A -> B + C -> D")
    parser.add_argument(
        "--asset-dir",
        required=True,
        help="Directory containing molecule images. File stems should match species names.",
    )
    parser.add_argument(
        "--asset-map",
        help=(
            "Optional JSON mapping from species name to image path. "
            "Use this when file names do not match equation species."
        ),
    )
    parser.add_argument("--output-dir", "-o", default="outputs/reaction_pathway_assets")
    parser.add_argument("--title", default="Reaction Pathway")
    parser.add_argument("--svg-name", default="pathway.svg")
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--height", type=int, default=620)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any species has no matching image. Default behavior also fails, but with this flag the intent is explicit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    asset_dir = Path(args.asset_dir)
    if not asset_dir.exists():
        raise FileNotFoundError(f"Asset directory not found: {asset_dir}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_map = load_asset_map(args.asset_map) if args.asset_map else {}
    spec_data = build_spec_data(
        equation=args.equation,
        asset_dir=asset_dir,
        asset_map=asset_map,
        title=args.title,
        width=args.width,
        height=args.height,
    )
    spec_path = output_dir / "generated_spec.json"
    spec_path.write_text(json.dumps(spec_data, indent=2, ensure_ascii=False), encoding="utf-8")

    spec = PathwaySpec.from_dict(spec_data)
    assets = render_molecule_assets(spec, output_dir / "molecules", backend="placeholder")
    svg_path = generate_pathway_svg(spec, assets, output_dir / args.svg_name)
    manifest = {
        "title": spec.title,
        "equation": spec.equation,
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

    print(f"Generated spec: {spec_path.resolve()}")
    print(f"Generated SVG: {svg_path.resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    return 0


def build_spec_data(
    equation: str,
    asset_dir: Path,
    asset_map: dict[str, Path],
    title: str,
    width: int,
    height: int,
) -> dict:
    species = species_tokens_from_equation(equation)
    image_index = index_images(asset_dir)
    missing: list[str] = []
    molecules: list[dict] = []

    for token in species:
        asset_path = find_asset_path(token, image_index, asset_map)
        if not asset_path:
            missing.append(token)
            continue
        molecules.append(
            {
                "id": token,
                "label": token,
                "asset_path": str(asset_path),
            }
        )

    if missing:
        available = ", ".join(sorted(path.name for path in asset_dir.iterdir() if path.is_file()))
        raise ValueError(
            "No matching molecule image for species: "
            + ", ".join(missing)
            + f". Available files: {available}"
        )

    data = {
        "title": title,
        "equation": equation,
        "layout": "linear",
        "canvas": {
            "width": width,
            "height": height,
            "background": "#ffffff",
            "title": True,
        },
        "molecules": molecules,
    }
    inferred = PathwaySpec.from_dict(data)
    data["main_chain"] = inferred.main_chain
    data["reactions"] = [
        {
            "from": edge.sources,
            "to": edge.targets,
            "label": edge.label,
            "conditions": edge.conditions,
            "kind": edge.kind,
            "side_products": edge.side_products,
        }
        for edge in inferred.reactions
    ]
    return data


def index_images(asset_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in sorted(asset_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        keys = {
            normalize_species_name(path.stem),
            normalize_species_name(path.name),
            compact_species_name(path.stem),
            normalize_species_name(path.stem.split("_", 1)[0]),
            compact_species_name(path.stem.split("_", 1)[0]),
        }
        for key in keys:
            index.setdefault(key, path)
    return index


def load_asset_map(path: str) -> dict[str, Path]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("--asset-map must be a JSON object: {\"species\": \"path/to/image.png\"}")
    return {normalize_species_name(str(key)): Path(str(value)) for key, value in data.items()}


def find_asset_path(
    species: str,
    image_index: dict[str, Path],
    asset_map: dict[str, Path],
) -> Path | None:
    direct = asset_map.get(normalize_species_name(species))
    if direct:
        if not direct.exists():
            raise FileNotFoundError(f"Mapped asset for `{species}` not found: {direct}")
        return direct

    exact_keys = []
    for alias in species_aliases(species):
        exact_keys.extend([normalize_species_name(alias), compact_species_name(alias)])
    for key in exact_keys:
        if key in image_index:
            return image_index[key]

    compact_aliases = [compact_species_name(alias) for alias in species_aliases(species)]
    candidates = [
        path for key, path in image_index.items()
        if any(key.startswith(alias) and len(alias) >= 2 for alias in compact_aliases)
    ]
    unique = sorted(set(candidates), key=lambda path: len(path.name))
    if len(unique) == 1:
        return unique[0]
    if len(unique) > 1:
        names = ", ".join(path.name for path in unique[:8])
        raise ValueError(
            f"Ambiguous image match for `{species}`. Use --asset-map. Candidates: {names}"
        )
    return None


def compact_species_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_species_name(value))


def species_aliases(species: str) -> list[str]:
    aliases = [species]
    paren_matches = re.findall(r"\(([^)]+)\)", species.replace("（", "(").replace("）", ")"))
    aliases.extend(match.strip() for match in paren_matches if match.strip())
    without_paren = re.sub(r"\([^)]*\)", "", species.replace("（", "(").replace("）", ")")).strip()
    if without_paren:
        aliases.append(without_paren)
    return list(dict.fromkeys(aliases))


if __name__ == "__main__":
    raise SystemExit(main())
