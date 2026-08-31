<p align="center">
  <img src="./assets/w-pack-hero.webp" alt="W-Pack — reference control for ChatGPT image generation" width="100%" />
</p>

<div align="center">

# W-Pack

### Reference-aware image generation control for ChatGPT

**Persistent Project sources. Explicit transport states. One STYLE_CORE with bounded STYLE_SUPPORT. High-salience hair control.**

[![Version](https://img.shields.io/badge/version-v0.5.1-111111?style=flat-square)](#project-status)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-Web%20%26%20Projects-111111?style=flat-square)](#quick-start)
[![Skill](https://img.shields.io/badge/ChatGPT-Skill-111111?style=flat-square)](./skill)
[![No API Key](https://img.shields.io/badge/API%20key-not%20required-111111?style=flat-square)](#how-it-works)

**English** · [한국어](./README.ko.md) · [日本語](./README.ja.md) · [简体中文](./README.zh-CN.md) · [繁體中文](./README.zh-TW.md) · [Español](./README.es.md) · [Português (Brasil)](./README.pt-BR.md) · [Français](./README.fr.md) · [Deutsch](./README.de.md)

</div>

---

W-Pack is a ChatGPT-native control layer for image generation and editing. It separates three problems that are often mixed together: **what a reference is allowed to control, whether that reference is actually transported to the image model, and how style fidelity is audited/recovered.**

## What changed in v0.5.1

- **Transport-aware references** — Project membership is no longer treated as proof that the image model received the source visually.
- **STYLE family model** — exactly one `STYLE_CORE`, plus zero to two bounded `STYLE_SUPPORT` adapters.
- **STYLE DNA fallback** — inspectable Project styles can be converted into high-specificity `style_signature` / `anti_drift_signature` profiles when direct binding is unverified.
- **Hair rendering grammar** — visible hair is now a dedicated high-salience style axis rather than generic texture.
- **CLEAN_MASS fallback** — suppresses dense flyaway halos, repeatedly split tips, random face-crossing wisps, and thread-like strand highlights when the source does not call for them.
- **Conditional single recovery** — structure-good/style-bad outputs may receive one restyle pass using `STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT`.
- **Schema/runtime sync** — validator, compiler, examples, Project instructions, and metadata now target manifest v1.1 / request v1.2 / compiled v1.3.

## Why W-Pack exists

ChatGPT can reason about Project files, current-chat images, and generated candidates, but those are not automatically equivalent image-model inputs. A selected Project reference can be semantically available to ChatGPT while its direct visual handoff remains unverified.

W-Pack therefore keeps **authority** and **transport** separate:

```text
Reference selected as authority
          ↓
  resolve bounded role
          ↓
 verify transport state
     /            \
visual bound   unverified
    ↓              ↓
direct use     source-derived profile
     \            /
       compile request
            ↓
       FRESH generation
            ↓
   structure / style audit
            ↓
 optional SINGLE_RESTYLE
```

## Authority model

| Role | Controls | Does not control by default |
| --- | --- | --- |
| `STYLE_CORE` | global medium, realism, abstraction, edge/value/color/surface/background grammar, visible-hair rendering grammar | identity, exact pose/composition, item identity |
| `STYLE_SUPPORT` | only declared support domains | core medium, realism, shape abstraction |
| `CHARACTER` | identity, facial features, hairstyle geometry, stable appearance | global style, layout, environment |
| `POSE` | body arrangement, gesture, stance | identity, environment, global style |
| `COMPOSITION` | framing, crop, camera angle, placement, hierarchy | identity, global style, item identity |
| `PROPORTION` | relative physical scale | identity, detailed pose, global style |
| `ITEM` | object identity, silhouette, structure, material | character identity, environment, global style |

> **Visible does not mean authorized. Selected does not mean visually bound.**

## STYLE_CORE + STYLE_SUPPORT

W-Pack does not average multiple equal styles.

`STYLE_CORE` owns the global grammar. `STYLE_SUPPORT` is a bounded adapter for declared domains such as color behavior, value structure, surface treatment, background rendering, edge treatment, or hair rendering grammar.

Core-only axes are:

```text
visual_medium
 degree_of_realism
 shape_abstraction
```

A resolved request may contain at most three STYLE references total: one CORE plus up to two SUPPORT sources. The overall first-pass reference limit remains five.

## Hair rendering

v0.5.1 adds a dedicated hair policy because unconstrained image generation often falls back to a recognizable micro-strand signature.

When the user or authoritative source does not explicitly require messy/frizzy/wet/windblown/strand-heavy hair, W-Pack uses the `CLEAN_MASS` fallback:

```text
silhouette
  → major grouped locks
  → internal texture
  → sparse micro-strands
```

The default favors a clean continuous silhouette, grouped ends, natural gravity flow, lock-level highlights, and only a few physically plausible flyaways. It specifically avoids turning hair into plastic or a helmet: volume, overlap, softness, and lock-level variation remain necessary.

If the source intentionally contains flyaways, curls, frizz, wet strands, or windblown separation, source authority wins over the fallback.

## Reference transport

W-Pack tracks these logical states:

- `VISUAL_BOUND`
- `VISUAL_INPUT_EXPECTED`
- `PROJECT_CONTEXT_ONLY`
- `TEXT_PROFILE_ONLY`
- `UNVERIFIED_PROJECT_SOURCE`
- `UNAVAILABLE`

Only `VISUAL_BOUND` is direct visual-binding proof. Automatic style recovery can also proceed from usable STYLE DNA, but text fallback must never be described as exact visual reference use.

## Conditional recovery

The normal path is one FRESH generation. Recovery is available only when:

1. mode was `FRESH`;
2. structure passes;
3. style fails;
4. exactly one STYLE_CORE exists; and
5. STYLE_CORE is visually bound or has usable STYLE DNA.

Recovery uses:

```text
STRUCTURE_EDIT_TARGET
+ STYLE_CORE
+ optional one STYLE_SUPPORT whose support domains match failure_axes
```

There is no recursive restyle and no automatic third generation pass.

## Quick start

1. Install [`skill/`](./skill) or a packaged `skill.zip`.
2. Add reusable images to your ChatGPT Project.
3. Copy [`project/PROJECT_INSTRUCTIONS.md`](./project/PROJECT_INSTRUCTIONS.md) into Project instructions.
4. Configure [`project/AUTHORITY_MANIFEST.example.json`](./project/AUTHORITY_MANIFEST.example.json).
5. Use natural-language image requests.

See [`QUICKSTART.md`](./QUICKSTART.md) for the compact setup guide.

## Schemas

| Layer | Current schema |
| --- | --- |
| Authority manifest | `WPACK_AUTHORITY_MANIFEST_v1.1` |
| Generation request | `WPACK_GENERATION_REQUEST_v1.2` |
| Compiled request | `WPACK_COMPILED_REQUEST_v1.3` |
| Style audit | `WPACK_STYLE_AUDIT_v1.1` |
| Style recovery | `WPACK_STYLE_RECOVERY_REQUEST_v1.1` |

Legacy manifest v1.0 and request v1.0/v1.1 remain accepted by the validator.

## Validate

```bash
python3 skill/scripts/self_test.py
```

Expected output:

```text
W-Pack self-test: PASS
```

## Project status

Current release: **`WPACK_v0.5.1-chat-native`**

The legacy `src/zpack` runtime remains provenance-only and is not installed or exposed by the ChatGPT Web harness.
