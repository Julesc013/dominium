import argparse
import os
import re
import sys


SOURCE_EXTS = {
    ".c", ".cc", ".cpp", ".cxx",
    ".h", ".hh", ".hpp", ".hxx",
    ".inl", ".inc", ".ipp",
    ".py",
}

SCAN_DIRS = (
    "app",
    "client",
    "engine",
    "game",
    "launcher",
    "libs",
    "server",
    "setup",
    "tools",
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
    "game/content/",
    "tools/ci/",
    "tools/worldgen_offline/",
)

ALLOWLIST = {
    "client/shell/client_shell.c",
}

FORBIDDEN_PATTERNS = [
    (re.compile(r"\bEarth\b", re.IGNORECASE), "Earth name"),
    (re.compile(r"\bSol\b", re.IGNORECASE), "Sol name"),
    (re.compile(r"\bMilky\s+Way\b", re.IGNORECASE), "Milky Way name"),
    (re.compile(r"body\.(sun|mercury|venus|earth|mars|jupiter|saturn|uranus|neptune)\b",
                re.IGNORECASE), "solar body id"),
    (re.compile(r"system\.sol\b", re.IGNORECASE), "Sol system id"),
    (re.compile(r"galaxy\.milky", re.IGNORECASE), "Milky Way id"),
]


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
    parser = argparse.ArgumentParser(description="SLICE-0 hardcoded identifier lint.")
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
                    for regex, label in FORBIDDEN_PATTERNS:
                        if regex.search(line):
                            violations.append((rel_path, idx, label, line.strip()))
                            break
        except OSError:
            continue

    if violations:
        for rel, line, label, text in violations:
            print("{0}:{1}: {2}: {3}".format(rel, line, label, text))
        return 1

    print("No hardcoded world identifiers detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
