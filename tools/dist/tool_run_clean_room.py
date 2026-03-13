#!/usr/bin/env python3
"""Run the DIST-3 clean-room portability harness against a portable bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.dist.clean_room_common import (  # noqa: E402
    DEFAULT_FINAL_DOC_PATH,
    DEFAULT_MODE_POLICY,
    DEFAULT_PLATFORM,
    DEFAULT_SEED,
    DEFAULT_WORK_ROOT,
    build_clean_room_report,
    write_clean_room_outputs,
    write_dist3_final_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-root", default="dist")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--mode-policy", default=DEFAULT_MODE_POLICY, choices=("gui", "tui", "cli"))
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--work-root", default=DEFAULT_WORK_ROOT)
    parser.add_argument("--report-path", default="")
    parser.add_argument("--doc-path", default="")
    parser.add_argument("--final-doc-path", default=DEFAULT_FINAL_DOC_PATH)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = build_clean_room_report(
        str(args.dist_root),
        platform_tag=str(args.platform_tag).strip() or DEFAULT_PLATFORM,
        seed=str(args.seed).strip() or DEFAULT_SEED,
        mode_policy=str(args.mode_policy).strip() or DEFAULT_MODE_POLICY,
        repo_root=repo_root,
        work_root=str(args.work_root).strip() or DEFAULT_WORK_ROOT,
    )
    write_clean_room_outputs(
        repo_root,
        report,
        report_path=str(args.report_path).strip(),
        doc_path=str(args.doc_path).strip(),
    )
    write_dist3_final_outputs(
        repo_root,
        [report],
        final_doc_path=str(args.final_doc_path).strip() or DEFAULT_FINAL_DOC_PATH,
    )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
