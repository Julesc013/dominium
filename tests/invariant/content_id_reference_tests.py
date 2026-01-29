import argparse
import os
import re
import sys

from invariant_utils import is_override_active


SOURCE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"}

ROOTS = ("engine", "game")
SKIP_DIRS = {
    ".git",
    ".vs",
    ".vscode",
    "build",
    "dist",
    "out",
    "legacy",
    "docs",
    "schema",
    "third_party",
    "external",
    "deps",
}

SKIP_SUBDIRS = (
    "engine/tests",
    "game/tests",
)

REVERSE_DNS_RE = re.compile(
    r'["\']([a-z][a-z0-9]+(?:\.[a-z0-9]+){2,}[a-z0-9]*)["\']',
    re.IGNORECASE,
)

ALLOWED_PREFIXES = (
    "noise.stream.",
    "rng.state.noise.stream.",
)


def repo_rel(repo_root, path):
    return os.path.relpath(path, repo_root).replace("\\", "/")


def iter_files(root, repo_root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = repo_rel(repo_root, dirpath).replace("\\", "/")
        if rel_dir.startswith(SKIP_SUBDIRS):
            dirnames[:] = []
            continue
        parts = rel_dir.split("/")
        if parts and parts[0] in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SOURCE_EXTS:
                continue
            yield os.path.join(dirpath, filename)


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: no content IDs in engine/game code.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    invariant_id = "INV-CONTENT-ID-REFS"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    for root in ROOTS:
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for path in iter_files(abs_root, repo_root):
            rel = repo_rel(repo_root, path)
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
            for match in REVERSE_DNS_RE.finditer(text):
                token = match.group(1)
                token_l = token.lower()
                if token_l.startswith(ALLOWED_PREFIXES):
                    continue
                violations.append("{}:{}".format(rel, token))

    if violations:
        print("Content ID references found in engine/game code:")
        for item in sorted(violations):
            print("  {}".format(item))
        return 1

    print("content-id invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
