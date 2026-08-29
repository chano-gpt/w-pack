#!/usr/bin/env python3
"""Run deterministic smoke tests for the W-Pack Skill scripts."""

from __future__ import annotations

import json
import tempfile
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
    assert compiled["schema_version"] == "WPACK_COMPILED_REQUEST_v1.0"
    assert compiled["mode"] == "FRESH"
    assert len(compiled["authorities"]) == 3
    assert compiled["generation_constraints"]["maximum_reference_count"] == 5

    bad_request = json.loads(json.dumps(request))
    bad_request["edit_target"] = "previous.png"
    bad_request["authorities"][0]["influence"] = ["identity"]
    bad_request["authorities"] = bad_request["authorities"] + [
        bad_request["authorities"][0],
        bad_request["authorities"][1],
        bad_request["authorities"][2],
    ]
    errors = validate_request(bad_request, manifest)
    expected = (
        "limit is 5",
        "not allowed to control 'identity'",
        "forbids control of 'identity'",
        "duplicate authority reference",
        "fresh generation cannot include",
    )
    for fragment in expected:
        assert any(fragment in error for error in errors), (fragment, errors)

    staged = json.loads(json.dumps(request))
    staged["mode"] = "STAGED_RESTYLE"
    staged["edit_target"] = "candidate.png"
    staged["explicit_opt_in"] = True
    staged["preserve"] = ["composition", "subject placement"]
    errors = validate_request(staged, manifest)
    assert not errors, errors
    compiled_staged = compile_request(manifest, staged)
    assert compiled_staged["edit_target"] == "candidate.png"
    assert compiled_staged["preserve"] == ["composition", "subject placement"]

    print("W-Pack self-test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
