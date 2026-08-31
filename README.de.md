# W-Pack

### Referenzsteuerung für Bildgenerierung in ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Deutsch**

W-Pack v0.5.1 trennt die **Authority** einer Referenz (was sie steuern darf) vom **Transport** (ob das Bild tatsächlich als visueller Input beim Bildmodell angekommen ist).

## v0.5.1

- Eine Datei im Project gilt nicht automatisch als `VISUAL_BOUND`.
- STYLE wird als ein `STYLE_CORE` plus bis zu zwei begrenzte `STYLE_SUPPORT`-Adapter aufgelöst.
- Wenn direkte visuelle Bindung nicht verifiziert werden kann, kann STYLE DNA über `style_signature` und `anti_drift_signature` genutzt werden.
- Haare werden als eigener hochgewichteter Stil-Achse `hair_rendering_grammar` geprüft.
- Der Fallback `CLEAN_MASS` reduziert dichte Flyaway-Halos, wiederholt gespaltene Spitzen, zufällige Strähnen vor dem Gesicht und fadenartige Einzelhaar-Highlights, sofern die Quelle dies nicht verlangt.
- `SINGLE_RESTYLE` ist nur einmal erlaubt, wenn die Struktur besteht und der Stil scheitert.

## Recovery

Automatische Wiederherstellung verlangt genau ein STYLE_CORE, das entweder `VISUAL_BOUND` ist oder nutzbares STYLE DNA besitzt.

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

Kein rekursives Restyle und keine automatische dritte Generierung.

Details: [`QUICKSTART.md`](./QUICKSTART.md) / [English README](./README.md)

Aktuelle Version: **`WPACK_v0.5.1-chat-native`**
