#!/usr/bin/env python3
"""Generate the Omega baseline universe artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.baseline_universe_common import generate_baseline_universe  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed-text", default="")
    parser.add_argument("--output-root-rel", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    result = generate_baseline_universe(
        repo_root,
        seed_text=str(args.seed_text or ""),
        output_root_rel=str(args.output_root_rel or ""),
        write_outputs=True,
    )
    output_paths = dict(result.get("output_paths") or {})
    payload = {
        "result": str(result.get("result", "")).strip() or "complete",
        "seed_text": str(result.get("seed_text", "")).strip(),
        "instance_manifest_rel": os.path.relpath(str(output_paths.get("instance_manifest_path", "")), repo_root).replace("\\", "/"),
        "pack_lock_rel": os.path.relpath(str(output_paths.get("pack_lock_path", "")), repo_root).replace("\\", "/"),
        "profile_bundle_rel": os.path.relpath(str(output_paths.get("profile_bundle_path", "")), repo_root).replace("\\", "/"),
        "save_rel": os.path.relpath(str(output_paths.get("save_path", "")), repo_root).replace("\\", "/"),
        "snapshot_rel": os.path.relpath(str(output_paths.get("snapshot_path", "")), repo_root).replace("\\", "/"),
        "snapshot_fingerprint": str((dict(result.get("snapshot_payload") or {}).get("record") or {}).get("deterministic_fingerprint", "")).strip(),
        "payload": dict(result.get("snapshot_payload") or {}),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

