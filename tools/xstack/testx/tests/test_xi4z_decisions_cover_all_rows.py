"""FAST test: XI-4z decisions classify every XI-4b mapping row exactly once."""

from __future__ import annotations


TEST_ID = "test_xi4z_decisions_cover_all_rows"
TEST_TAGS = ["fast", "xi", "restructure", "coverage"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4b_src_domain_mapping_testlib import committed_src_domain_mapping
    from tools.xstack.testx.tests.xi4z_structure_approval_testlib import committed_decisions

    mapping = committed_src_domain_mapping(repo_root)
    decisions = committed_decisions(repo_root)
    mapping_paths = [str(row.get("file_path", "")).strip() for row in list(mapping.get("mappings") or [])]
    decision_paths = [str(row.get("file_path", "")).strip() for row in list(decisions.get("decisions") or [])]
    if sorted(mapping_paths) != mapping_paths:
        return {"status": "fail", "message": "XI-4b mapping paths must stay sorted"}
    if sorted(decision_paths) != decision_paths:
        return {"status": "fail", "message": "XI-4z decision paths must stay sorted"}
    if mapping_paths != decision_paths:
        return {"status": "fail", "message": "XI-4z decisions must cover every XI-4b mapping row exactly once"}
    summary = dict(decisions.get("summary") or {})
    total = (
        int(summary.get("approved_for_xi5", 0) or 0)
        + int(summary.get("approved_to_attic", 0) or 0)
        + int(summary.get("deferred_to_xi5b", 0) or 0)
    )
    if total != len(mapping_paths):
        return {"status": "fail", "message": "XI-4z decision summary does not add up to the mapping count"}
    return {"status": "pass", "message": "XI-4z decisions classify every XI-4b mapping row exactly once"}
