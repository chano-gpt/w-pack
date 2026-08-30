<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — 面向 ChatGPT 的受控參考圖像生成" width="100%" />
</p>

<div align="center">

# W-Pack

### 面向 ChatGPT 的 Reference-bounded Image Generation

**自然使用參考圖片，同時明確限制每張圖片的影響範圍。**

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · **繁體中文** · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack 是一個面向 **ChatGPT Web、ChatGPT Projects 與 ChatGPT Skills** 的 chat-native 圖像生成與編輯控制層，用來限制參考圖片可以影響哪些視覺屬性。

一般的多參考圖請求容易產生混雜：風格參考圖中的人物、構圖、背景或物件可能被模型意外帶入結果。W-Pack 為每張參考圖指定一個明確角色：`STYLE`、`CHARACTER`、`POSE`、`COMPOSITION`、`PROPORTION` 或 `ITEM`。

```text
第一張圖只參考風格。
第二張圖的人物保持不變。
使用第三張圖的構圖。
這張圖保留臉和構圖，只修改服裝。
```

使用者不需要手寫 JSON 或 manifest ID。

## 核心功能

- **自然語言參考控制** — 支援「用這個感覺」「保留這個人物」「用這個姿勢」「照這個構圖」等表達。
- **Inline reference** — 當前對話中上傳的圖片不需要 manifest 即可使用。
- **6 種 Authority role** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`。
- **FRESH / EDIT** — 區分新圖生成與既有圖像編輯。
- **Project source profile** — 可用簡短指令啟用重複使用的參考圖組合。
- **Deterministic validation** — 檢查權限衝突、重複引用與無效編輯要求。

## 快速開始

1. 將 [`skill/`](./skill) 安裝或上傳為 ChatGPT Skill。
2. 上傳一張或多張參考圖。
3. 用自然語言說明每張圖應該控制什麼。

```text
@W-Pack

第一張圖只參考風格。
第二張圖的人物保持不變。
使用第三張圖的構圖生成新圖。

背景：夕陽室內、柔和自然光。
比例：4:5 直式。
```

不需要 API Key、本地 CLI 或獨立圖像 API。

## Authority model

| Role | 可控制 | 預設不控制 |
| --- | --- | --- |
| `STYLE` | 色彩、質感、光線語言、渲染、圖形處理 | 人物身分、姿勢、精確構圖、物件身分 |
| `CHARACTER` | 人物身分、臉部、髮型、穩定外觀 | 背景、光線、版面、無關物件 |
| `POSE` | 身體配置、動作、姿態、方向 | 人物身分、服裝、環境、風格 |
| `COMPOSITION` | 取景、裁切、機位、位置關係、留白 | 人物身分、服裝、物件身分、整體風格 |
| `PROPORTION` | 身體/物件比例、相對尺寸 | 人物身分、細部姿勢、風格 |
| `ITEM` | 物件身分、輪廓、關鍵結構 | 人物身分、環境、整體風格 |

> **看得見，不代表被授權。**

參考圖中偶然出現的元素，除非對應 Authority 明確允許，否則不應影響生成結果。

## FRESH 與 EDIT

### `FRESH`
用於生成新圖或依參考圖重新生成，不會預設重用之前的生成結果。

### `EDIT`
用於修改既有圖像並保留指定內容。內部可分類為 `MODIFY`、`RESTYLE` 或 `RECOMPOSE`。

## ChatGPT Project

若有固定重複使用的參考圖，可將其存入 ChatGPT Project，並套用 [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md)。

Project 中存在的圖片不會自動成為輸入。W-Pack 只選擇目前請求需要的最小參考集合。

## 工作流程

```text
自然語言請求
  -> 判斷 FRESH / EDIT
  -> 解析參考圖與 Authority role
  -> 可選 Source Profile
  -> 驗證作用域與衝突
  -> 編譯 scene / composition / lighting / text / preserve / avoid
  -> ChatGPT 圖像生成
  -> 靜默 audit
```

單次生成最多使用 5 張參考圖。

## 驗證

```bash
python3 skill/scripts/self_test.py
```

預期結果：

```text
W-Pack self-test: PASS
```

## 目前狀態

目前版本為 `WPACK_v0.3.0-chat-native`，重點包含 Inline reference、自然語言 Authority 解析、`COMPOSITION`、FRESH/EDIT、Project Source Profile 與 deterministic validation。
