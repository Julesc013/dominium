from __future__ import annotations

from tools.xstack.testx.tests.xi4z_fix3_testlib import fresh_hashes


def test_xi4z_fix3_outputs_deterministic(repo_root: str) -> None:
    first = fresh_hashes(repo_root)
    second = fresh_hashes(repo_root)
    assert first == second
