# W-Pack

### 面向 ChatGPT 的 Project-source-first 图像生成控制层

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **简体中文** · [繁體中文](./README.zh-TW.md)

W-Pack v0.4 默认使用 ChatGPT Project 中的持久参考图，并通过受限的 authority 角色控制风格、人物、姿势、构图、比例和物体的影响范围。

## v0.4 核心变化

- 自动启用 Project `DEFAULT` 源
- 将唯一的 STYLE 参考内部提升为 `STYLE_CORE`
- 强化媒介、写实程度、轮廓、抽象方式、明暗、色彩、纹理和背景渲染的一致性
- 首先只进行一次 FRESH 生成
- 仅当“结构通过、风格失败”时执行一次 `SINGLE_RESTYLE`
- 禁止递归 restyle，也不会自动进行第三次生成
- 当前聊天上传的图片仅作为临时 override / add-on

```text
Project DEFAULT sources
        ↓
   FRESH generation
        ↓
 structure/style audit
     /          \
  PASS       style FAIL
   ↓              ↓
 DONE       SINGLE RESTYLE
```

恢复阶段只使用两个角色：新生成的候选图作为 `STRUCTURE_EDIT_TARGET`，STYLE_CORE 作为唯一风格 authority。保持人物、姿势、构图、相机、空间关系、物体数量/接触和场景条件，只改变渲染风格。

`85mm`、长焦、低机位等术语只影响光学和构图，不会把非写实 STYLE_CORE 自动变成照片。

当前版本：`WPACK_v0.4.0-chat-native`
