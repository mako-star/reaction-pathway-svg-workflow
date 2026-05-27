#!/usr/bin/env python3
"""Thin wrapper for `python -m reaction_pathway.from_readme`."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reaction_pathway.from_readme import main


if __name__ == "__main__":
    raise SystemExit(main())
