"""STRICT test: derived provenance artifacts are compacted deterministically."""

from __future__ import annotations

import sys

from tools.xstack.testx.tests.provenance_compaction_testlib import (
    build_compaction_fixture_state,
    read_provenance_classification_rows,
)


TEST_ID = "test_derived_artifacts_compactable"
TEST_TAGS = ["strict", "provenance", "compaction", "derived"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.provenance import compact_provenance_window

    classifications = read_provenance_classification_rows(repo_root)
    state = build_compaction_fixture_state("derived")
    result = compact_provenance_window(
        state_payload=state,
        classification_rows=classifications,
        shard_id="shard.derived",
        start_tick=5,
        end_tick=8,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "compaction run failed in derived fixture"}
    out_state = dict(result.get("state") or {})

    explain_rows = [dict(row) for row in list(out_state.get("explain_artifact_rows") or []) if isinstance(row, dict)]
    if len(explain_rows) != 1 or int(explain_rows[0].get("tick", -1)) != 11:
        return {"status": "fail", "message": "derived explain artifacts were not compacted in-window"}

    inspection_rows = [dict(row) for row in list(out_state.get("inspection_snapshot_rows") or []) if isinstance(row, dict)]
    if len(inspection_rows) != 1 or int(inspection_rows[0].get("tick", -1)) != 12:
        return {"status": "fail", "message": "derived inspection snapshots were not compacted in-window"}

    model_rows = [dict(row) for row in list(out_state.get("model_evaluation_results") or []) if isinstance(row, dict)]
    if model_rows:
        return {"status": "fail", "message": "model evaluation rows inside compaction window should be removed"}

    info_rows = [dict(row) for row in list(out_state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    info_types = sorted(str(row.get("artifact_type_id", "")).strip() for row in info_rows)
    if info_types != ["artifact.energy_ledger_entry", "artifact.explain"]:
        return {"status": "fail", "message": "unexpected post-compaction info artifact classes: {}".format(",".join(info_types))}
    if int(sum(1 for row in info_rows if int(row.get("tick", -1)) == 6)) != 1:
        return {"status": "fail", "message": "derived info artifact at tick 6 should have been compacted"}

    summary_rows = [dict(row) for row in list(out_state.get("provenance_compaction_summaries") or []) if isinstance(row, dict)]
    if not summary_rows:
        return {"status": "fail", "message": "derived compaction summary row missing"}
    removed_total = int(summary_rows[-1].get("removed_total", 0) or 0)
    if removed_total <= 0:
        return {"status": "fail", "message": "derived compaction summary reports no removed rows"}
    return {"status": "pass", "message": "derived artifacts compacted with summary marker"}
