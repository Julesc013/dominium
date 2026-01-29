import argparse
import os
import re
import sys

from invariant_utils import is_override_active


SOURCE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".inc", ".ipp"}

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
    "client/tests",
    "server/tests",
    "launcher/tests",
    "setup/tests",
    "tools/tests",
)

SCOPE_PREFIX_RE = re.compile(r'["\'](game|client|client\.ui|launcher|setup|tools|ops)\.[^"\']+["\']',
                             re.IGNORECASE)

ROOT_RULES = {
    "engine": (),
    "game": ("game.",),
    "server": ("game.", "ops."),
    "client": ("client.", "client.ui."),
    "launcher": ("launcher.", "ops."),
    "setup": ("setup.", "ops."),
    "tools": ("tools.", "ops."),
}


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
    parser = argparse.ArgumentParser(description="Invariant: capability scopes do not cross.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    invariant_id = "INV-CAPABILITY-SCOPE"
    if is_override_active(repo_root, invariant_id):
        print("override active for {}".format(invariant_id))
        return 0

    violations = []
    for root, allowed_prefixes in ROOT_RULES.items():
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for path in iter_files(abs_root, repo_root):
            rel = repo_rel(repo_root, path)
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
            for match in SCOPE_PREFIX_RE.finditer(text):
                token = match.group(1).lower()
                token_prefix = token + "."
                if token_prefix in allowed_prefixes:
                    continue
                violations.append("{}:{}".format(rel, match.group(0)))

    if violations:
        print("Capability scope crossing detected:")
        for item in sorted(violations):
            print("  {}".format(item))
        return 1

    print("capability-scope invariant OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
