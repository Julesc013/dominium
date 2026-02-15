"""STRICT test: launcher create-session persists explicit pipeline_id in SessionSpec."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.launcher.create_session_pipeline"
TEST_TAGS = ["strict", "session", "bundle"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.launcher.launch import cmd_create_session

    save_id = "save.testx.launcher.create_session_pipeline"
    created = cmd_create_session(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id="bundle.base.lab",
        pipeline_id="pipeline.client.default",
        scenario_id="scenario.lab.galaxy_nav",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        privilege_level="operator",
        compile_outputs=True,
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "launcher create-session refused valid request"}

    spec_rel = str(created.get("session_spec_path", ""))
    spec_abs = os.path.join(repo_root, spec_rel.replace("/", os.sep))
    if not os.path.isfile(spec_abs):
        return {"status": "fail", "message": "launcher create-session did not write session_spec.json"}
    payload = json.load(open(spec_abs, "r", encoding="utf-8"))
    if str(payload.get("pipeline_id", "")) != "pipeline.client.default":
        return {"status": "fail", "message": "launcher create-session must persist explicit pipeline_id"}
    return {"status": "pass", "message": "launcher create-session pipeline_id check passed"}
