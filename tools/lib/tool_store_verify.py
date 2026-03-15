#!/usr/bin/env python3
"""Run deterministic store verification and write STORE-GC-0 verify outputs."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.lib.store_gc_common import write_store_verify_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a Dominium content-addressable store deterministically.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--store-root", default="")
    parser.add_argument("--install-root", action="append", dest="install_roots", default=[])
    parser.add_argument("--registry-path", default="")
    args = parser.parse_args(argv)

    outputs = write_store_verify_outputs(
        os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT))),
        store_root=str(args.store_root or "").strip(),
        install_roots=[str(item).strip() for item in list(args.install_roots or []) if str(item).strip()],
        registry_path=str(args.registry_path or "").strip(),
    )
    report = dict(outputs.get("report") or {})
    verify_report = dict(report.get("store_verify_report") or {})
    sys.stdout.write(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "store_id": str(verify_report.get("store_id", "")).strip(),
                "artifact_count": int(verify_report.get("artifact_count", 0) or 0),
                "verified_hash_count": int(len(list(verify_report.get("verified_hashes") or []))),
                "error_count": int(len(list(verify_report.get("errors") or []))),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "report_doc_path": str(outputs.get("report_doc_path", "")).strip(),
                "report_json_path": str(outputs.get("report_json_path", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    sys.stdout.write("\n")
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
