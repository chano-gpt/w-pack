# Style Recovery Policy

Use this policy only as a conditional recovery after a FRESH generation.

## Trigger

Run `SINGLE_RESTYLE` only when:

- mode was `FRESH`
- exactly one STYLE_CORE is active
- `structure_status=PASS`
- `style_status=FAIL`

Do not recover with restyle when structure fails. Structure includes required subject/content, composition, camera, pose, geometry, object count, contact, scene conditions, hairstyle geometry, and exact text placement/content when relevant.

## Recovery references

Use exactly:

1. `STRUCTURE_EDIT_TARGET` — the fresh candidate, with no style authority.
2. `STYLE_CORE` — the sole style authority.

Do not include other Project or inline authorities in the restyle pass.

## Preservation

Preserve the structure target's:

- subject identity and stable appearance
- pose and body arrangement
- composition, crop, camera angle, and spatial relationships
- object count, scale, ownership, contact, and scene conditions
- hairstyle geometry: length, parting, fringe/bang shape, volume, direction, and major lock placement
- exact text content when present

## Allowed change

Change rendering style only. Apply STYLE_CORE global visual grammar across subject and background.

When hair rendering is a failed axis, change only its rendering grammar: lock grouping, strand density, silhouette noise, tip branching, flyaway density, and highlight granularity. Preserve the hairstyle itself.

Use the compact positive hair clause from `hair-rendering-policy.md` unless the STYLE_CORE clearly requires another grammar.

## Prohibited changes

Do not recompose, crop, rotate, mirror, zoom, add, remove, replace, duplicate, redesign, or reinterpret scene content. Do not invent a new hairstyle while fixing hair rendering.

## Pass limit

- maximum restyle depth: 1
- recursive restyle: forbidden
- automatic third generation/edit pass: forbidden
- automatic fresh retry after recovery failure: forbidden

If recovery fails, the next retry must begin a new FRESH chain from original Project sources and the original brief.
