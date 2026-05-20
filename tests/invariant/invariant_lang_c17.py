import argparse
import os
import re
import sys

from invariant_utils import is_override_active

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "ci")))
from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings


SCAN_ROOTS = (
    os.path.join("engine", "modules"),
    os.path.join("engine", "render"),
    os.path.join("engine", "tests"),
)

SOURCE_EXTS = [".c", ".h"]

FORBIDDEN_PATTERNS = [
    (re.compile(r"\b_Atomic\b"), "C atomics are not the portable concurrency substrate"),
    (re.compile(r"\batomic_[A-Za-z0-9_]+\b"), "C atomics are not the portable concurrency substrate"),
    (re.compile(r"\b(thrd|mtx|cnd|tss)_[A-Za-z0-9_]+\b"), "C threads are not the portable concurrency substrate"),
]

FORBIDDEN_INCLUDES = (
    "<stdatomic.h>",
    "<threads.h>",
    "<complex.h>",
)


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: C17 deterministic C subset.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-LANG-C17"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    for rel_root in SCAN_ROOTS:
        root = os.path.join(repo_root, rel_root)
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, SOURCE_EXTS):
            rel = repo_rel(repo_root, path)
            text = read_text(path)
            if text is None:
                continue
            for idx, line in enumerate(text.splitlines(), start=1):
                for inc in FORBIDDEN_INCLUDES:
                    if inc in line:
                        violations.append("{}:{}: forbidden include {}".format(rel, idx, inc))
                        break
            stripped = strip_c_comments_and_strings(text)
            for idx, line in enumerate(stripped.splitlines(), start=1):
                for pattern, label in FORBIDDEN_PATTERNS:
                    if pattern.search(line):
                        violations.append("{}:{}: {}".format(rel, idx, label))

    if violations:
        print("{}: C17 subset violations detected".format(invariant_id))
        for item in sorted(set(violations)):
            print(item)
        return 1

    print("C17 deterministic subset scan OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
