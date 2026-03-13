#!/usr/bin/env python3
"""Assemble a deterministic DIST-1 portable bundle tree."""

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
    build_dist_minimize_report,
    build_dist_tree,
    render_dist_content_audit,
    render_dist_final_report,
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
    parser = argparse.ArgumentParser(description="Assemble a deterministic DIST-1 portable bundle tree.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--platform-tag", default=DEFAULT_PLATFORM_TAG)
    parser.add_argument("--channel", default=DEFAULT_RELEASE_CHANNEL)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--report-path", default="data/audit/dist_tree_assembly_report.json")
    parser.add_argument("--content-report-path", default="data/audit/dist_content_audit.json")
    parser.add_argument("--content-doc-path", default="docs/audit/DIST_CONTENT_AUDIT.md")
    parser.add_argument("--final-doc-path", default="docs/audit/DIST_TREE_ASSEMBLY_FINAL.md")
    args = parser.parse_args(argv)

    report = build_dist_tree(
        args.repo_root,
        platform_tag=str(args.platform_tag).strip(),
        channel_id=str(args.channel).strip() or DEFAULT_RELEASE_CHANNEL,
        output_root=str(args.output_root).strip() or DEFAULT_OUTPUT_ROOT,
    )
    bundle_root = str(report.get("bundle_root_abs", "")).strip()
    content_report = build_dist_minimize_report(bundle_root)
    _write_json(str(args.report_path), report)
    _write_json(str(args.content_report_path), content_report)
    _write_text(str(args.content_doc_path), render_dist_content_audit(content_report))
    _write_text(str(args.final_doc_path), render_dist_final_report(report, content_report))
    stdout_payload = {
        "result": "complete",
        "bundle_root": str(report.get("bundle_root", "")).strip(),
        "bundle_hash": str(report.get("bundle_hash", "")).strip(),
        "release_manifest_hash": str(report.get("release_manifest_hash", "")).strip(),
        "file_count": int(report.get("file_count", 0)),
        "platform_tag": str(report.get("platform_tag", "")).strip(),
    }
    sys.stdout.write(json.dumps(stdout_payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
