# Legacy upstream boundary

The `src/zpack/`, `pack/`, `private-assets/`, and `output/` paths originate from the upstream Z-Pack starter.

They are retained temporarily for provenance and migration reference. They are **not** part of the W-Pack ChatGPT web execution path.

W-Pack web execution lives under:

- `skill/` — Skill instructions, deterministic validators, and policy references.
- `project/` — recommended ChatGPT Project instructions and manifest/request examples.
- `PACK_SPEC.json` — web-native harness contract.

The legacy `zpack` command is intentionally no longer exposed by `pyproject.toml` in the web port.

Do not add new web-specific logic to `src/zpack`. New logic belongs in the Skill bundle unless a future runtime adapter explicitly requires otherwise.
