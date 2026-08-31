# Generation Policy

## First pass

Compile and generate one fresh candidate first. Do not perform two image-generation passes by default.

Resolve persistent sources before optional inline references. Resolve a singular STYLE authority as STYLE_CORE when possible.

## STYLE_CORE contract

Preserve the STYLE_CORE global visual grammar, including medium, stylization level, contour behavior, abstraction, shading/value structure, color behavior, texture, background rendering, and degree of realism.

Do not convert a non-photographic STYLE_CORE into generic photorealism unless explicitly requested.

Treat camera brand, focal length, telephoto, depth of field, low angle, or high angle as optical/composition instructions, not as a medium override.

## Freshness

`FRESH` means create a completely new integrated candidate from approved active authorities. Do not reuse prior generated candidates as hidden style inputs.

## Reference selection

- Maximum five first-pass generation references.
- Prefer the configured Project profile.
- Do not add visually similar Project files merely because they look relevant.
- Do not substitute missing named authorities.

## Composition

Keep composition independent from STYLE_CORE. User camera/framing instructions can modify layout while STYLE_CORE continues to control rendering grammar.

## Text

Preserve exact text spelling, capitalization, punctuation, and requested line content.

## Recovery handoff

After the fresh candidate, use `audit-policy.md`. Invoke `style-recovery-policy.md` only when structure passes and style fails.
