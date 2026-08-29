"""Z-Pack command-line interface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    ZPackError, add_asset, add_style_source, analyze_asset, analyze_style_source,
    approve_asset, approve_style_source, audit_result, compile_request,
    compile_restyle_request, compile_staged_draft_request, continue_style_workflow,
    create_restyle_request, create_scene, managed_workspace_root,
    load_json, pack_root, prepare_restyle_run, prepare_run, prepare_staged_draft_run,
    register_result, retry_request, select_references, validate,
    style_workflow_policy, validate_output_path, verify_run_integrity,
)


def write(value: object, output: Path | None, root: Path | None = None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if output:
        if root is not None:
            validate_output_path(root, output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")


def main() -> None:
    parser = argparse.ArgumentParser(prog="zpack")
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="command")
    init = sub.add_parser("init")
    init.add_argument("workspace", type=Path, nargs="?")
    sub.add_parser("doctor")
    for name in ("select", "compile", "audit"):
        item = sub.add_parser(name)
        item.add_argument("request", type=Path)
        item.add_argument("--output", type=Path)
    asset = sub.add_parser("asset")
    asset_sub = asset.add_subparsers(dest="asset_command", required=True)
    add = asset_sub.add_parser("add")
    add.add_argument("source", type=Path)
    add.add_argument("--id", required=True)
    add.add_argument("--role", required=True, choices=("character", "proportion", "item", "pose"))
    add.add_argument("--output", type=Path)
    analyze = asset_sub.add_parser("analyze")
    analyze.add_argument("source", type=Path)
    analyze.add_argument("--id", required=True)
    analyze.add_argument("--role", required=True, choices=("character", "proportion", "item", "pose"))
    analyze.add_argument("--output", type=Path, required=True)
    approve = asset_sub.add_parser("approve")
    approve.add_argument("analysis", type=Path)
    approve.add_argument("--owner-verdict", required=True, choices=("PASS", "FAIL", "HOLD"))
    approve.add_argument("--output", type=Path)
    asset_validate = asset_sub.add_parser("validate")
    asset_validate.add_argument("--id")
    scene = sub.add_parser("scene")
    scene_sub = scene.add_subparsers(dest="scene_command", required=True)
    create = scene_sub.add_parser("create")
    create.add_argument("workspace", type=Path)
    create.add_argument("--id", required=True)
    style = sub.add_parser("style")
    style_sub = style.add_subparsers(dest="style_command", required=True)
    style_add = style_sub.add_parser("add")
    style_add.add_argument("source", type=Path)
    style_add.add_argument("--id", required=True)
    style_add.add_argument("--role", required=True, choices=("primary", "support"))
    style_add.add_argument("--original-source-attestation", action="store_true", required=True)
    style_add.add_argument("--output", type=Path)
    style_analyze = style_sub.add_parser("analyze")
    style_analyze.add_argument("source", type=Path)
    style_analyze.add_argument("--id", required=True)
    style_analyze.add_argument("--role", required=True, choices=("primary", "support"))
    style_analyze.add_argument("--family", required=True)
    style_analyze.add_argument("--domain", action="append", default=[])
    style_analyze.add_argument("--output", type=Path, required=True)
    style_approve = style_sub.add_parser("approve")
    style_approve.add_argument("analysis", type=Path)
    style_approve.add_argument("--owner-verdict", required=True, choices=("PASS", "FAIL", "HOLD"))
    style_approve.add_argument("--output", type=Path)
    references = sub.add_parser("references")
    references_sub = references.add_subparsers(dest="references_command", required=True)
    reference_select = references_sub.add_parser("select")
    reference_select.add_argument("request", type=Path)
    reference_select.add_argument("--output", type=Path)
    register = sub.add_parser("register")
    register.add_argument("registration", type=Path)
    register.add_argument("--output", type=Path)
    retry = sub.add_parser("retry")
    retry.add_argument("request", type=Path)
    retry.add_argument("--failed-check", required=True)
    retry.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run")
    run_sub = run.add_subparsers(dest="run_command", required=True)
    prepare = run_sub.add_parser("prepare")
    prepare.add_argument("request", type=Path)
    prepare.add_argument("--id", required=True)
    prepare.add_argument("--workspace", type=Path)
    verify = run_sub.add_parser("verify")
    verify.add_argument("run_root", type=Path)
    restyle = sub.add_parser("restyle")
    restyle_sub = restyle.add_subparsers(dest="restyle_command", required=True)
    restyle_create = restyle_sub.add_parser("create")
    restyle_create.add_argument("candidate", type=Path)
    restyle_create.add_argument("--source-run", type=Path, required=True)
    restyle_create.add_argument("--style-core", required=True)
    restyle_create.add_argument("--preserve", action="append", default=[])
    restyle_create.add_argument("--output", type=Path, required=True)
    restyle_compile = restyle_sub.add_parser("compile")
    restyle_compile.add_argument("request", type=Path)
    restyle_compile.add_argument("--output", type=Path)
    restyle_prepare = restyle_sub.add_parser("prepare")
    restyle_prepare.add_argument("request", type=Path)
    restyle_prepare.add_argument("--id", required=True)
    restyle_prepare.add_argument("--workspace", type=Path)
    restyle_audit = restyle_sub.add_parser("audit")
    restyle_audit.add_argument("evidence", type=Path)
    restyle_audit.add_argument("--output", type=Path)
    workflow = sub.add_parser("workflow")
    workflow_sub = workflow.add_subparsers(dest="workflow_command", required=True)
    workflow_sub.add_parser("policy")
    workflow_compile = workflow_sub.add_parser("compile")
    workflow_compile.add_argument("request", type=Path)
    workflow_compile.add_argument("--output", type=Path)
    workflow_start = workflow_sub.add_parser("start")
    workflow_start.add_argument("request", type=Path)
    workflow_start.add_argument("--id", required=True)
    workflow_start.add_argument("--workspace", type=Path)
    workflow_continue = workflow_sub.add_parser("continue")
    workflow_continue.add_argument("candidate", type=Path)
    workflow_continue.add_argument("--source-run", type=Path, required=True)
    workflow_continue.add_argument("--id", required=True)
    workflow_continue.add_argument("--workspace", type=Path)
    workflow_continue.add_argument("--preserve", action="append", default=[])
    args = parser.parse_args()
    if args.version:
        print("Z-Pack / ZPACK / ZPACK_v1.2.0")
        return
    try:
        if args.command == "init":
            root = pack_root()
            workspace = managed_workspace_root(root, args.workspace)
            workspace.mkdir(parents=True, exist_ok=True)
            write({"status": "PASS", "workspace": str(workspace)}, None)
            return
        root = pack_root()
        if args.command == "doctor":
            write(validate(root), None)
        elif args.command == "select":
            write(select_references(root, load_json(args.request)), args.output, root)
        elif args.command == "compile":
            write(compile_request(root, load_json(args.request)), args.output, root)
        elif args.command == "audit":
            write(audit_result(load_json(args.request), root), args.output, root)
        elif args.command == "asset" and args.asset_command == "add":
            write(add_asset(root, args.source, args.id, args.role), args.output)
        elif args.command == "asset" and args.asset_command == "analyze":
            write(analyze_asset(args.source, args.id, args.role), args.output)
        elif args.command == "asset" and args.asset_command == "approve":
            write(approve_asset(root, load_json(args.analysis), args.owner_verdict), args.output)
        elif args.command == "asset" and args.asset_command == "validate":
            result = validate(root)
            if args.id:
                assets = load_json(root / "private-assets/PRIVATE_ASSET_MANIFEST.json")["assets"]
                if args.id not in {item["id"] for item in assets}:
                    raise ZPackError(f"approved asset not found: {args.id}")
                result["asset_id"] = args.id
            write(result, None)
        elif args.command == "scene" and args.scene_command == "create":
            write(create_scene(managed_workspace_root(root, args.workspace), args.id), None)
        elif args.command == "style" and args.style_command == "add":
            write(
                add_style_source(root, args.source, args.id, args.role, args.original_source_attestation),
                args.output, root,
            )
        elif args.command == "style" and args.style_command == "analyze":
            write(
                analyze_style_source(root, args.source, args.id, args.role, args.family, args.domain),
                args.output, root,
            )
        elif args.command == "style" and args.style_command == "approve":
            write(approve_style_source(root, load_json(args.analysis), args.owner_verdict), args.output, root)
        elif args.command == "references" and args.references_command == "select":
            write(select_references(root, load_json(args.request)), args.output, root)
        elif args.command == "register":
            write(register_result(root, load_json(args.registration)), args.output, root)
        elif args.command == "retry":
            write(retry_request(load_json(args.request), [args.failed_check]), args.output, root)
        elif args.command == "run" and args.run_command == "prepare":
            workspace = managed_workspace_root(root, args.workspace)
            write(prepare_run(root, workspace, args.id, load_json(args.request)), None)
        elif args.command == "run" and args.run_command == "verify":
            write(verify_run_integrity(root, args.run_root), None)
        elif args.command == "restyle" and args.restyle_command == "create":
            write(
                create_restyle_request(
                    root, args.candidate, args.source_run, args.style_core, args.preserve,
                ),
                args.output,
                root,
            )
        elif args.command == "restyle" and args.restyle_command == "compile":
            write(compile_restyle_request(root, load_json(args.request)), args.output, root)
        elif args.command == "restyle" and args.restyle_command == "prepare":
            workspace = managed_workspace_root(root, args.workspace)
            write(prepare_restyle_run(root, workspace, args.id, load_json(args.request)), None)
        elif args.command == "restyle" and args.restyle_command == "audit":
            write(audit_result(load_json(args.evidence), root), args.output, root)
        elif args.command == "workflow" and args.workflow_command == "policy":
            write(style_workflow_policy(root), None)
        elif args.command == "workflow" and args.workflow_command == "compile":
            write(compile_staged_draft_request(root, load_json(args.request)), args.output, root)
        elif args.command == "workflow" and args.workflow_command == "start":
            workspace = managed_workspace_root(root, args.workspace)
            write(prepare_staged_draft_run(root, workspace, args.id, load_json(args.request)), None)
        elif args.command == "workflow" and args.workflow_command == "continue":
            workspace = managed_workspace_root(root, args.workspace)
            write(
                continue_style_workflow(
                    root, workspace, args.id, args.candidate, args.source_run, args.preserve,
                ),
                None,
            )
        else:
            parser.print_help()
    except ZPackError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
