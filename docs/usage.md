# Usage Guide

本文档是项目的命令行使用说明。这里采用唯一输入模型：一次生成任务必须同时具备化学反应方程式、分子结构图、模板图。

## 0. 核心原则

不要把输入拆成三种方式。正确理解是：

```text
化学反应方程式 + 分子结构图 + 模板图 = 一个完整输入包
```

三者缺一不可：

- 没有反应方程式，无法知道反应路径和物种关系。
- 没有分子结构图，无法替换模板中的化学内容。
- 没有模板图，无法确定最终图的布局和风格。

README、JSON、asset map、脚本参数只是内部承载格式，不是独立输入方式。

## 1. 环境准备

进入项目目录：

```powershell
cd C:\Users\MECHREVO\reaction-pathway-svg-workflow
```

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

确认主脚本可用：

```powershell
python scripts\generate_all_unified_pathways.py --help
python scripts\validate_unified_svgs.py --help
```

## 2. 标准输入包格式

每条反应路径放在一个独立文件夹中，文件夹名建议以 `Path` 或 `Pass` 结尾：

```text
HMF_Formaldehyde_Path/
  README.md
  template.png
  HMF_S1350_bond1.2.png
  C3H5O2_S3400_bond1.2.png
  C3HO_S3573_bond1.2.png
  CH2O_S596_bond1.2.png
  C2H3O_S2044_bond1.2.png
```

这个文件夹必须同时包含三类输入。

### 2.1 化学反应方程式

当前实现从 `README.md` 中读取反应方程式。`README.md` 里必须有一个包含反应箭头的代码块：

````markdown
## 反应方程式

```text
C₆H₆O₃ (HMF) → C₃H₅O₂ + C₃HO → CH₂O + C₂H₃O
```
````

复杂路径可以继续写详细步骤：

```markdown
1. `C₆H₆O₃ → C₃H₅O₂ + C₃HO`
2. `C₃H₅O₂ → CH₂O + C₂H₃O`
3. `CH₂O + H· → CH₃O`
4. `C₂H₃O + CH₃O → C₃H₆O₂`
```

这些步骤用于明确并行、分支、汇聚等拓扑关系。

### 2.2 分子结构图

方程式中出现的每个物种都必须有对应分子结构图。推荐命名：

```text
<species>_anything.png
```

示例：

| 方程式物种 | 推荐图片文件 |
| --- | --- |
| `HMF` | `HMF_S1350_bond1.2.png` |
| `CH₂O` | `CH2O_S596_bond1.2.png` |
| `C₃H₅O₂` | `C3H5O2_S3400_bond1.2.png` |
| `C₂H₃O` | `C2H3O_S2044_bond1.2.png` |
| `H·` | `H_S3830_bond1.2.png` |

支持的图片格式：

```text
.png .jpg .jpeg .svg .webp
```

最稳定的是 PNG。当前 unified SVG 工作流会把分子 PNG 压缩后内嵌进最终 SVG。

### 2.3 模板图

模板图必须存在。推荐命名：

```text
template.png
```

也可以放在：

```text
template/reference.png
template.svg
template/reference.svg
```

模板图用于定义最终 SVG 的视觉目标：

- 画布比例；
- 主路径方向；
- 分子卡片大小；
- 反应式框大小和位置；
- 箭头粗细、箭头大小、虚线样式；
- title、subtitle、step label、legend 的位置和风格。

当前代码里的 `unified_card_template.py` 和 `hydroxyacetone_convergent.py` 是已经代码化的模板实现。后续接入 SAM/Roboflow 时，模板图应先被分割成卡片、箭头、文本框、legend 等模板元素，再生成可编辑 SVG。

## 3. 主生成命令

主脚本：

```text
scripts/generate_all_unified_pathways.py
```

生成项目自带示例：

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

生成本地 OpenClaw/ReacNet 数据：

```powershell
python scripts\generate_all_unified_pathways.py --root D:\data\openclaw_reacnet
```

只生成一条路径：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Formaldehyde_Path
```

只生成多条指定路径：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Formaldehyde_Path `
  --only HMF_Hydroxyacetone_like_Path
```

改输出目录名：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --output-subdir svg_output
```

参数说明：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--root` | `examples/openclaw_reacnet` | 包含多个完整输入包的根目录 |
| `--only` | 空 | 只生成指定路径文件夹，可重复 |
| `--output-subdir` | `unified_svg` | 输出子目录名 |
| `--generic-only` | false | 开发调试用，禁用专用模板 |

输出：

```text
<PathFolder>/unified_svg/
  generated_spec.json
  pathway_unified.svg
```

## 4. 验证命令

生成后运行：

```powershell
python scripts\validate_unified_svgs.py --root examples\openclaw_reacnet
```

验证本地数据：

```powershell
python scripts\validate_unified_svgs.py --root D:\data\openclaw_reacnet
```

验证内容：

- SVG 能被 XML parser 正常解析；
- SVG 有明确 `width` 和 `height`；
- 至少包含一个内嵌 `data:image/png;base64` 图片；
- 没有外链图片；
- 没有 SVG `filter=`。

示例输出：

```text
OK examples\openclaw_reacnet\HMF_Formaldehyde_Path\unified_svg\pathway_unified.svg canvas=1456x1024 embedded_png=5 external_assets=0 filters=0
OK examples\openclaw_reacnet\HMF_Hydroxyacetone_like_Path\unified_svg\pathway_unified.svg canvas=2400x1600 embedded_png=8 external_assets=0 filters=0
```

## 5. 模板选择和画布规则

当前有两类模板实现：

```text
reaction_pathway/unified_card_template.py
reaction_pathway/hydroxyacetone_convergent.py
```

`unified_card_template.py` 用于普通线性路径。

`hydroxyacetone_convergent.py` 用于 `HMF_Hydroxyacetone_like_Path`，因为它有四步、并行输入和汇聚重组，需要更大画布。

规则：

- 两步或三步线性路径可以使用通用模板。
- 多步、并行、汇聚路径应使用大画布或专用模板。
- 不要为了塞进固定画布而把箭头画得过小。
- 模板图如果显示空间更宽，SVG 画布也应相应扩大。

## 6. 内部工具说明

仓库里仍然保留了一些早期脚本：

```text
scripts/stitch_reaction_pathway.py
scripts/stitch_path_readme.py
scripts/generate_reaction_pathway.py
reaction_pathway/from_assets.py
reaction_pathway/from_readme.py
reaction_pathway/cli.py
```

这些脚本不是用户工作流里的“其他输入方式”。它们只是内部工具：

- 用于调试某个阶段；
- 用于兼容早期实验；
- 用于未来前端把完整输入包转换成结构化 spec。

产品说明只保留下面这一种表述：

```text
唯一输入方式：反应方程式 + 分子结构图 + 模板图。
README、asset map、JSON spec 都只是这个完整输入包的内部表示。
```

## 7. SAM/Roboflow 模板分割

如果输入模板图是 PNG，后续可以用 SAM/Roboflow 做模板元素分割：

```powershell
python -m reaction_pathway.sam_roboflow `
  --image <template.png> `
  --output-dir <输出目录> `
  --prompts "molecular node,reaction equation box,step label,legend,arrow,text box"
```

输出可作为模板元素库：

```text
outputs/template_segmentation/
  samed_roboflow.png
  boxlib_roboflow.json
  roboflow_raw.json
  icons/
```

这个步骤的定位是“模板图解析”，不是独立输入方式。它服务于同一个完整输入包。

## 8. 推荐日常流程

第一步：准备完整输入包。

```text
D:\data\openclaw_reacnet\
  HMF_Formaldehyde_Path\
    README.md
    template.png
    HMF_S1350_bond1.2.png
    C3H5O2_S3400_bond1.2.png
    C3HO_S3573_bond1.2.png
    CH2O_S596_bond1.2.png
    C2H3O_S2044_bond1.2.png
```

第二步：生成。

```powershell
python scripts\generate_all_unified_pathways.py --root D:\data\openclaw_reacnet
```

第三步：验证。

```powershell
python scripts\validate_unified_svgs.py --root D:\data\openclaw_reacnet
```

第四步：打开 SVG。

```text
D:\data\openclaw_reacnet\<PathFolder>\unified_svg\pathway_unified.svg
```

## 9. 前端包装建议

前端不要设计成三个入口。应设计成一个上传任务：

```text
上传完整输入包
  ├─ 反应方程式
  ├─ 分子结构图
  └─ 模板图
```

推荐请求结构：

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

如果前端直接传 JSON，也必须包含三类字段：

```json
{
  "equation": "...",
  "molecules": [
    {"id": "HMF", "asset_path": "..."}
  ],
  "template": {
    "image": "template.png",
    "layout_data": "optional parsed template boxes"
  }
}
```

这仍然是同一个输入方式，只是换了数据承载格式。

## 10. 常见错误

### 缺少反应方程式

错误：

```text
README.md not found
Could not find a fenced reaction equation
```

处理：补齐 `README.md` 或等价的结构化 `equation` 字段。

### 缺少分子结构图

错误：

```text
No matching molecule image for species: CH2O
```

处理：补齐对应图片，或通过 asset map 明确指定物种和图片路径。

### 缺少模板图

应视为输入不完整。处理：补齐 `template.png`、`template.svg` 或已解析好的 template layout data。

### SVG 在 Inkscape 里图片丢失

运行：

```powershell
python scripts\validate_unified_svgs.py --root <root>
```

确认：

```text
external_assets=0
embedded_png > 0
filters=0
```

### 路径步骤多，图太挤

不要把内容压进固定画布。应根据模板图扩大画布，或者新增专用模板。`HMF_Hydroxyacetone_like_Path` 已经使用 `2400 x 1600`。

## 11. 命令清单

主流程：

```powershell
python scripts\generate_all_unified_pathways.py --help
python scripts\validate_unified_svgs.py --help
```

模板解析：

```powershell
python -m reaction_pathway.sam_roboflow --help
```

内部调试工具：

```powershell
python scripts\stitch_reaction_pathway.py --help
python scripts\stitch_path_readme.py --help
python scripts\generate_reaction_pathway.py --help
python -m reaction_pathway.unified_card_template --help
python -m reaction_pathway.hydroxyacetone_convergent --help
```
