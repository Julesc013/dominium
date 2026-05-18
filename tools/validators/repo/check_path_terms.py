#!/usr/bin/env python3
"""Classify tracked paths containing forbidden naming terms."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


FORBIDDEN_TERMS = set([
    "src", "source", "sources", "code", "impl", "common", "shared", "misc",
    "new", "old", "modern", "legacy", "classic", "universal", "compat",
])

ALLOWED_PREFIXES = {
    "archive/legacy": "historical archive classification",
    "contracts/compatibility": "compatibility contract ownership",
    "docs/compatibility": "compatibility documentation ownership",
}

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


def allowed_prefix(path):
    if path.startswith("archive/"):
        return "historical material under archive"
    for prefix, reason in ALLOWED_PREFIXES.items():
        if path == prefix or path.startswith(prefix + "/"):
            return reason
    return ""


def classify(path, term, index):
    root = path.split("/", 1)[0]
    reason = allowed_prefix(path)
    if reason:
        return "info", "allowed_exception", reason
    if root in TRANSITIONAL_ROOTS:
        return "warning", "excepted_transitional_debt", "active layout exception or generated-adjacent debt"
    if index == 0:
        return "blocker", "unexcepted_forbidden_root", "forbidden term used as top-level root"
    return "warning", "needs_owner_review", "nested generic/status term needs owner review"


def build_report(repo_root, max_findings):
    findings = []
    counts = {}
    for path in git_files(repo_root):
        segments = path.split("/")[:-1]
        for index, segment in enumerate(segments):
            if segment in FORBIDDEN_TERMS:
                severity, disposition, reason = classify(path, segment, index)
                counts[segment] = counts.get(segment, 0) + 1
                findings.append({
                    "path": path,
                    "segment": segment,
                    "segment_index": index,
                    "severity": severity,
                    "disposition": disposition,
                    "reason": reason,
                    "rule": "forbidden_path_terms",
                })
    return {
        "schema_version": "dominium.repo.naming.path_terms.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if any(item["severity"] == "blocker" for item in findings) else "PASS_WITH_WARNINGS" if findings else "PASS",
        "counts_by_term": counts,
        "finding_count": len(findings),
        "blocker_count": sum(1 for item in findings if item["severity"] == "blocker"),
        "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
        "info_count": sum(1 for item in findings if item["severity"] == "info"),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def write_markdown(report, path):
    lines = [
        "# NAME-00 Path Term Conflict Report",
        "",
        "- Status: `{0}`".format(report["status"]),
        "- Findings: `{0}`".format(report["finding_count"]),
        "- Blockers: `{0}`".format(report["blocker_count"]),
        "- Warnings: `{0}`".format(report["warning_count"]),
        "- Info: `{0}`".format(report["info_count"]),
        "",
        "## Counts By Term",
        "",
    ]
    for key in sorted(report["counts_by_term"]):
        lines.append("- `{0}`: {1}".format(key, report["counts_by_term"][key]))
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
    if args.strict and report["blocker_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
