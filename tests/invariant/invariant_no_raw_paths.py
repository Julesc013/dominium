import argparse
import os
import re
import sys

from invariant_utils import is_override_active


SCAN_DIRS = (
    ("data", "packs"),
    ("data", "world"),
    ("data", "worldgen"),
    ("schema",),
    ("tests", "fixtures"),
    ("tests", "contract"),
)

TEXT_EXTS = {
    ".md",
    ".schema",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".txt",
    ".replay",
    ".worlddef",
    ".save",
    ".pack",
    ".manifest",
    ".ini",
    ".cfg",
}

ABS_WIN_RE = re.compile(r"[A-Za-z]:[\\/]")
ABS_UNIX_RE = re.compile(r"/(Users|home|var|etc|opt|usr|private)/")
ABS_UNC_RE = re.compile(r"\\\\\\\\[^\\\\/]+[\\\\/]")


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def iter_files(repo_root, parts):
    root = os.path.join(repo_root, *parts)
    if not os.path.isdir(root):
        return []
    files = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() not in TEXT_EXTS:
                continue
            files.append(os.path.join(dirpath, name))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no raw absolute paths in packs/worlddefs/saves/replays.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-NO-RAW-PATHS"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    for parts in SCAN_DIRS:
        for path in iter_files(repo_root, parts):
            rel = repo_rel(repo_root, path)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                    for idx, line in enumerate(handle, start=1):
                        if ABS_WIN_RE.search(line):
                            violations.append("{}:{}: windows absolute path".format(rel, idx))
                            break
                        if ABS_UNIX_RE.search(line):
                            violations.append("{}:{}: unix absolute path".format(rel, idx))
                            break
                        if ABS_UNC_RE.search(line):
                            violations.append("{}:{}: UNC absolute path".format(rel, idx))
                            break
            except OSError:
                continue

    if violations:
        print("{}: raw path violations detected".format(invariant_id))
        for item in sorted(violations):
            print(item)
        return 1

    print("no raw absolute paths detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
