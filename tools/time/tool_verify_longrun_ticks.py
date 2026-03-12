#!/usr/bin/env python3
"""Verify TIME-ANCHOR-0 long-run tick width, anchors, and replay checks."""

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
    DEFAULT_FINAL_DOC_REL,
    DEFAULT_VERIFY_REPORT_REL,
    verify_compaction_anchor_alignment,
    verify_longrun_ticks,
    write_time_anchor_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--report-path", default=DEFAULT_VERIFY_REPORT_REL)
    parser.add_argument("--compaction-report-path", default=DEFAULT_COMPACTION_REPORT_REL)
    parser.add_argument("--final-doc-path", default=DEFAULT_FINAL_DOC_REL)
    args = parser.parse_args(argv)

    verify_report = verify_longrun_ticks(args.repo_root)
    compaction_report = verify_compaction_anchor_alignment(args.repo_root)
    written = write_time_anchor_outputs(
        args.repo_root,
        verify_report=verify_report,
        compaction_report=compaction_report,
        verify_report_path=str(args.report_path),
        compaction_report_path=str(args.compaction_report_path),
        final_doc_path=str(args.final_doc_path),
    )
    payload = {
        "verify_report": verify_report,
        "compaction_report": compaction_report,
        "written_outputs": written,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    status_ok = (
        str(verify_report.get("result", "")) == "complete"
        and str(compaction_report.get("result", "")) == "complete"
    )
    return 0 if status_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
