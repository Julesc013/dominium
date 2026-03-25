#!/usr/bin/env python3
"""Run a deterministic Ω-9 toolchain matrix profile for one environment."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.mvp.toolchain_matrix_common import (  # noqa: E402
    DEFAULT_ENV_ID,
    DEFAULT_PROFILE_ID,
    run_toolchain_matrix,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--env-id", default=DEFAULT_ENV_ID)
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--output-root-rel", default="")
    parser.add_argument("--allow-heavy", action="store_true")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    result = run_toolchain_matrix(
        repo_root,
        env_id=str(args.env_id or DEFAULT_ENV_ID),
        profile_id=str(args.profile_id or DEFAULT_PROFILE_ID),
        output_root_rel=str(args.output_root_rel or ""),
        allow_heavy=bool(args.allow_heavy),
        write_outputs=True,
    )
    payload = {
        "result": str(result.get("result", "")).strip(),
        "run_id": str(result.get("run_id", "")).strip(),
        "run_root_rel": str(result.get("run_root_rel", "")).strip(),
        "env_root_rel": str(result.get("env_root_rel", "")).strip(),
        "hashes_fingerprint": str((dict(result.get("hashes_payload") or {})).get("deterministic_fingerprint", "")).strip(),
        "env_report": dict(result.get("env_report") or {}),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
