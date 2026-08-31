---
name: w-pack
description: ChatGPT-native control layer for image generation and editing with persistent Project references as the default visual source set and current-chat images as optional overrides or add-ons. Use when a user asks ChatGPT to create, restyle, modify, or refine an image with reusable Project sources or explicitly attached references, including requests about style, character, pose, composition, proportion, or item fidelity.
---

# W-Pack

Use W-Pack as a lightweight control layer for ChatGPT web and ChatGPT Projects. Treat persistent Project sources as the primary reference path. Treat current-chat image attachments as optional overrides or additions, not as the default workflow.

## Core workflow

1. Determine whether the request is `FRESH` or `EDIT`.
2. Resolve persistent Project sources first. If the manifest defines `default_source_profile`, activate it automatically. Otherwise activate a profile named `DEFAULT` when it exists.
3. Disable default Project sources only when the user explicitly requests generation without sources or the request sets `use_default_sources` to false.
4. Resolve current-chat references only when the user explicitly points to them or clearly assigns an influence. Inline images are secondary to the persistent Project source set.
5. Assign bounded roles: `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, and `ITEM`.
6. When an explicit inline or per-request reference claims a role already supplied by the default profile, treat the explicit reference as an override for that role unless the user clearly asks to combine both.
7. Compile scene intent, aspect ratio, composition, lighting, text, preserve constraints, avoid constraints, edit target, active profile, and selected references.
8. Apply style fidelity rules before generation. An active `STYLE` authority controls the visual medium and rendering domain, not merely colors.
9. Validate reference count and authority conflicts. Use no more than 5 generation references.
10. Invoke ChatGPT's built-in image-generation capability immediately when the request is sufficiently specified.
11. Audit the result silently and surface only material failures.

Read `references/source-profiles.md` for default-source behavior, `references/authority-model.md` for authority boundaries, `references/generation-policy.md` for style fidelity and fresh generation, `references/edit-policy.md` for editing, and `references/chat-intent-resolution.md` for natural-language mapping.

## Default Project sources

Persistent Project sources are active by default. The user does not need to say "use the sources" on every request.

Use this precedence:

1. Explicit per-request user instructions.
2. Explicit current-chat reference overrides.
3. Explicitly requested source profile.
4. Manifest `default_source_profile`.
5. A profile named `DEFAULT` when present.

A phrase equivalent to "use the sources" confirms the already-default behavior. A phrase equivalent to "without references" or "ignore project sources" disables the default source set for that request.

Do not automatically promote every current-chat image to a generation reference. An attachment becomes active only when the user points to it or its intended role is clear from the request.

## Style fidelity and medium lock

When an active reference has role `STYLE`, preserve its visual medium, rendering language, stylization level, texture behavior, edge treatment, color behavior, surface treatment, and degree of realism within the allowed scope.

Do not normalize a stylized, illustrated, painted, anime-like, graphic, print-like, collage-like, 3D, or otherwise non-photographic STYLE reference into generic photorealism unless the user explicitly requests a photographic rendering style.

Treat photographic terms such as lens length, camera brand, depth of field, low angle, high angle, or telephoto as composition or optical-behavior instructions. They do not override a non-photographic STYLE medium unless the user explicitly asks for photorealism or photography.

Default internal behavior when STYLE is active:

- `style_fidelity`: `HIGH`
- `medium_lock`: `REFERENCE`
- `photorealism_normalization`: `DISABLED`

## Reference roles

- `STYLE`: palette, texture, lighting language, typography character, graphic treatment, rendering language, surface treatment, visual medium, stylization level, and degree of realism.
- `CHARACTER`: identity, facial features, hair, stable appearance traits, and explicitly scoped wardrobe.
- `POSE`: body arrangement, gesture, stance, limb relationship, and camera-relative orientation.
- `COMPOSITION`: framing, crop, camera angle, subject placement, layout structure, visual hierarchy, negative space, and broad spatial arrangement.
- `PROPORTION`: physical scale and relative dimensions.
- `ITEM`: specified object identity, silhouette, structure, material, and scoped color.

Keep the roles bounded. A STYLE authority does not silently control identity or exact composition, and a CHARACTER authority does not silently control the global rendering style.

## Modes

Use `FRESH` for new images and new remakes. Do not silently reuse a previous generated candidate as an input.

Use `EDIT` when the user points to a usable existing target and asks to modify, preserve, refine, restyle, continue, or recompose it. Inside `EDIT`, use `MODIFY`, `RESTYLE`, or `RECOMPOSE` internally when helpful.

## Internal request contract

Use this logical shape before generation. Keep it internal unless the user asks to inspect it.

```json
{
  "schema_version": "WPACK_GENERATION_REQUEST_v1.1",
  "mode": "FRESH",
  "scene": "...",
  "aspect_ratio": "4:5",
  "use_default_sources": true,
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

## Conflict handling

- Let explicit user instructions override Project defaults when compatible with safety and tool constraints.
- When an explicit reference replaces a default authority for the same role, remove the default authority for that role before generation unless the user asks to combine them.
- If two active references still incompatibly claim the same property, surface the specific conflict instead of guessing.
- Preserve exact user-specified image text, including spelling, capitalization, punctuation, and line content.
- If a named Project authority cannot be resolved, state what is missing instead of substituting a visually similar file.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not request API keys, standalone image APIs, Codex OAuth, or a local GPU.

## Supporting resources

- `references/source-profiles.md` - default persistent source selection and override behavior.
- `references/authority-model.md` - authority semantics and influence boundaries.
- `references/chat-intent-resolution.md` - natural-language role and mode resolution.
- `references/generation-policy.md` - fresh generation, style fidelity, and medium lock.
- `references/edit-policy.md` - edit-target and preservation rules.
- `references/audit-policy.md` - post-generation review rules.
- `references/project-setup.md` - recommended ChatGPT Project configuration.
- `references/authority-manifest.example.json` - persistent Project-authority and default-profile template.
- `references/generation-request.example.json` - request template.
- `scripts/validate_authorities.py` - deterministic manifest/request validation.
- `scripts/compile_request.py` - deterministic default-profile resolution and request compilation.
- `scripts/self_test.py` - smoke tests for default sources, inline overrides, style locks, and edit flows.

## Script verification

When modifying the Skill scripts, run:

```bash
python3 scripts/self_test.py
```

Require `W-Pack self-test: PASS` before packaging or distributing the Skill.
