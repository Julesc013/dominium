#!/usr/bin/env python3
"""Collect small CTest timing samples without running the full suite by default."""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def ctest_base(args):
    if args.preset:
        command = ["ctest", "--preset", args.preset]
    elif args.test_dir:
        command = ["ctest", "--test-dir", args.test_dir]
    else:
        raise SystemExit("Either --preset or --test-dir is required.")

    if args.config:
        command.extend(["-C", args.config])
    if args.label_regex:
        command.extend(["-L", args.label_regex])
    if args.timeout:
        command.extend(["--timeout", str(args.timeout)])
    return command


def list_tests(args):
    command = ctest_base(args)
    if args.regex:
        command.extend(["-R", args.regex])
    command.append("-N")
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout or ""
    tests = []
    for line in output.splitlines():
        match = re.search(r"Test\s+#\d+:\s+(.+)$", line)
        if match:
            tests.append(match.group(1).strip())
    total_match = re.findall(r"Total Tests:\s+(\d+)", output)
    total = int(total_match[-1]) if total_match else len(tests)
    return completed.returncode, command, output, tests, total


def run_one(args, test_name):
    command = ctest_base(args)
    command.extend(["-R", "^{}$".format(re.escape(test_name)), "--output-on-failure"])
    start = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    elapsed = time.monotonic() - start
    return {
        "name": test_name,
        "seconds": round(elapsed, 3),
        "returncode": completed.returncode,
        "command": command,
    }


def write_json(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_markdown(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-05-16",
        "Supersedes: none",
        "Superseded By: none",
        "",
        "# CTest Timing Sample",
        "",
        "| Test | Seconds | Result |",
        "| --- | ---: | --- |",
    ]
    for result in payload["results"]:
        outcome = "PASS" if result["returncode"] == 0 else "FAIL"
        lines.append("| `{}` | {:.3f} | {} |".format(result["name"], result["seconds"], outcome))
    if not payload["results"]:
        lines.append("| none | 0.000 | not run |")
    lines.extend(
        [
            "",
            "Listed tests: {}".format(payload["listed_count"]),
            "Selected tests: {}".format(payload["selected_count"]),
        ]
    )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset")
    parser.add_argument("--test-dir")
    parser.add_argument("--config", default="Debug")
    parser.add_argument("--regex")
    parser.add_argument("--label-regex")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--out", required=True)
    parser.add_argument("--md-out")
    args = parser.parse_args(argv)

    code, command, discovery_output, tests, total = list_tests(args)
    if code != 0:
        print(discovery_output, end="")
        return code

    selected = tests[: max(args.limit, 0)]
    results = []
    if not args.list_only and args.limit != 0:
        for test in selected:
            result = run_one(args, test)
            results.append(result)
            print("{name}: {seconds:.3f}s rc={returncode}".format(**result))

    payload = {
        "schema_version": "dominium.ctest_timing_sample.v1",
        "command": command,
        "regex": args.regex,
        "label_regex": args.label_regex,
        "listed_count": total,
        "selected_count": len(selected),
        "list_only": args.list_only or args.limit == 0,
        "results": results,
    }
    write_json(args.out, payload)
    if args.md_out:
        write_markdown(args.md_out, payload)
    return 0 if all(result["returncode"] == 0 for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
