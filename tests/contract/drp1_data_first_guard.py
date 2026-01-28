import argparse
import os
import sys
from typing import Iterable, List


DATA_ROOTS = (
    ("data",),
    ("tests", "fixtures"),
)

DISALLOWED_EXTS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hpp",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".cs",
    ".js",
    ".ts",
    ".py",
    ".rb",
    ".lua",
    ".swift",
    ".m",
    ".mm",
    ".vb",
    ".sh",
    ".bat",
    ".ps1",
}


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def iter_files(root: str) -> Iterable[str]:
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            yield os.path.join(dirpath, name)


def main() -> int:
    parser = argparse.ArgumentParser(description="DRP-1 data-first guard.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations: List[str] = []

    for parts in DATA_ROOTS:
        root = os.path.join(repo_root, *parts)
        if not os.path.isdir(root):
            continue
        for path in iter_files(root):
            _, ext = os.path.splitext(path)
            if ext.lower() in DISALLOWED_EXTS:
                violations.append("code file under data-first root: {}".format(
                    repo_rel(repo_root, path)
                ))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("DRP-1 data-first guard OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
