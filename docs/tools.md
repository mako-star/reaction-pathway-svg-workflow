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

- `reaction_pathway.unified_card_template`: generic standalone SVG generator.
- `reaction_pathway.hydroxyacetone_convergent`: enlarged custom layout for the
  HMF hydroxyacetone-like convergent pathway.
- `reaction_pathway.from_readme`: extracts reaction equations from pathway
  README files.
- `reaction_pathway.from_assets`: matches molecule species to local image
  assets and builds structured specs.
- `scripts/generate_all_unified_pathways.py`: batch entry point for `*Path` and
  `*Pass` folders.
- `scripts/validate_unified_svgs.py`: XML/resource validation for generated SVGs.

## Upstream/External Tools Used In The Data Pipeline

These are not required to regenerate the checked-in SVGs if PNG molecule assets
already exist, but they are part of the upstream molecule-rendering workflow:

- `mako-star/smiles-to-3d`: SMILES-to-3D molecule rendering project.
- RDKit: molecule parsing, embedding, and chemistry utilities.
- PyMOL: high-quality molecular rendering.
- Inkscape: manual inspection and downstream SVG editing.
- Microsoft Edge/Chromium headless mode: optional local SVG screenshot preview.

## Optional Future Tools

- Roboflow/SAM-style segmentation can be used for template/icon detection when
  starting from a raster reference image, but the current reproducible workflow
  does not require it. The current output is generated directly as SVG groups.
- A web frontend can wrap this workflow by uploading a pathway folder and
  returning the generated standalone SVG plus `generated_spec.json`.
