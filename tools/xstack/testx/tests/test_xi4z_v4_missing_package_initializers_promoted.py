from __future__ import annotations

from tools.xstack.testx.tests.xi4z_fix3_testlib import committed_fix3_report, committed_lock_v4


def test_xi4z_v4_missing_package_initializers_promoted(repo_root: str) -> None:
    lock_payload = committed_lock_v4(repo_root)
    report_payload = committed_fix3_report(repo_root)

    promoted = sorted(report_payload.get("missing_package_initializers_promoted") or [])
    assert promoted == [
        "src/client/interaction/__init__.py",
        "src/lib/store/__init__.py",
    ]

    approved_targets = {
        str(dict(row or {}).get("source_path") or dict(row or {}).get("file_path") or "").replace("\\", "/"): str(dict(row or {}).get("target_path") or "").replace("\\", "/")
        for row in list(lock_payload.get("approved_for_xi5") or [])
    }
    assert approved_targets["src/client/interaction/__init__.py"] == "client/interaction/__init__.py"
    assert approved_targets["src/lib/store/__init__.py"] == "lib/store/__init__.py"
