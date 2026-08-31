# Source Profiles

Use Project source profiles as W-Pack's primary persistent reference mechanism.

## Resolution order

1. If `use_default_sources=false`, activate no automatic Project profile.
2. If the request names `source_profile`, use it.
3. Otherwise use manifest `default_source_profile`.
4. Otherwise use a profile named `DEFAULT` when present.

Recommended v0.5.1 profile:

```json
{
  "default_source_profile": "DEFAULT",
  "source_profiles": {
    "DEFAULT": ["STYLE_CORE_01", "STYLE_SUPPORT_01", "CHARACTER_01", "PROPORTION_01"]
  }
}
```

The user does not need to repeat a phrase such as "use the sources".

## Inline overrides

Treat current-chat images as secondary.

- Activate an inline image only when the user points to it or its intended influence is clear.
- For non-STYLE roles, an explicit inline reference replaces the default Project authority of the same role for that request.
- By default, any explicit inline STYLE replaces the entire Project style family for that request.
- Keep unaffected Project non-STYLE authorities active.
- Do not promote an unmentioned attachment into the source set.

## Combining style sources

Set `combine_style_sources=true` only when the user explicitly wants the Project style family and current-chat STYLE references combined.

The resolved family must still contain exactly one STYLE_CORE and no more than two STYLE_SUPPORT references. Inline supports must declare `style_role: "SUPPORT"` and a bounded influence list. Do not silently turn an extra style into a second CORE.

## Limits

Keep at most five active generation references after profile expansion and overrides. Within that total, allow at most three STYLE references: one CORE and up to two SUPPORT adapters.
