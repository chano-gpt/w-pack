---
name: w-pack
description: Compile, validate, and audit ChatGPT web image-generation requests using explicit project or conversation reference-image authorities. Use for image generation or image editing when references must have bounded roles such as style, character, pose, proportion, or item.
---

# W-Pack

W-Pack is the control layer for image generation inside ChatGPT web and ChatGPT Projects.

## Core workflow

1. Read the user's scene brief.
2. Resolve only explicitly named or clearly identified reference images from the current conversation or Project files.
3. Assign each reference exactly one primary authority role: `STYLE`, `CHARACTER`, `POSE`, `PROPORTION`, or `ITEM`.
4. Read `references/authority-model.md` and enforce allowed and forbidden influence for every authority.
5. Refuse to silently infer a reference's role from visual similarity alone.
6. Enforce a maximum of 5 generation references.
7. Build a `WPACK_GENERATION_REQUEST_v1.0` request object.
8. When script execution is available, run `scripts/validate_authorities.py` against the authority manifest and request. Fail closed on validation errors.
9. When script execution is available, run `scripts/compile_request.py` to produce the bounded generation brief. Otherwise perform the same checks directly from this Skill and its references.
10. Invoke ChatGPT's built-in image-generation capability using the compiled brief and the resolved reference images.
11. Generate fresh by default. Never reuse a previous generated candidate as an input unless the user explicitly requests a staged restyle or edit.
12. After generation, perform the audit in `references/audit-policy.md` and report only material failures that require another generation.

## Request contract

Use this logical shape before generation:

```json
{
  "schema_version": "WPACK_GENERATION_REQUEST_v1.0",
  "mode": "FRESH",
  "scene": "...",
  "aspect_ratio": "4:5",
  "exact_text": null,
  "authorities": [
    {
      "id": "STYLE_CORE_01",
      "role": "STYLE",
      "influence": ["palette", "rendering_language"]
    }
  ]
}
```

Do not expose this JSON to the user unless it materially helps the task or the user asks for it.

## Conflict handling

- Explicit user instructions override manifest defaults when they are compatible with safety and tool constraints.
- If two authorities claim the same visual property incompatibly, stop generation and identify the conflict.
- A `STYLE` authority must not silently control identity, pose, exact composition, or item design.
- A `CHARACTER` authority must not silently control background, lighting, graphic treatment, or composition.
- Preserve exact user-specified text whenever text must appear in the image.
- Do not treat filename proximity, upload order, or visual similarity as authority assignment.

## Project mode

When used inside a ChatGPT Project:

- Treat `project/PROJECT_INSTRUCTIONS.md` as the recommended project-level control prompt.
- Treat the user's project reference images as the authority library.
- If `AUTHORITY_MANIFEST` metadata is available, use it to resolve authority IDs and scopes.
- If no manifest exists, the user may define an authority inline, for example: `STYLE: first attached image`.
- Project files are references, not automatic generation inputs. Only pass the references selected for the current request.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not request API keys, standalone image APIs, Codex OAuth, or a local GPU.

## Legacy boundary

The repository may retain upstream `src/zpack` files for provenance during migration. They are not part of the ChatGPT web execution path and must not be invoked by this Skill.

## Supporting references

- `references/authority-model.md` — authority semantics and influence boundaries.
- `references/generation-policy.md` — fresh generation, staged restyle, compilation rules.
- `references/audit-policy.md` — post-generation review rules.
- `scripts/validate_authorities.py` — deterministic metadata/request validation.
- `scripts/compile_request.py` — deterministic bounded-request compilation.
