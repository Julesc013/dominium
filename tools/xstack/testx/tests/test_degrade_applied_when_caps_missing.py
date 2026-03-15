"""FAST test: CAP-NEG-4 degrade ladders apply when optional capabilities are missing."""

from __future__ import annotations


TEST_ID = "test_degrade_applied_when_caps_missing"
TEST_TAGS = ["fast", "compat", "cap_neg", "degrade", "interop"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg4_testlib import interop_stress_report, scenario_row

    rendered_row = scenario_row(interop_stress_report(repo_root), "interop.client_server.rendered_to_tui")
    rendered_substitutions = set(str(item).strip() for item in list(rendered_row.get("substituted_capability_ids") or []))
    if "cap.ui.rendered->cap.ui.tui" not in rendered_substitutions:
        return {"status": "fail", "message": "missing rendered->tui fallback substitution"}

    compiled_row = scenario_row(interop_stress_report(repo_root), "interop.engine_server.compiled_to_l1")
    compiled_substitutions = set(str(item).strip() for item in list(compiled_row.get("substituted_capability_ids") or []))
    if "cap.logic.compiled_automaton->cap.logic.l1_eval" not in compiled_substitutions:
        return {"status": "fail", "message": "missing compiled-automaton->l1_eval substitution"}

    return {"status": "pass", "message": "degrade ladders apply for missing capabilities"}
