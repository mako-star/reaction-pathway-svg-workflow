# Reaction Pathway SVG Workflow

This repository packages a reproducible workflow for generating publication-style
editable SVG reaction pathway figures.

## Core Rule

There is only one valid input model for the intended workflow. A pathway job is
allowed to run only when the following three inputs are present together:

1. A chemical reaction equation.
2. Molecule structure images for every species in the equation.
3. A template image that defines the visual style and layout target.

These are not three alternative modes. They are one complete input package. The
equation provides chemical topology, the molecule images provide visual content,
and the template image provides the figure style to reproduce. If any one of the
three is missing, the workflow is incomplete and should not proceed.

## What It Produces

The workflow converts one complete pathway input package into a standalone
`pathway_unified.svg`:

- molecule images are embedded as resized `data:image/png;base64` assets;
- the SVG has no external image links;
- the SVG avoids fragile SVG filters;
- major visual blocks are grouped with stable SVG ids for later editing in
  Inkscape or another SVG editor.

## Expected Input Package

Each reaction pathway lives in one folder:

```text
Some_Reaction_Path/
  README.md                  # contains the reaction equation
  template.png               # required visual template/reference image
  HMF_S1350_bond1.2.png       # molecule image
  C3H5O2_S3400_bond1.2.png    # molecule image
  C3HO_S3573_bond1.2.png      # molecule image
  CH2O_S596_bond1.2.png       # molecule image
  C2H3O_S2044_bond1.2.png     # molecule image
```

The current command-line implementation reads the reaction equation and molecule
images directly. Template handling is represented by the selected SVG template
implementation; future segmentation/template-parsing code should consume the
template image explicitly before generation.

## Quick Start

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Generate checked-in examples:

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

Validate generated SVG files:

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
- [Example data: equations and molecule images](docs/openclaw_reacnet_examples.md)

## Important Constraint

Do not present equation-only, molecule-image-only, README-only, or JSON-only
generation as user-facing workflows. Those scripts may exist as internal
developer utilities, but the product workflow requires the complete three-part
input package.
