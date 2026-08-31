---
name: w-pack
description: ChatGPT-native image generation and editing control layer that uses persistent Project references as the default visual source set, keeps reference roles bounded, preserves a single STYLE_CORE visual grammar, and conditionally performs one style-only recovery edit when a fresh result has acceptable structure but poor style fidelity. Use for fresh image generation, restyling, reference-guided edits, or requests involving reusable Project sources, character, pose, composition, proportion, item, or style fidelity.
---

# W-Pack

Use W-Pack as a Project-source-first control layer for ChatGPT image generation. Keep normal interaction conversational; keep authority resolution, auditing, and recovery logic internal.

## Core workflow

1. Resolve `FRESH` vs `EDIT`.
2. Activate persistent Project sources by default using `default_source_profile`, otherwise `DEFAULT` when present.
3. Treat current-chat images as optional per-request overrides or additions, not as the primary source path.
4. Assign bounded roles: `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, `ITEM`.
5. Resolve exactly one active `STYLE` authority as `STYLE_CORE` when possible. If an explicit inline STYLE overrides the Project STYLE, promote the inline STYLE to `STYLE_CORE` for that request.
6. Compile the first pass as `FRESH_FIRST` for new images. Preserve the STYLE_CORE medium and global visual grammar.
7. Generate one fresh candidate.
8. Audit structure and style separately.
9. If structure passes and style fails, run exactly one `SINGLE_RESTYLE` recovery using only the fresh candidate as `STRUCTURE_EDIT_TARGET` and the active `STYLE_CORE` as the sole style authority.
10. Never recursively restyle. Never run an automatic third image-generation pass. If the recovery still fails, stop the automatic chain; the next retry must begin fresh from the original sources.

Read `references/style-recovery-policy.md` before applying the two-stage path. Read `references/source-profiles.md`, `references/authority-model.md`, `references/generation-policy.md`, `references/edit-policy.md`, and `references/audit-policy.md` as needed.

## Persistent sources

Project sources are active by default. The user does not need to repeat "use the sources".

Precedence:

1. Explicit user instruction for the current request.
2. Explicit current-chat reference override.
3. Explicitly named source profile.
4. Manifest `default_source_profile`.
5. Profile named `DEFAULT`.

Disable default Project sources only when the user explicitly asks to ignore them or the internal request has `use_default_sources=false`.

If an explicit reference claims a role already supplied by the active Project profile, replace that default role for the current request unless the user clearly asks to combine both.

## STYLE_CORE

Treat one active STYLE authority as the global visual grammar anchor.

Preserve its:

- visual medium and rendering domain
- stylization level and degree of realism
- contour and edge behavior
- shape and feature abstraction
- shading and value structure
- color behavior
- texture and surface treatment
- background simplification or rendering behavior

Do not normalize a stylized or non-photographic STYLE_CORE into generic photorealism unless the user explicitly asks for photography or photorealism.

Camera and lens terms control framing, perspective, depth of field, or optical behavior. They do not override STYLE_CORE medium by themselves.

Default STYLE_CORE constraints:

- `style_fidelity`: `HIGH`
- `medium_lock`: `REFERENCE`
- `photorealism_normalization`: `DISABLED_UNLESS_EXPLICITLY_REQUESTED`
- `style_core_precedence`: `ABSOLUTE_FOR_GLOBAL_VISUAL_GRAMMAR`

STYLE_CORE must not copy reference identity, exact pose, exact composition, item identity, or unrelated scene content unless separately authorized.

## Conditional two-stage recovery

Do not make two-stage generation the default. The normal path is one fresh generation.

Run the recovery pass only when all are true:

- original mode is `FRESH`
- exactly one STYLE_CORE exists
- the fresh candidate's structure is acceptable
- style fidelity materially fails

Material style failure includes any of:

- visual medium class mismatch
- non-photographic source drifting into generic photorealism
- severe degree-of-realism mismatch
- clear global grammar drift across multiple style fingerprint axes

Do not use restyle to repair anatomy, scene, composition, missing objects, or other structural failures. Restart fresh on the next retry instead.

During `SINGLE_RESTYLE`:

- Image 1 / current candidate = `STRUCTURE_EDIT_TARGET`; it has no style authority.
- Project STYLE_CORE = sole style authority.
- Preserve subject identity, pose, composition, camera decision, spatial relationships, object count, physical contact, scene conditions, and exact text when present.
- Change rendering style only.
- Do not crop, mirror, zoom, rotate, add, remove, replace, duplicate, or redesign content.
- Perform one restyle pass maximum.

## Modes

Use `FRESH` for a new image or a new remake. Do not silently reuse prior candidates.

Use `EDIT` when the user explicitly targets an existing usable image for modification. `EDIT` may internally be `MODIFY`, `RESTYLE`, or `RECOMPOSE`, but the automatic `SINGLE_RESTYLE` recovery described above is reserved for a failed FRESH style audit.

## Internal first-pass contract

Use this logical shape internally:

```json
{
  "schema_version": "WPACK_GENERATION_REQUEST_v1.1",
  "mode": "FRESH",
  "scene": "...",
  "aspect_ratio": "4:5",
  "use_default_sources": true,
  "source_profile": null,
  "references": [],
  "composition": [],
  "lighting": [],
  "exact_text": null,
  "preserve": [],
  "avoid": [],
  "edit_target": null
}
```

The compiler emits `WPACK_COMPILED_REQUEST_v1.2` with a `workflow` block describing `FRESH_FIRST` and conditional recovery.

## Conflict handling

- Fail closed on incompatible authority claims.
- Keep reference count at 5 or fewer.
- Keep STYLE_CORE singular for automatic recovery. If multiple active STYLE authorities cannot be reduced to one clear core, disable automatic style recovery rather than guessing.
- Preserve exact user-specified text.
- Do not substitute unresolved Project authorities with visually similar files.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not require an API key, standalone image API, Codex OAuth, or a local GPU.

## Supporting resources

- `references/source-profiles.md` — persistent source activation and inline override rules.
- `references/authority-model.md` — bounded authority semantics and STYLE_CORE rules.
- `references/chat-intent-resolution.md` — conversational role and mode resolution.
- `references/generation-policy.md` — first-pass generation rules.
- `references/style-recovery-policy.md` — conditional fresh-to-single-restyle workflow.
- `references/edit-policy.md` — user-requested image editing.
- `references/audit-policy.md` — structure/style audit and recovery trigger.
- `references/project-setup.md` — recommended Project configuration.
- `references/authority-manifest.example.json` — default profile example.
- `references/generation-request.example.json` — first-pass request example.
- `scripts/validate_authorities.py` — manifest/request validation and default-source resolution.
- `scripts/compile_request.py` — first-pass compilation and style-recovery compilation.
- `scripts/self_test.py` — deterministic smoke tests.

## Verification

After modifying scripts, run:

```bash
python3 scripts/self_test.py
```

Require `W-Pack self-test: PASS` before packaging or distributing the Skill.
