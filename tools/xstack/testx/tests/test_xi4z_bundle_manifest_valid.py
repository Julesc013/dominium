"""FAST test: XI-4z bundle manifest includes the required readiness entries."""

from __future__ import annotations


TEST_ID = "test_xi4z_bundle_manifest_valid"
TEST_TAGS = ["fast", "xi", "restructure", "bundle"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4z_structure_approval_testlib import fresh_snapshot

    rendered = dict(dict(fresh_snapshot(repo_root).get("rendered") or {}))
    manifest_text = str(rendered.get("bundle_manifest_text", "")).strip()
    if not manifest_text:
        return {"status": "fail", "message": "XI-4z bundle manifest text must be rendered"}
    required_entries = (
        "REVIEW_FIRST.md",
        "docs/restructure/XI_4Z_DECISION_REPORT.md",
        "docs/restructure/XI_4Z_XI5_READINESS.md",
        "data/restructure/src_domain_mapping_lock_approved.json",
        "data/restructure/xi5_readiness_contract.json",
        "data/architecture/architecture_graph.json",
        "data/refactor/convergence_execution_log.json",
    )
    for marker in required_entries:
        if marker not in manifest_text:
            return {"status": "fail", "message": f"XI-4z bundle manifest missing '{marker}'"}
    if not rendered.get("bundle_bytes"):
        return {"status": "fail", "message": "XI-4z bundle bytes are empty"}
    return {"status": "pass", "message": "XI-4z bundle manifest includes the required readiness entries"}
