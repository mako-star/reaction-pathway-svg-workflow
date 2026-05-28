# Reaction Pathway SVG Workflow

本文档定义项目的真实工作流边界。这里不再把输入拆成多种模式；本项目只有一种有效输入方式。

## 1. 唯一输入方式

一次反应路径 SVG 生成任务必须同时具备三个输入：

```text
化学反应方程式
分子结构图
模板图
```

这三个输入不是可选项，也不是三种入口。它们共同构成一个完整任务：

- 化学反应方程式：定义物种、反应顺序、主链、副产物、并行或汇聚关系。
- 分子结构图：提供每个物种真实可视化内容，不能用占位图代替最终输出。
- 模板图：定义最终图的视觉框架、构图方式、字号层级、配色、箭头风格、legend 位置等。

只有三者同时存在，才进入后续解析、匹配、布局和 SVG 生成流程。缺少任何一个输入时，任务应停止并返回明确错误，而不是降级成另一种生成方式。

## 2. 输入包目录

推荐每条反应路径使用一个独立目录：

```text
My_Reaction_Path/
  README.md
  template.png
  HMF_S1350_bond1.2.png
  C3H5O2_S3400_bond1.2.png
  C3HO_S3573_bond1.2.png
  CH2O_S596_bond1.2.png
  C2H3O_S2044_bond1.2.png
```

### 2.1 反应方程式

`README.md` 中必须包含一个带反应箭头的代码块：

````markdown
## 反应方程式

```text
C₆H₆O₃ (HMF) → C₃H₅O₂ + C₃HO → CH₂O + C₂H₃O
```
````

如果路径包含并行、汇聚或多步反应，可以继续在 README 中写结构化步骤说明，但核心方程式仍然必须存在。

### 2.2 分子结构图

每个方程式物种都必须能匹配到一张分子结构图。推荐命名：

```text
<species>_anything.png
```

例如：

```text
HMF_S1350_bond1.2.png
CH2O_S596_bond1.2.png
C3H6O2_S2140_bond1.2.png
```

脚本会把 `CH₂O`、`CH2O`、`CH2O_S596_bond1.2.png` 这类写法归一化后匹配。命名无法自动匹配时，后续应通过显式映射表解决，但这仍然属于同一个完整输入包，不是新的输入模式。

### 2.3 模板图

模板图必须随输入包一起提供。推荐文件名：

```text
template.png
```

也可以使用：

```text
template.svg
template/reference.png
template/reference.svg
```

模板图的职责是提供视觉目标，而不是提供化学信息。模板图应决定：

- 主路径是横向、纵向还是汇聚布局；
- 分子卡片形态和大小；
- 反应方程式框位置；
- 箭头粗细、曲率和虚线风格；
- step label、title、subtitle、legend 的风格；
- 画布比例和留白。

当前仓库中的 `unified_card_template.py` 和 `hydroxyacetone_convergent.py` 是代码化模板实现。后续如果接入 SAM/Roboflow 分割，模板图应先被解析成模板元素库，再驱动 SVG 布局。

## 3. 总体流程

```text
完整输入包
  ├─ README.md / reaction.md: 化学反应方程式
  ├─ molecule images: 分子结构图
  └─ template image: 模板图
        |
        v
输入校验
  ├─ 方程式是否存在
  ├─ 每个物种是否有分子图
  └─ 模板图是否存在
        |
        v
结构化解析
  ├─ species
  ├─ reaction edges
  ├─ main chain / side products
  └─ template/layout target
        |
        v
SVG 生成
  ├─ 嵌入分子图
  ├─ 套用模板布局
  ├─ 绘制箭头、方程框、legend
  └─ 输出 standalone editable SVG
```

## 4. 输出

每个路径目录生成：

```text
My_Reaction_Path/
  unified_svg/
    generated_spec.json
    pathway_unified.svg
```

`pathway_unified.svg` 是最终交付物。它必须满足：

- 单文件可打开；
- 分子图内嵌；
- 无外链图片；
- 无 fragile SVG filter；
- 主要元素有稳定 group id，方便 Inkscape/Figma/前端继续编辑。

`generated_spec.json` 是中间结构化记录，用于复现、调试和后续前端编辑。

## 5. 现有脚本在工作流中的位置

现有脚本分为两类：主流程脚本和内部工具脚本。

主流程脚本：

```text
scripts/generate_all_unified_pathways.py
scripts/validate_unified_svgs.py
```

它们应该面向完整输入包运行。

内部工具脚本：

```text
scripts/stitch_reaction_pathway.py
scripts/stitch_path_readme.py
scripts/generate_reaction_pathway.py
reaction_pathway/from_assets.py
reaction_pathway/from_readme.py
reaction_pathway/cli.py
```

这些脚本只用于开发、调试或兼容早期实现。不要把它们描述成用户可选择的独立输入方式。正确表述是：

```text
唯一输入方式：反应方程式 + 分子结构图 + 模板图。
README、asset map、JSON spec 只是这个输入包在不同实现阶段的内部承载格式。
```

## 6. 模板图与专用模板

通用模板适合线性、少步骤反应。复杂路径必须扩大画布或使用专用模板。

例如 `HMF_Hydroxyacetone_like_Path`：

- 反应有四步；
- 存在并行输入；
- `C₂H₃O` 分支后又与 `CH₃O` 汇聚；
- 因此使用 `2400 x 1600` 的专用汇聚布局。

规则很直接：如果模板图显示路径较长、分支较多或汇聚关系复杂，就应优先扩大画布，而不是压缩箭头和卡片。

## 7. 前端集成原则

前端上传时不要拆成多个入口。接口应要求一次提交完整输入包：

```text
upload/
  Some_Path/
    README.md
    template.png
    *.png
```

后端执行：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root <uploaded-root> `
  --only <folder-name>
```

后端返回：

```json
{
  "svg": "<PathFolder>/unified_svg/pathway_unified.svg",
  "spec": "<PathFolder>/unified_svg/generated_spec.json"
}
```

如果后续前端直接提交 JSON，也必须包含三类信息：

- equation；
- molecule image references；
- template reference 或 template layout data。

JSON 只是承载格式，不是新的输入方式。

## 8. 错误处理

生成前必须检查：

- 没有反应方程式：停止。
- 方程式中某个物种没有分子结构图：停止。
- 没有模板图或模板布局数据：停止。
- 模板图无法解析且没有 fallback 模板：停止。
- SVG 生成后存在外链图片：失败。
- SVG 生成后分子图没有内嵌：失败。

这些错误不应该被静默降级。否则生成出来的图和用户给定的模板/化学输入不一致，后续编辑会失控。
