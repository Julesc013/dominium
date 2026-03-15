#!/usr/bin/env python3
"""Run deterministic UPDATE-MODEL-0 generation and baseline reporting."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.dist.dist_tree_common import build_dist_tree
from tools.release.update_model_common import write_update_model_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic UPDATE-MODEL-0 generation.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--platform-tag", default="win64")
    parser.add_argument("--dist-root", default="")
    parser.add_argument("--write-release-index", action="store_true")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    dist_root = str(args.dist_root or "").strip()
    if not dist_root:
        dist_root = os.path.join(repo_root, "dist", "v0.0.0-mock", str(args.platform_tag or "win64").strip() or "win64", "dominium")
    dist_root = os.path.normpath(os.path.abspath(dist_root))
    if not os.path.isfile(os.path.join(dist_root, "manifests", "release_manifest.json")):
        build_dist_tree(
            repo_root,
            platform_tag=str(args.platform_tag or "win64").strip() or "win64",
            channel_id="mock",
            output_root=os.path.join(repo_root, "build", "tmp", "update_model_dist"),
            install_profile_id="install.profile.full",
        )
        dist_root = os.path.join(repo_root, "build", "tmp", "update_model_dist", "v0.0.0-mock", str(args.platform_tag or "win64").strip() or "win64", "dominium")

    outputs = write_update_model_outputs(
        repo_root,
        platform_tag=str(args.platform_tag or "win64").strip() or "win64",
        dist_root=dist_root,
        write_release_index_file=bool(args.write_release_index),
    )
    report = dict(outputs.get("report") or {})
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")).strip(),
                "release_index_hash": str(report.get("release_index_hash", "")).strip(),
                "update_plan_fingerprint": str(report.get("update_plan_fingerprint", "")).strip(),
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
