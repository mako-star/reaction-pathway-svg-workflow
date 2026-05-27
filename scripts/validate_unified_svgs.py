#!/usr/bin/env python3
"""Validate generated standalone SVG pathway outputs."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate generated pathway_unified.svg files.")
    parser.add_argument(
        "--root",
        default="examples/openclaw_reacnet",
        help="Root directory containing generated *Path/*Pass folders.",
    )
    parser.add_argument(
        "--svg-name",
        default="pathway_unified.svg",
        help="SVG filename inside each unified_svg directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    failures: list[str] = []

    for svg in sorted(root.glob(f"*/unified_svg/{args.svg_name}")):
        result = validate_svg(svg)
        status = "OK" if result.ok else "FAIL"
        print(
            f"{status} {svg} "
            f"canvas={result.canvas} embedded_png={result.embedded_png} "
            f"external_assets={result.external_assets} filters={result.filters}"
        )
        failures.extend(f"{svg}: {message}" for message in result.errors)

    if failures:
        print("\nValidation failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


class SvgValidation:
    def __init__(
        self,
        *,
        ok: bool,
        canvas: str,
        embedded_png: int,
        external_assets: int,
        filters: int,
        errors: list[str],
    ) -> None:
        self.ok = ok
        self.canvas = canvas
        self.embedded_png = embedded_png
        self.external_assets = external_assets
        self.filters = filters
        self.errors = errors


def validate_svg(svg: Path) -> SvgValidation:
    errors: list[str] = []
    try:
        ET.parse(svg)
    except ET.ParseError as exc:
        errors.append(f"invalid XML: {exc}")

    text = svg.read_text(encoding="utf-8")
    size = re.search(r"<svg[^>]*width=\"([0-9.]+)\"[^>]*height=\"([0-9.]+)\"", text)
    canvas = "unknown"
    if size:
        canvas = f"{size.group(1)}x{size.group(2)}"
    else:
        errors.append("missing explicit SVG width/height")

    embedded_png = text.count("data:image/png;base64,")
    if embedded_png == 0:
        errors.append("no embedded PNG molecule assets found")

    filters = text.count("filter=")
    if filters:
        errors.append("contains SVG filters, which can be fragile in Inkscape")

    hrefs = re.findall(r"(?:href|xlink:href)=\"([^\"]+)\"", text)
    external_assets = len([href for href in hrefs if not href.startswith("data:image/")])
    if external_assets:
        errors.append("contains external linked assets")

    return SvgValidation(
        ok=not errors,
        canvas=canvas,
        embedded_png=embedded_png,
        external_assets=external_assets,
        filters=filters,
        errors=errors,
    )


if __name__ == "__main__":
    raise SystemExit(main())
