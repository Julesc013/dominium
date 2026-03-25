#!/usr/bin/env python3
"""Verify the Omega baseline universe against the committed freeze artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.baseline_universe_common import (  # noqa: E402
    BASELINE_VERIFY_DOC_REL,
    BASELINE_VERIFY_JSON_REL,
    verify_baseline_universe,
    write_baseline_universe_verify_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed-text", default="")
    parser.add_argument("--snapshot-path", default="")
    parser.add_argument("--save-path", default="")
    parser.add_argument("--output-path", default="")
    parser.add_argument("--doc-path", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = verify_baseline_universe(
        repo_root,
        seed_text=str(args.seed_text or ""),
        snapshot_path=str(args.snapshot_path or ""),
        save_path=str(args.save_path or ""),
    )
    written = write_baseline_universe_verify_outputs(
        repo_root,
        report,
        json_path=str(args.output_path or ""),
        doc_path=str(args.doc_path or ""),
    )
    result = {
        "result": str(report.get("result", "")).strip(),
        "json_output_rel": os.path.relpath(str(written.get("json_path", "")), repo_root).replace("\\", "/") if str(written.get("json_path", "")).strip() else BASELINE_VERIFY_JSON_REL,
        "doc_output_rel": os.path.relpath(str(written.get("doc_path", "")), repo_root).replace("\\", "/") if str(written.get("doc_path", "")).strip() else BASELINE_VERIFY_DOC_REL,
        "report": report,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if bool(report.get("matches_snapshot")) and bool(report.get("save_reload_matches")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
