# ChatGPT Project Setup

Use this file when configuring a dedicated ChatGPT Project for W-Pack.

## Recommended Project instructions

Use W-Pack for image-generation and image-editing requests in this Project. Treat natural-language chat as the primary interface; do not require users to write JSON or authority IDs when intent is clear.

Every reference used for generation must have a bounded role:

- `STYLE`: visual language only
- `CHARACTER`: subject identity and stable appearance only
- `POSE`: pose and body arrangement only
- `COMPOSITION`: framing, crop, camera angle, placement, hierarchy, and negative space only
- `PROPORTION`: relative physical scale only
- `ITEM`: specified object identity and structure only

Natural-language cues such as "이 느낌으로", "이 사람 그대로", "이 포즈로", and "이 구도로" may assign roles when the referent is clear. Do not infer roles merely from incidental image content.

Prefer stable authority IDs for reusable Project files. Current-chat images may be used as inline authorities without manifest entries.

Use no more than five generation references and prefer the minimum necessary set.

Generate fresh by default. Use EDIT only when the user points to a usable existing image and asks to modify, preserve, refine, restyle, continue, or recompose it. Do not silently use previous generated outputs as references.

When exact image text is specified, preserve it exactly. If references conflict on the same property, surface the conflict briefly instead of guessing.

Use ChatGPT's built-in image-generation capability. Do not ask for an API key, Codex OAuth, or a local image-generation runtime.

## Project reference library

Store reusable reference images in the Project and optionally assign stable authority IDs in an authority manifest. Start from `authority-manifest.example.json`.

Project files are references, not automatic generation inputs. For each generation, pass only the minimum explicitly selected references.

Optionally define source profiles such as `DEFAULT` to bundle recurring Project authorities. A source profile remains subject to authority boundaries and the five-reference limit.
