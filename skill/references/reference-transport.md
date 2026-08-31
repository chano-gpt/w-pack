# Reference Transport

Treat authority selection and image-model transport as separate decisions. A Project file can be selected as an authority without being visually bound to the image-generation model.

## Transport states

- `VISUAL_BOUND` — direct visual binding is confirmed for the current generation path.
- `VISUAL_INPUT_EXPECTED` — a current-chat visual input is expected, but binding has not been independently confirmed.
- `PROJECT_CONTEXT_ONLY` — ChatGPT can inspect the Project source, but the image model is not confirmed to receive it directly.
- `TEXT_PROFILE_ONLY` — only a derived text authority profile is available.
- `UNVERIFIED_PROJECT_SOURCE` — the source is selected from Project context and its visual handoff is unknown.
- `UNAVAILABLE` — neither a usable visual source nor a usable derived profile is available.

Never convert Project membership into `VISUAL_BOUND` automatically.

## Fallback order

1. Use `VISUAL_BOUND` when direct visual handoff is confirmed.
2. Otherwise, if ChatGPT can inspect the source, derive or reuse a bounded source profile. For STYLE, use `style_signature` and `anti_drift_signature` as STYLE DNA.
3. Use `TEXT_PROFILE_ONLY` when only the derived profile remains available.
4. Mark the authority unusable when no visual source and no meaningful profile exist.

Text fallback is degraded transport. Do not describe it as exact visual reference use.

## Role implications

STYLE can degrade to text STYLE DNA more gracefully than CHARACTER, POSE, COMPOSITION, PROPORTION, or ITEM. Exact identity, pose, geometry, item, or composition claims require stronger visual transport evidence.

## Recovery

Automatic `SINGLE_RESTYLE` requires exactly one STYLE_CORE and either:

- confirmed `VISUAL_BOUND`, or
- usable STYLE DNA in `style_signature` / `anti_drift_signature`.

`VISUAL_INPUT_EXPECTED` or `UNVERIFIED_PROJECT_SOURCE` alone is not sufficient proof for automatic recovery.
