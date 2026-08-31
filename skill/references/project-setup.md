# Project Setup

Use persistent ChatGPT Project sources as W-Pack's primary reusable reference catalog.

## Recommended setup

1. Add reusable reference images to the Project.
2. Define bounded authorities in manifest schema `WPACK_AUTHORITY_MANIFEST_v1.1`.
3. Mark STYLE authorities as one `style_role: "CORE"` plus optional bounded `SUPPORT` sources.
4. Add concrete `style_signature` and `anti_drift_signature` fields for STYLE sources when possible.
5. Define `source_profiles.DEFAULT` and set `default_source_profile` to `DEFAULT`.
6. Keep the total DEFAULT profile at five references or fewer; a typical set is STYLE_CORE + one STYLE_SUPPORT + CHARACTER + PROPORTION.
7. Add W-Pack Project instructions from `project/PROJECT_INSTRUCTIONS.md`.

The user should not need to reattach recurring sources or repeat "use the sources".

## Transport note

Project storage is not direct visual-binding proof. Leave Project sources as `UNVERIFIED_PROJECT_SOURCE` unless direct visual transport is actually confirmed. W-Pack may use source-derived text profiles as degraded fallback when ChatGPT can inspect the source.

## Current-chat references

Use current-chat attachments for temporary overrides or explicitly requested additions. An inline STYLE replaces the Project style family by default; combine style sources only when the user clearly asks for it.
