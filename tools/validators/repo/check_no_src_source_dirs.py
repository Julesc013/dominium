#!/usr/bin/env python3
"""Classify tracked src/source/sources directory segments.

Default mode is audit/warning. Strict mode fails only for unexcepted active
source paths outside archive and known transitional roots.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


FORBIDDEN = set(["src", "source", "sources"])
TRANSITIONAL_ROOTS = set([
    "core", "control", "data", "packs", "profiles", "bundles", "compat",
    "lib", "libs", "locks", "repo", "safety", "security", "specs",
    "updates", "meta", "governance", "performance", "validation",
    "modding", "models", "templates", "net", "dist", "artifacts",
])


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
        return []
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def classify(path, term):
    root = path.split("/", 1)[0]
    if path.startswith("archive/"):
        return "info", "historical_archive"
    if root in TRANSITIONAL_ROOTS:
        return "warning", "excepted_transitional_debt"
    return "blocker", "unexcepted_active_path"


def build_report(repo_root, max_findings):
    findings = []
    counts = {}
    for path in git_files(repo_root):
        for segment in path.split("/")[:-1]:
            if segment in FORBIDDEN:
                severity, disposition = classify(path, segment)
                counts[segment] = counts.get(segment, 0) + 1
                findings.append({
                    "path": path,
                    "segment": segment,
                    "severity": severity,
                    "disposition": disposition,
                    "rule": "no_src_source_dirs",
                    "message": "tracked path contains forbidden directory segment '{0}'".format(segment),
                })
    return {
        "schema_version": "dominium.repo.naming.no_src_source_dirs.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if any(item["severity"] == "blocker" for item in findings) else "PASS_WITH_WARNINGS" if findings else "PASS",
        "counts_by_segment": counts,
        "finding_count": len(findings),
        "blocker_count": sum(1 for item in findings if item["severity"] == "blocker"),
        "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
        "info_count": sum(1 for item in findings if item["severity"] == "info"),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def write_markdown(report, path):
    lines = [
        "# NAME-00 No src/source Directory Report",
        "",
        "- Status: `{0}`".format(report["status"]),
        "- Findings: `{0}`".format(report["finding_count"]),
        "- Blockers: `{0}`".format(report["blocker_count"]),
        "- Warnings: `{0}`".format(report["warning_count"]),
        "- Info: `{0}`".format(report["info_count"]),
        "",
        "## Counts By Segment",
        "",
    ]
    for key in sorted(report["counts_by_segment"]):
        lines.append("- `{0}`: {1}".format(key, report["counts_by_segment"][key]))
    lines.extend(["", "## Sample Findings", ""])
    for item in report["findings"]:
        lines.append("- `{severity}` `{segment}` `{disposition}`: `{path}`".format(**item))
    if report["truncated"]:
        lines.append("")
        lines.append("Report is truncated by `--max-findings`.")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    parser.add_argument("--md-out")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()
    report = build_report(args.repo_root, args.max_findings)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    if args.md_out:
        write_markdown(report, args.md_out)
    if args.json or not (args.out or args.md_out):
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.strict and report["blocker_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
