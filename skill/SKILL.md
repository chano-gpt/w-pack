---
name: w-pack
description: ChatGPT-native image-generation and editing control layer for persistent Project references, direct visual references, multi-source style families, and source-fidelity recovery. Use when creating, restyling, modifying, or refining images with Project or current-chat references, especially when style, character, pose, composition, proportion, item fidelity, or reference-image handoff matters.
---

# W-Pack

Use W-Pack as a transport-aware, Project-source-first control layer for ChatGPT image generation. Keep interaction conversational. Keep authority resolution, source-binding checks, STYLE DNA, auditing, and recovery internal unless the user asks to inspect them or a material limitation must be surfaced.

## Core workflow

1. Resolve `FRESH` vs `EDIT`.
2. Activate persistent Project sources by default using `default_source_profile`, otherwise `DEFAULT` when present.
3. Resolve bounded roles: `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
4. Verify reference transport before generation. A Project file being present is **not** proof that the image-generation model received it as a visual reference.
5. Resolve the style family: exactly one `STYLE_CORE`, plus zero to two bounded `STYLE_SUPPORT` sources when configured.
6. If a Project style image is inspectable but direct visual binding is unverified, derive or reuse a detailed text STYLE DNA. Never describe text fallback as equivalent to direct visual binding.
7. Compile and generate one fresh candidate first.
8. Audit reference binding, structure, STYLE_CORE fidelity, and STYLE_SUPPORT domains separately.
9. If structure passes and style fails, run exactly one `SINGLE_RESTYLE` recovery using the fresh candidate, STYLE_CORE, and at most one relevant STYLE_SUPPORT.
10. Never recursively restyle or run an automatic third image-generation pass.

Read `references/reference-transport.md` whenever persistent or prior references are involved. Read `references/style-family.md` for multi-style behavior. Read `references/source-profiles.md`, `references/authority-model.md`, `references/generation-policy.md`, `references/style-recovery-policy.md`, `references/edit-policy.md`, and `references/audit-policy.md` as needed.

## Persistent sources

Persistent Project authorities remain the primary reusable catalog. The user does not need to repeat "use the sources".

Precedence:

1. Explicit per-request user instruction.
2. Explicit current-chat reference override.
3. Explicitly named source profile.
4. Manifest `default_source_profile`.
5. Profile named `DEFAULT`.

Disable default Project sources only when the user explicitly asks to ignore them or `use_default_sources=false`.

An explicit current-chat STYLE replaces the Project style family for that request unless the user explicitly asks to combine them. Keep unaffected non-style Project authorities active.

## Reference transport is separate from authority

Never assume that a selected Project image is automatically a usable visual input to the image model.

Use this hierarchy:

1. **Direct visual binding available**: use the actual image reference.
2. **Project image inspectable, visual handoff unverified**: analyze the source and use a source-derived authority profile. For STYLE, compile STYLE DNA.
3. **Text profile only**: use it as degraded fallback and do not claim exact visual fidelity.
4. **No image and no usable profile**: do not pretend the source was applied.

For exact CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM fidelity, direct visual binding is materially stronger than text-only fallback. If binding is unavailable, do not claim exact preservation.

## STYLE family

Do not average several equal global styles.

### STYLE_CORE

Resolve exactly one STYLE_CORE when style authority exists. STYLE_CORE has absolute precedence for global visual grammar:

- visual medium and rendering domain
- degree of realism
- shape and feature abstraction
- contour and edge grammar
- dominant shading and value structure
- color behavior
- texture and surface treatment
- background rendering behavior

Do not normalize a stylized or non-photographic STYLE_CORE into generic photorealism unless the user explicitly asks for photography or photorealism.

Camera brand, focal length, telephoto, depth of field, low angle, and high angle control optical/composition behavior; they do not override STYLE_CORE medium by themselves.

### STYLE_SUPPORT

Allow up to two STYLE_SUPPORT sources. A support source is a bounded adapter, not a second equal style. It may influence only declared support domains such as color behavior, value structure, surface treatment, or background rendering.

STYLE_SUPPORT must not override STYLE_CORE medium, realism level, or shape abstraction. If style sources disagree, preserve STYLE_CORE rather than averaging them.

## STYLE DNA

When direct Project-image visual binding cannot be confirmed but ChatGPT can inspect the source, derive a compact high-specificity STYLE DNA from observable properties:

- medium and mark-making
- line width, taper, edge hardness, and contour hierarchy
- face/eye/hair abstraction
- shape language
- shadow shapes, value bands, gradient behavior
- highlight geometry and material treatment
- saturation and palette relationships
- texture and surface treatment
- background simplification and depth cues
- degree of realism
- anti-drift traits that must not appear

Use the CORE DNA globally. Apply SUPPORT DNA only to declared support domains. Avoid vague labels such as "anime style" when the source contains more specific observable grammar.

## Conditional recovery

Normal path: one FRESH generation.

Run `SINGLE_RESTYLE` only when all are true:

- original mode is `FRESH`
- one STYLE_CORE exists
- structure is materially acceptable
- style materially fails
- STYLE_CORE is visually bound or usable STYLE DNA exists

During recovery:

- fresh candidate = `STRUCTURE_EDIT_TARGET`; content/geometry authority only
- STYLE_CORE = global style authority
- optionally one matching STYLE_SUPPORT = bounded style adapter only
- preserve identity, pose, composition, camera, spatial relationships, object count/contact, scene content, and exact text
- change rendering style only
- do not crop, rotate, mirror, zoom, add, remove, replace, duplicate, or redesign content

Do not use style recovery to fix structural failures.

## Modes

Use `FRESH` for new images and remakes. Do not silently reuse prior generated candidates.

Use `EDIT` when the user explicitly targets a usable existing image for modification. User-requested `EDIT` is distinct from automatic `SINGLE_RESTYLE` recovery.

## Internal request contract

Use this logical shape internally:

```json
{
  "schema_version": "WPACK_GENERATION_REQUEST_v1.2",
  "mode": "FRESH",
  "scene": "...",
  "aspect_ratio": "4:5",
  "use_default_sources": true,
  "combine_style_sources": false,
  "source_profile": null,
  "references": [],
  "composition": [],
  "lighting": [],
  "exact_text": null,
  "preserve": [],
  "avoid": [],
  "edit_target": null
}
```

The compiler emits `WPACK_COMPILED_REQUEST_v1.3` with explicit reference-transport, style-family, STYLE DNA, and recovery policy metadata.

## Conflict handling

- Fail closed on incompatible authority claims.
- Keep first-pass reference count at five or fewer.
- Permit multiple STYLE references only as one CORE plus up to two SUPPORT sources.
- Do not let a SUPPORT silently become a second global style.
- Preserve exact user-specified text.
- Do not substitute unresolved Project authorities with visually similar files.
- Do not hide source-transport failure behind stronger prompt wording.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not require an API key, standalone image API, Codex OAuth, or local GPU.

## Supporting resources

- `references/reference-transport.md` — visual binding vs Project context and fallback rules.
- `references/style-family.md` — STYLE_CORE, STYLE_SUPPORT, and STYLE DNA.
- `references/source-profiles.md` — persistent source activation and overrides.
- `references/authority-model.md` — bounded authority semantics.
- `references/chat-intent-resolution.md` — conversational role and mode resolution.
- `references/generation-policy.md` — first-pass generation and fallback rules.
- `references/style-recovery-policy.md` — conditional single-restyle workflow.
- `references/edit-policy.md` — user-requested editing.
- `references/audit-policy.md` — binding/structure/style audit.
- `references/project-setup.md` — recommended Project configuration.
- `references/authority-manifest.example.json` — v1.1 style-family manifest example.
- `references/generation-request.example.json` — v1.2 request example.
- `scripts/validate_authorities.py` — deterministic manifest/request validation.
- `scripts/compile_request.py` — transport-aware first-pass/recovery compilation.
- `scripts/self_test.py` — deterministic smoke tests.

## Verification

After modifying scripts, run:

```bash
python3 scripts/self_test.py
```

Require `W-Pack self-test: PASS` before packaging or distributing the Skill.
