"""STRICT test: cli/tui/gui stage workspace parity for session status."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.stage_parity.status_surfaces"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.sessionx.stage_parity import surface_stage_status

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".parity.status"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        pipeline_id=str(fixture.get("pipeline_id", "pipeline.client.default")),
        scenario_id=str(fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(fixture.get("budget_policy_id", "policy.budget.default_lab")),
        fidelity_policy_id=str(fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(fixture.get("rng_seed_string", "seed.testx.session.fixture")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(fixture.get("universe_seed_string", "seed.testx.universe.fixture")),
        universe_id="",
        entitlements=list(fixture.get("entitlements") or []),
        epistemic_scope_id=str(fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(fixture.get("visibility_level", "placeholder")),
        privilege_level=str(fixture.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before parity status test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if boot.get("result") != "complete":
        return {"status": "fail", "message": "boot failed before parity status test"}

    rows = []
    for surface in ("cli", "tui", "gui"):
        payload = surface_stage_status(
            surface=surface,
            repo_root=repo_root,
            session_spec_path=spec_abs,
        )
        if payload.get("result") != "complete":
            return {"status": "fail", "message": "surface '{}' stage status failed".format(surface)}
        rows.append(payload)

    baseline = rows[0]
    for payload in rows[1:]:
        if str(payload.get("current_stage_id", "")) != str(baseline.get("current_stage_id", "")):
            return {"status": "fail", "message": "stage_id mismatch across surfaces"}
        if list(payload.get("stage_log") or []) != list(baseline.get("stage_log") or []):
            return {"status": "fail", "message": "stage_log mismatch across surfaces"}
        if list(payload.get("refusal_codes") or []) != list(baseline.get("refusal_codes") or []):
            return {"status": "fail", "message": "refusal_codes mismatch across surfaces"}
    return {"status": "pass", "message": "stage status parity checks passed across cli/tui/gui"}
