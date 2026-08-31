# Quick start

W-Pack v0.4 is designed for ChatGPT Web, ChatGPT Projects, and ChatGPT Skills.

## 1. Install the Skill

Upload `skill.zip` to ChatGPT Skills.

## 2. Configure persistent Project sources

1. Add reusable reference images to the ChatGPT Project.
2. Copy `project/PROJECT_INSTRUCTIONS.md` into Project instructions.
3. Define bounded authorities in `project/AUTHORITY_MANIFEST.example.json`.
4. Put the normal source set in `source_profiles.DEFAULT` and set `default_source_profile` to `DEFAULT`.
5. Keep one normal STYLE authority in DEFAULT so W-Pack can use it as STYLE_CORE.

The Project sources are then used automatically. You do not need to attach them again in every chat.

## 3. Ask normally

```text
@W-Pack
푸른 하늘, 여자, 흰 셔츠와 청바지.
하늘을 보고 한 손으로 머리를 넘긴다.
정오의 태양, 아래에서 위로 보는 구도, 2:3.
```

W-Pack uses the Project sources by default.

## 4. Optional chat overrides

Attach a current-chat image only when you want a temporary pose, composition, character, item, or style override.

## 5. Conditional style recovery

W-Pack generates once first. If the structure is good but STYLE_CORE fidelity materially fails, it may perform one style-only restyle using the fresh candidate plus STYLE_CORE. It never recursively restyles or performs an automatic third pass.
