#!/usr/bin/env python3
"""Reconcile generated AIDE root inventory wave evidence."""

from __future__ import print_function

import argparse
import json
import sys
from pathlib import Path

from root_recycling_common import load_json, source_head, write_json


TARGET_ROOTS = [
    "governance",
    "meta",
    "validation",
    "performance",
    "ide",
    "data",
    "packs",
    "profiles",
    "bundles",
    "modding",
    "models",
    "templates",
    "compat",
    "locks",
    "repo",
    "safety",
    "security",
    "specs",
    "updates",
    "core",
    "control",
    "net",
    "lib",
    "libs",
]


def load_optional(path):
    if not path.exists():
        return None
    return load_json(path)


def reconcile(repo_root):
    repo_root = Path(repo_root).resolve()
    reports = repo_root / ".aide" / "reports" / "roots"
    roots = []
    totals = {
        "root_count": 0,
        "present_roots": 0,
        "file_count": 0,
        "directory_count": 0,
        "preserve_unknown_count": 0,
        "reference_count": 0,
        "draft_salvage_map_count": 0,
    }
    missing = []
    for root in TARGET_ROOTS:
        inventory = load_optional(reports / (root + ".inventory.json"))
        classification = load_optional(reports / (root + ".classification.json"))
        references = load_optional(reports / (root + ".references.json"))
        salvage = load_optional(reports / (root + ".salvage_map.draft.json"))
        scan_paths = [
            reports / (root + ".identity_scan.json"),
            reports / (root + ".authority_scan.json"),
            reports / (root + ".semantic_scan.json"),
            reports / (root + ".abi_build_scan.json"),
        ]
        scans = [path.name for path in scan_paths if path.exists()]
        if not inventory:
            missing.append(root + ".inventory.json")
        if not classification:
            missing.append(root + ".classification.json")
        if not references:
            missing.append(root + ".references.json")
        if not salvage:
            missing.append(root + ".salvage_map.draft.json")
        fate_counts = (classification or {}).get("summary", {}).get("fate_counts", {})
        risk_counts = (classification or {}).get("summary", {}).get("risk_counts", {})
        sensitivity_counts = (classification or {}).get("summary", {}).get("sensitivity_counts", {})
        record = {
            "root": root,
            "inventory_present": inventory is not None,
            "classification_present": classification is not None,
            "references_present": references is not None,
            "salvage_map_present": salvage is not None,
            "scan_files": scans,
            "exists": bool((inventory or {}).get("exists", False)),
            "file_count": (inventory or {}).get("summary", {}).get("file_count", 0),
            "directory_count": (inventory or {}).get("summary", {}).get("directory_count", 0),
            "fate_counts": fate_counts,
            "risk_counts": risk_counts,
            "sensitivity_counts": sensitivity_counts,
            "reference_count": (references or {}).get("summary", {}).get("reference_count", 0),
            "apply_allowed": bool((salvage or {}).get("apply_allowed", False)),
            "approval_status": (salvage or {}).get("approval_status", "missing"),
        }
        roots.append(record)
        totals["root_count"] += 1
        if record["exists"]:
            totals["present_roots"] += 1
        totals["file_count"] += record["file_count"]
        totals["directory_count"] += record["directory_count"]
        totals["preserve_unknown_count"] += int(fate_counts.get("preserve_unknown", 0))
        totals["reference_count"] += record["reference_count"]
        if record["salvage_map_present"]:
            totals["draft_salvage_map_count"] += 1
    return {
        "schema_version": "dominium.aide.root_reconciliation.v1",
        "task_id": "AIDE-ROOT-06",
        "source_head": source_head(repo_root),
        "roots": roots,
        "summary": totals,
        "missing_evidence": sorted(missing),
        "moves_applied": False,
        "deletes_applied": False,
        "renames_applied": False,
        "reference_rewrites_applied": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    data = reconcile(repo_root)
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
