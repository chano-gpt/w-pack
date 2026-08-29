---
name: w-pack
description: Compile, validate, and audit ChatGPT web image-generation requests using explicit Project or conversation reference-image authorities. Use for image generation or image editing when references must have bounded roles such as style, character, pose, proportion, or item, especially in ChatGPT Projects with reusable reference libraries.
---

# W-Pack

Use W-Pack as the control layer for image generation inside ChatGPT web and ChatGPT Projects.

## Core workflow

1. Read the user's scene brief.
2. Resolve only explicitly named or clearly identified reference images from the current conversation or Project files.
3. Assign each reference exactly one primary authority role: `STYLE`, `CHARACTER`, `POSE`, `PROPORTION`, or `ITEM`.
4. Read `references/authority-model.md` and enforce allowed and forbidden influence for every authority.
5. Do not infer a reference role from visual similarity, upload order, filename proximity, or incidental content.
6. Enforce a maximum of 5 generation references and prefer the minimum necessary set.
7. Build a `WPACK_GENERATION_REQUEST_v1.0` request object internally.
8. When script execution is available, run `scripts/validate_authorities.py` against the authority manifest and request. Fail closed on validation errors.
9. When script execution is available, run `scripts/compile_request.py` to produce `WPACK_COMPILED_REQUEST_v1.0`. Otherwise perform equivalent semantic validation and compilation directly.
10. Invoke ChatGPT's built-in image-generation capability with the compiled brief and only the selected reference images.
11. Generate fresh by default. Reuse a previous candidate only when the user explicitly requests an edit, refinement, continuation, preservation, or staged restyle.
12. After generation, audit the result using `references/audit-policy.md`. Surface only material defects.

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

Do not expose internal request JSON unless the user asks for it or it materially helps resolve a conflict.

## Conflict handling

- Let explicit user instructions override manifest defaults only when they remain compatible with safety and tool constraints.
- If two authorities claim the same visual property incompatibly, stop generation and identify the conflict.
- Do not let `STYLE` silently control identity, pose, exact composition, or item design.
- Do not let `CHARACTER` silently control background, lighting, graphic treatment, or composition.
- Preserve exact user-specified image text, including spelling, capitalization, punctuation, and line content.
- If an authority ID cannot be resolved to an available image, state what is missing instead of substituting another file.

## Project mode

When configuring a dedicated ChatGPT Project, read `references/project-setup.md` and use its Project instructions. Use `references/authority-manifest.example.json` and `references/generation-request.example.json` as starting templates.

Treat Project files as a persistent reference library, not as automatic generation inputs. Pass only the references selected for the current request.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not request API keys, standalone image APIs, Codex OAuth, or a local GPU.

## Legacy boundary

Ignore upstream `src/zpack`, `pack`, `private-assets`, and local workspace logic when this Skill is used. Those files may remain in the repository only for migration provenance and are not part of the ChatGPT web execution path.

## Supporting resources

- `references/authority-model.md` — authority semantics and influence boundaries.
- `references/generation-policy.md` — fresh generation, staged restyle, and compilation rules.
- `references/audit-policy.md` — post-generation review rules.
- `references/project-setup.md` — recommended ChatGPT Project configuration.
- `references/authority-manifest.example.json` — self-contained manifest template.
- `references/generation-request.example.json` — self-contained request template.
- `scripts/validate_authorities.py` — deterministic metadata/request validation.
- `scripts/compile_request.py` — deterministic bounded-request compilation.
- `scripts/self_test.py` — smoke test for valid, invalid, and staged-restyle flows.

## Script verification

When modifying the Skill's scripts, run:

```bash
python3 scripts/self_test.py
```

Require a `W-Pack self-test: PASS` result before packaging or distributing the Skill.
