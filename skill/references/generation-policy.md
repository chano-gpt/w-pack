# Generation Policy

## Compile before generation

Before image generation, internally compile:

- scene
- aspect ratio
- references and bounded authority scopes
- composition constraints
- lighting constraints
- exact text
- preserve constraints
- avoid constraints
- generation mode
- edit target when editing
- requested source profile when present

Do not expose the compiled structure unless the user asks for it or a conflict needs explanation.

## Fresh generation

`FRESH` is the default mode for new images and new remakes from approved references.

A fresh run may use only the current user brief, explicitly resolved inline references, and explicitly requested Project authorities/source profiles. Do not silently use a previous generated candidate as an input.

A current-chat reference image is valid in FRESH mode when it is being used as a bounded STYLE, CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM authority rather than as an edit target.

## Edit generation

Use `EDIT` only when a usable existing target image is present and the user asks to modify, preserve, refine, restyle, continue, or recompose it. Read `edit-policy.md`.

## Reference selection

- Maximum 5 generation references.
- Prefer the minimum set required to satisfy the brief.
- Project authorities may be resolved from a manifest.
- Inline authorities may be resolved directly from current-chat images and do not require manifest membership.
- Do not add visually similar Project files merely because they appear relevant.
- When a user names a Project authority ID, resolve that ID before generation.
- If a requested Project authority cannot be resolved, state what is missing instead of substituting another image.

## Composition

Keep composition independent from STYLE. When the user requests a reference's framing, crop, camera angle, subject placement, visual hierarchy, negative space, or layout structure, use a COMPOSITION authority.

## Text

When exact text is specified, preserve spelling, capitalization, punctuation, and line content exactly. Layout may change unless the user explicitly fixes line breaks or placement.

## Preservation and avoidance

Compile explicit "keep", "그대로", "유지", and equivalent language into `preserve`. Compile explicit negative constraints into `avoid`. In EDIT mode, a request to change only one property should not be treated as permission to redesign unrelated properties.
