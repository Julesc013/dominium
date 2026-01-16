#!/usr/bin/env python3
from __future__ import print_function

import os
import re
import sys


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')

SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".inl", ".inc", ".ipp",
}

RULES = {
    "engine": {
        "forbid": [
            "dom_contracts/",
            "dominium/",
            "dsk/",
            "dsu/",
            "dui/",
            "launcher/",
            "setup/",
            "tools/",
            "game/",
        ],
    },
    "launcher": {
        "forbid": [
            "dsk/",
            "dsu/",
            "dui/",
            "setup/",
            "tools/",
            "engine/",
        ],
    },
    "setup": {
        "forbid": [
            "domino/",
            "dominium/",
            "dui/",
            "launcher/",
            "tools/",
            "engine/",
        ],
    },
    "tools": {
        "forbid": [
            "dsk/",
            "dsu/",
            "launcher/",
            "setup/",
            "engine/",
        ],
    },
    "game": {
        "forbid": [
            "engine/",
            "modules/",
            "core/",
            "ecs/",
            "sim/",
            "world/",
            "io/",
            "sys/",
            "render/",
            "dsk/",
            "dsu/",
            "dui/",
            "launcher/",
            "setup/",
            "tools/",
        ],
    },
    "client": {
        "forbid": [
            "engine/",
            "modules/",
            "core/",
            "ecs/",
            "sim/",
            "world/",
            "io/",
            "sys/",
            "render/",
            "game/",
            "rules/",
            "ai/",
            "economy/",
            "content/",
            "mods/",
            "ui/",
        ],
    },
    "server": {
        "forbid": [
            "engine/",
            "modules/",
            "core/",
            "ecs/",
            "sim/",
            "world/",
            "io/",
            "sys/",
            "render/",
            "game/",
            "rules/",
            "ai/",
            "economy/",
            "content/",
            "mods/",
            "ui/",
        ],
    },
}

SKIP_DIRS = {
    ".git",
    ".vs",
    ".vscode",
    "build",
    "dist",
    "out",
    "legacy",
    "docs",
    "schema",
    "ci",
    "tests",
}


def iter_source_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = os.path.relpath(dirpath, REPO_ROOT)
        parts = rel_dir.split(os.sep)
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() not in SOURCE_EXTS:
                continue
            full_path = os.path.join(dirpath, name)
            yield full_path


def product_for_path(path):
    rel = os.path.relpath(path, REPO_ROOT)
    parts = rel.split(os.sep)
    if not parts:
        return None
    return parts[0]


def scan_file(path, rules):
    rel = os.path.relpath(path, REPO_ROOT)
    try:
        with open(path, "r", errors="ignore") as handle:
            for idx, line in enumerate(handle, start=1):
                match = INCLUDE_RE.match(line)
                if not match:
                    continue
                include_path = match.group(1).replace("\\", "/")
                for prefix in rules.get("forbid", []):
                    if include_path.startswith(prefix):
                        yield (rel, idx, include_path, prefix)
                        break
    except IOError:
        return


def main():
    violations = []
    for path in iter_source_files():
        product = product_for_path(path)
        if product not in RULES:
            continue
        rules = RULES[product]
        for rel, idx, include_path, prefix in scan_file(path, rules):
            violations.append((rel, idx, include_path, product, prefix))

    if not violations:
        print("Include sanity OK.")
        return 0

    print("Include sanity violations:")
    for rel, idx, include_path, product, prefix in violations:
        print(
            "{0}:{1}: {2} includes '{3}' (forbidden prefix '{4}')".format(
                rel, idx, product, include_path, prefix
            )
        )
    print("Total violations:", len(violations))
    return 1


if __name__ == "__main__":
    sys.exit(main())
