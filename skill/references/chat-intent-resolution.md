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
- Replace the same default role for the current request unless combination is explicit.
- If inline STYLE replaces Project STYLE, promote it to STYLE_CORE internally.
- Do not infer unrestricted influence from the whole image.

## Recovery intent

Automatic style recovery does not require the user to ask for "two stages". It is an internal fallback only after a fresh candidate has acceptable structure but materially fails STYLE_CORE fidelity.
