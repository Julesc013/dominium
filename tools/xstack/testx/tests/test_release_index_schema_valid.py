"""FAST test: release index report is structurally valid and complete."""

from __future__ import annotations


TEST_ID = "test_release_index_schema_valid"
TEST_TAGS = ["fast", "release", "update-model", "schema"]


def run(repo_root: str):
    from tools.xstack.testx.tests.update_model_testlib import build_report, load_release_index_payload

    payload = load_release_index_payload(repo_root)
    report = build_report(repo_root)
    if str(payload.get("channel", "")).strip() != "mock":
        return {"status": "fail", "message": "release index channel must be mock for UPDATE-MODEL-0 baseline"}
    if not str(payload.get("release_series", "")).strip():
        return {"status": "fail", "message": "release index must declare release_series"}
    if not str(payload.get("semantic_contract_registry_hash", "")).strip():
        return {"status": "fail", "message": "release index must declare semantic_contract_registry_hash"}
    if not str(payload.get("component_graph_hash", "")).strip():
        return {"status": "fail", "message": "release index must declare component_graph_hash"}
    if not list(payload.get("platform_matrix") or []):
        return {"status": "fail", "message": "release index must declare platform_matrix entries"}
    if not list(payload.get("components") or []):
        return {"status": "fail", "message": "release index must declare component descriptors"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "update-model report did not complete successfully"}
    return {"status": "pass", "message": "release index report is structurally valid"}
