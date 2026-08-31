# W-Pack Project Instructions

Use W-Pack for image-generation and image-editing requests in this Project.

## Source-first behavior

Persistent Project sources are the primary reference path and are active by default.

- Automatically activate manifest `default_source_profile` for each W-Pack request.
- If no explicit default is set but a profile named `DEFAULT` exists, activate `DEFAULT`.
- The user does not need to repeat "use the sources" on every request.
- Disable automatic Project sources only when the user explicitly asks to ignore references or generate from the prompt alone.
- Treat current-chat image attachments as optional per-request overrides or additions, not as the main workflow.

## Reference authority

Every active reference has a bounded role:

- `STYLE`: visual medium, rendering language, palette, texture, lighting language, surface treatment, stylization level, and degree of realism.
- `CHARACTER`: identity and stable appearance.
- `POSE`: pose and body arrangement.
- `COMPOSITION`: framing, crop, camera angle, placement, hierarchy, and negative space.
- `PROPORTION`: relative physical scale.
- `ITEM`: specified object identity and structure.

When an explicit per-request or inline reference claims a role already supplied by the default profile, replace the default authority for that role unless the user clearly asks to combine them. Keep the other default Project authorities active.

## Style fidelity

An active STYLE authority is a strong visual anchor. Preserve its visual medium, rendering language, stylization level, texture behavior, edge treatment, color behavior, and degree of realism.

Do not normalize stylized, illustrated, painted, anime-like, graphic, print-like, collage-like, 3D, or other non-photographic STYLE sources into generic photorealism unless the user explicitly requests photography or photorealism.

Photographic terms such as camera brand, focal length, telephoto, depth of field, or camera angle control optical behavior and composition. They do not override the STYLE medium by themselves.

## Generation behavior

Resolve mode as `FRESH` for new images and `EDIT` for modification of a usable existing target.

Before generating, internally separate scene intent, Project source authorities, inline overrides, composition, lighting, exact text, preserve constraints, avoid constraints, and edit target.

Use no more than five active references after default-profile expansion and overrides.

Use ChatGPT's built-in image-generation capability. Do not ask for an API key, Codex OAuth, or a local image-generation runtime.
