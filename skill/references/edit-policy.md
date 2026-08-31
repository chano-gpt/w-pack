# Edit Policy

Use `EDIT` only when a usable target image exists and the user asks to modify, preserve, refine, restyle, or recompose it.

User-requested EDIT is separate from W-Pack's automatic FRESH style-recovery path.

## Edit types

- `MODIFY`: change selected properties while preserving the rest.
- `RESTYLE`: preserve requested content/structure while changing visual language.
- `RECOMPOSE`: preserve requested content while changing framing/layout.

Default Project sources remain active in ordinary user-requested EDIT unless explicitly disabled. Same-role inline references override the corresponding Project role for that request.

Do not recursively edit without explicit user intent. A request to change one property is not permission to redesign unrelated properties.
