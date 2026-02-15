"""STRICT test: SRZ scheduling is worker-count invariant."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.srz.worker_invariance"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def _create_session(repo_root: str, suffix: str) -> dict:
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + suffix
    return create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.script_runner import run_intent_script

    created = _create_session(repo_root, ".srz.worker")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before SRZ worker invariance test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.region_traversal.fixture.json")
    bundle_id = str(created.get("bundle_id", "bundle.base.lab"))

    workers_1 = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=1,
    )
    workers_2 = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=2,
        write_state=False,
        logical_shards=1,
    )
    if workers_1.get("result") != "complete" or workers_2.get("result") != "complete":
        return {"status": "fail", "message": "script replay failed for worker-count invariance test"}
    if str(workers_1.get("composite_hash", "")) != str(workers_2.get("composite_hash", "")):
        return {"status": "fail", "message": "SRZ composite hash changed across worker-count variation"}
    if list(workers_1.get("tick_hash_anchors") or []) != list(workers_2.get("tick_hash_anchors") or []):
        return {"status": "fail", "message": "per-tick SRZ hashes changed across worker-count variation"}
    if str(workers_1.get("deterministic_fields_hash", "")) != str(workers_2.get("deterministic_fields_hash", "")):
        return {"status": "fail", "message": "deterministic_fields_hash changed across worker-count variation"}
    return {"status": "pass", "message": "SRZ worker-count invariance check passed"}
