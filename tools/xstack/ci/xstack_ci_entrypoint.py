#!/usr/bin/env python3
"""Run the deterministic Xi-7 XStack CI guardrail profile."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.ci.ci_common import CI_REPORT_JSON_REL, CI_REPORT_MD_REL, Xi7InputsMissing, run_ci_profile  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--profile", required=True, choices=("FAST", "STRICT", "FULL"))
    parser.add_argument("--testx-subset", default="")
    args = parser.parse_args(argv)

    try:
        report = run_ci_profile(
            args.repo_root,
            args.profile,
            testx_subset_override=[item.strip() for item in str(args.testx_subset or "").split(",") if item.strip()],
        )
    except Xi7InputsMissing as exc:
        sys.stdout.write(str(exc).strip())
        sys.stdout.write("\n")
        return 4

    payload = {
        "profile": str(report.get("profile", "")).strip(),
        "result": str(report.get("result", "")).strip(),
        "stage_count": len(list(report.get("stages") or [])),
        "failing_stage_count": len([row for row in list(report.get("stages") or []) if str(dict(row or {}).get("status", "")).strip() != "pass"]),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        "report_json_path": CI_REPORT_JSON_REL,
        "report_md_path": CI_REPORT_MD_REL,
    }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
