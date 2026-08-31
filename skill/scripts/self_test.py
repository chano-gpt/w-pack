#!/usr/bin/env python3
"""Run deterministic smoke tests for the W-Pack Skill scripts."""

from __future__ import annotations

import json
from pathlib import Path

from compile_request import compile_request
from validate_authorities import load_json, validate_manifest, validate_request

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "references" / "authority-manifest.example.json"
REQUEST = ROOT / "references" / "generation-request.example.json"


def main() -> int:
    manifest = load_json(MANIFEST)
    request = load_json(REQUEST)

    errors = validate_manifest(manifest)
    assert not errors, errors
    errors = validate_request(request, manifest)
    assert not errors, errors

    compiled = compile_request(manifest, request)
    assert compiled["schema_version"] == "WPACK_COMPILED_REQUEST_v1.1"
    assert compiled["mode"] == "FRESH"
    assert compiled["source_profile"] == "DEFAULT"
    assert compiled["use_default_sources"] is True
    assert len(compiled["references"]) == 4
    assert [ref["id"] for ref in compiled["references"][:3]] == [
        "STYLE_CORE_01", "CHARACTER_01", "PROPORTION_01"
    ]
    assert compiled["references"][3]["id"] == "INLINE_COMPOSITION_01"
    assert compiled["generation_constraints"]["project_sources_default_active"] is True
    assert compiled["generation_constraints"]["style_fidelity"] == "HIGH"
    assert compiled["generation_constraints"]["medium_lock"] == "REFERENCE"
    assert compiled["generation_constraints"]["photorealism_normalization"] == "DISABLED_UNLESS_EXPLICITLY_REQUESTED"

    override_request = json.loads(json.dumps(request))
    override_request["references"].append(
        {
            "source": "INLINE_AUTHORITY",
            "id": "INLINE_STYLE_01",
            "role": "STYLE",
            "influence": ["visual_medium", "rendering_language", "degree_of_realism"],
        }
    )
    errors = validate_request(override_request, manifest)
    assert not errors, errors
    compiled_override = compile_request(manifest, override_request)
    ids = [ref["id"] for ref in compiled_override["references"]]
    assert "STYLE_CORE_01" not in ids
    assert "INLINE_STYLE_01" in ids
    assert "CHARACTER_01" in ids
    assert "PROPORTION_01" in ids

    no_sources_request = json.loads(json.dumps(request))
    no_sources_request["use_default_sources"] = False
    compiled_no_sources = compile_request(manifest, no_sources_request)
    assert compiled_no_sources["source_profile"] is None
    assert [ref["id"] for ref in compiled_no_sources["references"]] == ["INLINE_COMPOSITION_01"]
    assert "style_fidelity" not in compiled_no_sources["generation_constraints"]

    overflow_request = json.loads(json.dumps(request))
    overflow_request["references"].extend(
        [
            {
                "source": "INLINE_AUTHORITY",
                "id": "INLINE_POSE_01",
                "role": "POSE",
                "influence": ["body_arrangement"],
            },
            {
                "source": "INLINE_AUTHORITY",
                "id": "INLINE_ITEM_01",
                "role": "ITEM",
                "influence": ["item_identity"],
            },
        ]
    )
    errors = validate_request(overflow_request, manifest)
    assert any("after default profile expansion" in error for error in errors), errors

    bad_request = json.loads(json.dumps(request))
    bad_request["edit_target"] = "previous.png"
    bad_request["references"][0]["influence"] = ["identity"]
    errors = validate_request(bad_request, manifest)
    assert any("not allowed to control 'identity'" in error for error in errors), errors
    assert any("fresh generation cannot include an edit target" in error for error in errors), errors

    edit_request = json.loads(json.dumps(request))
    edit_request["mode"] = "EDIT"
    edit_request["edit_target"] = "current-conversation-image"
    edit_request["edit_type"] = "MODIFY"
    edit_request["preserve"] = ["identity", "background", "composition"]
    edit_request["references"] = []
    errors = validate_request(edit_request, manifest)
    assert not errors, errors
    compiled_edit = compile_request(manifest, edit_request)
    assert compiled_edit["mode"] == "EDIT"
    assert compiled_edit["edit_target"] == "current-conversation-image"
    assert compiled_edit["source_profile"] == "DEFAULT"
    assert len(compiled_edit["references"]) == 3

    print("W-Pack self-test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
