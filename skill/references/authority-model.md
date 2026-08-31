# Authority Model

Assign one primary bounded role to each active reference. Resolve authority from the Project manifest or explicit user intent, not incidental visual content.

## STYLE / STYLE_CORE

Allowed: palette, texture, lighting language, typography character, graphic treatment, rendering language, surface treatment, visual medium, stylization level, contour and edge behavior, shape abstraction, value structure, color behavior, background rendering behavior, and degree of realism.

Forbidden by default: identity, exact pose, exact composition, item identity, and unrelated factual scene content.

When exactly one STYLE authority is active, treat it as `STYLE_CORE` internally. STYLE_CORE has absolute precedence for global visual grammar while remaining bounded against content leakage.

## CHARACTER

Allowed: identity, facial features, hair, stable appearance traits, and explicitly scoped wardrobe.

Forbidden by default: background, global lighting, camera angle, composition, global style, and unrelated items.

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

During automatic `SINGLE_RESTYLE`, use exactly two conceptual authorities:

- `STRUCTURE_EDIT_TARGET`: the fresh candidate; controls content and geometry only.
- `STYLE_CORE`: controls rendering grammar only.

Do not send CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM sources into the recovery pass. Their successful output is already embodied in the structure target.
