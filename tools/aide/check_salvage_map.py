#!/usr/bin/env python3
"""Validate a draft salvage map without applying it."""

from __future__ import print_function

import argparse
import json
import sys
from pathlib import Path

from root_recycling_common import load_json, validate_salvage_map


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--map", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    map_path = Path(args.map)
    if not map_path.is_absolute():
        map_path = repo_root / map_path
    result = validate_salvage_map(load_json(map_path), strict=args.strict)
    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        print("Salvage map check: {0}".format(result["result"]))
        for error in result["errors"]:
            print("- ERROR: {0}".format(error))
        for warning in result["warnings"]:
            print("- WARN: {0}".format(warning))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
