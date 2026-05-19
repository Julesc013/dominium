#!/usr/bin/env python3
"""Validate that tools/ uses canonical role-based first-level roots."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


ALLOWED_ROOTS = {
    "aide",
    "audit",
    "build",
    "codegen",
    "diagnostics",
    "domain",
    "export",
    "import",
    "migration",
    "package",
    "performance",
    "release",
    "repo",
    "test",
    "validators",
    "xstack",
}

ALLOWED_TOP_LEVEL_FILES = {"__init__.py", "CMakeLists.txt"}

SUGGESTED_ROOT_TARGETS = {
    "_shared": "tools/build/host",
    "appshell": "runtime/shell or tools/validators/shell/codegen/shell",
    "blueprint_editor": "apps/workbench/module/blueprint/editor",
    "core": "split into tools/repo, tools/build, tools/validators, or runtime/game/contracts",
    "data": "tools/import/data or content/<owner>",
    "editor_gui": "apps/workbench/module/<module>/editor or runtime/ui",
    "engine": "tools/validators/engine or engine/<owner>",
    "game_edit": "apps/workbench/module/game/editor",
    "gui": "apps/workbench/module/<module>/<role> or runtime/ui",
    "item_editor": "apps/workbench/module/domain/item/editor",
    "launcher": "tools/package/launcher or apps/launcher",
    "launcher_edit": "apps/workbench/module/launcher/editor",
    "lib": "split into tools/package/libraries/<area> or runtime/<owner>",
    "net": "tools/test/network or tools/validators/network",
    "network": "tools/test/network or tools/validators/network",
    "pack_editor": "apps/workbench/module/pack/editor",
    "policy_editor": "apps/workbench/module/policy/editor",
    "process_editor": "apps/workbench/module/process/editor",
    "render": "tools/validators/render or runtime/render",
    "replay_analyzer": "apps/workbench/module/replay/analyzer",
    "replay_viewer": "apps/workbench/module/replay/viewer",
    "runtime": "runtime/<subsystem>",
    "save_edit": "apps/workbench/module/save/editor",
    "save_inspector": "apps/workbench/module/save/inspector",
    "server": "tools/test/server or apps/server",
    "setup": "tools/package/setup or apps/setup",
    "share": "tools/export/share",
    "struct_editor": "apps/workbench/module/domain/structure/editor",
    "tech_editor": "apps/workbench/module/domain/technology/editor",
    "tests": "tools/test or tests/<family>",
    "tool_editor": "apps/workbench/module/tooling/editor",
    "transport_editor": "apps/workbench/module/domain/transport/editor",
    "ui_bind": "tools/codegen/ui",
    "ui_editor": "apps/workbench/module/ui/editor",
    "ui_preview_host": "apps/workbench/module/ui/preview",
    "ui_shared": "runtime/ui or tools/codegen/ui based on content",
    "universe_editor": "apps/workbench/module/domain/universe/editor",
    "validate": "tools/validators",
    "validation": "tools/validators",
    "validator": "tools/validators",
    "world_edit": "apps/workbench/module/world/editor",
    "world_editor": "apps/workbench/module/world/editor",
    "worldgen_offline": "tools/domain/worldgen/offline",
}

DOMAIN_ROOTS = {
    "animal": "tools/domain/animals",
    "astro": "tools/domain/astronomy",
    "chem": "tools/domain/chemistry",
    "electric": "tools/domain/electricity",
    "fields": "tools/domain/fields",
    "fluid": "tools/domain/fluids",
    "geo": "tools/domain/geology",
    "geology": "tools/domain/geology",
    "materials": "tools/domain/materials",
    "mechanics": "tools/domain/mechanics",
    "physics": "tools/domain/physics",
    "thermal": "tools/domain/thermal",
    "worldgen": "tools/domain/worldgen",
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
        ["git", "ls-files", "tools"],
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


def _suggest_for_root(root):
    if root in SUGGESTED_ROOT_TARGETS:
        return SUGGESTED_ROOT_TARGETS[root]
    if root in DOMAIN_ROOTS:
        return DOMAIN_ROOTS[root]
    if root.endswith("_editor"):
        return "apps/workbench/module/{}/editor".format(root[:-7].replace("_", "/"))
    if root.endswith("_viewer"):
        return "apps/workbench/module/{}/viewer".format(root[:-7].replace("_", "/"))
    if root.endswith("_inspector"):
        return "apps/workbench/module/{}/inspector".format(root[:-10].replace("_", "/"))
    return "tools/<aide|audit|build|codegen|import|export|migration|package|release|repo|test|validators|xstack|domain>"


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


def build_findings(paths):
    candidates = set(paths) | tracked_directories(paths)
    findings = []

    for path in sorted(candidates):
        if not path.startswith("tools/"):
            continue
        parts = path.split("/")
        if len(parts) == 2:
            name = parts[1]
            if "." in name and name not in ALLOWED_TOP_LEVEL_FILES:
                _add(
                    findings,
                    path,
                    "tooling_file_at_tools_root",
                    "tools/ root should expose role directories, not ad hoc root-level tool implementations.",
                    "tools/<role>/<area>/{}".format(name),
                )
            continue

        root = parts[1]
        if root in ALLOWED_ROOTS:
            continue

        _add(
            findings,
            "tools/{}".format(root),
            "noncanonical_tools_root",
            "tools/ first-level directories must be durable tool roles, not source/product/runtime/domain mirrors.",
            _suggest_for_root(root),
        )

    unique = {}
    for item in findings:
        unique[(item["path"], item["disposition"], item["suggested_target"])] = item
    return sorted(unique.values(), key=lambda item: (item["path"], item["disposition"]))


def build_report(repo_root, max_findings):
    tracked = git_files(repo_root)
    findings = build_findings(tracked)
    blocker_count = len(findings)
    return {
        "schema_version": "dominium.repo.tools.taxonomy.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS",
        "allowed_roots": sorted(ALLOWED_ROOTS),
        "finding_count": blocker_count,
        "blocker_count": blocker_count,
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def self_test():
    cases = [
        (["tools/validator/check.py"], True),
        (["tools/validators/check.py"], False),
        (["tools/world_editor/main.cpp"], True),
        (["apps/workbench/module/world/editor/main.cpp"], False),
        (["tools/domain/geology/tool.py"], False),
        (["tools/render/backend.cpp"], True),
        (["tools/CMakeLists.txt", "tools/__init__.py"], False),
        (["tools/random.py"], True),
    ]
    for paths, should_fail in cases:
        failed = bool(build_findings(paths))
        if failed != should_fail:
            raise AssertionError("unexpected tools taxonomy result for {0}: {1}".format(paths, failed))


def main():
    parser = argparse.ArgumentParser(description="Validate tools taxonomy.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("tools taxonomy self-test: PASS")
        return 0

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("tools taxonomy: {0}".format(report["status"]))
        for item in report["findings"]:
            print("{severity} {path}: {reason} -> {suggested_target}".format(**item))
    return 1 if args.strict and report["blocker_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
