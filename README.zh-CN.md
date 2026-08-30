<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — 面向 ChatGPT 的受控参考图像生成" width="100%" />
</p>

<div align="center">

# W-Pack

### 面向 ChatGPT 的 Reference-bounded Image Generation

**自然地使用参考图，同时明确限制每张图的影响范围。**

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **简体中文** · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack 是一个面向 **ChatGPT Web、ChatGPT Projects 和 ChatGPT Skills** 的 chat-native 图像生成与编辑控制层，用于限制参考图像可以影响哪些视觉属性。

普通的多参考图请求很容易产生混杂：风格参考图中的人物、构图、背景或物体可能被模型无意带入结果。W-Pack 为每张参考图赋予一个明确角色：`STYLE`、`CHARACTER`、`POSE`、`COMPOSITION`、`PROPORTION` 或 `ITEM`。

```text
第一张图只参考风格。
第二张图的人物保持不变。
使用第三张图的构图。
在这张图中保留脸和构图，只修改服装。
```

用户无需手写 JSON 或 manifest ID。

## 核心功能

- **自然语言参考控制** — 支持“用这个感觉”“保留这个人物”“使用这个姿势”“按这个构图”等表达。
- **Inline reference** — 当前对话中上传的图片无需 manifest 即可使用。
- **6 种 Authority role** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`。
- **FRESH / EDIT** — 区分新图生成与已有图像编辑。
- **Project source profile** — 可用短指令激活重复使用的参考图组合。
- **Deterministic validation** — 检查权限冲突、重复引用和无效编辑请求。

## 快速开始

1. 将 [`skill/`](./skill) 安装或上传为 ChatGPT Skill。
2. 上传一张或多张参考图。
3. 用自然语言说明每张图应该控制什么。

```text
@W-Pack

第一张图只参考风格。
第二张图的人物保持不变。
使用第三张图的构图生成新图。

背景：日落时分的室内，柔和自然光。
比例：4:5 竖图。
```

无需 API Key、无需本地 CLI、无需独立图像 API。

## Authority model

| Role | 允许控制 | 默认不控制 |
| --- | --- | --- |
| `STYLE` | 色彩、质感、光照语言、渲染、图形处理 | 人物身份、姿势、精确构图、物体身份 |
| `CHARACTER` | 人物身份、面部、发型、稳定外观 | 背景、光照、布局、无关物体 |
| `POSE` | 身体布局、动作、姿态、方向 | 人物身份、服装、环境、风格 |
| `COMPOSITION` | 取景、裁切、机位、位置关系、留白 | 人物身份、服装、物体身份、整体风格 |
| `PROPORTION` | 身体/物体比例、相对尺寸 | 人物身份、细节姿势、风格 |
| `ITEM` | 物体身份、轮廓、关键结构 | 人物身份、环境、整体风格 |

> **看得见，不等于被授权。**

参考图里偶然出现的元素，除非对应 Authority 明确允许，否则不应影响生成结果。

## FRESH 与 EDIT

### `FRESH`
用于生成新图或基于参考图重新生成。不会默认复用之前的生成结果。

### `EDIT`
用于修改已有图像，同时保留指定内容。内部可进一步归类为 `MODIFY`、`RESTYLE` 或 `RECOMPOSE`。

## ChatGPT Project

如果有重复使用的参考图，可以将它们保存在 ChatGPT Project 中，并应用 [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md)。

Project 中存在的图片不会自动成为输入。W-Pack 只选择当前请求需要的最小参考集合。

## 工作流程

```text
自然语言请求
  -> 判断 FRESH / EDIT
  -> 解析参考图与 Authority role
  -> 可选 Source Profile
  -> 校验作用域与冲突
  -> 编译 scene / composition / lighting / text / preserve / avoid
  -> ChatGPT 图像生成
  -> 静默审计
```

单次生成最多使用 5 张参考图，并优先使用最少必要数量。

## 验证

```bash
python3 skill/scripts/self_test.py
```

预期结果：

```text
W-Pack self-test: PASS
```

## 当前状态

当前版本为 `WPACK_v0.3.0-chat-native`，重点包括 Inline reference、自然语言 Authority 解析、`COMPOSITION`、FRESH/EDIT、Project Source Profile 与 deterministic validation。
