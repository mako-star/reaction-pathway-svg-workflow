# OpenClaw/ReacNet Pathway Examples

This directory is a small reproducible dataset for the reaction-pathway SVG
workflow. It mirrors the local folders used during development:

- `Cellulose_C2_to_HMF_Path`
- `HMF_Formaldehyde_Path`
- `HMF_Glycolaldehyde_like_Path`
- `HMF_Hydroxyacetone_like_Path`

Each example contains a pathway README, molecule PNG assets, and the generated
standalone SVG output under `unified_svg`.

Regenerate every example from this directory:

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

Validate every generated SVG:

```powershell
python scripts\validate_unified_svgs.py --root examples\openclaw_reacnet
```

The detailed equation and SMILES inventory is documented in
`docs/openclaw_reacnet_examples.md`.
