#!/usr/bin/env python3
"""Run deterministic TRUST-STRICT-VERIFY-0 reporting."""

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

from tools.security.trust_strict_common import (
    build_trust_strict_baseline,
    run_trust_strict_suite,
    write_trust_fixture_outputs,
    write_trust_strict_baseline_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic TRUST-STRICT-VERIFY-0 reporting.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    fixture_outputs = write_trust_fixture_outputs(repo_root)
    report = run_trust_strict_suite(repo_root, write_outputs=True)
    baseline_out = {}
    if bool(args.write_baseline):
        baseline = build_trust_strict_baseline(report)
        baseline_out = write_trust_strict_baseline_outputs(repo_root, baseline)
    sys.stdout.write(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "case_count": int(len(list(report.get("cases") or []))),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "fixture_count": int(len(list(dict(fixture_outputs or {}).get("fixtures") or []))),
                "baseline_written": bool(baseline_out),
                "baseline_json_path": str(dict(baseline_out).get("json_path", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
