#!/usr/bin/env python3
"""Verify TIME-ANCHOR-0 compaction boundaries align to epoch anchors."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.time.time_anchor_common import (  # noqa: E402
    DEFAULT_COMPACTION_REPORT_REL,
    verify_compaction_anchor_alignment,
    write_time_anchor_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--report-path", default=DEFAULT_COMPACTION_REPORT_REL)
    args = parser.parse_args(argv)

    report = verify_compaction_anchor_alignment(args.repo_root)
    written = write_time_anchor_outputs(
        args.repo_root,
        compaction_report=report,
        compaction_report_path=str(args.report_path),
    )
    payload = dict(report)
    payload["written_outputs"] = written
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
