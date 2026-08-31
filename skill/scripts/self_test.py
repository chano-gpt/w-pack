#!/usr/bin/env python3
"""Run deterministic smoke tests for W-Pack v0.4 web workflow."""

from __future__ import annotations

import json
from pathlib import Path

from compile_request import COMPILED_SCHEMA, RECOVERY_SCHEMA, STYLE_AUDIT_SCHEMA, compile_request, compile_style_recovery
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
    assert not validate_manifest(manifest), validate_manifest(manifest)
    assert not validate_request(request, manifest), validate_request(request, manifest)
    compiled = compile_request(manifest, request)
    assert compiled["schema_version"] == COMPILED_SCHEMA
    assert compiled["source_profile"] == "DEFAULT"
    assert [ref["id"] for ref in compiled["references"]] == ["STYLE_CORE_01", "CHARACTER_01", "PROPORTION_01"]
    style_core = compiled["references"][0]
    assert style_core["authority_role"] == "STYLE_CORE"
    assert compiled["generation_constraints"]["style_core_precedence"] == "ABSOLUTE_FOR_GLOBAL_VISUAL_GRAMMAR"
    assert compiled["workflow"]["mode"] == "FRESH_FIRST"
    assert compiled["workflow"]["automatic_generation_pass_limit"] == 2
    assert compiled["workflow"]["style_recovery"]["enabled"] is True
    assert compiled["workflow"]["style_recovery"]["maximum_restyle_depth"] == 1
    assert compiled["workflow"]["style_recovery"]["automatic_third_pass_allowed"] is False
    audit = {"schema_version": STYLE_AUDIT_SCHEMA, "structure_status": "PASS", "style_status": "FAIL", "failure_axes": ["visual_medium", "degree_of_realism", "edge_grammar"]}
    recovery = compile_style_recovery(manifest, request, audit)
    assert recovery["schema_version"] == RECOVERY_SCHEMA
    assert recovery["operation"] == "SINGLE_RESTYLE"
    assert recovery["restyle_pass"] == 1
    assert len(recovery["references"]) == 2
    assert recovery["references"][0]["role"] == "STRUCTURE_EDIT_TARGET"
    assert recovery["references"][1]["role"] == "STYLE_CORE"
    assert recovery["references"][1]["id"] == "STYLE_CORE_01"
    assert recovery["constraints"]["use_default_sources"] is False
    assert recovery["constraints"]["no_additional_authority_references"] is True
    assert recovery["constraints"]["recursive_restyle_allowed"] is False
    assert recovery["constraints"]["automatic_third_pass_allowed"] is False
    structure_fail = {**audit, "structure_status": "FAIL"}
    expect_error(lambda: compile_style_recovery(manifest, request, structure_fail), "requires structure_status=PASS and style_status=FAIL")
    style_pass = {**audit, "style_status": "PASS"}
    expect_error(lambda: compile_style_recovery(manifest, request, style_pass), "requires structure_status=PASS and style_status=FAIL")
    no_sources = json.loads(json.dumps(request))
    no_sources["use_default_sources"] = False
    compiled_no_sources = compile_request(manifest, no_sources)
    assert compiled_no_sources["references"] == []
    assert compiled_no_sources["workflow"]["automatic_generation_pass_limit"] == 1
    assert compiled_no_sources["workflow"]["style_recovery"]["enabled"] is False
    inline_override = json.loads(json.dumps(request))
    inline_override["references"] = [{"source": "INLINE_AUTHORITY", "id": "INLINE_STYLE_01", "role": "STYLE", "influence": ["visual_medium", "rendering_language", "degree_of_realism"]}]
    compiled_override = compile_request(manifest, inline_override)
    ids = [ref["id"] for ref in compiled_override["references"]]
    assert "STYLE_CORE_01" not in ids
    assert "INLINE_STYLE_01" in ids
    override_core = next(ref for ref in compiled_override["references"] if ref["id"] == "INLINE_STYLE_01")
    assert override_core["authority_role"] == "STYLE_CORE"
    assert "CHARACTER_01" in ids and "PROPORTION_01" in ids
    multi_style = json.loads(json.dumps(request))
    multi_style["references"] = [
        {"source": "INLINE_AUTHORITY", "id": "INLINE_STYLE_A", "role": "STYLE", "influence": ["visual_medium"]},
        {"source": "INLINE_AUTHORITY", "id": "INLINE_STYLE_B", "role": "STYLE", "influence": ["color_behavior"]},
    ]
    assert not validate_request(multi_style, manifest), validate_request(multi_style, manifest)
    compiled_multi = compile_request(manifest, multi_style)
    assert sum(1 for ref in compiled_multi["references"] if ref.get("authority_role") == "STYLE_CORE") == 0
    assert compiled_multi["workflow"]["style_recovery"]["enabled"] is False
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
