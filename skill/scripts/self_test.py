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
    assert len(compiled["references"]) == 3
    assert compiled["references"][2]["source"] == "INLINE_AUTHORITY"
    assert compiled["references"][2]["role"] == "COMPOSITION"
    assert compiled["generation_constraints"]["maximum_reference_count"] == 5

    bad_request = json.loads(json.dumps(request))
    bad_request["edit_target"] = "previous.png"
    bad_request["references"][0]["influence"] = ["identity"]
    bad_request["references"] = bad_request["references"] + [
        bad_request["references"][0],
        bad_request["references"][1],
        bad_request["references"][2],
    ]
    errors = validate_request(bad_request, manifest)
    expected = (
        "limit is 5",
        "not allowed to control 'identity'",
        "forbids control of 'identity'",
        "duplicate reference",
        "fresh generation cannot include an edit target",
    )
    for fragment in expected:
        assert any(fragment in error for error in errors), (fragment, errors)

    edit_request = json.loads(json.dumps(request))
    edit_request["mode"] = "EDIT"
    edit_request["edit_target"] = "current-conversation-image"
    edit_request["edit_type"] = "MODIFY"
    edit_request["preserve"] = ["identity", "background", "composition"]
    edit_request["references"] = [
        {
            "source": "INLINE_AUTHORITY",
            "id": "INLINE_ITEM_01",
            "role": "ITEM",
            "influence": ["item_identity", "silhouette"]
        }
    ]
    errors = validate_request(edit_request, manifest)
    assert not errors, errors
    compiled_edit = compile_request(manifest, edit_request)
    assert compiled_edit["mode"] == "EDIT"
    assert compiled_edit["edit_target"] == "current-conversation-image"
    assert compiled_edit["edit_type"] == "MODIFY"
    assert compiled_edit["preserve"] == ["identity", "background", "composition"]

    profile_request = json.loads(json.dumps(request))
    profile_request["source_profile"] = "DEFAULT"
    errors = validate_request(profile_request, manifest)
    assert not errors, errors
    assert compile_request(manifest, profile_request)["source_profile"] == "DEFAULT"

    print("W-Pack self-test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
