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
  -> validate authority scopes
  -> compile bounded generation brief
  -> ChatGPT built-in image generation
  -> audit scene compliance / fidelity / leakage / structure
```

Fresh generation is the default. Previous generated candidates are reused only when the user explicitly requests an edit, refinement, continuation, or staged restyle.

## Skill structure

```text
skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── authority-model.md
    ├── generation-policy.md
    └── audit-policy.md
```

The Skill is intentionally instruction-led. ChatGPT handles semantic compilation and review directly; deterministic scripts should be added only where they materially improve reliability.

## Project files

```text
project/
├── PROJECT_INSTRUCTIONS.md
└── AUTHORITY_MANIFEST.example.json
```

Project files are the bridge between a persistent ChatGPT Project reference library and W-Pack's authority model.

## Current status

`WPACK_v0.1.0-web` is the first web-port foundation. The repository still contains legacy Z-Pack CLI/runtime files from the upstream fork; those are not part of the ChatGPT web execution path and will be isolated or removed as the port matures.
