---
name: w-pack
description: ChatGPT-native control layer for image generation and image editing with bounded reference-image influence. Use when a user asks ChatGPT to create, restyle, modify, or refine an image using current-chat uploads or reusable Project references, especially with natural-language cues such as "이 느낌으로", "이 사람 그대로", "이 포즈로", "이 구도로", "소스 참고해서", or equivalent requests that need style, character, pose, composition, proportion, or item references kept separate.
---

# W-Pack

Use W-Pack as a lightweight control layer for ChatGPT web and ChatGPT Projects. Optimize for natural conversation first; keep manifests and compiled request objects internal unless they are needed for validation or the user asks to see them.

## Core workflow

1. Determine whether the request is `FRESH` or `EDIT` from the user's intent.
2. Resolve only references the user explicitly names, clearly points to, or requests through an explicit Project source profile.
3. Resolve authority roles from the user's language and context, not from incidental visual content. Supported roles are `STYLE`, `CHARACTER`, `POSE`, `COMPOSITION`, `PROPORTION`, and `ITEM`.
4. Accept both persistent Project authorities and current-conversation inline authorities. Do not require an inline upload to exist in a Project manifest.
5. Internally compile scene intent, composition, lighting, text, preserve constraints, avoid constraints, edit target, and selected references.
6. Validate reference count and authority conflicts. Use no more than 5 generation references and prefer the minimum necessary set.
7. Invoke ChatGPT's built-in image-generation capability immediately when the request is sufficiently specified. Do not expose internal JSON unless useful for resolving a conflict.
8. Audit the result silently and surface only material failures.

Read `references/chat-intent-resolution.md` when mapping natural-language reference cues. Read `references/authority-model.md` for authority boundaries. Read `references/generation-policy.md` for fresh generation rules, `references/edit-policy.md` for editing, and `references/source-profiles.md` when a Project default source set is requested.

## Natural-language reference handling

Treat language such as the following as explicit role instructions when the referent is clear:

- "이 느낌으로", "이 스타일로" -> `STYLE`
- "이 사람 그대로", "얼굴 유지" -> `CHARACTER`
- "이 포즈로" -> `POSE`
- "이 구도로", "이 배치처럼", "프레이밍 참고" -> `COMPOSITION`
- "이 비율로", "크기 관계 참고" -> `PROPORTION`
- "이 옷/제품/소품 그대로" -> `ITEM`

This is intent inference from the user's words. It is allowed. Do not infer an authority role merely because a reference happens to contain a face, pose, object, or notable style.

If the user says only "참고해서", "소스 참고해서", or equivalent and a Project source profile is explicitly configured for W-Pack, use that profile. If no profile exists and a single current-chat reference is clearly the intended source, use it only when the requested influence is clear from context. Otherwise ask only when the ambiguity materially changes the result.

## Reference sources

A reference may be either:

- `PROJECT_AUTHORITY`: a persistent Project file optionally defined in an authority manifest.
- `INLINE_AUTHORITY`: an image attached or clearly identified in the current conversation.

Inline authorities do not need manifest IDs. Assign stable internal IDs such as `INLINE_STYLE_01` only for the current request.

Project files are a reusable library, not automatic generation inputs. Never pass every Project image merely because it exists.

## Modes

Use `FRESH` by default when the user asks for a new image, a remake from references, or a new variation without asking to preserve a previous generated candidate.

Use `EDIT` when the user asks to change an existing image, preserve part of it, continue from it, restyle it, or modify only selected properties.

Inside `EDIT`, classify the operation internally when useful:

- `MODIFY`: change selected properties while preserving the rest.
- `RESTYLE`: preserve structure/content while changing visual language.
- `RECOMPOSE`: preserve selected content while changing framing/layout/composition.

Do not require the user to name these modes.

## Internal request contract

Use this logical shape before generation. This is an internal contract, not a user-facing form.

```json
{
  "schema_version": "WPACK_GENERATION_REQUEST_v1.1",
  "mode": "FRESH",
  "scene": "...",
  "aspect_ratio": "4:5",
  "references": [],
  "composition": [],
  "lighting": [],
  "exact_text": null,
  "preserve": [],
  "avoid": [],
  "edit_target": null,
  "source_profile": null
}
```

Each reference may contain `source`, `id`, `role`, and `influence`. `source` is `PROJECT_AUTHORITY` or `INLINE_AUTHORITY`.

## Conflict handling

- Let explicit user instructions override profile or manifest defaults when compatible with safety and tool constraints.
- If two references incompatibly claim the same property, stop and surface the specific conflict instead of guessing.
- Do not let `STYLE` silently control identity, pose, composition, or item design.
- Do not let `COMPOSITION` silently control identity, style, wardrobe, or item identity.
- Do not let `CHARACTER` silently control background, lighting, graphic treatment, or composition.
- Preserve exact user-specified image text, including spelling, capitalization, punctuation, and line content.
- If a named Project authority cannot be resolved, state what is missing instead of substituting a visually similar file.

## Generation transport

Use ChatGPT's built-in image-generation capability. Do not request API keys, standalone image APIs, Codex OAuth, or a local GPU.

## Supporting resources

- `references/chat-intent-resolution.md` - natural-language role and mode resolution.
- `references/authority-model.md` - authority semantics and influence boundaries.
- `references/generation-policy.md` - fresh generation and request compilation rules.
- `references/edit-policy.md` - edit-target and preservation rules.
- `references/source-profiles.md` - reusable Project source-profile behavior.
- `references/audit-policy.md` - post-generation review rules.
- `references/project-setup.md` - recommended ChatGPT Project configuration.
- `references/authority-manifest.example.json` - persistent Project-authority template.
- `references/generation-request.example.json` - request template.
- `scripts/validate_authorities.py` - deterministic manifest/request validation.
- `scripts/compile_request.py` - deterministic bounded-request compilation.
- `scripts/self_test.py` - smoke tests for fresh, inline-reference, profile, composition, and edit flows.

## Script verification

When modifying the Skill scripts, run:

```bash
python3 scripts/self_test.py
```

Require `W-Pack self-test: PASS` before packaging or distributing the Skill.
