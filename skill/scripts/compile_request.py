#!/usr/bin/env python3
"""Compile a validated W-Pack request into a bounded image-generation brief."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_authorities import load_json, validate_manifest, validate_request

COMPILED_SCHEMA = "WPACK_COMPILED_REQUEST_v1.0"


def compile_request(manifest: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if not errors:
        errors.extend(validate_request(request, manifest))
    if errors:
        raise ValueError("; ".join(errors))

    known = manifest["authorities"]
    compiled_authorities = []
    for ref in request.get("authorities", []):
        authority_id = ref["id"]
        authority = known[authority_id]
        influence = ref.get("influence") or authority["allowed_influence"]
        compiled_authorities.append(
            {
                "id": authority_id,
                "file": authority["file"],
                "role": authority["role"],
                "allowed_influence": influence,
                "forbidden_influence": authority["forbidden_influence"],
            }
        )

    return {
        "schema_version": COMPILED_SCHEMA,
        "mode": request.get("mode", "FRESH"),
        "scene": request["scene"].strip(),
        "aspect_ratio": request.get("aspect_ratio"),
        "exact_text": request.get("exact_text"),
        "authorities": compiled_authorities,
        "generation_constraints": {
            "use_chatgpt_builtin_image_generation": True,
            "maximum_reference_count": 5,
            "fresh_generation_default": True,
            "do_not_infer_reference_roles": True,
            "do_not_expand_authority_scope": True,
            "preserve_exact_text_when_present": True,
            "do_not_reuse_prior_candidate_unless_mode_is_staged_restyle": True,
        },
        "edit_target": request.get("edit_target") if request.get("mode") == "STAGED_RESTYLE" else None,
        "preserve": request.get("preserve", []) if request.get("mode") == "STAGED_RESTYLE" else [],
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
