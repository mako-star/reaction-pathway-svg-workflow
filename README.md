# Reaction Pathway SVG Workflow

This repository packages a reproducible workflow for turning chemistry reaction
pathway folders into publication-style editable SVG figures.

## What It Does

The pathway workflow takes a directory containing:

- `README.md` with a fenced reaction equation;
- molecule structure PNGs generated from SMILES/3D rendering tools;
- optional pathway-specific layout rules.

It produces a standalone `pathway_unified.svg` that is safe to open in Inkscape:

- molecule PNGs are embedded as resized `data:image/png;base64` assets;
- no external asset links are required;
- no SVG filters are used;
- each major visual block is grouped with a stable SVG id for later editing.

### Quick Start

Install the Python dependency:

```powershell
python -m pip install -r requirements.txt
```

Generate all checked-in examples:

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

Validate the generated SVG files:

```powershell
python scripts\validate_unified_svgs.py --root examples\openclaw_reacnet
```

Generate from the local OpenClaw/ReacNet data folder:

```powershell
python scripts\generate_all_unified_pathways.py --root D:\data\openclaw_reacnet
```

Generate one pathway only:

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Hydroxyacetone_like_Path
```

## Documentation

- [Detailed usage and commands](docs/usage.md)
- [Workflow guide](docs/reaction_pathway_workflow.md)
- [Tool inventory](docs/tools.md)
- [Today example data: equations and SMILES](docs/openclaw_reacnet_examples.md)

The checked-in example data lives under `examples/openclaw_reacnet`.

## Common Commands

Show help for the main batch generator:

```powershell
python scripts\generate_all_unified_pathways.py --help
```

Generate all checked-in demo pathways:

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

Generate one pathway from a local OpenClaw/ReacNet folder:

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Formaldehyde_Path
```

Validate generated standalone SVG files:

```powershell
python scripts\validate_unified_svgs.py --root examples\openclaw_reacnet
```

For full command formats, input-folder rules, output files, and troubleshooting,
see [docs/usage.md](docs/usage.md).
