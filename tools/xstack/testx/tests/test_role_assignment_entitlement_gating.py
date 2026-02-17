"""STRICT test: role assignment is entitlement and law gated."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.role_assignment_entitlement_gating"
TEST_TAGS = ["strict", "civilisation", "orders", "institutions", "authority"]


def _assign_once(*, entitlements: list[str], allow_role_delegation: bool) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.order_testlib import authority_context, base_state, law_profile, policy_context, with_cohort

    state = with_cohort(base_state(), "cohort.role.alpha", size=5, faction_id="faction.alpha", location_ref="region.alpha")
    law = law_profile(["process.role_assign"], allow_role_delegation=allow_role_delegation)
    authority = authority_context(entitlements)
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.role.assign.001",
            "process_id": "process.role_assign",
            "inputs": {
                "subject_id": "cohort.role.alpha",
                "role_id": "role.leader",
                "institution_type_id": "inst.band_council",
                "faction_id": "faction.alpha",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy_context(),
    )
    return {
        "result": dict(result),
        "state": state,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    missing = _assign_once(entitlements=["entitlement.civ.order"], allow_role_delegation=True)
    missing_result = dict(missing.get("result") or {})
    if str(missing_result.get("result", "")) != "refused":
        return {"status": "fail", "message": "role assign should refuse when entitlement.civ.role_assign is missing"}
    missing_refusal = dict(missing_result.get("refusal") or {})
    if str(missing_refusal.get("reason_code", "")) != "refusal.civ.entitlement_missing":
        return {"status": "fail", "message": "missing role-assign entitlement should map to refusal.civ.entitlement_missing"}

    blocked = _assign_once(entitlements=["entitlement.civ.role_assign"], allow_role_delegation=False)
    blocked_result = dict(blocked.get("result") or {})
    if str(blocked_result.get("result", "")) != "refused":
        return {"status": "fail", "message": "role assign should refuse when law disables delegation"}
    blocked_refusal = dict(blocked_result.get("refusal") or {})
    if str(blocked_refusal.get("reason_code", "")) != "refusal.civ.law_forbidden":
        return {"status": "fail", "message": "law delegation disable should map to refusal.civ.law_forbidden"}

    allowed_a = _assign_once(entitlements=["entitlement.civ.role_assign"], allow_role_delegation=True)
    allowed_b = _assign_once(entitlements=["entitlement.civ.role_assign"], allow_role_delegation=True)
    allowed_a_result = dict(allowed_a.get("result") or {})
    allowed_b_result = dict(allowed_b.get("result") or {})
    if str(allowed_a_result.get("result", "")) != "complete" or str(allowed_b_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "role assignment should complete when entitlement and law allow delegation"}
    if str(allowed_a_result.get("assignment_id", "")) != str(allowed_b_result.get("assignment_id", "")):
        return {"status": "fail", "message": "role assignment_id must be deterministic"}

    role_rows = sorted(
        (dict(row) for row in list((allowed_a.get("state") or {}).get("role_assignment_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("assignment_id", "")),
    )
    if len(role_rows) != 1:
        return {"status": "fail", "message": "expected exactly one role assignment row after successful assign"}
    row = dict(role_rows[0])
    if str(row.get("role_id", "")) != "role.leader":
        return {"status": "fail", "message": "role assignment role_id mismatch"}
    granted = sorted(set(str(item).strip() for item in (row.get("granted_entitlements") or []) if str(item).strip()))
    if "entitlement.civ.role_assign" not in granted:
        return {"status": "fail", "message": "leader role should carry delegated entitlement.civ.role_assign in bounded list"}
    return {"status": "pass", "message": "role assignment entitlement and law gating passed"}

