"""FAST test: XI-4b lock proposal captures the expected approval structure."""

from __future__ import annotations


TEST_ID = "test_xi4b_lock_proposal_schema_valid"
TEST_TAGS = ["fast", "xi", "restructure", "lock"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4b_src_domain_mapping_testlib import committed_lock_proposal

    payload = committed_lock_proposal(repo_root)
    if str(payload.get("report_id", "")).strip() != "xi.4b.src_domain_mapping_lock_proposal.v1":
        return {"status": "fail", "message": "XI-4b lock proposal report_id drifted"}
    if str(payload.get("stability_class", "")).strip() != "provisional":
        return {"status": "fail", "message": "XI-4b lock proposal must remain provisional"}
    if str(payload.get("replacement_target", "")).strip() != "approved mapping lock for Ξ-5":
        return {"status": "fail", "message": "XI-4b lock proposal replacement target drifted"}
    option = str(payload.get("preferred_layout_option", "")).strip()
    if option not in {"A", "B", "C"}:
        return {"status": "fail", "message": "XI-4b lock proposal must identify a preferred option"}
    if not list(payload.get("high_confidence_mappings") or []):
        return {"status": "fail", "message": "XI-4b lock proposal must retain high-confidence mappings"}
    if "conflicts" not in payload:
        return {"status": "fail", "message": "XI-4b lock proposal must carry the conflict set"}
    if "source_evidence_fingerprints" not in payload:
        return {"status": "fail", "message": "XI-4b lock proposal must carry evidence fingerprints"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4b lock proposal missing deterministic_fingerprint"}
    return {"status": "pass", "message": "XI-4b lock proposal captures the expected approval structure"}
