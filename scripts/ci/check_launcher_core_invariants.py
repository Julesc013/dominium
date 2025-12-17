#!/usr/bin/env python3
"""
Deterministic invariant checks for the launcher core.

This is a lightweight guardrail for PROMPT L-8 hardening:
- No UI/toolkit includes in launcher core.
- No direct use of global nondeterminism sources (rand/time/env).

The checks are intentionally conservative and grep-like; they do not attempt
full C/C++ parsing.
"""

from __future__ import annotations

import pathlib
import re
import sys


CORE_ROOT = pathlib.Path("source/dominium/launcher/core")


FORBIDDEN_INCLUDE_PREFIXES = (
    "domino/dui",
    "domino/dgfx",
    "domino/view_ui",
    "dominium/launcher/ui",
)

FORBIDDEN_INCLUDES_EXACT = {
    "windows.h",
    "winuser.h",
    "unistd.h",
    "sys/time.h",
    "sys/stat.h",
    "sys/types.h",
    "mach/mach_time.h",
    "Cocoa/Cocoa.h",
    "UIKit/UIKit.h",
    "X11/Xlib.h",
}

# Global nondeterminism sources (best-effort).
FORBIDDEN_CALL_PATTERNS = (
    re.compile(r"\brand\s*\("),
    re.compile(r"\bsrand\s*\("),
    re.compile(r"\bgetenv\s*\("),
    re.compile(r"\bsetenv\s*\("),
    re.compile(r"\bputenv\s*\("),
    re.compile(r"\btime\s*\("),
)

INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]")


def iter_source_files(root: pathlib.Path) -> list[pathlib.Path]:
    exts = {".c", ".cpp", ".h"}
    files: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in exts:
            files.append(path)
    files.sort(key=lambda p: str(p).replace("\\", "/"))
    return files


def main() -> int:
    if not CORE_ROOT.exists():
        print(f"ERROR: expected {CORE_ROOT} to exist", file=sys.stderr)
        return 2

    violations: list[str] = []
    for path in iter_source_files(CORE_ROOT):
        try:
            data = path.read_bytes()
        except OSError as exc:
            violations.append(f"{path}: read_failed: {exc}")
            continue

        text = data.decode("utf-8", errors="replace")
        lines = text.splitlines()

        for i, line in enumerate(lines, start=1):
            m = INCLUDE_RE.match(line)
            if m:
                hdr = m.group(1)
                hdr_norm = hdr.replace("\\", "/")
                hdr_base = hdr_norm.split("/")[-1]
                for pref in FORBIDDEN_INCLUDE_PREFIXES:
                    if hdr_norm.startswith(pref):
                        violations.append(f"{path}:{i}: forbidden_include_prefix:{hdr_norm}")
                        break
                if hdr_base in FORBIDDEN_INCLUDES_EXACT or hdr_norm in FORBIDDEN_INCLUDES_EXACT:
                    violations.append(f"{path}:{i}: forbidden_include:{hdr_norm}")

            for pat in FORBIDDEN_CALL_PATTERNS:
                if pat.search(line):
                    violations.append(f"{path}:{i}: forbidden_call:{pat.pattern}")
                    break

    if violations:
        print("Launcher core invariant check FAILED:")
        for v in violations:
            print(f"- {v}")
        return 1

    print("Launcher core invariant check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

