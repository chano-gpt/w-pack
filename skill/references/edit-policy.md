# Edit Policy

Use `EDIT` only when a usable target image exists and the user asks to modify, preserve, refine, restyle, continue, or recompose it.

## Edit types

- `MODIFY`: change selected properties while preserving the rest.
- `RESTYLE`: preserve selected content or structure while changing visual language.
- `RECOMPOSE`: preserve selected content while changing framing or layout.

## Project sources during edits

The default Project source profile remains active during EDIT unless the user explicitly disables Project sources. Explicit edit instructions still have higher priority than Project defaults.

If an inline reference is explicitly assigned to a role that also exists in the default Project profile, use the inline reference as the per-request override for that role unless the user requests combination.

Do not treat an edit target itself as unrestricted authority over all properties. Preserve only what the user asked to preserve or what the edit type logically requires.
