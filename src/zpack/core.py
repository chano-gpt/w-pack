"""Fail-closed Z-Pack manifests, reference selection, compilation, and audit."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STYLE_REQUEST_V3 = "ZPACK_STYLE_REQUEST_v3.0"
COMPILED_REQUEST_V3 = "ZPACK_COMPILED_REQUEST_v3.0"
AUDIT_EVIDENCE_V3 = "ZPACK_AUDIT_EVIDENCE_v3.0"
STAGED_RESTYLE_REQUEST_V1 = "ZPACK_STAGED_RESTYLE_REQUEST_v1.0"
STAGED_RESTYLE_COMPILED_V1 = "ZPACK_STAGED_RESTYLE_COMPILED_v1.0"
STAGED_RESTYLE_RUN_RECEIPT_V1 = "ZPACK_STAGED_RESTYLE_RUN_RECEIPT_v1.0"
STAGED_RESTYLE_AUDIT_V1 = "ZPACK_STAGED_RESTYLE_AUDIT_v1.0"
STAGED_DRAFT_COMPILED_V1 = "ZPACK_STAGED_DRAFT_COMPILED_v1.0"
STAGED_DRAFT_RUN_RECEIPT_V1 = "ZPACK_STAGED_DRAFT_RUN_RECEIPT_v1.0"
FRESH_RUN_RECEIPT_SCHEMAS = {"ZPACK_RUN_RECEIPT_v3.0", STAGED_DRAFT_RUN_RECEIPT_V1}
IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}
STYLE_LIFECYCLE = (
    "INBOX", "ANALYZED", "PENDING_FIDELITY", "PROMOTED",
)
AUDIT_VERDICTS = {"PASS", "FAIL", "HOLD"}
STYLE_ROUTING_AXES = (
    "shot_scale", "time_of_day", "weather", "environment", "subject_mode",
    "action_level", "lighting_mode", "material_focus",
)
COMPOSITION_VISIBILITY_AXES = (
    "must_visible", "may_crop", "may_occlude", "off_frame_expected",
)


class ZPackError(RuntimeError):
    """A contract failure that must stop generation."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ZPackError(f"expected object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def pack_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "PACK_SPEC.json").is_file():
            return candidate
    raise ZPackError("PACK_SPEC.json not found")


def resolve_pack_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute():
        raise ZPackError(f"absolute asset path forbidden: {relative}")
    resolved_root = root.resolve()
    resolved = (resolved_root / path).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ZPackError(f"asset path escapes pack: {relative}") from error
    return resolved


def validate_workspace(root: Path, workspace: Path) -> Path:
    """Return a safe external workspace path or fail before any write."""
    resolved_root = root.resolve()
    resolved = workspace.resolve()
    broad = {Path("/").resolve(), Path.home().resolve(), resolved_root.parent.resolve()}
    if resolved in broad:
        raise ZPackError(f"unsafe broad workspace path: {resolved}")
    if resolved == resolved_root or _is_relative_to(resolved, resolved_root):
        raise ZPackError("WORKSPACE_INSIDE_PACK_FORBIDDEN")
    return resolved


def validate_output_path(root: Path, output: Path) -> Path:
    resolved_root = root.resolve()
    resolved = output.resolve()
    if resolved == resolved_root or _is_relative_to(resolved, resolved_root):
        raise ZPackError("OUTPUT_INSIDE_PACK_FORBIDDEN")
    return resolved


def _manifest_authorities(root: Path) -> dict[str, dict[str, Any]]:
    manifest = load_json(root / "pack/styles/default/STYLE_SOURCE_MANIFEST.json")
    style = [
        entry
        for entry in manifest["sources"]
        if entry.get("generation_reference_eligible") is True
        and entry.get("lifecycle_status") == "PROMOTED"
    ]
    restyle_policy_path = root / "pack/styles/default/STAGED_RESTYLE_POLICY.json"
    if restyle_policy_path.is_file():
        restyle_ids = set(load_json(restyle_policy_path).get("allowed_style_core_ids", []))
        style.extend(entry for entry in manifest["sources"] if entry["id"] in restyle_ids)
    assets = load_json(root / "private-assets/PRIVATE_ASSET_MANIFEST.json")["assets"]
    return {entry["id"]: entry for entry in [*style, *assets]}


def pack_authority_inventory(root: Path) -> list[dict[str, str]]:
    inventory = []
    for authority_id, entry in sorted(_manifest_authorities(root).items()):
        path = resolve_pack_path(root, entry["path"])
        if not path.is_file():
            raise ZPackError(f"missing authority: {authority_id}")
        inventory.append({
            "id": authority_id,
            "path": entry["path"],
            "sha256": sha256(path),
        })
    return inventory


def default_workspace_root(root: Path) -> Path:
    spec = load_json(root / "PACK_SPEC.json")
    configured = spec["workspace_policy"]["default_root"]
    return validate_workspace(root, (root / configured).resolve())


def managed_workspace_root(root: Path, workspace: Path | None = None) -> Path:
    """Resolve a CLI-managed workspace below the pack's single canonical root."""
    canonical = default_workspace_root(root)
    resolved = canonical if workspace is None else validate_workspace(root, workspace)
    if resolved != canonical and not _is_relative_to(resolved, canonical):
        raise ZPackError(
            f"WORKSPACE_OUTSIDE_CANONICAL_ROOT_FORBIDDEN: expected {canonical}, got {resolved}"
        )
    return resolved


def validate(root: Path) -> dict[str, Any]:
    spec = load_json(root / "PACK_SPEC.json")
    if spec.get("scope") == "PUBLIC_TEMPLATE_IMAGE_GENERATION_HARNESS":
        return _validate_public_template(root, spec)
    expected = {
        "display_name": "Z-Pack",
        "pack_id": "ZPACK",
        "pack_version": "ZPACK_v1.2.0",
        "repository": "chaos1358/z-pack",
    }
    errors = [f"{key} mismatch" for key, value in expected.items() if spec.get(key) != value]
    if spec.get("standalone_api_allowed") is not False:
        errors.append("standalone API must be disabled")
    if spec.get("reference_slot_limit") != 5:
        errors.append("reference slot limit must be 5")
    composition_policy_path = spec.get("composition_policy_path")
    composition_policy: dict[str, Any] = {}
    if not isinstance(composition_policy_path, str):
        errors.append("missing composition policy path")
    else:
        try:
            composition_policy = load_json(resolve_pack_path(root, composition_policy_path))
        except (OSError, ValueError, json.JSONDecodeError, ZPackError):
            errors.append("invalid composition policy path")
    if composition_policy and (
        composition_policy.get("schema_version") != "ZPACK_COMPOSITION_POLICY_v1.0"
        or composition_policy.get("status") != "ACTIVE"
        or composition_policy.get("planning_phase") != "PRE_GENERATION_ONLY"
        or composition_policy.get("style_routing_independent") is not True
        or composition_policy.get("restyle_canvas_mutation_allowed") is not False
        or composition_policy.get("automatic_layout_retry_count") != 0
        or composition_policy.get("allowed_aspect_ratios") != ["4:5", "2:3", "1:1", "4:3", "3:2"]
        or composition_policy.get("priority_order") != [
            "physical_scale_anatomy_and_perspective",
            "mandatory_focal_anchors",
            "natural_occlusion_and_crop",
            "optional_complete_visibility",
        ]
    ):
        errors.append("invalid composition policy")
    workspace_policy = spec.get("workspace_policy", {})
    if workspace_policy.get("must_be_outside_pack") is not True:
        errors.append("workspace must be outside pack")
    if (
        workspace_policy.get("default_root") != "../zpack-workspace"
        or workspace_policy.get("location_strategy") != "PACK_SIBLING_SINGLE_ROOT"
        or workspace_policy.get("cli_override_scope") != "CANONICAL_ROOT_OR_DESCENDANT"
    ):
        errors.append("invalid canonical workspace policy")
    audit_policy = spec.get("audit_policy", {})
    if audit_policy.get("evidence_required") is not True:
        errors.append("audit evidence must be required")
    candidate_policy = spec.get("candidate_policy", {})
    staged_exception = candidate_policy.get("staged_restyle_exception", {})
    if (
        staged_exception.get("enabled") is not True
        or staged_exception.get("mode") != "EXPLICIT_OPT_IN_ONLY"
        or staged_exception.get("maximum_restyle_depth") != 1
        or staged_exception.get("maximum_style_references") != 1
        or staged_exception.get("style_adapter_allowed") is not False
        or staged_exception.get("recursive_restyle_allowed") is not False
    ):
        errors.append("invalid staged restyle exception")
    recommended_workflow = candidate_policy.get("recommended_style_workflow", {})
    if recommended_workflow != {
        "enabled": True,
        "mode": "FRESH_DRAFT_THEN_SINGLE_RESTYLE",
        "policy_path": "pack/styles/default/STAGED_RESTYLE_POLICY.json",
        "default_fresh_draft_count": 1,
        "default_restyle_count": 1,
        "default_retry_count": 0,
        "automatic_retry_allowed": False,
        "retry_must_start_fresh_chain": True,
    }:
        errors.append("invalid recommended style workflow")
    staged_policy_path = staged_exception.get("policy_path")
    staged_policy: dict[str, Any] = {}
    if not isinstance(staged_policy_path, str):
        errors.append("missing staged restyle policy path")
    else:
        try:
            staged_policy = load_json(resolve_pack_path(root, staged_policy_path))
        except (OSError, ValueError, json.JSONDecodeError, ZPackError):
            errors.append("invalid staged restyle policy path")
    if staged_policy and (
        staged_policy.get("schema_version") != "ZPACK_STAGED_RESTYLE_POLICY_v1.0"
        or staged_policy.get("status") != "LIMITED_DEFAULT"
        or staged_policy.get("enabled") is not True
        or staged_policy.get("maximum_restyle_depth") != 1
        or staged_policy.get("style_adapter_allowed") is not False
        or staged_policy.get("recursive_restyle_allowed") is not False
        or staged_policy.get("required_reference_roles") != ["structure_edit_target", "style_core"]
        or staged_policy.get("accepted_source_receipt_schemas") != sorted(FRESH_RUN_RECEIPT_SCHEMAS)
        or staged_policy.get("required_audit_axes") != [
            "STYLE_REFERENCE_FIDELITY", "STYLE_CONTENT_LEAKAGE",
            "SCENE_PROMPT_COMPLIANCE", "STRUCTURE_PRESERVATION",
        ]
    ):
        errors.append("invalid staged restyle policy")
    workflow_contract = staged_policy.get("workflow_contract", {})
    if workflow_contract != {
        "id": "ZPACK_FRESH_DRAFT_SINGLE_RESTYLE_v1",
        "mode": "FRESH_DRAFT_THEN_SINGLE_RESTYLE",
        "default_for_style_family_ids": ["ZPACK_STYLE_FAMILY"],
        "draft_compiled_schema": STAGED_DRAFT_COMPILED_V1,
        "draft_receipt_schema": STAGED_DRAFT_RUN_RECEIPT_V1,
        "default_fresh_draft_count": 1,
        "default_restyle_count": 1,
        "default_retry_count": 0,
        "automatic_retry_allowed": False,
        "operator_requested_fresh_chain_retry_allowed": True,
        "retry_reuses_prior_candidate": False,
    }:
        errors.append("invalid staged workflow contract")
    staged_list_fields = (
        "allowed_style_core_ids", "shared_style_signature", "anti_drift_signatures",
        "required_preservation_axes", "required_audit_axes",
    )
    if staged_policy and any(
        not isinstance(staged_policy.get(field), list) or not staged_policy[field]
        or any(not isinstance(item, str) or not item.strip() for item in staged_policy[field])
        for field in staged_list_fields
    ):
        errors.append("invalid staged restyle policy lists")

    style_manifest_path = root / "pack/styles/default/STYLE_SOURCE_MANIFEST.json"
    private_manifest_path = root / "private-assets/PRIVATE_ASSET_MANIFEST.json"
    style = load_json(style_manifest_path)
    private = load_json(private_manifest_path)
    sources = style.get("sources", [])
    runtime_sources = [
        source for source in sources
        if source.get("generation_reference_eligible") is True
        and source.get("lifecycle_status") == "PROMOTED"
    ]
    configured_staged_core_ids = staged_policy.get("allowed_style_core_ids", [])
    staged_core_ids = set(configured_staged_core_ids) if isinstance(configured_staged_core_ids, list) else set()
    staged_sources = [
        source for source in sources
        if source.get("id") in staged_core_ids and source not in runtime_sources
    ]
    checked = 0
    for entry in [*runtime_sources, *staged_sources, *private.get("assets", [])]:
        path = resolve_pack_path(root, entry["path"])
        if not path.is_file():
            errors.append(f"missing runtime authority: {entry['path']}")
            continue
        checked += 1
        if sha256(path) != entry["sha256"]:
            errors.append(f"SHA mismatch: {entry['path']}")
    if style.get("source_count") != len(sources):
        errors.append("style source count mismatch")
    required_style_fields = {
        "id", "path", "sha256", "style_role", "family_id", "allowed_domains",
        "forbidden_content_signatures", "lifecycle_status", "benchmark_reference_eligible",
        "generation_reference_eligible", "owner_verdict_receipt_sha", "benchmark_report_sha",
        "promoted_at",
    }
    for source in sources:
        missing = sorted(required_style_fields - set(source))
        if missing:
            errors.append(f"style source fields missing: {source.get('id')}:{','.join(missing)}")
        if source.get("lifecycle_status") not in STYLE_LIFECYCLE:
            errors.append(f"invalid style lifecycle: {source.get('id')}")
        if source.get("style_role") == "primary" and source.get("allowed_domains"):
            errors.append(f"primary allowed domains must be empty: {source.get('id')}")
        if source.get("style_role") == "support" and not source.get("allowed_domains"):
            errors.append(f"support allowed domains required: {source.get('id')}")
        if source.get("generation_reference_eligible") and source.get("lifecycle_status") != "PROMOTED":
            errors.append(f"unpromoted generation source: {source.get('id')}")
    for source_id in sorted(staged_core_ids):
        source = next((item for item in sources if item.get("id") == source_id), None)
        if (
            source is None
            or source.get("style_role") != "primary"
            or source.get("lifecycle_status") not in {"PENDING_FIDELITY", "PROMOTED"}
            or source.get("benchmark_reference_eligible") is not True
        ):
            errors.append(f"invalid staged restyle core: {source_id}")
    registry = load_json(root / "pack/styles/default/STYLE_PROFILE_REGISTRY.json")
    source_by_id = {source["id"]: source for source in sources}
    for profile in registry.get("profiles", []):
        primary = source_by_id.get(profile.get("primary_id"))
        if primary is None or primary.get("style_role") != "primary":
            errors.append(f"invalid profile primary: {profile.get('id')}")
            continue
        if profile.get("family_id") != primary.get("family_id"):
            errors.append(f"invalid profile family: {profile.get('id')}")
        if 1 + len(profile.get("support_ids", [])) > spec.get("reference_slot_limit", 5):
            errors.append(f"profile exceeds reference limit: {profile.get('id')}")
        for support_id in profile.get("support_ids", []):
            support = source_by_id.get(support_id)
            if (
                support is None or support.get("style_role") != "support"
                or support.get("family_id") != primary.get("family_id")
            ):
                errors.append(f"invalid profile support: {profile.get('id')}:{support_id}")
    router_path = root / "pack/styles/default/STYLE_FAMILY_ROUTER.json"
    if not router_path.is_file():
        errors.append("missing style family router")
    else:
        router = load_json(router_path)
        if router.get("schema_version") != "ZPACK_STYLE_FAMILY_ROUTER_v1.1":
            errors.append("invalid style family router schema")
        if router.get("free_text_keyword_routing_allowed") is not False:
            errors.append("free-text style routing must be disabled")
        family_ids: set[str] = set()
        for family in router.get("families", []):
            family_id = family.get("id")
            if not family_id or family_id in family_ids:
                errors.append(f"invalid or duplicate routed family: {family_id}")
                continue
            family_ids.add(family_id)
            if family.get("lifecycle_status") not in {"PENDING_FIDELITY", "PROMOTED"}:
                errors.append(f"invalid routed family lifecycle: {family_id}")
            approval_sha = family.get("owner_routing_approval_sha256")
            if not isinstance(approval_sha, str) or re.fullmatch(r"[0-9a-f]{64}", approval_sha) is None:
                errors.append(f"invalid routed family approval: {family_id}")
            signature = family.get("shared_style_signature")
            if (
                not isinstance(signature, list) or not signature
                or any(not isinstance(item, str) or not item for item in signature)
            ):
                errors.append(f"invalid routed family signature: {family_id}")
            anti_drift = family.get("anti_drift_signatures")
            if (
                not isinstance(anti_drift, list) or not anti_drift
                or any(not isinstance(item, str) or not item for item in anti_drift)
            ):
                errors.append(f"invalid routed family anti-drift signature: {family_id}")
            maximum = family.get("maximum_contextual_style_references")
            minimum = family.get("minimum_contextual_style_references")
            if not isinstance(maximum, int) or not 1 <= maximum <= spec.get("reference_slot_limit", 5):
                errors.append(f"invalid routed family maximum: {family_id}")
            if not isinstance(minimum, int) or not isinstance(maximum, int) or not 1 <= minimum <= maximum:
                errors.append(f"invalid routed family minimum: {family_id}")
            weights = family.get("axis_weights", {})
            if set(weights) != set(STYLE_ROUTING_AXES) or any(
                not isinstance(value, int) or value <= 0 for value in weights.values()
            ):
                errors.append(f"invalid routed family weights: {family_id}")
            routed_ids: set[str] = set()
            route_priorities: set[int] = set()
            for routed in family.get("sources", []):
                source_id = routed.get("id")
                source = source_by_id.get(source_id)
                if not source_id or source_id in routed_ids or source is None:
                    errors.append(f"invalid routed source: {family_id}:{source_id}")
                    continue
                routed_ids.add(source_id)
                priority = routed.get("route_priority")
                if not isinstance(priority, int) or priority in route_priorities:
                    errors.append(f"invalid routed source priority: {family_id}:{source_id}")
                else:
                    route_priorities.add(priority)
                if routed.get("sha256") != source.get("sha256"):
                    errors.append(f"routed source SHA mismatch: {family_id}:{source_id}")
                tags = routed.get("tags", {})
                if set(tags) != set(STYLE_ROUTING_AXES) or any(
                    not isinstance(values, list) or not values
                    or any(not isinstance(value, str) or not value for value in values)
                    for values in tags.values()
                ):
                    errors.append(f"invalid routed source tags: {family_id}:{source_id}")
                risks = routed.get("content_leakage_risk")
                if (
                    not isinstance(risks, list) or not risks
                    or any(not isinstance(item, str) or not item for item in risks)
                ):
                    errors.append(f"invalid routed source leakage risks: {family_id}:{source_id}")
            if not routed_ids:
                errors.append(f"routed family has no sources: {family_id}")
            if not set(family.get("fallback_source_ids", [])).issubset(routed_ids):
                errors.append(f"invalid routed family fallback: {family_id}")
            core_source_id = family.get("core_source_id")
            adapters = family.get("maximum_domain_adapters")
            if core_source_id not in routed_ids:
                errors.append(f"invalid routed family core: {family_id}")
            if adapters != 1 or maximum != 1 + adapters:
                errors.append(f"invalid routed family adapter limit: {family_id}")
            if family.get("lifecycle_status") == "PROMOTED" and any(
                not source_by_id[source_id].get("generation_reference_eligible")
                or source_by_id[source_id].get("lifecycle_status") != "PROMOTED"
                for source_id in routed_ids
            ):
                errors.append(f"promoted routed family has unpromoted source: {family_id}")
    if errors:
        raise ZPackError("; ".join(errors))
    return {"status": "PASS", "checked_assets": checked, **expected}


def _validate_public_template(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    """Validate the distributable starter without requiring private authorities."""
    expected = {
        "display_name": "Z-Pack",
        "pack_id": "ZPACK",
        "pack_version": "ZPACK_v1.2.0-public",
        "repository": "chaos1358/z-pack",
    }
    errors = [f"{key} mismatch" for key, value in expected.items() if spec.get(key) != value]
    if spec.get("standalone_api_allowed") is not False:
        errors.append("standalone API must be disabled")
    if spec.get("reference_slot_limit") != 5:
        errors.append("reference slot limit must be 5")
    if spec.get("workspace_policy", {}).get("must_be_outside_pack") is not True:
        errors.append("workspace must be outside pack")

    style = load_json(root / "pack/styles/default/STYLE_SOURCE_MANIFEST.json")
    private = load_json(root / "private-assets/PRIVATE_ASSET_MANIFEST.json")
    sources = style.get("sources")
    assets = private.get("assets")
    if not isinstance(sources, list) or style.get("source_count") != len(sources):
        errors.append("invalid style source manifest")
    if not isinstance(assets, list):
        errors.append("invalid private asset manifest")

    checked = 0
    for entry in [*(sources or []), *(assets or [])]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
            errors.append("invalid local authority record")
            continue
        path = resolve_pack_path(root, entry["path"])
        if not path.is_file():
            errors.append(f"missing local authority: {entry['path']}")
            continue
        checked += 1
        if sha256(path) != entry["sha256"]:
            errors.append(f"SHA mismatch: {entry['path']}")
    if errors:
        raise ZPackError("; ".join(errors))
    return {"status": "PASS", "checked_assets": checked, **expected}


def _select_non_style(root: Path, request: dict[str, Any]) -> list[dict[str, Any]]:
    requested = list(request.get("required_authorities", []))
    approved = {
        asset["id"]: asset
        for asset in load_json(root / "private-assets/PRIVATE_ASSET_MANIFEST.json")["assets"]
    }
    selected = []
    seen = set()
    for reference in requested:
        reference_id = reference.get("id")
        if reference_id in seen:
            raise ZPackError(f"duplicate required authority: {reference_id}")
        seen.add(reference_id)
        authority = approved.get(reference_id)
        if authority is None:
            raise ZPackError(f"unapproved required authority: {reference_id}")
        for field in ("path", "sha256"):
            supplied = reference.get(field)
            if supplied is not None and supplied != authority[field]:
                raise ZPackError(f"required authority {field} mismatch: {reference_id}")
        short_role = {
            "APPROVED_CHARACTER_SOURCE": "character",
            "APPROVED_PROPORTION_SOURCE": "proportion",
            "APPROVED_ITEM_SOURCE": "item",
            "APPROVED_POSE_CONTROL": "pose",
        }.get(authority["role"])
        accepted_roles = {authority["role"], short_role}
        if reference.get("role") is not None and reference["role"] not in accepted_roles:
            raise ZPackError(f"required authority role mismatch: {reference_id}")
        path = resolve_pack_path(root, authority["path"])
        if not path.is_file() or sha256(path) != authority["sha256"]:
            raise ZPackError(f"approved authority unavailable or changed: {reference_id}")
        selected.append({key: authority[key] for key in ("id", "role", "path", "sha256")})
    return selected


def _style_sources(root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = load_json(root / "pack/styles/default/STYLE_SOURCE_MANIFEST.json")
    return manifest, {source["id"]: source for source in manifest["sources"]}


def _assert_style_source(root: Path, source: dict[str, Any], role: str, benchmark: bool) -> None:
    if source.get("style_role", source.get("role")) != role:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    eligible_key = "benchmark_reference_eligible" if benchmark else "generation_reference_eligible"
    allowed_states = {"PENDING_FIDELITY", "PROMOTED"} if benchmark else {"PROMOTED"}
    if not source.get(eligible_key) or source.get("lifecycle_status") not in allowed_states:
        if not benchmark and source.get("lifecycle_status") != "PROMOTED":
            raise ZPackError("STYLE_SOURCE_NOT_PROMOTED")
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    path = resolve_pack_path(root, source["path"])
    if not path.is_file() or sha256(path) != source["sha256"]:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")


def _assert_routed_style_source(root: Path, source: dict[str, Any], benchmark: bool) -> None:
    role = source.get("style_role", source.get("role"))
    if role not in {"primary", "support"}:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    _assert_style_source(root, source, role, benchmark)


def _normalize_scene_traits(family: dict[str, Any], value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict) or not value:
        raise ZPackError("STYLE_SCENE_TRAITS_REQUIRED")
    unknown_axes = sorted(set(value) - set(STYLE_ROUTING_AXES))
    if unknown_axes:
        raise ZPackError("STYLE_SCENE_TRAIT_AXIS_UNKNOWN: " + ",".join(unknown_axes))
    vocabulary = {
        axis: {
            tag
            for source in family["sources"]
            for tag in source["tags"][axis]
        }
        for axis in STYLE_ROUTING_AXES
    }
    normalized: dict[str, list[str]] = {}
    for axis, supplied in value.items():
        values = [supplied] if isinstance(supplied, str) else supplied
        if (
            not isinstance(values, list) or not values
            or any(not isinstance(item, str) or not item.strip() for item in values)
        ):
            raise ZPackError(f"STYLE_SCENE_TRAIT_INVALID: {axis}")
        clean = sorted({item.strip() for item in values})
        unknown = sorted(set(clean) - vocabulary[axis])
        if unknown:
            raise ZPackError(f"STYLE_SCENE_TRAIT_UNKNOWN: {axis}:{','.join(unknown)}")
        normalized[axis] = clean
    return normalized


def _route_style_family(
    root: Path,
    family: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    request: dict[str, Any],
    available_style_slots: int,
) -> tuple[list[str], dict[str, Any]]:
    benchmark = request.get("benchmark_mode") is True
    lifecycle = family.get("lifecycle_status")
    if benchmark:
        if lifecycle not in {"PENDING_FIDELITY", "PROMOTED"}:
            raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    elif lifecycle != "PROMOTED":
        raise ZPackError("STYLE_SOURCE_NOT_PROMOTED")
    traits = _normalize_scene_traits(family, request.get("scene_traits"))
    weights = family["axis_weights"]
    ranked = []
    for routed in family["sources"]:
        source = by_id.get(routed["id"])
        if source is None or source.get("sha256") != routed.get("sha256"):
            raise ZPackError("STYLE_SOURCE_INELIGIBLE")
        _assert_routed_style_source(root, source, benchmark)
        matched = {
            axis: sorted(set(values) & set(routed["tags"][axis]))
            for axis, values in traits.items()
        }
        matched = {axis: values for axis, values in matched.items() if values}
        score = sum(weights[axis] * len(values) for axis, values in matched.items())
        ranked.append({
            "id": routed["id"],
            "score": score,
            "matched_traits": matched,
            "route_priority": routed["route_priority"],
        })
    ranked.sort(key=lambda item: (-item["score"], -len(item["matched_traits"]), item["route_priority"], item["id"]))
    by_ranked_id = {item["id"]: item for item in ranked}
    core_id = family["core_source_id"]
    core = by_ranked_id.get(core_id)
    if core is None:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    requested_adapter_limit = request.get("style_adapter_limit")
    if requested_adapter_limit is None:
        adapter_limit = family["maximum_domain_adapters"]
    else:
        if (
            isinstance(requested_adapter_limit, bool)
            or not isinstance(requested_adapter_limit, int)
            or requested_adapter_limit < 0
            or requested_adapter_limit > family["maximum_domain_adapters"]
        ):
            raise ZPackError("STYLE_ADAPTER_LIMIT_INVALID")
        adapter_limit = requested_adapter_limit
    limit = min(family["maximum_contextual_style_references"], available_style_slots)
    chosen = [{**core, "authority_role": "STYLE_CORE"}]
    adapter_candidates = [
        item for item in ranked
        if item["id"] != core_id and item["score"] > 0
    ]
    if limit > 1 and adapter_limit > 0 and adapter_candidates:
        chosen.append({**adapter_candidates[0], "authority_role": "STYLE_DOMAIN_ADAPTER"})
    routing = {
        "mode": "FIXED_CORE_PLUS_SINGLE_DOMAIN_ADAPTER",
        "family_id": family["id"],
        "core_source_id": core_id,
        "configured_adapter_maximum": family["maximum_domain_adapters"],
        "requested_adapter_limit": requested_adapter_limit,
        "effective_adapter_limit": adapter_limit,
        "scene_traits": traits,
        "configured_maximum": family["maximum_contextual_style_references"],
        "available_style_slots": available_style_slots,
        "selection_limit": limit,
        "capacity_reduced": limit < family["maximum_contextual_style_references"],
        "selected": [
            {
                "id": item["id"],
                "authority_role": item["authority_role"],
                "score": item["score"],
                "matched_traits": item["matched_traits"],
            }
            for item in chosen
        ],
        "family_contract_sha256": canonical_sha(family),
    }
    routing["routing_sha256"] = canonical_sha(routing)
    return [item["id"] for item in chosen], routing


def _select_style_ids(
    root: Path, request: dict[str, Any], available_style_slots: int,
) -> dict[str, Any]:
    _, by_id = _style_sources(root)
    compatibility_mode = request.get("compatibility_mode")
    if compatibility_mode == "e4_primary_only":
        selector = load_json(root / "pack/styles/default/STYLE_REFERENCE_SELECTOR.json")
        primary_id = selector.get("compatibility_primary_id") or selector.get("primary_id")
        if not primary_id:
            raise ZPackError("E4_COMPATIBILITY_PRIMARY_MISSING")
        source = by_id.get(primary_id)
        if source is None or not source.get("generation_reference_eligible"):
            raise ZPackError(f"invalid primary style reference: {primary_id}")
        return {"ids": [primary_id], "profile_id": None, "family_id": None, "routing": None}
    if compatibility_mode is not None:
        raise ZPackError(f"unsupported compatibility mode: {compatibility_mode}")
    if request.get("schema_version") != STYLE_REQUEST_V3:
        raise ZPackError("STYLE_REQUEST_V3_REQUIRED")
    primary_id = request.get("style_primary_id")
    profile_id = request.get("style_profile_id")
    family_id = request.get("style_family_id")
    selected_modes = [value for value in (primary_id, profile_id, family_id) if value]
    if not selected_modes:
        raise ZPackError("STYLE_SELECTION_REQUIRED")
    if len(selected_modes) != 1:
        raise ZPackError("STYLE_SELECTION_MUTUALLY_EXCLUSIVE")
    if request.get("scene_traits") is not None and not family_id:
        raise ZPackError("STYLE_SCENE_TRAITS_REQUIRE_FAMILY")
    if request.get("style_adapter_limit") is not None and not family_id:
        raise ZPackError("STYLE_ADAPTER_LIMIT_REQUIRES_FAMILY")
    benchmark = request.get("benchmark_mode") is True
    if primary_id:
        source = by_id.get(primary_id)
        if source is None:
            raise ZPackError("STYLE_SOURCE_INELIGIBLE")
        _assert_style_source(root, source, "primary", benchmark)
        return {"ids": [primary_id], "profile_id": None, "family_id": None, "routing": None}
    if family_id:
        router = load_json(root / "pack/styles/default/STYLE_FAMILY_ROUTER.json")
        family = next((item for item in router.get("families", []) if item.get("id") == family_id), None)
        if family is None:
            raise ZPackError("STYLE_SOURCE_INELIGIBLE")
        ids, routing = _route_style_family(root, family, by_id, request, available_style_slots)
        return {"ids": ids, "profile_id": None, "family_id": family_id, "routing": routing}
    registry = load_json(root / "pack/styles/default/STYLE_PROFILE_REGISTRY.json")
    profile = next((item for item in registry["profiles"] if item["id"] == profile_id), None)
    if profile is None:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    if benchmark:
        if profile.get("lifecycle_status") not in {"PENDING_FIDELITY", "PROMOTED"}:
            raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    elif profile.get("lifecycle_status") != "PROMOTED":
        raise ZPackError("STYLE_SOURCE_NOT_PROMOTED")
    ids = [profile["primary_id"], *profile.get("support_ids", [])]
    primary = by_id.get(ids[0])
    if primary is None:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    _assert_style_source(root, primary, "primary", benchmark)
    family_id = primary.get("family_id")
    for source_id in ids[1:]:
        source = by_id.get(source_id)
        if source is None or source.get("family_id") != family_id or not source.get("allowed_domains"):
            raise ZPackError("STYLE_SOURCE_INELIGIBLE")
        _assert_style_source(root, source, "support", benchmark)
    return {"ids": ids, "profile_id": profile_id, "family_id": None, "routing": None}


def select_references(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    maximum = load_json(root / "PACK_SPEC.json")["reference_slot_limit"]
    non_style = _select_non_style(root, request)
    if len(non_style) >= maximum:
        raise ZPackError("STYLE_REFERENCE_CAPACITY_HOLD")
    _, by_id = _style_sources(root)
    available = maximum - len(non_style)
    style_selection = _select_style_ids(root, request, available)
    style_ids = style_selection["ids"]
    profile_id = style_selection["profile_id"]
    if profile_id is not None and len(style_ids) > available:
        raise ZPackError("STYLE_REFERENCE_CAPACITY_HOLD")
    chosen = style_ids[:available]
    if not chosen or chosen[0] != style_ids[0]:
        raise ZPackError("STYLE_REFERENCE_CAPACITY_HOLD")
    family_id = style_selection["family_id"]
    family_roles = {
        item["id"]: {
            "STYLE_CORE": "style_core",
            "STYLE_DOMAIN_ADAPTER": "style_adapter",
        }[item["authority_role"]]
        for item in (style_selection["routing"] or {}).get("selected", [])
    }
    references = [
        {
            "id": source_id,
            "role": (
                family_roles[source_id] if family_id else
                by_id[source_id].get("style_role", by_id[source_id]["role"])
            ),
            "path": by_id[source_id]["path"],
            "sha256": by_id[source_id]["sha256"],
        }
        for source_id in chosen
    ] + non_style
    excluded = [
        {"id": source_id, "reason": "REFERENCE_CAPACITY"}
        for source_id in style_ids[len(chosen):]
    ]
    return {
        "status": "PASS",
        "style_profile_id": profile_id,
        "style_family_id": family_id,
        "style_routing": style_selection["routing"],
        "selected": references,
        "selected_count": len(references),
        "available_style_slots": available,
        "excluded": excluded,
        "selection_sha256": canonical_sha(references),
    }


def _proportion_contract(root: Path, request: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    proportion_contract_id = request.get("proportion_contract_id")
    if not proportion_contract_id:
        return None, None
    proportion_lock = load_json(root / "pack/styles/default/PROPORTION_LOCK.json")
    contract_path = proportion_lock["contracts"].get(proportion_contract_id)
    if not contract_path:
        raise ZPackError(f"unknown proportion contract: {proportion_contract_id}")
    return proportion_contract_id, load_json(resolve_pack_path(root, contract_path))


def resolve_composition_plan(root: Path, request: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve structured spatial intent without parsing scene prose or style tags."""
    value = request.get("composition")
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ZPackError("COMPOSITION_PLAN_INVALID")
    allowed_fields = {
        "canvas_policy", "aspect_ratio", "dominant_span", "framing", "span_pressure",
        *COMPOSITION_VISIBILITY_AXES,
    }
    if set(value) - allowed_fields:
        raise ZPackError("COMPOSITION_PLAN_FIELDS_INVALID")
    policy = load_json(resolve_pack_path(
        root, load_json(root / "PACK_SPEC.json")["composition_policy_path"],
    ))
    canvas_policy = value.get("canvas_policy")
    if canvas_policy not in {"AUTO", "EXPLICIT"}:
        raise ZPackError("COMPOSITION_CANVAS_POLICY_INVALID")
    dominant_span = value.get("dominant_span")
    framing = value.get("framing")
    span_pressure = value.get("span_pressure")
    if dominant_span not in policy["allowed_dominant_spans"]:
        raise ZPackError("COMPOSITION_DOMINANT_SPAN_INVALID")
    if framing not in policy["allowed_framings"]:
        raise ZPackError("COMPOSITION_FRAMING_INVALID")
    if span_pressure not in policy["allowed_span_pressures"]:
        raise ZPackError("COMPOSITION_SPAN_PRESSURE_INVALID")
    supplied_ratio = value.get("aspect_ratio")
    if canvas_policy == "AUTO":
        if supplied_ratio is not None:
            raise ZPackError("AUTO_COMPOSITION_ASPECT_OVERRIDE_FORBIDDEN")
        selected_ratio = policy["auto_selection"][dominant_span][span_pressure]
    else:
        if supplied_ratio not in policy["allowed_aspect_ratios"]:
            raise ZPackError("COMPOSITION_ASPECT_RATIO_INVALID")
        selected_ratio = supplied_ratio
    visibility: dict[str, list[str]] = {}
    maximum = policy["maximum_visibility_items_per_axis"]
    for axis in COMPOSITION_VISIBILITY_AXES:
        items = value.get(axis, [])
        if (
            not isinstance(items, list) or len(items) > maximum
            or any(not isinstance(item, str) or not item.strip() or len(item) > 120 for item in items)
        ):
            raise ZPackError(f"COMPOSITION_{axis.upper()}_INVALID")
        visibility[axis] = [item.strip() for item in items]
    if not visibility["must_visible"]:
        raise ZPackError("COMPOSITION_MUST_VISIBLE_REQUIRED")
    orientation = {
        "4:5": "portrait", "2:3": "portrait", "1:1": "square",
        "4:3": "landscape", "3:2": "landscape",
    }[selected_ratio]
    plan = {
        "canvas_policy": canvas_policy,
        "selected_aspect_ratio": selected_ratio,
        "orientation": orientation,
        "dominant_span": dominant_span,
        "framing": framing,
        "span_pressure": span_pressure,
        **visibility,
        "style_routing_independent": True,
        "automatic_layout_retry_count": 0,
        "priority_order": policy["priority_order"],
    }
    plan["composition_plan_sha256"] = canonical_sha(plan)
    return plan


def _composition_prompt(plan: dict[str, Any] | None) -> str:
    if plan is None:
        return ""
    lines = [
        f"Canvas plan: {plan['orientation']} {plan['selected_aspect_ratio']} "
        f"({plan['canvas_policy']} from {plan['dominant_span']} span, {plan['span_pressure']} pressure, "
        f"{plan['framing']} framing).",
        "Protect from accidental cropping: " + "; ".join(plan["must_visible"]) + ".",
    ]
    labels = {
        "may_crop": "Natural frame exit is allowed for",
        "may_occlude": "Natural viewpoint-correct occlusion is allowed for",
        "off_frame_expected": "Expected outside the frame",
    }
    for axis, label in labels.items():
        if plan[axis]:
            lines.append(label + ": " + "; ".join(plan[axis]) + ".")
    lines.append(
        "Never shorten, bend, compress, detach, or relocate anatomy or objects to fit the canvas. "
        "Physical scale, anatomy, camera perspective, contact, and mechanical continuity outrank optional visibility."
    )
    return "\n".join(lines)


def _compile_legacy_e4(root: Path, request: dict[str, Any], scene: str) -> dict[str, Any]:
    """Frozen v2 compiler used only by the explicit E4 compatibility lane."""
    selection = select_references(root, request)
    profile = load_json(root / "pack/styles/default/STYLE_PROFILE.json")
    authority_policy = load_json(root / "pack/styles/default/REFERENCE_AUTHORITY_POLICY.json")
    forbidden_shortcuts = [
        shortcut for shortcut in profile["forbidden_prompt_shortcuts"]
        if shortcut.casefold() in scene.casefold()
    ]
    if forbidden_shortcuts:
        raise ZPackError("GENERIC_STYLE_SHORTCUT_FORBIDDEN: " + ", ".join(forbidden_shortcuts))
    proportion_contract_id, proportion_contract = _proportion_contract(root, request)
    role_lines = []
    for reference in selection["selected"]:
        role = reference["role"]
        if role == "primary":
            policy_key = "STYLE_PRIMARY"
        elif role == "support":
            policy_key = "STYLE_SUPPORT"
        else:
            policy_key = role
        policy = authority_policy["roles"][policy_key]
        role_lines.append(
            f"{reference['id']}: use only {', '.join(policy['allowed'])}; "
            f"do not transfer {', '.join(policy['forbidden'])}."
        )
    proportion_lines = (
        proportion_contract["invariants"] if proportion_contract else
        ["Preserve plausible adult anatomy and pose-aware connected joints."]
    )
    prompt = "\n".join(
        [
            "[AUTHORITY PRECEDENCE]",
            *role_lines,
            "[STYLE RENDER CONTRACT]",
            *[item["require"] for item in profile["render_contract"]],
            "[IDENTITY CONTRACT]",
            "Use character references only for the declared identity features; re-render every visible surface through the style contract.",
            "[PROPORTION AND PERSPECTIVE CONTRACT]",
            *proportion_lines,
            "[SCENE AND COMPOSITION CONTRACT]",
            scene,
            "[OBJECT COUNT / SCALE / CONTACT CONTRACT]",
            "Keep every requested object count exact, preserve plausible relative scale, and make ownership and physical contact unambiguous.",
            "[OCCLUSION / MECHANICAL CONTINUITY CONTRACT]",
            "Never rearrange anatomy, equipment, or camera geometry merely to expose every component. Correct partial or full occlusion is valid and preferred whenever demanded by viewpoint, depth, contact, or pose; an occluded component does not need to remain visibly complete.",
            "Judge a mechanism by physical continuity, not component visibility. Preserve the true connection order, shared axis, load path, and contact ownership across visible and occluded segments. Never duplicate, detach, offset, or relocate a component so that it can be shown separately.",
            "For held tools and projectiles, keep the hand, contact point, connector, and working element on one mechanically plausible chain. If the camera hides a joint or attachment, let the nearer surface occlude it and show only the portions that would actually be visible.",
            "[FORBIDDEN DEFAULT BIASES]",
            *profile["forbidden_default_biases"],
            "[FRESH GENERATION ATTESTATION]",
            "Generate a completely new integrated image from approved authorities. Do not edit, patch, layer, trace, or reference any generated candidate.",
        ]
    )
    result = {
        "schema_version": "ZPACK_COMPILED_REQUEST_v2.0",
        "scene": scene,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "references": selection["selected"],
        "selection_sha256": selection["selection_sha256"],
        "proportion_contract_id": proportion_contract_id,
        "authority_policy_sha256": canonical_sha(authority_policy),
        "style_profile_sha256": canonical_sha(profile),
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION",
        "api_key_required": False,
        "local_gpu_required": False,
        "owner_visual_verdict_required": True,
    }
    result["compile_sha256"] = canonical_sha(result)
    return result


def _ascii_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def compile_request(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    forbidden = ("prior_candidate", "edit_target", "patch", "layer_composite")
    if any(request.get(key) for key in forbidden):
        raise ZPackError("PRIOR_CANDIDATE_OR_GENERATIVE_EDIT_FORBIDDEN")
    scene = str(request.get("scene", "")).strip()
    if not scene:
        raise ZPackError("scene is required")
    if request.get("compatibility_mode") == "e4_primary_only":
        return _compile_legacy_e4(root, request, scene)

    selection = select_references(root, request)
    composition_plan = resolve_composition_plan(root, request)
    authority_policy = load_json(root / "pack/styles/default/REFERENCE_AUTHORITY_POLICY.json")
    proportion_contract_id, proportion_contract = _proportion_contract(root, request)
    role_lines = []
    routed_family = None
    routed_by_id: dict[str, dict[str, Any]] = {}
    if selection["style_family_id"]:
        router = load_json(root / "pack/styles/default/STYLE_FAMILY_ROUTER.json")
        routed_family = next(
            item for item in router["families"]
            if item["id"] == selection["style_family_id"]
        )
        routed_by_id = {item["id"]: item for item in routed_family["sources"]}
    for reference in selection["selected"]:
        role = reference["role"]
        if role in {"style_core", "style_adapter"}:
            risks = routed_by_id[reference["id"]].get("content_leakage_risk", [])
            routed_selection = next(
                item for item in selection["style_routing"]["selected"]
                if item["id"] == reference["id"]
            )
            if role == "style_core":
                line = (
                    f"{reference['id']}: absolute global STYLE_CORE. Match its face abstraction, eye geometry, "
                    "contours, hair grouping, shadow shapes, value range, highlight geometry, and background simplification."
                )
            else:
                matched = "; ".join(
                    f"{axis}={','.join(values)}"
                    for axis, values in routed_selection["matched_traits"].items()
                )
                line = (
                    f"{reference['id']}: STYLE_DOMAIN_ADAPTER only for {matched}. "
                    "Never alter or average the STYLE_CORE visual grammar."
                )
            if risks:
                line += f" Do not copy {', '.join(risks)}."
            role_lines.append(line)
            continue
        policy_key = {
            "primary": "STYLE_PRIMARY",
            "support": "STYLE_SUPPORT",
        }.get(role, role)
        policy = authority_policy["roles"][policy_key]
        line = (
            f"{reference['id']}: use only {', '.join(policy['allowed'])}; "
            f"do not transfer {', '.join(policy['forbidden'])}."
        )
        role_lines.append(line)
    family_lines = []
    if routed_family:
        family_lines = [
            "The first STYLE_CORE overrides every adapter for all global visual grammar.",
            "Core fingerprint: " + "; ".join(routed_family["shared_style_signature"]) + ".",
            "Reject drift toward " + ", ".join(routed_family["anti_drift_signatures"]) + ".",
        ]
    style_block = "\n".join(
        ["[STYLE AUTHORITY]", *family_lines, *role_lines]
        if routed_family else [
            "[STYLE AUTHORITY]",
            "Follow the selected style sample only for line, color, shading, value, material, and background rendering.",
            "Do not copy its person, costume, pose, object, composition, or scene.",
            *role_lines,
        ]
    )
    non_negotiable = list(request.get("non_negotiable", []))
    if proportion_contract:
        non_negotiable.extend(proportion_contract["invariants"])
    if not non_negotiable:
        non_negotiable.append("Keep requested camera, action, object count, contact, and safe framing exact.")
    scene_block = "[SCENE]\n" + scene
    composition_text = _composition_prompt(composition_plan)
    if composition_text:
        scene_block += "\n\n" + composition_text
    blocks = {
        "style_authority": style_block,
        "scene": scene_block,
        "non_negotiable": "[NON-NEGOTIABLE]\n" + "\n".join(non_negotiable),
        "fresh_generation": (
            "[FRESH GENERATION]\nCreate a completely new integrated image from approved authorities. "
            "Do not edit or reuse any generated candidate."
        ),
    }
    common_text = "\n".join(value for key, value in blocks.items() if key != "scene")
    common_words = _ascii_word_count(common_text)
    if common_words > 250:
        raise ZPackError("COMMON_PROMPT_WORD_LIMIT_EXCEEDED")
    prompt = "\n\n".join(blocks.values())
    _, sources = _style_sources(root)
    style_contract = [
        sources[item["id"]] for item in selection["selected"]
        if item["role"] in {"primary", "support", "style_core", "style_adapter"}
    ]
    result = {
        "schema_version": COMPILED_REQUEST_V3,
        "request_schema_version": STYLE_REQUEST_V3,
        "scene": scene,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_blocks": {
            key: {"characters": len(value), "ascii_words": _ascii_word_count(value)}
            for key, value in blocks.items()
        },
        "common_instruction_ascii_words": common_words,
        "references": selection["selected"],
        "selection_sha256": selection["selection_sha256"],
        "style_profile_id": selection["style_profile_id"],
        "style_family_id": selection["style_family_id"],
        "style_routing": selection["style_routing"],
        "style_contract_sha256": canonical_sha(style_contract),
        "proportion_contract_id": proportion_contract_id,
        "composition_plan": composition_plan,
        "authority_policy_sha256": canonical_sha(authority_policy),
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION",
        "api_key_required": False,
        "local_gpu_required": False,
        "owner_visual_verdict_required": True,
    }
    result["compile_sha256"] = canonical_sha(result)
    return result


def _staged_restyle_policy(root: Path) -> dict[str, Any]:
    spec = load_json(root / "PACK_SPEC.json")
    exception = spec.get("candidate_policy", {}).get("staged_restyle_exception", {})
    if exception.get("enabled") is not True or exception.get("mode") != "EXPLICIT_OPT_IN_ONLY":
        raise ZPackError("STAGED_RESTYLE_DISABLED")
    policy_path = exception.get("policy_path")
    if not isinstance(policy_path, str):
        raise ZPackError("STAGED_RESTYLE_POLICY_INVALID")
    policy = load_json(resolve_pack_path(root, policy_path))
    if (
        policy.get("schema_version") != "ZPACK_STAGED_RESTYLE_POLICY_v1.0"
        or policy.get("status") != "LIMITED_DEFAULT"
        or policy.get("enabled") is not True
        or policy.get("maximum_restyle_depth") != 1
        or policy.get("style_adapter_allowed") is not False
        or policy.get("recursive_restyle_allowed") is not False
        or policy.get("required_reference_roles") != ["structure_edit_target", "style_core"]
        or policy.get("accepted_source_receipt_schemas") != sorted(FRESH_RUN_RECEIPT_SCHEMAS)
    ):
        raise ZPackError("STAGED_RESTYLE_POLICY_INVALID")
    list_fields = (
        "allowed_style_core_ids", "shared_style_signature", "anti_drift_signatures",
        "required_preservation_axes", "required_audit_axes",
    )
    if any(
        not isinstance(policy.get(field), list) or not policy[field]
        or any(not isinstance(item, str) or not item.strip() for item in policy[field])
        for field in list_fields
    ):
        raise ZPackError("STAGED_RESTYLE_POLICY_INVALID")
    if policy["required_audit_axes"] != [
        "STYLE_REFERENCE_FIDELITY", "STYLE_CONTENT_LEAKAGE",
        "SCENE_PROMPT_COMPLIANCE", "STRUCTURE_PRESERVATION",
    ]:
        raise ZPackError("STAGED_RESTYLE_POLICY_INVALID")
    if policy.get("workflow_contract") != {
        "id": "ZPACK_FRESH_DRAFT_SINGLE_RESTYLE_v1",
        "mode": "FRESH_DRAFT_THEN_SINGLE_RESTYLE",
        "default_for_style_family_ids": ["ZPACK_STYLE_FAMILY"],
        "draft_compiled_schema": STAGED_DRAFT_COMPILED_V1,
        "draft_receipt_schema": STAGED_DRAFT_RUN_RECEIPT_V1,
        "default_fresh_draft_count": 1,
        "default_restyle_count": 1,
        "default_retry_count": 0,
        "automatic_retry_allowed": False,
        "operator_requested_fresh_chain_retry_allowed": True,
        "retry_reuses_prior_candidate": False,
    }:
        raise ZPackError("STAGED_RESTYLE_POLICY_INVALID")
    return policy


def style_workflow_policy(root: Path) -> dict[str, Any]:
    """Return the materialized limited-default workflow contract."""
    policy = _staged_restyle_policy(root)
    contract = policy["workflow_contract"]
    return {
        "schema_version": "ZPACK_STYLE_WORKFLOW_POLICY_v1.0",
        "status": policy["status"],
        "workflow_id": contract["id"],
        "mode": contract["mode"],
        "default_for_style_family_ids": contract["default_for_style_family_ids"],
        "allowed_style_core_ids": policy["allowed_style_core_ids"],
        "default_fresh_draft_count": contract["default_fresh_draft_count"],
        "default_restyle_count": contract["default_restyle_count"],
        "default_retry_count": contract["default_retry_count"],
        "automatic_retry_allowed": contract["automatic_retry_allowed"],
        "operator_requested_fresh_chain_retry_allowed": (
            contract["operator_requested_fresh_chain_retry_allowed"]
        ),
        "retry_reuses_prior_candidate": contract["retry_reuses_prior_candidate"],
        "benchmark_or_test_runtime_dependency": False,
    }


def compile_staged_draft_request(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    """Compile phase one of the limited-default fresh-draft/restyle workflow."""
    allowed_fields = {
        "schema_version", "style_family_id", "scene_traits", "style_adapter_limit",
        "scene", "non_negotiable", "required_authorities", "proportion_contract_id",
        "composition",
        "benchmark_mode", "prior_candidate", "edit_target", "patch", "layer_composite",
    }
    if set(request) - allowed_fields:
        raise ZPackError("STAGED_DRAFT_REQUEST_FIELDS_INVALID")
    if request.get("schema_version") != STYLE_REQUEST_V3:
        raise ZPackError("STYLE_REQUEST_V3_REQUIRED")
    benchmark_mode = request.get("benchmark_mode")
    if benchmark_mode not in (None, False) or isinstance(benchmark_mode, int) and not isinstance(benchmark_mode, bool):
        raise ZPackError("STAGED_WORKFLOW_BENCHMARK_MODE_FORBIDDEN")
    if any(request.get(key) for key in ("prior_candidate", "edit_target", "patch", "layer_composite")):
        raise ZPackError("PRIOR_CANDIDATE_OR_GENERATIVE_EDIT_FORBIDDEN")
    adapter_limit = request.get("style_adapter_limit")
    if adapter_limit is not None and (isinstance(adapter_limit, bool) or adapter_limit != 0):
        raise ZPackError("STAGED_WORKFLOW_ADAPTER_FORBIDDEN")
    scene = str(request.get("scene", "")).strip()
    if not scene:
        raise ZPackError("scene is required")

    composition_plan = resolve_composition_plan(root, request)
    policy = _staged_restyle_policy(root)
    contract = policy["workflow_contract"]
    family_id = request.get("style_family_id")
    if family_id not in contract["default_for_style_family_ids"]:
        raise ZPackError("STAGED_WORKFLOW_FAMILY_NOT_ALLOWED")
    router = load_json(root / "pack/styles/default/STYLE_FAMILY_ROUTER.json")
    family = next((item for item in router.get("families", []) if item.get("id") == family_id), None)
    if family is None:
        raise ZPackError("STAGED_WORKFLOW_FAMILY_NOT_ALLOWED")
    traits = _normalize_scene_traits(family, request.get("scene_traits"))
    core_id = family.get("core_source_id")
    if core_id not in policy["allowed_style_core_ids"]:
        raise ZPackError("STAGED_RESTYLE_CORE_NOT_ALLOWED")
    _, sources = _style_sources(root)
    core = sources.get(core_id)
    routed_core = next((item for item in family.get("sources", []) if item.get("id") == core_id), None)
    if (
        core is None
        or routed_core is None
        or routed_core.get("sha256") != core.get("sha256")
        or core.get("style_role") != "primary"
        or core.get("lifecycle_status") not in {"PENDING_FIDELITY", "PROMOTED"}
        or core.get("benchmark_reference_eligible") is not True
    ):
        raise ZPackError("STAGED_RESTYLE_CORE_NOT_ALLOWED")
    core_path = resolve_pack_path(root, core["path"])
    if not core_path.is_file() or sha256(core_path) != core["sha256"]:
        raise ZPackError("STAGED_RESTYLE_CORE_NOT_ALLOWED")

    required_authorities = request.get("required_authorities", [])
    if (
        not isinstance(required_authorities, list)
        or any(not isinstance(item, dict) for item in required_authorities)
    ):
        raise ZPackError("REQUIRED_AUTHORITIES_INVALID")
    non_style = _select_non_style(root, request)
    maximum = load_json(root / "PACK_SPEC.json")["reference_slot_limit"]
    if 1 + len(non_style) > maximum:
        raise ZPackError("STYLE_REFERENCE_CAPACITY_HOLD")
    authority_policy = load_json(root / "pack/styles/default/REFERENCE_AUTHORITY_POLICY.json")
    role_lines = []
    for reference in non_style:
        role_policy = authority_policy["roles"][reference["role"]]
        role_lines.append(
            f"{reference['id']}: use only {', '.join(role_policy['allowed'])}; "
            f"do not transfer {', '.join(role_policy['forbidden'])}."
        )
    proportion_contract_id, proportion_contract = _proportion_contract(root, request)
    non_negotiable = request.get("non_negotiable", [])
    if (
        not isinstance(non_negotiable, list) or len(non_negotiable) > 12
        or any(not isinstance(item, str) or not item.strip() or len(item) > 500 for item in non_negotiable)
    ):
        raise ZPackError("NON_NEGOTIABLE_INVALID")
    non_negotiable = [item.strip() for item in non_negotiable]
    if proportion_contract:
        non_negotiable.extend(proportion_contract["invariants"])
    if not non_negotiable:
        non_negotiable.append("Keep requested camera, action, object count, contact, and safe framing exact.")
    style_signature = "; ".join(policy["shared_style_signature"])
    anti_drift = ", ".join(policy["anti_drift_signatures"])
    content_risks = ", ".join(core.get("forbidden_content_signatures", []))
    scene_block = "[SCENE]\n" + scene
    composition_text = _composition_prompt(composition_plan)
    if composition_text:
        scene_block += "\n\n" + composition_text
    blocks = {
        "workflow": (
            "[LIMITED DEFAULT WORKFLOW — PHASE 1 OF 2]\n"
            "Create exactly one completely fresh integrated draft. This phase establishes the requested "
            "scene, composition, anatomy, object geometry, contact, weather, and lighting. Do not use any "
            "prior candidate. The next and only edit phase may restyle this draft once."
        ),
        "style": (
            "[SOLE STYLE CORE PREVIEW]\n"
            f"Use {core_id} as the only visual-style reference. Apply {style_signature}. "
            f"Reject {anti_drift}. Do not copy {content_risks}. No adapter is permitted."
        ),
        "authorities": "[NON-STYLE AUTHORITIES]\n" + (
            "\n".join(role_lines) if role_lines else "No additional identity, item, or pose authority."
        ),
        "scene": scene_block,
        "non_negotiable": "[NON-NEGOTIABLE]\n" + "\n".join(non_negotiable),
        "fresh": (
            "[FRESH DRAFT ATTESTATION]\nGenerate one new image from these snapshots only. "
            "Do not edit, patch, trace, composite, or reuse a generated candidate."
        ),
    }
    prompt = "\n\n".join(blocks.values())
    references = [{
        "id": core_id,
        "role": "style_core",
        "path": core["path"],
        "sha256": core["sha256"],
    }, *non_style]
    result = {
        "schema_version": STAGED_DRAFT_COMPILED_V1,
        "request_schema_version": STYLE_REQUEST_V3,
        "operation": "STAGED_STYLE_WORKFLOW_DRAFT",
        "workflow_contract": contract,
        "workflow_phase": "FRESH_DRAFT",
        "scene": scene,
        "scene_traits": traits,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_blocks": {
            key: {"characters": len(value), "ascii_words": _ascii_word_count(value)}
            for key, value in blocks.items()
        },
        "references": references,
        "selection_sha256": canonical_sha(references),
        "style_family_id": family_id,
        "style_core_id": core_id,
        "style_adapter_used": False,
        "style_contract_sha256": canonical_sha({"policy": policy, "source": core, "family": family}),
        "proportion_contract_id": proportion_contract_id,
        "composition_plan": composition_plan,
        "authority_policy_sha256": canonical_sha(authority_policy),
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION",
        "api_key_required": False,
        "local_gpu_required": False,
        "prior_candidate_used": False,
        "automatic_retry_count": 0,
        "owner_visual_verdict_required": True,
    }
    result["compile_sha256"] = canonical_sha(result)
    return result


def _external_file(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ZPackError(f"{label}_PATH_REQUIRED")
    path = Path(value)
    if not path.is_absolute():
        raise ZPackError(f"{label}_ABSOLUTE_PATH_REQUIRED")
    resolved = path.resolve()
    if resolved == root.resolve() or _is_relative_to(resolved, root.resolve()):
        raise ZPackError(f"{label}_INSIDE_PACK_FORBIDDEN")
    if not resolved.is_file():
        raise ZPackError(f"{label}_FILE_NOT_FOUND")
    return resolved


def _validate_structure_target(root: Path, target: Any) -> tuple[dict[str, Any], Path, Path]:
    if not isinstance(target, dict):
        raise ZPackError("STRUCTURE_EDIT_TARGET_REQUIRED")
    required = {"path", "sha256", "source_run_receipt_path", "source_run_receipt_sha256"}
    if set(target) != required:
        raise ZPackError("STRUCTURE_EDIT_TARGET_FIELDS_INVALID")
    candidate_path = _external_file(root, target["path"], "STRUCTURE_EDIT_TARGET")
    if candidate_path.suffix.casefold() not in IMAGE_SUFFIXES:
        raise ZPackError("STRUCTURE_EDIT_TARGET_IMAGE_REQUIRED")
    if candidate_path.stat().st_size == 0:
        raise ZPackError("STRUCTURE_EDIT_TARGET_EMPTY")
    for key in ("sha256", "source_run_receipt_sha256"):
        if not isinstance(target[key], str) or re.fullmatch(r"[0-9a-f]{64}", target[key]) is None:
            raise ZPackError("STRUCTURE_EDIT_TARGET_BINDING_INVALID")
    if sha256(candidate_path) != target["sha256"]:
        raise ZPackError("STRUCTURE_EDIT_TARGET_SHA_MISMATCH")
    receipt_path = _external_file(root, target["source_run_receipt_path"], "SOURCE_RUN_RECEIPT")
    if sha256(receipt_path) != target["source_run_receipt_sha256"]:
        raise ZPackError("SOURCE_RUN_RECEIPT_SHA_MISMATCH")
    receipt = load_json(receipt_path)
    if receipt.get("schema_version") not in FRESH_RUN_RECEIPT_SCHEMAS:
        raise ZPackError("RECURSIVE_RESTYLE_FORBIDDEN")
    required_receipt_fields = {
        "run_id", "pack_root", "workspace_root", "compile_sha256",
        "snapshot_references", "prior_candidate_used",
    }
    if not required_receipt_fields.issubset(receipt):
        raise ZPackError("SOURCE_RUN_RECEIPT_INVALID")
    if receipt.get("prior_candidate_used") is not False:
        raise ZPackError("SOURCE_RUN_NOT_FRESH_GENERATION")
    source_run_root = Path(receipt.get("workspace_root", "")).resolve()
    if receipt_path != source_run_root / "run-receipt.json":
        raise ZPackError("SOURCE_RUN_RECEIPT_LOCATION_INVALID")
    if Path(receipt.get("pack_root", "")).resolve() != root.resolve():
        raise ZPackError("SOURCE_RUN_PACK_MISMATCH")
    candidate_root = (source_run_root / "candidates").resolve()
    if not _is_relative_to(candidate_path, candidate_root):
        raise ZPackError("STRUCTURE_EDIT_TARGET_NOT_FRESH_CANDIDATE")
    reference_shas = {
        item.get("snapshot_sha256") for item in receipt.get("snapshot_references", [])
    }
    if target["sha256"] in reference_shas:
        raise ZPackError("STRUCTURE_EDIT_TARGET_IS_SOURCE_REFERENCE")
    integrity = verify_run_integrity(root, source_run_root)
    if integrity["status"] != "PASS":
        raise ZPackError("SOURCE_RUN_INTEGRITY_FAILED")
    return receipt, candidate_path, receipt_path


def compile_restyle_request(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    """Compile the single-pass, explicitly opted-in structure-to-style edit lane."""
    allowed_fields = {
        "schema_version", "operation", "opt_in", "restyle_pass",
        "structure_edit_target", "style_core_id", "preservation_requirements",
    }
    if set(request) - allowed_fields:
        raise ZPackError("STAGED_RESTYLE_REQUEST_FIELDS_INVALID")
    if request.get("schema_version") != STAGED_RESTYLE_REQUEST_V1:
        raise ZPackError("STAGED_RESTYLE_REQUEST_V1_REQUIRED")
    if request.get("operation") != "STAGED_RESTYLE" or request.get("opt_in") is not True:
        raise ZPackError("STAGED_RESTYLE_EXPLICIT_OPT_IN_REQUIRED")
    if request.get("restyle_pass") != 1:
        raise ZPackError("RECURSIVE_RESTYLE_FORBIDDEN")
    policy = _staged_restyle_policy(root)
    source_receipt, target_path, source_receipt_path = _validate_structure_target(
        root, request.get("structure_edit_target")
    )
    core_id = request.get("style_core_id")
    if core_id not in policy.get("allowed_style_core_ids", []):
        raise ZPackError("STAGED_RESTYLE_CORE_NOT_ALLOWED")
    _, sources = _style_sources(root)
    core = sources.get(core_id)
    if core is None:
        raise ZPackError("STAGED_RESTYLE_CORE_NOT_ALLOWED")
    _assert_style_source(root, core, "primary", benchmark=True)
    if sha256(target_path) == core["sha256"]:
        raise ZPackError("STRUCTURE_TARGET_AND_STYLE_CORE_MUST_DIFFER")
    preservation = request.get("preservation_requirements", [])
    if (
        not isinstance(preservation, list) or len(preservation) > 12
        or any(
            not isinstance(item, str) or not item.strip() or len(item) > 300
            or not item.strip().casefold().startswith(("preserve ", "보존", "유지"))
            for item in preservation
        )
    ):
        raise ZPackError("PRESERVATION_REQUIREMENTS_INVALID")
    preservation = [item.strip() for item in preservation]
    preservation_axes = [*policy["required_preservation_axes"], *preservation]
    style_signature = "; ".join(policy["shared_style_signature"])
    anti_drift = ", ".join(policy["anti_drift_signatures"])
    content_risks = ", ".join(core.get("forbidden_content_signatures", []))
    blocks = {
        "structure_target": (
            "[STRUCTURE EDIT TARGET — IMAGE 1]\n"
            "Use Image 1 only as the immutable content and geometry target. Preserve every visible subject, "
            "object, spatial relationship, camera decision, and scene condition. It has no style authority."
        ),
        "style_authority": (
            "[SOLE STYLE AUTHORITY — IMAGE 2]\n"
            f"Use {core_id} as the only rendering-style authority. Transfer only its global visual grammar; "
            f"do not copy {content_risks}. No adapter or other style reference is permitted."
        ),
        "style_transfer": (
            "[STYLE TRANSFER]\nApply this grammar across both subject and background: " + style_signature
            + ". Reject drift toward " + anti_drift + "."
        ),
        "preservation": (
            "[STRICT PRESERVATION]\nPreserve exactly:\n- " + "\n- ".join(preservation_axes)
        ),
        "single_pass": (
            "[SINGLE PASS BOUNDARY]\nEdit rendering style only. Do not recompose, crop, rotate, mirror, zoom, "
            "add, remove, replace, duplicate, or redesign content. Perform exactly one restyle pass and do not "
            "use this result as another edit target."
        ),
    }
    prompt = "\n\n".join(blocks.values())
    references = [
        {
            "id": "STRUCTURE_EDIT_TARGET",
            "role": "structure_edit_target",
            "path": str(target_path),
            "sha256": sha256(target_path),
        },
        {
            "id": core_id,
            "role": "style_core",
            "path": core["path"],
            "sha256": core["sha256"],
        },
    ]
    result = {
        "schema_version": STAGED_RESTYLE_COMPILED_V1,
        "request_schema_version": STAGED_RESTYLE_REQUEST_V1,
        "operation": "STAGED_RESTYLE",
        "experimental_opt_in": True,
        "restyle_depth": 1,
        "maximum_restyle_depth": 1,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_blocks": {
            key: {"characters": len(value), "ascii_words": _ascii_word_count(value)}
            for key, value in blocks.items()
        },
        "references": references,
        "selection_sha256": canonical_sha(references),
        "source_generation_binding": {
            "run_id": source_receipt["run_id"],
            "compile_sha256": source_receipt["compile_sha256"],
            "receipt_path": str(source_receipt_path),
            "receipt_sha256": sha256(source_receipt_path),
            "candidate_sha256": sha256(target_path),
            "prior_candidate_used": False,
        },
        "style_core_id": core_id,
        "style_adapter_used": False,
        "style_contract_sha256": canonical_sha({"policy": policy, "source": core}),
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION_EDIT",
        "api_key_required": False,
        "local_gpu_required": False,
        "owner_visual_verdict_required": True,
        "required_audit_axes": policy["required_audit_axes"],
    }
    result["compile_sha256"] = canonical_sha(result)
    return result


def create_restyle_request(
    root: Path,
    candidate: Path,
    source_run_root: Path,
    style_core_id: str,
    preservation_requirements: list[str] | None = None,
) -> dict[str, Any]:
    """Build and validate a restyle request without manual SHA transcription."""
    source_run_root = validate_workspace(root, source_run_root)
    candidate = candidate.resolve()
    receipt = source_run_root / "run-receipt.json"
    if not candidate.is_file():
        raise ZPackError("STRUCTURE_EDIT_TARGET_FILE_NOT_FOUND")
    if not receipt.is_file():
        raise ZPackError("SOURCE_RUN_RECEIPT_FILE_NOT_FOUND")
    request = {
        "schema_version": STAGED_RESTYLE_REQUEST_V1,
        "operation": "STAGED_RESTYLE",
        "opt_in": True,
        "restyle_pass": 1,
        "structure_edit_target": {
            "path": str(candidate),
            "sha256": sha256(candidate),
            "source_run_receipt_path": str(receipt),
            "source_run_receipt_sha256": sha256(receipt),
        },
        "style_core_id": style_core_id,
    }
    if preservation_requirements:
        request["preservation_requirements"] = preservation_requirements
    compile_restyle_request(root, request)
    return request


SCENE_AUDIT_CHECKS = (
    "OBJECT_COUNT", "CONTACT_OWNERSHIP", "LIGHT_DIRECTION", "CAST_SHADOW",
    "MATERIAL_SEPARATION", "DRY_SURFACE_BIAS", "OCCLUSION_GEOMETRY",
    "MECHANICAL_CONTINUITY", "SAFE_FRAME", "FRAME_PRESSURE_DISTORTION",
)


OWNER_AXIS_VERDICTS = (
    "OWNER_STYLE_VERDICT", "OWNER_BODY_PROPORTION_VERDICT", "OWNER_OBJECT_SCALE_VERDICT",
    "OWNER_COMPOSITION_ACTION_VERDICT", "OWNER_LIGHT_SHADOW_MATERIAL_VERDICT",
)


def required_audit_checks(root: Path) -> tuple[str, ...]:
    style = load_json(root / "pack/styles/default/STYLE_LOCK.json")["required_checks"]
    proportion = load_json(root / "pack/styles/default/PROPORTION_LOCK.json")["required_checks"]
    return tuple([*style, *proportion, *SCENE_AUDIT_CHECKS])


def prepare_staged_draft_run(
    root: Path, workspace: Path, run_id: str, request: dict[str, Any],
) -> dict[str, Any]:
    """Prepare the single fresh draft required by the limited-default workflow."""
    _validate_asset_id(run_id)
    workspace = validate_workspace(root, workspace)
    compiled = compile_staged_draft_request(root, request)
    run_root = workspace / "runs" / run_id
    if run_root.exists():
        raise ZPackError("run already exists")
    for name in ("request", "input-snapshot", "compiled", "candidates", "audit", "evidence"):
        (run_root / name).mkdir(parents=True, exist_ok=False)
    snapshot_references = []
    for index, reference in enumerate(compiled["references"], start=1):
        source = resolve_pack_path(root, reference["path"])
        destination = run_root / "input-snapshot" / f"{index:02d}_{reference['id']}{source.suffix.lower()}"
        shutil.copy2(source, destination)
        copied_sha = sha256(destination)
        if copied_sha != reference["sha256"]:
            raise ZPackError(f"snapshot SHA mismatch: {reference['id']}")
        snapshot_references.append({
            **reference,
            "snapshot_path": destination.relative_to(run_root).as_posix(),
            "snapshot_sha256": copied_sha,
        })
    compiled_with_snapshot = {**compiled, "references": snapshot_references}
    inventory = pack_authority_inventory(root)
    request_path = run_root / "request/request.json"
    compiled_path = run_root / "compiled/compiled-request.json"
    write_json(request_path, request)
    write_json(compiled_path, compiled_with_snapshot)
    receipt = {
        "schema_version": STAGED_DRAFT_RUN_RECEIPT_V1,
        "run_id": run_id,
        "pack_root": str(root.resolve()),
        "workspace_root": str(run_root.resolve()),
        "pack_version": load_json(root / "PACK_SPEC.json")["pack_version"],
        "operation": "STAGED_STYLE_WORKFLOW_DRAFT",
        "workflow_contract": compiled["workflow_contract"],
        "workflow_phase": "FRESH_DRAFT",
        "style_family_id": compiled["style_family_id"],
        "style_core_id": compiled["style_core_id"],
        "style_adapter_used": False,
        "compile_sha256": compiled["compile_sha256"],
        "selection_sha256": compiled["selection_sha256"],
        "request_sha256": sha256(request_path),
        "pack_authorities_before": inventory,
        "snapshot_references": snapshot_references,
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION",
        "api_key_used": False,
        "local_gpu_used": False,
        "prior_candidate_used": False,
        "automatic_retry_count": 0,
        "automatic_retry_allowed": False,
        "pack_mutation_check": "PENDING",
    }
    write_json(run_root / "run-receipt.json", receipt)
    return {
        "status": "READY",
        "workflow_status": "FRESH_DRAFT_READY",
        "workflow_phase": "FRESH_DRAFT",
        "run_id": run_id,
        "run_root": str(run_root),
        "compiled_path": str(compiled_path),
        "receipt_path": str(run_root / "run-receipt.json"),
        "candidate_directory": str(run_root / "candidates"),
        "reference_paths": [str(run_root / item["snapshot_path"]) for item in snapshot_references],
        "style_core_id": compiled["style_core_id"],
        "default_retry_count": 0,
        "automatic_retry_allowed": False,
        "next_step": "Generate exactly one fresh draft and save it under candidate_directory, then run workflow continue.",
        "compile_sha256": compiled["compile_sha256"],
    }


def prepare_run(root: Path, workspace: Path, run_id: str, request: dict[str, Any]) -> dict[str, Any]:
    """Create an external run with immutable authority snapshots and bindings."""
    _validate_asset_id(run_id)
    workspace = validate_workspace(root, workspace)
    compiled = compile_request(root, request)
    run_root = workspace / "runs" / run_id
    if run_root.exists():
        raise ZPackError("run already exists")
    for name in ("request", "input-snapshot", "compiled", "candidates", "audit", "evidence"):
        (run_root / name).mkdir(parents=True, exist_ok=False)
    snapshot_references = []
    for index, reference in enumerate(compiled["references"], start=1):
        source = resolve_pack_path(root, reference["path"])
        destination = run_root / "input-snapshot" / f"{index:02d}_{reference['id']}{source.suffix.lower()}"
        shutil.copy2(source, destination)
        copied_sha = sha256(destination)
        if copied_sha != reference["sha256"]:
            raise ZPackError(f"snapshot SHA mismatch: {reference['id']}")
        snapshot_references.append({
            **reference,
            "snapshot_path": destination.relative_to(run_root).as_posix(),
            "snapshot_sha256": copied_sha,
        })
    compiled_with_snapshot = {**compiled, "references": snapshot_references}
    inventory = pack_authority_inventory(root)
    write_json(run_root / "request/request.json", request)
    write_json(run_root / "compiled/compiled-request.json", compiled_with_snapshot)
    receipt = {
        "schema_version": (
            "ZPACK_RUN_RECEIPT_v3.0"
            if compiled["schema_version"] == COMPILED_REQUEST_V3
            else "ZPACK_RUN_RECEIPT_v2.0"
        ),
        "run_id": run_id,
        "pack_root": str(root.resolve()),
        "workspace_root": str(run_root.resolve()),
        "pack_version": load_json(root / "PACK_SPEC.json")["pack_version"],
        "compile_sha256": compiled["compile_sha256"],
        "selection_sha256": compiled["selection_sha256"],
        "pack_authorities_before": inventory,
        "snapshot_references": snapshot_references,
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION",
        "api_key_used": False,
        "local_gpu_used": False,
        "prior_candidate_used": False,
        "pack_mutation_check": "PENDING",
    }
    write_json(run_root / "run-receipt.json", receipt)
    return {
        "status": "READY",
        "run_id": run_id,
        "run_root": str(run_root),
        "compiled_path": str(run_root / "compiled/compiled-request.json"),
        "receipt_path": str(run_root / "run-receipt.json"),
        "reference_paths": [str(run_root / item["snapshot_path"]) for item in snapshot_references],
        "compile_sha256": compiled["compile_sha256"],
    }


def prepare_restyle_run(
    root: Path, workspace: Path, run_id: str, request: dict[str, Any],
) -> dict[str, Any]:
    """Create an external two-reference snapshot for one staged restyle pass."""
    _validate_asset_id(run_id)
    workspace = validate_workspace(root, workspace)
    compiled = compile_restyle_request(root, request)
    run_root = workspace / "runs" / run_id
    if run_root.exists():
        raise ZPackError("run already exists")
    for name in ("request", "input-snapshot", "compiled", "candidates", "audit", "evidence"):
        (run_root / name).mkdir(parents=True, exist_ok=False)
    snapshot_references = []
    for index, reference in enumerate(compiled["references"], start=1):
        source = (
            Path(reference["path"]).resolve()
            if reference["role"] == "structure_edit_target"
            else resolve_pack_path(root, reference["path"])
        )
        destination = run_root / "input-snapshot" / f"{index:02d}_{reference['id']}{source.suffix.lower()}"
        shutil.copy2(source, destination)
        copied_sha = sha256(destination)
        if copied_sha != reference["sha256"]:
            raise ZPackError(f"snapshot SHA mismatch: {reference['id']}")
        snapshot_references.append({
            **reference,
            "snapshot_path": destination.relative_to(run_root).as_posix(),
            "snapshot_sha256": copied_sha,
        })
    source_receipt = Path(compiled["source_generation_binding"]["receipt_path"])
    source_receipt_record = load_json(source_receipt)
    limited_default = source_receipt_record.get("schema_version") == STAGED_DRAFT_RUN_RECEIPT_V1
    source_receipt_snapshot = run_root / "input-snapshot/source-run-receipt.json"
    shutil.copy2(source_receipt, source_receipt_snapshot)
    source_receipt_sha = sha256(source_receipt_snapshot)
    if source_receipt_sha != compiled["source_generation_binding"]["receipt_sha256"]:
        raise ZPackError("SOURCE_RUN_RECEIPT_SHA_MISMATCH")
    source_binding = {
        **compiled["source_generation_binding"],
        "snapshot_path": source_receipt_snapshot.relative_to(run_root).as_posix(),
        "snapshot_sha256": source_receipt_sha,
    }
    compiled_with_snapshot = {
        **compiled,
        "references": snapshot_references,
        "source_generation_binding": source_binding,
    }
    inventory = pack_authority_inventory(root)
    write_json(run_root / "request/request.json", request)
    write_json(run_root / "compiled/compiled-request.json", compiled_with_snapshot)
    receipt = {
        "schema_version": STAGED_RESTYLE_RUN_RECEIPT_V1,
        "run_id": run_id,
        "pack_root": str(root.resolve()),
        "workspace_root": str(run_root.resolve()),
        "pack_version": load_json(root / "PACK_SPEC.json")["pack_version"],
        "compile_sha256": compiled["compile_sha256"],
        "selection_sha256": compiled["selection_sha256"],
        "pack_authorities_before": inventory,
        "snapshot_references": snapshot_references,
        "source_generation_binding": source_binding,
        "transport": "CODEX_OAUTH_BUILTIN_IMAGE_GENERATION_EDIT",
        "api_key_used": False,
        "local_gpu_used": False,
        "prior_candidate_used": True,
        "prior_candidate_scope": "STRUCTURE_EDIT_TARGET_ONLY",
        "generated_candidate_input_used": True,
        "style_adapter_used": False,
        "restyle_depth": 1,
        "maximum_restyle_depth": 1,
        "recursive_restyle_allowed": False,
        "pack_mutation_check": "PENDING",
    }
    if limited_default:
        receipt.update({
            "workflow_contract": source_receipt_record["workflow_contract"],
            "workflow_phase": "SINGLE_RESTYLE",
            "limited_default_workflow": True,
            "automatic_retry_count": 0,
            "automatic_retry_allowed": False,
        })
    write_json(run_root / "run-receipt.json", receipt)
    return {
        "status": "READY",
        "mode": "LIMITED_DEFAULT_STAGED_RESTYLE" if limited_default else "STAGED_RESTYLE_OPT_IN",
        "run_id": run_id,
        "run_root": str(run_root),
        "compiled_path": str(run_root / "compiled/compiled-request.json"),
        "receipt_path": str(run_root / "run-receipt.json"),
        "reference_paths": [str(run_root / item["snapshot_path"]) for item in snapshot_references],
        "compile_sha256": compiled["compile_sha256"],
        "restyle_depth": 1,
    }


def continue_style_workflow(
    root: Path,
    workspace: Path,
    run_id: str,
    candidate: Path,
    source_run_root: Path,
    preservation_requirements: list[str] | None = None,
) -> dict[str, Any]:
    """Bind one staged-draft candidate and prepare the workflow's sole restyle pass."""
    source_run_root = validate_workspace(root, source_run_root)
    receipt_path = source_run_root / "run-receipt.json"
    if not receipt_path.is_file():
        raise ZPackError("SOURCE_RUN_RECEIPT_FILE_NOT_FOUND")
    receipt = load_json(receipt_path)
    policy = _staged_restyle_policy(root)
    if (
        receipt.get("schema_version") != STAGED_DRAFT_RUN_RECEIPT_V1
        or receipt.get("workflow_phase") != "FRESH_DRAFT"
        or receipt.get("workflow_contract") != policy["workflow_contract"]
        or receipt.get("style_core_id") not in policy["allowed_style_core_ids"]
        or receipt.get("prior_candidate_used") is not False
        or receipt.get("automatic_retry_count") != 0
    ):
        raise ZPackError("STAGED_WORKFLOW_SOURCE_INVALID")
    if verify_run_integrity(root, source_run_root)["status"] != "PASS":
        raise ZPackError("SOURCE_RUN_INTEGRITY_FAILED")
    request = create_restyle_request(
        root,
        candidate,
        source_run_root,
        receipt["style_core_id"],
        preservation_requirements,
    )
    prepared = prepare_restyle_run(root, workspace, run_id, request)
    return {
        **prepared,
        "workflow_status": "SOLE_RESTYLE_READY",
        "workflow_phase": "SINGLE_RESTYLE",
        "source_draft_run_id": receipt["run_id"],
        "default_retry_count": 0,
        "automatic_retry_allowed": False,
        "next_step": "Perform exactly one image edit with the emitted two snapshots, then audit and verify.",
    }


def verify_run_integrity(root: Path, run_root: Path) -> dict[str, Any]:
    run_root = validate_workspace(root, run_root)
    receipt_path = run_root / "run-receipt.json"
    receipt = load_json(receipt_path)
    before = receipt.get("pack_authorities_before", [])
    after = pack_authority_inventory(root)
    changed = before != after
    snapshot_errors = []
    for reference in receipt.get("snapshot_references", []):
        snapshot = (run_root / reference["snapshot_path"]).resolve()
        if not _is_relative_to(snapshot, run_root) or not snapshot.is_file():
            snapshot_errors.append(reference["id"] + ":MISSING")
        elif sha256(snapshot) != reference["snapshot_sha256"]:
            snapshot_errors.append(reference["id"] + ":SHA")
    if receipt.get("schema_version") == STAGED_DRAFT_RUN_RECEIPT_V1:
        draft_invariants = {
            "operation": "STAGED_STYLE_WORKFLOW_DRAFT",
            "workflow_phase": "FRESH_DRAFT",
            "style_adapter_used": False,
            "prior_candidate_used": False,
            "automatic_retry_count": 0,
            "automatic_retry_allowed": False,
        }
        for key, expected in draft_invariants.items():
            if receipt.get(key) != expected:
                snapshot_errors.append(f"STAGED_DRAFT:{key}")
        try:
            policy = _staged_restyle_policy(root)
            if receipt.get("workflow_contract") != policy["workflow_contract"]:
                snapshot_errors.append("STAGED_DRAFT:WORKFLOW_CONTRACT")
            if receipt.get("style_core_id") not in policy["allowed_style_core_ids"]:
                snapshot_errors.append("STAGED_DRAFT:STYLE_CORE")
        except ZPackError:
            snapshot_errors.append("STAGED_DRAFT:POLICY")
        request_path = run_root / "request/request.json"
        if not request_path.is_file() or sha256(request_path) != receipt.get("request_sha256"):
            snapshot_errors.append("STAGED_DRAFT:REQUEST")
    if receipt.get("schema_version") == STAGED_RESTYLE_RUN_RECEIPT_V1:
        roles = [item.get("role") for item in receipt.get("snapshot_references", [])]
        if roles != ["structure_edit_target", "style_core"]:
            snapshot_errors.append("STAGED_RESTYLE:REFERENCE_ROLES")
        staged_invariants = {
            "prior_candidate_used": True,
            "generated_candidate_input_used": True,
            "style_adapter_used": False,
            "restyle_depth": 1,
            "maximum_restyle_depth": 1,
            "recursive_restyle_allowed": False,
        }
        for key, expected in staged_invariants.items():
            if receipt.get(key) != expected:
                snapshot_errors.append(f"STAGED_RESTYLE:{key}")
        source_binding = receipt.get("source_generation_binding", {})
        source_snapshot = (run_root / source_binding.get("snapshot_path", "")).resolve()
        if (
            not _is_relative_to(source_snapshot, run_root)
            or not source_snapshot.is_file()
            or sha256(source_snapshot) != source_binding.get("snapshot_sha256")
            or source_binding.get("snapshot_sha256") != source_binding.get("receipt_sha256")
        ):
            snapshot_errors.append("STAGED_RESTYLE:SOURCE_RECEIPT")
        elif receipt.get("limited_default_workflow") is True:
            source_record = load_json(source_snapshot)
            policy = _staged_restyle_policy(root)
            limited_invariants = {
                "workflow_phase": "SINGLE_RESTYLE",
                "automatic_retry_count": 0,
                "automatic_retry_allowed": False,
            }
            for key, expected in limited_invariants.items():
                if receipt.get(key) != expected:
                    snapshot_errors.append(f"STAGED_RESTYLE:{key}")
            if (
                source_record.get("schema_version") != STAGED_DRAFT_RUN_RECEIPT_V1
                or receipt.get("workflow_contract") != policy["workflow_contract"]
                or source_record.get("workflow_contract") != policy["workflow_contract"]
            ):
                snapshot_errors.append("STAGED_RESTYLE:LIMITED_DEFAULT_BINDING")
    status = "PASS" if not changed and not snapshot_errors else "FAIL"
    return {
        "status": status,
        "pack_mutated": changed,
        "snapshot_errors": snapshot_errors,
        "authority_count": len(after),
    }


def _audit_v3(result: dict[str, Any], root: Path) -> dict[str, Any]:
    required_axes = (
        "STYLE_REFERENCE_FIDELITY", "STYLE_CONTENT_LEAKAGE", "SCENE_PROMPT_COMPLIANCE",
    )
    missing = []
    failed = []
    candidate = result.get("candidate", {})
    candidate_path = Path(candidate.get("path", ""))
    workspace_value = result.get("workspace_root")
    try:
        workspace = validate_workspace(root, Path(workspace_value)) if workspace_value else None
    except ZPackError:
        workspace = None
        failed.append("WORKSPACE_BOUNDARY")
    if not candidate_path.is_file():
        failed.append("CANDIDATE_FILE")
    elif sha256(candidate_path) != candidate.get("sha256"):
        failed.append("CANDIDATE_SHA")
    elif workspace is None or not _is_relative_to(candidate_path.resolve(), workspace):
        failed.append("CANDIDATE_WORKSPACE_BOUNDARY")
    for key in ("candidate_id", "run_id", "compile_sha256"):
        if not result.get(key):
            missing.append(key)
    reference_shas = result.get("reference_sha256")
    if not isinstance(reference_shas, list) or not reference_shas:
        missing.append("reference_sha256")
    receipt_relative = result.get("run_receipt_path")
    receipt = None
    if workspace is None or not receipt_relative:
        missing.append("run_receipt_path")
    else:
        receipt_path = (workspace / receipt_relative).resolve()
        if not _is_relative_to(receipt_path, workspace) or not receipt_path.is_file():
            failed.append("RUN_RECEIPT_PATH")
        elif sha256(receipt_path) != result.get("run_receipt_sha256"):
            failed.append("RUN_RECEIPT_SHA")
        else:
            receipt = load_json(receipt_path)
    if receipt is not None:
        receipt_reference_shas = []
        snapshot_paths = set()
        for item in receipt.get("snapshot_references", []):
            snapshot_relative = item.get("snapshot_path")
            snapshot_sha = item.get("snapshot_sha256")
            if not snapshot_relative or not snapshot_sha:
                failed.append("RUN_RECEIPT_SNAPSHOT_METADATA")
                continue
            snapshot_path = (workspace / snapshot_relative).resolve()
            if (
                not _is_relative_to(snapshot_path, workspace)
                or not snapshot_path.is_file()
                or sha256(snapshot_path) != snapshot_sha
                or snapshot_path in snapshot_paths
            ):
                failed.append("RUN_RECEIPT_SNAPSHOT_INTEGRITY")
                continue
            snapshot_paths.add(snapshot_path)
            receipt_reference_shas.append(snapshot_sha)
        if receipt.get("run_id") != result.get("run_id"):
            failed.append("RUN_RECEIPT_RUN_ID")
        if receipt.get("compile_sha256") != result.get("compile_sha256"):
            failed.append("RUN_RECEIPT_COMPILE_SHA")
        if Path(receipt.get("workspace_root", "")).resolve() != workspace:
            failed.append("RUN_RECEIPT_WORKSPACE")
        if reference_shas != receipt_reference_shas:
            failed.append("RUN_RECEIPT_REFERENCE_SHA")
        if receipt.get("prior_candidate_used") is not False:
            failed.append("PRIOR_CANDIDATE_INPUT_FORBIDDEN")
        if candidate.get("sha256") in set(receipt_reference_shas):
            failed.append("PRIOR_CANDIDATE_INPUT_FORBIDDEN")
    checks = result.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    for axis in required_axes:
        record = checks.get(axis)
        if not isinstance(record, dict) or record.get("verdict") not in AUDIT_VERDICTS:
            missing.append(axis)
            continue
        if record["verdict"] == "FAIL":
            failed.append(axis)
        elif record["verdict"] == "HOLD":
            missing.append(axis)
        if not record.get("observation"):
            missing.append(axis + ":OBSERVATION")
    review = result.get("owner_review", {})
    if not review.get("id") or review.get("verdict") not in AUDIT_VERDICTS:
        missing.append("OWNER_REVIEW")
    elif review["verdict"] == "FAIL":
        failed.append("OWNER_REVIEW")
    elif review["verdict"] == "HOLD":
        missing.append("OWNER_REVIEW")
    status = "PASS" if not missing and not failed else "HOLD"
    return {"status": status, "missing": sorted(set(missing)), "failed": sorted(set(failed))}


def _audit_staged_restyle(result: dict[str, Any], root: Path) -> dict[str, Any]:
    """Audit style transfer and structure preservation as independent terminal axes."""
    policy = _staged_restyle_policy(root)
    required_axes = policy["required_audit_axes"]
    missing: list[str] = []
    failed: list[str] = []
    workspace_value = result.get("workspace_root")
    try:
        workspace = validate_workspace(root, Path(workspace_value)) if workspace_value else None
    except ZPackError:
        workspace = None
        failed.append("WORKSPACE_BOUNDARY")
    candidate = result.get("candidate", {})
    candidate_path = Path(candidate.get("path", ""))
    if not candidate_path.is_file():
        failed.append("CANDIDATE_FILE")
    elif sha256(candidate_path) != candidate.get("sha256"):
        failed.append("CANDIDATE_SHA")
    elif candidate_path.suffix.casefold() not in IMAGE_SUFFIXES or candidate_path.stat().st_size == 0:
        failed.append("CANDIDATE_IMAGE")
    elif workspace is None or not _is_relative_to(
        candidate_path.resolve(), (workspace / "candidates").resolve()
    ):
        failed.append("CANDIDATE_WORKSPACE_BOUNDARY")
    for key in ("candidate_id", "run_id", "compile_sha256"):
        if not result.get(key):
            missing.append(key)
    reference_shas = result.get("reference_sha256")
    if not isinstance(reference_shas, list) or len(reference_shas) != 2:
        missing.append("reference_sha256")
    receipt = None
    receipt_relative = result.get("run_receipt_path")
    if workspace is None or not isinstance(receipt_relative, str):
        missing.append("run_receipt_path")
    else:
        receipt_path = (workspace / receipt_relative).resolve()
        if receipt_path != workspace / "run-receipt.json" or not receipt_path.is_file():
            failed.append("RUN_RECEIPT_PATH")
        elif sha256(receipt_path) != result.get("run_receipt_sha256"):
            failed.append("RUN_RECEIPT_SHA")
        else:
            receipt = load_json(receipt_path)
    if receipt is not None:
        if receipt.get("schema_version") != STAGED_RESTYLE_RUN_RECEIPT_V1:
            failed.append("STAGED_RESTYLE_RUN_RECEIPT_SCHEMA")
        if receipt.get("run_id") != result.get("run_id"):
            failed.append("RUN_RECEIPT_RUN_ID")
        if receipt.get("compile_sha256") != result.get("compile_sha256"):
            failed.append("RUN_RECEIPT_COMPILE_SHA")
        if Path(receipt.get("workspace_root", "")).resolve() != workspace:
            failed.append("RUN_RECEIPT_WORKSPACE")
        references = receipt.get("snapshot_references", [])
        roles = [item.get("role") for item in references]
        receipt_reference_shas = [item.get("snapshot_sha256") for item in references]
        if roles != ["structure_edit_target", "style_core"]:
            failed.append("STAGED_RESTYLE_REFERENCE_ROLES")
        if len(references) == 2:
            _, sources = _style_sources(root)
            core_reference = references[1]
            core = sources.get(core_reference.get("id"))
            if (
                core_reference.get("id") not in policy["allowed_style_core_ids"]
                or core is None
                or core_reference.get("snapshot_sha256") != core.get("sha256")
            ):
                failed.append("STAGED_RESTYLE_CORE_BINDING")
        if reference_shas != receipt_reference_shas:
            failed.append("RUN_RECEIPT_REFERENCE_SHA")
        for item in references:
            snapshot = (workspace / item.get("snapshot_path", "")).resolve()
            if (
                not _is_relative_to(snapshot, workspace)
                or not snapshot.is_file()
                or sha256(snapshot) != item.get("snapshot_sha256")
            ):
                failed.append("RUN_RECEIPT_SNAPSHOT_INTEGRITY")
        invariants = {
            "prior_candidate_used": True,
            "prior_candidate_scope": "STRUCTURE_EDIT_TARGET_ONLY",
            "generated_candidate_input_used": True,
            "style_adapter_used": False,
            "restyle_depth": 1,
            "maximum_restyle_depth": 1,
            "recursive_restyle_allowed": False,
        }
        for key, expected in invariants.items():
            if receipt.get(key) != expected:
                failed.append("STAGED_RESTYLE_BOUNDARY")
        if candidate.get("sha256") in set(receipt_reference_shas):
            failed.append("RESTYLE_OUTPUT_MUST_BE_NEW")
        source_binding = receipt.get("source_generation_binding", {})
        if len(references) == 2 and source_binding.get("candidate_sha256") != references[0].get("snapshot_sha256"):
            failed.append("STRUCTURE_EDIT_TARGET_BINDING")
        source_receipt_snapshot = (workspace / source_binding.get("snapshot_path", "")).resolve()
        if (
            not _is_relative_to(source_receipt_snapshot, workspace)
            or not source_receipt_snapshot.is_file()
            or sha256(source_receipt_snapshot) != source_binding.get("snapshot_sha256")
            or source_binding.get("snapshot_sha256") != source_binding.get("receipt_sha256")
        ):
            failed.append("SOURCE_RUN_RECEIPT_INTEGRITY")
        else:
            source_receipt = load_json(source_receipt_snapshot)
            if (
                source_receipt.get("schema_version") not in FRESH_RUN_RECEIPT_SCHEMAS
                or source_receipt.get("prior_candidate_used") is not False
            ):
                failed.append("RECURSIVE_RESTYLE_FORBIDDEN")
    checks = result.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    for axis in required_axes:
        record = checks.get(axis)
        if not isinstance(record, dict) or record.get("verdict") not in AUDIT_VERDICTS:
            missing.append(axis)
            continue
        if record["verdict"] == "FAIL":
            failed.append(axis)
        elif record["verdict"] == "HOLD":
            missing.append(axis)
        if not record.get("observation"):
            missing.append(axis + ":OBSERVATION")
    review = result.get("owner_review", {})
    if not review.get("id") or review.get("verdict") not in AUDIT_VERDICTS:
        missing.append("OWNER_REVIEW")
    elif review["verdict"] == "FAIL":
        failed.append("OWNER_REVIEW")
    elif review["verdict"] == "HOLD":
        missing.append("OWNER_REVIEW")
    status = "PASS" if not missing and not failed else "HOLD"
    return {"status": status, "missing": sorted(set(missing)), "failed": sorted(set(failed))}


def audit_result(result: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    """Validate evidence-bound terminal audit data; never infer a visual PASS."""
    if root is None:
        root = pack_root(Path(__file__))
    if result.get("schema_version") == STAGED_RESTYLE_AUDIT_V1:
        return _audit_staged_restyle(result, root)
    if result.get("schema_version") == AUDIT_EVIDENCE_V3:
        return _audit_v3(result, root)
    if result.get("schema_version") != "ZPACK_AUDIT_EVIDENCE_v2.0":
        return {
            "status": "HOLD",
            "missing": ["AUDIT_SCHEMA_V2_V3_OR_STAGED_RESTYLE_V1"],
            "failed": [],
            "owner_axis_verdicts": {},
        }
    candidate = result.get("candidate", {})
    candidate_path = Path(candidate.get("path", ""))
    bindings = result.get("bindings", {})
    binding_missing = [
        key for key in ("compile_sha256", "selection_sha256", "authorities")
        if not bindings.get(key)
    ]
    integrity_failures = []
    if not candidate_path.is_file():
        integrity_failures.append("CANDIDATE_FILE")
    elif sha256(candidate_path) != candidate.get("sha256"):
        integrity_failures.append("CANDIDATE_SHA")
    workspace_value = result.get("workspace_root")
    workspace = Path(workspace_value).resolve() if workspace_value else None
    if workspace is None:
        binding_missing.append("workspace_root")
    else:
        try:
            validate_workspace(root, workspace)
        except ZPackError:
            integrity_failures.append("WORKSPACE_BOUNDARY")
    records = result.get("checks", [])
    if not isinstance(records, list):
        records = []
    indexed = {record.get("check_id"): record for record in records if isinstance(record, dict)}
    missing = [check for check in required_audit_checks(root) if check not in indexed]
    failed = []
    evidence_failures = []
    for check_id in required_audit_checks(root):
        record = indexed.get(check_id)
        if not record:
            continue
        verdict = record.get("verdict")
        if verdict == "FAIL":
            failed.append(check_id)
        elif verdict != "PASS":
            missing.append(check_id)
        if not record.get("observation") or not record.get("confidence") or not record.get("reviewer"):
            evidence_failures.append(f"{check_id}:METADATA")
        evidence = record.get("evidence_path")
        if not evidence or workspace is None:
            evidence_failures.append(f"{check_id}:EVIDENCE")
            continue
        evidence_path = (workspace / evidence).resolve()
        if not _is_relative_to(evidence_path, workspace) or not evidence_path.is_file():
            evidence_failures.append(f"{check_id}:EVIDENCE_PATH")
        elif sha256(evidence_path) != record.get("evidence_sha256"):
            evidence_failures.append(f"{check_id}:EVIDENCE_SHA")
    owner = result.get("owner_axis_verdicts", {})
    owner_missing = [axis for axis in OWNER_AXIS_VERDICTS if owner.get(axis) not in {"PASS", "FAIL", "HOLD"}]
    owner_failed = [axis for axis in OWNER_AXIS_VERDICTS if owner.get(axis) == "FAIL"]
    owner_hold = [axis for axis in OWNER_AXIS_VERDICTS if owner.get(axis) == "HOLD"]
    all_missing = sorted(set([*missing, *binding_missing, *owner_missing, *evidence_failures]))
    all_failed = sorted(set([*failed, *integrity_failures, *owner_failed]))
    status = "PASS" if not all_missing and not all_failed and not owner_hold else "HOLD"
    return {
        "status": status,
        "missing": all_missing,
        "failed": all_failed,
        "owner_holds": owner_hold,
        "owner_axis_verdicts": owner,
    }


ASSET_ROLES = {
    "character": "APPROVED_CHARACTER_SOURCE",
    "proportion": "APPROVED_PROPORTION_SOURCE",
    "item": "APPROVED_ITEM_SOURCE",
    "pose": "APPROVED_POSE_CONTROL",
}


def _validate_asset_id(asset_id: str) -> None:
    if not asset_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in asset_id):
        raise ZPackError("invalid asset id")


def add_asset(root: Path, source: Path, asset_id: str, role: str) -> dict[str, Any]:
    """Copy a candidate into the non-authoritative inbox for review."""
    _validate_asset_id(asset_id)
    if role not in ASSET_ROLES:
        raise ZPackError(f"unsupported asset role: {role}")
    if not source.is_file():
        raise ZPackError(f"source file not found: {source}")
    destination = root / "private-assets/inbox" / f"{asset_id}{source.suffix.lower()}"
    if destination.exists() and sha256(destination) != sha256(source):
        raise ZPackError("ASSET_ID_COLLISION")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(source, destination)
    return {
        "status": "PENDING_REVIEW",
        "asset_id": asset_id,
        "requested_role": role,
        "path": destination.relative_to(root).as_posix(),
        "sha256": sha256(destination),
        "generation_authority": False,
    }


def analyze_asset(source: Path, asset_id: str, role: str) -> dict[str, Any]:
    _validate_asset_id(asset_id)
    if role not in ASSET_ROLES:
        raise ZPackError(f"unsupported asset role: {role}")
    if not source.is_file():
        raise ZPackError(f"source file not found: {source}")
    return {
        "schema_version": "ZPACK_ASSET_ANALYSIS_v1.0",
        "asset_id": asset_id,
        "requested_role": role,
        "source_path": str(source.resolve()),
        "source_sha256": sha256(source),
        "bytes": source.stat().st_size,
        "facts": {
            "identity": "NOT_OBSERVED",
            "proportion": "NOT_OBSERVED",
            "item_geometry": "NOT_OBSERVED",
            "pose": "NOT_OBSERVED",
        },
        "owner_approval": "PENDING",
    }


def approve_asset(root: Path, analysis: dict[str, Any], owner_verdict: str) -> dict[str, Any]:
    if owner_verdict != "PASS":
        raise ZPackError("OWNER_APPROVAL_HOLD")
    role = analysis["requested_role"]
    if role not in ASSET_ROLES:
        raise ZPackError(f"unsupported asset role: {role}")
    source = Path(analysis["source_path"])
    if not source.is_file() or sha256(source) != analysis["source_sha256"]:
        raise ZPackError("SOURCE_SHA_MISMATCH")
    asset_id = analysis["asset_id"]
    _validate_asset_id(asset_id)
    suffix = source.suffix.lower()
    destination = root / "private-assets" / (role + "s") / f"{asset_id}{suffix}"
    if destination.exists() and sha256(destination) != analysis["source_sha256"]:
        raise ZPackError("ASSET_ID_COLLISION")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(source, destination)
    record = {
        "id": asset_id,
        "path": destination.relative_to(root).as_posix(),
        "role": ASSET_ROLES[role],
        "sha256": analysis["source_sha256"],
        "rights_holder": "PROJECT_OWNER",
        "license": "LOCAL_ONLY",
        "redistribution_permission": False,
        "derivative_permission": "PRIVATE_ONLY",
        "publication_status": "LOCAL_UNTRACKED_ONLY",
        "metadata_review": "LOCAL_REVIEW_REQUIRED",
    }
    manifest_path = root / "private-assets/PRIVATE_ASSET_MANIFEST.json"
    manifest = load_json(manifest_path)
    assets = [item for item in manifest["assets"] if item["id"] != asset_id]
    assets.append(record)
    manifest["assets"] = sorted(assets, key=lambda item: item["id"])
    write_json(manifest_path, manifest)
    return {"status": "PASS", "asset": record, "owner_verdict": owner_verdict}


def add_style_source(
    root: Path, source: Path, source_id: str, style_role: str,
    original_source_attested: bool = False,
) -> dict[str, Any]:
    """Copy a style sample to a non-authoritative inbox."""
    _validate_asset_id(source_id)
    if style_role not in {"primary", "support"}:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    if not original_source_attested:
        raise ZPackError("ORIGINAL_STYLE_SOURCE_ATTESTATION_REQUIRED")
    if not source.is_file():
        raise ZPackError(f"source file not found: {source}")
    forbidden_parts = {"candidates", "evidence", "output", "edit-targets", "patches"}
    if forbidden_parts.intersection(part.casefold() for part in source.resolve().parts):
        raise ZPackError("CANDIDATE_OR_EVIDENCE_STYLE_SOURCE_FORBIDDEN")
    _, by_id = _style_sources(root)
    if source_id in by_id:
        raise ZPackError("STYLE_SOURCE_ID_COLLISION")
    destination = root / "pack/styles/default/inbox" / f"{source_id}{source.suffix.lower()}"
    if destination.exists() and sha256(destination) != sha256(source):
        raise ZPackError("STYLE_SOURCE_ID_COLLISION")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(source, destination)
    receipt = {
        "schema_version": "ZPACK_STYLE_SOURCE_ADD_v1.0",
        "status": "INBOX",
        "source_id": source_id,
        "style_role": style_role,
        "path": destination.relative_to(root).as_posix(),
        "sha256": sha256(destination),
        "benchmark_reference_eligible": False,
        "generation_reference_eligible": False,
        "original_source_attested": True,
    }
    receipt["receipt_sha256"] = canonical_sha(receipt)
    receipt_path = destination.with_suffix(destination.suffix + ".receipt.json")
    write_json(receipt_path, receipt)
    return {**receipt, "receipt_path": receipt_path.relative_to(root).as_posix()}


def analyze_style_source(
    root: Path, source: Path, source_id: str, style_role: str, family_id: str,
    allowed_domains: list[str],
) -> dict[str, Any]:
    _validate_asset_id(source_id)
    _validate_asset_id(family_id)
    if style_role not in {"primary", "support"}:
        raise ZPackError("STYLE_SOURCE_INELIGIBLE")
    if not source.is_file():
        raise ZPackError(f"source file not found: {source}")
    style_inbox = (root / "pack/styles/default/inbox").resolve()
    if not _is_relative_to(source.resolve(), style_inbox):
        raise ZPackError("STYLE_SOURCE_NOT_IN_INBOX")
    receipt_path = source.with_suffix(source.suffix + ".receipt.json")
    if not receipt_path.is_file():
        raise ZPackError("ORIGINAL_STYLE_SOURCE_ATTESTATION_REQUIRED")
    receipt = load_json(receipt_path)
    receipt_sha = receipt.get("receipt_sha256")
    unsigned_receipt = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if (
        receipt_sha != canonical_sha(unsigned_receipt)
        or receipt.get("original_source_attested") is not True
        or receipt.get("source_id") != source_id
        or receipt.get("style_role") != style_role
        or receipt.get("sha256") != sha256(source)
    ):
        raise ZPackError("ORIGINAL_STYLE_SOURCE_ATTESTATION_REQUIRED")
    domains = sorted(set(allowed_domains))
    if style_role == "primary" and domains:
        raise ZPackError("PRIMARY_ALLOWED_DOMAINS_MUST_BE_EMPTY")
    if style_role == "support" and not domains:
        raise ZPackError("SUPPORT_ALLOWED_DOMAINS_REQUIRED")
    return {
        "schema_version": "ZPACK_STYLE_SOURCE_ANALYSIS_v1.0",
        "status": "ANALYZED",
        "source_id": source_id,
        "source_path": str(source.resolve()),
        "source_sha256": sha256(source),
        "add_receipt_path": str(receipt_path.resolve()),
        "add_receipt_sha256": receipt_sha,
        "style_role": style_role,
        "family_id": family_id,
        "allowed_domains": domains,
        "forbidden_content_signatures": [],
        "owner_verdict": "PENDING",
    }


def approve_style_source(root: Path, analysis: dict[str, Any], owner_verdict: str) -> dict[str, Any]:
    if analysis.get("schema_version") != "ZPACK_STYLE_SOURCE_ANALYSIS_v1.0":
        raise ZPackError("STYLE_ANALYSIS_SCHEMA_REQUIRED")
    if owner_verdict != "PASS":
        raise ZPackError("OWNER_APPROVAL_HOLD")
    source = Path(analysis["source_path"])
    if not source.is_file() or sha256(source) != analysis["source_sha256"]:
        raise ZPackError("SOURCE_SHA_MISMATCH")
    style_inbox = (root / "pack/styles/default/inbox").resolve()
    if not _is_relative_to(source.resolve(), style_inbox):
        raise ZPackError("STYLE_SOURCE_NOT_IN_INBOX")
    receipt_path = Path(analysis.get("add_receipt_path", ""))
    if not receipt_path.is_file() or not _is_relative_to(receipt_path.resolve(), style_inbox):
        raise ZPackError("ORIGINAL_STYLE_SOURCE_ATTESTATION_REQUIRED")
    add_receipt = load_json(receipt_path)
    unsigned_receipt = {key: value for key, value in add_receipt.items() if key != "receipt_sha256"}
    if (
        add_receipt.get("receipt_sha256") != canonical_sha(unsigned_receipt)
        or add_receipt.get("receipt_sha256") != analysis.get("add_receipt_sha256")
        or add_receipt.get("original_source_attested") is not True
        or add_receipt.get("sha256") != analysis["source_sha256"]
    ):
        raise ZPackError("ORIGINAL_STYLE_SOURCE_ATTESTATION_REQUIRED")
    source_id = analysis["source_id"]
    style_role = analysis["style_role"]
    _validate_asset_id(source_id)
    destination = root / "pack/styles/default/sources" / style_role / f"{source_id}{source.suffix.lower()}"
    if destination.exists() and sha256(destination) != analysis["source_sha256"]:
        raise ZPackError("STYLE_SOURCE_ID_COLLISION")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(source, destination)
    approval_receipt = {
        "source_id": source_id,
        "source_sha256": analysis["source_sha256"],
        "analysis_sha256": canonical_sha(analysis),
        "owner_verdict": owner_verdict,
    }
    record = {
        "id": source_id,
        "path": destination.relative_to(root).as_posix(),
        "role": style_role,
        "style_role": style_role,
        "family_id": analysis["family_id"],
        "allowed_domains": analysis["allowed_domains"],
        "forbidden_content_signatures": analysis.get("forbidden_content_signatures", []),
        "sha256": analysis["source_sha256"],
        "lifecycle_status": "PENDING_FIDELITY",
        "benchmark_reference_eligible": True,
        "generation_reference_eligible": False,
        "owner_verdict_receipt_sha": canonical_sha(approval_receipt),
        "benchmark_report_sha": None,
        "promoted_at": None,
        "publication_status": "LOCAL_UNTRACKED_ONLY",
    }
    manifest_path = root / "pack/styles/default/STYLE_SOURCE_MANIFEST.json"
    manifest = load_json(manifest_path)
    if any(item["id"] == source_id for item in manifest["sources"]):
        raise ZPackError("STYLE_SOURCE_ID_COLLISION")
    manifest["sources"] = sorted([*manifest["sources"], record], key=lambda item: item["id"])
    manifest["source_count"] = len(manifest["sources"])
    write_json(manifest_path, manifest)
    return {"status": "PENDING_FIDELITY", "source": record, "owner_verdict": owner_verdict}


def create_scene(workspace: Path, scene_id: str) -> dict[str, Any]:
    if not scene_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in scene_id):
        raise ZPackError("invalid scene id")
    scene_root = workspace.resolve() / scene_id
    if scene_root.exists():
        raise ZPackError("scene already exists")
    scene_root.mkdir(parents=True)
    request = {
        "schema_version": STYLE_REQUEST_V3,
        "style_primary_id": "REPLACE_WITH_PROMOTED_STYLE_ID",
        "scene": "Describe the requested scene.",
        "style_domains": [],
        "required_authorities": [],
        "prior_candidate": False,
        "edit_target": False,
        "patch": False,
        "layer_composite": False,
    }
    write_json(scene_root / "request.json", request)
    return {"status": "PASS", "scene_id": scene_id, "request": str(scene_root / "request.json")}


def register_result(root: Path, registration: dict[str, Any]) -> dict[str, Any]:
    candidate = Path(registration.get("candidate_path", ""))
    if not candidate.is_file():
        raise ZPackError("candidate file not found")
    resolved_candidate = candidate.resolve()
    if resolved_candidate == root.resolve() or _is_relative_to(resolved_candidate, root.resolve()):
        raise ZPackError("CANDIDATE_INSIDE_PACK_FORBIDDEN")
    if registration.get("used_as_generation_input"):
        raise ZPackError("PRIOR_CANDIDATE_INPUT_FORBIDDEN")
    result = {
        "schema_version": "ZPACK_RESULT_REGISTRATION_v1.0",
        "run_id": registration.get("run_id"),
        "candidate_path": str(resolved_candidate),
        "candidate_sha256": sha256(candidate),
        "compile_sha256": registration.get("compile_sha256"),
        "operator_attestation_sha256": registration.get("operator_attestation_sha256"),
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "candidate_role": "COMPARISON_AND_AUDIT_ONLY",
        "generation_authority": False,
    }
    if not result["run_id"] or not result["compile_sha256"] or not result["operator_attestation_sha256"]:
        raise ZPackError("registration binding missing")
    return result


def retry_request(request: dict[str, Any], failed_checks: list[str]) -> dict[str, Any]:
    if len(failed_checks) != 1:
        raise ZPackError("retry requires exactly one failed check axis")
    known = set(SCENE_AUDIT_CHECKS) | {
        "STYLE_EDGE_DETAIL", "STYLE_SHADING_GRAMMAR", "STYLE_COLOR_VALUE",
        "STYLE_SKIN_RENDERING", "STYLE_HAIR_RENDERING", "STYLE_FABRIC_RENDERING",
        "STYLE_BACKGROUND_RENDERING", "STYLE_FULL_FRAME_COHERENCE", "STYLE_GPT_DEFAULT_BIAS",
        "BODY_HEAD_SHOULDER_RATIO", "BODY_TORSO_PELVIS_CONNECTION", "BODY_ARM_HAND_CHAIN",
        "BODY_LEG_FOOT_CHAIN", "BODY_SEATED_CONTACT", "OBJECT_RELATIVE_SCALE",
        "PERSPECTIVE_FORESHORTENING",
    }
    if failed_checks[0] not in known:
        raise ZPackError("unknown failed check axis")
    retried = json.loads(json.dumps(request))
    retried["retry_failed_check"] = failed_checks[0]
    retried["prior_candidate"] = False
    retried["edit_target"] = False
    retried["patch"] = False
    retried["layer_composite"] = False
    retried["correction_mode"] = "RECOMPILE_FROM_APPROVED_AUTHORITIES"
    return retried
