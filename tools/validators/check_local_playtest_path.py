#!/usr/bin/env python3
"""Audit the documented canonical local playtest path.

This validator is intentionally conservative. By default it checks that the
documented runtime proof surfaces and command references are coherent. Strict
mode requires an actually buildable/local product path and therefore fails
while POST-CONVERGE-07 remains blocked by missing binaries or toolchain proof.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Iterable, List, Mapping


PRODUCTS = (
    {
        "product": "client",
        "target": "dominium_client",
        "output": "client",
        "cmake": os.path.join("apps", "client", "CMakeLists.txt"),
        "source": os.path.join("apps", "client", "app", "main_client.c"),
    },
    {
        "product": "server",
        "target": "dominium_server",
        "output": "server",
        "cmake": os.path.join("apps", "server", "CMakeLists.txt"),
        "source": os.path.join("apps", "server", "app", "main_server.c"),
        "python_entrypoint": os.path.join("apps", "server", "server_main.py"),
    },
    {
        "product": "setup",
        "target": "setup_cli",
        "output": "setup",
        "cmake": os.path.join("apps", "setup", "CMakeLists.txt"),
        "source": os.path.join("apps", "setup", "cli", "setup_cli_main.c"),
    },
    {
        "product": "launcher",
        "target": "launcher_cli",
        "output": "launcher",
        "cmake": os.path.join("apps", "launcher", "CMakeLists.txt"),
        "source": os.path.join("apps", "launcher", "cli", "launcher_cli_main.c"),
    },
)

REQUIRED_DOCS = (
    os.path.join("docs", "runtime", "CANONICAL_LOCAL_PLAYTEST.md"),
    os.path.join("docs", "release", "LOCAL_RUNTIME_PROOF.md"),
    os.path.join("docs", "repo", "audits", "POST_CONVERGE_07_LOCAL_RUNTIME_PROOF.md"),
    os.path.join("docs", "repo", "BUILD_VERIFICATION_PATHS.md"),
)

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


def _load_presets(repo_root: str) -> Mapping[str, object]:
    path = os.path.join(repo_root, "CMakePresets.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def _verify_preset_present(repo_root: str) -> bool:
    payload = _load_presets(repo_root)
    for row in list(payload.get("configurePresets") or []):
        if isinstance(row, dict) and str(row.get("name", "")).strip() == "verify":
            return True
    return False


def _product_rows(repo_root: str) -> List[Dict[str, object]]:
    rows = []
    for product in PRODUCTS:
        cmake_rel = str(product["cmake"])
        source_rel = str(product["source"])
        cmake_text = _read_text(os.path.join(repo_root, cmake_rel))
        source_text = _read_text(os.path.join(repo_root, source_rel))
        binary_path = _first_existing(_binary_candidates(repo_root, str(product["output"])))
        rows.append(
            {
                "product": str(product["product"]),
                "target": str(product["target"]),
                "output": str(product["output"]),
                "cmake_path": _norm(cmake_rel),
                "source_path": _norm(source_rel),
                "cmake_exists": bool(cmake_text),
                "source_exists": bool(source_text),
                "target_declared": "add_executable({}".format(str(product["target"])) in cmake_text,
                "output_declared": 'OUTPUT_NAME "{}"'.format(str(product["output"])) in cmake_text,
                "help_declared": "--help" in source_text,
                "version_declared": "--version" in source_text,
                "status_declared": "--status" in source_text,
                "smoke_declared": "--smoke" in source_text,
                "binary_found": bool(binary_path),
                "binary_path": _norm(os.path.relpath(binary_path, repo_root)) if binary_path else "",
            }
        )
    return rows


def _server_python_entrypoint(repo_root: str) -> Dict[str, object]:
    rel_path = os.path.join("apps", "server", "server_main.py")
    text = _read_text(os.path.join(repo_root, rel_path))
    forwards_sys_argv = "main(sys.argv[1:])" in text or "main(list(sys.argv[1:]))" in text
    return {
        "path": _norm(rel_path),
        "exists": bool(text),
        "actual_script_forwards_cli_args": bool(forwards_sys_argv),
        "note": (
            "script invocation does not forward sys.argv[1:]"
            if text and not forwards_sys_argv
            else ""
        ),
    }


def build_report(repo_root: str, dry_run: bool = False) -> Dict[str, object]:
    repo_root_abs = os.path.abspath(repo_root)
    docs = [
        {"path": _norm(rel_path), "exists": _exists(repo_root_abs, rel_path)}
        for rel_path in REQUIRED_DOCS
    ]
    products = _product_rows(repo_root_abs)
    server_python = _server_python_entrypoint(repo_root_abs)
    missing_docs = [row["path"] for row in docs if not row["exists"]]
    missing_product_refs = [
        row["product"]
        for row in products
        if not (row["cmake_exists"] and row["source_exists"] and row["target_declared"])
    ]
    missing_binaries = [row["product"] for row in products if not row["binary_found"]]
    blockers = []
    if missing_docs:
        blockers.append("required runtime proof docs are missing: {}".format(", ".join(missing_docs)))
    if not _verify_preset_present(repo_root_abs):
        blockers.append("CMake configure preset 'verify' is missing")
    if missing_product_refs:
        blockers.append("product target/source references are incomplete: {}".format(", ".join(missing_product_refs)))
    if missing_binaries:
        blockers.append("built product binaries are missing: {}".format(", ".join(missing_binaries)))
    if server_python.get("exists") and not server_python.get("actual_script_forwards_cli_args"):
        blockers.append("apps/server/server_main.py script invocation does not forward CLI args")

    proof_status = "full_proof" if not blockers and all(row["binary_found"] for row in products) else "blocked"
    commands = [
        {
            "step": "configure",
            "command": "cmake --preset verify",
            "status": "blocked" if missing_binaries else "proven_elsewhere",
        },
        {
            "step": "build",
            "command": "cmake --build --preset verify",
            "status": "blocked" if missing_binaries else "proven_elsewhere",
        },
        {
            "step": "test",
            "command": "ctest --preset verify",
            "status": "blocked" if missing_binaries else "proven_elsewhere",
        },
    ]
    for row in products:
        commands.append(
            {
                "step": "{} help".format(row["product"]),
                "command": "{} --help".format(row["output"]),
                "status": "blocked" if not row["binary_found"] else "available",
            }
        )
    return {
        "result": "complete",
        "validator": "check_local_playtest_path",
        "repo_root": _norm(repo_root_abs),
        "proof_status": proof_status,
        "dry_run": bool(dry_run),
        "verify_preset_present": _verify_preset_present(repo_root_abs),
        "docs": docs,
        "products": products,
        "server_python_entrypoint": server_python,
        "commands": commands,
        "blockers": blockers,
    }


def _print_text(report: Mapping[str, object]) -> None:
    print("Local playtest path audit")
    print("proof_status: {}".format(report.get("proof_status")))
    print("verify_preset_present: {}".format(str(report.get("verify_preset_present")).lower()))
    print("")
    print("Product surfaces:")
    for row in list(report.get("products") or []):
        print(
            "- {product}: target={target} output={output} binary_found={binary_found}".format(
                **dict(row)
            )
        )
    print("")
    blockers = list(report.get("blockers") or [])
    if blockers:
        print("Blockers:")
        for blocker in blockers:
            print("- {}".format(blocker))
    else:
        print("Blockers: none")
    if bool(report.get("dry_run")):
        print("")
        print("Dry-run command sequence:")
        for row in list(report.get("commands") or []):
            print("- [{status}] {command}".format(**dict(row)))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the canonical local playtest path.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Fail unless a full local playtest path is available.")
    parser.add_argument("--dry-run", action="store_true", help="Print the documented command sequence without running it.")
    args = parser.parse_args(argv)

    report = build_report(args.repo_root, dry_run=bool(args.dry_run))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    if bool(args.strict) and str(report.get("proof_status", "")) != "full_proof":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
