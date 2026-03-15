#!/usr/bin/env python3
"""Generate the deterministic DIST-REFINE-1 install-profile registry and baseline report."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.release.install_profile_common import write_install_profile_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic DIST-REFINE-1 install-profile generation.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--platform-tag", default="win64")
    parser.add_argument("--write-registry", action="store_true")
    args = parser.parse_args(argv)
    outputs = write_install_profile_outputs(
        os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT))),
        platform_tag=str(args.platform_tag or "win64").strip() or "win64",
        write_registry=bool(args.write_registry),
    )
    report = dict(outputs.get("report") or {})
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "install_profile_registry_hash": str(report.get("install_profile_registry_hash", "")).strip(),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
                "baseline_doc_path": str(outputs.get("baseline_doc_path", "")).strip(),
                "report_json_path": str(outputs.get("report_json_path", "")).strip(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
