#!/usr/bin/env python3
"""Compile a validated chat-native W-Pack request into a bounded generation brief."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_authorities import (
    DEFAULT_INLINE_ALLOWED,
    load_json,
    resolve_active_references,
    resolve_profile_name,
    validate_manifest,
    validate_request,
)

COMPILED_SCHEMA = "WPACK_COMPILED_REQUEST_v1.1"


def compile_request(manifest: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if not errors:
        errors.extend(validate_request(request, manifest))
    if errors:
        raise ValueError("; ".join(errors))

    known = manifest["authorities"]
    active_references = resolve_active_references(manifest, request)
    compiled_references = []

    for ref in active_references:
        source = ref.get("source", "PROJECT_AUTHORITY")
        authority_id = ref["id"]
        if source == "PROJECT_AUTHORITY":
            authority = known[authority_id]
            role = authority["role"]
            allowed = ref.get("influence") or authority["allowed_influence"]
            forbidden = authority["forbidden_influence"]
            file_name = authority["file"]
        else:
            role = ref["role"]
            allowed = ref.get("influence") or sorted(DEFAULT_INLINE_ALLOWED[role])
            forbidden = []
            file_name = ref.get("file")

        compiled_references.append(
            {
                "id": authority_id,
                "source": source,
                "file": file_name,
                "role": role,
                "allowed_influence": allowed,
                "forbidden_influence": forbidden,
            }
        )

    mode = request.get("mode", "FRESH")
    profile_name = resolve_profile_name(manifest, request)
    style_active = any(ref["role"] == "STYLE" for ref in compiled_references)

    generation_constraints: dict[str, Any] = {
        "use_chatgpt_builtin_image_generation": True,
        "maximum_reference_count": 5,
        "fresh_generation_default": True,
        "project_sources_default_active": request.get("use_default_sources", True),
        "resolved_default_source_profile": profile_name,
        "inline_references_are_secondary": True,
        "explicit_same_role_reference_overrides_profile_default": True,
        "resolve_roles_from_user_language_not_visual_incidence": True,
        "do_not_expand_authority_scope": True,
        "preserve_exact_text_when_present": True,
        "do_not_reuse_prior_candidate_without_edit_intent": True,
    }

    if style_active:
        generation_constraints.update(
            {
                "style_fidelity": "HIGH",
                "medium_lock": "REFERENCE",
                "photorealism_normalization": "DISABLED_UNLESS_EXPLICITLY_REQUESTED",
                "photographic_terms_do_not_override_reference_medium": True,
            }
        )

    return {
        "schema_version": COMPILED_SCHEMA,
        "mode": mode,
        "scene": request["scene"].strip(),
        "aspect_ratio": request.get("aspect_ratio"),
        "references": compiled_references,
        "composition": request.get("composition", []),
        "lighting": request.get("lighting", []),
        "exact_text": request.get("exact_text"),
        "preserve": request.get("preserve", []),
        "avoid": request.get("avoid", []),
        "edit_target": request.get("edit_target") if mode == "EDIT" else None,
        "edit_type": request.get("edit_type") if mode == "EDIT" else None,
        "source_profile": profile_name,
        "use_default_sources": request.get("use_default_sources", True),
        "generation_constraints": generation_constraints,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile W-Pack image-generation request")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        compiled = compile_request(load_json(args.manifest), load_json(args.request))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    text = json.dumps(compiled, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
