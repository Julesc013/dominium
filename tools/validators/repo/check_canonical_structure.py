#!/usr/bin/env python3
"""Validate high-signal canonical structure invariants.

This validator is intentionally bounded. It fails hard on retired active paths
that have clear canonical routes, and reports remaining taxonomy work as
warnings unless --strict-final is requested.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import fnmatch
import json
import os
import subprocess
import sys


ALLOWED_ACTIVE_ROOTS = {
    ".aide",
    ".aide.local.example",
    ".github",
    ".vscode",
    "apps",
    "engine",
    "game",
    "runtime",
    "contracts",
    "content",
    "docs",
    "tests",
    "tools",
    "scripts",
    "cmake",
    "external",
    "release",
    "archive",
}

ALLOWED_ROOT_FILES = {
    ".agentignore",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CMakeLists.txt",
    "CMakePresets.json",
    "CODE_CHANGE_JUSTIFICATION.md",
    "CONTRIBUTING.md",
    "DOMINIUM.md",
    "GOVERNANCE.md",
    "LICENSE.md",
    "MODDING.md",
    "README.md",
    "SECURITY.md",
    "sitecustomize.py",
}

ALLOWED_ROOT_FILE_PATTERNS = ("VERSION_*",)

FORBIDDEN_ACTIVE_ROOTS = {
    "src",
    "source",
    "sources",
    "core",
    "control",
    "data",
    "packs",
    "profiles",
    "bundles",
    "compat",
    "lib",
    "libs",
    "locks",
    "repo",
    "safety",
    "security",
    "specs",
    "updates",
    "meta",
    "governance",
    "performance",
    "validation",
    "modding",
    "models",
    "templates",
    "net",
    "ide",
    "modules",
    "plugins",
    "services",
    "workspaces",
    "sdk",
}

GENERATED_LOCAL_ROOTS = {
    ".aide.local",
    ".dominium.local",
    "build",
    "out",
    "dist",
    "artifacts",
    "reports",
    "tmp",
    "__pycache__",
}

OLD_TEST_ROOTS = {
    "app": "tests/apps",
    "control": "tests/runtime/control",
    "data_1": "tests/contract/data1",
    "renderer": "tests/runtime/render",
    "schema": "tests/contract/schema",
    "share": "tests/packaging/share",
    "systemic": "tests/integration/systemic",
    "testx": "tests/tools/testx",
    "tourist": "tests/integration/tourist",
    "ui_parity": "tests/runtime/ui/parity",
}

FINAL_TEST_ROOTS = {
    "apps",
    "compat",
    "contract",
    "fixtures",
    "golden",
    "integration",
    "migration",
    "packaging",
    "performance",
    "replay",
    "runtime",
    "smoke",
    "tools",
    "unit",
    "validation",
}

RUNTIME_RETIRED_PREFIXES = {
    "runtime/render/soft": "runtime/render/software",
    "runtime/render/stub": "runtime/render/null",
    "runtime/render/client/renderers": "runtime/render/backend",
    "runtime/shell/commands": "runtime/shell/command",
    "runtime/shell/ui_backends": "runtime/ui/backend",
    "runtime/capability/capability": "runtime/capability/core",
    "runtime/ui/core": "runtime/ui/service or a precise runtime/ui area",
    "runtime/ui/tui": "runtime/projection/text",
    "runtime/ui/dui": "runtime/ui or archive after classification",
    "runtime/ui/ir": "contracts/view or runtime/view",
    "runtime/render/vector2d": "runtime/render/draw",
}

ENGINE_INCLUDE_RETIRED_PREFIXES = {
    "engine/include/domino/app": "runtime/include/domino/shell or contracts/app",
    "engine/include/domino/cli": "runtime/include/domino/command",
    "engine/include/domino/gui": "runtime/include/domino/ui",
    "engine/include/domino/input": "runtime/include/domino/input",
    "engine/include/domino/io": "runtime/include/domino/storage or runtime/include/domino/platform",
    "engine/include/domino/pkg": "runtime/include/domino/package or contracts/package",
    "engine/include/domino/render": "runtime/include/domino/render",
    "engine/include/domino/tui": "runtime/include/domino/ui",
    "engine/include/domino/world": "game/include/dominium/world or documented shared namespace",
    "engine/include/render": "runtime/include/domino/render",
}

CONTENT_RETIRED_PREFIXES = {
    "content/domain-data": "content/domains or content/packs",
    "content/data": "content/<canonical-root> or tests/fixtures",
    "content/domains/game/core": "content/domains/<canonical-domain>",
}

PRESENTATION_CONTRACT_ROOTS = {
    "contracts/command",
    "contracts/action",
    "contracts/result",
    "contracts/refusal",
    "contracts/diagnostic",
    "contracts/diagnostics",
    "contracts/document",
    "contracts/patch",
    "contracts/view",
    "contracts/presentation",
}

RUNTIME_PROJECTION_ROOTS = {
    "runtime/projection/cli",
    "runtime/projection/text",
    "runtime/projection/rendered",
    "runtime/projection/native",
    "runtime/projection/headless",
}

FINITE_EXCEPTION_PREFIXES = {
    "runtime/ui/client": "documented reusable client UI-facing systems; route remains pending a focused runtime/ui versus apps/client decision",
    "contracts/schema/tool": "explicitly retained schema tool bucket in current taxonomy",
}

SCHEMA_LEGACY_BUCKETS = {
    "astro": "contracts/schema/domain/astronomy",
    "client": "contracts/schema/runtime/client or contracts/app",
    "engine": "contracts/schema/engine or contracts/abi",
    "meta": "contracts/schema/repo or contracts/schema/governance",
    "server": "contracts/schema/runtime/server or contracts/app",
    "shell": "contracts/schema/runtime/shell",
    "syscaps": "contracts/schema/capability",
    "system": "contracts/schema/runtime or contracts/schema/domain",
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
        raise SystemExit(result.returncode)
    return [posix(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def tracked_dirs(paths):
    dirs = set()
    for path in paths:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:index]))
    return dirs


def root_allowed_file(path):
    if "/" in path:
        return False
    if path in ALLOWED_ROOT_FILES:
        return True
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in ALLOWED_ROOT_FILE_PATTERNS)


def add(findings, severity, path, code, message, target=""):
    findings.append(
        {
            "severity": severity,
            "path": path,
            "code": code,
            "message": message,
            "target": target,
        }
    )


def has_prefix(path, prefix):
    return path == prefix or path.startswith(prefix + "/")


def check_prefixes(paths_and_dirs, prefixes, findings, code):
    for path in sorted(paths_and_dirs):
        for prefix, target in sorted(prefixes.items()):
            if has_prefix(path, prefix):
                add(
                    findings,
                    "blocker",
                    path,
                    code,
                    "retired active path remains under {0}".format(prefix),
                    target,
                )
                break


def build_report(repo_root, max_findings):
    tracked = git_files(repo_root)
    tracked_set = set(tracked)
    dirs = tracked_dirs(tracked)
    paths_and_dirs = tracked_set | dirs
    findings = []

    for path in sorted(tracked):
        root = path.split("/", 1)[0]
        if "/" not in path:
            if root_allowed_file(path):
                continue
            add(findings, "blocker", path, "unexpected_root_file", "unexpected tracked root file")
            continue
        if root in FORBIDDEN_ACTIVE_ROOTS:
            add(findings, "blocker", root, "forbidden_active_root", "forbidden active top-level root", "archive or canonical root")
        elif root in GENERATED_LOCAL_ROOTS:
            add(findings, "blocker", root, "tracked_generated_local_root", "generated or local root is tracked", "archive/generated or untracked local state")
        elif root not in ALLOWED_ACTIVE_ROOTS:
            add(findings, "blocker", root, "unexpected_active_root", "tracked path is outside the active root allowlist")

    check_prefixes(paths_and_dirs, RUNTIME_RETIRED_PREFIXES, findings, "retired_runtime_path")
    check_prefixes(paths_and_dirs, ENGINE_INCLUDE_RETIRED_PREFIXES, findings, "retired_engine_include_path")
    check_prefixes(paths_and_dirs, CONTENT_RETIRED_PREFIXES, findings, "retired_content_path")

    for path in sorted(paths_and_dirs):
        if has_prefix(path, "game/rules") or has_prefix(path, "game/include/dominium/rules"):
            add(findings, "blocker", path, "retired_game_rules_path", "game/rules paths are retired", "game/rule, game/law, or game/domain")
        if path.startswith("tests/"):
            parts = path.split("/")
            if len(parts) >= 2 and parts[1] in OLD_TEST_ROOTS:
                add(findings, "blocker", "tests/" + parts[1], "retired_test_root", "retired test root remains active", OLD_TEST_ROOTS[parts[1]])

    for prefix, reason in sorted(FINITE_EXCEPTION_PREFIXES.items()):
        if any(has_prefix(path, prefix) for path in paths_and_dirs):
            add(findings, "warning", prefix, "finite_exception", reason)

    for root in sorted(SCHEMA_LEGACY_BUCKETS):
        prefix = "contracts/schema/" + root
        if any(has_prefix(path, prefix) for path in paths_and_dirs):
            add(
                findings,
                "warning",
                prefix,
                "schema_taxonomy_debt",
                "legacy schema bucket remains and needs a focused schema taxonomy route",
                SCHEMA_LEGACY_BUCKETS[root],
            )

    for path in sorted(tracked):
        if path.startswith("tests/"):
            parts = path.split("/")
            if len(parts) >= 2 and "." not in parts[1] and parts[1] not in FINAL_TEST_ROOTS:
                add(
                    findings,
                    "warning",
                    "tests/" + parts[1],
                    "test_taxonomy_debt",
                    "test first-level root is outside the final proof taxonomy",
                    "tests/<proof-type>",
                )

    if "sitecustomize.py" in tracked_set:
        add(
            findings,
            "warning",
            "sitecustomize.py",
            "root_file_finite_exception",
            "root Python bootstrap is documented by docs/repo/ROOT_FILE_POLICY.md",
            "keep documented or retire in a focused bootstrap pass",
        )

    for root in sorted(PRESENTATION_CONTRACT_ROOTS):
        if root not in dirs and root not in tracked_set:
            add(findings, "warning", root, "missing_presentation_contract_root", "presentation contract root is absent")

    for root in sorted(RUNTIME_PROJECTION_ROOTS):
        if root not in dirs and root not in tracked_set:
            add(findings, "warning", root, "missing_runtime_projection_root", "runtime projection mode root is absent")

    if any(path.startswith("apps/workbench/") for path in tracked):
        for root in ("apps/workbench/module", "apps/workbench/workspace", "apps/workbench/shell"):
            if root not in dirs and root not in tracked_set:
                add(
                    findings,
                    "warning",
                    root,
                    "workbench_split_incomplete",
                    "Workbench final split expects shell/module/workspace when content exists",
                )

    unique = {}
    for item in findings:
        key = (item["severity"], item["path"], item["code"], item["target"])
        unique[key] = item
    findings = sorted(unique.values(), key=lambda item: (item["severity"] != "blocker", item["path"], item["code"]))
    blocker_count = sum(1 for item in findings if item["severity"] == "blocker")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    status = "BLOCKED" if blocker_count else "PASS_WITH_WARNINGS" if warning_count else "PASS"
    return {
        "schema_version": "dominium.repo.canonical_structure.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": status,
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "finding_count": len(findings),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate canonical structure hard blockers.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail on hard blockers.")
    parser.add_argument("--strict-final", action="store_true", help="Fail on blockers or warnings.")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("canonical structure: {0}".format(report["status"]))
        for item in report["findings"]:
            record = dict(item)
            record["target_text"] = " -> {0}".format(item["target"]) if item.get("target") else ""
            print("{severity} {path}: {code}: {message}{target_text}".format(**record))

    if args.strict_final and report["finding_count"]:
        return 1
    if args.strict and report["blocker_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
