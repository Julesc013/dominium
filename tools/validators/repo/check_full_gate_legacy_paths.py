#!/usr/bin/env python3
"""Validate that full-gate tests do not require retired active roots.

This is a narrow maintenance validator for FULL-GATE-LEGACY-TEST-ROUTE-01.
It checks the known full-gate tests that previously encoded pre-canon paths
as required active source paths, while also verifying that canonical structure
guards still reject the retired roots.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


FULL_GATE_EXPECTATIONS = [
    {
        "path": "tools/validators/ci/phase6_audit_checks.py",
        "forbidden": [
            r"docs/ci/CI_ENFORCEMENT_MATRIX\.md",
            r"os\.path\.join\(repo_root,\s*\"docs\",\s*\"ci\"",
        ],
        "required": ["docs/testing/ci/CI_ENFORCEMENT_MATRIX.md"],
    },
    {
        "path": "tests/integration/integration_meta_test.py",
        "forbidden": [
            r"docs/app/",
            r"docs/platform/",
            r"docs/render/",
            r"docs/repox/",
            r"runtime/app/app_runtime\.c",
            r"os\.path\.join\(repo_root,\s*\"runtime\",\s*\"app\"",
        ],
        "required": [
            '"docs", "apps", "README.md"',
            '"docs", "runtime", "platform", "README.md"',
            '"docs", "runtime", "render", "README.md"',
            '"docs", "repo", "repox", "APRX_INTEGRATION_HOOKS.md"',
            '"runtime", "shell", "lifecycle", "app_runtime.c"',
            '"docs", "apps", "CLI_CONTRACTS.md"',
        ],
    },
    {
        "path": "tests/contract/determinism_hardlock_tests.py",
        "forbidden": [
            r"game/rules",
            r"os\.path\.join\(repo_root,\s*\"game\",\s*\"rules\"",
        ],
        "required": [
            '"game", "domain", "fabrication", "fab_interpreters.cpp"',
            '"game", "domain", "scale", "scale_collapse_expand.cpp"',
            '"game", "domain"',
            '"game", "law"',
            '"game", "rule"',
        ],
    },
    {
        "path": "tests/contract/srz_contract_tests.py",
        "forbidden": [
            r"contracts/schemas",
            r"os\.path\.join\(repo_root,\s*\"contracts\",\s*\"schemas\"",
        ],
        "required": [
            '"contracts", "schema", "srz.zone.schema"',
            '"contracts", "schema", "process.log.schema"',
            '"contracts", "schema", "process.hashchain.schema"',
        ],
    },
    {
        "path": "tests/contract/capability_gating_contracts.py",
        "forbidden": [
            r"libs/appcore",
            r"os\.path\.join\(repo_root,\s*\"libs\",\s*\"appcore\"",
        ],
        "required": ['"runtime", "shell", "command", "command_registry.c"'],
    },
    {
        "path": "tests/apps/baseline_sku_tests.py",
        "forbidden": [
            r"contracts/schemas",
            r"os\.path\.join\(repo_root,\s*\"contracts\",\s*\"schemas\"",
        ],
        "required": ['"contracts", "schema", "capability_baseline.schema"'],
    },
    {
        "path": "tests/apps/modpack_workspace_tests.py",
        "forbidden": [
            r"os\.path\.join\(repo_root,\s*\"tools\",\s*\"modpack\"",
            r"os\.path\.join\(repo_root,\s*\"tools\",\s*\"workspace\"",
            r"tools/modpack/modpack_cli\.py",
            r"tools/workspace/workspace_cli\.py",
        ],
        "required": [
            '"tools", "package", "modpack", "modpack_cli.py"',
            '"tools", "repo", "workspace", "workspace_cli.py"',
        ],
    },
    {
        "path": "tests/distribution/distribution_legacy_platform_profiles_tests.py",
        "forbidden": [
            r"data/profiles",
            r"os\.path\.join\(repo_root,\s*\"data\",\s*\"profiles\"",
            r'"tools",\s*"distribution",\s*"compat_dry_run\.py"',
            r"tools/distribution/compat_dry_run\.py",
        ],
        "required": [
            '"content", "profiles"',
            '"tools", "package", "distribution", "compat_dry_run.py"',
        ],
    },
    {
        "path": "tests/distribution/distribution_sdk_profile_tests.py",
        "forbidden": [
            r"data/profiles",
            r"os\.path\.join\(repo_root,\s*\"data\",\s*\"profiles\"",
        ],
        "required": ['"content", "profiles"'],
    },
]

STRUCTURE_GUARD_EXPECTATIONS = [
    {
        "path": "tools/validators/repo/check_canonical_structure.py",
        "required": [
            "game/rules",
            "retired_game_rules_path",
            "FORBIDDEN_ACTIVE_ROOTS",
            '"data"',
            '"libs"',
            '"profiles"',
        ],
    },
    {
        "path": "tools/validators/repo/check_bad_root_absence.py",
        "required": ['"data"', '"libs"', '"profiles"'],
    },
]


def finding(level: str, code: str, message: str, path: Optional[str] = None) -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\\", "/")


def check_required_text(text: str, required: Iterable[str], path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for token in required:
        if token.replace("\\", "/") not in text:
            findings.append(
                finding(
                    "error",
                    "missing_canonical_route",
                    f"expected canonical route token is absent: {token}",
                    path,
                )
            )
    return findings


def check_forbidden_text(text: str, patterns: Iterable[str], path: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for pattern in patterns:
        if re.search(pattern, text):
            findings.append(
                finding(
                    "error",
                    "retired_root_expected_by_full_gate",
                    f"full-gate test still contains retired active path expectation: {pattern}",
                    path,
                )
            )
    return findings


def build_report(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    for item in FULL_GATE_EXPECTATIONS:
        rel = item["path"]
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "full_gate_test_missing", "expected full-gate test file is absent", rel))
            continue
        text = normalized_text(path)
        findings.extend(check_forbidden_text(text, item.get("forbidden", []), rel))
        findings.extend(check_required_text(text, item.get("required", []), rel))

    for item in STRUCTURE_GUARD_EXPECTATIONS:
        rel = item["path"]
        path = repo_root / rel
        if not path.exists():
            findings.append(finding("error", "structure_guard_missing", "expected canonical structure guard is absent", rel))
            continue
        text = normalized_text(path)
        findings.extend(check_required_text(text, item.get("required", []), rel))

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_full_gate_legacy_paths",
        "status": "BLOCKED" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS",
        "summary": {"errors": len(errors), "warnings": len(warnings), "findings": len(findings)},
        "findings": findings,
    }


def print_text(report: Dict[str, Any]) -> None:
    print(f"full-gate legacy paths: {report['status']}")
    print(f"errors: {report['summary']['errors']}")
    print(f"warnings: {report['summary']['warnings']}")
    for item in report["findings"]:
        path = f"{item['path']}: " if item.get("path") else ""
        print(f"{item['level']}: {path}{item['code']}: {item['message']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail on error findings.")
    args = parser.parse_args(argv)
    report = build_report(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 1 if args.strict and report["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
