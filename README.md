# W-Pack

W-Pack is a chat-native reference control layer for image generation and editing in ChatGPT web and ChatGPT Projects.

It lets users speak naturally — for example, "이 느낌으로", "이 사람 그대로", "이 포즈로", "이 구도로", or "소스 참고해서" — while keeping each reference image bounded to the visual properties it is actually allowed to influence.

## Target environment

W-Pack is designed for:

- ChatGPT web
- ChatGPT Projects
- ChatGPT Skills
- ChatGPT built-in image generation

It does not require a standalone image API, API key, local GPU, Codex OAuth, or a local CLI.

## Chat-native authority model

References can come from reusable Project files or directly from images attached in the current conversation.

Supported authority roles:

- `STYLE` — palette, texture, lighting language, rendering and graphic treatment
- `CHARACTER` — identity and stable appearance
- `POSE` — body arrangement and gesture
- `COMPOSITION` — framing, crop, camera angle, subject placement, hierarchy, negative space
- `PROPORTION` — relative physical scale
- `ITEM` — specified object identity and structure

A reference must not silently influence unrelated properties.

## Natural-language examples

```text
@W-Pack
20대 여성, 교복, 셀카, 부드러운 빛.
소스 참고해서 새 이미지로 제작.
```

```text
@W-Pack
첫 번째 첨부 이미지는 느낌만 참고하고,
두 번째 이미지의 인물은 그대로 유지.
세 번째 이미지 구도로 만들어.
```

```text
@W-Pack
이 이미지에서 얼굴과 구도는 그대로 두고 옷만 바꿔.
```

W-Pack resolves these requests internally instead of requiring the user to write JSON or manifest IDs.

## Modes

- `FRESH` — default for new generations and remakes from references.
- `EDIT` — used when an existing image target is being modified, preserved, refined, restyled, or recomposed.

EDIT may be classified internally as `MODIFY`, `RESTYLE`, or `RECOMPOSE`; users do not need to name these subtypes.

## Project sources and inline sources

- `PROJECT_AUTHORITY` — reusable reference stored in a ChatGPT Project, optionally registered in an authority manifest.
- `INLINE_AUTHORITY` — image attached or clearly identified in the current conversation. No manifest entry is required.

Projects may optionally define source profiles such as `DEFAULT` for recurring source sets. A request such as "소스 참고해서" can activate an explicitly configured profile while keeping all authority boundaries intact.

## Workflow

```text
User chat request
  -> resolve FRESH vs EDIT
  -> resolve explicit references and natural-language roles
  -> apply optional Project source profile
  -> validate scopes and conflicts
  -> compile scene / composition / lighting / text / preserve / avoid
  -> ChatGPT built-in image generation
  -> silent audit for fidelity and reference leakage
```

Use no more than five generation references and prefer the minimum necessary set. Previous generated candidates are never silently reused in FRESH mode.

## Skill structure

```text
skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── validate_authorities.py
│   ├── compile_request.py
│   └── self_test.py
└── references/
    ├── chat-intent-resolution.md
    ├── authority-model.md
    ├── generation-policy.md
    ├── edit-policy.md
    ├── source-profiles.md
    ├── audit-policy.md
    └── project-setup.md
```

## Validation

Run:

```bash
python3 skill/scripts/self_test.py
```

Expected result:

```text
W-Pack self-test: PASS
```

## Current status

`WPACK_v0.3.0-chat-native` focuses on ChatGPT web ergonomics: inline references, natural-language authority resolution, composition authority, FRESH/EDIT semantics, and optional Project source profiles.

Legacy `src/zpack`, `pack`, `private-assets`, and `output` paths remain provenance-only and are not part of the ChatGPT web execution path.
