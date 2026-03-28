"""STRICT test: LOGIC-10 degradation order is deterministic and canonical."""

from __future__ import annotations

import sys


TEST_ID = "test_degradation_order_deterministic"
TEST_TAGS = ["strict", "logic", "envelope", "degrade", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.eval import plan_logic_degradation_actions

    kwargs = {
        "compiled_available": True,
        "current_tick": 8,
        "requested_network_ids": ["net.logic.envelope.0001", "net.logic.envelope.0002", "net.logic.envelope.0003", "net.logic.envelope.0004"],
        "low_priority_network_ids": ["net.logic.envelope.0003", "net.logic.envelope.0004"],
        "safety_critical_network_ids": ["net.logic.envelope.0001"],
        "skipped_network_ids": ["net.logic.envelope.0001", "net.logic.envelope.0004"],
        "per_tick_network_cap": 2,
        "tick_bucket_stride": 2,
        "active_debug_sessions": 6,
        "debug_session_capacity": 3,
    }
    first = plan_logic_degradation_actions(**kwargs)
    second = plan_logic_degradation_actions(**kwargs)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "logic degradation plan drifted across equivalent runs"}
    expected_order = [
        "prefer_compiled_execution",
        "reduce_low_priority_eval_frequency",
        "cap_networks_per_tick",
        "reduce_debug_sampling_rate",
        "refuse_new_debug_sessions",
        "apply_fail_safe_outputs",
    ]
    observed = [str(row.get("action_id", "")).strip() for row in list(first.get("plan_rows") or [])]
    if observed != expected_order:
        return {"status": "fail", "message": "logic degradation order drifted from canonical sequence"}
    return {"status": "pass", "message": "logic degradation order is deterministic and canonical"}
