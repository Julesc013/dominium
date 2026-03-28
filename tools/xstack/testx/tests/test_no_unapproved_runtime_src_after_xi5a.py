from __future__ import annotations

from tools.xstack.testx.tests.xi5a_v4_testlib import committed_residual_report


def test_no_unapproved_runtime_src_after_xi5a(repo_root: str) -> None:
    residual = committed_residual_report(repo_root)
    assert residual.get("report_id") == "xi.5a.postmove_residual_src_report.v4"
    assert list(residual.get("unexpected_remaining_src_paths") or []) == []
