#!/usr/bin/env python3
"""Reject third-party library includes outside provider and external boundaries."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


ALLOWED_PREFIXES = (
    "archive/",
    "external/upstream/",
    "runtime/platform/providers/",
    "runtime/input/providers/",
    "runtime/render/providers/",
    "runtime/audio/providers/",
    "runtime/asset/providers/",
    "runtime/script/providers/",
    "runtime/ui/providers/",
    "apps/client/proof/",
    "apps/workbench/proof/",
    "tools/validators/third_party/",
)
FORBIDDEN_PREFIXES = (
    "engine/",
    "game/",
    "contracts/",
    "content/",
    "runtime/include/",
    "tests/replay/",
    "tests/compat/",
)
SKIP_PREFIXES = (
    "archive/",
)
CODE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".ipp", ".m", ".mm"}
THIRD_PARTY_INCLUDE_RE = re.compile(
    r"^\s*#\s*include\s*[<\"](?:raylib|raymath|rlgl|raygui|raudio|SDL|SDL2/SDL|lua|lauxlib|lualib)\.h[>\"]",
    re.MULTILINE,
)
THIRD_PARTY_STABLE_TYPE_RE = re.compile(
    r"\b(Texture2D|SDL_Window|SDL_Event|SDL_Keycode|lua_State)\b"
)
THIRD_PARTY_CONTEXTUAL_TYPE_RE = re.compile(
    r"\b(Vector2|Vector3|Color|Image|Model|Sound|Music)\b"
)


def finding(level: str, code: str, message: str, path: str = "") -> Dict[str, Any]:
    item: Dict[str, Any] = {"level": level, "code": code, "message": message}
    if path:
        item["path"] = path
    return item


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


def allowed(path: str) -> bool:
    return path.startswith(ALLOWED_PREFIXES)


def forbidden(path: str) -> bool:
    return path.startswith(FORBIDDEN_PREFIXES)


def skipped(path: str) -> bool:
    return path.startswith(SKIP_PREFIXES)


def build_report(repo_root: Path) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    for path in git_ls_files(repo_root):
        if skipped(path):
            continue
        rel = Path(path)
        if rel.suffix.lower() not in CODE_SUFFIXES:
            continue
        try:
            text = (repo_root / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        has_include = bool(THIRD_PARTY_INCLUDE_RE.search(text))
        has_stable_type = bool(THIRD_PARTY_STABLE_TYPE_RE.search(text))
        has_contextual_stable_type = has_include and bool(THIRD_PARTY_CONTEXTUAL_TYPE_RE.search(text))
        if has_include and not allowed(path):
            findings.append(finding("error", "third_party_include_outside_provider_boundary", "third-party include is only allowed in provider/external/proof validator boundaries", path))
        if has_include and forbidden(path):
            findings.append(finding("error", "third_party_include_forbidden_root", "third-party include appears in an explicitly forbidden root", path))
        if (has_stable_type or has_contextual_stable_type) and forbidden(path):
            findings.append(finding("error", "third_party_type_forbidden_root", "third-party stable type appears in an explicitly forbidden root", path))
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {
        "validator": "check_forbidden_includes",
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
        print(f"third-party forbidden includes: {report['status']}")
        print(f"errors: {report['summary']['errors']}")
        print(f"warnings: {report['summary']['warnings']}")
        for item in report["findings"]:
            print(f"{item['level']}: {item.get('path', '')}: {item['code']}: {item['message']}")
    return 1 if args.strict and report["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
