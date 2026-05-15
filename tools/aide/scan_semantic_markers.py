#!/usr/bin/env python3
"""Scan a root for runtime, authority, deterministic, and network markers."""

from __future__ import print_function

import argparse
import json
import sys
from pathlib import Path

from root_recycling_common import SEMANTIC_MARKERS, scan_markers, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--root", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    data = scan_markers(repo_root, args.root, SEMANTIC_MARKERS, "dominium.aide.semantic_marker_scan.v1")
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
