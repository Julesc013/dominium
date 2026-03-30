from __future__ import annotations

from tools.xstack.testx.tests.xi8_testlib import (
    committed_structure_lock,
    recompute_structure_lock_content_hash,
    recompute_structure_lock_fingerprint,
)

TEST_ID = "test_repository_structure_lock_valid"
TEST_TAGS = ["fast", "xi8", "structure", "schema"]


def run(repo_root: str):
    payload = committed_structure_lock(repo_root)
    if str(payload.get("report_id", "")).strip() != "repo.structure.lock.v1":
        return {"status": "fail", "message": "repository structure lock report_id drifted"}
    for field_name in (
        "allowed_top_level_directories",
        "allowed_top_level_files",
        "allowed_source_like_roots",
        "architecture_graph_v1_content_hash",
        "module_boundary_rules_v1_content_hash",
        "content_hash",
        "deterministic_fingerprint",
    ):
        if payload.get(field_name) in ("", None, []):
            return {"status": "fail", "message": "repository structure lock missing {}".format(field_name)}
    if str(payload.get("content_hash", "")).strip() != recompute_structure_lock_content_hash(payload):
        return {"status": "fail", "message": "repository structure lock content_hash drifted"}
    if str(payload.get("deterministic_fingerprint", "")).strip() != recompute_structure_lock_fingerprint(payload):
        return {"status": "fail", "message": "repository structure lock deterministic_fingerprint drifted"}
    return {"status": "pass", "message": "Xi-8 repository structure lock is complete and hash-stable"}
