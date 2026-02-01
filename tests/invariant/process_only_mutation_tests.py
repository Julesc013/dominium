import argparse
import os
import re
import sys

from invariant_utils import is_override_active

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "ci")))
from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings


SCAN_ROOTS = (
    "engine",
    "game",
)

ALLOWLIST_DIRS = (
    os.path.join("engine", "modules", "ecs"),
    os.path.join("engine", "modules", "execution"),
)
ALLOWLIST_FILES = (
    os.path.join("engine", "include", "domino", "ecs", "ecs_storage_iface.h"),
)

MUTATION_TOKENS = (
    re.compile(r"\bapply_writes\s*\("),
    re.compile(r"\bapply_write\s*\("),
    re.compile(r"\bapply_reduce\s*\("),
    re.compile(r"\bdom_ecs_write_op\b"),
    re.compile(r"\bdom_ecs_write_buffer\b"),
)


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def is_allowlisted(rel_path):
    for allow in ALLOWLIST_DIRS:
        if rel_path.startswith(allow.replace("\\", "/") + "/"):
            return True
    for allow in ALLOWLIST_FILES:
        if rel_path == allow.replace("\\", "/"):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: state mutation occurs only via Process execution.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-PROCESS-ONLY-MUTATION"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    exts = [".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"]
    for root in SCAN_ROOTS:
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for path in iter_files([abs_root], DEFAULT_EXCLUDES, exts):
            rel = repo_rel(repo_root, path)
            if rel.startswith("engine/tests/") or rel.startswith("game/tests/"):
                continue
            if is_allowlisted(rel):
                continue
            text = read_text(path)
            if text is None:
                continue
            stripped = strip_c_comments_and_strings(text)
            for idx, line in enumerate(stripped.splitlines(), start=1):
                for token_re in MUTATION_TOKENS:
                    if token_re.search(line):
                        violations.append("{}:{}: {}".format(rel, idx, token_re.pattern))

    if violations:
        print("Process-only mutation invariant violated:")
        for item in sorted(violations):
            print("  {}".format(item))
        return 1

    print("process-only-mutation invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
