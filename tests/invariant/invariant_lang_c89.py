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

SOURCE_EXTS = [".c"]

FORBIDDEN_PATTERNS = [
    (re.compile(r"\brestrict\b"), "restrict keyword"),
    (re.compile(r"\binline\b"), "inline keyword"),
    (re.compile(r"\b_Bool\b"), "_Bool keyword"),
    (re.compile(r"\b_Complex\b"), "_Complex keyword"),
    (re.compile(r"\b_Imaginary\b"), "_Imaginary keyword"),
    (re.compile(r"\b_Static_assert\b"), "_Static_assert keyword"),
    (re.compile(r"\bstatic_assert\b"), "static_assert keyword"),
    (re.compile(r"\blong\\s+long\b"), "long long type"),
    (re.compile(r"\bfor\s*\(\s*(?:signed\s+|unsigned\s+)?(?:short|long|int|size_t|uint\d+_t|int\d+_t)\b"),
     "for-loop declaration"),
]

FORBIDDEN_INCLUDES = (
    "<stdint.h>",
    "<stdbool.h>",
    "<inttypes.h>",
)


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: C89-only engine C sources.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-LANG-C89"
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
        print("{}: C89 violations detected".format(invariant_id))
        for item in sorted(set(violations)):
            print(item)
        return 1

    print("C89 source scan OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
