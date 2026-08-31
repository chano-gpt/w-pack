# W-Pack v0.5 Quick Start

## 1. Install the Skill

Install the packaged `skill.zip` or the `skill/` directory.

## 2. Add reusable Project sources

Add the images you want to reuse across chats to the ChatGPT Project. Configure them in `project/AUTHORITY_MANIFEST.example.json`.

A recommended DEFAULT profile is:

```text
STYLE_CORE + optional STYLE_SUPPORT + CHARACTER + PROPORTION
```

Keep the first pass at five references or fewer.

## 3. Build STYLE DNA

For each style source, add a concrete `style_signature` and `anti_drift_signature`. W-Pack may derive these from Project images when ChatGPT can inspect them.

Do not rely on labels such as “anime” or “cinematic.” Capture medium, edge grammar, abstraction, shading/value, color, material treatment, background behavior, realism level, and anti-drift traits.

## 4. Understand source binding

Project storage and image-generation visual binding are not the same thing.

W-Pack prefers the actual visual source when it is available to the image-generation path. When direct binding is unverified but ChatGPT can inspect the Project image, W-Pack falls back to source-derived STYLE DNA instead of pretending the image was visually passed through.

## 5. Generate normally

You do not need to say “use the sources” every time.

```text
@w-pack
20대 여성, 흰 셔츠와 청바지.
정오의 푸른 하늘, 아래에서 위로 촬영.
2:3 비율.
```

W-Pack resolves DEFAULT sources, transport state, style family, and generation constraints internally.

## 6. Conditional style recovery

The first pass is always fresh. If structure is good but style materially drifts, W-Pack may perform one style-only recovery with:

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one STYLE_SUPPORT
```

There is no recursive restyle or automatic third pass.
