import argparse
import os
import re
import sys


HEADER_EXTS = {".h", ".hh", ".hpp", ".hxx", ".inl"}

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

FORBIDDEN_INCLUDES = [
    "<thread>",
    "<mutex>",
    "<atomic>",
    "<future>",
    "<chrono>",
    "<filesystem>",
    "<regex>",
    "<initializer_list>",
]


def iter_headers(root):
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            _, ext = os.path.splitext(name)
            if ext.lower() not in HEADER_EXTS:
                continue
            yield os.path.join(dirpath, name)


def check_headers(repo_root, rel_root, violations):
    base = os.path.join(repo_root, rel_root)
    if not os.path.isdir(base):
        return
    for path in iter_headers(base):
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for idx, line in enumerate(handle, start=1):
                    for token in FORBIDDEN_TOKENS:
                        if re.search(r"\\b" + re.escape(token) + r"\\b", line):
                            violations.append((rel, idx, "forbidden token {}".format(token)))
                            raise StopIteration
                    for inc in FORBIDDEN_INCLUDES:
                        if inc in line:
                            violations.append((rel, idx, "forbidden include {}".format(inc)))
                            raise StopIteration
        except StopIteration:
            continue
        except OSError:
            continue


def main():
    parser = argparse.ArgumentParser(description="Legacy public header checks.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    for rel_root in ("engine/include", "game/include", "sdk"):
        check_headers(repo_root, rel_root, violations)

    if violations:
        for rel, line, detail in violations:
            print("{0}:{1}: {2}".format(rel, line, detail))
        return 1

    print("Legacy header checks OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
