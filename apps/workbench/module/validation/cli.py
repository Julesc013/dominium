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

from apps.workbench.module.validation.command import SUPPORTED_PROFILES, SUPPORTED_SURFACES, run_validation_command  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--target", default="all")
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
