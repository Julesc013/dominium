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

FLOAT_TOKEN_RE = re.compile(r"\b(long\s+double|double|float)\b")


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no floating point in authoritative code.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-AUTH-FLOAT"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    for rel_dir in AUTHORITATIVE_DIRS:
        root = os.path.join(repo_root, rel_dir)
        if not os.path.isdir(root):
            continue
        for path in iter_files([root], DEFAULT_EXCLUDES, [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"]):
            rel = repo_rel(repo_root, path)
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            for idx, line in enumerate(stripped.splitlines(), start=1):
                if FLOAT_TOKEN_RE.search(line):
                    violations.append("{}:{}: floating point token".format(rel, idx))

    if violations:
        print("Floating point usage detected in authoritative code:")
        for item in sorted(violations):
            print("  {}".format(item))
        return 1

    print("float-authoritative invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
