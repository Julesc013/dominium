#!/usr/bin/env python3
from __future__ import print_function

import os
import re
import sys


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

INCLUDE_DIR_RE = re.compile(r'^\s*include_directories\s*\(', re.IGNORECASE)

SKIP_DIRS = {
    ".git",
    ".vs",
    ".vscode",
    "build",
    "dist",
    "out",
    "legacy",
    "external",
    "third_party",
    "deps",
    "artifacts",
    "schema",
    "docs",
}


def iter_cmake_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = os.path.relpath(dirpath, REPO_ROOT)
        parts = rel_dir.split(os.sep)
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name == "CMakeLists.txt" or name.lower().endswith(".cmake"):
                yield os.path.join(dirpath, name)


def scan_file(path):
    rel = os.path.relpath(path, REPO_ROOT)
    try:
        with open(path, "r", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                if INCLUDE_DIR_RE.search(line):
                    return (rel, idx, line.strip())
    except IOError:
        return None
    return None


def main():
    violations = []
    for path in iter_cmake_files():
        hit = scan_file(path)
        if hit:
            violations.append(hit)

    if not violations:
        print("CMake global include check OK.")
        return 0

    print("CMake global include violations:")
    for rel, idx, line in violations:
        print("{0}:{1}: {2}".format(rel, idx, line))
    print("Total violations:", len(violations))
    return 1


if __name__ == "__main__":
    sys.exit(main())
