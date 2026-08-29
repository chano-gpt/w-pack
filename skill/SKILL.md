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
7. Compile a bounded generation brief before invoking built-in image generation.
8. Generate fresh by default. Never reuse a previous generated candidate as an input unless the user explicitly requests a staged restyle or edit.
9. After generation, perform the audit in `references/audit-policy.md` and report only material failures that require another generation.

## Conflict handling

- Explicit user instructions override manifest defaults when they are compatible with safety and tool constraints.
- If two authorities claim the same visual property incompatibly, stop generation and identify the conflict.
- A `STYLE` authority must not silently control identity, pose, exact composition, or item design.
- A `CHARACTER` authority must not silently control background, lighting, graphic treatment, or composition.
- Preserve exact user-specified text whenever text must appear in the image.

## Project mode

When used inside a ChatGPT Project:

- Treat `project/PROJECT_INSTRUCTIONS.md` as the recommended project-level control prompt.
- Treat the user's project reference images as the authority library.
- If `AUTHORITY_MANIFEST` metadata is available, use it to resolve authority IDs and scopes.
- If no manifest exists, the user may define an authority inline, for example: `STYLE: first attached image`.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not request API keys, standalone image APIs, Codex OAuth, or a local GPU.

## Supporting references

- `references/authority-model.md` — authority semantics and influence boundaries.
- `references/generation-policy.md` — fresh generation, staged restyle, compilation rules.
- `references/audit-policy.md` — post-generation review rules.
