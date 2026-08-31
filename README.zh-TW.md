# W-Pack

### 面向 ChatGPT 的參考圖控制型影像生成 Harness

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · **繁體中文**

W-Pack v0.5.1 將參考圖的 **authority（允許控制什麼）** 與 **transport（是否真的作為視覺輸入傳給影像模型）** 分開處理。

## v0.5.1

- Project 中存在檔案不再等同於 `VISUAL_BOUND`。
- STYLE 解析為 1 個 `STYLE_CORE` + 最多 2 個 `STYLE_SUPPORT`。
- 直接視覺綁定無法確認時，可使用 `style_signature` / `anti_drift_signature` 形式的 STYLE DNA。
- 頭髮新增獨立高權重風格軸 `hair_rendering_grammar`。
- 預設 `CLEAN_MASS` 抑制密集碎髮光環、反覆分叉髮尾、隨機穿過臉部的細髮，以及線狀單髮高光。
- 只有「結構通過、風格失敗」時才允許執行一次 `SINGLE_RESTYLE`。

## STYLE family

`STYLE_CORE` 控制全域媒介、寫實度、形狀抽象、邊緣、明暗、色彩、表面、背景及可見頭髮的渲染文法。`STYLE_SUPPORT` 只能作用於宣告的 support domain，不能覆蓋 CORE 的媒介、寫實度或形狀抽象。

## Hair rendering

預設順序：

```text
silhouette → major grouped locks → internal texture → sparse micro-strands
```

如果權威參考圖明確包含捲髮、毛躁、濕髮、風吹或大量獨立髮絲，則以參考圖為準。

## Recovery

自動復原要求：結構 PASS、風格 FAIL、恰好一個 STYLE_CORE，且 STYLE_CORE 已 `VISUAL_BOUND` 或具有可用 STYLE DNA。

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

禁止遞迴 restyle 與自動第三次生成。

詳細說明：[`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

目前版本：**`WPACK_v0.5.1-chat-native`**
