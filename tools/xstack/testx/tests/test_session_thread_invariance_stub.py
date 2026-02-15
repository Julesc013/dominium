"""STRICT test: worker-count stub must preserve deterministic script outcomes."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.thread_invariance_stub"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    script_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.camera_nav.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".script.thread_stub"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        scenario_id=str(session_fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(session_fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(session_fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(session_fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(session_fixture.get("budget_policy_id", "policy.budget.default_lab")),
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
        return {"status": "fail", "message": "session create failed before thread invariance stub test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    single_worker = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    dual_worker = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=2,
        write_state=False,
    )
    if single_worker.get("result") != "complete" or dual_worker.get("result") != "complete":
        return {"status": "fail", "message": "script runner failed for worker-count invariance stub"}
    if str(single_worker.get("final_state_hash", "")) != str(dual_worker.get("final_state_hash", "")):
        return {"status": "fail", "message": "final_state_hash must remain invariant across worker counts"}
    if list(single_worker.get("state_hash_anchors") or []) != list(dual_worker.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "state hash anchors must remain invariant across worker counts"}
    if str(single_worker.get("deterministic_fields_hash", "")) != str(dual_worker.get("deterministic_fields_hash", "")):
        return {"status": "fail", "message": "deterministic fields hash must remain invariant across worker counts"}
    if int(dual_worker.get("workers_effective", 0)) != 1:
        return {"status": "fail", "message": "thread-count stub must report deterministic single-worker scheduler for now"}
    return {"status": "pass", "message": "thread-count invariance stub check passed"}
