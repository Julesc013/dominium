"""STRICT test: cli/tui/gui parity for abort/resume stage transitions."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.stage_parity.transitions_surfaces"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def _run_surface_flow(repo_root: str, fixture: dict, surface: str) -> dict:
    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.sessionx.stage_parity import surface_abort_session, surface_resume_session

    save_id = "{}.parity.transition.{}".format(
        str(fixture.get("save_id", "save.testx.session.fixture")),
        str(surface),
    )
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
        return {"status": "fail", "message": "session create failed for surface '{}'".format(surface)}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if boot.get("result") != "complete":
        return {"status": "fail", "message": "boot failed for surface '{}'".format(surface)}

    aborted = surface_abort_session(
        surface=surface,
        repo_root=repo_root,
        session_spec_path=spec_abs,
        stage_id="stage.session_ready",
        reason="test_stage_parity_transitions",
    )
    if aborted.get("result") != "complete":
        return {"status": "fail", "message": "abort failed for surface '{}'".format(surface)}

    resumed = surface_resume_session(
        surface=surface,
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
    )
    if resumed.get("result") != "complete":
        return {"status": "fail", "message": "resume failed for surface '{}'".format(surface)}

    return {
        "status": "pass",
        "surface": surface,
        "last_stage_id": str(resumed.get("last_stage_id", "")),
        "pack_lock_hash": str(resumed.get("pack_lock_hash", "")),
        "registry_hashes": dict(resumed.get("registry_hashes") or {}),
        "stage_log": list(resumed.get("stage_log") or []),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    fixture = _load_fixture(repo_root)
    rows = []
    for surface in ("cli", "tui", "gui"):
        row = _run_surface_flow(repo_root=repo_root, fixture=fixture, surface=surface)
        if row.get("status") != "pass":
            return row
        rows.append(row)

    baseline = rows[0]
    for row in rows[1:]:
        if str(row.get("last_stage_id", "")) != str(baseline.get("last_stage_id", "")):
            return {"status": "fail", "message": "resume last_stage mismatch across surfaces"}
        if str(row.get("pack_lock_hash", "")) != str(baseline.get("pack_lock_hash", "")):
            return {"status": "fail", "message": "resume pack_lock_hash mismatch across surfaces"}
        if dict(row.get("registry_hashes") or {}) != dict(baseline.get("registry_hashes") or {}):
            return {"status": "fail", "message": "resume registry hash mismatch across surfaces"}
        if list(row.get("stage_log") or []) != list(baseline.get("stage_log") or []):
            return {"status": "fail", "message": "resume stage_log mismatch across surfaces"}
    return {"status": "pass", "message": "abort/resume parity checks passed across cli/tui/gui"}
