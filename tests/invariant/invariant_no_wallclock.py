import argparse
import argparse
import os
import re
import sys

from invariant_utils import is_override_active

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "ci")))
from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings


AUTHORITATIVE_DIRS = (
    os.path.join("engine", "modules", "core"),
    os.path.join("engine", "modules", "sim"),
    os.path.join("engine", "modules", "world"),
    os.path.join("game", "core"),
    os.path.join("game", "rules"),
)

SOURCE_EXTS = [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"]

FORBIDDEN_TIME_CALL_RE = re.compile(
    r"\b(time|clock|gettimeofday|clock_gettime|QueryPerformanceCounter|GetSystemTime|"
    r"GetTickCount|GetTickCount64|mach_absolute_time)\s*\("
)
FORBIDDEN_TIME_TOKEN_RE = re.compile(r"\bCLOCK_REALTIME\b")
FORBIDDEN_CHRONO_RE = re.compile(r"\bstd::chrono::|\bchrono::")


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no wall-clock dependencies in authoritative logic.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-DET-NO-WALLCLOCK"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, SOURCE_EXTS):
            rel = repo_rel(repo_root, path)
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            for idx, line in enumerate(stripped.splitlines(), start=1):
                if FORBIDDEN_TIME_CALL_RE.search(line) or FORBIDDEN_TIME_TOKEN_RE.search(line) or FORBIDDEN_CHRONO_RE.search(line):
                    violations.append("{}:{}: wall-clock dependency".format(rel, idx))

    if violations:
        print("{}: wall-clock usage detected".format(invariant_id))
        for item in sorted(violations):
            print(item)
        return 1

    print("no wall-clock dependencies detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
