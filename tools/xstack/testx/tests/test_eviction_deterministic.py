"""FAST test: MW-4 cache eviction is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_eviction_deterministic"
TEST_TAGS = ["fast", "mw4", "worldgen", "cache", "eviction"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.worldgen.refinement.refinement_cache import build_refinement_cache_entry, evict_refinement_cache_entries
    from tools.xstack.testx.tests.geo8_testlib import worldgen_cell_key

    rows = [
        build_refinement_cache_entry(
            cache_key="cache.{}".format(index),
            geo_cell_key=worldgen_cell_key([index, 0, 0]),
            refinement_level=2,
            last_used_tick=tick,
            extensions={},
        )
        for index, tick in ((0, 4), (1, 1), (2, 3), (3, 2))
    ]
    first = evict_refinement_cache_entries(cache_entry_rows=rows, max_entries_by_level={2: 2})
    second = evict_refinement_cache_entries(cache_entry_rows=list(reversed(rows)), max_entries_by_level={2: 2})
    first_evicted = [str(row.get("cache_key", "")) for row in list(first.get("evicted_rows") or [])]
    second_evicted = [str(row.get("cache_key", "")) for row in list(second.get("evicted_rows") or [])]
    if first_evicted != second_evicted:
        return {"status": "fail", "message": "cache eviction order drifted across repeated runs"}
    if first_evicted != ["cache.1", "cache.3"]:
        return {"status": "fail", "message": "cache eviction did not drop least-recently-used rows first"}
    return {"status": "pass", "message": "MW-4 cache eviction is deterministic"}
