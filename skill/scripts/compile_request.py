#!/usr/bin/env python3
"""Compile W-Pack first-pass and conditional style-recovery requests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_authorities import DEFAULT_INLINE_ALLOWED, load_json, resolve_active_references, resolve_profile_name, validate_manifest, validate_request

COMPILED_SCHEMA = "WPACK_COMPILED_REQUEST_v1.2"
STYLE_AUDIT_SCHEMA = "WPACK_STYLE_AUDIT_v1.0"
RECOVERY_SCHEMA = "WPACK_STYLE_RECOVERY_REQUEST_v1.0"

STYLE_FINGERPRINT_AXES = ["visual_medium", "degree_of_realism", "edge_grammar", "shape_abstraction", "value_structure", "color_behavior", "surface_treatment", "background_rendering"]


def _compile_references(manifest: dict[str, Any], request: dict[str, Any]) -> list[dict[str, Any]]:
    known = manifest["authorities"]
    active = resolve_active_references(manifest, request)
    compiled: list[dict[str, Any]] = []
    for ref in active:
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
        compiled.append({"id": authority_id, "source": source, "file": file_name, "role": role, "allowed_influence": allowed, "forbidden_influence": forbidden})
    style_refs = [item for item in compiled if item["role"] == "STYLE"]
    if len(style_refs) == 1:
        style_refs[0]["authority_role"] = "STYLE_CORE"
    return compiled


def _style_core(references: list[dict[str, Any]]) -> dict[str, Any] | None:
    cores = [item for item in references if item.get("authority_role") == "STYLE_CORE"]
    return cores[0] if len(cores) == 1 else None


def compile_request(manifest: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if not errors:
        errors.extend(validate_request(request, manifest))
    if errors:
        raise ValueError("; ".join(errors))
    references = _compile_references(manifest, request)
    mode = request.get("mode", "FRESH")
    profile_name = resolve_profile_name(manifest, request)
    core = _style_core(references)
    recovery_enabled = mode == "FRESH" and core is not None
    constraints: dict[str, Any] = {
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
    if core is not None:
        constraints.update({
            "style_fidelity": "HIGH",
            "medium_lock": "REFERENCE",
            "photorealism_normalization": "DISABLED_UNLESS_EXPLICITLY_REQUESTED",
            "photographic_terms_do_not_override_reference_medium": True,
            "style_core_precedence": "ABSOLUTE_FOR_GLOBAL_VISUAL_GRAMMAR",
            "style_fingerprint_axes": STYLE_FINGERPRINT_AXES,
        })
    workflow = {
        "mode": "FRESH_FIRST" if mode == "FRESH" else "USER_REQUESTED_EDIT",
        "first_pass_count": 1,
        "automatic_generation_pass_limit": 2 if recovery_enabled else 1,
        "style_recovery": {
            "enabled": recovery_enabled,
            "trigger": "STRUCTURE_PASS_AND_STYLE_FAIL",
            "method": "SINGLE_RESTYLE",
            "maximum_restyle_depth": 1,
            "recursive_restyle_allowed": False,
            "automatic_third_pass_allowed": False,
            "automatic_fresh_retry_after_recovery_failure": False,
            "requires_singular_style_core": True,
        },
    }
    return {
        "schema_version": COMPILED_SCHEMA,
        "mode": mode,
        "scene": request["scene"].strip(),
        "aspect_ratio": request.get("aspect_ratio"),
        "references": references,
        "composition": request.get("composition", []),
        "lighting": request.get("lighting", []),
        "exact_text": request.get("exact_text"),
        "preserve": request.get("preserve", []),
        "avoid": request.get("avoid", []),
        "edit_target": request.get("edit_target") if mode == "EDIT" else None,
        "edit_type": request.get("edit_type") if mode == "EDIT" else None,
        "source_profile": profile_name,
        "use_default_sources": request.get("use_default_sources", True),
        "generation_constraints": constraints,
        "workflow": workflow,
    }


def compile_style_recovery(manifest: dict[str, Any], original_request: dict[str, Any], audit: dict[str, Any], candidate_id: str = "current-generated-candidate") -> dict[str, Any]:
    compiled = compile_request(manifest, original_request)
    recovery = compiled["workflow"]["style_recovery"]
    if not recovery["enabled"]:
        raise ValueError("style recovery is not enabled for this request")
    if audit.get("schema_version") != STYLE_AUDIT_SCHEMA:
        raise ValueError(f"audit.schema_version must be {STYLE_AUDIT_SCHEMA}")
    if audit.get("structure_status") != "PASS" or audit.get("style_status") != "FAIL":
        raise ValueError("style recovery requires structure_status=PASS and style_status=FAIL")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")
    core = _style_core(compiled["references"])
    if core is None:
        raise ValueError("style recovery requires exactly one STYLE_CORE")
    failure_axes = audit.get("failure_axes", [])
    if not isinstance(failure_axes, list) or any(not isinstance(item, str) for item in failure_axes):
        raise ValueError("audit.failure_axes must be a string array")
    preserve = [
        "subject identity and stable appearance",
        "pose and body arrangement",
        "composition, crop, camera angle, and spatial relationships",
        "object count, scale, ownership, and physical contact",
        "scene conditions and environment content",
    ]
    if original_request.get("exact_text"):
        preserve.append("exact text content and placement")
    recovery_refs = [
        {"id": "STRUCTURE_EDIT_TARGET", "source": "CURRENT_CANDIDATE", "candidate_id": candidate_id, "role": "STRUCTURE_EDIT_TARGET", "authority": "CONTENT_AND_GEOMETRY_ONLY", "style_authority": False},
        {"id": core["id"], "source": core["source"], "file": core.get("file"), "role": "STYLE_CORE", "authority": "GLOBAL_VISUAL_GRAMMAR_ONLY", "allowed_influence": core["allowed_influence"], "forbidden_influence": core["forbidden_influence"]},
    ]
    return {
        "schema_version": RECOVERY_SCHEMA,
        "operation": "SINGLE_RESTYLE",
        "restyle_pass": 1,
        "source_generation_mode": "FRESH",
        "trigger": {"structure_status": "PASS", "style_status": "FAIL", "failure_axes": failure_axes},
        "references": recovery_refs,
        "preserve": preserve,
        "change_only": ["rendering style and global visual grammar"],
        "constraints": {
            "use_default_sources": False,
            "sole_style_authority": core["id"],
            "no_additional_authority_references": True,
            "no_recompose": True,
            "no_crop": True,
            "no_rotate": True,
            "no_mirror": True,
            "no_zoom": True,
            "no_add_remove_replace_duplicate_content": True,
            "maximum_restyle_depth": 1,
            "recursive_restyle_allowed": False,
            "automatic_third_pass_allowed": False,
            "automatic_fresh_retry_after_failure": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile W-Pack generation request")
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
