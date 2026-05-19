#!/usr/bin/env python3
"""Validate that docs/ uses canonical first-level documentation roots."""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


ALLOWED_ROOTS = {
    "apps",
    "architecture",
    "archive",
    "build",
    "compatibility",
    "content",
    "development",
    "distribution",
    "domains",
    "engine",
    "game",
    "governance",
    "modding",
    "operations",
    "performance",
    "reference",
    "release",
    "repo",
    "runtime",
    "safety",
    "security",
    "testing",
    "validation",
    "workbench",
}

FINITE_EXCEPTION_ROOTS = {
    "canon": "protected canonical doctrine path required by AGENTS.md authority order",
    "planning": "protected planning doctrine path required by AGENTS.md authority order",
}

ALLOWED_TOP_LEVEL_FILES = {"README.md", ".gitignore"}

SUGGESTED_ROOT_TARGETS = {
    "accessibility": "docs/runtime/ui/accessibility",
    "agents": "docs/game/agents or docs/governance/agents",
    "aide": "docs/development/aide",
    "app": "docs/apps or docs/runtime/shell",
    "appshell": "docs/runtime/shell",
    "audit": "docs/archive/audit or docs/repo/audits",
    "blueprint": "docs/archive/blueprint or docs/architecture",
    "ci": "docs/testing/ci",
    "civilisation": "docs/domains/civilization",
    "client": "docs/apps/client",
    "contracts": "docs/reference/contracts or contracts/<owner>",
    "control": "docs/governance/control",
    "core": "docs/architecture, docs/engine, docs/runtime, or docs/archive",
    "data": "docs/content or docs/archive",
    "diag": "docs/runtime/diagnostics or docs/operations/diagnostics",
    "diegetics": "docs/game/diegetics",
    "electric": "docs/domains/electricity",
    "embodiment": "docs/domains/embodiment",
    "epistemics": "docs/game/epistemics",
    "examples": "docs/reference/examples or docs/content/examples",
    "fields": "docs/domains/fields",
    "fluid": "docs/domains/fluids",
    "gameplay": "docs/game/gameplay",
    "geo": "docs/domains/geology",
    "glossary": "docs/reference/glossary",
    "guides": "docs/development/guides",
    "impact": "docs/archive/impact or docs/repo/impact",
    "infrastructure": "docs/domains/infrastructure",
    "interaction": "docs/game/interaction",
    "interior": "docs/domains/interiors",
    "knowledge": "docs/domains/knowledge",
    "launcher": "docs/apps/launcher",
    "lib": "docs/runtime/storage or docs/distribution",
    "logic": "docs/domains/logic",
    "materials": "docs/domains/materials",
    "mechanics": "docs/domains/mechanics",
    "meta": "docs/governance/meta",
    "mobility": "docs/domains/mobility",
    "mvp": "docs/release/mvp",
    "net": "docs/runtime/network",
    "omega": "docs/archive/omega",
    "ops": "docs/operations",
    "pack_format": "docs/distribution/package-format",
    "packs": "docs/content/packs or docs/modding/packs",
    "physical": "docs/domains/physics",
    "platform": "docs/runtime/platform",
    "player": "docs/game/player",
    "policies": "docs/governance/policies",
    "pollution": "docs/domains/pollution",
    "post_canon": "docs/archive/post-canon",
    "process": "docs/domains/processes",
    "prompts": "docs/archive/prompts",
    "realities": "docs/game/realities",
    "reality": "docs/domains/reality",
    "refactor": "docs/archive/refactor",
    "render": "docs/runtime/render",
    "repox": "docs/repo/repox",
    "restructure": "docs/archive/restructure",
    "roadmap": "docs/release/roadmap",
    "scale": "docs/domains/scale",
    "schema": "docs/reference/schema or contracts/schema",
    "server": "docs/apps/server",
    "settings": "docs/runtime/settings",
    "setup": "docs/apps/setup",
    "signals": "docs/domains/signals",
    "sol": "docs/domains/astronomy/sol",
    "specs": "docs/reference/specs or contracts/<owner>",
    "system": "docs/architecture/system",
    "time": "docs/engine/time or docs/runtime/time",
    "tools": "docs/development/tools or docs/workbench",
    "ui": "docs/runtime/ui",
    "universe": "docs/domains/universe",
    "ux": "docs/runtime/ui/ux",
    "visualization": "docs/runtime/render/visualization",
    "worldgen": "docs/domains/worldgen",
    "xstack": "docs/development/xstack",
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
        ["git", "ls-files", "docs"],
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
    return SUGGESTED_ROOT_TARGETS.get(root, "docs/<canonical-root>")


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
        if not path.startswith("docs/"):
            continue
        parts = path.split("/")
        if len(parts) == 2:
            name = parts[1]
            if "." in name and name not in ALLOWED_TOP_LEVEL_FILES:
                _add(
                    findings,
                    path,
                    "doc_file_at_docs_root",
                    "docs/ root should expose canonical documentation roots, not ad hoc root-level prose files.",
                    "docs/<canonical-root>/{}".format(name),
                )
            continue

        root = parts[1]
        if root in ALLOWED_ROOTS or root in FINITE_EXCEPTION_ROOTS:
            continue

        _add(
            findings,
            "docs/{}".format(root),
            "noncanonical_docs_root",
            "docs/ first-level directories must be durable documentation categories, not source-root mirrors or historical staging buckets.",
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
        "schema_version": "dominium.repo.docs.taxonomy.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS",
        "allowed_roots": sorted(ALLOWED_ROOTS),
        "finite_exception_roots": FINITE_EXCEPTION_ROOTS,
        "finding_count": blocker_count,
        "blocker_count": blocker_count,
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def self_test():
    cases = [
        (["docs/geo/GEOLOGY.md"], True),
        (["docs/domains/geology/GEOLOGY.md"], False),
        (["docs/appshell/SHELL.md"], True),
        (["docs/runtime/shell/SHELL.md"], False),
        (["docs/specs/schema.json"], True),
        (["docs/archive/specs/schema.json"], False),
        (["docs/README.md", "docs/.gitignore"], False),
        (["docs/random.md"], True),
        (["docs/canon/constitution_v1.md", "docs/planning/AUTHORITY_ORDER.md"], False),
    ]
    for paths, should_fail in cases:
        failed = bool(build_findings(paths))
        if failed != should_fail:
            raise AssertionError("unexpected docs taxonomy result for {0}: {1}".format(paths, failed))


def main():
    parser = argparse.ArgumentParser(description="Validate docs taxonomy.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("docs taxonomy self-test: PASS")
        return 0

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("docs taxonomy: {0}".format(report["status"]))
        for item in report["findings"]:
            print("{severity} {path}: {reason} -> {suggested_target}".format(**item))
    return 1 if args.strict and report["blocker_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
