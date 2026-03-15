#!/usr/bin/env python3
"""Run deterministic STORE-GC-0 baseline generation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.lib.store_gc_common import write_store_gc_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic STORE-GC-0 baseline artifacts.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    args = parser.parse_args(argv)

    outputs = write_store_gc_outputs(os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT))))
    report = dict(outputs.get("report") or {})
    sys.stdout.write(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "policy_ids": list(report.get("policy_ids") or []),
                "store_verify_fingerprint": str(report.get("store_verify_fingerprint", "")).strip(),
                "gc_none_fingerprint": str(report.get("gc_none_fingerprint", "")).strip(),
                "gc_safe_fingerprint": str(report.get("gc_safe_fingerprint", "")).strip(),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "baseline_doc_path": str(outputs.get("baseline_doc_path", "")).strip(),
                "report_json_path": str(outputs.get("report_json_path", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
