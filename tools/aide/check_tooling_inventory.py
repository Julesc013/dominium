#!/usr/bin/env python3
"""Validate AIDE-STRUCTURE-01 tool recycling inventory shape."""

import argparse
import json
import sys
from pathlib import Path


REQUIRED_ITEM_FIELDS = [
    "path",
    "display_name",
    "family",
    "current_name",
    "stable_future_owner",
    "aide_task_type",
    "fate",
    "risk",
    "execution_safety",
    "execution_allowed_now",
    "apply_allowed_now",
    "network_allowed_now",
    "writes_allowed_now",
    "known_outputs",
    "known_inputs",
    "preservation_required",
    "wrapper_candidate",
    "wrapper_priority",
    "reason",
    "blockers",
    "evidence_refs",
]


def load_inventory(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(data):
    errors = []
    warnings = []
    if data.get("schema_version") != "dominium.aide.tool_recycling_inventory.v1":
        errors.append("unexpected schema_version")
    if data.get("task_id") != "AIDE-STRUCTURE-01":
        errors.append("unexpected task_id")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        items = []
    paths = [item.get("path") for item in items]
    if paths != sorted(paths, key=lambda value: (str(value).lower(), str(value))):
        errors.append("items are not sorted deterministically by path")
    for index, item in enumerate(items):
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                errors.append("item {0} missing field {1}".format(index, field))
        if item.get("family") == "unknown" and item.get("execution_allowed_now"):
            errors.append("unknown item is execution-enabled: {0}".format(item.get("path")))
        if item.get("risk") in {"high", "protected", "unknown"} and item.get("execution_allowed_now"):
            errors.append("high/protected/unknown item is execution-enabled: {0}".format(item.get("path")))
        if item.get("fate") == "drop" and item.get("apply_allowed_now"):
            errors.append("drop candidate has apply_allowed_now true: {0}".format(item.get("path")))
    summary = data.get("summary", {})
    if summary.get("execution_allowed_count", 0) != 0:
        errors.append("execution_allowed_count must remain zero for inventory-only task")
    if summary.get("wrapper_candidate_count", 0) <= 0:
        warnings.append("no wrapper candidates found")
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--input", default=".aide/reports/tool-recycling-inventory.json", help="Inventory JSON path.")
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = repo_root / input_path
    data = load_inventory(input_path)
    errors, warnings = validate(data)
    report = {
        "schema_version": "dominium.aide.tool_recycling_inventory_check.v1",
        "input": str(input_path),
        "result": "FAIL" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS",
        "errors": errors,
        "warnings": warnings,
        "item_count": len(data.get("items", [])),
    }
    if args.json:
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        print(report["result"])
        for error in errors:
            print("ERROR: {0}".format(error))
        for warning in warnings:
            print("WARN: {0}".format(warning))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
