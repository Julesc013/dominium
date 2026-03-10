"""FAST test: boot proof surfaces must include semantic contract hashes."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_proof_includes_contract_hashes"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "proof"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.testx.tests.compat_sem1_testlib import create_session, read_json

    fixture, created, spec_abs, _save_dir = create_session(repo_root, "proof")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session creation failed before proof test"}

    booted = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if str(booted.get("result", "")) != "complete":
        return {"status": "fail", "message": "boot failed before proof test"}
    if len(str(booted.get("contract_bundle_hash", "")).strip()) != 64:
        return {"status": "fail", "message": "boot result missing contract_bundle_hash"}
    if len(str(booted.get("semantic_contract_registry_hash", "")).strip()) != 64:
        return {"status": "fail", "message": "boot result missing semantic_contract_registry_hash"}
    proof_bundle = dict(booted.get("semantic_contract_proof_bundle") or {})
    if str(proof_bundle.get("universe_contract_bundle_hash", "")).strip() != str(booted.get("contract_bundle_hash", "")).strip():
        return {"status": "fail", "message": "boot proof bundle universe contract hash mismatch"}
    if str(proof_bundle.get("semantic_contract_registry_hash", "")).strip() != str(booted.get("semantic_contract_registry_hash", "")).strip():
        return {"status": "fail", "message": "boot proof bundle semantic contract registry hash mismatch"}

    run_meta_abs = os.path.join(repo_root, str(booted.get("run_meta_path", "")).replace("/", os.sep))
    run_meta = read_json(run_meta_abs)
    if str(run_meta.get("contract_bundle_hash", "")).strip() != str(booted.get("contract_bundle_hash", "")).strip():
        return {"status": "fail", "message": "run-meta missing contract_bundle_hash"}
    if str(run_meta.get("semantic_contract_registry_hash", "")).strip() != str(booted.get("semantic_contract_registry_hash", "")).strip():
        return {"status": "fail", "message": "run-meta missing semantic contract registry hash"}
    return {"status": "pass", "message": "proof surfaces include semantic contract hashes deterministically"}
