"""FAST test: universe creation must pin semantic contract bundle metadata into identity and session artifacts."""

from __future__ import annotations

import os
import sys


TEST_ID = "test_universe_creation_pins_contracts"
TEST_TAGS = ["fast", "compat", "semantic_contracts", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.compat_sem1_testlib import create_session, read_json

    _fixture, created, spec_abs, save_dir = create_session(repo_root, "pin")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session creation failed before contract pin test"}

    identity_abs = os.path.join(save_dir, "universe_identity.json")
    bundle_abs = os.path.join(save_dir, "universe_contract_bundle.json")
    if not os.path.isfile(identity_abs) or not os.path.isfile(bundle_abs):
        return {"status": "fail", "message": "expected universe identity/bundle artifacts were not written"}

    spec_payload = read_json(spec_abs)
    identity_payload = read_json(identity_abs)
    bundle_payload = read_json(bundle_abs)
    if str(identity_payload.get("universe_contract_bundle_ref", "")) != "universe_contract_bundle.json":
        return {"status": "fail", "message": "UniverseIdentity did not pin the canonical bundle sidecar ref"}
    identity_hash = str(identity_payload.get("universe_contract_bundle_hash", "")).strip()
    if len(identity_hash) != 64:
        return {"status": "fail", "message": "UniverseIdentity missing contract bundle hash"}
    if str(bundle_payload.get("deterministic_fingerprint", "")).strip() != identity_hash:
        return {"status": "fail", "message": "UniverseIdentity contract bundle hash does not match bundle payload"}
    if str(spec_payload.get("contract_bundle_hash", "")).strip() != identity_hash:
        return {"status": "fail", "message": "SessionSpec contract_bundle_hash does not match universe contract bundle hash"}
    if len(str(spec_payload.get("semantic_contract_registry_hash", "")).strip()) != 64:
        return {"status": "fail", "message": "SessionSpec missing semantic contract registry hash"}
    return {"status": "pass", "message": "universe creation pins contract bundle metadata deterministically"}
