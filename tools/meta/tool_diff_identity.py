#!/usr/bin/env python3
"""Diff UNIVERSAL-ID blocks between two artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.identity import canonicalize_universal_identity_block, validate_identity_path  # noqa: E402


FIELDS = (
    "identity_kind_id",
    "identity_id",
    "content_hash",
    "semver",
    "build_id",
    "format_version",
    "schema_version",
    "contract_bundle_hash",
    "stability_class_id",
    "deterministic_fingerprint",
)


def _report_for(repo_root: str, artifact_path: str) -> dict:
    artifact_abs = os.path.normpath(os.path.abspath(artifact_path))
    rel_path = os.path.relpath(artifact_abs, repo_root).replace("\\", "/")
    return validate_identity_path(repo_root, rel_path, strict_missing=False)


def _diff_rows(left: dict, right: dict) -> list[dict]:
    left_block = canonicalize_universal_identity_block(dict(left.get("identity_block") or {}))
    right_block = canonicalize_universal_identity_block(dict(right.get("identity_block") or {}))
    rows = []
    for field in FIELDS:
        left_value = left_block.get(field)
        right_value = right_block.get(field)
        if left_value == right_value:
            continue
        rows.append({"field": field, "left": left_value, "right": right_value})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare universal identity blocks between two artifacts.")
    parser.add_argument("left_path")
    parser.add_argument("right_path")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(args.repo_root))
    left_report = _report_for(repo_root, args.left_path)
    right_report = _report_for(repo_root, args.right_path)
    diff = {
        "left_path": str(left_report.get("path", "")).replace("\\", "/"),
        "right_path": str(right_report.get("path", "")).replace("\\", "/"),
        "differences": _diff_rows(left_report, right_report),
    }
    if args.json:
        print(json.dumps(diff, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print("left: {}".format(diff["left_path"]))
        print("right: {}".format(diff["right_path"]))
        if not diff["differences"]:
            print("differences: none")
        else:
            print("differences:")
            for row in diff["differences"]:
                print("  - {}: {!r} != {!r}".format(row["field"], row["left"], row["right"]))
    return 0 if not diff["differences"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
