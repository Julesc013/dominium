from __future__ import annotations

from tools.xstack.testx.tests.xi4z_fix2_testlib import committed_lock_v3, committed_readiness_contract_v3


def test_xi4z_v3_lock_schema_valid(repo_root: str) -> None:
    lock_payload = committed_lock_v3(repo_root)
    readiness_payload = committed_readiness_contract_v3(repo_root)

    assert lock_payload.get("report_id") == "xi.4z.src_domain_mapping_lock_approved.v3"
    assert lock_payload.get("selected_layout_option") == "C"
    assert isinstance(lock_payload.get("approved_for_xi5"), list)
    assert isinstance(lock_payload.get("approved_to_attic"), list)
    assert isinstance(lock_payload.get("deferred_to_xi5b"), list)
    assert lock_payload.get("deterministic_fingerprint")

    assert readiness_payload.get("approved_lock_path") == "data/restructure/src_domain_mapping_lock_approved_v3.json"
    assert readiness_payload.get("readiness_contract_path") == "data/restructure/xi5_readiness_contract_v3.json"
    assert readiness_payload.get("path_derivation_policy") == "forbidden"
