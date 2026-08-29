# Generation Policy

## Compile before generation

Before image generation, internally compile the request into these fields:

- scene_intent
- aspect_ratio
- exact_text
- authorities
- composition_constraints
- lighting_constraints
- must_preserve
- must_avoid
- generation_mode

Do not expose the compiled structure unless the user asks for it.

## Fresh generation

`fresh` is the default generation mode.

A fresh run may use only the user brief and currently approved authorities. Do not silently use a previous generated candidate as a style or structure reference.

## Staged restyle

A previous generated candidate may be used only when the user explicitly asks to edit, restyle, refine, preserve, or continue that candidate.

For staged restyle:

- treat the candidate as `STRUCTURE_EDIT_TARGET`, not as a general style authority;
- separately identify any STYLE authority;
- preserve requested structure while limiting style influence to the STYLE authority;
- do not recursively restyle a restyled candidate unless the user explicitly asks again.

## Reference selection

- Maximum 5 generation references.
- Prefer the minimum set required to satisfy the brief.
- Do not add visually similar Project files merely because they appear relevant.
- When a user names an authority ID, resolve that ID before generation.
- If the requested authority cannot be resolved to an available Project file or current conversation image, state what is missing instead of substituting another image.

## Text

When exact text is specified, preserve spelling, capitalization, punctuation, and line content exactly. Layout may change unless the user explicitly fixes line breaks.
