"""STRICT test: affordance lists are deterministic for identical perceived/law/authority input."""

from __future__ import annotations

import sys


TEST_ID = "testx.interaction.affordance_list_deterministic"
TEST_TAGS = ["strict", "interaction", "determinism"]


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

    perceived = perceived_model()
    law = law_profile()
    authority = authority_context(entitlements=["entitlement.inspect", "entitlement.move"])
    registry = interaction_action_registry()

    first = build_affordance_list(
        perceived_model=perceived,
        target_semantic_id="agent.alpha",
        law_profile=law,
        authority_context=authority,
        interaction_action_registry=registry,
        include_disabled=True,
        repo_root="",
    )
    second = build_affordance_list(
        perceived_model=perceived,
        target_semantic_id="agent.alpha",
        law_profile=law,
        authority_context=authority,
        interaction_action_registry=registry,
        include_disabled=True,
        repo_root="",
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "affordance generation refused unexpectedly"}

    first_payload = dict(first.get("affordance_list") or {})
    second_payload = dict(second.get("affordance_list") or {})
    if first_payload != second_payload:
        return {"status": "fail", "message": "affordance list payload drifted across identical inputs"}
    if str(first.get("list_hash", "")) != str(second.get("list_hash", "")):
        return {"status": "fail", "message": "affordance list hash drifted across identical inputs"}

    rows = list(first_payload.get("affordances") or [])
    ordered = sorted(rows, key=lambda row: (str(row.get("display_name", "")).lower(), str(row.get("process_id", "")), str(row.get("affordance_id", ""))))
    if rows != ordered:
        return {"status": "fail", "message": "affordance ordering is not deterministic"}
    return {"status": "pass", "message": "affordance list determinism passed"}
