# Authority Model

Every active generation reference has one primary authority role. A role limits what the reference may influence. Resolve roles from the Project manifest or the user's explicit intent, not from incidental visual content.

## STYLE

Allowed: palette, texture, lighting language, typography character, graphic treatment, rendering language, surface treatment, visual medium, stylization level, edge treatment, and degree of realism.

Forbidden by default: subject identity, exact pose, exact composition, item identity, and unrelated factual scene content.

A STYLE authority is a strong visual anchor. When active, preserve the reference medium and rendering domain. Do not normalize a non-photographic reference into generic photorealism unless the user explicitly requests photography or photorealism.

## CHARACTER

Allowed: identity, facial features, hair, stable appearance traits, and wardrobe only when explicitly scoped.

Forbidden by default: background, global lighting, camera angle, composition, global graphic treatment, and unrelated items.

## POSE

Allowed: body arrangement, gesture, stance, limb relationship, and broad camera-relative orientation.

Forbidden by default: identity, wardrobe, environment, style, and composition outside pose-dependent framing.

## COMPOSITION

Allowed: framing, crop, camera angle, subject placement, layout structure, hierarchy, negative space, and broad spatial arrangement.

Forbidden by default: identity, facial features, wardrobe, global style, palette, item identity, and exact factual content.

## PROPORTION

Allowed: physical scale, body-to-object ratio, object-to-object scale, and framing-relevant relative dimensions.

Forbidden by default: identity, pose details, style, and material appearance.

## ITEM

Allowed: specified object identity, silhouette, key structural details, material, and color when explicitly scoped.

Forbidden by default: subject identity, pose, environment, global style, and composition.

## Scope rules

- Project authorities may be automatically activated through the default source profile.
- Current-chat authorities are optional and secondary.
- If an explicit per-request authority claims the same role as a default Project authority, it overrides that default role unless the user asks to combine them.
- Never copy incidental elements merely because they are visible.
