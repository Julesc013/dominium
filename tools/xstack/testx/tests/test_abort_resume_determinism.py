"""STRICT test: abort/resume flow remains deterministic and pipeline-safe."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.abort_resume_determinism"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str) -> dict:
    path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(path, "r", encoding="utf-8"))


def _create_session(repo_root: str, save_suffix: str) -> dict:
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = _load_fixture(repo_root)
    save_id = "{}{}".format(str(fixture.get("save_id", "save.testx.session.fixture")), save_suffix)
    return create_session_spec(
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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.sessionx.session_control import abort_session_spec, resume_session_spec, session_stage_status

    created = _create_session(repo_root, ".abort_resume")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before abort/resume test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if boot.get("result") != "complete":
        return {"status": "fail", "message": "boot failed before abort/resume test"}

    stage = session_stage_status(repo_root=repo_root, session_spec_path=spec_abs)
    if stage.get("result") != "complete":
        return {"status": "fail", "message": "session stage command failed before abort"}
    if str(stage.get("current_stage_id", "")) != "stage.session_ready":
        return {
            "status": "fail",
            "message": "expected stage.session_ready before abort, got '{}'".format(str(stage.get("current_stage_id", ""))),
        }

    first_abort = abort_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        stage_id="stage.session_ready",
        reason="test_abort_resume_determinism",
    )
    if first_abort.get("result") != "complete":
        return {"status": "fail", "message": "abort failed"}

    first_resume = resume_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
    )
    if first_resume.get("result") != "complete":
        return {"status": "fail", "message": "resume failed after first abort"}

    second_abort = abort_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        stage_id="stage.session_ready",
        reason="test_abort_resume_determinism",
    )
    if second_abort.get("result") != "complete":
        return {"status": "fail", "message": "second abort failed"}

    second_resume = resume_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
    )
    if second_resume.get("result") != "complete":
        return {"status": "fail", "message": "second resume failed"}

    for key in ("pack_lock_hash", "last_stage_id"):
        if str(first_resume.get(key, "")) != str(second_resume.get(key, "")):
            return {"status": "fail", "message": "resume mismatch for '{}'".format(key)}
    if dict(first_resume.get("registry_hashes") or {}) != dict(second_resume.get("registry_hashes") or {}):
        return {"status": "fail", "message": "resume registry hashes changed across repeated flow"}
    if list(first_resume.get("stage_log") or []) != list(second_resume.get("stage_log") or []):
        return {"status": "fail", "message": "resume stage log changed across repeated flow"}
    return {"status": "pass", "message": "abort/resume deterministic checks passed"}
