#!/usr/bin/env python3
from __future__ import print_function

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(os.path.join(THIS_DIR, os.pardir, os.pardir))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.compat.shims import run_legacy_validate_all  # noqa: E402

def repo_root_from_script():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def find_validate_all(repo_root):
    candidates = [
        os.path.join(repo_root, "build", "msvc-base", "bin", "validate_all.exe"),
        os.path.join(repo_root, "build", "msvc-base", "bin", "validate_all"),
        os.path.join(repo_root, "build", "bin", "validate_all.exe"),
        os.path.join(repo_root, "build", "bin", "validate_all"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Run unified governance validation (GOV0).")
    parser.add_argument("--repo-root", default=None, help="Repository root path")
    parser.add_argument("--exe", default=None, help="Path to validate_all executable")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json-out", default=None, help="Optional JSON report path")
    parser.add_argument("--text-out", default=None, help="Optional text report path")
    args = parser.parse_args()

    repo_root = args.repo_root or repo_root_from_script()
    report = run_legacy_validate_all(
        repo_root=repo_root,
        strict=bool(args.strict),
        profile="STRICT" if bool(args.strict) else "FAST",
        json_out=str(args.json_out or "").strip(),
        text_out=str(args.text_out or "").strip(),
        ignored_exe_path=str(args.exe or find_validate_all(repo_root) or "").strip(),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
