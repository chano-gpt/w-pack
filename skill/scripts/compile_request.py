#!/usr/bin/env python3
"""Compile W-Pack first-pass and conditional style-recovery requests."""

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
    resolve_style_role,
    validate_manifest,
    validate_request,
)

COMPILED_SCHEMA = "WPACK_COMPILED_REQUEST_v1.3"
STYLE_AUDIT_SCHEMA = "WPACK_STYLE_AUDIT_v1.1"
RECOVERY_SCHEMA = "WPACK_STYLE_RECOVERY_REQUEST_v1.1"

STYLE_FINGERPRINT_AXES = [
    "visual_medium",
    "degree_of_realism",
    "edge_grammar",
    "shape_abstraction",
    "value_structure",
    "color_behavior",
    "surface_treatment",
    "background_rendering",
    "hair_rendering_grammar",
]

VISUALLY_CONFIRMED_STATES = {"VISUAL_BOUND"}
TEXT_PROFILE_STATES = {"PROJECT_CONTEXT_ONLY", "TEXT_PROFILE_ONLY", "UNVERIFIED_PROJECT_SOURCE"}


def _as_text_profile(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _default_transport_state(source: str) -> str:
    return "VISUAL_INPUT_EXPECTED" if source == "INLINE_AUTHORITY" else "UNVERIFIED_PROJECT_SOURCE"


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
            style_signature = ref.get("style_signature", authority.get("style_signature"))
            anti_drift = ref.get("anti_drift_signature", authority.get("anti_drift_signature"))
            support_domains = ref.get("support_domains", authority.get("support_domains", []))
            transport_state = ref.get("transport_state", authority.get("transport_state", _default_transport_state(source)))
        else:
            role = ref["role"]
            allowed = ref.get("influence") or sorted(DEFAULT_INLINE_ALLOWED[role])
            forbidden = []
            file_name = ref.get("file")
            style_signature = ref.get("style_signature")
            anti_drift = ref.get("anti_drift_signature")
            support_domains = ref.get("support_domains", ref.get("influence", []))
            transport_state = ref.get("transport_state", _default_transport_state(source))

        item: dict[str, Any] = {
            "id": authority_id,
            "source": source,
            "file": file_name,
            "role": role,
            "allowed_influence": allowed,
            "forbidden_influence": forbidden,
            "transport": {
                "state": transport_state,
                "direct_visual_binding_confirmed": transport_state in VISUALLY_CONFIRMED_STATES,
                "runtime_verification_required": transport_state not in VISUALLY_CONFIRMED_STATES,
            },
        }
        if role == "STYLE":
            item["style_role"] = resolve_style_role(ref, manifest)
            item["style_signature"] = _as_text_profile(style_signature)
            item["anti_drift_signature"] = _as_text_profile(anti_drift)
            item["support_domains"] = support_domains if isinstance(support_domains, list) else []
        compiled.append(item)

    style_refs = [item for item in compiled if item["role"] == "STYLE"]
    if len(style_refs) == 1 and style_refs[0].get("style_role") is None:
        style_refs[0]["style_role"] = "CORE"
    for item in style_refs:
        if item.get("style_role") == "CORE":
            item["authority_role"] = "STYLE_CORE"
        elif item.get("style_role") == "SUPPORT":
            item["authority_role"] = "STYLE_SUPPORT"
    return compiled


def _style_core(references: list[dict[str, Any]]) -> dict[str, Any] | None:
    cores = [item for item in references if item.get("authority_role") == "STYLE_CORE"]
    return cores[0] if len(cores) == 1 else None


def _style_supports(references: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in references if item.get("authority_role") == "STYLE_SUPPORT"]


def _text_style_dna_available(ref: dict[str, Any] | None) -> bool:
    if ref is None:
        return False
    return bool(ref.get("style_signature") or ref.get("anti_drift_signature"))


def _core_usable_for_recovery(core: dict[str, Any] | None) -> bool:
    if core is None:
        return False
    state = core.get("transport", {}).get("state")
    return state in VISUALLY_CONFIRMED_STATES or _text_style_dna_available(core)


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
    supports = _style_supports(references)
    recovery_enabled = mode == "FRESH" and core is not None and _core_usable_for_recovery(core)

    constraints: dict[str, Any] = {
        "use_chatgpt_builtin_image_generation": True,
        "maximum_reference_count": 5,
        "fresh_generation_default": True,
        "project_sources_default_active": request.get("use_default_sources", True),
        "resolved_default_source_profile": profile_name,
        "inline_references_are_secondary": True,
        "combine_style_sources": request.get("combine_style_sources", False),
        "resolve_roles_from_user_language_not_visual_incidence": True,
        "do_not_expand_authority_scope": True,
        "preserve_exact_text_when_present": True,
        "do_not_reuse_prior_candidate_without_edit_intent": True,
        "project_membership_is_not_visual_binding_proof": True,
        "reference_transport_verification_required": True,
        "text_fallback_must_not_claim_exact_visual_fidelity": True,
        "hair_rendering_default": "CLEAN_MASS_WHEN_UNSPECIFIED",
    }
    if core is not None:
        constraints.update({
            "style_fidelity": "HIGH",
            "medium_lock": "STYLE_CORE",
            "photorealism_normalization": "DISABLED_UNLESS_EXPLICITLY_REQUESTED",
            "photographic_terms_do_not_override_reference_medium": True,
            "style_core_precedence": "ABSOLUTE_FOR_GLOBAL_VISUAL_GRAMMAR",
            "style_fingerprint_axes": STYLE_FINGERPRINT_AXES,
            "style_support_count": len(supports),
            "style_support_may_override_core": False,
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
            "requires_visual_binding_or_style_dna": True,
            "maximum_support_adapters": 1,
        },
    }

    style_family = {
        "style_core_id": core["id"] if core else None,
        "style_support_ids": [item["id"] for item in supports],
        "core_transport_state": core.get("transport", {}).get("state") if core else None,
        "core_style_dna_available": _text_style_dna_available(core),
        "core_usable_for_recovery": _core_usable_for_recovery(core),
        "support_may_override_core": False,
    }

    return {
        "schema_version": COMPILED_SCHEMA,
        "mode": mode,
        "scene": request["scene"].strip(),
        "aspect_ratio": request.get("aspect_ratio"),
        "references": references,
        "style_family": style_family,
        "composition": request.get("composition", []),
        "lighting": request.get("lighting", []),
        "exact_text": request.get("exact_text"),
        "preserve": request.get("preserve", []),
        "avoid": request.get("avoid", []),
        "edit_target": request.get("edit_target") if mode == "EDIT" else None,
        "edit_type": request.get("edit_type") if mode == "EDIT" else None,
        "source_profile": profile_name,
        "use_default_sources": request.get("use_default_sources", True),
        "combine_style_sources": request.get("combine_style_sources", False),
        "generation_constraints": constraints,
        "workflow": workflow,
    }


def _select_recovery_support(references: list[dict[str, Any]], failure_axes: list[str]) -> dict[str, Any] | None:
    failures = set(failure_axes)
    for support in _style_supports(references):
        domains = set(support.get("support_domains") or support.get("allowed_influence") or [])
        if failures & domains:
            return support
    return None


def compile_style_recovery(
    manifest: dict[str, Any],
    original_request: dict[str, Any],
    audit: dict[str, Any],
    candidate_id: str = "current-generated-candidate",
) -> dict[str, Any]:
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
    if not _core_usable_for_recovery(core):
        raise ValueError("style recovery requires confirmed STYLE_CORE visual binding or usable STYLE DNA")

    failure_axes = audit.get("failure_axes", [])
    if not isinstance(failure_axes, list) or any(not isinstance(item, str) for item in failure_axes):
        raise ValueError("audit.failure_axes must be a string array")
    support = _select_recovery_support(compiled["references"], failure_axes)

    preserve = [
        "subject identity and stable appearance",
        "pose and body arrangement",
        "composition, crop, camera angle, and spatial relationships",
        "object count, scale, ownership, and physical contact",
        "scene conditions and environment content",
    ]
    change_only = ["rendering style and global visual grammar"]
    if "hair_rendering_grammar" in failure_axes:
        preserve.append("hairstyle geometry: length, parting, bang shape, volume, direction, and major lock placement")
        change_only.append("hair rendering grammar: strand density, silhouette noise, tip branching, highlight granularity, and lock grouping")
    if original_request.get("exact_text"):
        preserve.append("exact text content and placement")

    recovery_refs: list[dict[str, Any]] = [
        {
            "id": "STRUCTURE_EDIT_TARGET",
            "source": "CURRENT_CANDIDATE",
            "candidate_id": candidate_id,
            "role": "STRUCTURE_EDIT_TARGET",
            "authority": "CONTENT_AND_GEOMETRY_ONLY",
            "style_authority": False,
        },
        {
            "id": core["id"],
            "source": core["source"],
            "file": core.get("file"),
            "role": "STYLE_CORE",
            "authority": "GLOBAL_VISUAL_GRAMMAR_ONLY",
            "allowed_influence": core["allowed_influence"],
            "forbidden_influence": core["forbidden_influence"],
            "transport": core.get("transport"),
            "style_signature": core.get("style_signature", []),
            "anti_drift_signature": core.get("anti_drift_signature", []),
        },
    ]
    if support is not None:
        recovery_refs.append({
            "id": support["id"],
            "source": support["source"],
            "file": support.get("file"),
            "role": "STYLE_SUPPORT",
            "authority": "BOUNDED_STYLE_ADAPTER_ONLY",
            "allowed_influence": support["allowed_influence"],
            "support_domains": support.get("support_domains", []),
            "transport": support.get("transport"),
            "style_signature": support.get("style_signature", []),
            "anti_drift_signature": support.get("anti_drift_signature", []),
        })

    return {
        "schema_version": RECOVERY_SCHEMA,
        "operation": "SINGLE_RESTYLE",
        "restyle_pass": 1,
        "source_generation_mode": "FRESH",
        "trigger": {
            "structure_status": "PASS",
            "style_status": "FAIL",
            "failure_axes": failure_axes,
        },
        "references": recovery_refs,
        "preserve": preserve,
        "change_only": change_only,
        "constraints": {
            "use_default_sources": False,
            "style_core_authority": core["id"],
            "style_support_adapter": support["id"] if support else None,
            "maximum_support_adapters": 1,
            "no_additional_non_style_authority_references": True,
            "style_support_may_override_core": False,
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
