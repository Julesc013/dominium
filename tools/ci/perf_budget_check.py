#!/usr/bin/env python3
from __future__ import print_function

import argparse
import configparser
import json
import os
import sys


def load_budget_block(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except IOError as exc:
        raise RuntimeError("Failed to read budgets file: {0}".format(exc))

    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("```perf-budgets"):
            start = idx + 1
            break
    if start is None:
        raise RuntimeError("Missing ```perf-budgets block in {0}".format(path))
    for idx in range(start, len(lines)):
        if lines[idx].strip().startswith("```"):
            end = idx
            break
    if end is None:
        raise RuntimeError("Unterminated ```perf-budgets block in {0}".format(path))

    block = "\n".join(lines[start:end])
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(block)
    budgets = {}
    for section in parser.sections():
        budgets[section] = {}
        for key, value in parser.items(section):
            try:
                budgets[section][key] = int(value)
            except ValueError:
                raise RuntimeError("Invalid budget value for {0}.{1}: {2}".format(section, key, value))
    return budgets


def load_reports(run_root):
    budget_dir = os.path.join(run_root, "perf", "budgets")
    if not os.path.isdir(budget_dir):
        raise RuntimeError("Budget directory not found: {0}".format(budget_dir))
    reports = []
    for name in sorted(os.listdir(budget_dir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(budget_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (IOError, ValueError) as exc:
            raise RuntimeError("Failed to parse {0}: {1}".format(path, exc))
        reports.append((path, data))
    return reports


def check_reports(budgets, reports, default_tier=None):
    failures = []
    missing = []
    for path, data in reports:
        tier = data.get("tier") or default_tier or "baseline"
        metrics = data.get("metrics") or {}
        if tier not in budgets:
            failures.append((path, "tier", tier, "unknown tier"))
            continue
        for key, limit in budgets[tier].items():
            if key not in metrics:
                missing.append((path, key))
                continue
            value = metrics[key]
            if value > limit:
                failures.append((path, key, value, limit))
    return failures, missing


def main():
    parser = argparse.ArgumentParser(description="PERF budget regression gate")
    parser.add_argument("--run-root", default=None, help="Run root path with perf/budgets outputs")
    parser.add_argument("--budgets", default=None, help="Path to PERF_BUDGETS.md")
    parser.add_argument("--tier", default=None, help="Tier override (baseline|modern|server)")
    args = parser.parse_args()

    run_root = args.run_root or os.environ.get("DOMINIUM_RUN_ROOT") or "."
    budgets_path = args.budgets or os.path.join(os.getcwd(), "docs", "policies", "PERF_BUDGETS.md")

    budgets = load_budget_block(budgets_path)
    reports = load_reports(run_root)
    if not reports:
        print("PERF-BUDGET-002: no budget reports found under {0}".format(run_root))
        print("Fix: run perf fixtures to generate reports under run_root/perf/budgets.")
        return 1

    failures, missing = check_reports(budgets, reports, default_tier=args.tier)
    if missing:
        print("PERF-PROFILE-001: missing metrics in budget reports")
        for path, key in missing:
            print("  {0}: missing {1}".format(path, key))
        print("Fix: ensure fixtures emit all required metrics listed in PERF_BUDGETS.md.")
        return 1
    if failures:
        print("PERF-BUDGET-002: performance budgets exceeded")
        for path, key, value, limit in failures:
            print("  {0}: {1}={2} > {3}".format(path, key, value, limit))
        print("Fix: optimize the workload or update PERF_BUDGETS.md with approved thresholds.")
        return 1

    print("Performance budgets OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
