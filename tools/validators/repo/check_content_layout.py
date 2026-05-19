#!/usr/bin/env python3
"""Validate canonical authored content layout paths."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


ALLOWED_PACK_CATEGORIES = set([
    "blueprint",
    "core",
    "derived",
    "domain",
    "example",
    "experience",
    "law",
    "official",
    "reality",
    "representation",
    "spec",
    "tool",
    "worldgen",
])

PACK_ROOT_FILES = set([
    "README.md",
    "__init__.py",
])

PACK_MANIFEST_NAMES = set([
    "pack.json",
    "pack.manifest",
    "pack.toml",
    "pack_manifest.json",
])


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


def _add(findings, path, disposition, reason):
    findings.append({
        "path": path,
        "severity": "blocker",
        "disposition": disposition,
        "reason": reason,
    })


def build_report(repo_root, max_findings):
    tracked = git_files(repo_root)
    tracked_set = set(tracked)
    tracked_dirs = set()
    for path in tracked:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            tracked_dirs.add("/".join(parts[:index]))

    findings = []
    if "content/domains/game/core" in tracked_dirs or "content/domains/game/core" in tracked_set:
        _add(
            findings,
            "content/domains/game/core",
            "retired_domain_wrapper",
            "domain content lives directly under content/domains/<canonical-domain>",
        )

    for path in sorted(tracked_set | tracked_dirs):
        if not path.startswith("content/domains/"):
            continue
        parts = path.split("/")
        if len(parts) > 3 and "content" in parts[2:]:
            _add(
                findings,
                path,
                "nested_content_wrapper",
                "content/domains must not contain tautological nested content/ wrappers",
            )

    pack_category_dirs = set()
    pack_dirs = set()
    manifest_by_pack = {}
    for path in tracked:
        if not path.startswith("content/packs/"):
            continue
        parts = path.split("/")
        if len(parts) == 3 and parts[2] in PACK_ROOT_FILES:
            continue
        if len(parts) >= 3:
            category = parts[2]
            pack_category_dirs.add(category)
            if category not in ALLOWED_PACK_CATEGORIES:
                disposition = "flat_pack_id" if "." in category else "unknown_pack_category"
                reason = (
                    "content/packs uses content/packs/<category>/<pack_id>; "
                    "direct pack IDs and unknown categories are not allowed"
                )
                _add(findings, "content/packs/" + category, disposition, reason)
        if len(parts) >= 4 and parts[2] in ALLOWED_PACK_CATEGORIES:
            pack_key = "/".join(parts[:4])
            pack_dirs.add(pack_key)
            if len(parts) == 5 and parts[4] in PACK_MANIFEST_NAMES:
                manifest_by_pack.setdefault(pack_key, []).append(path)

    for directory in sorted(tracked_dirs):
        if not directory.startswith("content/packs/"):
            continue
        parts = directory.split("/")
        if len(parts) == 3:
            category = parts[2]
            pack_category_dirs.add(category)
            if category not in ALLOWED_PACK_CATEGORIES:
                disposition = "flat_pack_id" if "." in category else "unknown_pack_category"
                _add(
                    findings,
                    directory,
                    disposition,
                    "content/packs direct children must be documented pack categories",
                )
        elif len(parts) >= 4 and parts[2] in ALLOWED_PACK_CATEGORIES:
            pack_dirs.add("/".join(parts[:4]))

    for pack_dir in sorted(pack_dirs):
        if pack_dir not in manifest_by_pack:
            _add(
                findings,
                pack_dir,
                "missing_pack_manifest",
                "pack leaves under content/packs/<category>/<pack_id> need pack.json, pack.toml, pack.manifest, or pack_manifest.json",
            )

    findings.sort(key=lambda item: (item["path"], item["disposition"]))
    blocker_count = len(findings)
    return {
        "schema_version": "dominium.repo.content.layout.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS",
        "allowed_pack_categories": sorted(ALLOWED_PACK_CATEGORIES),
        "finding_count": blocker_count,
        "blocker_count": blocker_count,
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate canonical content layout.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("content layout: {}".format(report["status"]))
        for item in report["findings"]:
            print("{severity} {path}: {reason}".format(**item))
    return 1 if args.strict and report["blocker_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
