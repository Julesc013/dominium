#!/usr/bin/env python3
"""Audit an assembled DIST-1 tree for content minimization drift."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.dist.dist_tree_common import (  # noqa: E402
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_PLATFORM_TAG,
    DEFAULT_RELEASE_CHANNEL,
    _bundle_root,
    build_dist_minimize_report,
    render_dist_content_audit,
)


def _write_json(path: str, payload: dict) -> str:
    target = os.path.normpath(os.path.abspath(path))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = os.path.normpath(os.path.abspath(path))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit an assembled DIST-1 tree for content minimization drift.")
    parser.add_argument("--bundle-root", default="")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    parser.add_argument("--channel", default=DEFAULT_RELEASE_CHANNEL)
    parser.add_argument("--report-path", default="data/audit/dist_content_audit.json")
    parser.add_argument("--doc-path", default="docs/audit/DIST_CONTENT_AUDIT.md")
    args = parser.parse_args(argv)

    bundle_root = str(args.bundle_root).strip() or _bundle_root(
        str(args.output_root).strip() or DEFAULT_OUTPUT_ROOT,
        str(args.platform_tag).strip() or DEFAULT_PLATFORM_TAG,
        str(args.channel).strip() or DEFAULT_RELEASE_CHANNEL,
    )
    report = build_dist_minimize_report(bundle_root)
    _write_json(str(args.report_path), report)
    _write_text(str(args.doc_path), render_dist_content_audit(report))
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    has_findings = bool(report.get("unexpected_top_level")) or bool(report.get("dev_artifacts")) or bool(report.get("missing_pack_paths")) or bool(report.get("unexpected_pack_paths"))
    return 1 if has_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
