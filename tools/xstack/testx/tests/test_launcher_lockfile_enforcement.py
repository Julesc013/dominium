"""STRICT test: launcher refuses session specs with mismatched pack_lock_hash."""

from __future__ import annotations

import json
import os
import sys
import tempfile


TEST_ID = "testx.launcher.lockfile_enforcement"
TEST_TAGS = ["strict", "session", "bundle"]


def _load_fixture(repo_root: str):
    path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.launcher.launch import cmd_run
    from tools.xstack.packagingx import build_dist_layout
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.launcher")) + ".launcher.lockfile"
    created = create_session_spec(
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
        rng_seed_string=str(fixture.get("rng_seed_string", "seed.testx.launcher")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(fixture.get("universe_seed_string", "seed.testx.launcher.universe")),
        universe_id="",
        entitlements=list(fixture.get("entitlements") or []),
        epistemic_scope_id=str(fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(fixture.get("visibility_level", "placeholder")),
        privilege_level=str(fixture.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before launcher enforcement test"}

    dist_out = "build/dist.testx.launcher"
    built = build_dist_layout(repo_root=repo_root, bundle_id="bundle.base.lab", out_dir=dist_out, use_cache=True)
    if built.get("result") != "complete":
        return {"status": "fail", "message": "dist build failed before launcher enforcement test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    payload = json.load(open(spec_abs, "r", encoding="utf-8"))
    payload["pack_lock_hash"] = "0" * 64
    tampered = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", suffix=".json", delete=False)
    try:
        with tampered as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        launched = cmd_run(
            repo_root=repo_root,
            dist_root=dist_out,
            session_spec_path=tampered.name,
            script_path="",
            workers=1,
            logical_shards=1,
            write_state=False,
            bundle_id="bundle.base.lab",
        )
    finally:
        try:
            os.remove(tampered.name)
        except OSError:
            pass

    if launched.get("result") != "refused":
        return {"status": "fail", "message": "launcher run should refuse tampered pack_lock_hash"}
    refusal = dict(launched.get("refusal") or {})
    if str(refusal.get("reason_code", "")) != "LOCKFILE_MISMATCH":
        return {
            "status": "fail",
            "message": "expected LOCKFILE_MISMATCH refusal, got '{}'".format(str(refusal.get("reason_code", ""))),
        }
    return {"status": "pass", "message": "launcher lockfile enforcement refusal passed"}

