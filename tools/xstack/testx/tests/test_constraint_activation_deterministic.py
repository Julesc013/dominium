"""FAST test: core constraint activation and enforcement hooks are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.constraint_activation_deterministic"
TEST_TAGS = ["fast", "core", "constraint", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.constraints.constraint_engine import build_constraint_enforcement_hooks
    from tools.xstack.compatx.canonical_json import canonical_sha256

    constraints = [
        {
            "schema_version": "1.0.0",
            "constraint_id": "constraint.alpha",
            "constraint_type_id": "constraint.guide_rail",
            "participant_ids": ["entity.a", "entity.b"],
            "parameters": {"lane_id": "lane.1"},
            "enforcement_policy_id": "policy.default",
            "active": True,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "constraint_id": "constraint.beta",
            "constraint_type_id": "constraint.docking",
            "participant_ids": ["entity.a", "entity.missing"],
            "parameters": {},
            "enforcement_policy_id": "policy.default",
            "active": True,
            "extensions": {},
        },
    ]
    participants = ["entity.a", "entity.b", "entity.c"]

    first = build_constraint_enforcement_hooks(
        constraint_rows=constraints,
        known_participant_ids=participants,
        max_constraints=64,
    )
    second = build_constraint_enforcement_hooks(
        constraint_rows=constraints,
        known_participant_ids=participants,
        max_constraints=64,
    )
    if first != second:
        return {"status": "fail", "message": "constraint activation output is non-deterministic"}

    hooks = dict(first.get("enforcement_hooks") or {})
    guide_rows = [dict(row) for row in list(hooks.get("constraint.guide_rail") or []) if isinstance(row, dict)]
    if len(guide_rows) != 1:
        return {"status": "fail", "message": "expected one valid guide_rail constraint hook"}

    violations = [dict(row) for row in list(first.get("violations") or []) if isinstance(row, dict)]
    if len(violations) != 1:
        return {"status": "fail", "message": "expected one deterministic participant-missing violation"}

    hash_a = canonical_sha256(first)
    hash_b = canonical_sha256(second)
    if hash_a != hash_b:
        return {"status": "fail", "message": "constraint deterministic hash diverged"}

    return {"status": "pass", "message": "Constraint activation deterministic behavior passed"}

