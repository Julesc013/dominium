"""FAST test: update resolution refuses deterministic contract mismatches."""

from __future__ import annotations


TEST_ID = "test_update_refuses_on_contract_mismatch"
TEST_TAGS = ["fast", "release", "update-model", "compat"]


def run(repo_root: str):
    from src.release import resolve_update_plan
    from tools.xstack.testx.tests.update_model_testlib import load_install_manifest, load_release_index_payload

    install_manifest = load_install_manifest(repo_root)
    release_index = load_release_index_payload(repo_root)
    release_index["semantic_contract_registry_hash"] = "0" * 64
    result = resolve_update_plan(
        install_manifest,
        release_index,
        install_profile_id=str(dict(install_manifest.get("extensions") or {}).get("official.install_profile_id", "")).strip(),
        release_index_path="manifests/release_index.json",
        component_graph=dict(dict(release_index.get("extensions") or {}).get("component_graph") or {}),
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "update resolution must refuse a semantic contract mismatch"}
    if str(result.get("refusal_code", "")).strip() != "refusal.update.contract_incompatible":
        return {"status": "fail", "message": "update resolution used the wrong refusal code for semantic contract mismatch"}
    return {"status": "pass", "message": "update resolution refuses contract mismatches deterministically"}
