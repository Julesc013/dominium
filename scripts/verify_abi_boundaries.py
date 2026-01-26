import argparse
import os
import re
import sys


FORBIDDEN_TOKENS = [
    "std::",
    "#include <string>",
    "#include <vector>",
    "#include <map>",
    "#include <set>",
    "#include <unordered_map>",
    "#include <unordered_set>",
    "#include <list>",
    "#include <deque>",
    "#include <array>",
    "#include <memory>",
    "#include <functional>",
    "#include <future>",
    "#include <thread>",
    "#include <mutex>",
    "#include <optional>",
    "#include <variant>",
    "#include <span>",
    "using namespace std",
]


def iter_headers(root):
    for base, _, files in os.walk(root):
        for name in files:
            if name.endswith((".h", ".hpp")):
                yield os.path.join(base, name)


def main():
    parser = argparse.ArgumentParser(description="Verify ABI boundary rules for public headers.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    public_roots = [
        "engine/include",
        "game/include",
        "libs/contracts/include",
        "launcher/include",
        "setup/include",
        "tools/ui_shared/include",
    ]

    violations = []
    for rel_root in public_roots:
        root = os.path.join(repo_root, rel_root)
        if not os.path.isdir(root):
            continue
        for path in iter_headers(root):
            rel = os.path.relpath(path, repo_root).replace("\\", "/")
            if "/_internal/" in rel:
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for lineno, line in enumerate(handle, start=1):
                    for token in FORBIDDEN_TOKENS:
                        if token in line:
                            violations.append((rel, lineno, token))

    if violations:
        for rel, lineno, token in violations:
            sys.stderr.write(f"{rel}:{lineno}: forbidden STL token '{token}'\n")
        return 1

    print("ABI boundary check OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
