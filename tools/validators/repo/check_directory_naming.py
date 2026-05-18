#!/usr/bin/env python3
"""Classify directory naming against NAME-00 lowercase ownership grammar."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import re
import subprocess
import sys


LOWER_SEGMENT = re.compile(r"^[a-z][a-z0-9_]*$")
LOWER_DOTTED = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+$")
METADATA_DIRS = set([".aide", ".github", ".vscode", ".aide.local.example", ".dominium.local"])


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


def directory_set(paths):
    dirs = set()
    for path in paths:
        parts = path.split("/")[:-1]
        current = []
        for part in parts:
            current.append(part)
            dirs.add("/".join(current))
    return sorted(dirs)


def segment_allowed(segment):
    if segment in METADATA_DIRS:
        return True
    if segment.startswith(".") and segment in METADATA_DIRS:
        return True
    if LOWER_SEGMENT.match(segment):
        return True
    if LOWER_DOTTED.match(segment):
        return True
    return False


def classify(path, segment):
    root = path.split("/", 1)[0]
    if root in (".aide", "archive"):
        return "info", "existing_evidence_or_archive"
    if "-" in segment:
        return "warning", "hyphenated_directory"
    if any(ch.isupper() for ch in segment):
        return "warning", "uppercase_directory"
    return "warning", "noncanonical_directory_case"


def build_report(repo_root, max_findings):
    findings = []
    counts = {}
    for directory in directory_set(git_files(repo_root)):
        for segment in directory.split("/"):
            if segment_allowed(segment):
                continue
            severity, disposition = classify(directory, segment)
            counts[disposition] = counts.get(disposition, 0) + 1
            findings.append({
                "path": directory,
                "segment": segment,
                "severity": severity,
                "disposition": disposition,
                "rule": "directory_case",
                "message": "directory segment is not lower_snake_or_single_lowerword",
            })
            break
    return {
        "schema_version": "dominium.repo.naming.directory_naming.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "PASS_WITH_WARNINGS" if findings else "PASS",
        "counts_by_disposition": counts,
        "finding_count": len(findings),
        "blocker_count": 0,
        "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
        "info_count": sum(1 for item in findings if item["severity"] == "info"),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def write_markdown(report, path):
    lines = [
        "# NAME-00 Directory Naming Report",
        "",
        "- Status: `{0}`".format(report["status"]),
        "- Findings: `{0}`".format(report["finding_count"]),
        "- Warnings: `{0}`".format(report["warning_count"]),
        "- Info: `{0}`".format(report["info_count"]),
        "",
        "## Counts By Disposition",
        "",
    ]
    for key in sorted(report["counts_by_disposition"]):
        lines.append("- `{0}`: {1}".format(key, report["counts_by_disposition"][key]))
    lines.extend(["", "## Sample Findings", ""])
    for item in report["findings"]:
        lines.append("- `{severity}` `{disposition}` `{segment}`: `{path}`".format(**item))
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
    parser.add_argument("--max-findings", type=int, default=300)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
