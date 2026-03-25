#!/usr/bin/env python3
"""Run the deterministic MVP gameplay loop and write the committed baseline snapshot."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.gameplay_loop_common import run_gameplay_loop  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed-text", default="")
    parser.add_argument("--instance-path", default="")
    parser.add_argument("--save-path", default="")
    parser.add_argument("--output-root-rel", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    result = run_gameplay_loop(
        repo_root,
        seed_text=str(args.seed_text or ""),
        instance_path=str(args.instance_path or ""),
        save_path=str(args.save_path or ""),
        output_root_rel=str(args.output_root_rel or ""),
        write_outputs=True,
    )
    output_paths = dict(result.get("output_paths") or {})
    payload = {
        "result": str(result.get("result", "")).strip() or "complete",
        "snapshot_rel": os.path.relpath(str(output_paths.get("snapshot_path", "")), repo_root).replace("\\", "/"),
        "run_doc_rel": os.path.relpath(str(output_paths.get("run_doc_path", "")), repo_root).replace("\\", "/"),
        "runtime_save_rel": os.path.relpath(str(result.get("runtime_save_path", "")), repo_root).replace("\\", "/"),
        "snapshot_fingerprint": str((dict(result.get("snapshot_payload") or {}).get("record") or {}).get("deterministic_fingerprint", "")).strip(),
        "payload": dict(result.get("snapshot_payload") or {}),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
