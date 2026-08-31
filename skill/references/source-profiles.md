# Source Profiles

Source profiles are the primary persistent reference mechanism for W-Pack in ChatGPT Projects.

## Default behavior

Project sources are active by default. The user should not need to attach images in every chat or repeat a phrase asking W-Pack to use the sources.

Resolve the active profile in this order:

1. If `use_default_sources` is false, activate no automatic Project profile.
2. If the request names `source_profile`, use that profile.
3. Otherwise use manifest `default_source_profile`.
4. Otherwise use a profile named `DEFAULT` when present.

A profile maps a profile name to a bounded set of Project authority IDs. Example:

```json
{
  "default_source_profile": "DEFAULT",
  "source_profiles": {
    "DEFAULT": ["STYLE_CORE_01", "CHARACTER_01", "PROPORTION_01"]
  }
}
```

## Inline references

Current-chat image attachments are secondary. Do not make them the default reference path.

When the user explicitly assigns an inline reference to a role already provided by the active profile, use the inline reference as the per-request override for that role. Keep the remaining Project authorities active.

When the inline reference has a different role, add it if the total active reference count remains within the limit.

Do not treat an unmentioned chat attachment as permission to replace the Project source set.

## Limits

- Maximum 5 active generation references after profile expansion and overrides.
- Keep every authority bound to its declared role and allowed influence.
- If a profile authority is missing, do not silently replace it with another Project image.
