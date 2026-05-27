# HMF → 羟基丙酮 (Hydroxyacetone-like) 反应路径

本目录包含 HMF 降解生成羟基丙酮类产物的反应路径图及相关分子 3D 渲染图。

---

## 工作流程

```
SMILES → SDF → PNG → SVG (单分子)
                      ↓
              路径图 SVG 组装
```

---

## 反应方程式

### 主反应链 (汇聚拓扑)

```
C₆H₆O₃ (HMF) → C₃H₅O₂ + C₃HO → CH₂O → CH₃O + H· → C₃H₆O₂
```

**详细步骤:**

1. **HMF 脱羰裂解**  
   `C₆H₆O₃ → C₃H₅O₂ + C₃HO`  
   HMF 的呋喃环断裂

2. **甲醛生成**  
   `C₃H₅O₂ → CH₂O + C₂H₃O`  
   生成甲醛和乙烯酮自由基

3. **甲氧基自由基生成** ⚠️ 并行反应  
   `CH₂O + H· → CH₃O`  
   甲醛捕获氢自由基

4. **汇聚重组**  
   `C₂H₃O + CH₃O → C₃H₆O₂`  
   乙烯酮自由基与甲氧基自由基结合

---

## 拓扑说明

⚠️ **汇聚拓扑 (Convergent Topology)**

此路径涉及两条并行反应的汇聚：
- 路径 A: CH₂O → CH₃O (甲醛 + H·)
- 路径 B: C₃H₅O₂ → C₂H₃O
- 汇聚: C₂H₃O + CH₃O → C₃H₆O₂

CH₃O 并非直接来自 HMF 主链的线性分解。

---

## 物种信息

| 化学式 | 名称 | 分子量 | SMILES | 角色 |
|--------|------|--------|--------|------|
| C₆H₆O₃ | 5-羟甲基糠醛 (HMF) | 126.11 | OCc1ccc(C=O)o1 | 起始物 |
| C₃H₅O₂ | 丙酮醛类碎片 | 73.06 | - | 中间体 |
| CH₂O | 甲醛 | 30.03 | C=O | 中间体 |
| H· | 氢自由基 | 1.01 | [H] | 反应物 |
| CH₃O | 甲氧基自由基 | 31.03 | [CH3]O | 中间体 |
| C₂H₃O | 乙烯酮自由基 | 43.02 | - | 中间体 |
| C₃H₆O₂ | 羟基丙酮类 | 74.08 | CC(=O)CO | 终点产物 |

---

## 文件说明

| 文件 | 说明 |
|------|------|
| Hydroxyacetone_like_Path.svg | 纯 SVG 路径图 |
| Hydroxyacetone_like_Path.pdf | PDF 版本 |
| Hydroxyacetone_like_Path_3D.html | HTML 包装的 3D 路径图 |
| *_bond1.2.png | 各分子的 PNG 渲染图 |

**生成 SVG**:
```python
from smiles_to_3d import smiles_to_svg

smiles_to_svg("OCc1ccc(C=O)o1", "HMF.svg")
smiles_to_svg("CC(=O)CO", "Hydroxyacetone.svg")
smiles_to_svg("[CH3]O", "CH3O.svg")
```

---

*模拟条件: ReaxFF, 2000K, 5000ps*
*输出格式: SVG (PNG 嵌入)*
