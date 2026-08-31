# W-Pack Project Instructions

Use W-Pack for image generation and image editing in this Project.

## Default sources

Persistent Project sources are the primary reusable catalog and are active by default.

- Activate manifest `default_source_profile` automatically.
- If no explicit default is set but `DEFAULT` exists, activate `DEFAULT`.
- Do not require the user to repeat "use the sources".
- Treat current-chat images as temporary overrides or explicitly requested additions.
- Disable Project sources only when the user explicitly requests prompt-only generation or no references.

## Authority and transport

Keep references bounded as STYLE, CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM.

Authority selection and visual transport are separate. A Project file being present does not prove that the image-generation model received it as a visual reference. Prefer confirmed direct visual binding; otherwise derive a bounded text profile when the source is inspectable, and do not claim exact visual fidelity from text-only fallback.

## STYLE family

Resolve STYLE as exactly one `STYLE_CORE` plus zero to two `STYLE_SUPPORT` adapters.

STYLE_CORE controls global visual grammar: medium, degree of realism, contour/edge grammar, shape abstraction, shading/value structure, color behavior, texture/surface treatment, background rendering, and visible-hair rendering grammar.

STYLE_SUPPORT may influence only declared support domains and must never override STYLE_CORE medium, realism level, or shape abstraction.

By default, an explicit current-chat STYLE replaces the Project style family. Combine them only when the user explicitly requests it.

## Hair rendering

When visible human hair is present, avoid the generic unconstrained micro-strand signature unless the user or source explicitly requires it.

Default fallback: build hair from silhouette -> major grouped locks -> internal texture -> sparse micro-strands. Prefer a clean continuous silhouette, grouped ends, natural gravity flow, lock-level highlights, and only a few physically plausible flyaways. Avoid dense flyaway halos, repeatedly forked tips, random face-crossing wisps, and thread-like highlights.

Preserve intentionally messy, frizzy, wet, windblown, curly, braided, or strand-heavy hair when the authoritative source shows it.

## Web workflow

For a new image:

1. Resolve authorities, STYLE family, and transport state.
2. Generate one FRESH candidate.
3. Audit structure and style separately, including hair rendering when visible.
4. If structure passes and style fails, perform at most one style-only recovery edit.
5. In recovery, use `STRUCTURE_EDIT_TARGET` + `STYLE_CORE` + optional one relevant `STYLE_SUPPORT`.
6. Preserve content, identity, pose, composition, camera, spatial relationships, object count/contact, scene conditions, hairstyle geometry, and exact text.
7. Never recursively restyle and never perform an automatic third image-generation pass.

Automatic recovery requires STYLE_CORE to be visually bound or backed by usable STYLE DNA. Do not use the recovery pass to fix structural failures.

Use ChatGPT built-in image generation. Do not ask for an API key, standalone image API, Codex OAuth, or local GPU runtime.
