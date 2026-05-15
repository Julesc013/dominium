#!/usr/bin/env python3
"""Conservatively classify an AIDE root inventory."""

from __future__ import print_function

import argparse
import json
import sys
from pathlib import Path

from root_recycling_common import classify_inventory, load_json, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    inventory_path = Path(args.inventory)
    if not inventory_path.is_absolute():
        inventory_path = repo_root / inventory_path
    data = classify_inventory(load_json(inventory_path))
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = repo_root / out
        write_json(out, data)
    if args.json or not args.out:
        sys.stdout.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
