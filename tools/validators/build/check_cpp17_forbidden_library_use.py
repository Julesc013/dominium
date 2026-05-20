#!/usr/bin/env python3
"""Check the C++17 mainline subset forbidden for macOS 10.9.5 support."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SCAN_ROOTS = ("engine", "game", "runtime", "apps", "tools", "tests", "libs", "client", "server", "launcher", "setup")
SOURCE_EXTS = {".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx", ".h", ".inl", ".ipp"}
EXCLUDE_MARKERS = (
    "/archive/",
    "/docs/",
    "/out/",
    "/build/",
    "/.git/",
    "/.dominium.local/",
    "/.aide.local/",
    "/__pycache__/",
)

FORBIDDEN_PATTERNS = [
    (re.compile(r"^\s*#\s*include\s*[<\"]filesystem[>\"]", re.M), "cpp17.macos109.no_filesystem", "std::filesystem requires a newer Apple libc++ deployment surface"),
    (re.compile(r"\bstd::filesystem\b"), "cpp17.macos109.no_filesystem", "std::filesystem requires a newer Apple libc++ deployment surface"),
    (re.compile(r"^\s*#\s*include\s*[<\"]memory_resource[>\"]", re.M), "cpp17.macos109.no_pmr", "std::pmr is not part of the macOS 10.9.5 C++17 subset"),
    (re.compile(r"\bstd::pmr\b"), "cpp17.macos109.no_pmr", "std::pmr is not part of the macOS 10.9.5 C++17 subset"),
    (re.compile(r"^\s*#\s*include\s*[<\"]charconv[>\"]", re.M), "cpp17.macos109.no_charconv", "std::to_chars/from_chars are not portable to the macOS 10.9.5 subset"),
    (re.compile(r"\bstd::(?:to_chars|from_chars)\b"), "cpp17.macos109.no_charconv", "std::to_chars/from_chars are not portable to the macOS 10.9.5 subset"),
    (re.compile(r"^\s*#\s*include\s*[<\"]any[>\"]", re.M), "cpp17.macos109.no_any", "std::any throwing access depends on newer standard-library support"),
    (re.compile(r"\bstd::any\b"), "cpp17.macos109.no_any", "std::any throwing access depends on newer standard-library support"),
]

WARNING_PATTERNS = [
    (re.compile(r"^\s*#\s*include\s*[<\"]optional[>\"]", re.M), "cpp17.macos109.optional_guard", "std::optional is allowed only when throwing value() access is avoided or guarded"),
    (re.compile(r"^\s*#\s*include\s*[<\"]variant[>\"]", re.M), "cpp17.macos109.variant_guard", "std::variant is allowed only when throwing access paths are avoided or guarded"),
    (re.compile(r"\.value\s*\("), "cpp17.macos109.no_throwing_optional_value", "value() access may throw; prefer bool/has_value/operator* or explicit result handling"),
]


def normalize(path) -> str:
    return str(path).replace("\\", "/")


def finding(level: str, code: str, path: str, message: str, line=None) -> dict:
    item = {"level": level, "code": code, "path": path, "message": message}
    if line is not None:
        item["line"] = line
    return item


def line_for(text: str, offset: int) -> int:
    return text[:offset].count("\n") + 1


def iter_files(repo_root: Path):
    for rel_root in SCAN_ROOTS:
        root = repo_root / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SOURCE_EXTS:
                continue
            rel = "/" + normalize(path.relative_to(repo_root))
            if any(marker in rel for marker in EXCLUDE_MARKERS):
                continue
            yield path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    findings: list[dict] = []
    files_checked = 0

    for path in iter_files(repo_root):
        files_checked += 1
        rel = normalize(path.relative_to(repo_root))
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern, code, message in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(finding("error", code, rel, message, line_for(text, match.start())))
        for pattern, code, message in WARNING_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(finding("warning", code, rel, message, line_for(text, match.start())))

    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    result = {
        "schema_version": "dominium.build.cpp17_subset.validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "strict": bool(args.strict),
        "files_checked": files_checked,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("C++17 restricted library validation: {0}".format(result["status"]))
        print("files: {0} errors: {1} warnings: {2}".format(files_checked, len(errors), len(warnings)))
        for item in findings[:80]:
            loc = item["path"] + (":{0}".format(item["line"]) if "line" in item else "")
            print("{0} {1}: {2}: {3}".format(item["level"].upper(), item["code"], loc, item["message"]))
        if len(findings) > 80:
            print("... {0} additional findings omitted; use --json for full detail".format(len(findings) - 80))
    if args.strict and errors:
        return 1
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
