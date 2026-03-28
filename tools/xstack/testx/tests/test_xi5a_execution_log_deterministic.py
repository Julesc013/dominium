from __future__ import annotations

from tools.xstack.testx.tests.xi5a_v4_testlib import (
    committed_attic_map,
    committed_execution_log,
    committed_move_map,
    committed_residual_report,
    recompute_fingerprint,
)


def test_xi5a_execution_log_deterministic(repo_root: str) -> None:
    for payload in (
        committed_move_map(repo_root),
        committed_attic_map(repo_root),
        committed_execution_log(repo_root),
        committed_residual_report(repo_root),
    ):
        assert payload.get("deterministic_fingerprint") == recompute_fingerprint(payload)
