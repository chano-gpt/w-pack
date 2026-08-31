# W-Pack Project Instructions

Use W-Pack for image generation and image editing in this Project.

## Default sources

Persistent Project sources are the primary reference path and are active by default.

- Activate manifest `default_source_profile` automatically.
- If no explicit default is set but `DEFAULT` exists, activate `DEFAULT`.
- Do not require the user to repeat "use the sources".
- Treat current-chat images as temporary overrides or additions.
- Disable Project sources only when the user explicitly requests prompt-only generation or no references.

## Authority roles

Keep references bounded as STYLE, CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM.

When exactly one STYLE is active, treat it internally as `STYLE_CORE`. STYLE_CORE controls global visual grammar but not identity, exact pose, exact composition, item identity, or unrelated scene content.

Preserve STYLE_CORE medium, stylization level, contour/edge behavior, shape abstraction, shading/value structure, color behavior, texture/surface treatment, background rendering, and degree of realism.

Do not let camera or lens terminology turn a non-photographic STYLE_CORE into generic photorealism unless the user explicitly asks for photography or photorealism.

## Web workflow

For a new image:

1. Generate one FRESH candidate from the normal Project sources.
2. Audit structure and style separately.
3. If structure passes and style fails, perform exactly one style-only recovery edit.
4. In recovery, use only the fresh candidate as `STRUCTURE_EDIT_TARGET` and STYLE_CORE as the sole style authority.
5. Preserve content, identity, pose, composition, camera, spatial relationships, object count/contact, scene conditions, and exact text.
6. Never recursively restyle and never perform an automatic third image-generation pass.

Do not use the recovery pass to fix structural failures. A later retry must restart from a fresh chain.

Use ChatGPT built-in image generation. Do not ask for an API key, Codex OAuth, or local GPU runtime.
