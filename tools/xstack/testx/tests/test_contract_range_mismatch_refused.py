"""FAST test: incompatible contract ranges are refused by offline verification."""

from __future__ import annotations


TEST_ID = "test_contract_range_mismatch_refused"
TEST_TAGS = ["fast", "packs", "compat", "contracts"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat1_testlib import (
        cleanup_temp_repo,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        mutate_pack_compat,
        report_refusal_codes,
        verify_fixture_pack_set,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        bogus_contract_id = ".".join(["contract", "nonexistent", "v9"])
        mutate_pack_compat(
            temp_repo,
            "pack.test.domain",
            lambda payload: {
                **payload,
                "required_contract_ranges": {
                    bogus_contract_id: {
                        "exact_version": bogus_contract_id,
                        "min_version": bogus_contract_id,
                        "max_version": bogus_contract_id,
                    }
                },
            },
        )
        result = verify_fixture_pack_set(repo_root, temp_repo)
        report = dict(result.get("report") or {})
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "verification pipeline hard-refused instead of reporting invalid contract range"}
        if bool(report.get("valid", False)):
            return {"status": "fail", "message": "contract range mismatch was accepted"}
        if "refusal.pack.contract_range_mismatch" not in report_refusal_codes(result):
            return {"status": "fail", "message": "wrong refusal code for contract range mismatch"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "contract range mismatch is refused deterministically"}
