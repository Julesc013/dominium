"""STRICT test: canonical provenance events are not compacted in-window."""

from __future__ import annotations

import sys

from tools.xstack.testx.tests.provenance_compaction_testlib import (
    build_compaction_fixture_state,
    read_provenance_classification_rows,
)


TEST_ID = "test_canonical_events_not_compacted"
TEST_TAGS = ["strict", "provenance", "compaction", "canonical"]

_CANONICAL_KEYS = (
    "energy_ledger_entries",
    "boundary_flux_events",
    "time_adjust_events",
    "fault_events",
    "exception_events",
    "leak_events",
    "burst_events",
    "relief_events",
    "branch_events",
)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from meta.provenance import compact_provenance_window

    classifications = read_provenance_classification_rows(repo_root)
    state = build_compaction_fixture_state("canonical")
    before = {
        key: [dict(row) for row in list(state.get(key) or []) if isinstance(row, dict)]
        for key in _CANONICAL_KEYS
    }
    result = compact_provenance_window(
        state_payload=state,
        classification_rows=classifications,
        shard_id="shard.canonical",
        start_tick=5,
        end_tick=8,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "compaction run failed in canonical fixture"}
    out_state = dict(result.get("state") or {})

    for key in _CANONICAL_KEYS:
        after_rows = [dict(row) for row in list(out_state.get(key) or []) if isinstance(row, dict)]
        if after_rows != before[key]:
            return {"status": "fail", "message": "canonical key '{}' changed during compaction".format(key)}

    marker_rows = [dict(row) for row in list(out_state.get("compaction_markers") or []) if isinstance(row, dict)]
    if len(marker_rows) != 1:
        return {"status": "fail", "message": "expected exactly one compaction marker row"}
    return {"status": "pass", "message": "canonical events remained untouched during compaction"}
