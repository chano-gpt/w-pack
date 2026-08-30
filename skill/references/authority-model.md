# Authority Model

Every generation reference has one primary authority role. A role limits what the reference may influence. Resolve roles from the user's explicit language or clearly stated intent, not from incidental image content.

## STYLE

Allowed: palette, texture, lighting language, typography character, graphic treatment, rendering language, surface treatment.

Forbidden by default: subject identity, exact pose, composition, item identity, factual scene content.

## CHARACTER

Allowed: identity, facial features, hair, stable appearance traits, clothing only when explicitly included in the authority scope.

Forbidden by default: background, lighting, camera angle, composition, graphic treatment, unrelated items.

## POSE

Allowed: body arrangement, gesture, stance, limb relationship, broad camera-relative orientation.

Forbidden by default: identity, wardrobe, environment, style, composition outside pose-dependent framing.

## COMPOSITION

Allowed: framing, crop, camera angle, subject placement, layout structure, visual hierarchy, negative space, broad spatial arrangement.

Forbidden by default: identity, facial features, wardrobe, global style, palette, item identity, exact factual content.

## PROPORTION

Allowed: physical scale, body-to-object ratio, object-to-object scale, framing-relevant relative dimensions.

Forbidden by default: identity, pose details, style, material appearance.

## ITEM

Allowed: specified object's identity, silhouette, key structural details, material and color when explicitly part of the item authority.

Forbidden by default: subject identity, pose, environment, global style, composition.

## Reference source types

- `PROJECT_AUTHORITY`: persistent Project reference, optionally governed by a manifest.
- `INLINE_AUTHORITY`: image attached or clearly identified in the current conversation. It may receive an ephemeral internal ID and does not require a manifest entry.

## Scope rules

- One image may serve multiple roles only when the user explicitly assigns or clearly requests multiple independent influences.
- Treat multiple roles as separate bounded authorities, not unrestricted permission for the image to control everything.
- When a Project manifest defines narrower `allowed_influence` or extra `forbidden_influence`, the narrower rule wins.
- Never copy incidental elements from a reference merely because they are visible.
- Natural-language cues such as "이 느낌으로", "이 포즈로", or "이 구도로" are valid role instructions when their referent is clear.
