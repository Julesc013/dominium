"""FAST test: replay must refuse when semantic contract registry hash mismatches the pinned bundle/runtime registry."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_refuses_mismatch"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.script_runner import run_intent_script
    from tools.xstack.testx.tests.compat_sem1_testlib import (
        create_session,
        load_script_fixture_path,
        read_json,
        write_json,
    )

    fixture, created, spec_abs, _save_dir = create_session(repo_root, "replay_mismatch")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session creation failed before replay mismatch test"}

    spec_payload = read_json(spec_abs)
    spec_payload["semantic_contract_registry_hash"] = "0" * 64
    write_json(spec_abs, spec_payload)
    result = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=load_script_fixture_path(repo_root),
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "replay did not refuse semantic contract registry mismatch"}
    reason = str(dict(result.get("refusal") or {}).get("reason_code", ""))
    if reason != "refusal.contract.mismatch":
        return {"status": "fail", "message": "expected refusal.contract.mismatch, got {}".format(reason or "<empty>")}
    return {"status": "pass", "message": "replay refuses deterministically on semantic contract registry mismatch"}
