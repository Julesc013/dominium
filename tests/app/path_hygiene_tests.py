import argparse
import os
import re
import sys


SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".py", ".inl", ".inc", ".ipp",
}

SCAN_DIRS = (
    "engine",
    "game",
    "client",
    "server",
    "launcher",
    "setup",
    "tools",
    "libs",
    "sdk",
    "app",
)

SKIP_PREFIXES = (
    "docs/",
    "schema/",
    "data/",
    "tests/",
    "legacy/",
    "build/",
    "dist/",
    "out/",
    "third_party/",
    "external/",
    "deps/",
    "game/tests/",
)

ALLOWLIST = {
    "setup/cli/setup_cli_main.c",
    "tools/tools_host_main.c",
}

ABS_PATH_RE = re.compile(r"[A-Za-z]:\\\\")
UNIX_PATH_RE = re.compile(r"/(Users|home|var|etc|opt)/")
PACK_ID_RE = re.compile(r"org\\.dominium\\.[A-Za-z0-9_.-]+")


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def should_skip(rel_path):
    for prefix in SKIP_PREFIXES:
        if rel_path.startswith(prefix):
            return True
    return False


def iter_files(repo_root):
    for base in SCAN_DIRS:
        root = os.path.join(repo_root, base)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = repo_rel(repo_root, dirpath)
            if should_skip(rel_dir + "/"):
                dirnames[:] = []
                continue
            for name in filenames:
                _, ext = os.path.splitext(name)
                if ext.lower() not in SOURCE_EXTS:
                    continue
                path = os.path.join(dirpath, name)
                rel_path = repo_rel(repo_root, path)
                if should_skip(rel_path):
                    continue
                yield path, rel_path


def main():
    parser = argparse.ArgumentParser(description="Path hygiene and pack-id checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations = []

    for path, rel_path in iter_files(repo_root):
        if rel_path in ALLOWLIST:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for idx, line in enumerate(handle, start=1):
                    if ABS_PATH_RE.search(line) or UNIX_PATH_RE.search(line):
                        violations.append((rel_path, idx, "absolute path literal"))
                        break
                    if PACK_ID_RE.search(line):
                        violations.append((rel_path, idx, "implicit base pack id"))
                        break
        except OSError:
            continue

    if violations:
        for rel, line, label in violations:
            print("{0}:{1}: {2}".format(rel, line, label))
        return 1

    print("Path hygiene checks OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
