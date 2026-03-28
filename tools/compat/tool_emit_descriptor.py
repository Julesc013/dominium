#!/usr/bin/env python3
"""Emit deterministic CAP-NEG-1 endpoint descriptors for product surfaces."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from compat.descriptor import descriptor_json_text, emit_product_descriptor  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit deterministic endpoint descriptor for a Dominium product.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--descriptor", action="store_true")
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--descriptor-file", default="")
    parser.add_argument("--product-version", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    try:
        emitted = emit_product_descriptor(
            repo_root,
            product_id=str(args.product_id),
            descriptor_file=str(args.descriptor_file),
            product_version=str(args.product_version),
        )
    except ValueError as exc:
        print(json.dumps({"result": "refused", "reason": str(exc)}, indent=2, sort_keys=True))
        return 2

    sys.stdout.write(descriptor_json_text(dict(emitted.get("descriptor") or {})))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
