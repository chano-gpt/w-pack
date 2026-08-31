# Generation Policy

## Compile before generation

Before image generation, internally compile scene, aspect ratio, resolved Project profile, references and bounded authority scopes, composition, lighting, exact text, preserve constraints, avoid constraints, generation mode, and edit target when editing.

## Persistent sources are default

Resolve the Project source profile before resolving optional inline references.

- If `use_default_sources` is false, skip automatic Project sources.
- Otherwise use an explicitly requested `source_profile` when present.
- Otherwise use manifest `default_source_profile`.
- Otherwise use a profile named `DEFAULT` when one exists.

Current-chat images are not the primary reference path. Treat them as explicit overrides or add-ons only when the user points to them or clearly assigns an influence.

When an explicit reference claims a role already supplied by the active Project profile, the explicit reference replaces the default authority for that role unless the user clearly requests additive combination.

## Style fidelity

An active `STYLE` authority defines the visual medium and rendering domain within its scope. Preserve palette, texture, lighting language, graphic treatment, rendering language, surface treatment, visual medium, stylization level, edge treatment, and degree of realism when those influences are authorized.

Do not convert a non-photographic STYLE reference into generic photorealism unless the user explicitly requests a photographic rendering style.

Photographic vocabulary such as camera brand, focal length, telephoto, depth of field, low angle, or high angle controls optical behavior, perspective, or composition. It does not change the reference medium by itself.

Default STYLE generation constraints:

- style fidelity: HIGH
- medium lock: REFERENCE
- photorealism normalization: DISABLED

## Fresh generation

`FRESH` is the default mode for new images and remakes. Do not silently use a previous generated candidate as an input.

## Edit generation

Use `EDIT` only when a usable existing target image is present and the user asks to modify, preserve, refine, restyle, continue, or recompose it. Read `edit-policy.md`.

## Reference selection

- Maximum 5 active generation references after default-profile expansion and explicit overrides.
- Prefer the configured persistent Project profile over ad hoc inline references.
- Do not add visually similar Project files merely because they appear relevant.
- If a requested Project authority cannot be resolved, state what is missing instead of substituting another image.

## Composition

Keep composition independent from STYLE. When the user requests framing, crop, camera angle, subject placement, hierarchy, negative space, or layout structure, use a COMPOSITION authority or direct composition constraints.

## Text

When exact text is specified, preserve spelling, capitalization, punctuation, and line content exactly.

## Preservation and avoidance

Compile explicit keep/preserve language into `preserve`. Compile explicit negative constraints into `avoid`. In EDIT mode, a request to change only one property is not permission to redesign unrelated properties.
