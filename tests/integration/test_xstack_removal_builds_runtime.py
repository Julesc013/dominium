import argparse
import os
from typing import Iterable, List


FORBIDDEN_TOKENS = (
    "tools/xstack",
    "tools\\xstack",
    "tools.xstack",
)

RUNTIME_ROOTS = (
    "engine",
    "game",
    "client",
    "server",
)

SOURCE_SUFFIXES = (
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".inl",
    ".inc",
    ".ipp",
    ".ixx",
    ".py",
    ".txt",
    ".cmake",
)


def _iter_source_files(root: str) -> Iterable[str]:
    for current, dirs, files in os.walk(root):
        dirs.sort()
        files.sort()
        for name in files:
            lower = name.lower()
            if lower.endswith(SOURCE_SUFFIXES) or name == "CMakeLists.txt":
                yield os.path.join(current, name)


def _scan_file(path: str, repo_root: str, violations: List[str]) -> None:
    try:
        text = open(path, "r", encoding="utf-8").read().lower()
    except (OSError, UnicodeDecodeError):
        return
    rel = os.path.relpath(path, repo_root).replace("\\", "/")
    for token in FORBIDDEN_TOKENS:
        if token in text:
            violations.append("{} references '{}'".format(rel, token))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Integration check: runtime targets remain decoupled from tools/xstack."
    )
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations: List[str] = []

    for runtime_root in RUNTIME_ROOTS:
        abs_root = os.path.join(repo_root, runtime_root)
        if not os.path.isdir(abs_root):
            violations.append("missing runtime root {}".format(runtime_root))
            continue
        for path in _iter_source_files(abs_root):
            _scan_file(path, repo_root, violations)

    cmake_roots = [
        os.path.join(repo_root, "CMakeLists.txt"),
    ]
    for runtime_root in RUNTIME_ROOTS:
        cmake_roots.append(os.path.join(repo_root, runtime_root, "CMakeLists.txt"))
    for path in cmake_roots:
        if os.path.isfile(path):
            _scan_file(path, repo_root, violations)

    if violations:
        print("xstack removability contract failed:")
        for row in sorted(set(violations)):
            print(" - {}".format(row))
        return 1

    print("xstack removability contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
