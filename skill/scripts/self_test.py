#!/usr/bin/env python3
"""Run deterministic smoke tests for the W-Pack v0.5.1 web workflow."""

from __future__ import annotations

import json
from pathlib import Path

from compile_request import (
    COMPILED_SCHEMA,
    RECOVERY_SCHEMA,
    STYLE_AUDIT_SCHEMA,
    STYLE_FINGERPRINT_AXES,
    compile_request,
    compile_style_recovery,
)
from validate_authorities import load_json, validate_manifest, validate_request

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "references" / "authority-manifest.example.json"
REQUEST = ROOT / "references" / "generation-request.example.json"


def expect_error(fn, fragment: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), (fragment, str(exc))
    else:
        raise AssertionError(f"expected error containing {fragment!r}")


def main() -> int:
    manifest = load_json(MANIFEST)
    request = load_json(REQUEST)

    assert manifest["schema_version"] == "WPACK_AUTHORITY_MANIFEST_v1.1"
    assert request["schema_version"] == "WPACK_GENERATION_REQUEST_v1.2"
    assert not validate_manifest(manifest), validate_manifest(manifest)
    assert not validate_request(request, manifest), validate_request(request, manifest)

    compiled = compile_request(manifest, request)
    assert compiled["schema_version"] == COMPILED_SCHEMA == "WPACK_COMPILED_REQUEST_v1.3"
    assert compiled["source_profile"] == "DEFAULT"
    assert [ref["id"] for ref in compiled["references"]] == [
        "STYLE_CORE_01", "STYLE_SUPPORT_01", "CHARACTER_01", "PROPORTION_01"
    ]
    style_core = compiled["references"][0]
    style_support = compiled["references"][1]
    assert style_core["authority_role"] == "STYLE_CORE"
    assert style_support["authority_role"] == "STYLE_SUPPORT"
    assert style_core["transport"]["state"] == "UNVERIFIED_PROJECT_SOURCE"
    assert style_core["transport"]["direct_visual_binding_confirmed"] is False
    assert compiled["style_family"]["style_core_id"] == "STYLE_CORE_01"
    assert compiled["style_family"]["style_support_ids"] == ["STYLE_SUPPORT_01"]
    assert compiled["style_family"]["core_style_dna_available"] is True
    assert compiled["style_family"]["core_usable_for_recovery"] is True
    assert "hair_rendering_grammar" in STYLE_FINGERPRINT_AXES
    assert compiled["generation_constraints"]["hair_rendering_default"] == "CLEAN_MASS_WHEN_UNSPECIFIED"
    assert compiled["generation_constraints"]["style_core_precedence"] == "ABSOLUTE_FOR_GLOBAL_VISUAL_GRAMMAR"
    assert compiled["workflow"]["mode"] == "FRESH_FIRST"
    assert compiled["workflow"]["automatic_generation_pass_limit"] == 2
    assert compiled["workflow"]["style_recovery"]["enabled"] is True
    assert compiled["workflow"]["style_recovery"]["maximum_support_adapters"] == 1

    audit = {
        "schema_version": STYLE_AUDIT_SCHEMA,
        "structure_status": "PASS",
        "style_status": "FAIL",
        "failure_axes": ["color_behavior", "hair_rendering_grammar"],
    }
    recovery = compile_style_recovery(manifest, request, audit)
    assert recovery["schema_version"] == RECOVERY_SCHEMA == "WPACK_STYLE_RECOVERY_REQUEST_v1.1"
    assert recovery["operation"] == "SINGLE_RESTYLE"
    assert recovery["restyle_pass"] == 1
    assert [ref["role"] for ref in recovery["references"]] == [
        "STRUCTURE_EDIT_TARGET", "STYLE_CORE", "STYLE_SUPPORT"
    ]
    assert recovery["references"][2]["id"] == "STYLE_SUPPORT_01"
    assert recovery["constraints"]["style_core_authority"] == "STYLE_CORE_01"
    assert recovery["constraints"]["style_support_adapter"] == "STYLE_SUPPORT_01"
    assert recovery["constraints"]["recursive_restyle_allowed"] is False
    assert recovery["constraints"]["automatic_third_pass_allowed"] is False
    assert any("hairstyle geometry" in item for item in recovery["preserve"])
    assert any("hair rendering grammar" in item for item in recovery["change_only"])

    hair_only = {**audit, "failure_axes": ["hair_rendering_grammar"]}
    hair_recovery = compile_style_recovery(manifest, request, hair_only)
    assert len(hair_recovery["references"]) == 2
    assert hair_recovery["constraints"]["style_support_adapter"] is None

    structure_fail = {**audit, "structure_status": "FAIL"}
    expect_error(
        lambda: compile_style_recovery(manifest, request, structure_fail),
        "requires structure_status=PASS and style_status=FAIL",
    )
    style_pass = {**audit, "style_status": "PASS"}
    expect_error(
        lambda: compile_style_recovery(manifest, request, style_pass),
        "requires structure_status=PASS and style_status=FAIL",
    )

    no_sources = json.loads(json.dumps(request))
    no_sources["use_default_sources"] = False
    compiled_no_sources = compile_request(manifest, no_sources)
    assert compiled_no_sources["references"] == []
    assert compiled_no_sources["workflow"]["automatic_generation_pass_limit"] == 1
    assert compiled_no_sources["workflow"]["style_recovery"]["enabled"] is False

    inline_override = json.loads(json.dumps(request))
    inline_override["references"] = [{
        "source": "INLINE_AUTHORITY",
        "id": "INLINE_STYLE_01",
        "role": "STYLE",
        "influence": ["visual_medium", "rendering_language", "degree_of_realism", "hair_rendering_grammar"],
    }]
    compiled_override = compile_request(manifest, inline_override)
    override_ids = [ref["id"] for ref in compiled_override["references"]]
    assert "STYLE_CORE_01" not in override_ids and "STYLE_SUPPORT_01" not in override_ids
    assert "INLINE_STYLE_01" in override_ids
    override_core = next(ref for ref in compiled_override["references"] if ref["id"] == "INLINE_STYLE_01")
    assert override_core["authority_role"] == "STYLE_CORE"
    assert "CHARACTER_01" in override_ids and "PROPORTION_01" in override_ids
    assert compiled_override["workflow"]["style_recovery"]["enabled"] is False

    combined = json.loads(json.dumps(request))
    combined["combine_style_sources"] = True
    combined["references"] = [{
        "source": "INLINE_AUTHORITY",
        "id": "INLINE_SUPPORT_02",
        "role": "STYLE",
        "style_role": "SUPPORT",
        "influence": ["color_behavior"],
        "support_domains": ["color_behavior"],
    }]
    assert not validate_request(combined, manifest), validate_request(combined, manifest)
    compiled_combined = compile_request(manifest, combined)
    assert len(compiled_combined["references"]) == 5
    assert compiled_combined["style_family"]["style_support_ids"] == ["STYLE_SUPPORT_01", "INLINE_SUPPORT_02"]

    ambiguous_multi_style = json.loads(json.dumps(request))
    ambiguous_multi_style["use_default_sources"] = False
    ambiguous_multi_style["references"] = [
        {"source": "INLINE_AUTHORITY", "id": "INLINE_STYLE_A", "role": "STYLE", "influence": ["visual_medium"]},
        {"source": "INLINE_AUTHORITY", "id": "INLINE_STYLE_B", "role": "STYLE", "influence": ["color_behavior"]},
    ]
    errors = validate_request(ambiguous_multi_style, manifest)
    assert any("must declare one CORE" in error for error in errors), errors

    no_dna_manifest = json.loads(json.dumps(manifest))
    no_dna_manifest["authorities"]["STYLE_CORE_01"].pop("style_signature", None)
    no_dna_manifest["authorities"]["STYLE_CORE_01"].pop("anti_drift_signature", None)
    assert not validate_manifest(no_dna_manifest), validate_manifest(no_dna_manifest)
    compiled_no_dna = compile_request(no_dna_manifest, request)
    assert compiled_no_dna["style_family"]["core_usable_for_recovery"] is False
    assert compiled_no_dna["workflow"]["style_recovery"]["enabled"] is False

    edit = json.loads(json.dumps(request))
    edit["mode"] = "EDIT"
    edit["edit_target"] = "current-conversation-image"
    compiled_edit = compile_request(manifest, edit)
    assert compiled_edit["workflow"]["mode"] == "USER_REQUESTED_EDIT"
    assert compiled_edit["workflow"]["style_recovery"]["enabled"] is False

    print("W-Pack self-test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
