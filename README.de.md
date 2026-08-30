<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — kontrollierte Referenzbild-Generierung für ChatGPT" width="100%" />
</p>

<div align="center">

# W-Pack

### Referenzgebundene Bildgenerierung für ChatGPT

**Referenzbilder natürlich verwenden, ohne ihnen unbegrenzte Kontrolle zu geben.**

[English](./README.md) · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · **Deutsch**

</div>

---

W-Pack ist eine chat-native Kontrollschicht für Bildgenerierung und Bildbearbeitung in **ChatGPT Web, ChatGPT Projects und ChatGPT Skills**. Sie begrenzt, welche visuellen Eigenschaften ein Referenzbild beeinflussen darf.

Bei mehreren Referenzen kann ein Stilbild unbeabsichtigt Identität, Komposition, Hintergrund oder Objekte übertragen. W-Pack weist jeder Referenz eine klare Authority zu: `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION` oder `ITEM`.

```text
Nutze das erste Bild nur für den Stil.
Behalte die Person aus dem zweiten Bild unverändert.
Nutze die Komposition des dritten Bildes.
Behalte in diesem Bild Gesicht und Komposition, ändere aber nur die Kleidung.
```

Kein manuelles JSON und keine Manifest-IDs erforderlich.

## Highlights

- **Natürlichsprachliche Referenzsteuerung** — versteht Anweisungen wie „nutze diesen Stil“, „behalte diese Person“, „nutze diese Pose“ oder „nutze diese Komposition“.
- **Inline references** — Bilder aus der aktuellen Unterhaltung benötigen keinen Manifest-Eintrag.
- **Sechs Authority roles** — `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
- **FRESH / EDIT** — trennt neue Generierung von der Bearbeitung eines vorhandenen Bildes.
- **Project source profiles** — wiederverwendbare Referenzsets können mit kurzen Befehlen aktiviert werden.
- **Deterministische Validierung** — erkennt Konflikte, doppelte Referenzen und ungültige Edit-Anfragen.

## Schnellstart

1. [`skill/`](./skill) als ChatGPT Skill installieren oder hochladen.
2. Ein oder mehrere Referenzbilder anhängen.
3. In natürlicher Sprache festlegen, was jedes Bild steuern soll.

```text
@W-Pack

Erstes Bild: nur Stil.
Behalte die Person aus dem zweiten Bild.
Nutze die Komposition des dritten Bildes.

Hintergrund: Innenraum bei Sonnenuntergang mit weichem natürlichem Licht.
Format: 4:5 Hochformat.
Generiere ein neues Bild.
```

Kein API Key, keine lokale CLI und keine separate Bild-API nötig.

## Authority model

| Role | Steuert | Steuert standardmäßig nicht |
| --- | --- | --- |
| `STYLE` | Farbe, Textur, Licht, Rendering, grafische Behandlung | Identität, Pose, exakte Komposition, Objektidentität |
| `CHARACTER` | Identität, Gesicht, Haare, stabiles Erscheinungsbild | Hintergrund, Licht, Layout, fremde Objekte |
| `POSE` | Körperanordnung, Gestik, Haltung, Orientierung | Identität, Kleidung, Umgebung, Stil |
| `COMPOSITION` | Framing, Crop, Kamerawinkel, Platzierung, Negativraum | Identität, Kleidung, Objektidentität, globaler Stil |
| `PROPORTION` | Körper-/Objektskala und relative Maße | Identität, detaillierte Pose, Stil |
| `ITEM` | Objektidentität, Silhouette, wichtige Struktur | Charakteridentität, Umgebung, globaler Stil |

> **Sichtbar bedeutet nicht autorisiert.**

Ein zufälliges Element in einer Referenz darf das Ergebnis nicht beeinflussen, wenn seine Authority dies nicht erlaubt.

## FRESH und EDIT

### `FRESH`
Für neue Bilder oder eine Neu-Generierung aus freigegebenen Referenzen. Frühere Ergebnisse werden nicht stillschweigend wiederverwendet.

### `EDIT`
Für die Bearbeitung eines vorhandenen Bildes unter Erhalt bestimmter Eigenschaften. Intern kann der Vorgang als `MODIFY`, `RESTYLE` oder `RECOMPOSE` klassifiziert werden.

## ChatGPT Project

Wenn dieselben Referenzen regelmäßig genutzt werden, können sie in einem ChatGPT Project gespeichert und mit [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md) konfiguriert werden.

Ein Bild wird nicht automatisch aktiv, nur weil es im Project vorhanden ist. W-Pack wählt nur die minimal erforderlichen Referenzen für die aktuelle Anfrage aus.

## Ablauf

```text
Natürlichsprachliche Anfrage
  -> FRESH / EDIT bestimmen
  -> Referenzen und Authority roles auflösen
  -> optionales Source Profile anwenden
  -> Scopes und Konflikte validieren
  -> scene / composition / lighting / text / preserve / avoid kompilieren
  -> ChatGPT-Bildgenerierung
  -> stille Prüfung
```

Pro Generierung werden maximal 5 Referenzen verwendet.

## Validierung

```bash
python3 skill/scripts/self_test.py
```

Erwartetes Ergebnis:

```text
W-Pack self-test: PASS
```

## Aktueller Stand

Die aktuelle Version ist `WPACK_v0.3.0-chat-native` mit Fokus auf Inline References, natürliche Authority-Auflösung, `COMPOSITION`, FRESH/EDIT, Project Source Profiles und deterministische Validierung.
