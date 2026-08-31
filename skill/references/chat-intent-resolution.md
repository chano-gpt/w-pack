# Chat Intent Resolution

Use conversational language as the primary interface. Do not force users to write authority IDs, JSON, profile names, or mode names when their intent is already clear.

## Mode resolution

Choose `FRESH` for new generation or a new remake. Choose `EDIT` when the user points to an existing target and asks to preserve, modify, refine, restyle, continue, or recompose it.

## Default source intent

Persistent Project sources are already active by default. Phrases meaning "use the source", "refer to the source", or "use the project references" confirm the default and do not require a special activation step.

Phrases meaning "without references", "ignore project sources", or "make it from the prompt only" disable automatic Project sources for that request.

## Authority cue mapping

Map explicit intent to roles:

| User intent | Authority |
| --- | --- |
| same visual feel / same style / use the color treatment | STYLE |
| keep this person / keep the face / same character | CHARACTER |
| use this pose / copy the stance | POSE |
| use this composition / use this framing | COMPOSITION |
| use these proportions / keep the size relationship | PROPORTION |
| keep this outfit / product / object | ITEM |

Equivalent language in any language should be treated the same way.

## Inline references

A current-conversation image can be used without a manifest, but it is optional and secondary to Project sources.

- If the user explicitly assigns an inline image to a role, activate it.
- If that role exists in the default Project profile, replace the default authority for that role for this request unless the user asks to combine them.
- If the role differs, add the inline authority when the reference limit permits.
- Do not infer unrestricted influence from the entire inline image.
- Do not promote an unmentioned attachment into the main source set.

## Editing precedence

When the user both preserves properties and asks for a change, preserve the named properties and change only the requested properties.
