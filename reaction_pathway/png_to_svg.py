"""Wrap rendered molecule PNGs as standalone SVG files."""

from __future__ import annotations

import argparse
import base64
import html
from pathlib import Path

from PIL import Image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert PNG molecule images into SVG wrappers.")
    parser.add_argument("input", help="PNG file or directory containing PNG files.")
    parser.add_argument("--output-dir", "-o", help="Directory for SVG files.")
    parser.add_argument("--pattern", default="*_bond1.2.png", help="Directory glob pattern.")
    parser.add_argument(
        "--mode",
        choices=["embed", "link"],
        default="embed",
        help="embed stores PNG bytes in SVG; link references the original PNG path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input)
    if input_path.is_dir():
        files = sorted(input_path.glob(args.pattern))
        output_dir = Path(args.output_dir) if args.output_dir else input_path / "molecule_svgs"
    else:
        files = [input_path]
        output_dir = Path(args.output_dir) if args.output_dir else input_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    if not files:
        raise FileNotFoundError(f"No PNG files matched: {input_path} / {args.pattern}")

    for png_path in files:
        svg_path = output_dir / f"{png_path.stem}.svg"
        svg_path.write_text(png_to_svg(png_path, mode=args.mode), encoding="utf-8")
        print(f"{png_path.name} -> {svg_path}")
    return 0


def png_to_svg(png_path: Path, mode: str = "embed") -> str:
    with Image.open(png_path) as img:
        width, height = img.size
    title = html.escape(png_path.stem)
    href = (
        f"data:image/png;base64,{base64.b64encode(png_path.read_bytes()).decode('ascii')}"
        if mode == "embed"
        else png_path.resolve().as_posix()
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <title>{title}</title>
  <image id="{title}" x="0" y="0" width="{width}" height="{height}"
         preserveAspectRatio="xMidYMid meet"
         href="{href}" xlink:href="{href}"/>
</svg>
"""


if __name__ == "__main__":
    raise SystemExit(main())
