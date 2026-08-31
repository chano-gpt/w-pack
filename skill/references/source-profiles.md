# Source Profiles

Use Project source profiles as W-Pack's primary persistent reference mechanism.

## Resolution order

1. If `use_default_sources=false`, activate no automatic Project profile.
2. If the request names `source_profile`, use it.
3. Otherwise use manifest `default_source_profile`.
4. Otherwise use a profile named `DEFAULT` when present.

Example:

```json
{
  "default_source_profile": "DEFAULT",
  "source_profiles": {
    "DEFAULT": ["STYLE_CORE_01", "CHARACTER_01", "PROPORTION_01"]
  }
}
```

The user does not need to repeat a phrase such as "use the sources".

## Inline overrides

Treat current-chat images as secondary.

- Activate an inline image only when the user points to it or its intended influence is clear.
- If an inline reference claims the same role as a default Project authority, replace that default role for the current request unless the user requests combination.
- If inline STYLE replaces Project STYLE, the inline STYLE becomes STYLE_CORE for that request.
- Keep unaffected Project authorities active.
- Do not promote an unmentioned attachment into the source set.

## Limits

Keep at most five active generation references after profile expansion and overrides. Keep exactly one STYLE authority in ordinary default profiles so automatic style recovery can resolve a singular STYLE_CORE.
