#!/usr/bin/env python3
"""Generate unified standalone SVGs for complete *Path/*Pass input packages.

The input folder convention is intentionally simple:

- each pathway lives in one directory whose name ends with Path or Pass;
- the directory contains a README.md with a fenced reaction equation;
- molecule renderings are stored beside the README as PNG files;
- a template image or code-backed template is available for the visual layout.

By default this script targets the local OpenClaw working directory used during
development, but the root is configurable so the workflow can be reproduced from
the checked-in examples or from a future frontend upload directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reaction_pathway.hydroxyacetone_convergent import main as generate_hydroxyacetone
from reaction_pathway.unified_card_template import main as generate_one


ROOT = Path("examples/openclaw_reacnet")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate standalone SVGs from complete pathway input packages.")
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Root directory containing complete *Path/*Pass input packages.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Generate only the named folder. Can be passed multiple times.",
    )
    parser.add_argument(
        "--output-subdir",
        default="unified_svg",
        help="Per-path output directory name.",
    )
    parser.add_argument(
        "--generic-only",
        action="store_true",
        help="Disable custom templates such as the enlarged hydroxyacetone convergent layout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    if not root.exists():
        raise FileNotFoundError(f"Pathway root not found: {root}")

    targets = sorted(
        path for path in root.iterdir()
        if path.is_dir() and (path.name.endswith("Path") or path.name.endswith("Pass"))
    )
    if args.only:
        wanted = set(args.only)
        targets = [path for path in targets if path.name in wanted]
    if not targets:
        raise FileNotFoundError(f"No matching *Path/*Pass folders found under {root}")

    for path in targets:
        print(f"\n=== {path.name} ===")
        output_dir = path / args.output_subdir
        if not args.generic_only and path.name == "HMF_Hydroxyacetone_like_Path":
            generate_hydroxyacetone(["--path-dir", str(path), "--output-dir", str(output_dir)])
        else:
            generate_one([str(path), "--output-dir", str(output_dir)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
