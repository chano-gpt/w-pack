# W-Pack

### Project-source-first Bildgenerierung für ChatGPT

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · **Deutsch**

W-Pack v0.4 verwendet persistente Referenzen aus einem ChatGPT Project standardmäßig und trennt die Zuständigkeiten für Stil, Charakter, Pose, Komposition, Proportion und Objekt.

## Neu in v0.4

- Das Project-Profil `DEFAULT` wird automatisch aktiviert.
- Eine einzelne STYLE-Referenz wird intern zu `STYLE_CORE`.
- Visuelles Medium, Realismusgrad, Konturen, Abstraktion, Werte/Schatten, Farbe, Textur und Hintergrunddarstellung werden stärker geschützt.
- Der Ablauf beginnt immer mit genau einer FRESH-Generierung.
- Nur wenn die Struktur passt, aber der Stil scheitert, ist ein einzelner `SINGLE_RESTYLE` erlaubt.
- Kein rekursives Restyling und kein automatischer dritter Generierungsschritt.
- Im Chat angehängte Bilder bleiben temporäre Overrides oder Ergänzungen.

Bei der Wiederherstellung werden nur der frisch erzeugte Kandidat als `STRUCTURE_EDIT_TARGET` und STYLE_CORE als einzige Stilautorität verwendet. Identität, Pose, Komposition, Kamera, räumliche Beziehungen, Objekte und Szenenbedingungen bleiben erhalten; nur die Rendering-Sprache wird geändert.

Aktuelle Version: `WPACK_v0.4.0-chat-native`
