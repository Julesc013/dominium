"""FAST test: EMB-1 mine task routes through process.geometry_remove only."""

from __future__ import annotations

import sys


TEST_ID = "test_mine_calls_geometry_remove"
TEST_TAGS = ["fast", "embodiment", "toolbelt", "geometry"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.embodiment import build_mine_at_cursor_task
    from tools.xstack.testx.tests.emb1_testlib import authority_context, selection

    payload = build_mine_at_cursor_task(
        authority_context=authority_context(entitlements=["entitlement.control.admin", "ent.tool.terrain_edit"]),
        subject_id="subject.player",
        selection=selection(),
        volume_amount=2,
    )
    if str(payload.get("result", "")) != "complete":
        return {"status": "fail", "message": "mine task refused unexpectedly"}
    sequence = list(payload.get("process_sequence") or [])
    if len(sequence) != 1 or str(dict(sequence[0]).get("process_id", "")).strip() != "process.geometry_remove":
        return {"status": "fail", "message": "mine task did not route to process.geometry_remove"}
    return {"status": "pass", "message": "mine task stays process-only through geometry_remove"}
