"""STRICT test: candidate_count limit refusal behavior is deterministic."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.worldgen.candidate_count_limit"
TEST_TAGS = ["strict", "worldgen", "determinism"]


def _load_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from worldgen.core.constraint_solver import solve_constraints

    module_registry = _load_json(os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json"))
    payload = {
        "schema_version": "1.0.0",
        "constraints_id": "constraints.test.candidate_limit",
        "universe_scope": "region",
        "hard_constraints": [],
        "soft_constraints": [],
        "scoring_functions": [],
        "deterministic_seed_policy": "multi",
        "candidate_count": 0,
        "tie_break_policy": "lexicographic",
        "refusal_codes": [
            "refusal.constraints_unsatisfiable",
            "refusal.search_exhausted",
        ],
        "extensions": {},
    }

    result = solve_constraints(
        repo_root=repo_root,
        constraints_payload=payload,
        module_registry_payload=module_registry,
        base_seed="seed.worldgen.limit.001",
    )
    if result.get("result") != "refused":
        return {"status": "fail", "message": "candidate_count=0 must refuse"}
    reason_code = str(((result.get("refusal") or {}).get("reason_code", "")))
    if reason_code != "refusal.search_exhausted":
        return {"status": "fail", "message": "unexpected refusal code for candidate_count limit"}
    return {"status": "pass", "message": "candidate_count limit refusal passed"}
