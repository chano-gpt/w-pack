# W-Pack

### ChatGPT向け Project-source-first 画像生成ハーネス

[English](./README.md) · [한국어](./README.ko.md) · **日本語** · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md)

W-Pack v0.4 は、ChatGPT Web / Projects で再利用可能な Project 参照画像をデフォルトで使い、各参照の影響範囲を分離しながらスタイル忠実度を管理します。

## v0.4 の要点

- Project の `DEFAULT` ソースを自動的に有効化
- 単一の STYLE 参照を内部的に `STYLE_CORE` として扱う
- 画材・レンダリング領域・写実度・輪郭・抽象化・陰影・色・質感を強く保持
- 最初は必ず 1 回の FRESH 生成
- 構造が成功し、スタイルだけが失敗した場合に限り 1 回だけ `SINGLE_RESTYLE`
- 再帰的 restyle と自動 3 回目の生成は禁止
- チャット添付画像は一時的な override / add-on として使用

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

`SINGLE_RESTYLE` では、生成済み候補を `STRUCTURE_EDIT_TARGET`、STYLE_CORE を唯一のスタイル権限として使用します。人物、ポーズ、構図、カメラ、空間関係、物体数、接触関係、シーン条件を維持し、レンダリングスタイルだけを変更します。

`85mm`、telephoto、low angle などのカメラ用語は光学・構図の指定であり、非写実 STYLE_CORE を自動的に写真へ変換しません。

現在のバージョン: `WPACK_v0.4.0-chat-native`
