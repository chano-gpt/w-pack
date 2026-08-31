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

Set style to `FAIL` immediately for a visual-medium class mismatch or non-photographic-to-generic-photoreal drift. Otherwise treat clear drift across at least three fingerprint axes as material style failure.

## Recovery decision

- Structure PASS + Style PASS -> finish.
- Structure PASS + Style FAIL + singular STYLE_CORE -> `SINGLE_RESTYLE` once.
- Structure FAIL -> do not restyle; automatic chain ends.
- Ambiguous/multiple STYLE authorities -> do not guess a recovery core; automatic chain ends.

## Recovery candidate audit

Check:

- STYLE_CORE fidelity improved materially.
- Structure target identity/content/geometry remained intact.
- No crop/recompose/object/content leakage occurred.

Never run another automatic restyle or a third image-generation pass.
