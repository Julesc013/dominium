#!/usr/bin/env python3
"""Run deterministic Xi-8 repository-freeze generation and validation."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.import_bridge import install_src_aliases  # noqa: E402

install_src_aliases(REPO_ROOT_HINT)


from tools.review.xi8_common import Xi8InputsMissing, run_xi8  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_xi8(args.repo_root, run_gates=not args.write_only)
    except Xi8InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    evaluation = dict(result.get("evaluation") or {})
    validation = dict(result.get("validation_report") or {})
    payload = {
        "result": str(result.get("result", "")).strip() or "blocked",
        "structure_status": str(evaluation.get("status", "")).strip() or "fail",
        "structure_finding_count": int(len(list(evaluation.get("structure_findings") or []))),
        "arch_graph_match_finding_count": int(len(list(evaluation.get("arch_graph_match_findings") or []))),
        "ci_strict_status": str(dict(validation.get("ci_strict") or {}).get("status", "")).strip(),
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
