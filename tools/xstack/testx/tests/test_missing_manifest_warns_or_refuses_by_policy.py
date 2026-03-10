"""FAST test: missing pack.compat.json warns in lab mode and refuses in strict mode."""

from __future__ import annotations


TEST_ID = "test_missing_manifest_warns_or_refuses_by_policy"
TEST_TAGS = ["fast", "packs", "compat", "policy"]


def run(repo_root: str):
    from tools.xstack.pack_loader.loader import load_pack_set
    from tools.xstack.testx.tests.pack_compat0_testlib import (
        cleanup_temp_repo,
        ensure_repo_on_path,
        make_temp_pack_compat_repo,
        remove_pack_compat,
    )

    ensure_repo_on_path(repo_root)
    temp_repo = make_temp_pack_compat_repo(repo_root)
    try:
        remove_pack_compat(temp_repo, "pack.test.base")
        lab = load_pack_set(
            repo_root=temp_repo,
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            mod_policy_id="mod_policy.lab",
        )
        if str(lab.get("result", "")) != "complete":
            return {"status": "fail", "message": "lab mode refused missing compat manifest"}
        warning_codes = sorted(str(row.get("code", "")) for row in list(lab.get("warnings") or []) if isinstance(row, dict))
        if "warn.pack.compat_manifest_missing" not in warning_codes:
            return {"status": "fail", "message": "lab mode did not warn on missing compat manifest"}

        strict = load_pack_set(
            repo_root=temp_repo,
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            mod_policy_id="mod_policy.strict",
        )
        if str(strict.get("result", "")) != "refused":
            return {"status": "fail", "message": "strict mode accepted missing compat manifest"}
        error_codes = sorted(str(row.get("code", "")) for row in list(strict.get("errors") or []) if isinstance(row, dict))
        if "refusal.pack.compat_manifest_missing" not in error_codes:
            return {"status": "fail", "message": "strict mode returned wrong refusal for missing compat manifest"}
    finally:
        cleanup_temp_repo(temp_repo)
    return {"status": "pass", "message": "missing pack.compat.json warns or refuses by policy"}
