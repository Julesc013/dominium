#!/usr/bin/env python3
"""CLI: validate lockfile integrity and deterministic hash semantics."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic lockfile payload.")
    parser.add_argument("path", help="lockfile path")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    lock_path = os.path.normpath(os.path.abspath(args.path))
    try:
        payload = json.load(open(lock_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        out = {
            "result": "refused",
            "errors": [
                {
                    "code": "refuse.lockfile.invalid_json",
                    "message": "unable to parse lockfile json",
                    "path": "$",
                }
            ],
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    schema_check = validate_instance(repo_root=repo_root, schema_name="bundle_lockfile", payload=payload, strict_top_level=True)
    if not bool(schema_check.get("valid", False)):
        out = {
            "result": "refused",
            "errors": schema_check.get("errors", []),
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    lock_check = validate_lockfile_payload(payload if isinstance(payload, dict) else {})
    print(json.dumps(lock_check, indent=2, sort_keys=True))
    return 0 if lock_check.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())

