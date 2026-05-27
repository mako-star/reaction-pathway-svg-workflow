"""Molecule asset rendering adapters."""

from __future__ import annotations

import html
import json
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .schema import Molecule, PathwaySpec


RenderBackend = Literal["auto", "smiles-to-3d", "placeholder"]


@dataclass(frozen=True)
class MoleculeAsset:
    molecule_id: str
    path: Path
    mime_type: str
    backend: str


def render_molecule_assets(
    spec: PathwaySpec,
    output_dir: str | Path,
    backend: RenderBackend = "auto",
) -> dict[str, MoleculeAsset]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    provided = _provided_assets(spec)
    remaining = [mol for mol in spec.molecules.values() if mol.id not in provided]

    rendered: dict[str, MoleculeAsset] = {}
    if remaining and backend in {"auto", "smiles-to-3d"}:
        try:
            rendered = _render_with_smiles_to_3d(remaining, output_dir)
        except Exception as exc:
            if backend == "smiles-to-3d":
                raise
            print(f"[reaction_pathway] smiles-to-3d unavailable, using placeholders: {exc}")

    missing = [mol for mol in remaining if mol.id not in rendered]
    if missing:
        rendered.update(_render_placeholders(missing, output_dir))
    return {**provided, **rendered}


def _render_with_smiles_to_3d(
    molecules_to_render: list[Molecule],
    output_dir: Path,
) -> dict[str, MoleculeAsset]:
    from smiles_to_3d.render import batch_render  # type: ignore

    molecules = [
        {"name": _safe_name(mol.id), "smiles": mol.smiles}
        for mol in molecules_to_render
        if mol.smiles
    ]
    if len(molecules) != len(molecules_to_render):
        missing = [mol.id for mol in molecules_to_render if not mol.smiles]
        raise RuntimeError(f"Missing SMILES for molecule assets: {', '.join(missing)}")
    results = batch_render(molecules, str(output_dir))
    assets: dict[str, MoleculeAsset] = {}
    id_by_safe = {_safe_name(mol.id): mol.id for mol in molecules_to_render}
    failures = []

    for result in results:
        mol_id = id_by_safe.get(result.get("name", ""), result.get("name", ""))
        if result.get("success"):
            assets[mol_id] = MoleculeAsset(
                molecule_id=mol_id,
                path=Path(result["png"]),
                mime_type="image/png",
                backend="smiles-to-3d",
            )
        else:
            failures.append({"id": mol_id, "error": result.get("error", "unknown error")})

    if failures:
        (output_dir / "render_failures.json").write_text(
            json.dumps(failures, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        missing = ", ".join(item["id"] for item in failures)
        raise RuntimeError(f"smiles-to-3d failed for: {missing}")
    return assets


def _render_placeholders(
    molecules_to_render: list[Molecule],
    output_dir: Path,
) -> dict[str, MoleculeAsset]:
    assets: dict[str, MoleculeAsset] = {}
    for mol in molecules_to_render:
        filename = f"{_safe_name(mol.id)}.svg"
        path = output_dir / filename
        path.write_text(_placeholder_svg(mol), encoding="utf-8")
        assets[mol.id] = MoleculeAsset(
            molecule_id=mol.id,
            path=path,
            mime_type="image/svg+xml",
            backend="placeholder",
        )
    return assets


def _provided_assets(spec: PathwaySpec) -> dict[str, MoleculeAsset]:
    assets: dict[str, MoleculeAsset] = {}
    for mol in spec.molecules.values():
        if not mol.asset_path:
            continue
        path = Path(mol.asset_path)
        if not path.exists():
            raise FileNotFoundError(f"Asset for molecule `{mol.id}` not found: {path}")
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        assets[mol.id] = MoleculeAsset(
            molecule_id=mol.id,
            path=path,
            mime_type=mime_type,
            backend="provided",
        )
    return assets


def _placeholder_svg(mol: Molecule) -> str:
    label = html.escape(mol.display_label)
    smiles = html.escape(_trim_middle(mol.smiles or "provided structure", 28))
    formula = html.escape(mol.formula or "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="320" viewBox="0 0 420 320">
  <rect x="8" y="8" width="404" height="304" rx="16" fill="#ffffff" stroke="#d3d7de" stroke-width="2"/>
  <g opacity="0.95">
    <circle cx="142" cy="152" r="34" fill="#8c8c8c"/>
    <circle cx="230" cy="116" r="26" fill="#e53935"/>
    <circle cx="262" cy="190" r="22" fill="#f7f7f7" stroke="#9aa0a6" stroke-width="2"/>
    <line x1="172" y1="140" x2="206" y2="126" stroke="#4a4a4a" stroke-width="12" stroke-linecap="round"/>
    <line x1="244" y1="141" x2="254" y2="168" stroke="#4a4a4a" stroke-width="9" stroke-linecap="round"/>
  </g>
  <text x="210" y="252" text-anchor="middle" font-family="Times New Roman, Times, serif" font-size="30" fill="#111">{label}</text>
  <text x="210" y="282" text-anchor="middle" font-family="Consolas, monospace" font-size="16" fill="#5f6368">{formula or smiles}</text>
</svg>
"""


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "molecule"


def _trim_middle(value: str, max_len: int) -> str:
    if len(value) <= max_len:
        return value
    keep = max_len - 3
    left = keep // 2
    right = keep - left
    return f"{value[:left]}...{value[-right:]}"
