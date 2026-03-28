from __future__ import annotations

from tools.xstack.testx.tests.xi4z_fix2_testlib import committed_fix2_report, committed_lock_v3


def test_xi4z_v3_no_stdlib_target_collisions(repo_root: str) -> None:
    lock_payload = committed_lock_v3(repo_root)
    report_payload = committed_fix2_report(repo_root)

    fixed = sorted(report_payload.get("stdlib_collision_targets_fixed") or [])
    assert fixed == ["platform", "time"]

    for row in list(lock_payload.get("approved_for_xi5") or []):
        target_path = str(dict(row or {}).get("target_path") or "").replace("\\", "/")
        top = target_path.split("/")[0] if target_path else ""
        assert top not in {"platform", "time"}
