"""STRICT test: deterministic ROI traversal hash lock remains stable."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.regression.roi_switch"
TEST_TAGS = ["strict", "regression", "session"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    baseline = _load_json(os.path.join(repo_root, "data", "regression", "observer_baseline.json"))
    fixture = _load_json(
        os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    )
    created = create_session_spec(
        repo_root=repo_root,
        save_id="save.testx.regression.roi_switch",
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
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
        return {"status": "fail", "message": "failed to create session for ROI regression check"}

    session_spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_abs = os.path.join(repo_root, str(baseline.get("script_path", "")).replace("/", os.sep))
    replay = run_intent_script(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        script_path=script_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        logical_shards=1,
        write_state=False,
    )
    if replay.get("result") != "complete":
        return {"status": "fail", "message": "script replay failed for ROI regression check"}

    roi_lock = dict(baseline.get("roi_switch_lock") or {})
    if str(replay.get("final_state_hash", "")) != str(roi_lock.get("final_state_hash", "")):
        return {"status": "fail", "message": "ROI final_state_hash changed relative to baseline"}
    tick_rows = list(replay.get("tick_hash_anchors") or [])
    final_tick_hash = str((tick_rows[-1] or {}).get("tick_hash", "")) if tick_rows else ""
    if final_tick_hash != str(roi_lock.get("final_tick_hash", "")):
        return {"status": "fail", "message": "ROI final tick hash changed relative to baseline"}
    return {"status": "pass", "message": "ROI switch regression lock passed"}
