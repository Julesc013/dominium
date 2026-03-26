"""FAST test: XI-4b src-domain mapping exposes the expected schema."""

from __future__ import annotations


TEST_ID = "test_src_domain_mapping_schema_valid"
TEST_TAGS = ["fast", "xi", "restructure", "schema"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4b_src_domain_mapping_testlib import committed_src_domain_mapping

    payload = committed_src_domain_mapping(repo_root)
    if str(payload.get("report_id", "")).strip() != "xi.4b.src_domain_mapping.v1":
        return {"status": "fail", "message": "XI-4b src-domain mapping report_id drifted"}
    mappings = list(payload.get("mappings") or [])
    if not mappings:
        return {"status": "fail", "message": "XI-4b src-domain mapping must contain mapping rows"}
    first = dict(mappings[0] or {})
    for key in ("file_path", "current_root", "proposed_domain", "proposed_module_id", "confidence", "category", "evidence"):
        if key not in first:
            return {"status": "fail", "message": f"XI-4b mapping row missing '{key}'"}
    if first.get("proposed_domain") not in {"engine", "game", "apps", "tools", "lib", "compat", "ui", "platform", "tests", "attic"}:
        return {"status": "fail", "message": "XI-4b mapping proposed_domain is outside the allowed domain set"}
    evidence = dict(first.get("evidence") or {})
    for key in ("build_targets", "dependencies", "duplicate_cluster", "canonical_candidate", "docs_refs"):
        if key not in evidence:
            return {"status": "fail", "message": f"XI-4b mapping evidence missing '{key}'"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4b src-domain mapping missing deterministic_fingerprint"}
    return {"status": "pass", "message": "XI-4b src-domain mapping exposes the expected schema"}
