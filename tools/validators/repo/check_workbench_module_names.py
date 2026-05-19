#!/usr/bin/env python3
"""Validate Workbench module naming and adjacent ownership paths."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


FORBIDDEN_EXACT_PREFIXES = {
    "apps/workbench/module/game/edit": "apps/workbench/module/game/editor",
    "apps/workbench/module/tool/editor": "apps/workbench/module/tooling/editor",
    "apps/workbench/module/ui/editor/gen": "tools/codegen/ui/<area>/gen",
    "apps/workbench/module/ui/editor/generated": "tools/codegen/ui/<area>/gen",
    "apps/workbench/module/ui/native": "apps/workbench/module/ui/preview/native or runtime/ui/backend",
}

FORBIDDEN_SEGMENTS = {
    "core": "Use a precise Workbench module role or move shared substrate to runtime/tools/contracts.",
    "common": "Use a precise Workbench module role or move shared substrate to runtime/tools/contracts.",
    "shared": "Use a precise Workbench module role or move shared substrate to runtime/tools/contracts.",
    "misc": "Use a precise Workbench module role or move shared substrate to runtime/tools/contracts.",
    "edit": "Use noun role `editor` for Workbench modules.",
    "gen": "Use tools/codegen/ui for generators and generated bindings.",
}


def _configure_stdio():
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdio()


def utc_now():
    return _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def posix(path):
    return str(path).replace("\\", "/")


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


def tracked_directories(tracked):
    dirs = set()
    for path in tracked:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:index]))
    return dirs


def _add(findings, path, disposition, reason, suggested_target):
    findings.append(
        {
            "path": path,
            "severity": "blocker",
            "disposition": disposition,
            "reason": reason,
            "suggested_target": suggested_target,
        }
    )


def build_report(repo_root, max_findings):
    tracked = git_files(repo_root)
    candidates = set(tracked) | tracked_directories(tracked)
    findings = []

    for path in sorted(candidates):
        if not path.startswith("apps/workbench/module/"):
            continue

        for prefix, target in sorted(FORBIDDEN_EXACT_PREFIXES.items()):
            if path == prefix or path.startswith(prefix + "/"):
                _add(
                    findings,
                    path,
                    "retired_workbench_module_path",
                    "Workbench modules use noun roles and generated/tooling/runtime code must live with its canonical owner.",
                    target,
                )

        parts = path.split("/")
        for index, segment in enumerate(parts):
            if index < 3:
                continue
            if segment in FORBIDDEN_SEGMENTS:
                _add(
                    findings,
                    path,
                    "forbidden_workbench_module_segment",
                    FORBIDDEN_SEGMENTS[segment],
                    "apps/workbench/module/<subject>/<editor|viewer|inspector|analyzer|preview|registry|doc> or a non-Workbench owner",
                )

    unique = {}
    for item in findings:
        unique[(item["path"], item["disposition"], item["suggested_target"])] = item
    findings = sorted(unique.values(), key=lambda item: (item["path"], item["disposition"]))
    blocker_count = len(findings)
    return {
        "schema_version": "dominium.repo.workbench.module_names.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS",
        "finding_count": blocker_count,
        "blocker_count": blocker_count,
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate Workbench module names.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("workbench module names: {0}".format(report["status"]))
        for item in report["findings"]:
            print("{severity} {path}: {reason} -> {suggested_target}".format(**item))
    return 1 if args.strict and report["blocker_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
