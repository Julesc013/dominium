#!/usr/bin/env python3
"""Audit the documented product boot matrix proof.

Default mode checks that product target declarations, proof documents, and
safe command references are coherent. Strict mode requires built product
binaries and therefore fails while POST-CONVERGE-08 remains only partially
proven by script/AppShell help surfaces.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Iterable, List, Mapping


PRODUCTS = (
    {
        "product": "setup",
        "target": "setup_cli",
        "output": "setup",
        "cmake": os.path.join("apps", "setup", "CMakeLists.txt"),
        "source": os.path.join("apps", "setup", "cli", "setup_cli_main.c"),
        "safe_command": [sys.executable, os.path.join("tools", "setup", "setup_cli.py"), "--help"],
        "script_entrypoint": os.path.join("tools", "setup", "setup_cli.py"),
        "expected_script_status": "blocked",
    },
    {
        "product": "launcher",
        "target": "launcher_cli",
        "output": "launcher",
        "cmake": os.path.join("apps", "launcher", "CMakeLists.txt"),
        "source": os.path.join("apps", "launcher", "cli", "launcher_cli_main.c"),
        "safe_command": [sys.executable, os.path.join("tools", "launcher", "launch.py"), "--help"],
        "script_entrypoint": os.path.join("tools", "launcher", "launch.py"),
        "expected_script_status": "partial",
    },
    {
        "product": "client",
        "target": "dominium_client",
        "output": "client",
        "cmake": os.path.join("apps", "client", "CMakeLists.txt"),
        "source": os.path.join("apps", "client", "app", "main_client.c"),
        "safe_command": [sys.executable, os.path.join("dist", "bin", "dominium_client"), "--help"],
        "script_entrypoint": os.path.join("dist", "bin", "dominium_client"),
        "expected_script_status": "partial",
    },
    {
        "product": "server",
        "target": "dominium_server",
        "output": "server",
        "cmake": os.path.join("apps", "server", "CMakeLists.txt"),
        "source": os.path.join("apps", "server", "app", "main_server.c"),
        "safe_command": [sys.executable, os.path.join("dist", "bin", "dominium_server"), "--help"],
        "script_entrypoint": os.path.join("dist", "bin", "dominium_server"),
        "expected_script_status": "partial",
    },
    {
        "product": "tools",
        "target": "dominium-tools",
        "output": "tools",
        "cmake": os.path.join("tools", "CMakeLists.txt"),
        "source": os.path.join("tools", "tools_host_main.c"),
        "safe_command": [
            sys.executable,
            os.path.join("tools", "appshell", "product_stub_cli.py"),
            "--product-id",
            "tool.attach_console_stub",
            "--help",
        ],
        "script_entrypoint": os.path.join("tools", "appshell", "product_stub_cli.py"),
        "expected_script_status": "partial",
    },
)

REQUIRED_DOCS = (
    os.path.join("docs", "release", "PRODUCT_BOOT_PROOF.md"),
    os.path.join("docs", "repo", "audits", "POST_CONVERGE_08_PRODUCT_BOOT_MATRIX_PROOF.md"),
    os.path.join("docs", "release", "PRODUCT_MODE_MATRIX.md"),
    os.path.join("docs", "release", "COMPONENT_MATRIX.md"),
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
    try:
        with open(os.path.join(repo_root, "CMakePresets.json"), "r", encoding="utf-8") as handle:
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
        script_rel = str(product["script_entrypoint"])
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
                "script_entrypoint": _norm(script_rel),
                "cmake_exists": bool(cmake_text),
                "source_exists": bool(source_text),
                "script_exists": _exists(repo_root, script_rel),
                "target_declared": "add_executable({}".format(str(product["target"])) in cmake_text,
                "output_declared": 'OUTPUT_NAME "{}"'.format(str(product["output"])) in cmake_text,
                "help_declared": "--help" in source_text,
                "version_declared": "--version" in source_text,
                "status_declared": "--status" in source_text,
                "smoke_declared": "--smoke" in source_text,
                "binary_found": bool(binary_path),
                "binary_path": _norm(os.path.relpath(binary_path, repo_root)) if binary_path else "",
                "safe_command": [str(token) for token in list(product["safe_command"])],
                "safe_command_text": " ".join(str(token) for token in list(product["safe_command"])),
                "expected_script_status": str(product["expected_script_status"]),
            }
        )
    return rows


def _run_safe_commands(repo_root: str, timeout: int) -> Dict[str, Dict[str, object]]:
    results: Dict[str, Dict[str, object]] = {}
    for product in PRODUCTS:
        command = [str(token) for token in list(product["safe_command"])]
        try:
            completed = subprocess.run(
                command,
                cwd=repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                timeout=max(1, int(timeout)),
            )
            output = completed.stdout or ""
            results[str(product["product"])] = {
                "command": " ".join(command),
                "exit_code": int(completed.returncode),
                "output_summary": "\n".join(output.splitlines()[:8]),
            }
        except subprocess.TimeoutExpired:
            results[str(product["product"])] = {
                "command": " ".join(command),
                "exit_code": -1,
                "output_summary": "timeout after {}s".format(max(1, int(timeout))),
            }
    return results


def build_report(
    repo_root: str,
    *,
    dry_run: bool = False,
    run_smoke: bool = False,
    timeout: int = 10,
) -> Dict[str, object]:
    repo_root_abs = os.path.abspath(repo_root)
    docs = [{"path": _norm(rel_path), "exists": _exists(repo_root_abs, rel_path)} for rel_path in REQUIRED_DOCS]
    products = _product_rows(repo_root_abs)
    smoke_results = _run_safe_commands(repo_root_abs, timeout) if run_smoke else {}
    missing_docs = [str(row["path"]) for row in docs if not row["exists"]]
    incomplete_refs = [
        str(row["product"])
        for row in products
        if not (row["cmake_exists"] and row["source_exists"] and row["target_declared"] and row["output_declared"])
    ]
    missing_binaries = [str(row["product"]) for row in products if not row["binary_found"]]
    missing_scripts = [str(row["product"]) for row in products if not row["script_exists"]]
    blockers = []
    if missing_docs:
        blockers.append("required product boot docs are missing: {}".format(", ".join(missing_docs)))
    if not _verify_preset_present(repo_root_abs):
        blockers.append("CMake configure preset 'verify' is missing")
    if incomplete_refs:
        blockers.append("product target/source declarations are incomplete: {}".format(", ".join(incomplete_refs)))
    if missing_binaries:
        blockers.append("built product binaries are missing: {}".format(", ".join(missing_binaries)))
    if missing_scripts:
        blockers.append("script or wrapper entrypoints are missing: {}".format(", ".join(missing_scripts)))
    if run_smoke:
        failed = [
            product
            for product, result in sorted(smoke_results.items())
            if int(dict(result).get("exit_code", 1)) != 0
        ]
        if failed:
            blockers.append("safe help smoke commands failed: {}".format(", ".join(failed)))

    partial_surfaces = [
        str(row["product"])
        for row in products
        if row["script_exists"] and str(row["expected_script_status"]) == "partial"
    ]
    proof_status = "proven" if not blockers and all(row["binary_found"] for row in products) else "partial"
    if not partial_surfaces and blockers:
        proof_status = "blocked"
    return {
        "result": "complete",
        "validator": "check_product_boot_matrix",
        "repo_root": _norm(repo_root_abs),
        "proof_status": proof_status,
        "dry_run": bool(dry_run),
        "run_smoke": bool(run_smoke),
        "verify_preset_present": _verify_preset_present(repo_root_abs),
        "docs": docs,
        "products": products,
        "smoke_results": smoke_results,
        "blockers": blockers,
    }


def _print_text(report: Mapping[str, object]) -> None:
    print("Product boot matrix audit")
    print("proof_status: {}".format(report.get("proof_status")))
    print("verify_preset_present: {}".format(str(report.get("verify_preset_present")).lower()))
    print("")
    print("Product surfaces:")
    for row in list(report.get("products") or []):
        print(
            "- {product}: target={target} output={output} binary_found={binary_found} script_exists={script_exists}".format(
                **dict(row)
            )
        )
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
        print("Dry-run safe product commands:")
        for row in list(report.get("products") or []):
            print("- {}".format(dict(row).get("safe_command_text")))
    if bool(report.get("run_smoke")):
        print("")
        print("Smoke command results:")
        for product, result in sorted(dict(report.get("smoke_results") or {}).items()):
            print("- {}: exit {}".format(product, dict(result).get("exit_code")))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit product boot matrix proof.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Fail unless product binaries are build-proven.")
    parser.add_argument("--dry-run", action="store_true", help="Print safe command references without running them.")
    parser.add_argument("--run-smoke", action="store_true", help="Run safe help/smoke commands only.")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for --run-smoke commands.")
    args = parser.parse_args(argv)

    report = build_report(
        args.repo_root,
        dry_run=bool(args.dry_run),
        run_smoke=bool(args.run_smoke),
        timeout=int(args.timeout),
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
