# HMF → 乙醇醛 (Glycolaldehyde-like) 反应路径

本目录包含 HMF 降解生成乙醇醛类产物的反应路径图及相关分子 3D 渲染图。

---

## 工作流程

```
SMILES → SDF → PNG → SVG (单分子)
                      ↓
              路径图 SVG 组装
```

---

## 反应方程式

### 主反应链

```
C₆H₆O₃ (HMF) → C₃H₅O₂ + C₃HO → C₂H₃O + CH₂O → C₂H₄O₂ + HO·
```

**详细步骤:**

1. **HMF 脱羰裂解**  
   `C₆H₆O₃ → C₃H₅O₂ + C₃HO`  
   HMF 的呋喃环断裂，生成丙酮醛类碎片和 C₃HO 自由基

2. **甲醛脱离**  
   `C₃H₅O₂ → C₂H₃O + CH₂O`  
   甲醛从主链脱离（不进入后续反应）

3. **羟基结合**  
   `C₂H₃O + HO· → C₂H₄O₂`  
   乙烯酮自由基捕获羟基自由基，生成乙醇醛类产物

---

## 物种信息

| 化学式 | 名称 | 分子量 | SMILES | 角色 |
|--------|------|--------|--------|------|
| C₆H₆O₃ | 5-羟甲基糠醛 (HMF) | 126.11 | OCc1ccc(C=O)o1 | 起始物 |
| C₃H₅O₂ | 丙酮醛类碎片 | 73.06 | - | 中间体 |
| C₃HO | C₃HO 自由基 | 53.03 | [CH]=C1[C]O1 | 副产物 |
| C₂H₃O | 乙烯酮自由基 | 43.02 | - | 中间体 |
| CH₂O | 甲醛 | 30.03 | C=O | 脱离产物 |
| HO· | 羟基自由基 | 17.01 | [OH] | 反应物 |
| C₂H₄O₂ | 乙醇醛类 | 60.05 | OCC=O | 终点产物 |

---

## 文件说明

| 文件 | 说明 |
|------|------|
| Glycolaldehyde_like_Path.svg | 纯 SVG 路径图 |
| Glycolaldehyde_like_Path.pdf | PDF 版本 |
| Glycolaldehyde_like_Path_3D.html | HTML 包装的 3D 路径图 |
| *_bond1.2.png | 各分子的 PNG 渲染图 |

**生成 SVG**:
```python
from smiles_to_3d import smiles_to_svg

smiles_to_svg("OCc1ccc(C=O)o1", "HMF.svg")
smiles_to_svg("OCC=O", "Glycolaldehyde.svg")
```

---

*路径特点: 甲醛脱离主链，HO· 从外部捕获*
*模拟条件: ReaxFF, 2000K, 5000ps*
*输出格式: SVG (PNG 嵌入)*
