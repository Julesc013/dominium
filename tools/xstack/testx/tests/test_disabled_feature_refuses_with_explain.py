"""FAST test: disabled negotiated features refuse with explicit explain metadata."""

from __future__ import annotations


TEST_ID = "test_disabled_feature_refuses_with_explain"
TEST_TAGS = ["fast", "compat", "cap_neg", "degrade", "embodiment"]


def run(repo_root: str):
    from src.embodiment import build_logic_trace_task
    from src.compat import build_degrade_runtime_state
    from tools.xstack.testx.tests.emb1_testlib import authority_context

    runtime_state = build_degrade_runtime_state(
        {
            "compatibility_mode_id": "compat.degraded",
            "enabled_capabilities": ["cap.ui.tui"],
            "disabled_capabilities": [
                {
                    "capability_id": "cap.logic.debug_analyzer",
                    "reason_code": "degrade.optional_capability_unavailable",
                    "owner_product_id": "client",
                    "user_message_key": "explain.feature_disabled.logic_debug_analyzer",
                }
            ],
            "substituted_capabilities": [],
        }
    )
    result = build_logic_trace_task(
        authority_context=authority_context(entitlements=["ent.tool.logic_trace"]),
        compat_runtime_state=runtime_state,
        subject_id="subject.logic.trace",
        measurement_point_ids=["measure.logic.signal"],
        targets=[{"network_id": "net.logic.sample"}],
        current_tick=10,
        duration_ticks=4,
    )
    details = dict(result.get("details") or {})
    if str(result.get("reason_code", "")) != "refusal.compat.feature_disabled":
        return {"status": "fail", "message": "disabled feature did not refuse with compatibility refusal"}
    if str(details.get("explain_key", "")) != "explain.feature_disabled.logic_debug_analyzer":
        return {"status": "fail", "message": "disabled feature refusal omitted explain key"}
    return {"status": "pass", "message": "disabled negotiated feature refuses with explicit explain metadata"}
