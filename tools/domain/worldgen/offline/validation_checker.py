import argparse
import json
import sys
from pathlib import Path

from _common import ensure_cache_path, load_json, repo_root, write_json


def diff_keys(expected, actual, path=""):
    diffs = []
    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    for missing in sorted(expected_keys - actual_keys):
        diffs.append(f"{path}/{missing}: missing")
    for extra in sorted(actual_keys - expected_keys):
        diffs.append(f"{path}/{extra}: unexpected")
    for key in sorted(expected_keys & actual_keys):
        exp_val = expected[key]
        act_val = actual[key]
        next_path = f"{path}/{key}"
        if isinstance(exp_val, dict) and isinstance(act_val, dict):
            diffs.extend(diff_keys(exp_val, act_val, next_path))
        elif exp_val != act_val:
            diffs.append(f"{next_path}: {exp_val!r} != {act_val!r}")
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline validation checker for tool outputs.")
    parser.add_argument("--expected", required=True, help="Expected output JSON.")
    parser.add_argument("--actual", required=True, help="Actual output JSON.")
    parser.add_argument("--strict", action="store_true", help="Compare full documents.")
    parser.add_argument("--report-out", help="Optional JSON report path under build/cache/assets.")
    args = parser.parse_args()

    expected = load_json(Path(args.expected))
    actual = load_json(Path(args.actual))

    if args.strict:
        diffs = diff_keys(expected, actual, path="")
    else:
        subset = {
            "tool_id": expected.get("tool_id"),
            "tool_version": expected.get("tool_version"),
            "request": expected.get("request"),
            "plan_summary": expected.get("plan_summary"),
        }
        actual_subset = {
            "tool_id": actual.get("tool_id"),
            "tool_version": actual.get("tool_version"),
            "request": actual.get("request"),
            "plan_summary": actual.get("plan_summary"),
        }
        diffs = diff_keys(subset, actual_subset, path="")

    report = {
        "tool_id": "dominium.tool.validation_checker",
        "tool_version": "1.0.0",
        "expected": args.expected,
        "actual": args.actual,
        "strict": args.strict,
        "diffs": diffs,
        "status": "match" if not diffs else "mismatch",
    }

    if args.report_out:
        root = repo_root()
        report_path = ensure_cache_path(Path(args.report_out), root)
        write_json(report_path, report)
        print(f"Wrote validation report: {report_path}")

    if diffs:
        print("Validation mismatch:")
        print(json.dumps(diffs, indent=2))
        return 2
    print("Validation match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
