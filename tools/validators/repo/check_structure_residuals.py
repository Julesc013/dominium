#!/usr/bin/env python3
"""Classify remaining repo-structure residuals without moving source trees.

This validator is deliberately conservative. It blocks authority violations
that are mechanically knowable, and records unresolved taxonomy work as
warnings tied to focused follow-up tasks.
"""

from __future__ import print_function

import argparse
import datetime as _datetime
import json
import os
import subprocess
import sys


DOC_REF = "docs/repo/structure_residual_classification.md"

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

RUNTIME_RESIDUALS = {
    "engine/compatx": (
        "CompatX core policy/validator implementation; not a generic engine compatibility bucket",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
    "engine/foundation": (
        "deterministic substrate pending a focused boundary review; must not become core/common catch-all",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
    "engine/serialization": (
        "deterministic engine serialization only; replay/save/protocol ownership remains separate",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
    "engine/session": (
        "engine-side session common code pending runtime/app boundary review",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
    "runtime/compatx": (
        "runtime-facing CompatX adapter/validator surface; not a payload or migration bucket",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
    "runtime/serialization": (
        "runtime canonical JSON utilities; must not subsume contracts/protocol/save/replay authority",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
    "runtime/session": (
        "runtime session protocol/common surface; not promoted truth",
        "RUNTIME-RESIDUAL-TAXONOMY-01",
    ),
}

SCHEMA_RESIDUAL_ROOTS = {}

RUNTIME_PROJECTION_ROOTS = {
    "runtime/projection/cli": "PROJECTION-CONFORMANCE-01",
    "runtime/projection/headless": "PROJECTION-CONFORMANCE-01",
    "runtime/projection/native": "PROJECTION-CONFORMANCE-01",
}

AIDE_STATE_LIKE_ROOTS = {
    "cache",
    "ledgers",
    "models",
    "providers",
    "queue",
    "release",
    "reports",
    "tools",
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


def has_prefix(path, prefix):
    return path == prefix or path.startswith(prefix + "/")


def add(findings, severity, path, code, message, target=""):
    findings.append(
        {
            "severity": severity,
            "path": path,
            "code": code,
            "message": message,
            "target": target,
            "doc": DOC_REF,
        }
    )


def pack_leaf(path):
    parts = path.split("/")
    if len(parts) < 4 or parts[0] != "content" or parts[1] != "packs":
        return None
    if parts[2] == "README.md" or "." in parts[2]:
        return None
    return "/".join(parts[:4])


def build_report(repo_root, max_findings):
    tracked = git_files(repo_root)
    tracked_set = set(tracked)
    dirs = tracked_dirs(tracked)
    paths_and_dirs = tracked_set | dirs
    findings = []

    for path in sorted(tracked):
        if path.startswith("contracts/package/packs/"):
            rel = path[len("contracts/package/packs/") :]
            if "/" in rel or not rel.endswith(".md"):
                add(
                    findings,
                    "blocker",
                    path,
                    "pack_contract_payload_authority_drift",
                    "contracts/package/packs may contain contract notes only, not authored pack payloads",
                    "content/packs or tests/fixtures/package",
                )

    if any(has_prefix(path, "contracts/diagnostics") for path in paths_and_dirs):
        add(
            findings,
            "blocker",
            "contracts/diagnostics",
            "retired_diagnostics_plural",
            "diagnostic contract root is singular",
            "contracts/diagnostic",
        )

    for local_root in (".aide.local", ".dominium.local", "tmp"):
        if any(has_prefix(path, local_root) for path in paths_and_dirs):
            add(
                findings,
                "blocker",
                local_root,
                "tracked_local_state",
                "local/generated state root is tracked",
                "untracked local root or archive/generated",
            )

    legacy_content_by_category = {}
    for path in sorted(tracked):
        leaf = pack_leaf(path)
        if not leaf:
            continue
        rest = path[len(leaf) + 1 :].split("/")
        if rest and rest[0] == "content":
            category = leaf.split("/")[2]
            legacy_content_by_category.setdefault(category, set()).add(leaf)
    for category, leaves in sorted(legacy_content_by_category.items()):
        add(
            findings,
            "warning",
            "content/packs/{0}".format(category),
            "pack_internal_content_root_classified",
            "{0} pack(s) use pack-local content/ payload roots; classified as legacy pack payload layout pending focused normalization".format(
                len(leaves)
            ),
            "PACK-INTERNAL-LAYOUT-CANON-01",
        )

    for path, classification in sorted(RUNTIME_RESIDUALS.items()):
        if any(has_prefix(candidate, path) for candidate in paths_and_dirs):
            message, target = classification
            add(findings, "warning", path, "runtime_residual_classified", message, target)

    schema_roots = sorted(
        path.split("/")[2]
        for path in dirs
        if path.startswith("contracts/schema/") and len(path.split("/")) == 3
    )
    if len(schema_roots) > 40:
        add(
            findings,
            "warning",
            "contracts/schema",
            "schema_taxonomy_broad",
            "contracts/schema has {0} first-level schema buckets; classify before further moves".format(len(schema_roots)),
            "SCHEMA-CANON-RESIDUAL-02",
        )
    for path, target in sorted(SCHEMA_RESIDUAL_ROOTS.items()):
        if any(has_prefix(candidate, path) for candidate in paths_and_dirs):
            add(
                findings,
                "warning",
                path,
                "schema_residual_classified",
                "legacy schema bucket remains pending focused schema canon pass",
                target,
            )

    if any(has_prefix(path, "runtime/projection") for path in paths_and_dirs):
        for path, target in sorted(RUNTIME_PROJECTION_ROOTS.items()):
            if not any(has_prefix(candidate, path) for candidate in paths_and_dirs):
                add(
                    findings,
                    "warning",
                    path,
                    "runtime_projection_root_deferred",
                    "runtime projection mode root is absent; do not create placeholders without projection conformance scope",
                    target,
                )

    if any(has_prefix(path, "apps/workbench") for path in paths_and_dirs) and not any(
        has_prefix(path, "apps/workbench/shell") for path in paths_and_dirs
    ):
        add(
            findings,
            "warning",
            "apps/workbench/shell",
            "workbench_shell_deferred",
            "Workbench shell root is deferred until real shell ownership exists",
            "WORKBENCH-SHELL-STRUCTURE-01",
        )

    aide_roots = sorted(
        path.split("/")[1]
        for path in dirs
        if path.startswith(".aide/") and len(path.split("/")) == 2
    )
    state_like = [root for root in aide_roots if root in AIDE_STATE_LIKE_ROOTS]
    if state_like:
        add(
            findings,
            "warning",
            ".aide",
            "aide_state_like_roots_classified",
            "tracked AIDE roots classified as control-plane/evidence roots: {0}".format(", ".join(state_like)),
            "AIDE-STATE-CLASSIFICATION-01",
        )

    test_roots = sorted(
        path.split("/")[1]
        for path in dirs
        if path.startswith("tests/") and len(path.split("/")) == 2
    )
    non_final_test_roots = [root for root in test_roots if root not in FINAL_TEST_ROOTS]
    if non_final_test_roots:
        add(
            findings,
            "warning",
            "tests",
            "test_taxonomy_residual_classified",
            "test roots outside final proof taxonomy remain non-blocking: {0}".format(", ".join(non_final_test_roots)),
            "targeted tests taxonomy cleanup after product gates",
        )

    unique = {}
    for item in findings:
        key = (item["severity"], item["path"], item["code"], item["target"])
        unique[key] = item
    findings = sorted(unique.values(), key=lambda item: (item["severity"] != "blocker", item["path"], item["code"]))
    blocker_count = sum(1 for item in findings if item["severity"] == "blocker")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "schema_version": "dominium.repo.structure_residuals.v1",
        "generated_utc": utc_now(),
        "repo_root": posix(os.path.abspath(repo_root)),
        "status": "BLOCKED" if blocker_count else "PASS_WITH_WARNINGS" if warning_count else "PASS",
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "finding_count": len(findings),
        "findings": findings[:max_findings],
        "truncated": len(findings) > max_findings,
    }


def main():
    parser = argparse.ArgumentParser(description="Classify canonical structure residuals.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail on blockers.")
    parser.add_argument("--strict-final", action="store_true", help="Fail on blockers or warnings.")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args()

    report = build_report(os.path.abspath(args.repo_root), args.max_findings)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    else:
        print("structure residuals: {0}".format(report["status"]))
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
