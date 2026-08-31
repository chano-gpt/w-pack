# Project Setup

W-Pack is designed to use persistent ChatGPT Project sources as its primary reference path.

## Recommended setup

1. Add reusable reference images to the Project.
2. Assign each reusable source a bounded authority in the manifest.
3. Define a `source_profiles.DEFAULT` set.
4. Set `default_source_profile` to `DEFAULT`.
5. Add the W-Pack Project instructions.

With this setup, users do not need to attach the same references or say "use the sources" on every image request.

## Recommended manifest shape

```json
{
  "schema_version": "WPACK_AUTHORITY_MANIFEST_v1.0",
  "default_source_profile": "DEFAULT",
  "source_profiles": {
    "DEFAULT": ["STYLE_CORE_01", "CHARACTER_01", "PROPORTION_01"]
  },
  "authorities": {}
}
```

Keep each authority bounded to one primary role. Use current-chat attachments only for temporary overrides or additions.
