#!/usr/bin/env python3
"""Run ``dominium.validation.run`` through the skeletal Workbench validation slice."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _install_repo_root() -> str:
    cursor = Path(__file__).resolve()
    for parent in cursor.parents:
        if (parent / "AGENTS.md").exists():
            root = str(parent)
            if root not in sys.path:
                sys.path.insert(0, root)
            return root
    return os.getcwd()


REPO_ROOT_HINT = _install_repo_root()

from apps.workbench.module.validation.command import (  # noqa: E402
    DEFAULT_CONTRACT_SCHEMA_TARGET,
    SUPPORTED_PROFILES,
    SUPPORTED_SURFACES,
    SUPPORTED_TARGET_KINDS,
    run_validation_command,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--target", default="all")
    parser.add_argument("--target-kind", default="", choices=("",) + SUPPORTED_TARGET_KINDS)
    parser.add_argument("--target-path", default="")
    parser.add_argument("--artifact-ref", default="")
    parser.add_argument("--suite-id", default="")
    parser.add_argument("--mode", default="", choices=("", "dry_run", "strict"))
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--require-capability", action="append", default=[])
    parser.add_argument("--profile", default="FAST", choices=SUPPORTED_PROFILES)
    parser.add_argument("--surface", default="cli", choices=SUPPORTED_SURFACES)
    parser.add_argument("--write-reports", action="store_true")
    parser.add_argument("--continue-on-fail", action="store_true")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    payload = {
        "target": args.target,
        "profile": args.profile,
        "surface": args.surface,
        "emit_reports": bool(args.write_reports),
        "continue_on_fail": bool(args.continue_on_fail),
    }
    if args.target_kind:
        payload["target_kind"] = args.target_kind
    if args.target_path:
        payload["target_path"] = args.target_path
    elif args.target_kind == "contract_schema":
        payload["target_path"] = DEFAULT_CONTRACT_SCHEMA_TARGET
    if args.artifact_ref:
        payload["artifact_ref"] = args.artifact_ref
    if args.suite_id:
        payload["suite_id"] = args.suite_id
    if args.mode:
        payload["mode"] = args.mode
    if args.capability:
        payload["capabilities"] = args.capability
    if args.require_capability:
        payload["required_capabilities"] = args.require_capability
    if args.json_out:
        payload["json_out"] = args.json_out

    result = run_validation_command(payload, repo_root=args.repo_root, invocation_surface=args.surface)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json_out:
        parent = os.path.dirname(os.path.abspath(args.json_out))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.write("\n")
    print(text)
    return 0 if result.get("status") in {"ok", "warning"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
