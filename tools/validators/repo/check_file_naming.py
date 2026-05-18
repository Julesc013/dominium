#!/usr/bin/env python3
"""Classify file naming against NAME-00 artifact-role grammar."""

from __future__ import print_function

import argparse
import datetime as _datetime
import fnmatch
import json
import os
import re
import subprocess
import sys


LOWER_FILE = re.compile(r"^[a-z0-9][a-z0-9_]*(\.[a-z0-9_]+)*$")
CONVENTIONAL = set([
    ".agentignore", ".gitattributes", ".gitignore",
    "README.md", "LICENSE", "LICENSE.md", "CHANGELOG.md", "SECURITY.md",
    "CONTRIBUTING.md", "AGENTS.md", "CLAUDE.md", "CMakeLists.txt",
    "CMakePresets.json", "CODE_CHANGE_JUSTIFICATION.md", "DOMINIUM.md",
    "GOVERNANCE.md", "MODDING.md",
])
CONVENTIONAL_PATTERNS = ["VERSION_*"]
ROLE_SUFFIXES = [
    ".schema.json", ".registry.json", ".manifest.json", ".contract.toml",
    ".policy.toml", ".matrix.toml", ".lock.json", ".proof.json",
    ".report.md", ".report.json", ".audit.md", ".audit.json",
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
        return []
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def conventional(name):
    if name in CONVENTIONAL:
        return True
    for pattern in CONVENTIONAL_PATTERNS:
        if fnmatch.fnmatchcase(name, pattern):
            return True
    for suffix in ROLE_SUFFIXES:
        if name.endswith(suffix):
            return True
    return False


def allowed(path):
    name = path.rsplit("/", 1)[-1]
    if conventional(name):
        return True
    if LOWER_FILE.match(name):
        return True
    return False


def classify(path):
    root = path.split("/", 1)[0]
    name = path.rsplit("/", 1)[-1]
    if root in (".aide", "archive"):
        return "info", "existing_evidence_or_archive"
    if name.endswith(".md") and any(ch.isupper() for ch in name):
        return "warning", "existing_uppercase_doc"
    if "-" in name:
        return "warning", "hyphenated_file"
    if any(ch.isupper() for ch in name):
        return "warning", "uppercase_file"
    return "warning", "noncanonical_file_case"


def build_report(repo_root, max_findings):
    findings = []
    counts = {}
    for path in git_files(repo_root):
        if allowed(path):
            continue
        severity, disposition = classify(path)
        counts[disposition] = counts.get(disposition, 0) + 1
        findings.append({
            "path": path,
            "file": path.rsplit("/", 1)[-1],
            "severity": severity,
            "disposition": disposition,
            "rule": "file_case",
            "message": "file name is not lower_snake_case or a conventional exception",
        })
    return {
        "schema_version": "dominium.repo.naming.file_naming.v1",
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
        "# NAME-00 File Naming Report",
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
        lines.append("- `{severity}` `{disposition}` `{file}`: `{path}`".format(**item))
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
