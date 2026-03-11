#!/usr/bin/env python3
"""Replay a DIAG-0 repro bundle and verify deterministic hashes."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.diag.diag0_probe import replay_diag0_bundle  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay a deterministic DIAG-0 repro bundle.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--bundle-path", required=True)
    parser.add_argument("--tick-window", type=int, default=16)
    args = parser.parse_args(argv)

    payload = replay_diag0_bundle(
        str(args.repo_root),
        bundle_path=str(args.bundle_path),
        tick_window=int(args.tick_window or 0),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if str(payload.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
