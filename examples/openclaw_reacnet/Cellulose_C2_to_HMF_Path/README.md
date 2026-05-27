# 纤维素 → HMF 反应路径 (Cellulose C2 to HMF Path)

本目录包含纤维素降解生成 HMF 及相关产物的反应路径图。

---

## 工作流程

```
SMILES → SDF → PNG → SVG (单分子)
                      ↓
              路径图 SVG 组装
```

---

## 反应方程式

### 主反应链 (Y-split 拓扑)

```
C₁₂H₂₂O₁₁ (纤维二糖) → C₆H₁₁O₆ + C₆H₁₁O₅ → LG + HO· + H·
```

**详细步骤:**

1. **糖苷键断裂**  
   `C₁₂H₂₂O₁₁ → C₆H₁₁O₆ + C₆H₁₁O₅`  
   纤维二糖的 β-1,4 糖苷键断裂，生成两个葡萄糖基碎片

2. **左旋葡聚糖生成**  
   `C₆H₁₁O₅ → LG (C₆H₁₀O₅) + HO·`  
   脱羟基生成左旋葡聚糖 (Levoglucosan)

3. **H· 释放**  
   `C₆H₁₁O₆ → 产物 + H·`  
   脱氢反应

---

## 完整降解路径

纤维素在 ReaxFF MD 模拟中的主要降解路径：

```
Cellulose (C₆H₁₀O₅)ₙ
    │
    ▼ 热解
Cellobiose (C₁₂H₂₂O₁₁)
    │
    ├─→ C₆H₁₁O₆ ─→ C₆H₉O₄ + H₂O
    │                   │
    │                   ▼
    │               C₅H₇O₄ (脱水糖)
    │                   │
    │                   ▼
    │               C₅H₈O₄ (去氧糖)
    │                   │
    │                   ▼
    │               HMF (C₆H₆O₃)
    │
    └─→ C₆H₁₁O₅ ─→ LG (C₆H₁₀O₅) + HO·
```

---

## 物种信息

| 化学式 | 名称 | 分子量 | SMILES | 角色 |
|--------|------|--------|--------|------|
| (C₆H₁₀O₅)ₙ | 纤维素 | - | - | 起始物 |
| C₁₂H₂₂O₁₁ | 纤维二糖 | 342.30 | OC[C@H]1OC(O[C@H]2OC(CO)[C@@H](O)[C@H]2O)[C@@H](O)[C@@H]1O | 初级产物 |
| C₆H₁₁O₆ | 葡萄糖基碎片 | 179.15 | - | 中间体 |
| C₆H₁₁O₅ | 葡萄糖基碎片 | 163.15 | - | 中间体 |
| C₆H₁₀O₅ | 左旋葡聚糖 (LG) | 162.14 | C1[C@@H]2[C@H]([C@@H]([C@H]([C@H](O1)O2)O)O)O | 终点产物 |
| HO· | 羟基自由基 | 17.01 | [OH] | 副产物 |
| H· | 氢自由基 | 1.01 | [H] | 副产物 |

---

## 文件说明

| 文件 | 说明 |
|------|------|
| Cellulose_C2_to_HMF_Path.svg | 纯 SVG 路径图 |
| Cellulose_C2_to_HMF_Path_3D.html | HTML 包装的 3D 路径图 |
| Cellulose_C2_to_HMF_Path_3D.pdf | PDF 版本 |
| Cellulose_C2_to_HMF_Path_3D_cropped.pdf | 裁剪后的 PDF |
| gen_pathway.py | 路径图生成脚本 |
| *_bond1.2.png | 各分子的 PNG 渲染图 |

**生成 SVG**:
```python
from smiles_to_3d import smiles_to_svg

# 生成关键分子 SVG
smiles_to_svg("C1[C@@H]2[C@H]([C@@H]([C@H]([C@H](O1)O2)O)O)O", "LG.svg")
```

---

*模拟条件: ReaxFF, 2000K, 5000ps*
*此路径为纤维素热解的基础路径，HMF 由 C5 碎片环化生成*
*输出格式: SVG (PNG 嵌入)*
