#!/usr/bin/env python3
"""Validate W-Pack manifests/requests and resolve Project-default references."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MANIFEST_SCHEMAS = {"WPACK_AUTHORITY_MANIFEST_v1.0", "WPACK_AUTHORITY_MANIFEST_v1.1"}
REQUEST_SCHEMAS = {
    "WPACK_GENERATION_REQUEST_v1.0",
    "WPACK_GENERATION_REQUEST_v1.1",
    "WPACK_GENERATION_REQUEST_v1.2",
}
ALLOWED_ROLES = {"STYLE", "CHARACTER", "POSE", "COMPOSITION", "PROPORTION", "ITEM"}
ALLOWED_SOURCES = {"PROJECT_AUTHORITY", "INLINE_AUTHORITY"}
STYLE_ROLES = {"CORE", "SUPPORT"}
REFERENCE_SLOT_LIMIT = 5
MAX_STYLE_REFERENCES = 3
MAX_STYLE_SUPPORTS = 2
TRANSPORT_STATES = {
    "VISUAL_BOUND",
    "VISUAL_INPUT_EXPECTED",
    "PROJECT_CONTEXT_ONLY",
    "TEXT_PROFILE_ONLY",
    "UNVERIFIED_PROJECT_SOURCE",
    "UNAVAILABLE",
}
CORE_ONLY_STYLE_AXES = {"visual_medium", "degree_of_realism", "shape_abstraction"}
STYLE_SUPPORT_AXES = {
    "palette",
    "texture",
    "lighting_language",
    "graphic_treatment",
    "surface_treatment",
    "value_structure",
    "color_behavior",
    "background_rendering",
    "edge_treatment",
    "edge_grammar",
    "hair_rendering_grammar",
}

ROLE_REQUIRED_ALLOWED = {
    "STYLE": set(),
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
    "STYLE": {
        "palette", "texture", "lighting_language", "graphic_treatment",
        "rendering_language", "surface_treatment", "typography_character",
        "visual_medium", "stylization_level", "edge_treatment", "edge_grammar",
        "shape_abstraction", "value_structure", "color_behavior",
        "background_rendering", "degree_of_realism", "hair_rendering_grammar",
    },
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


def _text_profile(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return bool(value.strip())
    values = _string_list(value)
    return values is not None and bool(values)


def _source_profiles(manifest: dict[str, Any]) -> dict[str, list[str]]:
    value = manifest.get("source_profiles", {})
    return value if isinstance(value, dict) else {}


def resolve_profile_name(manifest: dict[str, Any], request: dict[str, Any]) -> str | None:
    if request.get("use_default_sources", True) is False:
        return None
    requested = request.get("source_profile")
    if isinstance(requested, str) and requested.strip():
        return requested
    configured = manifest.get("default_source_profile")
    if isinstance(configured, str) and configured.strip():
        return configured
    profiles = _source_profiles(manifest)
    return "DEFAULT" if "DEFAULT" in profiles else None


def _reference_role(ref: dict[str, Any], manifest: dict[str, Any]) -> str | None:
    if ref.get("source", "PROJECT_AUTHORITY") == "PROJECT_AUTHORITY":
        authority = manifest.get("authorities", {}).get(ref.get("id"), {})
        return authority.get("role")
    return ref.get("role")


def resolve_style_role(ref: dict[str, Any], manifest: dict[str, Any]) -> str | None:
    explicit = ref.get("style_role")
    if explicit in STYLE_ROLES:
        return explicit
    if ref.get("source", "PROJECT_AUTHORITY") == "PROJECT_AUTHORITY":
        authority = manifest.get("authorities", {}).get(ref.get("id"), {})
        declared = authority.get("style_role")
        return declared if declared in STYLE_ROLES else None
    return None


def resolve_active_references(manifest: dict[str, Any], request: dict[str, Any]) -> list[dict[str, Any]]:
    profile_name = resolve_profile_name(manifest, request)
    profiles = _source_profiles(manifest)
    explicit = request.get("references", request.get("authorities", []))
    if not isinstance(explicit, list):
        return []

    defaults: list[dict[str, Any]] = []
    if profile_name is not None:
        for authority_id in profiles.get(profile_name, []):
            defaults.append({"source": "PROJECT_AUTHORITY", "id": authority_id})

    explicit_non_style_roles = {
        role for ref in explicit
        if isinstance(ref, dict)
        and (role := _reference_role(ref, manifest)) in ALLOWED_ROLES
        and role != "STYLE"
    }
    defaults = [
        ref for ref in defaults
        if _reference_role(ref, manifest) not in explicit_non_style_roles
    ]

    explicit_styles = [
        ref for ref in explicit
        if isinstance(ref, dict) and _reference_role(ref, manifest) == "STYLE"
    ]
    if explicit_styles and not request.get("combine_style_sources", False):
        defaults = [ref for ref in defaults if _reference_role(ref, manifest) != "STYLE"]

    merged = defaults + [ref for ref in explicit if isinstance(ref, dict)]
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ref in merged:
        source = ref.get("source", "PROJECT_AUTHORITY")
        key = f"{source}:{ref.get('id')}"
        if key in seen:
            continue
        seen.add(key)
        output.append(ref)
    return output


def _style_family_errors(refs: list[dict[str, Any]], manifest: dict[str, Any], context: str) -> list[str]:
    errors: list[str] = []
    styles = [ref for ref in refs if _reference_role(ref, manifest) == "STYLE"]
    if not styles:
        return errors
    if len(styles) > MAX_STYLE_REFERENCES:
        errors.append(f"{context} uses {len(styles)} STYLE references; limit is {MAX_STYLE_REFERENCES}")
        return errors

    resolved = [resolve_style_role(ref, manifest) for ref in styles]
    if len(styles) == 1 and resolved[0] is None:
        return errors

    if any(role is None for role in resolved):
        errors.append(f"{context} with multiple STYLE references must declare one CORE and all others SUPPORT")
        return errors
    cores = sum(role == "CORE" for role in resolved)
    supports = sum(role == "SUPPORT" for role in resolved)
    if cores != 1:
        errors.append(f"{context} must resolve exactly one STYLE CORE; found {cores}")
    if supports > MAX_STYLE_SUPPORTS:
        errors.append(f"{context} uses {supports} STYLE SUPPORT references; limit is {MAX_STYLE_SUPPORTS}")
    return errors


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") not in MANIFEST_SCHEMAS:
        errors.append(f"schema_version must be one of {sorted(MANIFEST_SCHEMAS)}")
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

        transport_state = authority.get("transport_state")
        if transport_state is not None and transport_state not in TRANSPORT_STATES:
            errors.append(f"{prefix}.transport_state must be one of {sorted(TRANSPORT_STATES)}")
        for field in ("style_signature", "anti_drift_signature"):
            if field in authority and not _text_profile(authority.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string or string array")

        if role == "STYLE":
            style_role = authority.get("style_role")
            if style_role is not None and style_role not in STYLE_ROLES:
                errors.append(f"{prefix}.style_role must be CORE or SUPPORT when present")
            if style_role == "CORE":
                for required in ("rendering_language", "visual_medium"):
                    if required not in allowed_set:
                        errors.append(f"{prefix} STYLE CORE must allow {required!r}")
            if style_role == "SUPPORT":
                invalid = sorted(allowed_set & CORE_ONLY_STYLE_AXES)
                if invalid:
                    errors.append(f"{prefix} STYLE SUPPORT cannot control core-only axes: {invalid}")
                domains = _string_list(authority.get("support_domains"))
                if domains is None or not domains:
                    errors.append(f"{prefix}.support_domains must be a non-empty string array for STYLE SUPPORT")
                else:
                    invalid_domains = sorted(set(domains) - STYLE_SUPPORT_AXES)
                    if invalid_domains:
                        errors.append(f"{prefix}.support_domains contains unsupported axes: {invalid_domains}")
                    outside_allowed = sorted(set(domains) - allowed_set)
                    if outside_allowed:
                        errors.append(f"{prefix}.support_domains must be included in allowed_influence: {outside_allowed}")

    profiles = manifest.get("source_profiles", {})
    if not isinstance(profiles, dict):
        errors.append("source_profiles must be an object when present")
        profiles = {}
    for profile_name, ids in profiles.items():
        prefix = f"source profile {profile_name!r}"
        id_list = _string_list(ids)
        if not isinstance(profile_name, str) or not profile_name.strip():
            errors.append("source profile names must be non-empty strings")
            continue
        if id_list is None or not id_list:
            errors.append(f"{prefix} must be a non-empty string array")
            continue
        if len(id_list) > REFERENCE_SLOT_LIMIT:
            errors.append(f"{prefix} uses {len(id_list)} references; limit is {REFERENCE_SLOT_LIMIT}")
        if len(set(id_list)) != len(id_list):
            errors.append(f"{prefix} contains duplicate authority IDs")
        refs: list[dict[str, Any]] = []
        non_style_roles: set[str] = set()
        for authority_id in id_list:
            if authority_id not in authorities:
                errors.append(f"{prefix} references unknown authority {authority_id!r}")
                continue
            refs.append({"source": "PROJECT_AUTHORITY", "id": authority_id})
            role = authorities[authority_id].get("role")
            if role != "STYLE":
                if role in non_style_roles:
                    errors.append(f"{prefix} contains more than one default authority for role {role}")
                non_style_roles.add(role)
        errors.extend(_style_family_errors(refs, manifest, prefix))

    default_profile = manifest.get("default_source_profile")
    if default_profile is not None:
        if not isinstance(default_profile, str) or not default_profile.strip():
            errors.append("default_source_profile must be a non-empty string when present")
        elif default_profile not in profiles:
            errors.append("default_source_profile must name an existing source profile")
    return errors


def _request_references(request: dict[str, Any]) -> Any:
    return request.get("references") if "references" in request else request.get("authorities", [])


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
    use_default_sources = request.get("use_default_sources", True)
    if not isinstance(use_default_sources, bool):
        errors.append("request.use_default_sources must be a boolean when present")
    combine_style_sources = request.get("combine_style_sources", False)
    if not isinstance(combine_style_sources, bool):
        errors.append("request.combine_style_sources must be a boolean when present")

    profiles = _source_profiles(manifest)
    source_profile = request.get("source_profile")
    if source_profile is not None:
        if not isinstance(source_profile, str) or not source_profile.strip():
            errors.append("request.source_profile must be a non-empty string when present")
        elif source_profile not in profiles:
            errors.append(f"request.source_profile {source_profile!r} is not defined in the manifest")

    references = _request_references(request)
    if not isinstance(references, list):
        errors.append("request.references must be an array")
        return errors
    if len(references) > REFERENCE_SLOT_LIMIT:
        errors.append(f"request uses {len(references)} explicit references; limit is {REFERENCE_SLOT_LIMIT}")

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
            declared_style_role = known[authority_id].get("style_role")
            if ref.get("style_role") is not None and ref.get("style_role") != declared_style_role:
                errors.append(f"{authority_id} style_role must match manifest declaration {declared_style_role!r}")
            unique_key = f"project:{authority_id}"
        else:
            if role not in ALLOWED_ROLES:
                errors.append(f"{prefix}.role must be one of {sorted(ALLOWED_ROLES)} for inline references")
                continue
            if not isinstance(authority_id, str) or not authority_id.strip():
                errors.append(f"{prefix}.id must be a non-empty ephemeral ID for inline references")
                continue
            allowed = DEFAULT_INLINE_ALLOWED[role]
            forbidden: set[str] = set()
            unique_key = f"inline:{authority_id}"

        if unique_key in seen_keys:
            errors.append(f"duplicate reference: {authority_id}")
            continue
        seen_keys.add(unique_key)

        if role == "STYLE":
            style_role = ref.get("style_role")
            if style_role is not None and style_role not in STYLE_ROLES:
                errors.append(f"{prefix}.style_role must be CORE or SUPPORT when present")
            if style_role == "SUPPORT":
                influence_value = ref.get("influence")
                if influence_value is None:
                    errors.append(f"{prefix}.influence is required for inline STYLE SUPPORT")
                else:
                    influence_list = _string_list(influence_value)
                    if influence_list is not None:
                        invalid = sorted(set(influence_list) & CORE_ONLY_STYLE_AXES)
                        if invalid:
                            errors.append(f"{prefix} STYLE SUPPORT cannot control core-only axes: {invalid}")

        transport_state = ref.get("transport_state")
        if transport_state is not None and transport_state not in TRANSPORT_STATES:
            errors.append(f"{prefix}.transport_state must be one of {sorted(TRANSPORT_STATES)}")
        for field in ("style_signature", "anti_drift_signature"):
            if field in ref and not _text_profile(ref.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string or string array")

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
                    if role != "STYLE":
                        prior = claimed_properties.get(prop)
                        if prior is not None and prior != unique_key:
                            errors.append(f"authority conflict for {prop!r}: {prior} and {unique_key} both claim it")
                        claimed_properties[prop] = unique_key

    if not errors:
        active = resolve_active_references(manifest, request)
        if len(active) > REFERENCE_SLOT_LIMIT:
            errors.append(f"request resolves to {len(active)} active references after default profile expansion; limit is {REFERENCE_SLOT_LIMIT}")
        errors.extend(_style_family_errors(active, manifest, "resolved request"))

    edit_target = request.get("edit_target")
    if mode == "FRESH" and edit_target:
        errors.append("fresh generation cannot include an edit target")
    if mode == "EDIT" and (not isinstance(edit_target, str) or not edit_target.strip()):
        errors.append("edit mode requires a non-empty edit_target")
    if request.get("aspect_ratio") is not None and not isinstance(request.get("aspect_ratio"), str):
        errors.append("request.aspect_ratio must be a string when present")
    exact_text = request.get("exact_text")
    if exact_text is not None and not isinstance(exact_text, str):
        errors.append("request.exact_text must be a string or null")
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
            errors.extend(validate_request(load_json(args.request), manifest))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
