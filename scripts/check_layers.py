#!/usr/bin/env python3
"""
Layering guardrails for kernel code.

- Scan kernel roots for forbidden OS/UI headers.
- Report exact file/line for violations.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys


KERNEL_ROOTS = (
    pathlib.Path("source/dominium/launcher/core/include"),
    pathlib.Path("source/dominium/launcher/core/src"),
    pathlib.Path("source/dominium/launcher/core/tests"),
    pathlib.Path("source/dominium/setup/core/include"),
    pathlib.Path("source/dominium/setup/core/src"),
)

FORBIDDEN_INCLUDE_EXACT = {
    "windows.h",
    "winuser.h",
    "commctrl.h",
    "shellapi.h",
    "shlobj.h",
    "shobjidl.h",
    "winsock.h",
    "winsock2.h",
    "ws2tcpip.h",
    "iphlpapi.h",
    "direct.h",
    "io.h",
    "unistd.h",
    "sys/time.h",
    "sys/stat.h",
    "sys/types.h",
    "sys/statvfs.h",
    "sys/socket.h",
    "netinet/in.h",
    "arpa/inet.h",
    "mach/mach_time.h",
    "cocoa/cocoa.h",
    "foundation/foundation.h",
    "appkit/appkit.h",
    "corefoundation/corefoundation.h",
    "uikit/uikit.h",
    "x11/xlib.h",
    "x11/xutil.h",
    "gtk/gtk.h",
    "gdk/gdk.h",
    "gdk/gdkx.h",
    "ncurses.h",
    "curses.h",
}

FORBIDDEN_INCLUDE_PREFIXES = (
    "domino/dui",
    "domino/dgfx",
    "domino/view_ui",
    "domino/ui",
    "domino/gui",
    "domino/tui",
    "domino/render",
    "domino/input",
    "dominium/launcher/ui",
    "dominium/setup/ui",
    "tools/launcher/ui",
    "tools/setup/ui",
    "x11/",
    "gtk",
    "gdk",
    "qt",
    "ncurses",
    "curses",
    "cocoa/",
    "foundation/",
    "appkit/",
    "corefoundation/",
    "uikit/",
)

FORBIDDEN_INCLUDE_SUFFIXES = (
    "_ui_actions_gen.h",
    "_ui_actions_user.h",
)

INCLUDE_RE = re.compile(r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]")


def decode_source(data: bytes) -> str:
    if data.startswith(b"\xff\xfe"):
        return data[2:].decode("utf-16-le", errors="replace")
    if data.startswith(b"\xfe\xff"):
        return data[2:].decode("utf-16-be", errors="replace")
    if b"\x00" in data[:1024]:
        try:
            return data.decode("utf-16-le", errors="replace")
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def iter_source_files(roots: tuple[pathlib.Path, ...]) -> list[pathlib.Path]:
    exts = {".c", ".cpp", ".h", ".hpp", ".inl"}
    files: list[pathlib.Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in exts:
                files.append(path)
    files.sort(key=lambda p: str(p).replace("\\", "/"))
    return files


def scan_includes(files: list[pathlib.Path]) -> list[str]:
    violations: list[str] = []
    for path in files:
        try:
            data = path.read_bytes()
        except OSError as exc:
            violations.append(f"{path}: read_failed: {exc}")
            continue
        text = decode_source(data)
        for i, line in enumerate(text.splitlines(), start=1):
            m = INCLUDE_RE.match(line)
            if not m:
                continue
            hdr_raw = m.group(1)
            hdr_norm = hdr_raw.replace("\\", "/")
            hdr_lower = hdr_norm.lower()
            hdr_base = hdr_lower.split("/")[-1]

            if hdr_lower in FORBIDDEN_INCLUDE_EXACT or hdr_base in FORBIDDEN_INCLUDE_EXACT:
                violations.append(f"{path}:{i}: forbidden_include:{hdr_norm}")
                continue

            for pref in FORBIDDEN_INCLUDE_PREFIXES:
                if hdr_lower.startswith(pref):
                    violations.append(f"{path}:{i}: forbidden_include_prefix:{hdr_norm}")
                    break
            else:
                for suf in FORBIDDEN_INCLUDE_SUFFIXES:
                    if hdr_lower.endswith(suf):
                        violations.append(f"{path}:{i}: forbidden_include_suffix:{hdr_norm}")
                        break
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Layering checks for kernel sources.")
    parser.add_argument("--build-dir", default="", help="Optional build dir (unused; reserved for future link checks).")
    args = parser.parse_args()

    if not any(root.exists() for root in KERNEL_ROOTS):
        print("ERROR: expected kernel roots to exist:", file=sys.stderr)
        for root in KERNEL_ROOTS:
            print(f"- {root}", file=sys.stderr)
        return 2

    files = iter_source_files(KERNEL_ROOTS)
    violations = scan_includes(files)

    if violations:
        print("Layering check FAILED:")
        for v in violations:
            print(f"- {v}")
        return 1

    print("Layering check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
