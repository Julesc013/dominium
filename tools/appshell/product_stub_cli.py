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


from tools.import_bridge import install_src_aliases


install_src_aliases(REPO_ROOT_HINT)

from appshell import appshell_main


def _split_stub_args(argv: list[str]) -> tuple[str, list[str]]:
    values = list(argv or [])
    if len(values) >= 2 and str(values[0]).strip() == "--product-id":
        product_id = str(values[1]).strip()
        remainder = list(values[2:])
        if remainder and str(remainder[0]).strip() == "--":
            remainder = list(remainder[1:])
        return product_id, remainder
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--product-id", required=True)
    parsed, remainder = parser.parse_known_args(values)
    if remainder and str(remainder[0]).strip() == "--":
        remainder = list(remainder[1:])
    return str(parsed.product_id).strip(), list(remainder)


def main(argv: list[str] | None = None) -> int:
    product_id, remainder = _split_stub_args(list(argv or sys.argv[1:]))
    return appshell_main(
        product_id=product_id,
        argv=list(remainder),
        repo_root_hint=REPO_ROOT_HINT,
        legacy_main=None,
        legacy_accepts_repo_root=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
