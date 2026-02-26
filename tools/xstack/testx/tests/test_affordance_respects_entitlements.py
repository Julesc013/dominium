"""STRICT test: affordance generation respects law/authority entitlements and emits disabled rows with hints."""

from __future__ import annotations

import sys


TEST_ID = "testx.interaction.affordance_respects_entitlements"
TEST_TAGS = ["strict", "interaction", "authority"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.affordance_generator import build_affordance_list
    from tools.xstack.testx.tests.interaction_testlib import (
        authority_context,
        interaction_action_registry,
        law_profile,
        perceived_model,
    )

    listed = build_affordance_list(
        perceived_model=perceived_model(),
        target_semantic_id="agent.alpha",
        law_profile=law_profile(),
        authority_context=authority_context(entitlements=["entitlement.move"]),
        interaction_action_registry=interaction_action_registry(),
        include_disabled=True,
        repo_root="",
    )
    if str(listed.get("result", "")) != "complete":
        return {"status": "fail", "message": "affordance listing refused unexpectedly"}

    rows = list((dict(listed.get("affordance_list") or {})).get("affordances") or [])
    inspect_row = {}
    move_row = {}
    for row in rows:
        process_id = str((dict(row)).get("process_id", "")).strip()
        if process_id == "process.inspect_generate_snapshot":
            inspect_row = dict(row)
        elif process_id == "process.agent_move":
            move_row = dict(row)

    if not inspect_row:
        return {"status": "fail", "message": "inspect affordance missing for allowed law process"}
    inspect_ext = dict(inspect_row.get("extensions") or {})
    if bool(inspect_ext.get("enabled", True)):
        return {"status": "fail", "message": "inspect affordance should be disabled when entitlement.inspect is missing"}
    missing = set(str(item).strip() for item in list(inspect_ext.get("missing_entitlements") or []) if str(item).strip())
    if "entitlement.inspect" not in missing:
        return {"status": "fail", "message": "disabled inspect affordance missing entitlement hint"}

    if not move_row:
        return {"status": "fail", "message": "move affordance missing"}
    move_ext = dict(move_row.get("extensions") or {})
    if not bool(move_ext.get("enabled", False)):
        return {"status": "fail", "message": "move affordance should remain enabled with entitlement.move"}
    return {"status": "pass", "message": "affordance entitlement gating passed"}
