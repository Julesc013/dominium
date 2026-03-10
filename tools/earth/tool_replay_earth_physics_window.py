#!/usr/bin/env python3
"""Replay deterministic EARTH-9 movement and terrain-contact windows."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.earth.earth9_stress_common import (  # noqa: E402
    DEFAULT_EARTH9_SEED,
    DEFAULT_PHYSICS_REPLAY_REL,
    replay_earth_physics_window,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay deterministic EARTH-9 physics windows.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", type=int, default=DEFAULT_EARTH9_SEED)
    parser.add_argument("--output-path", default=DEFAULT_PHYSICS_REPLAY_REL)
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    report = replay_earth_physics_window(
        repo_root=repo_root,
        seed=int(args.seed),
    )
    output_path = str(args.output_path or "").strip()
    if output_path:
        write_json(os.path.normpath(os.path.abspath(output_path)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
