"""FAST test: invalid contract ranges in pack.compat.json refuse deterministically."""

from __future__ import annotations


TEST_ID = "test_contract_range_check"
TEST_TAGS = ["fast", "packs", "compat", "contracts"]


def run(repo_root: str):
    from tools.xstack.testx.tests.pack_compat0_testlib import (
        cleanup_temp_repo,
        compile_fixture_bundle,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        mutate_pack_compat,
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
                        "max_version": bogus_contract_id,
                        "min_version": bogus_contract_id,
                    }
                },
            },
        )
        result = compile_fixture_bundle(repo_root, temp_repo, "mod_policy.lab")
        if str(result.get("result", "")) != "refused":
            return {"status": "fail", "message": "invalid contract range was accepted"}
        codes = sorted(str(row.get("code", "")) for row in list(result.get("errors") or []) if isinstance(row, dict))
        if "refusal.pack.contract_mismatch" not in codes:
            return {"status": "fail", "message": "wrong refusal code for invalid contract range"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "invalid contract ranges refuse deterministically"}
