import argparse
import os
import re
import sys


INCLUDE_RE = re.compile(r'^\s*#\s*include\s*[<"]([^">]+)[">]')

FORBIDDEN_PREFIXES = [
    "engine/",
    "game/",
    "server/",
    "client/presentation/",
    "client/net/",
    "client/input/",
    "engine/modules/",
    "game/source/",
]


def is_forbidden_include(path):
    if path.startswith("../") or path.startswith("..\\"):
        return True, "parent include outside UI shell"
    for prefix in FORBIDDEN_PREFIXES:
        if path.replace("\\", "/").startswith(prefix):
            return True, f"forbidden include prefix: {prefix}"
    return False, ""


def iter_source_files(root):
    for base, _, files in os.walk(root):
        for name in files:
            if name.endswith((".c", ".cpp", ".h", ".hpp")):
                yield os.path.join(base, name)


def main():
    parser = argparse.ArgumentParser(description="Verify UI shell purity.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    parser.add_argument("--roots", nargs="*", default=None, help="UI shell roots (relative)")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    default_roots = [
        "client/ui",
        "launcher/gui",
        "launcher/tui",
        "setup/gui",
        "setup/tui",
        "tools/editor_gui",
        "tools/launcher/ui",
        "tools/setup/ui",
        "tools/ui_shared",
    ]
    roots = args.roots or default_roots
    roots = [os.path.join(repo_root, r) for r in roots if os.path.isdir(os.path.join(repo_root, r))]

    violations = []
    for root in roots:
        for path in iter_source_files(root):
            rel = os.path.relpath(path, repo_root).replace("\\", "/")
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for lineno, line in enumerate(handle, start=1):
                    match = INCLUDE_RE.match(line)
                    if not match:
                        continue
                    include_path = match.group(1)
                    forbidden, reason = is_forbidden_include(include_path)
                    if forbidden:
                        violations.append((rel, lineno, reason, include_path))

    if violations:
        for rel, lineno, reason, inc in violations:
            sys.stderr.write(f"{rel}:{lineno}: {reason} ({inc})\n")
        return 1

    print("UI shell purity OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
