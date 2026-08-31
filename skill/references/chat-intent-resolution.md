# Chat Intent Resolution

Use natural conversational language. Do not require users to write authority IDs, schemas, profiles, or workflow names when intent is clear.

## Mode

Choose `FRESH` for new generation or a new remake. Choose `EDIT` when the user targets an existing usable image for modification.

## Default Project sources

Persistent Project sources are active by default. Phrases such as "소스 참고", "use the project sources", or equivalents merely confirm the default.

Phrases meaning "without references", "ignore project sources", or "prompt only" disable automatic Project sources for that request.

## Authority cues

| User intent | Authority |
| --- | --- |
| same visual feel / same style / same rendering | STYLE |
| keep this person / same character | CHARACTER |
| use this pose / stance | POSE |
| use this composition / framing | COMPOSITION |
| keep these proportions / scale | PROPORTION |
| keep this outfit / product / object | ITEM |

Equivalent language in any language should map the same way.

## Inline references

An inline image is optional and secondary.

- Activate it when explicitly referenced or when its intended role is clear.
- For non-STYLE roles, replace the same default Project role for the current request unless combination is explicitly requested.
- By default, an explicit inline STYLE replaces the entire Project STYLE family for that request.
- If the inline STYLE is the only active STYLE, infer it as STYLE_CORE.
- Combine Project and inline STYLE only when the user explicitly asks to mix/combine styles; then set `combine_style_sources=true` and keep exactly one CORE plus bounded SUPPORT sources.
- Do not infer unrestricted influence from the whole image.

## Hair intent

Treat hairstyle requests and hair-rendering requests separately when possible.

- length, parting, fringe, curl pattern, tied/untied state, and overall silhouette are primarily CHARACTER/structure intent.
- strand density, flyaways, tip behavior, lock grouping, edge softness, and highlight granularity are hair rendering grammar and normally belong to STYLE.

Explicit user wording overrides the default `CLEAN_MASS` fallback.

## Recovery intent

Automatic style recovery does not require the user to ask for "two stages". It is an internal fallback only after a fresh candidate has acceptable structure but materially fails style fidelity, with exactly one usable STYLE_CORE.
