# Authority Model

Every generation reference has one primary authority role. The role limits what the reference may influence.

## STYLE

Allowed: palette, texture, lighting language, typography character, graphic treatment, rendering language, surface treatment.

Forbidden by default: subject identity, exact pose, exact composition, item identity, factual scene content.

## CHARACTER

Allowed: identity, facial features, hair, stable appearance traits, clothing only when explicitly included in the authority scope.

Forbidden by default: background, lighting, camera angle, composition, graphic treatment, unrelated items.

## POSE

Allowed: body arrangement, gesture, stance, limb relationship, broad camera-relative orientation.

Forbidden by default: identity, wardrobe, environment, style, lighting.

## PROPORTION

Allowed: physical scale, body-to-object ratio, object-to-object scale, framing-relevant relative dimensions.

Forbidden by default: identity, pose details, style, material appearance.

## ITEM

Allowed: specified object's identity, silhouette, key structural details, material and color when explicitly part of the item authority.

Forbidden by default: subject identity, pose, environment, global style.

## Scope rules

- One file may be referenced more than once only when the user explicitly assigns multiple roles.
- Multiple roles must be treated as separate scoped authorities, not as unrestricted permission for the image to influence everything.
- When the manifest defines narrower `allowed_influence` or additional `forbidden_influence`, the narrower rule wins.
- Never copy incidental elements from a reference merely because they are visible.
