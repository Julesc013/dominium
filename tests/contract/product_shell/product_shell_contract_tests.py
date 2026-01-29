import argparse
import os
import re
import sys
from typing import List, Set


REQUIRED_DOCS = {
    "docs/architecture/PRODUCT_SHELL_CONTRACT.md": [
        "## A) Setup",
        "## B) Launcher",
        "## C) Client (Out of Game)",
        "## D) Client (In Game - Baseline Only)",
        "## E) Server",
        "## F) Tools",
        "SHELL-PARITY-CLI-CANON",
    ],
    "docs/ui/UX_RULES.md": [
        "UX-PARITY-CLI-CANON",
        "UX-PARITY-NO-UI-ONLY",
        "UX-REFUSAL-VISIBLE",
        "UX-MISSING-CONTENT-EXPLAINED",
        "UX-DEBUG-DISCOVERABLE",
    ],
    "docs/dev/DEBUG_AND_DIAGNOSTICS_MODEL.md": [
        "Logging expectations",
        "Error vs refusal",
        "Replay",
        "Bugreport",
    ],
    "docs/architecture/CHECKPOINTS.md": [
        "Checkpoint 1: Product shell confidence",
        "Checkpoint 2: Exploration baseline",
        "Checkpoint 3: Interaction baseline",
    ],
}

REQUIRED_ALLOW_IDS = {
    "PS-SETUP-MINIMAL",
    "PS-SETUP-OFFLINE",
    "PS-LAUNCHER-PREFLIGHT",
    "PS-LAUNCHER-COMPAT-REPORT",
    "PS-CLIENT-ZERO-ASSET",
    "PS-CLIENT-PARITY",
    "PS-SERVER-HEADLESS",
    "PS-TOOLS-READONLY",
    "PS-TOOLS-REPLAY",
}

REQUIRED_FORBID_IDS = {
    "PS-SETUP-AUTO-CONTENT",
    "PS-SETUP-SILENT-MUTATION",
    "PS-SETUP-ASSUME-CONTENT",
    "PS-LAUNCHER-HIDE-REFUSALS",
    "PS-LAUNCHER-BYPASS-COMPAT",
    "PS-CLIENT-REQUIRE-PACKS",
    "PS-CLIENT-UI-ONLY",
    "PS-SERVER-NO-LOGS",
    "PS-TOOLS-MUTATE-DEFAULT",
    "PS-TOOLS-BYPASS-LAW",
}

BEHAVIOR_RE = re.compile(r"^(?:-\s*)?(ALLOW|FORBID):\s*([A-Z0-9_-]+)\b")


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def parse_behavior_ids(text: str) -> (Set[str], Set[str]):
    allow: Set[str] = set()
    forbid: Set[str] = set()
    for line in text.splitlines():
        match = BEHAVIOR_RE.match(line.strip())
        if not match:
            continue
        kind = match.group(1)
        value = match.group(2)
        if kind == "ALLOW":
            allow.add(value)
        else:
            forbid.add(value)
    return allow, forbid


def check_required_docs(repo_root: str) -> List[str]:
    violations: List[str] = []
    for rel_path, tokens in REQUIRED_DOCS.items():
        path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(path):
            violations.append("missing required doc: {}".format(rel_path))
            continue
        text = load_text(path)
        for token in tokens:
            if token not in text:
                violations.append("missing token '{}' in {}".format(token, rel_path))
    return violations


def check_behavior_matrix(repo_root: str) -> List[str]:
    violations: List[str] = []
    path = os.path.join(repo_root, "docs", "architecture", "PRODUCT_SHELL_CONTRACT.md")
    if not os.path.isfile(path):
        violations.append("missing product shell contract: {}".format(repo_rel(repo_root, path)))
        return violations

    text = load_text(path)
    allow, forbid = parse_behavior_ids(text)
    if not allow:
        violations.append("no ALLOW behaviors found in product shell contract")
    if not forbid:
        violations.append("no FORBID behaviors found in product shell contract")

    overlap = allow.intersection(forbid)
    if overlap:
        violations.append("behavior ids appear in both ALLOW and FORBID: {}".format(
            ", ".join(sorted(overlap))
        ))

    missing_allow = REQUIRED_ALLOW_IDS.difference(allow)
    if missing_allow:
        violations.append("missing required ALLOW ids: {}".format(
            ", ".join(sorted(missing_allow))
        ))

    missing_forbid = REQUIRED_FORBID_IDS.difference(forbid)
    if missing_forbid:
        violations.append("missing required FORBID ids: {}".format(
            ", ".join(sorted(missing_forbid))
        ))

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Product shell contract guard.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    violations: List[str] = []
    violations.extend(check_required_docs(repo_root))
    violations.extend(check_behavior_matrix(repo_root))

    if violations:
        for violation in violations:
            print(violation)
        return 1

    print("Product shell contract guard OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
