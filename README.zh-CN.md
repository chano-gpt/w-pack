# W-Pack

### 面向 ChatGPT 的参考图控制型图像生成 Harness

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **简体中文** · [繁體中文](./README.zh-TW.md)

W-Pack v0.5.1 将参考图的 **authority（允许控制什么）** 与 **transport（是否真的作为视觉输入传给图像模型）** 分开处理。

## v0.5.1

- Project 中存在文件不再等同于 `VISUAL_BOUND`。
- STYLE 解析为 1 个 `STYLE_CORE` + 最多 2 个 `STYLE_SUPPORT`。
- 直接视觉绑定无法确认时，可使用 `style_signature` / `anti_drift_signature` 形式的 STYLE DNA。
- 头发新增独立的高权重风格轴 `hair_rendering_grammar`。
- 默认 `CLEAN_MASS` 抑制密集碎发光环、反复分叉的发梢、随机穿过面部的细发以及线状单发高光。
- 只有“结构通过、风格失败”时才允许执行一次 `SINGLE_RESTYLE`。

## STYLE family

`STYLE_CORE` 控制全局媒介、写实度、形状抽象、边缘、明暗、颜色、表面、背景以及可见头发的渲染语法。`STYLE_SUPPORT` 只能作用于声明的 support domain，不能覆盖 CORE 的媒介、写实度或形状抽象。

## Hair rendering

默认顺序：

```text
silhouette → major grouped locks → internal texture → sparse micro-strands
```

如果权威参考图明确包含卷曲、毛躁、湿发、风吹或大量独立发丝，则以参考图为准。

## Recovery

自动恢复要求：结构 PASS、风格 FAIL、恰好一个 STYLE_CORE，并且 STYLE_CORE 已 `VISUAL_BOUND` 或具有可用 STYLE DNA。

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

禁止递归 restyle 和自动第三次生成。

详细说明：[`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

当前版本：**`WPACK_v0.5.1-chat-native`**
