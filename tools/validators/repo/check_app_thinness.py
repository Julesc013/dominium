#!/usr/bin/env python3
"""Validate that apps/ stays limited to product entrypoints and glue."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


FORBIDDEN_PRODUCT_CHILDREN = {
    "core": "runtime/<subsystem> or game/<owner>, depending content",
    "model": "runtime/ui/<product>/model or contracts/view",
    "network": "runtime/network",
    "package": "runtime/package or contracts/package",
    "persistence": "runtime/storage or runtime/save",
    "platform": "runtime/platform",
    "presentation": "runtime/ui or runtime/render",
    "render": "runtime/render",
    "runtime": "runtime/<subsystem>",
    "storage": "runtime/storage or runtime/save",
    "ui": "runtime/ui or apps/workbench/module for user-facing modules",
}

FORBIDDEN_EXACT_DIRS = {
    "apps/server/authority": "game/law or contracts/capability",
    "apps/server/persistence": "runtime/storage or runtime/save",
    "apps/server/shard": "runtime/network/server/shard unless strictly product-local",
}

ALLOWED_PRODUCT_CHILDREN = {
    "adapters",
    "app",
    "cli",
    "gui",
    "include",
    "lifecycle",
    "local_server",
    "main",
    "resources",
    "tui",
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
        if not path.startswith("apps/"):
            continue
        if path.startswith("apps/workbench/module/"):
            continue

        if path in FORBIDDEN_EXACT_DIRS:
            _add(
                findings,
                path,
                "fat_app_directory",
                "apps/server must not own shared authority, persistence, or shard implementation",
                FORBIDDEN_EXACT_DIRS[path],
            )
            continue

        parts = path.split("/")
        if len(parts) < 3:
            continue
        product_child = parts[2]
        if product_child in ALLOWED_PRODUCT_CHILDREN:
            continue
        if product_child in FORBIDDEN_PRODUCT_CHILDREN:
            _add(
                findings,
                "/".join(parts[:3]),
                "shared_subsystem_under_app",
                "apps/<product> is limited to product entrypoints, descriptors, resources, and product-specific glue",
                FORBIDDEN_PRODUCT_CHILDREN[product_child],
            )

    unique = {}
    for item in findings:
        unique[(item["path"], item["disposition"])] = item
    findings = sorted(unique.values(), key=lambda item: (item["path"], item["disposition"]))
    blocker_count = len(findings)
    return {
        "schema_version": "dominium.repo.app.thinness.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS",
        "allowed_product_children": sorted(ALLOWED_PRODUCT_CHILDREN),
        "finding_count": blocker_count,
        "blocker_count": blocker_count,
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate thin app ownership.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("app thinness: {}".format(report["status"]))
        for item in report["findings"]:
            print(
                "{severity} {path}: {reason} -> {suggested_target}".format(
                    **item
                )
            )
    return 1 if args.strict and report["blocker_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
