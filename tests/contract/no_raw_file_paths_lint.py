import argparse
import os
import re
import sys
from typing import Iterable, List, Sequence, Tuple


SCAN_DIRS = (
    ("docs", "arch"),
    ("docs", "roadmap"),
    ("schema",),
    ("tests", "contract"),
)

TEXT_EXTS = {
    ".md",
    ".schema",
    ".json",
    ".txt",
    ".yaml",
    ".yml",
    ".py",
}

ABS_WIN_RE = re.compile(r"[A-Za-z]:[\\/]")
ABS_UNIX_RE = re.compile(r"/(Users|home|var|etc|opt|usr)/")


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def iter_files(repo_root: str, parts: Sequence[str]) -> Iterable[str]:
    root = os.path.join(repo_root, *parts)
    if not os.path.isdir(root):
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() not in TEXT_EXTS:
                continue
            yield os.path.join(dirpath, name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint for raw absolute file paths in contracts.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations: List[Tuple[str, int, str]] = []

    for parts in SCAN_DIRS:
        for path in iter_files(repo_root, parts):
            rel_path = repo_rel(repo_root, path)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                    for idx, line in enumerate(handle, start=1):
                        if ABS_WIN_RE.search(line):
                            violations.append((rel_path, idx, "windows absolute path"))
                            break
                        if ABS_UNIX_RE.search(line):
                            violations.append((rel_path, idx, "unix absolute path"))
                            break
            except OSError:
                continue

    if violations:
        for rel_path, line_no, label in violations:
            print("{0}:{1}: {2}".format(rel_path, line_no, label))
        return 1

    print("No raw absolute file paths detected in contract surfaces.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
