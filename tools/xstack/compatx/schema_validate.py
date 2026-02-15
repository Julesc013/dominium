#!/usr/bin/env python3
"""CLI: deterministic strict validation for canonical schema payloads."""

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


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _load_payload(path: str):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle), ""
    except (OSError, ValueError):
        return None, "invalid json file: {}".format(path.replace("\\", "/"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a JSON instance against canonical schema v1 contracts.")
    parser.add_argument("schema_name", help="schema name without suffix, for example: session_spec")
    parser.add_argument("file_path", help="path to JSON instance file")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = _repo_root(args.repo_root)
    payload_path = os.path.normpath(os.path.abspath(args.file_path))
    payload, load_error = _load_payload(payload_path)
    if load_error:
        result = {
            "schema_name": str(args.schema_name),
            "schema_file": "",
            "schema_version": "",
            "payload_hash": "",
            "valid": False,
            "errors": [
                {
                    "code": "instance_load_error",
                    "path": "$",
                    "message": load_error,
                }
            ],
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1

    result = validate_instance(
        repo_root=repo_root,
        schema_name=str(args.schema_name),
        payload=payload,
        strict_top_level=True,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if bool(result.get("valid", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())

