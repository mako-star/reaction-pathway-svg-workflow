"""Load reaction pathway specs from JSON, with optional YAML support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import PathwaySpec


def load_pathway_spec(path: str | Path) -> PathwaySpec:
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix == ".json":
        data = json.loads(raw)
    elif suffix in {".yaml", ".yml"}:
        data = _load_yaml(raw)
    else:
        raise ValueError("Spec file must be .json, .yaml, or .yml.")
    if not isinstance(data, dict):
        raise ValueError("Spec root must be an object.")
    return PathwaySpec.from_dict(data)


def _load_yaml(raw: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "YAML specs require PyYAML. Install with `pip install pyyaml`, "
            "or use the JSON spec format."
        ) from exc
    return yaml.safe_load(raw)
