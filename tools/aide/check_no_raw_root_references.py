#!/usr/bin/env python3
"""Audit raw root references; strict mode fails on active references."""

from __future__ import print_function

import argparse
import json
import sys
from pathlib import Path

from root_recycling_common import scan_references


ACTIVE_CLASSES = set(["active_source", "tools", "tests"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--root", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    scan = scan_references(repo_root, args.root)
    active = [ref for ref in scan["references"] if ref.get("classification") in ACTIVE_CLASSES]
    result = {
        "schema_version": "dominium.aide.raw_root_reference_check.v1",
        "root": args.root,
        "strict": bool(args.strict),
        "result": "FAIL" if args.strict and active else "PASS",
        "reference_count": len(scan["references"]),
        "active_reference_count": len(active),
        "references": scan["references"],
    }
    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        print("Raw root reference check: {0}".format(result["result"]))
        print("references: {0}".format(result["reference_count"]))
        print("active references: {0}".format(result["active_reference_count"]))
    return 1 if result["result"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
