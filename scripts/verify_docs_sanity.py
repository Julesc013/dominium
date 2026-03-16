import argparse
import os
import re
import sys


LINK_RE = re.compile(r"`([^`]+)`")
REQUIRED_PATHS = (
    "docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md",
    "docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md",
    "docs/architecture/PROJECTION_LIFECYCLE.md",
    "docs/architecture/GENERATED_CODE_POLICY.md",
    "docs/architecture/LEGACY_SUPPORT_STRATEGY.md",
    "docs/architecture/FUTURE_COMPATIBILITY_AND_ARCH.md",
    "docs/policies/IDE_CONTRIBUTION_RULES.md",
    "ide/README.md",
    "ide/manifests/projection_manifest.schema.json",
)
PATH_PREFIXES = ("docs/", "schema/", "ide/", "scripts/")
PLACEHOLDER_TOKENS = ("*", "<", ">", "{", "}", "...", "::", "|")


def _normalized_target(target: str) -> str:
    token = str(target or "").strip()
    if "#" in token:
        token = token.split("#", 1)[0].strip()
    return token


def _is_concrete_repo_target(target: str) -> bool:
    token = _normalized_target(target)
    if not token or token.startswith("http"):
        return False
    if not token.startswith(PATH_PREFIXES):
        return False
    return not any(marker in token for marker in PLACEHOLDER_TOKENS)


def _scan_markdown(repo_root: str, rel_path: str, violations: list[tuple[str, str]]) -> None:
    abs_path = os.path.join(repo_root, rel_path)
    with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            for match in LINK_RE.findall(line):
                target = _normalized_target(match)
                if not _is_concrete_repo_target(target):
                    continue
                if not os.path.exists(os.path.join(repo_root, target)):
                    violations.append((f"{rel_path}:{lineno}", f"missing link target {target}"))


def main():
    parser = argparse.ArgumentParser(description="Verify required REPOX docs and link targets exist.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not os.path.exists(os.path.join(repo_root, rel)):
            violations.append((rel, "missing required doc"))

    for rel in REQUIRED_PATHS:
        if rel.endswith(".md") and os.path.exists(os.path.join(repo_root, rel)):
            _scan_markdown(repo_root, rel, violations)

    if violations:
        for path, msg in violations:
            sys.stderr.write(f"{path}: {msg}\n")
        return 1

    print("Docs sanity OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
