"""FAST test: EMB-1 tool affordances require explicit tool entitlements."""

from __future__ import annotations

import sys


TEST_ID = "test_tool_entitlement_required"
TEST_TAGS = ["fast", "embodiment", "toolbelt", "authority"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from embodiment import build_mine_at_cursor_task
    from tools.xstack.testx.tests.emb1_testlib import authority_context, selection

    denied = build_mine_at_cursor_task(
        authority_context=authority_context(entitlements=["entitlement.control.admin"]),
        subject_id="subject.player",
        selection=selection(),
        volume_amount=1,
    )
    if str(denied.get("result", "")) != "refused":
        return {"status": "fail", "message": "terrain tool should refuse without ent.tool.terrain_edit"}
    allowed = build_mine_at_cursor_task(
        authority_context=authority_context(entitlements=["entitlement.control.admin", "ent.tool.terrain_edit"]),
        subject_id="subject.player",
        selection=selection(),
        volume_amount=1,
    )
    if str(allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "terrain tool should complete with ent.tool.terrain_edit"}
    return {"status": "pass", "message": "EMB-1 tool affordances require explicit entitlements"}
