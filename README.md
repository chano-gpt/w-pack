<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — Project-source-first image generation for ChatGPT" width="100%" />
</p>

<div align="center">

# W-Pack

### Project-source-first image generation for ChatGPT

**Persistent references by default. Bounded authorities. Conditional style recovery when the first pass drifts.**

[![Version](https://img.shields.io/badge/version-v0.4.0-111111?style=flat-square)](#project-status)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-Web%20%26%20Projects-111111?style=flat-square)](#quick-start)
[![Skill](https://img.shields.io/badge/ChatGPT-Skill-111111?style=flat-square)](./skill)
[![No API Key](https://img.shields.io/badge/API%20key-not%20required-111111?style=flat-square)](#how-it-works)

**English** · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack is a ChatGPT-native control layer for image generation and editing. It adapts the core Z-Pack ideas—bounded visual authorities, fresh generation, fail-closed reference handling, and deliberate style control—to ChatGPT Web and Projects.

## What changed in v0.4

- **Project sources are the default** — reusable Project references are active without repeating “use the sources.”
- **STYLE_CORE** — a singular active STYLE reference becomes the global visual-grammar anchor.
- **Stronger style fidelity** — medium, realism level, contours, abstraction, shading/value, color, texture, and background rendering are protected.
- **Conditional two-stage recovery** — W-Pack generates once first; only a structure-good/style-bad result may receive one style-only restyle.
- **No recursive editing loop** — maximum restyle depth is one and there is no automatic third pass.
- **Inline images stay secondary** — current-chat attachments are temporary overrides/add-ons, not the normal source path.

## Why this workflow

A one-shot multi-reference request is normally best on the web. Two-stage generation adds value only when the first image gets the scene and geometry right but drifts away from the intended style.

W-Pack therefore uses:

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
               ↓
          final audit / stop
```

`SINGLE_RESTYLE` uses only:

1. the fresh candidate as `STRUCTURE_EDIT_TARGET` — content and geometry authority only;
2. the selected `STYLE_CORE` — sole rendering-style authority.

It does not feed CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM references into the recovery edit.

## Authority model

| Role | Controls | Does not control by default |
| --- | --- | --- |
| `STYLE` / internal `STYLE_CORE` | visual medium, rendering grammar, palette, texture, abstraction, value/shading, degree of realism | identity, exact pose, exact composition, item identity |
| `CHARACTER` | identity, face, hair, stable appearance | global style, layout, environment |
| `POSE` | body arrangement, gesture, stance | identity, environment, global style |
| `COMPOSITION` | framing, crop, camera angle, placement, hierarchy | identity, global style, item identity |
| `PROPORTION` | relative physical scale | identity, detailed pose, global style |
| `ITEM` | object identity, silhouette, structure | character identity, environment, global style |

> **Visible does not mean authorized.**

## STYLE_CORE

When exactly one STYLE authority is active, W-Pack treats it as `STYLE_CORE` internally.

The core controls global visual grammar: medium, realism level, edge language, shape abstraction, shading/value structure, color behavior, surface treatment, and background rendering. Photographic terms such as “85mm”, “telephoto”, or “low angle” affect optical behavior and composition; they do not automatically turn an illustration into a photograph.

## Project sources first

A normal ChatGPT Project setup looks like:

```text
ChatGPT Project
├── reusable reference images
├── Project instructions
├── authority manifest
└── DEFAULT source profile
```

The DEFAULT profile is active automatically. Current-chat attachments are used only when the user explicitly wants a temporary override or addition.

## Quick start

1. Install [`skill/`](./skill) or the packaged `skill.zip`.
2. Copy [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md) into your ChatGPT Project.
3. Configure [`project/AUTHORITY_MANIFEST.example.json`](./project/AUTHORITY_MANIFEST.example.json) with your reusable sources.
4. Use natural-language image requests.

See [`QUICKSTART.md`](./QUICKSTART.md).

## How it works

```text
Natural request
  -> resolve FRESH vs EDIT
  -> activate DEFAULT Project profile
  -> apply optional inline overrides
  -> resolve bounded roles + singular STYLE_CORE
  -> compile FRESH_FIRST request
  -> ChatGPT image generation
  -> structure/style audit
  -> optional SINGLE_RESTYLE on style-only failure
  -> stop; never recursive-restyle automatically
```

W-Pack allows at most five first-pass references.

## Validation

```bash
python3 skill/scripts/self_test.py
```

Expected:

```text
W-Pack self-test: PASS
```

## Project status

`WPACK_v0.4.0-chat-native` is the current ChatGPT Web milestone.

This version keeps the Z-Pack-inspired authority chain while adapting it to a chat-native environment: persistent sources replace repeated explicit ID selection, and Z-Pack's staged style idea becomes a conditional recovery rather than the default path.

## Repository map

| Path | Purpose |
| --- | --- |
| [`skill/`](./skill) | installable ChatGPT Skill source |
| [`project/`](./project) | ChatGPT Project setup templates |
| [`PACK_SPEC.json`](./PACK_SPEC.json) | machine-readable W-Pack contract |
| [`QUICKSTART.md`](./QUICKSTART.md) | setup guide |
| [`LEGACY.md`](./LEGACY.md) | upstream runtime migration boundary |
