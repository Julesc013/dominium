#!/usr/bin/env python3
"""Generate PERFORMANCE-ENVELOPE-0 reports and baseline outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.perf.performance_envelope_common import DEFAULT_PLATFORM_TAG, write_performance_outputs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    args = parser.parse_args(argv)

    outputs = write_performance_outputs(args.repo_root, platform_tag=str(args.platform_tag).strip() or DEFAULT_PLATFORM_TAG)
    report = dict(outputs.get("report") or {})
    stdout_payload = {
        "result": str(report.get("result", "")).strip(),
        "platform_tag": str(report.get("platform_tag", "")).strip(),
        "report_json_path": str(outputs.get("report_json_path", "")).strip(),
        "report_doc_path": str(outputs.get("report_doc_path", "")).strip(),
        "baseline_doc_path": str(outputs.get("baseline_doc_path", "")).strip(),
        "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
    }
    sys.stdout.write(json.dumps(stdout_payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if stdout_payload["result"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
