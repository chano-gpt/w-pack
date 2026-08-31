# Audit Policy

Audit generated candidates silently unless a material failure must be surfaced.

## Fresh candidate audit

Evaluate structure and style independently. Also verify whether the reference transport assumptions used by the request remain credible; do not convert an unverified Project source into a claim of direct visual binding after the fact.

### Structure status

Set `PASS` only when the requested subject/content, pose, composition, camera, spatial relationships, object count, scale/contact, scene conditions, hairstyle geometry, and exact text requirements are materially acceptable.

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

Audit each STYLE_SUPPORT only inside its declared `support_domains`. A support mismatch must not be interpreted as permission to replace STYLE_CORE grammar.

For hair, inspect silhouette noise, lock grouping, micro-strand density, split/forked tip behavior, face-crossing wisps, highlight granularity, gravity flow, and agreement with the active STYLE or CHARACTER source.

Set style to `FAIL` immediately for a visual-medium class mismatch or non-photographic-to-generic-photoreal drift. Otherwise treat clear drift across at least three fingerprint axes as material style failure.

Hair is a high-salience exception: if hairstyle geometry is structurally acceptable but rendering clearly falls back to dense flyaway halos, repeatedly split filament tips, random face-crossing wisps, or bright thread-like strand highlights contrary to the active source or `CLEAN_MASS` fallback, set `style_status=FAIL` even when fewer than three other axes fail.

## Recovery decision

- Structure PASS + Style PASS -> finish.
- Structure PASS + Style FAIL + exactly one STYLE_CORE + (`VISUAL_BOUND` or usable STYLE DNA) -> `SINGLE_RESTYLE` once.
- Add at most one STYLE_SUPPORT in recovery, and only when its `support_domains` intersect `failure_axes`.
- Structure FAIL -> do not restyle; automatic chain ends.
- Unresolved STYLE family, missing usable STYLE_CORE, or unavailable style transport/profile -> do not guess; automatic chain ends.

## Recovery candidate audit

Check:

- STYLE_CORE fidelity improved materially.
- Any included STYLE_SUPPORT stayed inside its declared domains.
- Hair rendering grammar improved when it was a failed axis, without changing hairstyle geometry.
- Structure target identity/content/geometry remained intact.
- No crop/recompose/object/content leakage occurred.

Never run another automatic restyle or a third image-generation pass.
