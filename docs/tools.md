# Tool Inventory

## Required Runtime

- Python 3.10+
- Pillow (`PIL`) for resizing molecule PNGs before embedding them into SVG
- Requests for the optional Roboflow/SAM segmentation helper

Install:

```powershell
python -m pip install -r requirements.txt
```

## Repository Tools

- `reaction_pathway.unified_card_template`: code implementation of the default
  template-driven standalone SVG generator.
- `reaction_pathway.hydroxyacetone_convergent`: enlarged custom layout for the
  HMF hydroxyacetone-like convergent pathway.
- `reaction_pathway.from_readme`: extracts reaction equations from pathway
  README files; internal utility, not a separate user input mode.
- `reaction_pathway.from_assets`: matches molecule species to local image
  assets and builds structured specs; internal utility, not a separate user
  input mode.
- `scripts/generate_all_unified_pathways.py`: batch entry point for `*Path` and
  `*Pass` folders containing the complete input package.
- `scripts/validate_unified_svgs.py`: XML/resource validation for generated SVGs.

## Upstream/External Tools Used In The Data Pipeline

These are not required to regenerate the checked-in SVGs if PNG molecule assets
already exist, but they are part of the upstream molecule-rendering workflow:

- `mako-star/smiles-to-3d`: SMILES-to-3D molecule rendering project.
- RDKit: molecule parsing, embedding, and chemistry utilities.
- PyMOL: high-quality molecular rendering.
- Inkscape: manual inspection and downstream SVG editing.
- Microsoft Edge/Chromium headless mode: optional local SVG screenshot preview.

## Template Tools

- Roboflow/SAM-style segmentation is used to parse a raster template image into
  template regions such as molecule cards, arrows, equation boxes, and legends.
- The current checked-in templates are code implementations of template images.
  They should be treated as the template part of the complete input package
  until raster-template parsing is fully connected.
- A web frontend should upload one complete pathway package containing reaction
  equation, molecule images, and template image, then return the generated
  standalone SVG plus `generated_spec.json`.
