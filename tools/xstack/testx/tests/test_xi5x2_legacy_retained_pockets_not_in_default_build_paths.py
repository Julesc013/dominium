from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_source_pocket_policy

TEST_ID = "test_xi5x2_legacy_retained_pockets_not_in_default_build_paths"
TEST_TAGS = ["fast", "xi5x2", "legacy"]


def run(repo_root: str):
    payload = committed_source_pocket_policy(repo_root)
    offenders = []
    for item in list(payload.get("policy_rows") or []):
        entry = dict(item or {})
        if not str(entry.get("path") or "").startswith("legacy/source/tests"):
            continue
        notes = dict(entry.get("legacy_archive_notes") or {})
        refs = list(notes.get("default_build_reference_files") or [])
        if refs:
            offenders.append(str(entry.get("path") or ""))
        if not bool(notes.get("references_missing_source_tree")):
            offenders.append(str(entry.get("path") or ""))
    if offenders:
        return {"status": "fail", "message": "Xi-5x2 legacy retained pockets are not fenced from default build paths"}
    return {"status": "pass", "message": "Xi-5x2 legacy retained pockets are fenced from default build paths"}
