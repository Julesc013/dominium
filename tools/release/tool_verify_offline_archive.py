#!/usr/bin/env python3
"""Verify the deterministic Omega offline archive bundle for v0.0.0-mock."""

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

from tools.release.offline_archive_common import (  # noqa: E402
    OFFLINE_ARCHIVE_VERIFY_DOC_REL,
    OFFLINE_ARCHIVE_VERIFY_JSON_REL,
    verify_offline_archive,
    write_offline_archive_verify_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--archive-path", default="")
    parser.add_argument("--baseline-path", default="")
    parser.add_argument("--output-path", default="")
    parser.add_argument("--doc-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    archive_path = str(args.archive_path or "").strip()
    if not archive_path:
        raise SystemExit("--archive-path is required")
    report = verify_offline_archive(
        repo_root,
        archive_path=archive_path,
        baseline_path=str(args.baseline_path or "").strip(),
    )
    written = write_offline_archive_verify_outputs(
        repo_root,
        report,
        json_path=str(args.output_path or "").strip(),
        doc_path=str(args.doc_path or "").strip(),
    )
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "archive_bundle_hash": str(report.get("archive_bundle_hash", "")).strip(),
                "archive_record_hash": str(report.get("archive_record_hash", "")).strip(),
                "archive_projection_hash": str(report.get("archive_projection_hash", "")).strip(),
                "json_output_rel": os.path.relpath(str(written.get("json_path", "")), repo_root).replace("\\", "/") if str(written.get("json_path", "")).strip() else OFFLINE_ARCHIVE_VERIFY_JSON_REL,
                "doc_output_rel": os.path.relpath(str(written.get("doc_path", "")), repo_root).replace("\\", "/") if str(written.get("doc_path", "")).strip() else OFFLINE_ARCHIVE_VERIFY_DOC_REL,
                "subcheck_results": {
                    key: str(dict(report.get("subchecks") or {}).get(key, {}).get("result", "")).strip()
                    for key in sorted(dict(report.get("subchecks") or {}).keys())
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
