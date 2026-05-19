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

FORBIDDEN_ACTIVE_PATH_PREFIXES = {
    "runtime/render/client": "runtime render client bucket retired; use runtime/render/backend",
    "runtime/render/soft": "soft is an abbreviation; use runtime/render/software",
    "runtime/render/stub": "stub is status wording; use runtime/render/null",
    "runtime/shell/commands": "shell command subsystem is singular runtime/shell/command",
    "runtime/shell/ui_backends": "UI backend implementation belongs under runtime/ui/backend",
    "runtime/capability/capability": "capability/capability is tautological; use runtime/capability/core or a precise leaf",
    "runtime/ui/core": "runtime/ui/core is vague; use runtime/ui/service or a precise UI leaf",
    "apps/workbench/module/game/edit": "Workbench game editor module is noun-based apps/workbench/module/game/editor",
    "apps/workbench/module/tool/editor": "Workbench tool editor is ambiguous; use apps/workbench/module/tooling/editor or route tooling out of Workbench",
    "apps/workbench/module/ui/editor/gen": "Workbench UI editor uses generated as the checked-in generated binding bucket",
    "apps/workbench/module/ui/native": "Native Workbench UI host belongs under apps/workbench/module/ui/preview/native or reusable runtime UI/platform owners",
    "apps/workbench/module/ui/preview/support": "Workbench UI preview shared helpers use apps/workbench/module/ui/preview/service",
    "engine/include/domino/app": "engine/include must not export runtime/app headers; use runtime/include/domino/shell or an app-owned include path",
    "engine/include/domino/audio.h": "engine/include must not export audio runtime headers; use runtime/include/domino/audio.h",
    "engine/include/domino/canvas.h": "engine/include must not export canvas/render runtime headers; use runtime/include/domino/canvas.h",
    "engine/include/domino/cli": "engine/include must not export CLI shell headers; use runtime/include/domino/shell/command or an app-owned include path",
    "engine/include/domino/gfx.h": "engine/include must not export render runtime headers; use runtime/include/domino/gfx.h",
    "engine/include/domino/gui": "engine/include must not export GUI/UI headers; use runtime/include/domino/ui or runtime/include/domino/platform",
    "engine/include/domino/input": "engine/include must not export input runtime headers; use runtime/include/domino/input",
    "engine/include/domino/io": "engine/include must not export IO/storage runtime headers; use runtime/include/domino/storage or runtime/include/domino/platform/io",
    "engine/include/domino/mod.h": "engine/include must not export package/mod runtime headers; use runtime/include/domino/mod.h",
    "engine/include/domino/pkg": "engine/include must not export package runtime headers; use runtime/include/domino/package or contracts/package",
    "engine/include/domino/render": "engine/include must not export render runtime headers; use runtime/include/domino/render",
    "engine/include/domino/tui": "engine/include must not export TUI runtime headers; use runtime/include/domino/ui/tui or runtime/include/domino/shell/tui",
    "engine/include/domino/world": "engine/include must not export game/world headers; use game/include/dominium/world or game/include/domino/world by documented convention",
    "engine/include/render": "engine/include must not export render runtime headers; use runtime/include/domino/render",
    "contracts/schema/compat": "schema compatibility contracts use contracts/schema/compatibility",
    "contracts/schema/core": "schema/core is an old-root bucket; route each schema to engine, runtime, domain, repo, or another canonical owner",
    "contracts/schema/diag": "diagnostic runtime schemas use contracts/schema/runtime/diagnostics or contracts/schema/diagnostics",
    "contracts/schema/lib": "schema/lib is an old wrapper bucket; route schemas to install, package, profile, save, runtime, or repo owners",
    "contracts/schema/models": "schema/models is ambiguous; use contracts/schema/domain/modeling or a precise canonical owner",
    "contracts/schema/mods": "modding package schemas use contracts/schema/package/modding",
    "contracts/schema/render": "render schemas use contracts/schema/runtime/render",
    "contracts/schema/specs": "spec/compliance schemas use contracts/schema/validation/specs or a precise canonical owner",
    "contracts/schema/material": "material schemas use the plural canonical domain path contracts/schema/domain/materials",
    "contracts/schema/materials": "materials schemas use contracts/schema/domain/materials, not a root-level duplicate",
    "contracts/schema/chem": "chemistry schemas use contracts/schema/domain/chemistry",
    "contracts/schema/geo": "geology schemas use contracts/schema/domain/geology",
    "contracts/schema/fluid": "fluid schemas use contracts/schema/domain/fluids",
    "contracts/schema/civ": "civilization schemas use contracts/schema/domain/civilization",
    "contracts/schema/civilisation": "civilization schemas use contracts/schema/domain/civilization",
    "contracts/schema/electric": "electricity schemas use contracts/schema/domain/electricity",
    "contracts/schema/physical": "physical schemas use contracts/schema/domain/physics or contracts/schema/domain/mechanics",
    "contracts/schema/fab": "fabrication schemas use contracts/schema/domain/fabrication",
    "contracts/schema/tech": "technology schemas use contracts/schema/domain/technology",
    "contracts/schema/technology": "technology schemas use contracts/schema/domain/technology",
    "contracts/schema/packs": "package/pack schemas use contracts/schema/package",
    "contracts/schema/net": "network schemas use contracts/schema/runtime/network or contracts/schema/protocol/network",
    "contracts/schema/control": "control schemas use contracts/schema/runtime/control, governance, or policy owners",
    "contracts/schema/tools": "tool schemas use contracts/schema/tool",
    "contracts/schema/validator": "validator schemas use contracts/schema/validation",
    "content/domains/game/core": "domain content lives directly under content/domains/<canonical-domain>, not game/core",
    "content/domains/worldgen/real/earth/content": "worldgen real-earth domain content should not use a nested content wrapper",
    "content/domains/worldgen/real/milky_way/content": "worldgen real-milky-way domain content should not use a nested content wrapper",
    "content/domains/worldgen/real/sol_system/content": "worldgen real-sol-system domain content should not use a nested content wrapper",
    "content/packs/blueprints": "pack category is singular content/packs/blueprint",
    "content/packs/specs": "pack category is singular content/packs/spec",
    "content/packs/physics": "physics packs belong under content/packs/domain",
    "content/packs/system_templates": "system template packs belong under content/packs/core or another canonical pack category",
    "content/packs/compatibility_payload": "executable package compatibility tooling belongs under tools/validators/package",
}

PACK_CONTRACT_GUARD_PREFIX = "contracts/package/packs/"
PACK_CONTRACT_GUARD_README = "contracts/package/packs/README.md"

SCHEMA_DUPLICATE_PATH_GROUPS = (
    (
        "chemistry",
        ("contracts/schema/chem", "contracts/schema/chemistry"),
        "contracts/schema/domain/chemistry",
    ),
    (
        "geology",
        ("contracts/schema/geo", "contracts/schema/geology"),
        "contracts/schema/domain/geology",
    ),
    (
        "fluids",
        ("contracts/schema/fluid", "contracts/schema/fluids"),
        "contracts/schema/domain/fluids",
    ),
    (
        "civilization",
        ("contracts/schema/civ", "contracts/schema/civilisation", "contracts/schema/civilization"),
        "contracts/schema/domain/civilization",
    ),
    (
        "materials",
        ("contracts/schema/material", "contracts/schema/materials"),
        "contracts/schema/domain/materials",
    ),
    (
        "tool",
        ("contracts/schema/tools",),
        "contracts/schema/tool",
    ),
)


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
    tracked_files = git_files(repo_root)
    tracked_paths = set(tracked_files)
    tracked_dirs = set()
    for path in tracked_files:
        segments = path.split("/")[:-1]
        for index in range(1, len(segments) + 1):
            tracked_dirs.add("/".join(segments[:index]))

    for domain_name, retired_roots, canonical_root in SCHEMA_DUPLICATE_PATH_GROUPS:
        active_retired = [
            root for root in retired_roots
            if root in tracked_dirs or root in tracked_paths
        ]
        canonical_present = canonical_root in tracked_dirs or canonical_root in tracked_paths
        if active_retired and canonical_present:
            for root in active_retired:
                reason = "{0} schemas must not be split between {1} and {2}".format(
                    domain_name,
                    root,
                    canonical_root,
                )
                findings.append({
                    "path": root,
                    "segment": root,
                    "segment_index": -1,
                    "severity": "blocker",
                    "disposition": "schema_duplicate_spelling",
                    "reason": reason,
                    "rule": "schema_duplicate_path_group",
                })
                counts[root] = counts.get(root, 0) + 1

    for path in tracked_files:
        if path.startswith(PACK_CONTRACT_GUARD_PREFIX) and path != PACK_CONTRACT_GUARD_README:
            reason = (
                "contracts/package/packs is guard-only; authored pack payloads belong under "
                "content/packs and fixtures under tests/fixtures/package"
            )
            findings.append({
                "path": path,
                "segment": "contracts/package/packs",
                "segment_index": -1,
                "severity": "blocker",
                "disposition": "pack_authority_violation",
                "reason": reason,
                "rule": "pack_authority_guard",
            })
            counts["contracts/package/packs"] = counts.get("contracts/package/packs", 0) + 1
        for prefix, reason in sorted(FORBIDDEN_ACTIVE_PATH_PREFIXES.items()):
            if path == prefix or path.startswith(prefix + "/"):
                findings.append({
                    "path": path,
                    "segment": prefix,
                    "segment_index": -1,
                    "severity": "blocker",
                    "disposition": "retired_runtime_path",
                    "reason": reason,
                    "rule": "retired_runtime_path",
                })
                counts[prefix] = counts.get(prefix, 0) + 1
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
