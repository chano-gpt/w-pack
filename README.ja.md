<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — ChatGPT向け参照制御画像生成" width="100%" />
</p>

<div align="center">

# W-Pack

### ChatGPTのための Reference-bounded Image Generation

**参照画像は自然に使いながら、影響範囲は明確に制限します。**

[English](./README.md) · [한국어](./README.ko.md) · **日本語** · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack は **ChatGPT Web、ChatGPT Projects、ChatGPT Skills** で画像生成・編集を行う際に、参照画像がどの要素へ影響できるかを制御する chat-native レイヤーです。

通常の複数参照では、スタイル画像から人物、構図、背景、アイテムなどが意図せず混ざることがあります。W-Pack は各参照に `STYLE`、`CHARACTER`、`POSE`、`COMPOSITION`、`PROPORTION`、`ITEM` のいずれかの権限を割り当てます。

```text
1枚目は雰囲気だけ参考にして。
2枚目の人物はそのまま維持して。
3枚目の構図を使って。
この画像では顔と構図を維持し、服だけ変えて。
```

JSON や manifest ID をユーザーが直接書く必要はありません。

## 主な機能

- **自然言語による参照制御** — 「この雰囲気で」「この人物をそのまま」「このポーズで」「この構図で」などを解釈します。
- **Inline reference** — 現在の会話に添付した画像は manifest なしで利用できます。
- **6つの Authority role** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`。
- **FRESH / EDIT** — 新規生成と既存画像の編集を分けて扱います。
- **Project source profile** — 繰り返し使う参照セットを短い指示で呼び出せます。
- **Deterministic validation** — 権限衝突、重複参照、不正な編集指定などを検証します。

## クイックスタート

1. [`skill/`](./skill) を ChatGPT Skill としてインストールまたはアップロードします。
2. 参照画像を1枚以上添付します。
3. 各画像が何を担当するかを自然言語で伝えます。

```text
@W-Pack

1枚目はスタイルのみ参照。
2枚目の人物はそのまま維持。
3枚目の構図を使って新しい画像を生成。

背景は夕暮れの室内、柔らかい自然光。
縦4:5。
```

API Key、ローカル CLI、独立した画像 API は不要です。

## Authority model

| Role | 制御する要素 | デフォルトでは制御しない要素 |
| --- | --- | --- |
| `STYLE` | 色、質感、光、レンダリング、グラフィック処理 | 人物の同一性、ポーズ、正確な構図、アイテム同一性 |
| `CHARACTER` | 人物の同一性、顔、髪、安定した外見 | 背景、照明、レイアウト、無関係な物体 |
| `POSE` | 身体配置、ジェスチャー、姿勢、向き | 人物、衣装、環境、スタイル |
| `COMPOSITION` | フレーミング、クロップ、カメラ角度、配置、余白 | 人物、衣装、アイテム同一性、全体スタイル |
| `PROPORTION` | 身体・物体の比率、相対サイズ | 人物、細かなポーズ、スタイル |
| `ITEM` | 物体の同一性、シルエット、構造 | 人物、環境、全体スタイル |

> **見えていることと、許可されていることは同じではありません。**

参照画像に偶然写っている要素は、その Authority が許可していない限り結果へ影響してはいけません。

## FRESH と EDIT

### `FRESH`
新しい画像や参照ベースの再生成に使います。過去の生成結果を自動的に再利用しません。

### `EDIT`
既存画像の一部変更、維持、再スタイル、再構成に使います。内部では `MODIFY`, `RESTYLE`, `RECOMPOSE` に分類されることがあります。

## ChatGPT Project

繰り返し使う参照画像がある場合は ChatGPT Project に保存し、[`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md) を適用できます。

Project 内に存在するだけで参照が自動使用されることはありません。W-Pack は現在のリクエストに必要な最小限の参照のみを選択します。

## 処理フロー

```text
自然言語リクエスト
  -> FRESH / EDIT 判定
  -> 参照と Authority role の解決
  -> 任意の Source Profile 適用
  -> スコープと衝突の検証
  -> scene / composition / lighting / text / preserve / avoid をコンパイル
  -> ChatGPT 画像生成
  -> サイレント監査
```

1回の生成で使用する参照は最大5つです。

## 検証

```bash
python3 skill/scripts/self_test.py
```

期待される結果:

```text
W-Pack self-test: PASS
```

## 現在の状態

現在のバージョンは `WPACK_v0.3.0-chat-native` です。Inline reference、自然言語 Authority 解決、`COMPOSITION`、FRESH/EDIT、Project Source Profile、deterministic validation に重点を置いています。
