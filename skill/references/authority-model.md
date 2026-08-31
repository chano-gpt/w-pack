# Authority Model

Assign one primary bounded role to each active reference. Resolve authority from the Project manifest or explicit user intent, not incidental visual content. Authority scope does not prove visual transport; use `reference-transport.md` separately.

## STYLE family

Resolve active STYLE references as one `STYLE_CORE` plus zero to two `STYLE_SUPPORT` adapters. A single legacy STYLE without an explicit style role may be inferred as CORE. Multiple STYLE references must resolve explicitly to exactly one CORE.

### STYLE_CORE

Allowed: palette, texture, lighting language, typography character, graphic treatment, rendering language, surface treatment, visual medium, stylization level, contour/edge grammar, shape abstraction, value structure, color behavior, background rendering, degree of realism, and visible-hair rendering grammar.

Forbidden by default: identity, exact pose, exact composition, item identity, and unrelated factual scene content.

STYLE_CORE has absolute precedence for global visual grammar while remaining bounded against content leakage. `visual_medium`, `degree_of_realism`, and `shape_abstraction` are core-only axes.

### STYLE_SUPPORT

A STYLE_SUPPORT is a bounded adapter, not a second global style. It may influence only declared `support_domains`, such as color behavior, value structure, surface treatment, background rendering, edge treatment, or hair rendering grammar.

STYLE_SUPPORT must not override STYLE_CORE medium, realism level, shape abstraction, or any explicit conflicting core decision.

## CHARACTER

Allowed: identity, facial features, hairstyle geometry, hair color/length, stable appearance traits, and explicitly scoped wardrobe.

Forbidden by default: background, global lighting, camera angle, composition, global style, and unrelated items.

Separate hairstyle geometry from hair rendering grammar. CHARACTER controls what the hair is; STYLE controls how the hair is rendered unless the user explicitly says otherwise.

## POSE

Allowed: body arrangement, gesture, stance, limb relationships, and camera-relative orientation.

Forbidden by default: identity, wardrobe, environment, global style, and unrelated composition.

## COMPOSITION

Allowed: framing, crop, camera angle, subject placement, layout structure, hierarchy, negative space, and broad spatial arrangement.

Forbidden by default: identity, facial features, wardrobe, global style, palette, and item identity.

## PROPORTION

Allowed: physical scale and relative dimensions.

Forbidden by default: identity, detailed pose, global style, and material appearance.

## ITEM

Allowed: specified object identity, silhouette, structural details, material, and explicitly scoped color.

Forbidden by default: subject identity, pose, environment, global style, and composition.

## Recovery boundary

During automatic `SINGLE_RESTYLE`, use:

1. `STRUCTURE_EDIT_TARGET` — the fresh candidate; controls content and geometry only.
2. `STYLE_CORE` — controls global rendering grammar.
3. Optionally one `STYLE_SUPPORT` — only when its support domains intersect the style-audit failure axes.

Do not send CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM sources into the recovery pass. Their successful output is already embodied in the structure target.
