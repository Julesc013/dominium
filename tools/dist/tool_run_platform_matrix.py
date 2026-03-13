#!/usr/bin/env python3
"""Run the DIST-4 cross-platform packaging matrix against portable bundles."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.dist.dist_platform_matrix_common import (  # noqa: E402
    DEFAULT_BUILD_OUTPUT_ROOT,
    DEFAULT_PLATFORM_TAGS,
    DIST4_FINAL_PATH,
    build_platform_matrix_report,
    write_platform_matrix_outputs,
)


def _parse_dist_specs(values: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in list(values or []):
        token = str(item or "").strip()
        if not token:
            continue
        platform_tag, separator, path_value = token.partition("=")
        if not separator or not platform_tag.strip() or not path_value.strip():
            raise ValueError("invalid --dist-spec {!r}; expected <platform_tag>=<path>".format(token))
        mapping[str(platform_tag).strip()] = str(path_value).strip()
    return dict(sorted(mapping.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--platform-tag", action="append", default=[])
    parser.add_argument("--dist-spec", action="append", default=[])
    parser.add_argument("--channel", default="mock")
    parser.add_argument("--build-output-root", default=DEFAULT_BUILD_OUTPUT_ROOT)
    parser.add_argument("--simulate-tty", choices=("yes", "no", "both"), default="both")
    parser.add_argument("--simulate-gui", choices=("yes", "no", "both"), default="both")
    parser.add_argument("--report-path", default="")
    parser.add_argument("--doc-path", default="")
    parser.add_argument("--supported-doc-path", default="")
    parser.add_argument("--final-doc-path", default=DIST4_FINAL_PATH)
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    try:
        bundle_roots = _parse_dist_specs(list(args.dist_spec or []))
    except ValueError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2
    platform_tags = [str(item or "").strip() for item in list(args.platform_tag or []) if str(item or "").strip()]
    if not platform_tags and not bundle_roots:
        platform_tags = list(DEFAULT_PLATFORM_TAGS)

    report = build_platform_matrix_report(
        repo_root,
        platform_tags=platform_tags,
        bundle_roots=bundle_roots,
        channel_id=str(args.channel or "mock").strip() or "mock",
        build_output_root=str(args.build_output_root or DEFAULT_BUILD_OUTPUT_ROOT).strip() or DEFAULT_BUILD_OUTPUT_ROOT,
        simulate_tty=str(args.simulate_tty or "both").strip() or "both",
        simulate_gui=str(args.simulate_gui or "both").strip() or "both",
    )
    write_platform_matrix_outputs(
        repo_root,
        report,
        report_path=str(args.report_path).strip(),
        doc_path=str(args.doc_path).strip(),
        supported_doc_path=str(args.supported_doc_path).strip(),
        final_doc_path=str(args.final_doc_path).strip() or DIST4_FINAL_PATH,
    )
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
