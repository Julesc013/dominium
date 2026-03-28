from __future__ import annotations

from tools.xstack.testx.tests.xi5a_v4_testlib import committed_execution_log


def test_xi5a_v4_lock_consumed(repo_root: str) -> None:
    execution_log = committed_execution_log(repo_root)
    assert execution_log.get("approved_lock_path") == "data/restructure/src_domain_mapping_lock_approved_v4.json"
    assert execution_log.get("readiness_contract_path") == "data/restructure/xi5_readiness_contract_v4.json"
    assert execution_log.get("consumed_lock_report_id") == "xi.4z.src_domain_mapping_lock_approved.v4"
