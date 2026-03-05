"""FAST test: SYS-4 template instantiation creates plan + MAT commitment artifacts."""

from __future__ import annotations

import sys


TEST_ID = "test_template_instantiate_creates_plan_and_commitments"
TEST_TAGS = ["fast", "system", "sys4", "template"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys4_testlib import cloned_state, execute_template_instantiate

    state = cloned_state()
    result = execute_template_instantiate(
        repo_root=repo_root,
        state=state,
        template_id="template.engine.ice_stub",
        instantiation_mode="micro",
        target_spatial_id="cell.sys4.test.micro",
        allow_macro=False,
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "template instantiate process did not complete for micro mode"}

    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    if not plan_rows:
        return {"status": "fail", "message": "template instantiate did not create plan artifact"}

    commitment_rows = [dict(row) for row in list(state.get("material_commitments") or []) if isinstance(row, dict)]
    if not any(str(row.get("commitment_type_id", "")).strip() == "commit.system.template_instantiate" for row in commitment_rows):
        return {"status": "fail", "message": "template instantiate did not emit expected MAT commitment row"}

    instance_rows = [
        dict(row)
        for row in list(state.get("system_template_instance_record_rows") or [])
        if isinstance(row, dict)
    ]
    if not instance_rows:
        return {"status": "fail", "message": "template instantiate did not persist template_instance_record rows"}
    return {"status": "pass", "message": "template instantiation emits plan, commitments, and instance records"}

