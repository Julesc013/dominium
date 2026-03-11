#!/usr/bin/env python3
"""Generate the deterministic LIB-7 library stress scenario workspace."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.lib.lib_stress_common import DEFAULT_LIB7_SEED, DEFAULT_WORKSPACE_REL, generate_lib_stress_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the LIB-7 deterministic library stress scenario.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--out-root", default=DEFAULT_WORKSPACE_REL.replace("\\", "/"))
    parser.add_argument("--seed", default=str(DEFAULT_LIB7_SEED))
    parser.add_argument("--slash-mode", default="forward", choices=("forward", "backward"))
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    out_root = os.path.normpath(os.path.abspath(os.path.join(repo_root, str(args.out_root or DEFAULT_WORKSPACE_REL))))
    payload = generate_lib_stress_scenario(
        repo_root=repo_root,
        out_root=out_root,
        seed=int(str(args.seed or DEFAULT_LIB7_SEED).strip() or DEFAULT_LIB7_SEED),
        slash_mode=str(args.slash_mode or "forward").strip() or "forward",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
