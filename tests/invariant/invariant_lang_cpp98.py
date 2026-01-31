import argparse
import os
import re
import sys

from invariant_utils import is_override_active

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "ci")))
from hygiene_utils import DEFAULT_EXCLUDES, iter_files, read_text, strip_c_comments_and_strings


SCAN_ROOTS = (
    "game",
)

SOURCE_EXTS = [".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".hh", ".h", ".inl", ".ipp"]

FORBIDDEN_TOKENS = [
    "nullptr",
    "constexpr",
    "static_assert",
    "noexcept",
    "decltype",
    "char16_t",
    "char32_t",
    "thread_local",
    "override",
    "final",
]

FORBIDDEN_INCLUDES = (
    "<thread>",
    "<mutex>",
    "<atomic>",
    "<future>",
    "<chrono>",
    "<filesystem>",
    "<regex>",
    "<initializer_list>",
)


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: C++98-only game sources.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-LANG-CPP98"
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
                for token in FORBIDDEN_TOKENS:
                    if re.search(r"\\b" + re.escape(token) + r"\\b", line):
                        violations.append("{}:{}: forbidden token {}".format(rel, idx, token))

    if violations:
        print("{}: C++98 violations detected".format(invariant_id))
        for item in sorted(set(violations)):
            print(item)
        return 1

    print("C++98 source scan OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
