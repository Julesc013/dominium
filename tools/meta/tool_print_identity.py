#!/usr/bin/env python3
"""Print UNIVERSAL-ID blocks for a governed artifact."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.identity import validate_identity_path  # noqa: E402


def _print_text(report: dict) -> None:
    expected = dict(report.get("expected") or {})
    actual = dict(report.get("identity_block") or {})
    print("path: {}".format(str(report.get("path", "")).replace("\\", "/")))
    print("result: {}".format(str(report.get("result", "")).strip() or "complete"))
    print("expected.kind: {}".format(str(expected.get("identity_kind_id", "")).strip()))
    print("expected.id: {}".format(str(expected.get("identity_id", "")).strip()))
    print("actual.kind: {}".format(str(actual.get("identity_kind_id", "")).strip()))
    print("actual.id: {}".format(str(actual.get("identity_id", "")).strip()))
    print("actual.content_hash: {}".format(str(actual.get("content_hash", "")).strip()))
    if list(report.get("warnings") or []):
        print("warnings:")
        for row in list(report.get("warnings") or []):
            item = dict(row or {})
            print("  - [{}] {}".format(str(item.get("code", "")).strip(), str(item.get("message", "")).strip()))
    if list(report.get("errors") or []):
        print("errors:")
        for row in list(report.get("errors") or []):
            item = dict(row or {})
            print("  - [{}] {}".format(str(item.get("code", "")).strip(), str(item.get("message", "")).strip()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the universal identity block for a governed artifact.")
    parser.add_argument("artifact_path", help="Path to the artifact JSON file")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict-missing", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(args.repo_root))
    artifact_abs = os.path.normpath(os.path.abspath(args.artifact_path))
    rel_path = os.path.relpath(artifact_abs, repo_root).replace("\\", "/")
    report = validate_identity_path(repo_root, rel_path, strict_missing=bool(args.strict_missing))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        _print_text(report)
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
