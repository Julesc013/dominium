"""FAST test: SYS-7 epistemic redaction policy is applied deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_redaction_policy_applied"
TEST_TAGS = ["fast", "system", "sys7", "forensics", "epistemic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys7_testlib import (
        base_state,
        execute_system_explain,
        seed_reliability_events,
    )

    state = base_state()
    health_result, reliability_result = seed_reliability_events(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick setup failed"}

    system_rows = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, dict)]
    system_id = str((system_rows[0] if system_rows else {}).get("system_id", "")).strip()
    if not system_id:
        return {"status": "fail", "message": "system_id missing from seeded state"}

    diegetic = execute_system_explain(
        repo_root=repo_root,
        state=state,
        system_id=system_id,
        explain_level="L3",
        requester_policy_id="policy.epistemic.diegetic",
        requester_subject_id="player.sys7",
    )
    inspector = execute_system_explain(
        repo_root=repo_root,
        state=state,
        system_id=system_id,
        explain_level="L3",
        requester_policy_id="policy.epistemic.inspector",
        requester_subject_id="inspector.sys7",
    )
    admin = execute_system_explain(
        repo_root=repo_root,
        state=state,
        system_id=system_id,
        explain_level="L3",
        requester_policy_id="policy.epistemic.admin",
        requester_subject_id="admin.sys7",
    )
    for label, result in (("diegetic", diegetic), ("inspector", inspector), ("admin", admin)):
        if str(result.get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "{} explain process failed".format(label)}

    diegetic_artifact = dict(diegetic.get("sys7_explain_artifact") or {})
    inspector_artifact = dict(inspector.get("sys7_explain_artifact") or {})
    admin_artifact = dict(admin.get("sys7_explain_artifact") or {})
    if not diegetic_artifact or not inspector_artifact or not admin_artifact:
        return {"status": "fail", "message": "one or more explain artifacts missing from state"}

    if str(diegetic_artifact.get("epistemic_redaction_level", "")).strip() != "diegetic":
        return {"status": "fail", "message": "diegetic artifact missing diegetic redaction level"}
    if str(inspector_artifact.get("epistemic_redaction_level", "")).strip() != "inspector":
        return {"status": "fail", "message": "inspector artifact missing inspector redaction level"}
    if str(admin_artifact.get("epistemic_redaction_level", "")).strip() != "admin":
        return {"status": "fail", "message": "admin artifact missing admin redaction level"}

    if list(diegetic_artifact.get("referenced_event_ids") or []):
        return {"status": "fail", "message": "diegetic artifact must not expose referenced_event_ids"}
    diegetic_causes = list(diegetic_artifact.get("cause_chain") or [])
    if not diegetic_causes:
        return {"status": "fail", "message": "diegetic cause chain missing"}
    if not all(bool(dict(row.get("extensions") or {}).get("coarse", False)) for row in diegetic_causes if isinstance(row, dict)):
        return {"status": "fail", "message": "diegetic cause chain should be coarse-redacted"}

    if not list(admin_artifact.get("referenced_event_ids") or []):
        return {"status": "fail", "message": "admin artifact should expose referenced_event_ids"}
    if len(list(admin_artifact.get("remediation_hints") or [])) < len(list(diegetic_artifact.get("remediation_hints") or [])):
        return {"status": "fail", "message": "admin remediation hints should be at least as rich as diegetic"}
    return {"status": "pass", "message": "SYS-7 redaction policy is applied deterministically by requester policy"}
