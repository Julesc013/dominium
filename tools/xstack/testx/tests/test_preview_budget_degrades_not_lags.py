"""STRICT test: preview path degrades deterministically under budget pressure instead of stalling execution."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.interaction.preview_budget_degrades_not_lags"
TEST_TAGS = ["strict", "interaction", "preview", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.interaction.preview_generator import generate_interaction_preview
    from tools.xstack.testx.tests.interaction_testlib import perceived_model, policy_context

    perceived = perceived_model(include_truth_overlay=True)
    expensive_affordance = {
        "affordance_id": "affordance.test.inspect",
        "target_semantic_id": "agent.alpha",
        "process_id": "process.inspect_generate_snapshot",
        "preview_capability": "expensive",
        "cost_units_estimate": 3,
        "extensions": {"enabled": True},
    }
    tight_runtime = copy.deepcopy(policy_context(max_inspection_budget_per_tick=0))
    first = generate_interaction_preview(
        perceived_model=perceived,
        affordance_row=expensive_affordance,
        parameters={"target_id": "agent.alpha"},
        preview_runtime=tight_runtime,
        repo_root=repo_root,
    )
    second = generate_interaction_preview(
        perceived_model=perceived,
        affordance_row=expensive_affordance,
        parameters={"target_id": "agent.alpha"},
        preview_runtime=copy.deepcopy(policy_context(max_inspection_budget_per_tick=0)),
        repo_root=repo_root,
    )
    if str(first.get("result", "")) != "refused" or str(second.get("result", "")) != "refused":
        return {"status": "fail", "message": "expensive preview should refuse under zero inspection budget"}
    reason_a = str((dict(first.get("refusal") or {})).get("reason_code", ""))
    reason_b = str((dict(second.get("refusal") or {})).get("reason_code", ""))
    if reason_a != "refusal.preview.budget_exceeded" or reason_b != "refusal.preview.budget_exceeded":
        return {"status": "fail", "message": "budget refusal reason code drifted for expensive preview"}

    cheap_affordance = dict(expensive_affordance)
    cheap_affordance["preview_capability"] = "cheap"
    cheap = generate_interaction_preview(
        perceived_model=perceived,
        affordance_row=cheap_affordance,
        parameters={"target_id": "agent.alpha"},
        preview_runtime=copy.deepcopy(policy_context(max_inspection_budget_per_tick=0)),
        repo_root=repo_root,
    )
    if str(cheap.get("result", "")) != "complete":
        return {"status": "fail", "message": "cheap preview fallback should complete even when expensive budget is unavailable"}
    summary = str((dict(cheap.get("preview") or {}).get("predicted_effects") or {}).get("summary", ""))
    if "will attempt process.inspect_generate_snapshot" not in summary:
        return {"status": "fail", "message": "cheap preview summary missing deterministic fallback output"}
    return {"status": "pass", "message": "preview budget degradation behavior passed"}
