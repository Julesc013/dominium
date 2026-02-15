#!/usr/bin/env python3
"""Deterministic developer acceleration CLI."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.dev.impact_graph import (  # noqa: E402
    build_graph_and_write,
    compute_impacted_sets,
    detect_changed_files,
)


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _resolve_changed(repo_root: str, changed_files: str, base_ref: str):
    if str(changed_files).strip():
        out = sorted(set(token.strip().replace("\\", "/") for token in changed_files.split(",") if token.strip()))
        return {"result": "complete", "changed_files": out}
    return detect_changed_files(repo_root=repo_root, base_ref=base_ref)


def _print(payload: Dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _run_proc(repo_root: str, argv: List[str]) -> Dict[str, object]:
    proc = subprocess.run(
        argv,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )
    return {
        "exit_code": int(proc.returncode),
        "output": str(proc.stdout or ""),
        "argv": list(argv),
    }


def _run_json_proc(repo_root: str, argv: List[str]) -> Dict[str, object]:
    executed = _run_proc(repo_root=repo_root, argv=argv)
    output = str(executed.get("output", ""))
    payload = {}
    err = ""
    try:
        payload = json.loads(output) if output.strip() else {}
    except ValueError:
        err = "invalid json output"
    executed["payload"] = payload if isinstance(payload, dict) else {}
    executed["json_error"] = err
    return executed


def _cmd_impact_graph(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    changed = _resolve_changed(repo_root=repo_root, changed_files=args.changed_files, base_ref=args.base_ref)
    if changed.get("result") != "complete":
        _print(changed)
        return 2
    built = build_graph_and_write(
        repo_root=repo_root,
        changed_files=list(changed.get("changed_files") or []),
        out_path=str(args.out),
    )
    payload = {
        "result": "complete",
        "graph_path": built.get("graph_path"),
        "graph_hash": built.get("graph_hash"),
        "node_count": built.get("node_count"),
        "edge_count": built.get("edge_count"),
        "changed_files": list(changed.get("changed_files") or []),
    }
    _print(payload)
    return 0


def _impacted(repo_root: str, changed_files: List[str], out_path: str) -> Dict[str, object]:
    built = build_graph_and_write(repo_root=repo_root, changed_files=changed_files, out_path=out_path)
    payload = dict(built.get("payload") or {})
    impacted = compute_impacted_sets(graph_payload=payload, changed_files=changed_files)
    return {
        "result": "complete",
        "graph_path": built.get("graph_path"),
        "graph_hash": built.get("graph_hash"),
        "node_count": built.get("node_count"),
        "edge_count": built.get("edge_count"),
        "changed_files": changed_files,
        "impacted": impacted,
    }


def _cmd_impacted_tests(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    changed = _resolve_changed(repo_root=repo_root, changed_files=args.changed_files, base_ref=args.base_ref)
    if changed.get("result") != "complete":
        _print(changed)
        return 2
    payload = _impacted(
        repo_root=repo_root,
        changed_files=list(changed.get("changed_files") or []),
        out_path=str(args.out),
    )
    _print(
        {
            "result": "complete",
            "graph_path": payload.get("graph_path"),
            "changed_files": payload.get("changed_files"),
            "impacted_test_ids": ((payload.get("impacted") or {}).get("impacted_test_ids") or []),
            "complete_coverage": bool(((payload.get("impacted") or {}).get("complete_coverage", False))),
            "missing_changed_files": ((payload.get("impacted") or {}).get("missing_changed_files") or []),
        }
    )
    return 0


def _cmd_impacted_build_targets(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    changed = _resolve_changed(repo_root=repo_root, changed_files=args.changed_files, base_ref=args.base_ref)
    if changed.get("result") != "complete":
        _print(changed)
        return 2
    payload = _impacted(
        repo_root=repo_root,
        changed_files=list(changed.get("changed_files") or []),
        out_path=str(args.out),
    )
    _print(
        {
            "result": "complete",
            "graph_path": payload.get("graph_path"),
            "changed_files": payload.get("changed_files"),
            "impacted_build_targets": ((payload.get("impacted") or {}).get("impacted_build_targets") or []),
            "complete_coverage": bool(((payload.get("impacted") or {}).get("complete_coverage", False))),
            "missing_changed_files": ((payload.get("impacted") or {}).get("missing_changed_files") or []),
        }
    )
    return 0


def _scenario_script(target: str) -> str:
    mapping = {
        "galaxy": "tools/dev/scenarios/script.galaxy.json",
        "sol": "tools/dev/scenarios/script.sol.json",
        "earth": "tools/dev/scenarios/script.earth.json",
    }
    return mapping.get(str(target), "")


def _cmd_run(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    target = str(args.target).strip().lower()
    is_observer = target == "observer"
    save_id = "save.dev.{}".format(target)
    law_profile = "law.lab.observe_only" if is_observer else "law.lab.unrestricted"
    privilege = "observer" if is_observer else "operator"
    entitlements = (
        ["session.boot", "ui.window.lab.nav"]
        if is_observer
        else [
            "session.boot",
            "entitlement.camera_control",
            "entitlement.teleport",
            "entitlement.time_control",
            "entitlement.inspect",
            "lens.nondiegetic.access",
            "ui.window.lab.nav",
        ]
    )

    create_argv = [
        sys.executable,
        os.path.join(repo_root, "tools", "xstack", "session_create.py"),
        "--repo-root",
        repo_root,
        "--save-id",
        save_id,
        "--bundle",
        "bundle.base.lab",
        "--experience-id",
        "profile.lab.developer",
        "--law-profile-id",
        law_profile,
        "--parameter-bundle-id",
        "params.lab.placeholder",
        "--budget-policy-id",
        "policy.budget.default_lab",
        "--fidelity-policy-id",
        "policy.fidelity.default_lab",
        "--rng-seed-string",
        "seed.dev.{}".format(target),
        "--universe-seed-string",
        "seed.dev.universe.{}".format(target),
        "--privilege-level",
        privilege,
        "--compile-outputs",
        "on",
    ]
    for entitlement in entitlements:
        create_argv.extend(["--entitlement", entitlement])

    created = _run_json_proc(repo_root=repo_root, argv=create_argv)
    if int(created.get("exit_code", 1)) != 0 or str(created.get("json_error", "")):
        _print(
            {
                "result": "refused",
                "reason_code": "refusal.dev_run_create_failed",
                "message": "session_create failed for dev run target '{}'".format(target),
                "details": created,
            }
        )
        return 2

    session_spec_rel = str((created.get("payload") or {}).get("session_spec_path", "")).strip()
    if not session_spec_rel:
        _print(
            {
                "result": "refused",
                "reason_code": "refusal.dev_run_session_spec_missing",
                "message": "session_create did not return session_spec_path",
            }
        )
        return 2
    session_spec_abs = os.path.join(repo_root, session_spec_rel.replace("/", os.sep))

    booted = _run_json_proc(
        repo_root=repo_root,
        argv=[
            sys.executable,
            os.path.join(repo_root, "tools", "xstack", "session_boot.py"),
            "--repo-root",
            repo_root,
            "--bundle",
            "bundle.base.lab",
            "--compile-if-missing",
            "off",
            session_spec_abs,
        ],
    )
    if int(booted.get("exit_code", 1)) != 0 or str(booted.get("json_error", "")):
        _print(
            {
                "result": "refused",
                "reason_code": "refusal.dev_run_boot_failed",
                "message": "session_boot failed for dev run target '{}'".format(target),
                "details": booted,
            }
        )
        return 2

    script_run = {}
    if not is_observer:
        script_rel = _scenario_script(target)
        script_abs = os.path.join(repo_root, script_rel.replace("/", os.sep))
        scripted = _run_json_proc(
            repo_root=repo_root,
            argv=[
                sys.executable,
                os.path.join(repo_root, "tools", "xstack", "session_script_run.py"),
                "--repo-root",
                repo_root,
                "--bundle",
                "bundle.base.lab",
                "--compile-if-missing",
                "off",
                "--workers",
                "1",
                "--logical-shards",
                "1",
                "--write-state",
                "off",
                session_spec_abs,
                script_abs,
            ],
        )
        if int(scripted.get("exit_code", 1)) != 0 or str(scripted.get("json_error", "")):
            _print(
                {
                    "result": "refused",
                    "reason_code": "refusal.dev_run_script_failed",
                    "message": "session_script_run failed for '{}'".format(target),
                    "details": scripted,
                }
            )
            return 2
        script_run = dict(scripted.get("payload") or {})

    _print(
        {
            "result": "complete",
            "command_id": "dev run {}".format(target),
            "bundle_id": "bundle.base.lab",
            "experience_id": "profile.lab.developer",
            "law_profile_id": law_profile,
            "session_spec_path": session_spec_rel,
            "run_meta_path": str((booted.get("payload") or {}).get("run_meta_path", "")),
            "script_result": script_run,
        }
    )
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    executed = _run_proc(
        repo_root=repo_root,
        argv=[
            sys.executable,
            os.path.join(repo_root, "tools", "auditx", "auditx.py"),
            "scan",
            "--repo-root",
            repo_root,
            "--format",
            "both",
        ],
    )
    print(str(executed.get("output", "")).rstrip())
    return int(executed.get("exit_code", 1))


def _cmd_verify(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    executed = _run_proc(
        repo_root=repo_root,
        argv=[
            sys.executable,
            os.path.join(repo_root, "tools", "xstack", "run.py"),
            "strict",
            "--repo-root",
            repo_root,
            "--cache",
            "on",
        ],
    )
    print(str(executed.get("output", "")).rstrip())
    return int(executed.get("exit_code", 1))


def _cmd_profile(args: argparse.Namespace) -> int:
    repo_root = _repo_root(args.repo_root)
    capture = _run_proc(
        repo_root=repo_root,
        argv=[
            sys.executable,
            os.path.join(repo_root, "tools", "dev", "tool_profile_capture.py"),
            "--repo-root",
            repo_root,
            "--session-id",
            "session.dev.profile",
            "--scenario-id",
            "scenario.lab.galaxy_nav",
            "--out",
            "docs/audit/perf/profile_trace.sample.json",
        ],
    )
    print(str(capture.get("output", "")).rstrip())
    return int(capture.get("exit_code", 1))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Developer acceleration command wrapper.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    for command in ("impact-graph", "impacted-tests", "impacted-build-targets"):
        node = sub.add_parser(command)
        node.add_argument("--base-ref", default="origin/main")
        node.add_argument("--changed-files", default="", help="comma-separated changed file list override")
        node.add_argument("--out", default="build/impact_graph.json")
    impacted_build = sub.add_parser("impacted-build")
    impacted_build.add_argument("--base-ref", default="origin/main")
    impacted_build.add_argument("--changed-files", default="", help="comma-separated changed file list override")
    impacted_build.add_argument("--out", default="build/impact_graph.json")

    run_cmd = sub.add_parser("run")
    run_sub = run_cmd.add_subparsers(dest="target", required=True)
    for target in ("observer", "galaxy", "sol", "earth"):
        run_sub.add_parser(target)

    sub.add_parser("audit")
    sub.add_parser("verify")
    sub.add_parser("profile")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "impact-graph":
        return _cmd_impact_graph(args)
    if args.command == "impacted-tests":
        return _cmd_impacted_tests(args)
    if args.command == "impacted-build-targets":
        return _cmd_impacted_build_targets(args)
    if args.command == "impacted-build":
        return _cmd_impacted_build_targets(args)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "audit":
        return _cmd_audit(args)
    if args.command == "verify":
        return _cmd_verify(args)
    if args.command == "profile":
        return _cmd_profile(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
