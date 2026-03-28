"""FAST test: PROC-4 capsule eligibility requires capsule_eligible maturity state."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_capsule_eligibility_requires_state"
TEST_TAGS = ["fast", "proc", "maturity", "capsule"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.maturity.maturity_engine import (
        process_capsule_eligibility_status,
        process_lifecycle_policy_rows_by_id,
    )

    lifecycle_registry = _load_json(
        repo_root, "data/registries/process_lifecycle_policy_registry.json"
    )
    lifecycle_rows = process_lifecycle_policy_rows_by_id(lifecycle_registry)
    default_policy = dict(lifecycle_rows.get("proc.lifecycle.default") or {})
    strict_policy = dict(lifecycle_rows.get("proc.lifecycle.rank_strict") or {})
    if not default_policy or not strict_policy:
        return {"status": "fail", "message": "missing lifecycle policies for eligibility checks"}

    not_ready = process_capsule_eligibility_status(
        maturity_state="certified",
        lifecycle_policy_row=default_policy,
        has_process_certificate=True,
        require_human_or_institution_cert=False,
    )
    if bool(not_ready.get("eligible", False)):
        return {"status": "fail", "message": "certified state must not be capsule eligible directly"}
    if str(not_ready.get("reason_code", "")).strip() != "maturity_state_not_capsule_eligible":
        return {"status": "fail", "message": "expected maturity-state refusal reason for non-capsule state"}

    strict_without_cert = process_capsule_eligibility_status(
        maturity_state="capsule_eligible",
        lifecycle_policy_row=strict_policy,
        has_process_certificate=False,
        require_human_or_institution_cert=False,
    )
    if bool(strict_without_cert.get("eligible", False)):
        return {"status": "fail", "message": "strict lifecycle policy must require process certificate"}

    strict_with_cert = process_capsule_eligibility_status(
        maturity_state="capsule_eligible",
        lifecycle_policy_row=strict_policy,
        has_process_certificate=True,
        require_human_or_institution_cert=False,
    )
    if not bool(strict_with_cert.get("eligible", False)):
        return {"status": "fail", "message": "capsule_eligible with cert should pass strict policy gate"}
    return {"status": "pass", "message": "PROC-4 capsule eligibility gating enforced"}
