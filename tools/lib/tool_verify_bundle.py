#!/usr/bin/env python3
"""Verify deterministic LIB-6 bundles offline."""

from __future__ import annotations

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.lib.bundle import verify_bundle_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a deterministic LIB-6 bundle directory.")
    parser.add_argument("--bundle", required=True)
    args = parser.parse_args(argv)

    result = verify_bundle_directory(os.path.abspath(str(args.bundle or "").strip()))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 3


if __name__ == "__main__":
    raise SystemExit(main())
