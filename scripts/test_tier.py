#!/usr/bin/env python3
"""Run Dominium validation tiers from tests/validation_tiers.json."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "tests" / "validation_tiers.json"


def load_manifest(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def render_args(args):
    rendered = []
    replacements = {
        "{python}": sys.executable,
        "{repo_root}": str(REPO_ROOT),
    }
    for arg in args:
        rendered.append(replacements.get(arg, arg))
    return rendered


def ctest_base_command(spec):
    if spec.get("preset"):
        command = ["ctest", "--preset", spec["preset"]]
    elif spec.get("test_dir"):
        command = ["ctest", "--test-dir", spec["test_dir"]]
    else:
        raise ValueError("ctest spec requires preset or test_dir")

    if spec.get("config"):
        command.extend(["-C", spec["config"]])
    if spec.get("regex"):
        command.extend(["-R", spec["regex"]])
    if spec.get("exclude_regex"):
        command.extend(["-E", spec["exclude_regex"]])
    if spec.get("label_regex"):
        command.extend(["-L", spec["label_regex"]])
    if spec.get("timeout"):
        command.extend(["--timeout", str(spec["timeout"])])
    if spec.get("parallel"):
        command.extend(["--parallel", str(spec["parallel"])])
    return command


def ctest_run_command(spec):
    command = ctest_base_command(spec)
    if spec.get("output_on_failure", True):
        command.append("--output-on-failure")
    return command


def ctest_discovery_command(spec):
    command = ctest_base_command(spec)
    command.append("-N")
    return command


def parse_total_tests(output):
    matches = re.findall(r"Total Tests:\s+(\d+)", output)
    if not matches:
        return None
    return int(matches[-1])


def run_command(command, dry_run=False):
    printable = " ".join(command)
    print(printable)
    if dry_run:
        return 0, ""
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    return completed.returncode, completed.stdout or ""


def preflight_ctest(spec, dry_run=False):
    command = ctest_discovery_command(spec)
    if dry_run:
        print(" ".join(command))
        return 0
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout or ""
    if output:
        print(output, end="")
    if completed.returncode != 0:
        return completed.returncode
    count = parse_total_tests(output)
    if spec.get("require_tests") and count == 0:
        print("CTest discovery found 0 tests for this tier.", file=sys.stderr)
        if spec.get("preset"):
            print(
                "Run `cmake --preset {}` before this tier, then retry.".format(
                    spec["preset"]
                ),
                file=sys.stderr,
            )
        return 2
    return 0


def run_tier(manifest, tier_name, dry_run=False, no_preflight=False, keep_going=False):
    tiers = manifest.get("tiers", {})
    if tier_name not in tiers:
        print("Unknown tier: {}".format(tier_name), file=sys.stderr)
        return 2

    tier = tiers[tier_name]
    print("== {} ==".format(tier_name))
    if tier.get("description"):
        print(tier["description"])

    failures = []
    for raw_command in tier.get("commands", []):
        code, _ = run_command(render_args(raw_command), dry_run=dry_run)
        if code != 0:
            failures.append(("command", code))
            if not keep_going:
                return code

    for spec in tier.get("ctest", []):
        if not no_preflight:
            code = preflight_ctest(spec, dry_run=dry_run)
            if code != 0:
                failures.append(("ctest-discovery", code))
                if not keep_going:
                    return code
        code, _ = run_command(ctest_run_command(spec), dry_run=dry_run)
        if code != 0:
            failures.append(("ctest", code))
            if not keep_going:
                return code

    if failures:
        return failures[0][1]
    return 0


def list_tiers(manifest):
    for name, tier in manifest.get("tiers", {}).items():
        marker = " promotion" if tier.get("promotion_gate") else ""
        print("{}{}: {}".format(name, marker, tier.get("description", "")))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--list", action="store_true", help="List available tiers.")
    parser.add_argument(
        "--tier",
        action="append",
        default=[],
        help="Tier to run. May be provided more than once.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-preflight", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_manifest(Path(args.manifest))

    if args.list:
        list_tiers(manifest)
        return 0

    if not args.tier:
        parser.error("--tier is required unless --list is used")

    result = 0
    for tier in args.tier:
        code = run_tier(
            manifest,
            tier,
            dry_run=args.dry_run,
            no_preflight=args.no_preflight,
            keep_going=args.keep_going,
        )
        if code != 0:
            result = code
            if not args.keep_going:
                break
    return result


if __name__ == "__main__":
    sys.exit(main())
