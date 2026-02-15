"""STRICT test: tiny budget policy enforces deterministic degrade/cap behavior."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.region_budget_exceed"
TEST_TAGS = ["strict", "session", "performx"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    script_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.region_budget_tiny.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".region.budget"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        scenario_id=str(session_fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(session_fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(session_fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(session_fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id="policy.budget.tiny_lab",
        fidelity_policy_id=str(session_fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(session_fixture.get("rng_seed_string", "seed.testx.session.fixture")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(session_fixture.get("universe_seed_string", "seed.testx.universe.fixture")),
        universe_id="",
        entitlements=list(session_fixture.get("entitlements") or []),
        epistemic_scope_id=str(session_fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(session_fixture.get("visibility_level", "placeholder")),
        privilege_level=str(session_fixture.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before budget exceed test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    result = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    if result.get("result") != "complete":
        return {"status": "fail", "message": "region budget script execution failed"}
    perf = result.get("performance_state")
    if not isinstance(perf, dict):
        return {"status": "fail", "message": "missing performance_state in region budget result"}
    outcome = str(perf.get("budget_outcome", "")).strip()
    if outcome not in ("degraded", "capped"):
        return {"status": "fail", "message": "tiny budget policy did not trigger deterministic degrade/cap outcome"}
    compute_units = int(perf.get("compute_units_used", 0) or 0)
    max_compute = int(perf.get("max_compute_units_per_tick", 0) or 0)
    if compute_units > max_compute:
        return {"status": "fail", "message": "budget enforcement exceeded max_compute_units_per_tick after processing"}
    if str(perf.get("budget_policy_id", "")) != "policy.budget.tiny_lab":
        return {"status": "fail", "message": "unexpected budget policy id in performance_state"}
    return {"status": "pass", "message": "region budget exceed deterministic check passed"}
