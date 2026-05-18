#!/usr/bin/env python3
"""Report tracked files remaining under former bad roots.

Default mode is advisory because MOVE-ROUTER-00 runs before apply. Use
--strict-final only after MOVE-ROUTER apply/repair tasks claim root closure.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import re
import subprocess
import sys


BAD_ROOTS = [
    "core", "control", "data", "packs", "profiles", "bundles", "compat",
    "lib", "libs", "locks", "repo", "safety", "security", "specs",
    "updates", "meta", "governance", "performance", "validation",
    "modding", "models", "templates", "net", "ide",
]


def utc_now():
    return _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def posix(path):
    return path.replace("\\", "/")


def git_files(repo_root):
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def active_exception_paths(repo_root):
    path = os.path.join(repo_root, "contracts", "repo", "layout_exceptions.toml")
    if not os.path.exists(path):
        return set()
    paths = set()
    active = False
    current_path = None
    path_re = re.compile(r'^path\s*=\s*"([^"]+)"')
    active_re = re.compile(r"^active\s*=\s*(true|false)")
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line.startswith("["):
                if current_path and active:
                    paths.add(current_path.strip("/"))
                current_path = None
                active = False
                continue
            path_match = path_re.match(line)
            if path_match:
                current_path = path_match.group(1).strip("/")
                continue
            active_match = active_re.match(line)
            if active_match:
                active = active_match.group(1) == "true"
    if current_path and active:
        paths.add(current_path.strip("/"))
    return paths


def build_report(repo_root):
    counts = {root: 0 for root in BAD_ROOTS}
    examples = {root: [] for root in BAD_ROOTS}
    for path in git_files(repo_root):
        root = path.split("/", 1)[0]
        if root in counts:
            counts[root] += 1
            if len(examples[root]) < 8:
                examples[root].append(path)
    exceptions = active_exception_paths(repo_root)
    roots = []
    total = 0
    for root in BAD_ROOTS:
        count = counts[root]
        total += count
        has_exception = root in exceptions
        roots.append({
            "root": root,
            "tracked_file_count": count,
            "exception_active": has_exception,
            "status": "empty" if count == 0 else "deferred_with_exception" if has_exception else "deferred_without_exception",
            "example_paths": examples[root],
        })
    nonempty_without_exception = [item["root"] for item in roots if item["tracked_file_count"] and not item["exception_active"]]
    return {
        "schema_version": "dominium.repo.bad_root_absence.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "PASS_WITH_WARNINGS" if total else "PASS",
        "bad_root_count": len(BAD_ROOTS),
        "tracked_bad_root_file_count": total,
        "nonempty_bad_root_count": sum(1 for item in roots if item["tracked_file_count"]),
        "nonempty_without_exception": nonempty_without_exception,
        "roots": roots,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict-final", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Alias for --strict-final.")
    parser.add_argument("--out")
    args = parser.parse_args()
    report = build_report(args.repo_root)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    if args.json or not args.out:
        print(json.dumps(report, indent=2, sort_keys=True))
    if (args.strict_final or args.strict) and report["tracked_bad_root_file_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
