# Edit Policy

Use `EDIT` when the user identifies an existing image target and asks to change, preserve, refine, restyle, or recompose it.

## Edit subtypes

- `MODIFY`: change selected properties while preserving unspecified target properties as much as practical.
- `RESTYLE`: preserve requested structure/content while changing visual language.
- `RECOMPOSE`: preserve selected subject or content while changing framing, layout, crop, or spatial arrangement.

These are internal classifications. Do not require the user to name them.

## Edit target

An EDIT request requires a usable existing image target in the current conversation or otherwise resolvable context. Do not invent or substitute an edit target.

The edit target is not automatically a STYLE, CHARACTER, or COMPOSITION authority. It is the image being modified. Any additional authority roles must be independently resolved from the user's instructions.

## Preservation

Convert explicit preservation language into `preserve` constraints. Examples:

- "얼굴 그대로" -> preserve identity and facial features
- "구도 유지" -> preserve framing and subject placement
- "배경은 그대로" -> preserve environment/background
- "텍스트 그대로" -> preserve exact text and line content when possible

When the user asks to change only one property, treat clearly unrelated target properties as preservation priorities rather than opportunities for redesign.

## Restyle leakage

A style reference may change only properties within STYLE scope. Do not allow it to replace the target identity, pose, factual objects, or composition unless the user separately authorizes those changes.

## Recompose

When recomposing, preserve only the subject/content properties the user names or clearly intends to keep. A COMPOSITION authority may guide framing, crop, layout, negative space, subject placement, and camera angle without controlling identity or global visual style.
