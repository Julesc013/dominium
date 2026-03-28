from __future__ import annotations

from tools.xstack.testx.tests.xi4z_fix3_testlib import committed_lock_v4


def test_xi4z_v4_only_dangerous_shadow_roots_approved(repo_root: str) -> None:
    lock_payload = committed_lock_v4(repo_root)

    for row in list(lock_payload.get("approved_for_xi5") or []):
        source_path = str(dict(row or {}).get("source_path") or dict(row or {}).get("file_path") or "").replace("\\", "/")
        assert source_path.startswith("src/") or source_path.startswith("app/src/")

    for row in list(lock_payload.get("approved_to_attic") or []):
        source_path = str(dict(row or {}).get("source_path") or dict(row or {}).get("file_path") or "").replace("\\", "/")
        assert source_path.startswith("src/") or source_path.startswith("app/src/")
