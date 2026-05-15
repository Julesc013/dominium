#!/usr/bin/env python3
"""Advisory forbidden-root check for the Dominium repo constitution."""

import argparse
import json
import sys
from pathlib import Path

from inventory_roots import inventory


KNOWN_OK = {
    "stable_root",
    "generated_root",
    "local_root",
    "transitional_root",
    "metadata_root",
    "optional_root",
    "allowed_root_file",
    "exception_backed",
}


def check(repo_root):
    data = inventory(repo_root)
    unknown = [entry for entry in data["entries"] if entry["classification"] not in KNOWN_OK]
    transitional = [entry for entry in data["entries"] if entry["classification"] == "transitional_root"]
    exception_backed = [entry for entry in data["entries"] if entry["classification"] == "exception_backed"]
    return {
        "schema_version": "dominium.aide.no_forbidden_roots.v1",
        "repo_root": str(repo_root),
        "mode": "audit",
        "advisory": True,
        "strict_promotes_unknowns_to_failure": True,
        "unknown_count": len(unknown),
        "transitional_count": len(transitional),
        "exception_backed_count": len(exception_backed),
        "unknown": unknown,
        "transitional": transitional,
        "exception_backed": exception_backed,
        "summary": data["summary"],
    }


def emit_human(report):
    print("Forbidden-root audit")
    print("====================")
    print("unknown_count: {0}".format(report["unknown_count"]))
    print("transitional_count: {0}".format(report["transitional_count"]))
    print("exception_backed_count: {0}".format(report["exception_backed_count"]))
    if report["unknown"]:
        print("")
        print("Unknown entries:")
        for entry in report["unknown"]:
            print("- {path} ({kind})".format(**entry))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Print deterministic JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when unknown roots are present.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    report = check(repo_root)
    report["mode"] = "strict" if args.strict else "audit"
    json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        sys.stdout.write(json_text)
    else:
        emit_human(report)
    if args.strict and report["unknown_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
