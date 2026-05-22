#!/usr/bin/env python3
"""Validate the AIDE-DEV-MAIN-POLICY-01 policy packet.

This is intentionally lightweight. It checks required files, required branch
role vocabulary, coordinator ownership rules, checkpoint/evidence requirements,
and fixture parseability without implementing branch automation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    ".aide/policy/dev_main_policy.md",
    ".aide/policy/checkpoint_policy.md",
    ".aide/policy/parallel_worktree_policy.md",
    ".aide/policy/dev_warning_policy.md",
    ".aide/fixtures/dev_main/valid_dev_integration.json",
    ".aide/fixtures/dev_main/valid_checkpoint_decision.json",
    ".aide/fixtures/dev_main/invalid_main_promotion_without_evidence.json",
]

REQUIRED_ROLES = [
    "origin/main",
    "origin/dev",
    "local/dev",
    "task/<task-id>",
    "repair/<task-id>",
    "repair/<blocker-id>",
    "checkpoint/<wave-id>",
    "quarantine/<reason>",
    "quarantine/<task-id>",
    "experiment/<name>",
]

DEV_MAIN_SNIPPETS = [
    "development is non-blocking",
    "promotion is evidence-blocked",
    "checkpointed, evidence-backed",
    "classified partial",
    "classified warnings",
    "BLOCKED_UNSAFE",
    ".aide/queue/current.toml",
    ".aide/context/latest-task-packet.md",
    "Full CTest remains T4/full-gate debt",
]

CHECKPOINT_SNIPPETS = [
    "checkpoint/<wave-id>",
    "included WorkUnits",
    "excluded WorkUnits",
    "validation plan",
    "warning dispositions",
    "promotion decision",
    "rollback",
    "defer",
]

PARALLEL_SNIPPETS = [
    "one worktree per task branch",
    "one task branch per WorkUnit",
    ".aide/queue/current.toml",
    "merge_conflict",
    "Do not use destructive git commands",
    "Large parallel execution remains unauthorized",
]

WARNING_SNIPPETS = [
    "PASS_WITH_WARNINGS",
    "Dev-accepted warnings are not automatically main-accepted warnings",
    "checkpoint report",
    "promotion decision",
    "BLOCKED_UNSAFE",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_snippets(errors: list[str], text: str, snippets: list[str], label: str) -> None:
    lowered = text.lower()
    for snippet in snippets:
        if snippet.lower() not in lowered:
            errors.append(f"{label} missing required snippet: {snippet}")


def load_fixture(errors: list[str], root: Path, rel: str) -> dict[str, object]:
    path = root / rel
    try:
        data = json.loads(read(path))
    except Exception as exc:  # pragma: no cover - command-line validator
        errors.append(f"fixture not valid JSON: {rel}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"fixture must be object: {rel}")
        return {}
    return data


def validate_fixtures(errors: list[str], root: Path) -> None:
    valid_dev = load_fixture(errors, root, ".aide/fixtures/dev_main/valid_dev_integration.json")
    valid_checkpoint = load_fixture(errors, root, ".aide/fixtures/dev_main/valid_checkpoint_decision.json")
    invalid_main = load_fixture(errors, root, ".aide/fixtures/dev_main/invalid_main_promotion_without_evidence.json")

    if valid_dev and valid_dev.get("expected_result") != "VALID":
        errors.append("valid_dev_integration fixture must declare expected_result VALID")
    if valid_dev and valid_dev.get("target_branch") != "origin/dev":
        errors.append("valid_dev_integration fixture must target origin/dev")
    if valid_dev and valid_dev.get("unsafe_blockers_present") is not False:
        errors.append("valid_dev_integration fixture must reject unsafe blockers")

    if valid_checkpoint and valid_checkpoint.get("expected_result") != "VALID":
        errors.append("valid_checkpoint_decision fixture must declare expected_result VALID")
    if valid_checkpoint and not valid_checkpoint.get("evidence_packet_exists"):
        errors.append("valid_checkpoint_decision fixture must include evidence")
    if valid_checkpoint and valid_checkpoint.get("target_branch") != "origin/main":
        errors.append("valid_checkpoint_decision fixture must target origin/main")

    if invalid_main and invalid_main.get("expected_result") != "INVALID":
        errors.append("invalid_main_promotion_without_evidence fixture must declare expected_result INVALID")
    if invalid_main and invalid_main.get("checkpoint_branch") is not None:
        errors.append("invalid main promotion fixture must lack checkpoint branch")
    if invalid_main and invalid_main.get("evidence_packet_exists") is not False:
        errors.append("invalid main promotion fixture must lack evidence")


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")

    if not errors:
        dev_main = read(root / ".aide/policy/dev_main_policy.md")
        checkpoint = read(root / ".aide/policy/checkpoint_policy.md")
        parallel = read(root / ".aide/policy/parallel_worktree_policy.md")
        warning = read(root / ".aide/policy/dev_warning_policy.md")

        for role in REQUIRED_ROLES:
            if role not in dev_main:
                errors.append(f"dev_main_policy missing branch role: {role}")

        require_snippets(errors, dev_main, DEV_MAIN_SNIPPETS, "dev_main_policy")
        require_snippets(errors, checkpoint, CHECKPOINT_SNIPPETS, "checkpoint_policy")
        require_snippets(errors, parallel, PARALLEL_SNIPPETS, "parallel_worktree_policy")
        require_snippets(errors, warning, WARNING_SNIPPETS, "dev_warning_policy")
        validate_fixtures(errors, root)

    if errors:
        print("AIDE dev/main policy check: FAIL")
        for error in errors:
            print(f"- FAIL {error}")
        return 1

    print("AIDE dev/main policy check: PASS")
    print(f"- checked files: {len(REQUIRED_FILES)}")
    print(f"- branch roles: {len(REQUIRED_ROLES)}")
    print("- coordinator ownership rules: present")
    print("- main promotion checkpoint/evidence gate: present")
    print("- dev warnings and unsafe blocker rules: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
