#!/usr/bin/env python3
"""Validate third-party source manifest and source-root policy."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

try:
    import tomllib  # type: ignore
except ImportError:  # pragma: no cover
    tomllib = None


MANIFEST = Path("external/manifests/third_party.toml")
ALLOWED_EXTERNAL_ROOTS = {"README.md", "manifests", "licenses", "patches", "upstream"}


def finding(level: str, code: str, message: str, path: str = "") -> Dict[str, Any]:
    row: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        row["path"] = path
    return row


def minimal_toml_load(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    current: Dict[str, Any] = root
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[[") and line.endswith("]]"):
            key = line[2:-2].strip()
            current = {}
            root.setdefault(key, []).append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part.strip(), {})
            continue
        if "=" not in line:
            raise ValueError(f"invalid TOML line: {raw_line}")
        key, value = line.split("=", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            current[key.strip()] = value[1:-1]
        elif value in {"true", "false"}:
            current[key.strip()] = value == "true"
        else:
            current[key.strip()] = value
    return root


def load_toml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    if tomllib is not None:
        return tomllib.loads(text)
    return minimal_toml_load(text)


def git_ls_files(repo_root: Path) -> List[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=str(repo_root),
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def dependency_ids(data: Dict[str, Any]) -> Set[str]:
    out: Set[str] = set()
    for item in data.get("dependency", []) or []:
        if isinstance(item, dict) and item.get("id"):
            out.add(str(item.get("id")))
    return out


def build_report(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    manifest_path = repo_root / MANIFEST
    if not manifest_path.exists():
        findings.append(finding("error", "third_party_manifest_missing", "third-party manifest is missing", MANIFEST.as_posix()))
        data: Dict[str, Any] = {}
    else:
        try:
            data = load_toml(manifest_path)
        except Exception as exc:
            data = {}
            findings.append(finding("error", "third_party_manifest_invalid", f"third-party manifest does not parse: {exc}", MANIFEST.as_posix()))

    manifest = data.get("manifest", {}) if isinstance(data, dict) else {}
    policy = data.get("policy", {}) if isinstance(data, dict) else {}
    if manifest and manifest.get("source_root") != "external/upstream":
        findings.append(finding("error", "source_root_not_upstream", "third-party source root must be external/upstream", MANIFEST.as_posix()))
    if policy and policy.get("third_party_types_fenced") is not True:
        findings.append(finding("error", "third_party_types_not_fenced", "third-party manifest must fence third-party types", MANIFEST.as_posix()))

    paths = git_ls_files(repo_root)
    external_roots = {
        path.split("/")[1] if "/" in path else path
        for path in paths
        if path.startswith("external/")
    }
    for root in sorted(external_roots):
        if root not in ALLOWED_EXTERNAL_ROOTS:
            findings.append(finding("error", "unknown_external_root", "external root is not allowed by third-party source policy", f"external/{root}"))
    if "upstream" in external_roots and "vendor" in external_roots:
        findings.append(finding("error", "mixed_upstream_vendor_roots", "do not mix external/upstream and external/vendor without explicit split policy", "external"))

    declared = dependency_ids(data)
    for path in paths:
        if not path.startswith("external/upstream/"):
            continue
        parts = path.split("/")
        if len(parts) >= 3 and parts[2] not in declared:
            findings.append(finding("error", "upstream_dependency_not_manifested", "external/upstream dependency has no manifest entry", path))

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_vendor_manifest",
        "status": "BLOCKED" if errors else "PASS_WITH_WARNINGS" if warnings else "PASS",
        "summary": {"errors": len(errors), "warnings": len(warnings), "findings": len(findings)},
        "findings": findings,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"third-party vendor manifest: {report['status']}")
        print(f"errors: {report['summary']['errors']}")
        print(f"warnings: {report['summary']['warnings']}")
        for item in report["findings"]:
            path = f"{item.get('path')}: " if item.get("path") else ""
            print(f"{item['level']}: {path}{item['code']}: {item['message']}")
    return 1 if args.strict and report["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
