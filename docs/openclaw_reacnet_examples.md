# OpenClaw/ReacNet Example Data

The checked-in examples under `examples/openclaw_reacnet` are the reproducible
sample set prepared during this workflow. Each folder includes:

- original pathway `README.md`;
- molecule structure PNGs generated upstream from SMILES/3D rendering;
- a template role supplied by the current code templates (`unified_card_template`
  or `hydroxyacetone_convergent`) rather than a separate raster `template.png`;
- generated standalone SVG in `unified_svg/pathway_unified.svg`;
- machine-readable generated spec in `unified_svg/generated_spec.json`.

For production use, treat the template as a required input alongside the
equation and molecule images. The checked-in examples are historical fixtures:
their template image has already been translated into Python template code.

## HMF -> Formaldehyde Path

Equation:

```text
C₆H₆O₃ (HMF) -> C₃H₅O₂ + C₃HO -> CH₂O + C₂H₃O
```

Detailed reactions:

```text
C₆H₆O₃ -> C₃H₅O₂ + C₃HO
C₃H₅O₂ -> CH₂O + C₂H₃O
```

Species:

| Species | Formula | SMILES | Asset |
| --- | --- | --- | --- |
| HMF | C₆H₆O₃ | `OCc1ccc(C=O)o1` | `HMF_S1350_bond1.2.png` |
| C3H5O2 | C₃H₅O₂ | unavailable in README | `C3H5O2_S3400_bond1.2.png` |
| C3HO | C₃HO | `[CH]=C1[C]O1` | `C3HO_S3573_bond1.2.png` |
| CH2O | CH₂O | `C=O` | `CH2O_S596_bond1.2.png` |
| C2H3O | C₂H₃O | unavailable in README | `C2H3O_S2044_bond1.2.png` |

## HMF -> Glycolaldehyde-Like Path

Equation:

```text
C₆H₆O₃ (HMF) -> C₃H₅O₂ + C₃HO -> C₂H₃O + CH₂O -> C₂H₄O₂ + HO·
```

Detailed reactions:

```text
C₆H₆O₃ -> C₃H₅O₂ + C₃HO
C₃H₅O₂ -> C₂H₃O + CH₂O
C₂H₃O + HO· -> C₂H₄O₂
```

Species:

| Species | Formula | SMILES | Asset |
| --- | --- | --- | --- |
| HMF | C₆H₆O₃ | `OCc1ccc(C=O)o1` | `HMF_S1350_bond1.2.png` |
| C3H5O2 | C₃H₅O₂ | unavailable in README | `C3H5O2_S3400_bond1.2.png` |
| C3HO | C₃HO | `[CH]=C1[C]O1` | `C3HO_S3573_bond1.2.png` |
| C2H3O | C₂H₃O | unavailable in README | `C2H3O_S2044_bond1.2.png` |
| CH2O | CH₂O | `C=O` | `CH2O_S596_bond1.2.png` |
| HO | HO· | `[OH]` | `HO_S3832_bond1.2.png` |
| C2H4O2 | C₂H₄O₂ | `OCC=O` | `C2H4O2_S2012_bond1.2.png` |

## HMF -> Hydroxyacetone-Like Path

Equation:

```text
C₆H₆O₃ -> C₃H₅O₂ + C₃HO
C₃H₅O₂ -> CH₂O + C₂H₃O
CH₂O + H· -> CH₃O
C₂H₃O + CH₃O -> C₃H₆O₂
```

This is a convergent topology. `C₂H₃O` branches from step 2 and recombines with
`CH₃O` in step 4.

Species:

| Species | Formula | SMILES | Asset |
| --- | --- | --- | --- |
| HMF | C₆H₆O₃ | `OCc1ccc(C=O)o1` | `HMF_S1350_bond1.2.png` |
| C3H5O2 | C₃H₅O₂ | unavailable in README | `C3H5O2_S3400_bond1.2.png` |
| C3HO | C₃HO | `[CH]=C1[C]O1` | `C3HO_S3573_bond1.2.png` |
| CH2O | CH₂O | `C=O` | `CH2O_S596_bond1.2.png` |
| C2H3O | C₂H₃O | unavailable in README | `C2H3O_S2044_bond1.2.png` |
| H | H· | `[H]` | `H_S3830_bond1.2.png` |
| CH3O | CH₃O | `[CH3]O` | `CH3O_S3359_bond1.2.png` |
| C3H6O2 | C₃H₆O₂ | `CC(=O)CO` | `C3H6O2_S2140_bond1.2.png` |

## Cellulose C2 -> HMF Path

Equation:

```text
C₁₂H₂₂O₁₁ (cellobiose) -> C₆H₁₁O₆ + C₆H₁₁O₅ -> LG + HO· + H·
```

Detailed reactions:

```text
C₁₂H₂₂O₁₁ -> C₆H₁₁O₆ + C₆H₁₁O₅
C₆H₁₁O₅ -> LG (C₆H₁₀O₅) + HO·
C₆H₁₁O₆ -> product + H·
```

Species with README SMILES:

| Species | Formula | SMILES |
| --- | --- | --- |
| Cellobiose | C₁₂H₂₂O₁₁ | `OC[C@H]1OC(O[C@H]2OC(CO)[C@@H](O)[C@H]2O)[C@@H](O)[C@@H]1O` |
| LG | C₆H₁₀O₅ | `C1[C@@H]2[C@H]([C@@H]([C@H]([C@H](O1)O2)O)O)O` |
| HO | HO· | `[OH]` |
| H | H· | `[H]` |

The folder includes additional ReaxFF intermediate PNGs from the source data.
