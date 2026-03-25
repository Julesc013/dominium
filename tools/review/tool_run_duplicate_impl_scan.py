#!/usr/bin/env python3
"""Run deterministic XI-1 duplicate implementation and shadow-module analysis."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.duplicate_impl_scan_common import (  # noqa: E402
    XiInputMissingError,
    build_duplicate_impl_snapshot,
    write_duplicate_impl_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic XI-1 duplicate implementation and shadow-module analysis.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    try:
        snapshot = build_duplicate_impl_snapshot(args.repo_root)
    except XiInputMissingError as exc:
        sys.stdout.write(
            json.dumps(
                {
                    "result": "refused",
                    "refusal_code": exc.refusal_code,
                    "missing_inputs": list(exc.missing_paths),
                    "remediation": exc.remediation,
                },
                indent=2,
                sort_keys=True,
            )
        )
        sys.stdout.write("\n")
        return 2

    write_duplicate_impl_snapshot(args.repo_root, snapshot)
    stdout_payload = {
        "duplicate_group_count": int(dict(snapshot.get("duplicate_impls") or {}).get("group_count", 0) or 0),
        "near_duplicate_cluster_count": int(dict(snapshot.get("duplicate_clusters") or {}).get("cluster_count", 0) or 0),
        "result": "complete",
        "shadow_module_count": int(dict(snapshot.get("shadow_modules") or {}).get("shadow_count", 0) or 0),
        "src_directory_count": int(dict(snapshot.get("src_directory_report") or {}).get("directory_count", 0) or 0),
    }
    sys.stdout.write(json.dumps(stdout_payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
