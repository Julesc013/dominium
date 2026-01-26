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
    "client",
    "game",
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

FORBIDDEN_PATTERNS = [
    (re.compile(r"\bgravity\b", re.IGNORECASE), "gravity assumption"),
    (re.compile(r"\batmospher\w*\b", re.IGNORECASE), "atmosphere assumption"),
    (re.compile(r"\boxygen\b", re.IGNORECASE), "oxygen assumption"),
    (re.compile(r"\bnitrogen\b", re.IGNORECASE), "nitrogen assumption"),
    (re.compile(r"\bsea\s+level\b", re.IGNORECASE), "sea-level assumption"),
    (re.compile(r"\b9\.81\b"), "earth gravity constant"),
    (re.compile(r"\b9\.8\b"), "earth gravity constant"),
    (re.compile(r"\b1g\b", re.IGNORECASE), "1g assumption"),
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
    parser = argparse.ArgumentParser(description="SLICE-1 hardcoded physical constants lint.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations = []

    for path, rel_path in iter_files(repo_root):
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

    print("No hardcoded physical constants detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
