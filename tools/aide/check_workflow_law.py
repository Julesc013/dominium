#!/usr/bin/env python3
"""Validate the AIDE-WORKFLOW-LAW-01 policy packet.

This is intentionally lightweight. It checks required files and key vocabulary
without implementing a scheduler, branch manager, or promotion engine.
"""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_FILES = [
    ".aide/policy/workflow_law.md",
    ".aide/policy/branch_roles.md",
    ".aide/policy/task_lifecycle.md",
    ".aide/policy/blocker_taxonomy.md",
    ".aide/policy/dirty_worktree_policy.md",
    ".aide/policy/parallel_execution_law.md",
    ".aide/policy/evidence_requirements.md",
    ".aide/policy/warning_acceptance_policy.md",
    "contracts/aide/aide_workflow_law.v1.json",
    ".aide/queue/current.toml",
]

REQUIRED_STATES = [
    "PROPOSED",
    "READY",
    "RUNNING",
    "DONE_LOCAL",
    "PARTIAL",
    "BLOCKED_REPAIRABLE",
    "BLOCKED_MISSING_PREREQ",
    "BLOCKED_NEEDS_DECISION",
    "BLOCKED_UNSAFE",
    "REPAIR_QUEUED",
    "RESUME_READY",
    "MERGE_CANDIDATE",
    "MERGED_TO_DEV",
    "CHECKPOINT_CANDIDATE",
    "CHECKPOINT_REPAIR",
    "PROMOTED_TO_MAIN",
    "QUARANTINED",
    "SUPERSEDED",
]

REQUIRED_ROLES = [
    "origin/main",
    "origin/dev",
    "local/dev",
    "task/<task-id>",
    "repair/<task-id>",
    "checkpoint/<wave-id>",
    "quarantine/<reason>",
    "experiment/<name>",
]

REQUIRED_BLOCKERS = [
    "dirty_worktree_unrelated",
    "dirty_worktree_same_task",
    "merge_conflict",
    "validator_failure_repairable",
    "validator_failure_policy",
    "missing_prerequisite",
    "missing_tool",
    "missing_connector",
    "missing_capability",
    "missing_secret",
    "unsafe_operation",
    "destructive_git_required",
    "architecture_decision_required",
    "human_review_required",
    "test_timeout",
    "flaky_test_suspected",
    "generated_artifact_drift",
    "stale_queue_state",
    "stale_context_packet",
    "source_authority_conflict",
]

QUEUE_REQUIRED_SNIPPETS = [
    'task = "AIDE-WORKFLOW-LAW-01"',
    'next_task = "AIDE-WORKUNIT-SCHEMA-01"',
    'alternate_next_task = "AIDE-DEV-MAIN-POLICY-01"',
    'secondary_follow_up = "AIDE-CHECKPOINT-LOOP-01"',
    'recommended_parallel_candidate = "PRESENTATION-CONTRACT-01"',
    "large_parallel_execution_authorized = false",
    "limited_parallel_prompt_generation_authorized = true",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")

    lifecycle = read(root / ".aide/policy/task_lifecycle.md") if not errors else ""
    roles = read(root / ".aide/policy/branch_roles.md") if not errors else ""
    blockers = read(root / ".aide/policy/blocker_taxonomy.md") if not errors else ""
    queue = read(root / ".aide/queue/current.toml") if (root / ".aide/queue/current.toml").is_file() else ""

    for state in REQUIRED_STATES:
        if state not in lifecycle:
            errors.append(f"missing lifecycle state: {state}")
    for role in REQUIRED_ROLES:
        if role not in roles:
            errors.append(f"missing branch role: {role}")
    for blocker in REQUIRED_BLOCKERS:
        if blocker not in blockers:
            errors.append(f"missing blocker class: {blocker}")
    for snippet in QUEUE_REQUIRED_SNIPPETS:
        if snippet not in queue:
            errors.append(f"queue missing required closeout field: {snippet}")

    if errors:
        print("AIDE workflow law check: FAIL")
        for error in errors:
            print(f"- FAIL {error}")
        return 1

    print("AIDE workflow law check: PASS")
    print(f"- checked files: {len(REQUIRED_FILES)}")
    print(f"- lifecycle states: {len(REQUIRED_STATES)}")
    print(f"- branch roles: {len(REQUIRED_ROLES)}")
    print(f"- blocker classes: {len(REQUIRED_BLOCKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
