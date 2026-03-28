from __future__ import annotations

from tools.xstack.testx.tests.xi5a_v4_testlib import committed_move_map, committed_residual_report


def test_deferred_paths_untouched(repo_root: str) -> None:
    move_map = committed_move_map(repo_root)
    residual = committed_residual_report(repo_root)
    moved_sources = {row.get("from") for row in list(move_map.get("rows") or [])}
    deferred_sources = {row.get("source_path") for row in list(residual.get("deferred_to_xi5b_remaining") or [])}
    assert "src/worldgen/__init__.py" in deferred_sources
    assert not (moved_sources & deferred_sources)
