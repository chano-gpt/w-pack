# W-Pack v0.5.1 Quick Start

## 1. Install the Skill

Install the packaged `skill.zip` or the `skill/` directory.

## 2. Add reusable Project sources

Add the images you want to reuse across chats to the ChatGPT Project. Configure them in `project/AUTHORITY_MANIFEST.example.json`.

Recommended DEFAULT profile:

```text
STYLE_CORE + optional STYLE_SUPPORT + CHARACTER + PROPORTION
```

Keep the first pass at five references or fewer. STYLE is limited to one CORE plus up to two SUPPORT adapters.

## 3. Build STYLE DNA

For each style source, add concrete `style_signature` and `anti_drift_signature` fields when possible. W-Pack may also derive these from Project images when ChatGPT can inspect them.

Do not rely on labels such as “anime” or “cinematic.” Capture medium, edge grammar, abstraction, shading/value, color, material treatment, background behavior, realism level, hair rendering grammar, and anti-drift traits.

## 4. Understand source binding

Project storage and image-generation visual binding are not the same thing.

W-Pack prefers the actual visual source when direct binding is available. When binding is unverified but ChatGPT can inspect the Project image, W-Pack uses source-derived STYLE DNA instead of pretending the image was visually handed to the generator.

## 5. Generate normally

You do not need to say “use the sources” every time.

```text
@w-pack
20대 여성, 흰 셔츠와 청바지.
정오의 푸른 하늘, 아래에서 위로 촬영.
2:3 비율.
```

W-Pack resolves DEFAULT sources, transport state, style family, hair grammar, and generation constraints internally.

## 6. Hair behavior

When no source explicitly requires strand-heavy hair, W-Pack defaults to `CLEAN_MASS`: coherent grouped locks, clean silhouette, grouped ends, lock-level highlights, and sparse physically plausible flyaways.

This is designed to suppress the common dense-flyaway / split-tip / thread-highlight signature without making hair plastic or helmet-like.

## 7. Conditional style recovery

The first pass is always fresh. If structure is good but style materially drifts, W-Pack may perform one style-only recovery with:

```text
STRUCTURE_EDIT_TARGET + STYLE_CORE + optional one relevant STYLE_SUPPORT
```

Automatic recovery requires STYLE_CORE to be visually bound or backed by usable STYLE DNA. There is no recursive restyle or automatic third pass.

## 8. Validate

```bash
python3 skill/scripts/self_test.py
```

Expected output:

```text
W-Pack self-test: PASS
```
