#!/usr/bin/env python3
"""Thin wrapper for `python -m reaction_pathway.cli`."""

from reaction_pathway.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
