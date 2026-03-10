#!/usr/bin/env python3
"""APPSHELL-0 product stub entrypoint for products without bundled runtime logic."""

from __future__ import annotations

import argparse
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.appshell import appshell_main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--product-id", required=True)
    parsed, remainder = parser.parse_known_args(list(argv or sys.argv[1:]))
    return appshell_main(
        product_id=str(parsed.product_id).strip(),
        argv=list(remainder),
        repo_root_hint=REPO_ROOT_HINT,
        legacy_main=None,
        legacy_accepts_repo_root=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
