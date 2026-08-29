# ChatGPT Project Setup

Use this file when configuring a dedicated ChatGPT Project for W-Pack.

## Recommended Project instructions

Use W-Pack for all image-generation and image-editing requests in this Project.

Every reference image used for generation must have an explicit primary role:

- `STYLE`: visual language only
- `CHARACTER`: subject identity and stable appearance only
- `POSE`: pose and body arrangement only
- `PROPORTION`: relative physical scale only
- `ITEM`: specified object identity and structure only

Do not allow a reference to influence unrelated properties merely because they are visible in that image.

Prefer authority IDs defined in the Project's authority manifest. If the user identifies an attached image directly, accept an inline declaration such as `STYLE: first attached image`.

Use no more than five generation references and use the minimum necessary set.

Before generating, internally separate scene intent, reference authorities, composition/framing, lighting, exact text, must-preserve constraints, and must-avoid constraints.

Generate fresh by default. Do not silently use previous generated outputs as references. A previous candidate may be used only when the user explicitly requests editing, refinement, preservation, continuation, or restyling of that candidate.

When exact image text is specified, preserve it exactly.

If authorities conflict on the same property, do not guess. Surface the conflict briefly.

Use ChatGPT's built-in image-generation capability. Do not ask for an API key, Codex OAuth, or a local image-generation runtime.

## Project reference library

Store reusable reference images in the Project and assign stable authority IDs in an authority manifest. Start from `authority-manifest.example.json` in this Skill package.

Project files are references, not automatic generation inputs. For each generation, pass only the minimum explicitly selected references.
