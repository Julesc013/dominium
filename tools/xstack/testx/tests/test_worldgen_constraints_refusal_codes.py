"""TestX refusal code checks for unsatisfiable worldgen constraints."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.worldgen.constraints_refusal_codes"
TEST_TAGS = ["strict", "worldgen", "determinism"]


def _load_module_registry(repo_root: str) -> dict:
    path = os.path.join(repo_root, "data", "registries", "worldgen_module_registry.json")
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from worldgen.core.constraint_solver import solve_constraints

    constraints_payload = {
        "schema_version": "1.0.0",
        "constraints_id": "constraints.test.unsat",
        "universe_scope": "region",
        "hard_constraints": [
            {
                "constraint_id": "hard.impossible.range",
                "target": "world.layer.elevation",
                "operator": "range",
                "value": {"min": 20000, "max": 25000},
                "weight": 0,
                "description": "force unsatisfiable threshold for deterministic refusal test",
            }
        ],
        "soft_constraints": [],
        "scoring_functions": [
            {
                "scoring_id": "score.elevation",
                "metric": "world.layer.elevation",
                "operator": "maximize",
                "weight": 1,
                "description": "placeholder scoring",
            }
        ],
        "deterministic_seed_policy": "multi",
        "candidate_count": 4,
        "tie_break_policy": "lexicographic",
        "refusal_codes": [
            "refusal.constraints_unsatisfiable",
            "refusal.search_exhausted",
        ],
        "extensions": {},
    }

    result = solve_constraints(
        repo_root=repo_root,
        constraints_payload=constraints_payload,
        module_registry_payload=_load_module_registry(repo_root),
        base_seed="seed.worldgen.unsat.001",
    )
    if result.get("result") != "refused":
        return {"status": "fail", "message": "unsatisfiable constraints must produce refusal result"}
    refusal_payload = result.get("refusal") if isinstance(result.get("refusal"), dict) else {}
    reason_code = str(refusal_payload.get("reason_code", ""))
    if reason_code != "refusal.constraints_unsatisfiable":
        return {"status": "fail", "message": "unexpected refusal code '{}'".format(reason_code)}
    return {"status": "pass", "message": "constraints refusal code checks passed"}

