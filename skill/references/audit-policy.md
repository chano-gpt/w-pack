# Audit Policy

Audit generated candidates silently unless a material failure must be surfaced.

## Fresh candidate audit

Evaluate two independent statuses.

### Structure status

Set `PASS` only when the requested subject/content, pose, composition, camera, spatial relationships, object count, scale/contact, scene conditions, and exact text requirements are materially acceptable.

### Style status

Compare the output with STYLE_CORE across these fingerprint axes:

1. visual medium / rendering domain
2. degree of realism
3. contour and edge grammar
4. shape and feature abstraction
5. shading and value structure
6. color behavior
7. texture and surface treatment
8. background simplification/rendering behavior
9. hair rendering grammar when visible human hair is materially present

For hair, inspect silhouette noise, lock grouping, micro-strand density, split/forked tip behavior, face-crossing wisps, highlight granularity, gravity flow, and agreement with the active STYLE or CHARACTER source.

Set style to `FAIL` immediately for a visual-medium class mismatch or non-photographic-to-generic-photoreal drift. Otherwise treat clear drift across at least three fingerprint axes as material style failure.

Hair is a high-salience exception: if the hairstyle geometry is structurally acceptable but the rendering clearly falls back to dense flyaway halos, repeatedly split filament tips, random face-crossing wisps, or bright thread-like strand highlights contrary to the active source or `CLEAN_MASS` fallback, set `style_status=FAIL` even when fewer than three other axes fail.

## Recovery decision

- Structure PASS + Style PASS -> finish.
- Structure PASS + Style FAIL + singular STYLE_CORE -> `SINGLE_RESTYLE` once.
- Structure FAIL -> do not restyle; automatic chain ends.
- Ambiguous/multiple STYLE authorities -> do not guess a recovery core; automatic chain ends.

## Recovery candidate audit

Check:

- STYLE_CORE fidelity improved materially.
- Hair rendering grammar improved when it was a failed axis, without changing hairstyle geometry.
- Structure target identity/content/geometry remained intact.
- No crop/recompose/object/content leakage occurred.

Never run another automatic restyle or a third image-generation pass.
