#!/usr/bin/env python3
"""Generate the Omega worldgen lock baseline snapshot."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.worldgen.worldgen_lock_common import (  # noqa: E402
    WORLDGEN_BASELINE_SEED_REL,
    WORLDGEN_BASELINE_SNAPSHOT_REL,
    build_worldgen_lock_snapshot,
    read_worldgen_baseline_seed,
    write_worldgen_lock_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed-text", default="")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    seed_text = read_worldgen_baseline_seed(repo_root, seed_text=str(args.seed_text or ""))
    payload = build_worldgen_lock_snapshot(repo_root, seed_text=seed_text)
    written = write_worldgen_lock_snapshot(repo_root, payload, output_path=str(args.output_path or ""))
    result = {
        "result": "complete",
        "baseline_seed_rel": WORLDGEN_BASELINE_SEED_REL,
        "output_rel": os.path.relpath(written, repo_root).replace("\\", "/") if os.path.isabs(written) else WORLDGEN_BASELINE_SNAPSHOT_REL,
        "snapshot_fingerprint": str((payload.get("record") or {}).get("deterministic_fingerprint", "")).strip(),
        "payload": payload,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
