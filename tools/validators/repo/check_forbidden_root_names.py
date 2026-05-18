#!/usr/bin/env python3
"""Advisory validator for forbidden repository path ownership terms."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


FORBIDDEN = set([
    "src", "source", "sources", "code", "impl", "common", "shared", "misc",
    "new", "old", "future", "modern", "legacy", "classic", "universal",
    "experimental", "research", "v2", "v3", "compat",
])

TRANSITIONAL_ROOTS = set([
    "core", "control", "data", "packs", "profiles", "bundles", "compat",
    "lib", "libs", "locks", "repo", "safety", "security", "specs",
    "updates", "meta", "governance", "performance", "validation",
    "modding", "models", "templates", "net", "ide",
])

ALLOWED_PREFIXES = {
    "archive/legacy": "historical archive classification",
    "contracts/compatibility": "compatibility contract ownership",
    "docs/compatibility": "compatibility documentation ownership",
}


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


def allowed_prefix(path):
    if path.startswith("archive/"):
        return "archive_material"
    for prefix in sorted(ALLOWED_PREFIXES):
        if path == prefix or path.startswith(prefix + "/"):
            return ALLOWED_PREFIXES[prefix]
    return ""


def classify(path, segment, index):
    root = path.split("/", 1)[0]
    allowed = allowed_prefix(path)
    if allowed:
        return "info", "allowed_exception", allowed
    if root in TRANSITIONAL_ROOTS:
        return "warning", "excepted_transitional_debt", "former bad root still under active cleanup"
    if index == 0:
        return "blocker", "forbidden_top_level_root", "new top-level forbidden ownership root"
    return "warning", "needs_owner_review", "nested forbidden term needs review before future enforcement"


def build_report(repo_root, max_findings):
    findings = []
    counts = {}
    for path in git_files(repo_root):
        segments = path.split("/")[:-1]
        for index, segment in enumerate(segments):
            lowered = segment.lower()
            if lowered in FORBIDDEN:
                severity, disposition, reason = classify(path, lowered, index)
                counts[lowered] = counts.get(lowered, 0) + 1
                findings.append({
                    "path": path,
                    "segment": lowered,
                    "segment_index": index,
                    "severity": severity,
                    "disposition": disposition,
                    "reason": reason,
                    "rule": "forbidden_root_or_directory_name",
                })
    blocker_count = sum(1 for item in findings if item["severity"] == "blocker")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    info_count = sum(1 for item in findings if item["severity"] == "info")
    return {
        "schema_version": "dominium.repo.naming.forbidden_root_names.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS_WITH_WARNINGS" if findings else "PASS",
        "finding_count": len(findings),
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "counts_by_term": dict(sorted(counts.items())),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out")
    parser.add_argument("--max-findings", type=int, default=300)
    args = parser.parse_args()
    report = build_report(args.repo_root, args.max_findings)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    if args.json or not args.out:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.strict and report["blocker_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
