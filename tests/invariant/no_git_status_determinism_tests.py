import argparse
import os
import sys


FORBIDDEN_PATTERNS = (
    "git status --porcelain",
    "repo must remain untouched",
    "working tree must remain untouched",
)


SCAN_PATHS = (
    os.path.join("tests", "tools", "tools_auditx_tests.py"),
    os.path.join("tests", "invariant", "derived_artifact_contract_tests.py"),
    os.path.join("tools", "auditx", "README.md"),
    os.path.join("docs", "governance", "AUDITX_MODEL.md"),
)


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Ensure determinism checks are canonical-hash based.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    violations = []
    for rel in SCAN_PATHS:
        abs_path = os.path.join(repo_root, rel)
        text = _read(abs_path).lower()
        if not text:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                violations.append("{} contains forbidden pattern '{}'".format(rel.replace("\\", "/"), pattern))
    if violations:
        for item in violations:
            sys.stderr.write("FAIL: {}\n".format(item))
        return 1
    print("no_git_status_determinism_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
