import argparse
import os
import re
import sys


LINK_RE = re.compile(r"`([^`]+)`")


def main():
    parser = argparse.ArgumentParser(description="Verify required docs and link targets exist.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    required = [
        "docs/arch/REPO_OWNERSHIP_AND_PROJECTIONS.md",
        "docs/arch/IDE_AND_TOOLCHAIN_POLICY.md",
        "docs/arch/PROJECTION_LIFECYCLE.md",
        "docs/arch/GENERATED_CODE_POLICY.md",
        "docs/arch/LEGACY_SUPPORT_STRATEGY.md",
        "docs/arch/FUTURE_COMPATIBILITY_AND_ARCH.md",
        "docs/policies/IDE_CONTRIBUTION_RULES.md",
        "ide/README.md",
        "ide/manifests/projection_manifest.schema.json",
    ]

    violations = []
    for rel in required:
        if not os.path.exists(os.path.join(repo_root, rel)):
            violations.append((rel, "missing required doc"))

    for root, _, files in os.walk(os.path.join(repo_root, "docs")):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, repo_root).replace("\\", "/")
            with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                for lineno, line in enumerate(handle, start=1):
                    for match in LINK_RE.findall(line):
                        target = match.strip()
                        if not target or target.startswith("http"):
                            continue
                        if target.startswith(("docs/", "schema/", "ide/", "scripts/")):
                            if not os.path.exists(os.path.join(repo_root, target)):
                                violations.append((f"{rel}:{lineno}", f"missing link target {target}"))

    if violations:
        for path, msg in violations:
            sys.stderr.write(f"{path}: {msg}\n")
        return 1

    print("Docs sanity OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
