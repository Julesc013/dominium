"""FAST test: governed packs ship valid compatibility sidecars."""

from __future__ import annotations


TEST_ID = "test_pack_compat_manifest_schema_valid"
TEST_TAGS = ["fast", "packs", "compat", "schema"]


def run(repo_root: str):
    from tools.xstack.pack_loader.loader import load_pack_set

    loaded = load_pack_set(
        repo_root=repo_root,
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        mod_policy_id="mod_policy.lab",
    )
    if str(loaded.get("result", "")) != "complete":
        return {"status": "fail", "message": "pack load failed while validating compatibility sidecars"}
    warnings = list(loaded.get("warnings") or [])
    if warnings:
        return {"status": "fail", "message": "unexpected pack compat warnings remain in governed pack set"}
    for row in list(loaded.get("packs") or []):
        if not str(row.get("compat_manifest_hash", "")).strip():
            return {
                "status": "fail",
                "message": "pack {} missing compat_manifest_hash after load".format(str(row.get("pack_id", ""))),
            }
    return {"status": "pass", "message": "governed packs ship valid compatibility sidecars"}
