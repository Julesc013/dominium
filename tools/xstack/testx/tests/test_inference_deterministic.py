"""FAST test: FORM-1 inference candidate generation is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.infrastructure.formalization.inference_deterministic"
TEST_TAGS = ["fast", "infrastructure", "formalization", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from infrastructure.formalization import infer_candidates

    kwargs = {
        "formalization_id": "formalization.det.alpha",
        "target_kind": "track",
        "target_context_id": "assembly.structure_instance.alpha",
        "raw_sources": ["part.c", "part.a", "part.b", "part.a"],
        "current_tick": 20,
        "max_search_cost_units": 8,
        "cost_units_per_candidate": 1,
        "max_candidates_cap": 16,
        "suggested_spec_ids": ["spec.track.standard_gauge.v1", "spec.track.standard_gauge.v1"],
        "extensions": {"source": "test"},
    }
    first = infer_candidates(**copy.deepcopy(kwargs))
    second = infer_candidates(**copy.deepcopy(kwargs))
    if first != second:
        return {"status": "fail", "message": "inference candidates drifted for identical inputs"}

    reordered = dict(kwargs)
    reordered["raw_sources"] = ["part.b", "part.c", "part.a"]
    third = infer_candidates(**copy.deepcopy(reordered))
    if first != third:
        return {"status": "fail", "message": "raw source ordering changed deterministic inference output"}
    if int(first.get("candidate_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "expected at least one deterministic inference candidate"}
    if not str(first.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "missing deterministic_fingerprint for inference output"}
    return {"status": "pass", "message": "formalization inference deterministic output is stable"}

