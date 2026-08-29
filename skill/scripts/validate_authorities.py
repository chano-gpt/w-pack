#!/usr/bin/env python3
"""Validate W-Pack authority manifests and optional generation requests.

This script validates metadata only. It does not inspect image pixels or resolve
ChatGPT Project files. Image availability remains the responsibility of the
calling ChatGPT session.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MANIFEST_SCHEMA = "WPACK_AUTHORITY_MANIFEST_v1.0"
REQUEST_SCHEMA = "WPACK_GENERATION_REQUEST_v1.0"
ALLOWED_ROLES = {"STYLE", "CHARACTER", "POSE", "PROPORTION", "ITEM"}
REFERENCE_SLOT_LIMIT = 5

ROLE_REQUIRED_ALLOWED = {
    "STYLE": {"palette", "rendering_language"},
    "CHARACTER": {"identity"},
    "POSE": {"body_arrangement"},
    "PROPORTION": {"proportion"},
    "ITEM": {"item_identity"},
}

ROLE_REQUIRED_FORBIDDEN = {
    "STYLE": {"identity", "pose", "exact_composition", "item_identity"},
    "CHARACTER": {"background", "composition", "graphic_treatment"},
    "POSE": {"identity", "environment", "style"},
    "PROPORTION": {"identity", "style"},
    "ITEM": {"identity", "background", "style"},
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    return value


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        errors.append(f"schema_version must be {MANIFEST_SCHEMA}")

    authorities = manifest.get("authorities")
    if not isinstance(authorities, dict) or not authorities:
        errors.append("authorities must be a non-empty object")
        return errors

    for authority_id, authority in authorities.items():
        prefix = f"authority {authority_id!r}"
        if not isinstance(authority_id, str) or not authority_id.strip():
            errors.append("authority IDs must be non-empty strings")
            continue
        if not isinstance(authority, dict):
            errors.append(f"{prefix} must be an object")
            continue

        file_name = authority.get("file")
        if not isinstance(file_name, str) or not file_name.strip():
            errors.append(f"{prefix}.file must be a non-empty string")

        role = authority.get("role")
        if role not in ALLOWED_ROLES:
            errors.append(f"{prefix}.role must be one of {sorted(ALLOWED_ROLES)}")
            continue

        allowed = _string_list(authority.get("allowed_influence"))
        forbidden = _string_list(authority.get("forbidden_influence"))
        if allowed is None or not allowed:
            errors.append(f"{prefix}.allowed_influence must be a non-empty string array")
            allowed_set: set[str] = set()
        else:
            allowed_set = set(allowed)
        if forbidden is None or not forbidden:
            errors.append(f"{prefix}.forbidden_influence must be a non-empty string array")
            forbidden_set: set[str] = set()
        else:
            forbidden_set = set(forbidden)

        overlap = sorted(allowed_set & forbidden_set)
        if overlap:
            errors.append(f"{prefix} has influence listed as both allowed and forbidden: {overlap}")

        missing_allowed = sorted(ROLE_REQUIRED_ALLOWED[role] - allowed_set)
        if missing_allowed:
            errors.append(f"{prefix} is missing minimum allowed influence for {role}: {missing_allowed}")

        missing_forbidden = sorted(ROLE_REQUIRED_FORBIDDEN[role] - forbidden_set)
        if missing_forbidden:
            errors.append(f"{prefix} is missing minimum forbidden influence for {role}: {missing_forbidden}")

    return errors


def validate_request(request: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if request.get("schema_version") != REQUEST_SCHEMA:
        errors.append(f"request.schema_version must be {REQUEST_SCHEMA}")

    mode = request.get("mode", "FRESH")
    if mode not in {"FRESH", "STAGED_RESTYLE"}:
        errors.append("request.mode must be FRESH or STAGED_RESTYLE")

    scene = request.get("scene")
    if not isinstance(scene, str) or not scene.strip():
        errors.append("request.scene must be a non-empty string")

    authorities = request.get("authorities", [])
    if not isinstance(authorities, list):
        errors.append("request.authorities must be an array")
        return errors
    if len(authorities) > REFERENCE_SLOT_LIMIT:
        errors.append(f"request uses {len(authorities)} authorities; limit is {REFERENCE_SLOT_LIMIT}")

    known = manifest.get("authorities", {})
    seen_ids: set[str] = set()
    claimed_properties: dict[str, str] = {}

    for index, ref in enumerate(authorities):
        prefix = f"request.authorities[{index}]"
        if not isinstance(ref, dict):
            errors.append(f"{prefix} must be an object")
            continue
        authority_id = ref.get("id")
        if not isinstance(authority_id, str) or authority_id not in known:
            errors.append(f"{prefix}.id is not present in the authority manifest")
            continue
        if authority_id in seen_ids:
            errors.append(f"duplicate authority reference: {authority_id}")
            continue
        seen_ids.add(authority_id)

        declared_role = known[authority_id].get("role")
        requested_role = ref.get("role", declared_role)
        if requested_role != declared_role:
            errors.append(
                f"{authority_id} requested as {requested_role}, but manifest role is {declared_role}"
            )

        influence = ref.get("influence")
        if influence is not None:
            influence_list = _string_list(influence)
            if influence_list is None:
                errors.append(f"{prefix}.influence must be a string array when present")
            else:
                allowed = set(known[authority_id].get("allowed_influence", []))
                forbidden = set(known[authority_id].get("forbidden_influence", []))
                for prop in influence_list:
                    if prop not in allowed:
                        errors.append(f"{authority_id} is not allowed to control {prop!r}")
                    if prop in forbidden:
                        errors.append(f"{authority_id} explicitly forbids control of {prop!r}")
                    prior = claimed_properties.get(prop)
                    if prior is not None and prior != authority_id:
                        errors.append(
                            f"authority conflict for {prop!r}: {prior} and {authority_id} both claim it"
                        )
                    claimed_properties[prop] = authority_id

    forbidden_fresh_fields = ("prior_candidate", "edit_target", "patch", "layer_composite")
    if mode == "FRESH" and any(request.get(key) for key in forbidden_fresh_fields):
        errors.append("fresh generation cannot include a prior candidate or generative edit target")

    if mode == "STAGED_RESTYLE":
        if request.get("explicit_opt_in") is not True:
            errors.append("staged restyle requires explicit_opt_in=true")
        edit_target = request.get("edit_target")
        if not isinstance(edit_target, str) or not edit_target.strip():
            errors.append("staged restyle requires a non-empty edit_target")
        style_refs = [
            ref for ref in authorities
            if isinstance(ref, dict)
            and ref.get("id") in known
            and known[ref["id"]].get("role") == "STYLE"
        ]
        if len(style_refs) > 1:
            errors.append("staged restyle allows at most one STYLE authority")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate W-Pack authority metadata")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--request", type=Path)
    args = parser.parse_args()

    try:
        manifest = load_json(args.manifest)
        errors = validate_manifest(manifest)
        if args.request is not None and not errors:
            request = load_json(args.request)
            errors.extend(validate_request(request, manifest))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]

    result = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
