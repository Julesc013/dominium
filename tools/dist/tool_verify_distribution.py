#!/usr/bin/env python3
"""Verify an assembled DIST tree offline and deterministically."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.dist.dist_verify_common import (  # noqa: E402
    DEFAULT_PLATFORM,
    _default_bundle_root,
    build_distribution_verify_report,
    write_distribution_verify_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-root", default="")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--report-path", default="")
    parser.add_argument("--doc-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root))) if str(args.repo_root).strip() else REPO_ROOT_HINT
    platform_tag = str(args.platform_tag).strip() or DEFAULT_PLATFORM
    dist_root = str(args.dist_root).strip()
    bundle_root = _default_bundle_root(dist_root or os.path.join(repo_root, "dist"), platform_tag)
    report = build_distribution_verify_report(bundle_root, platform_tag=platform_tag, repo_root=repo_root)
    write_distribution_verify_outputs(
        repo_root,
        report,
        report_path=str(args.report_path).strip(),
        doc_path=str(args.doc_path).strip(),
    )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
