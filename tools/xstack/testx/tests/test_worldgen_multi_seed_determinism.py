"""TestX deterministic multi-seed search selection checks for worldgen constraints."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.worldgen.multi_seed_determinism"
TEST_TAGS = ["strict", "worldgen", "determinism"]


def _load_module_registry(repo_root: str) -> dict:
    path = os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json")
    return json.load(open(path, "r", encoding="utf-8"))


def _constraints_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "constraints_id": "constraints.test.multi_seed",
        "universe_scope": "region",
        "hard_constraints": [],
        "soft_constraints": [
            {
                "constraint_id": "soft.elevation.min",
                "target": "world.layer.elevation",
                "operator": "min",
                "value": 1000,
                "weight": 5,
                "description": "prefer higher elevation",
            }
        ],
        "scoring_functions": [
            {
                "scoring_id": "score.elevation",
                "metric": "world.layer.elevation",
                "operator": "maximize",
                "weight": 3,
                "description": "maximize elevation metric",
            }
        ],
        "deterministic_seed_policy": "multi",
        "candidate_count": 8,
        "tie_break_policy": "lexicographic",
        "refusal_codes": [
            "refusal.constraints_unsatisfiable",
            "refusal.search_exhausted",
        ],
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from worldgen.core.constraint_solver import solve_constraints

    module_registry = _load_module_registry(repo_root)
    payload = _constraints_payload()
    first = solve_constraints(
        repo_root=repo_root,
        constraints_payload=payload,
        module_registry_payload=module_registry,
        base_seed="seed.worldgen.multi.001",
    )
    if first.get("result") != "complete":
        return {"status": "fail", "message": "first solve_constraints invocation failed"}
    second = solve_constraints(
        repo_root=repo_root,
        constraints_payload=payload,
        module_registry_payload=module_registry,
        base_seed="seed.worldgen.multi.001",
    )
    if second.get("result") != "complete":
        return {"status": "fail", "message": "second solve_constraints invocation failed"}

    first_plan = dict(first.get("search_plan") or {})
    second_plan = dict(second.get("search_plan") or {})
    if first_plan.get("selected_seed") != second_plan.get("selected_seed"):
        return {"status": "fail", "message": "selected_seed must be deterministic"}
    if first_plan.get("deterministic_hash") != second_plan.get("deterministic_hash"):
        return {"status": "fail", "message": "search plan deterministic_hash mismatch across identical runs"}
    if list(first_plan.get("candidate_seeds") or []) != list(second_plan.get("candidate_seeds") or []):
        return {"status": "fail", "message": "candidate_seeds ordering drift detected"}
    return {"status": "pass", "message": "multi-seed deterministic selection passed"}

