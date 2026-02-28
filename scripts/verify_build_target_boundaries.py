#!/usr/bin/env python3
"""Deterministic ARCH-REF-3 build boundary scanner.

Governance-only check: validates structural boundaries without changing runtime semantics.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Iterable, List


OS_TOKEN_PATTERNS = (
    re.compile(r"^\s*#\s*include\s*[<\"]windows\.h[\">]", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]X11/", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]Cocoa/", re.IGNORECASE),
    re.compile(r"\bctypes\.windll\b", re.IGNORECASE),
    re.compile(r"\bimport\s+win32api\b", re.IGNORECASE),
)

RUNTIME_ROOTS = ("src", "engine", "game", "client", "server")
RUNTIME_EXTS = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp")
SKIP_PREFIXES = ("build/", "dist/", "docs/", "legacy/", "tools/xstack/out/")
QUARANTINE_SKIP_PREFIXES = ("build/", "dist/", "docs/", "tools/xstack/out/")

CORE_REVERSE_IMPORT_PATTERNS = (
    re.compile(r"^\s*from\s+src\.(materials|logistics|interior|interaction|machines|inspection)\b"),
    re.compile(r"^\s*import\s+src\.(materials|logistics|interior|interaction|machines|inspection)\b"),
)

RENDER_TRUTH_PATTERN = re.compile(r"\b(truth_model|truthmodel|universe_state)\b", re.IGNORECASE)
TOOLS_IMPORT_PATTERNS = (
    re.compile(r"^\s*from\s+tools\.auditx\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.auditx\b", re.IGNORECASE),
    re.compile(r"^\s*from\s+tools\.governance\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.governance\b", re.IGNORECASE),
    re.compile(r"^\s*from\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
    re.compile(r"^\s*import\s+tools\.xstack\.(repox|testx|auditx|controlx)\b", re.IGNORECASE),
    re.compile(r"^\s*#\s*include\s*[<\"]tools/", re.IGNORECASE),
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _iter_files(repo_root: str, rel_root: str, exts: tuple[str, ...]) -> Iterable[str]:
    abs_root = os.path.join(repo_root, rel_root.replace("/", os.sep))
    if not os.path.isdir(abs_root):
        return []
    out: List[str] = []
    for walk_root, dirs, files in os.walk(abs_root):
        dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
        for name in sorted(files):
            if exts and (not name.endswith(exts)):
                continue
            out.append(_norm(os.path.relpath(os.path.join(walk_root, name), repo_root)))
    return out


def _read_lines(repo_root: str, rel_path: str) -> List[str]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return []


def _check_runtime_no_tool_imports(repo_root: str, failures: List[str]) -> None:
    for root in RUNTIME_ROOTS:
        for rel_path in _iter_files(repo_root, root, RUNTIME_EXTS):
            if rel_path.startswith(SKIP_PREFIXES):
                continue
            for line_no, line in enumerate(_read_lines(repo_root, rel_path), start=1):
                if not any(pattern.search(line) for pattern in TOOLS_IMPORT_PATTERNS):
                    continue
                failures.append(
                    "BOUNDARY-TOOLS-001 {}:{} runtime module imports/includes tools path".format(rel_path, line_no)
                )


def _check_platform_isolation(repo_root: str, failures: List[str]) -> None:
    for rel_path in _iter_files(repo_root, "src", RUNTIME_EXTS):
        if rel_path.startswith("src/platform/"):
            continue
        for line_no, line in enumerate(_read_lines(repo_root, rel_path), start=1):
            if not any(pattern.search(line) for pattern in OS_TOKEN_PATTERNS):
                continue
            failures.append(
                "BOUNDARY-PLATFORM-001 {}:{} platform/OS token outside src/platform".format(rel_path, line_no)
            )


def _check_render_truth_isolation(repo_root: str, failures: List[str]) -> None:
    for rel_path in _iter_files(repo_root, "src/client/render", (".py",)):
        for line_no, line in enumerate(_read_lines(repo_root, rel_path), start=1):
            if not RENDER_TRUTH_PATTERN.search(line):
                continue
            failures.append(
                "BOUNDARY-RENDER-001 {}:{} render path references truth symbol".format(rel_path, line_no)
            )


def _check_core_dependency_direction(repo_root: str, failures: List[str]) -> None:
    for rel_path in _iter_files(repo_root, "src/core", (".py",)):
        for line_no, line in enumerate(_read_lines(repo_root, rel_path), start=1):
            if not any(pattern.search(line) for pattern in CORE_REVERSE_IMPORT_PATTERNS):
                continue
            failures.append(
                "BOUNDARY-CORE-001 {}:{} core module imports domain module".format(rel_path, line_no)
            )


def _check_cmake_boundary_markers(repo_root: str, failures: List[str]) -> None:
    cmake_rel = "CMakeLists.txt"
    cmake_lines = _read_lines(repo_root, cmake_rel)
    if not cmake_lines:
        failures.append("BOUNDARY-CMAKE-001 missing CMakeLists.txt")
        return
    cmake_text = "\n".join(cmake_lines)

    required_tokens = (
        'option(DOM_BUILD_TOOLS "Build tools" OFF)',
        "if(DOM_BUILD_TOOLS)",
        "add_subdirectory(tools)",
        "dom_assert_no_link(domino_engine",
        "tools_shared",
        "dominium-tools",
    )
    for token in required_tokens:
        if token in cmake_text:
            continue
        failures.append("BOUNDARY-CMAKE-002 missing required boundary token '{}'".format(token))


def _check_quarantine_policy(repo_root: str, failures: List[str]) -> None:
    legacy_abs = os.path.join(repo_root, "legacy")
    quarantine_abs = os.path.join(repo_root, "quarantine")
    if not os.path.isdir(legacy_abs):
        failures.append("BOUNDARY-LEGACY-000 missing legacy/ directory")
    if not os.path.isdir(quarantine_abs):
        failures.append("BOUNDARY-LEGACY-000 missing quarantine/ directory")

    cmake_lines = _read_lines(repo_root, "CMakeLists.txt")
    cmake_text = "\n".join(cmake_lines)
    for token in ("add_subdirectory(legacy", "add_subdirectory(quarantine"):
        if token in cmake_text:
            failures.append("BOUNDARY-CMAKE-003 forbidden CMake linkage token '{}'".format(token))

    for root in RUNTIME_ROOTS:
        for rel_path in _iter_files(repo_root, root, RUNTIME_EXTS):
            if rel_path.startswith(QUARANTINE_SKIP_PREFIXES):
                continue
            for line_no, line in enumerate(_read_lines(repo_root, rel_path), start=1):
                lowered = str(line).replace("\\", "/")
                if "legacy/" not in lowered and "quarantine/" not in lowered:
                    continue
                failures.append(
                    "BOUNDARY-LEGACY-001 {}:{} runtime module references legacy/quarantine path".format(
                        rel_path,
                        line_no,
                    )
                )



def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic build boundary scanner.")
    parser.add_argument("--repo-root", default="")
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root or os.getcwd()))
    failures: List[str] = []

    _check_runtime_no_tool_imports(repo_root, failures)
    _check_platform_isolation(repo_root, failures)
    _check_render_truth_isolation(repo_root, failures)
    _check_core_dependency_direction(repo_root, failures)
    _check_cmake_boundary_markers(repo_root, failures)
    _check_quarantine_policy(repo_root, failures)

    if failures:
        for item in sorted(set(failures)):
            print(item)
        return 1

    print("BOUNDARY-OK: build boundary checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
