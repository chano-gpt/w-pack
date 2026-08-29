# W-Pack

W-Pack is a reference-bounded image-generation harness for ChatGPT web and ChatGPT Projects.

It separates *what you want to create* from *what each reference image is allowed to influence*, then applies fresh-generation and audit rules before and after ChatGPT's built-in image generation.

## Target environment

W-Pack is designed for:

- ChatGPT web
- ChatGPT Projects
- ChatGPT Skills
- ChatGPT built-in image generation

It does **not** require a standalone image API, API key, local GPU, or Codex OAuth.

## Authority roles

Each generation reference receives an explicit primary role:

- `STYLE` — palette, texture, lighting language, rendering/graphic treatment
- `CHARACTER` — identity and stable appearance
- `POSE` — body arrangement and gesture
- `PROPORTION` — relative physical scale
- `ITEM` — specified object identity and structure

A reference must not silently influence properties outside its authority scope.

## Recommended ChatGPT Project setup

1. Create a dedicated ChatGPT Project for image work.
2. Add your reusable reference images to the Project.
3. Copy `project/PROJECT_INSTRUCTIONS.md` into the Project instructions.
4. Create an authority manifest based on `project/AUTHORITY_MANIFEST.example.json`.
5. Install or upload the W-Pack Skill from `skill/` when Skill support is available in your workspace.

Example request:

```text
Create a 4:5 fashion editorial poster.

STYLE: STYLE_CORE_01
CHARACTER: CHARACTER_01
POSE: POSE_01

Scene: brutalist concrete interior with late-afternoon directional light.
Generate fresh. Do not use previous candidates as references.
```

## Workflow

```text
User brief
  -> resolve explicit authorities
  -> validate manifest and request
  -> compile bounded generation brief
  -> ChatGPT built-in image generation
  -> audit scene compliance / fidelity / leakage / structure
```

Fresh generation is the default. Previous generated candidates are reused only when the user explicitly requests an edit, refinement, continuation, or staged restyle.

## Deterministic validation

The web port keeps deterministic checks inside the Skill bundle rather than the upstream local CLI runtime.

```text
skill/scripts/validate_authorities.py
```

Checks include:

- valid authority roles and influence boundaries
- maximum of five generation references
- unknown or duplicate authority IDs
- authority-scope expansion
- overlapping explicit influence claims
- accidental prior-candidate/edit-target use in `FRESH` mode
- explicit opt-in requirements for `STAGED_RESTYLE`

The bounded request compiler is:

```text
skill/scripts/compile_request.py
```

It produces `WPACK_COMPILED_REQUEST_v1.0`, which is the semantic contract used immediately before ChatGPT image generation.

Example metadata files are available under `project/`:

```text
project/
├── PROJECT_INSTRUCTIONS.md
├── AUTHORITY_MANIFEST.example.json
└── GENERATION_REQUEST.example.json
```

## Skill structure

```text
skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── validate_authorities.py
│   └── compile_request.py
└── references/
    ├── authority-model.md
    ├── generation-policy.md
    └── audit-policy.md
```

The semantic tasks remain instruction-led. Deterministic scripts cover only checks where fail-closed behavior materially improves reliability.

## Legacy boundary

The upstream `src/zpack`, `pack`, `private-assets`, and `output` paths remain temporarily for provenance and migration reference. They are not part of the ChatGPT web execution path. See `LEGACY.md`.

The root package no longer exposes the legacy `zpack` CLI in the web-port branch.

## Current status

`WPACK_v0.2.0-web` is the second web-port milestone: ChatGPT-native authority semantics plus deterministic manifest/request validation and compilation.
