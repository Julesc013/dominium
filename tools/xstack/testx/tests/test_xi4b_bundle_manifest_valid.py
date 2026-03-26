"""FAST test: XI-4b bundle manifest includes the required review entries."""

from __future__ import annotations


TEST_ID = "test_xi4b_bundle_manifest_valid"
TEST_TAGS = ["fast", "xi", "restructure", "bundle"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4b_src_domain_mapping_testlib import fresh_snapshot

    rendered = dict(dict(fresh_snapshot(repo_root).get("rendered") or {}))
    manifest_text = str(rendered.get("bundle_manifest_text", "")).strip()
    if not manifest_text:
        return {"status": "fail", "message": "XI-4b bundle manifest text must be rendered"}
    required_entries = (
        "REVIEW_FIRST.md",
        "docs/restructure/XI_4B_REVIEW_GUIDE.md",
        "docs/restructure/STRUCTURE_OPTIONS_REPORT.md",
        "data/restructure/src_domain_mapping_lock_proposal.json",
        "data/architecture/architecture_graph.json",
        "data/refactor/convergence_execution_log.json",
    )
    for marker in required_entries:
        if marker not in manifest_text:
            return {"status": "fail", "message": f"XI-4b bundle manifest missing '{marker}'"}
    bundle_entries = dict(rendered.get("bundle_entries") or {})
    if "REVIEW_FIRST.md" not in bundle_entries:
        return {"status": "fail", "message": "XI-4b bundle must contain REVIEW_FIRST.md"}
    if not rendered.get("bundle_bytes"):
        return {"status": "fail", "message": "XI-4b bundle bytes are empty"}
    return {"status": "pass", "message": "XI-4b bundle manifest includes the required review entries"}
