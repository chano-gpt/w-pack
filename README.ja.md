# W-Pack

### ChatGPT 向けリファレンス制御型画像生成ハーネス

[English](./README.md) · [한국어](./README.ko.md) · **日本語** · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md)

W-Pack v0.5.1 は、ChatGPT Web / Projects で再利用する画像リファレンスを **authority（何を制御するか）** と **transport（画像モデルへ実際に渡ったか）** に分けて扱います。

## v0.5.1

- Project にファイルが存在するだけでは `VISUAL_BOUND` と見なしません。
- STYLE は `STYLE_CORE` 1つ + `STYLE_SUPPORT` 最大2つで解決します。
- 直接の視覚バインドが不明な場合は、`style_signature` / `anti_drift_signature` による STYLE DNA を利用できます。
- 髪を `hair_rendering_grammar` という独立した高重要度のスタイル軸として監査します。
- 既定の `CLEAN_MASS` は、過剰なアホ毛、繰り返し分岐する毛先、顔を横切るランダムな細毛、糸状ハイライトを抑制します。
- 構造が成功しスタイルだけが失敗した場合のみ、`SINGLE_RESTYLE` を1回だけ実行できます。

## STYLE family

`STYLE_CORE` が媒体、写実度、形状抽象化、エッジ、明暗、色、表面、背景、髪のレンダリング文法を支配します。`STYLE_SUPPORT` は宣言された support domain のみを補助し、CORE の媒体・写実度・形状抽象化を上書きできません。

## Hair rendering

既定の順序:

```text
silhouette → major grouped locks → internal texture → sparse micro-strands
```

ただし、参照画像が意図的に縮れ毛、濡れ髪、風になびく髪、強い毛束分離を示す場合は参照側を優先します。

## Recovery

自動回復には、構造 PASS / スタイル FAIL / STYLE_CORE 1つに加え、STYLE_CORE が `VISUAL_BOUND` または利用可能な STYLE DNA を持つ必要があります。

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

再帰 restyle と自動3回目生成は禁止です。

詳細: [`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

現在のバージョン: **`WPACK_v0.5.1-chat-native`**
