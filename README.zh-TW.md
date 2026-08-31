# W-Pack

### 適用於 ChatGPT 的 Project-source-first 圖像生成控制層

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · **繁體中文**

W-Pack v0.4 預設使用 ChatGPT Project 中的持久參考圖，並以受限 authority 角色控制風格、人物、姿勢、構圖、比例與物件的影響範圍。

## v0.4 重點

- 自動啟用 Project `DEFAULT` 來源
- 將唯一 STYLE 參考在內部提升為 `STYLE_CORE`
- 強化媒介、寫實程度、輪廓、抽象方式、明暗、色彩、材質與背景渲染的一致性
- 先只進行一次 FRESH 生成
- 僅在「結構通過、風格失敗」時執行一次 `SINGLE_RESTYLE`
- 禁止遞迴 restyle，也不會自動進行第三次生成
- 當前聊天上傳圖片只作為臨時 override / add-on

恢復階段只使用兩個角色：剛生成的候選圖作為 `STRUCTURE_EDIT_TARGET`，STYLE_CORE 作為唯一風格 authority。保留人物、姿勢、構圖、相機、空間關係、物件數量/接觸與場景條件，只改變渲染風格。

`85mm`、長焦、低角度等術語只影響光學與構圖，不會把非寫實 STYLE_CORE 自動變成照片。

目前版本：`WPACK_v0.4.0-chat-native`
