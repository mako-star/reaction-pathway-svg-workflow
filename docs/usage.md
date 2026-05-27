# Usage Guide

本文档是这个项目的命令行使用手册，目标是让你后期可以直接把这些脚本包进一个前端上传流程里。

当前核心工作流是：

```text
Path/Pass 文件夹
  README.md 里的反应方程式
  分子结构 PNG 图
        |
        v
generated_spec.json
        |
        v
pathway_unified.svg
```

生成结果是单文件 SVG：分子 PNG 会被压缩后内嵌进 SVG，不依赖外部图片路径，适合 Inkscape 打开和继续编辑。

## 1. 环境准备

进入项目目录：

```powershell
cd C:\Users\MECHREVO\reaction-pathway-svg-workflow
```

可选：创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

确认脚本能正常显示帮助：

```powershell
python scripts\generate_all_unified_pathways.py --help
python scripts\validate_unified_svgs.py --help
```

## 2. 输入文件夹格式

每条反应路径放在一个单独文件夹里，文件夹名建议以 `Path` 或 `Pass` 结尾。批量脚本只会扫描这两类后缀。

```text
HMF_Formaldehyde_Path/
  README.md
  HMF_S1350_bond1.2.png
  C3H5O2_S3400_bond1.2.png
  C3HO_S3573_bond1.2.png
  CH2O_S596_bond1.2.png
  C2H3O_S2044_bond1.2.png
```

`README.md` 里需要有一个包含反应箭头的代码块。脚本会提取第一个包含 `→`、`->` 或 `=>` 的代码块。

推荐写法：

````markdown
## 反应方程式

```text
C₆H₆O₃ (HMF) → C₃H₅O₂ + C₃HO → CH₂O + C₂H₃O
```
````

更复杂的路径可以在说明部分写详细步骤：

```markdown
1. `C₆H₆O₃ → C₃H₅O₂ + C₃HO`
2. `C₃H₅O₂ → CH₂O + C₂H₃O`
```

注意：当前通用脚本主要根据主反应链代码块自动生成布局。复杂汇聚拓扑需要专门模板，例如 `HMF_Hydroxyacetone_like_Path`。

## 3. 分子图片命名规则

脚本会把方程式里的物种名规范化后，与图片文件名匹配。

常见匹配例子：

| 方程式物种 | 可匹配文件名 |
| --- | --- |
| `HMF` | `HMF_S1350_bond1.2.png` |
| `CH₂O` | `CH2O_S596_bond1.2.png` |
| `C₃H₅O₂` | `C3H5O2_S3400_bond1.2.png` |
| `HO·` | `HO_S3832_bond1.2.png` |
| `H·` | `H_S3830_bond1.2.png` |

支持的图片扩展名：

```text
.png .jpg .jpeg .svg .webp
```

最稳定的命名方式是：

```text
<species>_anything.png
```

例如：

```text
C3H6O2_S2140_bond1.2.png
CH3O_S3359_bond1.2.png
```

## 4. 最常用脚本：批量生成 SVG

脚本：

```text
scripts/generate_all_unified_pathways.py
```

命令格式：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root <包含多个 Path/Pass 文件夹的根目录> `
  [--only <只生成某个文件夹名>] `
  [--output-subdir <输出子目录名>] `
  [--generic-only]
```

参数说明：

| 参数 | 是否必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--root` | 否 | `examples/openclaw_reacnet` | 包含多个 `*Path` / `*Pass` 文件夹的根目录 |
| `--only` | 否 | 空 | 只生成指定文件夹；可以重复传多次 |
| `--output-subdir` | 否 | `unified_svg` | 每个路径文件夹内的输出目录名 |
| `--generic-only` | 否 | false | 强制所有路径都用通用模板，不启用自定义模板 |

生成项目自带示例：

```powershell
python scripts\generate_all_unified_pathways.py --root examples\openclaw_reacnet
```

生成你本地 OpenClaw/ReacNet 数据：

```powershell
python scripts\generate_all_unified_pathways.py --root D:\data\openclaw_reacnet
```

只生成一条路径：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Formaldehyde_Path
```

只生成两条路径：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Formaldehyde_Path `
  --only HMF_Hydroxyacetone_like_Path
```

改输出目录名，例如输出到 `svg_output`：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --output-subdir svg_output
```

默认输出：

```text
<PathFolder>/unified_svg/
  generated_spec.json
  pathway_unified.svg
```

其中：

- `pathway_unified.svg` 是最终可编辑 SVG。
- `generated_spec.json` 是从 README 和图片资产解析出来的结构化中间文件。

## 5. 生成单个通用 Path 文件夹

如果你不想扫描整个根目录，可以直接调用通用模板模块：

```powershell
python -m reaction_pathway.unified_card_template <PathFolder> `
  --output-dir <输出目录> `
  --svg-name pathway_unified.svg
```

例子：

```powershell
python -m reaction_pathway.unified_card_template `
  D:\data\openclaw_reacnet\HMF_Formaldehyde_Path `
  --output-dir D:\data\openclaw_reacnet\HMF_Formaldehyde_Path\unified_svg `
  --svg-name pathway_unified.svg
```

适用场景：

- 两步或三步线性路径；
- 有副产物分支，但没有复杂汇聚；
- 想快速从 `README.md + PNG` 得到统一风格 SVG。

## 6. 生成羟基丙酮汇聚路径专用 SVG

`HMF_Hydroxyacetone_like_Path` 是四步并行汇聚反应，通用小画布会挤。因此项目里有专用模板：

```text
reaction_pathway/hydroxyacetone_convergent.py
```

命令格式：

```powershell
python -m reaction_pathway.hydroxyacetone_convergent `
  --path-dir <HMF_Hydroxyacetone_like_Path 文件夹> `
  --output-dir <输出目录>
```

例子：

```powershell
python -m reaction_pathway.hydroxyacetone_convergent `
  --path-dir D:\data\openclaw_reacnet\HMF_Hydroxyacetone_like_Path `
  --output-dir D:\data\openclaw_reacnet\HMF_Hydroxyacetone_like_Path\unified_svg
```

这个模板的输出特点：

- 画布为 `2400 x 1600`；
- 主链是 `HMF -> C3H5O2 -> CH2O -> CH3O -> C3H6O2`；
- `C3HO` 和 `C2H3O` 作为侧支；
- `C2H3O` 通过虚线汇聚到最终产物；
- 右侧 legend 独立，不压住反应路径。

批量脚本默认会自动识别 `HMF_Hydroxyacetone_like_Path` 并调用这个专用模板。如果你不想用专用模板，可以加：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root D:\data\openclaw_reacnet `
  --only HMF_Hydroxyacetone_like_Path `
  --generic-only
```

## 7. 验证生成的 SVG

脚本：

```text
scripts/validate_unified_svgs.py
```

命令格式：

```powershell
python scripts\validate_unified_svgs.py `
  --root <包含多个 Path/Pass 文件夹的根目录> `
  [--svg-name pathway_unified.svg]
```

验证项目自带示例：

```powershell
python scripts\validate_unified_svgs.py --root examples\openclaw_reacnet
```

验证你本地数据：

```powershell
python scripts\validate_unified_svgs.py --root D:\data\openclaw_reacnet
```

验证另一个输出文件名：

```powershell
python scripts\validate_unified_svgs.py `
  --root D:\data\openclaw_reacnet `
  --svg-name pathway.svg
```

验证内容：

- SVG 能被 XML parser 正常解析；
- SVG 有明确 `width` 和 `height`；
- 至少包含一个内嵌 `data:image/png;base64` 图片；
- 没有外链图片；
- 没有 SVG `filter=`。

正常输出类似：

```text
OK examples\openclaw_reacnet\HMF_Formaldehyde_Path\unified_svg\pathway_unified.svg canvas=1456x1024 embedded_png=5 external_assets=0 filters=0
OK examples\openclaw_reacnet\HMF_Hydroxyacetone_like_Path\unified_svg\pathway_unified.svg canvas=2400x1600 embedded_png=8 external_assets=0 filters=0
```

## 8. 从“方程式 + 现成分子图片目录”直接生成

如果你没有标准 `README.md` 文件夹，只是手里有一个分子图片目录，可以用：

```text
scripts/stitch_reaction_pathway.py
```

它是 `python -m reaction_pathway.from_assets` 的薄包装。

命令格式：

```powershell
python scripts\stitch_reaction_pathway.py `
  --equation "<反应方程式>" `
  --asset-dir <分子图片目录> `
  --output-dir <输出目录> `
  [--title <图标题>] `
  [--svg-name pathway.svg] `
  [--width 1400] `
  [--height 620] `
  [--asset-map <JSON 映射文件>]
```

例子：

```powershell
python scripts\stitch_reaction_pathway.py `
  --equation "HMF -> C3H5O2 + C3HO -> CH2O + C2H3O" `
  --asset-dir D:\data\openclaw_reacnet\HMF_Formaldehyde_Path `
  --output-dir outputs\hmf_formaldehyde_from_assets `
  --title "HMF Formaldehyde Path"
```

输出：

```text
outputs/hmf_formaldehyde_from_assets/
  generated_spec.json
  manifest.json
  pathway.svg
  molecules/
```

如果文件名和物种名对不上，使用 `--asset-map`。

`asset_map.json` 例子：

```json
{
  "HMF": "D:/data/openclaw_reacnet/HMF_Formaldehyde_Path/HMF_S1350_bond1.2.png",
  "C3H5O2": "D:/data/openclaw_reacnet/HMF_Formaldehyde_Path/C3H5O2_S3400_bond1.2.png",
  "C3HO": "D:/data/openclaw_reacnet/HMF_Formaldehyde_Path/C3HO_S3573_bond1.2.png",
  "CH2O": "D:/data/openclaw_reacnet/HMF_Formaldehyde_Path/CH2O_S596_bond1.2.png",
  "C2H3O": "D:/data/openclaw_reacnet/HMF_Formaldehyde_Path/C2H3O_S2044_bond1.2.png"
}
```

运行：

```powershell
python scripts\stitch_reaction_pathway.py `
  --equation "HMF -> C3H5O2 + C3HO -> CH2O + C2H3O" `
  --asset-dir D:\data\openclaw_reacnet\HMF_Formaldehyde_Path `
  --asset-map D:\data\openclaw_reacnet\HMF_Formaldehyde_Path\asset_map.json `
  --output-dir outputs\hmf_formaldehyde_from_assets
```

## 9. 从 README 单文件夹生成旧版 pathway.svg

脚本：

```text
scripts/stitch_path_readme.py
```

它会从一个 Path 文件夹读取 README，并输出旧版 `pathway.svg`。现在推荐优先使用 `generate_all_unified_pathways.py` 或 `reaction_pathway.unified_card_template`，但这个脚本保留给早期流程兼容。

命令格式：

```powershell
python scripts\stitch_path_readme.py <PathFolder> `
  --output-dir <输出目录> `
  [--title <标题>] `
  [--width 1400] `
  [--height 620]
```

例子：

```powershell
python scripts\stitch_path_readme.py `
  D:\data\openclaw_reacnet\HMF_Formaldehyde_Path `
  --output-dir outputs\hmf_from_readme
```

输出：

```text
outputs/hmf_from_readme/
  generated_spec.json
  manifest.json
  pathway.svg
  molecules/
```

## 10. 从 JSON spec 生成 SVG

脚本：

```text
scripts/generate_reaction_pathway.py
```

它是 `python -m reaction_pathway.cli` 的薄包装，适合未来前端直接提交结构化 JSON，而不是 README。

命令格式：

```powershell
python scripts\generate_reaction_pathway.py <spec.json> `
  --output-dir <输出目录> `
  [--backend auto|smiles-to-3d|placeholder] `
  [--svg-name pathway.svg]
```

用项目自带 spec 生成：

```powershell
python scripts\generate_reaction_pathway.py `
  examples\reaction_pathway_hmf.json `
  --output-dir outputs\hmf_spec_demo `
  --backend placeholder
```

输出：

```text
outputs/hmf_spec_demo/
  manifest.json
  pathway.svg
  molecules/
```

`--backend` 说明：

| backend | 说明 |
| --- | --- |
| `placeholder` | 不调用真实分子渲染，只生成占位分子图，适合测试布局 |
| `smiles-to-3d` | 尝试调用本地 `smiles-to-3d` 工作流 |
| `auto` | 优先真实渲染，不可用时回退 |

当前主工作流已经假设你有现成 PNG，所以一般不需要这个入口。

## 11. 可选：Roboflow/SAM 分割参考图

脚本：

```text
reaction_pathway/sam_roboflow.py
```

用途：当你手里只有一张参考 PNG，希望先分割出图里的节点、箭头、legend、方程框等区域时，可以用这个脚本生成 box library。当前 SVG 生成流程不依赖它。

先设置 API key：

```powershell
$env:ROBOFLOW_API_KEY="你的 Roboflow API key"
```

命令格式：

```powershell
python -m reaction_pathway.sam_roboflow `
  --image <参考图 PNG> `
  --output-dir <输出目录> `
  [--prompts "molecular node,reaction equation box,legend,arrow"] `
  [--min-score 0.0] `
  [--min-area 900] `
  [--merge-threshold 0.65]
```

例子：

```powershell
python -m reaction_pathway.sam_roboflow `
  --image "C:\Users\MECHREVO\Downloads\template.png" `
  --output-dir outputs\template_segmentation `
  --prompts "molecular node,reaction equation box,step label,legend,arrow,text box"
```

输出：

```text
outputs/template_segmentation/
  samed_roboflow.png
  boxlib_roboflow.json
  roboflow_raw.json
  icons/
```

## 12. 推荐的日常工作顺序

第一步：准备每条路径的文件夹。

```text
D:\data\openclaw_reacnet\
  HMF_Formaldehyde_Path\
    README.md
    HMF_S1350_bond1.2.png
    ...
  HMF_Hydroxyacetone_like_Path\
    README.md
    HMF_S1350_bond1.2.png
    ...
```

第二步：批量生成。

```powershell
python scripts\generate_all_unified_pathways.py --root D:\data\openclaw_reacnet
```

第三步：验证。

```powershell
python scripts\validate_unified_svgs.py --root D:\data\openclaw_reacnet
```

第四步：用 Inkscape 打开目标文件。

```text
D:\data\openclaw_reacnet\<PathFolder>\unified_svg\pathway_unified.svg
```

## 13. 前端包装建议

后期做前端时，建议接口按这个结构设计：

上传内容：

```text
root/
  Some_Path/
    README.md
    *.png
```

后端执行：

```powershell
python scripts\generate_all_unified_pathways.py `
  --root <上传解压后的 root> `
  --only <用户选择的 Path 文件夹名>
```

后端返回：

```json
{
  "svg": "<PathFolder>/unified_svg/pathway_unified.svg",
  "spec": "<PathFolder>/unified_svg/generated_spec.json"
}
```

如果前端直接提交结构化数据，可以跳过 README 解析，生成 JSON spec 后走：

```powershell
python scripts\generate_reaction_pathway.py <spec.json> --output-dir <output>
```

## 14. 常见问题

### 找不到 README.md

报错类似：

```text
README.md not found
```

检查目标路径是不是直接指向某个 Path 文件夹，或者 `--root` 下是否真的有 `*Path` / `*Pass` 子文件夹。

### 找不到分子图片

报错类似：

```text
No matching molecule image for species: CH2O
```

检查图片名是否能对应物种名。例如 `CH₂O` 最好命名为：

```text
CH2O_S596_bond1.2.png
```

如果命名无法统一，用 `scripts/stitch_reaction_pathway.py --asset-map` 手动指定。

### SVG 在 Inkscape 里图片丢失

运行验证：

```powershell
python scripts\validate_unified_svgs.py --root <root>
```

确认：

```text
external_assets=0
embedded_png > 0
filters=0
```

如果 `external_assets` 不是 0，说明 SVG 里还有外链图片路径，需要重新用本项目的 unified 工作流生成。

### 反应步骤太多，图显得挤

这种情况不要强行用小画布。当前 `HMF_Hydroxyacetone_like_Path` 已经使用 `2400 x 1600` 专用模板。后续如果有新的四步、五步、汇聚或并行路径，建议新增一个专用模板，或者扩展通用模板的画布自动缩放规则。

### 想看所有命令参数

每个脚本都支持 `--help`：

```powershell
python scripts\generate_all_unified_pathways.py --help
python scripts\validate_unified_svgs.py --help
python scripts\stitch_reaction_pathway.py --help
python scripts\stitch_path_readme.py --help
python scripts\generate_reaction_pathway.py --help
python -m reaction_pathway.unified_card_template --help
python -m reaction_pathway.hydroxyacetone_convergent --help
python -m reaction_pathway.sam_roboflow --help
```
