#!/usr/bin/env python3
"""Generate the deterministic Omega disaster-suite case registry and doctrine surfaces."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.disaster_suite_common import generate_disaster_suite  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--output-root-rel", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    result = generate_disaster_suite(
        repo_root,
        output_root_rel=str(args.output_root_rel or ""),
        write_outputs=True,
    )
    payload = {
        "result": str(result.get("result", "")).strip() or "complete",
        "cases_rel": os.path.relpath(str((dict(result.get("written") or {})).get("cases_path", "")), repo_root).replace("\\", "/"),
        "model_doc_rel": os.path.relpath(str((dict(result.get("written") or {})).get("model_doc_path", "")), repo_root).replace("\\", "/"),
        "case_count": int((dict((dict(result.get("cases_payload") or {}).get("record") or {})).get("case_count", 0) or 0)),
        "fingerprint": str((dict((dict(result.get("cases_payload") or {}).get("record") or {})).get("deterministic_fingerprint", "")).strip()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
