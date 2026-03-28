"""FAST test: EMB-1 logic analyzer sessions are bounded deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_trace_bounded"
TEST_TAGS = ["fast", "embodiment", "toolbelt", "logic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from embodiment import build_logic_trace_task
    from tools.xstack.testx.tests.emb1_testlib import authority_context

    payload = build_logic_trace_task(
        authority_context=authority_context(entitlements=["ent.tool.logic_trace"]),
        subject_id="net.logic.sample",
        measurement_point_ids=["measure.logic.signal"],
        targets=[
            {
                "subject_id": "net.logic.sample",
                "network_id": "net.logic.sample",
                "element_id": "inst.logic.and.1",
                "port_id": "out.q",
                "measurement_point_id": "measure.logic.signal",
            }
        ],
        current_tick=7,
        duration_ticks=99,
    )
    if str(payload.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic analyzer task refused unexpectedly"}
    if int(payload.get("bounded_duration_ticks", 0) or 0) != 32:
        return {"status": "fail", "message": "logic analyzer duration was not bounded to registry policy"}
    return {"status": "pass", "message": "logic analyzer duration stays bounded deterministically"}
