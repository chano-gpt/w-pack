#!/usr/bin/env python3
"""Validate W-Pack Project manifests and chat-native generation requests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MANIFEST_SCHEMA = "WPACK_AUTHORITY_MANIFEST_v1.0"
REQUEST_SCHEMAS = {"WPACK_GENERATION_REQUEST_v1.0", "WPACK_GENERATION_REQUEST_v1.1"}
ALLOWED_ROLES = {"STYLE", "CHARACTER", "POSE", "COMPOSITION", "PROPORTION", "ITEM"}
ALLOWED_SOURCES = {"PROJECT_AUTHORITY", "INLINE_AUTHORITY"}
REFERENCE_SLOT_LIMIT = 5

ROLE_REQUIRED_ALLOWED = {
    "STYLE": {"palette", "rendering_language"},
    "CHARACTER": {"identity"},
    "POSE": {"body_arrangement"},
    "COMPOSITION": {"framing"},
    "PROPORTION": {"proportion"},
    "ITEM": {"item_identity"},
}

ROLE_REQUIRED_FORBIDDEN = {
    "STYLE": {"identity", "pose", "composition", "item_identity"},
    "CHARACTER": {"background", "composition", "graphic_treatment"},
    "POSE": {"identity", "environment", "style"},
    "COMPOSITION": {"identity", "style", "item_identity"},
    "PROPORTION": {"identity", "style"},
    "ITEM": {"identity", "background", "style"},
}

DEFAULT_INLINE_ALLOWED = {
    "STYLE": {"palette", "texture", "lighting_language", "graphic_treatment", "rendering_language", "surface_treatment", "typography_character"},
    "CHARACTER": {"identity", "facial_features", "hair", "stable_appearance", "wardrobe"},
    "POSE": {"body_arrangement", "gesture", "stance", "limb_relationship", "camera_relative_orientation"},
    "COMPOSITION": {"framing", "crop", "camera_angle", "subject_placement", "layout_structure", "visual_hierarchy", "negative_space", "spatial_arrangement"},
    "PROPORTION": {"proportion", "physical_scale", "body_to_object_ratio", "object_to_object_scale", "relative_dimensions"},
    "ITEM": {"item_identity", "silhouette", "structural_details", "material", "item_color"},
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


def _request_references(request: dict[str, Any]) -> Any:
    if "references" in request:
        return request.get("references")
    return request.get("authorities", [])


def validate_request(request: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if request.get("schema_version") not in REQUEST_SCHEMAS:
        errors.append(f"request.schema_version must be one of {sorted(REQUEST_SCHEMAS)}")

    mode = request.get("mode", "FRESH")
    if mode not in {"FRESH", "EDIT"}:
        errors.append("request.mode must be FRESH or EDIT")

    scene = request.get("scene")
    if not isinstance(scene, str) or not scene.strip():
        errors.append("request.scene must be a non-empty string")

    references = _request_references(request)
    if not isinstance(references, list):
        errors.append("request.references must be an array")
        return errors
    if len(references) > REFERENCE_SLOT_LIMIT:
        errors.append(f"request uses {len(references)} references; limit is {REFERENCE_SLOT_LIMIT}")

    known = manifest.get("authorities", {})
    seen_keys: set[str] = set()
    claimed_properties: dict[str, str] = {}

    for index, ref in enumerate(references):
        prefix = f"request.references[{index}]"
        if not isinstance(ref, dict):
            errors.append(f"{prefix} must be an object")
            continue

        source = ref.get("source", "PROJECT_AUTHORITY")
        if source not in ALLOWED_SOURCES:
            errors.append(f"{prefix}.source must be one of {sorted(ALLOWED_SOURCES)}")
            continue

        authority_id = ref.get("id")
        role = ref.get("role")
        allowed: set[str]
        forbidden: set[str]

        if source == "PROJECT_AUTHORITY":
            if not isinstance(authority_id, str) or authority_id not in known:
                errors.append(f"{prefix}.id is not present in the authority manifest")
                continue
            declared_role = known[authority_id].get("role")
            if role is None:
                role = declared_role
            if role != declared_role:
                errors.append(f"{authority_id} requested as {role}, but manifest role is {declared_role}")
            allowed = set(known[authority_id].get("allowed_influence", []))
            forbidden = set(known[authority_id].get("forbidden_influence", []))
            unique_key = f"project:{authority_id}"
        else:
            if role not in ALLOWED_ROLES:
                errors.append(f"{prefix}.role must be one of {sorted(ALLOWED_ROLES)} for inline references")
                continue
            if not isinstance(authority_id, str) or not authority_id.strip():
                errors.append(f"{prefix}.id must be a non-empty ephemeral ID for inline references")
                continue
            allowed = DEFAULT_INLINE_ALLOWED[role]
            forbidden = set()
            unique_key = f"inline:{authority_id}"

        if unique_key in seen_keys:
            errors.append(f"duplicate reference: {authority_id}")
            continue
        seen_keys.add(unique_key)

        influence = ref.get("influence")
        if influence is not None:
            influence_list = _string_list(influence)
            if influence_list is None:
                errors.append(f"{prefix}.influence must be a string array when present")
            else:
                for prop in influence_list:
                    if prop not in allowed:
                        errors.append(f"{authority_id} is not allowed to control {prop!r}")
                    if prop in forbidden:
                        errors.append(f"{authority_id} explicitly forbids control of {prop!r}")
                    prior = claimed_properties.get(prop)
                    if prior is not None and prior != unique_key:
                        errors.append(f"authority conflict for {prop!r}: {prior} and {unique_key} both claim it")
                    claimed_properties[prop] = unique_key

    edit_target = request.get("edit_target")
    if mode == "FRESH" and edit_target:
        errors.append("fresh generation cannot include an edit target")
    if mode == "EDIT" and (not isinstance(edit_target, str) or not edit_target.strip()):
        errors.append("edit mode requires a non-empty edit_target")

    source_profile = request.get("source_profile")
    if source_profile is not None and (not isinstance(source_profile, str) or not source_profile.strip()):
        errors.append("request.source_profile must be a non-empty string when present")

    for field in ("composition", "lighting", "preserve", "avoid"):
        value = request.get(field, [])
        if value is not None and _string_list(value) is None:
            errors.append(f"request.{field} must be a string array when present")

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
