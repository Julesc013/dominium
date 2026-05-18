#!/usr/bin/env python3
"""Audit portable projection contract and smoke readiness.

Default mode is non-destructive and checks that the distribution contract,
portable layout docs, package docs, and known package/projection tools are
coherent. Strict mode requires an actual projection root or build-proven
product binaries and therefore fails while POST-CONVERGE-09 remains partial.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, Iterable, List, Mapping, Optional


REQUIRED_DOCS = (
    os.path.join("docs", "repo", "DISTRIBUTION_LAYOUT_CANON.md"),
    os.path.join("docs", "distribution", "PORTABLE_INSTALL_LAYOUT.md"),
    os.path.join("docs", "distribution", "PACKAGE_EXPORT_ROOTS.md"),
    os.path.join("docs", "distribution", "CACHE_AND_STAGING_LAYOUT.md"),
    os.path.join("docs", "distribution", "BUNDLE_AND_DIAGNOSTIC_LAYOUTS.md"),
    os.path.join("docs", "release", "PACKAGING_MATRIX.md"),
    os.path.join("docs", "release", "COMPONENT_MATRIX.md"),
    os.path.join("docs", "distribution", "PORTABLE_PROJECTION_SMOKE_PROOF.md"),
    os.path.join("docs", "release", "PACKAGE_SMOKE_PROOF.md"),
    os.path.join("docs", "repo", "audits", "POST_CONVERGE_09_PORTABLE_PROJECTION_PROOF.md"),
)

REQUIRED_TOOLS = (
    os.path.join("apps", "setup", "packages", "scripts", "packaging", "pipeline.py"),
    os.path.join("tools", "distribution", "tool_pkg_pack.py"),
    os.path.join("tools", "distribution", "tool_pkg_verify.py"),
    os.path.join("tools", "distribution", "tool_pkg_index.py"),
    os.path.join("tools", "distribution", "tool_pkg_extract.py"),
    os.path.join("tools", "distribution", "pkg_pack_all.py"),
    os.path.join("tools", "distribution", "pkg_verify_all.py"),
    os.path.join("tools", "distribution", "build_manifest.py"),
)

REQUIRED_MANIFESTS = (
    "install.manifest.json",
    "semantic_contract_registry.json",
    "release.manifest.json",
)

REQUIRED_PORTABLE_PATHS = (
    "bin",
    "descriptors",
    "store/packs",
    "store/profiles",
    "store/locks",
    "instances",
    "saves",
    "exports",
    "logs",
    "runtime/ipc",
    "runtime/locks",
    "runtime/temp",
    "cache",
    "ops/transactions",
    "docs",
    "LICENSES",
)

PRODUCT_OUTPUTS = ("setup", "launcher", "client", "server", "tools")

BUILD_BIN_DIRS = (
    os.path.join("out", "build", "vs2026", "verify", "bin"),
    os.path.join("out", "build", "vs2026", "verify-win-vs2026", "bin"),
    os.path.join("build", "verify", "bin"),
)


def _norm(path: str) -> str:
    return path.replace(os.sep, "/")


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _exists(repo_root: str, rel_path: str) -> bool:
    return os.path.exists(os.path.join(repo_root, rel_path))


def _binary_candidates(repo_root: str, output: str) -> List[str]:
    names = [output, output + ".exe"]
    out = []
    for rel_dir in BUILD_BIN_DIRS:
        for name in names:
            out.append(os.path.join(repo_root, rel_dir, name))
    return out


def _first_existing(paths: Iterable[str]) -> str:
    for path in paths:
        if os.path.exists(path):
            return path
    return ""


def _contract_summary(repo_root: str) -> Dict[str, object]:
    rel_path = os.path.join("contracts", "distribution", "layout.contract.toml")
    text = _read_text(os.path.join(repo_root, rel_path))
    logical_roots = re.findall(r"^\[logical_roots\.([A-Z0-9_]+)\]", text, flags=re.MULTILINE)
    projections = re.findall(r"^\[projections\.([A-Za-z0-9_]+)\]", text, flags=re.MULTILINE)
    portable_paths: List[str] = []
    match = re.search(r"\[projections\.portable_install\](.*?)(?:\n\[|\Z)", text, flags=re.DOTALL)
    if match:
        paths_match = re.search(r"paths\s*=\s*\[(.*?)\]", match.group(1), flags=re.DOTALL)
        if paths_match:
            portable_paths = re.findall(r'"([^"]+)"', paths_match.group(1))
    return {
        "path": _norm(rel_path),
        "exists": bool(text),
        "logical_roots": sorted(logical_roots),
        "projections": sorted(projections),
        "portable_paths": sorted(portable_paths),
        "portable_install_declared": "portable_install" in projections,
        "package_export_declared": "package_export" in projections,
    }


def _build_binaries(repo_root: str) -> List[Dict[str, object]]:
    rows = []
    for output in PRODUCT_OUTPUTS:
        existing = _first_existing(_binary_candidates(repo_root, output))
        rows.append(
            {
                "product": output,
                "binary_found": bool(existing),
                "binary_path": _norm(os.path.relpath(existing, repo_root)) if existing else "",
            }
        )
    return rows


def _projection_root_rows(projection_root: str) -> Dict[str, object]:
    root_abs = os.path.abspath(projection_root)
    manifests = []
    for rel_path in REQUIRED_MANIFESTS:
        path = os.path.join(root_abs, rel_path)
        manifests.append({"path": _norm(rel_path), "present": os.path.isfile(path)})
    paths = []
    for rel_path in REQUIRED_PORTABLE_PATHS:
        path = os.path.join(root_abs, rel_path.replace("/", os.sep))
        paths.append({"path": _norm(rel_path), "present": os.path.isdir(path)})
    absolute_path_findings = []
    for rel_path in REQUIRED_MANIFESTS:
        path = os.path.join(root_abs, rel_path)
        if not os.path.isfile(path):
            continue
        text = _read_text(path)
        root_token = root_abs.replace("\\", "\\\\")
        if root_abs in text or root_token in text:
            absolute_path_findings.append(rel_path)
    return {
        "projection_root": _norm(root_abs),
        "exists": os.path.isdir(root_abs),
        "manifests": manifests,
        "paths": paths,
        "absolute_path_findings": absolute_path_findings,
    }


def _doc_rows(repo_root: str) -> List[Dict[str, object]]:
    return [{"path": _norm(rel_path), "exists": _exists(repo_root, rel_path)} for rel_path in REQUIRED_DOCS]


def _tool_rows(repo_root: str) -> List[Dict[str, object]]:
    return [{"path": _norm(rel_path), "exists": _exists(repo_root, rel_path)} for rel_path in REQUIRED_TOOLS]


def _dry_run_commands() -> List[Dict[str, str]]:
    return [
        {
            "purpose": "configure canonical verify lane",
            "command": "cmake --preset verify",
            "status": "blocked_until_vs2022_generator_available",
        },
        {
            "purpose": "build product binaries",
            "command": "cmake --build --preset verify",
            "status": "blocked_until_configure_passes",
        },
        {
            "purpose": "assemble artifact root",
            "command": "python release/packaging/setup/scripts/packaging/pipeline.py assemble --build-dir out/build/vs2026/verify --out <temp>/artifact_root --version 0.0.0-smoke",
            "status": "blocked_until_build_output_exists",
        },
        {
            "purpose": "create portable archive",
            "command": "python release/packaging/setup/scripts/packaging/pipeline.py portable --artifact <temp>/artifact_root --out <temp>/portable --version 0.0.0-smoke",
            "status": "blocked_until_artifact_root_exists",
        },
        {
            "purpose": "validate projection root",
            "command": "python tools/validators/check_portable_projection.py --repo-root . --projection-root <temp>/DominiumPortable",
            "status": "blocked_until_projection_root_exists",
        },
    ]


def build_report(
    repo_root: str,
    *,
    projection_root: str = "",
    dry_run: bool = False,
    allow_missing_binaries: bool = False,
    allow_missing_manifests: bool = False,
) -> Dict[str, object]:
    repo_root_abs = os.path.abspath(repo_root)
    contract = _contract_summary(repo_root_abs)
    docs = _doc_rows(repo_root_abs)
    tools = _tool_rows(repo_root_abs)
    binaries = _build_binaries(repo_root_abs)
    projection = _projection_root_rows(projection_root) if projection_root else {}
    blockers = []

    missing_docs = [str(row["path"]) for row in docs if not row["exists"]]
    missing_tools = [str(row["path"]) for row in tools if not row["exists"]]
    missing_binaries = [str(row["product"]) for row in binaries if not row["binary_found"]]
    if not contract.get("exists"):
        blockers.append("distribution layout contract is missing")
    if not contract.get("portable_install_declared"):
        blockers.append("portable_install projection is not declared in distribution contract")
    if not contract.get("package_export_declared"):
        blockers.append("package_export projection is not declared in distribution contract")
    if missing_docs:
        blockers.append("required distribution/package docs are missing: {}".format(", ".join(missing_docs)))
    if missing_tools:
        blockers.append("required package/projection tools are missing: {}".format(", ".join(missing_tools)))
    if missing_binaries and not allow_missing_binaries:
        blockers.append("built product binaries are missing: {}".format(", ".join(missing_binaries)))
    if not projection_root:
        blockers.append("no projection root was provided or generated")
    else:
        if not bool(projection.get("exists")):
            blockers.append("projection root does not exist: {}".format(_norm(os.path.abspath(projection_root))))
        missing_projection_paths = [
            str(row["path"]) for row in list(projection.get("paths") or []) if not bool(row.get("present"))
        ]
        missing_projection_manifests = [
            str(row["path"]) for row in list(projection.get("manifests") or []) if not bool(row.get("present"))
        ]
        if missing_projection_paths:
            blockers.append("projection root is missing required paths: {}".format(", ".join(missing_projection_paths)))
        if missing_projection_manifests and not allow_missing_manifests:
            blockers.append("projection root is missing required manifests: {}".format(", ".join(missing_projection_manifests)))
        if list(projection.get("absolute_path_findings") or []):
            blockers.append(
                "projection manifests contain absolute host path tokens: {}".format(
                    ", ".join(str(item) for item in list(projection.get("absolute_path_findings") or []))
                )
            )

    coherent = bool(contract.get("exists")) and not missing_docs and not missing_tools
    proof_status = "proven" if not blockers else ("partial" if coherent else "blocked")
    return {
        "result": "complete",
        "validator": "check_portable_projection",
        "repo_root": _norm(repo_root_abs),
        "proof_status": proof_status,
        "dry_run": bool(dry_run),
        "allow_missing_binaries": bool(allow_missing_binaries),
        "allow_missing_manifests": bool(allow_missing_manifests),
        "contract": contract,
        "docs": docs,
        "tools": tools,
        "build_binaries": binaries,
        "projection_root": projection,
        "expected_manifests": list(REQUIRED_MANIFESTS),
        "expected_paths": list(REQUIRED_PORTABLE_PATHS),
        "commands": _dry_run_commands() if dry_run else [],
        "blockers": blockers,
    }


def _print_text(report: Mapping[str, object]) -> None:
    print("Portable projection audit")
    print("proof_status: {}".format(report.get("proof_status")))
    contract = dict(report.get("contract") or {})
    print("contract_present: {}".format(str(contract.get("exists")).lower()))
    print("portable_install_declared: {}".format(str(contract.get("portable_install_declared")).lower()))
    print("package_export_declared: {}".format(str(contract.get("package_export_declared")).lower()))
    print("")
    print("Build binaries:")
    for row in list(report.get("build_binaries") or []):
        print("- {product}: binary_found={binary_found}".format(**dict(row)))
    blockers = list(report.get("blockers") or [])
    print("")
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            print("- {}".format(blocker))
    else:
        print("Blockers: none")
    if bool(report.get("dry_run")):
        print("")
        print("Dry-run sequence:")
        for row in list(report.get("commands") or []):
            payload = dict(row)
            print("- [{status}] {command}".format(**payload))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit portable projection/package smoke readiness.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Fail unless a real portable projection can be validated.")
    parser.add_argument("--dry-run", action="store_true", help="Print the expected projection command sequence.")
    parser.add_argument("--projection-root", default="", help="Validate an existing portable projection root.")
    parser.add_argument("--allow-missing-binaries", action="store_true", help="Do not treat missing built binaries as blockers.")
    parser.add_argument("--allow-missing-manifests", action="store_true", help="Allow missing manifests in projection-root mode.")
    args = parser.parse_args(argv)

    report = build_report(
        args.repo_root,
        projection_root=str(args.projection_root or ""),
        dry_run=bool(args.dry_run),
        allow_missing_binaries=bool(args.allow_missing_binaries),
        allow_missing_manifests=bool(args.allow_missing_manifests),
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    if bool(args.strict) and str(report.get("proof_status", "")) != "proven":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
