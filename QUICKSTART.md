# Quick start

W-Pack is designed for ChatGPT web, ChatGPT Projects, and ChatGPT Skills. No local CLI, API key, Codex OAuth, or GPU is required.

## 1. Install the Skill

Upload the packaged `skill.zip` to ChatGPT Skills when Skill upload is available in your workspace.

## 2. Optional Project setup

For reusable image sources in a ChatGPT Project:

1. Add the reference images to the Project.
2. Copy `project/PROJECT_INSTRUCTIONS.md` into the Project instructions.
3. Optionally maintain reusable authority IDs with `project/AUTHORITY_MANIFEST.example.json`.
4. Optionally define a Project source profile such as `DEFAULT` for recurring source sets.

Current-chat images do not need manifest entries.

## 3. Use natural language

Examples:

```text
@W-Pack
20대 여성, 교복, 셀카, 부드러운 빛.
소스 참고해서 새 이미지로 제작.
```

```text
@W-Pack
첫 번째 첨부 이미지의 느낌만 참고하고,
두 번째 이미지의 인물은 그대로 유지.
세 번째 이미지의 구도로 만들어.
```

```text
@W-Pack
이 이미지에서 얼굴과 구도는 그대로 두고 옷만 바꿔.
```

W-Pack resolves these requests into bounded STYLE, CHARACTER, COMPOSITION, ITEM, and edit constraints internally, then uses ChatGPT's built-in image generation.
