# Reaction Pathway SVG Workflow

This workflow packages the chemistry-specific version of the AutoFigure-style
idea used in the current project:

```text
reaction equation + molecule PNG assets -> structured pathway spec -> standalone editable SVG
```

The current implementation assumes molecule structures have already been
rendered, for example by `smiles-to-3d`, RDKit, PyMOL, or another molecular
visualization route. The SVG generator focuses on connecting those molecular
images into a consistent pathway figure.

For copy-paste command lines and every script parameter, see
[`docs/usage.md`](usage.md).

## Directory Contract

Each pathway should be placed in one folder whose name ends with `Path` or
`Pass`:

```text
My_Reaction_Path/
  README.md
  HMF_S1350_bond1.2.png
  CH2O_S596_bond1.2.png
  ...
```

The folder must contain:

- `README.md`: includes a fenced code block under `反应方程式`.
- `*_bond1.2.png` or similarly named molecule PNGs.

The generator extracts the first fenced reaction equation from the README and
matches species names to image filenames. For example, `CH₂O` is matched to
`CH2O_S596_bond1.2.png`.

## Generate SVGs

Generate all examples checked into the repository:

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

Generate all local OpenClaw/ReacNet folders:

```powershell
python scripts\generate_all_unified_pathways.py --root D:\data\openclaw_reacnet
```

Generate one folder:

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Formaldehyde_Path
```

Outputs are written to:

```text
<PathFolder>/unified_svg/
  generated_spec.json
  pathway_unified.svg
```

## Validate Outputs

Run:

```powershell
python scripts\validate_unified_svgs.py --root examples\openclaw_reacnet
```

The validator checks that each SVG:

- parses as XML;
- has explicit canvas size;
- embeds molecule PNGs as `data:image/png;base64`;
- has no external asset links;
- has no SVG filters.

## Layout Rules

The default layout is a vertical card style:

- main-chain species are placed in equal-sized cards;
- each reaction step gets a compact reaction-equation box;
- side products are placed in small side cards;
- the right panel contains title and species/formula legend.

`HMF_Hydroxyacetone_like_Path` uses a custom convergent layout because the
reaction has four steps and a branch that later recombines. Its canvas is larger
(`2400 x 1600`) so arrows and side branches stay editable instead of being
cramped.

## Frontend Integration Shape

A future frontend can upload:

```text
README.md
molecule PNG files
optional explicit JSON spec
```

The backend route can call the same Python entry point:

```powershell
python scripts\generate_all_unified_pathways.py --root <uploaded-root> --only <folder-name>
```

Then return:

- `pathway_unified.svg` for editing/export;
- `generated_spec.json` for provenance and future regeneration.

## Important Constraints

- Keep generated SVGs standalone when the target editor is Inkscape.
- Keep molecule renderings as input assets; do not rely on remote links.
- Use a larger canvas when the pathway has more than three steps or contains
  convergent/parallel reactions.
- Prefer grouped SVG elements with stable ids so later UI editing can target
  cards, arrows, equations, and legends independently.
